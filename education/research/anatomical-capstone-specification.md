# Exposed anatomical arm: implementation specification

This additive research branch replaces the capstone's independent scalar lifting torque with reactions from named mechanical tissues. It does not amend the production simulator scope under `docs/`. The anatomy and mechanics review guidance now supplies a workable engineering specification; patient-specific calibration is not a prerequisite for this educational milestone. Anatomical, numerical and biological acceptance remain separate.

## Geometry and evidence

The retained BodyParts3D right humerus (FJ3368), radius (FJ3349), ulna (FJ3391), brachialis (FJ1486), biceps short/long heads (FJ1512/FJ1478), triceps medial/lateral/long heads (FJ1480/FJ1477/FJ1479), and brachioradialis (FJ1487) are one shared atlas assembly. Original coordinates are metres, +X anatomical left, +Y posterior, +Z superior. No part is independently centred, registered to another dataset, or represented as a patient scan. Original OBJ notices and the current [BodyParts3D CC BY 4.0 notice](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) remain in `elbow-v1`.

`config/landmarks.json` retains original triangle/barycentric picks and their authored uncertainty. The original surface-pick axis is rejected and preserved in history. `audit/interior-axis-fit.json` records an interior circle fit to connected articular regions, an area-weighted normal-covariance axis, and an explicit finite collision-constrained centre search. The new centre is (-0.211000, -0.070235, 1.044410) m, direction (-0.954743, 0.103123, 0.278982), and bind angle 16.2783 degrees. This authored atlas-derived axis remains pending anatomical review. `audit/apposition-results.json` records zero transverse bone crossings at 25 tested poses, plus sampled articular distances. Finite poses, omitted cartilage, sampled distances and untested coplanar/containment cases do not establish a clinical or continuous-motion guarantee.

`config/attachments.json` now retains edge-connected source regions, original face IDs, face centroids, areas, area weights and outward normals. Humeral origins use broad anterior/posterior/lateral bands. Radial tuberosity is selected on the medial side; brachialis uses an anterior ulnar coronoid/tuberosity region; brachioradialis uses the lateral distal radius. These authored source selections require anatomical review. Seed points are for inspection only; actual distributed mechanical transfer must use the source face samples, not a whole-belly cap tied to a centroid.

`generated/arm-geometry.json` preserves three distinct welded, closed and consistently oriented bone surfaces. It derives seven separate reference belly volumes from original mesh cross sections. The authored first remesh uses seven longitudinal sections, sixteen perimeter vertices and a common non-convex triangulation (252 quadratic tetrahedra per belly). It rejects non-manifold source sections, missing common triangulations and nonpositive reference quadrature. Concave brachialis sections are preserved rather than filled by a radial fan through the humerus. The 25% peak-area cut, perimeter sampling and centreline fibre guides are **authored atlas-derived approximations**, not measured belly, tendon, aponeurosis or pennation architecture. Source outlines and region overlays remain available for review. Mesh refinement and surface discrepancy must be quantified before scientific acceptance.

Both biceps heads remain distinct. Their shared distal apparatus ending at the radial-tuberosity patch is specified but not implemented in this milestone. Brachialis uses a broad distal-anterior humeral origin and a deep ulnar fan/tendon. Triceps heads end at the olecranon; brachioradialis ends on distal radius. Their passive state must retain mechanical attachments and reactions. Fixed scapular origin estimates may be authored from the retained geometry; they must not be called measured coracoid/supraglenoid landmarks. Optional shoulder mesh acquisition failed at the proxy before any bytes transferred and is not a prerequisite. No external skin is added until a reviewed tissue envelope exists.

## One constitutive owner

For every accepted quadrature point, F=Ds Dm⁻¹, J=det(F)>0, λ=|F f0| and f0 is a normalized reference fibre guide. Use

\[
 W_{pas}=\frac{\mu}{2}(J^{-2/3}\operatorname{tr}(F^T F)-3)+\frac K2(\ln J)^2+
 \frac{k_f}{b^2}(e^{b e}-1-b e),\quad e=\max(\lambda-1,0).
\]

At fixed activation a, use exactly one active solve potential

\[
 U_{act}=a\sigma_0\int_1^\lambda f_L(s)\,ds,
 \qquad f_L(s)=\max(0,1-((s-1)/0.5)^2)^2.
\]

Derive P=∂(Wpas+Uact)/∂F and Cauchy stress PFᵀ/J from that same potential. Do not also add a preferred-length spring or a scalar series-muscle lifting torque. Uact is a fixed-activation optimization device, not stored passive energy or a metabolic estimate. Track active mechanical work independently. fV=1 in this milestone, so transient contraction speeds are not physiological predictions. This choice follows the finite-strain architecture distinction in [Blemker et al. (2005)](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf); it is not a reproduction or validation of that model.

