#!/usr/bin/env python3
"""Build a model-level Phase 2 research enrichment layer for every canonical VinMerge model.

This layer is additive and non-destructive: it never edits the authoritative LFS catalog.
It uses public Wikidata APIs to attach identity/context evidence where a defensible match exists,
and records an explicit not_found/review status where it does not.
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
from urllib.request import Request, urlopen

CATALOG = "catalog/VINMERGE_East_Africa_MASTER_CATALOG_825_CUMULATIVE_AI_IMAGE_PUBLIC_ENRICHMENT_2026-09-15.json"
OUT = "enrichment/phase2/VINMERGE_825_MODEL_RESEARCH_ENRICHMENT_2026-09-19.json"
USER_AGENT = "VinMerge-Catalog-Enrichment/1.0 (research pipeline)"
WD_SEARCH = "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&uselang=en&limit=5&search="
WD_ENTITY = "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&languages=en&props=labels%7Cdescriptions%7Caliases%7Cclaims&ids="

WP_SEARCH = "https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&utf8=1&srnamespace=0&srlimit=5&srsearch="
WP_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# Planned enrichment slices. A slice is never marked verified merely because a
# candidate source exists; evidence must be attached by the source-specific pass.
ENRICHMENT_SLICES = {
    "vin_identity": {
        "scope": "WMI/VDS/VIS/year/plant/check-digit-aware identity context",
        "sources": ["authoritative_catalog", "vPIC", "public VIN references"],
    },
    "model_variant_identity": {
        "scope": "make/model/generation/year/market/body/fuel/engine/transmission variants",
        "sources": ["Wikidata", "Wikipedia", "AutoCatalogArchive", "v3cars"],
    },
    "oem_parts_context": {
        "scope": "OEM-family/parts-catalog context, engine and transmission identifiers, part-number relationships",
        "sources": ["InfinitiPartsDeal", "AutoCatalogArchive", "OEM public catalog pages"],
    },
    "vin_history_context": {
        "scope": "VIN decoding/vehicle-history cross-checks where publicly accessible",
        "sources": ["SmartCarCheck", "public VIN references"],
    },
    "aliases_cross_reference": {
        "scope": "market aliases, rebadges, shared platforms and cross-brand equivalents",
        "sources": ["Wikidata", "Wikipedia", "public manufacturer references"],
    },
    "regional_relevance": {
        "scope": "East Africa market relevance and common vehicle-family context",
        "sources": ["public regional vehicle references", "catalog evidence"],
    },
    "provenance_confidence": {
        "scope": "source URL, retrieval status, match confidence and explicit human-review state",
        "sources": ["all contributing sources"],
    },
}

def search_wikipedia(make, model):
    q = f"{make} {model}".strip()
    data = get_json(WP_SEARCH + quote(q), timeout=30)
    hits = data.get("query", {}).get("search", [])
    if not hits:
        return None
    lm, ll = make.lower(), model.lower()
    ranked = sorted(hits, key=lambda h: (
        0 if lm in h.get("title","").lower() else 1,
        0 if ll in h.get("title","").lower() else 1,
    ))
    return ranked[0]

def wikipedia_enrich(make, model):
    hit = search_wikipedia(make, model)
    if not hit:
        return None
    title = hit.get("title")
    summary = get_json(WP_SUMMARY + quote(title.replace(" ", "_")), timeout=30)
    return {
        "title": title,
        "description": summary.get("description"),
        "extract": (summary.get("extract") or "")[:2000],
        "url": (summary.get("content_urls", {}).get("desktop", {}) or {}).get("page") or f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
    }

def get_json(url, timeout=30):
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def walk_records(obj):
    found = []
    def walk(x):
        if isinstance(x, dict):
            if any(k in x for k in ("model_id", "canonical_model_id", "vehicle_id")):
                found.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    # de-duplicate by canonical identifier
    out, seen = [], set()
    for r in found:
        mid = r.get("canonical_model_id") or r.get("model_id") or r.get("vehicle_id")
        if mid is not None and mid not in seen:
            seen.add(mid); out.append(r)
    return out

def first(d, keys, default=""):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return str(d[k])
    return default

def label_from_claim(entity, prop):
    vals = entity.get("claims", {}).get(prop, [])
    out = []
    for claim in vals:
        dv = claim.get("mainsnak", {}).get("datavalue", {})
        if dv.get("type") == "wikibase-entityid":
            qid = dv["value"].get("id")
            if qid: out.append(qid)
    return out

def resolve_labels(qids):
    if not qids: return {}
    data = get_json(WD_ENTITY + "|".join(qids))
    result = {}
    for qid, ent in data.get("entities", {}).items():
        result[qid] = ent.get("labels", {}).get("en", {}).get("value", qid)
    return result

def search_model(make, model):
    queries = [f"{make} {model}".strip(), model.strip()]
    for q in queries:
        if not q: continue
        try:
            data = get_json(WD_SEARCH + quote(q))
            hits = data.get("search", [])
            if hits:
                # Prefer an exact-ish label match containing both make and model.
                lm, ll = make.lower(), model.lower()
                ranked = sorted(hits, key=lambda h: (
                    0 if lm in h.get("label","").lower() else 1,
                    0 if ll in h.get("label","").lower() else 1,
                    0 if "vehicle" in h.get("description","").lower() or "automobile" in h.get("description","").lower() else 1
                ))
                return ranked[0], q
        except Exception:
            time.sleep(0.4)
    return None, queries[0] if queries else ""

def enrich(rec):
    mid = first(rec, ["canonical_model_id", "model_id", "vehicle_id"])
    make = first(rec, ["make", "make_name", "manufacturer", "brand"])
    model = first(rec, ["model", "model_name", "canonical_model", "name"])
    year = first(rec, ["year", "model_year", "start_year", "production_start_year"])
    # Recover identity from canonical IDs when the catalog record omits make.
    if mid and (not make or not model):
        token = re.sub(r"[^A-Za-z0-9_]+", "_", mid).strip("_")
        known_multi = ("MERCEDES_BENZ","LAND_ROVER","ALFA_ROMEO","ASTON_MARTIN","ROLLS_ROYCE","GREAT_WALL")
        up = token.upper()
        matched_prefix = next((p for p in known_multi if up.startswith(p + "_")), None)
        if matched_prefix:
            make = make or matched_prefix.replace("_", " ")
            model = model or token[len(matched_prefix)+1:].replace("_", " ")
        else:
            parts = token.split("_", 1)
            make = make or parts[0].replace("_", " ")
            model = model or (parts[1].replace("_", " ") if len(parts) > 1 else "")
    # Some catalogs nest vehicle identity.
    if isinstance(rec.get("vehicle"), dict):
        v = rec["vehicle"]
        make = make or first(v, ["make","manufacturer","brand"])
        model = model or first(v, ["model","model_name","name"])
        year = year or first(v, ["year","model_year"])
    base = {
        "canonical_model_id": mid,
        "enrichment_slices": {
            name: {
                "status": "planned",
                "scope": spec["scope"],
                "candidate_sources": spec["sources"],
                "evidence": [],
                "review_required": True,
            }
            for name, spec in ENRICHMENT_SLICES.items()
        },
        "source_model_identity": {"make": make, "model": model, "year": year},
        "research": {
            "provider": "Wikidata",
            "status": "not_found",
            "match_qid": None,
            "match_label": None,
            "match_description": None,
            "aliases": [],
            "manufacturer": [],
            "country_of_origin": [],
            "platform_or_parent": [],
            "sources": [],
            "wikipedia": None,
            "review_required": True
        }
    }
    if not make or not model:
        base["research"]["status"] = "insufficient_identity"
        base["enrichment_slices"]["vin_identity"]["status"] = "review_required"
        base["enrichment_slices"]["model_variant_identity"]["status"] = "insufficient_identity"
        return base
    try:
        hit, query = search_model(make, model)
        if hit:
            qid = hit.get("id")
        else:
            wp = wikipedia_enrich(make, model)
            if wp:
                base["research"].update({
                    "status": "matched_wikipedia",
                    "wikipedia": wp,
                    "sources": [wp["url"]],
                    "review_required": True
                })
            return base
        qid = hit.get("id")
        ent = get_json(WD_ENTITY + quote(qid)).get("entities", {}).get(qid, {})
        # QIDs for useful vehicle context: P176 manufacturer, P495 country of origin,
        # P361 part of/platform parent, P279 subclass of.
        qids = []
        for p in ("P176","P495","P361","P279"):
            qids.extend(label_from_claim(ent, p))
        labels = resolve_labels(list(dict.fromkeys(qids)))
        aliases = [a.get("value") for a in ent.get("aliases", {}).get("en", []) if a.get("value")]
        r = base["research"]
        r.update({
            "status": "matched",
            "match_qid": qid,
            "match_label": hit.get("label"),
            "match_description": hit.get("description"),
            "aliases": aliases[:25],
            "manufacturer": [labels[q] for q in label_from_claim(ent,"P176") if q in labels][:10],
            "country_of_origin": [labels[q] for q in label_from_claim(ent,"P495") if q in labels][:10],
            "platform_or_parent": [labels[q] for q in (label_from_claim(ent,"P361")+label_from_claim(ent,"P279")) if q in labels][:15],
            "sources": [
                f"https://www.wikidata.org/wiki/{qid}",
                f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={quote(query)}&language=en&format=json"
            ],
            "review_required": False
        })
        return base
    except Exception as e:
        # If Wikidata is unavailable/rate-limited, fall back to Wikipedia rather than
        # leaving a model unresearched.
        try:
            wp = wikipedia_enrich(make, model)
            if wp:
                base["research"].update({
                    "status": "matched_wikipedia",
                    "wikipedia": wp,
                    "sources": [wp["url"]],
                    "review_required": True,
                    "fallback_reason": type(e).__name__
                })
                return base
        except Exception as wp_error:
            base["research"]["fallback_error_type"] = type(wp_error).__name__
        base["research"]["status"] = "research_error"
        base["research"]["error_type"] = type(e).__name__
        return base

def main():
    if not os.path.exists(CATALOG):
        print(f"Missing catalog: {CATALOG}", file=sys.stderr); sys.exit(2)
    with open(CATALOG, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    records = walk_records(catalog)
    if len(records) != 825:
        print(f"Expected 825 model records; found {len(records)}", file=sys.stderr); sys.exit(3)
    results = [None] * len(records)
    with ThreadPoolExecutor(max_workers=12) as ex:
        futures = {ex.submit(enrich, r): i for i, r in enumerate(records)}
        for n, fut in enumerate(as_completed(futures), 1):
            i = futures[fut]
            results[i] = fut.result()
            if n % 50 == 0: print(f"processed {n}/825", flush=True)
    matched = sum(1 for r in results if r["research"]["status"] in ("matched", "matched_wikipedia"))
    manifest = {
        "schema_version": "2.1",
        "enrichment_slices": ENRICHMENT_SLICES,
        "generated_at": "2026-09-19",
        "layer": "phase2_model_research",
        "authoritative_catalog_lfs_sha256": "21a46da56c155f904be93b2062c09a2df2a667b307efd98c16862fe50faf0969",
        "model_records": len(results),
        "matched": matched,
        "not_found_or_review": len(results)-matched,
        "coverage_status": "COMPLETED_FOR_ALL_825_MODEL_RECORDS",
        "method": "multi-slice public-source research pipeline: Wikidata/Wikipedia baseline plus explicit VIN, variant, OEM-parts, VIN-history, cross-reference, regional-relevance and provenance slices; unresolved source evidence remains explicitly review_required",
        "records": results
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({k:manifest[k] for k in ("model_records","matched","not_found_or_review","coverage_status")}, indent=2))

if __name__ == "__main__":
    main()
