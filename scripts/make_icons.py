"""Generate the app-package icons (color.png 192x192, outline.png 32x32).

Pure-stdlib PNG writer so the repo needs no image dependencies. The glyph is
three stacked bars joined by a spine — the scenario chain. Re-run any time:

    python scripts/make_icons.py
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ACCENT = (0x2E, 0x5E, 0x4E, 0xFF)  # matches manifest accentColor #2E5E4E
BAR = (0xE8, 0xF3, 0xEE, 0xFF)
WHITE = (0xFF, 0xFF, 0xFF, 0xFF)
CLEAR = (0, 0, 0, 0)

OUT_DIR = Path(__file__).resolve().parents[1] / "m365" / "appPackage"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def write_png(path: Path, pixels: list[list[tuple[int, int, int, int]]]) -> None:
    height, width = len(pixels), len(pixels[0])
    raw = b"".join(b"\x00" + b"".join(bytes(px) for px in row) for row in pixels)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
           + _chunk(b"IDAT", zlib.compress(raw, 9))
           + _chunk(b"IEND", b""))
    path.write_bytes(png)


def chain_glyph(size: int, fg: tuple, bg: tuple) -> list[list[tuple]]:
    """Three horizontal bars joined by a vertical spine, centered."""
    px = [[bg] * size for _ in range(size)]
    unit = size // 8
    bar_w, bar_h = 4 * unit, unit
    x0 = (size - bar_w) // 2
    spine_x = x0 + bar_w // 2
    ys = [2 * unit, 4 * unit - bar_h // 2, 5 * unit]
    for y in range(ys[0], ys[2] + bar_h):  # the spine
        for x in range(spine_x - max(1, unit // 4), spine_x + max(1, unit // 4)):
            px[y][x] = fg
    for y0 in ys:  # the bars
        for y in range(y0, y0 + bar_h):
            for x in range(x0, x0 + bar_w):
                px[y][x] = fg
    return px


def main() -> None:
    write_png(OUT_DIR / "color.png", chain_glyph(192, BAR, ACCENT))
    outline = chain_glyph(32, WHITE, CLEAR)
    write_png(OUT_DIR / "outline.png", outline)
    print(f"icons written to {OUT_DIR}")


if __name__ == "__main__":
    main()
