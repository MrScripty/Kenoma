# Teaching control repair evidence

Base: published main `2e05953581cdbd4f58c9070cd27e9ebce0d8c276`. This repair is independent of the anatomical research branch. No checkout `AGENTS.md` or `.agents/skills` were present; the repository and education READMEs supplied the build instructions.

## Reproductions

`lab7-before.txt` records the real controller regression on unchanged Lab7 source: skin ablation replaces activation 0.6 with zero. After a dynamic lift it also erases pose, velocity, time, accumulated work/dissipation and step counters.

`force-before/force-observed.json` records actual Chromium canvas marker pixels: 8, 18 and 32 m all appear at pixel offset 116. `property-before/property-observed.json` records doubled numerical strain with unchanged SVG bar heights. Their receipts contain the exact worktree source hashes; these two captures were made after the first Lab7 fix, while their respective audited sources were still unchanged.

## Behavior and invariants

Lab7 non-excitation edits pause playback and cancel the automatic pulse, retain activation and hinge state, and discard the old trace segment while preserving physical time, work, dissipation and step counters. Angle edits explicitly relocate the pose, zero velocity and clear the domain halt; entering prescribed hold zeros velocity and synchronizes the pose control. Ordinary parameter edits retain an existing halt. Reset, pulse and compression remain deliberate initializations. Excitation changes retain the established same-time current-row policy.

The tissue solver still starts from its deterministic initialization at each current pose/activation. No mesh, optimizer history or dual state is transferred. Node regressions check finite coordinates, positive guarded volumes, fixed endpoints, same-pose baseline, descending accepted energy and unchanged line-actuator results under active-shape ablation. This preserves the original solver guards and residual criteria.

Lab1 uses one position scale for the entire 0–2 s trajectory at each selected mass/force. Its readout reports physical grid spacing; force and velocity arrows have separate scales. Property lab 3 disables both numeric and slider controls that do not apply to the mode. Its plot uses fixed ±0.05 strain within the existing illustrative range and explicitly expands beyond that range to avoid hiding overflow. The 5% warning and bar equations are unchanged. Dead-centre readouts explain zero actuator leverage at q = 0° in Labs 4, 5 and 7 without moving the joint or inventing torque.

## Recorded checks

| Check | Evidence |
| --- | --- |
| Full Node suite, 141 passed | `node-tests.txt` |
| Python suite, 17 passed | `python-tests.txt` |
| Focused controller/solver regressions | `focused-node-tests.txt` |
| Real Chromium controls and screenshots | `browser-tests.txt`, `after/receipt.json` |
| Existing three-property-lab browser suite | `property-browser-tests.txt` |

`tests/teaching_controls_browser.py` builds a focused page with the production HTML generators and the production app bundle using the same esbuild options as the book. It measures the Lab1 marker directly from canvas pixels, compares actual SVG heights and numeric strain, exercises Lab7 controls/exports/reset and checks dead-centre text after one simulated second. The same checks are called by `tests/browser.py` for future integrated-book runs.

The repaired marker offsets are 28.5, 65.5 and 116 pixels at 8, 18 and 32 m. Passive force 0.3 → 0.6 N doubles strain and bar heights. At q = 90°, a = 0.6, active shape on/off changes centre fibre arc 0.165003 → 0.181196 m while line fibre remains 0.144035 m. The paired screenshots were inspected. Both shape solves remain labeled finite approximations; ablation residuals differ and are not hidden.

Lowering volume stiffness reaches min J ≈ 0.0100000014 with free residual ≈ 8.66 N. This is an existing guarded finite approximation, not an equilibrium qualification. Its behavior is preserved and exposed, not recalibrated.

The local browser scope is generated control sections, not a rebuilt full book/PDF or fresh Lean proof compilation. The existing property preview/suite was also run without advertising compiled claims. Hosted exact-head book/proof qualification remains required before release. Nothing was merged or deployed; the repairs do not complete anatomical or biological validation.

## Separate bounded follow-up proposal

Review the chapter dependency order and introductions in a separate change: simple deformation/volume measurements → prescribed isochoric kinematics → nonuniform axial strain → material laws and contact mechanics. Preserve proof/source links and worked examples, then rebuild and check navigation, print layout and lab context as one coherent review.

The revised introductions should explicitly distinguish imposed volume-preserving geometry from material-driven transverse redistribution, and the axial bar compatibility calculation from transverse equilibrium. Bulk/shear/confinement, fibre aggregation, force–length/velocity and dissipation lessons remain pending until implemented and qualified. This proposal is not an assertion that these lessons, a complete muscle model or biological validation already exist.
