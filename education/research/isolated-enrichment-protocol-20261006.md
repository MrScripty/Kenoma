# Isolated displacement enrichment and qualification protocol

This documented successor starts from diagnosis/evidence `645022c3c22a8b1b30b3928b668d583f0cb0c9d8`, qualified diagnosis source `401c306e1564be5dc82427193c159d1452f81787`, after main `596df78f5cb652b4ac70917a82d8aa908b617056`. Independent review supports the narrow omitted-direction diagnosis. Original sources, numerical states, unsuccessful physical gates and published book candidates stay unchanged. The input manifest binds 24 existing source/evidence files. The structural checker runs no nonlinear solve or constitutive evaluation.

Root authorization now permits **one smallest paired 45/46-mode response experiment** after protocol/source and structural preflight are frozen. Choose **FJ1486 brachialis**, the fixture with no embedded sheets; its existing empty sheet model is retained. Geometry, reference fibres, fitted sigma0 = 3,599,330.7341830498 Pa, activation = 1, mu = 1,000 Pa, bulk = 1,000,000 Pa, kf = 20,000 Pa, b = 6 and all other original law parameters remain fixed. No force rematching, target enforcement, pressure law, material fitting, contact, joint dynamics, mesh refinement or anatomy download enters this experiment. The protocol also defines later enrichment comparisons; execution authorization presently covers only the smallest pair.

## Documented correction: different state and different residual metric

The historical **0.0173851553295 N** number in `anatomical-further-integration.json` comes from the **coupled 0.10 s dense state**. The audit substitutes 2,048-point projected body gradients into the existing **coupled generalized incremental-gradient vector** and takes its infinity norm. That vector retains other coupled potential contributions, including the scaled joint's inertia, gravity, stop and damping terms. It is **not** the 1,485-component free nodal vector of an isolated specimen. Its 256-point coupled residual was 0.0000900055773 N. Both the state and residual space differ from the isolated diagnosis; those values are not a same-metric convergence comparison. This clarification supplements the frozen original report and JSON without rewriting them.

The isolated 256→2,048 maximum **component changes in the full free gradient vector** are 0.00710946946, 0.0888455081 and 0.0466920918 N, respectively: **71.09×, 888.46× and 466.92×** the unchanged **0.0001 N** gate. Their relative L2 changes are small beside the large defect, but integration is **not qualified at the absolute gate**. The old 45-mode coordinates themselves fail the 2,048-point projected gate. A comparison against the original 32-point fit would confound re-equilibration with enrichment.

## Spaces from the actual fixed mesh and caps

For each head, use its existing 252 conforming ten-node P2 tetrahedra, 585 global nodes, 112 vertex nodes and shared edge-midpoint identities. Let H be the explicit distal/proximal union (90 held nodes), F its complement (495 free nodes), and E_F insert free components into the full nodal vector with **exact zeros on H**. Complete six-node P2 cap faces must be held; checking only vertex nodes is insufficient. Lateral faces retain their natural boundary condition. No nodes are released by classifying a tiny mode coefficient as zero.

Let B_F be the actual original free rows of the 45 vector columns, free coordinate indices 9…53. The canonical admissible original variation space is

\[
V_0=\{E_F B_F z:z\in\mathbb R^{45}\}.
\]

The source is a Cartesian product of 15 scalar columns with three physical components. Exact dyadic row elimination confirms rank 15, hence rank 45, for these stored free columns. Let S be a selected subset of free P2 nodes and define

\[
T(S)=V_0+\operatorname{span}\{\phi_i e_a:i\in S,\ a=1,2,3\},
\quad \dim T(S)=3\bigl(|S|+\operatorname{rank} B_{F\setminus S}^{\rm scalar}\bigr).
\]

Here phi_i is the existing P2 nodal basis, not a P1 pressure or P1 displacement basis. Classify midpoint nodes using shared mesh edges and tetrahedral boundary faces, independent of observed force or compression. Add all free vertex nodes, then free midpoints whose edge touches either cap, then remaining lateral edge midpoints, then remaining interior midpoints. The sets are cumulative and inclusion follows directly from their spanning sets. All three existing fixtures give:

| Level | Added free nodes | Cumulative selected nodes | Vector dimension |
|---|---:|---:|---:|
| T0: original space | 0 | 0 | 45 |
| T1: P2 vertex axes | 80 | 80 | 285 |
| T2: cap-adjacent midpoint axes | 90 | 170 | 555 |
| T3: other lateral midpoint axes | 208 | 378 | 1,179 |
| T4: remaining interior midpoint axes | 117 | 495 | 1,485 |

