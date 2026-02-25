"""Strict JSON parser for GitHub Issue submission bodies.

Validates schema, types, and field lengths. No LLM, no string interpolation,
no shell command construction from user input. Deterministic and safe.
"""
from __future__ import annotations

import json
import sys
from typing import Any

MAX_NAME_LEN = 200
MAX_EQUATION_LEN = 2000
MAX_DESCRIPTION_LEN = 4000
MAX_SOURCE_LEN = 100
MAX_SUBMITTER_LEN = 100
MAX_ASSUMPTION_LEN = 500
MAX_EVIDENCE_LEN = 500
MAX_ARRAY_ITEMS = 20

REQUIRED_KEYS = {"name", "equation", "description"}
OPTIONAL_KEYS = {"source", "submitter", "units", "theory", "assumptions", "evidence"}
ALL_KEYS = REQUIRED_KEYS | OPTIONAL_KEYS

VALID_UNITS = {"OK", "TBD", "WARN"}
VALID_THEORY = {"PASS", "PASS-WITH-ASSUMPTIONS", "TBD", "FAIL"}


class ValidationError(Exception):
    pass


def _check_str(val: Any, field: str, max_len: int) -> str:
    if not isinstance(val, str):
        raise ValidationError(f"{field}: expected string, got {type(val).__name__}")
    if len(val) > max_len:
        raise ValidationError(f"{field}: exceeds max length {max_len} (got {len(val)})")
    return val.strip()


def _check_str_list(val: Any, field: str, max_item_len: int, max_items: int) -> list[str]:
    if not isinstance(val, list):
        raise ValidationError(f"{field}: expected array, got {type(val).__name__}")
    if len(val) > max_items:
        raise ValidationError(f"{field}: exceeds max items {max_items} (got {len(val)})")
    result = []
    for i, item in enumerate(val):
        if not isinstance(item, str):
            raise ValidationError(f"{field}[{i}]: expected string, got {type(item).__name__}")
        if len(item) > max_item_len:
            raise ValidationError(f"{field}[{i}]: exceeds max length {max_item_len}")
        result.append(item.strip())
    return result


def parse_submission(raw_text: str) -> dict:
    """Parse and validate a submission JSON from an issue body.

    Returns a clean dict with validated fields.
    Raises ValidationError on any problem.
    """
    # Strip markdown code fences if present
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines).strip()

    if not text:
        raise ValidationError("empty submission body")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValidationError(f"invalid JSON: {e}")

    if not isinstance(data, dict):
        raise ValidationError(f"expected JSON object, got {type(data).__name__}")

    # Reject unknown keys
    unknown = set(data.keys()) - ALL_KEYS
    if unknown:
        raise ValidationError(f"unknown keys: {', '.join(sorted(unknown))}")

    # Check required keys
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValidationError(f"missing required keys: {', '.join(sorted(missing))}")

    result: dict[str, Any] = {}

    result["name"] = _check_str(data["name"], "name", MAX_NAME_LEN)
    result["equation"] = _check_str(data["equation"], "equation", MAX_EQUATION_LEN)
    result["description"] = _check_str(data["description"], "description", MAX_DESCRIPTION_LEN)

    if not result["name"]:
        raise ValidationError("name: cannot be empty")
    if not result["equation"]:
        raise ValidationError("equation: cannot be empty")
    if not result["description"]:
        raise ValidationError("description: cannot be empty")

    result["source"] = _check_str(data.get("source", "github-issue"), "source", MAX_SOURCE_LEN)
    result["submitter"] = _check_str(data.get("submitter", "anonymous"), "submitter", MAX_SUBMITTER_LEN)

    units = _check_str(data.get("units", "TBD"), "units", 20)
    if units not in VALID_UNITS:
        raise ValidationError(f"units: must be one of {VALID_UNITS}, got '{units}'")
    result["units"] = units

    theory = _check_str(data.get("theory", "TBD"), "theory", 30)
    if theory not in VALID_THEORY:
        raise ValidationError(f"theory: must be one of {VALID_THEORY}, got '{theory}'")
    result["theory"] = theory

    if "assumptions" in data:
        result["assumptions"] = _check_str_list(data["assumptions"], "assumptions", MAX_ASSUMPTION_LEN, MAX_ARRAY_ITEMS)
    else:
        result["assumptions"] = []

    if "evidence" in data:
        result["evidence"] = _check_str_list(data["evidence"], "evidence", MAX_EVIDENCE_LEN, MAX_ARRAY_ITEMS)
    else:
        result["evidence"] = []

    return result


def main() -> None:
    """Read JSON from stdin or first argument, validate, print cleaned result."""
    if len(sys.argv) > 1:
        text = open(sys.argv[1], encoding="utf-8").read()
    else:
        text = sys.stdin.read()

    try:
        result = parse_submission(text)
    except ValidationError as e:
        print(f"VALIDATION_ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
