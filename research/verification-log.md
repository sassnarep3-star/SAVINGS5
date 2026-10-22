# Verification log — 2026-10-22

Every figure in `data/` was transcribed from a page fetched on this date. This log records what was fetched and what it
showed, including the pages that failed. It is the audit trail behind the site.

## Government sources

| Page | Result used |
|---|---|
| FDIC, *Are My Deposit Accounts Insured by the FDIC?* (`fdic.gov/resources/deposit-insurance/financial-products-insured`) | Ownership categories; $250,000 single, $250,000 per co-owner joint, $250,000 certain retirement, trust formula owners x beneficiaries x $250,000 capped at $1,250,000 per owner; covered vs non-covered products. |
| FDIC, *Understanding Deposit Insurance* | Coverage is per depositor, per ownership category, per bank; same-category balances are added together. |
| FDIC, *National Rates and Rate Caps — October 2026* | Savings 0.38% national rate, 4.63% cap; 12-month CD 1.76%; 60-month CD 1.41%; Treasury 12-month 4.54%, 60-month 5.09%; all as of 2026-10-19. |
| FDIC BankFind institutions API | 16 institutions: NAME, CERT, ASSET, DEPDOM, ACTIVE, INSFDIC, BKCLASS, INSDATE, ESTYMD, CITY, STALP. Discover Bank (5649) returned ACTIVE = 0. |

## Bank rate pages

| Bank | Page | What it showed |
|---|---|---|
| Synchrony | `synchrony.com/banking/products/hys-core` | 3.55% APY, no minimum deposit, no minimum balance, no monthly fees, app for iOS/Android. |
| Marcus | `marcus.com/us/en/savings/high-yield-savings` | 3.50% APY as of 2026-10-21, no fees, no minimum deposit. |
| Marcus referrals | `marcus.com/us/en/savings/referrals` | +1.00% APY for 3 months for both parties, up to 5 referrals, combined 3.75% for the year. |
| Ally | `ally.com/bank/online-savings-account/` | 3.1% as of 10/21/26, no monthly fees or minimum balance, 10 withdrawals per statement cycle. |
| American Express | `americanexpress.com/en-us/banking/online-savings/account/` | 3.20% APY, no minimum balance, no monthly fees. |
| Capital One | `capitalone.com/bank/savings-accounts/` | 3.20% variable APY (category page); no fees, no minimums. Product page rendered APY as `NaN`. |
| SoFi | `sofi.com/banking/high-yield-savings-account/` | 3.30% APY as of 10/20/26; 4.40% with 1.10% boost for up to 6 months; $50/$400 bonus; FDIC up to $3M via network. |
| U.S. Bank | `usbank.com/.../savings-account-interest-rates.html` | Effective 2026-10-21, ZIP 55402: standard 0.05%; relationship tiers 1.00% / 2.00% / 3.50%. |
| Wells Fargo | `wellsfargo.com/savings-cds/rates/` | Way2Save 0.01%; Platinum new-customer 3.25% on $25,000+; standard Platinum 0.01%; $12 fee waived at $3,500. |
| Bank of America | `bankofamerica.com/salesservices/deposits/resources/personal-schedule-fees/` | Advantage Savings: $8.00 monthly fee, waived at $500 daily balance, $100 minimum to open, first six months waived. |
| Bank of America rates | `bankofamerica.com/deposits/bank-account-interest-rates/` | ZIP/county-gated PDF only. The Virginia/non-branch-states sheet (effective 2026-10-21) shows 0.04% APY on all tiers. Not New York. |
| Chase | `chase.com/personal/savings/savings-account` and ABSF PDF | $5 monthly fee, five waivers, no minimum to open, ZIP-gated rates. |
| Chase offer | `account.chase.com/consumer/banking/savingsoffer` | $100 on $5,000-$9,999; $200 on $10,000+; must hold 90 days; expires 2027-01-27. |
| Citibank | `citi.com/banking/savings-account` | Accelerate Savings, relationship tiers, $4.50 monthly fee waived at $500 average monthly balance. APY rendered as `:BLUE_AccSavings_Rate%`. |
| Citibank guide | `citi.com/banking/personal-banking-guide/savings/how-to-open-a-savings-account` | No minimum opening deposit; zero balance for 90 days subject to closure. |
| Truist | `truist.com/savings/truist-one-savings/disclosures-and-fees` | 0.01% rate and APY on every tier as of 2026-09-28; $50 minimum; $5 fee with four waivers; $5 per withdrawal over six. |
| TD Bank | `td.com/us/en/personal-banking/savings-accounts/rates` | Rate tables served empty; disclosures state APY accuracy as of 10/21/2026 but no numbers. $0 minimum, $5 fee, $300 waiver. |
| PNC | `pnc.com/en/personal-banking/banking/savings/high-yield-savings.html` | Page returned "This Product Isn't Available in Your Area"; rate center ZIP-gated. Title carries 3.15% APY, not confirmed in body. |
| Fifth Third | `53.com/.../bank/savings.html` | $0 minimum, $0 fee with $500 balance or a Fifth Third checking account, otherwise $7.50; no APY published. |
| Charles Schwab | `schwab.com/savings` | 0.15% APY, $0 monthly fees, unlimited ATM rebates, application by mail/phone/branch. |

## Pages that failed or were unusable

- `citi.com/banking/savings-accounts` — 404.
- `truist.com/personal-banking/savings` — 404; `truist.com/personal-banking/checking-savings/savings` — 404. The working URL is `truist.com/savings`.
- `chase.com/personal/checking/checking-offers` and `chase.com/personal/savings/savings-account/offers` — 404.
- `bankofamerica.com/deposits/savings/savings-rates/` and `.../savings-offers/` — HTTP 405.
- `media.bac-assets.com/DigitalDeposit_NY.pdf`, `..._NY_NY.pdf`, `..._NY_NY_Excluding_DC.pdf` — "Not found".
- `ally.com/bank/savings-account/` — 404; the working URL is `ally.com/bank/online-savings-account/`.
- `online.citi.com/US/JRS/pands/detail.do?ID=CurrentRates` — no rate content served.
- `pnc.com/.../deposit-rates/high-yield-savings.html` — "This product is not available in your area" (ZIP 15222).
- FDIC API `search=` parameter returns zero rows; `filters=` works (e.g. `filters=NAME:SoFi*`).

## Deliberate omissions

- Third-party aggregator rates were not used. One example: a comparison site listed a Truist savings APY that Truist itself
  did not publish on its product page — the official disclosure page was found later and used instead.
- No mobile-app claim was made for Marcus, American Express or Fifth Third, because their savings pages do not name an app.
- No security ranking was produced.
