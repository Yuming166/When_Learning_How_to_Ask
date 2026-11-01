"""Local, deterministic artifact utilities; no network or model transport."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(obj):return hashlib.sha256(obj if isinstance(obj,bytes) else canonical(obj).encode()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def jsonl(path):return [json.loads(line) for line in Path(path).read_text().splitlines() if line]
