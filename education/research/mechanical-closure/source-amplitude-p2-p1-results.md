# Source-amplitude experiment: one rejection and a verified unstable equilibrium

**A published155kPa amplitude does not remove the existing instantaneous law's descending-limb negative curvature.** The1.25 coarse/fine pair passes original equilibrium, pressure, geometry, replay, derivative and matched-static refinement gates. The1.01 perturbed coarse solve fails pointwise pressure compatibility and remains rejected/unrefined. This is a bounded composite educational block result, not a measured specimen or arm validation.

The [primary-source binding](../../data/anatomical-arm-v1/review/source-amplitude-p2-p1/primary-source-binding.json) selects the original Krivickas2011 Table1 TypeI SF mean15.5N/cm²:155,000Pa. Its chemically skinned VL,15°C protocol and source corrections remain attached. The normalization/reference mapping and block mechanics are educational assumptions. The [precommitted protocol](source-amplitude-p2-p1-protocol.md) retains all other coefficients, geometry, starts, numerical tolerances and budgets.

## Actual outcomes

| Case | Full free-force residual N | Pointwise pressure RMS | Cap reaction N | Lowest verified physical eigenvalue N/m | Disposition |
| --- | ---: | ---: | ---: | ---: | --- |
| coarse1.01 | 3.0834378e-5 | **3.3512715e-4** | 62.0446803, diagnostic only | Unassessed | Reject: pressure gate1e-6 fails; no fine request |
| coarse1.25 | 9.6594609e-5 | 6.4792890e-8 | 39.76114486 | **−9477.446195** | Stationary/derivative qualified; negative direction retained |
| fine1.25 | 5.9210517e-5 | 1.1615361e-7 | 39.76114575 | **−6705.235559** | Stationary/derivative qualified; negative direction retained |

Coarse1.01 reaches the original force stopping gate after4 Newton steps, but both32/256-point replay reject pointwise pressure compatibility. Its weak pressure residual is small; exact weak pressure elimination does not establish pointwise compatibility. No further iterations, new start, relaxed pressure gate, curvature classification or refinement was attempted.

Both1.25 solves stop after2 steps under the unchanged80/24 budgets. Their sampled J ranges are **1.00025364455–1.00025431424** and **1.00025292109–1.00025485235**. All original32/256-point stationarity/reaction/pressure/geometry/strict-crossing checks pass. Largest independent assembly difference is4.7032e-14N. Active lowest-witness derivative errors at1e-7/5e-8m are **3.4088e-10/5.3285e-10** (coarse) and **7.0336e-10/1.1096e-9** (fine), under the original1e-4 relative gate.

Matched-static refinement passes: maximum interpolated node difference **2.9847160e-9m**, relative cap-force difference **2.2516720e-8**, J-extrema difference **7.2345918e-7**. Pressure ranks are20/20 and81/81; scaled inf-sup ratio **.87669388**, above the original.5 concern threshold. This homogeneous two-level result is not a nonuniform atlas, mesh-family, spectrum or timestep-convergence claim. Eigenvalue magnitudes use mesh-dependent Euclidean nodal normalization.

Activation0 at the same accepted1.25 configurations also passes its stationarity/replay and derivative checks. Lowest values are **+1.97895876/+0.46849134N/m**. Worst passive derivative relative error is1.1524e-5, below1e-4. These controls isolate the active contribution; they are not proposed deactivated replacements.

## Preserved first-run gate-scope mistake

The first wrapper additionally imposed the stationary pointwise-pressure gate on arbitrary nonstationary derivative probes. That was not the original [verify_full_p2_p1.py](../../tools/verify_full_p2_p1.py) criterion. Its extra check rejected1.25 despite accurate gradients. The [additive scope correction](source-amplitude-gate-scope-correction.md) restores the original derivative criteria and preserves every first-run field and classification. Accepted equilibria still meet both original pressure gates. Probe pointwise residuals remain visible as diagnostics, including values above1e-6.

The retained coarse1.25 record was reclassified read-only; no coarse solve was repeated. Only its eligible fine case was executed. [First-run log](../../data/anatomical-arm-v1/review/source-amplitude-p2-p1/execution.log) and [successor log](../../data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2/execution.log) distinguish these operations. First runner commit `873e53812db6e89ccfff44aba17d8687e3e0ab3a`; successor preexecution commit `8015b76e0d1c90c0f5771d5afb92515f726eb35f`. Recorded elapsed times16.677s/47.075s; both exit0. Three wrapper/source-unit/equivalence tests and one gate-scope regression passed, with their raw logs retained.

## Matched-force control and smallest remaining model issue

The equivalence control passes at **alpha=87,083.873701Pa**: old sigma0=8,708,387.370105Pa at activation.01 versus155,000Pa at activation **.5618314432**. Direct stress/tangent/energy and assembled gradient/Hessian match below the declared1e-12 relative control gate. Original32/256-point force/pressure/reaction/geometry checks also pass. The preserved old witness gives **−4293.98749642736/−4293.987496427361N/m** in the two parameterizations. No activation measurement or force target is fitted.

The new full-activation cases use alpha155,000Pa, a different carried-force amplitude. Changing peak stress while matching alpha is exactly a relabeling of this instantaneous law; reducing alpha at fixed activation is not a matched-force constitutive repair.

**The smallest remaining constitutive issue is the held-state response:** the present instantaneous isometric active law retains negative interior stiffness at the accepted descending equilibrium. Before interpreting it as a credible transient tissue law, specify and implement a contractile/internal-state evolution and compare fast versus relaxed perturbations at matched force. An additional passive damping term or peak-stress relabeling does not answer that test. Separately, the1.01 solver outcome remains a pointwise-pressure qualification failure. Neither issue is resolved by this amplitude experiment.

## Deliverables and limits

[PNG](../../data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2/source-amplitude.png), [PDF](../../data/anatomical-arm-v1/review/source-amplitude-p2-p1-v2/source-amplitude.pdf) and the actual PDF raster were visually inspected: labels, axes, rejected-case status and scope notes are readable without overlap. Raw request/terminal fields, histories, witnesses, original Node replays and failed classifications are retained in both packets. No earlier source-bound evidence, production/book/Lean/protected files, source-access policy, skin or physical time/state advancement changed. Full anatomical mechanics and a self-consistent denser loaded trajectory remain unqualified.
