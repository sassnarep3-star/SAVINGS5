# COORDINATION — Shared Multi-Session Task Board & Audit Ledger

**Repo:** `sassnarep3-star/SAVINGS5`
**Last updated:** 2026-10-22 (UTC)
**Account Opening / Benchmark Anchor Date:** `2026-10-22`
**Active Integration Session:** `5f0ee759` (branch `arena/5f0ee759-savings5`, reconciling and auditing completed session `a67a75fe`)
**Prior Completed Session:** `a67a75fe` (branch `arena/a67a75fe-savings5`, merged PR #1 `012e522` & PR #2 `2165a9b`)
**Live site:** https://sassnarep3-star.github.io/SAVINGS5/

---

## Coordination rules in force

1. Read this file before starting any task.
2. Claim a task by adding your session ID + file scope, then commit and push the claim **immediately**.
3. Never start a task another live session has claimed. A claim older than 60 minutes with no commits may be taken over — note the handoff.
4. Keep scopes non-overlapping. If you need to change a file owned by another session, log a request here instead of editing it.
5. Small, frequent commits. `git pull --rebase` / `git fetch --all` before every push. Never drop another session's work to resolve a conflict.
6. Never mark anything "verified" without an official source link and the date it was checked (`2026-10-22` retrieval; exact source effective date recorded). Leave unconfirmed values blank (`null` / `—`) and flag them on `flagged.html` with source links.
7. Shared outputs (`data/*.json`, `index.html`, nav, site pages) are changed only by a final integration session once all other tasks are done. That session merges the branches without discarding prior work, re-verifies the combined data line by line against official sources, confirms zero broken links, and publishes to GitHub Pages.

---

## Unified Task Board (Sessions `a67a75fe` + `5f0ee759`)

### Session `a67a759` / `a67a75fe` Completed Baseline Tasks (`T1–T10`, preserved intact from `origin/main` `2165a9b`)

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
| T10 | PR to `main`, merge, deploy verification | done | a67a75fe | `COORDINATION.md` (PR #1 & PR #2 merged) |

### Session `5f0ee759` Research, Line-by-Line Repo Audit & Final Integration Tasks (`TASK-01–TASK-07`)

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|------------|
| TASK-01 | Macro & Regulatory Benchmark Verification (`FDIC`, `Federal Reserve FOMC`, `U.S. Treasury`) | done | 5f0ee759 | `data/benchmarks.json`, `data/repo_audit.json`, `data/fdic.json` |
| TASK-02 | National Institution Screening, Active-Charter Ranking Audit & Mobile App Store Verification (18 Active Top-56 Banks + Merged Discover `#5649`) | done | 5f0ee759 | `data/institutions.json`, `research/verification-log.md` |
| TASK-03 | Direct National HYSA Verification & Expansion (`Barclays Select 4.25%` + `Tiered 3.50%/3.65%`, `Alto by BMO 3.00%`, `SoFi Plus 4.70%`, `Synchrony`, `Marcus`, `Capital One`, `Amex`, `Ally`) | done | 5f0ee759 | `data/accounts.json`, `data/bonuses.json` |
| TASK-04 | Branch Megabank Primary PDF & Promo Verification (`Chase NY PDF rdny1.pdf`, `Citi Fact_Sheet.pdf 3.75% final day`, `TD $200 bonus + Simple 0.02%`, `BofA`, `Wells Fargo`, `U.S. Bank`, `PNC`, `Truist`, `Fifth Third`, `Schwab`) | done | 5f0ee759 | `data/accounts.json`, `data/bonuses.json` |
| TASK-05 | Merge Conflict Resolution & Line-by-Line Verification Audit of `origin/main` (`2165a9b`) | done | 5f0ee759 | `COORDINATION.md` (zero work discarded; 8 concrete defects found & remediated) |
| TASK-06 | Final Integration Build: Multi-Charter `CERT`-Safe Return Engine + Interactive Filtering, Custom Deposit/Lifespan Calculator, FDIC Coverage Planner & Modern Executive UI | in_progress | 5f0ee759 | `tools/build_returns.py`, `tools/build_site.py`, `tools/check_site.py`, `assets/style.css`, `assets/app.js`, `*.html`, `README.md` |
| TASK-07 | Build Gate, Zero-Broken-Link Verification, PR to `main`, Merge & GitHub Pages Deployment Verification | pending | 5f0ee759 | `COORDINATION.md` |

---

## Merge Conflict Resolution Log (`arena/5f0ee759-savings5` <- `origin/main` `2165a9b`)

- **Conflict encountered (`2026-10-22T00:18Z`)**: Parallel session `5f0ee759` initialized `COORDINATION.md` on `arena/5f0ee759-savings5` at `2026-10-22T00:05:30Z` (`84dd3b4`), while parallel session `a67a75fe` independently created `COORDINATION.md` on `arena/a67a75fe-savings5` and merged PR #1 (`012e522`) and PR #2 (`2165a9b`) to `main` at `2026-10-22T00:14:19Z` before `5f0ee759` integrated shared outputs.
- **Resolution action**: Stopped immediately on `AA COORDINATION.md`, inspected every file and commit on `origin/main` (`8f2dc3a..2165a9b`), preserved **100% of `a67a75fe`'s files, task records, session notes, scripts, and 16-institution baseline dataset**, merged cleanly with `--no-ff`, and transitioned `5f0ee759` into the final integration & line-by-line verification role defined by rule #7.

---

## Line-by-Line Audit of `origin/main` (`2165a9b`) — Defects Caught & Remediated by `5f0ee759`

1. **`tools/build_returns.py` — FDIC Per-Charter Double-Counting Bug (`account["id"]` vs `account["cert"]`)**:
   - **Defect in `2165a9b`**: The multi-bank FDIC ladder builder deduplicated chosen accounts by `len({c["id"] for c in chosen})` instead of FDIC Certificate number (`cert`). Whenever an insured institution offers multiple savings accounts in the pool (e.g., Wells Fargo `CERT 3511` or Barclays `CERT 57203`), placing `$250,000` into two accounts at the same bank charter was counted as `$500,000` "fully covered" when `$250,000` would be uninsured under FDIC single-ownership aggregation rules (`https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance`).
   - **Fix**: Enforced strict **one-account-per-FDIC-`CERT` deduplication** across all multi-bank FDIC ladders (`distinct_certs = len({c["cert"] for c in chosen})`).
2. **`data/institutions.json` — Inactive-Bank Pollution in Asset Rankings**:
   - **Defect in `2165a9b`**: `institutions.json` reported `Ally Bank` as rank `#34`, `Synchrony Bank` as rank `#49`, and `SoFi Bank` as rank `#89` among active FDIC-insured banks because its `ASSET:[X TO *]` count omitted `ACTIVE:1`, including 43 failed/merged historical institutions (Washington Mutual, First Republic, Silicon Valley Bank, Discover Bank, etc.).
   - **Fix**: Verified exact active-only ordering via `https://api.fdic.gov/banks/institutions?filters=ACTIVE:1%20AND%20INSFDIC:1&sort_by=ASSET&sort_order=DESC`: true U.S. active asset ranks are **Ally `#24`**, **Synchrony `#30`**, **SoFi `#46`**, **BMO `#16`**, and **Barclays `#56`**. Every active bank in the combined dataset is among the **Top 56 active FDIC-insured U.S. banks**.
3. **`data/bonuses.json` — Incorrect `$1,000 -> $400` Direct Deposit Requirement for SoFi Cash Bonus**:
   - **Defect in `2165a9b`**: Listed `{"bonus_usd": 400, "requirement": "Eligible direct deposit of $1,000 or more"}`.
   - **Fix**: Verified against Official Direct Deposit Bonus Table on `https://www.sofi.com/banking/high-yield-savings-account/`: `$1,000.00–$4,999.99` in qualifying direct deposits within 25 calendar days earns **`$50`**, while **`$400` requires `$5,000.00 or more`** within the 25-day evaluation period. Also verified `https://www.sofi.com/legal/banking-rate-sheet` (`SoFi-Bank-Rate-Sheet-October-20-2026.pdf`), adding **`4.70%` APY on `≤$20,000` (`$10/mo` SoFi Plus)** and documenting the **`0.80%` APY non-qualifying base rate**.
4. **`data/accounts.json` — Contradictory `$0` Monthly Fee Field on Fifth Third Momentum Savings**:
   - **Defect in `2165a9b`**: Set `"monthly_fee_usd": 0` while `"fee_waiver"` stated `"otherwise $7.50"`, understating non-waived fee drag in `build_returns.py`.
   - **Fix**: Verified on `https://www.53.com/content/fifth-third/en/personal-banking/bank/savings.html`: updated `"monthly_fee_usd": 7.5` (waived with `$500+` balance or linked Fifth Third checking).
5. **Primary Official Rate PDF & Promo Discoveries Added (`Chase`, `Citibank`, `TD Bank`, `Barclays`, `BMO / Alto`)**:
   - **Chase (`CERT 628`)**: Verified official New York Deposit Rate Sheet PDF `https://www.chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf` (`Effective 2026-10-16`): **`0.01%` APY** on `Chase Savings℠` (`0.02%` relationship APY on `Chase Premier Savings℠`); retained flag noting regional variation on `chase.com`.
   - **Citibank (`CERT 7213`)**: Verified official `https://banking.citi.com/cbol/OM/checking/enhanced-direct-deposit-offer/default.htm` (**`3.75%` 3-month promotional rate on `$25,000+` new funds**; `0.98%–1.05%` 1-yr blended APY; `0.03%–0.12%` standard rate) AND `https://www.citi.com/content/dam/cfs/mobile/assets/JRS/popups/ao/Fact_Sheet.pdf` proving **`2026-10-22` is the final day before Citi discontinues the 3-month promotional rate on `2026-10-23`**! Standard non-promo base APY on `citi.com/banking/savings-account` remains `null` (`unverified`) due to Citi's `:BLUE_AccSavings_Rate%` template defect.
   - **Barclays Bank Delaware (`CERT 57203`)**: Added **`Select Savings from Barclays` (`4.25%` APY all balances, AARP required + `$400` cash bonus expiring `2026-10-31`)** (`https://banking.us.barclays/select-home/`) — highest ongoing verified APY in the entire study — and **`Barclays Tiered Savings` (`3.50%` `<$250k` / `3.65%` `$250k–$1M` + `$200` cash bonus expiring `2026-10-31`)** (`https://banking.us.barclays/tiered-savings`), flagging its **`$250,000.00` Single-Owner FDIC Boundary Trap**.
   - **TD Bank (`CERT 18409`)**: Verified **`$200` Savings Bonus** (`$10,000+` within 20 days held 90 days through `2026-11-30`, `https://www.td.com/us/en/personal-banking/savings-accounts/featured`) + **`TD Simple Savings` (`0.02%` APY)** (`https://www.td.com/us/en/personal-banking/savings-accounts/simple`), while keeping **`TD Signature Savings`** APY `null` (`unverified`) behind TD's empty geo-modal rate table.
   - **Alto Online Savings by BMO (`CERT 16571`)**: Added (`3.00%` APY as of `2026-10-21`, `https://www.alto.bmo.com/en-us/`) and explicitly flagged/disqualified from mobile-first ladders because Alto **has NO mobile app** and shares `CERT 16571` with BMO Bank N.A.
6. **Official Mobile App & Security Pages Verified for `Marcus`, `American Express`, `Fifth Third`, and All Peers**:
   - Verified directly on official bank domains (`https://www.marcus.com/us/en/marcus-mobile-banking-app`, `https://www.americanexpress.com/en-us/banking/online-savings/high-yield-savings-account/`, `https://www.53.com/content/fifth-third/en/personal-banking/bank/online-mobile-banking/mobile-banking.html`, plus official bank security centers and Apple App Store listings).
7. **Macro Monetary & U.S. Treasury Curve Context Added (`data/fdic.json` & `data/benchmarks.json`)**:
   - Verified Federal Reserve FOMC `2026-09-17` target range **`3.75%–4.00%`** (`https://www.federalreserve.gov/newsevents/pressreleases/monetary20260917a.htm`) and latest U.S. Treasury daily par yield curve `2026-10-21` (`3M 4.25%`, `6M 4.35%`, `1Y 4.52%`, `2Y 4.81%`, `3Y 4.89%`, `5Y 4.95%`, `10Y 5.13%`, `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202610`).
8. **Synchrony Stale Calculator Widget Discrepancy Flagged**:
   - Documented on `flagged.html` that Synchrony's embedded earnings calculator widget on `https://www.synchrony.com/banking/products/hys-core` still calculates with stale `2.85%` while the page headline and October 2026 official rate disclosure state **`3.55%` APY**.

---

## Preserved Session Log — `a67a75fe` (`2026-10-22`, preserved from `origin/main` `2165a9b`)

#### a67a75fe — 2026-10-22

**Claim.** Repo had one initial commit and no `COORDINATION.md`; no other sessions or branches were present. Claimed T1–T10
immediately and pushed the claim before starting work. The harness pins this session to `arena/a67a75fe-savings5`, so
per-session branches (`session-<id>/<task>`) are folded into this one branch — recorded so a later session does not read the
branch name as a conflict.

**What was built (baseline PR #1 + PR #2).**
- 16 FDIC-insured institutions, 17 savings accounts, 21 tables, 253 table rows, every row carrying an official source link.
- Return model at 8 deposit sizes ($10k–$2.5M) and 4 terms (1/2/3/5 years), with a constant-rate scenario and a stress-case scenario, plus FDIC ladder plans for $250k–$5M.
- Static site of 10 pages (`index.html`, `accounts.html`, `returns.html`, `bonuses.html`, `rules.html`, `security.html`, `competitiveness.html`, `flagged.html`, `sources.html`, `methodology.html`).
- Baseline PR #1: https://github.com/sassnarep3-star/SAVINGS5/pull/1 (`MERGED`, `012e522131a4b8507b044f5eb4894a2b6adf33f6`, `2026-10-22T00:13:15Z`).
- Follow-up PR #2: https://github.com/sassnarep3-star/SAVINGS5/pull/2 (`MERGED`, `2165a9bf...`, `2026-10-22T00:14:19Z`).
