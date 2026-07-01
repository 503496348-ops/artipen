#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长文写作规划器 — 从素材到公众号长文蓝图

吸收高质量公众号写作 Skill 的方法论，但保持 ArtiPen 自身品牌：
选题质检 → 文章原型 → 叙事弧 → 标题/开头/结构/自检清单。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .content_analyzer import analyze_content


@dataclass
class HKRScore:
    happy: int
    knowledge: int
    resonance: int
    total: int
    verdict: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "happy": self.happy,
            "knowledge": self.knowledge,
            "resonance": self.resonance,
            "total": self.total,
            "verdict": self.verdict,
            "reasons": self.reasons,
        }


@dataclass
class LongformPlan:
    title: str
    prototype: str
    hkr: HKRScore
    core_claim: str
    reader: str
    narrative_arc: List[str]
    outline: List[Dict]
    title_candidates: List[str]
    opening_hooks: List[str]
    style_checks: List[str]
    approval_gate: List[str]

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "prototype": self.prototype,
            "hkr": self.hkr.to_dict(),
            "core_claim": self.core_claim,
            "reader": self.reader,
            "narrative_arc": self.narrative_arc,
            "outline": self.outline,
            "title_candidates": self.title_candidates,
            "opening_hooks": self.opening_hooks,
            "style_checks": self.style_checks,
            "approval_gate": self.approval_gate,
        }


def score_hkr(text: str) -> HKRScore:
    """HKR 选题质检：好奇、知识、共鸣。"""
    analysis = analyze_content(text)
    title = analysis.title or "未命名选题"
    body = text.lower()
    happy = 3
    knowledge = 3
    resonance = 3
    reasons: List[str] = []

    if re.search(r"\?|？|为什么|怎么|到底|首次|突然|爆火|翻车|突破|离谱|真相", text):
        happy += 3
        reasons.append("有悬念、冲突或好奇心入口")
    if analysis.data_points or analysis.code_blocks or re.search(r"模型|论文|架构|API|参数|实验|benchmark|数据|案例", text, re.I):
        knowledge += 3
        reasons.append("有数据、技术或案例可展开")
    if re.search(r"我|我们|用户|开发者|老师|学生|测试|运营|创作者|普通人|工作|成本|效率|焦虑|机会", text):
        resonance += 3
        reasons.append("能连接具体人群的处境")
    if len(text) > 1200:
        knowledge += 1
    if analysis.quotes:
        resonance += 1
    if len(title) > 8:
        happy += 1

    happy = min(happy, 10)
    knowledge = min(knowledge, 10)
    resonance = min(resonance, 10)
    total = round((happy + knowledge + resonance) / 30 * 100)
    if total >= 80:
        verdict = "S级选题：可以进入长文生产"
    elif total >= 65:
        verdict = "A级选题：建议补强证据或人群切口后再写"
    elif total >= 50:
        verdict = "B级选题：适合短内容，不建议直接写长文"
    else:
        verdict = "不通过：缺少明确钩子、知识增量或共鸣点"
    return HKRScore(happy, knowledge, resonance, total, verdict, reasons or ["需要补充更具体的事实和读者场景"])


def classify_prototype(text: str) -> str:
    """判断长文原型。"""
    if re.search(r"我试了|实测|亲自|体验|上手|测试|跑了一遍|踩坑", text):
        return "调查实验型 / 产品体验型"
    if re.search(r"方法|步骤|怎么做|指南|SOP|清单|工作流", text, re.I):
        return "方法论分享型"
    if re.search(r"为什么|现象|刷屏|爆火|争议|趋势|背后", text):
        return "现象解读型"
    if re.search(r"工具|插件|模型|产品|平台|应用", text):
        return "工具/产品分享型"
    return "观点叙事型"


def _first_sentence(text: str) -> str:
    clean = re.sub(r"[#>*`\-]+", "", text).strip()
    parts = re.split(r"[。！？\n]", clean)
    for p in parts:
        p = p.strip()
        if len(p) >= 8:
            return p[:80]
    return clean[:80] or "这个选题值得被认真讲清楚"


