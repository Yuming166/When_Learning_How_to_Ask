"""Development-only task search with every attempted design recorded."""
from collections import Counter
from itertools import product
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json,random,time
import numpy as np
import richer_preferences as prior

OUT=Path(__file__).resolve().parent/'排序探索'
FIELDS=prior.FIELDS
METHODS=['Fixed','ProfileIG','DecisionSetIG','DV1','DV4']
P0=prior.P

def source_rows():
    with ZipFile(prior.SOURCE) as z:
        blob=z.read(next(n for n in z.namelist() if n.endswith('/catalogue_strict.jsonl')))
    return [r for r in map(json.loads,blob.decode('utf-8-sig').splitlines())
            if all(r['attributes'].get(f,{}).get('status')=='reported' for f in FIELDS if f!='budget')]

def labels_for(rows):
    labels={f:[s for s,n in sorted(Counter(r['attributes'][f]['value'] for r in rows).items(),key=lambda x:(-x[1],x[0]))[:2]]
            for f in FIELDS if f!='budget'}
    labels['budget']=np.quantile([float(r['source_price']['minimum']) for r in rows],[.5,.75]).tolist()
    assert all(len(v)==2 for v in labels.values())
    return labels

def menus(rows,seed,n,count):
    rng=random.Random(seed)
    selected=set();result=[]
    import math
    count=min(count,math.comb(len(rows),n))
    while len(result)<count:
        ids=tuple(sorted(r['product_id'] for r in rng.sample(rows,n)))
        if ids not in selected:
            selected.add(ids);result.append(ids)
    return result

def components(cards,labels,belief):
    p=belief.bits;ceiling=np.asarray(labels['budget'])[p[:,5]]
    prices=np.array([float(r['source_price']['minimum']) for r in cards])
    match=[]
    for j,key in enumerate(FIELDS[:belief.d]):
        if key=='budget':continue
        choices=np.array(labels[key])[p[:,j]]
        match.append(choices[:,None]==np.array([r['attributes'][key]['value'] for r in cards])[None,:])
    return np.stack(match,axis=2),prices[None,:]/ceiling[:,None]

def signatures(match,ratio,config):
    weights=np.array(config['weights'])
    value=match@weights/weights.sum()-config['price_penalty']*ratio
    allowed=ratio<=1
    if config['hard']:
        fields=[f for f in FIELDS[:config['d']] if f!='budget']
        for f in config['hard']:
            allowed &= match[:,:,fields.index(f)]
    if config['answer']=='acceptable':
        accept=(value>=config['threshold'])&allowed
        return np.column_stack((accept,~accept.any(1)))
    values=np.column_stack((np.where(allowed,value,-np.inf),np.full(len(match),config['threshold'])))
    return np.isclose(values,values.max(1,keepdims=True),atol=1e-12,rtol=0)

def evaluate(model,accept,details=False):
    n=len(accept[0]);sig=accept@(1<<np.arange(n))
    probs=model.marginals(accept);success=[p.max(1) for p in probs]
    labels=np.unique(sig)
    classes=model.marginals(sig[:,None]==labels)
    entropy=[-(p*np.log(np.maximum(p,1e-300))).sum(1) for p in classes]
    profile=-(model.p*np.log(model.p)+(1-model.p)*np.log(1-model.p))
    policies=[];values=success[4]
    for i in reversed(range(4)):
        future=model.expect(values,i)
        a=np.array([np.full(len(model.codes[i]),i),
            model.choose(np.broadcast_to(profile,(len(model.codes[i]),model.d)),i),
            model.choose(-model.expect(entropy[i+1],i),i),
            model.choose(model.expect(success[i+1],i),i),
            model.choose(future,i)])
        policies.insert(0,a);values=future[np.arange(len(future)),a[4]]
    result=np.broadcast_to(success[4],(5,len(success[4]))).copy()
    for i in reversed(range(4)):
        result=np.array([model.expect(v,i)[np.arange(len(model.codes[i])),policies[i][m]] for m,v in enumerate(result)])
    rates=result[:,0]
    assert rates[4]>=rates[:4].max()-1e-10
    mass=np.prod(np.where(model.bits,model.p,1-model.p),axis=1)
    summary=dict(rates=rates.tolist(),no_question=float(success[0][0]),no_buy=float(mass[accept[:,-1]].sum()),
                 multi_acceptable=float(mass[(accept[:,:-1].sum(1)>1)].sum()))
    if details:
        state=np.zeros((5,len(model.bits)),int)
        for step in range(4):
            q=policies[step][np.arange(5)[:,None],state]
            y=model.bits[np.arange(len(model.bits))[None,:],q]
            state=model.children[step][state,q,y]
        choice=probs[4].argmax(1)[state]
        hit=accept[np.arange(len(accept))[None,:],choice]
        assert np.allclose(hit@mass,rates,atol=1e-12)
        summary['hit_by_profile']=hit.astype(int).tolist()
        summary['mass']=mass.tolist()
        summary['choice_by_profile']=choice.tolist()
        fixed=(success[4]*model.prob[4]).reshape(len(model.fixed_sets),16).sum(1)
        summary['fixed_sets']=fixed.tolist()
    return summary

