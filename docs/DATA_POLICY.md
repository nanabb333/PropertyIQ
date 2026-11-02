# Public data policy

This source snapshot contains no real Zillow ZHVI/ZORI, FRED, Freddie Mac, BLS, Census or other source observations and no artifact derived from those observations. Copied modules contain financial formulas, fictional templates and compatibility identifiers, not a dataset export. The invented market generator is independent of the private research dataset.

Excluded material includes raw and processed files, databases, trained research artifacts, prospective registries, reports with real numeric outputs, charts/screenshots based on licensed observations, HTTP bodies/headers, reviewer records and private run receipts. No data will be fetched to repair a missing file: the application has no acquisition path.

Official references checked during release review on 2026-10-29:

- Zillow Research data: https://www.zillow.com/research/data/
- Zillow terms (page states updated 2025-10-28): https://www.zillow.com/corporate/terms-of-use/
- FRED terms and underlying third-party rights: https://fred.stlouisfed.org/legal/
- Freddie Mac content policy: https://www.freddiemac.com/terms/linking
- NY Fed reference-rate conditions: https://www.newyorkfed.org/privacy/termsofuse

Research download or analysis permission was not treated as permission to mirror raw data in GitHub or relicense it under MIT. The Zillow aggregate-display exception was not assumed to apply to this release. Relevant attribution would need to accompany a separately approved real-data display, but it is not a substitute for permission. No such display is shipped here.

Only user-triggered synthetic review JSON can be downloaded from the application. Do not load personal records or credentials; no upload, free-form credential entry, OAuth or provider connection exists. The Streamlit server binds loopback and disables its usage telemetry. Browser framework infrastructure is not a claim that all operating-system or browser background networking is absent.

## v1.2 ZIP-token fixture boundary

The three ZIP strings used as scenario keys are identifiers, not a copied geographic mapping or market dataset. All scenario constants and type/layout/area factors are authored fictional assumptions, documented in METHODS.md. Five-digit format validation does not establish postal assignment. No city/state labels, real ZIP rents, sales comparables, valuations or observed trends are shipped. Unmatched tokens use an explicit generic fallback. User profile edits remain local session inputs and are never used to calibrate the fictional index generator. External v1.2 tests, preview logs, screenshots and the new freeze manifest remain outside the release package.
