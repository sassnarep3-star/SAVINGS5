#!/usr/bin/env python3
"""
Build data/returns.json from data/accounts.json and data/fdic.json.

Model rules (also documented on the site's Methodology page):
  * APY already includes compounding, so constant-rate future value is
    balance = deposit * (1 + APY)^years.
  * Two rate columns are produced for every account and deposit size:
      standard_apy - the rate that applies with no relationship, no new-customer
                     status and no direct-deposit condition
      best_apy     - the highest rate the bank publishes for that balance, where
                     the balance falls inside a published tier; the condition is
                     recorded on the row and repeated in the tables
  * No rate is assumed, averaged, or trended. Accounts without a transcribed APY
    are excluded from every projection and listed in excluded_accounts.
  * Fee drag is shown separately: monthly_fee * 12, i.e. the cost if the fee
    waiver is not met. Net figures subtract that fee.
  * Two scenarios per projection:
      constant - today's APY held for the whole term (mechanical, not a forecast)
      fallback - year 1 at today's APY, remaining years at the lower of today's
                 APY and the FDIC national savings rate (0.38%, 2026-10-19)
"""

import json
import math
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

DEPOSITS = [10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000]
YEARS = [1, 2, 3, 5]

# Year-1 blended yields for time-limited promotions. Each number comes from the
# bank's own page; the derivation is printed in the site's formulas section.
PROMO_YEAR1 = {
    "sofi-savings": {
        "label": "4.40% for months 1-6, then 3.30%",
        "apy_pct": round(((1.044 ** 0.5) * (1.033 ** 0.5) - 1) * 100, 4),
        "source": "https://www.sofi.com/banking/high-yield-savings-account/",
        "derivation": "(1.044^0.5 * 1.033^0.5 - 1) = 3.85% year-1 blended yield",
    },
    "marcus-online-savings": {
        "label": "3.50% plus one 1.00% referral boost for 3 months",
        "apy_pct": 3.75,
        "source": "https://www.marcus.com/us/en/savings/referrals",
        "derivation": "Marcus states the combined APY would be 3.75% for the year with one referral",
    },
}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def fv(principal, apy_pct, years):
    return principal * ((1 + apy_pct / 100.0) ** years)


def round2(x):
    return round(x + 1e-9, 2)


def tier_rate(account, deposit, include_transient=False):
    """Highest published permanent tier whose balance band contains `deposit`.

    Tiers flagged transient (e.g. a 6-month APY boost) are excluded here; they are
    handled separately as a year-1 promo so they cannot inflate a 5-year balance.
    """
    best = None
    for t in account.get("apy_tiers", []):
        if t.get("transient") and not include_transient:
            continue
        lo = t.get("min_usd", 0) or 0
        hi = t.get("max_usd")
        if deposit >= lo and (hi is None or deposit <= hi):
            if best is None or t["apy_pct"] > best["apy_pct"]:
                best = t
    return best


def clean_cond(text):
    t = (text or "").strip()
    if not t or t.lower().startswith("none"):
        return ""
    return t


def best_rate(account, deposit):
    """Best published permanent rate at this balance, falling back to standard."""
    t = tier_rate(account, deposit)
    standard = account["apy_regular_pct"]
    if t is None:
        return standard, ""
    if t["apy_pct"] <= standard:
        return standard, clean_cond(t.get("requires", ""))
    return t["apy_pct"], clean_cond(t.get("requires", ""))


def promo_year1_rate(account, deposit):
    """Blended year-1 rate if a documented time-limited boost applies."""
    promo = PROMO_YEAR1.get(account["id"])
    if not promo:
        return None, None
    if account["id"] == "sofi-savings" and deposit < 1:
        return None, None
    return promo["apy_pct"], promo["label"]


