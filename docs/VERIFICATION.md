# Final source candidate verification

## Desktop-first release reassessment — 2026-11-01

This reassessment supersedes the earlier mobile-blocked publication decision for the desktop-first scope only. The user explicitly deferred mobile viewport QA. Mobile responsiveness remains UNVERIFIED at 320×700, 375×812, 390×844 and 430×932; no mobile compatibility or mobile QA completion is claimed.

All six desktop workflow pages were opened in the existing local browser: Market explorer, Financial comparison, Scenario lab, Forecast lab, Evidence explorer and Human review. Expected page headings rendered without visible application exceptions. Existing desktop screenshots remain evidence of the previously inspected layouts, not mobile evidence. The complete 125-test public suite was rerun after these documentation changes; workflow tests exercise all six pages and profile/application/override/session/review behavior. See the external desktop verification record for execution results and final hashes.

No runtime source, tests, financial formulas, dependencies, synthetic fixtures, screenshots or licensing scope changed in this reassessment. Only README, this verification document and the included-file hash manifest were updated. All 97 allowlisted paths remain; EXCLUDED_FILES.json remains unchanged. External QA metadata and the new complete SHA-256 freeze are outside the release package. The existing isolated Python environment was reused; no fresh install is claimed.

Decision: GO for desktop-first portfolio publication readiness, with the disclosed mobile/platform/financial/research limitations. No additional desktop-specific release blocker was identified in this scoped review. This is not an authorization to commit, push, change visibility or deploy. Real datasets, provider authentication, Keychain and inference remain excluded. Historical zero-history and account-verification statements below describe their original gates, not the current repository state.

## v1.2 Property Profile and fictional ZIP scenarios — 2026-11-01

This section supersedes the current-version claims below. Prior v1.1/Step 3B freezes are historical and cannot certify v1.2. Preflight found a clean main branch at 634afe2dbd7dd04a945f15afd13f985fc6ad95cf (restored editable value), the intended origin URL, 97 tracked files byte-identical to the reviewed v1.1 freeze, and no unexpected nonignored files. Existing ignored .venv and Python caches were local runtime artifacts, not release contents. Nothing was reset or overwritten. Baseline: 99/99 tests passed before implementation.

The new profile model/validation, fixture selector, explicit financial application and pure engine adapter are separated as helpers in src/public_demo.py. UI/session/provenance handling stays in app/streamlit_app.py. No financial engine contract or dependency changed; all 12 copied engine/scenario module hashes remain unchanged. All 99 pre-existing test method bodies are AST-identical to the baseline. New helpers and fixtures remain within the existing approved project-authored paths, with no expansion of the 40-path MIT scope.

Implemented fields: five-digit ZIP (format only), all five property types, standard/custom layouts, interior sqft, optional parking/year built, independent current value, purchase price, debt, rent, HOA, property tax, insurance and maintenance; explicit loan rate/term and illustrative tax basis. Compact summaries distinguish entered values, calculated USD/sq ft, source labels and unavailable market evidence. No city/state mapping is asserted. See METHODS.md for exact fixture constants, factors, units, ranges and limitations.

ZIP/type/layout/area edits change proposal metadata and the review fingerprint, never financial values automatically. An explicit checkbox plus apply button replaces only the four previewed rent/HOA/insurance/maintenance fields. Per-field receipts preserve the original applied fixture/version/source/profile hash even after a later profile change. Manual edits remove that field's receipt and mark User input. Market value/purchase/debt/basis remain independent; scenarios/evidence/review share the resulting assumptions. Per-case non-widget drafts preserve user edits and matching source labels even when Streamlit cleans up inactive widgets. Invalid drafts clear prior review before stopping, including when later reverted. All raw profile data remains in local session memory; no input file/log/analytics/network persistence was added. Existing explicit result export omits raw ZIP/layout fields. Invalid inputs fail closed without displaying stale results.

