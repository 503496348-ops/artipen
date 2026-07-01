#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
妙笔生花 · ArtiPen — 多平台文章编排引擎
"""

__version__ = "1.2.0"
__author__ = "AtomCollide-智械工坊"

from .platform_adapter import adapt_to_platform, adapt_to_all
from .content_analyzer import analyze_content, ContentAnalysis
from .style_config import StyleConfig
from .topic_intelligence import generate_topic_brief, rank_topics, score_topic
from .longform_writer import build_longform_plan, render_plan_markdown
from .research_brief import build_research_brief, render_research_brief_markdown

__all__ = [
    "adapt_to_platform",
    "adapt_to_all",
    "analyze_content",
    "ContentAnalysis",
    "StyleConfig",
    "generate_topic_brief",
    "rank_topics",
    "score_topic",
    "build_longform_plan",
    "render_plan_markdown",
    "build_research_brief",
    "render_research_brief_markdown",
]