There are 28 complete P2 cap faces per head. At the last level every free nodal axis is present, so T4 is the full fixed-mesh P2 field with those caps. No density or continuum limit follows from this finite sequence on one mesh. Orthonormal coordinates can use selected nodal unit vectors plus twice-orthogonalized remaining original-column tails. Preserve the original span and compare exact dyadic rank against numerical rank; **a mismatch blocks execution instead of silently dropping a direction**. Carry physical nodal fields between levels, record reconstruction error, and never treat arbitrary coordinate scaling as force convergence.

One boundary qualification is necessary. Raw FJ1478 has a cap coefficient 1.1546319456101628e-14 at node 519, base 45, and its saved cap position differs from reference by at most 2.220446049250313e-16 m. Literal preservation of that raw nonzero cap trace and exact zero cap variations are incompatible. V0 preserves **every original free-node column exactly** and enforces the stated complete cap condition; it does not claim literal preservation of the nonadmissible floating cap leakage. Original files are untouched. Any future long-biceps solve must first document the nominal-cap roundoff normalization and compare its frozen baseline numerically. Brachialis has no such leakage or cap-position difference, so the authorized pair avoids this boundary ambiguity.

## The paired 45/46-mode response

Use one frozen **2,048-point positive body rule**, the same reference gradients, fixed material constants, activation, caps and sheet embedding for both branches. Save the original failed pose first. Re-equilibrate **45 modes** under this rule, starting from the original fit, and retain the entire trace and any refusal. Record its independent full nodal gradient g_F and original projected gradient B_F^T g_F. Passing the latter does not imply g_F = 0.

Only if the declared projected solve succeeds with valid geometry, define and freeze

\[
r=(I-P_0)g_F,\qquad d=-r/\|r\|_2,
\quad V_{46}=V_0+\operatorname{span}\{E_Fd\},
\]

where P0 is the Euclidean orthogonal projector onto B_F. If the omitted norm is negligible, do not invent a direction; report that condition and the full gate. Check norm(d)=1, zero cap trace, independent added rank, near-zero B_F^T d and the actual derivative g_F^T d by two energy perturbation sizes. Direction selection is predeclared and occurs **once from the same-rule re-equilibrated 45-mode control**, not after examining a favorable 46-mode result. All earlier dry directions copied from the frozen diagnosis are labeled structural examples and cannot substitute for this production direction.

Initialize the 46-mode candidate at the **identical 45-mode physical field**, with the new coefficient zero. Retain the original 45 coordinates and add one coefficient in metres. Use the same bounded nonlinear algorithm, projected stationarity criteria, line-search/domain rules and iteration ceiling for 45 and 46 modes. Also replay the retained original-coordinate gradient for the 46-mode candidate. Report both projected and full residuals and **do not label either candidate full equilibrium unless its full free-node infinity norm passes 0.0001 N**. Trial refusals, rejected physical gates and the unadvanced old state must survive. Stop on unresolved geometry/domain failure, failed projected solve or detected unstable response; do not loosen the force gate or retune a physical parameter to continue.

The later nested response family can keep the frozen direction throughout: V0 subset V46 subset W1 subset W2 subset W3 subset W4, with Wl = T(S_l) + span(E_F d) and W4 = full P2. Dimensions may depend on whether d is already in a level; check rank rather than assume an increment. The existing failed-pose dry direction gives 46 → 286 → 556 → 1,180 → 1,485 in the structural check, **not future solved-state results**. One 46-mode result is a response experiment, not convergence.

## Metrics, work and tangent controls

For every original, control, candidate and failed state, save the physical nodal positions and the exact source/rule/basis identities. Independently assemble body plus sheet energy and nodal gradients. Report the following in declared units:

| Quantity | Required distinction |
|---|---|
| Original residual, max abs(B_F^T g_F), N | The historical 45-mode projected condition; keep the 0.0001 N gate. |
| Added-coordinate derivative d^T g_F, N | New response direction only; does not replace original or full residuals. |
| Full residual, max abs(g_F), N | 1,485 free nodal components; retain the same 0.0001 N full gate. |
| Norms of P_l g_F and (I-P_l)g_F, N | Euclidean, basis-invariant force-direction diagnostics; not spatial-error estimators. |
| Potential and components, J | Passive matrix/volume/fibre/sheet storage and fixed-activation active solve potential separately. |
| Virtual work g_F^T delta y_F, J | Specify the displacement in m; no physiological work or dissipation interpretation. |
| d^T H d and tangent checks, N/m | Analytic directional tangent and two gradient/energy differences; report sign, errors and branch crossings. |
| Reactions, N | Sum **full nodal** cap gradients; axial reaction uses the stored anatomical axis. Also retain the reduced conjugate reaction separately. No target force enforcement. |
| Local J, dimensionless | Minimum queried values/corner locations, sampled reference-volume fractions below 0.9, and global volume ratio separately. |
| Orientation | Exact dyadic P2 determinant certificate for both reference and current interpolants; no global injectivity assertion. |

