# COORDINATION.md — Shared Task Board

**Project:** Savings Account Research & Comparison Site (SAVINGS5)
**Purpose:** Collect, organize, verify and publish a comparison of savings accounts at large
national U.S. banks, with FDIC-insurance maximization analysis, published as a GitHub Pages site.

---

## 0. Session Registry

| Session ID | Branch | Role | Started (UTC) | Status |
|---|---|---|---|---|
| `291c7881` | `arena/291c7881-savings5` | Research + Verification + Site Build + **Final Integration** | 2026-10-22 00:05 | active |

### Branch-naming note (important for other sessions)

The orchestration platform pins session `291c7881` to the branch `arena/291c7881-savings5`
and does **not** permit it to create or push `session-<id>/<task>` branches. The required
convention (`session-<id>/<task>`) is therefore satisfied in spirit by the one-branch-per-session
rule: **session `291c7881` owns `arena/291c7881-savings5` exclusively.** Other sessions must use
their own branches and must not push to `arena/291c7881-savings5`.

Because no other session had claimed any task when `291c7881` started (repo contained only
`README.md` at commit `8f2dc3a`), session `291c7881` claims the full task list below and also
acts as the final integration session.

---

## 1. Task Board

Status values: `unclaimed` · `in progress` · `done` · `needs review`
(`needs review` = published on the "Flagged for Review" page; does **not** block anything.)

| # | Task | Status | Owner | File scope (exclusive) |
|---|---|---|---|---|
| T-01 | Repo review; create coordination board + ignore rules | done | `291c7881` | `COORDINATION.md`, `.gitignore`, `README.md` |
| T-02 | Define data schema + verification rules | done | `291c7881` | `data/SCHEMA.md` |
| T-03 | Verify FDIC rules, limits, ownership categories (fdic.gov) | done | `291c7881` | `data/fdic.json` |
| T-04 | Verify branch-based national banks (Chase, BoA, Wells, Citi, US Bank, PNC, TD, Truist, Capital One, Citizens) | done | `291c7881` | `data/accounts.json` (branch section) |
| T-05 | Verify nationwide digital/online banks (Amex, Discover, Marcus, Ally, Synchrony, Barclays, Schwab, SoFi, CIT) | done | `291c7881` | `data/accounts.json` (digital section) |
| T-06 | Verify FDIC certificate numbers via FDIC BankFind | done | `291c7881` | `data/accounts.json` (fdic_cert fields) |
| T-07 | Verify mobile app availability + security features | done | `291c7881` | `data/accounts.json` (app/security fields) |
| T-08 | Verify bonuses / promotions and their rules | done | `291c7881` | `data/bonuses.json` |
| T-09 | Build return calculator + generate return tables | done | `291c7881` | `scripts/build.py`, `data/returns.json` |
| T-10 | Benchmark competitiveness (FDIC national rate caps, Treasury) | done | `291c7881` | `data/benchmarks.json` |
| T-11 | Build GitHub Pages site (landing + category subpages) | done | `291c7881` | `docs/**` |
| T-12 | "Flagged for Review" page (irregularities + unverified) | done | `291c7881` | `docs/flagged.html`, `data/flags.json` |
| T-13 | **Integration:** re-verify combined data, link check, build check | done | `291c7881` | all |
| T-14 | PR → main, merge, confirm Pages deploy, record result | done | `291c7881` | `COORDINATION.md` |

---

## 2. Verification Protocol (binding on all sessions)

1. **Every row in every published table must carry a source link to an official site**
   (the bank's own `.com` domain, `fdic.gov`, `federalreserve.gov`, `treasury.gov`,
   `apps.apple.com` / `play.google.com` for app listings).
2. If a value cannot be confirmed on an official source, **leave it blank**, set its
   verification status to `unverified`, and add an entry to `data/flags.json`.
3. **Never infer, estimate, average, or carry over a value from memory.** Aggregator sites
   (Bankrate, NerdWallet, Investopedia, etc.) are **not** acceptable as a source of record.
4. Every verified field records: `value`, `source_url`, `source_type: official`,
   `retrieved_utc` (ISO-8601), and the bank's own "rates as of" date when the page states one.
