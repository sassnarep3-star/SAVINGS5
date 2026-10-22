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
| T-14 | PR → main, merge, confirm Pages deploy, record result | in progress | `291c7881` | `COORDINATION.md` |

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

Every record in `data/*.json` carries its own `source_url` and `retrieved_utc`; the complete,
de-duplicated list of **64 source URLs across 24 domains**
is published at `docs/sources.html`. Domain index:

| Domain | Used for |
|---|---|
| `api.fdic.gov` | Discover Bank rates & terms |
| `apps.apple.com` | Bank of America mobile app; PNC Bank mobile app |
| `banking.us.barclays` | Barclays (US Consumer Bank) mobile app; Barclays (US Consumer Bank) rates & terms; Barclays (US Consumer Bank) security statements |
| `banks.data.fdic.gov` | Barclays (US Consumer Bank) security statements; FDIC certificate / charter status |
| `edie.fdic.gov` | Deposit-insurance rules |
| `media.bac-assets.com` | Bank of America rates & terms |
| `play.google.com` | Bank of America mobile app; PNC Bank mobile app |
| `www.ally.com` | Ally Bank mobile app; Ally Bank rates & terms; Ally Bank security statements |
| `www.americanexpress.com` | American Express mobile app; American Express rates & terms; American Express security statements |
| `www.bankofamerica.com` | Bank of America rates & terms (secondary); Bank of America security statements |
| `www.capitalone.com` | Capital One mobile app; Capital One rates & terms; Capital One rates & terms (secondary) |
| `www.chase.com` | Chase mobile app; Chase rates & terms; Chase security statements |
| `www.cit.com` | CIT Bank mobile app; CIT Bank rates & terms |
| `www.citi.com` | Citi mobile app; Citi rates & terms |
| `www.citizensbank.com` | Citizens mobile app; Citizens offer terms; Citizens rates & terms |
| `www.fdic.gov` | Deposit-insurance rules; National rates & rate caps |
| `www.marcus.com` | Marcus by Goldman Sachs mobile app; Marcus by Goldman Sachs offer terms; Marcus by Goldman Sachs rates & terms |
| `www.pnc.com` | PNC Bank rates & terms; PNC Bank security statements |
| `www.sofi.com` | SoFi mobile app; SoFi offer terms; SoFi rates & terms |
| `www.synchrony.com` | Synchrony Bank mobile app; Synchrony Bank rates & terms; Synchrony Bank security statements |
| `www.td.com` | TD Bank mobile app; TD Bank rates & terms |
| `www.truist.com` | Truist mobile app; Truist rates & terms |
| `www.usbank.com` | U.S. Bank mobile app; U.S. Bank rates & terms; U.S. Bank security statements |
| `www.wellsfargo.com` | Wells Fargo mobile app; Wells Fargo offer terms; Wells Fargo rates & terms |

**Corrections made during verification** (legacy hostnames and dead paths found in the original plan):

| Planned source | Actual source of record | Reason |
|---|---|---|
| `synchronybank.com` | `synchrony.com/banking/products/hys-core` | Legacy hostname redirects |
| `banking.barclaysus.com` | `banking.us.barclays` | Legacy hostname redirects |
| `discover.com` | — (dropped) | Redirects to Capital One; FDIC BankFind shows Discover Bank cert 5649 inactive 2025-05-18 (F-02) |
| `schwab.com` | — (dropped) | Savings APY never obtained from an official page; excluded rather than guessed |
| `citi.com` / `online.citi.com` | — (no value captured) | Every official rates URL returned an empty JS shell or a 404 (F-01) |
| `chase.com` HTML rates page | `chase.com/.../ratesheets/pdfs/rdny1.pdf` | HTML page is ZIP-gated; the state rate sheet is the authoritative public document |
| `bankofamerica.com` HTML page | `media.bac-assets.com/DigitalDeposit_VA_VA_Excluding_DC.pdf` | HTML page renders `$XXXX` placeholders until a ZIP is supplied (F-06) |
| `federalreserve.gov`, `home.treasury.gov` | — (not needed) | Treasury yields used for the rate caps are republished inside the FDIC table itself |

