"""Final receipt and public staging only; no scientific/confirmation execution."""
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from t1d.integrity import digest,verify,history_check


def main():
    source=verify();r=json.loads((ROOT/'RESULTS.json').read_text());v=json.loads((ROOT/'VALIDATION.json').read_text())
    ex=json.loads((ROOT/'artifacts/execution.json').read_text())
    required=['T1D_PROTOCOL.md','POLICY_SEMANTICS_AND_SOURCE_AUDIT.md','NONUNIFORM_ALLOCATION_ABLATION.md',
              'CROSS_BUDGET_EVALUATION.md','PAIRED_STATISTICAL_REPORT.md','COMPUTATIONAL_COST.md','WWW_CONTRIBUTION_ASSESSMENT.md','FINAL_DECISION.md']
    assert all((ROOT/n).is_file() for n in required)
    pub={}
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(x in rel.parts for x in ['artifacts','fixtures','__pycache__']) or p.name=='FINAL_RECEIPT.json' or p.suffix=='.pyc':continue
        pub[str(rel)]=digest(p)
    artifacts={str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'artifacts').rglob('*')) if p.is_file()}
    fixtures={str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'audit/fixtures').rglob('*')) if p.is_file()}
    receipt={'status':'COMPLETED_BOUNDED_DEVELOPMENT' if ex['status']=='completed' and v['passed'] else 'BOUNDED_DEVELOPMENT_INCOMPLETE_OR_INVALID',
        'base_commit':'3186587','branch':'training/t1d_nonuniform_robustness','decisions':r['decisions'],
        'public_files':pub,'artifact_files':artifacts,'engineering_fixture_files':fixtures,
        'public_files_excluding_receipt':len(pub),'required_reports':required,
        'source_preexecution_commitment':source,'full_historical_public_preservation':history_check(),
        'planned_independent_worlds':96,'planned_paths':v['planned_paths'],'finished_paths':v['finished_paths'],
        'invalid_check_examples':v['errors'],'uncompleted_planned_paths':v['uncompleted_planned_paths'],
        'terminal_certificates':v['certificates'],'wrong_certificates':v['wrong_certificates'],
        'costs_including_partial':ex['costs_including_partial'],'retries':ex['retries'],
        'training_updates':0,'model_calls':0,'rl_training_rollouts':0,'confirmation_worlds':0,'confirmation_entropy_created':False,
        'automatic_next_stage':False,'privacy':'artifacts/private and literal fixtures git-ignored; old private and reserved confirmation seeds unopened',
        'T1c_defect_rewritten':False,'verification_scope':'source/integrity and descriptive statistical checks; no independent efficacy rerun or proof assistant certification'}
    (ROOT/'FINAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    repo=ROOT.parents[1];allowed=[str((ROOT/n).relative_to(repo)) for n in pub]+[str((ROOT/'FINAL_RECEIPT.json').relative_to(repo))]
    subprocess.run(['git','add','--',*allowed],cwd=repo,check=True)
    subprocess.run(['git','diff','--cached','--check'],cwd=repo,check=True)
    staged=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=repo).decode().strip('\0').split('\0')
    assert set(staged)==set(allowed)
    assert all('/artifacts/' not in p and '/fixtures/' not in p for p in staged)
    print(json.dumps({'sealed_public_files':len(staged),'local_only_artifacts':len(artifacts),'source_verified':source,'commit_created':False}))


if __name__=='__main__':main()
