#!/usr/bin/env python3
"""
Build data/returns.json from data/accounts.json, data/bonuses.json, and data/fdic.json.

Strict verification & projection rules:
  * Anchor date: Account Open Date 2026-10-22 across all horizons:
      3M (2027-01-22), 6M (2027-04-22), 1Y (2027-10-22),
      2Y (2028-10-22), 3Y (2029-10-22), 5Y (2031-10-22), 10Y (2036-10-22).
  * APY already reflects annual compounding: balance = deposit * (1 + APY)^years.
  * Accounts with null APY are NEVER estimated or filled from third-party aggregators;
    they are excluded from return math and listed in excluded_accounts.
  * Multi-bank FDIC ladders enforce BOTH:
      1. mobile_app.value == "yes" (excludes web-only Alto by BMO)
      2. Strict one-account-per-FDIC-certificate (cert) deduplication so shared charters
         (Barclays Select + Tiered CERT 57203, Wells Fargo CERT 3511, TD CERT 18409,
         Capital One + merged Discover CERT 4297) NEVER double-count FDIC limits.
"""

import json
import math
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

DEPOSITS = [10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000, 1_250_000, 2_500_000]
YEARS = [1, 2, 3, 5, 10]

PROMO_YEAR1 = {
    "cit-platinum-savings": {
        "label": "4.25% for months 1-6 (promo code BOOST50), then 3.75% standard tier on $5,000+",
        "apy_pct": round(((1.0425 ** 0.5) * (1.0375 ** 0.5) - 1) * 100, 4),
        "source": "https://www.cit.com/cit-bank/platinum-savings/boost",
        "derivation": "(1.0425^0.5 * 1.0375^0.5 - 1) = 3.9997% (~4.00%) Year-1 blended APY on >= $5,000",
    },
    "sofi-savings": {
        "label": "4.40% for months 1-6 (+1.10% DD boost), then 3.30% ongoing DD rate",
        "apy_pct": round(((1.044 ** 0.5) * (1.033 ** 0.5) - 1) * 100, 4),
        "source": "https://www.sofi.com/banking/high-yield-savings-account/",
        "derivation": "(1.044^0.5 * 1.033^0.5 - 1) = 3.8485% (~3.85%) Year-1 blended APY",
    },
    "marcus-online-savings": {
        "label": "4.50% for months 1-3 (+1.00% referral boost), then 3.50% ongoing",
        "apy_pct": 3.75,
        "source": "https://www.marcus.com/us/en/savings/referrals",
        "derivation": "Marcus states one 3-month +1.00% referral boost produces 3.75% combined APY for Year 1 (up to $1,000,000)",
    },
}

CASH_BONUS_RULES = {
    "barclays-select-savings": [(40_000, 400, "$400 bonus on $40k+ held 120d (exp. 2026-10-31)")],
    "barclays-tiered-savings": [(25_000, 200, "$200 bonus on $25k+ held 120d (exp. 2026-10-31)")],
    "sofi-savings": [
        (5_000, 400, "$400 DD bonus ($5,000+ qualifying DD in 25d)"),
        (1_000, 50, "$50 DD bonus ($1,000-$4,999.99 qualifying DD in 25d)"),
    ],
    "td-simple-savings": [(10_000, 200, "$200 bonus on $10k+ held 90d (exp. 2026-11-30)")],
    "chase-savings": [
        (10_000, 200, "$200 bonus on $10k+ held 90d (exp. 2027-01-27)"),
        (5_000, 100, "$100 bonus on $5k-$9,999.99 held 90d (exp. 2027-01-27)"),
    ],
}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def fv(principal, apy_pct, years):
    return principal * ((1 + apy_pct / 100.0) ** years)


def round2(x):
    return round(x + 1e-9, 2)


def tier_rate(account, deposit, include_transient=False):
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
    t = tier_rate(account, deposit)
    standard = account["apy_regular_pct"]
    if t is None:
        return standard, ""
    if t["apy_pct"] <= standard:
        return standard, clean_cond(t.get("requires", ""))
    return t["apy_pct"], clean_cond(t.get("requires", ""))


def promo_year1_rate(account, deposit):
    promo = PROMO_YEAR1.get(account["id"])
    if not promo:
        return None, None
    if account["id"] == "marcus-online-savings" and deposit > 1_000_000:
        # Boost applies up to $1M balance cap; conservative blended rate above $1M
        boosted_part = 1_000_000 * 0.0375 + (deposit - 1_000_000) * 0.0350
        return round(boosted_part / deposit * 100, 4), promo["label"] + " (capped at $1M)"
    return promo["apy_pct"], promo["label"]


