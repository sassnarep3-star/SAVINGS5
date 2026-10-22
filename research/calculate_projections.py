#!/usr/bin/env python3
"""Generate transparent, conditional savings-return scenarios from research.json.

No external packages are required. This script writes CSVs under data/ and is
intentionally explicit about variable APYs, offer conditions, source dates, and
unknown NYC rates. The estimates are scenarios, not rate forecasts.
"""
from __future__ import annotations

import csv
import json
from datetime import date
from math import prod
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESEARCH = ROOT / "research"
OPEN_DATE = date(2026, 10, 22)
DEPOSITS = (5_000, 25_000, 100_000, 250_000)
HORIZONS = (1, 3, 5)
FDIC_LIMIT = 250_000

with (DATA / "research.json").open(encoding="utf-8") as f:
    research = json.load(f)
SOURCE_BY_ID = {s["id"]: s for s in research["sources"]}
ACCOUNT_BY_ID = {a["id"]: a for a in research["accounts"]}
OFFER_BY_ID = {o["id"]: o for o in research["offers"]}


def year_end(years: int) -> date:
    return date(OPEN_DATE.year + years, OPEN_DATE.month, OPEN_DATE.day)


def apy_factor(apy_percent: float, days: int) -> float:
    return (1.0 + apy_percent / 100.0) ** (days / 365.0)


def interest_for_schedule(principal: float, schedule: list[tuple[int, float]], days: int) -> float:
    """Apply sequential APY windows, clipping each to the requested horizon."""
    remaining = days
    factor = 1.0
    for duration, apy_percent in schedule:
        if remaining <= 0:
            break
        applied = min(duration, remaining)
        factor *= apy_factor(apy_percent, applied)
        remaining -= applied
    if remaining > 0:
        # The final schedule entry is the post-promotion/base rate.
        factor *= apy_factor(schedule[-1][1], remaining)
    return principal * (factor - 1.0)


def source_fields(ids: list[str]) -> tuple[str, str]:
    uniq = list(dict.fromkeys(ids))
    return ";".join(uniq), ";".join(SOURCE_BY_ID[i]["url"] for i in uniq)


def rate_for(account_id: str, principal: int) -> tuple[float, str, str, list[str]] | None:
    if account_id == "barclays-tiered":
        rate = 3.65 if principal >= 250_000 else 3.50
        label = "3.65% tier at $250,000+" if principal >= 250_000 else "3.50% tier below $250,000"
        return rate, label, "2026-10-07", ["barclays_tiered"]
    if account_id == "sofi":
        return None
    account = ACCOUNT_BY_ID[account_id]
    variants = [r for r in account.get("standardRates", []) if r.get("projectionEligible")]
    if not variants:
        return None
    r = variants[0]
    return r["apyPercent"], r["label"], r["asOf"], account["sourceIds"][:1]


