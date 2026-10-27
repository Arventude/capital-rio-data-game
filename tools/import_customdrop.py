#!/usr/bin/env python3
"""Import the CustomDrop character assets into the Capital Rio data package.

The original Lua files target MTA APIs and are retained only as reference. The
APK consumes the extracted DFF/TXD/PNG assets through asset_manifest.v1.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import zipfile

ALLOWED = {".dff", ".txd", ".png"}
ROOT_MARKERS = (
    ("/customcharacter/assets/loader/", "mods/customdrop/"),
    ("/customcharacter/assets/textures/", "mods/customdrop/textures/"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_file", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    args = parser.parse_args()

    selected: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(args.zip_file) as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue
            suffix = pathlib.Path(name).suffix.lower()
            if suffix not in ALLOWED:
                continue
            marker, destination_prefix = next(
                ((marker, prefix) for marker, prefix in ROOT_MARKERS if marker in name),
                (None, None),
            )
            if marker is None:
                continue
            relative = name.split(marker, 1)[1]
            parts = pathlib.PurePosixPath(relative).parts
            if len(parts) < 1 or (marker.endswith("loader/") and parts[0] not in {"maleskin", "femaleskin"}):
                continue
            if any(part in {"", ".", ".."} for part in parts):
                raise ValueError(f"unsafe archive path: {name}")
            selected.append((str(pathlib.PurePosixPath(destination_prefix) / relative), archive.read(name)))

    if not selected:
        raise ValueError("no supported CustomDrop character assets found")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_lines = [
        "# Capital Rio CustomDrop asset_manifest.v1",
        "# key|relativePath|sha256|version|sizeBytes|required",
    ]
    for relative, data in sorted(selected):
        output_relative = pathlib.PurePosixPath(relative)
        target = args.output_dir / pathlib.Path(output_relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        key = "customdrop/" + relative.removeprefix("mods/customdrop/").replace("/", "_")
        required = "1" if pathlib.PurePosixPath(relative).name in {"male.dff", "male.txd"} else "0"
        manifest_lines.append(f"{key}|{output_relative}|{digest}|1|{len(data)}|{required}")

    manifest = args.output_dir / "asset_manifest.v1"
    manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    print(f"imported {len(selected)} assets into {args.output_dir}")
    print(f"manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
