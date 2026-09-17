#!/usr/bin/env python3
"""Validate the generated VINMERGE visual sidecar against its schemas."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, RefResolver

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(instance_path: Path, schema_path: Path) -> None:
    schema = load(schema_path)
    visual_path = SCHEMA_DIR / "vinmerge-visual-intelligence.schema.json"
    visual_schema = load(visual_path)

    # Register both the repository-local URI and the schema's public $id so
    # validation never depends on network access or the public host being live.
    store = {
        visual_path.as_uri(): visual_schema,
        visual_schema["$id"]: visual_schema,
    }
    resolver = RefResolver(schema_path.as_uri(), schema, store=store)
    validator = Draft202012Validator(schema, resolver=resolver, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(load(instance_path)), key=lambda e: list(e.path))
    if errors:
        for error in errors:
            print(f"{instance_path}: {'/'.join(map(str, error.path))}: {error.message}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_visual_layer.py <visual-index.json>")
    validate(Path(sys.argv[1]), SCHEMA_DIR / "vinmerge-visual-index.schema.json")
    print("visual layer schema validation passed")
