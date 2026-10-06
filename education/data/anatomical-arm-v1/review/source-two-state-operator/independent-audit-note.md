# Independent held-capacity operator qualification

**PASS: all 72 declared one-step backward-Euler cases, 10 equilibrium checks, 6 auxiliary checks and 22 intended input/arithmetic rejections passed. No failure, retry, changed start, extra solver budget or relaxed gate occurred.** This is a synthetic mathematical operator qualification. It does not supply a physiological trajectory, article/code replay, load or series-element experiment, SI calibration, anatomical solve or continuum stability result.

The [independent tool](../../../../tools/audit_source_two_state_operator.py) was executed once on 2026-10-06 against [source_two_state_operator.py](../../../../tools/source_two_state_operator.py), after protocol commit `ffc50039b359eb4712571182e4c99e5e7ff22423`. The [predeclared protocol](../../../../research/mechanical-closure/source-two-state-operator-protocol.md) and [analytical audit](../../../../research/mechanical-closure/source-two-state-implicit-internal-audit.md) define the fixed domain 0≤Σpi≤N≤1, held N, positive detachment rates and nonnegative attachment cell rates.

The independent reference uses mpmath at 60 digits and solves the original coupled vector BE residual, not the reduced quadratic. It starts at the old state, uses the full analytic Jacobian, tolerance 1e-45 and maximum 20 Newton steps. Every reference independently passed strict nonnegative-bin and B≤N bounds and its unscaled full residual gate 1e-40. Equilibrium references solve the original vector RHS from zero. Candidate states separately passed strict bounds with no capacity tolerance, clipping or rescaling.

| Check | Worst observed | Fixed gate |
|---|---:|---:|
| BE state difference from mp60 vector root, max absolute | 1.7446523282e-16 | 2e-12 |
| Full BE residual divided by max(1,N,hΣFi,h max(gi)N) | 1.6309780511e-16 | 1e-12 |
| Reference's own full BE residual, unscaled | 7.5904763410e-46 | 1e-40 |
| Independent Jacobian vs centered numerical difference | 4.2896306581e-39 | 1e-25 |
| Implemented Jacobian vs independent mp60 analytic entries, scaled | 9.0278291478e-17 | 1e-12 |
| Equilibrium state difference from mp60 vector root | 1.0973668806e-16 | 2e-12 |
| Equilibrium full RHS residual, scaled | 3.0470512131e-18 | 1e-12 |

The largest BE state difference occurred on the seven-bin grid at N=1, saturated old mass and h=.001. The largest normalized BE residual occurred on the three-bin grid at the same N, saturation and h. All original case inputs, states, independent references, unscaled/scaled residuals and Jacobian diagnostics are retained in the [raw JSON](independent-audit.json); the [log](independent-audit.log) records every outcome. The smallest candidate population among the 72 cases was 2.7251682762e-42, still positive.

Zero attachment, zero N, sparse attachment/mass, bin permutation and tiny-I equilibrium passed. The tiny-I attached mass was 2.9384e-25 and was preserved by population reconstruction rather than subtraction from N. At N=B_old=1, h=1e-18 and g=.05, direct subtraction gives W=0 in binary64; positive accumulation gives 5.0000000000000005e-20, agreeing with mp60 W=5.0000000000000006350e-20. This witness confirms why the implementation's positive detached-increment calculation matters; it is not a physical time history.

All 22 rejection checks passed, including a capacity decrease below the OLD attached population even though a putative detached U would fit, a negative individual bin with otherwise admissible total, invalid N/rates/h/shapes, nonfinite inputs and finite-input coefficient overflow. The candidate operator did not accept an unphysical alternate nonlinear branch or hide invalid input using a bound allowance.

## Identity receipts

| Artifact | SHA-256 |
|---|---|
| Committed protocol | `13533025be37b52a6c83b1e17e2fe77eb1ae999f44d4eef44f27fbd5041f80ba` |
| Operator source | `21d42a4af37d25f984843dc32db8ec2f9e6608b7c157e177feaaff951e520824` |
| Independent audit source | `d89a3dfe58c49999cbeab19ec1e59b7203025551da5099c41fec423b14abb597` |
| Raw independent JSON | `f7d2f37f36ff0d1730a22a6fb42a318ed48d4d8c211ab631846602be7079625d` |
| Independent log | `f8f610f43405782bdd1fea6fc067780a474e7cb96f65f7b58bccdcc043e09568` |

The independent source and protocol hashes are recorded in the raw receipt. No prior packet or source file was edited, no prior simulation was rerun, and this lane performed no Git operation. The now separate original-table pixel evidence does not remove the remaining article/code convention and SI force/area calibration obligations. A later direct-CE or series-coupled experiment requires its own declared inputs, initialization, boundary transport, normalization and refinement gates.