Automated suite: **125/125 passed**, including the unchanged 99 baseline tests and 26 focused additions covering valid/invalid ZIPs, all property types, standard/custom layouts, zero/nonfinite area, optional fields, value/sqft, generic fallback, formula/version/unit provenance, explicit application, override preservation, all-strategy recalculation, debt/basis/purchase independence, workflows/session isolation, review invalidation, and no network/files/logging in pure profile calculations. pip check and Git diff whitespace checks passed. The existing isolated Python 3.14/macOS arm64 environment was reused; no fresh installation or broader platform validation is claimed for v1.2.

Browser verification: all six actual workflow pages opened with their expected headings. Unsupported token 99999 displayed GENERIC_FALLBACK and not-observed-data wording; the apply button was disabled until explicit consent, then only the previewed fields changed. Financial inputs, source labels, profile summary and calculated unit value were visually inspected. Desktop screenshots included 1600×900 and intermediate-width 1057×1066/1418×1066 captures with wrapping and sidebar scrolling. The tooling did not expose controlled viewport sizing, and a zoom attempt did not establish a mobile breakpoint: **phone-width behavior remains unverified**; mobile testing is deferred and is outside the desktop-first acceptance scope. The updated financial screenshot contains approved fictional defaults only; no private user property values were captured. External browser proof remains outside the package.

The release still has 97 allowlisted files. INCLUDED_FILES.json is regenerated; EXCLUDED_FILES.json still excludes 294 original candidate versions and all raw/private/runtime material. Its same-path overlaps are separately authored public replacements (.gitignore, .streamlit/config.toml, empty tests/__init__.py), not the excluded original content. Original Git history is not copied into release files; this working repository retains its existing legitimate release history. A new complete v1.2 SHA-256 freeze and this run's audit/test/browser records are stored outside the repository and are excluded from the public package.

Effective MIT, the approved path scope, dependency lock/inventory and all 55 third-party legal texts remain unchanged. Newly authored fixture numbers are explicitly fictional and use no Zillow/FRED/Freddie Mac observations, restricted derivatives or geocoding lookup. Pattern/import/artifact scans provide scoped evidence, not an absolute secret, legal or vulnerability guarantee. No real credentials, OAuth, Keychain, paid API, commit, push, deployment or visibility action is performed.

Reproduce: `python -B -m unittest discover -s tests -v`, `python -m pip check`, then `python -B -m streamlit run app/streamlit_app.py --server.port 8512`. The old pre-commit validator's zero-history/remote assertion intentionally fails after legitimate commits; privacy/hash checks are audited separately. Any subsequent source change invalidates the v1.2 freeze. The desktop-first candidate is eligible for publication review; mobile acceptance is deferred. Commit, push, visibility changes and deployment still require separate authorization. This is scenario customization, not verified valuation or demonstrated prediction improvement.


## Local property-value input restoration — 2026-11-01

This local update supersedes the current-code test count and freeze claims below; the Step 3B details remain historical records. The old external freeze and future-push script no longer match this modified candidate. No commit, push, remote change or deployment was performed for this update.

Root cause: the original local app/forms.py automatically rendered property.current_value via number_input, while the public UI reduced the controls to preset selection and read-only metrics, and case() had no override parameter. The shared sidebar now includes Current market value (USD), initialized from approved fictional defaults. A positive finite override replaces only current_value before deterministic compare(); unchanged loan, rent, acquisition and tax basis assumptions remain explicit. All financial workflows use the same result and input fingerprint, so changing value invalidates an earlier human review. Values are held in the local Streamlit session; the update adds no file/log/network persistence. Existing user-triggered synthetic result download remains available.

Baseline: all existing 94 public tests passed before changes. Updated suite: **99 tests passed** (66 unchanged portable finance tests, 26 synthetic/demo tests, 7 UI tests). Five new tests cover exact sale-proceeds and terminal-value deltas, all three strategies, illustrative taxes, sensitivity/evidence, invalid input, editable displayed value, review invalidation and session/case isolation. The network/credential lookup guard also runs with an edited value. Browser verification changed fictional USD 650,000 to 750,000 and confirmed the metric and all three financial rows updated. Source financial engines, external observations and private data were not changed or imported. No dependency was added.

