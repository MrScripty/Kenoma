# Kenoma educational book

This additive track provides one illustrated research book, seven resettable 3D teaching laboratories, three progressive property lessons and Lab 5’s bulk/confinement extension, actual atlas-data inspection, a coupled engineering fixture and an anatomical apparatus candidate. It preserves the production simulator plans. The research edition has 21 chapters and 33 compiled Lean4 claims across five source files. Primary sources and independently licensed anatomy/trial/Arm26 data are cited separately from authored teaching geometry and material assumptions.

The published spatial teaching lab uses a one-way quasistatic line actuator and schematic skin/fascia. The newer anatomical candidate connects seven atlas-derived P2 volumes through shared tendon apparatuses and a jointly solved elbow. Its held rest and all 15 recorded loaded/released steps pass independently replayed reduced force and finite geometry checks after material contact-witness refinement. The original failures remain source-bound regressions. Lift/release receipts, compression and remaining model limits are reported in the anatomical apparatus chapter; no medical or subject-specific validation is claimed.

## Build and read

Prerequisites: Node 22 or later, Python 3.12, Pandoc (tested 3.1.11.1), and pinned Lean 4.19.0. The local milestone used Node 24.19.0; CI selects Node 22; the reviewed foundation passed remotely, and the articulated-elbow descendant passed its own exact-head workflow; each new apparatus revision requires its own workflow check. A Linux x86_64 installer downloads the official Lean archive and checks its recorded SHA-256. For another platform, use the official Lean release matching `proofs/lean-toolchain`.

```bash
cd education
npm ci
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 tools/install_lean.py --directory .tools
export LEAN="$PWD/.tools/lean-4.19.0-linux/bin/lean"
python3 tools/build_property_mathlib.py
npm test
npm run build
npm run pdf
npm run test:browser
npm run test:mobile
python3 tests/anatomical_arm_inspection.py
python3 tests/property_browser.py dist
python3 tests/artifacts.py
python3 -m http.server 8000 --directory dist
```

The contact regression and trajectory commands retain the original failed inputs and re-evaluate their gates:

```bash
node tools/verify-anatomical-rejected-steps.mjs
node tools/verify-anatomical-cold-candidate.mjs
npm run anatomy:contact
```

The last command solves the recorded 0.5 kg lifting/release schedule and then independently replays force, finite geometry and the mechanical ledger. CPU solves can take minutes per step. Archived coordinates supply nonlinear initial guesses; the old accepted state defines inertia and activation, and collision or force failures retain that state. Contact gaps and force tolerances remain at their original values.

Open `http://localhost:8000`. Generated outputs are `dist/kenoma-mechanics.md`, `dist/kenoma-mechanics.pdf`, and `dist/index.html`, with locally bundled assets, complete proof sources, citations, receipts, experiment measurements, and third-party notices. Serve the directory rather than opening HTML via `file://`, since module scripts need HTTP. Every URL is relative for a project-base path such as `/Kenoma/`.

A system Chromium can be used when installed; `CHROMIUM_EXECUTABLE=/absolute/path/to/chromium` overrides selection. The local verified render used system Chromium because the Playwright CDN was unavailable. Browser versions are recorded in the generated receipts. PDF byte identity and cross-browser transcendental bit identity are not claimed.

## Authoring and evidence

- Edit canonical chapter Markdown in `book/chapters/`; order comes from `book/book.json`.
- `{{demo:force}}`, `{{demo:torque}}`, `{{demo:energy}}`, `{{demo:elbow}}`, `{{demo:series}}` expand into HTML laboratories or static Markdown descriptions. `{{demo:continuum}}` and `{{demo:spatial}}` add the advanced lessons. Original SVGs are generated from actual solved fixture coordinates as well as elementary diagrams.
- `{{proof:ID}}` connects a claim to the declaration in `proofs/claims.json`. `tools/check_proofs.py` invokes Lean afresh, rejects unknown/custom axiom dependencies and admissions, and writes a source-bound receipt only on success. No manual checked flag is accepted.
- `{{property:deformation}}`, `{{property:isochoric}}` and `{{property:tapered}}` add independent boundary-volume and axial-bar lessons with static print figures. `tools/check_property_proofs.py` freshly checks eight real kinematic/material declarations, including Lab 5’s split energy, and pins each transitive Git dependency before emitting a receipt.
- `{{experiment}}` executes the browser's pure mechanics module to generate the table and JSON result. Tests independently compare reference values and convergence, without claiming implementation refinement proofs.
- The PDF prints the same HTML manuscript with native MathML and static diagrams. Controls and canvases are omitted; all prose, worked examples and exact claims remain.

The 3D renderer initializes only when requested and keeps one active canvas. Numerical controls work without WebGL. A zero-JavaScript reader retains all chapter text, figures, mathematical claims and the numerical experiment table. Labs start paused; Reset restores all parameters and camera. Only deliberate requested summaries are announced, rather than every frame.

The original 25 declarations use exact integer domains and bundled Std. Eight additional declarations in `ContinuumProperties.lean` use real matrices, the real square root, real powers and Lab 5’s declared split energy with pinned mathlib v4.19.0; `proofs/mathlib-lock.json` binds its commit and dependency manifest. The source build uses two jobs and does not require a binary cache. These are mathematical contracts, not real-valued biological model validation. The twelve checks cover cancellation, torque identities, kinetic-energy numerator nonnegativity, an exact worked torque, an integer convex-mixture numerator bound and signed virtual-power algebra, plus element-gradient resultants, centroid force-transfer power, a compliant-denominator bound and Armijo acceptance. Every card declares its domain and limits. These exact contracts do not prove the numerical implementation or biological response.

## GitHub Pages foundation

`.github/workflows/education.yml` validates branch/PR changes and uploads a reviewable artifact. The actions are pinned to verified upstream commit SHAs. Publication is a separate job available only through explicit `workflow_dispatch` with `publish=true` on `main`, after all build checks pass. The repository must have Pages configured to use GitHub Actions before that hosted job can succeed. No settings are changed by the local build and no Pages publication has been performed. Foundation head `ffde6989f72f8a60bf63977aa3375495a0ae6def` passed its remote build-only workflow, independently confirmed by review at https://github.com/MrScripty/Kenoma/actions/runs/37194337186 . The current edition needs its own exact-head remote check before publication.

Do not describe a local build as a hosted site or a passing future workflow. Confirm the Actions run and deployment URL after review. Adding this workflow does not amend the Bevy MVP, require a full simulator, or authorize a merge.

## Spatial lesson boundaries

`web/spatial.mjs` implements central-edge energies, actual tetrahedral volume gradients, independent skin edges, compliant fascia vector tethers and bone-capsule vertex/centroid penalties. It uses deterministic limited-memory BFGS with Armijo/positive-J guards, reports finite-solve defects and limits q to 0–100°. It is not FEM, pressure measurement, self-contact or CCD. Its reactions do not drive the hinge, and instantaneous shape energy is not hinge active work.

`contributions/continuum_reference/` retains the separately reviewed original module, chapter and source-bound fixtures. `npm test` explicitly discovers its 11 tests. Reference solves must converge before being displayed; static analytic error stays separate from matched implicit iterative error. Element assembly is cached across sweeps/camera changes. The original measured timing environment is retained; no universal browser speed claim is made.

Lab 5’s compression extension retains `web/tissue.mjs`, distinguishes imposed height from imposed force, and compares free/confined sides. `node --test tests/compression.test.mjs` and `python3 tests/compression_browser.py` check its independent oracles, force limits and actual controls. It uses a quadratic volume penalty; the anatomical arm’s logarithmic penalty is unchanged.
