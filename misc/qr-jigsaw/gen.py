#!/usr/bin/env python3
import re
import secrets
from pathlib import Path

import qrcode
from qrcode.util import ALPHA_NUM
from PIL import Image

FLAG = "NHC/QR-I5NT-7H4T-R4ND0M/"
# Ensure version 1
assert len(FLAG) <= 25
assert all(c in ALPHA_NUM.decode() for c in FLAG)
GRID = 5
BOX_SIZE = 10
OUT = Path("pieces")


def make_qr(data: str) -> Image.Image:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=BOX_SIZE, border=2
    )
    qr.add_data(data)
    qr.make(fit=True)
    print(qr.data_list[0].mode)
    print(qr.version)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def split_sizes(length: int, max_size: int) -> list[int]:
    if max_size < 1:
        raise SystemExit("GRID must be >= 1")
    sizes = []
    remaining = length
    while remaining > 0:
        sizes.append(min(max_size, remaining))
        remaining -= sizes[-1]
    return sizes


def cut_squares(img: Image.Image) -> list[Image.Image]:
    widths = split_sizes(img.size[0], GRID * BOX_SIZE)
    heights = split_sizes(img.size[1], GRID * BOX_SIZE)
    xs, ys = [0], [0]
    for w in widths:
        xs.append(xs[-1] + w)
    for h in heights:
        ys.append(ys[-1] + h)

    squares = []
    for row in range(len(heights)):
        for col in range(len(widths)):
            box = (xs[col], ys[row], xs[col + 1], ys[row + 1])
            squares.append(img.crop(box))
    return squares


def write_index_constants(count: int, box_size: int, width: int, height: int) -> None:
    path = Path("index.html")
    html = path.read_text()
    replacements = {
        "PIECE_COUNT": count,
        "BOX_SIZE": box_size,
        "FULL_WIDTH": width,
        "FULL_HEIGHT": height,
    }
    for name, value in replacements.items():
        html, n = re.subn(rf"(const {name} = )\d+", rf"\g<1>{value}", html, count=1)
        if n != 1:
            raise SystemExit(f"index.html is missing {name} constant")
    path.write_text(html)
    print(f"wrote {replacements} into index.html")


def main() -> None:
    full = make_qr(FLAG)
    full.save("full.png")
    squares = cut_squares(full)
    secrets.SystemRandom().shuffle(squares)

    if OUT.exists():
        for old in OUT.glob("*.png"):
            old.unlink()
    OUT.mkdir(exist_ok=True)

    for i, square in enumerate(squares, start=1):
        path = OUT / f"{i}.png"
        square.save(path)
        print(f"wrote {path}")

    write_index_constants(len(squares), BOX_SIZE, full.size[0], full.size[1])

if __name__ == "__main__":
    main()
