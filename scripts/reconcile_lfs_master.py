#!/usr/bin/env python3
import hashlib, json, pathlib, sys

CATALOG = pathlib.Path(sys.argv[1])
ENRICHMENT = pathlib.Path(sys.argv[2])
REPORT = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else pathlib.Path("/tmp/vinmerge-reconciliation-report.json")

def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def model_id(rec):
    if not isinstance(rec, dict):
        return None
    for key in ("model_id", "canonical_model_id", "vehicle_id"):
        if isinstance(rec.get(key), str) and rec[key].strip():
            return rec[key].strip()
    return None

def collect_model_records(obj, out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        if model_id(obj):
            out.append(obj)
        for value in obj.values():
            collect_model_records(value, out)
    elif isinstance(obj, list):
        for value in obj:
            collect_model_records(value, out)
    return out

catalog_obj = load(CATALOG)
enrichment_obj = load(ENRICHMENT)
catalog = collect_model_records(catalog_obj)
enrichment = collect_model_records(enrichment_obj)

catalog_ids = [model_id(r) for r in catalog]
enrichment_ids = [model_id(r) for r in enrichment]
catalog_set, enrichment_set = set(catalog_ids), set(enrichment_ids)

missing_catalog_ids = sorted(i for i in enrichment_set - catalog_set if i)
missing_enrichment_ids = sorted(i for i in catalog_set - enrichment_set if i)
duplicate_catalog_ids = sorted({i for i in catalog_ids if i and catalog_ids.count(i) > 1})
duplicate_enrichment_ids = sorted({i for i in enrichment_ids if i and enrichment_ids.count(i) > 1})

catalog_sha256 = hashlib.sha256(CATALOG.read_bytes()).hexdigest()

result = {
    "schema_version": "1.1",
    "catalog_sha256": catalog_sha256,
    "catalog_model_records_found": len(catalog),
    "enrichment_model_records_found": len(enrichment),
    "model_records_compared": len(catalog_set & enrichment_set),
    "catalog_duplicate_model_ids": duplicate_catalog_ids,
    "enrichment_duplicate_model_ids": duplicate_enrichment_ids,
    "enrichment_ids_missing_from_catalog": missing_catalog_ids,
    "catalog_ids_missing_from_enrichment": missing_enrichment_ids,
    "status": "PASS" if (
        len(catalog_set) == 825 and len(enrichment_set) == 825 and
        not duplicate_catalog_ids and not duplicate_enrichment_ids and
        not missing_catalog_ids and not missing_enrichment_ids
    ) else "FAIL"
}
REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
if result["status"] != "PASS":
    raise SystemExit(1)
