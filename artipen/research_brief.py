#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
研究证据包生成器 — 为深度长文准备纵向/横向/交叉洞察材料

该模块把“横纵分析”转成 ArtiPen 可执行的内容生产前置步骤：
纵向时间线、横向竞品/同类对比、证据缺口、写作角度与发布门禁。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .content_analyzer import analyze_content


@dataclass
class EvidencePoint:
    claim: str
    source: str = ""
    source_type: str = "unknown"
    confidence: str = "medium"
    note: str = ""

    def to_dict(self) -> Dict:
        return {
            "claim": self.claim,
            "source": self.source,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "note": self.note,
        }


@dataclass
class ResearchBrief:
    subject: str
    research_question: str
    vertical_axis: List[str]
    horizontal_axis: List[str]
    evidence_points: List[EvidencePoint]
    gaps: List[str]
    insights: List[str]
    article_angles: List[str]
    verification_gate: List[str]

    def to_dict(self) -> Dict:
        return {
            "subject": self.subject,
            "research_question": self.research_question,
            "vertical_axis": self.vertical_axis,
            "horizontal_axis": self.horizontal_axis,
            "evidence_points": [x.to_dict() for x in self.evidence_points],
            "gaps": self.gaps,
            "insights": self.insights,
            "article_angles": self.article_angles,
            "verification_gate": self.verification_gate,
        }


def _extract_urls(text: str) -> List[str]:
    return re.findall(r"https?://[^\s\)\]}>\"']+", text)


def _extract_year_events(text: str) -> List[str]:
    events: List[str] = []
    for m in re.finditer(r"((?:20\d{2}|19\d{2})[年\-/\. ]{0,2}\d{0,2}[月\-/\. ]{0,2}\d{0,2}[^。！？\n]{4,80})", text):
        events.append(m.group(1).strip())
    return events[:12]


def _split_candidates(text: str) -> List[str]:
    candidates = re.findall(r"(?:竞品|对手|同类|替代|相比|类似|包括|例如|比如)[：:，, ]([^。！？\n]{2,120})", text)
    names: List[str] = []
    for c in candidates:
        for part in re.split(r"[、,，/]|和|与|以及", c):
            cleaned = re.sub(r"[\s。；;]+", "", part)
            if 2 <= len(cleaned) <= 30 and cleaned not in names:
                names.append(cleaned)
    return names[:8]


def _source_type(url: str) -> str:
    if "github.com" in url:
        return "code/repository"
    if "arxiv.org" in url or "doi.org" in url:
        return "paper"
    if any(x in url for x in ["openai.com", "anthropic.com", "deepmind.google", "microsoft.com", "meta.com"]):
        return "official"
    return "web"


