import unittest
from copy import deepcopy
from pathlib import Path
import json

from t1.core import messages_for,build_state
from t1.qwen import encode_row


class CompletionMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from transformers import AutoTokenizer
        cfg=json.loads((Path(__file__).resolve().parents[1]/'config.json').read_text())
        cls.tokenizer=AutoTokenizer.from_pretrained(cfg['checkpoint'],local_files_only=True)

    def row(self):
        public={'d':4,'groups':[{'targets':[0]},{'targets':[1,2,3]}],
                'type_accuracy':[.8,.8],'rate_domain':{'eta':.05}}
        counts=[[[1,0],[0,1]] for _ in range(4)]
        state=build_state(public,{'high':[],'low':[]},counts,counts,[[0,0],[0,0]],64,2048)
        return {'messages':messages_for(state,[13,13,13,13,12,12,12,12,0,0])}

    def test_real_chat_template_completion_mask(self):
        row=self.row();enc=encode_row(self.tokenizer,row)
        n=enc['prompt_tokens']
        self.assertGreater(n,0);self.assertGreater(enc['target_tokens'],0)
        self.assertTrue(all(x==-100 for x in enc['labels'][:n]))
        self.assertEqual(enc['labels'][n:],enc['input_ids'][n:])
        actual=self.tokenizer.decode(enc['input_ids'][n:],skip_special_tokens=True)
        self.assertEqual(actual.strip(),row['messages'][-1]['content'])

    def test_long_input_rejected_without_truncation(self):
        row=self.row();row['messages'][1]['content']='observed '*1500
        with self.assertRaisesRegex(ValueError,'No truncation'):
            encode_row(self.tokenizer,row)


if __name__=='__main__':unittest.main()
