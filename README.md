# 🏈 Flag Football Play Designer

Draw flag football plays in the browser, then print them as cards for a QB wristband.

- **`index.html`**: a single-page play designer. No build step and no dependencies; just open it.
- **`wristband.py`**: turns exported plays into a printable PDF sized for a 3-window wristband.

## Play designer

Open `index.html` in any browser (desktop or phone).

- **Players:** set how many are on the field (1–11). Each one gets a default spot and name (QB, C, X, Z, Y, …).
- **Names & colors:** rename any bubble and pick its color in the sidebar. Bubbles widen to fit longer names.
- **Draw routes:** in ✏️ **Draw** mode, press on a player and drag. When you let go, the freehand line is
  cleaned up into crisp cuts and finished with an arrow. Drawing again replaces that player's route.
- **Move players:** in ✋ **Move** mode, drag bubbles to set the formation. Their routes move with them.
- **Undo** (Ctrl+Z), clear one route (✕) or all routes, and **Reset formation**.
- **Download PNG:** saves the play with its name in a title bar, ready to share or print.
- **Shortcuts:** `D` draw, `M` move, `Ctrl+Z` undo.

Your current play is saved automatically in the browser's local storage, so a refresh won't lose it.

## Wristband cards

`wristband.py` lays out the PNGs from **Download PNG** on cards for a QB wristband with three windows
(**Top / Inside / Bottom**), on one Letter-size page.

```bash
pip install pymupdf pillow numpy

# Two plays per window, in the order given (numbered 1–6)
python wristband.py --out wristband.pdf rz-whip.png blitz-beater.png posts-under.png \
    slants.png qb-eligible.png screen-pass-option.png

# Same thing for a black-and-white printer
python wristband.py --bw --out wristband-bw.pdf rz-whip.png blitz-beater.png ...
```

How it lays them out:

- Plays are **numbered in the order you list them**, so the coach can call them by number.
- They're **spread evenly** across the three windows (e.g. 6 plays → 2 per window), and partly filled
  rows are centered.
- Every play is **cropped to the same part of the field** (wherever any route goes), so all plays are
  drawn at the same scale.
- The play name sits in a dark strip above each diagram, so it never covers a route.

| Option | What it does |
|---|---|
| `--card WxH` | Card size in inches. Default `4.5x2.75`; measure your band's window and change it to match. |
| `--bw` | Black-and-white mode: white field, dark routes and players. Use it for B&W printers, where the green field otherwise prints as a dark gray block and the red/purple routes disappear into it. |
| `--per-window N` | Fix how many plays go on each card instead of spreading them evenly. |
| `--fill` | Stretch diagrams sideways to fill each card. Depth stays accurate, but bubbles become ovals. Pairs well with `--per-window 4`. |
| `--out FILE` | Output PDF path (default `wristband-plays.pdf`). |

### Printing tips

- Print at **100% / "Actual size"**, not "Fit to page", or the cards come out smaller than the window.
- Cut on the dashed lines. The TOP / INSIDE / BOTTOM labels sit outside the cut line.
- **Two plays per window** is the most readable layout. At four per window, routes are still clear, but
  the letters inside the bubbles are too small to read, so you'll read players by color or position.
- Print one test page and check it at arm's length before cutting a full set.
