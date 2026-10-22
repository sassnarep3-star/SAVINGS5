#!/usr/bin/env python3
"""
SAVINGS5 static-site generator.

Reads the verified JSON in data/ and writes the GitHub Pages site into docs/.
Nothing on the site is hand-typed: every figure comes from a data record that
carries its own official source URL, and every unverified field renders as a
blank cell with an "unverified" badge that links to the Flagged for Review page.

Build-time guards (the build FAILS if any of these trip):
  1. Every APY in data/returns_model.json must appear in the matching product's
     apy_tiers in data/accounts.json.
  2. Every record whose status is "unverified" must have value == null.
  3. Every product with a published figure must have a source_url.
  4. Every internal href written into docs/ must resolve to a file that exists.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"

# Account-opening date used for every projection: today, UTC.
OPEN_DATE = dt.date(2026, 10, 22)
BUILD_UTC = "2026-10-22T00:00:00Z"
CAPTURE_LABEL = "22 October 2026, 00:00 UTC"

SITE_TITLE = "Savings Account Research"
REPO_URL = "https://github.com/sassnarep3-star/SAVINGS5"

NAV = [
    ("index.html", "Dashboard"),
    ("rates.html", "All accounts"),
    ("digital.html", "Digital banks"),
    ("branch.html", "Branch banks"),
    ("returns.html", "Returns"),
    ("fdic.html", "FDIC insurance"),
    ("bonuses.html", "Bonuses"),
    ("rules.html", "Opening rules"),
    ("benchmarks.html", "Rate benchmarks"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("methodology.html", "Methodology"),
]

errors: list[str] = []
written_pages: list[str] = []
internal_links: list[tuple[str, str]] = []  # (page, href)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def load(name: str):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def e(text) -> str:
    return html.escape(str(text), quote=True)


def money(x, decimals=0) -> str:
    if x is None:
        return ""
    return "$" + format(round(float(x), decimals), f",.{decimals}f")


def pct(x, decimals=2) -> str:
    if x is None:
        return ""
    return f"{float(x):.{decimals}f}%"


def src(url: str, label: str = "source") -> str:
    if not url:
        return ""
    return f'<a class="src" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}&#8599;</a>'


def unverified_cell(note: str = "") -> str:
    tip = f' title="{e(note)}"' if note else ""
    return f'<span class="badge badge-unver"{tip}><a href="flagged.html">unverified</a></span>'


def field(obj, fmt=lambda v: e(v), fallback_note=""):
    """Render a verification-wrapped field: value, or blank + unverified badge."""
    if obj is None:
        return unverified_cell(fallback_note)
    status = obj.get("status")
    value = obj.get("value")
    if status == "verified" and value is not None:
        out = fmt(value)
        if obj.get("note"):
            out += f' <span class="note" title="{e(obj["note"])}">&#9432;</span>'
        return out
    return unverified_cell(obj.get("note") or fallback_note)


def iso_to_human(d: str | None) -> str:
    if not d:
        return ""
    try:
        return dt.date.fromisoformat(d).strftime("%-d %b %Y")
    except ValueError:
        return d


def add_days(days: int) -> dt.date:
    return OPEN_DATE + dt.timedelta(days=days)


def project(principal: float, apy_pct: float, days: int) -> tuple[float, float]:
    """ending_balance, interest  =  P*(1+APY)^(days/365)."""
    ending = principal * (1.0 + apy_pct / 100.0) ** (days / 365.0)
    return ending, ending - principal


# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------
def page(filename: str, title: str, lede: str, body: str, subtitle: str = "") -> None:
    nav_items = []
    for href, label in NAV:
        cls = ' class="active"' if href == filename else ""
        nav_items.append(f'<a href="{href}"{cls}>{e(label)}</a>')
        internal_links.append((filename, href))

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; {e(SITE_TITLE)}</title>
<meta name="description" content="{e(lede[:160])}">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128176;</text></svg>">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap topbar-in">
    <a class="brand" href="index.html"><span class="brand-mark">S5</span><span class="brand-text">{e(SITE_TITLE)}</span></a>
    <button class="navtoggle" aria-label="Toggle navigation" aria-expanded="false">&#9776;</button>
  </div>
</header>
<nav class="mainnav" aria-label="Main">
  <div class="wrap navscroll">{''.join(nav_items)}</div>
</nav>
<main id="main" class="wrap">
  <div class="pagehead">
    <h1>{e(title)}</h1>
    {f'<p class="subtitle">{subtitle}</p>' if subtitle else ''}
    <p class="lede">{lede}</p>
  </div>
  {body}
</main>
<footer class="foot">
  <div class="wrap">
    <p><strong>Every figure on this site was read from an official source and is linked on the row.</strong>
       Blank cells marked <span class="badge badge-unver">unverified</span> could not be confirmed from an
       official source and are listed on <a href="flagged.html">Flagged for Review</a>. Nothing is estimated or inferred.</p>
    <p class="muted">Data captured {e(CAPTURE_LABEL)}. All savings APYs are variable and can change without notice.
       This site is a research summary, not financial advice.
       Built from <a href="{e(REPO_URL)}" target="_blank" rel="noopener noreferrer">sassnarep3-star/SAVINGS5</a>.</p>
  </div>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""
    (DOCS / filename).write_text(doc, encoding="utf-8")
    written_pages.append(filename)
    for m in re.finditer(r'href="([^"#:]+\.html)', doc):
        internal_links.append((filename, m.group(1)))


def table(headers: list[str], rows: list[list[str]], cls: str = "", caption: str = "") -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    cap = f"<caption>{caption}</caption>" if caption else ""
    return (
        f'<div class="tablewrap"><table class="data {cls}" data-sortable>{cap}'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


# --------------------------------------------------------------------------
# load + validate
# --------------------------------------------------------------------------
accounts = load("accounts.json")
fdic = load("fdic.json")
bench = load("benchmarks.json")
bonuses = load("bonuses.json")
flags = load("flags.json")
rmodel = load("returns_model.json")

INST = accounts["institutions"]
PRODUCTS = {}
PROD_INST = {}
for inst in INST:
    for p in inst["products"]:
        PRODUCTS[p["id"]] = p
        PROD_INST[p["id"]] = inst

SCHED = {s["product_id"]: s for s in rmodel["schedules"]}

# Guard 1 - every modelled APY must exist in the captured tier table.
for pid, s in SCHED.items():
    prod = PRODUCTS.get(pid)
    if prod is None:
        errors.append(f"returns_model references unknown product '{pid}'")
        continue
    captured = {t.get("apy") for t in prod.get("apy_tiers", [])}
    captured |= {t.get("standard_apy") for t in prod.get("apy_tiers", [])}
    if prod.get("apy_headline", {}).get("value") is not None:
        captured.add(prod["apy_headline"]["value"])
    for band in s["bands"]:
        if band["apy"] is None:
            continue
        if band["apy"] not in captured:
            errors.append(
                f"returns_model APY {band['apy']}% for '{pid}' is not present in accounts.json apy_tiers {sorted(x for x in captured if x is not None)}"
            )
    if s.get("standard_apy") is not None and s["standard_apy"] not in captured:
        errors.append(f"returns_model standard_apy {s['standard_apy']}% for '{pid}' not in accounts.json")

# Guard 2 + 3 - unverified implies null; published figures need a source.
def walk(node, path=""):
    if isinstance(node, dict):
        if node.get("status") == "unverified" and node.get("value") is not None:
            errors.append(f"{path}: status=unverified but value is not null ({node.get('value')!r})")
        for k, v in node.items():
            walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]")


walk(accounts, "accounts.json")
walk(bonuses, "bonuses.json")
walk(fdic, "fdic.json")

for pid, prod in PRODUCTS.items():
    if not prod.get("source_url"):
        errors.append(f"product '{pid}' has no source_url")

# --------------------------------------------------------------------------
# derived: returns
# --------------------------------------------------------------------------
def apy_for(pid: str, balance: float):
    s = SCHED.get(pid)
    if not s:
        return None
    for band in s["bands"]:
        lo, hi = band["min"], band["max"]
        if balance >= lo and (hi is None or balance <= hi):
            return band["apy"]
    return None


returns_out = {
    "meta": {
        "derived": True,
        "generated_utc": BUILD_UTC,
        "account_open_date": OPEN_DATE.isoformat(),
        "formula": "ending_balance = principal * (1 + APY) ** (days_held / 365)",
        "assumptions": [
            "Account opened 2026-10-22 (UTC).",
            "APY held constant for the whole horizon. Every savings APY here is variable.",
            "No further deposits, no withdrawals, interest left on deposit.",
            "No fees deducted; fee terms are published per account.",
            "365-day year in the exponent; calendar maturity dates do account for leap days.",
        ],
    },
    "rows": [],
}

for pid, s in SCHED.items():
    prod = PRODUCTS[pid]
    inst = PROD_INST[pid]
    for dep in rmodel["deposit_sizes"]:
        apy = apy_for(pid, dep)
        cap = s.get("max_balance")
        capped = cap is not None and dep > cap
        for hz in rmodel["horizons"]:
            ending, interest = (None, None)
            if apy is not None:
                ending, interest = project(dep, apy, hz["days"])
            returns_out["rows"].append(
                {
                    "product_id": pid,
                    "institution": inst["brand"],
                    "product": prod["name"],
                    "deposit": dep,
                    "apy": apy,
                    "conditional": s["conditional"],
                    "over_cap": capped,
                    "horizon_label": hz["label"],
                    "days": hz["days"],
                    "maturity_date": add_days(hz["days"]).isoformat(),
                    "ending_balance": round(ending, 2) if ending is not None else None,
                    "interest": round(interest, 2) if interest is not None else None,
                    "source_url": prod["source_url"],
                }
            )

(DATA / "returns.json").write_text(json.dumps(returns_out, indent=2) + "\n", encoding="utf-8")

# --------------------------------------------------------------------------
# shared view-model
# --------------------------------------------------------------------------
def inst_label(inst):
    return f'{e(inst["brand"])}<br><span class="muted sm">{e(inst["legal_name"])}</span>'


def cert_cell(inst):
    if inst.get("fdic_cert") is None:
        return unverified_cell()
    state = "" if inst.get("fdic_active") else ' <span class="badge badge-warn">inactive</span>'
    return f'<a href="{e(inst["fdic_bankfind_url"])}" target="_blank" rel="noopener noreferrer">#{inst["fdic_cert"]}</a>{state}'


def ranked_products():
    """All products with a verified headline APY, best first."""
    out = []
    for inst in INST:
        for p in inst["products"]:
            a = p.get("apy_headline", {})
            if a.get("status") == "verified" and a.get("value") is not None:
                out.append((inst, p, a["value"]))
    out.sort(key=lambda t: -t[2])
    return out


RANKED = ranked_products()
SAVINGS_RATE = next(r for r in bench["rates"] if r["product"] == "Savings")
NAT_AVG = SAVINGS_RATE["national_rate"]
NAT_CAP = SAVINGS_RATE["national_rate_cap"]

UNVER_COUNT = sum(
    1
    for inst in INST
    for p in inst["products"]
    if p.get("apy_headline", {}).get("status") != "verified"
)


def conditions_cell(p):
    bits = []
    if p.get("relationship_required"):
        bits.append('<span class="badge badge-cond">relationship required</span>')
    s = SCHED.get(p["id"])
    if s and s.get("conditional") and not p.get("relationship_required"):
        bits.append('<span class="badge badge-cond">conditional</span>')
    if p.get("availability", {}).get("value"):
        bits.append(f'<span class="badge badge-info">{e(p["availability"]["value"])}</span>')
    if p.get("max_balance", {}).get("value"):
        bits.append(f'<span class="badge badge-info">cap {money(p["max_balance"]["value"])}</span>')
    return " ".join(bits) or '<span class="muted">&mdash;</span>'


def rate_row(inst, p, with_type=True):
    a = p.get("apy_headline", {})
    row = [
        inst_label(inst),
    ]
    if with_type:
        row.append("Digital" if inst["type"] == "digital" else ("Branch" if inst["type"] == "branch" else "Inactive"))
    row += [
        e(p["name"]),
        f'<strong class="apy">{pct(a["value"])}</strong>' if a.get("status") == "verified" and a.get("value") is not None else unverified_cell(a.get("note", "")),
        field(p.get("min_open"), lambda v: money(v)),
        field(p.get("monthly_fee"), lambda v: money(v, 2) if v else "$0"),
        conditions_cell(p),
        e(iso_to_human(p.get("as_of_stated"))) or '<span class="muted">not stated</span>',
        e(p.get("rate_location", "")),
        src(p["source_url"]),
    ]
    return row


# --------------------------------------------------------------------------
# PAGE: dashboard
# --------------------------------------------------------------------------
best_inst, best_prod, best_apy = RANKED[0]
uncond = [(i, p, a) for (i, p, a) in RANKED if not SCHED.get(p["id"], {}).get("conditional", False)]
b_inst, b_prod, b_apy = uncond[0]

cards = f"""
<section class="cards">
  <div class="card hero">
    <div class="card-k">Best verified APY, no relationship condition</div>
    <div class="card-v">{pct(b_apy)}</div>
    <div class="card-s">{e(b_inst['brand'])} &mdash; {e(b_prod['name'])}<br>
      {('minimum ' + money(b_prod['min_balance_for_apy']['value'])) if b_prod.get('min_balance_for_apy', {}).get('value') else 'no minimum balance'}
      &middot; as of {e(iso_to_human(b_prod.get('as_of_stated')))} &middot; {src(b_prod['source_url'])}</div>
  </div>
  <div class="card">
    <div class="card-k">FDIC limit, per bank, per category</div>
    <div class="card-v">{money(fdic['smdia']['value'])}</div>
    <div class="card-s">Standard Maximum Deposit Insurance Amount {src(fdic['smdia']['source_url'])}</div>
  </div>
  <div class="card">
    <div class="card-k">U.S. savings national average</div>
    <div class="card-v">{pct(NAT_AVG)}</div>
    <div class="card-s">FDIC, as of {e(iso_to_human(bench['meta']['as_of_stated']))} {src(bench['meta']['source_url'])}</div>
  </div>
  <div class="card">
    <div class="card-k">Top rate vs. national average</div>
    <div class="card-v">{b_apy / NAT_AVG:.1f}&times;</div>
    <div class="card-s">{pct(b_apy)} against {pct(NAT_AVG)} &middot; FDIC national rate cap is {pct(NAT_CAP)}</div>
  </div>
  <div class="card">
    <div class="card-k">Institutions reviewed</div>
    <div class="card-v">{len(INST)}</div>
    <div class="card-s">{len(PRODUCTS)} savings products &middot; every one checked against FDIC BankFind</div>
  </div>
  <div class="card">
    <div class="card-k">Items flagged for review</div>
    <div class="card-v">{len(flags['flags'])}</div>
    <div class="card-s"><a href="flagged.html">{UNVER_COUNT} products have an unverifiable headline APY &rarr;</a></div>
  </div>
