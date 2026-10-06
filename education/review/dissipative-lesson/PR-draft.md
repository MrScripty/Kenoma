# Add a bounded axial load–hold–release lesson with independently checked loss

The elastic bar cannot teach delayed creep, stress relaxation or viscous loss.
This separate small-strain standard-linear-solid lesson keeps the earlier bar's
geometry and equilibrium modulus, then adds a Maxwell internal state. Continuous
load, force-or-extension hold, unload and zero-force recovery drive the same
spatial field, fixed-scale image, history and energy readouts. Disabling the
branch recovers the actual earlier elastic runtime. Coefficients remain authored
teaching examples.

Parameter edits explicitly start a new experiment; invalid edits preserve the
prior state. Boundary work and viscous loss are independently integrated. The
controller exports the initial observation and every accepted step, uses bounded
animation batches, and supports paced Play, Step, pause/resume and default reset.

Eleven fresh real-number declarations cover local constitutive signs, derivatives,
power balance under the Maxwell ODE, the elastic limit and held-strain exponential
contracts. Each card states its assumptions and limits. Independent per-cell RK4
plus separate Simpson integration and actual-browser histories cover the bar,
quadrature, finite protocol and implementation separately. The proof renderer now
preserves literal powers and extracts only the named theorem for both tactic and
term proofs; the failures and regression evidence are retained.

Validation passed (exact results and bindings in `qualification.json`): 198 Node tests (unchanged Node inputs after the last renderer fix),
34 Python tests, all 64 fresh strict Lean declarations, actual SLS controls and
seven traces/captures, both damaged delivered modules, six damaged artifact
copies, six existing book/worker browser lanes, property/material controls,
desktop/mobile proof captures, complete PDF continuation and portable-package
checks. Exact completion status and hashes are in `qualification.json`.

Source checkpoint: `569e6686aaa08c7a2005ed25441c59db7afee4f8`.
Based on accepted `f0973f46e55faa881ab3b34c6a848dfee313142e`.
This is separate from the frozen current-main 53-declaration candidate
`e8fa239e3c01468cee86615e1f306dd6659999fa`; coordinate the PR sequence with
that candidate before opening this draft.

Existing finite-strain material equations/calibration, anatomical sources,
acceptance limits, force–velocity boundary and unfinished-capstone labels stay
unchanged. Local Chromium and mobile emulation are the browser scope; no hosted
publication, physical-phone certification or biological validation is claimed.
