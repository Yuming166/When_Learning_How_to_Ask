"""Verify and unpack released synthetic histories; never overwrite a different file."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    frozen = json.loads((HERE/'FREEZE.json').read_text())
    for rel, expected in frozen['local_sha256'].items():
        assert digest(HERE/rel) == expected, rel
    for rel, expected in frozen['dependency_sha256'].items():
        assert digest(ROOT/rel) == expected, rel
    receipt = json.loads((HERE/'results/archive_receipt.json').read_text())
    archive = HERE/receipt['path']
    assert digest(archive) == receipt['sha256']
    payloads = []
    with tarfile.open(archive, 'r:gz') as tar:
        names = set()
        for member in tar.getmembers():
            rel = PurePosixPath(member.name)
            assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts
            assert rel.parts[0] == 'artifacts' and rel.suffix == '.json'
            assert member.name not in names
            names.add(member.name)
            payload = tar.extractfile(member).read()
            target = HERE/rel
            if target.exists():
                assert target.read_bytes() == payload, f'refusing overwrite: {rel}'
            payloads.append((target, payload))
    for target, payload in payloads:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    manifest = json.loads((HERE/'RECEIPT.json').read_text())
    for rel, expected in manifest['sha256'].items():
        assert digest(HERE/rel) == expected, rel
    print(json.dumps({'status':'SOURCE_ARCHIVE_AND_MANIFEST_PASS','archive_members':len(payloads),'manifest_entries':len(manifest['sha256']),'source_hashes':len(frozen['local_sha256'])+len(frozen['dependency_sha256']),'new_model_calls':0}))


if __name__ == '__main__':
    main()
