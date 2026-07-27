"""
make_info_card.py — neofetch-style info card SVG, line-by-line fade-in.
"""
from pathlib import Path
import os

WIDTH, HEIGHT = 490, 260
BG = "#161b22"
ACCENT = "#58a6ff"
LABEL = "#8b949e"
VALUE = "#e6edf3"
LINE_H = 22
PAD = 18
FONT_FAM = "monospace,JetBrains Mono,Fira Code,Consolas"

# Content — edit here
ROWS = [
    ("OS", "Windows 11"),
    ("Host", "ThiagoIbrahimVieira"),
    ("Kernel", "10.0.26100"),
    ("Shell", "PowerShell 7"),
    ("", ""),
    ("Role", "Estudante de TI"),
    ("Stack", "Python, Java, TypeScript, Full Stack"),
    ("", ""),
    ("Highlights", "Programador de 16 anos"),
    ("", "  construindo springboards pro futuro"),
]

STATIC = os.getenv("STATIC") == "1"


def text_el(x: int, y: int, label: str, value: str, idx: int) -> str:
    if STATIC:
        return f"""<g>
  <text x="{x}" y="{y}" fill="{LABEL}" font-family="{FONT_FAM}" font-size="13">{label}</text>
  <text x="{x+80}" y="{y}" fill="{VALUE}" font-family="{FONT_FAM}" font-size="13">{value}</text>
 </g>"""

    delay = idx * 120
    return f"""<g opacity="0">
  <text x="{x}" y="{y}" fill="{LABEL}" font-family="{FONT_FAM}" font-size="13">{label}</text>
  <text x="{x+80}" y="{y}" fill="{VALUE}" font-family="{FONT_FAM}" font-size="13">{value}</text>
  <animate attributeName="opacity" from="0" to="1" begin="{delay}ms" dur="300ms" fill="freeze"/>
  <animateTransform attributeName="transform" type="translate" from="20,0" to="0,0"
    begin="{delay}ms" dur="300ms" fill="freeze"/>
 </g>"""


def main() -> None:
    title_h = 28
    svg_lines = [
        f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     width="{WIDTH}" height="{HEIGHT}">
  <rect width="100%" height="100%" rx="6" fill="{BG}" />
  <rect x="0" y="0" width="{WIDTH}" height="{title_h}" rx="6" fill="#21262d" />
  <circle cx="12" cy="{title_h//2}" r="5" fill="#ff5f57" />
  <circle cx="28" cy="{title_h//2}" r="5" fill="#ffbd2e" />
  <circle cx="44" cy="{title_h//2}" r="5" fill="#28ca42" />
  <text x="{WIDTH//2}" y="{title_h//2+4}" text-anchor="middle"
        fill="{ACCENT}" font-family="{FONT_FAM}" font-size="12">~/thiago@github $ whoami</text>""",
    ]

    for i, (label, value) in enumerate(ROWS):
        y = title_h + 22 + i * LINE_H
        if not label and not value:
            continue
        svg_lines.append(text_el(PAD, y, label, value, i))

    svg_lines.append("</svg>")
    out = Path(__file__).parent.parent / "info-card.svg"
    out.write_text("\n".join(svg_lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()