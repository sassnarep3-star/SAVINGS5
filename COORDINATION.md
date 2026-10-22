# COORDINATION — Shared Task Board

**Repo:** `sassnarep3-star/SAVINGS5`
**Last updated:** 2026-10-22 (UTC)
**Coordinating session:** `a67a75fe` (T1–T10) · `291c7881` (T11–T13, integration)
**Session branch:** `arena/a67a75fe-savings5` (assigned by the Arena harness; this session may only commit/push to this branch)
**Live site:** https://sassnarep3-star.github.io/SAVINGS5/

## Coordination rules in force

1. Read this file before starting any task.
2. Claim a task by adding your session ID + file scope, then commit and push the claim **immediately**.
3. Never start a task another live session has claimed. A claim older than 60 minutes with no commits may be taken over — note the handoff.
4. Keep scopes non-overlapping. If you need to change a file owned by another session, log a request here instead of editing it.
5. Small, frequent commits. `git pull --rebase` before every push. Never drop another session's work to resolve a conflict.
6. Never mark anything "verified" without an official source link and the date it was checked.
7. Shared outputs (`data/*.json`, `index.html`, nav) are integration-session only.

## Task board

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|------------|
| T1 | Coordination board + repo scaffold | done | a67a75fe | `COORDINATION.md`, `README.md`, `.gitignore`, `.nojekyll` |
| T2 | Verify FDIC insurance framework (limits, ownership categories, covered products) | done | a67a75fe | `data/fdic.json` |
| T3 | Verify bank universe from FDIC BankFind (16 institutions, certificates, assets, charter class) | done | a67a75fe | `data/institutions.json`, `research/verification-log.md` |
| T4 | Verify APY, minimums, fees, waivers and opening rules, official bank pages | done | a67a75fe | `data/accounts.json` |
| T5 | Verify bonuses/promotions and log banks with none published | done | a67a75fe | `data/bonuses.json` |
| T6 | Return model (8 deposit sizes x 4 terms), FDIC ladder plans, coverage arithmetic | done | a67a75fe | `data/returns.json`, `tools/build_returns.py` |
| T7 | Site build: landing page + 9 category subpages | done | a67a75fe | `index.html`, `accounts.html`, `returns.html`, `bonuses.html`, `rules.html`, `security.html`, `competitiveness.html`, `flagged.html`, `sources.html`, `methodology.html`, `assets/style.css`, `tools/build_site.py` |
| T8 | Build gate: sources on every table row, internal links, unresolved tokens | done | a67a75fe | `tools/check_site.py` |
| T9 | Publish to GitHub Pages | done | a67a75fe | repo root (Pages source: `main` / root, legacy build) |
| T10 | PR to `main`, merge, deploy verification | done | a67a75fe | `COORDINATION.md` |
| T11 | Supplemental official-source rate, account and offer refresh | done | `arena/3a8e8ff0-savings5` | `data/research.json`, `data/standard-projections.csv`, `data/promotion-projections.csv`, new `research/` files |
| T12 | Integrate the supplemental refresh into the already-deployed dashboard | done — PR #11 merged; Pages built | `arena/3a8e8ff0-savings5` | `index.html`, `rates-refresh.html`, `flagged.html`, `sources.html`, `README.md`, `tools/build_site.py`, `tools/check_site.py`, `COORDINATION.md`; preserve all existing research/site pages and data |
| T13 | Independent second verification of every published rate | done | 291c7881 | `data/session-291c7881/**` |
| T14 | Integrate the institutions missing from the study (CIT, Barclays, Citizens) | done | 291c7881 | `data/institutions.json`, `data/accounts.json`, `data/bonuses.json` |
| T15 | Re-run return model, ladder pools and site copy against the enlarged dataset | done | 291c7881 | `tools/build_returns.py`, `tools/build_site.py` |

### Session log

#### a67a75fe — 2026-10-22

**Claim.** Repo had one initial commit and no `COORDINATION.md`; no other sessions or branches were present. Claimed T1–T10
immediately and pushed the claim before starting work. The harness pins this session to `arena/a67a75fe-savings5`, so
per-session branches (`session-<id>/<task>`) are folded into this one branch — recorded so a later session does not read the
branch name as a conflict.

