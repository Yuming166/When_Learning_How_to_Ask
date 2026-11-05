"""Download and clean, or overlap cleaning with an already running downloader."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import os

ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/'code'
FILES={'metadata':('meta_Clothing_Shoes_and_Jewelry.jsonl.gz',4051587355),
       'google':('extended_amazon2023_dataset.jsonl.zip',2860481866),
       'reviews':('Clothing_Shoes_and_Jewelry.jsonl.gz',7109695439)}

def run(script,*args):
    subprocess.run([sys.executable,'-u',str(CODE/script),*args],check=True,
                   env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})

def ready(stage):
    filename,size=FILES[stage]
    p=ROOT/'raw'/filename
    state=ROOT/'raw'/(filename+'.download.json')
    while True:
        if p.exists() and p.stat().st_size==size:
            if state.exists():
                try:
                    if len(json.loads(state.read_text())['completed'])==(size+33554431)//33554432: return
                except json.JSONDecodeError: pass
            if (ROOT/'sources.json').exists(): return
        time.sleep(10)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--download-running',action='store_true')
    args=parser.parse_args()
    if not args.download_running: run('download_data.py')
    for stage in ('metadata','attributes','google','reviews'):
        if stage in FILES: ready(stage)
        marker=ROOT/(stage+'_statistics.json')
        if marker.exists():
            print('ALREADY_COMPLETE',stage,flush=True)
        else: run('clean_data.py',stage)
    while not (ROOT/'sources.json').exists(): time.sleep(5)
    run('finalize_data.py')

if __name__=='__main__': main()
