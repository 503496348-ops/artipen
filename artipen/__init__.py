#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
妙笔生花 · ArtiPen — 多平台文章编排引擎
"""

__version__ = "1.0.0"
__author__ = "AtomCollide-智械工坊"

from .platform_adapter import adapt_to_platform, adapt_to_all
from .content_analyzer import analyze_content, ContentAnalysis
from .style_config import StyleConfig

__all__ = [
    "adapt_to_platform",
    "adapt_to_all",
    "analyze_content",
    "ContentAnalysis",
    "StyleConfig",
]
