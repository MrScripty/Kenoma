# Selective whole-patch finite-integration proposal

**Proposal only: no runner implementation or material execution is authorized.**
Retain both frozen fields, terminal virtual direction, material/activation,
all 585 nodes and every patch element:
`195,196,197,198,199,200,202,203,206,237,240,243,244,246,247,248`.
The 236 outside elements retain their exact U3 contributions. No optimizer,
refit, new field, publication or anatomical claim is included.

## Why target seven elements

The [retained-only analysis](fixed-patch-selective-proposal-20261007-analysis.json)
shows that the 15 elements other than247 already have small D4/D5 differences:
worst total element-triangle bounds6.498455462633501e-8N (control) and
2.874429978483306e-7N (terminal). Their terminal U5/D5 signed difference is
7.622816703189983e-6N, but the cancellation-resistant element triangle is
1.6338786164471486e-5N. Thus neither deleting247 nor replacing a failing
triangle with a signed maximum is sufficient. These new arithmetic summaries
are producer-derived proposal evidence, not an independently checked preflight. Its151 consumed input blobs match the exact
recovery snapshot, with no new material calls or quadrature generation.

All six secondary elements stay explicit. Terminal total local differences:

| Element | U4/U5 (N) | D4/D5 (N) | U5/D5 (N) |
| --- | ---: | ---: | ---: |
|197|2.631870763e-05|4.199064918e-08|2.517083662e-06|
|200|1.937610536e-05|2.304121338e-08|1.797754537e-06|
|203|5.765241941e-05|8.642971139e-08|5.894572467e-06|
|206|7.659505061e-05|1.590732310e-07|6.976407168e-06|
|246|4.575791007e-05|7.386542400e-08|5.042914303e-06|
|248|1.289212730e-05|2.039934799e-08|1.824640080e-06|

The remaining nine are195/196/198/199/202/237/240/243/244. Retained D4/D5
and U5/D5 independently cover their complete tetrahedra at both fields. Their
worst total cross-family triangles are1.193659700748917e-6N (control) and
7.558982249022961e-7N (terminal), leaving substantial room within the unchanged
patch gate. Reuse those independent results; do not reevaluate all 16 uniformly.

## Smallest defensible first schedule

Use the accepted positive Gauss 5 dyadic-shell family, without changing the law
or reference-weight convention `normalizedWeight*det(referenceJacobian)/6`.
For each secondary element, center the complete shell chart at its local
node 92 index:197/200→3,203→2,206→1,246/248→0. Permute barycentric coordinates
and polynomial moments consistently; the opposite face uses ascending local
indices. This is a coverage chart, not a claim that secondary error is singular
there. Every rule includes all shells and the corner core.

Secondary C55/A55 use depth 20, Gauss 5 in all coordinates, one radial part,
and respectively1/2 angular parts on each angular axis (2625/10500 points).
For 247, F44 extends the demonstrated s1/s2 angular4 resolution through **all**
21 regions:depth 20, radial1, angular4, face123,42000 points. R44 changes only
radial parts to2 (84000 points). X44 uses depth 22/angular4/radial1/face231
(46000 points); it is a deliberately coupled depth/chart cross-check.

Three complete patch candidates, at **each** retained field:

| Candidate | Quiet nine | Secondary six |247|
| --- | --- | --- | --- |
|Q0 lower|retained D4|new C55|retained A55|
|Q1 primary|retained D5|new A55|F44|
|Q2 independent cross-check|retained U5|retained D5|X44|

Require Q0→Q1 and Q1↔Q2 agreement. Both comparisons independently sample every
element;247's tail is newly angular-refined and its cross-check independently
samples all regions. Q0↔Q2 remains informational. Also require isolated247
F44/R44 agreement at the **same angular resolution**; the other 15 contributions
cancel in that isolated check and cannot acquire new qualification from it.
Retain all old comparisons, including the failed U4/U5 and247 C55/A55 results.
This is a new finite protocol, not a passing reinterpretation of those failures.

For terminal F44 only, reuse the 4000 accepted retained s1/s2 measurements from
the incomplete run. Evaluate its19 tails anew (38000 callbacks); evaluate all
42000 control points. Reuse numerical values with exact hashes and explicit
old provenance; never relabel the historical exit1 as operational completion.
If reuse fails hash/schema/field/law checks, stop rather than spend replacement
calls or change the schedule. Convergence is unknown; this is a plausible first
candidate, not proof of a globally minimal or convergent schedule.

## Unchanged gates and cancellation protection

For matrix, volume, passive fiber, active potential and independently assembled
total, require all 585×3 signed differences≤1e-5N and saved-direction work
differences≤5.492029235357012e-7J at both fields. Keep stationarity1e-4N,
component reconstruction1e-8N/1e-9J and held direction exactly zero.

