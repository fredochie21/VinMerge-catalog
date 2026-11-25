#!/usr/bin/env python3
"""Validate VinMerge part contracts and synthetic fixtures."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema"
FIXTURE_DIR = ROOT / "examples" / "parts"

PAIRS = [
    ("vinmerge-parts-product.schema.json", "synthetic-part-product.json"),
    ("vinmerge-part-number-reference.schema.json", "synthetic-part-number-reference.json"),
    ("vinmerge-part-fitment.schema.json", "synthetic-part-fitment.json"),
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema, instance):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(
        schema, format_checker=FormatChecker()
    ).validate(instance)


def normalize_part_number(value: str) -> str:
    """Contract rule: uppercase and remove separators, never strip letters."""
    return "".join(character for character in value.upper() if character.isalnum())


def must_reject(schema, instance, message: str):
    try:
        validate(schema, instance)
    except ValidationError:
        print(f"PASS: {message}")
        return
    raise SystemExit(f"FAIL: {message}")


def main():
    loaded = {}
    for schema_name, fixture_name in PAIRS:
        schema = load(SCHEMA_DIR / schema_name)
        fixture = load(FIXTURE_DIR / fixture_name)
        validate(schema, fixture)
        loaded[schema_name] = (schema, fixture)
        print(f"PASS: {schema_name} accepts {fixture_name}")

    # A verified identifier without evidence must fail.
    schema, fixture = loaded["vinmerge-part-number-reference.schema.json"]
    bad = copy.deepcopy(fixture)
    bad["status"] = "VERIFIED"
    must_reject(schema, bad, "verified part-number reference without evidence is rejected")

    # A verified fitment without evidence/reviewer/timestamp must fail.
    schema, fixture = loaded["vinmerge-part-fitment.schema.json"]
    bad = copy.deepcopy(fixture)
    bad["status"] = "VERIFIED"
    must_reject(schema, bad, "verified fitment without evidence/reviewer/timestamp is rejected")

    # Prefix preservation is a mandatory normalization contract.
    normalized = normalize_part_number("gdb-1234")
    if normalized != "GDB1234":
        raise SystemExit(f"FAIL: alphabetic prefix was not preserved: {normalized}")
    print("PASS: aftermarket alphabetic prefix is preserved during normalization")

    print("PASS: all part contract checks completed")


if __name__ == "__main__":
    main()
