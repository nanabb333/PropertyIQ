# Final source candidate verification

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