The candidate still contains 97 files; INCLUDED_FILES.json was regenerated. The old pre-commit validator intentionally flags the existing initial commit/refs/origin, which were already present at preflight; its content/privacy scan has no findings. Git history was preserved. Current local test/scan/screenshot records are outside the package. Any future publication requires a new reviewed freeze and separate authorization.


Review date: 2026-10-29. Step 3B decision: CONDITIONAL GO for a later first private push. The author explicitly approved the exact 40 contributions and MIT is now active for that scope. Separate commit/push authorization and destination privacy/empty-history verification remain required. No Git write or publication was performed.

## Exact release scope

Root INCLUDED_FILES.json lists every release file, with SHA-256 and byte size. Its own entry has null digest/size to avoid impossible recursive self-hashing; the verifier still checks its presence and exact file set. EXCLUDED_FILES.json lists 294 of 306 original nonignored candidates excluded in full, with 12 source modules copied in full. Four portable test AST nodes were extracted from an otherwise excluded original test file. Ignored datasets, private records, environments and Git metadata are also excluded by policy; 294 is not a count of all private ignored files.

The candidate contains 97 release files: 55 upstream legal notice files and 42 other project/provenance/demo files. The per-file rights matrix covers all 97; 40 entries license only the author-approved project-authored expression under MIT. The effective standard LICENSE instrument and upstream dependency metadata are separate from those 40 contributions, alongside the 55 notices. The proposal was removed and replaced by LICENSE; the release still has 97 files. The staging .git directory is local infrastructure, not a release file.

## Clean environment and execution

A second new venv was created outside the release and installed from requirements-lock.txt, with no access to the private research data directory. Python 3.14.5, macOS arm64; no system site packages. Installation completed successfully from PyPI. pip check: No broken requirements found. Thirty-four pinned runtime distributions matched the inventory. Other OS/Python combinations remain unverified.

Full public suite: **94 tests, 94 passed, 0 failed**. Step 3B post-activation regression passed in 1.465 seconds. The earlier fresh-install run passed in 12.473 seconds. The existing isolated environment was reused and revalidated; no new install was claimed in Step 3B. This is 66 portable finance tests, 23 synthetic/demo tests and 5 Streamlit UI tests; one UI test iterates all six workflows. It is not the private project's 852-test suite.

A separate fresh-environment AppTest pass rendered every workflow without exceptions:

| Workflow | Result | Checked behavior |
|---|---|---|
| Market explorer | PASS | Three invented series, 120 months each, no external observations |
| Financial comparison | PASS | Deterministic engine; missing tax results withheld |
| Scenario lab | PASS | Matched appreciation alternatives; no assigned probabilities |
| Forecast lab | PASS | Prefix-only training, 60-month minimum, synthetic score disclosure |
| Evidence explorer | PASS | Six fixed read-only local routes; unknown prompts rejected |
| Human review | PASS | No default; explicit confirmation; changed inputs clear choice |

Step 3B restarted the app using the isolated venv on 127.0.0.1:8504, confirmed `ok` at /_stcore/health, and stopped its own preview process. A separate AppTest pass rendered all six workflows without exceptions after activation. Local preview is not deployment. Browser inspection and screenshot capture used the same candidate UI on an earlier isolated 127.0.0.1:8502 preview. Both screenshots show only fictional demonstration content and were normalized to actual PNG encoding; no EXIF, local path or account metadata. AppTest checks behavior, not pixel-perfect cross-browser compatibility.

## Security, privacy and data provenance

Complete release-file scan: no personal home-directory literal, provider-key pattern, private-key block, credential file, database, raw observation file, private reviewer record or execution log identified. No symlinks or unexplained binary files; the only images are the two inspected synthetic screenshots. No OAuth, Keychain, native-helper or provider runtime is included. Mentioning excluded component names in manifests/documentation does not ship those components. Package notices retain upstream public author contact details as required attribution.

Reviewed generated formulas and fixed fictional inputs have no real-data ingestion, calibration or research output dependency. All twelve copied modules match the origin inventory; eleven match Phase 4A/4B creation receipts. Four selected original test nodes match structurally. These comparisons prove correspondence, not copyright ownership. The public core test additionally rejects socket creation and credential-environment lookup. The application imports no provider/network/keychain library; Streamlit's loopback browser/server infrastructure remains necessary.

