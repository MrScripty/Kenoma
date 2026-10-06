# Archived segment audit outcome

Source commit: `24090b4c27e37c7142cc77f9eacc27a5818ab575`, direct child of frozen response `cfe6d18b742b2f85cb1bb849adf3b6f9dc52e1cf`. Separate branch: `research/isolated-globalization-proposal-20261006`. This outcome supplements the frozen [proposal](isolated-globalization-proposal-20261006.md); it does not edit any previous response/report.

The [geometry receipt](../review/isolated-globalization-proposal-20261006/geometry-audit.json) passes all frozen input/source hashes, all 15,120 independent reference/start/end spatial coefficient comparisons, saved-field reconstruction, exact cap checks and increment checks. The [geometry kernel tests](../tests/isolated_segment_geometry.test.mjs) pass 3/3, including the damage case with positive endpoints but inverted interior. No constitutive evaluations, new optimizer trials, force refit or physical state advancement occurred. Full-nodal physical force gates remain failed in the saved evidence.

## Exact guarded interval

For the saved segment from last valid46 to refused trial, **all 20,160 guarded space×time Bernstein controls are strictly positive** on:

`0 ≤ t ≤ 371693072511/1099511627776 = 0.33805288013445534`.

This certifies the unchanged `J>binary64(1e-6)` guard throughout all 252 P2 elements and the complete intervening path. Reference coefficients are positive and all 90 held nodes remain exactly at reference position. The binary64 guard is exactly `4722366482869645/4722366482869645213696`.

The adjacent upper fraction is:

`371693072512/1099511627776 = 0.33805288013536483`.

The generic sufficient certificate reports unsupported there. In this particular record its witness has spatial multi-index `[3,0,0,0]` in element247 and time-control3. A pure spatial corner coefficient is the actual corner determinant; the last time Bernstein control is the actual endpoint value times a positive denominator. Its guarded numerator is negative. Thus this upper fraction additionally has an **actual corner domain-guard violation**, although it does not establish negative orientation there. The lower full-path proof plus that witness bracket the first loss of the retained guarded domain within `2^-40` of t. No maximal unguarded orientation interval is asserted.

Element247's unguarded corner determinant has a unique zero between `0.338053670948284` and `0.3380536709491935`; all three derivative Bernstein controls are negative on `[0,1]`. The other saved negative corners have unique zeros in element250 at `[0.4093482676162239,0.4093482676171334]` and element251 at `[0.563442949810451,0.5634429498113604]`. These corner brackets do not certify the rest of the spatial field after the guarded safe prefix. The saved t=1 endpoint is inverted. All per-cell guarded control minima and exact corner polynomials are retained in the receipt for reproduction. Raw numerator minima across different element denominators are not a physical margin.

## Scaling and local descent

| Saved increment | Maximum nodal increment, m | Euclidean free-vector increment, m | Extra coordinate increment, m | Valid-start linear virtual work, J |
|---|---:|---:|---:|---:|
| Control45 → last valid46 | 0.00020000000000000562 | 0.001782793568546328 | 0.0007433158092602007 | −0.28211211812590314 |
| Last valid46 → refused trial | 0.00019999999999988774 | 0.001754161744167322 | 0.0008702732639144689 | −0.298819745155294 |

The physical maximum increments match the 0.0002 m source bound within binary64 storage roundoff. Reconstructed basis increments differ from stored nodal differences by at most `3.6843900326488654e-16 m`; cap increments are exactly zero. The L2 direction norm is `0.9999999999999996`, maximum node norm `0.17047889080869053`, and maximum dot with original columns `5.010098239055516e-16`. All saved positions reconstruct exactly in the source implementation. The raw unscaled Newton vector/scaling factor is unavailable and has not been recomputed.

Both steps are local descent increments. The accepted energy change was −0.2691656578664876 J. No energy or force is defined/evaluated here for the refused trial or any shortened segment position. Geometry certifies only admissibility; it cannot establish sufficient energy decrease or convergence.

## Correct reporting and next boundary

The target is **987.26 N**; the old achieved fit is **987.2744117188512 N**. At the unchanged45 control, the extended46 maximum is **379.5319801935699 N**; after the valid step it is **343.38593717301023 N**. The original45 maximum rises from **0.00005820078105145399 N** to **0.8778785510185041 N**. The trace's independently assembled original45 maximum differs from the retained-column audit by about `3.2e-12 N`; this does not change any gate outcome. Full-free maxima remain **64.06683747708074 N** and **53.595914611257406 N**, both above the unchanged `1e-4 N` gate.

The [bounded geometry-first proposal](isolated-globalization-proposal-20261006.md#proposal-requiring-frozen-review-before-another-experiment) retains the same physical laws, caps, direction, potential, Armijo and force tests. It is a reviewable proposal only. Independent review and a frozen protocol are required before any next experiment. No equilibrium, anatomical completion, spatial/quadrature convergence or stability claim follows. No PR, publication, deployment, existing-branch change, protection or credential change is part of this outcome.
