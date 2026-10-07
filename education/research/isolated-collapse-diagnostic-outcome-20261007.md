# Saved-state diagnosis: local resistance, global descent and unresolved quadrature

The refused run is preserved. This bounded diagnostic evaluated only three exact saved valid fields, without solving, advancing coordinates, refitting force, changing parameters or evaluating a rejected candidate. **The evidence identifies a combination of localized geometry, globally coupled restricted directions and underresolved integration; it does not identify smaller line fractions as a solution.** The implemented bulk law resists local compression. Its aggregate energy decrease is not evidence that it favors the collapsing corner.

Source/protocol: `e28ab8be8ed1403f4c3034f88191b6d698421cb3`, based directly on refused-run evidence `713d74645a32fc24c02b71a7879d90dabd93441c`. Diagnostic data and arithmetic-summary source: `f546d5fb67f2aed816c0df42d4b5ba5d91c5dab6`. There were **2,844,788 diagnostic material-point evaluations**, below the frozen3,000,000 ceiling, and zero optimizer trials/solves, refits, model changes or field advancement. Five helper tests pass. Component stresses add exactly to the existing Piola stress at all evaluated points; saved full-free force replay differs by at most1.13e-12 N and component energies by about3.2e-11 J, below the declared replay checks. The raw refused result SHA256 remains `d781d7a68cd742b4019ae89d5464109d42b758e8f30419341b5ee55421e1406d`.

**Review limit:** the parent independently acknowledged the refusal and targeted witnesses, but did not independently replay the full50.6 MB raw result or55 additional material-gate certificates. Prior reproduction of those inventories was this agent's own verification. This new diagnostic also awaits independent review; it does not expand that review coverage by assertion.

## What is actually implemented

For dimensionless deformation gradient F, normalized reference fibre f0, J=det(F), I1=F:F, full fibre stretch lambda=|F f0| and e=max(lambda−1,0), the existing reference-volume densities are:

- Isochoric matrix: `W_matrix = mu/2 * (J^(-2/3)*I1−3)`.
- Finite-bulk volume: `W_volume = K/2 * (log J)^2`.
- Passive fibre: `W_fibre = kf/b^2 * (expm1(b*e)−b*e)`; tension only.
- Active solve potential: `W_active = a*sigma0*C(lambda)`, with C the existing primitive of the compact-support active curve. This is a fixed-activation solve device, not passive stored energy.

The corresponding first Piola terms are the derivatives of these densities. In particular `P_volume=K*log(J)*F^(-T)` and `P_matrix=mu*J^(-2/3)*(F−I1/3*F^(-T))`. Fibre/active stresses use the full transported fibre direction, not an isochoric fibre stretch. Their sum reproduces the existing material source, including the original guard. External energy/force is **exactly zero in this isolated objective**: no applied target-force work, gravity, inertia, arm contact or tendon potential. Its checked sheet fixture has zero branches/strips. Fixed caps generate constraint reactions, not an added external potential.

W and P have units Pa (W is J/m³ of reference volume); reference weights are m³ and reference shape gradients1/m, giving nodal/generalized energy gradients in N. Coordinates/increments are m and virtual work is J. Component quantities below are energy gradients; physical internal nodal forces carry the opposite sign. No SI conversion mismatch was found in this source/replay.

The authored config supplies mu=1000 Pa, K=1,000,000 Pa, kf=20,000 Pa, b=6, optimumStretch=1 and activeWidth=0.5. Activation is1 and the implemented velocity multiplier is1. Sigma0=3,599,330.7341830498 Pa is the historical45-free-mode,32-point fixed-end fit, replacing the300,000 Pa placeholder. The target987.26 N is the Arm26 BRA actuator's `max_isometric_force`; the old achieved987.2744117188512 N is a numerical restricted-space fit. Sigma0/K=3.59933 and sigma0/mu=3599.33 are model ratios, not measured tissue properties or medical validation. They deserve re-examination after discretization/model qualification, not silent retuning.

## Where the geometry collapses and what quadrature sees