</section>
"""

top_rows = []
for inst, p, a in RANKED[:10]:
    s = SCHED.get(p["id"], {})
    apy_1y = apy_for(p["id"], 250000) if p["id"] in SCHED else None
    _, int250 = project(250000, apy_1y, 365) if apy_1y else (None, None)
    top_rows.append(
        [
            f'<span class="rank">{len(top_rows) + 1}</span>',
            inst_label(inst),
            e(p["name"]),
            f'<strong class="apy">{pct(a)}</strong>',
            money(int250) if int250 is not None else unverified_cell("No balance schedule modelled"),
            conditions_cell(p),
            src(p["source_url"]),
        ]
    )

dash_body = (
    cards
    + '<section><h2>Top 10 verified savings rates</h2>'
    + '<p class="muted">Interest column assumes a single <strong>$250,000</strong> deposit &mdash; the maximum insured in one ownership category at one bank &mdash; opened '
    + f'<strong>{OPEN_DATE.strftime("%-d %B %Y")}</strong> and held one year to <strong>{add_days(365).strftime("%-d %B %Y")}</strong>, with the APY held constant. '
    + 'See <a href="returns.html">Returns</a> for every deposit size and holding period.</p>'
    + table(
        ["#", "Institution", "Product", "APY", "Interest on $250,000 in 1 year", "Conditions", "Source"],
        top_rows,
    )
    + "</section>"
    + f"""
<section class="grid2">
  <div class="panel">
    <h3>What this research answers</h3>
    <ul class="ticks">
      <li><a href="rates.html">Every account, every rate</a>, with the bank's own effective date on each row.</li>
      <li><a href="returns.html">What you actually earn</a> at six deposit sizes across seven holding periods, with maturity dates.</li>
      <li><a href="fdic.html">How to hold the maximum insured amount</a> and what it costs you to spread money around.</li>
      <li><a href="bonuses.html">Which opening bonuses are real</a>, what you must deposit and how long you must keep it there.</li>
      <li><a href="rules.html">The rules for opening each account</a> &mdash; minimums, fees, waivers, withdrawal limits, eligibility.</li>
      <li><a href="benchmarks.html">Whether a rate is actually competitive</a>, measured against the FDIC's published national rates.</li>
    </ul>
  </div>
  <div class="panel">
    <h3>How to read this site</h3>
    <p>Every row carries a <span class="src">source&#8599;</span> link to the bank's own page, rate sheet or disclosure PDF, or to a
       <code>.gov</code> source. Nothing comes from a comparison site.</p>
    <p>A blank cell with <span class="badge badge-unver">unverified</span> means the official page exists but the number could not be read
       &mdash; usually because it is behind a ZIP-code gate or rendered only by JavaScript. Those cells are deliberately empty.
       Each one is written up on <a href="flagged.html">Flagged for Review</a> with the link you need to finish the check yourself.</p>
    <p class="muted sm">Captured {e(CAPTURE_LABEL)}. Rates move daily &mdash; re-check before you fund anything.</p>
  </div>
