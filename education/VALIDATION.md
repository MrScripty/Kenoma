# Foundation milestone 1 validation

Validated locally on 2026-10-04. This records the first educational slice, not completion of the anatomical book or capstone.

- All eight mechanics tests pass: analytic force/work, signed lever torque, potential gradient, integer torque identities, deterministic replay, explicit-Euler energy growth, bounded oscillator comparisons, Verlet convergence, and input domains.
- Six exact-integer theorems compile with official Lean 4.19.0, bundled `Std`, and warnings treated as errors. Fresh kernel dependency reports contain only the documented foundational axioms. No `sorry`, custom axiom, or `native_decide` is used.
- The single-source build generates one coherent Markdown manuscript, portable HTML with locally bundled Three.js, original schematic SVG diagrams, and source-bound proof cards. The oscillator table is generated from an executed synthetic experiment, with independent analytic tests.
- Chromium 151.0.7922.173 browser checks pass at desktop and 390 px mobile sizes, including keyboard operation, reset and pause, integrator changes, real WebGL scenes, one active canvas, non-WebGL fallback, and reading without JavaScript. This is not a cross-browser certification or complete accessibility audit.
- The illustrated PDF has 16 pages. All pages were rendered to PNG and visually reviewed; content extraction and page-boundary checks pass. This does not imply PDF/UA certification.
- Existing `docs/plans/` files and the Apache-2.0 licence are unchanged. All figures in this slice are original teaching geometry; no third-party anatomy assets or actual medical measurements are included.

Build commands, prerequisites, and hosted publication controls are in [README.md](README.md). Exact proof, browser, PDF, experiment, and build receipts are generated under `dist/`, which is deliberately untracked. The review bundle contains those receipts.

Remote workflow execution and its result have not been verified for this milestone. The branch push may trigger build-only validation; the GitHub Actions API lookup was forbidden in this environment. GitHub Pages has not been deployed, and repository Pages settings are unchanged. A draft PR awaits review. Pending educational work includes integration of the received research, asset-level data licensing and provenance, active muscle/tendon models, compliant skin/fascia and contact, further formal contracts, and the arm/dumbbell versus naive-skinning capstone. The three incoming research packages and their corrections are recorded in [research/integration-notes.md](research/integration-notes.md).