**What was built.**

- 16 FDIC-insured institutions, 17 savings accounts, 21 tables, 252 table rows, every row carrying an official source link.
- 11 accounts with a verified numeric APY; 6 accounts deliberately excluded from every projection because no official numeric
  APY could be read (Chase, Bank of America, Citibank, TD Bank, Fifth Third, PNC).
- 5 documented promotions (Chase savings bonus, SoFi bonus + APY boost, Marcus referral, Wells Fargo new-customer rate,
  U.S. Bank relationship rate) and 13 banks logged as "no savings bonus published on the account page checked".
- Return model at 8 deposit sizes ($10k–$2.5M) and 4 terms (1/2/3/5 years), with a constant-rate scenario and a stress-case
  scenario, plus FDIC ladder plans for $250k–$5M.
- Static site of 10 pages, plain HTML/CSS, no JavaScript, no external assets.

**Verification performed.**

- Every institution checked individually in the FDIC BankFind institutions API: `ACTIVE`, `INSFDIC`, `BKCLASS`, `ASSET`,
  `DEPDOM`, `CERT`.
- Every rate transcribed from the bank's own page with the bank's own effective date. ZIP-gated, empty or placeholder rates
  left blank.
- `tools/check_site.py` run before each publish. Final run:

```
pages checked        : 10
tables checked       : 21
table rows checked   : 252
data files validated : 5
OK - every table row has a source link, every internal link resolves, no unresolved tokens.
```

- All internal links resolved on the deployed site; `index.html`, `returns.html` and `flagged.html` were also fetched live
  from GitHub Pages after deployment and inspected.

**Sources.** FDIC BankFind institutions API (index `institutions_20261016090006`); FDIC *Are My Deposit Accounts Insured by
the FDIC?*; FDIC *Understanding Deposit Insurance*; FDIC *National Rates and Rate Caps — October 2026* (as of 2026-10-19);
and the banks' own product, rate, fee-schedule and disclosure pages, all fetched 2026-10-22. The complete list with retrieval
dates is on the site's Sources page and in `research/verification-log.md`.

**Irregularities flagged (published on the Flagged for review page, non-blocking).**

1. Bank of America's product page renders its fee block as literal `$XXXX`; fee data taken from the Personal Schedule of Fees PDF instead.
2. Capital One's product page renders its APY as `NaN`; the 3.20% rate comes from Capital One's own category page.
3. Citibank renders the savings APY as the unresolved token `:BLUE_AccSavings_Rate%`; APY left blank.
4. PNC High Yield Savings returned "This Product Isn't Available in Your Area"; its 3.15% page-title rate is not asserted.
5. Bank of America's New York rate sheet (`DigitalDeposit_NY*.pdf`) could not be retrieved; the Virginia/non-branch sheet shows
   0.04% APY and is documented but not used for New York.
6. Discover Bank (CERT 5649) is `ACTIVE = 0` in FDIC data; treated as part of Capital One, per Capital One's own FDIC pooling note.
7. Marcus, American Express and Fifth Third do not name a mobile app on their savings pages — marked "not confirmed", not assumed.
8. Security controls were not audited; FDIC status and app existence are verified, no security ranking is made.
9. Wells Fargo, U.S. Bank and PNC rates were read from the location each site served (CA 94105, ZIP 55402, ZIP 15222) and may
   differ in New York; disclosed on the flagged page.

**Publish record (T10).**

| Item | Value |
|---|---|
| PR | https://github.com/sassnarep3-star/SAVINGS5/pull/1 |
| PR state | MERGED (merge commit `012e522131a4b8507b044f5eb4894a2b6adf33f6`) |
| Merged at | 2026-10-22T00:13:15Z |
| Pages build | `built`, commit `012e522`, created 2026-10-22T00:13:17Z, completed 2026-10-22T00:13:35Z, no error |
| Pages status | `built`, source `main` / root, HTTPS enforced |
| Live URL | https://sassnarep3-star.github.io/SAVINGS5/ |

