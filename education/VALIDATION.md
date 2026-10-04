# Foundation milestone 1 validation

Validated locally on 2026-10-04. This records the first educational slice, not completion of the anatomical book or capstone.

- All eight mechanics tests pass: analytic force/work, signed lever torque, potential gradient, integer torque identities, deterministic replay, explicit-Euler energy growth, bounded oscillator comparisons, Verlet convergence, and input domains.
- Six exact-integer theorems compile with official Lean 4.19.0, bundled `Std`, and warnings treated as errors. Fresh kernel dependency reports contain only the documented foundational axioms. No `sorry`, custom axiom, or `native_decide` is used.
- The single-source build generates one coherent Markdown manuscript, portable HTML with locally bundled Three.js, original schematic SVG diagrams, and source-bound proof cards. The oscillator table is generated from an executed synthetic experiment, with independent analytic tests.
- Chromium 151.0.7922.173 browser checks pass at desktop and 390 px mobile sizes, including keyboard operation, reset and pause, integrator changes, real WebGL scenes, one active canvas, non-WebGL fallback, and reading without JavaScript. This is not a cross-browser certification or complete accessibility audit.
- The illustrated PDF has 16 pages. All pages were rendered to PNG and visually reviewed; content extraction and page-boundary checks pass. This does not imply PDF/UA certification.
- Existing `docs/plans/` files and the Apache-2.0 licence are unchanged. All figures in this slice are original teaching geometry; no third-party anatomy assets or actual medical measurements are included.

Build commands, prerequisites, and hosted publication controls are in [README.md](README.md). Exact proof, browser, PDF, experiment, and build receipts are generated under `dist/`, which is deliberately untracked. The review bundle contains those receipts.

At the initial handoff, remote workflow execution had not been verified because the executor API lookup was forbidden. Subsequent independent review confirmed the exact foundation head `ffde6989f72f8a60bf63977aa3375495a0ae6def` passed [its build-only workflow](https://github.com/MrScripty/Kenoma/actions/runs/37194337186). The supported GitHub connector subsequently confirmed the same run. GitHub Pages has not been deployed, and repository Pages settings are unchanged. The three incoming research packages and their corrections are recorded in [research/integration-notes.md](research/integration-notes.md).

## Articulated elbow milestone 2

This descendant integrates three original teaching chapters covering anatomical evidence, the force-driven elbow and activation, and tissue/contact/graphics mechanisms. Published architecture summaries were checked in Murray et al.'s original Table 2; the indentation study's two fitted moduli were checked against its original abstract. These biological study summaries are separate from the simulation's authored parameters. Raw medical trials and anatomical assets are not integrated.

The new schematic laboratory implements a single hinge, point-load dumbbell and forearm gravity, one synthetic flexor line, exact constant-input activation transients, a rigid tendon, authored active/passive force laws, and forward dynamics with RK4 work accounting. Excitation release retains activation and velocity. A prescribed static hold reports its external support moment explicitly. The belly is a one-way drawing; it contributes no second actuator force. Force–velocity effects, pennation, tendon compliance, tissue/contact and skinning are absent.

Local checks pass: 13 mechanics tests (eight retained plus five new), eight checked Lean theorems, browser interaction/replay and JSON trace-download checks, and the 26-page PDF's content/bounds checks. All pages were rendered and visually reviewed. The pulse/release timestep experiment reports decreasing maximum work-balance residuals: approximately 1.70e-5, 8.53e-6 and 7.77e-7 J at h = 0.01, 0.005 and 0.0025 s. These are synthetic numerical results, not measured physiological agreement.

Both foundation review findings are repaired here: PDF proof links resolve to internal source/receipt/dependency appendices, and Reset clears stale `aria-invalid`. The targeted PDF check verifies all 24 proof links have resolved internal destinations and rejects loopback/file URLs. Browser regressions check blank-input→Reset and sequential typing of 0.35. Browser receipts now bind the generated HTML and JavaScript hashes and are removed before a new check, so stale receipts cannot satisfy artifact validation.

Milestone 2 remains available on its own branch: exact head `ac49eb17ba317db0937336a08314a9489dc2e187` passed https://github.com/MrScripty/Kenoma/actions/runs/37195582366 . The full capstone still needs actual asset/trial integration, compliant tendon, deformable skin/fascia, explicit elbow compression/contact, and the synchronized naive-skinning comparison. No PR merge or Pages deployment is authorized by these checks.


## Tendon, tissue and actual-data milestone 3

The descendant `education/tendon-tissue` adds Laboratory 5 and a separate evidence viewer. Nineteen numerical tests pass, including independent energy/stress finite differences, tissue energy/hinge-moment consistency, fixed-end tendon storage and release, force equilibrium, the rigid-tendon limit, contact and volume ablations, LBS vertex-transform determinant, deterministic replay and coupled timestep refinement. The 0.6 s synthetic pulse/release fixtures have maximum work residuals ~7.99e-5, 1.14e-5 and 8.46e-7 J for macrosteps 0.01, 0.005 and 0.0025 s; all use 16 local event splits. This is numerical evidence for the authored proxy, not an accuracy ranking or biological validation.

All eight existing Lean 4.19.0 declarations compile afresh. Their exact integer domains are unchanged; no declaration claims to prove the series equilibrium, continuum/contact equations, JavaScript arithmetic or biological validity.

The 2,058,262-byte actual-data ZIP matches SHA-256 `af02aaeb37d626f448a658183f764dc6cf68b979730c413ba31997f26062d169`. The package's 992 structural/data/provenance checks pass during every build. Ten original atlas meshes (20,218 triangles), 4,403 normalized recorded samples/172 display bins and six Arm26 actuator parameter sets are integrated with full source licences, preserved historical OBJ comments, immutable source bytes and per-file provenance. Atlas, recording and model are independent evidence streams.

Chromium desktop and 390 px mobile browser checks pass for the five laboratories, fixed-end activation/release, compliant/rigid and contact/bulk switches, trace downloads, same-pose graphics comparison, actual atlas part/camera selection, keyboard recording-bin navigation and reset. One active canvas is retained. Responsive source figures fixed a detected mobile overflow. The 33-page illustrated PDF was rendered and every page visually reviewed; content, glyph bounds and all 24 internal proof destinations pass. Data-source links in PDF are immutable repository URLs, and loopback/file links are rejected. Receipts are bound to exact HTML, JavaScript and source hashes.

The build remains additive: original production plans and repository licence are unchanged. The affine block is a quasistatic reduced continuum ansatz, not spatial FEM, a skin/fascia model or a validated anatomical contact solve. The full capstone still requires anatomical registration, attachment/material fields, spatial tissue and mesh contact, validation and reviewed publication. Hosted CI must be matched to the pushed milestone head; no PR merge, Pages settings change or Pages deployment is performed by these checks.