Author the engineering fixture constants μ=1 kPa, K=1 MPa, kf=20 kPa, b=6 and λopt=1 at reference. Half/double sensitivity and bulk/mesh/quadrature sensitivity are mandatory receipts. σ0=0.3 MPa is currently only a material-test placeholder. Replace it with a documented fixed-end model-reference match separately for long biceps 624.3 N, short biceps 435.56 N and brachialis 987.26 N from the retained [Arm26 model](https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim). These are existing model parameters, not human measurements. Arm26 lumped tendon slack lengths and scalar pennation are not drawn tendon lengths or spatial fibre maps. Preserve its CC BY 3.0 notice independently.

Tendon/aponeurosis axial strain is ε=l/L0−1. Nominal stress is zero for ε≤0; E ε²/(2εtoe) in the toe region; E(ε−εtoe/2) above it. Integrate this stress for the stored energy, and use F=A0 stress. Initial E=50 MPa and εtoe=0.03 are authored engineering assumptions. Derive L0/A0 from recorded geometry choices, not Arm26 lumped lengths. Aponeurosis needs an explicitly weak transverse matrix; a tension-only axial network is a reduced intermediate, not a full aponeurosis solid. No compressive tendon force is allowed.

## Coupling, controls and acceptance

Fix shoulder and supination, retain one elbow-flexion q. Jointly minimize tissue coordinates and one implicit joint step:

\[
 \frac{I}{2h^2}(q-q_n-h\omega_n)^2+U_{pas}(x,q)+U_{act}(x,q,a_{next})+V_g(q)+U_{contact}(x,q).
\]

Any damping adds a documented D(q−qn)²/(2h). Differentiate actual attachment/contact maps with respect to q. Independently verify Q=Σ Bᵀf and transferred power. Count tissue mass once in segment inertia/gravity; omit local quasistatic tissue sag explicitly. A held-angle diagnostic has an external motor and reports its support reaction. No hidden pose clamp acts as support.

The fixture worker advances time and activation only after a converged solve, warm starts, uses analytic gradients and Hessian-vector products with energy-decreasing steps, and rejects determinant violations. Failed steps preserve state; automatic step subdivision is not yet implemented. Quadratic displacement tetrahedra and positive four-point/refined-32-point quadrature are the initial choice. Assess locking through mesh/quadrature/bulk sensitivity; use a stable mixed formulation if necessary, without silently reducing K. The 150–300 element budget is a profiling hypothesis rather than an accuracy promise.

Primary controls are effort/excitation and dumbbell mass. Activation, tissue tension, angle, fibre stretch/length, volume and residuals are outputs. Mass and release preserve the dynamic state, with a separately reported energy event for a mass change. Reset is deterministic. Skin-weighting comparison eventually uses the same accepted assembled anatomy and pose.

Acceptance proceeds through mesh/patch review; objective stress derivatives; fixed-end, free/loaded-shortening and passive-stretch fixtures; slack continuity; attachment resultant/moment/power; locking and refinement sensitivity; actual tissue-driven joint trajectories; full supported-pose surface intersections; then mobile controls and coherent book/PDF regeneration. Existing compiled Lean claims stay narrow. New exact distributed-transpose identities must compile and link to the actual mapping; they cannot certify floating-point solutions, anatomy or biology. The book's old strip example remains an explicitly intermediate lesson until this replacement passes review.

## Current reproducible receipts

`node tools/build-anatomical-geometry.mjs` writes source-backed geometry and quality receipts without downloads. `node tools/build-anatomy-inspector.mjs` builds a local interactive source/region/remesh viewer. `node --test tests/anatomical-material.test.mjs tests/anatomical-element.test.mjs` checks the implemented constitutive and element laws. These do not yet constitute a coupled anatomical arm, an accepted tendon architecture, human calibration, or a published replacement capstone.


## Coupled fixture and compiled mathematics milestone

`web/anatomical-coupled-fixture.mjs` jointly solves an actual 27-node, six-P2-tetrahedron block, nine distributed tensile branches and one rigid hinge. Tendon energy supplies all tissue hinge torque. This is an engineering fixture, not the anatomical apparatus. `audit/coupling-results.json` preserves loaded/released coordinates, torque/work residuals, three step sizes and unchanged-material matched L-BFGS/Newton profiles. Newton's reference-elasticity Cholesky preconditioner is appropriate to this small fixture; seven-belly scalability remains unproved.

`CoupledMechanics.lean` compiles seven exact integer-numerator claims: `impulse_balance`, `kinetic_increment_identity`, `implicit_kinetic_work_balance`, `implicit_dissipation_numerator_nonnegative`, `mass_event_work_numerator`, `tendon_toe_energy_numerator_nonnegative`, and `quadratic_partition_numerator`. The two prior attachment transfer identities also compile. The 21 total book cards link the actual source, fresh receipts, assumptions and limitations; the new claims do not certify constitutive gradients, JavaScript arithmetic, anatomical attachments, biology or whole-system energy conservation. The measured nonlinear work defect remains visible.

The book adds one coherent coupled-mechanics chapter and demotes the old strip from requested-capstone status. Skin remains absent from the new fixture and anatomical inspector. Full anatomical assembly, explicit shared tendon/aponeurosis transfer, remesh/bone clearance correction, contact and the anatomy-matched skinning comparison remain required.