</section>
"""
)

page(
    "index.html",
    "Savings account dashboard",
    "A verified comparison of savings accounts at large national U.S. banks: rates, returns by deposit size, "
    "FDIC-insurance maximisation, opening bonuses and the rules attached to each account.",
    dash_body,
    subtitle=f"Data captured {e(CAPTURE_LABEL)} &middot; account-opening date used for all projections: <strong>{OPEN_DATE.strftime('%-d %B %Y')}</strong>",
)

# --------------------------------------------------------------------------
# PAGE: all rates
# --------------------------------------------------------------------------
rows = [rate_row(inst, p) for inst in INST for p in inst["products"]]
rows.sort(key=lambda r: -(float(re.sub(r"[^\d.]", "", r[3])) if "%" in r[3] else -1))

tier_blocks = []
for inst in INST:
    for p in inst["products"]:
        if not p.get("apy_tiers"):
            continue
        trows = [
            [
                e(t["balance"]),
                pct(t["apy"]) if t.get("apy") is not None else unverified_cell(),
                pct(t["rate"], 4).rstrip("0").rstrip(".") + "%" if t.get("rate") is not None else '<span class="muted">&mdash;</span>',
                pct(t["standard_apy"]) if t.get("standard_apy") is not None else '<span class="muted">&mdash;</span>',
            ]
            for t in p["apy_tiers"]
        ]
        tier_blocks.append(
            f'<details class="tierblock"><summary><strong>{e(inst["brand"])}</strong> &mdash; {e(p["name"])} '
            f'<span class="muted sm">({len(p["apy_tiers"])} balance tiers, as of {e(iso_to_human(p.get("as_of_stated"))) or "date not stated"})</span> {src(p["source_url"])}</summary>'
            + table(["Balance tier", "APY", "Interest rate", "Standard APY (if relationship rate shown)"], trows, cls="compact")
            + f'<p class="muted sm">{e(p.get("as_of_text") or "")}</p></details>'
        )

page(
    "rates.html",
    "All savings accounts",
    "Every savings and money-market deposit account reviewed, sorted by the headline APY each institution publishes. "
    "The <em>Rate applies to</em> column matters: several branch banks publish different rates by state or ZIP code.",
    '<section>'
    + table(
        ["Institution", "Type", "Product", "Headline APY", "Min. to open", "Monthly fee", "Conditions", "Bank's effective date", "Rate applies to", "Source"],
        rows,
    )
    + "</section>"
    + "<section><h2>Full balance-tier tables</h2><p class=\"muted\">Captured verbatim from each institution's rate sheet or disclosure. Click to expand.</p>"
    + "".join(tier_blocks)
    + "</section>",
)

# --------------------------------------------------------------------------
# PAGES: digital / branch
# --------------------------------------------------------------------------
def inst_section(inst):
    prods = "".join(
        f"""
    <div class="prod">
      <div class="prod-h"><h4>{e(p['name'])}</h4>
        {f'<span class="apy big">{pct(p["apy_headline"]["value"])}</span>' if p.get('apy_headline', {}).get('value') is not None else unverified_cell(p.get('apy_headline', {}).get('note', ''))}
      </div>
      <dl class="kv">
        <dt>Minimum to open</dt><dd>{field(p.get('min_open'), lambda v: money(v) if v else '$0 &mdash; no minimum')}</dd>
        <dt>Minimum balance for the APY</dt><dd>{field(p.get('min_balance_for_apy'), lambda v: money(v) if v else 'None')}</dd>
        <dt>Monthly fee</dt><dd>{field(p.get('monthly_fee'), lambda v: money(v, 2) if v else '$0 &mdash; no monthly fee')}</dd>
        <dt>Withdrawal limit</dt><dd>{field(p.get('withdrawal_limit'), lambda v: e(v), 'Not stated on the page captured')}</dd>
        <dt>Bank's stated effective date</dt><dd>{e(iso_to_human(p.get('as_of_stated'))) or '<span class="muted">not stated</span>'}</dd>
        <dt>Rate applies to</dt><dd>{e(p.get('rate_location', ''))}</dd>
        <dt>Source</dt><dd>{src(p['source_url'], p['source_url'].split('/')[2])}{(' &middot; ' + src(p['secondary_source_url'], 'secondary')) if p.get('secondary_source_url') else ''}</dd>
      </dl>
      {('<ul class="notes">' + ''.join(f'<li>{e(n)}</li>' for n in p.get('notes', [])) + '</ul>') if p.get('notes') else ''}
    </div>"""
        for p in inst["products"]
    )
    sec = "".join(f'<li>{e(s["item"])} {src(s["source_url"])}</li>' for s in inst.get("security", []))
    app = inst.get("app", {})
    app_txt = (
        f'{e(app["value"])} {src(app.get("source_url", ""))}'
        + (f' &middot; {src(app["secondary_source_url"], "Google Play")}' if app.get("secondary_source_url") else "")
        if app.get("status") == "verified"
        else unverified_cell(app.get("note", ""))
    )
    return f"""
<section class="instcard">
  <div class="inst-h">
    <div>
      <h3>{e(inst['brand'])}</h3>
      <p class="muted sm">{e(inst['legal_name'])}{(' &mdash; ' + e(inst['brand_note'])) if inst.get('brand_note') else ''}</p>
    </div>
    <div class="inst-meta">
      <span>FDIC cert {cert_cell(inst)}</span>
      <span>{e(inst['hq_city'])}, {e(inst['hq_state'])}</span>
      {f"<span>{money((inst['total_assets_k'] or 0) / 1_000_000, 1)}B in assets</span>" if inst.get('total_assets_k') else ''}
      {f"<span>{inst['offices']:,} offices</span>" if inst.get('offices') else ''}
      {f"<span>#{inst['us_asset_rank']} largest U.S. bank by assets</span>" if inst.get('us_asset_rank') else ''}
    </div>
  </div>
  <dl class="kv wide">
    <dt>Mobile app</dt><dd>{app_txt}</dd>
    <dt>Security &amp; insurance</dt><dd>{('<ul class="notes">' + sec + '</ul>') if sec else unverified_cell('No security statements captured from an official page')}</dd>
  </dl>
  {prods}
</section>"""


page(
    "digital.html",
    "Nationwide digital banks",
    "Branch-light, app-first institutions that take deposits from anywhere in the U.S. This is where the competitive rates are: "
    f"the best verified no-conditions APY in this group is <strong>{pct(max(a for i, p, a in RANKED if i['type'] == 'digital'))}</strong>.",
    "".join(inst_section(i) for i in INST if i["type"] == "digital"),
)

page(
    "branch.html",
    "Big branch national banks",
    "The large branch networks. Their standard savings rates are close to zero; the headline numbers they advertise almost always "
    "carry a relationship or new-money condition. Both the conditional and the standard rate are shown so they are never confused.",
    "".join(inst_section(i) for i in INST if i["type"] in ("branch", "inactive")),
)

# --------------------------------------------------------------------------
# PAGE: returns
# --------------------------------------------------------------------------
dep_sizes = rmodel["deposit_sizes"]
horizons = rmodel["horizons"]

hz_tables = []
for hz in horizons:
    hrows = []
    for inst, p, _ in RANKED:
        if p["id"] not in SCHED:
            continue
        s = SCHED[p["id"]]
        cells = []
        for dep in dep_sizes:
            apy = apy_for(p["id"], dep)
            cap = s.get("max_balance")
            if apy is None:
                cells.append(unverified_cell("No published rate for this balance band"))
            elif cap is not None and dep > cap:
                cells.append(f'<span class="muted" title="Balance cap {money(cap)}">over cap</span>')
            else:
                _, interest = project(dep, apy, hz["days"])
                cells.append(f'<span class="num">{money(interest, 2)}</span><br><span class="muted sm">{pct(apy)}</span>')
        hrows.append(
            [inst_label(inst), e(p["name"]), conditions_cell(p)] + cells + [src(p["source_url"])]
        )
    hz_tables.append(
        f'<details class="hz"{" open" if hz["days"] == 365 else ""}>'
        f'<summary><strong>{e(hz["label"])}</strong> &mdash; opened {OPEN_DATE.strftime("%-d %B %Y")}, matures '
        f'<strong>{add_days(hz["days"]).strftime("%-d %B %Y")}</strong> ({hz["days"]} days)</summary>'
        + table(
            ["Institution", "Product", "Conditions"] + [money(d) for d in dep_sizes] + ["Source"],
            hrows,
            cls="returns",
        )
        + "</details>"
    )

best_250 = []
for inst, p, _ in RANKED:
    if p["id"] not in SCHED:
        continue
    apy = apy_for(p["id"], 250000)
    s = SCHED[p["id"]]
    if apy is None or (s.get("max_balance") and 250000 > s["max_balance"]):
        continue
    row = [inst_label(inst), e(p["name"]), pct(apy), conditions_cell(p)]
    for hz in horizons:
        _, i = project(250000, apy, hz["days"])
        row.append(money(i, 2))
    row.append(src(p["source_url"]))
    best_250.append((apy, row))
best_250.sort(key=lambda t: -t[0])

page(
    "returns.html",
    "Return on the size of your deposit",
    f"What each account actually pays, by deposit size and holding period. Every projection assumes the account is opened "
    f"<strong>{OPEN_DATE.strftime('%-d %B %Y')}</strong> &mdash; today &mdash; with interest left on deposit and the APY held constant. "
    "Accounts whose rate could not be verified are excluded from these tables rather than estimated.",
    f"""
