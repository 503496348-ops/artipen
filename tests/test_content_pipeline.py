from artipen.longform_writer import build_longform_plan
from artipen.research_brief import build_research_brief
from artipen.topic_intelligence import TopicItem, rank_topics


def test_topic_ranking_prefers_evidence_and_ai_context():
    items = [
        TopicItem(title="普通观点", summary="一些泛泛讨论"),
        TopicItem(
            title="新模型正式开源，开发者 API 成本下降 30%",
            summary="包含模型、benchmark、开发者工作流影响",
            url="https://example.com/model",
            source="official",
            category="ai-models",
            published_at="2026-07-01T00:00:00Z",
        ),
    ]
    ranked = rank_topics(items, limit=2)
    assert ranked[0].item.title.startswith("新模型")
    assert ranked[0].total > ranked[1].total
    assert ranked[0].recommended_format == "模型发布解读"


def test_longform_plan_contains_publish_gates():
    text = "# AI Agent 为什么突然进入教育场景？\n\n我们测试了三个产品，发现老师备课效率提升 30%，但证据还需要复核。"
    plan = build_longform_plan(text)
    assert plan.hkr.total >= 50
    assert plan.title_candidates
    assert any("AI 味检测" in item for item in plan.approval_gate)
    assert len(plan.outline) >= 5


def test_research_brief_extracts_evidence_and_gaps():
    text = "# ArtiPen 调研\n\n2024 年首次发布，2026 年进入内容生产链路。参考 https://github.com/503496348-ops/artipen ，效率提升 30%。竞品包括 Notion AI、公众号编辑器、Markdown 工具。"
    brief = build_research_brief(text, subject="ArtiPen")
    assert brief.subject == "ArtiPen"
    assert brief.evidence_points
    assert any(point.source_type == "code/repository" for point in brief.evidence_points)
    assert brief.vertical_axis
    assert brief.horizontal_axis
