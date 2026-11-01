"""Offline W1.1 assembly, evidence-integrity checks, and provenance bookkeeping.

Semantic decisions are explicit authored inputs in drafts/ and claims.json.
No network, model, training, or benchmark execution is implemented here.
"""
import csv
import hashlib
import html
import itertools
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / 'w1_averitec_audit_20261101'
LABELS = {'ASSERT_SUPPORT','ASSERT_REFUTE','ATTRIBUTED_ONLY','MIXED','NOT_ADDRESSED'}


def sha(b): return hashlib.sha256(b).hexdigest()
def load(path): return json.loads(path.read_text())
def save(name, data): (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def original(url):
    m=re.match(r'https?://web\.archive\.org/web/[^/]+/(https?://.*)',url)
    return m.group(1) if m else url


def check_parent():
    receipt=load(ROOT/'PARENT_RECEIPT.json')
    assert sha((PARENT/'MANIFEST.sha256').read_bytes())==receipt['manifest_sha256']
    for f in receipt['files']:
        assert sha((PARENT/f['path']).read_bytes())==f['sha256'], f['path']
    return len(receipt['files'])


def evidence_text(path):
    if path.suffix=='.json':
        obj=load(path)
        return obj.get('result',json.dumps(obj,ensure_ascii=False))
    raw=path.read_text()
    if path.suffix=='.html':
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(raw,'html.parser')
        return soup.get_text(' ')+' '+ ' '.join(n.get('content','') for n in soup.find_all('meta'))
    return raw


def norm(text): return ' '.join(html.unescape(text).split())


def csv_write(name, rows, fields):
    with (ROOT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k:('UNKNOWN' if row.get(k) is None else row[k]) for k in fields})


