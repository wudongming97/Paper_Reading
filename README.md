# 我的论文阅读记录

读过的论文，用 Cursor 的 readpaper 生成中文讲解，放在这里备查。

**在线阅读：** https://wudongming97.github.io/Paper_Reading/

---

## 怎么用

1. 在 Cursor 里对一篇论文跑 readpaper，得到 HTML
2. 运行（把路径和标题改成你的）：

```bash
python3 papers/scripts/add_paper.py 讲解.html \
  --title "论文标题" \
  --slug 简短英文名 \
  --arxiv "https://arxiv.org/abs/xxxx" \
  --tldr "一句话总结"
```

3. `git add . && git commit -m "读：某论文" && git push`

推上去几分钟后，网站上就能看到。

---

## 文件放哪

所有内容在 `papers/` 里：每篇论文一个文件夹，首页 `papers/index.html` 是目录。

本地看一眼：`cd papers && python3 -m http.server 8080`，打开 http://localhost:8080
