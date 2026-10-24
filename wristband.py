"""Build a printable wristband PDF from play PNGs exported by the play designer.

Plays are spread across the band's windows (Top / Inside / Bottom), numbered so
the coach can call them by number. Every play is cropped to the same part of
the field (wherever any route goes), so they're all drawn at the same scale.
Print at 100% / "Actual size", then cut on the dashed lines.

    python wristband.py ~/Downloads/simmons.png ~/Downloads/slants.png ...
    python wristband.py --card 4.5x2.75 --out plays.pdf *.png
"""
import argparse
import io
import math
import os

import numpy as np
import pymupdf
from PIL import Image

PT = 72  # points per inch
WINDOWS = ["TOP", "INSIDE", "BOTTOM"]
TITLE_BAND = 88 / 1088  # dark title strip on exported PNGs, as a fraction of height
QB_Y = 470 / 500        # bottom of the default QB bubble, as a fraction of field height
PAD = 0.03              # padding around the used area, as a fraction of field width
LABEL_H = 0.15 * PT     # name strip above each diagram


def load_fields(paths):
    """Load each PNG with the title strip cut off, all resized to the first one's size."""
    imgs = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        w, h = img.size
        img = img.crop((0, round(h * TITLE_BAND), w, h))
        if imgs and img.size != imgs[0].size:
            img = img.resize(imgs[0].size)
        imgs.append(img)
    return imgs


def shared_crop(imgs):
    """Box covering every player and route across all plays.

    The per-pixel median of all plays is close to an empty field, so anything
    that differs from it is a route or a player.
    """
    w, h = imgs[0].size
    stack = np.stack([np.asarray(i, dtype=np.int16) for i in imgs])
    if len(imgs) >= 3:
        blank = np.median(stack, axis=0)
        used = (np.abs(stack - blank).max(axis=3) > 60).any(axis=0)
    else:
        used = np.zeros((h, w), bool)
    used[round(h * QB_Y) - 1, w // 2] = True  # always keep the backfield down to the QB
    ys, xs = np.nonzero(used)
    pad = round(w * PAD)
    return (max(0, xs.min() - pad), max(0, ys.min() - pad),
            min(w, xs.max() + pad), min(h, ys.max() + pad))


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def pick_grid(n_plays, n_windows, card_w, card_h, aspect):
    """Choose the cols x rows per window that makes each play diagram biggest."""
    best = None
    for cols in range(1, 7):
        for rows in range(1, 5):
            if cols * rows * n_windows < n_plays:
                continue
            img_h = min(card_w / cols / aspect, card_h / rows - LABEL_H)
            key = (img_h, -cols * rows)
            if best is None or key > best[0]:
                best = (key, cols, rows)
    return best[1], best[2]


def play_name(path):
    return os.path.splitext(os.path.basename(path))[0].replace("-", " ").replace("_", " ").upper()


def build(paths, out, card_w_in, card_h_in):
    windows = len(WINDOWS)
    card_w, card_h = card_w_in * PT, card_h_in * PT
    imgs = load_fields(paths)
    box = shared_crop(imgs)
    aspect = (box[2] - box[0]) / (box[3] - box[1])
    cols, rows = pick_grid(len(imgs), windows, card_w, card_h, aspect)
    if len(imgs) > cols * rows * windows:
        raise SystemExit(f"Too many plays ({len(imgs)}) for {windows} windows")
    per_card = math.ceil(len(imgs) / windows)  # spread plays evenly so every window gets used

    doc = pymupdf.open()
    page = doc.new_page(width=8.5 * PT, height=11 * PT)
    page.insert_text((0.5 * PT, 0.6 * PT), "Wristband play cards", fontsize=16, fontname="hebo")
    page.insert_text((0.5 * PT, 0.85 * PT),
                     f'Print at 100% / "Actual size". Cut on the dashed lines. Each card is {card_w_in}" x {card_h_in}".',
                     fontsize=9, color=(0.35, 0.35, 0.35))

    gap = 0.35 * PT
    x0 = (8.5 * PT - card_w) / 2
    y = 1.15 * PT
    cell_w, cell_h = card_w / cols, card_h / rows
    img_h = min(cell_w / aspect, cell_h - LABEL_H) - 2
    img_w = img_h * aspect
    for w_i, window in enumerate(WINDOWS):
        card = pymupdf.Rect(x0, y, x0 + card_w, y + card_h)
        page.draw_rect(card, color=(0.4, 0.4, 0.4), width=0.6, dashes="[4 3] 0")
        # Window label outside the cut line so it doesn't end up on the card
        page.insert_text((card.x1 + 6, card.y0 + 12), window, fontsize=10, fontname="hebo",
                         color=(0.4, 0.4, 0.4))

        count = max(0, min(per_card, len(imgs) - w_i * per_card))
        rows_used = math.ceil(count / cols)
        for slot in range(count):
            idx = w_i * per_card + slot
            row, col = divmod(slot, cols)
            # Center partly filled rows, and center the used rows within the card
            in_row = min(cols, count - row * cols)
            left = card.x0 + (col + (cols - in_row) / 2) * cell_w + (cell_w - img_w) / 2
            top = card.y0 + (row + (rows - rows_used) / 2) * cell_h + (cell_h - img_h - LABEL_H) / 2
            rect = pymupdf.Rect(left, top + LABEL_H, left + img_w, top + LABEL_H + img_h)
            page.insert_image(rect, stream=png_bytes(imgs[idx].crop(box)))

            # Number + name in a dark strip above the field, like the designer's export
            label = f"{idx + 1}  {play_name(paths[idx])}"
            size = 8
            while pymupdf.get_text_length(label, "hebo", size) > img_w - 7 and size > 5:
                size -= 0.5
            page.draw_rect(pymupdf.Rect(left, top, left + img_w, top + LABEL_H), color=None, fill=(0.12, 0.14, 0.16))
            page.insert_text((left + 3.5, top + LABEL_H / 2 + size * 0.36), label, fontsize=size, fontname="hebo",
                             color=(1, 1, 1))
        y += card_h + gap

    doc.save(out)
    print(f"Wrote {out}: {len(imgs)} plays, {cols}x{rows} per window, card {card_w_in}x{card_h_in} in, "
          f"diagrams {img_w / PT:.2f}x{img_h / PT:.2f} in")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+", help="play PNGs, in the order to number them")
    ap.add_argument("--card", default="4.5x2.75", help="card size in inches, WIDTHxHEIGHT (default 4.5x2.75)")
    ap.add_argument("--out", default="wristband-plays.pdf")
    args = ap.parse_args()
    w, h = (float(v) for v in args.card.lower().split("x"))
    build(args.images, args.out, w, h)
