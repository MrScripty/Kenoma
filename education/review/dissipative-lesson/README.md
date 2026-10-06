# Separate dissipative load–hold–release lesson

Source checkpoint: `569e6686aaa08c7a2005ed25441c59db7afee4f8`, on
`education/dissipative-load-hold-release`, based on accepted 53-declaration
edition `f0973f46e55faa881ab3b34c6a848dfee313142e`. The independently
qualified current-main 53-declaration composition remains frozen at
`e8fa239e3c01468cee86615e1f306dd6659999fa`.

This lesson adds a separate, small-strain, quasistatic axial standard linear
solid: an equilibrium spring in parallel with a Maxwell branch. Its authored
coefficients are examples, not muscle measurements. It preserves the earlier
passive-bar geometry and equilibrium modulus and recovers that actual runtime
when the Maxwell spring is disabled. The existing finite-strain compression
law, force–velocity boundary, anatomical calibration, acceptance limits and
unfinished-capstone labels remain unchanged.

The learner runs continuous finite load/hold/unload/recovery protocols. A force
hold creeps; an extension hold relaxes force without boundary work. The same
spatial field drives the fixed-scale image, extension history and storage.
Work and viscous loss are independently integrated, rather than filling in
loss from a zero balance residual. Every accepted observation is exportable.
Parameter changes deliberately begin a new experiment and clear memory,
physical time and the ledger; invalid controls retain the prior experiment.

Eleven new Real declarations establish local storage/loss signs, the storage
derivative, power balance assuming the Maxwell ODE, the elastic limit, and
held-strain exponential derivative/bounds/weak monotonicity. They do not prove
the force-controlled bar reduction, spatial quadrature, JavaScript arithmetic,
full discrete protocol or biological behavior. All 64 cards retain their
explicit assumptions and implementation boundaries.

Independent per-cell RK4 and separate Simpson integration check both state
variables and independently integrated work/loss across the exported history,
including stiff and tiny-positive-branch cases. Actual browser checks exercise
both hold modes, real SVG displacement and history points, viscosity/refinement,
reset/invalid edits, paced playback, bounded batches, pause/resume and the actual
JSON download. Counterfactual numerical tests and two damaged delivered modules
show that a closed-looking ledger and an accidental force hold are insufficient.
Six damaged artifact copies test proof, source, trace and visual bindings.

`prototype-literal-card-failure.json` preserves the integration failure that
revealed Pandoc interpreting literal ASCII carets in proof-map prose as
superscripts. The corrected renderer preserves exact literals in HTML and PDF.
The earlier `final-*` logs describe source `6fa7aae`; the `c603-*` logs describe
the intermediate caret fix. Actual PDF review then found the term-proof
statement extraction issue, preserved in
`prototype-statement-extraction-failure.json` and `pre-statement-fix-c603/`.
The `569e-*` logs describe the exact final checkpoint above. Earlier receipts
are superseded evidence and are not interchangeable qualifications.

The 198 passing Node tests were run at `c603d508`; every Node runtime and test
input is byte-identical at the final checkpoint. The final 34 Python tests
include two meaningful statement-extraction regressions. An initial c603 book
invocation lacked the pinned Lean executable path; its raw failed log is kept
and the environment restored without source or guard changes.

All release gates passed: 198 Node tests on unchanged Node inputs, 34 Python
tests, all 64 fresh strict Lean declarations, the SLS controls and both damaged
delivered modules, six existing browser lanes, six damaged SLS artifacts,
property/material controls and full render/artifact/package checks.
The PDF has 86 pages. Final results and exact source/output hashes are in
`qualification.json` and `evidence-inventory.json`. Appearance review
is limited to the captures listed there. Browser checks use local Chromium and
mobile emulation, not physical phones or hosted publication. No PR, merge or
deployment is performed by this branch without parent coordination.

Portable archive: `/workspace/kenoma-dissipative-portable.zip`, 76,864,847 bytes,
1,070 files; SHA-256
`7cc84f72cfff169155196eb9068b28998e6a81702d66c4ee7ec2976c86ffa7c0`.
The complete per-file inventory and checked CRC are recorded in
`portable-package.json`. Superseded exploratory standalone captures and logs
are preserved locally at `/workspace/kenoma-sls-prototype-evidence`; the relevant
renderer failure captures and final retry logs are retained in this directory.

Only the two authorized repository-local Git identity fields were used. Every
new source/evidence commit has actual author and committer
`MrScripty <TheEnvironmentGuy@protonmail.com>`. No global Git identity, credentials,
authentication, signing, remotes or historical commit metadata was changed.
