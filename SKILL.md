---
authors:
  - AtomCollide-智械工坊团队
name: artipen
description: "内容生产全链路引擎。热点选题+研究证据包+公众号长文规划+公众号HTML/小红书/知乎/掘金多平台编排+AI味检测。当需要从选题到发布完整生产内容时使用。"
version: 1.2.0
triggers:
  - 公众号排版
  - 小红书图片
  - 知乎文章
  - 掘金文章
  - 文章编排
  - 热点选题
  - 长文规划
  - 研究证据包
  - 多平台发布
  - 妙笔生花
  - artipen
---
authors:
  - AtomCollide-智械工坊团队

# 妙笔生花 · ArtiPen

> 📖 详细文档见 `references/` 目录

> 内容生产全链路引擎。热点发现 → 选题评分 → 研究证据包 → 长文规划 → 四个平台最优格式。

## 能力总览

| 能力 | 说明 | 来源 |
|------|------|------|
| 多平台排版 | 公众号/小红书/知乎/掘金自动适配 |
| 小红书卡片 | 1-10张轮播图文，12风格×8布局×3配色 |
| 公众号HTML | 带样式HTML，代码高亮，外链转引用 |
| 知乎/掘金MD | 标准化Markdown，保留代码块/引用/标题 |
| 封面生成 | 5维控制(类型/配色/渲染/文字/情绪) |
| 文章配图 | 自动识别配图位置，类型×风格×配色 |
| 信息图 | 21布局×22风格，高密度信息大图 |
| AI味检测 | 33类模式+5维度评分+12项Quick Checks | AI味检测引擎 |
| 热点选题 | 公开 AI 热点源 + HKR/时效/证据评分，生成选题简报 | 融合外部 MIT Skill 方法论并重写实现 |
| 长文规划 | 文章原型、叙事弧、标题候选、开头钩子、自检门禁 | 融合外部 MIT Skill 方法论并重写实现 |
| 研究证据包 | 纵向时间线、横向竞品/替代、证据卡、缺口与洞察 | 融合外部 MIT Skill 方法论并重写实现 |

## 使用方式

### 一键全流程

```bash
python artipen/cli.py article.md --platforms wechat,xhs,zhihu,juejin
```

### 单平台排版

```bash
# 公众号
python artipen/cli.py article.md --platform wechat

# 小红书（生成卡片图片）
python artipen/cli.py article.md --platform xhs

# 知乎
python artipen/cli.py article.md --platform zhihu

# 掘金
python artipen/cli.py article.md --platform juejin
```

### 仅配图

```bash
python artipen/cli.py article.md --cover --illustrations --infographic
```

### AI味检测

```bash
python artipen/cli.py article.md --check-ai-flavor
```

### 热点选题简报

```bash
python artipen/cli.py article.md --topic-brief --topic-category ai-models --topic-limit 5
```

### 公众号长文规划

```bash
python artipen/cli.py article.md --longform-plan
```

### 深度研究证据包

```bash
python artipen/cli.py article.md --research-brief --subject "目标产品/议题"
```

## 输出结构

```
output/
├── wechat/
│   ├── article.html          # 公众号兼容HTML
│   └── cover.png             # 封面图prompt
├── xhs/
│   ├── card_01.png           # 小红书卡片1
│   ├── card_02.png           # 小红书卡片2
│   └── ...
├── zhihu/
│   └── article.md            # 知乎标准Markdown
├── juejin/
│   └── article.md            # 掘金标准Markdown
├── illustrations/
│   ├── ill_01.png            # 配图1
│   └── ...
└── infographic.png           # 信息图
```

## 平台适配规则

### 公众号
- 外链自动转底部引用（微信不支持外链）
- 代码块带语法高亮
- 支持Mermaid/PlantUML（渲染为PNG）
- 主题：默认/暗色/学术/极简

### 小红书
- 长文自动拆分为1-10张卡片
- 12种视觉风格：极简/杂志/科技/手绘/...
- 8种布局：标题卡/要点卡/数据卡/引用卡/...
- 3种配色：暖色/冷色/中性
- 每张卡片1080×1440（3:4竖版）

### 知乎
- 标准Markdown，保留标题层级
- 代码块保留语言标注
- 数学公式保留LaTeX格式
- 引用块标准化

### 掘金
- 标准Markdown，兼容掘金编辑器
- 代码块支持掘金指定语言
- 标签自动提取
- frontmatter标准化

## 风格配置

### 小红书卡片风格（12种）
minimal / magazine / tech / handdrawn / pastel / neon / vintage / nature / luxury / playful / academic / bold

### 小红书布局（8种）
title / keypoints / data / quote / comparison / timeline / list / summary

### 封面5维控制
- Type（类型）：cinematic / widescreen / square
- Palette（配色）：11种预设
- Rendering（渲染）：7种风格
- Text（文字）：标题/副标题/无
- Mood（情绪）：6种基调

### 信息图风格（22种）
minimal / magazine / tech / handdrawn / corporate / playful / vintage / neon / pastel / dark / nature / luxury / academic / bold / retro / futuristic / watercolor / geometric / organic / monochrome / gradient / mosaic

## 工作流

使用此技能时，按以下步骤执行：
- [ ] 1. 确认目标：热点发现、长文规划、研究证据包、AI味检测、还是多平台编排。
- [ ] 2. 若用户还没有选题，先跑 `--topic-brief` 生成候选池并选择高分题。
- [ ] 3. 若文章需要深度可信度，跑 `--research-brief` 补齐纵向/横向/证据/缺口。
- [ ] 4. 若要写公众号长文，跑 `--longform-plan` 生成标题、开头、叙事弧和自检门禁。
- [ ] 5. 完成正文后跑 `--check-ai-flavor`，问题过多时先改写。
- [ ] 6. 最后用 `--platforms wechat,xhs,zhihu,juejin` 生成发布包。
- [ ] 7. 验证输出文件、链接、数据来源和平台适配结果后再交付。


---

## 技术架构

- **生成引擎**: 多模型调度（文生图/文生文），支持SDXL/Flux等后端
- **风格系统**: 20+预设风格模板，自定义风格训练
- **上游引擎**: 热点选题评分、长文规划、研究证据包
- **质量控制**: 生成→评分→筛选→重试循环
- **API服务**: FastAPI RESTful接口，SQLite持久化
- **批处理**: 并行渲染+自动命名归档
