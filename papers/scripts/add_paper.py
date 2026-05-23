#!/usr/bin/env python3
"""Add a readpaper HTML artifact under papers/<slug>/."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "papers.json"


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "paper"


def extract_body(html: str) -> str:
    m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return html.strip()


def strip_outer_wrappers(fragment: str) -> str:
    fragment = re.sub(r"(?is)<!DOCTYPE[^>]*>", "", fragment)
    fragment = re.sub(r"(?is)<html[^>]*>|</html>", "", fragment)
    fragment = re.sub(r"(?is)<head[^>]*>.*?</head>", "", fragment)
    return fragment.strip()


def rewrite_body_css(fragment: str) -> str:
    return re.sub(r"(?m)^(\s*)body\s*\{", r"\1.readpaper-body {", fragment)


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_page(*, title: str, fragment: str, arxiv: str, pdf: str) -> str:
    links = []
    if arxiv:
        links.append(f'<a href="{escape(arxiv)}" target="_blank" rel="noopener">arXiv</a>')
    if pdf:
        links.append(f'<a href="{escape(pdf)}" target="_blank" rel="noopener">PDF</a>')
    links_html = (
        f'<div class="article-links">{"".join(links)}</div>' if links else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)} — Paper Reading</title>
  <link rel="stylesheet" href="../assets/site.css" />
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a class="site-logo" href="../">← Paper Reading</a>
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


def write_index(catalog: dict) -> None:
    papers = sorted(
        catalog.get("papers", []),
        key=lambda p: p.get("date", ""),
        reverse=True,
    )
    items = []
    for p in papers:
        slug = escape(p["slug"])
        title = escape(p["title"])
        subtitle = escape(p.get("subtitle", ""))
        tldr = escape(p.get("tldr", ""))
        date_str = escape(p.get("date", ""))
        sub = f'<div class="meta">{subtitle} · {date_str}</div>' if subtitle or date_str else ""
        items.append(
            f"""    <li>
      <a href="{slug}/">
        <h2>{title}</h2>
        {sub}
        <p class="tldr">{tldr}</p>
      </a>
    </li>"""
        )
    items_html = "\n".join(items) if items else "    <li><p>暂无论文</p></li>"

    ROOT.joinpath("index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Paper Reading</title>
  <link rel="stylesheet" href="assets/site.css" />
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <div class="site-logo">Paper Reading</div>
      <p class="site-tagline">readpaper 生成的可视化论文解读</p>
    </div>
  </header>
  <main>
    <section class="hero">
      <h1>论文解读</h1>
      <p>每篇论文一个子目录，由 readpaper 生成 HTML 后收录于此。</p>
    </section>
    <ul class="paper-list">
{items_html}
    </ul>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


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
    parser = argparse.ArgumentParser(description="Add readpaper HTML to papers/.")
    parser.add_argument("html_file", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug", help="URL slug (default: from title)")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--tags", default="")
    parser.add_argument("--arxiv", default="")
    parser.add_argument("--pdf", default="")
    parser.add_argument("--tldr", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    src = args.html_file.expanduser().resolve()
    if not src.is_file():
        print(f"Error: file not found: {src}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    dest_dir = ROOT / slug
    dest_file = dest_dir / "index.html"

    if dest_file.exists() and not args.force:
        print(f"Error: {dest_file} exists. Use --force.", file=sys.stderr)
        return 1

    raw = src.read_text(encoding="utf-8")
    fragment = rewrite_body_css(strip_outer_wrappers(extract_body(raw)))
    page = build_page(
        title=args.title,
        fragment=fragment,
        arxiv=args.arxiv,
        pdf=args.pdf,
    )

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file.write_text(page, encoding="utf-8")

    catalog = load_json(CATALOG_PATH)
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
    save_json(CATALOG_PATH, catalog)
    write_index(catalog)

    print(f"Wrote {dest_file}")
    print(f"Updated {CATALOG_PATH} and index.html")
    print(f"Preview: cd papers && python3 -m http.server 8080")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