At fixed activation, the potential derivative is the implemented residual. Along a differentiable **admissible** path, its gradient line integral equals the potential change by the chain rule; this is an arithmetic consistency check, not a physiological energy balance. A straight segment between orientation-positive endpoints is not automatically admissible. For finite probes and solver trials, retain domain/orientation refusals rather than integrating through invalid geometry. Active potential is a solve device, not passive storage. Fixed caps do no displacement work in this isolated fixture.

Tangent curvature should be measured along the added normalized direction at the 45-mode control and the final 46-mode candidate. Positive curvature in one direction does not prove a positive full tangent or stability. Constitutive/toe transition points need declared one-sided or piecewise checks, rather than an unsupported global C2 assumption. Numerical search regularization, if any, is recorded separately from material energy. A negative/indeterminate directional response is a failure to qualify the experiment, not a reason to adjust the bulk modulus.

## Separating integration, displacement resolution and nonlinear error

First compare the 45/46 pair at the **same 2,048-point potential**. Keep inner solver error visible and below the declared projected force criterion; report full residuals regardless. Then re-evaluate each saved state under 32, 256 and 2,048 points, without moving it. Compare the **same 1,485-component gradient**, projected gradient, potential components, nodal reactions and local J diagnostics. Frozen-state changes quantify integration sensitivity; they are not finer equilibria. Since 256→2,048 differences already exceed the absolute gate, even 2,048-point acceptance remains rule-specific unless an independently justified further integration/error check qualifies it. Do not call the finest available rule exact.

A later authorized comparison would re-equilibrate **each of the same two fixed spaces** under each frozen rule using identical loads/materials/caps and starting-state lineage; never change quadrature inside a Newton/line-search objective. Separate those solves from frozen-state reintegration. Re-solving at a finer rule addresses that rule's equilibrium, not fixed-mesh/full-nodal or continuum convergence automatically. Reaction differences are outcomes; do not fit sigma0 to erase them.

For a later spatial study, introduce a separately reviewed conforming mesh sequence, inherited geometry/cap/sheet maps, nested or explicitly tested transfers, consistent integration/error controls and a declared stable solution branch. Full-P2 results on the current mesh are only discrete references. Positive element orientation does not certify global injectivity; rank sufficiency does not certify mixed inf-sup stability, absence of locking or near-incompressibility. Keep finite K and the current active law unchanged in the present experiment.

## What nesting does and does not establish

At **one fixed potential and identical admissibility conditions**, nested feasible sets imply nonincreasing **global infima** by set inclusion. If attained, this orders global minimum potential values. It does not order computed local stationary states, full residuals, local compression, reactions, tangent spectra or physiological accuracy. If continuation accepts energy-decreasing steps from an exactly lifted old field, that run's decrease is an algorithm receipt, not a monotone convergence theorem. The historical six-coordinate coupled enrichment made compression worse despite projected stationarity; its source/evidence is retained.

No coercivity, unique stable minimizer, uniform nonsingular tangent, branch regularity, consistent quadrature limit or continuum approximation hypothesis has been established for this active nonlinear model. [Armijo's original 1966 paper](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-s.pdf) states specific differentiability, level-set and stationary-point conditions for its gradient-method theorem; a safeguarded Newton receipt does not inherit them. [Brezzi, Rappaz and Raviart (1980)](https://link.springer.com/article/10.1007/BF01395985) explicitly study nonsingular solution branches; only the publisher's primary abstract/metadata were accessible here, so no detailed theorem constants or applicability claim is taken from its restricted full text. These sources motivate stating assumptions, not a convergence claim for Kenoma.

## Reproduction and review artifacts

```sh
cd education
node --test tests/isolated_displacement_family.test.mjs
node tools/check-isolated-enrichment-protocol.mjs
```

The checker requires committed clean protocol sources, validates frozen input hashes, and refuses to overwrite a completed receipt. Outputs under `review/isolated-enrichment-protocol-20261006/` include compact structural/rank checks, the documented state-and-metric clarification, and a compact derived copy of existing 2,048-point free vectors/dry directions for API-readable independent review. The compact copy performs no new physical evaluation and never rewrites the large original result. Nonlinear response code/source/preflight/results will be separately identified before execution.

The accepted diagnosis concerns a large discrete force defect outside the restricted field. Authored educational anatomy, missing experimental architecture/conditions and physiological/calibration gaps remain explicit. No anatomical completion, release change or external publication is authorized by this protocol.