def build():
    accounts_doc = load("accounts.json")
    fdic = load("fdic.json")
    accounts = accounts_doc["accounts"]
    open_date = accounts_doc["open_date"]
    national_savings = next(
        r["national_deposit_rate_pct"] for r in fdic["national_rates"]["rows"] if r["product"] == "Savings"
    )

    eligible = [a for a in accounts if a["apy_regular_pct"] is not None]
    excluded = [
        {
            "brand": a["brand"],
            "account_name": a["account_name"],
            "reason": a["apy_note"],
            "sources": a["sources"],
        }
        for a in accounts
        if a["apy_regular_pct"] is None
    ]

    projections = []
    for a in eligible:
        fee_year = (a["monthly_fee_usd"] or 0) * 12
        rows = []
        for p in DEPOSITS:
            std = float(a["apy_regular_pct"])
            best, condition = best_rate(a, p)
            promo_rate, promo_label = promo_year1_rate(a, p)
            year1_rate = promo_rate if promo_rate is not None else best
            row = {
                "deposit_usd": p,
                "standard_apy_pct": std,
                "best_apy_pct": best,
                "best_condition": condition,
                "promo_year1_apy_pct": promo_rate,
                "promo_label": promo_label,
                "year1_effective_apy_pct": year1_rate,
                "fdic_insured_usd": min(p, 250000),
                "fdic_uninsured_usd": max(0, p - 250000),
                "annual_fee_if_not_waived_usd": round2(fee_year),
            }
            for y in YEARS:
                if y == 1:
                    bal = fv(p, year1_rate, 1)
                else:
                    bal = fv(p, year1_rate, 1) * ((1 + best / 100.0) ** (y - 1))
                row[f"balance_{y}y"] = round2(bal)
                row[f"interest_{y}y"] = round2(bal - p)
                row[f"net_interest_{y}y"] = round2(bal - p - fee_year * y)
                if y == 1:
                    fb = bal
                else:
                    # stress case: rate moves to the FDIC national average but never
                    # above today's rate, so a low-rate account cannot "gain" from it
                    fb_rate = min(best, national_savings)
                    fb = fv(p, year1_rate, 1) * ((1 + fb_rate / 100.0) ** (y - 1))
                row[f"fallback_balance_{y}y"] = round2(fb)
                row[f"fallback_interest_{y}y"] = round2(fb - p)
            rows.append(row)
        projections.append(
            {
                "id": a["id"],
                "brand": a["brand"],
                "account_name": a["account_name"],
                "cert": a["cert"],
                "standard_apy_pct": a["apy_regular_pct"],
                "apy_as_of": a["apy_as_of"],
                "apy_source": a["sources"][0]["url"],
                "monthly_fee_usd": a["monthly_fee_usd"],
                "fdic_limit_usd": 250000,
                "rows": rows,
                "promo": PROMO_YEAR1.get(a["id"]),
            }
        )

    # ---- Leaderboards: best published rate at that balance ------------------
    leaderboard = []
    for p in DEPOSITS:
        ranked = []
        for a in eligible:
            rate, cond = best_rate(a, p)
            promo_rate, promo_label = promo_year1_rate(a, p)
            eff = promo_rate if promo_rate is not None else rate
            ranked.append((eff, a, cond, rate, promo_label))
        ranked.sort(key=lambda x: x[0], reverse=True)
        leaderboard.append(
            {
                "deposit_usd": p,
                "banks_needed_single_owner": math.ceil(p / 250000),
                "top": [
                    {
                        "id": a["id"],
                        "brand": a["brand"],
                        "account_name": a["account_name"],
                        "apy_pct": rate,
                        "year1_effective_apy_pct": eff,
                        "promo_label": promo_label,
                        "condition": cond,
                        "year1_interest_usd": round2(p * eff / 100.0),
                        "year1_net_of_fee_usd": round2(p * eff / 100.0 - (a["monthly_fee_usd"] or 0) * 12),
                        "source": a["sources"][0]["url"],
                    }
                    for eff, a, cond, rate, promo_label in ranked[:6]
                ],
            }
        )

    # ---- FDIC ladder plans -------------------------------------------------
    # no-conditions: APY applies with no relationship/new-customer/DD condition.
    # max-rate: also allows published conditional and promotional rates.
    no_condition_ids = {
        "synchrony-hys",
        "marcus-online-savings",
        "sofi-savings",
        "capone-360-performance",
        "amex-hysa",
        "ally-savings",
        "wf-way2save",
        "schwab-investor-savings",
        "cit-savings-connect",
        "barclays-tiered-savings",
    }
    conditional_ids = {"usbank-smartly-savings", "wf-platinum-savings", "cit-platinum-savings"}
    # Accounts whose only published condition is a balance threshold. A $250,000
    # FDIC slot satisfies those thresholds by construction, so the tier rate is the
    # rate actually earned - unlike a relationship, direct-deposit or new-customer
    # condition, which the depositor still has to go and meet.
    balance_tier_ids = {"barclays-tiered-savings", "cit-platinum-savings"}

    def rate_for_ladder(a, amount):
        if a["id"] in balance_tier_ids:
            return best_rate(a, amount)[0]
        if a["id"] in no_condition_ids:
            return float(a["apy_regular_pct"])
        return best_rate(a, amount)[0]

    ladders = []
    for total in [250_000, 500_000, 1_000_000, 2_500_000, 5_000_000]:
        banks_needed = math.ceil(total / 250000)
        for kind, ids in (("no-conditions", no_condition_ids), ("max-rate", no_condition_ids | conditional_ids)):
            # one account per institution: two products at the same FDIC certificate
            # share a single $250,000 limit, so they cannot both be used as a slot
            pool, seen_certs = [], set()
            for a in sorted([a for a in eligible if a["id"] in ids],
                            key=lambda a: rate_for_ladder(a, 250000), reverse=True):
                if a["cert"] in seen_certs:
                    continue
                seen_certs.add(a["cert"])
                pool.append(a)
            chosen = pool[:banks_needed]
            remaining = total
            allocations = []
            for c in chosen:
                amount = min(250000, remaining)
                if amount <= 0:
                    break
                allocations.append({
                    "brand": c["brand"],
                    "account_name": c["account_name"],
                    "apy_pct": rate_for_ladder(c, amount),
                    "amount_usd": round2(amount),
                    "source": c["sources"][0]["url"],
                })
                remaining -= amount
            placed = total - max(0, remaining)
            interest = sum(x["amount_usd"] * x["apy_pct"] / 100.0 for x in allocations)
            blended = (sum(x["amount_usd"] * x["apy_pct"] for x in allocations) / placed) if placed else 0.0
            uninsured = max(0, remaining)
            ladders.append(
                {
                    "total_usd": total,
                    "kind": kind,
                    "banks_needed": banks_needed,
                    "distinct_banks_used": len({x["brand"] for x in allocations}),
                    "pool_size": len(pool),
                    "placed_usd": round2(placed),
                    "uninsured_usd": round2(uninsured),
                    "allocation_each_usd": round2(250000 if len(allocations) > 1 else placed),
                    "blended_apy_pct": round(blended, 4),
                    "year1_interest_usd": round2(interest),
                    "insured_usd": round2(placed),
                    "status": "fully covered" if uninsured == 0 else "not fully covered by this pool",
                    "allocations": allocations,
                }
            )

    # ---- Coverage gap illustration ----------------------------------------
    coverage_gap = []
    for amount in [250_000, 500_000, 1_000_000, 2_500_000, 5_000_000]:
        coverage_gap.append(
            {
                "deposit_usd": amount,
                "single_owner_coverage_usd": 250000,
                "uninsured_if_one_bank_usd": max(0, amount - 250000),
                "banks_required_single_owner": math.ceil(amount / 250000),
                "joint_coverage_two_owners_usd": 500000,
                "banks_required_joint_two_owners": math.ceil(amount / 500000),
            }
        )

    out = {
        "open_date": open_date,
        "generated": date.today().isoformat(),
        "assumptions": {
            "compounding": "Future value uses APY as an annual compounded rate: balance = deposit * (1 + APY)^years.",
            "constant_rate": "Scenario 'constant' holds today's APY unchanged for the whole term. Savings APYs are variable; this is a mechanical projection, not a forecast.",
            "fallback_rate": "Scenario 'fallback' applies today's APY for year 1, then the lower of today's APY and the FDIC national savings rate - a stress case that can only reduce the balance relative to the constant-rate case.",
            "fallback_rate_pct": national_savings,
            "fallback_source": "https://www.fdic.gov/national-rates-and-rate-caps",
            "fdic_limit": "Single-owner coverage of $250,000 per depositor, per bank, per ownership category.",
            "fdic_source": "https://www.fdic.gov/resources/deposit-insurance/financial-products-insured",
            "fees": "Projections are gross of account fees; 'net_interest' subtracts the account's monthly fee x 12 for each year, i.e. the case where the fee waiver is not met.",
            "taxes": "Projections are pre-tax. Interest on savings is generally taxable; no tax rate is applied here.",
            "best_rate": "Where a bank publishes tiered or conditional rates, 'best_apy' uses the tier that contains the deposit and the table repeats the condition. It is not available to everyone.",
        },
        "projections": projections,
        "excluded_accounts": excluded,
        "leaderboard": leaderboard,
        "ladders": ladders,
        "coverage_gap": coverage_gap,
    }

    with open(os.path.join(DATA, "returns.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"returns.json written: {len(projections)} projected, {len(excluded)} excluded, {len(ladders)} ladder rows")


if __name__ == "__main__":
    build()
