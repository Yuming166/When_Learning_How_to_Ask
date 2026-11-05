"""Optional exact-source downloader. Existing verified bytes are always reused."""
import hashlib
import json
import pathlib
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent


def main():
    config = json.loads((BASE / "config.json").read_text())
    target = BASE / "artifacts/source" / config["source_file"]
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != config["source_sha256"]:
            raise ValueError("Existing source hash differs; preserve and investigate it")
        print("Reused verified local source; zero network requests")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    url = (f"https://huggingface.co/datasets/{config['source_repo']}/resolve/"
           f"{config['source_revision']}/{config['source_file']}?download=true")
    partial = target.with_suffix(target.suffix + ".partial")
    if partial.exists():
        raise ValueError("Prior partial download exists; preserve it before a separate acquisition")
    # No retry, authentication, image access, TLS bypass or upstream code execution.
    with urllib.request.urlopen(url, timeout=30) as response, partial.open("xb") as f:
        total = 0
        while chunk := response.read(65536):
            total += len(chunk)
            if total > 4 * 1024 * 1024:
                raise ValueError("4MB source download cap exceeded")
            f.write(chunk)
        length = response.headers.get("Content-Length")
        if length and int(length) != total:
            raise ValueError("Truncated source response; partial bytes preserved")
    if hashlib.sha256(partial.read_bytes()).hexdigest() != config["source_sha256"]:
        raise ValueError("Source hash differs; partial bytes preserved")
    partial.rename(target)
    print("Downloaded and SHA256-verified pinned source")


if __name__ == "__main__":
    main()
