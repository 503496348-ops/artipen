"""
Format Templates — pre-built templates for common content formats.
Provides ready-to-use schemas and prompts for articles, emails,
reports, summaries, and other structured content.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContentTemplate:
    """A reusable content template."""
    name: str
    description: str
    schema: dict
    example: dict
    prompt_template: str

    def render_prompt(self, **kwargs) -> str:
        """Render the prompt template with variables."""
        return self.prompt_template.format(**kwargs)

    def get_schema_prompt(self) -> str:
        """Get a prompt that enforces this template's schema."""
        from schema_prompts import SchemaToPrompt
        return SchemaToPrompt.from_json_schema(self.schema)


# === Article Templates ===

ARTICLE_TEMPLATE = ContentTemplate(
    name="article",
    description="Structured article with sections and key points",
    schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "subtitle": {"type": "string"},
            "introduction": {"type": "string"},
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "content": {"type": "string"},
                        "key_points": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["heading", "content"],
                },
            },
            "conclusion": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["title", "introduction", "sections", "conclusion"],
    },
    example={
        "title": "The Future of AI Agents",
        "subtitle": "How autonomous systems are reshaping software",
        "introduction": "AI agents represent a paradigm shift...",
        "sections": [
            {
                "heading": "What Are AI Agents?",
                "content": "AI agents are autonomous systems that...",
                "key_points": ["Autonomy", "Tool use", "Planning"],
            }
        ],
        "conclusion": "The future of AI agents is bright...",
        "tags": ["AI", "agents", "automation"],
    },
    prompt_template="Write a {word_count}-word article about: {topic}\nTone: {tone}\nAudience: {audience}",
)

# === Email Templates ===

EMAIL_TEMPLATE = ContentTemplate(
    name="email",
    description="Professional email with subject, body, and CTA",
    schema={
        "type": "object",
        "properties": {
            "subject": {"type": "string"},
            "greeting": {"type": "string"},
            "body": {"type": "string"},
            "call_to_action": {"type": "string"},
            "closing": {"type": "string"},
            "signature": {"type": "string"},
        },
        "required": ["subject", "body"],
    },
    example={
        "subject": "Project Update: Q2 Milestones",
        "greeting": "Hi team,",
        "body": "I wanted to share our progress on...",
        "call_to_action": "Please review the attached document by Friday.",
        "closing": "Best regards,",
        "signature": "The Project Team",
    },
    prompt_template="Write a {tone} email about: {purpose}\nRecipient: {recipient}\nKey message: {message}",
)

# === Report Templates ===

REPORT_TEMPLATE = ContentTemplate(
    name="report",
    description="Structured report with findings and recommendations",
    schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "executive_summary": {"type": "string"},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "detail": {"type": "string"},
                        "significance": {"type": "string", "enum": ["high", "medium", "low"]},
                        "evidence": {"type": "string"},
                    },
                },
            },
            "recommendations": {"type": "array", "items": {"type": "string"}},
            "next_steps": {"type": "array", "items": {"type": "string"}},
            "appendix": {"type": "string"},
        },
        "required": ["title", "executive_summary", "findings"],
    },
    example={
        "title": "Market Analysis Report",
        "executive_summary": "Our analysis reveals...",
        "findings": [
            {
                "topic": "Market Growth",
                "detail": "The market is growing at 15% annually",
                "significance": "high",
                "evidence": "According to industry reports...",
            }
        ],
        "recommendations": ["Expand into Asian markets", "Invest in R&D"],
        "next_steps": ["Schedule follow-up meeting", "Prepare detailed proposal"],
    },
    prompt_template="Generate a {report_type} report about: {topic}\nData: {data_points}\nAudience: {audience}",
)

# === Summary Templates ===

SUMMARY_TEMPLATE = ContentTemplate(
    name="summary",
    description="Concise summary with key takeaways",
    schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "one_liner": {"type": "string"},
            "key_points": {"type": "array", "items": {"type": "string"}},
            "details": {"type": "string"},
            "action_items": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["title", "one_liner", "key_points"],
    },
    example={
        "title": "Meeting Summary",
        "one_liner": "Discussed Q2 roadmap and resource allocation",
        "key_points": ["Approved new feature", "Hiring 2 engineers", "Launch in July"],
        "details": "The team met to discuss...",
        "action_items": ["Prepare spec by Friday", "Post job listings"],
    },
    prompt_template="Summarize the following:\n\n{content}\n\nFocus on: {focus}",
)

# === Review Templates ===

REVIEW_TEMPLATE = ContentTemplate(
    name="review",
    description="Structured product/service review",
    schema={
        "type": "object",
        "properties": {
            "product": {"type": "string"},
            "overall_rating": {"type": "number"},
            "summary": {"type": "string"},
            "aspects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "rating": {"type": "number"},
                        "pros": {"type": "array", "items": {"type": "string"}},
                        "cons": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "verdict": {"type": "string"},
            "alternatives": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["product", "overall_rating", "summary", "verdict"],
    },
    example={
        "product": "ProductX",
        "overall_rating": 4.2,
        "summary": "A solid choice for developers...",
        "aspects": [
            {
                "name": "Ease of Use",
                "rating": 4.5,
                "pros": ["Intuitive interface", "Good docs"],
                "cons": ["Steep learning curve for advanced features"],
            }
        ],
        "verdict": "Recommended for intermediate users",
        "alternatives": ["ProductY", "ProductZ"],
    },
    prompt_template="Review: {product}\nAspects: {aspects}\nExperience: {experience}",
)

# === Template Registry ===

TEMPLATES = {
    "article": ARTICLE_TEMPLATE,
    "email": EMAIL_TEMPLATE,
    "report": REPORT_TEMPLATE,
    "summary": SUMMARY_TEMPLATE,
    "review": REVIEW_TEMPLATE,
}


def get_template(name: str) -> Optional[ContentTemplate]:
    """Get a template by name."""
    return TEMPLATES.get(name)


def list_templates() -> list[dict]:
    """List all available templates."""
    return [
        {"name": t.name, "description": t.description}
        for t in TEMPLATES.values()
    ]


def generate_from_template(
    template_name: str,
    llm_fn: callable,
    **kwargs,
) -> dict:
    """
    Generate content using a template.

    Args:
        template_name: Name of the template to use
        llm_fn: LLM function to call
        **kwargs: Variables for the prompt template

    Returns:
        Generated content matching the template schema
    """
    from structured_generator import StructuredGenerator
    from output_validator import OutputValidator

    template = get_template(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")

    prompt = template.render_prompt(**kwargs)
    generator = StructuredGenerator(llm_fn=llm_fn)
    result = generator.generate_json(prompt, template.schema)

    if not result.is_valid:
        # Try with lenient validation
        validator = OutputValidator(strategy="lenient")
        val_result = validator.validate_json(result.raw_text, template.schema)
        if val_result.is_valid:
            return val_result.output

    return result.parsed