def assemble():
    preserved=check_parent()
    claims=load(ROOT/'claims.json')
    selected=load(PARENT/'selected_claims.json')
    for c,s in zip(claims,selected):
        assert c['case_id']==s['case_id'] and c['original_claim']==s['record']['claim']
        assert c['dataset_reference_label']==s['record']['label'] and not c['target_replaced']
        assert c['Y'] is None and not c['binary_subset_approved']
    assert len(claims)==12
    inventory={r['page_id']:r for r in load(PARENT/'url_inventory.json')}
    old={(r['case_id'],r['page_id']):r for r in load(PARENT/'page_annotations.json')}
    access={r['page_id']:r for r in map(json.loads,(PARENT/'access_log.jsonl').read_text().splitlines())}
    pages=[]; statements=[]; per_source=Counter(); source_text_cache={}
    for fname,key in [('drafts/semantics_01_06.json','pages'),('drafts/semantics_07_12.json','rows')]:
        draft=load(ROOT/fname)
        for i,p in enumerate(draft[key]):
            cid,pid=p['case_id'],p['page_id']; prior=old[(cid,pid)]; inv=inventory[pid]
            assert p['semantic_label'] is None or p['semantic_label'] in LABELS
            assert p['Y'] is None and p.get('historical_semantic_label') is None
            assert p.get('human_signoff') in (False,'PENDING',None)
            ids=[]
            for j,s in enumerate(p['statements']):
                sid=s['statement_id'];ids.append(sid)
                span=s.get('exact_short_evidence_span',s.get('evidence_span'))
                loc=s['evidence_locator']
                if isinstance(loc,dict):
                    efile=loc['w1_file'].split('w1_averitec_audit_20261101/',1)[1]
                    locator=loc.get('page_internal_lines',str(loc))
                else: efile=s['evidence_file']; locator=loc
                source=PARENT/efile
                assert source.exists(),source
                if source not in source_text_cache: source_text_cache[source]=norm(evidence_text(source))
                assert norm(span) in source_text_cache[source], (sid,span)
                # Keep exact quotes only in original authored draft, not duplicate outputs.
                word_group='RADAR_SAME_ARTICLE' if pid in ('P042','P048') else pid
                per_source[word_group]+=len(span.split())
                statements.append({'statement_id':sid,'case_id':cid,'page_id':pid,
                    'record_pointer':f'{fname}#/{key}/{i}/statements/{j}',
                    'speaker':s.get('speaker',s.get('speaker_or_attribution')),
                    'proposition_summary':s.get('proposition',s.get('summary')),
                    'proposition_polarity':s.get('polarity'),
                    'polarity_contract':'For authored proposition records, apply polarity to that proposition only. For summary-only records, the summary already expresses the attributed meaning; do not negate again.',
                    'relation_to_target':s.get('relation_to_frozen_claim',s.get('target_relation')),
                    'publisher_adoption':s['publisher_adoption'],
                    'layer':s.get('layer',s.get('modality','BODY')),
                    'event_time':s.get('event_time'), 'applicable_time':s.get('applicable_time'),
                    'publication_time':s.get('publication_time'), 'update_time':s.get('update_time'),
                    'evidence_file':'../w1_averitec_audit_20261101/'+efile,
                    'evidence_locator':locator,'evidence_file_sha256':sha(source.read_bytes()),
                    'exact_span_verified':True,'human_signoff':'PENDING','Y':None})
            url=inv['url'];u=original(url)
            m=re.match(r'https?://web\.archive\.org/web/(\d{14})',url)
            dates={'publication_time':p.get('publication_time'), 'update_time':p.get('update_time'),
                   'event_time':p.get('event_time'),
                   'statement_time_record_ids':ids,
                   'requested_archive_timestamp':m.group(1) if m else None,
                   'acquired_archive_snapshot_time':None,
                   'publication_or_update_metadata':p.get('time_metadata'),
                   'time_note':p.get('time_notes',p.get('version_note')),
                   'raw_access_started_utc':access[pid]['started_utc'],
                   'browser_crawl_time':'relative crawl information retained in original tool receipt, not converted to invented exact date'}
            if pid=='P051': dates['publication_year_only']=p.get('publication_year')
            alignment=alignment_for(pid,p)
            pages.append({'case_id':cid,'page_id':pid,'dataset_url':url,
                'nominated_nonarchive_url':u,'roles':prior['roles'],
                'semantic_label':p['semantic_label'],'body_semantic_label':p.get('body_semantic_label',p['semantic_label']),
                'metadata_semantic_label':p.get('metadata_semantic_label'),
                'availability':p['availability'],'reason':p['reason'],
                'representation':'inspected frozen W1 nonarchive-URL representation where present; not a live guarantee',
                'historical_semantic_label':None,'time':dates,'comparison':alignment,
                'statement_ids':ids,'source_record_pointer':f'{fname}#/{key}/{i}',
                'reference_only':prior['reference_only'],'W1_page_candidate_preserved':prior['page_candidate'],
                'direct_assertion_candidate_before_human':p['semantic_label'] in ('ASSERT_SUPPORT','ASSERT_REFUTE')
                    and not prior['reference_only'] and alignment['overall'] in ('FULL','CONTEXT_QUALIFIED'),
                'independent_review':'PENDING','binary_subset_approved':False,'Y':None})
    assert all(n<=20 for n in per_source.values()),per_source
    assert len(pages)==len(old) and {(p['case_id'],p['page_id']) for p in pages}==set(old)
    assert len({s['statement_id'] for s in statements})==len(statements)
    pages.sort(key=lambda p:(p['case_id'],p['page_id']))
    save('pages.json',pages);save('statement_index.json',statements)
    csv_write('page_semantics.csv',pages,['case_id','page_id','dataset_url','roles','semantic_label','metadata_semantic_label','availability','reason','binary_subset_approved'])
    csv_write('statement_index.csv',statements,['statement_id','case_id','page_id','speaker','proposition_summary','proposition_polarity','polarity_contract','relation_to_target','publisher_adoption','layer','evidence_file','evidence_locator','record_pointer'])
    graph=make_graph(inventory,pages,statements)
    real=[p for p in pages if p['page_id']!='P002']
    stats={'claims':len(claims),'real_urls':len(real),'metadata_case_rows':len(pages)-len(real),
           'real_url_semantic_labels':dict(Counter(p['semantic_label'] or 'UNOBSERVED' for p in real)),
           'observed_body_labels':sum(p['semantic_label'] is not None for p in real),
           'metadata_only_assertion_leads':sum(p['metadata_semantic_label'] is not None for p in real),
           'statement_records':len(statements),'statements_with_verified_short_spans':len(statements),
           'direct_assertion_pages_including_references':sum(p['semantic_label'] in ('ASSERT_SUPPORT','ASSERT_REFUTE') for p in real),
           'nonreference_direct_assertion_candidates_before_human':sum(p['direct_assertion_candidate_before_human'] for p in real),
           'W1_historical_candidates_preserved':2,'W1_historical_quarantines_preserved':10,
           'newly_approved_binary_pages':0,'human_signoffs':0,'human_review_packets':2,
           'historical_semantic_observations':0,'independently_verified_natural_source_errors':0,
           'new_claims':0,'new_page_requests':0,'model_service_calls':0,'Y_observations':0,
           'preserved_parent_files':preserved,
           'known_nominated_document_identity_groups':len(graph['document_groups']),
           'known_material_lineage_groups':len(graph['material_lineage_groups']),
           'within_claim_page_pairs':len(load(ROOT/'dependency_pairs.json')),
           'within_claim_pair_relationships':dict(Counter(r['relationship'] for r in load(ROOT/'dependency_pairs.json'))),
           'unresolved_cross_lineage_independence':'UNKNOWN_DEPENDENCE; no independent-root count established',
           'decisions':{'representation':'GO_AS_DEVELOPMENT_AUDIT','human_signoff':'PENDING',
                        'natural_error_subset':'NO_GO_IN_FIXED_CORPUS','model_reading':'NO_GO_PENDING_HUMAN_AND_TARGET_FREEZE',
                        'controlled_corruption':'DESIGN_ONLY_PENDING_SEPARATE_DECISION'}}
    save('SUMMARY.json',stats)
    save('CHECKS.json',{'parent_hashes_match':True,'parent_files':preserved,'all_12_original_targets_and_labels_preserved':True,
                       'coverage_case_field_rows':len(pages),'all_Y_null':True,'all_historical_semantics_null':True,
                       'all_approved_binary_false':True,'exact_short_spans_verified':len(statements),
                       'quote_words_by_unique_source':dict(per_source),'new_requests':0})
    make_casebook(claims,pages)
    print(json.dumps(stats,ensure_ascii=False,indent=2))


