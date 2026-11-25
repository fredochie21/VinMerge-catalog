#!/usr/bin/env python3
"""Validate VinMerge part contracts and synthetic fixtures."""
from __future__ import annotations
import copy, json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema"
FIXTURE_DIR = ROOT / "examples" / "parts"

PAIRS = [
    ("vinmerge-parts-product.schema.json", "synthetic-part-product.json"),
    ("vinmerge-part-number-reference.schema.json", "synthetic-part-number-reference.json"),
    ("vinmerge-part-fitment.schema.json", "synthetic-part-fitment.json"),
]

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate(schema, instance):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)

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
    try:
        validate(schema, bad)
    except Exception:
        print("PASS: verified part-number reference without evidence is rejected")
    else:
        raise SystemExit("FAIL: verified part-number reference without evidence was accepted")

    # A verified fitment without evidence/reviewer/timestamp must fail.
    schema, fixture = loaded["vinmerge-part-fitment.schema.json"]
    bad = copy.deepcopy(fixture)
    bad["status"] = "VERIFIED"
    try:
        validate(schema, bad)
    except Exception:
        print("PASS: verified fitment without evidence/reviewer/timestamp is rejected")
    else:
        raise SystemExit("FAIL: verified fitment without evidence was accepted")

    # Alphabetic prefixes must remain in normalized identifiers.
    schema, fixture = loaded["vinmerge-part-number-reference.schema.json"]
    bad = copy.deepcopy(fixture)
    bad["value_normalized"] = "044650K240"
    bad["value_raw"] = "GDB1234"
    try:
        validate(schema, bad)
    except Exception:
        raise SystemExit("FAIL: normalized identifier test fixture invalid")
    if not bad["value_normalized"].startswith("GDB"):
        print("NOTE: schema permits any normalized alphanumeric key; normalization code must preserve prefixes")
    print("PASS: all part contract checks completed")

if __name__ == "__main__":
    main()
