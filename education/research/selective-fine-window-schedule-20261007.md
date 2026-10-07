# Prospective targeted fine-window schedule

**Cost/scope proposal only. No implementation, quadrature generation, new
material calls, execution authorization or publication.** Base review commit:
`6759c66d2269bd0b2159ddce564014590b4a8320`. The completed result
`38ae8a2e2af57cf33254af987b724824b9d84357` remains
`UNRESOLVED_FIXED_PATCH_INTEGRATION`; its Q0/Q1 failures and every gate stay
unchanged. This is a proposed new finite protocol, governed by the
[accepted prospective criterion](selective-fixed-patch-fine-window-criterion-20261007.md),
not a reinterpretation of the old protocol.

The [frozen cost/scope manifest](selective-fine-window-schedule-20261007.json)
and [exact reuse index](../review/selective-fine-window-schedule-20261007/reuse-index.json)
are the review inputs. Freeze them before independent scientific review.
No runner or generator is added. No old authorization is edited or reused.

## Complete candidates and priority

Keep the same control45/terminal46 coordinates, terminal direction, activation1,
material, reference configuration, cap/J guards and all585 nodes including
held reactions. The16-element patch is195/196/197/198/199/200/202/203/206/
237/240/243/244/246/247/248. Quiet9 are195/196/198/199/202/237/240/243/244.
Sensitive7 are197/200/203/206/246/247/248. No new calls on quiet9 or outside236.

| Complete candidate, both fields | Quiet9 | Secondary6 |247|
|---|---|---|---|
|S0 fine-window lower|retained D5|retained A55 angular2|retained A55 angular2|
|S1 middle|retained D5|new P4 angular4|retained F44 angular4|
|S2 upper|retained D5|new P8 angular8|new P8 angular8|
|I0 independent lower|retained U4|new graded-tetra face4/radial1|same independent recipe|
|I1 independent upper|retained U5|new graded-tetra face8/radial2|same independent recipe|

S0 differs from historical Q1 specifically at247: it uses A55, not F44.
The sensitive7 have a genuine angular2→4→8 sequence. All primary recipes use
Gauss5 in r/a/b, depth20, radialparts1 and the same ascending opposite-face
chart. P4/P8 have42000/168000 points per complete element per field, including
all20 shells and the core. P4 is the missing secondary angular4 witness.
Calling S0 sufficiently fine is a prospective hypothesis tested by both new
fine increments; it is not an already accepted numerical fact. A failed
S0/S1 cannot be relabeled post hoc by sliding the window.

Quiet9 values repeat in S0/S1/S2. Their identical differences earn **no new
resolution evidence**. Their separate retained witnesses are D4→D5 at fixed
subdivision, U4→U5 within the symmetric subdivision family, and D5↔U5 across
families. The new independent candidates use U4/U5 on quiet9, so finest
S2/I1 compares D5/U5 there, rather than identical reuse. This is a compositional
schedule with explicit previously measured quiet witnesses, not three new
uniform full-patch resolutions. Those witnesses, including their finite
limitations, must pass the allocations below at both fields/all components.

Eventual fixed order, if separately authorized: (1) P4 on secondary6 at both
fields; (2) P8 on sensitive7 at both fields; (3) I0 and I1 on sensitive7 at both
fields; (4) the three isolated axis checks below. No recipe substitutions,
extra levels, replacement calls, retries or favorable-pair selection. A future
runner may refuse/abort on a required failure, but must retain the partial
evidence and cannot report operational completion or a passing fine window.
An accepted complete operation requires the entire declared schedule.

## Independent family: graded affine tetrahedra

Uniform U5/D5 disagreement remains unresolved on secondary6. Reusing D4/D5
on the same uniform grid does not establish adequate spatial resolution,
especially at247. Instead, use a genuinely different sampling construction on
all7 sensitive elements, covering every physical shell and the core.

Use the same corner and physical radial regions r=1−Lcorner:20 dyadic shells
and core[0,2^-20]. Triangulate the opposite face on the equal barycentric grid
of side resolution m, yielding exactly m² face triangles. Give every grid
vertex a stable integer index and sort each triangle's three vertices by that
index. For each triangle and radial interval[lo,hi], let its lower vertices be
A0/A1/A2 and upper vertices B0/B1/B2, where
`A_i=C+lo*(V_i-C)` and `B_i=C+hi*(V_i-C)`; C is the corner and V_i a face
vertex. Decompose this homothetic triangular frustum into exactly:

- `[A0,A1,A2,B2]`;
- `[A0,A1,B1,B2]`;
- `[A0,B0,B1,B2]`.

The consistent vertex ordering defines shared-face diagonals. Each core face
triangle forms one tetrahedron with C; it does not use degenerate frustum
tetrahedra at lo=0. Evaluate each affine reference subtetrahedron using a
positive tensor Duffy Gauss5 rule (125 points). Orient each tetrahedron
consistently and certify positive reference volume. These oblique affine
tetrahedral charts and nodes differ from the primary r/a/b tensor-shell
sampling; sharing physical shell boundaries is not sampling identity.

