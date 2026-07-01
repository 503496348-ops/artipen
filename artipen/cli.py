#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
妙笔生花 · ArtiPen — CLI 入口

用法:
    python artipen/cli.py article.md --platforms wechat,xhs,zhihu,juejin
    python artipen/cli.py article.md --platform wechat
    python artipen/cli.py article.md --platform xhs
    python artipen/cli.py article.md --check-ai-flavor
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 确保可以导入同级模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="妙笔生花 ArtiPen — 多平台文章编排引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s article.md --platforms wechat,xhs,zhihu,juejin
  %(prog)s article.md --platform wechat
  %(prog)s article.md --platform xhs --xhs-style tech
  %(prog)s article.md --check-ai-flavor
  %(prog)s article.md --analyze
  %(prog)s article.md --topic-brief --topic-category ai-models
  %(prog)s article.md --longform-plan
  %(prog)s article.md --research-brief --subject "目标产品"
        """
    )

    parser.add_argument("input", help="输入文件路径（Markdown/纯文本）")
    parser.add_argument("--platforms", help="目标平台（逗号分隔：wechat,xhs,zhihu,juejin）")
    parser.add_argument("--platform", help="单个目标平台")
    parser.add_argument("--output", "-o", default="output", help="输出目录（默认：output）")
    parser.add_argument("--theme", default="default", help="公众号主题（default/dark/academic/minimal）")
    parser.add_argument("--xhs-style", default="minimal", help="小红书风格（minimal/magazine/tech/...）")
    parser.add_argument("--xhs-palette", default="neutral", help="小红书配色（warm/cool/neutral）")
    parser.add_argument("--check-ai-flavor", action="store_true", help="检测AI味")
    parser.add_argument("--analyze", action="store_true", help="仅分析内容结构")
    parser.add_argument("--topic-brief", action="store_true", help="从 AI 热点源生成选题简报")
    parser.add_argument("--topic-query", help="热点选题关键词")
    parser.add_argument("--topic-category", choices=["ai-models", "ai-products", "industry", "paper", "tip"], help="热点分类")
    parser.add_argument("--topic-limit", type=int, default=10, help="选题数量（默认10）")
    parser.add_argument("--longform-plan", action="store_true", help="生成公众号长文写作蓝图")
    parser.add_argument("--research-brief", action="store_true", help="生成深度研究证据包")
    parser.add_argument("--subject", help="研究对象/文章主题")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")

    # 热点选题简报：input 可用任意占位文件，实际从公开热点源拉取
    if args.topic_brief:
        from artipen.topic_intelligence import generate_topic_brief
        brief = generate_topic_brief(
            query=args.topic_query,
            category=args.topic_category,
            limit=args.topic_limit,
        )
        if args.format == "json":
            print(json.dumps({k: v for k, v in brief.items() if k != "markdown"}, ensure_ascii=False, indent=2))
        else:
            print(brief["markdown"])
        return

    # 内容分析
    from artipen.content_analyzer import analyze_content, recommend_platform_config
    analysis = analyze_content(text)

    if args.longform_plan:
        from artipen.longform_writer import build_longform_plan, render_plan_markdown
        plan = build_longform_plan(text)
        if args.format == "json":
            print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(render_plan_markdown(plan))
        return

    if args.research_brief:
        from artipen.research_brief import build_research_brief, render_research_brief_markdown
        brief = build_research_brief(text, subject=args.subject)
        if args.format == "json":
            print(json.dumps(brief.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(render_research_brief_markdown(brief))
        return

    if args.analyze:
        if args.format == "json":
            print(json.dumps(analysis.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"📄 内容分析报告")
            print(f"{'='*50}")
            print(f"标题: {analysis.title}")
            print(f"副标题: {analysis.subtitle}")
            print(f"关键词: {', '.join(analysis.keywords)}")
            print(f"总字数: {analysis.total_words}")
            print(f"章节数: {len(analysis.sections)}")
            print(f"代码块: {analysis.code_blocks}")
            print(f"含数学公式: {'是' if analysis.has_math else '否'}")
            print(f"含Mermaid图: {'是' if analysis.has_mermaid else '否'}")
            print(f"预估小红书卡片数: {analysis.estimated_cards}")
            print(f"配图位置: 第{', '.join(str(i+1) for i in analysis.illustration_positions)}节")
            if analysis.data_points:
                print(f"数据点: {', '.join(analysis.data_points[:5])}")
            if analysis.quotes:
                print(f"金句: {analysis.quotes[0][:50]}...")
        return

    # AI味检测
    if args.check_ai_flavor:
        try:
            from artipen.ai_flavor_engine import detect_ai_flavor
            report = detect_ai_flavor(text)
            if args.format == "json":
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"\n{'='*50}")
                print(f"🔍 AI味检测报告")
                print(f"{'='*50}")
                d = report.dimension_score.to_dict()
                for k, v in d.items():
                    if k != "需修订":
                        bar = "█" * int(v) + "░" * (10 - int(v))
                        print(f"  {k}: {bar} {v}/10")
                print(f"  需修订: {'是 ⚠️' if d['需修订'] else '否 ✅'}")
                print(f"\n命中模式: {len(report.pattern_hits)}项")
                for p in report.pattern_hits[:5]:
                    print(f"  ⚠️ [{p.category}] {p.name}")
                print(f"\n总问题数: {report.total_issues}")
        except ImportError:
            print("⚠️ AI味检测模块未找到，请确保 ai_flavor_engine.py 在 artipen/ 目录下", file=sys.stderr)
        return

    # 平台适配
    from artipen.platform_adapter import adapt_to_platform, adapt_to_all
    from artipen.style_config import StyleConfig

    config = StyleConfig(
        theme=args.theme,
        xhs_style=args.xhs_style,
        xhs_palette=args.xhs_palette,
    )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",")]
    elif args.platform:
        platforms = [args.platform]
    else:
        platforms = ["wechat", "xhs", "zhihu", "juejin"]

    for platform in platforms:
        config.platform = platform
        result = adapt_to_platform(text, platform, config)

        platform_dir = output_dir / platform
        platform_dir.mkdir(parents=True, exist_ok=True)

        if platform == "wechat":
            out_file = platform_dir / f"{input_path.stem}.html"
            out_file.write_text(result["output"], encoding="utf-8")
            print(f"✅ 公众号HTML: {out_file}")

        elif platform == "xhs":
            prompts = result["output"]
            for prompt in prompts:
                card_file = platform_dir / f"card_{prompt['card_index']:02d}.txt"
                card_file.write_text(prompt["prompt_text"], encoding="utf-8")
            print(f"✅ 小红书卡片: {platform_dir}/ ({len(prompts)}张)")

        elif platform == "zhihu":
            out_file = platform_dir / f"{input_path.stem}.md"
            out_file.write_text(result["output"], encoding="utf-8")
            print(f"✅ 知乎Markdown: {out_file}")

        elif platform == "juejin":
            out_file = platform_dir / f"{input_path.stem}.md"
            out_file.write_text(result["output"], encoding="utf-8")
            print(f"✅ 掘金Markdown: {out_file}")

    # 输出分析摘要
    print(f"\n📊 内容分析:")
    print(f"  标题: {analysis.title}")
    print(f"  字数: {analysis.total_words}")
    print(f"  章节: {len(analysis.sections)}")
    print(f"  小红书卡片: {analysis.estimated_cards}张")
    print(f"  配图位置: {len(analysis.illustration_positions)}处")

    # 推荐配置
    recommended = recommend_platform_config(analysis)
    print(f"\n💡 推荐配置:")
    for k, v in recommended.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