def alignment_for(pid,p):
    axes={k:'NOT_EVALUABLE' for k in ['entity','relation','value','event_time','geography','units','qualifiers']}
    if p['semantic_label'] is None: return {'overall':'NOT_EVALUABLE','axes':axes,'reference_truth_independently_verified':False}
    axes={k:'MATCH_WITH_CONTEXT' for k in axes}
    overall='FULL'
    if pid in {'P007','P027','P036','P041'}:
        overall='NO_RELEVANT_PROPOSITION';axes={k:'NOT_ADDRESSED' for k in axes}
    elif pid=='P019': overall='PARTIAL';axes['relation']='MISMATCH';axes['event_time']='UNRESOLVED'
    elif pid=='P023': overall='MISMATCH';axes['value']='DIFFERENT_WINDOW';axes['event_time']='MISMATCH'
    elif pid=='P030': overall='DIFFERENT_SCOPED_PROPOSITION';axes['geography']='NARROWER_SPECIFIC_EVENT';axes['qualifiers']='UNRESOLVED'
    elif pid=='P031': overall='PARTIAL_AND_MISMATCH';axes['geography']='MISMATCH_FOR_GP_PASSAGE';axes['relation']='PARTIAL'
    elif pid=='P033': overall='PARTIAL';axes['entity']='SAME_OFFICE_UNRESOLVED';axes['qualifiers']='SINGULAR_PLURAL_UNRESOLVED'
    elif pid in {'P021','P022','P034','P035','P039'}:
        overall='CONTEXT_QUALIFIED';axes['event_time']='CONTEXT_QUALIFIED';axes['qualifiers']='CONTEXT_QUALIFIED'
    elif pid in {'P042','P043','P046','P048'}:
        overall='PARTIAL_MODALITY_AND_TIME_UNRESOLVED';axes['event_time']='UNRESOLVED';axes['relation']='ORDERED_VS_PAID_VS_DENIED_UNRESOLVED'
    elif pid=='P044':overall='DIFFERENT_PROPOSITION';axes['relation']='MISMATCH';axes['value']='NOT_ADDRESSED'
    elif pid=='P051':overall='MISMATCH';axes['event_time']='MISMATCH';axes['value']='DIFFERENT_INTERVAL'
    return {'overall':overall,'axes':axes,'reference_truth_independently_verified':False,
            'publication_date_difference_alone_is_not_mismatch':True}


