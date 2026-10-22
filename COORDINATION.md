# Multi-Session Coordination Log — `sassnarep3-star/SAVINGS5`

- **Repository:** `sassnarep3-star/SAVINGS5`
- **Live GitHub Pages URL:** <https://sassnarep3-star.github.io/SAVINGS5/> (`main` branch, root `/`)
- **Account Open & Verification Anchor Date:** `2026-10-22`

---

## Multi-Session Coordination Rules

1. **Pull / fetch before every push** (`git fetch --all --prune` and merge/rebase cleanly against `origin/main`).
2. **Never discard another session's work** — preserve all verified datasets, supplementary research CSVs/JSONs, `docs/*.html` compatibility stubs, `data/session-291c7881/*` cross-check artifacts, and prior coordination records.
3. **Strict Official Primary-Source Rule** — cite only `.gov` agencies (`fdic.gov`, `api.fdic.gov`, `federalreserve.gov`, `home.treasury.gov`), first-party bank `.com` disclosures/PDFs, and official App Store listings (`apps.apple.com`). **Zero third-party rate aggregators** anywhere in `data/` or HTML.
4. **Never Hallucinate / Infer** — any APY, fee, or term gated behind client-side ZIP modals, unresolved server template tokens, or missing pages stays strictly blank (`null` / `—`) and is documented on `flagged.html` with its primary link.
5. **Dual Build Gate** — both `python3 research/validate_research.py` AND `python3 tools/check_site.py` (plus `git diff --check`) must pass 100% before opening or merging any PR to `main`.

---

## Summary of All Four Parallel Sessions Reconciled on `main`

All four parallel sessions forked from initial seed commit `8f2dc3a4237a03c0c40a7ef29af9d403b9c433ca` (`README.md` only) and have now been reconciled with **zero lost work**:

| Session Branch | Task IDs | PRs Merged to `main` | Preserved Deliverables & Cross-Session Contributions |
|---|---|---|---|
| `arena/a67a75fe-savings5` | `T1`–`T10` | `#1`–`#9` | Initial 16-bank / 17-account verified dataset (`data/fdic.json`, `institutions.json`, `accounts.json`, `bonuses.json`, `returns.json`), initial 10 root HTML pages, `tools/build_site.py`, `tools/check_site.py`, `research/verification-log.md`. |
| `arena/3a8e8ff0-savings5` | `T11`–`T12` | `#11`–`#12` (`34c801f`) | Supplemental NYC HTML capture & CSV scenario suite (`data/research.json`, `data/standard-projections.csv`, `data/promotion-projections.csv`, `research/calculate_projections.py`, `research/validate_research.py`, `research/source-matrix.csv`, `research/research-summary.md`, `research/projection-method.md`) and `rates-refresh.html`. |
| `arena/291c7881-savings5` | `T13`–`T15` | `#10`, `#13` (`6661c6f`) | Preserved independent cross-check archive in `data/session-291c7881/*`, `docs/*.html` redirect stubs (`docs/.nojekyll`), plus `cit-savings-connect` (`3.65%` APY) and `citizens-one-deposit-savings` (`CERT 57957`). |
| `arena/5f0ee759-savings5` | `TASK-01`–`TASK-08` | Final Integration PR (recorded below) | Line-by-line audit across all files + expansion to **20 active Top-56 U.S. banks (`$15.31T` assets) + merged Discover (`#5649`) = 21 bank records & 24 savings accounts**, **10 verified bonuses/boosts**, **14 mobile-enabled FDIC charters (`$3.50M` single / `$7.00M` joint / `$17.50M` trust)**, interactive custom deposit/lifespan/ownership FDIC optimizer (`assets/app.js` + `assets/style.css`), dark/light theme, live table search/sort/CSV export, and full cross-session defect remediation. |

---

## Line-by-Line Audit Findings & Cross-Session Corrections (`arena/5f0ee759-savings5`)

1. **Barclays US Consumer Bank (`CERT 57203`) — Complete Product & Bonus Verification:**
   - Added **Select Savings from Barclays (`4.25%` APY all balances, AARP membership required)** + **`$400` cash bonus** (`$40,000` new money held 120 days, expires `2026-10-31`) — top Year-1 single-owner insured return (`$11,025` gain on `$250,000`).
   - Added **Barclays Tiered Savings `$200` cash bonus** (`$25,000–$30,000` held 120 days) alongside its `3.50%` (`<$250k`) / `3.65%` (`$250k–$1M`) tiers, and verified **Barclays US App (`4.8★`, `apps.apple.com/us/app/barclays-us-app/id619260292`)**.
   - Flagged the **`$250,000.00` Single-Owner FDIC Boundary Trap**: qualifying at `3.65%` leaves `$0` insured headroom for accrued interest under single ownership unless titled Joint (`$500k`) or POD Trust (up to `$1,250k`), or capped at Day-1 principal `$241,196`.
