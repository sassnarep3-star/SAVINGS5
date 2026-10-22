# SAVINGS5 — savings account research

A verified comparison of savings accounts at the largest US banks, published as a static dashboard on GitHub Pages.

**Live site:** https://sassnarep3-star.github.io/SAVINGS5/

**Research date:** 2026-10-22 (this is also the account open date used in every projection).

## What it answers

- Which large national banks pay the most on savings, right now, and how each rate compares with the FDIC national average and Treasury yields.
- What each account requires to open: minimum deposit, fees, fee waivers, withdrawal limits, age and ID rules.
- What a deposit actually earns at $10k, $25k, $50k, $100k, $250k, $500k, $1M and $2.5M over 1, 2, 3 and 5 years.
- How far $250,000 of FDIC coverage stretches, and how to ladder larger balances so every dollar stays insured.
- Which promotional bonuses exist, what they require, and when they expire.
- Every value that could **not** be confirmed from an official source — left blank and listed on the Flagged for review page.

## Non-negotiable rules used here

1. **Every table row links to an official source.** Enforced automatically by `tools/check_site.py`, which fails the build otherwise.
2. **No value is inferred.** If a bank does not publish a readable APY (ZIP gate, empty table, template placeholder), the cell is blank and the reason is on the flagged page.
3. **No bonuses folded into APY.** Bonuses are one-off; adding them to a rate would misstate the ongoing yield.
4. **No security ranking.** FDIC status and the existence of an app are verified; security controls are not audited.

## Repository layout

```
index.html … methodology.html   generated pages (do not edit by hand)
assets/style.css                shared stylesheet
data/accounts.json              17 accounts, field-level values + sources
data/institutions.json          FDIC BankFind records, 16 institutions + Discover note
data/fdic.json                  coverage rules, national rates, Treasury yields
data/bonuses.json               documented promotions + "no bonus found" log
data/returns.json               generated projections, leaderboards, ladder plans
tools/build_returns.py          builds data/returns.json from the data files
tools/build_site.py             renders all HTML from data/
tools/check_site.py             build gate: sources, links, tokens
research/verification-log.md    what was fetched, when, and what it showed
COORDINATION.md                 multi-session task board
```

## Rebuilding

```bash
python3 tools/build_returns.py
python3 tools/build_site.py
python3 tools/check_site.py
```

The checker must print `OK` before publishing. It verifies that every internal link resolves and that every table data row
contains an official source link.

## Data provenance

- Institution data: FDIC BankFind Suite institutions API (`https://api.fdic.gov/banks/institutions`), index
  `institutions_20261016090006`, retrieved 2026-10-22.
- Coverage rules: FDIC.gov, *Are My Deposit Accounts Insured by the FDIC?* and *Understanding Deposit Insurance*.
- Rate benchmarks: FDIC, *National Rates and Rate Caps — October 2026* (as of 2026-10-19).
- Bank rates, fees and rules: each bank's own product, rate or fee-schedule page. Full list on the site's Sources page.

## Licence and disclaimer

Research, not financial advice. Rates are variable and change without notice; the bank's live page is authoritative.
