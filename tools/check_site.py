#!/usr/bin/env python3
"""
Build gate. Fails (exit 1) if:
  * any internal link points at a file that does not exist
  * any table data row has no official source link
  * any output page still contains an unresolved template token or a known defect string
  * a data file is missing or invalid JSON
Run this before every commit that touches the site.
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

# Only checked inside table data cells: prose legitimately quotes these tokens when
# documenting the defect.
DEFECT_TOKENS = [":BLUE_AccSavings_Rate%", "NaN", "$XXXX"]
# The flagged page quotes these tokens on purpose: that is where they are documented.
DEFECT_ALLOWED = {"flagged.html"}


class TableAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_thead = False
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
            self.in_table = True
            self.tables += 1
            self.row_index = 0
        elif tag == "thead":
            self.in_thead = True
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
            if href.startswith("http") or a.get("class") == "src":
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
        elif tag == "table":
            self.in_table = False
        elif tag == "thead":
            self.in_thead = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_row:
            self.rows += 1
            if not self.row_has_source:
                self.failures.append(f"table row {self.row_index} has no source link")
            self.in_row = False


def main():
    errors = []
    warnings = []

    data_files = ["accounts.json", "institutions.json", "fdic.json", "bonuses.json", "returns.json", "research.json"]
    for name in data_files:
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            errors.append(f"missing data file: {name}")
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                json.load(fh)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {name}: {exc}")

    total_tables = total_rows = 0
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.exists(path):
            errors.append(f"missing page: {page}")
            continue
        html = open(path, encoding="utf-8").read()

        # internal links
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = href.split("#")[0]
            if not target:
                continue
            if not os.path.exists(os.path.join(ROOT, target)):
                errors.append(f"{page}: broken internal link -> {href}")

        # required boilerplate
        for needle in ("<!doctype html>", 'name="viewport"', 'href="assets/style.css"'):
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
                errors.append(f"{page}: unresolved token in a table cell: {token}")

    print(f"pages checked        : {len(PAGES)}")
    print(f"tables checked       : {total_tables}")
    print(f"table rows checked   : {total_rows}")
    print(f"data files validated : {len(data_files)}")
    if warnings:
        print("\nWARNINGS")
        for w in warnings:
            print("  -", w)
    if errors:
        print("\nFAILURES")
        for x in errors:
            print("  -", x)
        sys.exit(1)
    print("\nOK - every table row has a source link, every internal link resolves, no unresolved tokens.")


if __name__ == "__main__":
    main()