Exact reference/current Bernstein coefficient ratios prove that the last valid field's **global minimum J is attained at element247, corner0, free node92**. Its exact rational value is approximately1.300982206042835e-6; the old floating corner query is1.3009819920047246e-6. Positive reference coefficients express J as a convex combination of their ratios; the smallest ratio is a pure-corner value, so the bound is attained. The adjacent formerly implicated elements250/251 have minima0.08555/0.24154, far above this corner.

Element247 is next to the proximal fixed cap: vertices109 and111 are held, while92 is free. Node92's reference position is `[-0.2081267604,−0.0790677480,1.1618222583] m`; current/control locations and connectivity are in the summary. The16 elements incident to92 occupy about**1.8105%** of reference volume; element247 alone occupies**0.03550%**, about2.31003e-8 m³. The exact inward barycentric J derivatives at the critical corner are positive:2.171995,0.926740,2.193105. The observed minimum is localized at a vertex, not a whole-cell uniform volume loss.

| Last-valid point | J | Full fibre stretch | Matrix density, Pa | Volume density, Pa | Reference integration weight, m³ |
|---|---:|---:|---:|---:|---:|
| Actual corner | 1.30098e-6 | 2.135212 | 2.35411e7 | 9.18337e7 | 0 |
| Nearest original2048 point | 0.0913917 | 2.136005 | 1.23337e4 | 2.86227e6 | 1.12794e-11 |

The nearest original point is about0.95754 mm away in reference geometry, at barycentric coordinates `[0.9481763,0.0172746,0.0172746,0.0172746]`. Its J is **70,248 times** the corner value. Corners receive zero weight in the old integral. The corner's matrix/volumetric Piola norms are about2.62e13/2.26e13 Pa; both local directional density derivatives strongly oppose the recorded terminal Newton increment. This is numerical material evaluation at the saved valid corner, not an added contribution to the old quadrature.

Crucially, the corner's fibre stretch is above1.5, outside the active curve's support. **Active stress is zero there**; its active primitive is saturated. The sampled element247 active potential is unchanged across these states. Thus the body's active energy reduction cannot be identified as direct active contraction at this corner. The near-cap fibre is stretched while J collapses, consistent with localized transverse flattening/shear; J loss is not simply fibre shortening.

## Directional evidence: patch versus whole body

The following are component derivatives along the **saved terminal scaled Newton nodal increment**, before any fraction is applied. They are local derivatives in J, not energies of an unexecuted new field.

| Term | Whole body, J | Node92 incident patch, J |
|---|---:|---:|
| Matrix | +0.000290404 | +0.000037070 |
| Volume | −0.070513005 | −0.004693810 |
| Passive fibre | −0.020445436 | +0.002014523 |
| Active potential | −0.165450682 | −0.004489862 |
| External | 0 | 0 |
| Total | **−0.256118719** | **−0.007132080** |

The rest of the body contributes−0.248986639 J. Local positive bulk/matrix resistance near the corner is outweighed by relaxation and active-potential decrease elsewhere under this globally coupled direction. Under the declared corner-graded rule, element247's volume derivative is **positive**, about+0.002308677 J, reinforcing the local-resistance finding.

From control to last valid, aggregate changes are active−0.232800 J, volume−0.113787 J, fibre−0.021468 J and matrix+0.000279 J. Even element247's integrated volume energy falls by0.002142425 J while its corner volume density rises from85,671 Pa to91,833,654 Pa: other spatial parts of that element relax enough to offset the tiny corner region. The element's passive fibre energy rises slightly; active energy is unchanged. Element-level inventories locate the positive and negative changes, so totals are not used as local causal evidence.

The once-selected extra direction exactly captures the original control's omitted gradient by construction. After deformation the full gradient rotates outside the fixed46-space: outside46 L2 grows from about3.75e-12 N at control to64.21546 N after the first step and **140.50001 N** at the last valid state. Full-free L2 is352.16854 N. This verifies loss of representational sufficiency as the field changes. It does not prove that adding arbitrary modes would cure the collapse; the failed projected/full gates and geometry limit still apply.

## Local refinement finds nonconvergence

The declared saved-control/final comparison leaves all elements outside the16-element incident patch at2048 points. Stage4 uses16,384 points on every patch element; stage5 raises only247 to131,072, keeping the other15 at16,384.

