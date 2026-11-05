"""Download official archives with validated byte ranges; no credentials needed."""
from pathlib import Path
import concurrent.futures as cf
import hashlib
import json
import os
import re
import threading
import time
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'raw'
SOURCES = [
    dict(name='metadata', filename='meta_Clothing_Shoes_and_Jewelry.jsonl.gz', size=4051587355,
         url='https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Clothing_Shoes_and_Jewelry.jsonl.gz'),
    dict(name='reviews', filename='Clothing_Shoes_and_Jewelry.jsonl.gz', size=7109695439,
         url='https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/review_categories/Clothing_Shoes_and_Jewelry.jsonl.gz'),
    dict(name='google_extension', filename='extended_amazon2023_dataset.jsonl.zip', size=2860481866,
         expected_sha256='184795702084df48cd7947ef136e014fd58e75818335b57f30b3763d5bbc8ce3',
         url='https://huggingface.co/datasets/google/extended_amazon_2023_dataset/resolve/main/extended_amazon2023_dataset.jsonl.zip'),
]
CHUNK = 32 * 1024 * 1024
LOCK = threading.Lock()
DONE = 0
START = time.monotonic()

def download(source):
    global DONE
    dst = RAW / source['filename']
    state_path = RAW / (source['filename'] + '.download.json')
    n = (source['size'] + CHUNK - 1) // CHUNK
    completed = set()
    if state_path.exists() and dst.exists() and dst.stat().st_size == source['size']:
        completed = set(json.loads(state_path.read_text())['completed'])
    elif dst.exists() and dst.stat().st_size == source['size'] and (ROOT/'sources.json').exists():
        saved = json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
        previous = next((x for x in saved['sources'] if x['filename']==source['filename']),None)
        if previous and previous.get('sha256'):
            completed = set(range(n))
        else:
            with dst.open('wb') as f:
                f.truncate(source['size'])
    else:
        with dst.open('wb') as f:
            f.truncate(source['size'])
    local_lock = threading.Lock()
    def part(i):
        global DONE
        if i in completed:
            return
        a, b = i * CHUNK, min((i + 1) * CHUNK, source['size']) - 1
        for attempt in range(6):
            try:
                # A distinct query avoids intermediary caches reusing a different range.
                url = source['url'] + '?download=true&range_start=' + str(a)
                with requests.get(url, headers={'Range': f'bytes={a}-{b}', 'Accept-Encoding': 'identity'},
                                  stream=True, timeout=(30, 90)) as r:
                    r.raise_for_status()
                    if r.status_code != 206 or r.headers.get('Content-Range') != f'bytes {a}-{b}/{source["size"]}':
                        raise RuntimeError('Server returned an unexpected byte range')
                    written = 0
                    with dst.open('r+b', buffering=0) as f:
                        f.seek(a)
                        for buf in r.iter_content(1024 * 1024):
                            if written + len(buf) > b - a + 1:
                                raise RuntimeError('Range response exceeds expected length')
                            f.write(buf)
                            written += len(buf)
                    if written != b - a + 1:
                        raise RuntimeError('Incomplete range response')
                with local_lock:
                    completed.add(i)
                    state_path.write_text(json.dumps({'completed': sorted(completed)}))
                with LOCK:
                    DONE += written
                return
            except Exception as e:
                if attempt == 5:
                    raise
                print(f'retry {source["name"]} part={i}: {type(e).__name__}', flush=True)
                time.sleep(min(2 ** attempt, 20))
    with cf.ThreadPoolExecutor(6) as pool:
        list(pool.map(part, range(n)))
    h = hashlib.sha256()
    with dst.open('rb') as f:
        for buf in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(buf)
    source = {**source, 'sha256': h.hexdigest(), 'downloaded_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    if source.get('expected_sha256') and source['expected_sha256'] != source['sha256']:
        raise RuntimeError('Published SHA256 mismatch: ' + source['name'])
    print(f'COMPLETE {source["name"]}: {source["size"]:,} bytes SHA256={source["sha256"]}', flush=True)
    return source

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    stop = threading.Event()
    def progress():
        while not stop.wait(20):
            secs = time.monotonic() - START
            print(f'DOWNLOAD {DONE / 1e9:.2f} GB transferred; {DONE / max(secs, 1) / 1e6:.1f} MB/s average', flush=True)
    t = threading.Thread(target=progress, daemon=True)
    t.start()
    try:
        with cf.ThreadPoolExecutor(3) as pool:
            result = list(pool.map(download, SOURCES))
        manifest = dict(sources=result, original_dataset='https://amazon-reviews-2023.github.io/',
                        google_dataset='https://huggingface.co/datasets/google/extended_amazon_2023_dataset',
                        google_license='CC-BY-4.0')
        (ROOT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    finally:
        stop.set()

if __name__ == '__main__':
    main()