def build_research_brief(
    text: str,
    *,
    subject: Optional[str] = None,
    competitors: Optional[Iterable[str]] = None,
) -> ResearchBrief:
    """根据素材生成深度研究证据包。"""
    analysis = analyze_content(text)
    subject = subject or analysis.title or "待研究对象"
    urls = _extract_urls(text)
    year_events = _extract_year_events(text)
    candidate_competitors = list(competitors or []) or _split_candidates(text)

    vertical_axis = year_events or [
        "起源：首次发布/提出/成立的时间、背景和原始问题是什么？",
        "演进：关键版本、融资、生态变化、用户增长或争议事件有哪些？",
        "转折：哪些决策改变了它后来的竞争位置？",
        "现状：今天的能力边界、用户群和商业模式是什么？",
    ]

    horizontal_axis = candidate_competitors or [
        "直接竞品：同一用户、同一任务、同一预算下会被拿来比较的产品/方案。",
        "间接替代：用户不采用它时，实际会用什么老方法或替代流程解决问题。",
        "生态位置：它是平台、工具、模型、工作流，还是某个大生态中的模块？",
    ]

    evidence_points: List[EvidencePoint] = []
    for url in urls[:12]:
        evidence_points.append(
            EvidencePoint(
                claim=f"素材中引用了来源：{url}",
                source=url,
                source_type=_source_type(url),
                confidence="high" if _source_type(url) in {"official", "paper", "code/repository"} else "medium",
                note="写作时应回到原文核验，不要只引用二手摘要。",
            )
        )

    if analysis.data_points:
        for d in analysis.data_points[:6]:
            evidence_points.append(
                EvidencePoint(
                    claim=f"素材包含数据点：{d}",
                    source="input_material",
                    source_type="data-point",
                    confidence="medium",
                    note="需要确认数据口径、时间范围和来源。",
                )
            )

    if not evidence_points:
        evidence_points.append(
            EvidencePoint(
                claim="当前素材缺少可引用来源",
                source="",
                source_type="gap",
                confidence="low",
                note="发布前必须补充官方文档、论文、仓库、财报或可信媒体来源。",
            )
        )

    gaps = []
    if not urls:
        gaps.append("缺少外部链接或一手来源。")
    if not year_events:
        gaps.append("缺少纵向时间线材料。")
    if not candidate_competitors:
        gaps.append("缺少横向竞品/替代方案清单。")
    if not analysis.data_points:
        gaps.append("缺少可量化数据点。")

    insights = [
        f"不要只回答「{subject} 是什么」，要回答它为什么在这个时间点变重要。",
        "把纵向历史里的关键决策，与横向竞品里的当前差异连接起来。",
        "每个强判断都要落到证据、用户场景和可验证后果上。",
    ]

    article_angles = [
        f"纵向故事：{subject} 从哪里来，哪一步决定了今天的样子。",
        f"横向对比：把 {subject} 放进同类方案里，看它赢在哪里、输在哪里。",
        f"读者行动：如果读者明天要用/买/学/投资/对标 {subject}，第一步该做什么。",
    ]

    verification_gate = [
        "至少 2 个一手来源支撑核心事实。",
        "竞品/替代方案不少于 3 个；确实没有直接竞品时要说明原因。",
        "所有数字必须带口径、时间和来源。",
        "每个推测句必须标注为推测，不能写成已发生事实。",
        "发布前跑 AI 味检测和平台适配预览。",
    ]

    return ResearchBrief(
        subject=subject,
        research_question=f"{subject} 的历史路径、当前生态位和未来机会是什么？",
        vertical_axis=vertical_axis,
        horizontal_axis=horizontal_axis,
        evidence_points=evidence_points,
        gaps=gaps or ["暂无明显缺口，但仍需发布前复核来源有效性。"],
        insights=insights,
        article_angles=article_angles,
        verification_gate=verification_gate,
    )


def render_research_brief_markdown(brief: ResearchBrief) -> str:
    """渲染研究证据包。"""
    lines = [
        f"# 研究证据包：{brief.subject}",
        "",
        f"研究问题：{brief.research_question}",
        "",
        "## 纵向轴：时间与演进",
    ]
    lines.extend(f"- {x}" for x in brief.vertical_axis)
    lines.extend(["", "## 横向轴：竞品与替代"])
    lines.extend(f"- {x}" for x in brief.horizontal_axis)
    lines.extend(["", "## 证据清单"])
    for i, e in enumerate(brief.evidence_points, 1):
        lines.extend([
            f"### {i}. {e.claim}",
            f"- 来源：{e.source or '待补充'}",
            f"- 类型：{e.source_type}",
            f"- 置信度：{e.confidence}",
            f"- 备注：{e.note}",
            "",
        ])
    lines.extend(["## 缺口清单"])
    lines.extend(f"- [ ] {x}" for x in brief.gaps)
    lines.extend(["", "## 交叉洞察"])
    lines.extend(f"- {x}" for x in brief.insights)
    lines.extend(["", "## 可写作角度"])
    lines.extend(f"- {x}" for x in brief.article_angles)
    lines.extend(["", "## 发布前验证门禁"])
    lines.extend(f"- [ ] {x}" for x in brief.verification_gate)
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    import sys

    source = sys.stdin.read()
    print(render_research_brief_markdown(build_research_brief(source)))
