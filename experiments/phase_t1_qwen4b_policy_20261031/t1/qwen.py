"""Single resident, local-only Qwen model; no service or base-weight mutations."""
from __future__ import annotations
import contextlib
import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


@contextlib.contextmanager
def claim_device():
    """Serialize this task; refuse an already occupied GPU without touching it."""
    import fcntl
    import subprocess
    visible=os.environ.get('CUDA_VISIBLE_DEVICES')
    if visible!='3':raise RuntimeError('Frozen single-device selection must be CUDA_VISIBLE_DEVICES=3')
    with (ROOT/'artifacts/gpu3_task.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        snapshot=subprocess.check_output(['nvidia-smi','-i','3','--query-gpu=uuid,memory.used','--format=csv,noheader,nounits'],text=True).strip()
        if int(snapshot.rsplit(',',1)[1].strip())>512:
            raise RuntimeError('Selected GPU is now occupied; no process was changed: '+snapshot)
        yield


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def model_load(adapter=None):
    import torch
    from transformers import AutoTokenizer, Qwen3_5ForConditionalGeneration
    from peft import LoraConfig, get_peft_model, PeftModel
    cfg=json.loads((ROOT/'config.json').read_text())
    torch.set_num_threads(1)
    torch.manual_seed(cfg['sft']['seed'])
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True, warn_only=True)
    started=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(cfg['checkpoint'],local_files_only=True)
    tokenizer.pad_token_id=tokenizer.eos_token_id
    model=Qwen3_5ForConditionalGeneration.from_pretrained(
        cfg['checkpoint'],dtype=torch.bfloat16,attn_implementation='sdpa',
        local_files_only=True,device_map={'':'cuda:0'})
    model.config.use_cache=False
    if adapter:
        model=PeftModel.from_pretrained(model,str(adapter),is_trainable=False)
    else:
        targets=r'model\.language_model\.layers\.\d+\.(self_attn\.(q_proj|k_proj|v_proj|o_proj)|linear_attn\.(in_proj_qkv|in_proj_z|in_proj_a|in_proj_b|out_proj)|mlp\.(gate_proj|up_proj|down_proj))'
        model=get_peft_model(model,LoraConfig(r=cfg['sft']['rank'],lora_alpha=cfg['sft']['alpha'],
            lora_dropout=0.,target_modules=targets,task_type='CAUSAL_LM',bias='none'))
    names=[(n,p.numel(),str(p.dtype)) for n,p in model.named_parameters() if p.requires_grad]
    if not adapter:
        assert names and all('lora_' in n and 'language_model' in n for n,_,_ in names)
        assert not any('visual' in n or 'vision' in n for n,_,_ in names)
    metadata={'checkpoint':cfg['checkpoint'],'model_class':model.base_model.model.__class__.__name__,
        'load_seconds':time.perf_counter()-started,'all_parameters':sum(p.numel() for p in model.parameters()),
        'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),
        'trainable_names':names,'base_precision':'bfloat16',
        'adapter_precision':sorted({str(p.dtype) for n,p in model.named_parameters() if 'lora_' in n}),
        'attention':'sdpa','device_name':torch.cuda.get_device_name(0),
        'cuda_capability':list(torch.cuda.get_device_capability(0)),
        'bf16_supported':torch.cuda.is_bf16_supported(),'model_base_frozen':all(not p.requires_grad for n,p in model.named_parameters() if 'lora_' not in n)}
    return model,tokenizer,metadata


