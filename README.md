# 妙笔生花 · ArtiPen

> 多平台文章编排引擎。一篇文章 → 四个平台最优格式。

## 产品定位

ArtiPen 是 AtomCollide 智械工坊的第 23 款产品，专注**多平台文章编排**：

- 输入：Markdown / 纯文本文章
- 输出：公众号HTML + 小红书卡片 + 知乎Markdown + 掘金Markdown + 配图 + 封面 + 信息图

## 核心能力

### 1. 多平台一键排版

丢入一篇文章，自动适配四个平台的最优格式：

| 平台 | 输出格式 | 特殊处理 |
|------|---------|---------|
| 公众号 | 带样式HTML | 外链转底部引用、代码高亮、Mermaid渲染 |
| 小红书 | 1-10张轮播卡片 | 12风格×8布局×3配色，1080×1440竖版 |
| 知乎 | 标准Markdown | 保留标题层级、LaTeX公式、代码块 |
| 掘金 | 标准Markdown | 兼容掘金编辑器、自动提取标签 |

### 2. 智能配图

- **封面图**：5维控制（类型/配色/渲染/文字/情绪），支持电影级/宽屏/方形
- **文章配图**：自动分析文章结构，识别需要配图的位置
- **信息图**：21种布局×22种风格，高密度信息大图

### 3. AI味检测

集成去AI味引擎（融合humanizer 25.6K⭐ + stop-slop 11.8K⭐）：
- 33类AI写作模式检测
- 5维度量化评分（直白度/节奏/信任感/真实感/密度）
- 12项Quick Checks预交付检查
- 声纹校准引擎

### 4. 内容分析

- 自动提取文章主题、关键词、结构
- 智能推荐最佳排版方案
- 自动生成摘要和标签

## 安装

```bash
git clone https://github.com/503496348-ops/artipen.git
cd artipen
pip install -r requirements.txt
```

## 使用

```bash
# 一键生成所有平台
python artipen/cli.py article.md --platforms wechat,xhs,zhihu,juejin

# 仅公众号
python artipen/cli.py article.md --platform wechat

# 仅小红书卡片
python artipen/cli.py article.md --platform xhs

# 仅配图
python artipen/cli.py article.md --cover --illustrations --infographic

# AI味检测
python artipen/cli.py article.md --check-ai-flavor
```

## 技术架构

```
artipen/
├── cli.py                  # CLI入口
├── platform_adapter.py     # 多平台适配引擎
├── content_analyzer.py     # 内容分析
├── style_config.py         # 风格配置
├── cover_generator.py      # 封面生成prompt
├── xhs_card_generator.py   # 小红书卡片生成prompt
├── infographic_generator.py # 信息图生成prompt
└── ai_flavor_engine.py     # AI味检测引擎
```

## 竞品对标

| 竞品 | Stars | 我们的差异化 |
|------|-------|-------------|
| auto-claude-writing-agent-pub | 422 | 我们覆盖4个平台，不止公众号 |
| xhs-content | 5 | 我们是全链路排版，不只是采集 |

## 版本历史

- v1.0 (2026-06-23) — 初始版本，多平台排版+配图+AI味检测

## 许可证

MIT License

## 作者

AtomCollide-智械工坊团队
