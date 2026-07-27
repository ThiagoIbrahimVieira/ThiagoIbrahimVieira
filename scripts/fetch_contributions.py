"""
fetch_contributions.py — scrape public contribution calendar → data/contributions.json
Parses the new <td class="ContributionCalendar-day" data-date data-level> format.
No token needed. Uses https://github.com/users/<user>/contributions
"""
from pathlib import Path
import json
import re
import requests
from bs4 import BeautifulSoup

USERNAME = "ThiagoIbrahimVieira"
URL = f"https://github.com/users/{USERNAME}/contributions"


def main() -> None:
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    days = []
    total_year = 0

    # Find the total contributions text: "97 contributions in the last year"
    total_match = re.search(r"(\d+)\s+contributions?\s+in\s+the\s+last\s+year", r.text)
    if total_match:
        total_year = int(total_match.group(1))

    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        level_str = td.get("data-level", "0")
        if not date:
            continue
        level = int(level_str)
        # We don't have exact daily counts; infer from level:
        # GitHub levels: 0=none, 1=1-3, 2=4-10, 3=11-20, 4=21+
        # For streak calculations, treat level > 0 as "active day"
        days.append({"date": date, "level": level, "active": level > 0})

    if not days:
        raise SystemExit("no day cells scraped — GitHub page format changed?")

    days.sort(key=lambda x: x["date"])

    # derived stats (using active = level > 0)
    cur = 0
    for d in reversed(days):
        if d["active"]:
            cur += 1
        elif cur > 0:
            break

    longest = run = 0
    for d in days:
        if d["active"]:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    best_day = max(days, key=lambda x: x["level"]) if days else None

    # monthly totals (count of active days)
    monthly = {}
    for d in days:
        m = d["date"][:7]
        monthly[m] = monthly.get(m, 0) + (1 if d["active"] else 0)

    payload = {
        "username": USERNAME,
        "days": days,
        "total": total_year,
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly": monthly,
    }

    out = Path(__file__).parent.parent / "data" / "contributions.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {out}  ({len(days)} days, total={total_year})")


if __name__ == "__main__":
    main()