Three defects were found after the first deploy and corrected in follow-up commits. This is why the site was re-checked
against the rendered page rather than only against its source data.

1. The flagged page listed Charles Schwab as having an unconfirmed app because the check matched the substring "app" inside
   the flag "Application is mail/phone/branch only". The check now reads the structured app verdict.
2. The stress-case return column could show a *higher* five-year balance than the constant-rate case for accounts paying below
   the FDIC national average (Truist and Way2Save showed $253,847 against $250,125). The stress case now uses the lower of the
   account's own APY and the national average, so it can only reduce a balance.
3. The FDIC ladder builder cycled through its pool to reach the number of banks required, so at $2.5M and $5M it placed a
   second $250,000 with institutions already used. That overstates insured coverage and contradicts the "at most $250,000 per
   bank" claim printed under the table. It also counted Wells Fargo Way2Save and Platinum as two banks and two slots when they
   share FDIC certificate 3511. The builder now takes one account per certificate, allocates at most $250,000 per institution,
   and reports the uninsured remainder explicitly. Corrected results: $2.5M is **not** fully coverable with this dataset — the
   no-conditions pool covers $2,000,000 (8 banks, $500,000 uninsured) and the max-rate pool covers $2,250,000 (9 banks,
   $250,000 uninsured); at $5M the shortfalls are $3,000,000 and $2,750,000.

**Follow-up PR.** This record is published to `main` through a second PR (see the table below), because `COORDINATION.md` can
only be updated after the merge result is known.

| Item | Value |
|---|---|
| Follow-up PR | https://github.com/sassnarep3-star/SAVINGS5/pull/2 (deploy fixes) — merged |
| Ladder fix | https://github.com/sassnarep3-star/SAVINGS5/pull/3 (FDIC coverage overstatement) — merged |
| Copy fix | https://github.com/sassnarep3-star/SAVINGS5/pull/4 (ladder intro) — merged |
| QA PR | https://github.com/sassnarep3-star/SAVINGS5/pull/5 (fee column, not-stated cells, bank count, FDIC table dedupe) — merged, commit `61503c6` |
| Record sync | https://github.com/sassnarep3-star/SAVINGS5/pull/6 (coordination record) — merged |
| KPI fix | https://github.com/sassnarep3-star/SAVINGS5/pull/7 (institution count on Methodology) — merged |
| Final copy fixes | PR #8 (stale Truist sentence on Sources), PR #9 (blank-cell count on the landing page) — merged; their own merge commits are not separately tracked |

#### 291c7881 — 2026-10-22 (integration)

**Collision, and how it was resolved.** Sessions `a67a75fe` and `291c7881` both started from commit `8f2dc3a`, when the repo
held only `README.md` and no coordination board, so each created a board and claimed the whole task list. Neither could see
the other's claim. `a67a75fe` reached `main` first and published the live site; `291c7881` had independently researched and
built a parallel dataset and site on `arena/291c7881-savings5`.

**Nothing of `a67a75fe`'s work was discarded.** `main` was merged into `arena/291c7881-savings5`, the published site, its
`tools/`, its `research/` log and all four of its `data/*.json` files were kept as the authoritative versions, and the
duplicate site built by `291c7881` was withdrawn rather than published alongside. The independent capture is retained in
`data/session-291c7881/` purely as evidence for the cross-check below. The two conflicting files (`README.md`,
`COORDINATION.md`) were resolved in favour of `a67a75fe`'s versions, with this section appended.

**Independent cross-check.** Every rate the two sessions verified separately, from separate retrievals of the same official
pages, agreed exactly:

| Account | `a67a75fe` | `291c7881` | Result |
|---|---|---|---|
| Wells Fargo Way2Save | 0.01% | 0.01% | agree |
| Truist One Savings | 0.01% | 0.01% | agree |
| Capital One 360 Performance Savings | 3.20% | 3.20% | agree |
| Marcus Online Savings | 3.50% | 3.50% | agree |
| American Express HYSA | 3.20% | 3.20% | agree |
| Ally Savings | 3.10% | 3.10% | agree |
| Synchrony High Yield Savings | 3.55% | 3.55% | agree |
| SoFi Savings | 3.30% | 3.30% | agree |
| Citi, TD | blank | blank | agree — both sessions failed to render an official APY |