Also apply the same force/work limits to sums of absolute comparison-unit
differences after scatter. Q0/Q1 units are nine whole elements plus the 21
shell bins for each of the six secondary elements and 247. Q1/Q2 units are
15 whole elements plus247's21 bins: retained D5 does not contain shell-resolved
stress contributions, so never invent a shell partition for that cross-check.
For depth 22, retain all23 original regions before grouping the final three
into the shared depth 20 core bin. The isolated radial test uses247's21 bins.
These guards prevent cross-element/region cancellation; cancellation within a
unit remains possible. Work bounds follow algebraically from force/direction
bounds and are not an independent integration-error certificate.

Form each full hybrid as retained U3 baseline minus its old complete16-element
patch plus the candidate patch. Retain local/patch/full vectors, energies,
all 585-node scatters and reaction entries; count each shared-node contribution
once. Hash and independently replay the common retained baseline before reuse.
No physical external-potential term, held trace or material parameter changes.

## Cost before implementation

| New work, both fields | New callbacks |
| --- | ---: |
|Secondary six C55|31500|
|Secondary six A55|126000|
|247 F44 (4000 terminal values reused)|80000|
|247 R44|168000|
|247 X44|92000|
|**Exact planned and maximum new callbacks**|**497500**|

This is94.4% fewer than the original8847360-call uniform schedule.
No236-element baseline recomputation is needed. Historical rates extrapolate
to 14.02 s (large full-patch run),75.25s (whole-shell run), or135.02s (small
changed-shell batch including its overhead). Plan20–180s including preparation
and writes, with a proposed300s external wall ceiling; these are estimates,
not guarantees or a new benchmark. One eventual invocation, no retries or
automatic refinement; an exhausted budget remains incomplete/unresolved.

Retaining physical weights once per element/rule costs2006000 bytes. Actual
normalized `(L0,L1,L2,L3,weight,r)` arrays, including the four distinct secondary
corner permutations, cost10776000 bytes. With634 logical shell records,
scatters/comparisons/provenance, plan20–32MiB of **new** artifacts, a64MiB output
ceiling,1GiB Node heap and2GiB RSS. Existing immutable payloads are referenced,
not copied into the new budget. Stream one element/region at a time. Freeze
storage schemas and count their worst-case size during structural preflight.

## Required preflight and later disposition

After design review, independently replay the reused full-patch/shell
arithmetic and hashes, implement only the agreed structural/runner scope,
then freeze its recipe/permutation, source inventory and budget. Independently
review structural preflight before any execution authorization. It uses no
specimen callbacks:
whole-field/cap/J certificates, positive reference weights, complete disjoint
shell/core coverage, independent rational moments (degree 5 normalized and
degree 2 physical barycentric), exact count/scatter/reuse checks, and byte-bound
point inventories. Include the corrected **nonzero producer→serialized JSON→
constructor** fixture for all six corner mappings,247 and composite patches;
damage missing/conflicting identity, region/element omission, held-node vectors,
false cancellation/pass flags, weights and resource receipts.

Future operational completion means exactly 497500 newly reserved/entered/
completed callbacks, accepted child/worker/public-entry exit0 and durable
terminal/resource receipts with no incomplete override. Count the 4000 reused
measurements separately. Finite-rule agreement is a separate result:
`PASS_BOUNDED_SELECTIVE_FIXED_PATCH_AGREEMENT` only if every required comparison
and invariant passes; otherwise `UNRESOLVED_FIXED_PATCH_INTEGRATION`. A completed
operation may still fail agreement. This proposal authorizes neither operation.

Finite comparisons provide no analytic quadrature error bound, continuum,
equilibrium, tangent, displacement or anatomical validation. Depth/chart
sensitivity remains coupled. The 236 unchanged elements remain unqualified.
The original failures and consumed authorization remain unchanged even if a
future new protocol passes.

## Exact retained anchors

- Full-patch raw result:`74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b`, executed
  `ef39f8335486b5cd7c9954361da181f46ea21c80`.
- Whole247 shell result:`4b83ec5dfebae73b08c3f964aa910f65e02458e0`, executed
  `07aafe8b1c1ef27d212434232f4546feb27449ac`.
- Failed two-shell evidence:`9c9edbc9f3dd9729f2becc5215054897d139735e`, executed
  `97da4bdea7d0be11fc18222221b8b551b53a8e3b`, exits1; authorization consumed.
- Accepted offline recovery:`f7cc2c0f10b536e94557ce978aa1691d6c92246f`, reviewed
  source`1671433376014ad148799e1ad7ff3f10219643f7`; artifact SHA-256
  `3efbc3f28b648cf7d5b0f152b865f13aae7ccc89fd752af58d0e35d92da103a6`.

The [analysis source](fixed-patch-selective-proposal-20261007-analysis.py) reads
retained JSON only; its output binds each consumed path, byte count and SHA-256
to the immutable recovery anchor. Both field identities, direction and original
law remain those in the [original protocol](fixed-field-integration-protocol-20261007.md).
Local proposal branch only; no existing branch, main, book, PR or deployment
changes, and no environment protection or credential changes.

Proposal arithmetic reproduction (not a specimen run):

```sh
PYTHONDONTWRITEBYTECODE=1 python education/research/fixed-patch-selective-proposal-20261007-analysis.py > /tmp/fixed-patch-proposal-analysis.json
```