I0 uses m=4 and one interval per dyadic shell. I1 uses m=8 and bisects every
dyadic shell radially; the core retains its complete triangulated cone.
Therefore:

| Independent rule | Reference subtetrahedra/element | Points/element/field |
|---|---:|---:|
|I0|`(3*20*1+1)*4² = 976`|122000|
|I1|`(3*20*2+1)*8² = 7744`|968000|

This refines both tangential spacing and radial spacing within an independent
family, at the same core depth. It is deliberately more demanding than merely
permuting a shell face or trusting a high point count. Its adequacy is tested,
not assumed: own fine increment I0/I1, finest S2/I1, and isolated primary-axis
checks must all pass. Two finite independent levels do not certify exact
integration or an asymptotic convergence order.

Before implementation/evaluation, future structural review must prove this
decomposition covers each frustum without gaps/overlaps, positive determinants,
consistent face diagonals, complete core, exact counts and distinct sampling
identities. Independently certify normalized rational moments through degree5
and reference physical moments through degree2 for every actual corner/chart,
with source-bound positive finite weights. The physical weighting stays
`normalizedWeight*det(referenceJacobian)/6`, with no current-J multiplier.
No geometry, points, moment sample or rule is generated during this design.

## Isolate other axes at the declared fine working level

Use S1's angular4 as the fixed fine working resolution, so each check changes
one axis and can reuse247's exact accepted radial witness:

| Check | Sensitive elements newly evaluated | Fixed choices | Changed choice |
|---|---|---|---|
|R4 radial|secondary6;247 R44 reused|Gauss5,angular4,depth20,ascending chart|radialparts1→2|
|H4 depth|all7|Gauss5,angular4,radial1,ascending chart|depth20→22|
|C4 chart|all7|Gauss5,angular4,radial1,depth20|ascending opposite face→cyclic left rotation|

H4 has46000 points and23 original regions. C4 has42000 points and21 regions.
Old X44 changes depth and chart together and is **not** either isolated check;
its close agreement is historical diagnostic evidence only. S1/R4, S1/H4 and
S1/C4 each form complete16-element comparisons, with quiet9 unchanged and
separately attributed to their old witnesses. The new R4 supplies secondary
radial evidence; old F44/R44 supplied247 only. Angular4-axis passes do not
prove every interaction at angular8 is small. The independent I1 increases
both tangential and radial spacing resolution, and S2/I1 tests the finest
primary against it. Missing or failing axis evidence rejects this proposed
finite-window result; no uniform analytic convergence claim follows.

## Comparisons, cancellation guards and shared budgets

Required, both fields/all five terms: S0/S1, S1/S2, I0/I1, S2/I1, and the
three isolated S1-axis checks. Every comparison covers all16 elements and all
585×3 entries including held reactions. Independently assemble matrix, volume,
passiveFiber, activePotential and total. Retain energies and saved-direction
work, all local gradients, region/element/patch/full reconstructions.

Use a stable156-unit partition: quiet9 whole elements plus21 actual physical
regions for each sensitive7. I0/I1 retain contributions by actual radial shell
and core; no shell vectors are invented from old whole-element data. Retain
all23 original H4 regions before grouping its final three into the depth20
core for comparison. Preserve microtetrahedron identity/ordering in deterministic
recipe metadata and original normalized point arrays, while streaming region
aggregates; do not claim a stronger per-microtetrahedron triangle than recorded.
Also retain a common16-whole-element diagnostic, separately labeled.

The unchanged global requirements are signed and unit-triangle force≤1e-5N,
signed and unit-work triangle≤5.492029235357012e-7J, for each component and
field. Reconstruction≤1e-8N/1e-9J and stationarity1e-4N remain separate.
Compute the actual complete scatter and triangles, including shared nodes;
baseline reused once, subtract its exact16 patch once, then add candidate16.

Additionally impose prospective sufficient subset allocations, applying to
both signed and triangle force/work metrics. These are stricter bookkeeping
requirements within the unchanged global gates, not relaxed replacement gates:

| Comparison class | Quiet9 force budget | Sensitive7 force budget | Work allocation |
|---|---:|---:|---|
|I0/I1|8.5e-6N|1.5e-6N|85%/15% of the same global work gate|
|Other required checks and quiet qualification|2e-6N|8e-6N|20%/80% of the same global work gate|

Quiet I0/I1's retained U4/U5 maximum across both fields/all terms is
8.378508899342663e-6N (volume, control); total is8.37501138850616e-6N.
It fits8.5e-6N and remains a finite witness with little allocated margin.
Quiet D5/U5's maximum is1.2198439485189283e-6N (volume, control), fitting2e-6N.
Quiet D4/D5 also fits. The
[retained-only scalar arithmetic](../review/selective-fine-window-schedule-20261007/retained-quiet-witnesses.json)
reports every component/field, all four metrics, and actual whole-element
partition. An independent reviewer must replay it. For primary/axis comparisons
quiet differences are identically zero; require the separate D4/D5 and D5/U5
qualification witnesses within their allocation anyway. Never count those
zeros as refinement. I0/I1 and finest S2/I1 have genuine nonidentical quiet
sampling. Allocated scalar bounds sum to the global gates; actual complete
shared-node scatter still must pass. Do not allocate each subset the full gate.

