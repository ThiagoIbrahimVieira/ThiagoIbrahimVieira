"""
make_ascii_svg.py — convert prepped grayscale → self-typing monochrome ASCII SVG.
"""
from pathlib import Path
import math
from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright(sparse)→dark(dense)
COLS, ROWS = 100, 53
FONT_W, FONT_H = 7.5, 13     # approximate char cell (px)
FILL = "#c0c0c0"             # light gray — clean terminal look

# Delay constants  (ms)
ROW_INTERVAL = 45             # ms between each row's first char
COL_INTERVAL = 6              # ms between each char within a row
CURSOR_WIPE = 120             # extra ms for the horizontal wipe edge


def pixel_to_glyph(p: int) -> str:
    idx = (p * (len(RAMP) - 1)) // 255
    return RAMP[idx]


def main() -> None:
    src = Path(__file__).parent / "source-prepped.png"
    if not src.exists():
        raise SystemExit("run prep_photo.py first")

    img = Image.open(src).convert("L")
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    data = [img.getpixel((c, r)) for r in range(ROWS) for c in range(COLS)]

    lines: list[str] = []
    total_dur = ROWS * (ROW_INTERVAL + COLS * COL_INTERVAL + CURSOR_WIPE) + 300

    for r in range(ROWS):
        row_glyphs = ""
        row_pixels = data[r * COLS:(r + 1) * COLS]
        for c, p in enumerate(row_pixels):
            g = pixel_to_glyph(p)
            g = g if g.strip() else " "  # keep space from ramp
            row_glyphs += g.replace(" ", "\u00a0")  # nbsp so SVG keeps whitespace
        # Re-wrap spaces as real spaces — SMIL clip handles blank rows fine
        row_glyphs = "".join("\u00a0" if ch == " " else ch for ch in row_glyphs)

        row_delay = r * ROW_INTERVAL
        row_end = row_delay + COLS * COL_INTERVAL + CURSOR_WIPE

        lines.append(f"""  <g transform="translate(0,{r*FONT_H})">
   <clipPath id="c{r}">
    <rect x="0" y="0" width="0" height="{FONT_H}">
     <animate attributeName="width" from="0" to="{COLS*FONT_W}"
      begin="{row_delay}ms" dur="{COLS*COL_INTERVAL + CURSOR_WIPE}ms" fill="freeze" />
    </rect>
   </clipPath>
   <text clip-path="url(#c{r})" x="0" y="{FONT_H-3}" fill="{FILL}"
         font-family="monospace,Courier New,Courier" font-size="13">{row_glyphs}</text>
  </g>""")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {COLS*FONT_W} {ROWS*FONT_H}"
     width="{COLS*FONT_W}" height="{ROWS*FONT_H}">
  <rect width="100%" height="100%" fill="#0d1117" />
{chr(10).join(lines)}
</svg>"""

    out = Path(__file__).parent.parent / "avi-ascii.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()