def grid():
    weights={
        'equal':[1]*8,
        'care_material':[1,1,1,2,2,1,1,1],
        'style':[2,2,2,1,1,1,1,1],
        'context_fit':[1,1,1,1,1,2,2,2],
    }
    distributions={'assigned':P0,'reversed':1-P0,'uniform':np.full(9,.5),
                   'uncertain_context':np.array([.15,.2,.85,.25,.7,.5,.5,.5,.5]),
                   'uncertain_style':np.array([.5,.5,.5,.35,.2,.6,.15,.2,.8])}
    out=[]
    for ans,(pn,p),(wn,w),cut in product(['acceptable','best'],distributions.items(),weights.items(),[.35,.45,.55,.65]):
        out.append(dict(id=f'{ans}-{pn}-{wn}-{cut}',d=9,menu_size=8,answer=ans,prior=p.tolist(),prior_name=pn,
                        weights=w,weight_name=wn,threshold=cut,price_penalty=.05,hard=[]))
    return out

def explore():
    OUT.mkdir(exist_ok=True)
    rows=source_rows()
    dev=[r for r in rows if (r['gender'],r['category'],r['split'])==('Women','Kurtas','development')]
    labels=labels_for(dev);byid={r['product_id']:r for r in dev}
    selected=menus(dev,20261105201,8,24)
    configs=grid()
    protocol=dict(scope='Development-only exploratory synthetic task construction. All catalogue response simulations are calculated, not observed human/LLM data.',
         methods=METHODS,budget=4,source_sha=hashlib.sha256(prior.SOURCE.read_bytes()).hexdigest(),
         split='Women/Kurtas development',menus=selected,labels=labels,configs=configs,
         target='Strict adjacent ordering DV1 > DecisionSetIG > ProfileIG > Fixed. Also report DV4. Prefer >2 pp adjacent development margins and avoid trivial all-buy/all-refusal cells.',
         planned_confirmation='Freeze the chosen configuration and methods before evaluating fresh menus. Report the original Women/Kurtas test pool as a reused catalogue pool; Men/Kurtas and Women/Dresses test products provide previously untested category transfer.',
         result_selection='Every attempted grid cell is kept. The declared simulated population and objective define a conditional task, not a general population claim.')
    path=OUT/'开发探索设计.json'
    if path.exists():assert json.loads(path.read_text('utf8'))==json.loads(json.dumps(protocol))
    else:prior.dump(path,protocol)
    models={};parts={};records=[];start=time.monotonic()
    resultpath=OUT/'开发探索结果.jsonl'
    done={json.loads(s)['id']:json.loads(s) for s in resultpath.read_text('utf8').splitlines()} if resultpath.exists() else {}
    with resultpath.open('a',encoding='utf8') as stream:
        for j,c in enumerate(configs):
            if c['id'] in done:records.append(done[c['id']]);continue
            key=c['prior_name']
            if key not in models:
                models[key]=prior.Belief(9,np.array(c['prior']))
                parts[key]=[components([byid[i] for i in ids],labels,models[key]) for ids in selected]
            result=[evaluate(models[key],signatures(a,b,c)) for a,b in parts[key]]
            average=np.mean([r['rates'] for r in result],0)*100
            gaps=np.array([average[3]-average[2],average[2]-average[1],average[1]-average[0]])
            entry=dict(id=c['id'],rates=average.tolist(),adjacent_gaps=gaps.tolist(),minimum_gap=float(gaps.min()),
                       no_buy=100*np.mean([r['no_buy'] for r in result]),no_question=100*np.mean([r['no_question'] for r in result]),
                       multi_acceptable=100*np.mean([r['multi_acceptable'] for r in result]),per_menu=result)
            stream.write(json.dumps(entry,ensure_ascii=False)+'\n');stream.flush();records.append(entry)
            if (j+1)%40==0:
                top=sorted(records,key=lambda r:r['minimum_gap'],reverse=True)[:2]
                print('done',j+1,'seconds',round(time.monotonic()-start),'leaders',[(r['id'],np.round(r['rates'],2).tolist(),round(r['minimum_gap'],2)) for r in top],flush=True)
    best=sorted(records,key=lambda r:r['minimum_gap'],reverse=True)
    prior.dump(OUT/'开发探索排序.json',[{k:v for k,v in r.items() if k!='per_menu'} for r in best])
    print('top',[(r['id'],np.round(r['rates'],2).tolist(),round(r['minimum_gap'],2)) for r in best[:8]],flush=True)

if __name__=='__main__':explore()
