Lab7's 90° compression fixture starts with activation 0.6, but any non-excitation control previously reinitialized activation to zero. The repair preserves the current hinge state across parameter edits and reruns the existing deterministic tissue solver. Explicit angle changes and prescribed holds enforce zero velocity; reset/pulse/compression retain their deliberate initialization behavior. Parameter edits begin a new trace segment at the existing physical time and step, with cumulative work explicitly labeled.

Also repairs two independently reproduced teaching-UI findings: Lab1's position marker no longer stops visually once displacement exceeds 4 m; its scale is fixed over the allowed trajectory and grid spacing is reported. Property lab 3 disables inputs irrelevant to its boundary condition and shows strain on a common ±0.05 scale, with explicit expansion above that range. Dead-centre readouts explain why the straight actuator at q = 0° produces no joint torque despite developed tension.

Source: `education/web/advanced.mjs`, `education/web/app.mjs`, `education/web/property-labs.mjs`; generated control labels/descriptions in `education/tools/build.py`; trace/state policy in `education/book/chapters/12-spatial-capstone.md`. No solver equations, calibration, acceptance limits, anatomical research files or pending-capstone labels change.

Validation:

- Full Node suite: 141 passed; Python suite: 17 passed. Final focused suite: 30 passed.
- `education/tests/spatial_controls.test.mjs` reproduces the original controller bug and checks state/counters/accounting, halt retention, pose/hold kinematics, fixed endpoints, positive guarded volumes, energy descent, physical ablations and deterministic active-shape restoration.
- `education/tests/teaching_controls_browser.py` exercises production-generated HTML and the production app bundle in real Chromium, measures actual Lab1 marker pixels, compares numerical strains and SVG heights, checks inactive controls, Lab7 state/exports/reset and active-shape rendering, and verifies dead-centre behavior. These checks are included in the integrated `education/tests/browser.py` suite.
- Existing property browser suite passed on the standalone preview, including desktop/mobile and print/no-JavaScript alternatives.
- Before/after receipts, logs, numeric snapshots and inspected screenshots: `education/review/teaching-controls/README.md` and adjacent files. The final browser receipt records exact worktree source and bundle hashes.

Measured Lab1 offsets at 8/18/32 m change from 116/116/116 pixels to 28.5/65.5/116 pixels. At q = 90°, a = 0.6, spatial active-shape on/off changes centre fibre arc 0.165003 → 0.181196 m while line fibre remains 0.144035 m. These are finite-iteration results with visible residual/status labels. The low-volume-stiffness fixture approaches the existing J guard with a large residual; no equilibrium qualification is inferred.

Local browser qualification covers generated control sections, not a full rebuilt book/PDF or fresh Lean compilation. Hosted exact-head qualification remains required before release. The lesson-ordering proposal is recorded separately in the evidence README; it is not implemented in this repair. No biological/anatomical validation, merge or deployment is implied.
