"""Fetch named official ZIP members with bounded HTTP ranges and CRC checks."""
import io
import json
import struct
import urllib.request
import zipfile
import zlib
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "https://aristo-data-public.s3.amazonaws.com/proofwriter/proofwriter-dataset-V2020.12.3.zip"


def get_range(start, end):
    req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        assert r.status == 206 and r.headers.get("Content-Range", "").startswith(f"bytes {start}-")
        data = r.read(end-start+2)
    assert len(data) == end-start+1
    return data


def main():
    (ROOT / "sources").mkdir(exist_ok=True)
    index = json.loads((ROOT / "source_indexes/proofwriter_zip_index.json").read_text())
    wanted = ["/README.md", "/OWA/depth-3/meta-train.jsonl", "/OWA/depth-3/meta-dev.jsonl"]
    receipt = []
    for suffix in wanted:
        item = next(x for x in index["files"] if x["name"].endswith(suffix))
        path = ROOT / "sources" / ("proofwriter_README.md" if suffix == "/README.md" else "proofwriter_owa3_" + Path(suffix).name)
        assert not path.exists(), "No source overwrite"
        offset = item["offset"]
        header = get_range(offset, offset+29)
        fields = struct.unpack("<4s5H3I2H", header)
        assert fields[0] == b"PK\x03\x04"
        start = offset + 30 + fields[-2] + fields[-1]
        compressed = get_range(start, start+item["compressed"]-1)
        content = zlib.decompress(compressed, -15)
        assert len(content) == item["size"] and zlib.crc32(content) == item["crc"]
        path.write_bytes(content)
        receipt.append({**item, "source_url": URL, "downloaded_bytes": len(compressed)+30,
                        "range_start": start, "sha256": hashlib.sha256(content).hexdigest(), "local_file": path.name})
        print(path.name, len(content), flush=True)
    (ROOT / "sources/proofwriter_fetch_receipt.json").write_text(json.dumps(receipt, indent=2)+"\n")


if __name__ == "__main__": main()
