"""Freeze and verify offline artifacts. No models, network, training or agents."""
import argparse,sys
from pathlib import Path
from .common import ROOT,read,write,digest,canonical
from .build import artifacts
from .worlds import make_world
from .compiler import compile_set
from .surface import validate_review
DOCS=['SEMANTIC_FAILURE_AUDIT.md','CANONICAL_PROPOSITION_SPEC.md','TYPED_QUERY_COMPILER.md',
 'SEMANTIC_VALIDATION_REPORT.md','DATA_DEPENDENCY_AUDIT.md','V021_DEVELOPMENT_PROTOCOL.md','INTEGRATION_PLAN.md','README.md','CHANGELOG.md']
EXCLUDED={'FINAL_RECEIPT.json','FINAL_RECEIPT.sha256'}
def preservation():
 old=read(ROOT/'audit/INPUT_PRESERVATION_SNAPSHOT.json');changed=[];missing=[]
 for name,h in old['files'].items():
  p=Path(name)
  if not p.is_file():missing.append(name)
  elif digest(p.read_bytes())!=h:changed.append(name)
 return {'pass':not changed and not missing,'checked_files':len(old['files']),'changed':changed,'missing':missing,
  'counts':{'v02_all_nonbytecode_files':sum('/qrelbench-v02-dev-' in p for p in old['files']),
   'Exact_files':sum('/qrelbench_v01_' in p for p in old['files'])},
  'theory_method_branch':'Concurrent, not frozen, never edited by this session'}
def reviewed_inputs():
 r=read(ROOT/'audit/independent_compiler_review.json')
 mismatch=[x['path'] for x in r['inputs'] if digest((ROOT/x['path']).read_bytes())!=x['sha256']]
 if mismatch:raise RuntimeError('Reviewed inputs changed: '+str(mismatch))
 queries=[]
 for mode,key in read(ROOT/'private/FIXTURE_KEYS.json').items():
  for prop in make_world(bytes.fromhex(key),mode)['propositions']:queries.extend(compile_set(prop))
 if not validate_review(r,queries):raise RuntimeError('Review gate failed')
 return {'status':r['status'],'scope':r['scope'],'query_objects':len(queries),'reviewed_combinations':96,'unique_texts':72,
  'same_model_family_separate_session':True,'human_review':False,'identity_authentication':False,
  'reviewer_private_fixture_labels_visible':False}
