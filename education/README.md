# Kenoma educational book

The [scoped source pipeline](research/source-first-reading-pipeline.md) builds and qualifies the complete functional Pages root plus six educational additions from fixed Git inputs. Use its manual workflow or scoped commands. The full historical commands below also execute scientific experiments and require their own qualification.

This additive track provides one illustrated research book, seven resettable 3D teaching laboratories, eight progressive property lessons, actual atlas-data inspection, a coupled engineering fixture and an anatomical apparatus candidate. It preserves the production simulator plans. The source-only integration candidate has 27 chapters and a registry of 115 Lean4 claims across fourteen source files. Fresh complete-book proof, browser and PDF qualification remain pending. Primary sources and independently licensed anatomy/trial/Arm26 data are cited separately from authored teaching geometry and material assumptions.

The published spatial teaching lab uses a one-way quasistatic line actuator and schematic skin/fascia. The newer anatomical candidate connects seven atlas-derived P2 volumes through shared tendon apparatuses and a jointly solved elbow. Its retained research receipts describe reduced force and finite geometry checks for held rest and 15 recorded steps. These do not establish acceptance or completion of the requested anatomical capstone. The original failures remain source-bound regressions. Lift/release receipts, compression and remaining model limits are reported in the anatomical apparatus chapter; no medical or subject-specific validation is claimed.

## Build and read

The reading order is defined by `book/book.json`, rather than filename numbering. Force, torque and energy lead into prescribed deformation measurements, imposed volume preservation and nonuniform axial strain, including the accepted local-versus-total volume map, then architecture-to-force bookkeeping, followed by material confinement, dissipative response and the separate serial blocks. Anatomy and actuation then lead into contact and spatial solvers. The fixed-field pressure-projection interlude follows the spatial continuum chapter, before interfaces and coupling. The property chapter's retained filename is `09a-properties.md`; its stable heading links continue to resolve. Its isochoric geometry is not a material solve, and its axial bar does not determine transverse muscle deformation.

Prerequisites: Node 22 or later, Python 3.12, Pandoc (tested 3.1.11.1), and pinned Lean 4.19.0. The local milestone used Node 24.19.0; CI selects Node 22; the reviewed foundation passed remotely, and the articulated-elbow descendant passed its own exact-head workflow; each new apparatus revision requires its own workflow check. A Linux x86_64 installer downloads the official Lean archive and checks its recorded SHA-256. For another platform, use the official Lean release matching `proofs/lean-toolchain`.

