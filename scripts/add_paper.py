#!/usr/bin/env python3
"""Add a readpaper HTML artifact to the site."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PAPERS_DIR = ROOT / "papers"


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "paper"


def extract_body(html: str) -> str:
    """Return inner HTML: full document body, or the fragment as-is."""
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return html.strip()


def strip_outer_wrappers(fragment: str) -> str:
    """Remove accidental html/head wrappers if pasted as fragment."""
    fragment = re.sub(r"(?is)<!DOCTYPE[^>]*>", "", fragment)
    fragment = re.sub(r"(?is)<html[^>]*>|</html>", "", fragment)
    fragment = re.sub(r"(?is)<head[^>]*>.*?</head>", "", fragment)
    return fragment.strip()


def rewrite_body_css(fragment: str) -> str:
    """Scope readpaper `body { ... }` rules to .readpaper-body."""
    return re.sub(
        r"(?m)^(\s*)body\s*\{",
        r"\1.readpaper-body {",
        fragment,
    )


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_page(
    *,
    title: str,
    fragment: str,
    arxiv: str,
    pdf: str,
    base: str,
) -> str:
    links = []
    if arxiv:
        links.append(f'<a href="{escape(arxiv)}" target="_blank" rel="noopener">arXiv</a>')
    if pdf:
        links.append(f'<a href="{escape(pdf)}" target="_blank" rel="noopener">PDF</a>')
    links_html = (
        f'<div class="article-links">{"".join(links)}</div>' if links else ""
    )
    if base:
        base = base.rstrip("/")
        home = f"{base}/"
        site_css = f"{base}/assets/site.css"
    else:
        home = "../../"
        site_css = "../../assets/site.css"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)} — Paper Reading</title>
  <link rel="stylesheet" href="{site_css}" />
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <div>
        <a class="site-logo" href="{home}">← Paper Reading</a>
      </div>
    </div>
  </header>
  <main>
    {links_html}
    <article class="readpaper-body">
{fragment}
    </article>
  </main>
</body>
</html>
"""


def upsert_catalog(
    catalog: dict,
    *,
    slug: str,
    title: str,
    subtitle: str,
    paper_date: str,
    tags: list[str],
    arxiv: str,
    pdf: str,
    tldr: str,
) -> None:
    papers = catalog.setdefault("papers", [])
    entry = {
        "slug": slug,
        "title": title,
        "subtitle": subtitle,
        "date": paper_date,
        "tags": tags,
        "arxiv": arxiv,
        "pdf": pdf,
        "tldr": tldr,
    }
    for i, p in enumerate(papers):
        if p.get("slug") == slug:
            papers[i] = {**p, **entry}
            return
    papers.append(entry)


def main() -> int:
    parser = argparse.ArgumentParser(description="Add readpaper HTML to the site.")
    parser.add_argument("html_file", type=Path, help="readpaper HTML artifact path")
    parser.add_argument("--title", required=True, help="Paper title for catalog")
    parser.add_argument("--slug", help="URL slug (default: derived from title)")
    parser.add_argument("--subtitle", default="", help="Short subtitle")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--arxiv", default="", help="arXiv URL")
    parser.add_argument("--pdf", default="", help="PDF URL")
    parser.add_argument("--tldr", default="", help="One-line summary for index card")
    parser.add_argument("--force", action="store_true", help="Overwrite existing slug")
    args = parser.parse_args()

    src = args.html_file.expanduser().resolve()
    if not src.is_file():
        print(f"Error: file not found: {src}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    dest_dir = PAPERS_DIR / slug
    dest_file = dest_dir / "index.html"

    if dest_file.exists() and not args.force:
        print(f"Error: {dest_file} exists. Use --force to overwrite.", file=sys.stderr)
        return 1

    raw = src.read_text(encoding="utf-8")
    fragment = rewrite_body_css(strip_outer_wrappers(extract_body(raw)))

    site = load_json(DATA_DIR / "site.json")
    base = (site.get("base") or "").rstrip("/")
    page = build_page(
        title=args.title,
        fragment=fragment,
        arxiv=args.arxiv,
        pdf=args.pdf,
        base=base,
    )

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(page, encoding="utf-8")

    catalog = load_json(DATA_DIR / "papers.json")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    upsert_catalog(
        catalog,
        slug=slug,
        title=args.title,
        subtitle=args.subtitle,
        paper_date=args.date,
        tags=tags,
        arxiv=args.arxiv,
        pdf=args.pdf,
        tldr=args.tldr,
    )
    save_json(DATA_DIR / "papers.json", catalog)

    print(f"Wrote {dest_file}")
    print(f"Updated {DATA_DIR / 'papers.json'}")
    print(f"Preview: python -m http.server 8080  (then open /papers/{slug}/)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