# Standard/current-rate scenario table. CIT and location-dependent rate views
# are deliberately excluded from this table; their status appears in review.
standard_scenarios: list[dict] = []
standard_keys = [
    ("barclays-tiered", "standard"),
    ("synchrony", "standard"),
    ("marcus", "standard"),
    ("sofi", "qualifying-activity"),
    ("sofi", "no-qualifying-activity"),
    ("sofi", "plus-membership"),
    ("amex", "standard"),
    ("capitalone", "standard"),
    ("ally", "standard"),
    ("barclays-select", "AARP-member"),
]
for account_id, scenario in standard_keys:
    for principal in DEPOSITS:
        for years in HORIZONS:
            end = year_end(years)
            days = (end - OPEN_DATE).days
            account = ACCOUNT_BY_ID[account_id]
            monthly_fee = 0.0
            source_ids: list[str]
            if account_id == "sofi" and scenario == "qualifying-activity":
                apy = 3.30
                rate_label = "3.30% with eligible direct deposit or $5,000 qualifying inflows every rolling 31 days"
                source_date = "2026-10-20"
                source_ids = ["sofi_rate_sheet", "sofi_savings"]
                gross = principal * (apy_factor(apy, days) - 1.0)
            elif account_id == "sofi" and scenario == "no-qualifying-activity":
                apy = 0.80
                rate_label = "0.80% without qualifying activity"
                source_date = "2026-10-20"
                source_ids = ["sofi_rate_sheet", "sofi_savings"]
                gross = principal * (apy_factor(apy, days) - 1.0)
            elif account_id == "sofi" and scenario == "plus-membership":
                # The official offer describes 4.70% on up to $20,000 and
                # 3.30% on the remaining savings balance. Model the higher
                # tier as a separate balance slice and subtract the listed fee.
                high_balance = min(principal, 20_000)
                regular_balance = principal - high_balance
                gross = (
                    high_balance * (apy_factor(4.70, days) - 1.0)
                    + regular_balance * (apy_factor(3.30, days) - 1.0)
                )
                monthly_fee = 10.0
                apy = 4.70 if principal <= 20_000 else 3.30
                rate_label = "4.70% on first $20,000; 3.30% on remaining balance"
                source_date = "Official rate page checked 2026-10-22; rate sheet dated 2026-10-20"
                source_ids = ["sofi_plus", "sofi_rate_sheet"]
            else:
                result = rate_for(account_id, principal)
                if result is None:
                    continue
                apy, rate_label, source_date, source_ids = result
                if account_id == "barclays-tiered":
                    source_ids = ["barclays_tiered"]
                elif account_id == "barclays-select":
                    source_ids = ["barclays_select"]
                else:
                    # Link the precise rate source where available.
                    primary = {
                        "synchrony": "synchrony_savings",
                        "marcus": "marcus_savings",
                        "amex": "amex_savings",
                        "capitalone": "capitalone_rates",
                        "ally": "ally_savings",
                    }[account_id]
                    source_ids = [primary]
                gross = principal * (apy_factor(apy, days) - 1.0)
            fees = monthly_fee * 12 * years
            net = gross - fees
            ids, urls = source_fields(source_ids)
            status = "conditional" if scenario in {"qualifying-activity", "AARP-member"} else "conditional-paid" if scenario == "plus-membership" else "standard"
            if scenario == "no-qualifying-activity":
                status = "standard-default"
            assumption = "APY held constant; principal remains on deposit; no taxes or cash bonuses."
            if scenario == "qualifying-activity":
                assumption += " Qualifying inflows continue every rolling 31 days."
            elif scenario == "no-qualifying-activity":
                assumption += " No eligible direct deposit or qualifying deposits are received."
            elif scenario == "AARP-member":
                assumption += " Active AARP membership; variable 4.25% APY held constant."
            elif scenario == "plus-membership":
                assumption += " $10/month membership fee charged for every month; no waiver/other Plus benefit assumed; split-balance tier as described by SoFi."
            if principal == FDIC_LIMIT:
                assumption += " $250,000 is principal only; accrued interest may exceed the standard FDIC limit."
            standard_scenarios.append({
                "account_id": account_id,
                "bank": account["bank"],
                "product": account["product"],
                "scenario": scenario,
                "evidence_status": account["status"],
                "deposit_usd": principal,
                "years": years,
                "opening_date_assumed": OPEN_DATE.isoformat(),
                "horizon_end_date": end.isoformat(),
                "elapsed_days": days,
                "apy_percent_or_top_tier": f"{apy:.2f}",
                "rate_description": rate_label,
                "rate_source_date": source_date,
                "gross_interest_usd": f"{gross:.2f}",
                "membership_fee_usd": f"{fees:.2f}",
                "net_interest_after_membership_fee_usd": f"{net:.2f}",
                "cash_bonus_usd": "0.00",
                "estimated_ending_balance_before_bonus_usd": f"{principal + net:.2f}",
                "assumptions": assumption,
                "source_ids": ids,
                "official_source_urls": urls,
            })

