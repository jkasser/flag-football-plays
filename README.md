# Flag Football Play Designer

A single-page, no-build play designer for flag football. Open `index.html` in a browser.

- **Players:** set how many are on the field (1–11), name each bubble, and pick its color.
- **Draw routes:** press on a player and drag. The freehand line is cleaned up into crisp cuts and finished with an arrow.
- **Move players:** switch to Move mode and drag bubbles to set the formation. Routes move with them.
- **Undo / Clear routes / Reset formation**, plus **Download PNG** to share the play.

Your current play is saved automatically in the browser's local storage.

## Wristband cards

`wristband.py` turns exported play PNGs into a printable PDF of cards for a 3-window QB wristband
(Top / Inside / Bottom). Plays are numbered in the order given, spread evenly across the windows, and
all cropped to the same part of the field so they're drawn at the same scale.

```
pip install pymupdf pillow numpy
python wristband.py --card 4.5x2.75 --out wristband-plays.pdf play1.png play2.png ...
```

Print at 100% / "Actual size" and cut on the dashed lines. Change `--card` to match your band's window.
