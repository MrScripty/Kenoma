# Retained fixed-field integration evidence

Result: **UNRESOLVED_FIXED_PATCH_INTEGRATION**, all8,847,360 declared callbacks completed once. See [outcome](../../research/fixed-field-integration-outcome-20261007.md), [protocol](../../research/fixed-field-integration-protocol-20261007.md) and [runtime source/authorization](../../research/fixed-field-integration-run-20261007.md).

- `completion-receipt.json`: source/preflight identities, counters, resource observations, output hashes and failed comparisons. An `incomplete-receipt.json`, if present, would override it; none was produced.
- `execution-receipt.json`, `execute.log`: external single-invocation timing/exit and final post-write runtime check.
- `saved-arrays.json`: exact two positions, terminal virtual direction, free/held order and complete patch.
- `U3/U4/U5/D4/D5-<state>-assembly.json`: full585-node component/total gradients, patch gradients, energies, directional derivatives, and references to retained element-local records. States are `control45` and `terminal46`.
- `<recipe>-<state>-element-<id>-local.json`: ten-node component/total gradients, energies, count and minimum sampled J. No new field is encoded.
- `<recipe>-normalized-points.f64le`: records of five little-endian Float64 values `(L0,L1,L2,L3,normalizedWeight)`, in the exact recipe enumeration order.
- `<recipe>-element-<id>-reference-weights.f64le`: one positive physical reference weight in m³ per normalized point, same order. U3 covers252 elements; each replacement rule covers16. Weights are retained once and checked identical across states. Their source recipe/reference mesh is immutable.
- `full-vector-comparisons.json`: all component differences and independent vector/work gates, including informational U3→U4 comparisons.
- `own-verification.json`: producer's hash/arithmetic/scatter check; does not imply independent acceptance.

All links and payloads are repository-relative. No hosted publication or anatomical/global-equilibrium qualification is claimed. Binary point coordinates/weights are reproducible binary64 values, not exact irrational Gauss constants. Recheck arithmetic without material calls with `python3 education/tools/verify-fixed-field-integration.py` from repository root.
