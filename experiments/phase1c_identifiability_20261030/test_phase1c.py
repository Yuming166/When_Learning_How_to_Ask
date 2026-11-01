import itertools
import json
import unittest
from fractions import Fraction as F
from design import ROOT,read_jsonl,parse_answer
from logic_audit import ground,closure,parse,opposite,positive_text
from identifiability import joint,tv,agreement
from policies import choose


class Phase1cTests(unittest.TestCase):
    def test_hard_negative_is_not_failure(self):
        row={'triples':{'triple1':{'representation':'("a" "is" "red" "+")'}},'rules':{
          'rule1':{'representation':'((("someone" "is" "blue" "~")) -> ("someone" "is" "green" "+"))'}}}
        f,r=ground(row);p,_=closure(f,r)
        self.assertNotIn(('a','is','green','+'),p)
        row['triples']['triple2']={'representation':'("a" "is" "blue" "-")'}
        f,r=ground(row);p,_=closure(f,r)
        self.assertIn(('a','is','green','+'),p)
    def test_relations_and_transitive_chain(self):
        row={'triples':{'triple1':{'representation':'("a" "sees" "b" "+")'}},'rules':{
          'rule1':{'representation':'((("someone" "sees" "b" "+")) -> ("someone" "is" "red" "+"))'},
          'rule2':{'representation':'((("someone" "is" "red" "+")) -> ("someone" "is" "blue" "-"))'}}}
        f,r=ground(row);p,d=closure(f,r)
        self.assertEqual(d[('a','is','blue','-')],2)
        self.assertEqual(p[('a','is','blue','-')],{'triple1','rule1','rule2'})
        self.assertNotIn(('b','is','red','+'),p)
    def test_selected_worlds_rederive_and_not_complements(self):
        worlds=read_jsonl(ROOT/'selected_worlds.jsonl');self.assertEqual(len(worlds),8)
        for w in worlds:
            f,r=ground(w);p,d=closure(f,r);seen=set()
            self.assertEqual(sum(t['theta'] for t in w['targets']),3)
            self.assertGreaterEqual(sum(t['verified_depth']>0 for t in w['targets']),2)
            for t in w['targets']:
                lit=tuple(t['literal']);self.assertEqual(lit[3],'+');self.assertNotIn(lit,seen);seen.add(lit)
                self.assertEqual(lit in p,t['theta']);self.assertEqual(opposite(lit) in p,not t['theta'])
                actual=lit if t['theta'] else opposite(lit)
                # Remove all facts outside a target's certificate; its label still has a proof.
                sub={a:fid for a,fid in f.items() if fid in t['fact_support']}
                pp,_=closure(sub,r);self.assertIn(actual,pp)
            for a,b in itertools.combinations(w['targets'],2):self.assertFalse(set(a['fact_support'])&set(b['fact_support']))
    def test_requests_repeat_identity_and_evidence_equivalence(self):
        rows=read_jsonl(ROOT/'data/requests.jsonl');self.assertEqual(len(rows),8*6*2*2)
        self.assertEqual(len({r['seed'] for r in rows}),192)
        for pref in {r['preference_id'] for r in rows}:
            rr=[r for r in rows if r['preference_id']==pref]
            self.assertEqual(len({r['evidence_sha256'] for r in rr}),1)
            self.assertEqual(len({r['option_flip'] for r in rr}),1)
            for m in ['A','B']:self.assertEqual(len({r['prompt'] for r in rr if r['format']==m}),1)
            a=next(r['prompt'] for r in rr if r['format']=='A');b=next(r['prompt'] for r in rr if r['format']=='B')
            self.assertEqual(a.split('Exactly one')[0],b.split('Exactly one')[0])
            self.assertEqual(a.split('\n0:')[1],b.split('\n0:')[1])
            for r in rr:self.assertTrue(set(r).isdisjoint({'theta','correct','correct_digit','proof','support'}))
    def test_strict_parser(self):
        self.assertEqual(parse_answer(' 1\n'),1)
        for s in ['10','yes','answer: 0','{"answer":1}','0 or 1','']:self.assertIsNone(parse_answer(s))
    def test_selector_label_canary_and_agreement(self):
        self.assertEqual(choose('g',[{'A':[1,1],'B':[0,1]}]),'A')
        self.assertEqual(choose('g',[{'A':[None,None],'B':[0,0]}]),'B')
        with self.assertRaises(AssertionError):choose('g',[{'A':[1,1],'B':[0,1],'theta':1}])
    def test_exact_identifiability_and_persistent_failure(self):
        p,q=F(3,4),F(3,5)
        self.assertEqual(tv(joint('AB',p,q),joint('AB',p,q,good='B')),0)
        self.assertEqual(tv(joint('AABB',p,q),joint('AABB',p,q,good='B')),F(21,200))
        self.assertEqual(tv(joint('AABB',p,q,persistent=True),joint('AABB',p,q,good='B',persistent=True)),0)
        self.assertEqual(agreement(p)-agreement(q),2*(p-q)*(p+q-1))
    def test_classification_is_not_unknown_collapsing(self):
        x=json.loads((ROOT/'proofwriter_structure.json').read_text());self.assertTrue(x['structural_gate'])
        for stats in x['summary'].values():
            self.assertEqual(stats['label_mismatches'],0);self.assertEqual(stats['complete_implication_mismatch_worlds'],0)
            self.assertEqual(sum(stats['source_'+k] for k in ['True','False','Unknown']),stats['questions'])


if __name__=='__main__':unittest.main()
