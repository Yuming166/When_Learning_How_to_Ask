"""Offline synthesis of provisional AI annotations; does not make semantic decisions."""
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from audit import ROOT, read, write, sha


def original(url):
    m = re.match(r'https?://web\.archive\.org/web/[^/]+/(https?://.*)', url)
    return m.group(1) if m else url


def dump_csv(name, rows, fields):
    with (ROOT/name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: ('UNOBSERVED' if k == 'Y' else 'UNKNOWN') if row.get(k) is None
                        else row[k] for k in fields})


def main():
    selected = read('selected_claims.json')
    inventory = {p['page_id']: p for p in read('url_inventory.json')}
    access = {p['page_id']: p for p in map(json.loads, (ROOT/'access_log.jsonl').read_text().splitlines())}
    raw_cases = []
    raw_pages = []
    for name in ['reviews_01_04.json', 'reviews_05_08.json', 'reviews_09_12.json']:
        review = read(name)
        for case in review['cases']:
            raw_cases.append((case, name))
            for page in case.get('pages', []):
                raw_pages.append((dict(page, case_id=case['case_id']), name))
        for page in review.get('pages', []):
            raw_pages.append((page, name))
    cases = []
    for c, source in raw_cases:
        s = next(v for v in selected if v['case_id'] == c['case_id'])
        r = s['record']
        cases.append({'case_id': c['case_id'], 'train_index': s['train_index'],
                      'claim': r['claim'], 'claim_date': r.get('claim_date'),
                      'dataset_label': r['label'], 'theta_reference': int(r['label'] == 'Supported'),
                      'theta_status': c['theta_status'],
                      'theta_note': c.get('theta_review', c.get('theta_note')),
                      'W2_candidate': c.get('case_candidate', c.get('w2_candidate', False)),
                      'reason': c.get('reason', c.get('case_reason', c.get('quarantine_reason', c.get('w2_caveat')))),
                      'annotation_source': source, 'Y': None, 'human_signoffs': 0})
    pages = []
    # Content actually inspected, including generic interfaces. These are not all evidence.
    readable = {'P007','P010','P016','P019','P021','P022','P023','P026','P027',
                'P028','P030','P031','P033','P034','P035','P036','P039','P041',
                'P042','P043','P044','P046','P048','P051'}
    for p, source in raw_pages:
        assert p.get('Y') is None and p.get('V_historical') is None
        assert p.get('human_signoffs', 0) == 0 and p.get('human_signoff', False) is False
        pid = p['page_id']; inv = inventory[pid]; a = access[pid]
        roles = sorted({o['role'] for o in inv['occurrences'] if o['case_id'] == p['case_id']})
        loc = p.get('evidence_locator', p.get('evidence_locators', []))
        if isinstance(loc, list): loc = '; '.join(loc)
        pages.append({'case_id': p['case_id'], 'page_id': pid, 'dataset_url': inv['url'],
                      'nominated_nonarchive_url': original(inv['url']), 'roles': '|'.join(roles),
                      'reference_only': 'reference' in roles,
                      'theta_reference': next(c['theta_reference'] for c in cases if c['case_id'] == p['case_id']),
                      'V_current': p.get('V_current'), 'V_historical': p.get('V_historical'), 'Y': None,
                      'representation_definition': 'V_current names inspected nonarchive-URL representation; browser cache may predate retrieval; not a guaranteed live snapshot',
                      'metadata_only': p.get('metadata_only', False),
                      'current_content_readable': pid in readable,
                      'status': p.get('disposition', p.get('stance_status')),
                      'reason': p.get('reason', p.get('note')),
                      'page_candidate': p.get('page_candidate', p.get('eligible_nonreference_w2_candidate', False)),
                      'evidence_locator': loc,
                      'raw_http_status': a['http_status'], 'raw_access_error': a['error'],
                      'raw_sha256': a.get('raw_sha256'), 'text_sha256': a.get('text_sha256'),
                      'annotation_source': source, 'human_signoffs': 0})
    cases.sort(key=lambda c: c['case_id']); pages.sort(key=lambda p: (p['case_id'],p['page_id']))
    expected = {(o['case_id'], p['page_id']) for p in inventory.values() for o in p['occurrences']}
    assert {(p['case_id'],p['page_id']) for p in pages} == expected
    assert len(pages) == len(expected), 'Duplicate page-case annotations'
    assert len(cases) == 12 and all(p['Y'] is None and p['V_historical'] is None for p in pages)
    for p in pages:
        if p['page_candidate']:
            assert p['V_current'] in (0,1) and not p['reference_only'] and not p['metadata_only']
    for c in cases:
        assert c['W2_candidate'] == any(p['page_candidate'] for p in pages if p['case_id']==c['case_id'])
    write('case_annotations.json', cases); write('page_annotations.json', pages)
    edges = []
    for c, source in raw_cases:
        for edge in c.get('provenance_findings', c.get('provenance', c.get('provenance_edges', []))):
            edges.append({'case_id': c['case_id'], 'annotation_source': source, **edge})
    write('provenance_relations.json', edges)
    # Every browser open is reconstructible from saved tool Source: open metadata.
    browser_access = []
    for path in sorted(ROOT.glob('browser_*/*.json')):
        obj = json.loads(path.read_text())
        result = obj.get('result', '')
        if not isinstance(result, str): continue
        for line in result.splitlines():
            m = re.search(r'Source: open\((\{.*?\})\)', line)
            if m:
                req = json.loads(m.group(1)); url = req['ref_id']
                browser_access.append({'requested_url': url,
                                       'page_ids': [pid for pid,x in inventory.items()
                                                    if original(x['url']) == url or x['url'] == url],
                                       'tool_source_line': line, 'receipt_path': str(path.relative_to(ROOT)),
                                       'receipt_sha256': sha(path.read_bytes())})
    write('browser_access_log.json', browser_access)
    data = read('inputs/train.json'); occ = read('url_occurrences.json')
    elig = Counter(r['label'] for r in data if r.get('label') in ('Supported','Refuted')
                   and isinstance(r.get('claim'),str) and r['claim'].strip())
    stats = {
        'total_train':len(data), 'train_label_counts':dict(Counter(r['label'] for r in data)),
        'eligible_nonempty_binary_claims':sum(elig.values()), 'eligible_by_label':dict(elig),
        'excluded_empty_binary_claims':sum(r.get('label') in ('Supported','Refuted') and not r.get('claim','').strip() for r in data),
        'selected':12, 'replacements':0,
        'unique_field_values':len(inventory), 'unique_http_urls':sum(p['url'].startswith(('http://','https://')) for p in inventory.values()),
        'url_field_occurrences':len(occ), 'metadata_occurrences':sum(x['page_id']=='P002' for x in occ),
        'http_url_occurrences':sum(x['page_id']!='P002' for x in occ),
        'case_page_rows_including_sentinel':len(pages), 'case_http_page_rows':sum(p['page_id']!='P002' for p in pages),
        'wayback_url_count':sum('web.archive.org/web/' in p['url'] for p in inventory.values()),
        'perma_url_count':sum('perma.cc/' in p['url'] for p in inventory.values()),
        'raw_access_ledger_rows':len(access), 'raw_http_attempted':len(access)-1,
        'raw_http_200':sum(a['http_status']==200 for a in access.values()),
        'raw_http_403':sum(a['http_status']==403 for a in access.values()),
        'raw_http_404':sum(a['http_status']==404 for a in access.values()),
        'raw_transport_failures':sum(a['http_status'] is None and a['page_id']!='P002' for a in access.values()),
        'raw_saved_bodies':sum(bool(a['raw_path']) for a in access.values()),
        'browser_open_records':len(browser_access),
        'inspected_nonarchive_body_or_interface_representations':len(readable),
        'readable_reference_representations':sum(p['current_content_readable'] and p['reference_only'] for p in pages),
        'reference_binary_full_claim_stances':sum(p['reference_only'] and p['V_current'] is not None for p in pages),
        'ordinary_binary_full_claim_page_candidates':sum(p['page_candidate'] for p in pages),
        'metadata_only_binary_leads':sum(p['metadata_only'] and p['V_current'] is not None for p in pages),
        'strict_case_candidates_W2':sum(c['W2_candidate'] for c in cases),
        'strict_case_quarantined':sum(not c['W2_candidate'] for c in cases),
        'historical_binary_stances':0, 'human_signed_off_cases':0, 'Y_observations':0,
        'model_service_calls':0, 'training_jobs':0, 'methodology_reruns':0,
        'ordinary_wrong_source_body_examples_established':0,
        'cases_with_three_independent_comparable_sources_established':0,
        'stage_decision':f"REVISE; {sum(c['W2_candidate'] for c in cases)} nonarchive-representation candidates for human review; NO_GO for W3 under present evidence"
    }
    write('SUMMARY.json',stats)
    dump_csv('case_audit.csv', cases, ['case_id','train_index','claim','claim_date','dataset_label','theta_reference','theta_status','W2_candidate','reason','Y','human_signoffs'])
    dump_csv('page_audit.csv', pages, ['case_id','page_id','dataset_url','nominated_nonarchive_url','roles','theta_reference','V_current','V_historical','Y','status','metadata_only','page_candidate','evidence_locator','reason'])
    cards = ['# W1：12 条声明 × 全部指定页面审计\n',
             '全部为 AI 辅助暂定标注；人工签核 0，Y 未采集。θ 是数据集参考标签。',
             '`V_current` 仅指本轮取得的非归档 URL 表示，可能来自浏览器缓存；不保证实时性。历史 V 一律 UNKNOWN。',
             '候选表示可供 W2 人工审阅，未授权 W3。页号 Pxxx 保留原 URL；归档与非归档表示不能互相代替。\n']
    for c in cases:
        cards.extend([f"## {c['case_id']} · train[{c['train_index']}]\n",c['claim']+'\n',
                      f"参考 θ={c['theta_reference']} ({c['dataset_label']}); 声明日期字段：{c['claim_date']}。",
                      f"参考核验：{c['theta_note']}",f"处置：{'W2 待人工审阅候选' if c['W2_candidate'] else '隔离'}。{c['reason']}\n",
                      '| 页面 | 角色 | 观察 V | 历史 V / Y | 判定与证据位置 |',
                      '|---|---|---:|---|---|'])
        for p in (p for p in pages if p['case_id']==c['case_id']):
            url = p['dataset_url']; label=f"[{p['page_id']}]({url})" if p['page_id']!='P002' else 'P002 Metadata'
            loc=(p['evidence_locator'] or 'access_log.jsonl:'+p['page_id']).replace('|',' / ')
            value='UNKNOWN' if p['V_current'] is None else str(p['V_current'])+(' (仅元数据)' if p['metadata_only'] else '')
            cards.append(f"| {label} | {p['roles'].replace('|',', ')} | {value} | UNKNOWN / 未观测 | {p['status']}; {loc} |")
        cards.append('')
    (ROOT/'CASEBOOK.md').write_text('\n'.join(cards)+'\n')
    print(json.dumps(stats,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
