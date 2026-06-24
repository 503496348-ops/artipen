"""
Structured Generator — constrain LLM output to typed schemas.
Inspired by Outlines' structured output approach.

Ensures LLM outputs match JSON Schema / Pydantic models /
regex patterns / literal choices at generation time.
"""

import json
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Type, get_type_hints
from enum import Enum

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    JSON = "json"
    PYDANTIC = "pydantic"
    REGEX = "regex"
    CHOICE = "choice"
    TEXT = "text"


@dataclass
class StructuredOutput:
    """Result of structured generation."""
    raw_text: str
    parsed: Any
    format: OutputFormat
    is_valid: bool
    validation_errors: list[str] = field(default_factory=list)
    attempts: int = 1

    def to_dict(self) -> dict:
        return {
            "parsed": self.parsed if not isinstance(self.parsed, Enum) else self.parsed.value,
            "format": self.format.value,
            "valid": self.is_valid,
            "attempts": self.attempts,
        }


class SchemaBuilder:
    """
    Build JSON schemas from Python type hints and Pydantic models.

    Supports:
    - Basic types (str, int, float, bool)
    - Optional types
    - List/Dict types
    - Nested models
    - Enums
    - Literal types
    """

    @staticmethod
    def from_type_hints(cls: type) -> dict:
        """Build JSON schema from a class with type hints."""
        hints = get_type_hints(cls)
        properties = {}
        required = []

        for name, hint in hints.items():
            if name.startswith('_'):
                continue

            prop, is_required = SchemaBuilder._type_to_schema(hint)
            properties[name] = prop
            if is_required:
                required.append(name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    @staticmethod
    def _type_to_schema(hint: type) -> tuple[dict, bool]:
        """Convert a type hint to JSON schema property."""
        # Handle Optional
        origin = getattr(hint, '__origin__', None)

        if origin is type(None):
            return {"type": "null"}, False

        if origin is type:
            # Optional[X] = Union[X, None]
            args = getattr(hint, '__args__', ())
            if len(args) == 2 and type(None) in args:
                inner = args[0] if args[1] is type(None) else args[1]
                prop, _ = SchemaBuilder._type_to_schema(inner)
                return prop, False

        if hint is str:
            return {"type": "string"}, True
        elif hint is int:
            return {"type": "integer"}, True
        elif hint is float:
            return {"type": "number"}, True
        elif hint is bool:
            return {"type": "boolean"}, True
        elif hint is list or origin is list:
            args = getattr(hint, '__args__', (str,))
            item_prop, _ = SchemaBuilder._type_to_schema(args[0]) if args else ({"type": "string"}, True)
            return {"type": "array", "items": item_prop}, True
        elif hint is dict or origin is dict:
            return {"type": "object"}, True
        elif isinstance(hint, type) and issubclass(hint, Enum):
            return {"type": "string", "enum": [e.value for e in hint]}, True
        elif hasattr(hint, '__annotations__'):
            # Nested model
            return SchemaBuilder.from_type_hints(hint), True
        else:
            return {"type": "string"}, True

    @staticmethod
    def from_pydantic_model(model) -> dict:
        """Build JSON schema from a Pydantic model."""
        try:
            if hasattr(model, 'model_json_schema'):
                return model.model_json_schema()
            elif hasattr(model, 'schema'):
                return model.schema()
        except Exception:
            pass
        # Fallback to type hints
        return SchemaBuilder.from_type_hints(model)

    @staticmethod
    def from_literal_choices(choices: list[str]) -> dict:
        """Build schema for literal choice constraint."""
        return {
            "type": "string",
            "enum": choices,
        }

    @staticmethod
    def from_regex(pattern: str) -> dict:
        """Build schema for regex constraint."""
        return {
            "type": "string",
            "pattern": pattern,
        }


class StructuredGenerator:
    """
    Generate structured outputs from LLMs.

    Features:
    - JSON Schema enforcement
    - Pydantic model generation
    - Regex pattern matching
    - Choice constraint
    - Retry with feedback
    - Schema-to-prompt conversion
    """

    def __init__(self, llm_fn: Optional[callable] = None, max_retries: int = 3):
        self.llm_fn = llm_fn
        self.max_retries = max_retries

    def generate_json(
        self,
        prompt: str,
        schema: dict,
        system_prompt: Optional[str] = None,
    ) -> StructuredOutput:
        """Generate JSON matching a schema."""
        enhanced_prompt = self._build_json_prompt(prompt, schema)

        for attempt in range(self.max_retries):
            raw = self._call_llm(enhanced_prompt, system_prompt)
            parsed, errors = self._validate_json(raw, schema)

            if not errors:
                return StructuredOutput(
                    raw_text=raw,
                    parsed=parsed,
                    format=OutputFormat.JSON,
                    is_valid=True,
                    attempts=attempt + 1,
                )

            # Retry with error feedback
            enhanced_prompt = self._build_retry_prompt(raw, errors, schema)

        return StructuredOutput(
            raw_text=raw,
            parsed=parsed,
            format=OutputFormat.JSON,
            is_valid=False,
            validation_errors=errors,
            attempts=self.max_retries,
        )

    def generate_choice(
        self,
        prompt: str,
        choices: list[str],
        system_prompt: Optional[str] = None,
    ) -> StructuredOutput:
        """Generate output constrained to specific choices."""
        choice_str = " | ".join(f'"{c}"' for c in choices)
        enhanced = f"{prompt}\n\nYou MUST respond with exactly one of: {choice_str}"

        for attempt in range(self.max_retries):
            raw = self._call_llm(enhanced, system_prompt).strip().strip('"\'')
            if raw in choices:
                return StructuredOutput(
                    raw_text=raw,
                    parsed=raw,
                    format=OutputFormat.CHOICE,
                    is_valid=True,
                    attempts=attempt + 1,
                )

        # Find closest match
        closest = min(choices, key=lambda c: self._levenshtein(raw, c))
        return StructuredOutput(
            raw_text=raw,
            parsed=closest,
            format=OutputFormat.CHOICE,
            is_valid=False,
            validation_errors=[f"'{raw}' not in choices, closest: '{closest}'"],
            attempts=self.max_retries,
        )

    def generate_regex(
        self,
        prompt: str,
        pattern: str,
        system_prompt: Optional[str] = None,
    ) -> StructuredOutput:
        """Generate output matching a regex pattern."""
        enhanced = f"{prompt}\n\nYour response must match this pattern: /{pattern}/"

        for attempt in range(self.max_retries):
            raw = self._call_llm(enhanced, system_prompt).strip()
            if re.fullmatch(pattern, raw):
                return StructuredOutput(
                    raw_text=raw,
                    parsed=raw,
                    format=OutputFormat.REGEX,
                    is_valid=True,
                    attempts=attempt + 1,
                )

        return StructuredOutput(
            raw_text=raw,
            parsed=raw,
            format=OutputFormat.REGEX,
            is_valid=False,
            validation_errors=[f"Output doesn't match /{pattern}/"],
            attempts=self.max_retries,
        )

    def generate_pydantic(
        self,
        prompt: str,
        model: Any,
        system_prompt: Optional[str] = None,
    ) -> StructuredOutput:
        """Generate output matching a Pydantic model."""
        schema = SchemaBuilder.from_pydantic_model(model)
        result = self.generate_json(prompt, schema, system_prompt)

        if result.is_valid:
            try:
                if hasattr(model, 'model_validate'):
                    result.parsed = model.model_validate(result.parsed)
                elif hasattr(model, 'parse_obj'):
                    result.parsed = model.parse_obj(result.parsed)
                result.format = OutputFormat.PYDANTIC
            except Exception as e:
                result.is_valid = False
                result.validation_errors.append(str(e))

        return result

    def _build_json_prompt(self, prompt: str, schema: dict) -> str:
        """Build a prompt that instructs JSON output."""
        schema_str = json.dumps(schema, indent=2)
        return f"""{prompt}

Respond with valid JSON matching this schema:
```json
{schema_str}
```

Return ONLY the JSON object, no markdown fences, no explanation."""

    def _build_retry_prompt(self, raw: str, errors: list[str], schema: dict) -> str:
        """Build a retry prompt with error feedback."""
        error_str = "\n".join(f"- {e}" for e in errors)
        schema_str = json.dumps(schema, indent=2)
        return f"""Your previous response had validation errors:
{error_str}

Your response was:
{raw}

Fix the errors and respond with valid JSON matching:
```json
{schema_str}
```

Return ONLY the JSON object."""

    def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call the LLM."""
        if self.llm_fn:
            if system_prompt:
                return self.llm_fn(prompt, system=system_prompt)
            return self.llm_fn(prompt)
        # Placeholder for when no LLM is configured
        return '{"error": "No LLM configured"}'

    def _validate_json(self, raw: str, schema: dict) -> tuple[Any, list[str]]:
        """Validate raw text against JSON schema."""
        errors = []

        # Try to extract JSON from response
        json_str = raw.strip()
        # Remove markdown fences
        json_str = re.sub(r'^```(?:json)?\s*', '', json_str)
        json_str = re.sub(r'\s*```$', '', json_str)

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            return None, [f"Invalid JSON: {e}"]

        # Basic schema validation
        if "required" in schema:
            for field in schema["required"]:
                if field not in parsed:
                    errors.append(f"Missing required field: {field}")

        if "properties" in schema:
            for field, spec in schema["properties"].items():
                if field in parsed:
                    expected_type = spec.get("type")
                    if expected_type and not self._check_type(parsed[field], expected_type):
                        errors.append(f"Field '{field}': expected {expected_type}, got {type(parsed[field]).__name__}")

        return parsed, errors

    def _check_type(self, value: Any, expected: str) -> bool:
        """Check if value matches expected JSON type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        expected_py = type_map.get(expected)
        if expected_py is None:
            return True
        return isinstance(value, expected_py)

    def _levenshtein(self, s1: str, s2: str) -> int:
        """Compute Levenshtein distance."""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev[j + 1] + 1
                deletions = curr[j] + 1
                substitutions = prev[j] + (c1 != c2)
                curr.append(min(insertions, deletions, substitutions))
            prev = curr
        return prev[-1]