2. **CIT Bank / First-Citizens Bank (`CERT 11063`) — Mobile App, `$0` Fee, `Savings Connect` & `BOOST50` Promo:**
   - Confirmed both **CIT Platinum Savings (`3.75%` APY `≥$5k` / `0.25%` `<$5k`, `$0` monthly fee)** and **CIT Savings Connect (`3.65%` APY all balances, `$0` monthly fee)** on `cit.com/cit-bank/resources/products-and-rates` (noting the `2026-07-01` rate-sheet date caveat), confirmed **CIT Bank Mobile Banking (`4.8★`, `apps.apple.com/us/app/cit-bank-mobile-banking/id1032693959`)**, and added verified **`BOOST50` `+0.50%` 6-month promotional boost (`4.25%` APY for 6 months = `4.00%` Year-1 blended APY through `2026-12-15`)** from `cit.com/cit-bank/platinum-savings/boost`.
3. **Citibank (`CERT 7213`) — Urgent `2026-10-22` Final-Day Promo Discontinuation & UAT URL Fix:**
   - Verified directly from Citibank's primary `Fact_Sheet.pdf` (`online.citi.com/.../Fact_Sheet.pdf`) that **today (`2026-10-22`) is the final day** before Citibank discontinues its `3.75%` APY 3-month promotional savings rate on **`2026-10-23`**, while the public web page prints raw `:BLUE_AccSavings_Rate%` template text.
   - Purged `sit58.online.citi.com` non-production UAT hostname leaked into `data/research.json` and `research/source-matrix.csv` during `T11`, replacing it with canonical `https://online.citi.com/...` and adding `"sit58."` to `tools/check_site.py` banned tokens.
4. **SoFi (`CERT 26881`) — Corrected `$50` vs `$400` Direct Deposit Cash Bonus Error:**
   - Prior `data/bonuses.json` on `main` misread SoFi's terms as awarding `$400` at `$1,000+` direct deposit. Official `sofi.com/banking/` terms prove `$1,000.00–$4,999.99` in 25 days pays **`$50`**, while **`$5,000.00+`** in 25 days is required for **`$400`**. Fixed in `data/bonuses.json`.
5. **Chase (`CERT 628`), TD (`CERT 18409`), BofA (`CERT 3510`), Citizens (`CERT 57957`) & Alto by BMO (`CERT 16571`):**
   - Verified **Chase Savings (`0.01%` APY)** from Chase's official NYC rate sheet PDF (`chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf`, effective `2026-10-16`) + **`$100`/`$200` new-customer bonus** (`account.chase.com/consumer/banking/checkingandsavingsoffer`, expires `2027-01-27`).
   - Verified **TD Simple Savings (`0.02%` APY)** + **TD `$200` Savings Bonus** (`$10,000` new money held 180 days, expires `2026-11-30`), while keeping **TD Signature Savings** APY blank due to unpopulated ZIP cells.
   - Documented **Bank of America Advantage Savings** keeping NYC APY blank while linking BofA's official Virginia PDF (`0.04%` APY) and `$XXXX` HTML fee defect.
   - Verified **Citizens One Deposit Savings (`CERT 57957`, `#17` bank at `$232.5B` assets)**: corrected `291c7881`'s erroneous `$200` minimum-balance fee waiver to Citizens' actual verbatim rule (*one deposit of any amount each monthly maintenance fee period waives the `$4.99` fee*), verified **Citizens Bank Mobile Banking (`4.8★`, `id388082488`)**, and kept APY strictly blank due to `#ProductLine=ODS|...|APY=LowTier(0.00)#%` placeholder tokens (`#ProductLine=` banned outside `flagged.html` in `tools/check_site.py`).
   - Added **Alto Online Savings by BMO (`CERT 16571`, `#16` bank at `$256.8B` assets, `3.00%` APY)** as the explicit control case excluded from recommended FDIC ladders solely because BMO states *"Alto is a web-based product only and does not offer a mobile app at this time"*.