def make_graph(inventory,pages,statements):
    real={pid:p for pid,p in inventory.items() if pid!='P002'}
    parent={pid:pid for pid in real}
    def find(x):
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    def union(a,b):parent[find(a)]=find(b)
    by_url={}
    for pid,p in real.items():
        u=original(p['url'])
        if u in by_url:union(pid,by_url[u])
        else:by_url[u]=pid
    union('P042','P048') # Explicitly inspected matching article paths; no version-equivalence claim.
    groups={}
    for pid in real:groups.setdefault(find(pid),[]).append(pid)
    groups=[{'group_id':f'D{i:02}','page_ids':sorted(ids),
             'meaning':'nominated document identity only; versions/content and stochastic independence not equated'}
            for i,ids in enumerate(sorted(groups.values(),key=lambda x:min(x)),1)]
    doc={pid:g['group_id'] for g in groups for pid in g['page_ids']}
    nodes=[{'node_id':'URL:'+pid,'kind':'URL_RESOURCE','page_id':pid,'url':p['url']} for pid,p in real.items()]
    nodes += [{'node_id':g['group_id'],'kind':'NOMINATED_DOCUMENT_IDENTITY'} for g in groups]
    edges=[{'from':'URL:'+pid,'to':doc[pid],'relation':'NOMINATES_DOCUMENT','verification':'URL_IDENTITY_OR_OBSERVED_ALIAS_ONLY'} for pid in real]
    for p in pages:
        if p['page_id']=='P002' or (p['semantic_label'] is None and not p['statement_ids']):continue
        rep='REP:'+p['page_id'];nodes.append({'node_id':rep,'kind':'OBSERVED_REPRESENTATION','availability':p['availability']})
        edges.append({'from':rep,'to':doc[p['page_id']],'relation':'REPRESENTATION_OF','verification':'FROZEN_W1_EVIDENCE; HISTORICAL_VERSION_NOT_OBSERVED'})
    for s in statements:
        nodes.append({'node_id':s['statement_id'],'kind':'ATTRIBUTED_STATEMENT','speaker':s['speaker'],'target_relation':s['relation_to_target']})
        edges.append({'from':s['statement_id'],'to':'REP:'+s['page_id'],'relation':'OCCURS_IN','verification':'EXACT_SHORT_SPAN_MATCH','evidence':s['record_pointer']})
    # These are material families; only identical quoted material is collapsed.
    lineages=[
      ('L05_STUDY_SERIES',['P021-S2','P022-S2'],'NAMED_STUDY_SERIES','U.S. Travel Association / Tourism Economics; exact weekly release identity unresolved','SHARED_FAMILY_NOT_IDENTICAL_RANDOM_DRAW'),
      ('L06_PRIMARY_PUBLICATION',['P026-S1','P028-S1','P028-S2'],'CITED_PRIMARY_AUTHORSHIP_CONTEXT','McSweeney primary publication; factchecker also cites other material','COMMON_INPUT_NOT_EQUIVALENT_TOTAL_EVIDENCE'),
      ('L07_NSW_CASES',['07-P031-S1','07-P033-S1','07-P033-S2'],'COMMON_HEALTH_AUTHORITY_CONTEXT','NSW Health case reports; individual records and office identities differ','COMMON_ORIGIN_NOT_IDENTICAL_FACT_REPORT'),
      ('L08_BIDEN_UTTERANCE',['08-P034-S1'],'NAMED_ORIGINAL_UTTERANCE','Biden debate statement; reference P035 explicitly links transcript','OBSERVED_UTTERANCE_WITH_REFERENCE_LINK'),
      ('L08_PEW_CONTEXT',['08-P035-S1','08-P035-S2'],'NAMED_UNFETCHED_POLL','Pew 2018 poll; primary poll not opened','UNFETCHED_UPSTREAM'),
      ('L11_RADAR_AMOUNT',['11-P042-S1','11-P048-S1','11-P046-S1'],'SAME_REPORTED_AMOUNT','Two Radar paths plus SI explicit attribution','KNOWN_SHARED_MATERIAL'),
      ('L11_JOINT_DENIAL',['11-P042-S2','11-P048-S2','11-P046-S2','11-P043-S2'],'SAME_JOINT_STATEMENT','Griffin/Cameron joint denial; intermediaries differ','KNOWN_SHARED_MATERIAL')]
    sids={s['statement_id'] for s in statements}
    material=[]
    for lid,ids,kind,desc,status in lineages:
        assert set(ids)<=sids,(lid,set(ids)-sids)
        nodes.append({'node_id':lid,'kind':'NOMINATED_MATERIAL_LINEAGE','description':desc})
        material.append({'lineage_id':lid,'statement_ids':ids,'kind':kind,'description':desc,
                         'status':status,'stochastic_root_identity':'NOT_IDENTIFIED',
                         'independence_from_other_lineages':'UNKNOWN_DEPENDENCE'})
        for sid in ids:edges.append({'from':sid,'to':lid,'relation':'DERIVES_FROM_OR_USES_NAMED_MATERIAL','verification':status})
    citations=[('P010','P013','CITES_STUDY','browser_01_04/P010.json L67-72'),
               ('P026','P028','LINKS_PRIMARY_PUBLICATION','browser_05_08/batch_02.json P026 L18'),
               ('P035','P034','LINKS_TRANSCRIPT','browser_05_08/batch_04.json P035 L24'),
               ('P039','P037','QUOTES_INACCESSIBLE_ORIGINAL','browser_09_12/references.json Lead Stories L14-25'),
               ('P046','P048','EXPLICIT_REPORT_ATTRIBUTION','browser_09_12/sources1.json SI L82'),
               ('P043','P042','EXPLICIT_REPORT_ATTRIBUTION','browser_09_12/references.json PolitiFact L55,70')]
    for a,b,kind,loc in citations:
        edges.append({'from':'URL:'+a,'to':'URL:'+b,'relation':kind,'verification':'DIRECTLY_OBSERVED_CITATION_NOT_WHOLE_PAGE_EQUIVALENCE','evidence':'../w1_averitec_audit_20261101/'+loc})
    uncertain=[{'from':'URL:P014','to':'URL:P019','relation':'REPORTED_DERIVATION','verification':'SECONDHAND_ONLY','evidence':'Vishvas P016 reports original post linked Mumbai Mirror; original body link unobserved'},
               {'from':'URL:P025','to':'URL:P028','relation':'REPORTED_MISATTRIBUTED_COPY','verification':'SECONDHAND_ONLY','evidence':'P026 describes copy; P025 not readable'},
               {'from':'URL:P015','to':'URL:P014','relation':'CACHED_URL_POINTS_TO_LOGIN_NOT_POST','verification':'TARGET_MISMATCH','merge_allowed':False},
               {'from':'URL:P018','to':'URL:P017','relation':'CACHED_URL_POINTS_TO_LOGIN_NOT_HASHTAG','verification':'TARGET_MISMATCH','merge_allowed':False},
               {'from':'URL:P011','to':'URL:P012','relation':'WWW_VS_NONWWW_RELATED_PATH','verification':'COMMON_IDENTITY_NOT_VERIFIED','merge_allowed':False}]
    graph={'nodes':nodes,'edges':edges,'document_groups':groups,'material_lineage_groups':material,
           'unresolved_edges':uncertain,'global_unknown_rule':'All other independence relationships UNKNOWN_DEPENDENCE; known graph connectedness never implies independent roots',
           'statistical_independent_root_count':None,'known_document_groups_are_not_evidence_counts':True}
    assert len({n['node_id'] for n in nodes})==len(nodes)
    nids={n['node_id'] for n in nodes}
    assert all(e['from'] in nids and e['to'] in nids for e in edges+uncertain)
    assert sum(n['kind']=='OBSERVED_REPRESENTATION' for n in nodes)==26
    save('provenance_graph.json',graph)
    csv_write('provenance_edges.csv',edges+uncertain,['from','to','relation','verification','evidence'])
    pair_rows=[]
    for cid in sorted({p['case_id'] for p in pages}):
        pids=sorted(p['page_id'] for p in pages if p['case_id']==cid and p['page_id']!='P002')
        for a,b in itertools.combinations(pids,2):
            common=[g for g in material if any(s.startswith(a+'-') or ('-'+a+'-') in s for s in g['statement_ids'])
                    and any(s.startswith(b+'-') or ('-'+b+'-') in s for s in g['statement_ids'])]
            related=[e for e in citations if {e[0],e[1]}=={a,b}]
            unknown=[e for e in uncertain if {e['from'],e['to']}=={'URL:'+a,'URL:'+b}]
            if doc[a]==doc[b]:status='SAME_NOMINATED_DOCUMENT_VERSION_CONTENT_NOT_EQUATED'
            elif common:status='KNOWN_SHARED_MATERIAL_OR_NAMED_UPSTREAM'
            elif related:status='EXPLICIT_CITATION_NOT_WHOLE_PAGE_EQUIVALENCE'
            elif unknown:status='UNRESOLVED_REPORTED_OR_TARGET_RELATION'
            else:status='UNKNOWN_DEPENDENCE'
            pair_rows.append({'case_id':cid,'page_a':a,'page_b':b,'relationship':status,
                              'material_lineages':'|'.join(g['lineage_id'] for g in common),
                              'statistical_independence':'NOT_ESTABLISHED'})
    save('dependency_pairs.json',pair_rows)
    csv_write('dependency_pairs.csv',pair_rows,['case_id','page_a','page_b','relationship','material_lineages','statistical_independence'])
    return graph


