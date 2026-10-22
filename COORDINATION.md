# COORDINATION.md — Shared Multi-Session Task Board (`SAVINGS5`)

> **Repository:** `sassnarep3-star/SAVINGS5`  
> **Reference Open / Verification Date:** `2026-10-22` (UTC)  
> **Coordination Protocol:** Read this file and run `git fetch --all --prune` before claiming or editing any files. Claim tasks with non-overlapping file scopes, commit and push immediately upon claiming, verify every figure line-by-line from official `.gov` or official bank websites only (never infer or hallucinate values; leave unconfirmable fields blank and record on Flagged for Review), and coordinate shared outputs cleanly during final integration.  
> **Platform Branch Note:** Session `5f0ee759` works on its Arena-assigned branch `arena/5f0ee759-savings5` and syncs against `origin/main` and all remote branches prior to every commit/push.

---

## Task Board

| Task ID | Task Name | Status | Owning Session ID | Claimed At (UTC) | File Scope | Notes / Review Summary |
|---|---|---|---|---|---|---|
| `TASK-01` | Initial Repo Line-by-Line Audit & Official Macro / Regulatory Benchmarks (FDIC Rules, National Rates, Treasury & Fed Curve) | `in progress` | `arena/5f0ee759-savings5` | `2026-10-22T00:05:30Z` | `data/benchmarks.json`, `data/repo_audit.json` | Auditing existing repository files (`README.md`) line-by-line and verifying FDIC insurance rules, FDIC national savings average, FOMC target range, and US Treasury par yields from `.gov` sources. |
| `TASK-02` | Official FDIC BankFind Charter, Asset Scale, App Availability & Security Verification | `unclaimed` | — | — | `data/charters_fdic.json` | Verify FDIC Cert #, legal charter name, total assets/deposits, charter-sharing traps, iOS/Android official apps, and security controls from official sources. |
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