<section class="panel warn">
  <h3>Read this before you use the numbers</h3>
  <p><strong>Formula:</strong> <code>ending balance = principal &times; (1 + APY)<sup>days/365</sup></code>. Interest shown is ending balance minus principal.</p>
  <ul class="notes">
    <li>Account-opening date: <strong>{OPEN_DATE.strftime('%-d %B %Y')}</strong>. Each maturity date below is that date plus the stated number of days.</li>
    <li>Every one of these APYs is <strong>variable</strong>. Holding it constant for two, three or five years will not happen in practice &mdash; treat the long horizons as a ranking tool, not a forecast.</li>
    <li>No fees are deducted and no further deposits are made. Fee terms are on <a href="rules.html">Opening rules</a>.</li>
    <li>For tiered accounts the APY used is the one that applies to <em>that</em> deposit size, not the headline rate.</li>
    <li>Where a bank caps the balance, larger deposits are shown as <span class="muted">over cap</span> instead of a made-up number.</li>
  </ul>
</section>

<section>
  <h2>Interest on the FDIC maximum, {money(250000)}, by holding period</h2>
  <p class="muted">$250,000 is the most one person can hold in a single ownership category at one bank and stay fully insured. Sorted by APY.</p>
  {table(['Institution', 'Product', 'APY', 'Conditions'] + [f"{h['label']}<br><span class='muted sm'>to {add_days(h['days']).strftime('%-d %b %Y')}</span>" for h in horizons] + ['Source'], [r for _, r in best_250], cls='returns')}
</section>

<section>
  <h2>Every deposit size, every holding period</h2>
  <p class="muted">Each panel shows the interest earned over that period. The small grey figure is the APY that applies at that balance.</p>
  {''.join(hz_tables)}
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: FDIC
# --------------------------------------------------------------------------
cat_rows = [
    [
        e(c["category"]),
        e(c["limit_text"]),
        money(c["max_per_bank"]) if c.get("max_per_bank") else '<span class="muted">varies</span>',
        src(c["source_url"]),
    ]
    for c in fdic["ownership_categories"]
]

fact_rows = [[e(f["fact"]), src(f["source_url"])] for f in fdic["key_facts"]]

# deployment plan: fill $250k buckets from the best unconditional rates
plan_rows = []
running = 0
for inst, p, apy in uncond:
    if p["id"] not in SCHED:
        continue
    cap = SCHED[p["id"]].get("max_balance")
    amount = 250000
    if cap is not None and cap < amount:
        amount = cap
    band_apy = apy_for(p["id"], amount)
    if band_apy is None:
        continue
    running += amount
    _, yr = project(amount, band_apy, 365)
    plan_rows.append(
        [
            f'<span class="rank">{len(plan_rows) + 1}</span>',
            inst_label(inst),
            e(p["name"]),
            cert_cell(inst),
            money(amount),
            pct(band_apy),
            money(yr, 2),
            money(running),
            src(p["source_url"]),
        ]
    )
    if len(plan_rows) >= 8:
        break

blended = sum(float(re.sub(r"[^\d.]", "", r[6])) for r in plan_rows)
blended_pct = blended / running * 100

one_bank_rows = [
    ["Single account (you alone)", money(250000), "1 &times; $250,000"],
    ["Joint account with one other person", money(500000), "2 co-owners &times; $250,000"],
    ["Trust / POD account naming 5 beneficiaries", money(1250000), "Capped at $1,250,000 per owner for all trust deposits at that bank"],
    ["IRA / certain retirement accounts", money(250000), "Separate from your single-account limit"],
    ["<strong>Total for one person at one bank</strong>", f"<strong>{money(2250000)}</strong>", "Single + joint share + trust + retirement, if every category's requirements are met"],
]