```bash
cd education
npm ci
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 tools/install_lean.py --directory .tools
export LEAN="$PWD/.tools/lean-4.19.0-linux/bin/lean"
python3 tools/build_property_mathlib.py
python3 tools/check_mixed_volume_proofs.py --build-dependencies
npm test
npm run build
npm run pdf
npm run test:browser
npm run test:mobile
python3 tests/projection_integration.py
python3 tests/anatomical_arm_inspection.py
python3 tests/property_browser.py dist
python3 tests/nonuniform_browser.py
python3 tests/architecture_force_book_browser.py
python3 tests/worker_lifecycle.py
python3 tools/inspect_property_integration.py
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

- Edit canonical chapter Markdown in `book/chapters/`; order comes from `book/book.json`. The integrated spatial-continuum text is `10a-spatial-continuum.md`; the contributed chapter remains an exact provenance-bound archive.
- `{{demo:force}}`, `{{demo:torque}}`, `{{demo:energy}}`, `{{demo:elbow}}`, `{{demo:series}}` expand into HTML laboratories or static Markdown descriptions. `{{demo:continuum}}` and `{{demo:spatial}}` add the advanced lessons. Original SVGs are generated from actual solved fixture coordinates as well as elementary diagrams.
- `{{proof:ID}}` connects a claim to the declaration in `proofs/claims.json`. `tools/check_proofs.py` invokes Lean afresh, rejects unknown/custom axiom dependencies and admissions, and writes a source-bound receipt only on success. No manual checked flag is accepted.
- `{{property:deformation}}`, `{{property:isochoric}}` and `{{property:tapered}}` add independent boundary-volume and axial-bar lessons with static print figures. `tools/check_property_proofs.py` freshly checks their four real kinematic declarations and pins each transitive Git dependency before emitting a receipt.
- `tools/check_real_lesson_proofs.py` uses the same pinned dependency check, then compiles the separate real material, mechanics, actuator, SLS, serial-block, fixed-vector projection, nonuniform-volume and architecture-force sources. All eight additional Real family receipts are withheld if any declaration fails. Real cards state their assumptions and limits; integer contracts, numerical checks and remaining finite-bulk specimen derivative/equilibrium and numerical refinement obligations remain distinct.
- `{{nonuniform-lab}}` adds the independently accepted prescribed nonuniform-volume map after properties and before material response. Its six Real contracts concern the declared gradient, positive interval stretch and algebraic cell error; differentiation/integration, mesh and floating-point obligations remain separately audited. Original 103 proof identities and anatomy references are preserved.
- `{{architecture-force-lab}}` adds the canonical `09ab-architecture-force.md` lesson and the locally bundled `architecture-force/index.html` lab. Static default values survive print and no-JavaScript reading. Six original claim IDs and the exact `ArchitectureForce.lean` source are registered with explicit assumptions; the thirteen contribution files and all anatomy data remain unchanged. The historical 103 + 6 = 109 nonuniform milestone stays distinct from this 115-declaration inventory. Prior standalone qualification does not qualify the book assembly.
- `{{dissipative:sls}}` adds the passive axial load/hold/unload/recovery protocol and energy ledger. `{{serial:assembly}}` adds two separate incompressible neo-Hookean blocks with bilateral sliding fixtures, a shared signed force, actual 3D geometry, local volume measurements and visible root residuals. The serial lesson has twelve scoped Real declarations; it proves neither continuous-taper fields nor unrestricted stability.
- `{{experiment}}` executes the browser's pure mechanics module to generate the table and JSON result. Tests independently compare reference values and convergence, without claiming implementation refinement proofs.
- The PDF prints the same HTML manuscript with native MathML and static diagrams. Controls and canvases are omitted; all prose, worked examples and exact claims remain.

Each 3D laboratory initializes only when requested and keeps one canvas for its surface. Numerical controls work without WebGL. A zero-JavaScript reader retains all chapter text, figures, mathematical claims and the numerical experiment table. Labs start paused; Reset restores all parameters and camera. Only deliberate requested summaries are announced, rather than every frame.

Thirty declarations use exact integer domains and bundled Std. Eighty-five registered declarations use reals with pinned mathlib. Four of those declarations in `ContinuumProperties.lean` use real matrices and the real square root with pinned mathlib v4.19.0; `proofs/mathlib-lock.json` binds its commit and dependency manifest. The source build uses two jobs and does not require a binary cache. These are mathematical contracts, not real-valued biological model validation. The original twelve Mechanics checks cover cancellation, torque identities, kinetic-energy numerator nonnegativity, an exact worked torque, an integer convex-mixture numerator bound and signed virtual-power algebra, plus element-gradient resultants, centroid force-transfer power, a compliant-denominator bound and Armijo acceptance. Every card declares its domain and limits. These exact contracts do not prove the numerical implementation or biological response.

## Source-only architecture-force integration checks

Run the bounded checks without starting the full build:

```bash
cd education
npm run test:architecture-force
python3 -m unittest discover -s tests -p 'test_real_lesson_proofs.py'
```

The first command runs the twelve preserved Node contracts, seven supplementary symbolic checks and source/assembly unit tests. Unit-test proof receipts are synthetic fixtures, not fresh Lean evidence. No browser, PDF, solver, dependency build or numerical campaign runs. The canonical lesson preserves anatomical stationarity, compression and calibration gaps. See [integration scope and remaining gates](research/architecture-force-book-integration.md).

`npm run build` is not a render-only operation: it freshly checks proofs and launches oscillator, elbow, series, spatial and material experiments. The broad workflow adds anatomical research operations. Full-build execution, integrated controls/PDF review and release/publication need a separate decision; no source-only check establishes that they passed.

## GitHub Pages foundation

`.github/workflows/education.yml` validates branch/PR changes and uploads a reviewable artifact. The actions are pinned to verified upstream commit SHAs. Publication is a separate job available only through explicit `workflow_dispatch` with `publish=true` on `main`, after all build checks pass. The repository must have Pages configured to use GitHub Actions before that hosted job can succeed. No settings are changed by the local build and no Pages publication has been performed. Foundation head `ffde6989f72f8a60bf63977aa3375495a0ae6def` passed its remote build-only workflow, independently confirmed by review at https://github.com/MrScripty/Kenoma/actions/runs/37194337186 . The current edition needs its own exact-head remote check before publication.

Do not describe a local build as a hosted site or a passing future workflow. Confirm the Actions run and deployment URL after review. Adding this workflow does not amend the Bevy MVP, require a full simulator, or authorize a merge.

## Spatial lesson boundaries

`web/spatial.mjs` implements central-edge energies, actual tetrahedral volume gradients, independent skin edges, compliant fascia vector tethers and bone-capsule vertex/centroid penalties. It uses deterministic limited-memory BFGS with Armijo/positive-J guards, reports finite-solve defects and limits q to 0–100°. It is not FEM, pressure measurement, self-contact or CCD. Its reactions do not drive the hinge, and instantaneous shape energy is not hinge active work.

`contributions/continuum_reference/` retains the separately reviewed original module, chapter and source-bound fixtures. `npm test` explicitly discovers its 11 tests. Reference solves must converge before being displayed; static analytic error stays separate from matched implicit iterative error. Element assembly is cached across sweeps/camera changes. The original measured timing environment is retained; no universal browser speed claim is made.

The source dependency build bootstraps the pinned ProofWidgets JavaScript assets in its standalone upstream package before restoring mathlib’s unchanged guarded configuration. See `research/ci-e19-proof-build-diagnosis.md` for the cold reproduction of the frozen delivery’s CI failure. Full dependency logs are retained on both failure and success; proof and artifact gates remain required.

The candidate adds a fixed-field projection interlude after spatial continuum and before interfaces/coupling. Its standalone lab, guide, complete Lean source and 27 statements are bundled locally. New continuous-specimen, scalar tension/mass controller and anatomical completion work remain excluded.

Generated downloads and capture collections are untracked. See [output policy and retained inputs](research/generated-output-cleanup.md) for regeneration, draft/full qualification boundaries and the unchanged reference-data package.
