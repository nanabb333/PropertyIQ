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
