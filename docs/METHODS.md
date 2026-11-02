# Methods and limitations

## Synthetic market observations

`src/public_demo.py:synthetic_markets()` generates 120 months from January 2015 through December 2024 for Harbor, Cedar and Summit, all fictional. Price and rent indices combine an arbitrary near-100 baseline, exponential drift and sine functions; the price formula also includes a mathematically specified dip. Constants are authored demonstration parameters, not fitted to real observations or labeled historical events. No noise seed, external input or source-data fetch is involved. The generator version and canonical SHA-256 are exported in SYNTHETIC_PROVENANCE.json.

## Forecast demonstration

Each fictional market uses the same expanding-window origins: at least 60 months of history, then an observed generated target 3, 6, 9 or 12 months later. Origins per market/model are respectively 58, 55, 52 and 49. Predictions receive only the prefix ending at origin. Models are no change, extrapolated 12-month growth, and seasonal naive. At a 12-month horizon seasonal naive equals no change; identical results are expected, not independent corroboration.

Growth is `100 * ln(target_index / origin_index)`. Errors, MAE and RMSE are in percentage points of log growth, not percentage errors of property prices. There is no hyperparameter selection, real forecast claim, interval calibration or future outcome verification. The generated suffix serves only as a synthetic target for testing evaluation mechanics.

## Financial and scenario calculations

Copied financial/scenario modules are byte-preserved relative to the allowlist recorded in ORIGIN_MANIFEST.json. Synthetic templates use fictional purchase prices, rents, debt and expenses. Public wrappers rename the property identifier; compatibility geography IDs do not make the inputs observed data.

The engine compares hold/occupy, sell/hold cash and rent out with common alternative-housing costs. NPV uses normalized opportunity-capital cash flows and configured discounting; terminal wealth is undiscounted. Reserve release, financing and terminal sale are accounted separately. There is no automatic strategy ranking. Tax calculations are illustrative arithmetic, not a jurisdiction-specific legal model. Default missing adjusted basis withholds all after-tax comparisons.

Scenario lab changes appreciation while holding the selected property's other inputs constant. These are matched hypothetical assumptions, not causation, probabilities or automatically applied market forecasts.

## Evidence and reviewer control

Six fixed questions map to deterministic read-only functions. No external model chooses tools or supplies numbers. This does not reproduce or claim the research agent's 16-tool coverage. Human choice is unset by default and cannot be inferred from financial maxima. Explicit choice plus confirmation creates a session-only demonstration packet; financial input changes invalidate it. The packet is neither an authenticated reviewer record nor a production decision.

## v1.2 Property Profile architecture and scenario contract

The existing financial engine and twelve copied source modules are unchanged. Minimal extensions remain in already approved project-owned paths: src/public_demo.py holds the frozen PropertyProfile dataclass, format/range validation, authored fixture selector, explicit suggestion application, summary calculation and profile-to-finance adapter. app/streamlit_app.py keeps widget/session/source management and the explicit apply interaction separate. Existing case() remains the v1.1 contract; profile_case() wraps the same engine, adding inspectable metadata. No dependency or external source file was added.

Property types: Condominium, Single-family home, Townhouse, Multifamily, Other. Layouts: Studio (0/1), 1/1, 2/1, 2/2, 3/2, or explicit custom counts. Bedrooms 0–20, positive bathrooms up to 20; interior area must be positive finite. Optional parking is 0–20, year built 1600–2026 for this fixture version. ZIP accepts five ASCII digits; no postal assignment or city/state mapping is verified. Descriptive fields do not directly alter numeric financial outcomes. The adapter records them in the input fingerprint so dependent human reviews still expire after edits.

### Authored fixture constants — not local statistics

| ZIP token | Base rent USD/month | Base HOA USD/month | Insurance USD/year | Maintenance USD/year |
|---|---:|---:|---:|---:|
| 20008 | 2400 | 350 | 1000 | 2000 |
| 19103 | 1800 | 250 | 1200 | 2300 |
| 15213 | 1300 | 150 | 1100 | 2600 |
| Generic fallback | 1500 | 200 | 1200 | 2400 |

Version: synthetic-property-profile-v1.2. These are independently authored demonstration constants, not rents, insurance quotes, HOA fees, costs, comparable sales or trends measured in those ZIPs. ZIP identifiers are tokens only. No real valuation or rent ranges are offered.

Suggested rent = base rent × area factor × property-type factor × layout factor, rounded to cents. Area factor = clip(interior sqft / 1000, 0.5, 2.0). Property-type rent/HOA factors respectively: Condominium 1/1; Single-family 1.1/0; Townhouse 1.05/0.5; Multifamily 1.6/0; Other 1/0.5. Layout factors: Studio 0.7; 1/1 0.85; 2/1 0.95; 2/2 1; 3/2 1.15; Custom 0.7 + 0.15×beds + 0.05×baths. Suggested HOA = base HOA × HOA factor, rounded to cents. Insurance/maintenance remain the fixed authored annual amounts. Factors are pedagogical choices, not fitted models, empirical adjustments, probabilities or local benchmarks.

Only four fields can be applied by explicit confirmation and button action. Current value, purchase price, loan balance, tax basis, interest rate/term and property tax are excluded from proposals. Before application the UI shows current/suggested values and units. Application receipts retain fixture/version/source/profile hash, formula factors, definition, unit and applied value. Changing profile does not rewrite historical receipts or user financial values; overriding a field removes its receipt and marks User input. All remaining model inputs are visible in the shared evidence expander.

Financial independence is preserved: purchase price is historical and does not recalculate closing cost/equity/basis; market value does not change debt or basis; rent does not automatically change the separately configured alternative-housing assumption. A zero-debt template exposes a default 240-month term for explicit later debt edits, with the displayed rate (possibly zero); no rate is inferred from ZIP. Illustrative tax validation still enforces compatible basis/depreciation inputs and withholds incomplete after-tax results. The operating-expense control is maintenance only; HOA/taxes/insurance and other template utility/management/leasing/repair/reserve inputs are separate and inspectable.

Sensitivity rows retain matched-input definitions, financial/source fingerprints, profile version, units and review requirements. Financial/scenario evidence exposes profile/proposal/source/application context. The human review hash includes profile and provenance, while explicit review exports contain result rows and an input hash rather than raw ZIP/layout details. All state stays in session memory; no cache decorator, file write, logging, geocoding, analytics or external request was introduced. No automatic ranking, appraisal, tax-law determination or real-world accuracy claim is made.
