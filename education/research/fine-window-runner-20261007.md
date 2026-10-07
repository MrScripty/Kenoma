# Fine-window runner preparation and structural preflight

Parent accepted preparation of the independently reviewed
[exact schedule](selective-fine-window-schedule-20261007.md), with **new** declared
budgets:19716000 planned/max new callbacks,512MiB output,7200s public-entry wall,
1GiB Node heap and2GiB RSS, one eventual invocation. These are not unchanged
limits from the consumed497500-call/300s/64MiB authorization.

Preparation authorizes implementation and geometry/structural/synthetic checks
only. **ZERO specimen/material-law calls.** No new execution authorization or
specimen run directory is created; the new launcher refuses both absent new
authorization and an old consumed scope. Future execution needs separate parent
acceptance bound to frozen source, preflight and independent structural review.

Source base `a20edf84cb3800b30d83dda3f419e3696a69da8d`; reviewed schedule freeze
`3f2f7b96dade17bacf5909dbd602e74b34f6b863`; original completed result
`38ae8a2e2af57cf33254af987b724824b9d84357` stays unresolved with Q0/Q1 and all
historical failures unchanged. No physical law, material parameter, fixed
field, cap trace, direction, reference weight or gate is changed.

## Implemented geometry and complete comparisons

The sensitive7 use primary angular2/4/8 with depth20/radial1/ascending chart.
Independent I0/I1 triangulate the opposite face at4/8 and split dyadic shell
radial intervals1/2, respectively. Exact integer reference-coordinate
determinants avoid tiny-core subtraction error. Lexicographic face-grid
ordering, three oriented subtetrahedra per homothetic frustum and core cones
are frozen. Exact mesh topology checks require paired oppositely oriented
interior faces, no exposed interior face, positive determinants, exact region
volumes and complete reference boundary. Gauss5 Duffy uses weighted degrees
7/6/5 for total barycentric degree5, within degree9 Gaussian exactness.
Preflight tests the actual arrays against independent rational normalized
degree5 moments and reference physical degree2 moments, with the unchanged
2e-11/2e-10 relative tolerances, every actual corner/chart and every region.

P4/P8, I0/I1, radialR4, isolated depthH4 and isolated chartC4 stay distinct.
H4 shared20shells reference earlier accepted P4 receipts (secondary6) or exact
old F44 (247). C4's247 shared20shells reference exact old X44 at chart231.
Shared identity earns no new refinement evidence. No value reuse across
elements and no missing-reuse replacement callbacks. The normalized arrays
can be shared across elements with identical reference charts; their physical
weights and new stress values remain element-specific.

All2002 logical region records survive:1682 new evaluated rows,320 explicit
shared references,94 complete stages,16 complete16-element hybrids and24
comparisons (14 required primary/independent/axis,6 required quiet witnesses,
4 predeclared informational cross-checks). Every field/component comparison
uses all585 nodes including held reactions and the matched156-unit partition.
Original23 H4 regions remain recorded before its last3 are grouped into the
common depth20 core. Common16 diagnostics are labeled supplementary.

Quiet9 repeated D5 values earn no new evidence. Their retained D4/D5, U4/U5
and D5/U5 witnesses remain separately required and attributed. Finest S2/I1
uses different D5/U5 quiet sampling. Signed/unit-triangle force/work global
gates are1e-5N/5.492029235357012e-7J for all5 terms/both fields. Prospective
subset allocations sum to those same global gates: independent increment
quiet85%/sensitive15%, other checks quiet20%/sensitive80%. Actual shared-node
scatter also must pass. Reconstruction1e-8N/1e-9J and stationarity1e-4N remain
unchanged and separate; no physical stationarity is claimed.

## Streaming serialization, counters and terminal semantics

Closed normal output inventory:3116 files, including454 normalized binary
arrays,841 physical-weight arrays,1682 new region JSON rows and all stage/
hybrid/comparison/source records. Binary payload345840000B. Bounded slots
8192B/region,131072B/stage,1048576B/hybrid,2097152B/comparison,1MiB start and
completion,2MiB provenance,131072B saved arrays,16384B terminal, ten64KiB
external/log slots and4MiB emergency reserve yield **448240000B** maximum,
below536870912B. Finite compact JSON limits depth32, strings512B, keys256B and
4096 entries; actual encoded bytes are checked before exclusive durable writes.
Worst numeric serialization fills variable numeric fields with the longest
finite binary64 values; immutable saved arrays/provenance use their actual
hash-bound bytes. Per-file caps refuse oversize instead of raising budgets.

One region at a time: maximum48000 points,2304000B normalized buffer and
384000B physical weights. Current complete/partial weights fit512KiB emergency
slots, including a truncated normal write. No whole point inventory is held
in memory. Runtime checks wall/RSS during callbacks and complete combined
output after durable writes. External watchdog/supervisor track the complete
public-entry clock, child RSS, combined bytes, private child/log cap, process
cleanup and actual child/worker/public exit. Accepted helpers receive the new
exact budget rather than altering their historical defaults.

Exactly19716000 unique new callbacks must be reserved, entered and completed.
The480000 same-invocation P4 values reused by H4 are counted at P4 only;80000
F44 and80000 X44 historical values incur no new callback. Stage logical points
and shared references are distinct from callback counters. No retries,
substitution, optimization/refit, new fields or automatic refinement.

Any callback, cap/J, identity, reconstruction, encoding, write, wall/RSS/storage,
postwrite, process-exit or terminal failure remains incomplete and dominates
provisional numerical success. Durable partial/current weights and counts are
retained, with forced termination limited to already-durable files. A complete
operation may still be numerically unresolved. A passing future result is
`PASS_BOUNDED_FINE_WINDOW_FIXED_PATCH_AGREEMENT` for this new protocol only.

## Reproduce structural preparation only

```sh
node --max-old-space-size=1024 education/tools/preflight-fine-window.mjs --output /tmp/kenoma-fine-preflight-FRESH
```

This command imports no call to the specimen evaluator. It generates actual
geometry, weights, exact/moment certificates, a complete nonzero synthetic
producer→boundedJSON→constructor→independent scalar verifier fixture, and
damage tests. The fixture archive references actual preflight binary hashes;
its constant stresses are explicitly synthetic and are not a specimen result.
New launcher refusal and accepted supervisor lifetime tests exercise terminal
failure priority and process cleanup. Frozen source/artifact hashes are required
again before any future accepted operation.

Independent geometry design review found exact topology and moment agreement;
it is not implementation acceptance. Actual source/preflight and their resource/
serialization/receipt paths require independent structural review before asking
for execution. No new scientific comparison is added beyond the accepted
schedule and its supplemental common16/quiet diagnostics.

Outside236 oldU3 elements remain unqualified. Even a future16-patch pass is
bounded finite integration agreement, not analytic convergence, whole-body
integration, equilibrium, tangent, displacement or anatomical acceptance.
Everything stays local; book/main/release/deployment/protections/credentials
are untouched. Repository-local author: MrScripty <TheEnvironmentGuy@protonmail.com>.
