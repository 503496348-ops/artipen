#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热点选题引擎 — AI 内容选题池与评分器

从公开 AI 动态源生成可写作选题，不依赖 API Key。默认使用 AI HOT
公开接口；网络不可用时仍可对本地条目做评分与选题编排。
"""

from __future__ import annotations

import json
import math
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional

AIHOT_BASE_URL = "https://aihot.virxact.com"
CATEGORY_LABELS = {
    "ai-models": "模型发布/更新",
    "ai-products": "产品发布/更新",
    "industry": "行业动态",
    "paper": "论文研究",
    "tip": "技巧与观点",
}


@dataclass
class TopicItem:
    """单条热点素材。"""

    title: str
    url: str = ""
    source: str = ""
    category: str = ""
    summary: str = ""
    published_at: str = ""
    raw: Dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: Dict) -> "TopicItem":
        title = (
            data.get("titleZh")
            or data.get("title")
            or data.get("name")
            or data.get("headline")
            or ""
        )
        summary = data.get("summaryZh") or data.get("summary") or data.get("description") or ""
        category = data.get("category") or data.get("section") or ""
        return cls(
            title=str(title).strip(),
            url=str(data.get("url") or data.get("link") or "").strip(),
            source=str(data.get("source") or data.get("site") or "").strip(),
            category=str(category).strip(),
            summary=str(summary).strip(),
            published_at=str(data.get("publishedAt") or data.get("published_at") or data.get("date") or "").strip(),
            raw=data,
        )

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "category_label": CATEGORY_LABELS.get(self.category, self.category),
            "summary": self.summary,
            "published_at": self.published_at,
        }


@dataclass
class TopicScore:
    """HKR + 时效 + 证据评分。"""

    item: TopicItem
    happy: int
    knowledge: int
    resonance: int
    freshness: int
    evidence: int
    total: int
    angle: str
    recommended_format: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "title": self.item.title,
            "url": self.item.url,
            "source": self.item.source,
            "category": self.item.category,
            "category_label": CATEGORY_LABELS.get(self.item.category, self.item.category),
            "summary": self.item.summary,
            "published_at": self.item.published_at,
            "score": {
                "happy": self.happy,
                "knowledge": self.knowledge,
                "resonance": self.resonance,
                "freshness": self.freshness,
                "evidence": self.evidence,
                "total": self.total,
            },
            "angle": self.angle,
            "recommended_format": self.recommended_format,
            "reasons": self.reasons,
        }


def _utc_since(days: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=max(0, days))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_aihot_items(
    *,
    mode: str = "selected",
    category: Optional[str] = None,
    query: Optional[str] = None,
    days: int = 7,
    take: int = 50,
    timeout: int = 20,
) -> List[TopicItem]:
    """获取 AI HOT 最近动态。

    items 接口最多覆盖最近 7 天；需要更早内容应走日报归档。这里默认
    使用 selected，避免把低质量噪声引入选题池。
    """
    params = {
        "mode": mode,
        "take": str(max(1, min(take, 100))),
        "since": _utc_since(min(days, 7)),
    }
    if category:
        params["category"] = category
    if query:
        params["q"] = query
    url = f"{AIHOT_BASE_URL}/api/public/items?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "ArtiPenTopicIntelligence/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return []
    return [item for item in (TopicItem.from_api(x) for x in items) if item.title]


def _contains_any(text: str, words: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(w.lower() in lowered for w in words)


def _freshness_score(published_at: str) -> int:
    if not published_at:
        return 5
    normalized = published_at.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return 5
    hours = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds() / 3600
    if hours <= 24:
        return 10
    if hours <= 72:
        return 8
    if hours <= 168:
        return 6
    return 3


def score_topic(item: TopicItem) -> TopicScore:
    """对单个选题做 HKR 评分。

    H = 好奇/悬念，K = 知识密度，R = 共鸣/传播。总分满分 100。
    """
    text = f"{item.title}\n{item.summary}\n{item.source}\n{item.category}"
    happy = 4
    knowledge = 4
    resonance = 4
    evidence = 4
    reasons: List[str] = []

    if _contains_any(text, ["发布", "正式", "开源", "突破", "首次", "万亿", "融资", "收购", "免费", "涨价"]):
        happy += 3
        reasons.append("标题具备新闻钩子或反差点")
    if _contains_any(text, ["模型", "论文", "参数", "benchmark", "推理", "agent", "api", "开源", "训练", "架构"]):
        knowledge += 3
        reasons.append("包含可展开的技术/产品知识")
    if _contains_any(text, ["开发者", "用户", "企业", "成本", "效率", "替代", "工作流", "教育", "内容", "安全"]):
        resonance += 3
        reasons.append("与真实使用场景或职业影响相关")
    if item.url:
        evidence += 3
        reasons.append("有可追溯链接，可进入证据包")
    if item.source:
        evidence += 1

    if item.category == "paper":
        recommended = "深度研究文章"
        angle = f"从一篇论文切入，解释 {item.title} 背后的技术变化和可落地场景。"
    elif item.category == "ai-models":
        recommended = "模型发布解读"
        angle = f"围绕 {item.title}，拆解模型能力、生态位置和对开发者的实际影响。"
    elif item.category == "ai-products":
        recommended = "产品体验/趋势文章"
        angle = f"把 {item.title} 放进产品演进脉络里，讲清楚它解决了谁的什么问题。"
    else:
        recommended = "公众号热点长文"
        angle = f"以 {item.title} 为入口，做现象观察、证据拆解和行动建议。"

    freshness = _freshness_score(item.published_at)
    happy = min(happy, 10)
    knowledge = min(knowledge, 10)
    resonance = min(resonance, 10)
    evidence = min(evidence, 10)
    total = round(happy * 2.2 + knowledge * 2.8 + resonance * 2.2 + freshness * 1.4 + evidence * 1.4)
    return TopicScore(
        item=item,
        happy=happy,
        knowledge=knowledge,
        resonance=resonance,
        freshness=freshness,
        evidence=evidence,
        total=min(total, 100),
        angle=angle,
        recommended_format=recommended,
        reasons=reasons or ["常规热点，可作为备选素材"],
    )


def rank_topics(items: Iterable[TopicItem], limit: int = 10) -> List[TopicScore]:
    """批量评分并按总分排序。"""
    scored = [score_topic(item) for item in items if item.title]
    scored.sort(key=lambda x: (x.total, x.freshness, len(x.item.summary)), reverse=True)
    return scored[: max(1, limit)]


def build_topic_brief(scores: List[TopicScore]) -> str:
    """生成 Markdown 选题简报。"""
    lines = ["# ArtiPen 热点选题简报", "", "## Top 选题池", ""]
    for i, s in enumerate(scores, 1):
        lines.extend(
            [
                f"### {i}. {s.item.title}",
                f"- 评分：{s.total}/100（H{s.happy}/K{s.knowledge}/R{s.resonance}/Fresh{s.freshness}/Evidence{s.evidence}）",
                f"- 类型：{s.recommended_format}",
                f"- 角度：{s.angle}",
                f"- 来源：{s.item.source or '未标注'} {s.item.url}",
                f"- 理由：{'；'.join(s.reasons)}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def generate_topic_brief(
    *,
    query: Optional[str] = None,
    category: Optional[str] = None,
    days: int = 7,
    take: int = 50,
    limit: int = 10,
) -> Dict:
    """端到端生成选题简报。"""
    items = fetch_aihot_items(query=query, category=category, days=days, take=take)
    scores = rank_topics(items, limit=limit)
    return {
        "source": "AI HOT public API",
        "query": query,
        "category": category,
        "days": min(days, 7),
        "items_count": len(items),
        "topics": [s.to_dict() for s in scores],
        "markdown": build_topic_brief(scores),
    }


if __name__ == "__main__":
    brief = generate_topic_brief(limit=5)
    print(brief["markdown"])
