import math

def worlds(split,cfg):
    if split in ('train','development'):
        panels=[{'name':'ID','partitions':[[1,3],[2,2],[4]],'rates':[[.85,.60],[.75,.60]],'alphas':[0,3],
                 'replicates':4 if split=='train' else 2}]
    elif split=='test':panels=cfg['test_panels']
    else:raise ValueError('Not a declared complete-world split')
    result=[];cell=0
    for panel in panels:
        for part in panel['partitions']:
            for p,q in panel['rates']:
                for alpha in panel['alphas']:
                    for rep in range(panel['replicates']):
                        result.append({'split':split,'panel':panel['name'],'partition':part,'p':p,'q':q,'alpha':alpha,
                          'R':16,'M':math.ceil(alpha*16),'s':.8,'eta':.05,'cell':cell,'replicate':rep,
                          'index':1750000+100*cell+rep,'channel':'iid','protocol':'fixed_budget',
                          'scenario':'T3 independent development pilot; not confirmatory', 'stop_mode':'terminal_certification_only'})
                    cell+=1
    return sorted(result,key=lambda j:(j['replicate'],j['panel'],j['cell']))

def jobs(split,cfg):
    result=[];seen={}
    for w in worlds(split,cfg):
        budgets=[32]
        if split=='test':
            n=seen.get(w['panel'],0);seen[w['panel']]=n+1
            if n<12:budgets=[16,32,48,64]
        for B in budgets:result.append({**w,'budget':B,'online_cap':B,'check_every':B,'milestones':[B]})
    return result
