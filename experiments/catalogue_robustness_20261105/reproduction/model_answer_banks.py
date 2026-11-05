"""Collect local model answer banks, then replay fixed policies without retuning."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, json, time
import requests
import numpy as np
import cross_catalogue as cross
from budget_comparison import BudgetBelief, BUDGETS, METHODS
import ranking_search as source

OUT=cross.OUT
MODELS=['qwen38-codex:latest','gemma4-e4b-q8kp:latest']
BASE='http://127.0.0.1:11434'
FIELDS=cross.FIELDS
PRETTY=['sleeve length','pattern','neckline','main fabric','wash care','maximum price']


def write(name,obj):
    cross.write(name,obj)


def prompt(labels,bits):
    card='\n'.join(f'- {label}: {labels[field][bit]}' for label,field,bit in zip(PRETTY,FIELDS,bits))
    questions='\n'.join(f'{field}: Which is your preference? A = {labels[field][0]}; B = {labels[field][1]}.' for field in FIELDS)
    return ('You are a simulated shopper. The following card states your fixed preferences. '
            'Answer the six questions using only these preferences. Do not change your preferences. '
            'No products or recommendation policies are shown.\nPreference card:\n'+card+
            '\nQuestions:\n'+questions+'\nReturn a JSON object with exactly these six field names. '
            'Each answer must be the string A or B. Give no explanation.')


def replay(model,accept,answers):
    post=model.marginals(accept);value=[p.max(1) for p in post]
    sig=accept@(1<<np.arange(accept.shape[1]));groups=model.marginals(sig[:,None]==np.unique(sig))
    ent=[-(p*np.log(np.maximum(p,1e-300))).sum(1) for p in groups]
    h=-(model.p*np.log(model.p)+(1-model.p)*np.log(1-model.p))
    mass=np.prod(np.where(model.bits,model.p,1-model.p),axis=1)
    state=np.zeros((4,len(model.bits)),int);alive=np.ones_like(state,bool);rates={}
    for n in range(5):
        policies=np.array([np.full(len(model.codes[n]),n),
                          model.choose(np.broadcast_to(h,(len(model.codes[n]),model.d)),n),
                          model.choose(-model.expect(ent[n+1],n),n),
                          model.choose(model.expect(value[n+1],n),n)])
        q=policies[np.arange(4)[:,None],state]
        y=answers[np.arange(len(model.bits))[None,:],q]
        alive &= y>=0
        state=model.children[n][state,q,np.maximum(y,0)]
        if n+1 in BUDGETS:
            decision=post[n+1].argmax(1)[state]
            hit=accept[np.arange(len(model.bits))[None,:],decision]&alive
            rates[n+1]=(hit@mass).tolist()
    return rates


def run():
    datasets,plan=cross.freeze();model=BudgetBelief(cross.PRIOR)
    session=requests.Session();session.trust_env=False
    tags=session.get(BASE+'/api/tags',timeout=20).json()['models']
    meta={m:next(x for x in tags if x['name']==m) for m in MODELS}
    schema=dict(type='object',properties={f:dict(type='string',enum=['A','B']) for f in FIELDS},required=FIELDS,additionalProperties=False)
    protocol=dict(models={m:{k:v for k,v in meta[m].items() if k in ['name','digest','size','details']} for m in MODELS},
                  model_identity='Qwen local checkpoint is a third-party modified Qwen-family 27.3B Q4_K_M checkpoint, tagged qwen38-codex but reporting qwen35 architecture. Gemma local checkpoint reports gemma4 architecture, 7.5B, Q8_0. No claim of official unmodified weights.',
                  server_version=session.get(BASE+'/api/version',timeout=20).json(),
                  datasets=list(datasets),profiles=model.bits.tolist(),fields=FIELDS,labels={k:v['labels'] for k,v in plan['cases'].items()},
                  generation=dict(temperature=0,num_ctx=2048,num_predict=128,seed=20261105545,think=False,format=schema),
                  interaction='One reset request per profile, six field answers as a bank. Each policy sees only the selected field at each step. No menus, method names, success criteria or comparative results in customer prompts.',
                  failures='Do not retry malformed/completed responses. Transport errors retained as invalid banks. A selected invalid answer makes that trajectory unsuccessful. All 64 profiles are retained and weighted by the same prior.',
                  scope='Post-confirmation single answer-bank interface check per model/profile; no human behavior claim, no claim of free multi-turn conversational validation, no task retuning.',
                  example_prompt=prompt(plan['cases']['Myntra']['labels'],model.bits[0]),
                  source_protocol_sha256=hashlib.sha256((OUT/'cross_catalogue_protocol.json').read_bytes()).hexdigest())
    path=OUT/'model_bank_protocol.json'
    if path.exists():assert json.loads(path.read_text(encoding='utf-8'))==json.loads(json.dumps(protocol))
    else:write(path.name,protocol)
    recordfile=OUT/'model_bank_responses.jsonl'
    done={}
    if recordfile.exists():
        for line in recordfile.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);done[(r['model'],r['dataset'],r['profile'])]=r
    for name in MODELS:
        for dataset,case in plan['cases'].items():
            for i,bits in enumerate(model.bits):
                if (name,dataset,i) in done:continue
                text=prompt(case['labels'],bits)
                payload=dict(model=name,messages=[dict(role='user',content=text)],stream=False,
                             think=False,format=schema,options=dict(temperature=0,num_ctx=2048,num_predict=128,seed=20261105545),keep_alive='10m')
                start=time.monotonic()
                result=dict(model=name,dataset=dataset,profile=i,truth=bits.tolist(),prompt=text)
                try:
                    response=session.post(BASE+'/api/chat',json=payload,timeout=180)
                    result['http_status']=response.status_code
                    response.raise_for_status();raw=response.json();result['raw']=raw
                    parsed=json.loads(raw['message']['content'])
                    valid=isinstance(parsed,dict) and set(parsed)==set(FIELDS) and all(parsed[f] in ('A','B') for f in FIELDS)
                    result['answers']=[int(parsed[f]=='B') for f in FIELDS] if valid else [-1]*6
                    result['schema_valid']=bool(valid)
                except Exception as e:
                    result.update(error=type(e).__name__,answers=[-1]*6,schema_valid=False)
                result['elapsed_seconds']=time.monotonic()-start
                with recordfile.open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
                done[(name,dataset,i)]=result
                if (i+1)%8==0:print(name,dataset,i+1,'/64',f'{result["elapsed_seconds"]:.1f}s',flush=True)
        # Release the first model before loading the next on the same GPU.
        session.post(BASE+'/api/generate',json=dict(model=name,keep_alive=0),timeout=30)
    outputs={}
    deterministic=json.loads((OUT/'cross_catalogue_results.json').read_text(encoding='utf-8'))
    for name in MODELS:
        outputs[name]={}
        for dataset,case in plan['cases'].items():
            answers=np.array([done[(name,dataset,i)]['answers'] for i in range(64)])
            rows={r['product_id']:r for r in datasets[dataset]};records=[]
            for menu in case['menus']:
                accept=source.signatures(*source.components([rows[x] for x in menu['items']],case['labels'],model),plan['config'])
                records.append(dict(**menu,rates=replay(model,accept,answers)))
            rates=100*np.mean([[r['rates'][b] for b in BUDGETS] for r in records],axis=0)
            outputs[name][dataset]=dict(valid_banks=int((answers>=0).all(1).sum()),total_banks=64,
                correct_fields=int((answers==model.bits).sum()),total_fields=384,
                accuracy_percent=rates.tolist(),dv_minus_set_ig_pp=(rates[:,3]-rates[:,2]).tolist(),
                max_difference_from_simulation_pp=float(np.max(np.abs(rates-np.array(deterministic['summary'][dataset]['accuracy_percent'])))),menus=records)
    write('model_bank_results.json',dict(methods=METHODS,budgets=BUDGETS,results=outputs,
        protocol_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_sha256=hashlib.sha256(recordfile.read_bytes()).hexdigest()))
    print(json.dumps({m:{d:{k:v for k,v in z.items() if k!='menus'} for d,z in r.items()} for m,r in outputs.items()},indent=2),flush=True)


if __name__=='__main__':run()