| Fixed field and diagnostic rule | Max full-free gradient difference from original2048, N | Full-free maximum, N | Original45 maximum, N |
|---|---:|---:|---:|
| Control, stage4 | 0.000523 | 64.066837 | 0.000137747 |
| Last valid, stage4 | 0.472970 | 57.102527 | 1.090436 |
| Last valid, stage5 | 0.615770 | 57.245327 | 1.092155 |

The unchanged physical gate is1e-4 N. Even the control's refined original45 residual fails it. Final gradient changes are thousands of gates; energy differences are only around1e-6 J, so energy agreement alone would conceal a force-resolution problem. Stage5 still samples minimum J≈0.022853 in247, far above the actual corner. It does **not** establish global quadrature convergence or a new equilibrium.

Grading the original corner cell to depths6/10/14/18 lowers the sampled J to0.0114277/0.000715474/0.0000459369/0.00000409073. At depth18 its closest weight is about3.2e-25 m³. That isolated corner contribution appears to stabilize across the deepest graded levels, while the uniform incident-patch force remains unresolved. The graded rule retains coarse original subcells elsewhere; it cannot qualify the entire nonlinear integral. The refined whole-body terminal derivative remains negative, about−0.256071776 J at stage5. Refinement exposes significant error but does not reverse the observed global descent balance within this bounded diagnostic.

## Mechanism and a correction proposal for separate review

The evidence supports three simultaneous mechanisms: a finite-bulk constitutive objective trading spatial compression/dilation and global active/passive energy; a fixed restricted direction coupling broad relaxation to a localized near-cap pinch; and quadrature that underrepresents the highly concentrated corner stresses. There is no verified external-load or SI-error explanation. The data cannot isolate one parameter as the cause, establish a fully resolved equilibrium or predict the outcome of a different space/model.

Pointwise divergence of the existing density as J approaches zero is not itself a proof of an infinite integrated barrier against an isolated corner collapse. For a conditional linear-corner pattern `J~r` with bounded F, the local volume integral scales as `integral r^2*(log r)^2 dr` and matrix energy as `integral r^(4/3) dr`; both are finite near zero. The positive inward slopes measured here support that local geometry, but this asymptotic observation is not a new evaluated limiting field or proof of a global solution. The finite-bulk law is not a constraint enforcing incompressibility.

A justified next research protocol should first qualify component forces and directional derivatives under fixed-field integration and a declared resolved displacement space, including the cap-adjacent region. Energy agreement and model-target matching are insufficient. If the intended tissue assumption requires tight local volume preservation, review a formulation with an explicit physically justified local volume constraint/pressure treatment and consistent energy, gradient and tangent, rather than treating this numerical1e-6 guard or a larger arbitrary bulk value as validation. Its compressibility and active-length assumptions, geometry and calibration must be reviewed together. Re-establish any stress fit only after those choices and discretization qualify; retain the old fit as historical evidence. No new formulation, parameter value, mode set, optimizer run or refit is implemented or authorized by this proposal.

Smaller fractions cannot cure the demonstrated integration deficit, growing omitted force or missing physical volume constraint. The old21-fraction stop and all original force/geometry failures remain unchanged. Any next experiment requires a separately frozen and reviewed protocol.

Evidence: [compact summary](../review/isolated-collapse-diagnostic-20261007/diagnostic-summary.json), [receipt](../review/isolated-collapse-diagnostic-20261007/diagnostic-receipt.json), [pointwise corner](../review/isolated-collapse-diagnostic-20261007/pointwise-corner.json), [exact neighborhood](../review/isolated-collapse-diagnostic-20261007/exact-corner-neighborhood.json), [component forces](../review/isolated-collapse-diagnostic-20261007/last-valid46-components.json), [patch refinement](../review/isolated-collapse-diagnostic-20261007/patch-quadrature.json), [graded corner](../review/isolated-collapse-diagnostic-20261007/graded-corner.json), [parameter provenance](../review/isolated-collapse-diagnostic-20261007/parameter-provenance.json). Every machine receipt is below1 MiB. No PR, merge, deployment, credential/protection change or book adoption occurred.