def encode_row(tokenizer,row):
    messages=row['messages']
    assert messages[-1]['role']=='assistant'
    prefix=tokenizer.apply_chat_template(messages[:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    full=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=False,enable_thinking=False)
    if not full.startswith(prefix):
        raise ValueError('Chat template does not provide a strict completion prefix')
    prefix_ids=tokenizer.encode(prefix,add_special_tokens=False)
    ids=tokenizer.encode(full,add_special_tokens=False)
    if ids[:len(prefix_ids)]!=prefix_ids:
        raise ValueError('Token boundary crosses prompt/completion prefix')
    if len(ids)>1024:raise ValueError(f'No truncation allowed: {len(ids)} tokens')
    labels=[-100]*len(prefix_ids)+ids[len(prefix_ids):]
    assert any(x!=-100 for x in labels)
    return {'input_ids':ids,'labels':labels,'prompt_tokens':len(prefix_ids),'target_tokens':len(ids)-len(prefix_ids)}


class QwenPolicy:
    def __init__(self,model,tokenizer,*,adapter_enabled,call_counter=None):
        self.model=model;self.tokenizer=tokenizer;self.adapter_enabled=adapter_enabled
        self.call_counter=call_counter

    def predict(self,state):
        from .core import SYSTEM_PROMPT,serialize_state,parse_percent
        import torch
        if self.call_counter is not None:self.call_counter()
        prompt=self.tokenizer.apply_chat_template(
            [{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':serialize_state(state)}],
            tokenize=False,add_generation_prompt=True,enable_thinking=False)
        inputs=self.tokenizer(prompt,return_tensors='pt',add_special_tokens=False).to('cuda:0')
        if inputs.input_ids.shape[-1]>960:raise ValueError('Evaluation prompt too long')
        self.model.eval()
        self.model.config.use_cache=True
        torch.cuda.synchronize();start=time.perf_counter();cpu=time.process_time()
        ctx=contextlib.nullcontext() if self.adapter_enabled else self.model.disable_adapter()
        with ctx,torch.inference_mode():
            output=self.model.generate(**inputs,do_sample=False,max_new_tokens=64,
                pad_token_id=self.tokenizer.pad_token_id,use_cache=True)
        torch.cuda.synchronize()
        elapsed=time.perf_counter()-start
        new=output[0,inputs.input_ids.shape[-1]:]
        raw=self.tokenizer.decode(new,skip_special_tokens=True)
        parsed=parse_percent(raw,state)
        return {**parsed,'raw':raw,'latency':elapsed,'latency_seconds':elapsed,
            'cpu_seconds':time.process_time()-cpu,'prompt_tokens':int(inputs.input_ids.numel()),
            'output_tokens':int(new.numel()),'adapter_enabled':self.adapter_enabled,
            'backend':'local_transformers_peft_bf16_sdpa_greedy'}


def smoke(long=False):
    """Technical backward test only: no optimizer update and no scientific row."""
    import torch
    import traceback
    receipt={'status':'started','scientific_optimizer_steps':0,'model_calls':0}
    target=ROOT/('artifacts/smoke_long.json' if long else 'artifacts/smoke.json')
    if target.exists():raise RuntimeError('Retain prior smoke receipt; choose explicit revision')
    dump(target,receipt)
    start=time.perf_counter()
    try:
        model,tok,meta=model_load()
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model.enable_input_require_grads()
        model.train();torch.cuda.reset_peak_memory_stats()
        row={'messages':[{'role':'system','content':'Return ten integer percentages as one JSON array.'},
            {'role':'user','content':'Allocate uniformly to eight task actions, with two type actions masked.'},
            {'role':'assistant','content':'[13,13,13,13,12,12,12,12,0,0]'}]}
        enc=encode_row(tok,row)
        if long:
            padding=1024-len(enc['input_ids'])
            assert padding>=0
            insert=enc['prompt_tokens']
            token=tok.encode('observed',add_special_tokens=False)[0]
            enc['input_ids']=enc['input_ids'][:insert]+[token]*padding+enc['input_ids'][insert:]
            enc['labels']=enc['labels'][:insert]+[-100]*padding+enc['labels'][insert:]
            enc['prompt_tokens']+=padding
            assert len(enc['input_ids'])==1024
        batch={k:torch.tensor([enc[k]],device='cuda:0') for k in ['input_ids','labels']}
        loss=model(**batch,use_cache=False).loss
        assert torch.isfinite(loss)
        loss.backward()
        grads=[p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
        assert grads and all(torch.isfinite(x).all() for x in grads)
        assert any(x.abs().max()>0 for x in grads)
        assert all(p.grad is None for n,p in model.named_parameters() if 'lora_' not in n)
        model.zero_grad(set_to_none=True)
        adapter_dir=ROOT/('artifacts/smoke_long_adapter' if long else 'artifacts/smoke_adapter')
        model.save_pretrained(adapter_dir,safe_serialization=True)
        from peft import get_peft_model_state_dict
        from safetensors.torch import load_file
        expected=get_peft_model_state_dict(model)
        saved=load_file(str(adapter_dir/'adapter_model.safetensors'))
        assert expected.keys()==saved.keys()
        assert all(torch.equal(t.detach().cpu(),saved[n]) for n,t in expected.items())
        receipt.update(status='passed',**meta,loss=float(loss.detach()),gradient_tensors=len(grads),
            peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),
            token_lengths={k:enc[k] for k in ['prompt_tokens','target_tokens']},adapter_roundtrip_exact=True,
            wall_seconds=time.perf_counter()-start,optimizer_steps=0)
    except BaseException as exc:
        receipt.update(status='failed',error=repr(exc),traceback=traceback.format_exc(),wall_seconds=time.perf_counter()-start)
        dump(target,receipt);raise
    dump(target,receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='trainable_names'},indent=2),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--long',action='store_true')
    args=parser.parse_args()
    with claim_device():smoke(long=args.long)