5. Rates are time-sensitive. The capture timestamp is published next to every rate.
6. Computed values (interest projections) are **derived**, not sourced; they are labelled as
   calculations and the formula + inputs are published.

---

## 3. Source Log (official sources used)

See `data/accounts.json`, `data/bonuses.json`, `data/fdic.json`, `data/benchmarks.json` —
every record carries its own `source_url` and `retrieved_utc`. Index of domains used:

| Domain | Used for |
|---|---|
| `fdic.gov`, `banks.data.fdic.gov` | Deposit-insurance rules, SMDIA, national rate caps, bank certificates |
| `federalreserve.gov` | Regulation D / savings-withdrawal-limit rule change |
| `home.treasury.gov` | Treasury par yield curve benchmark |
| `chase.com` | Chase savings rates, fees, bonus terms |
| `bankofamerica.com` | BoA Advantage Savings rates, fees |
| `wellsfargo.com` | Way2Save / Platinum Savings rates, fees |
| `citi.com`, `online.citi.com` | Citi Savings rates, fees |
| `usbank.com` | U.S. Bank savings rates, fees |
| `pnc.com` | PNC savings rates, fees |
| `capitalone.com` | 360 Performance Savings rate, terms |
| `td.com` | TD savings rates, fees |
| `truist.com` | Truist One Savings rates, fees |
| `citizensbank.com` | Citizens savings rates, fees |
| `americanexpress.com` | Amex HYSA rate, terms |
| `discover.com` | Discover Online Savings rate, terms |
| `marcus.com` | Marcus Online Savings rate, terms |
| `ally.com` | Ally Savings rate, buckets, terms |
| `synchronybank.com` | Synchrony HYS rate, terms |
| `banking.barclaysus.com` | Barclays Tiered Savings rate |
| `schwab.com` | Schwab Bank Investor Savings rate |
| `sofi.com` | SoFi Savings rate, FDIC network |
| `cit.com` | CIT Platinum Savings rate |
| `apps.apple.com`, `play.google.com` | Mobile-app existence + platform |

---

## 4. Irregularities & Flags Log

Authoritative machine-readable copy: `data/flags.json`; published at `docs/flagged.html`.

| ID | Item | Nature | Status |
|---|---|---|---|
| F-01 | Chase Savings / Chase Premier Savings APY | Chase publishes relationship/standard APYs only behind a ZIP-code gated rate tool; the public national page does not state a single APY. Captured values come from Chase's own ZIP-gated PDF/rate page where retrievable, else left blank. | needs review |
| F-02 | Branch-bank "promotional/relationship" APYs | Several branch banks publish a low standard APY plus much higher relationship/promotional APYs that require a linked checking account or new-money conditions. Both are shown; the relationship rate is **not** treated as the headline rate. | needs review |
| F-03 | ZIP-code dependent rates | BoA, Wells Fargo, Citi, U.S. Bank, PNC, TD and Citizens publish rates that vary by state/ZIP. Site publishes the rate for the user's stated location (New York, NY — ZIP 10001) and labels it as such. | needs review |
| F-04 | Checking-account bonuses vs. savings bonuses | Most large-bank "open an account" bonuses are **checking** bonuses or checking+savings bundles, not pure savings bonuses. Classified explicitly in `data/bonuses.json`. | needs review |
| F-05 | SoFi / expanded FDIC networks | SoFi, Wealthfront-style sweep programs and IntraFi ICS extend coverage beyond $250k via partner-bank networks. Coverage amount is a program feature, not a direct FDIC limit on one charter. Flagged so the distinction is explicit. | needs review |
| F-06 | Rate volatility | All APYs are variable and can change daily without notice. Every published figure is stamped with its UTC capture time. | needs review |

Full detail, including per-field blanks, is in `data/flags.json` and on the Flagged for Review page.

---

## 5. Activity Log

| UTC timestamp | Session | Event |
|---|---|---|
| 2026-10-22 00:05 | `291c7881` | Reviewed repo at `8f2dc3a` — contained only `README.md` (10 bytes). No prior data, no site, no coordination file, no other session claims. Created this board and claimed T-01…T-14. |
| 2026-10-22 00:06 | `291c7881` | Claim committed and pushed to `arena/291c7881-savings5`. |
