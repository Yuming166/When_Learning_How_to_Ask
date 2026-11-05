"""Controlled catalogue pilot. All tastes and exact replies are synthetic, not collected shoppers."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,random
import numpy as np

ROOT=Path(__file__).resolve().parent
SOURCE=Path('C:/Users/22797/Documents/xwechat_files/wxid_x1dbwm93ncbz22_0ccc/msg/file/2026-11/Myntra_Structured_Catalogue_v01.zip')
FIELDS=['sleeve_length','pattern','neckline','fabric','wash_care','budget','occasion','garment_length','shape']
SEEDS=[20261105101,20261105102]
P=np.array([.5,.35,.6,.45,.4,.5,.65,.35,.55])
NAMES=['Fixed','ProfileIG','DecisionSetIG','DV1','DV4','MenuFixed','TrainedFixed']

def dump(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')

def data():
    with ZipFile(SOURCE) as z:
        name=next(s for s in z.namelist() if s.endswith('/catalogue_strict.jsonl'))
        raw=z.read(name);rows=[json.loads(l) for l in raw.decode('utf-8-sig').splitlines()]
    rows=[r for r in rows if r['gender']=='Women' and r['category']=='Kurtas'
          and all(r['attributes'].get(k,{}).get('status')=='reported' for k in FIELDS if k!='budget')]
    rows.sort(key=lambda r:r['product_id'])
    dev=[r for r in rows if r['split']=='development']
    labels={f:[v for v,n in sorted(Counter(r['attributes'][f]['value'] for r in dev).items(),key=lambda x:(-x[1],x[0]))[:2]]
            for f in FIELDS if f!='budget'}
    labels['budget']=np.quantile([float(r['source_price']['minimum']) for r in dev],[.5,.75]).tolist()
    menus=[]
    for split in ['development','validation_reserved','test_reserved']:
        pool=[r for r in rows if r['split']==split];seen=set()
        for seed in SEEDS:
            rng=random.Random(seed+len(split))
            for k in range(48):
                while True:
                    sample=tuple(sorted(r['product_id'] for r in rng.sample(pool,8)))
                    if sample not in seen:
                        seen.add(sample);break
                menus.append(dict(split=split,seed=seed,items=sample))
    protocol=dict(source=str(SOURCE),source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
       catalogue_sha=hashlib.sha256(raw).hexdigest(),fields=FIELDS,labels=labels,budget=4,menus=menus,
       dimension_settings=[6,9],prior_scenarios={'assigned':P.tolist(),'reversed':(1-P).tolist(),'uniform':[.5]*9},
       interaction='One perfect binary answer reveals which of two declared labels the synthetic customer prefers. At most four questions.',
       utility='Among items within the disclosed hard price ceiling, mean attribute matches minus 0.05 times price/ceiling. NO_BUY has utility 0.5. All tied maximizers count as correct.',
       methods=NAMES,main='Compare 6 and 9 unknown tastes on the same eight-item menus, always four queries. Report every cell and both one-step DV and four-step DV.',
       scope='Synthetic taste and response model, exact enumeration of its 64/512 states. This is a new catalogue diagnostic, not a reproduction of the attached structured-disclosure experiment or LLM/human evidence.')
    file=ROOT/'固定四题_扩展偏好设计.json'
    if file.exists():assert json.loads(file.read_text('utf-8'))==json.loads(json.dumps(protocol))
    else:dump(file,protocol)
    return rows,protocol

class Belief:
    def __init__(self,d,p):
        self.d=d;self.p=p;self.bits=np.array(list(product((0,1),repeat=d)))
        self.base=3**np.arange(d-1,-1,-1);self.codes=[];self.masks=[];self.prob=[];self.subsets=[]
        for n in range(5):
            codes=[];masks=[];probs=[];subsets=[]
            for subset in combinations(range(d),n):
                for values in product((0,1),repeat=n):
                    codes.append(sum((v+1)*self.base[j] for j,v in zip(subset,values)))
                    masks.append(sum(1<<j for j in subset))
                    probs.append(np.prod([p[j] if v else 1-p[j] for j,v in zip(subset,values)]))
                    subsets.append(subset)
            self.codes.append(np.array(codes));self.masks.append(np.array(masks));self.prob.append(np.array(probs));self.subsets.append(subsets)
        self.children=[];self.unasked=[]
        for n in range(4):
            lookup={code:i for i,code in enumerate(self.codes[n+1])};child=np.zeros((len(self.codes[n]),d,2),int)
            unknown=(self.masks[n][:,None]&(1<<np.arange(d)))==0
            for i,code in enumerate(self.codes[n]):
                for j in range(d):
                    if unknown[i,j]:
                        child[i,j]=[lookup[code+self.base[j]],lookup[code+2*self.base[j]]]
            self.children.append(child);self.unasked.append(unknown)
        self.fixed_sets=list(combinations(range(d),4))

    def marginals(self,values):
        a=values.reshape((2,)*self.d+(-1,)).astype(float)
        for j in range(self.d):
            zero=np.take(a,0,axis=j);one=np.take(a,1,axis=j)
            a=np.stack(((1-self.p[j])*zero+self.p[j]*one,zero,one),axis=j)
        a=a.reshape(3**self.d,-1)
        return [a[c] for c in self.codes]

    def expect(self,values,n):
        return (1-self.p)*values[self.children[n][:,:,0]]+self.p*values[self.children[n][:,:,1]]

    def choose(self,scores,n):
        scores=np.where(self.unasked[n],scores,-np.inf)
        return (scores>=scores.max(1,keepdims=True)-1e-12).argmax(1)

    def evaluate(self,signature):
        accept=(signature[:,None]&(1<<np.arange(9)))!=0
        acceptance=self.marginals(accept)
        success=[m.max(1) for m in acceptance]
        distinct=np.unique(signature);probs=self.marginals(signature[:,None]==distinct)
        ent=[-(v*np.log(np.maximum(v,1e-300))).sum(1) for v in probs]
        profile_entropy=-(self.p*np.log(self.p)+(1-self.p)*np.log(1-self.p))
        policies=[None]*4;best=success[4]
        for n in reversed(range(4)):
            future=self.expect(best,n)
            actions=[np.full(len(self.codes[n]),n),
                     self.choose(np.broadcast_to(profile_entropy,(len(self.codes[n]),self.d)),n),
                     self.choose(-self.expect(ent[n+1],n),n),
                     self.choose(self.expect(success[n+1],n),n),
                     self.choose(future,n)]
            policies[n]=np.array(actions)
            best=future[np.arange(len(future)),actions[-1]]
        result=success[4][None,:].repeat(5,0)
        for n in reversed(range(4)):
            nxt=[]
            for m in range(5):
                e=self.expect(result[m],n);q=policies[n][m]
                nxt.append(e[np.arange(len(q)),q])
            result=np.array(nxt)
        fixed=(success[4]*self.prob[4]).reshape(len(self.fixed_sets),16).sum(1)
        assert best[0]>=fixed.max()-1e-10
        assert best[0]>=result[:,0].max()-1e-10
        assert np.isclose(fixed[0],result[0,0])
        states=np.zeros((5,len(self.bits)),int)
        for n in range(4):
            question=policies[n][np.arange(5)[:,None],states]
            replies=self.bits[np.arange(len(self.bits))[None,:],question]
            states=self.children[n][states,question,replies]
        decision=acceptance[4].argmax(1)[states]
        correct=(signature[None,:]&(1<<decision))!=0
        mass=np.prod(np.where(self.bits,self.p,1-self.p),axis=1)
        assert np.allclose(correct@mass,result[:,0],atol=1e-12)
        purchase=(signature&256)==0
        alternate={}
        for name,prior in [('assigned',P[:self.d]),('reversed',1-P[:self.d]),('uniform',np.full(self.d,.5))]:
            actual_mass=np.prod(np.where(self.bits,prior,1-prior),axis=1)
            alternate[name]=(correct@actual_mass).tolist()
        return result[:,0],fixed,dict(
            purchase_mass=float(mass[purchase].sum()),
            purchase_correct=(correct[:,purchase]@mass[purchase]).tolist(),
            no_buy_correct=(correct[:,~purchase]@mass[~purchase]).tolist(),
            alternate_population=alternate)

def signatures(rows,labels,model):
    prefs=model.bits;price=np.array([float(r['source_price']['minimum']) for r in rows])
    ceiling=np.array(labels['budget'])[prefs[:,5]]
    utility=np.zeros((len(prefs),8));count=0
    for j,key in enumerate(FIELDS[:model.d]):
        if key=='budget':continue
        choices=np.array(labels[key])[prefs[:,j]]
        values=np.array([r['attributes'][key]['value'] for r in rows])
        utility+=(choices[:,None]==values[None,:]);count+=1
    utility=utility/count-.05*price[None,:]/ceiling[:,None]
    utility=np.where(price[None,:]<=ceiling[:,None],utility,-np.inf)
    utility=np.column_stack((utility,np.full(len(prefs),.5)))
    return (np.isclose(utility,utility.max(1,keepdims=True),rtol=0,atol=1e-12)@(1<<np.arange(9))).astype(int)

def run():
    rows,protocol=data();byid={r['product_id']:r for r in rows};output=[]
    for prior,p in protocol['prior_scenarios'].items():
        for d in protocol['dimension_settings']:
            model=Belief(d,np.array(p[:d]));records=[]
            mass=np.prod(np.where(model.bits,np.array(p[:d]),1-np.array(p[:d])),axis=1)
            for menu in protocol['menus']:
                sig=signatures([byid[x] for x in menu['items']],protocol['labels'],model)
                scores,fixed,classes=model.evaluate(sig)
                records.append(dict(**menu,accuracy=scores.tolist(),fixed_sets=fixed.tolist(),classes=classes,no_buy=float(mass[sig==256].sum()),
                    no_question=float((mass[:,None]*((sig[:,None]&(1<<np.arange(9)))!=0)).sum(0).max())))
            dev=np.mean([r['fixed_sets'] for r in records if r['split']=='development'],0)
            selected=int(np.flatnonzero(dev>=dev.max()-1e-12)[0])
            for r in records:r['accuracy']+=[max(r['fixed_sets']),r['fixed_sets'][selected]]
            summary={}
            for split in ['development','validation_reserved','test_reserved']:
                group=[r for r in records if r['split']==split]
                buy=sum(r['classes']['purchase_mass'] for r in group)
                summary[split]=dict(accuracy=(np.mean([r['accuracy'] for r in group],0)*100).tolist(),
                    no_buy=100*np.mean([r['no_buy'] for r in group]),no_question=100*np.mean([r['no_question'] for r in group]),
                    purchase_correct=(np.sum([r['classes']['purchase_correct'] for r in group],0)*100/buy).tolist(),
                    no_buy_correct=(np.sum([r['classes']['no_buy_correct'] for r in group],0)*100/(len(group)-buy)).tolist(),
                    alternate_population={name:(100*np.mean([r['classes']['alternate_population'][name] for r in group],0)).tolist() for name in protocol['prior_scenarios']})
            output.append(dict(prior=prior,dimensions=d,trained_fixed_fields=[FIELDS[j] for j in model.fixed_sets[selected]],summary=summary,menus=records))
            print(prior,d,summary['test_reserved'],flush=True)
    intervals={};rng=np.random.default_rng(20261105103)
    for prior in protocol['prior_scenarios']:
        pairs={r['dimensions']:[x for x in r['menus'] if x['split']=='test_reserved'] for r in output if r['prior']==prior}
        assert [r['items'] for r in pairs[6]]==[r['items'] for r in pairs[9]]
        a=np.array([r['accuracy'] for r in pairs[6]])
        b=np.array([r['accuracy'] for r in pairs[9]])
        contrasts=100*np.column_stack([b[:,4]-b[:,2],(b[:,4]-b[:,2])-(a[:,4]-a[:,2]),b[:,3]-b[:,2]])
        sampled=[]
        for _ in range(50):
            ix=np.hstack([rng.integers(j*48,(j+1)*48,size=(100,48)) for j in range(2)])
            sampled.extend(contrasts[ix].mean(1))
        intervals[prior]=np.percentile(sampled,[2.5,97.5],axis=0).T.tolist()
    dump(ROOT/'固定四题_扩展偏好结果.json',dict(protocol_sha=hashlib.sha256((ROOT/'固定四题_扩展偏好设计.json').read_bytes()).hexdigest(),
         code_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),methods=NAMES,results=output,
         menu_conditional_intervals={'labels':['nine DV4 minus DSIG','increase in DV4 minus DSIG','nine DV1 minus DSIG'],
         'scope':'Paired menus resampled within seed; catalogue, labels, known synthetic population and preferences held fixed.',
         'values':intervals}))

if __name__=='__main__':run()
