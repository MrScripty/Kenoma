# One bounded geometry-aware run: refused at the declared fraction limit

The single authorized paired run at **`f3d36e4de69bce20f04c6368e4c28fc055d26148`** stopped with **`REFUSED_BOUNDED_RESPONSE`**, child exit1, after iteration13 of the46-coordinate stage exhausted all21 permitted fractions. The45 control passed its projected gate; the46 projected and full-nodal physical gates remain failed. **No retry, parameter change, force fit, added modes or changed initialization occurred.** This is an exploratory failure record, not anatomical, convergence, production or book qualification.

The frozen [protocol](isolated-geometry-backtracking-20261006.md) remains unchanged. Operator/protocol source is `14c0ac1db9161bcca6c89f6b8a2ba8553fb288bb`. Raw execution evidence is commit `44f7ea657137186c1af5e92d76ea442f7cf41cd4`; geometry/arithmetic verification source `016d615f4a0b1b73327eb7ad37791f0bf7ea3385`; terminal endpoint-inspection source `2226163b4d4b1dfd8125984ad70536a17707c551`. The execution ran once from2026-10-07T00:07:11.868758Z to00:14:38.205039Z. It did not reach or extend the60-iteration ceiling.

## Identity and gates

The original frozen initialization, archived45 control coordinates and nodal field, and exact archived once-selected direction all match. The control orientation artifact is byte-identical to the old control artifact. All old experiment/proposal/source/preflight hashes match. Material, fixed activation1, fitted sigma0, fibres,252 P2 elements,2048 points per element,90 exact cap nodes,495 free nodes and the45/46 basis remain unchanged. Reference target **987.26 N** and old achieved fit **987.2744117188512 N** remain distinct; neither is enforced by a new fit.

| Recorded field | Original45 maximum, N | Extended46 maximum, N | Full-free maximum, N | Full-free L2, N |
|---|---:|---:|---:|---:|
| Unchanged45 control, extra coefficient zero | 0.000058200781 | 379.531980194 | 64.066837477 | 379.531980194 |
| First accepted46 field, iteration1 | 0.877878551 | 343.385937173 | 53.595914611 | 349.338833043 |
| Last valid46 field, iteration13 | 1.084400800 | 322.927666783 | 56.629557236 | 352.168538536 |

The original45 entries are independently assembled retained-coordinate gradients; the45 operator stopping maximum is5.820077786236932e-5 N, differing by about3.2e-12 N from that independent assembly. Both pass the45 projected stopping gate. Adding the frozen direction exposes379.531980 N at the identical control; the extended46 maximum falls to322.927667 N while the original45 residual rises above1 N. Comparing the latter46 residual to the tiny45 control residual would mix spaces. Every physical force criterion remains **1e-4 N**. The full-free maximum initially improves, reaches51.787500 N at iteration2, then increases to56.629557 N. None of these full-nodal states passes physical qualification.

All16 evaluated trace states have recorded positive Cholesky tangents, exact zero cap displacements and certified unchanged whole-path domain. The four original-size derivative probes reproduce the old derivative checks and pass fresh rounded-path gates. The accepted direction retains its initial direct/relaxed curvatures54015.62317293791/44501.72683367138 N/m; no new terminal curvature or global stability claim is inferred from these local checks.

## Accepted steps and declared stop

The45 solve accepts fraction1 and reproduces its old control exactly. The46 accepted fractions for iterations0–12 are:

`1, 1/4, 1/16, 1/64, 1/256, 1/512, 1/2048, 1/4096, 1/16384, 1/32768, 1/65536, 1/262144, 1/1048576`.

Each candidate is newly rounded and independently certified before material evaluation; all14 accepted updates across both stages satisfy the unchanged Armijo inequality. There are **156 unsupported-geometry rejections**, **zero material evaluations on rejected candidates**, zero sufficient-decrease rejections and zero unexpected post-certification failures. The terminal iteration13 rejects fractions1 through2^-20, all21, then stops with `Exhausted21 fractions through2^-20 without admissible sufficient decrease`. The last valid field remains retained; no rejected coordinate field becomes the next optimizer state.

Every raw Newton coordinate/nodal vector, scaling and actual rounded increment is in the raw record. For example, the initial46 raw maximum is0.0022947117230379707 m, scale0.08715691735571031, and scaled nodal bound0.00019999999999999998 m. At terminal iteration13 the raw maximum is0.000812786590837395 m, scale0.24606705161553502, scaled maximum0.0002 m and local predicted slope−0.25611871863271646 J. The local slope remains negative; the finite candidates cannot pass the retained geometry/domain gate within the declared fractions.

