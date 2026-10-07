# Bounded fixed-field integration qualification protocol

Freeze from `3b5a091872e9fa2195a5aa06a9da60a33eab21d6`, retaining diagnostic evidence `19009142398ba6c0b7665fedb35e5398207eadb6`. This authorizes protocol and structural preflight only. **Do not execute material assembly until separately reviewed and authorized.** No optimizer, displacement enrichment, state advancement, constitutive change, bulk increase, stress fit, PR, publication or deployment is included. Prior source-bound failures and independent review limits remain unchanged.

## Exact states, direction and scope

Use FJ1486's existing P2 mesh, 585 nodes, 252 elements, 90 held and 495 free nodes, activation1 and historical material parameters. Read exact binary64 arrays from the frozen geometry result: control45 (`45-mode-control`, iteration1) and terminal (`46-mode-response`, iteration13). Their JSON-array SHA-256 identities are respectively `07e50e29f34c3f6880f3895bb63c3a53dd18afee90217b6816099681e2c8132e` and `655eb058007d2432689257b0bbe84f9b054500587672b087b03dbecf0bdfc410`.

Use only the saved terminal iteration13 `scaledNodalIncrementM`. Its identity is `bb8bc986540e2e3e098969db2b34b3682f55602d868c9972e35b42464972cdab`, maximum nodal norm0.0002m, L1 norm0.05492029235357011m. It is a virtual direction at **both** saved fields, never an applied increment. All held entries are exactly zero. Do not replace it with the older selected enrichment direction or generate a new Newton direction.

Before any constitutive callback, check saved hashes, finite dimensions, exact cap traces and certify each unchanged self-state against the exact whole-element `J>binary64(1e-6)` gate. No rejected-state material call is allowed. Source and reference geometry hashes, material JSON and all old evidence are bound in [the input manifest](fixed-field-integration-protocol-20261007-inputs.json).

The replacement patch is **every element incident to node92**, in source order:

`195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248`.

Each new rule covers the complete reference tetrahedron of all16 elements, including formerly coarse regions. The236 other elements retain their exact original2048 rule. Reassemble that common baseline once per field, retain baseline patch contributions, and form each comparison as `baseline − originalPatch + newPatch`, separately for all four energy/stress terms and independently evaluated total stress. Shared-node contributions add once per element; caps remain in the full vectors. Nonzero patch contribution outside its nodal support is refused. Do not edit the original assembly or substitute an old scalar maximum for its vector.

## Frozen recipes, finite schedule and resources

The [structural helper](../tools/fixed-field-integration-protocol.mjs) defines exact binary64 constants, child vertex ordering and deterministic enumeration. U3 calls the original `furtherQuadrature()` verbatim, preserving binary64 point coordinates and order exactly. U4/U5 use the same eight-child midpoint tetrahedral subdivision and positive symmetric four-point family at depths4/5. Normalized weights are `8^(−depth)/4`; physical reference weights are `weight × det(referenceJacobian)/6`.

D4/D5 cover **all depth3 cells**, with positive tensor Gauss–Legendre rules of order4/5 on `[0,1]³`. Their local barycentrics are `((1−r)(1−s)(1−t), r, (1−r)s, (1−r)(1−s)t)`, mapped by the cell vertices. Normalized weight is `cellWeight × 6 w_r w_s w_t (1−r)²(1−s)`. They change the points and integration family; they are not merely deeper sampling of one corner. These finite rules are not an analytic error bound for the nonlinear integrand.

| Stage | Covered elements per field | Points/element | Material calls, both fields |
|---|---:|---:|---:|
| U3 baseline | 252 | 2,048 | 1,032,192 |
| U4 | 16 | 16,384 | 524,288 |
| U5 | 16 | 131,072 | 4,194,304 |
| D4 | 16 | 32,768 | 1,048,576 |
| D5 | 16 | 64,000 | 2,048,000 |
| **Declared total** | | | **8,847,360** |

One invocation, no retries, no additional fields/probes/rules. Ceiling **9,000,000 constitutive point calls**, **900s wall time**, Node heap**6,144MiB**, process RSS**8GiB**, output storage**256MiB**. Stream one element at a time; never retain all physical-point operators in memory. Reserve each element's calls and check time before its batch; monitor RSS and storage between batches, retaining partial records on refusal. The spare152,640 calls do not authorize extra work. Abort on nonfinite values, guard/source/hash failure, resource exhaustion or unexpected callback failure; do not catch a failure and retry under a looser criterion.