**What the integration added.** Three FDIC-insured institutions that the study had missed, all re-pulled from the same
BankFind index (`institutions_20261016090006`) the original rows came from:

| Added | Cert | Why it mattered |
|---|---|---|
| CIT Bank (First-Citizens Bank & Trust) | 11063 | Platinum Savings pays **3.75%** at $5,000+ — the highest ongoing rate in the study. Savings Connect pays 3.65% with no balance condition. |
| Barclays Bank Delaware | 57203 | Tiered Savings pays 3.50%, rising to **3.65%** from $250,000, and carries the only pure **$200 cash bonus on a savings account** found on an official page. |
| Citizens Bank, N.A. | 57957 | 19th-largest US bank. APY left **blank** — its page prints unresolved template tokens and reports the product unavailable in the capture location. |

Before this merge the site's best published rate was Synchrony at 3.55%; the two best savings accounts in the market were
absent. Knock-on corrections, all re-derived rather than hand-edited:

1. **FDIC ladder.** `tools/build_returns.py` selected ladder banks from a hardcoded allowlist of account IDs, so the new
   institutions could never be chosen. CIT Savings Connect and Barclays were added to the no-conditions pool and CIT Platinum
   to the max-rate pool. A `balance_tier_ids` set was introduced: where an account's only published condition is a balance
   threshold, a $250,000 FDIC slot satisfies it by construction, unlike a relationship or direct-deposit condition. **$2,500,000
   is now fully coverable** (10 banks, blended 3.40% max-rate / 2.73% no-conditions); the previous record that it was not is
   superseded. Blended rates improved at every rung: $250k 3.55%→3.75%, $1M 3.4625%→3.6125%.
2. **Landing-page copy.** The best/worst spread finding was hardcoded to "Synchrony pays 3.55%" and is now derived from the
   data (CIT 3.75% vs Wells Fargo 0.01%, a 374bp gap). The institution count in the lede was hardcoded to "sixteen" and is now
   computed. Citizens was added to the list of banks that publish no readable APY.
3. **Pre-existing defect fixed.** On `competitiveness.html` the sentence "the gap between the best and worst *savings* account
   is about N basis points" was printing `best − national average` (337bp), not best − worst (374bp). The words and the
   arithmetic disagreed. Both figures are now computed and both are stated.

**Verification standard held.** No value was carried across from `291c7881`'s dataset without its own official source link, and
no blank was filled in. Citizens' APY stays blank. The three mobile-app claims that could not be confirmed on an official page
(CIT, Barclays) are recorded as "not stated" and appear on the Flagged for Review page.

**Gate.** `tools/check_site.py` passes: 10 pages, 21 tables, **296 table rows** (was 252), 5 data files, every table row has a
source link, every internal link resolves, no unresolved tokens.

| Item | Value |
|---|---|
| Integration PR | https://github.com/sassnarep3-star/SAVINGS5/pull/10 — **MERGED**, merge commit `670e59ade4f748fe7eb1593599b19760ef75165a` |
| Pages build | `built`, commit `670e59a`, 2026-10-22T00:36:28Z, no error |
| Live URL | https://sassnarep3-star.github.io/SAVINGS5/ — verified serving CIT Bank 3.75% as highest ongoing APY |
| Follow-up PR | see below — last hardcoded leaderboard sentence made data-driven |

### Open requests to other sessions

_No request is pending. T11/T12 are claimed by `arena/3a8e8ff0-savings5`; no other concurrent session is active.

## Follow-up session activity

### `arena/3a8e8ff0-savings5` — T11 official-source refresh

**Claim and handoff.** This session had claimed the official-source refresh in its pre-rebase coordination board before creating the research files. On reconciling with current `main`, T1–T10 were confirmed complete and no concurrent owner was active. The existing published site, FDIC ladder, and earlier account research are preserved; T11 adds distinct research files only.

