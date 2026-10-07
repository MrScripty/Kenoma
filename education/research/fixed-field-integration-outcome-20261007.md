# Fixed-field cap-patch integration remains unresolved

The one authorized invocation completed all declared stages and refused qualification: **`UNRESOLVED_FIXED_PATCH_INTEGRATION`**. This is a failed integration-agreement result, not a resource failure, new equilibrium or accepted model correction. No retry or further experiment was run.

## Immutable source and execution

Ancestry: reviewed protocol/evidence `da435ea4595b4f1cb23ab1a0815f21574288d41a` → runner source `15e224ed603a66fa2acd63a1b758638104b7b271` → runtime-preflight/executed head **`ef39f8335486b5cd7c9954361da181f46ea21c80`**. Source was frozen and preflight evidence pushed before the invocation.

Runtime preflight passed17 tests and98 source hashes, with zero specimen constitutive calls. Its SHA-256 is `8de8f9b1f6168985ab5087ffc9449bb3c4c33fff87366aacef2e9f1b3a1acf88`. The command was exactly:

```sh
node --max-old-space-size=6144 education/tools/run-fixed-field-integration.mjs --execute
```

The external invocation receipt records one launch, 2026-10-07T01:19:40.961247Z to01:23:50.323919Z, exit0 and249.363084s. The authoritative numerical receipt reports exactly **8,847,360 reservations, actual constitutive callbacks and successfully returned callbacks**. No spare9-million-ceiling allowance was consumed. The post-final-write check completed at249.237726s of Node uptime, within900s; peak sampled RSS was385,560,576 bytes (367.699MiB), within8GiB. Runtime output storage was49,624,403 bytes, within256MiB. No wall/RSS/storage/domain/count refusal or incomplete receipt occurred.

The unchanged two saved valid fields, terminal virtual direction, material/activation and16-element patch identities are those in the [reviewed protocol](fixed-field-integration-protocol-20261007.md). All236 other elements retained the bit-identical U3 assembly. No new physical field, mode, material parameter, optimizer, fit or external potential was introduced. The structural exact whole-element domain checks and U3 gradient/energy replay passed. Complete normalized rules, physical weights, local/scattered component vectors, independently assembled total and pairwise full differences are retained.

## Fixed criteria and failed comparisons

All585 nodes, including held reactions, were compared component by component. Integration budgets remained **10⁻⁵N** for vector infinity differences and **5.492029235357012×10⁻⁷J** for work along the unchanged terminal nodal direction. The original physical stationarity gate remains10⁻⁴N. No tolerance was changed during execution.

| Field | Required comparison | Total vector difference, N | Total directional-work difference, J | Fixed criteria |
|---|---|---:|---:|---|
| Control45 | U4→U5 | 4.265416846e-5 | 1.321931842e-9 | Force fails |
| Control45 | D4→D5 | 4.523190533e-8 | 1.587674436e-12 | All components pass |
| Control45 | U5↔D5 | 4.105293874e-6 | 1.039263120e-10 | All components pass |
| Terminal46 | U4→U5 | **0.1428391647** | **1.065601907e-5** | Force and work fail |
| Terminal46 | D4→D5 | **0.0843283220** | **6.207604186e-6** | Force and work fail |
| Terminal46 | U5↔D5 | **0.0239239038** | **1.720190660e-6** | Force and work fail |

Control U4→U5 fails volume and total force; its work criterion passes. At the terminal field every required comparison fails matrix, volume and total force. Matrix work differences remain below the budget, while volume and total work fail. Passive-fibre and active-potential components pass both criteria for every required pair. These are integration comparisons at fixed fields, not diagnoses of a constitutive cause or errors measured relative to a known exact integral.

The terminal total-vector maximum difference is consistently at node505, component1 (reference coordinate index y). For U4→U5 it comprises approximately0.1416573N of volume and0.0011819N of matrix difference. The finest-family cross-comparison still exceeds the force budget by2,392 times and the work budget by3.13 times. The control's U4→U5 failure prevents calling even that complete bounded sequence qualified, despite agreement of its final cross-family pair.

Scalar whole-vector maxima alone conceal these differences: the held-node-dominated full nodal maximum is59.9848000043N for every terminal rule. It does not imply unchanged full vectors. Energy is also insufficient: U5↔D5 terminal volume energies differ by only about6.67e-9J while the corresponding total force vector differs by0.02392N. This run retained the actual vectors and work checks rather than drawing an accuracy conclusion from either scalar diagnostic.

## Evidence and review limits

The [raw completion receipt](../review/fixed-field-integration-run-20261007/completion-receipt.json) binds100 source/preflight hashes and966 output hashes. The [full comparisons](../review/fixed-field-integration-run-20261007/full-vector-comparisons.json) retain every component difference entry. [Own verification](../review/fixed-field-integration-run-20261007/own-verification.json) reproduced those hashes, force differences, directional work, pass/fail arithmetic and all local-to-nodal scatters, with **zero constitutive calls**. This was the producing agent's check, not independent reviewer acceptance. The [arithmetic verifier](../tools/verify-fixed-field-integration.py) allows that check to be repeated without an assembly.

The previous full50.6MB raw geometry run and55 additional material-gate certificates still lack independently replayed coverage as recorded in the prior diagnostic. Hashing those old files here does not change that limit. The new retained force/weight evidence awaits independent review.

There is no evidence here qualifying global integration over the236 unchanged elements, continuum convergence, equilibrium, displacement resolution, tangent correctness or anatomy. The entire selected patch was refined, including the previously coarse regions, and still fails the preregistered finite comparisons. A new integration protocol would need separate review and authorization; no displacement sequence, arbitrary bulk increase, selected pressure formulation or stress refit is justified by this unresolved result. Main, previous branches, book artifacts, PRs, protections, credentials and deployment were untouched.
