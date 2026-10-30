# Third-party dependencies and notices

The public source imports Streamlit, NumPy and pandas. Dependencies are installed separately; this repository does not ship their executable package code or a virtual environment. Scoped project MIT licensing does not relicense those packages or their data, bundled components or trademarks.

`docs/DEPENDENCY_INVENTORY.json` records every installed runtime distribution in the tested clean environment, its exact version, declared SPDX expression/classifiers, upstream project URLs and copied notice files. `requirements-lock.txt` records the tested dependency resolution. The inventory is a packaging record, not a legal opinion or vulnerability audit.

License/copyright/NOTICE files supplied by the installed distributions are retained verbatim under `docs/licenses/<distribution>/`. Streamlit's installed wheel did not supply a standalone license file; its Apache-2.0 text was retrieved from the exact upstream version:
https://raw.githubusercontent.com/streamlit/streamlit/1.66.1/LICENSE
Checked and retrieved 2026-10-29. Other notice files came from the installed wheels and retain embedded upstream acknowledgments, author names and public contact details. These public notices are not the project author's private information and must not be silently edited away.

Direct dependency summaries:

- Streamlit 1.66.1: Apache-2.0.
- NumPy 2.4.6: its metadata declares BSD-3-Clause plus additional permissive components; wheel-specific bundled-library terms are preserved in its supplied notices.
- pandas 3.0.3: BSD-3-Clause and included component notices.

Important transitive examples include Apache-2.0 projects, BSD/MIT variants, Pillow's license, certifi's MPL-2.0 CA bundle, Unicode-related data notices and Python-dateutil's supplied licenses. Consult each recorded distribution and file rather than declaring the entire environment “MIT”. No GPL incompatibility or blanket compatibility conclusion is inferred from package names. Before distributing binaries or wheels, review that distribution's additional obligations; this source-only snapshot does not authorize such redistribution.

The copied legal texts are deliberately excluded from the approved project MIT scope. No third-party dataset, logo or SDK has been vendored. If dependencies are updated, regenerate the lock/inventory, preserve the new notices, rerun public tests, and review any changed obligations.
