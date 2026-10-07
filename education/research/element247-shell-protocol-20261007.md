# Whole-element247 corner-shell method protocol

**Protocol and structural preflight only. No new material assembly is authorized.**
This new research branch starts from retained run/evidence
`74054f5c611c57c0b9ddb1fd77a9aaba20ee9c8b`, whose executed source was
`ef39f8335486b5cd7c9954361da181f46ea21c80`. The old result remains
**`UNRESOLVED_FIXED_PATCH_INTEGRATION`**. Parent thread
`01a103c3-a2e6-7606-8c1e-06987ac710f1` requested the smallest bounded,
whole-element247 corner-resolving method study, with a protocol, resource
budget, fixed independent criteria and structural preflight before any new
material assembly. This document does not extend the earlier one-invocation
authorization. A future runner and its actual runtime enforcement need
separate review and authorization.

## Why this method and what stays frozen

The parent's independent retained-data localization reports that247 supplies
about99.97% of the terminal U4→U5 peak discrepancy; the whole-patch volume
term supplies about99.17% of that total peak. These percentages have different
numerators. Removing247 diagnostically still leaves
about7.66e-5N. Secondary elements197/200/203/206/246/248 cannot be omitted from
qualification. The preflight separately reconstructs every component's local
differences for **all16 incident elements** from the retained vectors and
records the residual after subtracting247. That arithmetic is a producing-agent
check, not a substitute for the parent's independent review.

The field is a P2 tetrahedral reference mapping, not an affine physical
tetrahedron. Element247 has corner0 at free node92 and ten-node connectivity
`[92,109,93,111,576,505,573,577,578,575]`. Preserve the mesh585nodes/252elements,
495free/90held nodes, material, activation1, reference fibres and all physical
laws. The domain gates remain current `J>1e-6` and reference Jacobian `>1e-15`.
The original physical stationarity gate is1e-4N; this study does not test or
establish stationarity.

The two unchanged valid positions are control45/iteration1 and
terminal46/iteration13, SHA-256 of `JSON.stringify` arrays respectively
`07e50e29f34c3f6880f3895bb63c3a53dd18afee90217b6816099681e2c8132e`
and `655eb058007d2432689257b0bbe84f9b054500587672b087b03dbecf0bdfc410`.
The unchanged terminal virtual direction is
`bb8bc986540e2e3e098969db2b34b3682f55602d868c9972e35b42464972cdab`,
L1norm0.05492029235357011m, zero on held nodes. No increment is applied.
The old parameter provenance remains: sigma0=3599330.7341830498Pa is a
historical45-mode fit to the Arm26model target, not measured physiological
stress. The active term is a fixed-activation potential, not passive storage.

At terminal corner0 the exact saved-field J is approximately1.300982206e-6.
Its three inward barycentric slopes are positive, approximately
2.171995293,0.926739670,2.193105419. The first-order scale
Jcorner/slope is roughly0.59e-6 to1.40e-6 in barycentric radius. This motivates
core radius2^-20≈0.954e-6 and a depth22 cross-check with core radius≈0.238e-6.
These are scale estimates, not an assertion that J is globally linear or a
proof of accuracy. The saved fields have a finite positive-J layer; no true
singularity or anatomical continuum solution is assumed.

## Derived whole-element coordinate map

Let **r=1−L0** be barycentric radial position, not physical distance. For
r,a,b in(0,1), define

```
L0 = 1-r
L1 = r*a
L2 = r*(1-a)*b
L3 = r*(1-a)*(1-b).
```

The map covers the entire reference tetrahedron once in its interior.
Conversely r=L1+L2+L3, a=L1/r and b=L2/(L2+L3); boundary degeneracies have
zero volume. The magnitude of its determinant with respect to(L1,L2,L3)
is **r²(1−a)**. Thus the normalized tetrahedral measure is
**6r²(1−a)dr da db**, and the physical reference weight is that normalized
weight multiplied by **det(DXreference(L))/6**. The current field's J is not
an integration weight. The curved reference geometry and its original shape
gradients are evaluated through the unchanged `referencePoint` helper.

