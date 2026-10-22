#!/usr/bin/env python3
"""Generate the unified 11-page interactive + static GitHub Pages dashboard from data/*.json."""

import csv
import html
import json
import math
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SITE_NAME = "SAVINGS5"
TAGLINE = "Verified U.S. National Bank Savings & FDIC Research"

NAV = [
    ("index.html", "Overview"),
    ("accounts.html", "Accounts"),
    ("returns.html", "Returns & FDIC"),
    ("bonuses.html", "Bonuses"),
    ("rules.html", "Rules & fees"),
    ("security.html", "FDIC & apps"),
    ("competitiveness.html", "Competitiveness"),
    ("rates-refresh.html", "NYC Refresh"),
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
RESEARCH = load("research.json")

with open(os.path.join(DATA, "standard-projections.csv"), newline="", encoding="utf-8") as fh:
    STANDARD_REFRESH = list(csv.DictReader(fh))
with open(os.path.join(DATA, "promotion-projections.csv"), newline="", encoding="utf-8") as fh:
    PROMOTION_REFRESH = list(csv.DictReader(fh))

RESEARCH_SOURCES = {source["id"]: source for source in RESEARCH["sources"]}
INST = {b["cert"]: b for b in INSTITUTIONS["banks"]}
ACC = {a["id"]: a for a in ACCOUNTS["accounts"]}
PROJ = {p["id"]: p for p in RETURNS["projections"]}
LEADER = {l["deposit_usd"]: l for l in RETURNS["leaderboard"]}
OPEN_DATE = ACCOUNTS["open_date"]
ACTIVE_BANKS = [b for b in INSTITUTIONS["banks"] if b.get("active") == 1]


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


def src(url, label="source"):
    return f'<a class="src" href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'


def research_source_links(source_ids, separator="<br>"):
    links = []
    clean_ids = [str(sid).strip() for sid in (source_ids or []) if str(sid).strip()]
    for sid in dict.fromkeys(clean_ids):
        source = RESEARCH_SOURCES.get(sid)
        if source:
            links.append(src(source["url"], source.get("title") or sid))
    return separator.join(links) if links else '<span class="muted">&mdash;</span>'


def csv_money(value):
    return "&mdash;" if value in (None, "") else money(float(value), cents=True)


def clean_source_text(value):
    return (
        str(value)
        .replace(":BLUE_AccSavings_Rate%", "unresolved rate token")
        .replace("#ProductLine=ODS|...|APY=LowTier(0.00)#%", "unresolved server placeholder token")
        .replace("NaN", "nonnumeric extraction")
        .replace("$XXXX", "masked fee placeholder")
    )


def badge(text, kind="plain"):
    return f'<span class="badge {kind}">{e(text)}</span>'


def apy_bar(val_pct, max_pct=4.5):
    if val_pct is None:
        return '<span class="badge warn">not published</span>'
    w = min(100, max(2, round((val_pct / max_pct) * 100)))
    return f'<div class="apy-bar-wrap"><span class="apy-bar"><i style="width:{w}%"></i></span><strong>{pct(val_pct)}</strong></div>'


def model_json_payload():
    bonus_map = {
        "barclays-select-savings": [{"min_dep": 40000, "usd": 400, "dd_required": False}],
        "barclays-tiered-savings": [{"min_dep": 25000, "usd": 200, "dd_required": False}],
        "sofi-savings": [
            {"min_dep": 5000, "usd": 400, "dd_required": True},
            {"min_dep": 1000, "usd": 50, "dd_required": True},
        ],
        "td-simple-savings": [{"min_dep": 10000, "usd": 200, "dd_required": False}],
        "chase-savings": [
            {"min_dep": 10000, "usd": 200, "dd_required": False},
            {"min_dep": 5000, "usd": 100, "dd_required": False},
        ],
    }
    payload = {
        "open_date": OPEN_DATE,
        "fdic_savings_avg": FDIC["national_rates"]["rows"][0]["national_deposit_rate_pct"],
        "accounts": [
            {
                "id": a["id"],
                "brand": a["brand"],
                "account_name": a["account_name"],
                "cert": a["cert"],
                "mobile_app": a["mobile_app"]["value"],
                "std_apy": a["apy_regular_pct"],
                "tiers": a["apy_tiers"],
                "bonuses": bonus_map.get(a["id"], []),
                "source": a["sources"][0]["url"],
            }
            for a in ACCOUNTS["accounts"]
            if a["apy_regular_pct"] is not None
        ],
    }
    return json.dumps(payload)


def simulator_widget(include_all_accounts_table=False):
    # Static pre-rendered default state ($250,000, 1 Year 2026-10-22 -> 2027-10-22, Single Owner $250k)
    default_ladder = next(l for l in RETURNS["ladders"] if l["total_usd"] == 250000 and l["kind"] == "max-rate")
    static_rows = []
    for i, al in enumerate(default_ladder["allocations"], 1):
        static_rows.append(
            f"<tr>"
            f"<td><span class='rank'>{i}</span></td>"
            f"<td><strong>{e(al['brand'])}</strong><br><span class='muted small'>{e(al['account_name'])} &middot; CERT {al['cert']}</span></td>"
            f"<td class='num'>{money(al['amount_usd'])}</td>"
            f"<td class='num'><strong>{pct(al['apy_pct'])}</strong></td>"
            f"<td class='num'>{money(al['interest_1y_usd'])}</td>"
            f"<td class='num'>$400</td>"
            f"<td class='num'><strong>{money(al['amount_usd'] + al['interest_1y_usd'] + 400)}</strong></td>"
            f"<td><span class='small'>Active AARP membership ($400 bonus exp. 2026-10-31)</span></td>"
            f"<td>{src(al['source'], 'official page')}</td>"
            f"</tr>"
        )

    extra_tbl = ""
    if include_all_accounts_table:
        srows = []
        for t in LEADER[250000]["top"]:
            srows.append(
                f"<tr>"
                f"<td><strong>{e(t['brand'])}</strong><br><span class='muted small'>{e(t['account_name'])}</span></td>"
                f"<td class='num'>{apy_bar(t['year1_effective_apy_pct'])}</td>"
                f"<td class='num'>{pct(t['apy_pct'])}</td>"
                f"<td class='num'>{money(t['year1_interest_usd'])}</td>"
                f"<td class='num'>{money(t['cash_bonus_usd']) if t['cash_bonus_usd'] else '&mdash;'}</td>"
                f"<td class='num'><strong>{money(250000 + t['year1_total_with_bonus_usd'])}</strong></td>"
                f"<td class='num'>{badge('100% insured', 'good')}</td>"
                f"<td>{src(t['source'], 'source')}</td>"
                f"</tr>"
            )
        extra_tbl = f"""
<h3 style="margin-top:20px">Side-by-side single-account comparison at selected deposit &amp; lifespan</h3>
<div class="tablewrap">
  <table>
    <thead><tr><th>Bank / account</th><th class="num">Effective APY</th><th class="num">Ongoing APY</th><th class="num">Interest</th><th class="num">Cash bonus</th><th class="num">Ending value</th><th class="num">Single-bank FDIC</th><th>Source</th></tr></thead>
    <tbody id="sim-accounts-body">{''.join(srows)}</tbody>
  </table>
</div>"""

    return f"""
<section class="sim-panel" id="savings5-simulator">
  <div class="sim-head">
    <div>
      <p class="eyebrow" style="margin-bottom:4px">Interactive Return &amp; Multi-Charter FDIC Optimizer &middot; Anchored to {OPEN_DATE}</p>
      <h2 style="margin:0">Calculate your exact insured return &amp; multi-bank split</h2>
    </div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;align-items:center">
      <label class="small" style="display:flex;gap:6px;align-items:center;cursor:pointer">
        <input type="checkbox" id="sim-bonus" checked> Include verified cash bonuses
      </label>
      <label class="small" style="display:flex;gap:6px;align-items:center;cursor:pointer">
        <input type="checkbox" id="sim-principal-buffer"> Cap Day-1 principal so Year-1 interest also stays &le; FDIC ceiling
      </label>
    </div>
  </div>
  <div class="preset-row">
    <span class="muted small" style="margin-right:4px">Quick deposit presets:</span>
    <button type="button" class="chip" data-dep-preset="10000">$10,000</button>
    <button type="button" class="chip" data-dep-preset="25000">$25,000</button>
    <button type="button" class="chip" data-dep-preset="50000">$50,000</button>
    <button type="button" class="chip" data-dep-preset="100000">$100,000</button>
    <button type="button" class="chip active" data-dep-preset="250000">$250,000 (1x Single FDIC)</button>
    <button type="button" class="chip" data-dep-preset="500000">$500,000 (Joint / 2-Bank)</button>
    <button type="button" class="chip" data-dep-preset="1000000">$1,000,000 (4-Bank)</button>
    <button type="button" class="chip" data-dep-preset="1250000">$1,250,000 (Max 5-Beneficiary Trust)</button>
    <button type="button" class="chip" data-dep-preset="2500000">$2,500,000 (10-Bank Single / 2-Bank Trust)</button>
    <button type="button" class="chip" data-dep-preset="3500000">$3,500,000 (14-Charter Single Max)</button>
  </div>
  <div class="sim-controls">
    <div class="sim-field">
      <label for="sim-deposit">Deposit Amount (USD)</label>
      <input type="number" id="sim-deposit" value="250000" min="100" max="50000000" step="1000">
    </div>
    <div class="sim-field">
      <label for="sim-horizon">Investment Lifespan (from {OPEN_DATE})</label>
      <select id="sim-horizon">
        <option value="0.25">3 Months (&rarr; 2027-01-22)</option>
        <option value="0.5">6 Months (&rarr; 2027-04-22)</option>
        <option value="1" selected>1 Year (&rarr; 2027-10-22)</option>
        <option value="2">2 Years (&rarr; 2028-10-22)</option>
        <option value="3">3 Years (&rarr; 2029-10-22)</option>
        <option value="5">5 Years (&rarr; 2031-10-22)</option>
        <option value="10">10 Years (&rarr; 2036-10-22)</option>
      </select>
    </div>
    <div class="sim-field">
      <label for="sim-ownership">FDIC Ownership Category (Per Bank Charter)</label>
      <select id="sim-ownership">
        <option value="250000" selected>Single Ownership ($250,000 / charter)</option>
        <option value="500000">Joint Account — 2 Co-Owners ($500,000 / charter)</option>
        <option value="750000">Revocable POD Trust — 3 Beneficiaries ($750,000 / charter)</option>
        <option value="1250000">Revocable POD Trust — 5+ Beneficiaries ($1,250,000 / charter)</option>
      </select>
    </div>
    <div class="sim-field">
      <label for="sim-mode">Rate Eligibility Filter</label>
      <select id="sim-mode">
        <option value="max" selected>Include Promos, AARP &amp; Relationship Tiers</option>
        <option value="unconditional">No Conditions / No Direct Deposit Only</option>
      </select>
    </div>
  </div>
  <div class="sim-summary" id="sim-stats">
    <div class="sim-stat"><div class="k">Optimal Insured Gain (1 Year)</div><div class="v">$11,025</div><div class="s">Open {OPEN_DATE} &rarr; 2027-10-22 (incl. $400 bonus)</div></div>
    <div class="sim-stat"><div class="k">Blended APY Across 1 Bank</div><div class="v">4.25%</div><div class="s">vs FDIC avg 0.38% (+$10,075 extra)</div></div>
    <div class="sim-stat"><div class="k">FDIC Insured Principal</div><div class="v">$250,000</div><div class="s">100% covered across distinct FDIC CERTs</div></div>
    <div class="sim-stat"><div class="k">Matched 1Y U.S. Treasury (4.52%)</div><div class="v">$11,300</div><div class="s">$275 Treasury yield premium</div></div>
  </div>
  <h3 style="margin:12px 0 8px">Optimal Multi-Charter FDIC Allocation Plan (1 Slot Maximum Per FDIC Certificate)</h3>
  <div class="tablewrap" style="margin-bottom:0">
    <table>
      <thead><tr><th>Slot</th><th>Bank &amp; FDIC Charter</th><th class="num">Allocated Principal</th><th class="num">Effective APY</th><th class="num">Interest Earned</th><th class="num">Cash Bonus</th><th class="num">Ending Value</th><th>Rate / Tier Condition</th><th>Source</th></tr></thead>
      <tbody id="sim-ladder-body">{''.join(static_rows)}</tbody>
    </table>
    <div class="tbl-note" id="sim-ladder-note">Anchored to Account Open Date {OPEN_DATE} through 2027-10-22 (1 Year). Strictly one account per FDIC Certificate (CERT) across mobile-app-verified banks; per-bank insurance cap set to $250,000.</div>
  </div>
  {extra_tbl}
</section>
<script type="application/json" id="savings5-model-data">{model_json_payload()}</script>
"""


def layout(page, title, body, description=""):
    links = "".join(
        f'<a href="{href}" class="{"active" if href == page else ""}">{e(label)}</a>' for href, label in NAV
    )
    desc = e(description or "Verified national bank savings rates, minimums, fees, multi-horizon returns and FDIC coverage.")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; {SITE_NAME}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site">
  <div class="wrap nav">
    <a class="brand" href="index.html"><span class="dot"></span><span>{SITE_NAME}<small>{TAGLINE}</small></span></a>
    <nav class="nav-links">{links}<button type="button" class="theme-btn" id="theme-toggle">Dark mode</button></nav>
  </div>
</header>
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer class="site">
  <div class="wrap footer-grid">
    <div style="max-width:66ch">
      <strong style="color:var(--ink)">{SITE_NAME}</strong> &mdash; line-by-line verified U.S. national bank savings research anchored to Account Open Date <strong>{OPEN_DATE}</strong>.<br>
      Covers <strong>{len(ACTIVE_BANKS)} active Top-56 FDIC-insured banks</strong> ({len(ACCOUNTS["accounts"])} savings accounts, {len(BONUSES["promotions"])} verified offers). Every table row links directly to an official <code>.gov</code> or first-party bank disclosure; unconfirmed or geo-gated rates remain blank and are documented on <a href="flagged.html">Flagged for review</a>. Informational research only, not financial advice.
    </div>
    <div>
      <a href="methodology.html">Methodology</a> &middot;
      <a href="sources.html">All official sources</a> &middot;
      <a href="flagged.html">Flagged items</a> &middot;
      <a href="rates-refresh.html">NYC strict refresh</a><br>
      <span class="muted">Account Open Date &amp; Verification Anchor: {OPEN_DATE}</span>
    </div>
  </div>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""


def page_head(title, lede, eyebrow=""):
    pills = (
        f'<div class="hero-meta">'
        f'{badge(f"Account Open Date: {OPEN_DATE}", "good")} '
        f'{badge(f"{len(ACTIVE_BANKS)} Top-56 Active FDIC Banks", "info")} '
        f'{badge("FDIC Avg 0.38% (2026-10-19)", "plain")} '
        f'{badge("Fed Funds 3.75%-4.00% (2026-09-17)", "plain")} '
        f'{badge("1Y Treasury 4.52% (2026-10-21)", "plain")}'
        f'</div>'
    )
    return f"""<section class="hero">
  {f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ''}
  <h1>{e(title)}</h1>
  <p class="lede">{lede}</p>
  {pills}
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
    t = (text or "").strip()
    if not t or t.lower().startswith("none"):
        return ""
    return t


def account_rate(accid, deposit=250000):
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


NOT_STATED = '<span class="muted">not stated</span>'


def index_page():
    best_ongoing = ACC["barclays-select-savings"]
    best_uncond = ACC["cit-platinum-savings"]
    lb250 = LEADER[250000]["top"]
    top_interest = lb250[0]

    mobile_certs = len({p["cert"] for p in RETURNS["projections"] if p["mobile_app"] == "yes"})
    kpis = f"""<div class="grid k4">
  <div class="card kpi"><div class="label">Highest Ongoing Verified APY</div><div class="value">{pct(best_ongoing["apy_regular_pct"])}</div>
    <div class="sub">{e(best_ongoing["brand"])} Select Savings (AARP; +$400 bonus exp. 2026-10-31) &middot; {pct(3.75)} CIT Platinum ($5k+) &middot; {pct(3.55)} Synchrony ($0+) &mdash; {src(best_ongoing["sources"][0]["url"], "official page")}</div></div>
  <div class="card kpi"><div class="label">Best Year-1 Return on $250,000</div><div class="value">{money(top_interest["year1_total_with_bonus_usd"])}</div>
    <div class="sub">{money(top_interest["year1_interest_usd"])} interest ({pct(top_interest["year1_effective_apy_pct"])}) + {money(top_interest["cash_bonus_usd"])} cash bonus ({OPEN_DATE} &rarr; 2027-10-22) &mdash; {src(top_interest["source"], "source")}</div></div>
  <div class="card kpi"><div class="label">FDIC Insured Capacity Verified</div><div class="value">{money(mobile_certs * 250000)}</div>
    <div class="sub">Single owner across {mobile_certs} mobile-app bank charters ($250k/CERT) &middot; {money(mobile_certs * 500000)} Joint &middot; {money(mobile_certs * 1250000)} Trust &mdash; {src(FDIC["coverage_limits"][0]["source"], "FDIC.gov")}</div></div>
  <div class="card kpi"><div class="label">Top-56 U.S. Banks Audited</div><div class="value">{len(ACTIVE_BANKS)}</div>
    <div class="sub">{len(ACCOUNTS["accounts"])} savings products ($43.5B–$4.09T assets) &middot; {len(RETURNS["excluded_accounts"])} unverified APYs kept blank &mdash; {src("https://banks.data.fdic.gov/bankfind-suite/bankfind", "BankFind")}</div></div>
</div>"""

    rows = []
    for i, t in enumerate(lb250, 1):
        rows.append([
            f'<span class="rank">{i}</span>',
            f'<strong>{e(t["brand"])}</strong><br><span class="muted small">{e(t["account_name"])} &middot; CERT {t["cert"]}</span>',
            apy_bar(t["year1_effective_apy_pct"]),
            pct(t["apy_pct"]),
            money(t["year1_interest_usd"]),
            money(t["cash_bonus_usd"]) if t["cash_bonus_usd"] else "&mdash;",
            f'<strong>{money(t["year1_total_with_bonus_usd"])}</strong>',
            e(t.get("promo_label") or t.get("condition") or "No condition ($0 min / $0 fee)"),
            src(t["source"]),
        ])
    top_table = table(
        ["#", "Bank / account", "Year-1 effective APY", "Ongoing APY", "Year-1 interest ($250k)", "Cash bonus", "Year-1 total gain", "Rate / tier condition", "Source"],
        rows,
        note=f"Account opened {OPEN_DATE} through 2027-10-22 at the $250,000 single-owner FDIC limit. Cash bonuses are shown in their own column and never mixed into ongoing APY.",
        classes=["", "", "num", "num", "num", "num", "num", "", ""],
    )

    urgent_callout = f"""<div class="callout bad">
  <p><strong>Time-sensitive primary-source alerts verified on {OPEN_DATE}:</strong>
  (1) <strong>Citibank's 3.75% 3-month promotional savings rate expires TODAY ({OPEN_DATE})</strong> &mdash; Citi's official <code>Fact_Sheet.pdf</code> states the promotional rate feature is discontinued tomorrow, <strong>2026-10-23</strong> {src("https://www.citi.com/content/dam/cfs/mobile/assets/JRS/popups/ao/Fact_Sheet.pdf", "Citi Fact Sheet PDF")};
  (2) <strong>Barclays' $400 Select Savings bonus (4.25% APY) and $200 Tiered Savings bonus expire in 9 days on 2026-10-31</strong> {src("https://banking.us.barclays/select-home/", "Barclays Select")};
  (3) <strong>Barclays Tiered Savings' 3.65% tier starts at exact $250,000.00</strong>, leaving accrued interest uninsured for a single owner unless held Joint ($500k) or POD Trust ($500k&ndash;$1.25M) {src("https://banking.us.barclays/tiered-savings", "Barclays Tiered")}.</p>
</div>"""

    findings = f"""<ul>
  <li><strong>A 424-basis-point chasm separates national direct HYSAs from branch megabanks.</strong>
    On $250,000 opened {OPEN_DATE}, Barclays Select Savings pays <strong>{money(10625)}</strong>/yr ({pct(4.25)}), CIT Bank Platinum with <code>BOOST50</code> pays <strong>{money(9999)}</strong> in Year 1 ({pct(4.00)} blended; {pct(3.75)} ongoing), and Synchrony pays <strong>{money(8875)}</strong>/yr unconditionally ({pct(3.55)}) &mdash; versus <strong>$25/yr</strong> ({pct(0.01)}) on Chase Savings, Wells Fargo Way2Save, and Truist One Savings. {src("https://banking.us.barclays/select-home/", "Barclays")} {src("https://www.chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf", "Chase NY PDF")}</li>
  <li><strong>Depositing exact $250,000.00 at one bank leaves Year-1 accrued interest uninsured for a single owner.</strong>
    FDIC coverage caps <em>principal + unpaid accrued interest</em> at $250,000 per charter. At {pct(4.25)} APY, depositing <strong>$239,808.15</strong> compounds to exact $250,000.00 at Year 1 with zero uninsured spillover &mdash; or titling as a 2-owner Joint account ($500,000/bank) or 5-beneficiary POD Trust ($1,250,000/bank) protects the entire principal plus multi-year compounding inside just 1&ndash;2 banks. {src("https://www.fdic.gov/resources/deposit-insurance/understanding-deposit-insurance", "FDIC rules")}</li>
  <li><strong>Shared bank charters create hidden FDIC aggregation traps across divisions &amp; mergers.</strong>
    Discover Bank merged into Capital One (<code>CERT 4297</code>) on May 18, 2025; CIT Bank is a division of First-Citizens Bank (<code>CERT 11063</code>); and BMO Alto is a web-only division of BMO Bank N.A. (<code>CERT 16571</code>) with <em>no mobile app</em>. Every multi-bank ladder on this site deduplicates strictly by FDIC Certificate number. {src("https://api.fdic.gov/banks/institutions?filters=CERT%3A5649", "FDIC API")}</li>
  <li><strong>Liquid savings beat the FDIC national average by 11.2&times;, yet trail U.S. Treasuries by 27&ndash;88 bps.</strong>
    Following the Federal Reserve's September 17, 2026 rate hike to <strong>3.75%&ndash;4.00%</strong>, 1-year and 5-year U.S. Treasury par yields sit at <strong>4.52%</strong> and <strong>4.95%</strong> (2026-10-21) &mdash; the exact liquidity premium you pay for instant penalty-free access. {src("https://www.federalreserve.gov/newsevents/pressreleases/monetary20260917a.htm", "FOMC")} {src("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202610", "Treasury.gov")}</li>
  <li><strong>Five geo-gated or placeholder bank rates are kept strictly blank rather than guessed.</strong>
    Bank of America (NY ZIP gate), Citibank base APY (<code>:BLUE_AccSavings_Rate%</code> token), TD Signature (blank JS table), PNC (<code>This Product Isn't Available in Your Area</code>), and Fifth Third (branch-quoted promos) remain blank and linked on <a href="flagged.html">Flagged for review</a>. {src("https://www.bankofamerica.com/deposits/bank-account-interest-rates/", "BofA")}</li>
</ul>"""

    tiles = [
        ("accounts.html", "Master Account Comparison", f"All {len(ACCOUNTS['accounts'])} accounts across {len(ACTIVE_BANKS)} Top-56 banks: APYs, tiers, minimums, fees, waivers and mobile app checks."),
        ("returns.html", "Returns & FDIC Ladder Plans", "Returns across 9 deposit sizes ($10k–$2.5M) & 7 lifespans (3M–10Y from 2026-10-22), plus Single, Joint & Trust ladders up to $5M."),
        ("bonuses.html", "Bonuses, Boosts & Deadlines", f"All {len(BONUSES['promotions'])} verified offers — including Citibank's final-day 2026-10-22 promo, Barclays $400/$200, SoFi $50/$400 & TD/Chase $200."),
        ("rules.html", "Opening Rules & Fee Drag", "Minimum deposits, opening friction, 6- to 10-withdrawal limits, 45-day closure rules, and fee drag math."),
        ("security.html", "FDIC Charters, Apps & Security", "Every FDIC CERT number, Q2 2026 asset rank, merged/shared charter alerts, iOS ratings, passkeys and MFA notes."),
        ("competitiveness.html", "Rate Competitiveness & Curve", "Every bank measured against FDIC National Rates (2026-10-19), Fed Funds (3.75%–4.00%), and U.S. Treasury yields (2026-10-21)."),
        ("rates-refresh.html", "NYC-Strict Snapshot & CSVs", "Companion NYC-strict view leaving location-specific views blank, with downloadable 120-row & 84-row CSV matrices."),
        ("flagged.html", "Flagged for Review Audit", "Every unconfirmed cell, broken bank page token, stale widget, geo-gate, and multi-session audit finding."),
    ]
    tile_html = "".join(
        f'<a class="tile" href="{href}"><div><div class="t">{e(t)}</div><div class="d">{e(d)}</div></div><span class="arrow">Explore &rarr;</span></a>'
        for href, t, d in tiles
    )

    cov_rows = [
        [
            money(c["deposit_usd"]),
            money(c["single_owner_coverage_usd"]),
            (f'<span style="color:var(--bad);font-weight:700">{money(c["uninsured_if_one_bank_usd"])}</span>' if c["uninsured_if_one_bank_usd"] else badge("$0 uninsured", "good")),
            str(c["banks_required_single_owner"]),
            str(c["banks_required_joint_two_owners"]),
            str(c["banks_required_trust5_one_owner"]),
            src("https://www.fdic.gov/resources/deposit-insurance/financial-products-insured", "FDIC rule"),
        ]
        for c in RETURNS["coverage_gap"]
    ]
    cov_table = table(
        ["Deposit size", "Single-bank insured (1 owner)", "Uninsured if held at 1 bank", "Banks needed (Single $250k)", "Banks needed (Joint $500k)", "Banks needed (5-Benef. Trust $1.25M)", "Source"],
        cov_rows,
        note="FDIC coverage is calculated per depositor, per ownership category, per separately chartered bank (CERT).",
        classes=["num", "num", "num", "num", "num", "num", ""],
    )

    body = f"""
{page_head("Best U.S. National Bank Savings Accounts & Max-FDIC Return Strategy",
          f"Line-by-line primary-source verification across {len(ACTIVE_BANKS)} of the largest U.S. FDIC-insured banks ($43.5B to $4.09T in assets), "
          f"anchored to Account Open Date {OPEN_DATE}. Compare verified APYs, cash bonuses, opening rules, mobile app & security status, and multi-charter FDIC coverage plans.",
          "Executive Research Dashboard · 2026-10-22")}
{urgent_callout}
{kpis}
{simulator_widget(include_all_accounts_table=False)}
<h2>Top National Savings Accounts at $250,000 (Max Single-Owner FDIC Slot)</h2>
<p class="muted">Ranked by Year-1 effective return for an account opened on {OPEN_DATE} and held through 2027-10-22.</p>
{top_table}
<h2>Key Strategic Findings</h2>
{findings}
<h2>Explore Category Subpages</h2>
<div class="grid k4">{tile_html}</div>
<h2>FDIC Insurance Coverage &amp; Bank-Split Arithmetic ($100,000 to $5,000,000)</h2>
<p>Holding more than $250,000 in an individual account at a single bank leaves every dollar above $250,000 exposed. Combining ownership categories or splitting across distinct FDIC certificates eliminates uninsured exposure completely.</p>
{cov_table}
"""
    return layout("index.html", "Executive Overview", body,
                  "Verified savings account rates, bonuses, multi-horizon returns and FDIC coverage across 19 large U.S. banks.")


def accounts_page():
    rows = []
    for a in sorted_accounts():
        rate250, cond = account_rate(a["id"], 250000)
        if a["apy_regular_pct"] is None:
            apy_cell = '<span class="badge warn">not published</span>'
            asof = "&mdash;"
        else:
            apy_cell = apy_bar(rate250)
            if cond:
                apy_cell += f'<div class="muted small" style="margin-top:3px">{e(cond)}</div>'
            if rate250 != a["apy_regular_pct"]:
                apy_cell += f'<div class="muted small">base {pct(a["apy_regular_pct"])}</div>'
            asof = e(a["apy_as_of"] or "")
        app_badge = badge("Confirmed", "good") if a["mobile_app"]["value"] == "yes" else badge("No mobile app", "bad")
        rows.append([
            f'<strong><a href="#{e(a["id"])}">{e(a["brand"])}</a></strong><br><span class="muted small">{e(a["account_name"])} &middot; CERT {a["cert"]}</span>',
            apy_cell,
            asof,
            money(a["min_open_usd"]) if a["min_open_usd"] is not None else NOT_STATED,
            money(a["monthly_fee_usd"], cents=True) if a["monthly_fee_usd"] is not None else NOT_STATED,
            money(a["min_balance_to_avoid_fee_usd"]) if a["min_balance_to_avoid_fee_usd"] else ("$0 (no fee)" if a["min_balance_to_avoid_fee_usd"] == 0 else NOT_STATED),
            app_badge,
            e(a["fee_waiver"]) if a["fee_waiver"] else NOT_STATED,
            src(a["sources"][0]["url"], "official page"),
        ])
    main = table(
        ["Bank / account", "Ongoing APY at $250k", "Effective date", "Min. open", "Monthly fee", "Waiver balance", "Mobile app", "Fee waiver & key notes", "Source"],
        rows,
        note=f"Sorted by verified ongoing APY at a $250,000 deposit as of {OPEN_DATE}. Click any column header to re-sort or use the search box above to filter.",
        classes=["", "num", "", "num", "num", "num", "", "", ""],
    )

    cards = ""
    for a in sorted_accounts():
        rate250, cond = account_rate(a["id"], 250000)
        inst = INST.get(a["cert"], {})
        flags = "".join(badge(f, "warn") for f in a["flags"]) or badge("Verified — no open flags", "good")
        sources = "".join(
            f'<li>{e(s["label"])} &mdash; {src(s["url"], s["url"])} <span class="muted">({e(s["as_of"])})</span></li>'
            for s in a["sources"]
        )
        cards += f"""
<div class="card" id="{e(a['id'])}" style="margin-bottom:14px">
  <div class="section-head">
    <h3 style="margin:0">{e(a['brand'])} &mdash; {e(a['account_name'])}</h3>
    <div class="tag-row" style="margin:0">{flags}</div>
  </div>
  <p class="muted small" style="margin-top:6px">{e(a['institution'])} &middot; FDIC CERT <strong>{a['cert']}</strong> &middot; {e(inst.get('bkclass_label',''))} &middot;
    U.S. Active Asset Rank <strong>#{inst.get('assets_rank')}</strong> ({money(inst.get('assets_usd'))}) &middot;
    <a class="src" href="https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{a['cert']}" target="_blank" rel="noopener">FDIC BankFind</a></p>
  <div class="grid k4" style="margin:12px 0">
    <div><div class="muted small">Ongoing APY ($250k)</div><div class="strong" style="font-size:20px">{pct(rate250) if rate250 is not None else 'Not published'}</div></div>
    <div><div class="muted small">Minimum to open</div><div class="strong" style="font-size:20px">{money(a['min_open_usd'])}</div></div>
    <div><div class="muted small">Monthly maintenance fee</div><div class="strong" style="font-size:20px">{money(a['monthly_fee_usd'], cents=True) if a['monthly_fee_usd'] is not None else 'Not stated'}</div></div>
    <div><div class="muted small">Mobile banking app</div><div class="strong" style="font-size:20px">{'Confirmed (iOS/Android)' if a['mobile_app']['value'] == 'yes' else 'None (Web-only)'}</div></div>
  </div>
  <p><strong>Rate &amp; tier details:</strong> {e(a['apy_note'])}</p>
  <p><strong>Fee waiver rules:</strong> {e(a['fee_waiver'] or 'Not published on geo-restricted page.')}</p>
  <p><strong>Account opening rules:</strong> {e(a['opening_requirements'])}</p>
  <p><strong>Withdrawal &amp; activity rules:</strong> {e(a['withdrawal_limit'] or 'No excess transaction fee stated on product page.')}</p>
  <p><strong>FDIC charter &amp; aggregation note:</strong> {e(a['fdic_beyond_250k'])}</p>
  <p><strong>Mobile app &amp; security check:</strong> {e(a['mobile_app']['note'])} {src(a['mobile_app']['source'], 'official app source')}</p>
  <details><summary>All verified primary sources ({len(a['sources'])})</summary><ul>{sources}</ul></details>
</div>"""

    body = f"""
{page_head("Complete National Bank Savings Comparison",
          f"All {len(ACCOUNTS['accounts'])} savings accounts across {len(ACTIVE_BANKS)} Top-56 FDIC-insured banks, verified line by line on {OPEN_DATE}.",
          "Category · Accounts")}
<div class="callout info">
  <p><strong>Zero-hallucination standard:</strong> Every rate below is transcribed from a first-party bank disclosure or official rate PDF with its stated effective date. The {len(RETURNS['excluded_accounts'])} accounts whose rates are blocked behind interactive ZIP modals or broken template tokens remain blank and are documented on <a href="flagged.html">Flagged for review</a>.</p>
</div>
{main}
<h2>Line-by-Line Account Dossiers</h2>
{cards}
"""
    return layout("accounts.html", "Account Comparison", body,
                  "Verified APYs, tiers, minimums, fees, mobile apps and primary sources for 22 national savings accounts.")


def returns_page():
    deposits = RETURNS["projections"][0]["rows"]
    dep_list = [r["deposit_usd"] for r in deposits]
    hdr = ["Bank / account"] + [money(d) for d in dep_list] + ["Source"]
    cls = [""] + ["num"] * len(dep_list) + [""]

    rows1, rows5 = [], []
    for a in sorted_accounts():
        p = PROJ.get(a["id"])
        if not p:
            continue
        label = f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["account_name"])}</span>'
        r1 = [label]
        r5 = [label]
        for d in dep_list:
            row = next(r for r in p["rows"] if r["deposit_usd"] == d)
            r1.append(money(row["interest_1y"]))
            r5.append(money(row["balance_5y"]))
        r1.append(src(p["apy_source"]))
        r5.append(src(p["apy_source"]))
        rows1.append(r1)
        rows5.append(r5)

    t1 = table(hdr, rows1,
               note=f"Pre-tax Year-1 interest ({OPEN_DATE} -> 2027-10-22) across all 9 deposit sizes, including $250,000 (Single Max FDIC), $500,000 (2-Owner Joint Max FDIC), and $1,250,000 (5-Beneficiary Trust Max FDIC).",
               classes=cls)
    t5 = table(hdr, rows5,
               note=f"Projected 5-year ending balance ({OPEN_DATE} -> 2031-10-22) holding ongoing APY constant after Year 1.",
               classes=cls)

    term_rows = []
    for a in sorted_accounts():
        p = PROJ.get(a["id"])
        if not p:
            continue
        row = next(r for r in p["rows"] if r["deposit_usd"] == 250000)
        term_rows.append([
            f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["account_name"])}</span>',
            pct(row["year1_effective_apy_pct"]),
            pct(row["best_apy_pct"]),
            money(p["max_day1_principal_for_full_year1_fdic_usd"], cents=True),
            money(row["interest_3m"]),
            money(row["interest_6m"]),
            money(row["interest_1y"]),
            money(row["balance_2y"]),
            money(row["balance_3y"]),
            money(row["balance_5y"]),
            money(row["balance_10y"]),
            money(row["fallback_balance_5y"]),
            src(p["apy_source"]),
        ])
    term = table(
        [
            "Bank / account", "Yr-1 APY", "Ongoing APY", "Max Day-1 Principal for 100% Yr-1 FDIC",
            "3M Int. (2027-01-22)", "6M Int. (2027-04-22)", "1Y Int. (2027-10-22)",
            "2Y Bal. (2028-10-22)", "3Y Bal. (2029-10-22)", "5Y Bal. (2031-10-22)", "10Y Bal. (2036-10-22)",
            "5Y Stress Case (0.38% Yr 2+)", "Source",
        ],
        term_rows,
        note=f"All horizons open on {OPEN_DATE} at $250,000. 'Max Day-1 Principal for 100% Yr-1 FDIC' = floor($250,000 / (1 + Yr1 APY)), ensuring principal + full Year-1 compounded interest never exceed $250,000.00. {src(FDIC['national_rates']['source'], 'FDIC rates 2026-10-19')}",
        classes=["", "num", "num", "num", "num", "num", "num", "num", "num", "num", "num", "num", ""],
    )

    lad_rows = []
    for l in RETURNS["ladders"]:
        alloc = "<br>".join(
            f'{e(x["brand"])} (CERT {x["cert"]}) &mdash; {money(x["amount_usd"])} @ {pct(x["apy_pct"])}'
            for x in l["allocations"][:5]
        )
        if len(l["allocations"]) > 5:
            alloc += f'<br><span class="muted small">+ {len(l["allocations"]) - 5} additional distinct FDIC charters</span>'
        status = badge("100% FDIC insured", "good") if l["status"] == "fully covered" else badge(l["status"], "warn")
        lad_rows.append([
            money(l["total_usd"]),
            e(l["kind_label"]),
            str(l["banks_needed"]),
            str(l["distinct_banks_used"]),
            pct(l["blended_apy_pct"]),
            money(l["year1_interest_usd"]),
            money(l["uninsured_usd"]) if l["uninsured_usd"] else "&mdash;",
            status,
            alloc,
            src(l["allocations"][0]["source"], "top bank source"),
        ])
    ladders = table(
        ["Total deposit", "Ownership & strategy", "Charters needed", "Charters used", "Blended Yr-1 APY", "Year-1 interest", "Uninsured remainder", "FDIC coverage status", "Charter-deduplicated allocation", "Source"],
        lad_rows,
        note="Every ladder includes ONLY accounts with confirmed mobile banking apps (excluding web-only Alto by BMO) and strictly at most ONE account per FDIC Certificate (CERT).",
        classes=["num", "", "num", "num", "num", "num", "num", "", "", ""],
    )

    excl = "".join(
        f'<li><strong>{e(x["brand"])} &mdash; {e(x["account_name"])}</strong> (CERT {x["cert"]}): {e(x["reason"])} {src(x["sources"][0]["url"], "official page checked")}</li>'
        for x in RETURNS["excluded_accounts"]
    )

    body = f"""
{page_head("Returns Across Deposit Sizes, Investment Lifespans & Max-FDIC Ladders",
          f"Exact compounded return projections anchored to Account Open Date {OPEN_DATE} across 3M, 6M, 1Y, 2Y, 3Y, 5Y and 10Y lifespans — from $10,000 up to $5,000,000 multi-charter structures.",
          "Category · Returns & FDIC")}
{simulator_widget(include_all_accounts_table=True)}
<h2>Full Lifespan Matrix at $250,000 ({OPEN_DATE} &rarr; 2036-10-22) &amp; Safe Day-1 FDIC Principal Cap</h2>
{term}
<h2>Year-1 Interest Matrix Across 9 Deposit Sizes ($10,000 to $2,500,000)</h2>
{t1}
<h2>5-Year Compounded Balance Matrix ({OPEN_DATE} &rarr; 2031-10-22)</h2>
{t5}
<h2>Multi-Bank FDIC Ladder Plans (Single, Joint &amp; 5-Beneficiary Trust Structures)</h2>
<p>With 14 distinct mobile-app-enabled FDIC charters verified in this study, a single owner can insure up to <strong>$3,500,000</strong> ($2,500,000 across 10 banks with $0 uninsured remainder), a 2-owner Joint structure insures up to <strong>$7,000,000</strong>, and a 5-beneficiary Revocable POD Trust insures <strong>$2,500,000 across just two top HYSA charters at 4.12% blended Year-1 APY</strong>.</p>
{ladders}
<h2>Accounts Excluded From Numeric Return Tables (Unverified APYs Kept Blank)</h2>
<ul>{excl}</ul>
"""
    return layout("returns.html", "Returns & FDIC Ladders", body,
                  "Multi-horizon savings return tables anchored to 2026-10-22 and multi-charter FDIC ladder plans.")


def bonuses_page():
    rows = []
    for p in BONUSES["promotions"]:
        tiers = "<br>".join(
            f'{money(t.get("deposit_usd"))}+ &rarr; {money(t.get("bonus_usd"))}' if t.get("deposit_usd") is not None and t.get("bonus_usd")
            else (f'{money(t.get("deposit_usd"))}+ deposit threshold' if t.get("deposit_usd") is not None else f'{money(t.get("bonus_usd"))} &mdash; {e(t.get("requirement",""))}')
            for t in p["tiers"]
        ) or "Rate boost / tier"
        exp = p["expires"] or "Ongoing / until revoked"
        exp_cell = badge(f"FINAL DAY: {exp}", "bad") if exp == "2026-10-22" else (badge(f"Expires {exp}", "warn") if p["expires"] else '<span class="muted">No stated expiry</span>')
        rows.append([
            f'<strong>{e(p["brand"])}</strong><br><span class="muted small">{e(p["type"])} &middot; CERT {p["cert"]}</span>',
            f'<strong>{e(p["headline"])}</strong>',
            tiers,
            e(p["requirements"]),
            e(p["eligibility"]),
            exp_cell,
            src(p["source"]),
        ])
    main = table(["Bank", "Verified offer", "Deposit / bonus tiers", "Qualification & hold rules", "Eligibility", "Expiration", "Source"],
                 rows,
                 note=f"All {len(BONUSES['promotions'])} offers verified directly on official bank pages/PDFs on {OPEN_DATE}.",
                 classes=["", "", "", "", "", "", ""])

    none_rows = [
        [f'<strong>{e(x["brand"])}</strong>', e(x["note"]), src(x["checked_url"], "page checked")]
        for x in BONUSES["no_savings_bonus_found"]
    ]
    none_tbl = table(["Bank", "Official page verification result", "Official page checked"], none_rows, classes=["", "", ""])

    body = f"""
{page_head("Account Opening Bonuses, Rate Boosts & Expiration Calendar",
          f"All {len(BONUSES['promotions'])} verified cash bonuses, APY boosts, and relationship rate offers active on {OPEN_DATE}, plus explicit verification of banks publishing no bonus.",
          "Category · Promotions & Bonuses")}
<div class="callout bad">
  <p><strong>Immediate deadline check ({OPEN_DATE}):</strong> Citibank's 3.75% 3-month promotional savings rate on $25,000+ ends <strong>TODAY ({OPEN_DATE})</strong> and is discontinued tomorrow, <strong>2026-10-23</strong> per Citi's official <code>Fact_Sheet.pdf</code>. Barclays' <strong>$400</strong> Select Savings bonus and <strong>$200</strong> Tiered Savings bonus expire <strong>2026-10-31</strong>. Note also that SoFi's <strong>$400</strong> cash bonus requires <strong>$5,000+</strong> in qualifying direct deposits within 25 days ($1,000&ndash;$4,999.99 earns $50).</p>
</div>
<h2>Verified Cash Bonuses &amp; Rate Promotions</h2>
{main}
<h2>Banks Checked With No Public Standalone Savings Cash Bonus on {OPEN_DATE}</h2>
{none_tbl}
"""
    return layout("bonuses.html", "Bonuses & Promotions", body,
                  "Verified bank savings account opening bonuses, rate boosts, hold periods and expiration dates.")


def rules_page():
    rows = []
    for a in sorted_accounts():
        rows.append([
            f'<strong>{e(a["brand"])}</strong><br><span class="muted small">{e(a["account_name"])}</span>',
            money(a["min_open_usd"]) if a["min_open_usd"] is not None else NOT_STATED,
            e(a["opening_requirements"]),
            e(a["withdrawal_limit"] or "No excess withdrawal fee stated on product page."),
            e(a["fee_waiver"] or NOT_STATED),
            src(a["sources"][0]["url"]),
        ])
    main = table(["Bank / account", "Min. open", "Account opening requirements", "Withdrawal, closure & companion rules", "Monthly fee waiver rules", "Source"],
                 rows, classes=["", "num", "", "", "", ""])

    fee_rows = []
    for a in sorted_accounts():
        fee = a["monthly_fee_usd"]
        annual = None if fee is None else fee * 12
        drag10k = None if fee is None else (fee * 12) / 10000 * 100
        fee_rows.append([
            f'<strong>{e(a["brand"])}</strong> &mdash; {e(a["account_name"])}',
            money(fee, cents=True) if fee is not None else NOT_STATED,
            money(annual, cents=True) if annual is not None else NOT_STATED,
            pct(drag10k, 2) if drag10k is not None else NOT_STATED,
            pct((fee * 12) / 250000 * 100, 3) if fee is not None else NOT_STATED,
            money(a["min_balance_to_avoid_fee_usd"]) if a["min_balance_to_avoid_fee_usd"] is not None else NOT_STATED,
            src(a["sources"][0]["url"]),
        ])
    fee_tbl = table(["Bank / account", "Monthly fee", "Annual cost (unwaived)", "Fee drag at $10,000", "Fee drag at $250,000", "Balance that waives fee", "Source"],
                    fee_rows,
                    note="Every direct online HYSA in this study charges $0 monthly fee with $0 balance minimum; branch megabanks charge $4.50–$15.00/month unless waived.",
                    classes=["", "num", "num", "num", "num", "num", ""])

    body = f"""
{page_head("Account Opening Requirements, Minimums & Fee Drag",
          "Side-by-side comparison of minimum opening deposits, identity/eligibility rules, withdrawal limits, automatic zero-balance closures, and monthly fee waivers.",
          "Category · Rules & Fees")}
<h2>Opening Rules &amp; Operational Restrictions</h2>
{main}
<h2>Monthly Maintenance Fee &amp; Yield Drag Analysis</h2>
{fee_tbl}
"""
    return layout("rules.html", "Rules & Fees", body,
                  "Minimum opening deposits, monthly fees, waivers and withdrawal rules across 22 national savings accounts.")


def security_page():
    rows = []
    for b in INSTITUTIONS["banks"]:
        cert = b["cert"]
        accts = [a for a in ACCOUNTS["accounts"] if a["cert"] == cert]
        products = "<br>".join(e(x["account_name"]) for x in accts) if accts else '<span class="muted">Merged into Capital One (CERT 4297)</span>'
        if b["active"] == 0:
            app = badge("Merged charter", "info")
        elif accts and all(x["mobile_app"]["value"] == "yes" for x in accts):
            rating = f' ({b["ios_rating"]}&starf; iOS)' if b.get("ios_rating") else ""
            app = badge(f"Confirmed{rating}", "good")
        else:
            app = badge("No mobile app (Web-only)", "bad")
        rows.append([
            f'<strong>{e(b["brand"])}</strong><br><span class="muted small">{e(b["name"])} ({e(b["city"])}, {e(b["state"])})</span>',
            f'<a class="src" href="https://banks.data.fdic.gov/bankfind-suite/bankfind/details/{cert}" target="_blank" rel="noopener">{cert}</a>',
            f'#{b["assets_rank"]}' if b.get("assets_rank") else "&mdash;",
            badge("Active", "good") if b.get("active") == 1 else badge("Inactive / Merged", "bad"),
            badge("FDIC Insured", "good") if b.get("insfdic") == 1 else badge("Uninsured", "bad"),
            e(b.get("bkclass_label", "")),
            money(b.get("assets_usd")),
            products,
            app,
        ])
    main = table(
        ["Institution", "FDIC CERT", "U.S. Active Rank", "Status", "FDIC Insurance", "Charter Class", "Total Assets (Q2 2026)", "Accounts Studied", "Mobile App"],
        rows,
        note=f"Source: FDIC BankFind Suite API ({e(INSTITUTIONS['dataset_index'])}), verified {OPEN_DATE}. Asset ranks reflect active FDIC-insured banks only (ACTIVE=1 AND INSFDIC=1). {src('https://api.fdic.gov/banks/institutions', 'FDIC API')}",
        classes=["", "num", "num", "", "", "", "num", "", ""],
    )

    cov_rows = [
        [e(c["category"]), e(c["rule"]), money(c["limit_usd"]), money(c["max_day1_principal_at_425bps_usd"], cents=True), src(c["source"])]
        for c in FDIC["coverage_limits"]
    ]
    cov = table(["Ownership category", "Official FDIC aggregation rule", "Statutory ceiling", "Max Day-1 Principal at 4.25% APY", "Source"],
                cov_rows, classes=["", "", "num", "num", ""])

    app_rows = []
    for a in sorted_accounts():
        inst = INST.get(a["cert"], {})
        app_rows.append([
            f'<strong>{e(a["brand"])}</strong> &mdash; {e(a["account_name"])}',
            badge("Yes — Mobile App", "good") if a["mobile_app"]["value"] == "yes" else badge("No — Web Browser Only", "bad"),
            e(inst.get("ios_app_name", "")),
            f'{inst["ios_rating"]}&starf;' if inst.get("ios_rating") else "Confirmed on bank domain",
            e(a["mobile_app"]["note"]),
            f'{src(a["mobile_app"]["source"], "bank page")} {src(inst.get("ios_app_url", a["mobile_app"]["source"]), "app / security")}',
        ])
    appt = table(["Account", "Meets Digital App Filter?", "Official App Name", "iOS App Store", "Security & Authentication Verification", "Sources"],
                 app_rows, classes=["", "", "", "num", "", ""])

    disc = INSTITUTIONS["discover_note"]
    body = f"""
{page_head("FDIC Charter Verification, Digital Apps & Account Security",
          f"Individual certificate verification across {len(ACTIVE_BANKS)} active Top-56 U.S. banks plus merged Discover Bank (CERT 5649), paired with official mobile app and MFA/passkey checks.",
          "Category · FDIC, Apps & Security")}
<div class="callout warn">
  <p><strong>Four shared-charter rules every large depositor must know:</strong>
  (1) <strong>Discover Bank (CERT 5649)</strong> merged into <strong>Capital One (CERT 4297)</strong> on 2025-05-18 &mdash; shared $250k ceiling;
  (2) <strong>CIT Bank</strong> is a division of <strong>First-Citizens Bank (CERT 11063)</strong> &mdash; shared $250k ceiling;
  (3) <strong>Alto by BMO</strong> is a web-only division of <strong>BMO Bank N.A. (CERT 16571)</strong> with <strong>no mobile app</strong>;
  (4) Multiple products at one bank (<strong>Barclays Select + Tiered CERT 57203</strong>, <strong>Wells Fargo CERT 3511</strong>, <strong>TD CERT 18409</strong>) share one limit per ownership category. {src(disc['sources'][0], 'FDIC API')} {src(disc['sources'][2], 'Capital One notice')}</p>
</div>
<h2>FDIC BankFind Institution Register (Q2 2026 Call Report)</h2>
{main}
<h2>FDIC Coverage Formulas &amp; Year-1 Interest Headroom</h2>
{cov}
<h2>Mobile Banking App &amp; Security Controls Verification</h2>
{appt}
"""
    return layout("security.html", "FDIC, Apps & Security", body,
                  "FDIC certificate numbers, active asset ranks, shared-charter alerts, mobile banking apps and security verification.")


def competitiveness_page():
    nat = {r["product"]: r for r in FDIC["national_rates"]["rows"]}
    sav = nat["Savings"]["national_deposit_rate_pct"]
    cd12 = nat["12 month CD"]["national_deposit_rate_pct"]
    t1y = FDIC["daily_treasury_par_curve"]["yields_pct"]["1Y"]
    fed_mid = 3.875

    rate_rows = []
    for a in sorted_accounts():
        r, cond = account_rate(a["id"], 250000)
        if r is None:
            rate_rows.append([
                f'<strong>{e(a["brand"])}</strong> &mdash; {e(a["account_name"])}',
                badge("not published", "warn"), "&mdash;", "&mdash;", "&mdash;", "&mdash;", "&mdash;", "&mdash;",
                src(a["sources"][0]["url"]),
            ])
            continue
        mult = r / sav
        spread_sav = (r - sav) * 100
        vs_fed = (r - 4.00) * 100
        vs_t1y = (r - t1y) * 100
        years_double = 0.693147 / math.log(1 + r / 100)
        rate_rows.append([
            f'<strong>{e(a["brand"])}</strong> &mdash; {e(a["account_name"])}' + (f'<br><span class="muted small">{e(cond)}</span>' if cond else ""),
            apy_bar(r),
            "{:.1f}&times;".format(mult),
            "{:+.0f} bps".format(spread_sav),
            "{:+.0f} bps".format((r - cd12) * 100),
            "{:+.0f} bps".format(vs_fed),
            "{:+.0f} bps".format(vs_t1y),
            ("> 1,000 yrs" if years_double > 1000 else "{:.1f} yrs".format(years_double)),
            src(a["sources"][0]["url"]),
        ])
    main = table(
        ["Bank / account", "Ongoing APY ($250k)", "Multiple of FDIC Avg (0.38%)", "Spread vs FDIC Avg", "vs 12M CD Avg (1.76%)", "vs Fed Upper Bound (4.00%)", "vs 1Y Treasury (4.52%)", "Years to Double", "Source"],
        rate_rows,
        note=f"Benchmarks: FDIC National Rates (2026-10-19) {src(FDIC['national_rates']['source'], 'FDIC.gov')}, FOMC Target 3.75%–4.00% (2026-09-17) {src(FDIC['fomc_policy']['source'], 'FederalReserve.gov')}, U.S. Treasury Par Curve (2026-10-21) {src(FDIC['daily_treasury_par_curve']['source'], 'Treasury.gov')}.",
        classes=["", "num", "num", "num", "num", "num", "num", "num", ""],
    )

    bench_rows = [
        [e(r["product"]), pct(r["national_deposit_rate_pct"], 2), pct(r["national_rate_cap_pct"], 2), src(FDIC["national_rates"]["source"])]
        for r in FDIC["national_rates"]["rows"]
    ]
    bench = table(["FDIC Product Benchmark (2026-10-19)", "National Deposit Rate", "National Rate Cap", "Source"],
                  bench_rows, classes=["", "num", "num", ""])

    tsy_rows = [
        [tenor, pct(val, 2), src(FDIC["daily_treasury_par_curve"]["source"], "Treasury.gov (2026-10-21)")]
        for tenor, val in FDIC["daily_treasury_par_curve"]["yields_pct"].items()
    ]
    tsy = table(["U.S. Treasury Par Maturity (2026-10-21)", "Par Yield", "Official Source"], tsy_rows, classes=["", "num", ""])

    body = f"""
{page_head("Rate Competitiveness Across Lifespans & Macro Benchmarks",
          f"Measuring every national savings account against FDIC National Rates (2026-10-19), the Federal Reserve's 3.75%–4.00% policy corridor (2026-09-17), and the U.S. Treasury Daily Par Yield Curve (2026-10-21).",
          "Category · Rate Competitiveness")}
<div class="callout warn">
  <p><strong>Macro Lifespan Takeaway:</strong> After the FOMC's September 17, 2026 hike to <strong>3.75%&ndash;4.00%</strong>, Barclays Select ({pct(4.25)}) is the <em>only</em> ongoing savings rate in this study that clears the 4.00% Fed upper bound (by +25 bps), while short-term boosts at SoFi ({pct(4.40)} for 6M), Marcus ({pct(4.50)} for 3M), and CIT Bank <code>BOOST50</code> ({pct(4.25)} for 6M) temporarily approach or beat 3M&ndash;6M Treasury bills (4.25%&ndash;4.35%). Across multi-year horizons (1Y 4.52% to 5Y 4.95%), variable savings rates carry re-pricing risk modeled in our 5Y Stress Case column on <a href="returns.html">Returns &amp; FDIC</a>.</p>
</div>
<h2>Account-by-Account Benchmark Spreads</h2>
{main}
<div class="grid k2">
  <div><h2>FDIC National Deposit Rates &amp; Caps (2026-10-19)</h2>{bench}</div>
  <div><h2>U.S. Treasury Daily Par Yield Curve (2026-10-21)</h2>{tsy}</div>
</div>
"""
    return layout("competitiveness.html", "Rate Competitiveness", body,
                  "Savings APYs compared against FDIC national averages, FOMC federal funds rate, and U.S. Treasury yields.")


def rates_refresh_page():
    meta = RESEARCH["meta"]
    source_rows = []
    for account in RESEARCH["accounts"]:
        status = account["status"]
        status_badge = (
            badge("Rate date 2026-07-01", "warn") if status == "official-rate-date-stale"
            else badge("NYC HTML unverified", "bad") if status in {"nyc-rate-unverified", "numeric-apy-unverified", "availability-and-rate-unverified"}
            else badge("Conditional", "warn") if "conditional" in status
            else badge("Verified official rate", "good")
        )
        rate_lines = []
        if status == "nyc-rate-unverified":
            rate_lines.append('<span class="muted">&mdash; Interactive ZIP gate on web HTML (see Master Accounts page for official NY PDF where published).</span>')
        elif status == "numeric-apy-unverified":
            rate_lines.append('<span class="muted">&mdash; No numeric APY rendered in static web HTML.</span>')
        elif status == "availability-and-rate-unverified":
            rate_lines.append('<span class="muted">&mdash; Geo-restricted availability notice in NY/branch market.</span>')
        else:
            for rate in account.get("standardRates", []):
                rate_lines.append(f'<strong>{pct(rate["apyPercent"])}</strong> &mdash; {e(rate["label"])} <span class="muted small">(as of {e(rate["asOf"])})</span>')
        opening = account["opening"]
        source_rows.append([
            f'<strong>{e(account["bank"] or account["id"].title())}</strong><br>{e(account["product"])}',
            status_badge,
            "<br>".join(rate_lines),
            f'Min open: {e(opening["minimumOpeningDeposit"])}<br>Fee: {e(opening["monthlyMaintenanceFee"])}',
            e(account["fdic"]["legalBank"]),
            research_source_links(account.get("sourceIds", [])),
        ])
    snap_tbl = table(
        ["Institution & product", "Web HTML status", "Published web rate tiers", "Opening terms", "Insured legal charter", "Official sources"],
        source_rows,
        note="Preserved companion snapshot from Session 3a8e8ff0 (T11/T12), with Citi internal staging URLs normalized to production online.citi.com.",
        classes=["", "", "", "", "", ""],
    )

    promo_rows = []
    for row in PROMOTION_REFRESH:
        if row.get("deposit_usd") == "250000" and row.get("horizon_years") == "1":
            promo_rows.append([
                f'<strong>{e(row["bank"])}</strong><br><span class="muted small">{e(row["offer_name"])}</span>',
                csv_money(row["deposit_usd"]),
                csv_money(row["projected_total_value_usd"]),
                csv_money(row["incremental_vs_standard_usd"]),
                e(row.get("qualification_summary", "")),
                research_source_links(row.get("source_ids", "").split(";")),
            ])
    promo_tbl = table(
        ["Bank & offer", "Deposit", "Year-1 ending value", "Gain vs standard rate", "Qualification summary", "Sources"],
        promo_rows,
        note="Extracted from data/promotion-projections.csv at $250,000 / 1-year horizon.",
        classes=["", "num", "num", "num", "", ""],
    )

    body = f"""
{page_head("Supplemental NYC Web-HTML Rate Snapshot & Scenario CSVs",
          f"Companion multi-session evidence registry ({len(RESEARCH['sources'])} source records, 120 standard scenarios, 84 promo scenarios) preserved alongside the unified 19-bank dataset.",
          "Supplemental Registry · Session 3a8e8ff0 + 5f0ee759")}
<p class="muted">Machine-readable exports: <a href="data/standard-projections.csv">standard-projections.csv (120 rows)</a> &middot; <a href="data/promotion-projections.csv">promotion-projections.csv (84 rows)</a> &middot; <a href="data/research.json">research.json</a> &middot; <a href="research/source-matrix.csv">source-matrix.csv</a></p>
<h2>Web-HTML Rate &amp; Charter Snapshot</h2>
{snap_tbl}
<h2>$250,000 Year-1 Conditional Promotion Scenarios</h2>
{promo_tbl}
"""
    return layout("rates-refresh.html", "NYC Refresh & CSVs", body,
                  "Supplemental NYC web-HTML rate snapshot and downloadable scenario matrices.")


def flagged_page():
    items = []
    for a in sorted_accounts():
        if a["apy_regular_pct"] is None:
            items.append({
                "area": "Unverified APY (Blank)",
                "item": f'{a["brand"]} — {a["account_name"]}',
                "detail": a["apy_note"],
                "status": "Unverified — left blank",
                "sources": a["sources"],
            })
        if a["mobile_app"]["value"] != "yes":
            items.append({
                "area": "Digital App Disqualification",
                "item": f'{a["brand"]} — {a["account_name"]}',
                "detail": a["mobile_app"]["note"],
                "status": "Disqualified from mobile ladders",
                "sources": [{"label": "Official page checked", "url": a["mobile_app"]["source"], "as_of": OPEN_DATE}],
            })

    items += [
        {
            "area": "Time-Sensitive Discontinuation",
            "item": "Citibank — 3.75% 3-month promotional rate ends TODAY (2026-10-22)",
            "detail": "Official Citibank Fact_Sheet.pdf states: 'Effective October 23, 2026, Promotional Rate Feature for New Citi Savings accounts will be discontinued.' 2026-10-22 is the final day to open under the 3.75% 3M offer before Citi transitions to Citi Premium Boost on 2026-10-26.",
            "status": "Verified — expires 2026-10-22",
            "sources": [
                {"label": "Citi Official Fact Sheet PDF", "url": "https://www.citi.com/content/dam/cfs/mobile/assets/JRS/popups/ao/Fact_Sheet.pdf", "as_of": "2026-10-22"},
                {"label": "Citi Promotional Rate Offer Page", "url": "https://banking.citi.com/cbol/OM/checking/enhanced-direct-deposit-offer/default.htm", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "FDIC Boundary Trap",
            "item": "Barclays Tiered Savings — 3.65% APY starts at exact $250,000.00 ceiling",
            "detail": "Barclays Tiered Savings pays 3.50% below $250,000 and 3.65% from $250,000.00 to $999,999.99. A single individual depositing $250,000.00 to unlock 3.65% leaves every cent of accrued interest uninsured unless held in a Joint ($500,000) or Revocable Trust ($500,000–$1,250,000) account.",
            "status": "Structural FDIC alert — verified",
            "sources": [{"label": "Barclays Tiered Savings", "url": "https://banking.us.barclays/tiered-savings", "as_of": "2026-10-07"}],
        },
        {
            "area": "Bank Page Rendering Defect",
            "item": "Capital One — 360 Performance Savings hero displays 'NaN APY'",
            "detail": "Capital One's product hero script renders 'NaN APY' with date 10/21/2026, while Capital One's category comparison page and rate disclosure text confirm 3.20% APY (3.1540% interest rate).",
            "status": "Resolved via primary disclosure",
            "sources": [
                {"label": "Product page (NaN hero defect)", "url": "https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/", "as_of": "2026-10-22"},
                {"label": "Category comparison page (3.20% APY)", "url": "https://www.capitalone.com/bank/savings-accounts/", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Bank Page Rendering Defect",
            "item": "Bank of America — product page displays '$XXXX' fee placeholders",
            "detail": "Advantage Savings HTML displays '$XXXX' in fee blocks; $8.00 monthly fee, $100 minimum opening deposit, and $500 daily balance waiver verified from BofA's Personal Schedule of Fees PDF (effective 2026-08-07).",
            "status": "Resolved via official fee schedule PDF",
            "sources": [
                {"label": "Advantage Savings page ($XXXX defect)", "url": "https://www.bankofamerica.com/deposits/savings/savings-accounts/", "as_of": "2026-10-22"},
                {"label": "Personal Schedule of Fees PDF", "url": "https://www.bankofamerica.com/salesservices/deposits/resources/personal-schedule-fees/?request_locale=en_US", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Stale Page Widget",
            "item": "Synchrony Bank — calculator widget uses stale 2.85% default",
            "detail": "Synchrony's embedded earnings calculator on hys-core defaults to 2.85% while the page headline and October 2026 official rate disclosure state 3.55% APY.",
            "status": "Verified — 3.55% disclosure used",
            "sources": [{"label": "Synchrony High Yield Savings", "url": "https://www.synchrony.com/banking/products/hys-core", "as_of": "2026-10-22"}],
        },
        {
            "area": "Corporate Merger / Shared CERT",
            "item": "Discover Bank (CERT 5649) merged into Capital One (CERT 4297)",
            "detail": "FDIC BankFind shows Discover Bank ACTIVE = 0 following its May 18, 2025 merger into Capital One, N.A. (CERT 4297); discover.com savings redirects to Capital One and shares one $250,000 limit.",
            "status": "Charter overlap enforced",
            "sources": [
                {"label": "FDIC BankFind CERT 5649", "url": "https://api.fdic.gov/banks/institutions?filters=CERT%3A5649", "as_of": "2026-10-22"},
                {"label": "Capital One FDIC notice", "url": "https://www.capitalone.com/bank/savings-accounts/online-performance-savings-account/", "as_of": "2026-10-22"},
            ],
        },
        {
            "area": "Cross-Session Audit Remediation",
            "item": "Corrected FDIC active bank rankings, SoFi $50/$400 direct-deposit tiers & staging URLs",
            "detail": "Line-by-line integration audit corrected: (a) Ally (#24 vs #34), Synchrony (#30 vs #49), and SoFi (#46 vs #89) active asset ranks where inactive historical banks had polluted counts; (b) SoFi's cash bonus tiers ($1,000–$4,999.99 DD = $50; $5,000+ DD in 25d = $400); (c) Chase's official first-party NY PDF rate sheet (rdny1.pdf, 0.01% APY eff. 2026-10-16); and (d) two sit58.online.citi.com UAT URLs normalized to online.citi.com.",
            "status": "Remediated & verified",
            "sources": [
                {"label": "FDIC Active Institutions API", "url": "https://api.fdic.gov/banks/institutions?filters=ACTIVE%3A1%20AND%20INSFDIC%3A1&sort_by=ASSET&sort_order=DESC&limit=65", "as_of": "2026-10-22"},
                {"label": "SoFi HYSA Bonus Terms", "url": "https://www.sofi.com/banking/high-yield-savings-account/", "as_of": "2026-10-22"},
                {"label": "Chase NY Rate Sheet PDF", "url": "https://www.chase.com/content/dam/chase-ux/ratesheets/pdfs/rdny1.pdf", "as_of": "2026-10-16"},
            ],
        },
    ]

    rows = []
    for i in items:
        links = "<br>".join(src(s["url"], s["label"]) for s in i["sources"])
        kind = "bad" if ("Unverified" in i["status"] or "Disqualified" in i["status"] or "expires 2026-10-22" in i["status"]) else ("warn" if "alert" in i["status"] else "good")
        rows.append([e(i["area"]), f'<strong>{e(i["item"])}</strong>', e(i["detail"]), badge(i["status"], kind), links])

    main = table(["Category", "Flagged Item", "Exact Finding & Verification Note", "Status", "Official Sources"], rows, classes=["", "", "", "", ""])

    refresh_rows = [
        [e(f["id"]), f'<strong>{e(f["title"])}</strong>', e(f["details"]), badge(f["severity"], "info"), research_source_links(f.get("sourceIds", []))]
        for f in RESEARCH["flags"]
    ]
    refresh_flags = table(["Registry ID", "Supplemental Flag", "Details", "Severity", "Official Sources"], refresh_rows, classes=["", "", "", "", ""])

    body = f"""
{page_head("Flagged for Review — Unverified Cells, Page Defects & Audit Log",
          f"Every unconfirmed field left blank, every broken bank template token, geo-gate, charter overlap, and multi-session audit finding verified on {OPEN_DATE}.",
          "Category · Transparency & Audit")}
{main}
<h2>Supplemental Research Registry Flags</h2>
{refresh_flags}
"""
    return layout("flagged.html", "Flagged for Review", body,
                  "Unverified bank rates kept blank, rendering defects, charter overlaps and multi-session audit log.")


def sources_page():
    seen = {}
    for a in ACCOUNTS["accounts"]:
        for s in a["sources"]:
            seen.setdefault(s["url"], {"label": s["label"], "as_of": s["as_of"], "used_for": set()})
            seen[s["url"]]["used_for"].add(a["brand"])
    for p in BONUSES["promotions"]:
        seen.setdefault(p["source"], {"label": f"{p['brand']} — {p['headline']}", "as_of": OPEN_DATE, "used_for": set()})
        seen[p["source"]]["used_for"].add(p["brand"])
    for x in BONUSES["no_savings_bonus_found"]:
        seen.setdefault(x["checked_url"], {"label": f"{x['brand']} bonus check", "as_of": OPEN_DATE, "used_for": set()})
        seen[x["checked_url"]]["used_for"].add(x["brand"])
    for c in FDIC["coverage_limits"]:
        seen.setdefault(c["source"], {"label": "FDIC Deposit Insurance Coverage Rules", "as_of": OPEN_DATE, "used_for": set()})
        seen[c["source"]]["used_for"].add("FDIC")
    seen.setdefault(FDIC["national_rates"]["source"], {"label": "FDIC National Rates and Rate Caps", "as_of": FDIC["national_rates"]["as_of"], "used_for": {"Benchmarks"}})
    seen.setdefault(FDIC["fomc_policy"]["source"], {"label": "Federal Reserve FOMC Policy Statement (3.75%–4.00%)", "as_of": FDIC["fomc_policy"]["meeting_date"], "used_for": {"Federal Reserve"}})
    seen.setdefault(FDIC["daily_treasury_par_curve"]["source"], {"label": "U.S. Treasury Daily Par Yield Curve Rates", "as_of": FDIC["daily_treasury_par_curve"]["as_of"], "used_for": {"U.S. Treasury"}})
    seen.setdefault(INSTITUTIONS["api_endpoint"], {"label": "FDIC BankFind Suite Institutions API", "as_of": OPEN_DATE, "used_for": {"All 19 Active + 1 Merged Banks"}})

    gov, bank = [], []
    for url, meta in sorted(seen.items(), key=lambda kv: kv[1]["label"].lower()):
        row = [f'<strong>{e(clean_source_text(meta["label"]))}</strong>', src(url, url), e(meta["as_of"]), e(", ".join(sorted(meta["used_for"])))]
        (gov if any(g in url for g in ("fdic.gov", "federalreserve.gov", "treasury.gov")) else bank).append(row)

    gov_tbl = table(["Government / Regulator Source", "Official URL", "Effective / Checked Date", "Scope"], gov, classes=["", "", "", ""])
    bank_tbl = table(["First-Party Bank Source", "Official URL", "Effective / Checked Date", "Institution"], bank, classes=["", "", "", ""])

    refresh_source_rows = []
    for source in RESEARCH["sources"]:
        claims = "<br>".join(f"&bull; {e(clean_source_text(claim))}" for claim in source.get("supports", []))
        refresh_source_rows.append([
            f'<strong>{e(source["organization"])}</strong><br>{e(source["title"])}<br><code>{e(source["id"])}</code>',
            f'Checked {e(source["checkedOn"])}<br><span class="muted small">{e(source.get("sourceDate") or "Undated")}</span>',
            claims,
            src(source["url"], "Official disclosure"),
        ])
    refresh_tbl = table(["Institution / Source ID", "Dates", "Verified Claims", "Official URL"], refresh_source_rows, classes=["", "", "", ""])

    body = f"""
{page_head("Primary Official Source Registry",
          f"Every single figure on {SITE_NAME} traces to an official U.S. government register (.gov) or first-party bank domain verified on {OPEN_DATE}. Zero third-party comparison or affiliate sites are used.",
          "Category · Official Sources")}
<h2>Federal Regulator &amp; Macroeconomic Sources (<code>.gov</code>)</h2>
{gov_tbl}
<h2>First-Party Bank Disclosures, Rate PDFs &amp; Product Pages ({len(bank)} URLs)</h2>
{bank_tbl}
<h2>Supplemental Evidence Registry ({len(RESEARCH['sources'])} Records)</h2>
{refresh_tbl}
"""
    return layout("sources.html", "Official Sources", body,
                  "Complete index of government and first-party bank sources retrieved on 2026-10-22.")


def methodology_page():
    nat_count = sum(1 for b in ACTIVE_BANKS if b.get("bkclass") == "N")
    facts = [
        ("Account Open Date anchor", OPEN_DATE),
        ("Active Top-56 U.S. banks verified", f"{len(ACTIVE_BANKS)} ({nat_count} National Banks + {len(ACTIVE_BANKS) - nat_count} State Banks)"),
        ("Savings accounts evaluated", f"{len(ACCOUNTS['accounts'])} ({len(RETURNS['projections'])} verified numeric APYs, {len(RETURNS['excluded_accounts'])} blank)"),
        ("Mobile-enabled distinct FDIC CERTs", "14 ($3,500,000 Single / $7,000,000 Joint / $17,500,000 Trust)"),
        ("Promotions & bonuses verified", str(len(BONUSES["promotions"]))),
        ("Deposit sizes modelled", "9 ($10,000 to $2,500,000 + interactive $100–$50M)"),
        ("Investment lifespans modelled", "7 (3M, 6M, 1Y, 2Y, 3Y, 5Y, 10Y -> 2036-10-22)"),
        ("Automated build gates", "tools/check_site.py + research/validate_research.py"),
    ]
    fn = "".join(
        f'<div class="card flat"><div class="muted small">{e(k)}</div><div style="font-weight:750;font-size:17px;margin-top:4px">{e(v)}</div></div>'
        for k, v in facts
    )
    body = f"""
{page_head("Methodology, Formulas & Verification Architecture",
          "Exact mathematical formulas, FDIC charter aggregation rules, screening criteria, and automated zero-hallucination build gates.",
          "Reference · Methodology")}
<h2>Study Architecture at a Glance</h2>
<div class="grid k4">{fn}</div>
<h2>1. Compounding &amp; Promotional Blending Formulas</h2>
<ul>
  <li><strong>Constant-APY future value:</strong> <code>FV = P &times; (1 + APY)<sup>t</sup></code> where <code>t</code> is measured from <strong>{OPEN_DATE}</strong> (<code>0.25, 0.50, 1, 2, 3, 5, 10</code> years).</li>
  <li><strong>CIT Bank <code>BOOST50</code> Year-1 blended APY (&ge;$5,000):</strong> <code>1.0425<sup>0.5</sup> &times; 1.0375<sup>0.5</sup> - 1 = 3.9997% (&approx; 4.00%)</code>.</li>
  <li><strong>SoFi 6-Month Direct-Deposit Boost Year-1 blended APY:</strong> <code>1.044<sup>0.5</sup> &times; 1.033<sup>0.5</sup> - 1 = 3.8485% (&approx; 3.85%)</code>.</li>
  <li><strong>Marcus 3-Month Referral Boost Year-1 APY:</strong> <code>3.75%</code> combined Year-1 APY per Marcus's official disclosure (up to $1,000,000 balance cap).</li>
  <li><strong>Day-1 Single-Owner Principal Buffer Cap:</strong> <code>P<sub>max</sub> = &lfloor;$250,000 / (1 + APY<sub>Yr1</sub>)&rfloor;</code> so principal plus full Year-1 compounded interest never exceed $250,000.00.</li>
  <li><strong>5-Year Rate-Cut Stress Case:</strong> Year 1 at today's verified effective yield, Years 2&ndash;5 at <code>min(ongoing APY, 0.38% FDIC National Average)</code>.</li>
</ul>
<h2>2. Automated Reproducibility</h2>
<p>Run <code>python3 tools/build_returns.py &amp;&amp; python3 tools/build_site.py &amp;&amp; python3 research/validate_research.py &amp;&amp; python3 tools/check_site.py</code> from repository root to regenerate every projection, page, link check, and source audit cleanly.</p>
"""
    return layout("methodology.html", "Methodology", body,
                  "Formulas, FDIC charter deduplication rules, and reproducible build pipeline.")


PAGES = {
    "index.html": index_page,
    "rates-refresh.html": rates_refresh_page,
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

DOCS_REDIRECTS = {
    "index.html": "../index.html",
    "rates.html": "../accounts.html",
    "branch.html": "../accounts.html",
    "digital.html": "../accounts.html",
    "returns.html": "../returns.html",
    "bonuses.html": "../bonuses.html",
    "rules.html": "../rules.html",
    "fdic.html": "../security.html",
    "benchmarks.html": "../competitiveness.html",
    "flagged.html": "../flagged.html",
    "sources.html": "../sources.html",
    "methodology.html": "../methodology.html",
}


def write_docs_redirects():
    docs_dir = os.path.join(ROOT, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    open(os.path.join(docs_dir, ".nojekyll"), "w", encoding="utf-8").close()
    for name, target in DOCS_REDIRECTS.items():
        html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Redirecting &middot; {SITE_NAME}</title>
<script>location.replace("{target}" + location.hash);</script>
</head>
<body><p>Redirecting to <a href="{target}">{target}</a>&hellip;</p></body>
</html>
"""
        with open(os.path.join(docs_dir, name), "w", encoding="utf-8") as fh:
            fh.write(html_doc)


def main():
    for filename, fn in PAGES.items():
        out = os.path.join(ROOT, filename)
        clean = "\n".join(line.rstrip() for line in fn().splitlines()) + "\n"
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(clean)
        print("wrote", filename)
    write_docs_redirects()
    print("site built:", datetime.now().isoformat(timespec="seconds"))


if __name__ == "__main__":
    main()
