# Independent completed fine-window arithmetic/provenance review

Verdict: **PASS_INDEPENDENT_RETAINED_ARITHMETIC_AND_PROVENANCE**. This is a successful evidence review of an **UNRESOLVED_FIXED_PATCH_INTEGRATION** result; it does not award scientific qualification.

Frozen result commit: `5f7612f6c7f6609d8946b3394d7363609d7a30b1`. Corrected runner source: `9611a4865e9591041fa5253c9df6c0f91da84089`.

The standalone scalar reducer imports only Python standard-library modules. It reads existing JSON/binaries and SHA256 hashes; it never imports repository execution, geometry or material code. ZERO specimen/material-law calls and ZERO quadrature generation. All artifacts were written only in this temporary review directory; the frozen worktree was clean before and after review.

46,793,317 assertions passed. Reviewed all 2,002 logical regional references, 94 stage aggregates, 16 hybrids and 24 comparisons (20 required). Global assembly and comparison arrays include all 585 nodes, including all 90 held nodes. The matched comparison partition has 156 units: nine quiet whole elements and 21 physical subregions for each of seven focus elements. Every component, original subregion, grouped bin, force vector, energy and directional-work value was checked.

Verified 2,936 source inventory entries, 3,114 output inventory entries, and 6,051 unique file SHA256 values. All point/weight binary files match the accepted preflight artifacts. Exact frozen positions, direction, reference mesh, material/law identities and gates are preserved. The original 38ae result, original failed two-shell evidence and prior consumed authorization have no Git changes.

The 19,716,000 new callbacks are distinct from 640,000 shared logical measurements: 480,000 same-invocation P4, 80,000 historical F44, and 80,000 historical X44. The original 4,000 failed two-shell measurements remain byte/value attributed through immutable F44 and are not counted as new.

The independently recomputed comparison vector discrepancy is at most 1.3552527156068805e-20 N; scalar comparison metrics differ at most 6.776263578034403e-21. Component force reconstruction error is at most 2.808482613136931e-12 N and energy reconstruction error at most 4.618527782440651e-13 J, below the unchanged 1e-8 N / 1e-9 J reconstruction gates. The gate decisions use the recomputed finite values, without adding a numerical tolerance to any force/work acceptance threshold.

| Field | Comparison | Required | Replayed verdict |
|---|---|---|---|
| control45 | S0/S1 | True | PASS |
| control45 | S1/S2 | True | PASS |
| control45 | I0/I1 | True | PASS |
| control45 | S2/I1 | True | PASS |
| control45 | S1/AR | True | PASS |
| control45 | S1/AH | True | PASS |
| control45 | S1/AC | True | PASS |
| control45 | S0/I0 | False | FAIL |
| control45 | S1/I1 | False | PASS |
| control45 | D4/D5 | True | PASS |
| control45 | U4/U5 | True | PASS |
| control45 | D5/U5 | True | PASS |
| terminal46 | S0/S1 | True | PASS |
| terminal46 | S1/S2 | True | PASS |
| terminal46 | I0/I1 | True | FAIL |
| terminal46 | S2/I1 | True | PASS |
| terminal46 | S1/AR | True | PASS |
| terminal46 | S1/AH | True | PASS |
| terminal46 | S1/AC | True | PASS |
| terminal46 | S0/I0 | False | FAIL |
| terminal46 | S1/I1 | False | PASS |
| terminal46 | D4/D5 | True | PASS |
| terminal46 | U4/U5 | True | PASS |
| terminal46 | D5/U5 | True | PASS |

Only terminal I0/I1 is a failed required comparison. Its volume force signed/triangle values are 4.460081948072867e-05 / 4.4600819482843576e-05 N; total force values are 4.474374534905057e-05 / 4.474374535162453e-05 N. They exceed the unchanged global 1e-5 N gate and independent-family focus allocation 1.5e-6 N. Both signed and triangle work checks pass the global and focus allocations.

Terminal S2/I1 passes all force/work/global/allocation checks; maximum force triangle value over the five components is 9.564050446831282e-07 N. This is retained finite agreement between the particular two rules at the fixed field. It supports investigating coarse I0 underresolution but cannot replace the failed required I0/I1 witness, prove convergence, or qualify outside elements.

Ten in-memory damage cases are refused: altered force/work gates, false term pass, unit omission, changed local force/work, changed triangle data, changed held-node data, NaN and changed scalar metric. No stored input bytes were changed.

Outside 236 elements remain unqualified. No anatomical-capstone completion, equilibrium, deformation, tangent/displacement or analytic convergence claim follows. No new execution is authorized by this review.

Files: [report.json](report.json), [review.py](review.py), [review.log](review.log), [damage.json](damage.json), [damage.py](damage.py), [damage.log](damage.log).
