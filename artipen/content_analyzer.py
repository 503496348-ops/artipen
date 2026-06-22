#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容分析模块 — 自动提取文章结构、主题、关键词、配图位置

"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ArticleSection:
    """文章段落/章节"""
    heading: str = ""
    heading_level: int = 0
    content: str = ""
    word_count: int = 0
    needs_illustration: bool = False
    illustration_type: str = ""  # concept/data/scene/process/comparison/mood


@dataclass
class ContentAnalysis:
    """内容分析结果"""
    title: str = ""
    subtitle: str = ""
    keywords: List[str] = field(default_factory=list)
    summary: str = ""
    sections: List[ArticleSection] = field(default_factory=list)
    total_words: int = 0
    estimated_cards: int = 0  # 小红书卡片数
    illustration_positions: List[int] = field(default_factory=list)
    data_points: List[str] = field(default_factory=list)  # 文中的数据/数字
    quotes: List[str] = field(default_factory=list)  # 文中的引用/金句
    code_blocks: int = 0
    has_math: bool = False
    has_mermaid: bool = False

    def to_dict(self) -> Dict:
        return {
            "标题": self.title,
            "副标题": self.subtitle,
            "关键词": self.keywords,
            "摘要": self.summary,
            "章节数": len(self.sections),
            "总字数": self.total_words,
            "预估卡片数": self.estimated_cards,
            "配图位置": self.illustration_positions,
            "数据点": self.data_points[:5],
            "金句": self.quotes[:3],
            "代码块数": self.code_blocks,
            "含数学公式": self.has_math,
            "含Mermaid图": self.has_mermaid,
        }


def analyze_content(text: str) -> ContentAnalysis:
    """分析文章内容，提取结构和元信息"""
    result = ContentAnalysis()

    # 提取标题（第一个#标题或第一行非空文本）
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            result.title = line[2:].strip()
            break
        elif line and not line.startswith('```'):
            result.title = line[:50]
            break

    # 提取副标题
    for line in lines:
        line = line.strip()
        if line.startswith('## '):
            result.subtitle = line[3:].strip()
            break

    # 统计总字数
    result.total_words = len(re.sub(r'\s+', '', text))

    # 检测代码块
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    result.code_blocks = len(code_blocks)

    # 检测数学公式
    result.has_math = bool(re.search(r'\$.*?\$|\\\[.*?\\\]', text))

    # 检测Mermaid
    result.has_mermaid = bool(re.search(r'```mermaid', text))

    # 提取章节
    sections = []
    current_section = ArticleSection()
    for line in lines:
        heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            if current_section.content.strip():
                current_section.word_count = len(re.sub(r'\s+', '', current_section.content))
                sections.append(current_section)
            current_section = ArticleSection(
                heading=heading_match.group(2),
                heading_level=len(heading_match.group(1)),
            )
        else:
            current_section.content += line + '\n'
    if current_section.content.strip():
        current_section.word_count = len(re.sub(r'\s+', '', current_section.content))
        sections.append(current_section)

    result.sections = sections

    # 估算小红书卡片数（每300字一张卡片，最少1张最多10张）
    result.estimated_cards = max(1, min(10, result.total_words // 300 + 1))

    # 识别需要配图的位置
    for i, section in enumerate(sections):
        # 数据密集段落
        if re.search(r'\d+%|\d+万|\d+亿|\d+倍|增长|下降|提升', section.content):
            section.needs_illustration = True
            section.illustration_type = "data"
            result.illustration_positions.append(i)
            # 提取数据点
            data_matches = re.findall(r'\d+[\.\d]*[%万亿倍]', section.content)
            result.data_points.extend(data_matches[:3])
        # 概念解释段落（超过200字且无数据）
        elif section.word_count > 200 and section.illustration_type == "":
            section.needs_illustration = True
            section.illustration_type = "concept"
            result.illustration_positions.append(i)

    # 提取金句（引用块或特定模式）
    quote_pattern = re.findall(r'>\s*(.{10,100})', text)
    result.quotes = quote_pattern[:5]

    # 提取关键词（从标题和章节标题中提取）
    all_headings = [result.title] + [s.heading for s in sections if s.heading]
    # 简单的关键词提取：去停用词，取高频词
    stopwords = {'的', '了', '是', '在', '和', '与', '为', '以', '及', '等',
                 '如何', '什么', '为什么', '怎么', '一', '二', '三', '四', '五'}
    words = []
    for h in all_headings:
        # 中文分词（简单按字符/标点分割）
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', h)
        words.extend([t for t in tokens if t not in stopwords and len(t) > 1])
    # 去重并取前5个
    seen = set()
    keywords = []
    for w in words:
        if w not in seen:
            seen.add(w)
            keywords.append(w)
    result.keywords = keywords[:5]

    # 生成摘要
    if result.sections:
        first_content = result.sections[0].content.strip()
        result.summary = first_content[:150] + ('...' if len(first_content) > 150 else '')

    return result


def recommend_platform_config(analysis: ContentAnalysis) -> Dict[str, str]:
    """根据内容分析推荐最佳平台配置"""
    config = {}

    # 小红书风格推荐
    if analysis.data_points:
        config["xhs_style"] = "tech"
        config["xhs_layout"] = "data"
    elif analysis.quotes:
        config["xhs_style"] = "magazine"
        config["xhs_layout"] = "quote"
    elif analysis.total_words > 2000:
        config["xhs_style"] = "minimal"
        config["xhs_layout"] = "keypoints"
    else:
        config["xhs_style"] = "minimal"
        config["xhs_layout"] = "title"

    # 公众号主题推荐
    has_code = analysis.code_blocks > 0
    if has_code:
        config["wechat_theme"] = "dark"
    elif analysis.has_math:
        config["wechat_theme"] = "academic"
    else:
        config["wechat_theme"] = "default"

    # 信息图推荐
    if analysis.data_points:
        config["infographic_layout"] = "dashboard"
        config["infographic_style"] = "tech"
    elif len(analysis.sections) > 5:
        config["infographic_layout"] = "hierarchy"
        config["infographic_style"] = "minimal"
    else:
        config["infographic_layout"] = "flowchart"
        config["infographic_style"] = "magazine"

    return config