def build_longform_plan(text: str, *, target_reader: str = "AI 产品/内容/技术实践者") -> LongformPlan:
    """生成公众号长文蓝图。"""
    analysis = analyze_content(text)
    title = analysis.title or _first_sentence(text)
    prototype = classify_prototype(text)
    hkr = score_hkr(text)
    core = _first_sentence(text)

    narrative_arc = [
        "具体事件切入：先抛出一个正在发生的事实、体验或冲突，不从宏大背景开场。",
        "好奇心推进：解释为什么这件事不只是新闻，而是值得继续追问。",
        "证据层展开：用数据、原始链接、案例、亲测过程或对比材料支撑判断。",
        "读者处境连接：回答它对目标读者的工作、学习、创作或决策有什么影响。",
        "行动建议收束：给出可以今天执行的一步，而不是停在感慨。",
    ]

    outline = [
        {
            "section": "开头",
            "goal": "用一个具体事实或反常识现象建立钩子",
            "prompt": f"围绕「{title}」写一个 150 字以内的故事化开头，避免时代背景套话。",
        },
        {
            "section": "背景",
            "goal": "补足必要知识，但不要像百科词条",
            "prompt": "只解释读者看懂后文必需的 3 个背景点，每点必须有具体名词。",
        },
        {
            "section": "证据",
            "goal": "把素材变成可信判断",
            "prompt": "列出一手来源、数据、用户场景和反例；没有证据的判断标记为推测。",
        },
        {
            "section": "洞察",
            "goal": "给出文章真正想留下的判断",
            "prompt": "写清楚这件事改变了什么、没改变什么、谁会被影响。",
        },
        {
            "section": "行动",
            "goal": "把读者带到可执行下一步",
            "prompt": "给出 3 条具体行动建议，并标注适用人群。",
        },
    ]

    title_candidates = [
        f"{title}，真正值得看的不是热闹",
        f"我重新看了一遍 {title}，发现重点不在表面",
        f"{title} 背后，藏着一个更大的变化",
        f"别急着转发 {title}，先看懂这几件事",
        f"从 {title} 开始，聊聊 AI 产品真正的分水岭",
        f"{title} 给普通创作者/开发者留下了什么机会",
        f"这一次，{title} 不是又一个普通更新",
        f"把 {title} 拆开看，答案比标题更有意思",
        f"如果你只看到了 {title}，可能漏掉了关键一层",
        f"关于 {title}，我最在意的是这件小事",
    ]

    opening_hooks = [
        f"故事可以从「{title}」说起。",
        f"我一开始以为这只是又一条 AI 新闻，直到我把细节拆开看了一遍。",
        f"这件事最有意思的地方，不是它发生了，而是它为什么现在发生。",
    ]

    style_checks = [
        "开头 300 字内必须出现具体事件/对象，不能出现“随着AI快速发展”。",
        "每 600 字至少出现一个具体名词、数据、链接、人物或场景。",
        "判断必须先给证据；推测必须明确标注，不伪装成事实。",
        "删除“综上所述、值得注意的是、不难发现、本质上、这意味着”等 AI 腔。",
        "长短句交替，关键判断可单独成段，但不要堆砌加粗和列表。",
        "结尾必须给行动建议或下一步观察指标。",
    ]

    approval_gate = [
        "涉及对外发布、品牌立场、商业承诺或社群转化 CTA 时必须人工确认。",
        "缺一手来源、链接失效或数据无法验证时，不得进入发布态。",
        "AI 味检测总问题数高于阈值时，必须先改写再排版。",
    ]

    return LongformPlan(
        title=title,
        prototype=prototype,
        hkr=hkr,
        core_claim=core,
        reader=target_reader,
        narrative_arc=narrative_arc,
        outline=outline,
        title_candidates=title_candidates,
        opening_hooks=opening_hooks,
        style_checks=style_checks,
        approval_gate=approval_gate,
    )


def render_plan_markdown(plan: LongformPlan) -> str:
    """渲染为 Markdown。"""
    lines = [
        f"# 长文写作蓝图：{plan.title}",
        "",
        f"- 文章原型：{plan.prototype}",
        f"- 目标读者：{plan.reader}",
        f"- 核心判断：{plan.core_claim}",
        f"- HKR：{plan.hkr.total}/100，{plan.hkr.verdict}",
        f"- 评分理由：{'；'.join(plan.hkr.reasons)}",
        "",
        "## 叙事弧",
    ]
    lines.extend(f"{i}. {x}" for i, x in enumerate(plan.narrative_arc, 1))
    lines.extend(["", "## 文章结构"])
    for sec in plan.outline:
        lines.extend([f"### {sec['section']}", f"- 目标：{sec['goal']}", f"- 写作提示：{sec['prompt']}", ""])
    lines.extend(["## 标题候选"])
    lines.extend(f"{i}. {x}" for i, x in enumerate(plan.title_candidates, 1))
    lines.extend(["", "## 开头候选"])
    lines.extend(f"- {x}" for x in plan.opening_hooks)
    lines.extend(["", "## 发布前自检"])
    lines.extend(f"- [ ] {x}" for x in plan.style_checks)
    lines.extend(["", "## 人工审批门禁"])
    lines.extend(f"- [ ] {x}" for x in plan.approval_gate)
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    import sys

    source = sys.stdin.read()
    plan = build_longform_plan(source)
    print(render_plan_markdown(plan))