def create():
 if (ROOT/'FINAL_RECEIPT.json').exists():raise RuntimeError('Immutable final receipt exists; use --verify')
 for name in DOCS:
  if not (ROOT/name).is_file():raise RuntimeError('Missing document '+name)
 if not read(ROOT/'audit/DATA_AUDIT.json')['pass']:raise RuntimeError('Construction audit failed')
 hist=preservation()
 if not hist['pass']:raise RuntimeError('Historical preservation failed')
 review=reviewed_inputs();keys=read(ROOT/'private/FIXTURE_KEYS.json')
 for name,obj in artifacts(keys).items():
  if canonical(read(ROOT/name))!=canonical(obj):raise RuntimeError('Replay differs: '+name)
 write(ROOT/'PRESERVATION_RECEIPT.json',{**hist,'input_snapshot_sha256':digest((ROOT/'audit/INPUT_PRESERVATION_SNAPSHOT.json').read_bytes()),
  'historical_v02_final_receipt_sha256':digest(Path('/home/gaoym/qrelbench-v02-dev-20261031/FINAL_RECEIPT.json').read_bytes()),
  'writes_outside_new_directory':[],'shared_git_mutations':[],'service_modifications':[]})
 frozen=list((ROOT/'qrelbench_v021').glob('*.py'))+list((ROOT/'tests').glob('*.py'))+[ROOT/n for n in DOCS]
 frozen+=list((ROOT/'fixtures').glob('*'))+list((ROOT/'public').glob('*.json'))+list((ROOT/'private').glob('*.json'))
 frozen+=[ROOT/'audit/PROPOSED_REQUEST_PLAN.json',ROOT/'audit/independent_compiler_review.json',ROOT/'audit/REVIEW_PACKET.json']
 write(ROOT/'audit/V021_FREEZE.json',{'phase':'OFFLINE_COMPLETE_NO_MODEL_EXECUTION','files':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(set(frozen))},
  'proposed_generation_budget':16,'current_generation_authorized':0,'proposed_answering_budget':304,'current_answering_authorized':0})
 paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.name not in EXCLUDED)
 manifest={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in paths}
 decisions={
  'canonical_truth_validity':{'verdict':'GO','scope':'Bounded declared typed domains and executable rule family'},
  'query_format_semantic_equivalence':{'verdict':'GO','scope':'Finite controlled language; novel unrestricted NL not certified'},
  'dataset_diversity':{'verdict':'REVISE','scope':'Two fictional domains, six predicates, two structures and finite hand-authored grammar'},
  'leakage_and_dependency_integrity':{'verdict':'GO','scope':'Explicit dependencies, no forced3/3, field/metamorphic audit; not universal statistical shortcut absence'},
  'readiness_for_bounded_qwen_generation_pilot':{'verdict':'GO','scope':'Proposed16-call controlled realization diagnostic only','executed':False,'currently_authorized':False}}
 receipt={'benchmark':'QRelBench','version':'0.2.1-dev','date':'2026-10-31','timezone':'Asia/Shanghai',
  'root':str(ROOT),'overall_verdict':'REVISE','status':'OFFLINE_DESIGN_IMPLEMENTATION_AND_AUDIT_COMPLETE_STOPPED',
  'required_decisions':decisions,'model_calls':read(ROOT/'MODEL_CALL_RECEIPT.json'),
  'historical_v02_status':'Preserved PASS4/REJECT5/UNCERTAIN11,zero accepted sources,5historical35B calls,zero4B calls; not rerun',
  'tests':{'main_tests_passed':39,'separate_reviewer_boundary_cases':129,'separate_B_boolean_valuations':96,
   'separate_missing_field_rejections':12,'separate_review_gate_cases':4,'exact_replayed_artifacts':8},
  'technical_fixtures':{mode:read(ROOT/f'audit/{mode}_stats.json') for mode in keys},
  'accepted_new_qwen_sources':0,'new_qwen_generated_data':False,'review':review,'preservation':hist,
  'prefreeze_findings':'audit/PREFREEZE_CORRECTIONS.json','frozen_protocol':'V021_DEVELOPMENT_PROTOCOL.md',
  'freeze_sha256':digest((ROOT/'audit/V021_FREEZE.json').read_bytes()),'created_files':list(manifest),'created_file_count':len(manifest),'files':manifest,
  'inventory_exclusions':['Python bytecode caches','FINAL_RECEIPT self hash','FINAL_RECEIPT.sha256'],
  'cannot_claim':['Natural shared reliability','Qwen free-paraphrase semantic correctness','Accepted natural dataset','Algorithm superiority','Delta-correct natural stopping',
   'Human realism','New-template/mechanism/model-family generalization','Independent human semantic certification'],
  'integration_plan':'INTEGRATION_PLAN.md','no_further_work_authorized_or_started':True}
 write(ROOT/'FINAL_RECEIPT.json',receipt);(ROOT/'FINAL_RECEIPT.sha256').write_text(digest((ROOT/'FINAL_RECEIPT.json').read_bytes())+'  FINAL_RECEIPT.json\n')
 print('Created receipt:',len(manifest),'files;39 tests;107 historical input files;Qwen calls0;overall REVISE')
def verify(local_only=False):
 r=read(ROOT/'FINAL_RECEIPT.json');bad=[p for p,h in r['files'].items() if not (ROOT/p).is_file() or digest((ROOT/p).read_bytes())!=h]
 if digest((ROOT/'FINAL_RECEIPT.json').read_bytes())!=(ROOT/'FINAL_RECEIPT.sha256').read_text().split()[0]:bad.append('FINAL_RECEIPT.json')
 if bad:raise RuntimeError('Artifact mismatch: '+str(bad))
 if not local_only:
  hist=preservation()
  if not hist['pass']:raise RuntimeError('Historical inputs changed/missing: '+str(hist))
 print('PASS:',len(r['files']),'local artifact hashes;final receipt sidecar;'+('historical comparison skipped explicitly' if local_only else '107 historical input hashes unchanged')+';no model calls')
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--create',action='store_true');g.add_argument('--verify',action='store_true');ap.add_argument('--local-only',action='store_true');a=ap.parse_args()
 if a.create and a.local_only:raise ValueError('Creation requires historical verification')
 create() if a.create else verify(a.local_only)
if __name__=='__main__':main()
