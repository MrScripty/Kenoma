# Source-informed CE/PE/SE initializer qualification results

The predeclared algebra-only qualification **PASSED** in one execution: **three stationary conditions, 27 initializer probes, 56 invalid-input rejection probes and four SE inverse boundary probes**. This establishes the declared normalized initializer's force balance, moment-based fast tangents and rejection gates for these fixed probes. No coupled trajectory, release, experimental fit, human calibration or production change was performed.

## Immutable protocol and raw evidence

Execution used protocol commit `a0456a4fad7041cb71f3841888445a9f8f80e22b`, tree `84013bf431a0fe80e2c1eca2306190fa658ee07d`. Before execution, the working runner matched the committed bytes exactly and HEAD matched that protocol commit. Runner SHA256: `7abe962f9888621b99591142c6b477e745a8e31a028008fe38a97f97b615ffd5`. The [predeclared design](source-ce-series-initialization-design.md) and [runner](../../tools/source_ce_series_initialization.py) are unchanged by this results extraction.

The new packet was created exclusively at `education/data/anatomical-arm-v1/review/source-ce-series-initialization/`. It preserves:

- [summary.json](../../data/anatomical-arm-v1/review/source-ce-series-initialization/summary.json): 67909 bytes; SHA256 `75724c0700b629d2f32cb3f482143d4d8cf6e00e1fac62a8db05db7ecfaf6a6d`; final status `PASSED`, completed context, no failed/current candidate.
- [execution-metadata.json](../../data/anatomical-arm-v1/review/source-ce-series-initialization/execution-metadata.json): exact executable/argv, cwd, environment override, protocol/runner identity, start/end, attempt count, exit status, runtime and output hashes.
- [execution.log](../../data/anatomical-arm-v1/review/source-ce-series-initialization/execution.log): raw combined stdout/stderr, 0 bytes. It is empty because the successful runner writes its receipt directly; SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

The sole qualifier invocation used `OPENBLAS_NUM_THREADS=1`, `--qualify --protocol-commit a0456a4fad7041cb71f3841888445a9f8f80e22b` and `--output education/data/anatomical-arm-v1/review/source-ce-series-initialization/summary.json`, at the exact Python executable recorded in the metadata. Start `2026-10-06T08:36:27.683105+00:00`; end `2026-10-06T08:36:29.725380+00:00`; elapsed `2039920323` nanoseconds (**2.039920323 s**); exit code **0**. There was **one attempt**, with no retry or settings change. Computation used 60 decimal digits; stored numerical fields use 55 significant decimal digits. All tables below are read-only transcriptions of the retained receipt, rounded for readability.

## Held stationary CE states

The independent stationary construction stays on `[-3,3]`, with source-informed conserved `M=1−B`, held N and overlap one. The original publication rates and calcium formula follow the [design](source-ce-series-initialization-design.md) and [visually verified original tables](original-plos-table-visual-audit.md), from [van der Zee et al. (2026)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748). This fixture combines the declared conserved-population convention with the article's raw CE force `Q/beta`; it is not a claim of exact publication/source-code trajectory parity.

| Condition | Held N | Attached B | Force moment Q | Raw CE Q/beta |
|---|---:|---:|---:|---:|
| pCa_4.5 | 0.999987435748 | 0.499346108624 | 0.494170041176 | 0.988340082352 |
| pCa_6.1 | 0.466007594329 | 0.275312890136 | 0.272459081797 | 0.544918163594 |
| N1_normalization_audit | 1.0 | 0.499350293102 | 0.494174182279 | 0.988348364557 |

pCa 4.5 retains its converted capacity **0.999987435748**, rather than replacing it with N=1. The separate N=1 audit gives raw CE force **0.988348364557**, without normalizing the baseline to one. The common force-moment variance is approximately **0.0829811385122**, positive in all three conditions. Strict population admission succeeded without clipping or resetting.

