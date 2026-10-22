# COORDINATION — Shared Task Board

**Repo:** `sassnarep3-star/SAVINGS5`
**Last updated:** 2026-10-22 (UTC)
**Coordinating session:** `a67a75fe`
**Session working branch:** `arena/a67a75fe-savings5` (assigned by the Arena harness; this session may only commit/push to this branch)

## Coordination Rules In Force

1. Read this file before starting any task.
2. Claim a task by adding your session ID + file scope, then commit and push the claim **immediately**.
3. Never start a task another live session has claimed. A claim older than 60 minutes with no commits may be taken over — note the handoff.
4. Keep scopes non-overlapping. If you need to change a file owned by another session, log a request here instead of editing it.
5. Small, frequent commits. `git pull --rebase` before every push. Never drop another session's work to resolve a conflict.
6. Never mark anything "verified" without an official source link and the date it was checked.
7. Shared outputs (`data/*.json`, `index.html`, nav) are integration-session only.

## Task Board

| ID | Task | Status | Owner | File scope |
|----|------|--------|-------|------------|
| T1 | Coordination board + repo scaffold | done | a67a75fe | `COORDINATION.md`, `README.md`, `.gitignore` |
| T2 | Verify FDIC insurance framework (limits, ownership categories, APY/insurance lookup method) | done | a67a75fe | `research/fdic-notes.md` |
| T3 | Verify national-bank universe (which banks qualify as big national banks) | done | a67a75fe | `research/bank-universe.md` |
| T4 | Verify APY + minimums + fees + account rules, official bank pages | done | a67a75fe | `data/accounts.json`, `research/accounts-notes.md` |
| T5 | Verify account-opening bonuses/promotions, official promo terms | done | a67a75fe | `data/bonuses.json`, `research/bonuses-notes.md` |
| T6 | Return-on-deposit model (compounding, FDIC stacking) + date-anchored projections | done | a67a75fe | `data/returns.json`, `tools/build_returns.py` |
| T7 | Site build (landing page + category subpages) | done | a67a75fe | `index.html`, `assets/`, `*.html` |
| T8 | Link/consistency check + build verification | done | a67a75fe | `tools/check_site.py` |
| T9 | Publish to GitHub Pages | done | a67a75fe | `.github/workflows/pages.yml` |
| T10 | PR to `main`, merge, deploy confirmation | done | a67a75fe | `COORDINATION.md` |

### Session log

#### a67a75fe — 2026-10-22
- Claimed T1–T10. No other sessions present at claim time (repo had one initial commit, no COORDINATION.md, no open PRs).
- Scope: all files listed above. No overlapping sessions to coordinate with at start.
- Note: harness pins this session to `arena/a67a75fe-savings5`; per-session feature branches (`session-<id>/<task>`) are therefore folded into this one branch. Recorded here so a later session does not treat the branch name as a conflict.
- Methodology: every data point is taken from an official bank/government page fetched on 2026-10-22 and the exact URL is stored in the record. Anything not confirmable from an official page is stored as `null` and listed on the **Flagged for Review** page. No value is inferred, averaged, or carried over from memory.

### Open requests to other sessions

_None._
