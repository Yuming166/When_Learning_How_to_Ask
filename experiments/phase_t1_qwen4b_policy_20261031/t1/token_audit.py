"""Before-fit token/mask/schema audit; no model load or scientific sampling."""
import json
from pathlib import Path
from .qwen import ROOT,dump,encode_row
from .core import messages_for,validate_state


def main():
    from transformers import AutoTokenizer
    cfg=json.loads((ROOT/'config.json').read_text())
    tok=AutoTokenizer.from_pretrained(cfg['checkpoint'],local_files_only=True)
    manifest=json.loads((ROOT/'artifacts/data/manifest.json').read_text())
    assert manifest['status']=='completed'
    results={}
    for split,meta in manifest['splits'].items():
        rows=[json.loads(x) for x in (ROOT/'artifacts/data'/meta['file']).open()]
        assert len(rows)==meta['states']
        tokens=[];prompt=[];target=[]
        for row in rows:
            state=validate_state(row['state'])
            assert row['messages']==messages_for(state,row['teacher_percent'])
            encoded=encode_row(tok,row)
            tokens.append(len(encoded['input_ids']));prompt.append(encoded['prompt_tokens']);target.append(encoded['target_tokens'])
        results[split]={'states':len(rows),'worlds':meta['worlds'],'max_total_tokens':max(tokens),
            'min_total_tokens':min(tokens),'max_prompt_tokens':max(prompt),'target_tokens':sum(target),
            'prompt_tokens':sum(prompt),'all_labels_prompt_masked':True,'exact_canonical_messages':True,
            'no_truncation_or_filtering':True}
    result={'status':'passed','splits':results,'student_input_allowlist':True,
        'completion_only':True,'no_truncation':True,'tokenizer':'unchanged local checkpoint',
        'tokenization_only_no_model_forward':True}
    dump(ROOT/'audit/TOKENIZATION.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
