# Activation-equality-only continuous-state split diagnostic

Continuous activation split/restart substantially reduces the measured crossing-step and propagation errors. All 66 pairwise comparisons among the twelve split prefixes pass the unchanged state gates in both declared windows, including all four RK4 step sizes and both representations/adaptive methods. Literal controls retain the earlier propagation integral failure. The split refinement ratios are irregular and do not qualify fourth-order convergence. This remains a scalar incoming-prefix diagnostic, with zero ordinary/sliding events and no production or anatomical adoption.

Frozen source: `d54020fb3e05a3cc770036483392c94292c172dc`; source tree: `f5377333181ffb6b7e03eb007718da47e0a5caad`. Protocol SHA256: `de11d380272e109c05a1d7a3045ee40689dcb2c7c42c39d743a4b445d561b948`. Raw-results milestone: `88823764304f3902d12d185a6e8b11aa92b7df2a`; raw tree: `9c6e92550987a2b36c06478ed5301e0729428a58`. The [protocol/source](activation-equality-diagnostic-protocol.md) and [machine bindings](../../data/activation-equality-diagnostic-v1/protocol.json) were committed and pushed before the real-case prefix matrix.

The nine corrected [preflight tests](../../data/activation-equality-diagnostic-v1/preflight/tests.log) include a high-equilibrium serialization step and injected invalid-state/kernel checks. They are not described as preceding every simulation. The [rejected first test](../../data/activation-equality-diagnostic-v1/preflight/rejected-unmatched-excitation-tests.log) and its original source are retained: it compared two rates at different actual excitations. The corrected check uses matched excitation for each original branch kernel, without changing the formulas, test tolerance or physical acceptance gates.

Exactly 24 mass-1 prefixes run literal-control versus split handling × full-source/reduced-independent × RK4 200/100/50/25 µs, DOP853 and Radau. Every run reaches .107 s (within original floating-time handling) with zero physical failures, before the first demonstrated ordinary crossing at about .107883 s. All 24 force/work/impulse/GL8 audits pass. Maximum independently re-evaluated accepted force discrepancy/residual is 9.1660012913052924e-13 N and maximum energy/ledger discrepancy is 3.2794374854594466e-12 J. These are accepted-prefix balance checks, not whole-arm or completed-controller certificates.

The [pinned original activation source](../../data/millard-reference-v1/upstream/MuscleFirstOrderActivationDynamicModel.cpp) retains a_dot=(u−a)/tau_A for u>a and (u−a)/tau_D otherwise, with tau_A=.01(.5+1.5a), tau_D=.04/(.5+1.5a) and original clipping. Both rates are zero at mathematical equality; their g derivatives 1/tau_A and 1/tau_D differ at this interior crossing. All ten other rates are unchanged. The separate JS adapter evaluates the original source mechanical kernels and the original one-sided activation formula; the independent branch uses the original Python formula.

For the split policy, trial stages use the original incoming activation field extension. The accepted event is localized on that actual dense polynomial, with ≤1 ps bracket, |g|≤1e−13 and at most 32 iterations. Accepted interval endpoints and GL8 nodes remain on the correct original side within the finite root target. The full eleven-coordinate event state is retained without projecting a to u. The original outgoing field then restarts at exactly that state. RK4 completes the original crossing-step remainder before rejoining its lattice; adaptive methods restart with unchanged tolerances, maximum step and Jacobian construction. The ordinary-crossing implementation, all laws/gains/physical gates and source velocity iteration budget remain fixed.

All twelve split accepted equality states and following restart states match exactly in all eleven coordinates. All 24 observed/localized roots are transversal in the positive-to-negative direction, with normals approximately −.230639/s. The largest root bracket is 8.9925593013684413e-13 s; at most 30 bisections were used. The largest one-sided rate discrepancy at the finite-residual numerical root is 1.5737444963478287e-11/s; mathematical equality still has zero discrepancy. No accepted coordinate is reset.

All eight adaptive reference runs (both policies, both representations, both methods) are retained and all 28 pairwise reference comparisons pass the original gates. Their equality-time span is 8.4606260756028839e-10 s, leaving 1.9991539373924396e-06 s under the original 2e−6 s event criterion. This comparison does not align histories by event time or establish an exact event-time error bound.

Across all 66 pairs within each policy, the worst errors and exact margins are:

| Window / policy | Max absolute ΔI | I margin under 1e−9 | Max absolute Δa | Max absolute Δraw | raw margin under 1e−8 |
|---|---:|---:|---:|---:|---:|
| transition / control | 3.859082627768822e-12 | 9.9614091737223124e-10 | 2.2100969471194887e-08 | 8.7897781414492115e-10 | 9.1210221858550791e-09 |
| transition / split | 9.9033190095786441e-13 | 9.990096680990422e-10 | 2.7249563716580383e-11 | 5.5280849342587146e-12 | 9.9944719150657415e-09 |
| propagation / control | 4.1013879193904645e-09 | -3.1013879193904647e-09 | 2.2100969471194887e-08 | 8.639962981171756e-09 | 1.3600370188282442e-09 |
| propagation / split | 3.7670457031513394e-12 | 9.9623295429684872e-10 | 2.1872600952654864e-11 | 4.3961102119682849e-11 | 9.9560388978803174e-09 |

The primary windows are transition [0,.003] and propagation [.003,.107], inclusive on the stored absolute 1 ms grid. The shared .003 endpoint can appear in both tables. Exact margins for all seven quantities, all pairs and both windows remain in [analysis.json](../../data/activation-equality-diagnostic-v1/review/analysis.json). The worst split-policy propagation errors preserve substantial margin in every quantity:

| Quantity | Original gate | Worst split propagation error | Exact margin |
|---|---:|---:|---:|
| y_m | 9.9999999999999995e-07 | 3.0849489629503068e-12 | 9.99996915051037e-07 |
| w_m_per_s | 1.0000000000000001e-05 | 4.708791689900238e-11 | 9.9999529120831018e-06 |
| a | 1.9999999999999999e-06 | 2.1872600952654864e-11 | 1.9999781273990473e-06 |
| q | 1.9999999999999999e-06 | 4.6798565023209449e-11 | 1.9999532014349767e-06 |
| FT_N | 0.0001 | 1.0869253941336865e-08 | 9.9989130746058668e-05 |
| I | 1.0000000000000001e-09 | 3.7670457031513394e-12 | 9.9623295429684872e-10 |
| raw | 1e-08 | 4.3961102119682849e-11 | 9.9560388978803174e-09 |

Across all eight adaptive references, propagation max |ΔI|=6.6267658895002857e-11 with margin 9.3373234110499721e-10; max |Δraw|=1.4404047399274589e-10 with margin 9.8559595260072543e-09. These include the literal adaptive implementations rather than replacing them with favorable split references.

Crossing-step error is measured separately using each RK method’s original nominal crossing interval. Compare accepted states at its two fixed absolute endpoints against all eight actual adaptive dense polynomials; no trial suffix, event alignment or inferred interpolation is used. End-point FT/raw are independently re-evaluated from those states; primary grid tables retain each representation’s stored outputs. All 128 crossing-step tables reproduce exactly from frozen source/accepted coefficients. The following signed activation errors versus split full-source DOP853 illustrate the distinction; the complete multi-reference evidence remains in the receipt:

| RK step (µs) | Nominal left/right (s) | Inherited left Δa, both RK policies | Control right Δa | Split right Δa | Control crossing-step Δa change | Split crossing-step Δa change |
|---|---|---:|---:|---:|---:|---:|
| 200 | 0.0024000000000000002 / 0.0026000000000000003 | 3.0732555389434424e-11 | 1.9761318123534544e-08 | 1.8871078311111233e-11 | 1.9730585568145109e-08 | -1.186147707832319e-11 |
| 100 | 0.0024000000000000002 / 0.0025000000000000001 | 1.8945331414776945e-12 | 2.980206664782159e-09 | -4.6156828359400492e-13 | 2.9783121316406813e-09 | -2.3561014250716994e-12 |
| 50 | 0.0024000000000000002 / 0.0024500000000000004 | 1.1714934577966574e-13 | -2.4754840191598682e-09 | -2.1238566461079245e-13 | -2.4756011685056478e-09 | -3.2953501039045818e-13 |
| 25 | 0.0024250000000000001 / 0.0024499999999999999 | 6.7862382380212694e-15 | 2.6205697334358291e-10 | 5.3082538364890297e-15 | 2.6205018710534489e-10 | -1.4779844015322396e-15 |

At 200 µs the inherited activation error before that crossing step is about 3.0733e−11 for both RK policies. The control crossing-step right error is 1.9761e−8, while the split right error is 1.8871e−11. The large control activation error arises within the crossing step and subsequently couples into the force/integral orbit: the full-source 200/100 propagation I error is 3.0964600042024393e−9 for controls versus 3.3183455983021304e−12 for split handling. This does not erase inherited smooth-step error or prove all remaining error is caused by equality. The signed crossing-step error change is never substituted for raw state errors or gate checks.