---

## 4. Irregularities & Flags Log

Authoritative machine-readable copy: `data/flags.json`. Published at `docs/flagged.html`
(linked from every page of the site). **20 items: 4 high, 8 medium, 8 low.**
None of these block the merge; all are published with the official link needed to resolve them.

| ID | Severity | Institution | Finding | Resolution applied |
|---|---|---|---|---|
| F-01 | high | Citibank, N.A. (FDIC cert 7213) | Citi publishes no readable savings APY | All Citi values left blank and marked unverified. No Citi number is published anywhere on this site. |
| F-02 | high | Discover Bank (FDIC cert 5649) | Discover Bank is no longer an active FDIC-insured institution | Discover is listed with status 'inactive' and no rate figures. Capital One's note that Capital One and Discover Bank deposit accounts opened on or after 18 May 2025 are aggregated for FDIC coverage is published on the FDIC page. |
| F-03 | high | TD Bank, N.A. (FDIC cert 18409) | TD Bank savings APYs did not render | Both TD APYs left blank and marked unverified. TD's fee and minimum-deposit terms, which did render, are published. |
| F-04 | high | Citizens Bank, N.A. (FDIC cert 57957) | Citizens savings APY table rendered as unresolved template tokens | All Citizens APYs left blank and marked unverified. Verified Citizens terms (no minimum deposit, $4.99 fee with waivers, no transaction limits, 15-state availability) are published. |
| F-05 | medium | PNC Bank, N.A. (FDIC cert 6384) | PNC High Yield Savings is not available in the capture location | 3.15% is published, attributed explicitly to PNC's own page title, and tagged as geographically restricted. Minimum deposit and fees are left blank and marked unverified. |
| F-06 | medium | Bank of America, N.A. (FDIC cert 3510) | Bank of America rate sheet is for Virginia, not New York | The 0.04% APY is published with its location stated on the row. Monthly fee and minimum balance left blank and marked unverified. |
| F-07 | medium | Wells Fargo Bank, N.A. (FDIC cert 3511) | Wells Fargo rates shown are for ZIP 94105, not New York | The rates are published with 'CA 94105' stated on the row and no as-of date claimed. |
| F-08 | medium | U.S. Bank, N.A. (FDIC cert 6548) | U.S. Bank rates shown are for ZIP 55402 and may not apply to existing clients | Rates published with location and the relationship requirement stated on the row. The standard (no-relationship) 0.05% APY is published alongside the 3.50% headline so the two are never confused. |
| F-09 | medium | Synchrony Bank (FDIC cert 27314) | Synchrony's own savings calculator shows a different APY from its headline | 3.55% is published as the APY because it is the figure Synchrony states twice with a dated APY disclosure. The calculator discrepancy is flagged rather than averaged or ignored. |
| F-10 | low | Goldman Sachs Bank USA (FDIC cert 33124) | Marcus cites a 0.40% national average; the FDIC table for the same date says 0.38% | This site uses the FDIC figure (0.38%) for every benchmark comparison. Marcus's own APY of 3.50% is unaffected and is published as stated. |
| F-11 | low | SoFi Bank, N.A. (FDIC cert 26881) | SoFi's competitor comparison table is out of date versus the banks' own current rates | No competitor figure from SoFi's table is used anywhere on this site. Every bank's rate comes from that bank's own source. |
| F-12 | low | Capital One, N.A. (FDIC cert 4297) | Capital One's APY is only readable from the disclosure page, and the two pages carry different dates | 3.20% APY / 3.1540% interest rate are published, sourced to the disclosure page, with the product page's 10/21/2026 effective date recorded alongside and both URLs cited. |
| F-13 | low | CIT Bank, Barclays, Marcus by Goldman Sachs, Wells Fargo, Truist, Citi | Mobile app not confirmed from an official source for six institutions | App field left blank and marked unverified for those six. No app claim is published for them. |
| F-14 | low | CIT Bank, Marcus by Goldman Sachs, Chase | Three fee and cap figures were not published by their institutions | All three left blank and marked unverified. |
| F-15 | medium | SoFi Bank, N.A. | Expanded FDIC coverage through partner-bank networks is a program feature, not a higher FDIC limit | SoFi's $3M figure is published with this distinction stated on the row and explained on the FDIC page. |
| F-16 | medium | All institutions | Every savings APY on this site is variable and can change without notice | Every published rate carries the institution's own stated effective date plus this site's UTC capture timestamp. All return projections are explicitly labelled as holding the APY constant, which will not happen in practice. |
| F-17 | medium | U.S. Bank, Wells Fargo, Chase | Headline rates at three big banks require a relationship or new-money condition | Both the conditional rate and the standard rate are published for each of these products, and a 'Conditions' column marks which rates are conditional. |
| F-18 | low | Barclays, Bank of America, Marcus | Balance caps limit how much you can actually place at the top rate | Caps are published on the account rows and factored into the FDIC deployment plan. |
| F-19 | low | SoFi, Wells Fargo, Marcus, Citizens | Several offers have no published expiry or payout timing | Those fields are left blank and marked unverified; the offers are still listed with the rules that did render. |
| F-20 | low | Session 291c7881 | Coordination: this session is pinned to a fixed branch name | Recorded in COORDINATION.md. The intent of the rule — one exclusive branch per session, no cross-session edits — is preserved: session 291c7881 owns arena/291c7881-savings5 exclusively and touched no other branch. |

