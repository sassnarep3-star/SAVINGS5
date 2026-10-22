#!/usr/bin/env python3
"""Validate the source registry and reproducible projection outputs."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESEARCH = ROOT / "research"
ALLOWED_DOMAIN_SUFFIXES = (
    "fdic.gov", "sofi.com", "synchrony.com", "marcus.com", "ally.com",
    "americanexpress.com", "capitalone.com", "barclays.com", "barclays", "cit.com",
    "usbank.com", "td.com", "chase.com", "bankofamerica.com", "citi.com",
    "wellsfargo.com", "pnc.com",
)

with (DATA / "research.json").open(encoding="utf-8") as f:
    research = json.load(f)

sources = research["sources"]
source_ids = [s["id"] for s in sources]
assert len(source_ids) == len(set(source_ids)), "duplicate source ID"
source_by_id = {s["id"]: s for s in sources}
for source in sources:
    parsed = urlparse(source["url"])
    assert parsed.scheme == "https", f"non-HTTPS source: {source['id']}"
    host = (parsed.hostname or "").lower()
    assert any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAIN_SUFFIXES), (
        f"source is not on an expected official institution/regulator domain: {source['id']} {host}"
    )
    assert source.get("checkedOn") == research["meta"]["snapshotDate"], (
        f"source check date mismatch: {source['id']}"
    )

for section in ("accounts", "offers", "flags"):
    seen = set()
    for item in research[section]:
        assert item["id"] not in seen, f"duplicate {section} ID {item['id']}"
        seen.add(item["id"])
        ids = item.get("sourceIds", [])
        assert ids, f"no source link on {section} row {item['id']}"
        assert all(i in source_by_id for i in ids), f"bad source reference on {section} row {item['id']}"
        assert all(source_by_id[i]["url"].startswith("https://") for i in ids)

# Numeric APY must have an explicit date and a provenance link.
for account in research["accounts"]:
    for rate in account.get("standardRates", []):
        assert isinstance(rate.get("apyPercent"), (int, float)), f"non-numeric APY in {account['id']}"
        assert rate.get("asOf"), f"APY without source date in {account['id']}"
    if account["status"] in {"numeric-apy-unverified", "nyc-rate-unverified", "availability-and-rate-unverified"}:
        if account["id"] != "usbank":
            assert account["projection"]["eligible"] is False, f"unverified account projected: {account['id']}"

for filename, expected in (("standard-projections.csv", 120), ("promotion-projections.csv", 84)):
    with (DATA / filename).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == expected, f"unexpected number of rows in {filename}: {len(rows)}"
    for number, row in enumerate(rows, start=2):
        ids = [i for i in row.get("source_ids", "").split(";") if i]
        urls = [u for u in row.get("official_source_urls", "").split(";") if u]
        assert ids and urls, f"projection row without official source at {filename}:{number}"
        assert len(ids) == len(urls), f"source ID/URL count mismatch at {filename}:{number}"
        assert all(i in source_by_id for i in ids), f"unknown projection source at {filename}:{number}"
        assert all(urls[j] == source_by_id[ids[j]]["url"] for j in range(len(ids))), (
            f"projection URL/source mismatch at {filename}:{number}"
        )

# CSV source matrix must mirror the current official source registry.
with (RESEARCH / "source-matrix.csv").open(newline="", encoding="utf-8") as f:
    matrix = list(csv.DictReader(f))
assert len(matrix) == len(sources), f"source matrix has {len(matrix)} rows, registry has {len(sources)}"
assert {r["source_id"] for r in matrix} == set(source_ids), "source matrix IDs do not match registry"
assert all(r["official_url"].startswith("https://") for r in matrix)

print(f"Research validation passed: {len(sources)} official sources, {len(research['accounts'])} accounts, "
      f"{len(research['offers'])} offers, {len(research['flags'])} review flags, "
      f"120 rate projections, 84 offer projections.")
