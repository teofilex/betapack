"""Kompresuje mobilne homepage slike iz PNG u JPEG ~150 KB."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

PUBLIC = Path(__file__).resolve().parents[1] / 'public'
TARGET_BYTES = 150 * 1024

SOURCES = (
    ('steelMobileVersion.png', 'steelMobileVersion.jpg', 1200),
    ('amabalazaMobileVersion.png', 'ambalazaMobileVersion.jpg', 1280),
)


def compress(src_name: str, out_name: str, max_width: int) -> None:
    img = Image.open(PUBLIC / src_name).convert('RGB')
    if img.width > max_width:
        height = int(img.height * max_width / img.width)
        img = img.resize((max_width, height), Image.Resampling.LANCZOS)

    lo, hi = 40, 90
    best: tuple[int, int, bytes] | None = None
    while lo <= hi:
        quality = (lo + hi) // 2
        buffer = io.BytesIO()
        img.save(buffer, 'JPEG', quality=quality, optimize=True, progressive=True)
        size = buffer.tell()
        if size <= TARGET_BYTES:
            best = (quality, size, buffer.getvalue())
            lo = quality + 1
        else:
            hi = quality - 1

    if best is None:
        buffer = io.BytesIO()
        img.save(buffer, 'JPEG', quality=60, optimize=True, progressive=True)
        best = (60, buffer.tell(), buffer.getvalue())

    (PUBLIC / out_name).write_bytes(best[2])
    print(f'{out_name}: {best[1] / 1024:.1f} KB (q={best[0]}, {img.width}x{img.height})')


if __name__ == '__main__':
    for src, out, width in SOURCES:
        compress(src, out, width)
