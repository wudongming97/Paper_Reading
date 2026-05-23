# 我的论文阅读记录

读过的论文，用 Cursor 的 readpaper 生成中文讲解，放在这里备查。

**在线阅读：** https://wudongming97.github.io/Paper_Reading/

## 分类

| 文件夹 | 含义 |
|--------|------|
| `LLM` | 大语言模型 |
| `Agent` | 智能体 |
| `Infra` | 训练/推理基础设施 |
| `VLA` | 视觉-语言-动作 |
| `WAM` | 世界模型/动作模型 |
| `CV` | 计算机视觉 |

## 添加一篇

```bash
python3 papers/scripts/add_paper.py 讲解.html \
  --category LLM \
  --title "论文标题" \
  --slug 简短英文名 \
  --arxiv "https://arxiv.org/abs/xxxx" \
  --tldr "一句话总结"
```

然后 `git add . && git commit -m "读：某论文" && git push`

本地预览：`cd papers && python3 -m http.server 8080`
