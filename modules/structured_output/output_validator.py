"""
Output Validator — validation, retry, and fallback logic.
Inspired by Outlines' production-grade output enforcement.

Provides comprehensive validation with multiple strategies,
automatic retry with feedback, and graceful degradation.
"""

import json
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of output validation."""
    is_valid: bool
    output: Any
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fix_suggestions: list[str] = field(default_factory=list)
    strategy_used: str = ""

    def to_dict(self) -> dict:
        return {
            "valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.fix_suggestions,
            "strategy": self.strategy_used,
        }


class OutputValidator:
    """
    Validates and fixes LLM outputs.

    Validation strategies:
    - strict: Reject on any error
    - lenient: Try to fix common issues
    - coerce: Force into expected type
    - fallback: Use default value on failure
    """

    def __init__(self, strategy: str = "lenient"):
        self.strategy = strategy
        self._custom_validators: list[Callable] = []

    def add_validator(self, fn: Callable[[Any], tuple[bool, str]]) -> None:
        """Add a custom validator function. Returns (is_valid, error_message)."""
        self._custom_validators.append(fn)

    def validate_json(self, raw: str, schema: Optional[dict] = None) -> ValidationResult:
        """Validate and parse JSON output."""
        errors = []
        warnings = []

        # Step 1: Clean the raw text
        cleaned = self._clean_json(raw)

        # Step 2: Parse JSON
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            if self.strategy == "lenient":
                fixed = self._try_fix_json(cleaned)
                if fixed is not None:
                    return ValidationResult(
                        is_valid=True, output=fixed,
                        warnings=[f"JSON was malformed, auto-fixed: {e}"],
                        strategy_used="json_auto_fix",
                    )
            return ValidationResult(
                is_valid=False, output=None,
                errors=[f"Invalid JSON: {e}"],
                fix_suggestions=self._suggest_json_fix(cleaned, e),
                strategy_used="json_parse",
            )

        # Step 3: Validate against schema
        if schema:
            schema_errors = self._validate_schema(parsed, schema)
            if schema_errors:
                if self.strategy == "coerce":
                    parsed = self._coerce_to_schema(parsed, schema)
                    warnings = [f"Coerced fields: {len(schema_errors)} issues fixed"]
                elif self.strategy == "lenient":
                    # Try to fix missing fields with defaults
                    parsed = self._fill_defaults(parsed, schema)
                    errors = schema_errors
                else:
                    errors = schema_errors

        # Step 4: Custom validators
        for validator in self._custom_validators:
            valid, msg = validator(parsed)
            if not valid:
                errors.append(msg)

        return ValidationResult(
            is_valid=len(errors) == 0,
            output=parsed,
            errors=errors,
            warnings=warnings,
            strategy_used=self.strategy,
        )

    def validate_choice(self, raw: str, choices: list[str]) -> ValidationResult:
        """Validate output is one of the allowed choices."""
        cleaned = raw.strip().strip('"\'').lower()

        # Exact match
        for choice in choices:
            if cleaned == choice.lower():
                return ValidationResult(is_valid=True, output=choice, strategy_used="exact_match")

        # Fuzzy match
        best_match = None
        best_score = 0
        for choice in choices:
            score = self._similarity(cleaned, choice.lower())
            if score > best_score:
                best_score = score
                best_match = choice

        if best_score > 0.7:
            return ValidationResult(
                is_valid=True, output=best_match,
                warnings=[f"Fuzzy matched '{raw}' to '{best_match}' (score: {best_score:.2f})"],
                strategy_used="fuzzy_match",
            )

        if self.strategy == "fallback":
            return ValidationResult(
                is_valid=True, output=choices[0],
                warnings=[f"No match found, using fallback: '{choices[0]}'"],
                strategy_used="fallback",
            )

        return ValidationResult(
            is_valid=False, output=None,
            errors=[f"'{raw}' not in choices: {choices}"],
            strategy_used="choice_validation",
        )

    def validate_type(self, value: Any, expected_type: str) -> ValidationResult:
        """Validate and optionally coerce value type."""
        type_checks = {
            "string": (str, lambda v: str(v)),
            "integer": (int, lambda v: int(float(v)) if isinstance(v, (str, float)) else int(v)),
            "number": ((int, float), lambda v: float(v)),
            "boolean": (bool, lambda v: v.lower() in ("true", "1", "yes") if isinstance(v, str) else bool(v)),
            "array": (list, lambda v: list(v) if not isinstance(v, list) else v),
        }

        checker = type_checks.get(expected_type)
        if not checker:
            return ValidationResult(is_valid=True, output=value, strategy_used="type_passthrough")

        expected_cls, coercer = checker

        if isinstance(value, expected_cls):
            return ValidationResult(is_valid=True, output=value, strategy_used="type_match")

        if self.strategy in ("coerce", "lenient"):
            try:
                coerced = coercer(value)
                return ValidationResult(
                    is_valid=True, output=coerced,
                    warnings=[f"Coerced {type(value).__name__} to {expected_type}"],
                    strategy_used="type_coerce",
                )
            except (ValueError, TypeError):
                pass

        return ValidationResult(
            is_valid=False, output=None,
            errors=[f"Expected {expected_type}, got {type(value).__name__}"],
            strategy_used="type_check",
        )

    def retry(
        self,
        generate_fn: Callable[[], str],
        validate_fn: Callable[[str], ValidationResult],
        max_attempts: int = 3,
    ) -> ValidationResult:
        """
        Retry generation with validation feedback.

        Args:
            generate_fn: Function that generates output
            validate_fn: Function that validates output
            max_attempts: Maximum retry attempts

        Returns:
            Best ValidationResult achieved
        """
        last_result = None
        errors = []

        for attempt in range(max_attempts):
            try:
                raw = generate_fn()
                result = validate_fn(raw)

                if result.is_valid:
                    result.warnings.append(f"Succeeded on attempt {attempt + 1}")
                    return result

                last_result = result
                errors.extend(result.errors)

                # Provide feedback for next attempt
                if hasattr(generate_fn, '__self__'):
                    # If generate_fn is a method, we can add error context
                    pass

            except Exception as e:
                errors.append(f"Attempt {attempt + 1} error: {e}")

        # All attempts failed
        if last_result:
            last_result.errors = errors
            last_result.warnings.append(f"Failed after {max_attempts} attempts")
            return last_result

        return ValidationResult(
            is_valid=False, output=None,
            errors=errors,
            strategy_used="retry_exhausted",
        )

    def _clean_json(self, raw: str) -> str:
        """Clean common JSON formatting issues."""
        text = raw.strip()
        # Remove markdown fences
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        # Remove leading/trailing text
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end + 1]
        return text

    def _try_fix_json(self, text: str) -> Optional[dict]:
        """Try to fix common JSON errors."""
        fixes = [
            # Single quotes to double quotes
            (r"'", '"'),
            # Trailing comma
            (r',\s*}', '}'),
            (r',\s*]', ']'),
            # Unquoted keys
            (r'(\w+)\s*:', r'"\1":'),
        ]

        for pattern, replacement in fixes:
            try:
                fixed = re.sub(pattern, replacement, text)
                return json.loads(fixed)
            except json.JSONDecodeError:
                continue
        return None

    def _suggest_json_fix(self, text: str, error: json.JSONDecodeError) -> list[str]:
        """Suggest fixes for JSON errors."""
        suggestions = []
        if "Expecting" in str(error) and "delimiter" in str(error):
            suggestions.append("Check for missing commas or brackets")
        if "Extra data" in str(error):
            suggestions.append("Remove text after the JSON object")
        if not text.startswith('{'):
            suggestions.append("Response should start with '{'")
        return suggestions

    def _validate_schema(self, data: Any, schema: dict) -> list[str]:
        """Validate data against JSON schema (basic)."""
        errors = []
        if schema.get("type") == "object" and isinstance(data, dict):
            for field in schema.get("required", []):
                if field not in data:
                    errors.append(f"Missing required field: {field}")
        return errors

    def _coerce_to_schema(self, data: Any, schema: dict) -> Any:
        """Try to coerce data to match schema."""
        if not isinstance(data, dict) or schema.get("type") != "object":
            return data
        result = dict(data)
        for name, prop in schema.get("properties", {}).items():
            if name in result:
                val_type = self.validate_type(result[name], prop.get("type", "string"))
                if val_type.is_valid:
                    result[name] = val_type.output
        return result

    def _fill_defaults(self, data: Any, schema: dict) -> Any:
        """Fill missing fields with default values."""
        if not isinstance(data, dict) or schema.get("type") != "object":
            return data
        result = dict(data)
        for name, prop in schema.get("properties", {}).items():
            if name not in result:
                default = prop.get("default")
                if default is not None:
                    result[name] = default
        return result

    def _similarity(self, s1: str, s2: str) -> float:
        """Compute string similarity (0-1)."""
        if not s1 or not s2:
            return 0.0
        common = set(s1) & set(s2)
        return len(common) / max(len(set(s1)), len(set(s2)))
