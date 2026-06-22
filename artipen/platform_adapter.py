#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台适配引擎 — 将Markdown/纯文本转换为各平台最优格式

支持平台：公众号(HTML) / 小红书(卡片prompt) / 知乎(Markdown) / 掘金(Markdown)

"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from .content_analyzer import ContentAnalysis, analyze_content
from .style_config import (
    StyleConfig, WECHAT_THEMES, XHS_STYLES, XHS_LAYOUTS, XHS_PALETTES,
)


# ═══════════════════════════════════════════════════════════════
# 公众号HTML转换
# ═══════════════════════════════════════════════════════════════

def _extract_external_links(text: str) -> List[str]:
    """提取Markdown中的外部链接"""
    return re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', text)


def _convert_links_to_footnotes(text: str) -> tuple:
    """将外部链接转为底部引用（微信不支持外链）"""
    links = _extract_external_links(text)
    if not links:
        return text, ""

    # 替换链接为上标编号
    for i, (label, url) in enumerate(links, 1):
        text = text.replace(f'[{label}]({url})', f'{label}<sup>[{i}]</sup>')

    # 生成底部引用
    footnotes = '\n'.join(
        f'<p style="font-size:12px;color:#999;margin:2px 0">[{i}] {label}: {url}</p>'
        for i, (label, url) in enumerate(links, 1)
    )
    return text, footnotes


def _render_code_blocks(html: str, theme: Dict) -> str:
    """渲染代码块带语法高亮"""
    def replace_code(match):
        lang = match.group(1) or ""
        code = match.group(2)
        return (
            f'<pre style="background:{theme["code-bg"]};padding:16px;border-radius:8px;'
            f'overflow-x:auto;font-size:14px;line-height:1.6;margin:16px 0">'
            f'<code>{code}</code></pre>'
        )
    return re.sub(r'```(\w*)\n([\s\S]*?)```', replace_code, html)


def _md_to_basic_html(text: str) -> str:
    """基础Markdown→HTML转换"""
    # 标题
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # 粗体/斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # 引用块
    text = re.sub(r'^>\s*(.+)$', r'<blockquote style="border-left:4px solid;padding-left:16px;margin:16px 0;color:#666">\1</blockquote>', text, flags=re.MULTILINE)

    # 列表
    text = re.sub(r'^[-*]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ul style="padding-left:20px">{m.group()}</ul>', text)

    # 段落
    paragraphs = text.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p style="margin:12px 0;line-height:1.8">{p}</p>'
        result.append(p)
    text = '\n'.join(result)

    return text


def to_wechat_html(text: str, config: StyleConfig) -> str:
    """转换为公众号兼容HTML"""
    theme = WECHAT_THEMES.get(config.theme, WECHAT_THEMES["default"])

    # 外链转底部引用
    text, footnotes = _convert_links_to_footnotes(text)

    # 基础HTML转换
    html = _md_to_basic_html(text)

    # 代码块渲染
    html = _render_code_blocks(html, theme)

    # 包装为完整HTML
    full_html = f"""<div style="max-width:680px;margin:0 auto;padding:20px;background:{theme['bg']};color:{theme['text']};font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;font-size:16px;line-height:1.8">
{html}
{f'<hr style="margin:30px 0;border:none;border-top:1px solid #eee"><div style="font-size:12px;color:#999"><strong>参考链接：</strong>{footnotes}</div>' if footnotes else ''}
</div>"""

    return full_html


# ═══════════════════════════════════════════════════════════════
# 小红书卡片prompt生成
# ═══════════════════════════════════════════════════════════════

def _split_content_to_cards(text: str, max_cards: int = 10) -> List[Dict]:
    """将长文拆分为卡片内容"""
    cards = []
    lines = text.strip().split('\n')
    current_card = {"type": "title", "content": "", "heading": ""}

    for line in lines:
        line = line.strip()

        # 标题卡
        if line.startswith('# ') and not cards:
            cards.append({
                "type": "title",
                "heading": line[2:],
                "content": "",
            })
            continue

        # 二级标题 → 新卡片
        if line.startswith('## '):
            if current_card["content"].strip():
                cards.append(current_card)
            current_card = {
                "type": "keypoints",
                "heading": line[3:],
                "content": "",
            }
            continue

        # 引用 → 金句卡
        if line.startswith('> '):
            if current_card["content"].strip():
                cards.append(current_card)
                current_card = {"type": "keypoints", "heading": "", "content": ""}
            cards.append({
                "type": "quote",
                "heading": "",
                "content": line[2:],
            })
            continue

        # 数字列表 → 要点卡
        if re.match(r'^\d+[\.\、]', line):
            current_card["content"] += line + '\n'
            current_card["type"] = "list"
            continue

        current_card["content"] += line + '\n'

    if current_card["content"].strip():
        cards.append(current_card)

    # 限制卡片数
    if len(cards) > max_cards:
        # 合并中间卡片
        merged = [cards[0]]  # 保留标题卡
        mid_content = ""
        for card in cards[1:-1]:
            mid_content += f"### {card['heading']}\n{card['content']}\n\n"
        # 按字数分割
        chunks = [mid_content[i:i+600] for i in range(0, len(mid_content), 600)]
        for chunk in chunks[:max_cards-2]:
            merged.append({"type": "keypoints", "heading": "", "content": chunk})
        if cards[-1]["type"] != "title":
            merged.append(cards[-1])
        cards = merged[:max_cards]

    # 添加总结卡
    if cards and cards[-1]["type"] != "summary":
        cards.append({
            "type": "summary",
            "heading": "总结",
            "content": f"本文核心要点整理\n来源：{cards[0].get('heading', '原创')}",
        })

    return cards


