# Savings-return model: method and audit notes

**Scenario opening/funding date:** 2026-10-22<br>
**Amounts:** $5,000, $25,000, $100,000, and $250,000<br>
**Horizons:** 1, 3, and 5 calendar years, ending 2027-10-22, 2029-10-22, and 2031-10-22.<br>
**Rate-source snapshot:** Official pages checked 2026-10-22; each bank's displayed/effective date is preserved separately in the output.

## Formula

For a constant APY `r` expressed as a percentage and `d` elapsed calendar days:

```text
estimated interest = principal × ((1 + r / 100)^(d / 365) − 1)
```

For promotional periods, the model multiplies the effective APY growth factors for each period. For example, a six-month offer is modeled at the displayed introductory APY through 2027-04-22 (182 days from the assumed opening date), then at the disclosed standard APY for the remaining days. The three-month Marcus referral boost uses 92 calendar days through 2027-01-22.

The calculation uses APY as an effective annual yield and prorates it by elapsed days. Banks' actual daily balance, leap-year, interest-crediting, posting, and rounding conventions may create small differences. The source file identifies the APY and assumptions used on every row.

## Included scenarios

- Current official APY snapshots: Barclays Tiered, Synchrony, Marcus, SoFi (qualifying and non-qualifying activity), American Express, Capital One, Ally, and Barclays Select/AARP.
- SoFi Plus is separated from free standard savings: the model splits up to $20,000 at 4.70% and the remaining balance at 3.30%, then subtracts the listed $10/month membership fee. No fee waiver or other Plus membership value is assumed. This balance-split model is an approximation based on the offer's wording; review current terms before relying on it. [Official SoFi Plus page](https://www.sofi.com/sofi-plus/) and [rate sheet](https://www.sofi.com/legal/banking-rate-sheet/).
- Promotional scenarios: Barclays Tiered $200, Barclays Select/AARP $400, SoFi APY Boost, SoFi direct-deposit bonus, Marcus referral boost, CIT BOOST50, and TD $200. Each offer remains explicitly conditional. The SoFi rate boost and cash bonus are calculated separately; stacking is not assumed.
- CIT's 3.75% standard / 4.25% introductory values are included only in the conditional-offer scenario because the official APY disclosure is dated 2026-07-01. Do not read its result as a freshly verified October rate. [CIT rate disclosure](https://www.cit.com/cit-bank/resources/products-and-rates).
- U.S. Bank rates displayed for ZIP 55402, and all unresolved New York-specific rates, are excluded from NYC return calculations. TD, Chase, Bank of America, Citi, Wells Fargo, and PNC do not receive guessed APYs.

## Interpretation and exclusions

- All savings rates are variable. The table holds the published value constant solely to compare arithmetic; it does not forecast future rate changes or guarantee that an account can be opened at that rate.
- Interest estimates assume an initial lump-sum deposit, no withdrawals, no recurring contributions, and no taxes. Bonuses are shown as conditional gross amounts; tax is not deducted.
- Except for SoFi Plus, no subscription or monthly service fee is included. The account rows identify fee waivers and eligibility conditions separately.
- Cash bonuses may be paid after a hold period; the projection adds the bonus once inside the chosen horizon when the stated eligibility is met, but does not credit interest on a future bonus before it is paid.
- Every $250,000 deposit starts at the standard single-bank/ownership-category FDIC limit before accrued interest. The model does not know the user's other deposits at that legal bank, so its coverage warning is not a personal coverage determination. The FDIC limit includes interest. [FDIC FAQ](https://www.fdic.gov/resources/deposit-insurance/faq).
- SoFi's optional Insured Deposit Program is not assumed; standard FDIC coverage only is used. [Official program terms](https://www.sofi.com/banking/fdic/sidpterms/).

## Reproduction

Run from the repository root:

```bash
python research/calculate_projections.py
```

This regenerates:

- [`data/standard-projections.csv`](../data/standard-projections.csv): 120 account/scenario/amount/horizon rows.
- [`data/promotion-projections.csv`](../data/promotion-projections.csv): 84 offer/amount/horizon rows, including blank interest when an official APY was not retrieved.

Both files include source IDs and official URLs on every row. Source metadata and checked/effective dates are in [`source-matrix.csv`](source-matrix.csv); underlying verified facts are in [`data/research.json`](../data/research.json).
