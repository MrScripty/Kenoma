# Nonuniform local-volume property lab

Separate, unintegrated review candidate for prescribed finite kinematics. No force balance, passive material law, activation, anatomical prediction, or new compiled Lean claim is asserted. The existing book and its 103 proof identities are unchanged.

The reference body is a regular polygonal prism. Material coordinate S has positive linear axial stretch λ(S); the axial coordinate is its exact integral. Transverse coordinates use b(S)=1/√λ(S) when local compensation is enabled. The complete gradient includes b′Y and b′Z, so det F=λb²=1 under compensation. Engineering strain λ−1 is explicitly the centerline strain; surface axial material lines also have shear components. Mean stretch one with compensation off is a counterexample: expansion/contraction cancel in the global volume, while local J ranges from 0.6 to 1.4 at the default gradient.

The displayed section uses the same vertices as the full closed three-dimensional triangle mesh. Boundary-triangle volume is checked independently against polygonal-frustum volumes and exact reference polygon area times length. A straight-cell mesh approximates the exact curved map: its nonzero volume error is reported and converges under refinement. The exact continuum result must not be represented as an exact finite-mesh measurement.

Validation commands, from this directory:

```bash
node --test model.test.mjs
python3 build.py --output ../../../.artifacts/nonuniform-volume-lab
python3 browser.py ../../../.artifacts/nonuniform-volume-lab
```

The generated HTML is self-contained and makes no external asset requests. Native browser tests cover desktop/mobile/narrow controls, rollback/reset, local-versus-global volume, real mesh refinement, gradient reversal, and two actual corrupted models. Review PDF text and diagram labels must meet an actual 10-point minimum. Generated HTML/PDF/screenshots/receipts remain downloadable artifacts, not committed source.

Remaining review: independent mathematical/model and appearance review, and a separately scoped Real Lean proof before any formal book registration. This prototype is neither the pending passive continuous specimen nor the unfinished anatomical capstone. Original code is licensed under the repository's Apache-2.0 license.
