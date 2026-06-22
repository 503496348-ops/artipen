#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风格配置模块 — 小红书卡片风格/布局/配色 + 封面5维控制 + 信息图风格

"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════
# 小红书卡片配置
# ═══════════════════════════════════════════════════════════════

# 12种视觉风格
XHS_STYLES = {
    "minimal": {"name": "极简", "desc": "大量留白，细线条，无衬线字体", "colors": ["#000", "#fff", "#f5f5f5"]},
    "magazine": {"name": "杂志", "desc": "大标题，图文混排，高级感", "colors": ["#1a1a1a", "#c9a96e", "#fff"]},
    "tech": {"name": "科技", "desc": "深色背景，霓虹色，代码风", "colors": ["#0a0a0a", "#00d4ff", "#3366ff"]},
    "handdrawn": {"name": "手绘", "desc": "手写字体，涂鸦元素，温暖感", "colors": ["#2c2c2c", "#f4a261", "#fff"]},
    "pastel": {"name": "粉彩", "desc": "柔和色调，圆润形状，可爱风", "colors": ["#ffd1dc", "#b5ead7", "#c7ceea"]},
    "neon": {"name": "霓虹", "desc": "黑色背景，荧光色，赛博朋克", "colors": ["#0a0a0a", "#ff00ff", "#00ffff"]},
    "vintage": {"name": "复古", "desc": "旧纸质感，衬线字体，暖色调", "colors": ["#f4e9d9", "#8b4513", "#2f4f4f"]},
    "nature": {"name": "自然", "desc": "绿色系，有机形状，清新感", "colors": ["#2d5016", "#a8d08d", "#f0f7ee"]},
    "luxury": {"name": "奢华", "desc": "金色点缀，深色背景，高级感", "colors": ["#0a0a0a", "#c9a96e", "#fff"]},
    "playful": {"name": "活泼", "desc": "明亮色彩，圆润形状，年轻感", "colors": ["#ff6b6b", "#4ecdc4", "#ffe66d"]},
    "academic": {"name": "学术", "desc": "严谨排版，衬线字体，蓝灰色系", "colors": ["#1a365d", "#2b6cb0", "#e2e8f0"]},
    "bold": {"name": "大胆", "desc": "强对比，大色块，冲击力", "colors": ["#000", "#ff0000", "#fff"]},
}

# 8种布局类型
XHS_LAYOUTS = {
    "title": {"name": "标题卡", "desc": "大标题+副标题+品牌标识", "use": "第一张/最后一张"},
    "keypoints": {"name": "要点卡", "desc": "3-5个核心要点，图标+文字", "use": "核心观点"},
    "data": {"name": "数据卡", "desc": "数据可视化，图表+关键数字", "use": "数据驱动内容"},
    "quote": {"name": "引用卡", "desc": "大字引用+出处", "use": "金句/名言"},
    "comparison": {"name": "对比卡", "desc": "左右/上下对比", "use": "对比分析"},
    "timeline": {"name": "时间线", "desc": "垂直/水平时间轴", "use": "流程/历史"},
    "list": {"name": "列表卡", "desc": "编号列表+图标", "use": "步骤/清单"},
    "summary": {"name": "总结卡", "desc": "核心结论+行动建议", "use": "最后一张"},
}

# 3种配色方案
XHS_PALETTES = {
    "warm": {"name": "暖色", "colors": ["#ff6b6b", "#f4a261", "#ffd1dc"]},
    "cool": {"name": "冷色", "colors": ["#2b6cb0", "#4ecdc4", "#a8d08d"]},
    "neutral": {"name": "中性", "colors": ["#2c2c2c", "#666", "#f5f5f5"]},
}


# ═══════════════════════════════════════════════════════════════
# 封面图5维配置
# ═══════════════════════════════════════════════════════════════

COVER_TYPES = {
    "cinematic": {"ratio": "2.35:1", "desc": "电影级宽幅"},
    "widescreen": {"ratio": "16:9", "desc": "标准宽屏"},
    "square": {"ratio": "1:1", "desc": "方形"},
}

