"""
Schema Prompts — auto-generate prompts from type definitions.
Inspired by Outlines' type system mapping.

Converts Python types, Pydantic models, and JSON schemas
into LLM prompts that enforce structured output.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SchemaToPrompt:
    """
    Convert schemas to LLM prompts.

    Generates natural language descriptions of expected output
    format from JSON Schema, Pydantic models, or type hints.
    """

    @staticmethod
    def from_json_schema(schema: dict, task: str = "") -> str:
        """Generate a prompt from a JSON schema."""
        parts = []

        if task:
            parts.append(task)
            parts.append("")

        parts.append("Respond with a JSON object matching this structure:")
        parts.append("")
        parts.append(SchemaToPrompt._describe_schema(schema, indent=0))
        parts.append("")
        parts.append("Return ONLY the JSON object, no markdown fences or explanation.")

        return "\n".join(parts)

    @staticmethod
    def from_dict_example(example: dict, task: str = "") -> str:
        """Generate a prompt from an example dict."""
        parts = []

        if task:
            parts.append(task)
            parts.append("")

        parts.append("Respond with JSON matching this format:")
        parts.append("```json")
        parts.append(json.dumps(example, indent=2, ensure_ascii=False))
        parts.append("```")
        parts.append("")
        parts.append("Return ONLY the JSON object.")

        return "\n".join(parts)

    @staticmethod
    def from_field_descriptions(fields: dict[str, str], task: str = "") -> str:
        """Generate a prompt from field descriptions."""
        parts = []

        if task:
            parts.append(task)
            parts.append("")

        parts.append("Your response must include these fields:")
        parts.append("")
        for name, desc in fields.items():
            parts.append(f'- **{name}**: {desc}')

        parts.append("")
        parts.append("Respond with a JSON object containing all fields.")

        return "\n".join(parts)

    @staticmethod
    def _describe_schema(schema: dict, indent: int = 0) -> str:
        """Recursively describe a JSON schema in natural language."""
        lines = []
        prefix = "  " * indent
        schema_type = schema.get("type", "any")

        if schema_type == "object":
            properties = schema.get("properties", {})
            required = set(schema.get("required", []))

            lines.append(f"{prefix}{{")
            for name, prop in properties.items():
                req_marker = " (required)" if name in required else " (optional)"
                desc = prop.get("description", "")
                prop_type = prop.get("type", "any")

                if prop_type == "object":
                    lines.append(f'{prefix}  "{name}":{req_marker}')
                    lines.append(SchemaToPrompt._describe_schema(prop, indent + 2))
                elif prop_type == "array":
                    items = prop.get("items", {})
                    item_type = items.get("type", "any")
                    lines.append(f'{prefix}  "{name}": [{item_type}]{req_marker}')
                    if desc:
                        lines.append(f"{prefix}    # {desc}")
                else:
                    enum_vals = prop.get("enum")
                    if enum_vals:
                        lines.append(f'{prefix}  "{name}": one of {enum_vals}{req_marker}')
                    else:
                        lines.append(f'{prefix}  "{name}": {prop_type}{req_marker}')
                    if desc:
                        lines.append(f"{prefix}    # {desc}")
            lines.append(f"{prefix}}}")

        elif schema_type == "array":
            items = schema.get("items", {})
            lines.append(f"{prefix}[")
            lines.append(SchemaToPrompt._describe_schema(items, indent + 1))
            lines.append(f"{prefix}]")

        else:
            enum_vals = schema.get("enum")
            if enum_vals:
                lines.append(f"{prefix}One of: {enum_vals}")
            else:
                lines.append(f"{prefix}{schema_type}")

        return "\n".join(lines)


class PromptTemplates:
    """Pre-built prompt templates for common content formats."""

    @staticmethod
    def article_prompt(topic: str, sections: int = 5, word_count: int = 1000) -> str:
        """Generate prompt for structured article."""
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Article title"},
                "subtitle": {"type": "string", "description": "Optional subtitle"},
                "introduction": {"type": "string", "description": "Opening paragraph"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "heading": {"type": "string"},
                            "content": {"type": "string"},
                            "key_points": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "conclusion": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "introduction", "sections", "conclusion"],
        }
        return SchemaToPrompt.from_json_schema(
            schema,
            task=f"Write a {word_count}-word article about: {topic}\nInclude {sections} main sections.",
        )

    @staticmethod
    def email_prompt(purpose: str, tone: str = "professional") -> str:
        """Generate prompt for structured email."""
        schema = {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "greeting": {"type": "string"},
                "body": {"type": "string"},
                "call_to_action": {"type": "string"},
                "closing": {"type": "string"},
            },
            "required": ["subject", "body"],
        }
        return SchemaToPrompt.from_json_schema(
            schema,
            task=f"Write a {tone} email for: {purpose}",
        )

    @staticmethod
    def report_prompt(title: str, data_points: list[str]) -> str:
        """Generate prompt for structured report."""
        schema = {
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
                        },
                    },
                },
                "recommendations": {"type": "array", "items": {"type": "string"}},
                "next_steps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "executive_summary", "findings"],
        }
        data_str = ", ".join(data_points)
        return SchemaToPrompt.from_json_schema(
            schema,
            task=f"Generate report: {title}\nData points to cover: {data_str}",
        )

    @staticmethod
    def review_prompt(product: str, aspects: list[str]) -> str:
        """Generate prompt for structured product review."""
        schema = {
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
            },
            "required": ["product", "overall_rating", "summary", "verdict"],
        }
        aspects_str = ", ".join(aspects)
        return SchemaToPrompt.from_json_schema(
            schema,
            task=f"Review: {product}\nAspects to evaluate: {aspects_str}",
        )
