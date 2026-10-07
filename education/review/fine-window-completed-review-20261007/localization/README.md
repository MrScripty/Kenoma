# Independent completed-run localization and witness design review

Verdict: **PASS_RETAINED_LOCALIZATION_AND_SYMBOLIC_DESIGN_REVIEW**. Read-only review of completed head `5f7612f6c7f6609d8946b3394d7363609d7a30b1`; 882 raw region JSON files match the frozen raw inventory, and reference geometry and saved fields/direction match that commit's blobs. Independent `math.fsum` reduction agrees with stored focus comparison metrics to at most `1.0587911840678754e-22`. All 42 I0/I1/P8 stages at both fields reproduce from 21 original region records within unchanged reconstruction gates. 6,633 arithmetic/count assertions passed. **Zero material calls and zero quadrature generation.** The failed completed result and consumed authorization remain unchanged.

## Retained failure localization

Terminal I0/I1 volume signed/region-triangle differences are `4.460081948072867e-5` / `4.4600819482843576e-5 N`; total differences are `4.474374534905057e-5` / `4.474374535162453e-5 N`. Their maximum is node 505, y. Those shared-node maxima combine contributions of elements 206, 246 and 247; they are not three unrelated maxima to which separate full budgets may be assigned.

Element 247 contributes total `4.3135464900032926e-5 N`: shell s1 `2.892166977197519e-5`, s2 `9.832160698053372e-6`, s3 `3.082732304093838e-6`, s4 `9.235077813585235e-7`. Element 206 contributes `1.428197500180849e-6`, mostly s1 `1.4187636576679097e-6`; element 246 contributes `1.8008294883679595e-7`. Full component/element/region tables and all other contributions are in localization.json and localization.csv.

For the **focus7 subset**, the matrix difference is `1.4292536974469965e-7 N`; passive-fiber and active-potential differences are at most about `1.3e-12 N`. These are focus7 metrics, not whole-patch component maxima: retained quiet9 contributions make the whole-patch passive-fiber and active-potential maxima larger. The focus7 total failure is dominated by the volume component. Both focus7 work metrics pass. Control I0/I1 focus total triangle is only `4.54448491817167e-8 N`.

At terminal, retained S2/P8 versus I1 focus total signed/triangle differences are `5.437358881193145e-7` / `6.118907592622646e-7 N`, already below the stricter `1.5e-6 N` independent focus budget. The **I0/P8 diagnostic derived from retained records**, with no new experimental comparison or evaluation, has focus7 total triangle `4.528748137912947e-5 N`. These observations support the hypothesis that I0 is underresolved, particularly on element 247's outer shells. They do not prove I1 converges, determine an asymptotic order, distinguish radial from tangential causes of the coupled I0/I1 change, or exclude shared bias between I1 and S2. Recorded physical shell contributions cannot reveal a finer within-shell cancellation bound.

## Smallest complete composite witness at the specified finer recipe

Predeclare four new regions: element 247 s1/s2/s3 and element 206 s1, at both frozen fields. Keep the same independent affine-tetra construction, chart, physical region boundaries, depth 20 and positive Gauss5 Duffy rule. Change tangential face resolution m=8 to m=16 while keeping radial parts=2. This is a real angular refinement of the independent family; it supplies no new radial-refinement evidence.

Each selected shell contains `3 * 2 * 16^2 = 1536` affine tetrahedra and `1536 * 125 = 192000` points per field. Exact planned new calls: **4 * 192000 * 2 = 1,536,000**. Four distinct corner/region normalized arrays total **36,864,000 bytes**, and four reference physical weight arrays reused between fields total **6,144,000 bytes**; **43,008,000 bytes** of new binary payload. JSON, receipts, logs and emergency storage still need separate bounded preparation; this is not a complete enforced output budget.