Maximum stationary population-balance residual: **4.66726145840e-61**; maximum independently integrated attached-mass residual: **4.66726145840e-61**. The largest sampled kinetic reaction residual was **3.48488855560e-59**, evaluated at the declared 129 positions per condition. Each is below the unchanged absolute gate `1e-12`; the sampled reaction check does not prove a continuum supremum.

## Coherent series initialization and fast tangent checks

Each stationary condition was combined with the three authored kappa values `0,.002,.02` and three authored PE offsets `−10,0,+10`, for nine cases per condition. All use the CE reference coordinate zero; total force is raw CE plus PE, and SE extension is obtained by the exact inverse exponential law. There is no settling interval or passive-force subtraction.

| Condition | Normalized total force range | Normalized SE extension range | Fast whole-series tangent range |
|---|---:|---:|---:|
| pCa_4.5 | 0.988340082352–1.18834099033 | 7.60349143784–8.25671584113 | 0.220392614093–0.249712240405 |
| pCa_6.1 | 0.544918163594–0.744919071572 | 5.63639616169–6.63931624547 | 0.133588380706–0.161051900064 |
| N1_normalization_audit | 0.988348364557–1.18834927253 | 7.60352072401–8.25674087781 | 0.220394228886–0.249713875950 |

The fast CE, parallel and whole-series tangents are specifically **full-support, held-population rigid moment probes with no outflow**, using `Q±B*h`. They are not derivatives of finite-domain clipped transport. The [continuous reference's escaped mass/moment ledgers](continuous-strain-ce-protocol.md) govern finite-domain jumps separately.

Maximum force-balance error was **1.75022304690e-61**, below the fixed absolute `1e-12` gate. The maximum SE inverse round-trip error across all 27 initialized cases was **0.0**. Centered finite differences used the fixed step `1e-15`. Maximum derivative errors were:

| Check | Maximum error | Fixed gate |
|---|---:|---:|
| PE tangent | 1.66643968419e-31 | `1e-8` |
| SE tangent | 9.60000000000e-33 | `1e-8` |
| Rigid CE+PE parallel tangent | 2.74788024713e-37 | `1e-8` |

For a zero analytic derivative, the retained check uses absolute error; otherwise it uses relative error, as predeclared.

## Fixed inverse boundaries and invalid-input probes

All four SE boundary probes preserve input, inverse, result and error:

| Input normalized force | Inverse normalized extension | Result normalized force | Absolute round-trip error |
|---:|---:|---:|---:|
| 0.0 | 0.0 | 0.0 | 0.0 |
| 1.0e-20 | 2.19298245614e-19 | 1.0e-20 | 1.05421979432e-81 |
| 1.0 | 7.64451880810 | 1.0 | 0.0 |
| 100.0 | 26.1158316254 | 100.0 | 0.0 |

All **56** declared invalid-input probes produced an explicit rejection: four population-domain probes, 22 parameter probes, six domain probes and 24 nonfinite scalar-input probes. Their input values and exception reasons are preserved individually in the receipt. The admissible kappa-zero cases are included in the successful initializer matrix; sigma/rho/beta must remain positive. No additional failure-injection or dynamic experiment was run in this packet.

## Bounded interpretation and remaining prerequisites

These results qualify algebra and admission behavior for the declared normalized source-informed law. PE kappa's mapping to the published Eq19 force prefactor remains unresolved because the original table displays a stiffness unit. Every numeric kappa and offset in this packet is an **authored mathematical probe**, including `.002`; none is an inferred source calibration or physical uncertainty interval. SE `.19/.24` remains conditional on the normalized stroke-coordinate interpretation specified in the design.

Physical F0, gamma, specimen area and absolute CE/PE/SE reference lengths remain symbolic and unselected. Positive instantaneous tangents under this rigid-moment convention establish neither a relaxed descending force-length path nor stability under dead loading. A coupled series trajectory or release requires a separate reviewed, committed protocol; a physical/continuum use also requires the unresolved force, coordinate, area and slack-length mappings in the [calibration reconciliation](calibration-source-reconciliation.md). The present results do not close those gates.