def cash_bonus_for(account_id, deposit):
    for min_dep, usd, label in CASH_BONUS_RULES.get(account_id, []):
        if deposit >= min_dep:
            return usd, label
    return 0, ""


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
            "id": a["id"],
            "brand": a["brand"],
            "account_name": a["account_name"],
            "cert": a["cert"],
            "reason": a["apy_note"],
            "sources": a["sources"],
        }
        for a in accounts
        if a["apy_regular_pct"] is None
    ]

    projections = []
    for a in eligible:
        fee_year = (a["monthly_fee_usd"] or 0) * 12
        waiver_bal = a["min_balance_to_avoid_fee_usd"]
        rows = []
        for p in DEPOSITS:
            std = float(a["apy_regular_pct"])
            best, condition = best_rate(a, p)
            promo_rate, promo_label = promo_year1_rate(a, p)
            year1_rate = promo_rate if promo_rate is not None else best
            bonus_usd, bonus_label = cash_bonus_for(a["id"], p)
            short_rate = (
                4.25 if (a["id"] == "cit-platinum-savings" and p >= 5_000)
                else (4.40 if a["id"] == "sofi-savings" else (4.50 if a["id"] == "marcus-online-savings" and p <= 1_000_000 else best))
            )
            bal_3m = fv(p, short_rate, 0.25)
            bal_6m = fv(p, 4.25 if (a["id"] == "cit-platinum-savings" and p >= 5_000) else (4.40 if a["id"] == "sofi-savings" else best), 0.50)
            if a["id"] == "marcus-online-savings" and p <= 1_000_000:
                bal_6m = fv(p, 4.50, 0.25) * ((1 + 0.035) ** 0.25)

            fee_applies_by_balance = fee_year if (waiver_bal is None or p < waiver_bal) else 0.0
            row = {
                "deposit_usd": p,
                "standard_apy_pct": std,
                "best_apy_pct": best,
                "best_condition": condition,
                "promo_year1_apy_pct": promo_rate,
                "promo_label": promo_label,
                "year1_effective_apy_pct": year1_rate,
                "cash_bonus_usd": bonus_usd,
                "cash_bonus_label": bonus_label,
                "balance_3m": round2(bal_3m),
                "interest_3m": round2(bal_3m - p),
                "balance_6m": round2(bal_6m),
                "interest_6m": round2(bal_6m - p),
                "fdic_insured_usd": min(p, 250000),
                "fdic_uninsured_usd": max(0, p - 250000),
                "fdic_joint_insured_usd": min(p, 500000),
                "fdic_trust5_insured_usd": min(p, 1250000),
                "annual_fee_if_not_waived_usd": round2(fee_year),
                "annual_fee_at_this_balance_usd": round2(fee_applies_by_balance),
            }
            for y in YEARS:
                if y == 1:
                    bal = fv(p, year1_rate, 1)
                else:
                    bal = fv(p, year1_rate, 1) * ((1 + best / 100.0) ** (y - 1))
                row[f"balance_{y}y"] = round2(bal)
                row[f"interest_{y}y"] = round2(bal - p)
                row[f"net_interest_{y}y"] = round2(bal - p - fee_year * y)
                row[f"total_return_with_bonus_{y}y"] = round2(bal - p + bonus_usd)
                if y == 1:
                    fb = bal
                else:
                    fb_rate = min(best, national_savings)
                    fb = fv(p, year1_rate, 1) * ((1 + fb_rate / 100.0) ** (y - 1))
                row[f"fallback_balance_{y}y"] = round2(fb)
                row[f"fallback_interest_{y}y"] = round2(fb - p)
            rows.append(row)

        y1_ref = next(r["year1_effective_apy_pct"] for r in rows if r["deposit_usd"] == 250_000)
        max_day1_principal = math.floor((250_000.0 / (1.0 + y1_ref / 100.0)) * 100) / 100.0
        projections.append(
            {
                "id": a["id"],
                "brand": a["brand"],
                "account_name": a["account_name"],
                "cert": a["cert"],
                "mobile_app": a["mobile_app"]["value"],
                "standard_apy_pct": a["apy_regular_pct"],
                "apy_as_of": a["apy_as_of"],
                "apy_source": a["sources"][0]["url"],
                "monthly_fee_usd": a["monthly_fee_usd"],
                "min_balance_to_avoid_fee_usd": a["min_balance_to_avoid_fee_usd"],
                "fdic_limit_usd": 250000,
                "max_day1_principal_for_full_year1_fdic_usd": max_day1_principal,
                "rows": rows,
                "promo": PROMO_YEAR1.get(a["id"]),
            }
        )

    # ---- Leaderboards by deposit size --------------------------------------
    leaderboard = []
    for p in DEPOSITS:
        ranked = []
        for a in eligible:
            rate, cond = best_rate(a, p)
            promo_rate, promo_label = promo_year1_rate(a, p)
            eff = promo_rate if promo_rate is not None else rate
            bonus_usd, bonus_label = cash_bonus_for(a["id"], p)
            ranked.append((eff, a, cond, rate, promo_label, bonus_usd, bonus_label))
        ranked.sort(key=lambda x: (x[0], x[5]), reverse=True)
        leaderboard.append(
            {
                "deposit_usd": p,
                "banks_needed_single_owner": math.ceil(p / 250000),
                "banks_needed_joint_two_owners": math.ceil(p / 500000),
                "banks_needed_trust_five_beneficiaries": math.ceil(p / 1250000),
                "top": [
                    {
                        "id": a["id"],
                        "brand": a["brand"],
                        "account_name": a["account_name"],
                        "cert": a["cert"],
                        "mobile_app": a["mobile_app"]["value"],
                        "apy_pct": rate,
                        "year1_effective_apy_pct": eff,
                        "promo_label": promo_label,
                        "condition": cond,
                        "cash_bonus_usd": bonus_usd,
                        "cash_bonus_label": bonus_label,
                        "year1_interest_usd": round2(p * eff / 100.0),
                        "year1_total_with_bonus_usd": round2(p * eff / 100.0 + bonus_usd),
                        "year1_net_of_fee_usd": round2(p * eff / 100.0 - (a["monthly_fee_usd"] or 0) * 12),
                        "source": a["sources"][0]["url"],
                    }
                    for eff, a, cond, rate, promo_label, bonus_usd, bonus_label in ranked[:8]
                ],
            }
        )

    # ---- Multi-Charter FDIC Ladder Plans (strictly mobile_app == 'yes' & 1 slot per CERT) ----
    mobile_eligible = [a for a in eligible if a["mobile_app"]["value"] == "yes"]

    no_condition_ids = {
        "cit-platinum-savings",
        "synchrony-hys",
        "marcus-online-savings",
        "barclays-tiered-savings",
        "capone-360-performance",
        "amex-hysa",
        "ally-savings",
        "sofi-savings",
        "schwab-investor-savings",
        "usbank-smartly-savings",
        "td-simple-savings",
        "chase-savings",
        "wf-way2save",
        "truist-one-savings",
    }

    def rate_no_cond(a):
        if a["id"] == "cit-platinum-savings":
            return 3.75
        return float(a["apy_regular_pct"])

    def rate_max_cond(a, slot_cap):
        r, _ = best_rate(a, slot_cap)
        pr, _ = promo_year1_rate(a, slot_cap)
        return pr if pr is not None else r

    ladders = []
    ladder_configs = [
        ("no-conditions", "Single Owner ($250k/bank, No Conditions)", 250_000, lambda a, cap: rate_no_cond(a),
         lambda a: a["id"] in no_condition_ids),
        ("max-rate", "Single Owner ($250k/bank, With Promo/Membership/Relationship)", 250_000, rate_max_cond,
         lambda a: True),
        ("joint-max-rate", "Joint 2-Owner ($500k/bank, Max Verified Rate)", 500_000, rate_max_cond,
         lambda a: True),
        ("trust5-max-rate", "Revocable/POD Trust 5 Beneficiaries ($1.25M/bank, Max Verified Rate)", 1_250_000, rate_max_cond,
         lambda a: True),
    ]

    for total in [250_000, 500_000, 1_000_000, 1_250_000, 2_500_000, 3_000_000, 5_000_000]:
        for kind, kind_label, per_bank_cap, rate_fn, filter_fn in ladder_configs:
            if kind in ("joint-max-rate", "trust5-max-rate") and total < 500_000:
                continue
            banks_needed = math.ceil(total / per_bank_cap)
            pool, seen_certs = [], set()
            candidates = sorted(
                [a for a in mobile_eligible if filter_fn(a)],
                key=lambda a: rate_fn(a, min(total, per_bank_cap)),
                reverse=True,
            )
            for a in candidates:
                if a["cert"] in seen_certs:
                    continue
                seen_certs.add(a["cert"])
                pool.append(a)

            chosen = pool[:banks_needed]
            distinct = len(chosen)
            remaining = total
            allocations = []
            for idx, c in enumerate(chosen):
                amt = min(per_bank_cap, remaining)
                remaining -= amt
                apy_slot = rate_fn(c, amt)
                allocations.append(
                    {
                        "brand": c["brand"],
                        "account_name": c["account_name"],
                        "cert": c["cert"],
                        "apy_pct": apy_slot,
                        "amount_usd": round2(amt),
                        "interest_1y_usd": round2(amt * apy_slot / 100.0),
                        "source": c["sources"][0]["url"],
                    }
                )
            insured_placed = sum(x["amount_usd"] for x in allocations)
            interest = sum(x["interest_1y_usd"] for x in allocations)
            blended = (interest / insured_placed * 100.0) if insured_placed > 0 else 0.0
            ladders.append(
                {
                    "total_usd": total,
                    "kind": kind,
                    "kind_label": kind_label,
                    "per_bank_cap_usd": per_bank_cap,
                    "banks_needed": banks_needed,
                    "distinct_banks_used": distinct,
                    "pool_size": len(pool),
                    "allocation_each_usd": round2(insured_placed / distinct) if distinct else 0,
                    "blended_apy_pct": round(blended, 4),
                    "year1_interest_usd": round2(interest),
                    "insured_usd": round2(insured_placed),
                    "uninsured_usd": round2(max(0.0, total - insured_placed)),
                    "status": "fully covered" if remaining <= 0 else f"${remaining:,.0f} exceeds {len(pool)}-bank charter pool",
                    "allocations": allocations,
                }
            )

    coverage_gap = []
    for amount in [100_000, 250_000, 500_000, 1_000_000, 1_250_000, 2_500_000, 3_000_000, 5_000_000]:
        coverage_gap.append(
            {
                "deposit_usd": amount,
                "single_owner_coverage_usd": min(amount, 250000),
                "uninsured_if_one_bank_usd": max(0, amount - 250000),
                "banks_required_single_owner": math.ceil(amount / 250000),
                "joint_coverage_two_owners_usd": min(amount, 500000),
                "banks_required_joint_two_owners": math.ceil(amount / 500000),
                "trust5_coverage_one_owner_usd": min(amount, 1250000),
                "banks_required_trust5_one_owner": math.ceil(amount / 1250000),
            }
        )

    out = {
        "open_date": open_date,
        "generated": date.today().isoformat(),
        "assumptions": {
            "compounding": "Future value uses APY as an annual compounded rate anchored to Account Open Date 2026-10-22: balance = deposit * (1 + APY)^years.",
            "constant_rate": "Scenario 'constant' holds today's verified ongoing APY unchanged after Year 1. Savings APYs are variable and can change at any time.",
            "fallback_rate": "Scenario 'fallback' applies Year-1 effective yield for Year 1, then min(account ongoing APY, FDIC national savings average 0.38%) for Years 2–10.",
            "fallback_rate_pct": national_savings,
            "fallback_source": "https://www.fdic.gov/national-rates-and-rate-caps",
            "fdic_limit": "Coverage is $250,000 single owner, $500,000 2-owner joint, and up to $1,250,000 revocable/irrevocable trust (5+ beneficiaries) per depositor per FDIC bank charter (CERT).",
            "fdic_source": "https://www.fdic.gov/resources/deposit-insurance/financial-products-insured",
            "fees": "Projections report gross interest and net-of-fee interest separately; cash opening bonuses are tracked separately and never mixed silently into ongoing APY.",
            "mobile_filter": "Multi-bank FDIC ladders include only accounts with confirmed mobile banking apps (excluding web-only Alto by BMO) and deduplicate strictly by FDIC Certificate (CERT).",
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
    print(f"returns.json written: {len(projections)} projected, {len(excluded)} excluded, {len(ladders)} ladder plans across {len({a['cert'] for a in mobile_eligible})} mobile-enabled FDIC charters")


if __name__ == "__main__":
    build()