The shells are [1/2,1],[1/4,1/2],…,[2^-D,2^-(D-1)] plus core[0,2^-D].
They cover[0,1] with no gaps or overlapping interiors. Each shell has exact
normalized mass hi³−lo³. No coarse outer tetrahedron or unintegrated corner
is retained. An interior positive Gauss product rule integrates each radial
interval and the full opposite triangular face parameterized by(a,b).
Radial subdivision bisects each interval; angular subdivision bisects each
of a,b, retaining its actual angular Jacobian. These are quadrature
subintervals, not new physical elements, mesh nodes or displacement modes.

The method follows the vertex-directed transformation idea in
[Duffy's original1982 paper](https://epubs.siam.org/doi/10.1137/0719090),
whose original publisher metadata and abstract were verified. The open-access
original [Mousavi and Sukumar paper](https://link.springer.com/content/pdf/10.1007/s00466-009-0424-1.pdf),
section2/equations1a–1b, derives transformation Jacobians and uses product
Gauss integration. Their power-singular kernels are different from this
saved finite-J specimen. We derive our tetrahedral map above and use a unit
radial exponent; we do not transfer their kernel-specific optimal exponent,
error estimate or convergence claim. The four/five Gauss tables are the
unchanged binary64 tables in the earlier accepted protocol. No new dependency,
table generator or build-time download is needed. The
[source ledger](element247-shell-protocol-20261007-sources.json) records exactly
which original content was verified and the applicability limits.

## Fixed finite sequence and bounded resources

| Rule | Core depth | Radial/face Gauss order | Radial parts per shell | Parts per a,b | Face order | Points/field |
|---|---:|---|---:|---:|---|---:|
| C44 |20|4/4|1|1|1,2,3|1,344|
| C55 |20|5/5|1|1|1,2,3|2,625|
| R55 |20|5/5|2|1|1,2,3|5,250|
| A55 |20|5/5|1|2|1,2,3|10,500|
| X55 |22|5/5|1|2|2,3,1|11,500|

C44→C55 is informational order sensitivity. Required comparisons are
C55↔R55(radial subdivision), C55↔A55(angular subdivision), and
A55↔X55(cyclic face chart and smaller core). The cyclic chart changes
point locations while preserving the physical domain and positive measure.
The latter changes two resolution features together and therefore checks
agreement rather than attributing any difference solely to either feature.
All five rules evaluate the entire247 element at both fixed fields, if later
authorized. Their **31,219points/field require exactly62,438callbacks**.
There are no extra adaptive attempts, trial displacements or tolerance tuning.

The proposed one-invocation limits are62,500maximum actual material callbacks,
180s wall time,1024MiB Node heap,2GiB process RSS and64MiB output. The actual
planned callback count must be62,438; the ceiling provides no spare
experiments. A future runner must distinguish reserved, entered and completed
callbacks, check elapsed time before/after callbacks and output, sample RSS
at least every128 callbacks and at shell boundaries, check output growth,
retain partial vectors/weights and stop without retry on resource/domain
failure. The already reviewed runtime helpers may be reused with these
smaller limits, after runner-specific damage tests. No such runner is created
or invoked by this protocol.

## Retention and fixed acceptance criteria

A future run must immediately retain, for each recipe/state/original shell:
all30local force entries for each of matrix, volume, passiveFiber,
activePotential and **independently assembled actual-law total**; their
energies and directional derivatives; completed point count and actual
reference physical weights. Also retain all five corresponding585×3
scattered vectors including held reactions, point-to-shell ranges and
component-sum reconstruction errors. Coordinates, field/direction hashes and
material provenance must match this protocol. No aggregate-only output is
sufficient. Original shell data must remain even after comparison regrouping.

For comparisons, depth22's last two shells and core are summed into the
depth20core, giving the same21geometric comparison regions. Other regions
match exactly. Retain signed local difference vectors per region, summed
difference vectors, per-entry sums of absolute shell differences and signed
and absolute-sum work differences. This regrouping retains full original
vectors and avoids subtracting unrelated spatial partitions.

For **each required pair, both states and every component including total**:

1. The infinity norm of the actual summed all-node force difference must be
   ≤**1e-5N**, and so must the infinity norm of the per-entry sum of absolute
   shell force differences. The latter triangle envelope blocks cancellation
   between shells. It is a finite-rule disagreement bound, not an error bound
   relative to the unknown exact nonlinear integral.
2. Both the absolute total signed directional difference and the sum of
   absolute per-shell directional differences must be
   ≤**5.492029235357012e-7J**, the unchanged whole terminal-direction budget.
   Directions use original global nodes and all three coordinates. No new
   energy tolerance can replace either force or work criterion.
3. Positive weights, exact coverage, original whole-element valid-field
   certification, source/field identities and component/total reconstruction
   must pass. An independent reviewer must reproduce retained shell sums,
   scatters, differences/work, inventory/weight hashes and pass/fail arithmetic
   without new material evaluation. This producer's preflight is not that
   independent acceptance.

Passing every finite comparison would permit only **bounded element247
fixed-field method agreement**. A failed comparison means unresolved247
integration; a resource stop means an incomplete study. Neither can be
relabelled equilibrium or material validation. Any pass cannot qualify the
16-element patch or its secondary contributions. All retained
U4/U5/D4/D5 local differences for197/200/203/206/246/248 and the other incident
elements remain present. They cannot be replaced with zero, removed, deemed
negligible, or retrospectively declared converged. Further patch qualification
would need its own bounded protocol; the236other elements also lack a global
integration claim.

## Structural preflight and review artifacts

The preflight verifies every immutable old source/raw-output hash plus new
tracked source hashes, both original whole-mesh valid-field certificates,
unchanged cap values/direction and the exact-reference Bernstein bound.
It generates all31,219normalized points and actual reference weights without
evaluating material stress or energy. Every original shell is checked against
an independent **exact rational** monomial integral through total degree5:

```
6 * (alpha1! alpha2! alpha3!)/(alpha1+alpha2+alpha3+2)!
  * integral(lo,hi) (1-r)^alpha0 * r^(alpha1+alpha2+alpha3+2) dr.
```

The radial integral uses the finite binomial expansion and exact dyadic
endpoints. For the full tetrahedron it reduces to
6·product(alpha_i!)/(sum(alpha_i)+3)!. Each positive moment is checked with
relative error≤2e-11, **including the tiny core**. No absolute cutoff can
silently discard it. Gauss4 integrates the mapped polynomial through degree5:
the radial degree is at most7, the a degree at most6 and the b degree at most5.
This is a polynomial fact, not a nonlinear constitutive accuracy claim.

The actual reference Jacobian is a degree3 barycentric Bernstein polynomial
from exact binary64 geometry. Its coefficients provide independent analytic
physical-reference moments through barycentric degree2 on every shell,
checked with relative error≤2e-10. This covers reference volume and the
quadratic reference-coordinate moment space. Whole-element physical volume
and weight positivity are also checked. The state geometry at the new points
is checked against the unchanged Jguard, without evaluating the law.

Eight damage/structural tests cover missing outer/core coverage, shell gaps
or duplicates, chart determinant, exact moments, all registered point counts,
wrong radial Jacobian, damaged or negative tiny-core weights, comparison
regrouping, concealed force/work cancellation and malformed retained vectors.
Run after committing the source:

```sh
node education/tools/preflight-element247-shell.mjs
```

For a review replay, use `--output /tmp/kenoma-shell-review-FRESH` to preserve
the earlier evidence. The committed
[structural receipt](../review/element247-shell-protocol-20261007/confirmation-preflight.json)
will bind source, rule ranges, per-shell normalized and physical moments,
positive weights, sample geometry and test evidence. The
[retained-data localization](../review/element247-shell-protocol-20261007/retained-patch-localization.json)
keeps every incident element's signed component vectors and diagnostic
residual after subtracting247. Review point files contain little-endian
Float64 records `(L0,L1,L2,L3,normalizedWeight,r)` in recipe/shell order;
physical-weight files contain one reference weight in m³ per record.
All artifact links are relative and portable within the checkout.

No law, calibration, displacement optimizer, accepted book, anatomical
completion claim, existing branch, main, PR, protection, credential,
deployment or publication is changed. Old unresolved results and historical
independent-review limits remain explicit.
