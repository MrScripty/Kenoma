# Continuous-strain CE reference qualification

The single precommitted **96-history run passed all declared initialization, strict population, translation, time and quadrature gates**. Each reference carried its own state through loading at 0 s, reversal at .2 s and the unchanged terminal time 1 s. No clipping, equilibrium reset, longer hold, external retry or numerical-gate change followed a failure. There was no numerical rejection in this run.

The executed [protocol](continuous-strain-ce-protocol.md), [reference implementation](../../tools/continuous_strain_ce_reference.py) and [static internal review](continuous-strain-ce-internal-audit.md) were committed at **f0aa3c11fd5a40107a68e35bcd8bf0a61fdd5800**, tree **76d0ae147eb795e06f61a201ce4034b91ce110f7**. Reference source SHA256 is **8f67cb3c84379ca1f1d6363e5f75d3e606113e120d17cf459240a9d944e0017e**. The [failure-export correction](conserved-ce-failure-export-results.md) and both intentional negative tests had already passed before this run. Frozen milestone **154d805386bdbe8b2c950af3d883c2ae54c376a8** remains an ancestor, with every earlier source, receipt, failure and render preserved.

## Raw evidence and fixed gates

[Raw execution log](../../data/anatomical-arm-v1/review/continuous-strain-ce/execution.log), [command/commit/tree/timing receipt](../../data/anatomical-arm-v1/review/continuous-strain-ce/execution-metadata.json), [full summary](../../data/anatomical-arm-v1/review/continuous-strain-ce/summary.json) and [matched-density archive](../../data/anatomical-arm-v1/review/continuous-strain-ce/matched-densities.npz) preserve the single 146.16 s execution. OPENBLAS_NUM_THREADS was one. DOP853 retained its ordinary embedded error control at rtol=1e-11, atol=1e-14 and the two predeclared maximum steps .001/.0005 s; there was no external restart after a gate failure.

There were **144,240 accepted solver nodes**, including both segment origins. Every admitted node and matched sample passed finite/nonnegative main, ghost and edge density checks and strict main-only B≤N. Zero is present in deliberately masked exterior ghost values. Attached mass came only from weighted main densities; auxiliary probes added no head population. Main counts 200/400/800, domains [-2.4,2.4]/[-3,3], pCa 4.5/6.1 and displacements ±.001/±.0005 are the complete declared matrix.

| Check | Maximum observed | Unchanged gate |
|---|---:|---:|
| Initial weighted full kinetic residual | 6.59944e-15/s | 1e-10/s |
| Initial moment versus adaptive stationary integral | 9.21485e-15 | 1e-10 |
| Matched time-pair B difference | 1.66533e-16 | 1e-10 |
| Matched time-pair F/E difference | 3.33067e-16 | 2e-10 |
| Successive quadrature B/F/E difference | 7.66054e-15 | 1e-9 |
| Mass, signed-force and elastic-energy jump identities | 2.35055e-16 | 2e-12 |

The maximum reported domain-extent moment difference was 1.22125e-15; this is a diagnostic, not a newly invented extent gate. Moment-refinement differences are near floating-point roundoff. These are matched moments, not a common full-density norm or an anatomical nodal-convergence certificate.

The evolved ghost field provides reversal evaluation directly, with no strain interpolator. Both direct escape ledgers retain the signed target force moment, nonnegative escaped mass and elastic energy. There is no upwind interpolation-variance work in this reference. Passing those elastic identities supplies no chemical-energy or thermodynamic closure. Fixed 32-point escaping-strip integration was checked by its accounting gates, not by an independent edge-node refinement family.

## Matched-time comparison and separated numerical errors

All **144 preserved BE/bin histories** were compared at their identical 11 physical event/time samples against the matching 800-node/.0005 s continuous reference. Raw and own-equilibrium-subtracted B/F/E errors are saved separately, with force-response errors divided by that model's own initial |F(0+)−F(0−)|. No new response threshold was selected. Bin masses and point densities have no declared common nodal L1 map.

At R=3, dx=.01 and BE dt=.001 s, maximum matched force-response error ranges **.419–.606% of the own initial force jump** over both calcium conditions and four signed displacement probes. Combined temporal and spatial errors can cancel; their minimum envelope does not decrease monotonically with bin refinement.

To separate that effect, [read-only analysis](../../tools/analyze_continuous_ce_bin_separation.py) also compared the **48 already qualified independent bin ODE references** to the new continuous reference. It ran no ODE or BE operator. The [raw spatial-separation receipt](../../data/anatomical-arm-v1/review/continuous-strain-ce/bin-spatial-separation.json) preserves every signed matched force-response error and its input hashes. Across all 16 domain/calcium/displacement groups, bin-width halving ratios are **.46783–.50766**. At R=3 the spatial-only force-response ranges are:

| Bin width | Relative matched response error |
|---|---:|
| .04 | .4116–.4775% |
| .02 | .2062–.2303% |
| .01 | .0990–.1109% |

The old first-order transport error remains disclosed. This comparison qualifies a continuous-strain numerical prerequisite for the SAME bounded held-N, overlap-one, conserved-M model; it does not retrospectively change the old runner's gates, work accounting or failed-case receipt gap.

## Reviewed render and remaining mechanics

[PNG](../../data/anatomical-arm-v1/review/continuous-strain-ce/continuous-reference.png), [PDF](../../data/anatomical-arm-v1/review/continuous-strain-ce/continuous-reference.pdf) and [actual PDF raster](../../data/anatomical-arm-v1/review/continuous-strain-ce/continuous-reference-pdf-raster.png) were visually inspected. The [render receipt](../../data/anatomical-arm-v1/review/continuous-strain-ce/render-receipt.json) binds inputs, renderer and outputs. [Analysis values](../../data/anatomical-arm-v1/review/continuous-strain-ce/continuous-analysis.json) retain the figure's definitions. Matplotlib used a temporary writable cache after its default home-cache warning; rendering exited zero and was not repeated.

Source anatomy/mechanics provenance remains the [original publication pixel audit](original-plos-table-visual-audit.md) and [source/code/calibration reconciliation](calibration-source-reconciliation.md). No constitutive assumption in the production arm, book or Lean changed. The separately qualified [dimensionless CE/PE/SE initializer](source-ce-series-initialization-results.md) closes algebraic force balance, not a coupled series-loaded trajectory. PE units/source mapping, F0/area, serial architecture, slack lengths, temperature/species transfer and human calibration remain unresolved.

The loaded anatomical result still has corner J=.712631 and unqualified full nodal/quadrature/timestep convergence. The isolated 256-point accepted increment is not a self-consistent dense arm trajectory. The fixed-active descending negative directions remain preserved and are not cured merely by bulk compression control. No skin or whole-envelope credibility claim follows from this numerical CE milestone.
