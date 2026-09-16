"""Render `docs/GUIDA_START_IIDS.md` to a formatted PDF (issue #8 follow-up).

The Markdown file is the single source of truth (versioned, kept in sync
with the rest of `docs/` the same way ADRs and the ROADMAP are); this
script is the reproducible build step, not a hand-authored PDF. Requires
the optional `docs` dependency group: `pip install -e .[docs]`.

Usage::

    python3 -m scripts.build_guide_pdf --out dist/GUIDA_START_IIDS.pdf
"""
from __future__ import annotations

import argparse
import pathlib

import markdown
from weasyprint import HTML

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "docs" / "GUIDA_START_IIDS.md"

CSS = """
@page {
    size: A4;
    margin: 2.2cm 2cm 2.4cm 2cm;
    @bottom-center {
        content: "START IIDS — Guida allo strumento · pagina " counter(page) " di " counter(pages);
        font-size: 8.5pt;
        color: #8A8A8A;
    }
}
body {
    font-family: 'DejaVu Sans', 'Segoe UI', sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1A1A1A;
}
h1 { color: #1F3864; font-size: 20pt; border-bottom: 3px solid #67C271; padding-bottom: 6px; }
h2 { color: #1F3864; font-size: 14.5pt; margin-top: 26px; border-bottom: 1px solid #ddd; padding-bottom: 3px; }
h3 { color: #1F3864; font-size: 12pt; margin-top: 16px; }
h1:first-of-type { margin-top: 0; }
a { color: #3E8A48; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 16px; font-size: 9pt; }
th, td { border: 1px solid #ddd; padding: 5px 7px; text-align: left; vertical-align: top; }
th { background: #1A1A1A; color: #fff; }
tr:nth-child(even) { background: #F7F8F6; }
blockquote { border-left: 3px solid #67C271; margin: 10px 0; padding: 4px 14px; color: #444; background: #F4F5F3; }
code { background: #F0F0EE; color: #1A1A1A; padding: 1px 4px; border-radius: 3px; font-size: 9pt; }
img { max-width: 100%; border: 1px solid #ddd; border-radius: 6px; margin: 8px 0 4px; }
hr { border: none; border-top: 1px solid #ddd; margin: 18px 0; }
.cover {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 24cm;
    text-align: center;
}
.cover .brandmark { width: 90px; height: 90px; margin-bottom: 24px; }
.cover h1 { border: none; font-size: 26pt; margin: 0; }
.cover .subtitle { font-size: 13pt; color: #444; margin-top: 8px; }
.cover .meta { margin-top: 40px; font-size: 10pt; color: #667; line-height: 1.8; }
"""

COVER_HTML = """
<div class="cover">
  <svg class="brandmark" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="4" width="92" height="92" fill="none" stroke="#67C271" stroke-width="10"/>
    <polygon points="50,22 61,39 39,39" fill="#67C271"/>
    <polygon points="35,43 65,43 71,55 29,55" fill="#67C271"/>
    <polygon points="26,59 74,59 80,71 20,71" fill="#67C271"/>
    <polygon points="18,75 82,75 88,86 12,86" fill="#67C271"/>
  </svg>
  <h1>START IIDS</h1>
  <div class="subtitle">Intelligent Industry Digital Shadow — Guida allo strumento</div>
  <div class="meta">
    Progetto START | SusTainable dAta-dRiven manufacTuring<br>
    DM 31 dicembre 2021 — Accordi per l'Innovazione<br>
    Versione 1.0 — 2026-09-16
  </div>
</div>
"""


def build(source_path: pathlib.Path, out_path: pathlib.Path) -> None:
    text = source_path.read_text(encoding="utf-8")
    body_html = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head>" \
           f"<body>{COVER_HTML}{body_html}</body></html>"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # base_url = docs/ so relative image paths (assets/guida/...) resolve.
    HTML(string=html, base_url=str(source_path.parent)).write_pdf(str(out_path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, default=SOURCE_PATH)
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("dist/GUIDA_START_IIDS.pdf"))
    args = parser.parse_args()
    build(args.source, args.out)
    print(f"Guida PDF scritta in {args.out}")


if __name__ == "__main__":
    main()
