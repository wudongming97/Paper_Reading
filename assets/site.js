async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return res.json();
}

function resolveBase(site) {
  if (site.base !== undefined && site.base !== "") return site.base.replace(/\/$/, "");
  const parts = location.pathname.split("/").filter(Boolean);
  if (parts.length === 0) return "";
  const last = parts[parts.length - 1];
  if (last.endsWith(".html") || !last.includes(".")) parts.pop();
  return parts.length ? `/${parts.join("/")}` : "";
}

function assetUrl(base, rel) {
  const b = base || "";
  const r = rel.startsWith("/") ? rel : `/${rel}`;
  return `${b}${r}`;
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso + "T12:00:00");
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function renderTags(tags) {
  if (!tags || !tags.length) return "";
  return `<div class="tags">${tags
    .map((t) => `<span class="tag">${escapeHtml(t)}</span>`)
    .join("")}</div>`;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function initHome() {
  const [site, catalog] = await Promise.all([
    loadJson(assetUrl("", "data/site.json")),
    loadJson(assetUrl("", "data/papers.json")),
  ]);

  const base = resolveBase(site);
  document.title = site.title;
  document.getElementById("site-title").textContent = site.title;
  document.getElementById("site-tagline").textContent = site.tagline || "";
  document.getElementById("hero-title").textContent = site.title;
  document.getElementById("hero-desc").textContent = site.tagline || "";

  const papers = [...(catalog.papers || [])].sort(
    (a, b) => (b.date || "").localeCompare(a.date || "")
  );

  const grid = document.getElementById("paper-grid");
  if (!papers.length) {
    grid.innerHTML = `
      <div class="empty-state">
        <p>还没有论文。用 readpaper 生成 HTML 后运行：</p>
        <p><code>python scripts/add_paper.py your.html --title "..." --slug my-paper</code></p>
      </div>`;
    return;
  }

  grid.innerHTML = papers
    .map((p) => {
      const href = assetUrl(base, `papers/${p.slug}/`);
      const links = [p.arxiv, p.pdf].filter(Boolean);
      return `
        <a class="paper-card" href="${href}">
          <h2>${escapeHtml(p.title)}</h2>
          ${p.subtitle ? `<div class="meta">${escapeHtml(p.subtitle)}</div>` : ""}
          <p class="tldr">${escapeHtml(p.tldr || "")}</p>
          <div class="meta">${formatDate(p.date)}${links.length ? " · 有外链" : ""}</div>
          ${renderTags(p.tags)}
        </a>`;
    })
    .join("");
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page === "home") initHome().catch(console.error);
});
