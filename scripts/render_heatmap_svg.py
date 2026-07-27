"""
render_heatmap_svg.py — 53-week × 7-day heatmap from data/contributions.json → contrib-heatmap.svg
"""
from pathlib import Path
import json
from datetime import date, timedelta

# GitHub levels: 0=none, 1=low, 2=mid, 3=high, 4=max
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL = 13
GAP = 4
SIDE_PAD = 28
TOP_PAD = 16
MONTH_H = 10
LEGEND_H = 28
FOOTER_H = 24
TOTAL_W = 53 * (CELL + GAP) + SIDE_PAD * 2
TOTAL_H = TOP_PAD + MONTH_H + 7 * (CELL + GAP) + LEGEND_H + FOOTER_H

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def main() -> None:
    data_path = Path(__file__).parent.parent / "data" / "contributions.json"
    if not data_path.exists():
        raise SystemExit("run fetch_contributions.py first")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    days = {d["date"]: d for d in data["days"]}
    if not data["days"]:
        raise SystemExit("no days")

    first = date.fromisoformat(data["days"][0]["date"])
    last = date.fromisoformat(data["days"][-1]["date"])
    # back up to Sunday
    start = first
    while start.weekday() != 6:
        start -= timedelta(days=1)

    els = []
    week = 0
    cur = start
    last_month = -1
    end = last + timedelta(days=(6 - last.weekday()) % 7)

    while cur <= end:
        # row: Sun=0..Sat=6
        row = (cur.weekday() + 1) % 7
        ds = cur.isoformat()
        lv = days.get(ds, {}).get("level", 0)
        color = PALETTE[min(lv, 4)]
        x = SIDE_PAD + week * (CELL + GAP)
        y = TOP_PAD + MONTH_H + row * (CELL + GAP)

        # month label on the first row when month changes
        if row == 0 and cur.month != last_month:
            last_month = cur.month
            els.append(f'<text x="{x}" y="{TOP_PAD + 9}" fill="#8b949e" '
                       f'font-family="monospace" font-size="10">{MONTHS[cur.month]}</text>')

        delay = row * 40 + week * 14
        els.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0,-180" to="0,0" begin="{delay}ms" dur="450ms" fill="freeze"/>'
            f'</rect>'
        )

        cur += timedelta(days=1)
        if row == 6:  # after Saturday → next week column
            week += 1

    # day-of-week labels
    for i, name in enumerate(["Mon", "Wed", "Fri"]):
        ry = (i * 2 + 1)  # Mon=1, Wed=3, Fri=5
        y = TOP_PAD + MONTH_H + ry * (CELL + GAP) + 10
        els.append(f'<text x="2" y="{y}" fill="#484f58" '
                   f'font-family="monospace" font-size="9">{name}</text>')

    # legend
    ly = TOP_PAD + MONTH_H + 7 * (CELL + GAP) + 10
    els.append(f'<text x="{SIDE_PAD}" y="{ly + 9}" fill="#8b949e" '
               f'font-family="monospace" font-size="10">Less</text>')
    for i, c in enumerate(PALETTE):
        lx = SIDE_PAD + 40 + i * (CELL + GAP)
        els.append(f'<rect x="{lx}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    els.append(f'<text x="{SIDE_PAD + 40 + len(PALETTE) * (CELL + GAP) + 4}" y="{ly + 9}" '
               f'fill="#8b949e" font-family="monospace" font-size="10">More</text>')

    # footer
    fy = ly + LEGEND_H + 4
    total = data.get("total", 0)
    streak = data.get("longest_streak", 0)
    els.append(f'<text x="{SIDE_PAD}" y="{fy + 12}" fill="#8b949e" '
               f'font-family="monospace" font-size="11">'
               f'{total:,} contributions in the last year · longest streak: {streak} days</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTAL_W} {TOTAL_H}" '
           f'width="{TOTAL_W}" height="{TOTAL_H}">\n'
           f'<rect width="100%" height="100%" fill="#0d1117" rx="8" />\n'
           + "\n".join(els) + "\n"
           f"</svg>")

    out = Path(__file__).parent.parent / "contrib-heatmap.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()