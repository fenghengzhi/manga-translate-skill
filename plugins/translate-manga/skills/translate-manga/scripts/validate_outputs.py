#!/usr/bin/env python3
"""Validate manga translation output files.

This script intentionally avoids third-party dependencies. It checks file
existence, basic image format, and dimensions for numbered manga pages.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path


def parse_pages(spec: str) -> list[str]:
    pages: list[str] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            width = max(len(start_s), len(end_s), 3)
            pages.extend(f"{n:0{width}d}" for n in range(start, end + 1))
        else:
            pages.append(f"{int(part):03d}" if part.isdigit() else part)
    return pages


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        data = f.read(24)
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        if f.read(2) != b"\xff\xd8":
            raise ValueError("not a JPEG")
        while True:
            marker_start = f.read(1)
            if not marker_start:
                raise ValueError("JPEG SOF marker not found")
            if marker_start != b"\xff":
                continue
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            if marker in {b"\xd8", b"\xd9"}:
                continue
            length_b = f.read(2)
            if len(length_b) != 2:
                raise ValueError("truncated JPEG segment")
            length = struct.unpack(">H", length_b)[0]
            if marker in {
                b"\xc0", b"\xc1", b"\xc2", b"\xc3",
                b"\xc5", b"\xc6", b"\xc7",
                b"\xc9", b"\xca", b"\xcb",
                b"\xcd", b"\xce", b"\xcf",
            }:
                segment = f.read(5)
                if len(segment) != 5:
                    raise ValueError("truncated JPEG SOF segment")
                height, width = struct.unpack(">HH", segment[1:5])
                return width, height
            f.seek(length - 2, os.SEEK_CUR)


def image_dimensions(path: Path) -> tuple[str, tuple[int, int]]:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return "PNG", png_dimensions(path)
    if suffix in {".jpg", ".jpeg"}:
        return "JPEG", jpeg_dimensions(path)
    raise ValueError(f"unsupported image extension: {path.suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate numbered manga translation outputs.")
    parser.add_argument("chapter_dir", type=Path)
    parser.add_argument("--pages", required=True, help="Page list/range, for example 1-22 or 002,003,004")
    parser.add_argument("--source-ext", default=".jpg")
    parser.add_argument("--target-suffix", default=".zh.png")
    parser.add_argument("--strict-dimensions", action="store_true", help="Fail when source/output dimensions differ")
    args = parser.parse_args()

    chapter_dir = args.chapter_dir
    pages = parse_pages(args.pages)
    failed = False
    targets_found = 0

    for page in pages:
        source = chapter_dir / f"{page}{args.source_ext}"
        target = chapter_dir / f"{page}{args.target_suffix}"
        row_failed = False

        if not source.is_file() or source.stat().st_size == 0:
            print(f"{page}: FAIL source missing or empty: {source}")
            failed = True
            continue
        if not target.is_file() or target.stat().st_size == 0:
            print(f"{page}: FAIL target missing or empty: {target}")
            failed = True
            continue

        try:
            source_kind, source_dims = image_dimensions(source)
            target_kind, target_dims = image_dimensions(target)
        except ValueError as exc:
            print(f"{page}: FAIL {exc}")
            failed = True
            continue

        if target_kind != "PNG":
            print(f"{page}: FAIL target is {target_kind}, expected PNG")
            failed = True
            row_failed = True

        dim_note = "match" if source_dims == target_dims else "DIFF"
        if args.strict_dimensions and source_dims != target_dims:
            failed = True
            row_failed = True

        status = "FAIL" if row_failed else "OK"
        print(f"{page}: {status} source={source_kind} {source_dims[0]}x{source_dims[1]} "
              f"target={target_kind} {target_dims[0]}x{target_dims[1]} dims={dim_note}")
        targets_found += 1

    print(f"checked={len(pages)} targets_found={targets_found}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
