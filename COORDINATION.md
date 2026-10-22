# COORDINATION — Shared Task Board

**Repo:** `sassnarep3-star/SAVINGS5`
**Last updated:** 2026-10-22 (UTC)
**Coordinating session:** `a67a75fe`
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
| Final copy fix | PR #8 (stale Truist sentence on Sources) — merged; its own merge commit is not separately tracked |

### Open requests to other sessions

_None._ No other session is active on this repository.
