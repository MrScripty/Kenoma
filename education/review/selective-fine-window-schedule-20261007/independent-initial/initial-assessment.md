# Independent scientific and cost review of frozen schedule

Reviewed commit: `a5d0243b36f99379a61f52a0845a3e01fc6470a0`.
See `initial-review.json` for exact source hashes and replay results.

**Initial verdict: FAIL_PROSE_QUOTE_ONLY.** The frozen document incorrectly
quotes quiet D5/U5 as 1.2198439485189283e-6 N (volume/control). Independent
replay gives **1.193659700748917e-6 N (total/control)**; volume/control is
1.193607632732352e-6 N. The retained JSON is correct. No budget or gate is
affected. Scientific design otherwise passes conditionally on future structural
qualification and actual prescribed comparisons.

The standalone standard-library reviewer read exact Git blobs and never
imported model/law/generator modules. It verified all 1342 reuse files, hashes,
byte counts and equality at the schedule freeze. It replayed all 120 quiet
metrics using `math.fsum`, with zero difference from the recorded JSON. All
4653 assertions passed, including call/file/region/stage/storage arithmetic,
unchanged material, held-direction zeros, shared allocations and old failed
operation provenance. The 4000 old values remain associated with an incomplete
operation; their retained local vectors/energies match F44's two reused rows.

## Scientific assessment

Sensitive7 angular2/4/8 is a genuine primary sequence. Quiet9 repetition
provides no new primary refinement evidence, but the design explicitly reuses
their D4/D5, U4/U5 and D5/U5 witnesses and gives them allocated budgets. The
independent sensitive family uses affine tetrahedra and different nodes/charts;
sharing shell boundaries does not make sampling identical. I0/I1 and finest
S2/I1 jointly test its adequacy, while independent primary radial/depth/chart
checks test axes separately. All comparisons cover both fields, all five terms,
all 16 elements and all 585 nodes including held reactions on a stable
156-unit partition. H4 original regions must be preserved before grouping.

The homothetic frustum construction is analytically coherent. Relative to the
positive corner-to-face cone determinant, the three absolute tetrahedron
determinants are proportional to
`(hi-lo)*lo^2`, `(hi-lo)*lo*hi`, `(hi-lo)*hi^2`.
Their sum equals `hi^3-lo^3`, the complete frustum volume factor. One of the
listed orders has opposite orientation; explicit reorientation is therefore
required, as prescribed. Consistent global vertex ordering gives the same
diagonal on shared radial quadrilaterals. The core is a complete cone and
must not use degenerate lo=0 frusta. This is an analytic design assessment,
not generated geometry or structural certification. Actual implementations
must prove disjoint coverage, positivity, moments and distinct sampling.

The evidence can support only the prospectively named bounded finite
agreement result, contingent on every prescribed check. Neither two fine
independent levels nor small increments provide an analytic error bound or
convergence proof. Within-shell cancellation remains possible, and polynomial
moment checks do not certify nonlinear material-stress integration. No
presumed Gaussian convergence rate or post-result window sliding is valid.

## Resource assessment

20,356,000 planned new calls, 358,000,000 binary payload bytes and
463,021,440-byte planned envelope are arithmetically correct, with
73,849,472-byte headroom below 512 MiB. Independent-family work accounts for
15,260,000 calls (74.97%); it dominates cost and is not proved minimal.
Historical rate extrapolations give 1761.41 and 5524.56 seconds; 30–100 minutes
and a 7200-second ceiling are reasonable planning values, not guarantees.
Streaming, precise capped encodings and actual refusal/resource receipts
need future implementation/structural review. No benchmark occurred.

The retained quiet U4/U5 volume/control bound 8.378508899342663e-6 N fits its
8.5e-6 N allocation by only 1.21491100657337e-7 N. This is permitted but leaves
little allocated margin. All future comparisons still have to pass actual
shared-node scatter and unit triangle; subset maxima cannot substitute for
that calculation.

## Preferred prospective reuse correction

Two exact-identity reuse savings are scientifically sound and preferred if
explicitly re-frozen with point/weight/law/field/dependency provenance:

- H4 s1 through s20 are identical to S1 at the same chart, angular4 and r1.
  Reuse secondary P4 rows produced earlier in the eventual invocation and
  accepted 247 F44 rows. Only H4 s21/s22/core are new: 84,000 calls instead
  of 644,000. New depth evidence is their complete grouped core difference;
  shared-shell zeros earn no resolution credit.
- For 247, C4 depth20/chart231 s1 through s20 match accepted X44
  depth22/chart231. Reuse those exact old rows and evaluate the depth20
  core anew. This saves 80,000 calls and leaves a genuine chart comparison
  against S1; the chart check cannot be inferred from old X44's grouped core.

Combined revised maximum would be 19,716,000 calls. P4 reuse requires an
explicit same-invocation receipt dependency, retaining those original rows
once. X44 reuse requires original row/point/weight/receipt closure and no
fallback/replacement calls. Both revisions preserve complete support, all
axis checks, all required comparisons and historical failures.

Outside236 U3 elements remain unqualified. No material/specimen calls,
quadrature or geometry generation, runner launch or source edits occurred.
