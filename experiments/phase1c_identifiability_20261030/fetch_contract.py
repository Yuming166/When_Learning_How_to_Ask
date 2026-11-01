"""Extract small official ContractNLI ZIP members, with size/CRC verification."""
import hashlib
import json
import struct
import subprocess
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
URL='https://stanfordnlp.github.io/contract-nli/resources/contract-nli.zip'


def get_range(start,end):
    tmp=ROOT/'sources/contract_member.tmp'
    subprocess.run(['curl','--silent','--show-error','--fail','--location',
        '--retry','2','--max-time','45','--max-filesize','2000000',
        '--range',f'{start}-{end}',URL,'--output',str(tmp)],check=True)
    data=tmp.read_bytes();tmp.unlink()
    assert len(data)==end-start+1, 'Server must honor exact byte range'
    return data


def main():
    (ROOT / "sources").mkdir(exist_ok=True)
    index=json.loads((ROOT/'source_indexes/contract_zip_index.json').read_text())
    receipt=[]
    for item in index['files']:
        path=ROOT/'sources'/('contract_'+Path(item['name']).name)
        offset=item['offset']
        header=get_range(offset,offset+29)
        fields=struct.unpack('<4s5H3I2H',header)
        assert fields[0]==b'PK\x03\x04' and fields[3]==8
        start=offset+30+fields[-2]+fields[-1]
        data=zlib.decompress(get_range(start,start+item['compressed']-1),-15)
        assert len(data)==item['size'] and zlib.crc32(data)==item['crc']
        if path.exists():assert path.read_bytes()==data
        else:path.write_bytes(data)
        receipt.append({**item,'source_url':URL,'sha256':hashlib.sha256(data).hexdigest(),
                        'local_file':path.name,'range_start':start,'downloaded_bytes':30+item['compressed']})
        print(path.name,len(data),flush=True)
    (ROOT/'sources/contract_fetch_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