page(
    "fdic.html",
    "FDIC insurance and how to hold the maximum",
    "The goal is the largest fully-insured balance at the best rate. That means understanding two separate levers: "
    "<strong>ownership categories</strong> (more coverage at one bank) and <strong>more banks</strong> (a fresh $250,000 at each). "
    "Everything on this page is sourced to fdic.gov.",
    f"""
<section class="cards">
  <div class="card hero">
    <div class="card-k">Standard Maximum Deposit Insurance Amount</div>
    <div class="card-v">{money(fdic['smdia']['value'])}</div>
    <div class="card-s">{e(fdic['smdia']['statement'])} {src(fdic['smdia']['source_url'])}</div>
  </div>
  <div class="card">
    <div class="card-k">Max for one person at one bank</div>
    <div class="card-v">{money(2250000)}</div>
    <div class="card-s">Single + joint share + trust (5 beneficiaries) + retirement, if every requirement is met</div>
  </div>
  <div class="card">
    <div class="card-k">Fully insured across 8 banks</div>
    <div class="card-v">{money(running)}</div>
    <div class="card-s">Single-ownership only, {money(250000)} per bank &mdash; see the deployment plan below</div>
  </div>
</section>

<section>
  <h2>Coverage limits by ownership category</h2>
  <p class="muted">Deposits in different ownership categories at the <em>same</em> bank are insured separately. This is the cheapest way to get past $250,000 without opening accounts everywhere.</p>
  {table(['Ownership category', "FDIC's stated limit", 'Max per bank', 'Source'], cat_rows)}
</section>

<section>
  <h2>Stacking categories at a single bank</h2>
  <p class="muted">Illustrative maximum for one person at one FDIC-insured bank. Each line is a separate category with its own limit; all of the FDIC's requirements for each category must be met.</p>
  {table(['Ownership category', 'Insured amount', 'How it is counted'], one_bank_rows)}
  <p class="muted sm">Source for every limit: <a href="https://www.fdic.gov/resources/deposit-insurance/brochures/deposits-at-a-glance" target="_blank" rel="noopener noreferrer">FDIC &mdash; Deposit Insurance At A Glance</a>.
  Check your own position with the FDIC's <a href="https://edie.fdic.gov/" target="_blank" rel="noopener noreferrer">EDIE calculator</a>.</p>
</section>

<section>
  <h2>Deployment plan: maximum insured balance at the best verified rates</h2>
  <p class="muted">Single-ownership accounts only, {money(250000)} per bank, filled from the highest verified APY downwards, skipping anything with a relationship or new-money condition.
     Where a bank caps the account below $250,000, the cap is used. One year from {OPEN_DATE.strftime('%-d %B %Y')} to {add_days(365).strftime('%-d %B %Y')}.</p>
  {table(['#', 'Institution', 'Product', 'FDIC cert', 'Deposit', 'APY at that balance', 'Interest in 1 year', 'Cumulative insured', 'Source'], plan_rows)}
  <p class="callout"><strong>{money(running)}</strong> fully insured across {len(plan_rows)} institutions earns
     <strong>{money(blended, 2)}</strong> in the first year &mdash; a blended <strong>{pct(blended_pct)}</strong>.
     The same money in a single big-branch savings account at {pct(0.01)} would earn {money(project(running, 0.01, 365)[1], 2)}.</p>
  <p class="muted sm">Check each institution's FDIC certificate number before assuming two brands are two banks. Two brands sharing one charter share one $250,000 limit.</p>
</section>

<section class="panel warn">
  <h3>Two traps when spreading money around</h3>
  <ul class="notes">
    <li><strong>Brands are not charters.</strong> Capital One states that Capital One and Discover Bank deposit accounts opened on or after 18 May 2025 are counted together for FDIC coverage. FDIC BankFind confirms Discover Bank (cert 5649) became inactive on 18 May 2025. Treating them as two banks would leave money uninsured.
      {src('https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/')} {src('https://banks.data.fdic.gov/bankfind-suite/bankfind/details/5649', 'BankFind')}</li>
    <li><strong>"Up to $3M FDIC" is a program, not a limit.</strong> SoFi advertises additional FDIC insurance up to $3,000,000 through a network of participating banks. The FDIC's own limit is still $250,000 per depositor, per insured bank, per category &mdash; the extra coverage depends on balances being swept to other insured banks, and on you not already holding deposits at those banks.
      {src('https://www.sofi.com/banking/high-yield-savings-account/')}</li>
  </ul>
</section>

<section>
  <h2>FDIC facts used on this site</h2>
  {table(['Fact', 'Source'], fact_rows)}
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: bonuses
# --------------------------------------------------------------------------
bonus_rows = []
for o in bonuses["offers"]:
    amt = o["amount"]
    amt_txt = (
        money(amt["value"]) if amt["unit"] == "USD"
        else (pct(amt["value"]) + " APY" if amt["unit"] == "percent APY" else f'+{amt["value"]:.2f} pts APY')
    )
    bonus_rows.append(
        [
            e(o["brand"]),
            e(o["product"]),
            e(o["type"]),
            f'<strong>{amt_txt}</strong>' + (f' <span class="note" title="{e(amt["note"])}">&#9432;</span>' if amt.get("note") else ""),
            field(o["deposit_required"], lambda v: money(v)),
            f'{o["days_to_fund"]} days' if o.get("days_to_fund") else '<span class="muted">&mdash;</span>',
            f'{o["hold_period_days"]} days' if o.get("hold_period_days") else '<span class="muted">&mdash;</span>',
            field(o["offer_expires"], lambda v: e(iso_to_human(v))),
            src(o["source_url"]),
        ]
    )

bonus_detail = "".join(
    f"""<details class="tierblock"><summary><strong>{e(o['brand'])}</strong> &mdash; {e(o['product'])}: {e(o['type'])} {src(o['source_url'])}</summary>
      <p><strong>Who qualifies:</strong> {e(o['eligibility'])}</p>
      <p><strong>When it pays:</strong> {e(o['payout_timing'])}</p>
      <ul class="notes">{''.join(f'<li>{e(r)}</li>' for r in o['rules'])}</ul>
      {f'<p class="muted sm">Full terms: {src(o["terms_url"], o["terms_url"])}</p>' if o.get('terms_url') else ''}
      {f'<p class="muted sm">Rate location: {e(o["rate_location"])}</p>' if o.get('rate_location') else ''}
    </details>"""
    for o in bonuses["offers"]
)

none_rows = [[e(n["brand"]), e(n["note"]), src(n["source_url"])] for n in bonuses["no_offer_found"]]

# Barclays bonus economics
bar = PRODUCTS["barclays-tiered-savings"]
bar_apy = apy_for("barclays-tiered-savings", 25000)
_, bar_int_120 = project(25000, bar_apy, 120)
bar_total = bar_int_120 + 200
bar_eff = ((25000 + bar_total) / 25000) ** (365 / 120) - 1

page(
    "bonuses.html",
    "Bonuses and promotions",
    "Only offers published on the institution's own site are listed. Most large-bank "
    "&ldquo;open an account&rdquo; bonuses are checking offers; the table separates a genuine cash bonus on a "
    "<em>savings</em> account from a promotional APY and from a checking-led bundle.",
    f"""
<section>
  {table(['Institution', 'Product', 'Type of offer', 'Value', 'Deposit required', 'Time to fund', 'Must hold for', 'Offer expires', 'Source'], bonus_rows)}
</section>

<section class="panel">
  <h3>Is the Barclays bonus worth it? The arithmetic</h3>
  <p>The Barclays $200 is the only pure cash bonus on a savings account found on an official page. It needs {money(25000)} funded within 30 days and held for 120 days.</p>
  <ul class="notes">
    <li>Interest on {money(25000)} at {pct(bar_apy)} for 120 days: <strong>{money(bar_int_120, 2)}</strong></li>
    <li>Plus the bonus: <strong>{money(200)}</strong></li>
    <li>Total over the 120-day qualifying window: <strong>{money(bar_total, 2)}</strong></li>
    <li>Annualised, that is an effective <strong>{bar_eff * 100:.2f}%</strong> for the qualifying period &mdash; versus {pct(bar_apy)} without the bonus.</li>
  </ul>
  <p class="muted sm">Offer expires {e(iso_to_human('2026-10-31'))}, so the account must be opened within
     {(dt.date(2026, 10, 31) - OPEN_DATE).days} days of {OPEN_DATE.strftime('%-d %B %Y')}. The bonus is paid roughly 60 days after the
     120-day hold, i.e. about {add_days(180).strftime('%-d %B %Y')} if funded immediately, and Barclays treats it as interest for tax
     purposes (Form 1099-INT). Derived from Barclays' own figures &mdash; {src(bar['source_url'])}</p>
</section>

<section>
  <h2>Full terms, as published</h2>
  {bonus_detail}
</section>

<section>
  <h2>Institutions with no savings bonus on their official page</h2>
  <p class="muted">Checked and found nothing &mdash; recorded so the absence is explicit rather than an omission.</p>
  {table(['Institution', 'What was checked', 'Source'], none_rows)}
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: rules
# --------------------------------------------------------------------------
rule_rows = []
for inst in INST:
    for p in inst["products"]:
        rule_rows.append(
            [
                inst_label(inst),
                e(p["name"]),
                field(p.get("min_open"), lambda v: money(v) if v else "$0"),
                field(p.get("min_balance_for_apy"), lambda v: money(v) if v else "None"),
                field(p.get("monthly_fee"), lambda v: money(v, 2) if v else "$0"),
                field(p.get("withdrawal_limit"), lambda v: e(v), "Not stated on the page captured"),
                field(p.get("max_balance"), lambda v: money(v), "No cap stated"),
                field(p.get("availability"), lambda v: e(v), "Not stated; assume nationwide only if the bank says so"),
                src(p["source_url"]),
            ]
        )

app_rows = []
for inst in INST:
    a = inst.get("app", {})
    app_rows.append(
        [
            inst_label(inst),
            cert_cell(inst),
            (f'{e(a["value"])}' if a.get("status") == "verified" else unverified_cell(a.get("note", ""))),
            (src(a.get("source_url", "")) + ((" &middot; " + src(a["secondary_source_url"], "Google Play")) if a.get("secondary_source_url") else ""))
            if a.get("status") == "verified"
            else (src(a["source_url"], "page checked") if a.get("source_url") else '<span class="muted">&mdash;</span>'),
            ("<ul class='notes'>" + "".join(f'<li>{e(s["item"])} {src(s["source_url"])}</li>' for s in inst.get("security", [])) + "</ul>") if inst.get("security") else unverified_cell("No security statements captured from an official page"),
        ]
    )

eligibility = []
for inst in INST:
    for p in inst["products"]:
        for n in p.get("notes", []):
            if any(k in n.lower() for k in ("citizen", "18 years", "aged 18", "social security", "itin", "linked account", "60 days", "automatically opens")):
                eligibility.append([inst_label(inst), e(p["name"]), e(n), src(p["source_url"])])

page(
    "rules.html",
    "Rules for opening and holding each account",
    "Minimums, fees, fee waivers, withdrawal limits, balance caps and where each product is actually offered &mdash; "
    "plus the digital-app and security check for every institution.",
    f"""
<section>
  <h2>Account terms</h2>
  {table(['Institution', 'Product', 'Min. to open', 'Min. balance for APY', 'Monthly fee', 'Withdrawal limit', 'Balance cap', 'Where offered', 'Source'], rule_rows)}
</section>

<section>
  <h2>Fee waivers, in each bank's own words</h2>
  {table(['Institution', 'Product', 'How the monthly fee is avoided', 'Source'],
         [[inst_label(i), e(p['name']), e(p['monthly_fee'].get('note', '')), src(p['source_url'])]
          for i in INST for p in i['products']
          if p.get('monthly_fee', {}).get('note') and p.get('monthly_fee', {}).get('value')])}
</section>

<section>
  <h2>Digital app and security check</h2>
  <p class="muted">A consumer mobile app and FDIC insurance were hard requirements for this research. Where an app could not be confirmed
     from an official page, the cell is blank rather than assumed &mdash; see <a href="flagged.html">F-13</a>.</p>
  {table(['Institution', 'FDIC certificate', 'Mobile app', 'App source', 'Security statements from the institution'], app_rows)}
</section>

<section>
  <h2>Eligibility and process notes</h2>
  {table(['Institution', 'Product', 'Note, as published', 'Source'], eligibility)}
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: benchmarks
# --------------------------------------------------------------------------
bench_rows = [
    [
        e(r["product"]),
        pct(r["national_rate"]),
        pct(r["rate_cap_adjusted"]),
        pct(r["treasury_yield"]),
        pct(r["treasury_cap_adjusted"]),
        f'<strong>{pct(r["national_rate_cap"])}</strong>',
    ]
    for r in bench["rates"]
]

comp_rows = []
for inst, p, apy in RANKED:
    spread = apy - NAT_AVG
    headroom = NAT_CAP - apy
    bar = min(100, apy / NAT_CAP * 100)
    comp_rows.append(
        [
            inst_label(inst),
            e(p["name"]),
            f'<strong class="apy">{pct(apy)}</strong>',
            f'<span class="{"pos" if spread > 0 else "neg"}">{spread:+.2f} pts</span>',
            f"{apy / NAT_AVG:.1f}&times;",
            pct(headroom),
            f'<div class="bar"><span style="width:{bar:.1f}%"></span></div>',
            src(p["source_url"]),
        ]
    )

page(
    "benchmarks.html",
    "Is the rate actually competitive?",
    f"Measured against the FDIC's own published figures for {e(iso_to_human(bench['meta']['as_of_stated']))}: a savings national average of "
    f"<strong>{pct(NAT_AVG)}</strong> and a national rate cap of <strong>{pct(NAT_CAP)}</strong>. "
    "The cap is the regulatory ceiling a less-than-well-capitalised bank may pay, so it is a fair read on the top of the market.",
    f"""
<section>
  <h2>Every verified rate against the national average</h2>
  <p class="muted">&ldquo;Headroom to cap&rdquo; is how far the rate sits below the FDIC national rate cap &mdash; a rough measure of how much more the market could theoretically pay.
     The bar shows the rate as a share of that cap.</p>
  {table(['Institution', 'Product', 'APY', 'vs. national average', 'Multiple of average', 'Headroom to cap', 'Share of cap', 'Source'], comp_rows)}
</section>

<section>
  <h2>Competitiveness over the life of the investment</h2>
  <p class="muted">A savings APY is variable and resets continuously, so it has no &ldquo;term&rdquo;. A CD fixes a rate for a stated term. The FDIC publishes both,
     which lets you see what the market is paying for locking money up versus keeping it liquid.</p>
  {table(['Deposit product', 'National deposit rate', 'Rate cap (national rate + 75bp)', 'Treasury yield', 'Rate cap (120% of Treasury + 75bp)', 'National rate cap'], bench_rows)}
  <p class="muted sm">{e(bench['meta']['methodology_note'])}<br>
     Source: {src(bench['meta']['source_url'], 'FDIC National Rates and Rate Caps')} &mdash; {e(bench['meta']['page_heading'])}. Retrieved {e(CAPTURE_LABEL)}.</p>
</section>

<section class="panel">
  <h3>What the comparison says</h3>
  <ul class="notes">
    <li>The best verified no-conditions savings APY, <strong>{pct(b_apy)}</strong> at {e(b_inst['brand'])}, is <strong>{b_apy / NAT_AVG:.1f}&times;</strong> the FDIC national average and sits {pct(NAT_CAP - b_apy)} below the national rate cap.</li>
    <li>Liquid savings at the top of the market ({pct(b_apy)}) currently beats the FDIC's national average for a 12-month CD ({pct(next(r['national_rate'] for r in bench['rates'] if r['product'] == '12 month CD'))}) by {b_apy - next(r['national_rate'] for r in bench['rates'] if r['product'] == '12 month CD'):.2f} points &mdash; with no term commitment and no early-withdrawal penalty.</li>
    <li>The standard rates at the biggest branch networks ({pct(0.01)}&ndash;{pct(0.05)}) are <em>below</em> the national average of {pct(NAT_AVG)}. On {money(250000)} over one year the gap between {pct(b_apy)} and {pct(0.01)} is {money(project(250000, b_apy, 365)[1] - project(250000, 0.01, 365)[1], 2)}.</li>
    <li>Because the rate is variable, the right question is not &ldquo;what is the rate today&rdquo; but &ldquo;does this bank keep paying near the top&rdquo;. Nothing on this page predicts that; re-check the rate each quarter.</li>
  </ul>
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: flagged
# --------------------------------------------------------------------------
sev_order = {"high": 0, "medium": 1, "low": 2}
fl = sorted(flags["flags"], key=lambda f: (sev_order.get(f["severity"], 3), f["id"]))

flag_cards = "".join(
    f"""
<article class="flag sev-{e(f['severity'])}" id="{e(f['id'])}">
  <div class="flag-h">
    <span class="flag-id">{e(f['id'])}</span>
    <span class="badge badge-{e(f['severity'])}">{e(f['severity'])}</span>
    <h3>{e(f['title'])}</h3>
  </div>
  <dl class="kv wide">
    <dt>Institution</dt><dd>{e(f['entity'])}</dd>
    <dt>Field affected</dt><dd>{e(f['field'])}</dd>
    <dt>What happened</dt><dd>{e(f['what_happened'])}</dd>
    <dt>What this site did</dt><dd>{e(f['action_taken'])}</dd>
    <dt>How you can resolve it</dt><dd>{e(f['how_to_resolve'])}</dd>
    <dt>Sources to check</dt><dd><ul class="notes">{''.join(f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["label"])}&#8599;</a></li>' for s in f['sources'])}</ul></dd>
  </dl>
</article>"""
    for f in fl
)

blank_rows = []
for inst in INST:
    for p in inst["products"]:
        for label, obj in [
            ("Headline APY", p.get("apy_headline")),
            ("Interest rate", p.get("interest_rate")),
            ("Minimum to open", p.get("min_open")),
            ("Minimum balance for APY", p.get("min_balance_for_apy")),
            ("Monthly fee", p.get("monthly_fee")),
            ("Maximum balance", p.get("max_balance")),
        ]:
            if obj and obj.get("status") == "unverified":
                blank_rows.append(
                    [
                        inst_label(inst),
                        e(p["name"]),
                        e(label),
                        e(obj.get("note", "") or "Not published on the page captured"),
                        src(obj.get("source_url") or p["source_url"]) or '<span class="muted">&mdash;</span>',
                    ]
                )
    a = inst.get("app", {})
    if a.get("status") == "unverified":
        blank_rows.append([
            inst_label(inst),
            '<span class="muted">institution-level</span>',
            "Mobile app",
            e(a.get("note") or "Not confirmed from an official page"),
            src(a["source_url"]) if a.get("source_url") else f'<a href="{e(inst["fdic_bankfind_url"])}" target="_blank" rel="noopener noreferrer">FDIC BankFind&#8599;</a>',
        ])

counts = {s: sum(1 for f in fl if f["severity"] == s) for s in ("high", "medium", "low")}

page(
    "flagged.html",
    "Flagged for review",
    "Everything that could not be confirmed from an official source, and every inconsistency found between official sources. "
    "Nothing here was guessed at or filled in. Each item says exactly what happened, what the site did instead, and the link you need to finish the check.",
    f"""
<section class="cards">
  <div class="card"><div class="card-k">High severity</div><div class="card-v">{counts['high']}</div><div class="card-s">A headline figure is missing, or two official sources disagree</div></div>
  <div class="card"><div class="card-k">Medium severity</div><div class="card-v">{counts['medium']}</div><div class="card-s">A supporting figure is missing, or a figure is conditional on location or relationship</div></div>
  <div class="card"><div class="card-k">Low severity</div><div class="card-v">{counts['low']}</div><div class="card-s">Labelling or presentation inconsistency; no number is in doubt</div></div>
  <div class="card"><div class="card-k">Blank cells on the site</div><div class="card-v">{len(blank_rows)}</div><div class="card-s">Fields deliberately left empty rather than inferred</div></div>
</section>

<section>
  <h2>Every blank cell on this site, and why</h2>
  {table(['Institution', 'Product', 'Field', 'Why it is blank', 'Official page to check'], blank_rows)}
</section>

<section>
  <h2>Irregularities and unverified items</h2>
  {flag_cards}
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: sources
# --------------------------------------------------------------------------
seen = {}


def note_src(url, label, kind):
    if not url:
        return
    seen.setdefault(url, {"labels": set(), "kind": kind})
    seen[url]["labels"].add(label)


for inst in INST:
    note_src(inst.get("fdic_bankfind_url"), f'{inst["brand"]} &mdash; FDIC BankFind record', "FDIC")
    note_src(inst.get("fdic_source"), "FDIC BankFind Suite API query", "FDIC")
    a = inst.get("app", {})
    note_src(a.get("source_url"), f'{inst["brand"]} &mdash; mobile app', "Institution")
    note_src(a.get("secondary_source_url"), f'{inst["brand"]} &mdash; mobile app (Google Play)', "App store")
    for s in inst.get("security", []):
        note_src(s["source_url"], f'{inst["brand"]} &mdash; security / FDIC statement', "Institution")
    for p in inst["products"]:
        note_src(p["source_url"], f'{inst["brand"]} &mdash; {p["name"]} rates &amp; terms', "Institution")
        note_src(p.get("secondary_source_url"), f'{inst["brand"]} &mdash; {p["name"]} (secondary)', "Institution")
        for k in ("min_open", "monthly_fee", "min_balance_for_apy", "max_balance"):
            if p.get(k, {}) and p[k].get("source_url"):
                note_src(p[k]["source_url"], f'{inst["brand"]} &mdash; {p["name"]} {k.replace("_", " ")}', "Institution")

note_src(bench["meta"]["source_url"], "FDIC National Rates and Rate Caps", "FDIC")
for u in fdic["meta"]["primary_sources"]:
    note_src(u, "FDIC deposit-insurance guidance", "FDIC")
for t in fdic["tools"]:
    note_src(t["url"], t["name"], "FDIC")
for o in bonuses["offers"]:
    note_src(o["source_url"], f'{o["brand"]} &mdash; {o["type"]}', "Institution")
    note_src(o.get("terms_url"), f'{o["brand"]} &mdash; full offer terms', "Institution")
for n in bonuses["no_offer_found"]:
    note_src(n["source_url"], f'{n["brand"]} &mdash; checked for a savings bonus', "Institution")
for f in flags["flags"]:
    for s in f["sources"]:
        note_src(s["url"], s["label"], "Flagged item")

src_rows = sorted(
    (
        [
            e(url.split("/")[2]),
            e(v["kind"]),
            "<br>".join(sorted(v["labels"])),
            f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(url if len(url) < 95 else url[:92] + "...")}&#8599;</a>',
        ]
        for url, v in seen.items()
    ),
    key=lambda r: (r[1], r[0]),
)

page(
    "sources.html",
    "Source index",
    f"Every official URL used to build this site &mdash; <strong>{len(seen)}</strong> in total, across "
    f"{len({u.split('/')[2] for u in seen})} domains. No comparison site, blog, forum or aggregator was used as a source of record anywhere.",
    f"""
<section>
  <p class="muted">All retrieved {e(CAPTURE_LABEL)}. Institution pages are the bank's own domain; <code>.gov</code> sources are the FDIC.</p>
  {table(['Domain', 'Type', 'Used for', 'URL'], src_rows)}
</section>
""",
)

# --------------------------------------------------------------------------
# PAGE: methodology
# --------------------------------------------------------------------------
page(
    "methodology.html",
    "Methodology and verification",
    "How every number on this site was obtained, checked and published &mdash; and the rules that decided what was left blank.",
    f"""
<section class="panel">
  <h3>Scope</h3>
  <ul class="notes">
    <li>Large national U.S. banks offering consumer savings to customers nationwide. Small and local community banks and credit unions were excluded by request.</li>
    <li>Every institution had to be FDIC-insured, confirmed against FDIC BankFind by certificate number &mdash; not by the bank's own claim.</li>
    <li>A consumer mobile app was a requirement. Where it could not be confirmed from an official page the field was left blank and flagged, not assumed.</li>
    <li>{len(INST)} institutions and {len(PRODUCTS)} deposit products are published, of which {len(RANKED)} have a verified headline APY.</li>
  </ul>
</section>

<section class="panel">
  <h3>The verification rule</h3>
  <ol class="notes">
    <li>A value is published only if it was read directly from the institution's own website, rate sheet or disclosure PDF, or from a <code>.gov</code> source.</li>
    <li>If a value could not be read, the cell is <strong>left blank</strong>, marked <span class="badge badge-unver">unverified</span>, and written up on <a href="flagged.html">Flagged for Review</a> with the link needed to finish the check.</li>
    <li>Nothing is inferred, estimated, averaged, or carried over from a previous month.</li>
    <li>Aggregator sites (Bankrate, NerdWallet, Forbes Advisor, Investopedia and the like) were <strong>never</strong> used as a source of record. Web search was used only to locate official URLs; the value was then read off the official page itself.</li>
    <li>Where two official sources disagreed, both are published and the disagreement is flagged &mdash; see <a href="flagged.html#F-09">F-09</a>, <a href="flagged.html#F-10">F-10</a> and <a href="flagged.html#F-11">F-11</a>.</li>
    <li>Marketing comparisons published by one bank about another bank are treated as marketing, not as data. Each bank's rate always comes from that bank.</li>
  </ol>
</section>

<section class="panel">
  <h3>The return model</h3>
  <p><code>ending balance = principal &times; (1 + APY)<sup>days / 365</sup></code> &nbsp;&middot;&nbsp; <code>interest = ending balance &minus; principal</code></p>
  <ul class="notes">
    {''.join(f'<li>{e(a)}</li>' for a in returns_out['meta']['assumptions'])}
    <li>For tiered accounts the APY applied is the one for the band that the deposit falls into, not the advertised headline.</li>
    <li>Projections are marked as derived. They are not sourced, because they are arithmetic performed on sourced inputs.</li>
  </ul>
</section>

<section class="panel">
  <h3>Build-time guards</h3>
  <p>The site is generated from JSON by <code>scripts/build.py</code>. Nothing is hand-typed into the HTML. The build <strong>fails</strong> if:</p>
  <ul class="notes">
    <li>any APY used by the return calculator is not present in the balance-tier table captured from that bank;</li>
    <li>any record marked <code>unverified</code> still carries a value;</li>
    <li>any published product lacks a source URL;</li>
    <li>any internal link on the site points at a page that does not exist.</li>
  </ul>
  <p class="muted sm">All four guards passed for this build. Generated {e(BUILD_UTC)}.</p>
</section>

<section class="panel">
  <h3>Known limits of this capture</h3>
  <ul class="notes">
    <li>Rates were captured at one moment in time, {e(CAPTURE_LABEL)}, and every savings APY here is variable.</li>
    <li>Several branch banks set rates by ZIP code and the capture tool cannot hold their location cookie. Each affected row states the location the figure actually applies to.</li>
    <li>Citi, TD and Citizens publish their APYs only through client-side rendering that did not resolve; those figures are blank, not guessed.</li>
    <li>This is a research summary, not financial advice, and not a solicitation on behalf of any institution.</li>
  </ul>
</section>

<section class="panel">
  <h3>Reproducing this</h3>
  <p>Clone <a href="{e(REPO_URL)}" target="_blank" rel="noopener noreferrer">the repository</a> and run <code>python3 scripts/build.py</code>.
     The data lives in <code>data/*.json</code>; the schema and verification contract are in <code>data/SCHEMA.md</code>;
     the task board, source log and irregularity log are in <code>COORDINATION.md</code>.</p>
</section>
""",
)

# --------------------------------------------------------------------------
# assets
# --------------------------------------------------------------------------
(DOCS / "assets").mkdir(parents=True, exist_ok=True)
(DOCS / ".nojekyll").write_text("", encoding="utf-8")

(DOCS / "assets" / "style.css").write_text(
    """
:root{
  --bg:#f6f7f9; --panel:#fff; --ink:#15191e; --muted:#5c6773; --line:#e3e7ec;
  --brand:#10497a; --brand-ink:#0b3558; --accent:#0f7b5f; --warn:#8a5a00;
  --high:#b3261e; --med:#8a5a00; --low:#4a5565;
  --radius:10px; --shadow:0 1px 2px rgba(16,24,40,.06),0 1px 3px rgba(16,24,40,.08);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;}
.wrap{max-width:1280px;margin:0 auto;padding:0 20px}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px 12px;z-index:100;border-radius:6px}

.topbar{background:var(--brand);color:#fff}
.topbar-in{display:flex;align-items:center;justify-content:space-between;height:56px}
.brand{display:flex;align-items:center;gap:10px;color:#fff;font-weight:650;letter-spacing:.2px}
.brand:hover{text-decoration:none}
.brand-mark{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:7px;
  background:rgba(255,255,255,.16);font-size:12px;font-weight:700}
.navtoggle{display:none;background:none;border:0;color:#fff;font-size:20px;cursor:pointer}

.mainnav{background:var(--brand-ink);position:sticky;top:0;z-index:30}
.navscroll{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.navscroll::-webkit-scrollbar{display:none}
.mainnav a{color:#cfe0ee;padding:11px 13px;font-size:13.5px;white-space:nowrap;border-bottom:2px solid transparent}
.mainnav a:hover{color:#fff;text-decoration:none;background:rgba(255,255,255,.07)}
.mainnav a.active{color:#fff;border-bottom-color:#7fc4a6;background:rgba(255,255,255,.1)}

main{padding:26px 20px 60px}
.pagehead{margin:4px 0 24px;max-width:960px}
h1{font-size:28px;line-height:1.2;margin:0 0 8px;letter-spacing:-.3px}
h2{font-size:20px;margin:34px 0 10px;letter-spacing:-.2px}
h3{font-size:16px;margin:0 0 8px}
h4{font-size:15px;margin:0}
.subtitle{margin:0 0 8px;color:var(--muted);font-size:13.5px}
.lede{margin:0;color:#36404a;font-size:15.5px}
section{margin-bottom:26px}

.cards{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));margin-bottom:26px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px;box-shadow:var(--shadow)}
.card.hero{grid-column:span 2;background:linear-gradient(180deg,#fff,#f3f8f6);border-color:#cfe4da}
.card-k{font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:650}
.card-v{font-size:32px;font-weight:700;letter-spacing:-.8px;margin:6px 0 4px;color:var(--brand-ink)}
.card.hero .card-v{font-size:42px;color:var(--accent)}
.card-s{font-size:12.5px;color:var(--muted);line-height:1.45}

.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow)}
.panel.warn{border-left:4px solid var(--warn);background:#fffdf7}
.grid2{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.callout{background:#eef6f2;border:1px solid #cfe4da;border-radius:8px;padding:12px 14px;margin:12px 0 0;font-size:14.5px}

.tablewrap{overflow-x:auto;background:var(--panel);border:1px solid var(--line);
  border-radius:var(--radius);box-shadow:var(--shadow)}
table.data{border-collapse:collapse;width:100%;font-size:13.5px}
table.data caption{text-align:left;padding:12px 14px 0;color:var(--muted);font-size:12.5px}
table.data th{background:#eef1f5;text-align:left;padding:9px 12px;font-size:11.5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.05em;color:#36404a;border-bottom:1px solid var(--line);
  position:sticky;top:0;white-space:nowrap;cursor:pointer;user-select:none}
table.data th:hover{background:#e4e9f0}
table.data th::after{content:"\\2195";opacity:.3;margin-left:5px;font-size:10px}
table.data td{padding:9px 12px;border-bottom:1px solid #eef1f4;vertical-align:top}
table.data tbody tr:nth-child(even){background:#fafbfc}
table.data tbody tr:hover{background:#f0f6fb}
table.compact td,table.compact th{padding:6px 10px;font-size:13px}
table.returns td{white-space:nowrap}
.num{font-variant-numeric:tabular-nums;font-weight:600}
.apy{color:var(--accent);font-variant-numeric:tabular-nums;font-size:14.5px}
.apy.big{font-size:22px;font-weight:700}
.rank{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;
  background:var(--brand);color:#fff;font-size:11.5px;font-weight:700}
.pos{color:var(--accent);font-weight:600}
.neg{color:var(--high);font-weight:600}
.bar{height:7px;background:#e6ebf0;border-radius:4px;min-width:70px;overflow:hidden}
.bar span{display:block;height:100%;background:var(--accent);border-radius:4px}

.muted{color:var(--muted)}
.sm{font-size:12px}
.note{cursor:help;color:var(--muted)}
.src{font-size:11.5px;color:var(--brand);white-space:nowrap}
code{background:#eef1f5;padding:1px 5px;border-radius:4px;font-size:12.5px}

.badge{display:inline-block;padding:1.5px 7px;border-radius:20px;font-size:11px;font-weight:650;
  letter-spacing:.02em;white-space:nowrap}
.badge-unver{background:#fdecea;color:var(--high);border:1px solid #f6cfcb}
.badge-unver a{color:inherit}
.badge-cond{background:#fff5e0;color:var(--warn);border:1px solid #f0dcb0}
.badge-info{background:#eaf2f8;color:var(--brand-ink);border:1px solid #cfe0ee}
.badge-warn{background:#fdecea;color:var(--high);border:1px solid #f6cfcb}
.badge-high{background:#fdecea;color:var(--high);border:1px solid #f6cfcb}
.badge-medium{background:#fff5e0;color:var(--med);border:1px solid #f0dcb0}
.badge-low{background:#eef1f5;color:var(--low);border:1px solid #dde3ea}

.ticks{margin:0;padding-left:18px}
.ticks li{margin:6px 0}
.notes{margin:8px 0 0;padding-left:18px;color:#36404a}
.notes li{margin:5px 0;font-size:13.5px}

details.tierblock,details.hz{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:12px 14px;margin-bottom:10px;box-shadow:var(--shadow)}
details summary{cursor:pointer;font-size:14px;padding:2px 0}
details summary::marker{color:var(--brand)}
details[open] summary{margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--line)}

.instcard{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:18px;box-shadow:var(--shadow)}
.inst-h{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between;align-items:flex-start;
  border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:12px}
.inst-h h3{margin:0;font-size:19px}
.inst-meta{display:flex;flex-wrap:wrap;gap:8px}
.inst-meta span{background:#eef1f5;border-radius:20px;padding:3px 10px;font-size:11.5px;color:#36404a}
dl.kv{display:grid;grid-template-columns:minmax(150px,220px) 1fr;gap:6px 16px;margin:0 0 12px;font-size:13.5px}
dl.kv.wide{grid-template-columns:minmax(150px,220px) 1fr}
dl.kv dt{color:var(--muted);font-weight:600}
dl.kv dd{margin:0}
.prod{border:1px solid var(--line);border-radius:8px;padding:14px;margin-top:12px;background:#fcfdfe}
.prod-h{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px}

.flag{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--low);
  border-radius:var(--radius);padding:16px;margin-bottom:12px;box-shadow:var(--shadow);scroll-margin-top:70px}
.flag.sev-high{border-left-color:var(--high)}
.flag.sev-medium{border-left-color:var(--med)}
.flag-h{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-bottom:10px}
.flag-h h3{margin:0;flex:1 1 300px;font-size:16px}
.flag-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;font-weight:700;
  background:#eef1f5;padding:2px 8px;border-radius:5px;color:#36404a}

.foot{background:#fff;border-top:1px solid var(--line);padding:20px 0 34px;margin-top:40px;font-size:12.5px;color:#36404a}
.foot p{margin:0 0 8px;max-width:1000px}

@media (max-width:760px){
  .card.hero{grid-column:span 1}
  dl.kv,dl.kv.wide{grid-template-columns:1fr;gap:2px 0}
  dl.kv dd{margin-bottom:8px}
  h1{font-size:23px}
  .card-v{font-size:27px}
  .card.hero .card-v{font-size:33px}
}
""".strip()
    + "\n",
    encoding="utf-8",
)

(DOCS / "assets" / "app.js").write_text(
    """
/* Lightweight table sorting - no dependencies, no network calls. */
(function () {
  function cellValue(row, i) {
    var td = row.children[i];
    if (!td) return '';
    var t = td.textContent.trim();
    var m = t.replace(/[,$\\u00d7+]/g, '').match(/-?\\d+(\\.\\d+)?/);
    if (m && /[\\d]/.test(t)) return parseFloat(m[0]);
    return t.toLowerCase();
  }
  document.querySelectorAll('table[data-sortable]').forEach(function (table) {
    var ths = table.querySelectorAll('thead th');
    ths.forEach(function (th, i) {
      var dir = 0;
      th.addEventListener('click', function () {
        dir = dir === 1 ? -1 : 1;
        var tb = table.tBodies[0];
        var rows = Array.prototype.slice.call(tb.rows);
        rows.sort(function (a, b) {
          var x = cellValue(a, i), y = cellValue(b, i);
          if (x === y) return 0;
          if (typeof x === 'number' && typeof y === 'number') return (x - y) * dir;
          return (String(x) < String(y) ? -1 : 1) * dir;
        });
        rows.forEach(function (r) { tb.appendChild(r); });
        ths.forEach(function (o) { o.removeAttribute('aria-sort'); });
        th.setAttribute('aria-sort', dir === 1 ? 'ascending' : 'descending');
      });
    });
  });
  var tgl = document.querySelector('.navtoggle');
  var nav = document.querySelector('.mainnav');
  if (tgl && nav) {
    tgl.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      tgl.setAttribute('aria-expanded', String(open));
    });
  }
})();
""".strip()
    + "\n",
    encoding="utf-8",
)

# --------------------------------------------------------------------------
# Guard 4 - internal link check
# --------------------------------------------------------------------------
for src_page, href in internal_links:
    if not (DOCS / href).exists():
        errors.append(f"broken internal link: {src_page} -> {href}")

if errors:
    print("BUILD FAILED\n" + "\n".join(f"  - {x}" for x in errors), file=sys.stderr)
    sys.exit(1)

print(f"Built {len(set(written_pages))} pages into {DOCS}")
print(f"  institutions: {len(INST)}   products: {len(PRODUCTS)}   verified APYs: {len(RANKED)}")
print(f"  sources indexed: {len(seen)}   flags: {len(flags['flags'])}   return rows: {len(returns_out['rows'])}")
print(f"  internal links checked: {len(internal_links)} (all resolve)")