For a newly named prospective composite protocol, lower T0 uses retained I1 inside the selected regions and retained I0 elsewhere; upper T1 uses new I2 inside and retained I1 elsewhere. Quiet9 retain U4 in T0 and U5 in T1. Require actual full 156-unit, all-16-element, all-585-node signed/triangle force and saved-direction-work comparisons for T0/T1 under the unchanged 85% quiet / 15% focus allocation, and S2/T1 under the unchanged 20% / 80% allocation, in both states and all five components. Retained I1/T1 is an additional diagnostic, not a substitute. Retain all original physical contributions and reconstruct region/element/patch/full vectors and energies at 1e-8 N / 1e-9 J. All old primary and separate angular/radial/depth/chart checks remain explicit immutable prior witnesses.

The retained T0/T1 complement has maximum force `1.4884189198342249e-6 N` across both fields and all five components. Consequently a conservative sufficient bound leaves only **1.158108016577515e-8 N** for the new selected-region increment within the existing 1.5e-6 focus budget. This is a real risk, not an expected pass. Evaluate the actual combined shared-node vectors and unit triangles; do not give the complement and selected regions separate fresh 1.5e-6 budgets or count identical reuse as new resolution evidence.

Four is the minimum physical-region count for this complete composite design: at node505/y in the total component, deleting the largest possible three physical-region absolute contributions still leaves `2.9071825775021348e-6 N`, above 1.5e-6. The selected four achieve a remainder below 1.5e-6. This proves minimum region count at the specified common m16/r2 recipe and frozen complement; it is not an absolute minimum over every conceivable quadrature family or parameter choice.

## Priced options, not automatic retries

Adding element 247 s4 costs **1,920,000 calls**, with **53,760,000 binary bytes**. Its retained-complement maximum is `5.649111384757014e-7 N`, leaving `9.350888615242987e-7 N` conservative new-increment room. This is substantially less fragile, but it is a different schedule requiring prospective choice and review; a failed four-region run cannot automatically extend into this option.

A single element247/s1 angular m16/r2 diagnostic costs **384,000** calls at both fields. A radial-only m8/r4 diagnostic costs **192,000** calls. Neither supplies a complete composite independent witness under the frozen focus budget. Full element247 m16/r2 costs **7,744,000** calls, but retaining all other I0/I1 contributions still exceeds the 1.5e-6 focus allocation; adding element206/s1 makes that option **8,128,000** calls. Refining both axes to m16/r4 doubles selected-shell costs and tests a coupled change rather than isolating tangential resolution.

No preparation, quadrature generation or execution is authorized by this review. Any future schedule needs frozen source identities, source/field/law hashes, independently verified exact coverage and moments, closed output envelopes, streamed 192000-point-region handling with durable failure receipts, and separate execution authorization. The old 512 KiB partial-weight reserve cannot hold a full new 192000-point region's 1,536,000 weight bytes; a future four-chunk design of at most 48000 points per chunk must explicitly preserve completed chunks and the current partial chunk, or freeze a different sufficient reserve before execution. No implementation is provided here.

The original I0/I1 failure remains immutable. Even a future passing composite witness establishes only its bounded finite comparison schedule. Identical retained contributions earn no new resolution credit. Outside236 elements and the anatomical capstone remain unqualified; no analytic error, continuum convergence, equilibrium, tangent, displacement, whole-body integration or anatomical acceptance claim follows.

## Artifacts

- README.initial.md: initial review prose preserved; the current README clarifies subset scope and derived-diagnostic attribution without changing numerical reports.
- localize.py: independent retained scalar reduction, no repository-module imports.
- localization.json / localization.csv: component, element and original-region data for both states and I0/I1, P8/I1, I0/P8.
- subsets.py / subset-localization.json: omitted-region bounds and minimum-count argument.
- design-check.py / design-check.json: frozen hash bindings, both-state/component complement metrics and symbolic costs.
- arithmetic-check.py / arithmetic-check.json: independent stored-metric/reconstruction/count assertions.
