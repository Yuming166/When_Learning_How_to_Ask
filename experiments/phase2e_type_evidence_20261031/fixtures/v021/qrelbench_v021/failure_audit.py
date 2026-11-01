"""Evidence-specific regression taxonomy, not a general semantic entailment classifier."""
import re
from .common import ROOT,read,write
TAXONOMY=['proposition_scope_change','truth_vs_textual_mention','entailment_vs_consistency',
 'incorrect_negation_or_undefined_predicate','placeholder_omission','answer_mapping_inconsistency','other_semantic_ambiguity']
def classify(frame):
 text=frame['frame'];low=text.lower();labels=[]
 if '{claim}' not in text:labels+=['proposition_scope_change','placeholder_omission']
 if re.search(r'\bstated\b|\bdoes the policy state\b',low):labels.append('truth_vs_textual_mention')
 if 'consistent with' in low:labels.append('entailment_vs_consistency')
 if frame['status']=='UNCERTAIN' and 'consistent with' not in low:labels.append('other_semantic_ambiguity')
 return sorted(set(labels))
def build():
 data=read(ROOT/'fixtures/v02_frameworks.json');result=[]
 for i,f in enumerate(data['frames']):result.append({'index':i,**f,'taxonomy':classify(f),'historical_disposition_unchanged':True,
  'evidence_level':'unresolved semantic interpretation' if f['status']=='UNCERTAIN' else 'observed task/placeholder or literal-mention mismatch' if f['status']=='REJECT' else 'historically accepted frame only, not a complete accepted source'})
 write(ROOT/'audit/FAILURE_TAXONOMY.json',{'total':20,'historical_counts':{s:sum(r['status']==s for r in result) for s in ['PASS','REJECT','UNCERTAIN']},
  'categories':{k:sum(k in r['taxonomy'] for r in result) for k in TAXONOMY},'records':result,'counts_overlap':True,
  'separate_policy_paraphrase_issue':'active is undefined relative to not suspended; not counted as a framework or observed negation error',
  'mapping_inconsistency':'No observed mapping inconsistency in the raw frames; no completed v0.2 query corpus. Not proof all mappings were semantically valid.'})
if __name__=='__main__':build()