The earlier provisional flag list (F-01…F-06, written at claim time before verification began)
has been replaced by this verified list. Two provisional entries proved to be non-issues:
Chase's rates *are* publicly retrievable from its state rate sheets, and Regulation D's
six-withdrawal limit is no longer imposed by most of these institutions — the actual
per-institution withdrawal terms are published on `docs/rules.html`.

---

## 5. Activity Log

| UTC timestamp | Session | Event |
|---|---|---|
| 2026-10-22 00:05 | `291c7881` | Reviewed repo at `8f2dc3a` — contained only `README.md` (10 bytes). No prior data, no site, no coordination file, no other session claims. Created this board and claimed T-01…T-14. |
| 2026-10-22 00:06 | `291c7881` | Claim committed and pushed to `arena/291c7881-savings5` (commit `2c7eee5`). |
| 2026-10-22 00:10–01:40 | `291c7881` | **T-03…T-08 verification.** ~50 official-page retrievals against bank domains, `fdic.gov` and the FDIC BankFind API. Captured 18 institutions / 23 products. Every FDIC certificate number read from BankFind, not from the bank's own claim. Citi, TD and Citizens APYs could not be rendered from any official URL and were left blank (F-01, F-03, F-04). Charles Schwab Bank was dropped for the same reason rather than estimated. |
| 2026-10-22 01:45 | `291c7881` | Wrote `data/SCHEMA.md`, `data/benchmarks.json`, `data/fdic.json`, `data/accounts.json`, `data/bonuses.json`, `data/flags.json`; committed and pushed. |
| 2026-10-22 01:55 | `291c7881` | **T-09/T-10.** Added `data/returns_model.json` (machine-readable restatement of each captured tier table) and `scripts/build.py`. 756 return rows generated into `data/returns.json`. |
| 2026-10-22 02:00 | `291c7881` | **T-11/T-12.** Generated the 12-page site into `docs/`. Four build-time guards added and passing: modelled APY ⊆ captured tier table; `unverified` ⇒ `value: null`; every product has a source URL; every internal link resolves (512 checked). |
| 2026-10-22 02:05 | `291c7881` | **T-13 integration check.** All 12 pages served and fetched at HTTP 200; no empty table cells; no placeholder or `NaN` leakage; JSON re-validated. Source index rebuilt in section 3 above from the data itself. Provisional flags F-01…F-06 replaced with the verified list of 20. |
