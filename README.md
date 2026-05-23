# Paper Reading

个人论文阅读笔记。每篇笔记会尽量用中文把论文的背景、核心想法、方法结构、结果和局限讲清楚，并配一些轻量的概念图，方便之后快速回看。

在线阅读：[wudongming97.github.io/Paper_Reading](https://wudongming97.github.io/Paper_Reading/)

## 当前收录

| 方向 | 论文 | 日期 |
|------|------|------|
| LLM | [Training Compute-Optimal Large Language Models](https://wudongming97.github.io/Paper_Reading/LLM/compute-optimal-2203-15556/) | 2022-03-29 |
| LLM | [Scaling Laws for Neural Language Models](https://wudongming97.github.io/Paper_Reading/LLM/scaling-laws-2001-08361/) | 2020-01-23 |

## 分类

| 分类 | 主题 |
|------|------|
| `LLM` | 大语言模型 |
| `Agent` | 智能体 |
| `Infra` | 训练与推理基础设施 |
| `VLA` | 视觉-语言-动作 |
| `WAM` | 世界模型 / 动作模型 |
| `CV` | 计算机视觉 |

## 目录

```text
papers/
  index.html              # GitHub Pages 首页
  papers.json             # 论文索引数据
  assets/site.css         # 站点样式
  scripts/add_paper.py    # 生成/更新页面的小工具
  LLM/...                 # 各分类下的论文页面
```

## 本地预览

```bash
cd papers
python3 -m http.server 8080
```

然后打开 `http://localhost:8080/`。
