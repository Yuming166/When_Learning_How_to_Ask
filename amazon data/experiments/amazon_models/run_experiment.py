"""Amazon-only replication: frozen Luna prompts and policy replay, eight API calls."""
import sys
sys.dont_write_bytecode = True
import concurrent.futures, datetime, hashlib, importlib.util, json, os, shutil, time
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = ROOT / 'Learning_How_to_Ask_Overleaf/research'
LUNA = SOURCE / 'luna'
BASE = 'https://cn-beijing.maas.qianwenaiapi.com/compatible-mode/v1'
MODELS = ['deepseek-v4.1-flash', 'glm-5.3']
SYSTEM = 'You answer as shoppers from the preference cards in the user message. Use only those cards. Return the requested answers directly. Do not use tools or consult files, websites, other conversations, or other agents. Use the customer IDs exactly as C followed by three digits. Return only the requested JSON object.'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def prepare(model):
    dest=OUT/model; dest.mkdir(exist_ok=True)
    plan=read(LUNA/'protocol.json')
    plan.update(requested_model=model,requested_reasoning='provider default',
        collection='Four fresh API requests, each containing 16 Amazon shoppers. Exact original Luna user prompts; same customer-only system prompt as successful Gemini replication. No tools, retries, answer repair, or additional model calls.',
        identity='Requested model slug and returned API model field retained; provider routes are not independently verified.',
        transport={'base_url':BASE,'system':SYSTEM,'max_tokens':4096,'temperature':'provider default','retries':0,'timeout_seconds':180},
        source_driver_sha256=sha(Path(__file__)),
        scorer_sha256=sha(LUNA/'luna_table2.py'),
        interval_comparisons='Six contrasts: two new models times three question budgets.')
    plan['batches']=[b for b in plan['batches'] if b['dataset']=='Amazon']
    for b in plan['batches']:
        p=dest/b['prompt_file']
        if not p.exists(): shutil.copyfile(LUNA/b['prompt_file'],p)
        assert sha(p)==b['prompt_sha256']
    p=dest/'protocol.json'
    if p.exists(): assert read(p)==plan
    else: write(p,plan)
    return dest,plan

def collect_model(model):
    dest,plan=prepare(model)
    receipts=[]
    for b in plan['batches']:
        rp=dest/(b['id']+'_receipt.json')
        if rp.exists(): receipts.append(read(rp));continue
        # Existing raw evidence without a receipt requires inspection, never another call.
        rawpath=dest/(b['id']+'_api.json')
        assert not rawpath.exists() and not (dest/b['response_file']).exists()
        payload={'model':model,'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':(dest/b['prompt_file']).read_text(encoding='utf-8')}],'max_tokens':4096}
        started=time.monotonic(); stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        error=None; obj={}; content=''; status=None
        try:
            r=requests.post(BASE+'/chat/completions',headers={'Authorization':'Bearer '+os.environ['RESEARCH_TASK_KEY']},json=payload,timeout=(30,180))
            status=r.status_code
            rawpath.write_text(r.text.replace(os.environ['RESEARCH_TASK_KEY'],'[redacted]'),encoding='utf-8')
            if r.ok:
                obj=r.json(); content=obj['choices'][0]['message']['content']
                if not isinstance(content,str): content='';error='nontext_content'
            else: error='HTTP_'+str(status)
        except Exception as e:
            error=type(e).__name__
        # Preserve exact model content, including fences or truncation if present.
        (dest/b['response_file']).write_text(content,encoding='utf-8')
        receipt={'batch':b['id'],'started_utc':stamp,'requested_model':model,'returned_model':obj.get('model'),'http_status':status,'error':error,'finish_reason':obj.get('choices',[{}])[0].get('finish_reason'),'usage':obj.get('usage'),'duration_seconds':time.monotonic()-started,'prompt_sha256':sha(dest/b['prompt_file']),'response_sha256':sha(dest/b['response_file'])}
        write(rp,receipt);receipts.append(receipt)
        print(model,b['id'],status,error or 'received',receipt['finish_reason'],receipt['usage'],flush=True)
    write(dest/'collection_receipt.json',{'model':model,'requests':len(receipts),'retries':0,'receipts':receipts})

def score(model):
    dest,plan=prepare(model)
    sys.path.insert(0,str(SOURCE))
    spec=importlib.util.spec_from_file_location('frozen_luna_scorer',LUNA/'luna_table2.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.OUT,m.SOURCE=dest,SOURCE
    m.TABLE1=ROOT/'outputs/01a1aa41-ac77-79e1-b73c-320625254096'
    original_read=m.read
    def amazon_only(p):
        obj=original_read(p)
        if Path(p)==SOURCE/'experiment_inputs.json': return {'common':{'Amazon':obj['common']['Amazon']}}
        return obj
    m.read=amazon_only
    m.score()
    result=read(dest/'results.json')
    result['interval_scope']='5000 paired-menu resamples within each of three seeds; Bonferroni correction over six model-budget contrasts (two new models times three budgets). Conditional on fixed products, synthetic profiles, and observed answer banks. Same percentile cutoffs as earlier Luna/Gemini.'
    write(dest/'results.json',result)
    (dest/'table2_luna.csv').replace(dest/'table_amazon.csv')

if __name__=='__main__':
    action=sys.argv[1] if len(sys.argv)>1 else 'all'
    for model in MODELS: prepare(model)
    if action=='all':
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(collect_model,MODELS))
    if action in ['all','score']:
        for model in MODELS: score(model)
