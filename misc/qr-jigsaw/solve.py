#!/usr/bin/env python3
import io
import urllib.request

from PIL import Image
from pyzbar import pyzbar
import itertools

HOST = "http://localhost:1337"

img = Image.new("RGBA", (250, 250))

def load_piece(i):
    try:
        data = urllib.request.urlopen(f"{HOST}/pieces/{i}.png", timeout=10).read()
        return Image.open(io.BytesIO(data))
    except Exception:
        return Image.open(f"pieces/{i}.png")

pieces = [load_piece(i + 1) for i in range(25)]
img.paste(pieces[18], (0, 0))
img.paste(pieces[16], (50, 0))
img.paste(pieces[2], (100, 0))
img.paste(pieces[0], (150, 0))
img.paste(pieces[19], (200, 0))
img.paste(pieces[10], (0, 50))
img.paste(pieces[9], (50, 50))
img.paste(pieces[3], (100, 50))
img.paste(pieces[13], (150, 50))
img.paste(pieces[7], (200, 50))
img.paste(pieces[8], (0, 100))
img.paste(pieces[23], (50, 100))
img.paste(pieces[24], (0, 150))
img.paste(pieces[14], (50, 150))
img.paste(pieces[11], (0, 200))
img.paste(pieces[4], (50, 200))
img.paste(pieces[21], (200, 200))

perm_right = [20, 12]
perm_bottom = [5, 6]
perm_center = [1, 17, 22, 15]


for right_chosen in itertools.permutations(perm_right):
    for bottom_chosen in itertools.permutations(perm_bottom):
        for center_chosen in itertools.permutations(perm_center):
            img_copy = img.copy()

            img_copy.paste(pieces[right_chosen[0]], (200, 100))
            img_copy.paste(pieces[right_chosen[1]], (200, 150))

            img_copy.paste(pieces[bottom_chosen[0]], (100, 200))
            img_copy.paste(pieces[bottom_chosen[1]], (150, 200))

            img_copy.paste(pieces[center_chosen[0]], (100, 100))
            img_copy.paste(pieces[center_chosen[1]], (100, 150))
            img_copy.paste(pieces[center_chosen[2]], (150, 100))
            img_copy.paste(pieces[center_chosen[3]], (150, 150))

            # img_copy.save("out.png")
            if decoded := pyzbar.decode(img_copy):
                print(decoded[0].data.decode())
