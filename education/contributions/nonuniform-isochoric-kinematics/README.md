# Nonuniform local-volume property lab

Separate, unintegrated review candidate for prescribed finite kinematics. No force balance, passive material law, activation or anatomical prediction is asserted. Six standalone Real contracts require a fresh source-bound kernel check before rendering. The existing book and its 103 proof identities are unchanged; book registration requires independent acceptance.

The reference body is a regular polygonal prism. Material coordinate S has positive linear axial stretch λ(S); the axial coordinate is its exact integral. Transverse coordinates use b(S)=1/√λ(S) when local compensation is enabled. The complete gradient includes b′Y and b′Z, so det F=λb²=1 under compensation. Engineering strain λ−1 is explicitly the centerline strain; surface axial material lines also have shear components. Mean stretch one with compensation off is a counterexample: expansion/contraction cancel in the global volume, while local J ranges from 0.6 to 1.4 at the default gradient.

The displayed section uses the same vertices as the full closed three-dimensional triangle mesh. Boundary-triangle volume is checked independently against polygonal-frustum volumes and exact reference polygon area times length. A straight-cell mesh approximates the exact curved map: its nonzero volume error is reported and converges under refinement. The exact continuum result must not be represented as an exact finite-mesh measurement.

Validation commands, from this directory:

```bash
node --test model.test.mjs
python3 -m pip install -r requirements-audit.txt
python3 model_audit.py --output /absolute/ignored/review/audit
python3 check_proofs.py --mathlib /absolute/pinned/mathlib4 --lean-bin /absolute/lean-4.19.0-linux/bin --output /absolute/ignored/review/proofs
python3 build.py --output /absolute/ignored/review/site --proof-receipt /absolute/ignored/review/proofs/nonuniform-proof-status.json --model-audit /absolute/ignored/review/audit/model-audit.json
python3 browser.py /absolute/ignored/review/site
```

The generated HTML is self-contained and makes no external asset requests. Its five relative proof/audit downloads are bundled alongside it. Native browser tests cover desktop/mobile/narrow controls, rollback/reset, local-versus-global volume, real mesh refinement, gradient reversal, and two actual corrupted models. Review PDF text and diagram labels must meet an actual 10-point minimum; all six complete statements and the complete checked Lean source must be present. PDF download links point to embedded appendices. Generated HTML/PDF/screenshots/receipts remain downloadable artifacts, not committed source.

`model_audit.py` separately differentiates the map symbolically, checks injectivity/volume assumptions, factors the straight-cell error, and independently checks 90 extreme/default/refinement states with high-precision oriented boundary volumes, regular-polygon/frustum measurements and closed-surface topology. These routes do not substitute for an independent peer acceptance.

The Lean contracts prove the declared matrix determinant, interval positivity and an algebraic cell-error formula. They do not formally derive the gradient from the map, prove the change-of-variables integral, certify the triangulation or refine floating-point computation. The positive-ratio error factorization explains the reported excess volume; finite triangles must not be represented as exactly isochoric under nonuniform compensation.

Remaining review: fresh genuine compilation and exact-source qualification, then independent model/text/appearance acceptance before book registration. This prototype is neither the pending passive continuous specimen nor the unfinished anatomical capstone. Original code is licensed under the repository's Apache-2.0 license.
