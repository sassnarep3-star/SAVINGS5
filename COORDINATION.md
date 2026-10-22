# COORDINATION.md — Shared Multi-Session Task Board (`SAVINGS5`)

> **Repository:** `sassnarep3-star/SAVINGS5`  
> **Reference Open / Verification Date:** `2026-10-22` (UTC)  
> **Coordination Protocol:** Read this file and run `git fetch --all --prune` before claiming or editing any files. Claim tasks with non-overlapping file scopes, commit and push immediately upon claiming, verify every figure line-by-line from official `.gov` or official bank websites only (never infer or hallucinate values; leave unconfirmable fields blank and record on Flagged for Review), and coordinate shared outputs cleanly during final integration.  
> **Platform Branch Note:** Session `5f0ee759` works on its Arena-assigned branch `arena/5f0ee759-savings5` and syncs against `origin/main` and all remote branches prior to every commit/push.

---

## Task Board

| Task ID | Task Name | Status | Owning Session ID | Claimed At (UTC) | File Scope | Notes / Review Summary |
|---|---|---|---|---|---|---|
| `TASK-01` | Initial Repo Line-by-Line Audit & Official Macro / Regulatory Benchmarks (FDIC Rules, National Rates, Treasury & Fed Curve) | `done` | `arena/5f0ee759-savings5` | `2026-10-22T00:05:30Z` | `data/benchmarks.json`, `data/repo_audit.json` | Verified line-by-line on `2026-10-22`: baseline `README.md` audited; FDIC national savings rate `0.38%` (cap `4.63%`, effective `2026-10-19`), FOMC target `3.75%–4.00%` (`2026-09-17`), Treasury curve (`2026-10-21`: 3M `4.25%`, 6M `4.35%`, 1Y `4.52%`, 2Y `4.81%`, 5Y `4.95%`), FDIC SMDIA `$250k` / Joint `$500k` / Trust up to `$1.25M`. |
| `TASK-02` | Official FDIC BankFind Charter, Asset Scale, App Availability & Security Verification | `in progress` | `arena/5f0ee759-savings5` | `2026-10-22T00:07:30Z` | `data/charters_fdic.json` | Verifying FDIC Cert #, active status, legal charter name, total assets/deposits, shared-charter traps, iOS/Android official apps, and security controls from official sources. |
| `TASK-03` | National High-Yield Direct Banks — Rates, Deposit Rules, Fees & Opening Bonuses | `unclaimed` | — | — | `data/national_direct_banks.json` | Line-by-line verification from official bank websites/disclosures (Capital One 360, American Express National Bank, Marcus by Goldman Sachs, Ally Bank, Discover Bank, Synchrony Bank, Barclays US, BMO Alto). |
| `TASK-04` | Major National Brick-and-Mortar Banks — Rates, Deposit Rules, Fees & Opening Bonuses | `unclaimed` | — | — | `data/national_branch_banks.json` | Line-by-line verification from official bank websites/PDF disclosures (Chase, Bank of America, Citibank, Wells Fargo, U.S. Bank, PNC Bank). Leave regional/JS-gated unconfirmable cells blank and log flags. |
| `TASK-05` | Flagged Irregularities & Unverified Fields Catalog | `unclaimed` | — | — | `data/flagged_items.json` | Compile every unverified blank cell and structural irregularity (e.g., shared FDIC charters, geo-gated ZIP rate lookup walls, promo terms) with official review links. |
| `TASK-06` | Static Site Architecture, Subpages, Styles, Progressive UI & Verification Script | `unclaimed` | — | — | `styles/main.css`, `js/app.js`, `scripts/build_and_verify.py` | Build clean dashboard templates, return matrix calculator anchored to `2026-10-22`, CSV export, and zero-hallucination / broken-link verifier. |
| `TASK-07` | Final Integration, Line-by-Line Re-Verification, Link Audit, PR Merge & GitHub Pages Deployment | `unclaimed` | — | — | `index.html`, `rates.html`, `returns.html`, `bonuses.html`, `rules.html`, `security.html`, `flagged.html`, `methodology.html`, `data/banks.json`, `data/savings_accounts_verified.csv`, `.nojekyll`, `README.md` | Merge/integrate all verified datasets, generate static HTML pages, run full link & source audit, open & merge PR to `main`, confirm live GitHub Pages deployment, and log PR + deployment status here. |

---

## Session Activity & Verification Log

### `2026-10-22T00:05:30Z` — Session `arena/5f0ee759-savings5`
- Checked `git fetch --all --prune`, remote branches (`origin/main` at commit `8f2dc3a4237a03c0c40a7ef29af9d403b9c433ca`), open/closed PRs (`none`), and GitHub Pages status (`https://sassnarep3-star.github.io/SAVINGS5/`, serving from `main:/`).
- Reviewed existing repository file inventory:
  - `README.md` (1 line, 10 bytes, no trailing newline: `# SAVINGS5` — contains project title header only; no pre-existing bank rate claims or data files in `8f2dc3a`).
- Created `COORDINATION.md` and claimed `TASK-01` (`data/benchmarks.json`, `data/repo_audit.json`).

### `2026-10-22T00:07:30Z` — Session `arena/5f0ee759-savings5` (`TASK-01` Complete → `TASK-02` Claimed)
- **Verification Completed (`TASK-01`):**
  - `https://www.fdic.gov/national-rates-and-rate-caps` — Confirmed FDIC October 2026 rate release (revised `2026-10-19`): National Savings deposit rate `0.38%`, Money Market `0.63%`, 3M CD `1.14%`, 6M CD `1.39%`, 12M CD `1.76%`, 24M CD `1.55%`, 36M CD `1.39%`, 60M CD `1.41%`; Savings National Rate Cap `4.63%`.
  - `https://www.federalreserve.gov/monetarypolicy/openmarket.htm` — Confirmed FOMC Federal Funds Target Range `3.75%–4.00%` effective `2026-09-17` (+25 bps change).
  - `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202610` — Confirmed Daily Treasury Par Yield Curve as of `2026-10-21`: 1M `4.09%`, 3M `4.25%`, 6M `4.35%`, 1Y `4.52%`, 2Y `4.81%`, 3Y `4.89%`, 5Y `4.95%`, 10Y `5.13%`, 30Y `5.42%`.
  - `https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance` & `https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance` — Confirmed `$250,000` standard per-depositor, per-insured-bank, per-ownership-category limit (`$500,000` joint for 2 co-owners; `$250,000` per beneficiary up to `$1,250,000` max under the FDIC Trust Rule effective `2024-04-01`).
- Claimed `TASK-02` (`data/charters_fdic.json`).