**File scope:** `data/research.json`, `data/standard-projections.csv`, `data/promotion-projections.csv`, and `research/calculate_projections.py`, `research/validate_research.py`, `research/source-matrix.csv`, `research/research-summary.md`, `research/projection-method.md`.

**Verification/status.** Complete: 57 official source records, 16 products, 8 offers, 9 review flags, 120 rate scenarios, and 84 conditional-offer scenarios. `python research/calculate_projections.py`, `python research/validate_research.py`, JSON parsing, and `git diff --check` pass. Unresolved New York/location-specific APYs and unverified opening-term fields remain blank; stale CIT rate, PNC availability conflict, Capital One extraction discrepancy, FDIC headroom, the historical Marcus limit wording discrepancy resolved by the current 2025 agreement/FAQ, and other caveats are disclosed in the registry and research summary.

### T12 — Integrate the supplemental refresh into the already-deployed dashboard

**Claim.** T1–T10 are complete and no other session is concurrently editing the site. This follow-up is limited to adding a clearly discoverable, source-linked view of T11’s rate and projection refresh to the existing GitHub Pages site. It does not replace the original accounts, FDIC coverage/ladder, bonus, or methodology pages. The previous site task is complete; this is a new, separately claimed follow-up and will retain its own build/link checks.

**File scope:** `index.html`, `flagged.html`, `sources.html`, `README.md`, new `rates-refresh.html`, `tools/build_site.py`, `tools/check_site.py`, and this board. The shared builder will regenerate the existing pages; only `index.html`, `flagged.html`, and `sources.html` should change besides the new page. The previous research, account, bonus, FDIC-ladder, and CSS assets remain untouched.

**Implementation and verification (2026-10-22).** Added the discoverable, source-linked rate/requirements/app-security/FDIC snapshot and 1/3/5-year return tables; surfaced all 9 supplemental flags on `flagged.html` and all 57 source records on `sources.html`. The original broad screen and FDIC ladder remain unchanged. `python research/validate_research.py` passes (57 sources, 16 accounts, 8 offers, 9 flags, 120/84 scenarios); `python3 tools/check_site.py` passes (11 pages, 28 tables, 372 data rows); `git diff --check` passes.

**Publish record (T12).**

| Item | Value |
|---|---|
| PR | https://github.com/sassnarep3-star/SAVINGS5/pull/11 |
| PR state | MERGED; merge commit `34c801fc0dcef181f64eb41ecd0fa8b4395cad81` |
| Merged at | 2026-10-22T00:32:14Z |
| Pages workflow | run `39700284874`, build and deploy jobs completed successfully |
| Pages build | `built`, commit `34c801fc0dcef181f64eb41ecd0fa8b4395cad81`, created 2026-10-22T00:32:16Z, completed 2026-10-22T00:33:15Z, no error |
| Pages status | `built`, source `main` / root, public, HTTPS enforced |
| Live URL | https://sassnarep3-star.github.io/SAVINGS5/ |

The successful run included only non-blocking GitHub runner/action deprecation notices.

### `arena/291c7881-savings5` — T13-T15 integration (recorded after T11/T12)

**Three-way collision.** Sessions `a67a75fe`, `3a8e8ff0` and `291c7881` all began from commit `8f2dc3a`, when the repo held
only `README.md` and no board, so each created a board and claimed a full task list without being able to see the others.
`291c7881` renumbered its rows to T13-T15 on discovering that `3a8e8ff0` had already published T11/T12.

**Nothing from either other session was discarded.** `main` was merged into `arena/291c7881-savings5` twice: once for
`a67a75fe`'s site and once for `3a8e8ff0`'s supplemental refresh. Both sessions' pages, data files, `research/` scripts and
builder changes were kept. The three conflicting generated pages (`index.html`, `flagged.html`, `sources.html`) were resolved
to `main`'s version and then regenerated from the shared builder, so both sessions' builder changes are live. The duplicate
12-page site `291c7881` had built on its own branch was withdrawn rather than published alongside; its independent capture is
retained in `data/session-291c7881/` purely as cross-check evidence.

