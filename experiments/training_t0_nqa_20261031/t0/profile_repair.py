"""Eight stored-state cProfile calls; no acquisition or fitting."""
import cProfile,pstats,json,time
from .bootstrap import ROOT
from .profile_existing import FusedOriginal
import numpy as np

def main():
    items=json.loads((ROOT/'artifacts/selected_public_states.json').read_text());last={}
    for r in items:last[r['audit']['existing_world_index']]=r
    assert len(last)<=8
    out=[]
    for item in last.values():
        o=item['observation'];s=FusedOriginal(o['public'],o['calibration'],o['R']);s.counts=np.array(o['counts'],dtype=np.int64);s.forced=np.array(o['forced_counts'],dtype=np.int64);s.types=[r[:] for r in o['types']];s.t=o['online']
        pr=cProfile.Profile(timer=time.process_time);pr.runcall(s._update);st=pstats.Stats(pr)
        names=['_update','_estimate','solve_allocation','minimum','inner','linprog']
        values={name:[{'file':k[0].split('/')[-1],'line':k[1],'calls':v[1],'own_cpu':v[2],'cumulative_cpu':v[3]} for k,v in st.stats.items() if k[2]==name] for name in names}
        out.append({'audit':item['audit'],'profile':values})
    obj={'calls':len(out),'records':out,'new_worlds':0,'new_actions':0,'training_updates':0,'scope':'intrusive cProfile; minimum() is the frozen radial-repair-only nested function'}
    (ROOT/'artifacts/repair_profile.json').write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'calls':len(out),'minimum_calls':[r['profile']['minimum'][0]['calls'] for r in out],
        'radial_cumulative_over_inner_cumulative':[sum(x['cumulative_cpu'] for x in r['profile']['minimum'])/sum(x['cumulative_cpu'] for x in r['profile']['inner']) for r in out]}))
if __name__=='__main__':main()
