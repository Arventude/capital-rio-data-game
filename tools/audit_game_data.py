#!/usr/bin/env python3
"""Audit a Capital Rio game-data ZIP before publishing it.

The current mobile client expects the original GTA San Andreas world. This tool
only audits names and gta.dat references; it never rewrites or deletes assets.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile

FORBIDDEN_PATH_MARKERS = (
    "loader/blackrussia_client.log",
    "/data/maps/portland/",
    "/data/maps/portland1/",
    "/data/maps/m_city/",
    "/data/maps/liberty/",
    "/data/maps/motor/",
    "/data/maps/staunton/",
    "/data/maps/vcsa.ide",
    "/data/maps/vcsa.ipl",
)
FORBIDDEN_DAT_REFERENCES = (
    r"data\maps\vcsa.ide",
    r"data\maps\vcsa.ipl",
    r"data\maps\trees_map.ide",
    r"data\maps\trees_map.ipl",
    "blackrussia",
    "black russia",
)
REQUIRED_SUFFIXES = (
    "cinfo.bin",
    "gtasatelem.set",
    "gta_sa.set",
    "stream.ini",
    "data/gta.dat",
    "samp/settings.ini",
    "texdb/gta3.img",
)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip", help="game-data ZIP to audit")
    args = parser.parse_args()

    findings: list[str] = []
    with zipfile.ZipFile(args.zip) as archive:
        files = [info for info in archive.infolist() if not info.is_dir()]
        names = [info.filename.replace("\\", "/") for info in files]
        lower_names = [name.lower() for name in names]
        print(f"archive={args.zip}")
        print(f"sha256={sha256(args.zip)}")
        print(f"files={len(files)}")

        for suffix in REQUIRED_SUFFIXES:
            ok = any(name.endswith(suffix.lower()) for name in lower_names)
            print(f"required:{suffix}={'OK' if ok else 'MISSING'}")
            if not ok:
                findings.append(f"missing required suffix: {suffix}")

        for original, name in zip(names, lower_names):
            if any(marker in name for marker in FORBIDDEN_PATH_MARKERS):
                findings.append(f"forbidden world path: {original}")

        for info, name in zip(files, lower_names):
            if not (name.endswith("/data/gta.dat") or name.endswith("/samp/gta.dat")):
                continue
            text = archive.read(info).decode("utf-8", errors="replace").lower()
            for marker in FORBIDDEN_DAT_REFERENCES:
                if marker in text:
                    findings.append(f"forbidden gta.dat reference in {info.filename}: {marker}")

    unique_findings = list(dict.fromkeys(findings))
    if unique_findings:
        print("status=REJECT")
        for finding in unique_findings[:100]:
            print(f"finding={finding}")
        return 2
    print("status=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