def to_xhs_prompts(text: str, config: StyleConfig) -> List[Dict]:
    """生成小红书卡片prompt列表"""
    cards = _split_content_to_cards(text)
    style = XHS_STYLES.get(config.xhs_style, XHS_STYLES["minimal"])
    palette = XHS_PALETTES.get(config.xhs_palette, XHS_PALETTES["neutral"])

    prompts = []
    for i, card in enumerate(cards):
        layout = XHS_LAYOUTS.get(card["type"], XHS_LAYOUTS["keypoints"])
        prompt = {
            "card_index": i + 1,
            "layout": layout["name"],
            "style": style["name"],
            "colors": palette["colors"],
            "heading": card.get("heading", ""),
            "content": card["content"][:300],
            "size": "1080x1440",
            "prompt_text": (
                f"Generate a {style['name']} style social media card for Xiaohongshu. "
                f"Layout: {layout['desc']}. "
                f"Colors: {', '.join(palette['colors'])}. "
                f"Size: 1080x1440px (3:4 vertical). "
                f"Heading: {card.get('heading', '')}. "
                f"Content: {card['content'][:200]}. "
                f"Style: {style['desc']}."
            ),
        }
        prompts.append(prompt)

    return prompts


# ═══════════════════════════════════════════════════════════════
# 知乎/掘金Markdown标准化
# ═══════════════════════════════════════════════════════════════

def to_zhihu_markdown(text: str, config: StyleConfig) -> str:
    """转换为知乎标准Markdown"""
    # 知乎保留标准Markdown格式
    # 1. 确保标题层级正确
    # 2. 保留代码块语言标注
    # 3. 保留LaTeX公式
    # 4. 引用块标准化

    # 清理非标准语法
    text = re.sub(r'```mermaid\n[\s\S]*?```', '[Mermaid图表请在知乎编辑器中重新绘制]', text)

    # 确保标题前有空行
    text = re.sub(r'([^\n])(\n#{1,6}\s)', r'\1\n\2', text)

    # 确保代码块前后有空行
    text = re.sub(r'([^\n])(\n```)', r'\1\n\2', text)
    text = re.sub(r'(```[^\n]*\n[\s\S]*?```)(\n[^\n])', r'\1\n\2', text)

    return text.strip()


def to_juejin_markdown(text: str, config: StyleConfig) -> str:
    """转换为掘金标准Markdown"""
    # 掘金兼容标准Markdown，但有一些特殊要求

    # 1. 提取/生成frontmatter
    title = ""
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if title_match:
        title = title_match.group(1)

    # 提取关键词作为标签
    keywords = re.findall(r'[\u4e00-\u9fff]{2,6}|[A-Za-z]{3,}', title)
    tags = keywords[:4] if keywords else ["技术"]

    frontmatter = f"""---
title: {title}
tags: {', '.join(tags)}
date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
---

"""

    # 2. 确保代码块有语言标注
    text = re.sub(r'```\n', '```text\n', text)

    # 3. 清理非标准语法
    text = re.sub(r'```mermaid\n[\s\S]*?```', '[流程图请使用掘金编辑器绘制]', text)

    return frontmatter + text.strip()


# ═══════════════════════════════════════════════════════════════
# 统一适配入口
# ═══════════════════════════════════════════════════════════════

def adapt_to_platform(text: str, platform: str, config: Optional[StyleConfig] = None) -> Dict:
    """
    统一适配入口：将文本转换为指定平台格式。

    Args:
        text: 输入文本（Markdown/纯文本）
        platform: 目标平台（wechat/xhs/zhihu/juejin）
        config: 风格配置（可选）

    Returns:
        Dict: {"platform": str, "output": str, "metadata": dict}
    """
    if config is None:
        config = StyleConfig(platform=platform)

    analysis = analyze_content(text)

    if platform == "wechat":
        output = to_wechat_html(text, config)
        return {
            "platform": "wechat",
            "format": "html",
            "output": output,
            "metadata": analysis.to_dict(),
        }

    elif platform == "xhs":
        prompts = to_xhs_prompts(text, config)
        return {
            "platform": "xhs",
            "format": "prompts",
            "output": prompts,
            "metadata": analysis.to_dict(),
        }

    elif platform == "zhihu":
        output = to_zhihu_markdown(text, config)
        return {
            "platform": "zhihu",
            "format": "markdown",
            "output": output,
            "metadata": analysis.to_dict(),
        }

    elif platform == "juejin":
        output = to_juejin_markdown(text, config)
        return {
            "platform": "juejin",
            "format": "markdown",
            "output": output,
            "metadata": analysis.to_dict(),
        }

    else:
        raise ValueError(f"Unsupported platform: {platform}")


def adapt_to_all(text: str, config: Optional[StyleConfig] = None) -> Dict[str, Dict]:
    """一键生成所有平台格式"""
    platforms = ["wechat", "xhs", "zhihu", "juejin"]
    results = {}
    for platform in platforms:
        results[platform] = adapt_to_platform(text, platform, config)
    return results
