#!/usr/bin/env python3
"""Add a readpaper HTML artifact under papers/<category>/<slug>/."""

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
DEFAULT_CATEGORIES = ["LLM", "Agent", "Infra", "VLA", "WAM", "CV"]

CATEGORY_DESC = {
    "LLM": "大语言模型",
    "Agent": "智能体",
    "Infra": "训练与推理基础设施",
    "VLA": "视觉-语言-动作",
    "WAM": "世界模型 / 动作模型",
    "CV": "计算机视觉",
}


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


def categories(catalog: dict) -> list[str]:
    return catalog.get("categories") or DEFAULT_CATEGORIES


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
  <link rel="stylesheet" href="../../assets/site.css" />
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <a class="site-brand" href="../../">
        <span class="site-mark">P</span>
        <span>
          <span class="site-logo">Paper Reading</span>
          <span class="site-tagline">返回阅读列表</span>
        </span>
      </a>
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
    cats = categories(catalog)
    by_cat: dict[str, list[dict]] = {c: [] for c in cats}
    for p in catalog.get("papers", []):
        cat = p.get("category", "LLM")
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(p)

    pills = []
    for cat in cats:
        n = len(by_cat.get(cat, []))
        cls = "cat-pill has-papers" if n else "cat-pill"
        pills.append(
            f'<a class="{cls}" href="#{cat}" data-cat="{escape(cat)}">'
            f'{escape(cat)} <span class="count">{n}</span></a>'
        )
    pills_html = "\n      ".join(pills)
    latest = sorted(catalog.get("papers", []), key=lambda p: p.get("date", ""), reverse=True)
    latest_link = ""
    if latest:
        p = latest[0]
        latest_link = f"""        <a class="hero-latest" href="{escape(p.get("category", "LLM"))}/{escape(p["slug"])}/">
          <span>最近阅读</span>
          <strong>{escape(p["title"])}</strong>
          <em>{escape(p.get("subtitle", ""))}</em>
        </a>"""

    sections = []
    for cat in cats:
        papers = sorted(by_cat.get(cat, []), key=lambda p: p.get("date", ""), reverse=True)
        desc = escape(CATEGORY_DESC.get(cat, ""))
        if papers:
            items = []
            for p in papers:
                href = f"{cat}/{escape(p['slug'])}/"
                title = escape(p["title"])
                subtitle = escape(p.get("subtitle", ""))
                tldr = escape(p.get("tldr", ""))
                date_str = escape(p.get("date", ""))
                meta = f'<p class="meta">{subtitle}</p>' if subtitle else ""
                items.append(
                    f"""        <li>
          <a class="paper-card" href="{href}">
            <div class="paper-card-top">
              <span class="paper-date">{date_str}</span>
              <span class="paper-arrow" aria-hidden="true">→</span>
            </div>
            <h3>{title}</h3>
            {meta}
            <p class="tldr">{tldr}</p>
          </a>
        </li>"""
                )
            list_html = f"""      <ul class="paper-list">
{chr(10).join(items)}
      </ul>"""
        else:
            list_html = '      <p class="category-empty">暂无阅读记录</p>'

        sections.append(
            f"""    <section class="category" id="{escape(cat)}" data-cat="{escape(cat)}">
      <div class="category-header">
        <span class="category-badge">{escape(cat)}</span>
        <span class="category-desc">{desc}</span>
      </div>
{list_html}
    </section>"""
        )

    body = "\n".join(sections)
    total = len(catalog.get("papers", []))

    ROOT.joinpath("index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="个人论文阅读记录与 readpaper 中文讲解" />
  <title>Paper Reading — 论文阅读记录</title>
  <link rel="stylesheet" href="assets/site.css" />
</head>
<body>
  <header class="site-header">
    <div class="site-header-inner">
      <div class="site-brand">
        <span class="site-mark" aria-hidden="true">P</span>
        <span>
          <div class="site-logo">Paper Reading</div>
          <p class="site-tagline">我的论文阅读记录 · 共 {total} 篇</p>
        </span>
      </div>
    </div>
  </header>
  <main>
    <section class="hero">
      <div class="hero-copy">
        <p class="hero-kicker">Paper Reading</p>
        <h1>论文阅读笔记</h1>
      </div>
      <div class="hero-panel" aria-label="最近阅读">
{latest_link}
      </div>
    </section>
    <nav class="cat-nav" aria-label="论文分类">
      {pills_html}
    </nav>
{body}
  </main>
  <footer class="site-footer">Paper Reading · wudongming</footer>
</body>
</html>
""",
        encoding="utf-8",
    )


def upsert_catalog(
    catalog: dict,
    *,
    category: str,
    slug: str,
    title: str,
    subtitle: str,
    paper_date: str,
    tags: list[str],
    arxiv: str,
    pdf: str,
    tldr: str,
) -> None:
    if "categories" not in catalog:
        catalog["categories"] = DEFAULT_CATEGORIES
    papers = catalog.setdefault("papers", [])
    entry = {
        "category": category,
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
        if p.get("slug") == slug and p.get("category") == category:
            papers[i] = {**p, **entry}
            return
    papers.append(entry)


def main() -> int:
    parser = argparse.ArgumentParser(description="Add readpaper HTML to papers/<category>/<slug>/.")
    parser.add_argument("html_file", type=Path)
    parser.add_argument("--category", required=True, choices=DEFAULT_CATEGORIES)
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
    dest_dir = ROOT / args.category / slug
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
        category=args.category,
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
    print(f"URL path: {args.category}/{slug}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
