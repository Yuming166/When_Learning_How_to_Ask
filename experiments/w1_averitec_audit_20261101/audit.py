"""W1 data-only audit: deterministic selection, URL inventory and one-pass capture.

No model clients, credentials, inference or experiment code are imported.
Online capture is an explicit command; verify is offline.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text())


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def select():
    data = read('inputs/train.json')
    ranked = []
    for label in ['Supported', 'Refuted']:
        group = [(sha(f"W1-v1|{i}|{r['claim']}".encode()), i, r)
                 for i, r in enumerate(data)
                 if r.get('label') == label and isinstance(r.get('claim'), str)
                 and r['claim'].strip()]
        ranked.extend(sorted(group)[:6])
    return [{'case_id': f'W1-{n:02}', 'train_index': i,
             'selection_sha256': k, 'record': r}
            for n, (k, i, r) in enumerate(sorted(ranked, key=lambda x: x[1]), 1)]


def inventory():
    urls = {}
    occurrences = []
    def add(case, role, locator, value):
        if not isinstance(value, str) or not value.strip():
            return
        url = value.strip()
        if url not in urls:
            uid = f'P{len(urls)+1:03}'
            urls[url] = {'page_id': uid, 'url': url,
                         'host': urllib.parse.urlparse(url).netloc,
                         'occurrences': []}
        entry = {'case_id': case, 'role': role, 'dataset_locator': locator,
                 'page_id': urls[url]['page_id']}
        occurrences.append(entry)
        urls[url]['occurrences'].append(entry)
    for x in read('selected_claims.json'):
        c, r = x['case_id'], x['record']
        for key, role in [('original_claim_url', 'original'),
                          ('cached_original_claim_url', 'original_archive'),
                          ('fact_checking_article', 'reference')]:
            add(c, role, key, r.get(key))
        for qi, q in enumerate(r.get('questions', [])):
            for ai, a in enumerate(q.get('answers', [])):
                for key, role in [('source_url', 'evidence'),
                                  ('cached_source_url', 'evidence_archive')]:
                    add(c, role, f'questions[{qi}].answers[{ai}].{key}', a.get(key))
    write('url_inventory.json', list(urls.values()))
    write('url_occurrences.json', occurrences)
    print(json.dumps({'unique_url_strings': len(urls), 'occurrences': len(occurrences)}))


def capture_one(page):
    from bs4 import BeautifulSoup
    uid, url = page['page_id'], page['url']
    result = {'page_id': uid, 'requested_url': url,
              'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'method': 'urllib_single_request', 'http_status': None,
              'error': None, 'raw_path': None, 'text_path': None}
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError('Non-HTTP URL string retained but not requested')
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; W1-Research-Audit/1.0)',
            'Accept': 'text/html,application/pdf,text/plain;q=0.8,*/*;q=0.2'})
        try:
            response = urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as e:
            response = e  # Preserve the error body as access evidence, not article content.
        with response:
            body = response.read(8000001)
            result.update(http_status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type', ''),
                          truncated=len(body) > 8000000)
        body = body[:8000000]
        suffix = '.pdf' if body.startswith(b'%PDF') else '.html'
        raw = ROOT / 'snapshots' / (uid + suffix)
        raw.write_bytes(body)
        result.update(raw_path=str(raw.relative_to(ROOT)), raw_sha256=sha(body), bytes=len(body))
        textpath = ROOT / 'texts' / (uid + '.txt')
        if suffix == '.pdf':
            cp = subprocess.run(['pdftotext', '-layout', str(raw), str(textpath)],
                                capture_output=True, timeout=20)
            result['extractor'] = 'pdftotext -layout'
            if cp.returncode:
                raise ValueError('PDF extraction failed')
        else:
            soup = BeautifulSoup(body, 'html.parser')
            result['title'] = soup.title.get_text(' ', strip=True) if soup.title else None
            for node in soup(['script', 'style', 'noscript', 'svg', 'template']):
                node.decompose()
            lines = [x.strip() for x in soup.get_text('\n').splitlines() if x.strip()]
            textpath.write_text('\n'.join(lines) + '\n')
            result['extractor'] = 'BeautifulSoup html.parser; script/style/noscript/svg/template removed'
        tb = textpath.read_bytes()
        result.update(text_path=str(textpath.relative_to(ROOT)), text_sha256=sha(tb),
                      text_chars=len(tb.decode()), text_lines=len(tb.decode().splitlines()))
    except Exception as e:
        result['error'] = type(e).__name__ + ': ' + str(e)[:400]
    result['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    return result


def capture():
    if (ROOT / 'access_log.jsonl').exists():
        raise SystemExit('Capture already exists; no silent refetch or overwriting.')
    (ROOT / 'snapshots').mkdir(exist_ok=True)
    (ROOT / 'texts').mkdir(exist_ok=True)
    with (ROOT / 'access_log.jsonl').open('x') as log:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(capture_one, p) for p in read('url_inventory.json')]
            for future in concurrent.futures.as_completed(futures):
                r = future.result()
                log.write(json.dumps(r, ensure_ascii=False) + '\n'); log.flush()
                print(r['page_id'], r['http_status'], r.get('text_chars'),
                      r['error'] or r.get('title', ''), flush=True)


def verify():
    assert sha((ROOT/'PROTOCOL.json').read_bytes()) == read('PROTOCOL_FREEZE.json')['protocol_sha256']
    assert select() == read('selected_claims.json'), 'Selection mismatch'
    assert len(select()) == 12
    assert sha((ROOT/'selected_claims.json').read_bytes()) == read('SELECTION_RECEIPT.json')['selection_sha256']
    for f in read('inputs/UPSTREAM_RECEIPT.json')['files']:
        assert sha((ROOT/'inputs'/Path(f['upstream_path']).name).read_bytes()) == f['sha256']
    inventory = read('url_inventory.json')
    log = [json.loads(x) for x in (ROOT/'access_log.jsonl').read_text().splitlines()]
    assert {r['page_id'] for r in log} == {r['page_id'] for r in inventory}
    assert len(log) == len(inventory)
    for r in log:
        for kind in ['raw', 'text']:
            if r.get(kind+'_path'):
                assert sha((ROOT/r[kind+'_path']).read_bytes()) == r[kind+'_sha256']
    print('PASS: protocol, exact selection, upstream hashes, complete URL access ledger and snapshots')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['inventory', 'capture', 'verify'])
    args = parser.parse_args()
    globals()[args.command]()
