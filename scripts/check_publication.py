"""Check exported files, source hashes, JSON, syntax, and credential patterns."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "github_credential": re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    "provider_credential": re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential_url": re.compile(r"https?://[^/\s:@]+:[^/\s@]+@"),
}


def main():
    failures = []
    manifest = json.loads((ROOT/"publication/SOURCE_MANIFEST.json").read_text())
    for row in manifest["source_files"]:
        target = ROOT/row["path"]
        expected = row.get("published_sha256", row["sha256"])
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            failures.append({"file": row["path"], "kind": "exported_source_hash"})
    parsed = {"python": 0, "json": 0, "text_files_scanned": 0}
    for target in sorted(ROOT.rglob("*")):
        rel = target.relative_to(ROOT)
        if not target.is_file() or any(part in {".git", ".venv", "venv", "__pycache__", ".deps", ".pytest_cache"} for part in rel.parts):
            continue
        if target.suffix in {".png", ".pdf"}:
            continue
        try:
            content = target.read_text()
        except UnicodeError:
            failures.append({"file": str(rel), "kind": "unexpected_binary"})
            continue
        parsed["text_files_scanned"] += 1
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                # Record location and category only, never the matching value.
                failures.append({"file": str(rel), "line": content[:match.start()].count("\n")+1, "kind": kind})
        try:
            if target.suffix == ".json":
                json.loads(content)
                parsed["json"] += 1
            elif target.suffix == ".py":
                ast.parse(content, filename=str(rel))
                parsed["python"] += 1
        except (ValueError, SyntaxError) as exc:
            failures.append({"file": str(rel), "kind": type(exc).__name__})
    print(json.dumps({"passed": not failures, "exported_source_files": len(manifest["source_files"]),
                      **parsed, "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
