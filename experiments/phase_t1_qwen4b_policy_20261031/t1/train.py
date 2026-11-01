"""One frozen, completion-only SFT pass; technical smoke/data gate must pass."""
import hashlib
import json
from pathlib import Path
import time
import traceback

from .qwen import ROOT,dump,model_load,encode_row,claim_device
from .freeze import verify


def main():
    import torch
    from .core import serialize_state
    cfg=json.loads((ROOT/'config.json').read_text());sft=cfg['sft']
    assert json.loads((ROOT/'artifacts/smoke.json').read_text())['status']=='passed'
    assert json.loads((ROOT/'artifacts/smoke_long.json').read_text())['status']=='passed'
    assert json.loads((ROOT/'audit/TOKENIZATION.json').read_text())['status']=='passed'
    assert 'FINAL PRE-TRAIN VERDICT: PASS' in (ROOT/'DATA_LEAKAGE_AUDIT.md').read_text()
    verify('training_freeze.json')
    receiptpath=ROOT/'artifacts/training/execution.json'
    if receiptpath.exists():raise RuntimeError('No scientific training retry/overwrite')
    start=time.perf_counter();cpu=time.process_time();steps=0;micro=0
    receipt={'status':'started','optimizer_steps':0,'microbatches':0,'training_seed':sft['seed']}
    dump(receiptpath,receipt)
    try:
        train=[json.loads(x) for x in (ROOT/'artifacts/data/train.jsonl').open()]
        val=[json.loads(x) for x in (ROOT/'artifacts/data/validation.jsonl').open()]
        assert len(train)==1024 and len(val)==128
        model,tok,metadata=model_load()
        encoded=[encode_row(tok,r) for r in train]
        validation=[encode_row(tok,r) for r in val]
        dump(ROOT/'artifacts/training/tokenization.json',{
            'train_examples':len(encoded),'validation_examples':len(validation),
            'max_total_tokens':max(len(r['input_ids']) for r in encoded+validation),
            'train_prompt_tokens':sum(r['prompt_tokens'] for r in encoded),
            'train_target_tokens':sum(r['target_tokens'] for r in encoded),
            'loss_mask':'all prompt tokens -100; completion including final im_end supervised',
            'no_truncation':True,'no_test_tokenization':True})
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
        model.enable_input_require_grads();model.config.use_cache=False;model.train()
        optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
            lr=sft['learning_rate'],weight_decay=0.,betas=(.9,.999))
        gen=torch.Generator().manual_seed(sft['seed'])
        order=torch.randperm(len(encoded),generator=gen).tolist()
        optimizer.zero_grad(set_to_none=True);torch.cuda.reset_peak_memory_stats()
        loss_sum=0.;block_loss=0.;n_target=0;weighted_loss=0.
        with (ROOT/'artifacts/training/steps.jsonl').open('x') as log:
            for i,index in enumerate(order):
                if time.perf_counter()-start>sft['hard_seconds']:raise TimeoutError('SFT hard deadline')
                row=encoded[index]
                batch={k:torch.tensor([row[k]],device='cuda:0') for k in ['input_ids','labels']}
                raw=model(**batch,use_cache=False).loss
                if not torch.isfinite(raw):raise FloatingPointError('nonfinite training loss')
                (raw/sft['gradient_accumulation']).backward()
                value=float(raw.detach());loss_sum+=value;block_loss+=value
                weighted_loss+=value*row['target_tokens'];n_target+=row['target_tokens'];micro+=1
                if micro%sft['gradient_accumulation']==0:
                    norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
                    if not torch.isfinite(norm):raise FloatingPointError('nonfinite gradient norm')
                    optimizer.step();optimizer.zero_grad(set_to_none=True);steps+=1
                    record={'step':steps,'microbatches':micro,'loss_mean':block_loss/sft['gradient_accumulation'],
                        'grad_norm':float(norm),'elapsed_seconds':time.perf_counter()-start,
                        'peak_allocated_bytes':torch.cuda.max_memory_allocated()}
                    log.write(json.dumps(record)+'\n');log.flush();block_loss=0.
                    if steps%8==0:print(json.dumps(record),flush=True)
        assert steps==128 and micro==1024
        model.eval();val_loss=0.;val_tokens=0
        with torch.inference_mode():
            for row in validation:
                if time.perf_counter()-start>sft['hard_seconds']:raise TimeoutError('Validation hard deadline')
                batch={k:torch.tensor([row[k]],device='cuda:0') for k in ['input_ids','labels']}
                loss=model(**batch,use_cache=False).loss
                if not torch.isfinite(loss):raise FloatingPointError('nonfinite validation loss')
                val_loss+=float(loss)*row['target_tokens'];val_tokens+=row['target_tokens']
        model.save_pretrained(ROOT/'artifacts/adapters/final',safe_serialization=True)
        tok.save_pretrained(ROOT/'artifacts/adapters/final')
        receipt.update(status='completed',optimizer_steps=steps,microbatches=micro,**metadata,
            train_loss_example_mean=loss_sum/micro,train_loss_token_mean=weighted_loss/n_target,
            validation_loss_token_mean=val_loss/val_tokens,validation_tokens=val_tokens,
            train_target_tokens=n_target,peak_allocated_bytes=torch.cuda.max_memory_allocated(),
            peak_reserved_bytes=torch.cuda.max_memory_reserved(),wall_seconds=time.perf_counter()-start,
            process_cpu_seconds=time.process_time()-cpu,adapter='artifacts/adapters/final',
            checkpoint_selection='final only; no validation or test selection',base_weights_saved_or_merged=False)
    except BaseException as exc:
        receipt.update(status='failed',optimizer_steps=steps,microbatches=micro,error=repr(exc),
            traceback=traceback.format_exc(),wall_seconds=time.perf_counter()-start,
            process_cpu_seconds=time.process_time()-cpu)
        dump(receiptpath,receipt);raise
    dump(receiptpath,receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='trainable_names'},indent=2),flush=True)


if __name__=='__main__':
    with claim_device():main()