Observed adjacent RK4 refinement is retained without an order fit. Each error triplet compares 200/100, 100/50 and 50/25 µs:

| Full-source policy / window / quantity | Error 200/100 | Error 100/50 | Error 50/25 | Ratio 1 | Ratio 2 |
|---|---:|---:|---:|---:|---:|
| control / transition / I | 2.5896814972667121e-12 | 1.2693072267355113e-12 | 6.1221408090359874e-13 | 2.040232217007877 | 2.0733061625470528 |
| control / transition / a | 1.6686970943924351e-08 | 5.413998527270536e-09 | 2.7155915502397043e-09 | 3.0821897826294897 | 1.9936718858889675 |
| control / propagation / I | 3.0964600042024393e-09 | 1.0049260581665442e-09 | 5.0389849237664208e-10 | 3.0812814326377729 | 1.9943025696044472 |
| control / propagation / a | 1.6686970943924351e-08 | 5.413998527270536e-09 | 2.7155915502397043e-09 | 3.0821897826294897 | 1.9936718858889675 |
| split / transition / I | 9.281342208190043e-13 | 7.9106756613474792e-14 | 2.1278722937855855e-14 | 11.732679489742964 | 3.7176458777392192 |
| split / transition / a | 2.5567797878878196e-11 | 1.5765652672250496e-12 | 2.1422447149532786e-13 | 16.217405273605127 | 7.3594078968678129 |
| split / propagation / I | 3.3183455983021304e-12 | 1.1229472213214464e-13 | 3.7066703872934426e-14 | 29.550325565588142 | 3.0295308295308296 |
| split / propagation / a | 1.9407010720673412e-11 | 2.3171048413317408e-13 | 2.1422447149532786e-13 | 83.755427784266161 | 1.0816247206296765 |

Control propagation I ratios remain 3.0813 and 1.9943. Split propagation ratios are 29.5503 and 3.02953; split transition I ratios are 11.7327 and 3.71765. These are not consistent evidence of a recovered fourth-order asymptotic rate. The finest split errors are small relative to observed reference/interpolation/floating uncertainty: for example the split plot versus Radau has a roughly 1e−12 propagation plateau while DOP853 comparisons continue lower. No higher order, exact solution or sole causal explanation is presumed. Both representations and I/a/raw/FT ratios are retained in [decision-summary.json](../../data/activation-equality-diagnostic-v1/review/decision-summary.json).

Literal controls exactly reproduce the corresponding preserved original eleven-coordinate states through .106 s. RK controls also reproduce .107; changing the adaptive solver upper bound to .107 changes Radau’s final interpolant by 2.1079318845984574e-13 in I (full-source) and 1.9510781879006345e-13 (independent), while DOP853 final I changes are zero. These endpoint effects are retained separately from activation handling. RK split/control states are identical through .002 before their nominal crossing step. Adaptive dense coefficients can be affected by stages across a future equality within a crossing trial, so no stronger blanket pre-equality identity claim is made.

Evidence includes 324 directional new/new comparison records covering all 276 unique cell pairs, plus twelve original-control comparisons: 672 window tables and 4,704 independently recomputed maxima/signed witnesses/exact margins. The 128 crossing-step tables retain inherited and subsequent changes separately. All 34,062 accepted interval polynomials and 24 equality auxiliaries are retained. Independent primary SciPy dense replay and RK coefficient evaluation validate 2,568 grid samples and 24 event states to ≤1e−12; maximum grid-state replay discrepancy is 1.9761969838327786e-14. [Verification](../../data/activation-equality-diagnostic-v1/review/verification.json) records twelve exact continuous restarts, the RK remainder rule, unchanged source bindings and all 1,913 baseline Git blobs byte-identical to b1689d07. The original rejected preflight and all earlier failed scientific classifications remain unchanged.

[PNG](../../data/activation-equality-diagnostic-v1/review/activation-refinement.png) and [SVG](../../data/activation-equality-diagnostic-v1/review/activation-refinement.svg) show both policies, all four steps, both representations, and both split adaptive methods. Literal adaptive references remain in the complete tables. The PNG was inspected and SVG parsed; any zero error is floored at 1e−17 solely for log-plot visibility.

This diagnostic supports activation equality as a substantial numerical error source in the original coarse crossing step and subsequent scalar propagation. It demonstrates strong split-prefix agreement under the declared gates, while asymptotic order remains unqualified. Combining this split policy with ordinary-crossing handling in a longer incoming trajectory is a separate protocol decision; this experiment stops before that interaction. It accepts no ordinary/sliding state and makes no book/Lean, production, whole-arm, bulk-compression, skin or anatomical qualification claim.
