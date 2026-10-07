# Independent geometry design review

Status: PASS_INDEPENDENT_GEOMETRY_DESIGN. This reviews the accepted schedule's mathematical construction, not yet the frozen implementation or actual preflight. No repository files edited, no specimen/material calls, no constitutive evaluator imports.

The standalone script `check_geometry.py` uses integer barycentric mesh coordinates with common denominator `2^20*m*radialParts`, exact determinant arithmetic, an independently written face-incidence checker, NumPy tensor nodes and an independent Fraction shell moment formula. It does not import repository code. The frozen schedule is at `/tmp/Kenoma-fine-window-schedule/education/research/selective-fine-window-schedule-20261007.json`.

All four corner charts pass for I0 and I1. Every subtetrahedron is positive after the declared final-two-vertex swap. Every internal face occurs twice with opposite induced orientation. Every exposed face lies on precisely one actual reference boundary plane, with the expected boundary counts. Each shell's determinant sum equals `hi^3-lo^3` exactly; full normalized mass equals1. The conforming, consistently oriented tetrahedral complex with the full triangulated reference boundary and positive tetrahedra establishes coverage: its oriented indicator degree is1 throughout the reference simplex and0 outside; positivity precludes overlapping multiplicity or gaps.

I0 has976 subtetrahedra,122000 points and508 boundary triangles. I1 has7744 subtetrahedra,968000 points and2008 boundary triangles. Consistent globally sorted face vertices give conforming shared-face diagonals. The core uses a cone tetrahedron per face triangle; no degenerate lo=0 frustum tetrahedra occur.

For an affine microtetrahedron, a barycentric polynomial of total degree≤5 composed with `(1-u,u(1-v),uv(1-w),uvw)` has per-variable degree≤5. With Jacobian `u^2*v`, weighted tensor degrees are≤7/6/5. Gauss5 exactly integrates through degree9 in each variable, so the required normalized degree5 moments are covered in exact arithmetic. Physical P2 reference Jacobian determinant is degree3, and multiplying a degree2 monomial gives degree5; the same exactness applies with the unchanged weight `normalizedWeight*det(referenceJacobian)/6`.

The independently generated corner0 numerical rule passed126 monomials per region over all21 regions:2646 checks per independent recipe. Maximum relative errors were4.30e-16 (I0) and4.44e-16 (I1), below existing2e-11 geometric tolerance. Other corner topology charts are exact coordinate permutations; the implementation must nevertheless test actual generated binary arrays for all four charts. Only one region is held at once:6000 points I0,48000 points I1. In total287778 independent assertions passed.

Implementation review prerequisites:

- Bind source and recipe identities, exact triangle/tetrahedron enumeration and orientation. Preserve original point arrays, deterministic metadata and hashes; independent design hashes use a different diagnostic encoding and are not production hashes.
- Compute tiny-core microtetrahedron volume robustly. Naive near1 binary64 reference-coordinate subtraction for corner1/2/3 can lose relative precision. Exact integer/rational determinant or translated corner-local coordinates are appropriate; actual all-corner moments must detect cancellation.
- Permute exponent and polynomial coefficient indices consistently so the actual corner exponent is first in the rational shell oracle. Use exact dyadic/Fraction power differences for tiny-core expected moments, never subtract nearly equal floating full-element moments.
- Verify actual positive finite normalized and physical weights, barycentric interior points and all21/23 regions. Independently verify normalized degree5 and physical degree2 moments for each actual element/chart. Count source geometric guard checks at both frozen fields separately from material calls.
- Prove H4's shared s1..s20 arrays equal P4/F44 exactly, and247 C4's shared arrays equal X44 exactly. No across-element material-value reuse. P4 rows referenced by H4 must have accepted completed prior same-invocation receipts. Shared regions earn no new resolution evidence.
- Keep seven declared scientific comparisons plus retained quiet witnesses, all16 elements, both fields, all components, actual156 units and all585 nodes, existing global gates and stricter subset allocations. No matrix/per-microtetrahedron triangle claim from aggregate-only data.
- Verify streamed actual encodings and enforcement fit512MiB output,1GiB heap/2GiB RSS,7200s and19716000callbacks. This design check does not prove process resources, receipt lifecycles or physical qualification.

Outside236 U3 elements remain unqualified. These geometric moment checks do not certify nonlinear stress integration, independent-family resolution adequacy, stationarity, equilibrium, whole-body acceptance or anatomy. The historical unresolved result and failed coarse comparisons remain unchanged.