Report all fine increments and any increases/decreases on this matched partition.
Claim empirical improvement only when the decrease exceeds independently
audited binary64 reduction noise. No imposed Gaussian convergence order or
unsupported Richardson extrapolation. Any missing witness, failed allocation,
global gate, reconstruction, identity or resource receipt remains unresolved.
Keep all historical failed comparisons, including coarse Q0/Q1 and secondary
U5/D5, visible; neither must magically change after the new experiment.

## Exact cost frozen before independent review

| New work, both fields | New material calls |
|---|---:|
|P4 secondary6: angular4 full support|504000|
|P8 sensitive7: angular8 full support|2352000|
|I0 sensitive7: independent lower|1708000|
|I1 sensitive7: independent refined|13552000|
|R4 secondary6: radial2 at angular4|1008000|
|H4 sensitive7: isolated depth22|644000|
|C4 sensitive7: isolated cyclic chart|588000|
|**Planned complete and maximum new calls**|**20356000**|

This is40.9166 times the completed497500-call run. Independent-family work is
15260000 calls (74.97% of the new schedule). Quiet9 and outside236 get zero
new calls. The expense is intentional independent-resolution evidence, not
uniform refinement of every patch element. Primary full-region rules avoid
claiming unmeasured angular8 tails were resolved from identical reuse. No
success or minimal-cost claim is made. A cheaper partial experiment may reveal
the missing angular4 behavior, but cannot pass this predeclared full window.

Reuse exactly the1342 byte-hashed files in the reuse index: complete U3 baseline
and frozen arrays; quiet D4/D5/U4/U5 locals; secondary A55;247 A55/F44/R44;
their actual normalized/physical weights and source/receipt closure. Each file
is checked against its exact immutable commit blob. Recipes, fields, direction,
material and law/helper module hashes are explicit. Existing normalized F44/R44
corner0 arrays can serve new geometry at the same chart; new element physical
weights and all its specimen values are still new. No across-element value
reuse. References do not count as new output copies or new material calls.

Retained terminal F44 carries4000 old s1/s2 values from the historical exit1
run, plus38000 successful-run tail values; control F44 has42000 successful-run
values. Retained A55/R44 provenance stays exact. The old failed operation is
never relabeled complete; its incomplete receipt stays pinned. Hash/schema/
law/field/point/weight mismatch stops reuse with no replacement-call allowance.

Proposed new output:276576000B normalized binary arrays (six binary64 values
per point, including r),81424000B physical weights retained once per element/
recipe with both-field identity checks; total358000000B binary payload.
There are554 new normalized files,1001 physical-weight files,2002 logical
region rows and94 stages. The manifest enumerates bounded slots for16 full
hybrids and24 comparison records:14 required,6 quiet witnesses and4
informational cross-checks. Comparison slots include156-unit data plus
common16 diagnostics within their cap. Byte envelopes are8192B/region,
131072B/stage,1048576B/hybrid and2097152B/comparison. Receipts/provenance,
two64KiB logs, external records and4MiB emergency reserve are included.
**Planned upper envelope463021440B**, below the proposed512MiB ceiling
(536870912B) by73849472B. Emergency partial weights get512KiB, enough for
I1's largest48000-point shell (384000B). These are design envelopes, **not
implemented/enforced or structurally qualified yet**. Future preflight must
freeze closed filenames, actual encodings and refusal paths before execution.

The observed43.048835s/497500-call rate extrapolates to1761.41s; the prior slow
135.02s batch extrapolates to5524.56s. Plan1800–6000s (30–100min), with a
proposed7200s public-entry-to-final-acceptance wall ceiling, one eventual
invocation,1GiB Node heap and2GiB RSS. Estimates include no new benchmark and
are not guarantees; new geometry/metadata overhead may change them. Streaming
one element/region at a time is required; do not hold the full358MB binary
payload or all points as JavaScript objects at once. Only future implementation
and structural resource review can validate those limits. The old300s/64MiB
authorization is consumed and does not authorize these new budgets.

## Review and remaining limits

First independent scientific/cost review of this exact frozen proposal, then
separate parent disposition of scope/cost. Only a later explicitly authorized
step may implement/generate structural preflight; its independent review and
separate new execution authorization must precede any specimen call. This
document grants none of those permissions. A scientific design pass is not a
parent cost acceptance, a structural pass or numerical convergence.

Outside236 elements retain their exact old U3 contributions and remain
unqualified. Even a future passing16-patch fine window establishes only bounded
finite integration agreement under this schedule. No analytic error bound,
whole-body integration, equilibrium, tangent, displacement or anatomical
acceptance follows. Main, book, release branches, deployment, environment
protections and credentials are untouched. Work stays local.
