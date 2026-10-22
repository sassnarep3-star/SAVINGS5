# COORDINATION — Shared Multi-Session Task Board & Audit Ledger

**Repo:** `sassnarep3-star/SAVINGS5`
**Last updated:** 2026-10-22 (UTC)
**Account Opening / Benchmark Anchor Date:** `2026-10-22`
**Active Integration Session:** `5f0ee759` (branch `arena/5f0ee759-savings5`, reconciling and auditing completed session `a67a75fe`)
**Prior Completed Session:** `a67a75fe` (branch `arena/a67a75fe-savings5`, merged PRs #1–#5 / #6)
**Live site:** https://sassnarep3-star.github.io/SAVINGS5/

---

## Coordination rules in force

1. Read this file before starting any task.
2. Claim a task by adding your session ID + file scope, then commit and push the claim **immediately**.
3. Never start a task another live session has claimed. A claim older than 60 minutes with no commits may be taken over — note the handoff.
4. Keep scopes non-overlapping. If you need to change a file owned by another session, log a request here instead of editing it.
5. Small, frequent commits. `git pull --rebase` / `git fetch --all` before every push. Never drop another session's work to resolve a conflict.
6. Never mark anything "verified" without an official source link and the date it was checked (`2026-10-22` retrieval; exact source effective date recorded). Leave unconfirmed values blank (`null` / `not stated`) and flag them on `flagged.html` with source links.
7. Shared outputs (`data/*.json`, `index.html`, nav, site pages) are changed only by a final integration session once all other tasks are done. That session merges the branches without discarding prior work, re-verifies the combined data line by line against official sources, confirms zero broken links, and publishes to GitHub Pages.

---

## Unified Task Board (Sessions `a67a75fe` + `5f0ee759`)

### Session `a67a75fe` Completed Baseline Tasks (`T1–T10`, preserved intact from `origin/main`)

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|------------|
| T1 | Coordination board + repo scaffold | done | a67a75fe | `COORDINATION.md`, `README.md`, `.nojekyll` |
| T2 | Verify FDIC insurance framework (limits, ownership categories, covered products) | done | a67a75fe | `data/fdic.json` |
| T3 | Verify bank universe from FDIC BankFind (16 institutions, certificates, assets, charter class) | done | a67a75fe | `data/institutions.json`, `research/verification-log.md` |
| T4 | Verify APY, minimums, fees, waivers and opening rules, official bank pages | done | a67a75fe | `data/accounts.json` |
| T5 | Verify bonuses/promotions and log banks with none published | done | a67a75fe | `data/bonuses.json` |
| T6 | Return model (8 deposit sizes x 4 terms), FDIC ladder plans, coverage arithmetic | done | a67a75fe | `data/returns.json`, `tools/build_returns.py` |
| T7 | Site build: landing page + 9 category subpages | done | a67a75fe | `index.html`, `accounts.html`, `returns.html`, `bonuses.html`, `rules.html`, `security.html`, `competitiveness.html`, `flagged.html`, `sources.html`, `methodology.html`, `assets/style.css`, `tools/build_site.py` |
| T8 | Build gate: sources on every table row, internal links, unresolved tokens | done | a67a75fe | `tools/check_site.py` |
| T9 | Publish to GitHub Pages | done | a67a75fe | repo root (Pages source: `main` / root, legacy build) |
| T10 | PR to `main`, merge, deploy verification | done | a67a75fe | `COORDINATION.md` (PRs #1–#5 merged) |

### Session `5f0ee759` Research, Line-by-Line Repo Audit & Final Integration Tasks (`TASK-01–TASK-07`)

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|------------|
| TASK-01 | Macro & Regulatory Benchmark Verification (`FDIC`, `Federal Reserve FOMC`, `U.S. Treasury`) | done | 5f0ee759 | `data/benchmarks.json`, `data/repo_audit.json`, `data/fdic.json` |
| TASK-02 | National Institution Screening, Active-Charter Ranking Audit & Mobile App Store Verification (18 Active Top-56 Banks + Merged Discover `#5649`) | done | 5f0ee759 | `data/institutions.json`, `research/verification-log.md` |
| TASK-03 | Direct National HYSA Verification & Expansion (`Barclays Select 4.25%` + `Tiered 3.50%/3.65%`, `Alto by BMO 3.00%`, `SoFi Plus 4.70%`, `Synchrony`, `Marcus`, `Capital One`, `Amex`, `Ally`) | done | 5f0ee759 | `data/accounts.json`, `data/bonuses.json` |
| TASK-04 | Branch Megabank Primary PDF & Promo Verification (`Chase NY PDF rdny1.pdf`, `Citi Fact_Sheet.pdf 3.75% final day`, `TD $200 bonus + Simple 0.02%`, `BofA`, `Wells Fargo`, `U.S. Bank`, `PNC`, `Truist`, `Fifth Third`, `Schwab`) | done | 5f0ee759 | `data/accounts.json`, `data/bonuses.json` |
| TASK-05 | Merge Conflict Resolution & Line-by-Line Verification Audit of `origin/main` | done | 5f0ee759 | `COORDINATION.md` (zero work discarded; all remaining defects & omissions remediated) |
| TASK-06 | Final Integration Build: Multi-Charter `CERT`-Safe Return Engine + Interactive Filtering, Custom Deposit/Lifespan Calculator, FDIC Coverage Planner & Modern Executive UI | in_progress | 5f0ee759 | `tools/build_returns.py`, `tools/build_site.py`, `tools/check_site.py`, `assets/style.css`, `assets/app.js`, `*.html`, `README.md` |
| TASK-07 | Build Gate, Zero-Broken-Link Verification, PR to `main`, Merge & GitHub Pages Deployment Verification | pending | 5f0ee759 | `COORDINATION.md` |

---

## Merge Conflict Resolution & Line-by-Line Audit of `origin/main` (`5f0ee759`)

- **Conflict encountered (`2026-10-22T00:18Z–00:19Z`)**: Session `5f0ee759` initialized `COORDINATION.md` on `arena/5f0ee759-savings5` at `2026-10-22T00:05:30Z` (`84dd3b4`), while parallel session `a67a75fe` merged PRs #1–#5 (`012e522` .. `61503c6`) to `main`.
- **Resolution action**: Stopped immediately on each `COORDINATION.md` conflict, preserved **100% of `a67a75fe`'s files, task records, session logs, scripts, QA fixes, and baseline dataset**, and audited every file line by line against live primary sources on `2026-10-22`:
  1. **`data/institutions.json` — Inactive-Bank Pollution in Asset Rankings**: `a67a75fe` ranked `Ally Bank` `#34`, `Synchrony Bank` `#49`, and `SoFi Bank` `#89` because its query omitted `ACTIVE:1`, counting 43 failed/merged historical institutions (WaMu, First Republic, SVB, Discover, etc.). Verified via `https://api.fdic.gov/banks/institutions?filters=ACTIVE:1%20AND%20INSFDIC:1&sort_by=ASSET&sort_order=DESC`: actual U.S. active bank ranks are **Ally `#24`**, **Synchrony `#30`**, **SoFi `#46`**, **BMO `#16`**, and **Barclays `#56`**. Every active institution in the combined dataset is among the **Top 56 active FDIC-insured banks in the United States**.
  2. **`data/bonuses.json` — False `$1,000 -> $400` SoFi Direct Deposit Bonus Tier**: `a67a75fe` listed `"Eligible direct deposit of $1,000 or more"` as earning `$400`. Verified against Official Footnote `#4` on `https://www.sofi.com/banking/high-yield-savings-account/`: `$1,000.00–$4,999.99` in qualifying direct deposits within 25 days pays **`$50`**, whereas **`$400` requires `$5,000.00 or more`** within the 25-day evaluation period. Also verified `https://www.sofi.com/legal/banking-rate-sheet` (`SoFi-Bank-Rate-Sheet-October-20-2026.pdf`), documenting **`4.70%` APY on `≤$20,000` (`$10/mo` SoFi Plus)** and the **`0.80%` APY non-qualifying base rate**.
  3. **Expanded Verified National Bank Coverage Solving the `$2.5M` Single-Owner FDIC Shortfall**:
     - Added **`Select Savings from Barclays` (`CERT 57203`)**: **`4.25%` APY** across all tiers (AARP membership required) + **`$400` cash bonus** (`$40,000` within 30 days, held 120 days, open by `2026-10-31`, `https://banking.us.barclays/select-home/`) — highest ongoing verified APY in the study.
     - Added **`Barclays Tiered Savings` (`CERT 57203`)**: **`3.50%` APY** (`<$250k`) / **`3.65%` APY** (`$250k–$1M`) + **`$200` cash bonus** (`$25,000` within 30 days, held 120 days, open by `2026-10-31`, `https://banking.us.barclays/tiered-savings`), and flagged the **`$250,000.00` Single-Owner FDIC Boundary Trap**.
     - Verified **first-party official Chase New York Deposit Rate Sheet PDF** hosted on `chase.com` (`https://www.chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf`, effective `2026-10-16`): **`0.01%` APY** on `Chase Savings℠` (`0.02%` relationship APY on `Chase Premier Savings℠`).
     - Verified **first-party Citibank Enhanced Direct Deposit & Promotional Rate disclosures** (`https://banking.citi.com/cbol/OM/checking/enhanced-direct-deposit-offer/default.htm`: **`3.75%` 3-month promotional rate on `$25,000+` new funds**; `0.98%–1.05%` 1-yr APY; `0.03%–0.12%` standard rate) AND `https://www.citi.com/content/dam/cfs/mobile/assets/JRS/popups/ao/Fact_Sheet.pdf` proving **`2026-10-22` is the final day before Citi discontinues the 3-month promotional rate on `2026-10-23`**, while keeping regional base APY on `citi.com/banking/savings-account` flagged.
     - Verified **first-party TD Bank `$200` Savings Bonus** (`https://www.td.com/us/en/personal-banking/savings-accounts/featured`, `$10,000+` within 20 days held 90 days through `2026-11-30`) + **`TD Simple Savings` (`0.02%` APY)** (`https://www.td.com/us/en/personal-banking/savings-accounts/simple`), while keeping **`TD Signature Savings`** APY `not stated` behind TD's empty geo-modal rate table.
     - Added **`Alto Online Savings by BMO` (`CERT 16571`, `3.00%` APY as of `2026-10-21`)** (`https://www.alto.bmo.com/en-us/`) and explicitly excluded it from mobile-first ladders because Alto **has NO mobile app** (`BMO Digital Banking` cannot access Alto).
     - Together, the **12 distinct verified mobile-app-enabled FDIC charters** now cover up to **`$3,000,000` single-owner FDIC insurance (`100%` of the `$2,500,000` ladder with `$0` uninsured remainder)**, **`$6,000,000` joint 2-owner**, and **`$15,000,000` 5-beneficiary revocable trust**, plus SoFi's optional **`$3,000,000` participating-bank network**.
  4. **Official First-Party Mobile App & Security Pages Verified Across `Marcus`, `American Express`, `Fifth Third`, and Peers**:
     - Confirmed `Marcus Mobile Banking App` (`https://www.marcus.com/us/en/marcus-mobile-banking-app`), `American Express® App` (`https://www.americanexpress.com/en-us/banking/online-savings/high-yield-savings-account/`), and `Fifth Third Mobile Banking App` (`https://www.53.com/content/fifth-third/en/personal-banking/bank/online-mobile-banking/mobile-banking.html`), plus US App Store ratings across all apps.
  5. **Macro Monetary & U.S. Treasury Benchmark Context Added (`data/fdic.json` & `data/benchmarks.json`)**:
     - Added Federal Reserve FOMC `2026-09-17` target range **`3.75%–4.00%`** (`https://www.federalreserve.gov/newsevents/pressreleases/monetary20260917a.htm`) and latest U.S. Treasury daily par yield curve `2026-10-21` (`3M 4.25%` – `10Y 5.13%`, `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202610`).
  6. **Synchrony Stale Calculator Widget Discrepancy Flagged**:
     - Flagged on `flagged.html` that Synchrony's calculator widget on `https://www.synchrony.com/banking/products/hys-core` still computes using stale `2.85%` while the page headline and October 2026 official rate disclosure state **`3.55%` APY**.

---

## Preserved Session Log — `a67a75fe` (`2026-10-22`, preserved from `origin/main`)

| Item | Value |
|---|---|
| Baseline PR #1 | https://github.com/sassnarep3-star/SAVINGS5/pull/1 (`MERGED`, `012e522131a4b8507b044f5eb4894a2b6adf33f6`, `2026-10-22T00:13:15Z`) |
| Follow-up PR #2 | https://github.com/sassnarep3-star/SAVINGS5/pull/2 (deploy fixes) — `MERGED` |
| Ladder fix PR #3 | https://github.com/sassnarep3-star/SAVINGS5/pull/3 (FDIC coverage overstatement) — `MERGED` |
| Copy fix PR #4 | https://github.com/sassnarep3-star/SAVINGS5/pull/4 (ladder intro) — `MERGED` |
| QA PR #5 | https://github.com/sassnarep3-star/SAVINGS5/pull/5 (fee column, not-stated cells, bank count, FDIC table dedupe) — `MERGED` |