with (DATA / "standard-projections.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(standard_scenarios[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(standard_scenarios)

# Conditional offer scenarios. The primary rate calculation includes only
# offers with a disclosed APY schedule. Cash-bonus-only TD/SoFi cases leave
# interest blank rather than inventing a base rate or assuming offers stack.
promotion_scenarios: list[dict] = []
for offer_id in ["barclays-200", "barclays-aarp-400", "sofi-apy-boost", "sofi-dd-bonus", "marcus-referral-boost", "cit-boost50", "td-200"]:
    offer = OFFER_BY_ID[offer_id]
    for principal in DEPOSITS:
        for years in HORIZONS:
            end = year_end(years)
            days = (end - OPEN_DATE).days
            gross: float | None = None
            cash_bonus: float | None = 0.0
            fee = 0.0
            rate_description = ""
            rate_dates = ""
            source_ids = offer["sourceIds"][:]
            assumptions = ["Offer eligibility is conditional; all variable APYs are held constant as stated."]
            include_bonus = False
            if offer_id == "barclays-200":
                apy = 3.65 if principal >= 250_000 else 3.50
                gross = principal * (apy_factor(apy, days) - 1.0)
                rate_description = f"Barclays Tiered Savings {apy:.2f}% APY tier"
                rate_dates = "2026-10-07"
                include_bonus = principal >= 25_000
                source_ids = ["barclays_tiered"]
                assumptions.append("Assumes a new eligible Barclays savings customer opens by 2026-10-31, funds/maintains $25,000 for 120 days, and receives the $200 bonus; source rate held constant.")
            elif offer_id == "barclays-aarp-400":
                gross = principal * (apy_factor(4.25, days) - 1.0)
                rate_description = "4.25% APY on all balance tiers"
                rate_dates = "2026-10-07"
                include_bonus = principal >= 40_000
                source_ids = ["barclays_select"]
                assumptions.append("Assumes active AARP membership, new eligible Select Savings account opened by 2026-10-31, required $40,000 maintained for 120 days, and $400 bonus if deposit threshold is met.")
            elif offer_id == "sofi-apy-boost":
                # Six calendar months from assumed open: 2026-10-22 to 2027-04-22.
                promo_days = (date(2027, 4, 22) - OPEN_DATE).days
                gross = interest_for_schedule(principal, [(promo_days, 4.40), (10**9, 3.30)], days)
                rate_description = "4.40% APY for 182 days, then 3.30% APY"
                rate_dates = "3.30% standard APY dated 2026-10-20; boost terms checked 2026-10-22"
                source_ids = ["sofi_boost_terms", "sofi_rate_sheet"]
                assumptions.append("Assumes the new-member 1.10-point boost begins immediately on opening and qualifying activity continues every 31 days; no SoFi Plus stacking.")
            elif offer_id == "sofi-dd-bonus":
                gross = None
                cash_bonus = 400.0
                rate_description = "Interest omitted: APY could be 3.30% or 0.80% depending on separate account activity"
                rate_dates = "2026-10-20 standard APY sheet"
                source_ids = ["sofi_bonus_terms", "sofi_rate_sheet"]
                assumptions.append("Bonus-only illustration: assumes eligible recurring income direct deposits total $5,000+ in the 25-day window. This cash bonus is not assumed to combine with another promotion.")
            elif offer_id == "marcus-referral-boost":
                promo_days = (date(2027, 1, 22) - OPEN_DATE).days
                gross = interest_for_schedule(principal, [(promo_days, 4.50), (10**9, 3.50)], days)
                rate_description = "4.50% APY for 92 days, then 3.50% APY"
                rate_dates = "Standard APY dated 2026-10-21; referral page checked 2026-10-22"
                source_ids = ["marcus_referral", "marcus_savings"]
                assumptions.append("Assumes a valid customer referral link and that the new primary owner qualifies; then-current standard APY is held at 3.50% after the offer.")
            elif offer_id == "cit-boost50":
                if principal >= 5_000:
                    promo_apy, base_apy = 4.25, 3.75
                    rate_description = "4.25% APY for 182 days, then last-published 3.75% APY (balance $5,000+)"
                else:
                    promo_apy, base_apy = 0.75, 0.25
                    rate_description = "0.75% APY for 182 days, then last-published 0.25% APY (balance below $5,000)"
                promo_days = (date(2027, 4, 22) - OPEN_DATE).days
                gross = interest_for_schedule(principal, [(promo_days, promo_apy), (10**9, base_apy)], days)
                rate_dates = "Underlying rates last explicitly accurate 2026-07-01"
                source_ids = ["cit_boost", "cit_rates", "cit_product"]
                assumptions.append("Stale-source scenario only: assumes valid BOOST50 enrollment by 2026-12-15 and uses the July 1, 2026 rate disclosure unchanged.")
            elif offer_id == "td-200":
                gross = None
                include_bonus = principal >= 10_000
                cash_bonus = 200.0 if include_bonus else 0.0
                rate_description = "Interest omitted: official numeric TD Signature APY not rendered"
                rate_dates = "TD APY accuracy date 2026-10-21; numeric rate unavailable"
                source_ids = ["td_offer", "td_rates"]
                assumptions.append("Bonus-only illustration; assumes a new eligible customer opens online, deposits $10,000 within 20 days, maintains it for the required 90 days, and receives the bonus. No interest is estimated.")
            if offer_id == "barclays-200":
                cash_bonus = 200.0 if include_bonus else 0.0
            elif offer_id == "barclays-aarp-400":
                cash_bonus = 400.0 if include_bonus else 0.0
            if offer_id == "cit-boost50":
                cash_bonus = 0.0
            if offer_id == "marcus-referral-boost":
                cash_bonus = 0.0
            if offer_id == "sofi-apy-boost":
                cash_bonus = 0.0
            total_known = None if gross is None else gross + (cash_bonus or 0.0)
            ids, urls = source_fields(source_ids)
            if principal == FDIC_LIMIT:
                assumptions.append("$250,000 is principal only; any accrued interest may exceed the standard FDIC limit.")
            promotion_scenarios.append({
                "offer_id": offer_id,
                "bank": offer["bank"],
                "product": offer["product"],
                "offer_kind": offer["kind"],
                "status": offer["status"],
                "deposit_usd": principal,
                "years": years,
                "opening_date_assumed": OPEN_DATE.isoformat(),
                "horizon_end_date": end.isoformat(),
                "elapsed_days": days,
                "rate_schedule_assumption": rate_description,
                "rate_source_date": rate_dates,
                "gross_interest_usd": "" if gross is None else f"{gross:.2f}",
                "cash_bonus_if_conditions_met_usd": "" if cash_bonus is None else f"{cash_bonus:.2f}",
                "known_interest_plus_bonus_usd": "" if total_known is None else f"{total_known:.2f}",
                "bonus_is_not_guaranteed": "yes",
                "assumptions_and_conditions": " ".join(assumptions),
                "source_ids": ids,
                "official_source_urls": urls,
            })

with (DATA / "promotion-projections.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(promotion_scenarios[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(promotion_scenarios)

# Rebuild the official-source matrix from the canonical evidence registry.
with (RESEARCH / "source-matrix.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow([
        "source_id", "organization", "official_page_title", "official_url",
        "checked_on", "effective_or_source_date", "verified_claims", "limitations_or_notes"
    ])
    for source in research["sources"]:
        writer.writerow([
            source["id"], source["organization"], source["title"], source["url"],
            source["checkedOn"], source.get("sourceDate", ""),
            "; ".join(source.get("supports", [])), source.get("notes", "")
        ])

print(f"Wrote {len(standard_scenarios)} standard/conditional rate rows to data/standard-projections.csv")
print(f"Wrote {len(promotion_scenarios)} conditional-offer rows to data/promotion-projections.csv")
print("Calendar-year endpoints:", ", ".join(f"{n}y={year_end(n).isoformat()} ({(year_end(n)-OPEN_DATE).days} days)" for n in HORIZONS))