Git check: zero commits, refs, loose objects, packed objects or remotes. All release files remain untracked; no commit/push/visibility change was made. Original project: 1,984 protected file hashes unchanged. Of 508 earlier Git metadata snapshot entries, 506 still match and two ephemeral refs under refs/codex/turn-diffs are now absent. These are platform-managed temporary capture/checkpoint references, not release content; their removal cause is not proven by the snapshot comparison. No restoration or Git mutation was attempted. This is a disclosed original-metadata difference, not a claim of byte-identical original Git metadata. Generated bytecode caches were removed from staging; environments, install logs and local test receipts are outside the candidate.

Scans and tests provide scoped evidence, not a guarantee against every secret type, dependency vulnerability or unknown ownership claim. This is not a complete CVE audit or legal opinion.

## Licensing

No concrete external source-code ownership or incompatible-license conflict was identified. One initializer lacks a separate creation record; this alone is not an exclusion reason. The author explicitly confirmed sufficient rights and absence of undisclosed restrictions for the exact 40 contributions in Step 3B. **Root LICENSE is active only for those project contributions.** The proposed artifact was removed. All independent third-party materials remain excluded from the project grant. See PROVENANCE_RIGHTS_MATRIX.json, AUTHOR_RIGHTS_DECLARATION.md and LICENSE_REVIEW.md.

All 55 upstream legal files remain separate from the scoped project MIT grant. Fifty-four were compared byte-for-byte to the newly installed wheels; Streamlit's standalone Apache-2.0 license was previously retrieved from its exact official version tag (URL in THIRD_PARTY_NOTICES.md). Dependencies are installed, not vendored. Redistribution of binary dependency bundles would require a separate packaging review. Zillow/FRED/Freddie Mac data and unapproved derivatives are absent, so no data redistribution permission is asserted.

## Reproduce from the candidate root

```sh
python3.14 -m venv /tmp/propertyiq-public-check
/tmp/propertyiq-public-check/bin/python -m pip install -r requirements-lock.txt
/tmp/propertyiq-public-check/bin/python -m pip check
/tmp/propertyiq-public-check/bin/python -B -m unittest discover -s tests -v
/tmp/propertyiq-public-check/bin/python -B scripts/verify_release.py
/tmp/propertyiq-public-check/bin/python -B -m streamlit run app/streamlit_app.py --server.port 8503
git status --short --ignored
git for-each-ref
git rev-list --all --count
git count-objects -v
git remote
```

Use an unused loopback port. Stop the preview with Ctrl-C. Initial installation requires PyPI; subsequent analytical workflows need no account or data download. The empty-history assertions are specific to this pre-commit gate and will intentionally fail after an authorized commit. Manifest hashes must be regenerated and reviewed after any later license or content change. README local links, both screenshots and referenced notice files were checked for existence. Missing required deliverables are now present.

## Activation and final freeze

Before modification, all 97 files matched the approved Step 3A freeze whose manifest SHA-256 was a3204b28e9838010e3a9fc279108756cbd7024564fe166ddab99b2f0ee9e77a6. Step 3B changes are limited to the LICENSE replacement and approved licensing/attribution/documentation/manifests. The 12 copied modules, extracted tests, all other runtime source/tests, screenshots and 55 upstream legal texts remain byte-identical to that freeze. No extra source contribution was licensed.

INCLUDED_FILES.json was regenerated for the effective LICENSE. External Step 3B verification, approval record, full 97-file SHA-256 manifest (including INCLUDED_FILES.json itself), and future Git command plan are explicitly excluded from the package in EXCLUDED_FILES.json. The external manifest is a reproducible digest checkpoint, not a signing or tamper-proof storage claim. Any later change invalidates the frozen hashes and requires another reviewed freeze.

## Remaining exact approval

No specific unresolved rights conflict has been identified within the approved scope. A future first commit and private push require separate explicit authorization. The intended repository's existence, private visibility, access and empty branch state have not been verified through an account in this phase. The future command plan requires those checks before writing or pushing; it is not executed. Public visibility and deployment remain unauthorized.
