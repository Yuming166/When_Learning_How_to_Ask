"""Create a local, self-contained catalogue bundle; never uploads anything."""
import argparse
import hashlib
import json
import pathlib
import zipfile

BASE = pathlib.Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path,
                        default=BASE / "artifacts/Myntra_Structured_Catalogue_v01.zip")
    args = parser.parse_args()
    files = list(BASE.glob("*.md")) + list(BASE.glob("*.py"))
    files += [BASE / "config.json", BASE / "FREEZE.json"]
    files += list((BASE / "schemas").glob("*.json"))
    files += [p for p in (BASE / "results").glob("*.json") if p.name != "BUNDLE.json"]
    files += [p for p in (BASE / "artifacts/catalogue_v01_final").rglob("*") if p.is_file()]
    files += list((BASE / "artifacts/source").glob("*.csv"))
    relative = sorted({str(p.relative_to(BASE)): p for p in files}.items())
    prefix = "Myntra_Structured_Catalogue_v01/"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in relative:
            info = zipfile.ZipInfo(prefix + name, date_time=(2026, 11, 4, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise ValueError("Bundle CRC failure")
        for name, path in relative:
            if archive.read(prefix + name) != path.read_bytes():
                raise ValueError("Bundle/source mismatch")
    receipt = {"file": args.output.name, "bytes": args.output.stat().st_size,
               "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
               "members": len(relative), "all_members_verified": True,
               "local_only": True, "uploaded": False}
    (BASE / "results/BUNDLE.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
