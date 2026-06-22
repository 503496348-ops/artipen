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

---

## 🚀 元素碰撞 — AtomCollide-AI 智能体实验室

> 测试人专属成长社群 · 正式招募

我们的目标很纯粹：**连接每一位测试工程师/AI使用探索与爱好者**，让你在这里既能扎实打磨技术硬实力，也能打通职业晋升的新通路。这是一个专注于AI领域的开源组织，汇聚了众多优秀学习者，使命——*for the learner，和学习者一起成长*。

### 核心价值

**💼 找工作：更省力，也更精准**
- 一线大厂内推通道（字节、阿里、腾讯等），比海投效率高3倍
- 全链路求职赋能包：AI测试面试题库、简历优化、面试技巧
- 线下技术沙龙 & 人脉网络

**🧪 学 AI 测试：真正落地，拒绝空谈**
- 从0到1实战落地体系：Skills、MCP、RAG、AI IDE等前沿技术
- 独家自研资料：《AtomCollide AI测试实战知识库》、AI测试自研平台
- 前沿技术同步与提效方案

### 📚 知识库

| 知识库 | 链接 |
|--------|------|
| 踩坑合集 | [进入](https://vcnvmnln7wit.feishu.cn/wiki/CjV9wG8IHiIpWikCdFEcxfErnne) |
| 商业化案例库 | [进入](https://vcnvmnln7wit.feishu.cn/wiki/LdIxwlrKGibFEVkWMocc2K9KnBh) |
| 科普专栏 | [进入](https://vcnvmnln7wit.feishu.cn/wiki/K1RPwM8zji9ZchkxlOmcivUgnJe) |
| Open Build | [进入](https://vcnvmnln7wit.feishu.cn/wiki/CThswol0PiNJJbkhgT1cZIxanLb) |
| LLM / Agent / 研究报告 | [进入](https://vcnvmnln7wit.feishu.cn/wiki/KwGQwS2TciT2EdkSBBtcYnbsnSd) |
| Skill 封装合集 | [进入](https://vcnvmnln7wit.feishu.cn/wiki/PDfpwqJZUibTyBkUa7TcZZ6Onpd) |
| 社区治理运营 | [进入](https://vcnvmnln7wit.feishu.cn/wiki/MSEGwrdnTiiF9Dk8qCVcNW6InJg) |

### 🎯 加入社群

> 请选择 1 个常用社群加入，内容全域同步，无需重复加入

| 社群 | 链接 |
|------|------|
| AI 探索交流 1 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=074vd565-6084-455c-ac52-9703e89a0697) |
| AI 探索交流 2 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=60bj94f0-1a67-48a7-abbb-9172b161c2b0) |
| AI 探索交流 3 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=13do1920-db46-4444-b635-005680beaf58) |
| AI 探索交流 4 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=f17o1b86-06f6-4f10-911a-69a299a25fe3) |
| AI 探索交流 5 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=2bbh6ab6-22c2-4753-b973-74bb1a2edcc9) |
| AI 探索交流 6 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=d19r19f7-2f47-42ba-b1ec-cb0342cf2e80) |
| AI 探索交流 7 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=fe9vdacc-7316-4b4d-ae4a-fdbcf56315e6) |
| AI 探索交流 8 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=103kfae8-1fd7-424f-984f-d66c210e42d1) |
| AI 探索交流 9 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=239p3cad-2f83-4baa-a230-f40386067548) |
| AI 探索交流 10 区 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=880r7cf5-3638-45ff-afb9-7944de991872) |
| AI 探索交流 — 网文作家 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=6a3v579b-ab43-4e1a-87f9-be63bab88da7) |
| AI 探索交流群 — 音乐达人 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=76at299e-73da-4eeb-9eba-32161e98f2f8) |
| AI 探索交流群 — 微笑驿站 | [加入](https://applink.feishu.cn/client/chat/chatter/add_by_link?link_token=f2av73d0-6bb4-4a9f-9095-5fbbe83e49ec) |

## 许可证

MIT License

## 作者

AtomCollide-智械工坊团队
