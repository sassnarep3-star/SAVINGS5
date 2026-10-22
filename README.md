# SAVINGS5 — Verified U.S. National Bank Savings & Max-FDIC Strategy

- **Live GitHub Pages Dashboard:** <https://sassnarep3-star.github.io/SAVINGS5/>
- **Account Open & Verification Anchor Date:** `2026-10-22`

Line-by-line primary-source research, return modeling, and multi-charter FDIC deposit insurance optimization across **20 active Top-56 U.S. FDIC-insured banks** (`$43.5B` to `$4.09T` in assets, totaling `$15.31T`; **24 savings accounts**, **10 verified promotions**, **zero third-party aggregator sources**).

## Key Highlights (`2026-10-22`)

- **Top Ongoing Verified APYs:**
  - **Barclays Select Savings (`CERT 57203`):** **`4.25%` APY** all balances (AARP required) + **`$400` cash bonus** (`$40k` held 120d, expires `2026-10-31`) — `$11,025` Year-1 gain on `$250,000`.
  - **CIT Bank Platinum Savings — First-Citizens Bank (`CERT 11063`):** **`3.75%` APY** ongoing on `≥ $5,000` (`4.25%` APY for 6 months w/ code `BOOST50` through `2026-12-15` -> **`4.00%` Year-1 blended APY**); **`CIT Savings Connect`** offers **`3.65%` APY** on all balances.
  - **SoFi Checking & Savings (`CERT 26881`):** **`4.40%` APY** for 6 months w/ direct deposit (**`3.85%` Year-1 blended** / `3.30%` ongoing DD; `0.80%` base) + **`$50` (`$1k–$4,999.99` DD) / `$400` (`$5,000+` DD in 25d)** bonus.
  - **Marcus by Goldman Sachs (`CERT 33124`):** **`3.50%` APY** ongoing (`4.50%` for 3 months w/ referral -> **`3.75%` Year-1 APY**).
  - **Barclays Tiered Savings (`CERT 57203`):** **`3.50%`** `<$250k` / **`3.65%`** `$250k–$1M` + **`$200` cash bonus** (flagged `$250,000.00` single-owner FDIC boundary trap).
  - **Synchrony High Yield Savings (`CERT 27314`):** **`3.55%` APY** unconditional from `$0.01`, `$0` minimum, `$0` fee.
- **Urgent `2026-10-22` Discontinuation Alert:** Citibank's official `Fact_Sheet.pdf` confirms **`2026-10-22` is the final day** before Citi discontinues its `3.75%` 3-month promotional savings rate on **`2026-10-23`**.
- **Max FDIC Coverage Architecture:** Deduplicates strictly by FDIC Certificate (`CERT`) across **14 mobile-app-verified national charters** (`$3,500,000` Single-Owner / `$7,000,000` 2-Owner Joint / `$17,500,000` 5-Beneficiary POD Trust).

## Site Pages

| Page | Coverage |
|---|---|
| [`index.html`](index.html) | Executive overview, interactive custom deposit/lifespan/ownership FDIC optimizer, `$250k` leaderboard & coverage table |
| [`accounts.html`](accounts.html) | Master 24-account comparison table + full line-by-line primary-source dossiers |
| [`returns.html`](returns.html) | 9 deposit sizes (`$10k–$2.5M`) × 7 lifespans (`3M–10Y` anchored to `2026-10-22`), Day-1 principal caps & multi-bank ladders |
| [`bonuses.html`](bonuses.html) | 10 verified cash bonuses & rate boosts + 10 verified non-bonus checks |
| [`rules.html`](rules.html) | Minimums, opening rules, excess withdrawal fees, closure rules & fee drag analysis |
| [`security.html`](security.html) | FDIC BankFind register, active asset ranks, shared-charter alerts, mobile app ratings & MFA/security checks |
| [`competitiveness.html`](competitiveness.html) | Spreads vs FDIC National Rates (`2026-10-19`), FOMC (`3.75%–4.00%`), and U.S. Treasury Par Curve (`2026-10-21`) |
| [`rates-refresh.html`](rates-refresh.html) | Supplemental NYC web-HTML snapshot & downloadable 120-row / 84-row CSV scenario matrices |
| [`flagged.html`](flagged.html) | Unverified/ZIP-gated blank cells, broken bank page tokens, charter overlaps & cross-session audit log |
| [`sources.html`](sources.html) | Master index of every `.gov` and first-party bank URL with retrieval & effective dates |
| [`methodology.html`](methodology.html) | Formulas, charter deduplication rules & build pipeline |

## Reproduce & Verify Locally

```bash
python3 tools/build_returns.py
python3 tools/build_site.py
python3 research/validate_research.py
python3 tools/check_site.py
```
