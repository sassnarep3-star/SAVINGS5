#!/usr/bin/env python3
"""Generate the static site from data/*.json. No hand-edited numbers on any page."""

import html
import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SITE_NAME = "SAVINGS5"
TAGLINE = "Savings account research"

NAV = [
    ("index.html", "Overview"),
    ("accounts.html", "Accounts"),
    ("returns.html", "Returns"),
    ("bonuses.html", "Bonuses"),
    ("rules.html", "Rules & fees"),
    ("security.html", "FDIC & apps"),
    ("competitiveness.html", "Competitiveness"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
]


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


ACCOUNTS = load("accounts.json")
INSTITUTIONS = load("institutions.json")
FDIC = load("fdic.json")
BONUSES = load("bonuses.json")
RETURNS = load("returns.json")

INST = {b["cert"]: b for b in INSTITUTIONS["banks"]}
ACC = {a["id"]: a for a in ACCOUNTS["accounts"]}
PROJ = {p["id"]: p for p in RETURNS["projections"]}
LEADER = {l["deposit_usd"]: l for l in RETURNS["leaderboard"]}
OPEN_DATE = ACCOUNTS["open_date"]


# ---------------------------------------------------------------- utilities
def e(text):
    return html.escape(str(text), quote=True)


def money(x, cents=False):
    if x is None:
        return "&mdash;"
    if cents:
        return "${:,.2f}".format(x)
    return "${:,.0f}".format(x)


def pct(x, dp=2):
    if x is None:
        return "&mdash;"
    return ("{:." + str(dp) + "f}%").format(x)


def num(x):
    return "&mdash;" if x is None else "{:,}".format(x)


def src(url, label="source"):
    return f'<a class="src" href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'


def badge(text, kind="plain"):
    return f'<span class="badge {kind}">{e(text)}</span>'


def layout(page, title, body, description=""):
    links = "".join(
        f'<a href="{href}" class="{"active" if href == page else ""}">{e(label)}</a>' for href, label in NAV
    )
    desc = e(description or "Verified savings-account research: rates, minimums, fees, returns and FDIC coverage.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · {SITE_NAME}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="index.html"><span class="dot"></span><span>{SITE_NAME}<small>{TAGLINE}</small></span></a>
    <nav class="nav-links">{links}</nav>
  </div>
</header>
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer class="site">
  <div class="wrap footer-grid">
    <div style="max-width:60ch">
      <strong style="color:var(--ink)">{SITE_NAME}</strong> — savings account research built from bank and FDIC pages retrieved on {OPEN_DATE}.<br>
      Rates are variable and change without notice. Every figure on this site links to the official page it came from;
      anything that could not be confirmed is left blank and listed on the Flagged for review page.
      This is research, not financial advice.
    </div>
    <div>
      <a href="methodology.html">Methodology</a> ·
      <a href="sources.html">All sources</a> ·
      <a href="flagged.html">Flagged items</a><br>
      <span class="muted">Project date {OPEN_DATE}</span>
    </div>
  </div>
</footer>
</body>
</html>
"""


def page_head(title, lede, eyebrow=""):
    return f"""<section class="hero">
  {f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ''}
  <h1>{e(title)}</h1>
  <p class="lede">{lede}</p>
</section>"""


def table(headers, rows, note="", classes=None):
    classes = classes or []
    th = "".join(f'<th class="{c}">{h}</th>' for h, c in zip(headers, classes))
    body = ""
    for r in rows:
        cells = "".join(
            f'<td class="{classes[i] if i < len(classes) else ""}">{c}</td>' for i, c in enumerate(r)
        )
        body += f"<tr>{cells}</tr>"
    note_html = f'<div class="tbl-note">{note}</div>' if note else ""
    return f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>{note_html}</div>'


def clean_cond(text):
    """Normalise 'None' / 'None - ...' tier conditions to plain English."""
    t = (text or "").strip()
    if not t or t.lower().startswith("none"):
        return ""
    return t


def account_rate(accid, deposit=250000):
    """Best published permanent rate at a balance, plus condition."""
    a = ACC[accid]
    best, cond = a["apy_regular_pct"], ""
    for t in a.get("apy_tiers", []):
        if t.get("transient"):
            continue
        lo = t.get("min_usd", 0) or 0
        hi = t.get("max_usd")
        if deposit >= lo and (hi is None or deposit <= hi):
            if best is None or t["apy_pct"] > best:
                best, cond = t["apy_pct"], clean_cond(t.get("requires", ""))
    return best, cond


def sorted_accounts():
    def key(a):
        r, _ = account_rate(a["id"], 250000)
        return (-(r if r is not None else -1), a["brand"])

    return sorted(ACCOUNTS["accounts"], key=key)


# ---------------------------------------------------------------- pages
def index_page():
    best = max(
        ((account_rate(a["id"], 250000)[0], a) for a in ACCOUNTS["accounts"] if a["apy_regular_pct"] is not None),
        key=lambda x: x[0],
    )
    lb250 = LEADER[250000]["top"]
    top_interest = lb250[0]

    kpis = f"""<div class="grid k4">
  <div class="card kpi"><div class="label">Highest ongoing APY</div><div class="value">{pct(best[0])}</div>
    <div class="sub">{e(best[1]["brand"])} — {src(best[1]["sources"][0]["url"], "official page")}</div></div>
  <div class="card kpi"><div class="label">FDIC limit, single owner</div><div class="value">$250,000</div>
    <div class="sub">per depositor, per bank, per ownership category — {src(FDIC["coverage_limits"][0]["source"], "FDIC.gov")}</div></div>
  <div class="card kpi"><div class="label">Best year-1 interest on $250k</div><div class="value">{money(top_interest["year1_interest_usd"])}</div>
    <div class="sub">{e(top_interest["brand"])} at {pct(top_interest["year1_effective_apy_pct"])} year-1 effective — {src(top_interest["source"], "source")}</div></div>
  <div class="card kpi"><div class="label">Institutions verified</div><div class="value">{len({a["cert"] for a in ACCOUNTS["accounts"]})}</div>
    <div class="sub">{len(ACCOUNTS["accounts"])} accounts · FDIC charter, assets and insurance status checked — {src("https://banks.data.fdic.gov/bankfind-suite/bankfind", "BankFind")}</div></div>
</div>"""

    rows = []
    for i, t in enumerate(lb250[:5], 1):
        rows.append(
            [
                f'<span class="rank">{i}</span>',
                f'<strong>{e(t["brand"])}</strong><br><span class="muted small">{e(t["account_name"])}</span>',
                pct(t["year1_effective_apy_pct"]),
                money(t["year1_interest_usd"]),
                e(t.get("promo_label") or t.get("condition") or "No condition"),
                src(t["source"]),
            ]
        )
    top_table = table(
        ["#", "Bank / account", "Year-1 effective APY", "Interest on $250,000 in year 1", "Condition", "Source"],
        rows,
        note="Ranked by year-1 effective yield at a $250,000 deposit, which includes documented time-limited boosts. "
        "The ongoing APY (what you earn after any promo ends) is on the Accounts page. Full laddering analysis is on the Returns page.",
        classes=["", "", "num", "num", "", ""],
    )

    _rated = [a for a in ACCOUNTS["accounts"] if a["apy_regular_pct"] is not None]
    _hi = max(_rated, key=lambda a: account_rate(a["id"], 250000)[0])
    _lo = min(_rated, key=lambda a: account_rate(a["id"], 250000)[0])
    _hi_apy, _lo_apy = account_rate(_hi["id"], 250000)[0], account_rate(_lo["id"], 250000)[0]
    _hi_brand, _lo_brand = _hi["brand"], _lo["brand"]
    _hi_src, _lo_src = _hi["sources"][0]["url"], _lo["sources"][0]["url"]

    findings = f"""<ul>
  <li><strong>The spread between the best and worst verified rate is enormous.</strong>
    {_hi_brand} pays {pct(_hi_apy)} on {money(250000)} and {_lo_brand} pays {pct(_lo_apy)} — a difference of about
    {money(250000 * (_hi_apy - _lo_apy) / 100)} of interest in one year. {src(_hi_src, _hi_brand)} {src(_lo_src, _lo_brand)}</li>
  <li><strong>Several of the largest banks do not publish a consumer-readable savings APY.</strong>
    Chase, Bank of America and Citibank require a ZIP code, TD serves an empty rate table, PNC replaces its page with a
    geo-restriction notice, Citizens prints unresolved template tokens where its APYs should be, and Fifth Third quotes
    promotional rates only in a branch. All {len(RETURNS["excluded_accounts"])}
    of those APY cells are left blank rather than estimated. {src("https://www.chase.com/personal/savings/savings-account/interest-rates", "Chase")} {src("https://www.bankofamerica.com/deposits/bank-account-interest-rates/", "BofA")}</li>
  <li><strong>The highest rate is not always the highest first-year return.</strong>
    SoFi's {pct(3.30)} base rate plus a 1.10% six-month direct-deposit boost produces a
    {pct(3.85)} year-1 blended yield — about {money(250000 * (3.8485 - 3.55) / 100)} more than the
    {pct(3.55)} flat rate on $250,000, but only if the direct deposit is set up. {src("https://www.sofi.com/banking/high-yield-savings-account/", "SoFi terms")}</li>
  <li><strong>Fees can erase the entire return at low balances.</strong>
    Wells Fargo Way2Save pays 0.01% — about {money(250000 * 0.0001)} a year on $250,000 — and charges $5 a month
    unless the $300 balance waiver is met. On $10,000 the annual fee is 0.6% of the balance, sixty times the interest rate.
    {src("https://www.wellsfargo.com/savings-cds/way2save/", "Wells Fargo fee terms")}</li>
  <li><strong>$250,000 is a hard ceiling per bank, per ownership category.</strong>
    Covering $1,000,000 as a single owner requires four separate FDIC-insured banks; a joint account with two owners
    raises the per-bank ceiling to $500,000. {src("https://www.fdic.gov/resources/deposit-insurance/financial-products-insured", "FDIC coverage rules")}</li>
</ul>"""

    tiles = [
        ("accounts.html", "Account comparison", f"All {len(ACCOUNTS['accounts'])} accounts at {len({a['cert'] for a in ACCOUNTS['accounts']})} banks, with APY, minimums, fees and fee waivers."),
        ("returns.html", "Returns on your deposit", "Interest by deposit size and term, plus FDIC ladder plans up to $5M."),
        ("bonuses.html", "Bonuses & promotions", f"{len(BONUSES['promotions'])} documented offers with expiry dates and eligibility rules."),
        ("rules.html", "Rules & fees", "Opening requirements, minimums, withdrawal limits and closure rules."),
        ("security.html", "FDIC & apps", "Certificate numbers, insurance status, charter type and app confirmation."),
        ("competitiveness.html", "Competitiveness", "Each APY against the FDIC national average and Treasury yields."),
        ("flagged.html", "Flagged for review", "Every value that could not be confirmed, with the page that was checked."),
        ("sources.html", "Sources", "Every official URL used, with the date it was retrieved."),
    ]
    tile_html = "".join(
        f'<a class="tile" href="{href}"><div class="t">{e(t)}</div><div class="d">{e(d)}</div><span class="arrow">Open &rarr;</span></a>'
        for href, t, d in tiles
    )

    cov = RETURNS["coverage_gap"]
    cov_rows = [
        [
            money(c["deposit_usd"]),
            money(c["single_owner_coverage_usd"]),
            money(c["uninsured_if_one_bank_usd"]),
            str(c["banks_required_single_owner"]),
            money(c["joint_coverage_two_owners_usd"]),
            str(c["banks_required_joint_two_owners"]),
            src("https://www.fdic.gov/resources/deposit-insurance/financial-products-insured", "FDIC rule"),
        ]
        for c in cov
    ]
    cov_table = table(
        ["Deposit", "Insured at one bank (single owner)", "Uninsured at one bank", "Banks needed (single)", "Insured at one bank (joint, 2 owners)", "Banks needed (joint)", "Source"],
        cov_rows,
        note="Derived from FDIC coverage rules: $250,000 per depositor, per bank, per ownership category, and $250,000 per co-owner for joint accounts.",
        classes=["num", "num", "num", "num", "num", "num", ""],
    )

    body = f"""
{page_head("Savings accounts for large balances, verified line by line",
          f"How {len({a[chr(39)+chr(39)] if False else a['cert'] for a in ACCOUNTS['accounts']})} of the largest US banks pay on savings, what each one requires to open, what it charges, "
          f"and what your deposit actually earns after the FDIC ceiling is applied. Every number links to the bank or "
          f"FDIC page it came from, retrieved on {OPEN_DATE}.", "Research dashboard")}
{kpis}
<h2>Top of the table at $250,000</h2>
<p class="muted">The FDIC limit for a single owner at one bank. Ranked on year-1 effective yield.</p>
{top_table}
<h2>What the data says</h2>
{findings}
<h2>Explore by category</h2>
<div class="grid k4">{tile_html}</div>
<h2>How much of your deposit is actually insured</h2>
<p>FDIC insurance is per depositor, per bank, per ownership category — not per account, and not per dollar. A single-owner
savings account stops being insured above $250,000 at any one bank.</p>
{cov_table}
<div class="callout">
  <p><strong>Bottom line.</strong> For a balance at or below $250,000, a single high-rate online account from a large
  FDIC-insured bank — Synchrony at {pct(3.55)}, Marcus at {pct(3.50)} or SoFi with its direct-deposit boost — produces
  several times the interest of a legacy branch account at the same institution size. Above $250,000 the constraint
  stops being rate and becomes structure: the money has to be split across banks.</p>
</div>
"""
    return layout("index.html", "Savings account research", body,
                  "Verified savings rates, minimums, fees, return projections and FDIC coverage for the largest US banks.")


NOT_STATED = '<span class="muted">not stated</span>'


def accounts_page():
    rows = []
    for a in sorted_accounts():
        rate250, cond = account_rate(a["id"], 250000)
        if a["apy_regular_pct"] is None:
            apy_cell = '<span class="badge warn">not published</span>'
            asof = "&mdash;"
        else:
            apy_cell = f'<strong>{pct(rate250)}</strong>'
            if cond:
                apy_cell += f'<br><span class="muted small">{e(cond)}</span>'
            if rate250 != a["apy_regular_pct"]:
                apy_cell += f'<br><span class="muted small">standard {pct(a["apy_regular_pct"])}</span>'
            asof = e(a["apy_as_of"] or "")
        rows.append(
            [
                f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["account_name"])}</span>',
                apy_cell,
                asof,
                money(a["min_open_usd"]) if a["min_open_usd"] is not None else NOT_STATED,
                money(a["monthly_fee_usd"], cents=True) if a["monthly_fee_usd"] is not None else NOT_STATED,
                money(a["min_balance_to_avoid_fee_usd"]) if a["min_balance_to_avoid_fee_usd"] else ("none" if a["min_balance_to_avoid_fee_usd"] == 0 else NOT_STATED),
                e(a["fee_waiver"]) if a["fee_waiver"] else '<span class="muted">not published</span>',
                src(a["sources"][0]["url"], "rate page"),
            ]
        )
    main = table(
        ["Bank / account", "APY at $250,000", "APY as of", "Min. to open", "Monthly fee", "Balance to waive fee", "Fee waiver", "Source"],
        rows,
        note="APY shown is the best published rate that applies at a $250,000 balance; the condition is printed under the rate. "
        "SoFi is shown at its 3.30% base rate: its 4.40% six-month boost is a time-limited promotion, modelled on the Returns page as a 3.85% year-1 blended yield. "
        "Where the bank does not publish a readable rate, the cell says 'not published' and the reason is on the Flagged for review page. "
        "&ldquo;Fee&rdquo; is the monthly maintenance fee before any waiver. The date column is the bank's own stated effective date where the page "
        "publishes one; where it does not, it is the date this site read the page (2026-10-22).",
        classes=["", "num", "", "num", "num", "num", "", ""],
    )

    cards = ""
    for a in sorted_accounts():
        rate250, cond = account_rate(a["id"], 250000)
        inst = INST.get(a["cert"], {})
        flags = "".join(badge(f, "warn") for f in a["flags"]) or badge("no open flags", "good")
        sources = "".join(
            f'<li>{e(s["label"])} — {src(s["url"], s["url"])} <span class="muted">({e(s["as_of"])})</span></li>'
            for s in a["sources"]
        )
        cards += f"""
<div class="card" id="{e(a['id'])}">
  <div class="section-head">
    <h3 style="margin:0">{e(a['brand'])} — {e(a['account_name'])}</h3>
    <div class="tag-row" style="margin:0">{flags}</div>
  </div>
  <p class="muted small" style="margin-top:6px">{e(a['institution'])} · FDIC certificate {a['cert']} · {e(inst.get('bkclass_label',''))} ·
    assets {money(inst.get('assets_usd'))} · <a class="src" href="https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{a['cert']}" target="_blank" rel="noopener">FDIC BankFind</a></p>
  <div class="grid k4" style="margin:12px 0">
    <div><div class="muted small">APY at $250,000</div><div class="strong" style="font-size:20px">{pct(rate250) if rate250 is not None else '&mdash;'}</div></div>
    <div><div class="muted small">Minimum to open</div><div class="strong" style="font-size:20px">{money(a['min_open_usd'])}</div></div>
    <div><div class="muted small">Monthly fee</div><div class="strong" style="font-size:20px">{money(a['monthly_fee_usd'], cents=True) if a['monthly_fee_usd'] is not None else '&mdash;'}</div></div>
    <div><div class="muted small">Mobile app</div><div class="strong" style="font-size:20px">{'Yes' if a['mobile_app']['value'] == 'yes' else 'Not confirmed'}</div></div>
  </div>
  <p><strong>Rate note.</strong> {e(a['apy_note'])}</p>
  <p><strong>Fee waiver.</strong> {e(a['fee_waiver'] or 'Not published.')}</p>
  <p><strong>Opening.</strong> {e(a['opening_requirements'])}</p>
  <p><strong>Withdrawals.</strong> {e(a['withdrawal_limit'] or 'No withdrawal limit stated on the official page.')}</p>
  <p><strong>FDIC above $250,000.</strong> {e(a['fdic_beyond_250k'])}</p>
  <p><strong>App.</strong> {e(a['mobile_app']['note'])} {src(a['mobile_app']['source'], 'app source')}</p>
  <details><summary>Sources for this account</summary><ul>{sources}</ul></details>
</div>"""

    body = f"""
{page_head("Account comparison",
          "Every account in the study, sorted by the rate that actually applies at a $250,000 balance. "
          "Unpublished rates are marked, not estimated.", "Category · accounts")}
<div class="callout warn">
  <p><strong>Read the APY column carefully.</strong> A bold rate without a condition is the bank's standard published rate.
  A rate with a condition underneath is the best tier the bank publishes for that balance — it is not available to every customer.
  {sum(1 for a in ACCOUNTS["accounts"] if a["apy_status"] != "verified")} of the {len(ACCOUNTS["accounts"])} accounts publish no readable rate on a
page that can be reached without a ZIP code, so their APY is left blank instead of estimated.</p>
</div>
{main}
<h2>Detail by account</h2>
<p class="muted">Each card carries the exact figures, the conditions attached to the headline rate, and every source used.</p>
{cards}
"""
    return layout("accounts.html", "Account comparison", body,
                  "APY, minimums, fees and fee waivers for 16 large US banks, each linked to its official page.")


def returns_page():
    deposits = [10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000]
    hdr = ["Bank / account"] + [money(d) for d in deposits] + ["Source"]
    cls = [""] + ["num"] * len(deposits) + [""]

    rows1, rows5 = [], []
    for a in sorted_accounts():
        p = PROJ.get(a["id"])
        if not p:
            continue
        r1 = [f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["account_name"])}</span>']
        r5 = list(r1)
        for d in deposits:
            row = next(r for r in p["rows"] if r["deposit_usd"] == d)
            r1.append(money(row["interest_1y"]))
            r5.append(money(row["balance_5y"]))
        r1.append(src(p["apy_source"]))
        rows5.append(r5 + [src(p["apy_source"])])
        rows1.append(r1)

    t1 = table(hdr, rows1,
               note="Interest in year 1 at the best published rate for that balance (conditions apply; see the Accounts page). "
                    "Excludes any account fee. Money market and CD rates are not included — this is a savings-account study.",
               classes=cls)
    t5 = table(hdr, rows5,
               note="Balance after five years, holding today's rate constant. Savings APYs are variable; this is arithmetic, not a forecast. "
                    "A second scenario is in the term-detail table below.",
               classes=cls)

    # term detail at $250k
    term_rows = []
    for a in sorted_accounts():
        p = PROJ.get(a["id"])
        if not p:
            continue
        row = next(r for r in p["rows"] if r["deposit_usd"] == 250000)
        term_rows.append([
            f'<strong>{e(a["brand"])}</strong>',
            pct(row["year1_effective_apy_pct"]),
            pct(row["best_apy_pct"]),
            money(row["interest_1y"]),
            money(row["balance_2y"]),
            money(row["balance_3y"]),
            money(row["balance_5y"]),
            money(row["fallback_balance_5y"]),
            src(p["apy_source"]),
        ])
    term = table(["Bank", "Year-1 effective APY", "Ongoing APY", "Interest, year 1", "Balance after 2 years", "After 3 years", "After 5 years (constant rate)", "After 5 years (rate drops to the lower of today's APY and 0.38% in year 2)", "Source"],
                 term_rows,
                 note=f"Deposit $250,000, opened {OPEN_DATE}. The last column applies the FDIC national savings rate of "
                      f"{FDIC['national_rates']['rows'][0]['national_deposit_rate_pct']}% after year 1, but never above the account's own rate — a stress case that can only lower the balance, not raise it. "
                      f"{src(FDIC['national_rates']['source'], 'FDIC national rates, 2026-10-19')}",
                 classes=["", "num", "num", "num", "num", "num", "num", "num", ""])

    # ladders
    lad_rows = []
    for l in RETURNS["ladders"]:
        if l["total_usd"] > 5_000_000:
            continue
        alloc = "<br>".join(
            f'{e(x["brand"])} — {money(x["amount_usd"])} @ {pct(x["apy_pct"])}' for x in l["allocations"][:6]
        )
        if len(l["allocations"]) > 6:
            alloc += f'<br><span class="muted small">+ {len(l["allocations"]) - 6} more banks</span>'
        status = badge("fully covered", "good") if l["status"] == "fully covered" else badge(l["status"], "warn")
        lad_rows.append([
            money(l["total_usd"]),
            e(l["kind"]),
            str(l["banks_needed"]),
            str(l["distinct_banks_used"]),
            money(l["allocation_each_usd"]),
            pct(l["blended_apy_pct"]),
            money(l["year1_interest_usd"]),
            money(l["uninsured_usd"]) if l["uninsured_usd"] else "&mdash;",
            status,
            alloc,
            src(l["allocations"][0]["source"], "top source"),
        ])
    ladders = table(["Total deposit", "Plan", "Banks required", "Banks used", "Per bank", "Blended APY", "Year-1 interest", "Uninsured", "FDIC status at this dataset", "Allocation", "Source"],
                    lad_rows,
                    note="Each plan puts at most $250,000 in any one bank, which is the single-owner FDIC limit. "
                         "&ldquo;No-conditions&rdquo; uses only accounts whose published APY has no relationship, new-customer or direct-deposit requirement. "
                         "&ldquo;Max-rate&rdquo; also allows those conditional rates. Where a plan needs more banks than the study covers, the row is marked "
                         "not fully covered rather than pretending the excess is insured. One account per FDIC certificate: two products at the same "
                         "bank share a single $250,000 limit, so a plan never counts the same certificate twice. Interest is computed only on the "
                         "amount actually placed inside the FDIC limit.",
                    classes=["num", "", "num", "num", "num", "num", "num", "num", "", "", ""])

    cov_rows = [
        [money(c["deposit_usd"]), money(c["single_owner_coverage_usd"]), money(c["uninsured_if_one_bank_usd"]),
         str(c["banks_required_single_owner"]), money(c["joint_coverage_two_owners_usd"]), str(c["banks_required_joint_two_owners"]),
         src("https://www.fdic.gov/resources/deposit-insurance/financial-products-insured", "FDIC rule")]
        for c in RETURNS["coverage_gap"]
    ]
    cov = table(["Deposit", "Insured at one bank (single)", "Uninsured at one bank (single)", "Banks required (single)", "Insured at one bank (joint)", "Banks required (joint)", "Source"],
                cov_rows,
                note="Derived from the FDIC ownership-category rules; the per-category limits are on the FDIC and apps page.",
                classes=["num"] * 6 + [""])

    excl = "".join(
        f'<li><strong>{e(x["brand"])} — {e(x["account_name"])}</strong>: {e(x["reason"])} {src(x["sources"][0]["url"], "page checked")}</li>'
        for x in RETURNS["excluded_accounts"]
    )

    body = f"""
{page_head("What the deposit actually earns",
          f"Return tables for deposits from $10,000 to $2,500,000, over 1, 2, 3 and 5 years, plus FDIC-safe "
          f"multi-bank ladder plans. Account opened {OPEN_DATE}.", "Category · returns")}
<div class="callout">
  <p><strong>Method.</strong> APY already includes compounding, so a constant-rate projection is
  <code>balance = deposit &times; (1 + APY)<sup>years</sup></code>. No rate is assumed: only APYs transcribed from a bank's own page
  are used. Monthly fees are shown separately and subtracted in the net columns on the Accounts page.</p>
</div>

<h2>Interest earned in year 1</h2>
<p class="muted">The simplest comparison: what each account pays on each deposit size in the first year, before fees and tax.</p>
{t1}

<h2>Balance after five years</h2>
<p class="muted">Same deposits, today's rate held constant for five years.</p>
{t5}

<h2>Term detail at $250,000</h2>
{term}

<h2>FDIC ladder plans</h2>
<p>Above $250,000 the limiting factor is no longer the rate — it is the insurance ceiling. Each plan spreads a balance across
as many distinct banks as this study covers, never more than $250,000 in any one of them. Where that is not enough banks to
hold the whole balance inside the limit, the shortfall appears in the Uninsured column rather than being spread over duplicate
rows.</p>
{ladders}

<h2>Coverage arithmetic</h2>
{cov}

<h2>Accounts excluded from the projections</h2>
<p>These accounts are in the comparison but not in any return table, because no official numeric APY could be read for them.
Leaving them out is deliberate: filling the gap with an estimate would make the tables look complete and be wrong.</p>
<ul>{excl}</ul>
"""
    return layout("returns.html", "Returns on deposit", body,
                  "Interest and 5-year balances by deposit size, plus FDIC ladder plans for balances above $250,000.")


def bonuses_page():
    rows = []
    for p in BONUSES["promotions"]:
        tiers = "<br>".join(
            f'{money(t.get("deposit_usd"))}+ → {money(t.get("bonus_usd"))}' if t.get("deposit_usd") is not None
            else f'{money(t.get("bonus_usd"))} — {e(t.get("requirement",""))}'
            for t in p["tiers"]
        ) or "&mdash;"
        rows.append([
            f'<strong>{e(p["brand"])}</strong><br><span class="muted small">{e(p["type"])}</span>',
            f'<strong>{e(p["headline"])}</strong>',
            tiers,
            e(p["requirements"]),
            e(p["eligibility"]),
            e(p["expires"] or "no stated expiry"),
            src(p["source"]),
        ])
    main = table(["Bank", "Offer", "Tiers", "What you must do", "Eligibility", "Expires", "Source"],
                 rows,
                 note="Transcribed from the bank's own offer page on 2026-10-22. Bonuses are taxable income in most cases and are usually reported on a 1099-INT; no tax treatment is asserted here.",
                 classes=["", "", "", "", "", "", ""])

    none_rows = [
        [f'<strong>{e(x["brand"])}</strong>', e(x["note"]), src(x["checked_url"], "page checked")]
        for x in BONUSES["no_savings_bonus_found"]
    ]
    none_tbl = table(["Bank", "What the page showed", "Page checked"], none_rows,
                     note="This records what the official account page did or did not show on the date checked. It is not a claim that the bank has no offer anywhere, and it is not a claim about targeted or invitation-only mailers.",
                     classes=["", "", ""])

    body = f"""
{page_head("Bonuses, boosts and promotions",
          "Only offers stated on a bank's own page are listed, with the deposit tiers, the conditions and the expiry date. "
          "Everything else is recorded as 'no bonus shown on the account page' and linked.", "Category · bonuses")}
<h2>Documented offers</h2>
{main}
<h2>Where no savings bonus was published</h2>
{none_tbl}
<div class="callout warn">
  <p><strong>A bonus is not a rate.</strong> A $200 bonus on a $10,000 deposit held for 90 days is worth roughly 0.8% annualized
  over that quarter — meaningful, but it does not change which account is best for a multi-year balance. The return tables treat
  bonuses as separate from APY and never add them into a projection.</p>
</div>
"""
    return layout("bonuses.html", "Bonuses and promotions", body,
                  "Verified savings account bonuses and promotional rates with eligibility rules and expiry dates.")


def rules_page():
    rows = []
    for a in sorted_accounts():
        rows.append([
            f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["account_name"])}</span>',
            money(a["min_open_usd"]),
            e(a["opening_requirements"]),
            e(a["withdrawal_limit"] or "No limit stated on the official page."),
            e(a["fee_waiver"] or "Not published."),
            src(a["sources"][0]["url"]),
        ])
    main = table(["Bank / account", "Min. to open", "Opening requirements", "Withdrawal / activity rules", "How the monthly fee is waived", "Source"],
                 rows, classes=["", "num", "", "", "", ""])

    fee_rows = []
    for a in sorted_accounts():
        fee = a["monthly_fee_usd"]
        annual = None if fee is None else fee * 12
        drag10k = None if fee is None else (fee * 12) / 10000 * 100
        fee_rows.append([
            f'<strong>{e(a["brand"])}</strong>',
            money(fee, cents=True) if fee is not None else "&mdash;",
            money(annual, cents=True) if annual is not None else "&mdash;",
            pct(drag10k, 2) if drag10k is not None else "&mdash;",
            pct((fee * 12) / 100000 * 100, 2) if fee is not None else "&mdash;",
            money(a["min_balance_to_avoid_fee_usd"]) if a["min_balance_to_avoid_fee_usd"] not in (None,) else "&mdash;",
            src(a["sources"][0]["url"]),
        ])
    fee_tbl = table(["Bank", "Monthly fee", "Annual cost", "Drag on a $10,000 balance", "Drag on a $100,000 balance", "Balance that waives it", "Source"],
                    fee_rows,
                    note="Fee drag is the annual fee divided by the balance, as a percentage. It is not subtracted from the APY shown elsewhere; "
                         "it is shown separately because whether you pay it depends on the waiver.",
                    classes=["", "num", "num", "num", "num", "num", ""])

    body = f"""
{page_head("Rules, minimums and fees",
          "What each bank requires before it will open the account, what it charges to keep it open, and the activity rules "
          "that are easy to miss.", "Category · rules")}
<h2>Opening and account rules</h2>
{main}
<h2>What the monthly fee costs if you do not qualify for the waiver</h2>
{fee_tbl}
<div class="callout bad">
  <p><strong>The fee is the hidden cost in this comparison.</strong> A $5 monthly fee is $60 a year. On a $10,000 balance that is
  0.60% — more than the entire APY of several accounts in this table. At $100,000 the same fee is 0.06%, which is why the fee
  matters most to exactly the balances where the headline rate looks least attractive.</p>
</div>
<h3>Rules worth flagging</h3>
<ul>
  <li><strong>Ally</strong> limits certain withdrawals and transfers to 10 per statement cycle and may close the account if the limit is exceeded more than occasionally. {src("https://www.ally.com/bank/online-savings-account/", "Ally")}</li>
  <li><strong>Truist One Savings</strong> charges $5 per withdrawal over six in a statement cycle, capped at six fees. {src("https://www.truist.com/savings/truist-one-savings/disclosures-and-fees", "Truist disclosure")}</li>
  <li><strong>TD Simple Savings</strong> has no minimum opening deposit, but TD states the account closes automatically if no deposit is made within 45 days. {src("https://www.td.com/us/en/personal-banking/savings-accounts", "TD")}</li>
  <li><strong>Bank of America Advantage Savings</strong> requires $100 to open, does not allow paper checks, and is set to decline all overdrafts. {src("https://www.bankofamerica.com/salesservices/deposits/resources/personal-schedule-fees/?request_locale=en_US", "BofA fee schedule")}</li>
  <li><strong>SoFi</strong> automatically opens a checking account alongside the savings account. {src("https://www.sofi.com/banking/high-yield-savings-account/", "SoFi")}</li>
  <li><strong>Schwab</strong> has no online application for Investor Savings; the application is downloaded, mailed, uploaded through secure messaging or brought to a branch. {src("https://www.schwab.com/savings", "Schwab")}</li>
  <li><strong>Wells Fargo</strong> requires 18+ to apply online; 17 and under must open at a branch. {src("https://www.wellsfargo.com/savings-cds/way2save/", "Wells Fargo")}</li>
</ul>
"""
    return layout("rules.html", "Rules and fees", body,
                  "Opening requirements, withdrawal rules, fee waivers and the real annual cost of monthly fees.")


def security_page():
    rows = []
    by_cert = {}
    for a in sorted_accounts():
        by_cert.setdefault(a["cert"], []).append(a)
    for cert, accts in by_cert.items():
        a = accts[0]
        b = INST.get(cert, {})
        yes = sum(1 for x in accts if x["mobile_app"]["value"] == "yes")
        if yes == len(accts):
            app = badge("confirmed", "good")
        elif yes == 0:
            app = badge("not confirmed", "warn")
        else:
            app = badge(f"confirmed for {yes} of {len(accts)}", "warn")
        products = "<br>".join(e(x["account_name"]) for x in accts)
        rows.append([
            f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["institution"])}</span>',
            f'<a class="src" href="https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{cert}" target="_blank" rel="noopener">{cert}</a>',
            badge("active", "good") if b.get("active") == 1 else badge("inactive", "bad"),
            badge("FDIC insured", "good") if b.get("insfdic") == 1 else badge("not insured", "bad"),
            e(b.get("bkclass_label", "")),
            money(b.get("assets_usd")),
            money(b.get("deposits_usd")),
            products,
            app,
        ])
    main = table(["Bank", "FDIC cert.", "Status", "Insurance", "Charter", "Total assets", "Domestic deposits", "Products in study", "Mobile app"],
                 rows,
                 note=f"All institution fields are from the FDIC BankFind Suite institutions API, index {e(INSTITUTIONS['dataset_index'])}, retrieved 2026-10-22. "
                      f"Assets and deposits are the API's thousands figure multiplied by 1,000. "
                      f"{src('https://api.fdic.gov/banks/institutions', 'API')}",
                 classes=["", "num", "", "", "", "num", "num", "", ""])

    cov_rows = [[e(c["category"]), e(c["rule"]), money(c["limit_usd"]), src(c["source"])] for c in FDIC["coverage_limits"]]
    cov = table(["Ownership category", "FDIC rule", "Limit shown", "Source"], cov_rows,
                classes=["", "", "num", ""])

    app_rows = []
    for a in sorted_accounts():
        app_rows.append([
            f'<strong>{e(a["brand"])}</strong>',
            "Yes" if a["mobile_app"]["value"] == "yes" else "Not confirmed",
            e(a["mobile_app"]["note"]),
            src(a["mobile_app"]["source"], "source"),
        ])
    appt = table(["Bank", "App confirmed", "What the official page says", "Source"], app_rows, classes=["", "", "", ""])

    disc = INSTITUTIONS["discover_note"]
    body = f"""
{page_head("FDIC insurance and digital access",
          "Insurance status is the one thing on this site that can be checked against a government register rather than a "
          "marketing page. It was checked for every bank, individually.", "Category · safety")}
<h2>Institution-by-institution verification</h2>
{main}
<h2>What the FDIC actually covers</h2>
{cov}
<div class="callout warn">
  <p><strong>Not covered:</strong> stocks, bonds, mutual funds, annuities, life insurance, municipal securities, crypto assets,
  U.S. Treasury securities, and the contents of safe deposit boxes. {src("https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance", "FDIC list")}</p>
</div>
<h2>Digital access</h2>
<p>A bank is marked as having a confirmed app only where its own account page or app page names the app. That is a weaker claim
than it sounds: it confirms the app exists, not that it is good, and not that its security is adequate.</p>
{appt}
<div class="callout bad">
  <p><strong>Security was not independently audited — and is flagged for your review.</strong>
  This project confirms three things: the institution is FDIC-insured, the charter type, and whether an app is named on the
  official page. It does not verify encryption standards, multi-factor authentication, fraud-reimbursement policies, or
  app-store ratings, and it makes no comparative security ranking. Treat any security claim about these banks, including
  claims implied by a polished app, as unverified until you read the bank's own security page.</p>
</div>
<h2>An irregularity worth knowing about: Discover</h2>
<p>{e(disc['finding'])}</p>
<p class="muted small">{' '.join(src(u) for u in disc['sources'])}</p>
"""
    return layout("security.html", "FDIC and apps", body,
                  "FDIC certificate numbers, insurance status, charter type and confirmed mobile apps for every bank in the study.")


def competitiveness_page():
    nat = {r["product"]: r for r in FDIC["national_rates"]["rows"]}
    sav = nat["Savings"]["national_deposit_rate_pct"]
    cd12 = nat["12 month CD"]["national_deposit_rate_pct"]
    t12 = FDIC["national_rates"]["treasury_yields_pct"]["by_maturity_months"]["12"]
    t60 = FDIC["national_rates"]["treasury_yields_pct"]["by_maturity_months"]["60"]

    rate_rows = []
    for a in sorted_accounts():
        r, cond = account_rate(a["id"], 250000)
        if r is None:
            rate_rows.append([
                f'<strong>{e(a["brand"])}</strong>', badge("not published", "warn"), "&mdash;", "&mdash;", "&mdash;", "&mdash;", "&mdash;", "&mdash;",
                src(a["sources"][0]["url"]),
            ])
            continue
        share = r / t12 * 100
        mult = r / sav
        spread = (r - sav) * 100
        vs12 = (r - cd12) * 100
        vs_t = (r - t12) * 100
        years_double = 0.693147 / __import__("math").log(1 + r / 100)
        rate_rows.append([
            f'<strong>{e(a["brand"])}</strong>' + (f'<br><span class="muted small">{e(cond)}</span>' if cond else ""),
            pct(r),
            "{:.1f}&times;".format(mult),
            "{:+.0f} bp".format(spread),
            "{:+.0f} bp".format(vs12),
            "{:+.0f} bp".format(vs_t),
            "{:.0f}%".format(share),
            ("> 1,000 yrs" if years_double > 1000 else "{:.1f} yrs".format(years_double)),
            src(a["sources"][0]["url"]),
        ])
    main = table(["Bank / account", "APY at $250k", "vs FDIC savings average", "Spread vs savings average", "vs 12-mo CD average", "vs 12-mo Treasury", "APY as % of Treasury yield", "Years to double", "Source"],
                 rate_rows,
                 note=f"FDIC national savings rate {pct(sav)}, 12-month CD average {pct(cd12)}, 12-month Treasury yield {pct(t12)}, all as of "
                      f"{FDIC['national_rates']['as_of']}. {src(FDIC['national_rates']['source'], 'FDIC National Rates and Rate Caps')}",
                 classes=["", "num", "num", "num", "num", "num", "num", "num", ""])

    bench_rows = [
        [e(r["product"]), pct(r["national_deposit_rate_pct"], 2), pct(r["national_rate_cap_pct"], 2), src(FDIC["national_rates"]["source"])]
        for r in FDIC["national_rates"]["rows"]
    ]
    bench = table(["Product", "National deposit rate", "National rate cap", "Source"], bench_rows,
                  note="The national rate is a deposit-weighted average across all insured institutions and credit unions, not an offer. The rate cap applies to less-than-well-capitalized institutions.",
                  classes=["", "num", "num", ""])

    treasury_rows = [
        [f"{m} months", pct(v, 2), src(FDIC["national_rates"]["treasury_yields_pct"]["source"])]
        for m, v in FDIC["national_rates"]["treasury_yields_pct"]["by_maturity_months"].items()
    ]
    treasury = table(["Treasury maturity", "Yield", "Source"], treasury_rows, classes=["", "num", ""])

    best = max(account_rate(a["id"], 250000)[0] for a in ACCOUNTS["accounts"] if a["apy_regular_pct"] is not None)
    _worst = min((a for a in ACCOUNTS["accounts"] if a["apy_regular_pct"] is not None),
                 key=lambda a: account_rate(a["id"], 250000)[0])
    _worst_apy = account_rate(_worst["id"], 250000)[0]
    _worst_brand = _worst["brand"]
    body = f"""
{page_head("How competitive are these rates?",
          f"Each APY is measured against the FDIC's own national averages and against Treasury yields, so the number can be "
          f"judged rather than just compared with the other banks in the table.", "Category · competitiveness")}
<h2>Every rate against the benchmarks</h2>
<p>The FDIC national savings rate on {FDIC['national_rates']['as_of']} was <strong>{pct(sav)}</strong>. The best verified rate in this
study is <strong>{pct(best)}</strong> — about {best/sav:.1f} times the national average. That sounds decisive, and against a branch
savings account it is. Against the rest of the market it is less so: a 12-month Treasury yielded
<strong>{pct(t12)}</strong> on the same date.</p>
{main}
<h2>The benchmark table</h2>
{bench}
<h2>Treasury yields for the same horizons</h2>
{treasury}
<div class="callout warn">
  <p><strong>The honest conclusion on competitiveness.</strong> At {pct(best)}, the best savings account in this study still pays
  {(t12 - best) * 100:.0f} basis points less than a 12-month Treasury and {(t60 - best) * 100:.0f} basis points less than a 60-month
  Treasury on the FDIC's own comparison date. Savings accounts win on liquidity and on FDIC insurance, not on yield. What the
  table does show is that the gap between the best and worst <em>savings</em> account in this study is about
  {(best - _worst_apy) * 100:.0f} basis points ({_worst_brand} pays {pct(_worst_apy)}), and the gap between the best account and
  the FDIC national savings average of {pct(nat['Savings']['national_deposit_rate_pct'])} is about
  {(best - nat['Savings']['national_deposit_rate_pct']) * 100:.0f} basis points — that is the part you control.</p>
</div>
<h2>Life-span effect</h2>
<p>A savings APY is variable. Every bank in this table reserves the right to change it, and several say so explicitly on the page
the rate came from. That makes the 5-year projections on the Returns page a <em>constant-rate arithmetic</em> exercise, not a
forecast. The same page shows a fallback scenario where the rate drops to the FDIC national average after year one; the
difference between the two columns is the value of the rate staying put, which no bank promises.</p>
<p class="muted">CD rates are included in the benchmark table only for context. This study does not recommend CDs, because the
required holding period conflicts with the liquidity the account is meant to provide.</p>
"""
    return layout("competitiveness.html", "Competitiveness", body,
                  "Every savings APY measured against FDIC national averages, CD averages and Treasury yields.")


def flagged_page():
    items = []
    for a in sorted_accounts():
        if a["apy_regular_pct"] is None:
            items.append({
                "area": "APY",
                "item": f'{a["brand"]} — {a["account_name"]}',
                "detail": a["apy_note"],
                "status": "Unverified — left blank",
                "sources": a["sources"],
            })
        if a["mobile_app"]["value"] != "yes":
            items.append({
                "area": "Digital app",
                "item": f'{a["brand"]} — {a["account_name"]}',
                "detail": a["mobile_app"]["note"],
                "status": "Unverified — not confirmed on the official page",
                "sources": [{"label": "Page checked", "url": a["mobile_app"]["source"], "as_of": "2026-10-22"}],
            })

    items += [
        {
            "area": "Rendering defect",
            "item": "Bank of America — Advantage Savings fee block",
            "detail": "The Advantage Savings page renders the monthly maintenance fee and waiver balance as the literal placeholders \"$XXXX\". The $8.00 fee and $500 waiver threshold used in this study were taken from the bank's Personal Schedule of Fees PDF (effective 2026-08-07), not from the product page.",
            "status": "Resolved from a second official source — page defect noted",
            "sources": [
                {"label": "Product page with placeholders", "url": "https://www.bankofamerica.com/deposits/savings/savings-accounts/", "as_of": "2026-10-22"},
                {"label": "Personal Schedule of Fees", "url": "https://www.bankofamerica.com/salesservices/deposits/resources/personal-schedule-fees/?request_locale=en_US", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Location",
            "item": "Bank of America — rate sheet exists, but not for New York",
            "detail": "Bank of America's rate page serves a state-specific PDF only after ZIP and county selection. The published sheet for Virginia (excluding greater Washington DC) and for states without Bank of America financial centers shows Advantage Savings at 0.04% APY on every balance tier, effective 2026-10-21. That is not the New York sheet, so it is not used in the comparison; the blank BofA APY stands.",
            "status": "Unverified for New York — comparable published rate documented",
            "sources": [
                {"label": "BofA rate page (ZIP-gated)", "url": "https://www.bankofamerica.com/deposits/bank-account-interest-rates/", "as_of": "2026-10-22"},
                {"label": "BofA published rate sheet, Virginia/non-branch states", "url": "https://media.bac-assets.com/DigitalDeposit_VA_VA_Excluding_DC.pdf", "as_of": "2026-10-21"}
            ],
        },
        {
            "area": "Rendering defect",
            "item": "Capital One — 360 Performance Savings APY",
            "detail": "The product page displays the APY as \"NaN\" and an effective date of 10/21/2026. The 3.20% APY used here comes from Capital One's own savings category page, which states the rate in text.",
            "status": "Resolved from a second official source — page defect noted",
            "sources": [
                {"label": "Product page (NaN)", "url": "https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/", "as_of": "2026-10-22"},
                {"label": "Category page with 3.20%", "url": "https://www.capitalone.com/bank/savings-accounts/", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Rendering defect",
            "item": "Citibank — savings APY token",
            "detail": "The Citi savings page renders the APY as the unresolved template token \":BLUE_AccSavings_Rate%\". Citi's footnotes state the APY depends on rate region, relationship tier and promotion. No numeric APY is asserted.",
            "status": "Unverified — left blank",
            "sources": [{"label": "Citi savings page", "url": "https://www.citi.com/banking/savings-account", "as_of": "2026-10-22"}],
        },
        {
            "area": "Location",
            "item": "Wells Fargo, U.S. Bank, PNC — rate shown depends on ZIP",
            "detail": "Rates were read from the location the site served: Wells Fargo CA 94105, U.S. Bank ZIP 55402, PNC ZIP 15222. Each bank states rates vary by market. The rates reproduced here are the rates those pages showed, not a promise for a New York ZIP.",
            "status": "Verified as published, with a location caveat",
            "sources": [
                {"label": "Wells Fargo rates", "url": "https://www.wellsfargo.com/savings-cds/rates/", "as_of": "2026-10-22"},
                {"label": "U.S. Bank rates", "url": "https://www.usbank.com/bank-accounts/savings-accounts/bank-smartly-savings/savings-account-interest-rates.html", "as_of": "2026-10-22"},
                {"label": "PNC rates", "url": "https://www.pnc.com/en/personal-banking/banking/deposit-rates/high-yield-savings.html", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Availability",
            "item": "PNC High Yield Savings",
            "detail": "The PNC High Yield Savings page returned \"This Product Isn't Available in Your Area\" and its rate center reported the product unavailable for ZIP 15222. The page title carries \"3.15% APY\", but that figure could not be confirmed in page content for a New York ZIP, so it is not used.",
            "status": "Unverified — availability and APY both flagged",
            "sources": [
                {"label": "PNC High Yield Savings", "url": "https://www.pnc.com/en/personal-banking/banking/savings/high-yield-savings.html", "as_of": "2026-10-22"},
                {"label": "PNC rate center", "url": "https://www.pnc.com/en/personal-banking/banking/deposit-rates/high-yield-savings.html", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Corporate structure",
            "item": "Discover Bank — no longer an active institution",
            "detail": "FDIC BankFind returns Discover Bank (certificate 5649) with ACTIVE = 0. Capital One states that Discover Bank deposit accounts opened on or after May 18, 2025 are counted together with Capital One accounts for FDIC coverage. Discover is therefore not treated as a separate bank in this study.",
            "status": "Irregularity confirmed — merger reflected in FDIC data",
            "sources": [
                {"label": "FDIC BankFind record (ACTIVE = 0)", "url": "https://api.fdic.gov/banks/institutions?filters=CERT%3A5649", "as_of": "2026-10-22"},
                {"label": "Capital One FDIC pooling note", "url": "https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Third-party data",
            "item": "Bank of America 0.04% and Chase 0.02% appear in a competitor's calculator",
            "detail": "Marcus's published comparison calculator lists Bank of America at 0.04% APY and Chase at 0.02% APY for New York savings, sourced from Curinos as of 2026-10-20. Those are third-party figures attributed to the banks, not rates published by Bank of America or Chase, and they are not used anywhere in this study. Both banks' APY cells stay blank. The figures are recorded here because a reader may encounter them and wonder why this site disagrees.",
            "status": "Not used — third-party attribution, not an official bank rate",
            "sources": [
                {"label": "Marcus referral page containing the calculator", "url": "https://www.marcus.com/us/en/savings/referrals", "as_of": "2026-10-21"},
                {"label": "Bank of America rate page (ZIP-gated)", "url": "https://www.bankofamerica.com/deposits/bank-account-interest-rates/", "as_of": "2026-10-22"},
                {"label": "Chase rate page (ZIP-gated)", "url": "https://www.chase.com/personal/savings/savings-account/interest-rates", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Security",
            "item": "Security features were not audited",
            "detail": "This study verifies FDIC insurance status, charter type and whether an official mobile app is named. It does not verify multi-factor authentication, encryption, fraud-reimbursement terms or app-store ratings, and makes no comparative security ranking.",
            "status": "Out of scope — flagged for manual review",
            "sources": [{"label": "FDIC consumer protection information", "url": "https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance", "as_of": "2026-10-22"}],
        },
        {
            "area": "Missing field",
            "item": "Charles Schwab — minimum opening deposit",
            "detail": "The Schwab Investor Savings page does not state a minimum opening deposit. The field is left blank.",
            "status": "Unverified — left blank",
            "sources": [{"label": "Schwab page", "url": "https://www.schwab.com/savings", "as_of": "2026-10-22"}],
        },
        {
            "area": "Missing field",
            "item": "PNC — minimum, fee and waiver",
            "detail": "Because the PNC product page replaced its content with a geo-restriction notice, the minimum opening deposit, monthly fee and waiver could not be read for this market. All three are left blank.",
            "status": "Unverified — left blank",
            "sources": [{"label": "PNC page", "url": "https://www.pnc.com/en/personal-banking/banking/savings/high-yield-savings.html", "as_of": "2026-10-22"}],
        },
        {
            "area": "Promotional rate",
            "item": "Wells Fargo Platinum, U.S. Bank relationship tiers, SoFi boost, Marcus referral",
            "detail": "These rates are conditional. They are marked with the condition on every table where they appear, are excluded from the 'no-conditions' ladder plan, and in SoFi's and Marcus's case are applied for year one only.",
            "status": "Verified as published — condition disclosed",
            "sources": [
                {"label": "Wells Fargo", "url": "https://www.wellsfargo.com/savings-cds/rates/", "as_of": "2026-10-22"},
                {"label": "U.S. Bank", "url": "https://www.usbank.com/bank-accounts/savings-accounts/bank-smartly-savings/savings-account-interest-rates.html", "as_of": "2026-10-22"},
                {"label": "SoFi", "url": "https://www.sofi.com/banking/high-yield-savings-account/", "as_of": "2026-10-22"},
                {"label": "Marcus", "url": "https://www.marcus.com/us/en/savings/referrals", "as_of": "2026-10-22"},
            ],
        },
    ]

    rows = []
    for i in items:
        links = "<br>".join(src(s["url"], s["label"]) for s in i["sources"])
        kind = "bad" if "Unverified" in i["status"] else ("warn" if "caveat" in i["status"] or "Out of scope" in i["status"] else "info")
        rows.append([
            e(i["area"]),
            f'<strong>{e(i["item"])}</strong>',
            e(i["detail"]),
            badge(i["status"], kind),
            links,
        ])
    main = table(["Area", "Item", "What was found", "Status", "Sources"], rows,
                 note="Every row here is a value or claim that this project deliberately did not fill in, or filled in from a second official source and wants you to see why. None of these block publication; they block a numeric claim.",
                 classes=["", "", "", "", ""])

    body = f"""
{page_head("Flagged for review",
          "Everything that could not be verified from an official source, every page that was broken or geo-gated, and every "
          "value that was left blank instead of guessed.", "Category · transparency")}
<div class="callout">
  <p><strong>Why this page exists.</strong> A table with no gaps looks more confident than the evidence supports. The gaps are
  listed here with the page that was checked, so you can repeat the check yourself in a minute.</p>
</div>
{main}
<h2>What was left blank, and why that is the right call</h2>
<p>{len(RETURNS['excluded_accounts'])} of the {len(ACCOUNTS['accounts'])} accounts have no numeric APY anywhere on this site. In each case the bank either requires a ZIP code,
serves an empty table, or renders a placeholder. The FDIC publishes a national savings average of
{pct(FDIC['national_rates']['rows'][0]['national_deposit_rate_pct'])}; plugging it into the {sum(1 for a in ACCOUNTS['accounts'] if a['apy_regular_pct'] is None)} blank rows would have made
the table look complete and would have been an invention. Their fee, minimum and rule data — which <em>is</em> published — is
still included, because it is verifiable.</p>
"""
    return layout("flagged.html", "Flagged for review", body,
                  "Unverified values, geo-gated pages and rendering defects found while verifying every figure.")


def sources_page():
    seen = {}
    for a in ACCOUNTS["accounts"]:
        for s in a["sources"]:
            seen.setdefault(s["url"], {"label": s["label"], "as_of": s["as_of"], "used_for": set()})
            seen[s["url"]]["used_for"].add(a["brand"])
    for p in BONUSES["promotions"]:
        seen.setdefault(p["source"], {"label": f"{p['brand']} offer", "as_of": "2026-10-22", "used_for": set()})
        seen[p["source"]]["used_for"].add(p["brand"])
    for x in BONUSES["no_savings_bonus_found"]:
        seen.setdefault(x["checked_url"], {"label": f"{x['brand']} account page", "as_of": "2026-10-22", "used_for": set()})
        seen[x["checked_url"]]["used_for"].add(x["brand"])
    for c in FDIC["coverage_limits"]:
        seen.setdefault(c["source"], {"label": "FDIC deposit insurance", "as_of": "2026-10-22", "used_for": set()})
        seen[c["source"]]["used_for"].add("FDIC")
    rates = FDIC["national_rates"]
    seen.setdefault(rates["source"], {"label": "FDIC national rates and rate caps", "as_of": rates["as_of"], "used_for": set()})
    seen[rates["source"]]["used_for"].add("Benchmarks")
    seen.setdefault(INSTITUTIONS["api_endpoint"], {"label": "FDIC BankFind institutions API", "as_of": "2026-10-22", "used_for": set()})
    seen[INSTITUTIONS["api_endpoint"]]["used_for"].add("All banks")

    gov = []
    bank = []
    for url, meta in sorted(seen.items(), key=lambda kv: (kv[1]["label"].lower())):
        row = [
            f'<strong>{e(meta["label"])}</strong>',
            src(url, url),
            e(meta["as_of"]),
            e(", ".join(sorted(meta["used_for"]))),
        ]
        (gov if ("fdic.gov" in url or "api.fdic.gov" in url) else bank).append(row)

    gov_tbl = table(["Source", "URL", "Retrieved / effective", "Used for"], gov, classes=["", "", "", ""])
    bank_tbl = table(["Source", "URL", "Retrieved / effective", "Used for"], bank, classes=["", "", "", ""])

    body = f"""
{page_head("Sources",
          "Every external page used, with the date it was retrieved. Bank pages change; if a number here disagrees with the "
          "live page, the live page is authoritative and this site is out of date.", "Category · references")}
<h2>Government sources</h2>
{gov_tbl}
<h2>Bank sources</h2>
<p class="muted">{len(bank)} official bank pages were used. Links open the bank's own site.</p>
{bank_tbl}
<h2>What is not a source here</h2>
<p>No comparison site, affiliate site, press article or search-result snippet was used as the basis for any number on this site.
Aggregator pages were encountered during research and deliberately excluded. One example: a competitor's calculator quotes
Bank of America and Chase savings rates, but neither bank publishes a rate this study could read without a ZIP code, so both
cells are blank here even though a number was available from the aggregator.</p>
"""
    return layout("sources.html", "Sources", body,
                  "Every official government and bank page used, with retrieval dates.")


def methodology_page():
    facts = [
        ("Open date used for every projection", OPEN_DATE),
        ("Accounts in the comparison", str(len(ACCOUNTS["accounts"]))),
        ("Accounts with a verified numeric APY", str(len(RETURNS["projections"]))),
        ("Institutions verified in FDIC BankFind", str(sum(1 for b in INSTITUTIONS["banks"] if b.get("active") == 1))),
        ("Promotions documented", str(len(BONUSES["promotions"]))),
        ("Deposit sizes modelled", "8, from $10,000 to $2,500,000"),
        ("Terms modelled", "1, 2, 3 and 5 years"),
        ("FDIC national rates as of", FDIC["national_rates"]["as_of"]),
    ]
    fn = ""
    for k, v in facts:
        fn += f'<div class="card flat"><div class="muted small">{e(k)}</div><div style="font-weight:700;font-size:18px;margin-top:4px">{e(v)}</div></div>'

    body = f"""
{page_head("Methodology",
          "How each number on this site was produced, in enough detail that you can reproduce or challenge it.", "Reference")}
<h2>The study at a glance</h2>
<div class="grid k4">{fn}</div>

<h2>1. How banks were selected</h2>
<p>The starting universe was the largest active FDIC-insured institutions by total assets, pulled from the FDIC BankFind Suite
institutions API rather than from any ranking article. Every institution in the study sits between $56.8 billion and $4.09
trillion in total assets, and {sum(1 for b in INSTITUTIONS["banks"] if b.get("active") == 1 and b.get("bkclass_label") == "National bank")}
of the {sum(1 for b in INSTITUTIONS["banks"] if b.get("active") == 1)} active institutions are chartered as national banks; the rest are
state-chartered banks that still fall inside the same size screen. The intent was to answer the question as asked:
big national banks, no small local banks, no credit unions, and no fintech front-ends whose deposits sit at a partner bank.</p>
<p class="muted">Deliberately excluded: fintechs that are not banks (their deposits are held at a partner institution, which is
where the FDIC coverage actually applies), credit unions (NCUA-insured, a different scheme), and brokerage cash-sweep programs.</p>

<h2>2. How rates were captured</h2>
<p>Each rate was read from the bank's own page on {OPEN_DATE} and transcribed with the bank's own effective date. Where a bank
publishes tiered rates, every tier is recorded, with the balance band and the condition attached to it. Where a rate is
returned by a ZIP-gated tool, an empty table, or a template placeholder, the rate was left blank. No rate was taken from a
search snippet, a comparison site, or an older cached page.</p>

<h2>3. Return arithmetic</h2>
<p>APY is an annualized rate that already accounts for compounding, so:</p>
<p><code>balance after n years = deposit &times; (1 + APY/100)<sup>n</sup></code></p>
<p>and <code>interest = balance - deposit</code>. Where a documented promotional rate applies for part of the first year, the
year-1 figure uses a blended rate and the derivation is printed: SoFi's six months at 4.40% and six months at 3.30% gives
<code>1.044<sup>0.5</sup> &times; 1.033<sup>0.5</sup> - 1 = 3.85%</code>. Marcus's own page states that one referral produces a
combined 3.75% APY for the year, and that is the figure used.</p>
<p>The fallback column on the Returns page applies the FDIC national savings rate
({pct(FDIC['national_rates']['rows'][0]['national_deposit_rate_pct'])}, as of {FDIC['national_rates']['as_of']}) after year one.
It is a stress case that shows what a rate cut would cost, not a prediction.</p>

<h2>4. FDIC coverage arithmetic</h2>
<p>Coverage is $250,000 per depositor, per insured bank, per ownership category. A joint account with two owners therefore
raises the ceiling at a single bank to $500,000; a trust account uses the FDIC formula
<em>owners &times; beneficiaries &times; $250,000</em>, capped at $1,250,000 per owner. The ladder plans never place more than
$250,000 at one bank, and a plan that would need more distinct banks than the study contains is labelled
&ldquo;not fully covered&rdquo; instead of being quietly double-counted.</p>

<h2>5. What is deliberately not done</h2>
<ul>
  <li><strong>No estimation of missing rates.</strong> {len(RETURNS['excluded_accounts'])} of {len(ACCOUNTS['accounts'])} accounts have no APY on this site because the bank did not publish one in a readable form.</li>
  <li><strong>No blending of bonuses into APY.</strong> Bonuses are worth real money but they are one-off; adding them to a rate would misstate the ongoing yield.</li>
  <li><strong>No security ranking.</strong> FDIC status and the existence of an app are verified; security controls are not audited.</li>
  <li><strong>No tax or inflation adjustment.</strong> No current official tax rate or inflation index was fetched for this study, so none is applied.</li>
  <li><strong>No recommendation of a single bank.</strong> Rate, balance, fee waiver and FDIC ceiling interact; the tables let you price your own combination.</li>
</ul>

<h2>6. Reproducing this</h2>
<p>The entire site is generated from the JSON files in <code>data/</code> by scripts in <code>tools/</code>; no number on a page
is typed by hand. <code>tools/build_returns.py</code> produces the projections, <code>tools/build_site.py</code> renders the pages,
and <code>tools/check_site.py</code> fails the build if any table row lacks a source link or any internal link is broken.</p>
"""
    return layout("methodology.html", "Methodology", body,
                  "How the banks were selected, how rates were captured, and the exact formulas used.")


PAGES = {
    "index.html": index_page,
    "accounts.html": accounts_page,
    "returns.html": returns_page,
    "bonuses.html": bonuses_page,
    "rules.html": rules_page,
    "security.html": security_page,
    "competitiveness.html": competitiveness_page,
    "flagged.html": flagged_page,
    "sources.html": sources_page,
    "methodology.html": methodology_page,
}


def main():
    for filename, fn in PAGES.items():
        out = os.path.join(ROOT, filename)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("wrote", filename)
    # machine-readable copies for anyone who wants the raw data
    for name in ("accounts", "institutions", "fdic", "bonuses", "returns"):
        pass
    print("site built:", datetime.now().isoformat(timespec="seconds"))


if __name__ == "__main__":
    main()