COVER_PALETTES = {
    "ocean": ["#006994", "#40e0d0", "#fff"],
    "sunset": ["#ff6b35", "#f7c59f", "#1a1a2e"],
    "forest": ["#2d5016", "#a8d08d", "#f0f7ee"],
    "midnight": ["#0a0a0a", "#3366ff", "#00d4ff"],
    "cherry": ["#ff6b6b", "#ffd1dc", "#fff"],
    "gold": ["#c9a96e", "#0a0a0a", "#fff"],
    "lavender": ["#9b59b6", "#e8daef", "#2c3e50"],
    "arctic": ["#e2e8f0", "#2b6cb0", "#fff"],
    "earth": ["#8b4513", "#f4e9d9", "#2f4f4f"],
    "neon": ["#ff00ff", "#00ffff", "#0a0a0a"],
    "monochrome": ["#000", "#333", "#666", "#999", "#ccc", "#fff"],
}

COVER_RENDERINGS = {
    "watercolor": "水彩风",
    "oil-painting": "油画风",
    "flat": "扁平风",
    "3d": "3D渲染",
    "photography": "摄影风",
    "illustration": "插画风",
    "pixel": "像素风",
}

COVER_MOODS = {
    "energetic": "充满活力",
    "calm": "平静安宁",
    "mysterious": "神秘深邃",
    "professional": "专业严谨",
    "playful": "活泼有趣",
    "elegant": "优雅高级",
}


# ═══════════════════════════════════════════════════════════════
# 信息图配置
# ═══════════════════════════════════════════════════════════════

INFOGRAPHIC_LAYOUTS = {
    "hierarchy": "层级结构",
    "flowchart": "流程图",
    "comparison": "对比图",
    "timeline": "时间线",
    "matrix": "矩阵图",
    "radial": "放射状",
    "grid": "网格",
    "pyramid": "金字塔",
    "funnel": "漏斗图",
    "venn": "维恩图",
    "mindmap": "思维导图",
    "orgchart": "组织架构",
    "dashboard": "仪表盘",
    "map": "地图",
    "chart": "图表",
    "storyboard": "故事板",
    "process": "过程图",
    "circular": "环形图",
    "layered": "分层图",
    "modular": "模块化",
    "narrative": "叙事流",
}

INFOGRAPHIC_STYLES = {
    "minimal": "极简",
    "magazine": "杂志",
    "tech": "科技",
    "handdrawn": "手绘",
    "corporate": "商务",
    "playful": "活泼",
    "vintage": "复古",
    "neon": "霓虹",
    "pastel": "粉彩",
    "dark": "暗黑",
    "nature": "自然",
    "luxury": "奢华",
    "academic": "学术",
    "bold": "大胆",
    "retro": "怀旧",
    "futuristic": "未来感",
    "watercolor": "水彩",
    "geometric": "几何",
    "organic": "有机",
    "monochrome": "单色",
    "gradient": "渐变",
    "mosaic": "马赛克",
}


# ═══════════════════════════════════════════════════════════════
# 公众号主题配置
# ═══════════════════════════════════════════════════════════════

WECHAT_THEMES = {
    "default": {
        "name": "默认",
        "bg": "#ffffff",
        "text": "#333333",
        "accent": "#1a73e8",
        "code-bg": "#f6f8fa",
        "blockquote-border": "#1a73e8",
    },
    "dark": {
        "name": "暗色",
        "bg": "#1a1a2e",
        "text": "#e2e8f0",
        "accent": "#00d4ff",
        "code-bg": "#16213e",
        "blockquote-border": "#00d4ff",
    },
    "academic": {
        "name": "学术",
        "bg": "#fff",
        "text": "#2c3e50",
        "accent": "#2b6cb0",
        "code-bg": "#f7fafc",
        "blockquote-border": "#2b6cb0",
    },
    "minimal": {
        "name": "极简",
        "bg": "#fff",
        "text": "#333",
        "accent": "#000",
        "code-bg": "#f5f5f5",
        "blockquote-border": "#000",
    },
}


@dataclass
class StyleConfig:
    """统一风格配置"""
    platform: str = "wechat"
    theme: str = "default"
    xhs_style: str = "minimal"
    xhs_layout: str = "title"
    xhs_palette: str = "neutral"
    cover_type: str = "widescreen"
    cover_palette: str = "midnight"
    cover_rendering: str = "flat"
    cover_mood: str = "professional"
    infographic_layout: str = "hierarchy"
    infographic_style: str = "minimal"

    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "theme": self.theme,
            "xhs_style": self.xhs_style,
            "xhs_layout": self.xhs_layout,
            "xhs_palette": self.xhs_palette,
            "cover_type": self.cover_type,
            "cover_palette": self.cover_palette,
            "cover_rendering": self.cover_rendering,
            "cover_mood": self.cover_mood,
            "infographic_layout": self.infographic_layout,
            "infographic_style": self.infographic_style,
        }
