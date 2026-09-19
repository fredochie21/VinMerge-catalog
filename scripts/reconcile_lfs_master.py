#!/usr/bin/env python3
import hashlib, json, pathlib, sys

CATALOG = pathlib.Path(sys.argv[1])
ENRICHMENT = pathlib.Path(sys.argv[2])
REPORT = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else pathlib.Path("/tmp/vinmerge-reconciliation-report.json")

def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def records(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for key in ("models", "catalog", "vehicles", "records", "data", "slices"):
            value = obj.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("Could not locate record list")

def model_id(rec):
    if not isinstance(rec, dict):
        return None
    for key in ("model_id", "id", "vehicle_id", "canonical_model_id"):
        if isinstance(rec.get(key), str) and rec[key].strip():
            return rec[key].strip()
    return None

catalog_obj = load(CATALOG)
enrichment_obj = load(ENRICHMENT)
catalog = records(catalog_obj)
enrichment = records(enrichment_obj)

catalog_ids = [model_id(r) for r in catalog]
enrichment_ids = [model_id(r) for r in enrichment]

missing_catalog_ids = [i for i in enrichment_ids if i and i not in set(catalog_ids)]
missing_enrichment_ids = [i for i in catalog_ids if i and i not in set(enrichment_ids)]
duplicate_catalog_ids = sorted({i for i in catalog_ids if i and catalog_ids.count(i) > 1})
duplicate_enrichment_ids = sorted({i for i in enrichment_ids if i and enrichment_ids.count(i) > 1})
unnamed_catalog = sum(i is None for i in catalog_ids)
unnamed_enrichment = sum(i is None for i in enrichment_ids)

catalog_sha256 = hashlib.sha256(CATALOG.read_bytes()).hexdigest()

result = {
    "schema_version": "1.0",
    "catalog_file": str(CATALOG),
    "catalog_sha256": catalog_sha256,
    "catalog_records": len(catalog),
    "enrichment_records": len(enrichment),
    "model_records_compared": min(len(catalog), len(enrichment)),
    "catalog_duplicate_model_ids": duplicate_catalog_ids,
    "enrichment_duplicate_model_ids": duplicate_enrichment_ids,
    "catalog_records_without_model_id": unnamed_catalog,
    "enrichment_records_without_model_id": unnamed_enrichment,
    "enrichment_ids_missing_from_catalog": missing_catalog_ids,
    "catalog_ids_missing_from_enrichment": missing_enrichment_ids,
    "status": "PASS" if (
        len(catalog) == 825 and len(enrichment) == 825 and
        not duplicate_catalog_ids and not duplicate_enrichment_ids and
        unnamed_catalog == 0 and unnamed_enrichment == 0 and
        not missing_catalog_ids and not missing_enrichment_ids
    ) else "FAIL"
}
REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
