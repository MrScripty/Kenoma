# Material-response compression review

This successor adds a bounded homogeneous elastic compression lesson immediately after the three early measurement/axial property lessons. The existing tissue law and dimensions are reused unchanged; none of the older solvers, material calibrations, acceptance limits or unfinished anatomical-capstone labels are changed.

The source checkpoint and complete SHA-256 input/output maps are recorded in the delivered `material-preview-manifest.json`. The standalone review compiles only the five new Std contracts freshly, renders the canonical new chapter with the production page template and app bundle, and executes its actual controls. Neighboring-chapter links explicitly point to the published book; this preview does not borrow historical proof cards or claim a fresh complete book release.

## Mechanics and counterexamples

- Shared plate height h; deformation diag(b,h,b); reference 80 × 60 × 50 mm. Free surfaces solve zero lateral traction. Smooth unilateral walls enforce b ≤ 1 with compressive reaction, or permit pull-away.
- Finite caps use separate wall-feasible brackets. Positive geometry acceptance and the displayed 1e-5 Pa lateral residual criterion are separate. This new numerical criterion does not alter existing lab gates.
- Default free result: b = 1.1146268835553577, J = 0.9939144716354632, plate force 4.536371031795807 N. Active walls: b = 1, J = 0.8, plate force 42.08871497512574 N, wall pressure 9738.910628109279 Pa. Both plate heights are 0.048 m.
- K = 0 gives isotropic contraction b = h, J = h³ and zero energy/force up to roundoff. K = 500 Pa permits wall pull-away. Neither is presented as a calibrated muscle response. A positive-J isochoric candidate at h < 1 penetrates the walls and is explicitly rejected.

The source derivation gives nominal stress, energy derivatives, plate force/current-area pressure, per-wall forces/gaps and complementarity work with SI units. The original-author reference is Bower's Applied Mechanics of Solids §3.5, opened for energy-derived hyperelastic stress and stress measures. The authored energy and boundary reduction are distinguished from that source and from any experimental material curve.

## Qualification

- Full Node suite: 148 tests passed. Seven new tests check energy derivatives, an independently derived J-based stationarity equation across 126 control combinations, feasible energy grids, SI conversions, wall onset, finite caps, zero/weak bulk, inversion/nonfinite/out-of-domain candidates and reversible restoration.
- Full Python suite: 24 tests passed. Python compilation and whitespace checks passed.
- Fresh Lean 4.19.0 compilation: all five MaterialResponse declarations succeeded with warnings treated as errors. Complete source, receipt, command, SHA-256 identities and transitive-axiom reports accompany the preview. The proof source is unchanged from checkpoint 04afa68.
- Actual Chromium checks: production bundle/template, numeric/select/slider controls, exported states, SVG dimensions on a fixed physical scale, named parameter comparisons at shared height, zero bulk, weak-bulk pull-away, finite residual failure/refinement, invalid-state retention, infeasible-candidate rejection, reset, mobile stacking/overflow, static print/PDF and no-JavaScript fallback. Desktop/mobile figures, controls/readouts and PDF derivation/comparison/source pages were visually inspected.
- `check_material_artifact.py` binds delivered proof, numerical, browser and image outputs to their actual source hashes and compares browser exports with independently generated experiment fixtures. The endpoint audit was genuinely rerun for the changed property-block dispatcher on this successor; its original historical receipt stays unchanged. PR7 remains frozen at 1ddebd8, and the editorial branch at 8e6dbf1.

The complete local book build was attempted. Its original 25 Std declarations compiled, then it stopped at the absent `.tools/mathlib4` workspace while checking the four existing real kinematic claims. The successful new material compilation is independent of that missing dependency. The full book/PDF/artifact release gate is therefore pending fresh CI. No archived full-book result is substituted, and no merge, deployment or publication is authorized by these preview results.

## Reproduction

From `education`, with the verified official Lean 4.19.0 binary configured in LEAN:

```sh
node --test tests/material_response.test.mjs
python tools/build_material_preview.py /tmp/kenoma-material-review-new
python tests/material_browser.py /tmp/kenoma-material-review-new
python tools/check_material_artifact.py /tmp/kenoma-material-review-new
```

Use a fresh output directory. Production integration is in `tools/build.py`, the `property:material` directive, `web/app.mjs`, the new proof family and PDF destinations. CI runs the integrated browser check before the full artifact gate.

## Exact limits

The five Lean claims are scaled integer contracts: confined volume ordering, bulk-penalty nonnegativity and zero condition, reaction-free separated walls given complementarity, and lateral work factorization. They do not formalize real fractional powers or prove solver convergence, root uniqueness, global optimality, spatial equilibrium, floating-point refinement or physical/biological validity. Numerical grid and residual checks are bounded implementation evidence. There is no anatomy, calibrated muscle, plasticity, damage, friction, dynamics, fluid flow or dissipative load/hold/release in this lesson. Those planned teaching items retain their separate status.