The previous diagnostic timestamps show516,096 calls in9.366/9.400s, and262,144 patch calls in5.801/5.915s: roughly18–23μs/call including its assembly work. The new declared calls extrapolate to about160–200s plus preparation, exact gates and output;900s is a finite allowance, not a performance guarantee. The preflight does not benchmark or execute constitutive assembly.

## Force and directional-derivative criteria

The historical physical stationarity gate remains **10⁻⁴N**. Integration agreement receives a stricter fixed budget **10⁻⁵N** (one tenth of that gate), without changing any physical or solver tolerance. For every field and each of `matrix`, `volume`, `passiveFiber`, `activePotential`, and the independently assembled total, compare **all585×3 nodal entries**, including reactions:

\[
\|g_B-g_A\|_\infty\le10^{-5}\;\mathrm N,
\qquad |g_B\cdot\delta u-g_A\cdot\delta u|
\le10^{-5}\|\delta u\|_1
=5.492029235357012\times10^{-7}\;\mathrm J.
\]

Both checks must pass; no percentage normalization or cancellation between terms. Required comparisons are **U4→U5**, **D4→D5**, and **U5↔D5**. U3→U4 and every difference from baseline are also retained, without requiring the intentionally coarse baseline to qualify. Confirm constituent sum versus directly evaluated total within10⁻⁸N and10⁻⁹J; replay the original U3 full-free gradient within10⁻⁸N and component energies within10⁻⁹J. These are reproduction/roundoff checks, not looser integration criteria.

These comparisons assess the bounded **patch** integral: unchanged outside contributions cancel between rules. Even a pass cannot qualify the236 unrefined elements, continuum convergence, equilibrium, a tangent or anatomical validity. Use `PASS_BOUNDED_FIXED_PATCH_AGREEMENT` only if every comparison and invariant passes; otherwise use `UNRESOLVED_FIXED_PATCH_INTEGRATION`, with offending components/entries and partial-stage status. Exhausted budgets are unresolved evidence. The current0.142800N difference between successive refined scalar maxima and140.500N omitted force remain historical unconverged diagnostics, not converged equilibrium errors.

## Required retained evidence for a future authorized run

- Exact source/head/input hashes, commands, start/stop times, resource measurements, actual call counters, domain certificates and refusal reason.
- The two full saved position arrays and terminal virtual-direction array (or exact immutable source pointers plus matching extracted-array hashes), material parameters and node/free/held orders.
- Common normalized point rules and physical reference weights, point counts and recipe identities. Store deterministic normalized `(L0,L1,L2,L3,weight)` arrays as little-endian Float64 and per-element physical weights in the same point order, with SHA-256, byte counts and schemas. Reference weights are state-independent: retain once per recipe/element, not twice. The planned physical-weight payload is35,389,440 bytes; common rules add9,850,880 bytes. Do not claim mathematical irrational Gauss constants are exact real values; these are reproducible binary64 recipes.
- For every stage/field: full nodal component vectors, independently assembled total, baseline/old/new patch vectors, component energies and saved-direction derivatives. Preserve all585 nodes, not only free maxima; retain per-element local ten-node contributions and energies to audit scatter/replacement and patch support.
- Full-vector differences for every required pair, maximum entry coordinates/component, free/held subsets, cap resultants, derivatives, all fixed criteria and disposition. Force gradients are N; internal physical forces have opposite sign. Derivatives are J. The isolated external potential remains zero.

Any later displacement sequence, stationarity or tangent experiment needs a new frozen protocol after review of these integration records. No material choice or stress refit follows from a finite patch-agreement result alone.

## Structural preflight only

The preflight verifies hashes, state/direction identities, whole-field geometry, material provenance, complete patch membership, recipes/positive weights/moments, counts/budgets and reference-domain validity. Synthetic tests damage geometry/caps/state, recipes, patch membership/support, vectors, equal maxima with cancellation, and budgets. They test bookkeeping and refusal before callbacks; they do not evaluate muscle material or produce new physical fields.

Freeze source first, then run:

```sh
node --test education/tests/fixed_field_integration_protocol.test.mjs
node education/tools/preflight-fixed-field-integration.mjs
```

No expensive runner or `--execute` action is supplied on this branch. The source-bound structural receipt must be independently reviewed together with this protocol before implementation or authorization of the assembly.
