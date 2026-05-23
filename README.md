# Paper Reading

仓库只维护 **`papers/`** 目录：每篇 readpaper 讲解一个子文件夹，由 GitHub Pages 发布。

## 目录结构

```
papers/
├── index.html              # 论文列表首页
├── papers.json             # 目录元数据
├── assets/site.css         # 共享样式
├── scripts/add_paper.py    # 入库脚本
└── <slug>/index.html       # 单篇讲解
```

## 添加新论文

```bash
python3 papers/scripts/add_paper.py path/to/artifact.html \
  --title "论文标题" \
  --slug my-paper \
  --arxiv "https://arxiv.org/abs/xxxx" \
  --tldr "一句话摘要"
```

## 本地预览

```bash
cd papers && python3 -m http.server 8080
# http://localhost:8080/
# http://localhost:8080/scaling-laws-2001-08361/
```

## GitHub Pages

1. Actions 跑绿后，**Settings → Pages** → Branch: `gh-pages` / `(root)`
2. 访问：https://wudongming97.github.io/Paper_Reading/

**注意：** 部署的是 `papers/` 的内容，URL 不再包含 `/papers/` 前缀：

- 首页：`/Paper_Reading/`
- 讲解：`/Paper_Reading/scaling-laws-2001-08361/`