The [terminal endpoint witnesses](../review/isolated-geometry-backtracking-20261006/terminal-corner-witnesses.json) sharpen the generic unsupported-certificate finding: **every recorded terminal fraction violates the unchanged domain at element247, corner0/node92**, using exact endpoint determinant numerators. At the smallest permitted fraction2^-20, the rounded maximum nodal increment is only1.907347368232023e-10 m, but its actual corner J is approximately**2.2946476123643858e-7**. Its determinant is positive, yet below1e-6. The exact guarded endpoint numerator is negative. This distinguishes positive orientation from the mandatory material-domain guard. No smaller fraction, alternative direction, new force or energy query was tried.

## Energy, J and reactions

| Quantity | Unchanged45 control | Last valid46 |
|---|---:|---:|
| Total fixed-activation potential, J | −33.48083147770711 | −33.848607777509955 |
| Matrix component, J | 0.013302835138244219 | 0.013581640652891701 |
| Volume component, J | 1.5033267674384176 | 1.3895396695218432 |
| Passive fibre component, J | 3.4366421214364897 | 3.4151740110510413 |
| Active potential, J | −38.43410320172026 | −38.66690309873573 |
| Minimum queried sampled J | 0.5683147059934479 | 0.0913917190032232 |
| Minimum queried corner J | 0.5594239031350546 | 0.0000013009819920047246 |
| Global volume ratio | 1.0478270856929301 | 1.0442321107021628 |
| Distal full-nodal axial reaction, N | 605.1193134928182 | 626.1074142415761 |
| Proximal full-nodal axial reaction, N | −765.6589734722645 | −793.3535714260607 |

Total potential decreases by**0.3677762998028413 J** from the same control. Active potential is not passive stored energy. The sample/corner minima are queries; the exact certificates prove the unchanged `J>binary64(1e-6)` bound throughout accepted paths. Raw coefficient numerators are sign witnesses, not comparable physical margins. The full-nodal cap reactions are distinct from the old fitted reduced-translation conjugates. Unequal cap reactions here coexist with nonzero free-node residual; they do not establish equilibrium or a new fit.

## Review evidence and practical limits

- [Execution receipt](../review/isolated-geometry-backtracking-20261006/execution-receipt.json): exact command/head, one invocation, exit1, source/preflight/log/result hashes.
- [Run summary](../review/isolated-geometry-backtracking-20261006/run-summary.json): complete final and control fields/gradients/energies/reactions and compact16-state trace.
- [Geometry/arithmetic verification](../review/isolated-geometry-backtracking-20261006/run-verification.json): all170 trial certificates and55 other material gates reproduced;189 unique whole paths recompiled. Raw/scaled/rounded increments, cap traces, accepted Armijo arithmetic, rejection retention and terminal21-fraction sequence match. Positive-tangent flags are recorded-run evidence, not freshly recomputed tangents.
- [Trial inventory](../review/isolated-geometry-backtracking-20261006/trial-inventory.json) and [Newton inventory](../review/isolated-geometry-backtracking-20261006/newton-inventory.json): compact independently reconstructible coordinates/vectors, hashes, certificate minima/failure witnesses and dispositions.
- [Complete raw results](../review/isolated-geometry-backtracking-20261006/results.json) and [execution log](../review/isolated-geometry-backtracking-20261006/execute.log): every stored state, direction, rejected fraction and stop. Raw results are50,610,659 bytes; compact review receipts are each below1 MiB.

Raw results SHA256: `d781d7a68cd742b4019ae89d5464109d42b758e8f30419341b5ee55421e1406d`; structural preflight SHA256: `a7d24e827b8936efcd684137ff98374845ee5dfc12b71e5e50a550fb96a216ac`. Both post-run analyses use geometry and arithmetic only: zero new constitutive evaluations or nonlinear solves. The original failed experiment is unchanged.

The experiment demonstrates a bounded progression beyond the earlier immediate refusal, followed by an honest failure at the unchanged limit. It establishes no equilibrium, continuum/spatial/quadrature convergence, stability, anatomical completion, production or book adoption. No PR, merge, deployment, protection or credential changes occurred. Further experiments require separate review and authorization; none is proposed or executed here.
