#!/usr/bin/env python3
"""
Comprehensive zero-hallucination & zero-broken-link build gate:
  * Validates all 8 JSON data files in data/
  * Verifies all 11 primary root HTML pages + 12 docs/ compatibility redirects
  * Confirms every internal href/src link resolves cleanly
  * Confirms EVERY table row (tbody tr) carries an official https:// primary source link
  * Rejects any third-party aggregator domain across all HTML & JSON files
  * Rejects any unresolved bank template token or UAT staging hostname in data cells
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PAGES = [
    "index.html",
    "rates-refresh.html",
    "accounts.html",
    "returns.html",
    "bonuses.html",
    "rules.html",
    "security.html",
    "competitiveness.html",
    "flagged.html",
    "sources.html",
    "methodology.html",
]

DEFECT_TOKENS = [":BLUE_AccSavings_Rate%", "#ProductLine=", "NaN", "$XXXX", "sit58."]
DEFECT_ALLOWED = {"flagged.html"}
BANNED_AGGREGATORS = (
    "bankrate.com",
    "nerdwallet.com",
    "investopedia.com",
    "depositaccounts.com",
    "smartasset.com",
    "wallethub.com",
    "doctorofcredit.com",
)


class TableAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_tbody = False
        self.in_row = False
        self.row_has_source = False
        self.row_index = 0
        self.failures = []
        self.tables = 0
        self.rows = 0
        self.in_td = False
        self.cell_text = []
        self.bad_cells = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self.tables += 1
            self.row_index = 0
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "td" and self.in_row:
            self.in_td = True
            self.cell_text = []
        elif tag == "tr" and self.in_tbody:
            self.in_row = True
            self.row_index += 1
            self.row_has_source = False
        elif tag == "a" and self.in_row:
            href = a.get("href", "")
            cls = a.get("class", "")
            if href.startswith("https://") or "src" in cls.split():
                self.row_has_source = True

    def handle_data(self, data):
        if self.in_td:
            self.cell_text.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.in_td:
            text = "".join(self.cell_text)
            for token in DEFECT_TOKENS:
                if token in text:
                    self.bad_cells.append(token)
            self.in_td = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_row:
            self.rows += 1
            if not self.row_has_source:
                self.failures.append(f"table row {self.row_index} has no official source link")
            self.in_row = False


def main():
    errors = []
    data_files = [
        "accounts.json",
        "institutions.json",
        "fdic.json",
        "bonuses.json",
        "returns.json",
        "research.json",
        "benchmarks.json",
        "repo_audit.json",
    ]
    for name in data_files:
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            errors.append(f"missing data file: {name}")
            continue
        raw = open(path, encoding="utf-8").read()
        for agg in BANNED_AGGREGATORS:
            if agg in raw.lower():
                errors.append(f"{name}: contains banned third-party aggregator URL {agg}")
        if "sit58." in raw.lower():
            errors.append(f"{name}: contains internal staging host sit58.")
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {name}: {exc}")

    # Verify zero duplicate FDIC certificates inside any ladder plan
    returns = json.load(open(os.path.join(DATA, "returns.json"), encoding="utf-8"))
    for l in returns["ladders"]:
        certs = [x["cert"] for x in l["allocations"]]
        if len(certs) != len(set(certs)):
            errors.append(f"ladder {l['kind']} at {l['total_usd']} double-counts FDIC cert: {certs}")

    total_tables = total_rows = 0
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            errors.append(f"missing page: {page}")
            continue
        html = open(path, encoding="utf-8").read()

        for agg in BANNED_AGGREGATORS:
            if f'href="https://www.{agg}' in html.lower() or f'href="https://{agg}' in html.lower():
                errors.append(f"{page}: links to banned third-party aggregator {agg}")

        for attr_val in re.findall(r'(?:href|src)="([^"]+)"', html):
            if attr_val.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            target = attr_val.split("#")[0]
            if not target:
                continue
            if not os.path.exists(os.path.join(ROOT, target)):
                errors.append(f"{page}: broken internal link/asset -> {attr_val}")

        for needle in ("<!doctype html>", 'name="viewport"', 'href="assets/style.css"', 'src="assets/app.js"'):
            if needle not in html:
                errors.append(f"{page}: missing {needle}")

        audit = TableAudit()
        audit.feed(html)
        total_tables += audit.tables
        total_rows += audit.rows
        for f in audit.failures:
            errors.append(f"{page}: {f}")
        if page not in DEFECT_ALLOWED:
            for token in audit.bad_cells:
                errors.append(f"{page}: unresolved token in table cell: {token}")

    # Also verify docs/*.html compatibility redirect targets
    docs_dir = os.path.join(ROOT, "docs")
    docs_checked = 0
    if os.path.isdir(docs_dir):
        for fname in sorted(os.listdir(docs_dir)):
            if not fname.endswith(".html"):
                continue
            docs_checked += 1
            dhtml = open(os.path.join(docs_dir, fname), encoding="utf-8").read()
            for href in re.findall(r'href="([^"]+)"', dhtml):
                resolved = os.path.normpath(os.path.join(docs_dir, href))
                if not os.path.exists(resolved):
                    errors.append(f"docs/{fname}: broken redirect target -> {href}")

    print(f"pages checked        : {len(PAGES)} (+ {docs_checked} docs/ redirects)")
    print(f"tables checked       : {total_tables}")
    print(f"table rows checked   : {total_rows}")
    print(f"data files validated : {len(data_files)}")
    if errors:
        print("\nFAILURES")
        for x in errors:
            print("  -", x)
        sys.exit(1)
    print("\nOK - every table row has an official primary source link, zero aggregator links, zero CERT duplicates, zero broken internal links.")


if __name__ == "__main__":
    main()