def make_casebook(claims,pages):
    out=['# W1.1：规范命题与全部页面语义\n',
         '原W1保留；本版是开发性表示审计。五种语义标签与不可观测分开。所有人工签核待完成、Y未观测。',
         '精确短引文只保存在 drafts/ 对应语句记录；statement_index.json 提供指针及已核对的证据哈希。\n']
    for c in claims:
        C=c['C'];out.extend([f"## {c['case_id']} · 原索引 {c['train_index']}\n",c['original_claim']+'\n',
            f"参考标签：{c['dataset_reference_label']}；规范化状态：{c['normalization_status']}。",
            f"实体：{C['entity']}；关系：{C['relation']}；值：{C['value']}。",
            f"事件时间：{json.dumps(C['event_time'],ensure_ascii=False)}；地点：{C['geography']}；单位：{C['units']}。",
            '限定：'+'；'.join(C['qualifiers'])+'。',c['normalization_note']+'\n',
            '| 页面 | 完整目标语义 | 可用性 | 可比较性 | 语句索引 |', '|---|---|---|---|---|'])
        for p in (p for p in pages if p['case_id']==c['case_id']):
            label=p['semantic_label'] or 'UNOBSERVED'
            if p['metadata_semantic_label']:label+='；元数据：'+p['metadata_semantic_label']
            out.append(f"| {p['page_id']} | {label} | {p['availability']} | {p['comparison']['overall']} | {', '.join(p['statement_ids']) or '无可检查语句'} |")
        out.append('')
    (ROOT/'CASEBOOK.md').write_text('\n'.join(out)+'\n')


if __name__=='__main__': assemble()