6. **Active-Only FDIC BankFind Ranks & `.gov` Macro Benchmarks (`data/benchmarks.json`, `data/fdic.json`):**
   - Fixed inactive-charter rank inflation across `data/institutions.json` (`ACTIVE:1` filter: `Chase #1`, `BofA #2`, `Citi #3`, `Wells Fargo #4`, `U.S. Bank #5`, `PNC #6`, `Truist #8`, `Capital One #9` + merged `Discover #5649`, `TD #10`, `First-Citizens/CIT #15`, `BMO #16`, `Citizens #17`, `Fifth Third #18`, `Ally #24`, `Synchrony #30`, `Amex #32`, `SoFi #46`, `Marcus/Goldman #11`, `Schwab #12`, `Barclays #56`).
   - Verified **FDIC National Rates (`2026-10-19`: Savings `0.38%`, Cap `4.63%`, MMDA `0.63%`, CDs `1.14%–1.76%`)**, **FOMC (`2026-09-17`: `3.75%–4.00%`)**, and **U.S. Treasury Daily Par Yield Curve (`2026-10-21`: `3M 4.25%`, `6M 4.35%`, `1Y 4.52%`, `2Y 4.81%`, `3Y 4.89%`, `5Y 4.95%`, `10Y 5.13%`)**.

---

## Preserved Prior Session Logs

### `arena/a67a75fe-savings5` (`T1–T10`, PRs `#1`–`#9`)
- Merged PR `#1` (`2165a9b`) through PR `#9` establishing initial 16-bank / 17-account verified dataset, FDIC coverage guide, multi-bank ladders, and 10 static HTML pages at repository root.

### `arena/3a8e8ff0-savings5` (`T11–T12`, PRs `#11`–`#12`)
- Merged PR `#11` (`34c801fc0dcef181f64eb41ecd0fa8b4395cad81`) and PR `#12` publishing `data/research.json` (57 sources, 16 products, 8 offers, 9 flags), `data/standard-projections.csv` (120 rows), `data/promotion-projections.csv` (84 rows), `research/calculate_projections.py`, `research/validate_research.py`, and `rates-refresh.html`.

### `arena/291c7881-savings5` (`T13–T15`, PRs `#10` & `#13`)
- Merged PR `#10` (`670e59ade4f748fe7eb1593599b19760ef75165a`) and PR `#13` (`6661c6f`) preserving `data/session-291c7881/*`, `docs/*.html` redirect stubs, `cit-savings-connect`, and `citizens-one-deposit-savings`.

---

## Final Build, Validation & Publication Record (`arena/5f0ee759-savings5`)

- `python3 tools/build_returns.py` -> **PASS** (`18` projected accounts, `6` unverified excluded accounts, `26` multi-bank FDIC ladder plans across `14` mobile-enabled distinct FDIC charters = `$3,500,000` single / `$7,000,000` joint / `$17,500,000` trust).
- `python3 tools/build_site.py` -> **PASS** (`11` root HTML pages + `12` `docs/*.html` redirect stubs generated).
- `python3 research/validate_research.py` -> **PASS** (`57` official sources, `16` accounts, `8` offers, `9` review flags, `120` rate projections, `84` offer projections).
- `python3 tools/check_site.py` -> **PASS** (`11` root pages + `12` `docs/*.html` redirects, `8` JSON data files, zero broken links, official primary `https://` source link in every single `<tbody><tr>`, zero third-party aggregators, zero duplicate FDIC `CERT`s in any ladder, zero leaked placeholder tokens outside `flagged.html`).
- Final PR URL, merge commit SHA, and live GitHub Pages HTTP verification:
  - **PR #14:** <https://github.com/sassnarep3-star/SAVINGS5/pull/14> — **MERGED** into `main` at `2026-10-22T00:46:50Z` (merge commit `a46ec8d6f567200ee17151c21261ad5dd1070434`).
  - **GitHub Pages Build:** `built` on commit `a46ec8d6f567200ee17151c21261ad5dd1070434` at `2026-10-22T00:47:07Z` (`main` branch, root `/`, HTTPS enforced).
  - **Live Deployment Verification:** Confirmed `200 OK` live serving at <https://sassnarep3-star.github.io/SAVINGS5/> across `index.html`, `accounts.html`, `returns.html`, `bonuses.html`, `rules.html`, `security.html`, `competitiveness.html`, `rates-refresh.html`, `flagged.html`, `sources.html`, and `methodology.html`.
