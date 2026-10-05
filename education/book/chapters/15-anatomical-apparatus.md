# Build an anatomical apparatus that can fail a check {#anatomical-apparatus}

The synthetic block in the previous chapter isolates coupling. The anatomical candidate instead connects **seven separate atlas-derived muscle volumes**, the humerus, radius and ulna, and two shared distal apparatuses. Its architecture is authored from source surfaces. It is not a measured tendon or fascicle segmentation, a subject-specific arm, or a clinically validated model.

The candidate keeps the source bones in their original shared coordinates. It repairs local intrusions of the derived belly reference volumes by recorded transverse ring translations, then reconstructs every quadratic midside node. The largest correction is 7.4132 mm in the medial triceps. Prism shape and reference volume are preserved to the reported numerical tolerance. The repair audit checks positive cell orientation, positive 32-point volume quadrature and finite boundary crossings. This geometric repair is separate from a constitutive law or a solved contact response.

[Inspect the complete reference-repair receipt](data/anatomical-arm-v1/audit/reference-repair.json). The original atlas and original remesh remain in the package, so a reader can reconstruct the before-and-after result.

## From a volume to a distributed attachment

Each head has 63 Galerkin displacement coordinates: seven longitudinal hats multiplied by a constant and two transverse affine features, in three displacement directions. Those coordinates act on the quadratic tetrahedron nodes and on 32 positive quadrature points per tetrahedron. This retains a volumetric energy and non-affine deformation while making the browser experiment smaller. A small reduced residual establishes equilibrium only in these 63 modes; it does not establish full nodal FEM convergence.

Both biceps heads meet the **same nine free distal guide coordinates**. Both contribute force to a common three-node sheet, which also receives the common distal tendon force from the radial-tuberosity face samples. All three triceps heads similarly meet one common apparatus ending on the olecranon patch. The weak transverse matrix and tensile fan laws are explicit approximations. Common distal branch area totals 20% of its candidate insertion patch. Each head fan totals 20% of the smaller of its cap area and that already scaled common area divided by head count; these fractions are authored, not measured tendon areas. They do not turn one free triangle into a resolved anatomical aponeurosis solid.

Within the biceps volumes, authored proximal-posterior and distal-anterior strips transmit axial force through embedded barycentric points. Their thickness, inset, transverse matrix and tensile properties are recorded engineering choices. The architectural motivation is the primary three-dimensional muscle study by [Blemker, Pinsky and Delp (2005)](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf); the present geometry and material law are not a reproduction of that study.

Broad humeral origins use individual source-patch faces and nearest points on the associated belly boundary. The previously shared medial/lateral triceps origin faces have exclusive ownership in the candidate configuration. This partition is an authored septum surrogate, not a measured anatomical border. The estimated proximal fans also have a weak connective-matrix boundary, using the recorded 1 kPa matrix scale, an authored 1 mm local interface thickness and a finite rest offset. This boundary compliance is separate from the routed tendon length. This authored restraint supports matrix compression when the separate axial tendon is slack; it is not a resolved tendon matrix or a measured attachment. Estimated scapular origins retain a 15 mm uncertainty radius and remain labelled estimates. They are not measured coracoid, supraglenoid or infraglenoid landmarks.

{{proof:shared-guide-balance}}

## A tendon path has one total length

A straight branch may cut through cortex even when both ends are outside bone. The reference routing tool therefore checks every axial segment against the closed source bones and adds authored frictionless polyline guides where needed. It records any estimated-origin projection separately and rejects corrections outside the established uncertainty radius. The source bone surfaces are unchanged.

For path points $x_0,\ldots,x_n$, use one total length and one integrated tensile law:

$$L=\sum_{i=0}^{n-1}\|x_{i+1}-x_i\|,\qquad W_t=W_t(L;L_0,A_0),\qquad T=\frac{\partial W_t}{\partial L}.$$

Every leg carries the same $T$. A fixed guide carries a support reaction and has zero prescribed-motion work. A guide attached to a rotating forearm bone contributes its force through the exact point Jacobian to elbow torque. The objective gradient and Hessian include all legs and the second derivative of rotating attachment points. The code never substitutes an independent scalar muscle torque for these attachment forces.

The fixed guide topology is a substantial limitation: it does not simulate sliding tendon wrapping, friction, finite tendon radius or measured retinacula. Finite line-contact quadrature and the complete segment audit are separate checks. A later pose that cuts cortex fails the acceptance gate. Passing the reference path audit alone is insufficient for a dynamic lift.

## Force matching exposes a material limitation

The fixed-end matching experiment equilibrates 45 interior modes at full activation; both end rings remain fixed. It matches the independently sourced Arm26 model-reference actuator forces within $10^{-4}$ relative error. These are actuator-model targets, not measured forces of the atlas subject. The fresh recheck recomputes the forces with the current operators.

| Head | Model-reference force (N) | Fitted stress scale (MPa) | Minimum local $J$ | Global volume ratio |
|---|---:|---:|---:|---:|
| Brachialis | 987.26 | 3.59933 | 0.59490 | 1.04781 |
| Biceps short | 435.56 | 8.70839 | 0.63832 | 1.02382 |
| Biceps long | 624.30 | 20.37812 | 0.63460 | 1.02796 |

These fitted scales and large local volume losses **do not establish medically credible material properties**. A nearly preserved global volume can coexist with substantial local compression. The shear, bulk and passive-fibre laws were kept at their recorded teaching values; the matching routine did not silently raise the bulk modulus to hide this result. A coupled pose using these scales must report its local $J$, force residual and contact checks. The numerical target match is an educational stress test, not a biological validation.

[Fresh fixed-end recheck](data/anatomical-arm-v1/audit/modal-fixed-end-recheck.json) · [Full fitting history](data/anatomical-arm-v1/audit/modal-fixed-end-results.json).

## Joint dynamics, release and an external mass event

The atlas frame has **+Z superior**, so gravitational potential is $+mgz$. Segment mass and inertia come from the pinned Arm26 rigid-segment model; their mapping to the atlas grip direction is authored. Local tissue sag is omitted. Segment tissue mass is counted once in the rigid segment rather than added again as separate deformable-body mass.

For a step of length $h$, solve tissue, shared guides and the joint coordinate together in the incremental potential:

$$\Phi(x,q)=W_{\mathrm{body}}+W_{\mathrm{tendon}}+W_{\mathrm{interface}}+W_{\mathrm{contact}}+V_g(q)+\frac{I}{2h^2}(q-q_n-h\omega_n)^2+\frac{d}{2h}(q-q_n)^2+W_{\mathrm{stop}}(q).$$

The declared end-stop energy acts outside 0–120 degrees; it is not a hidden pose clamp. Activation follows an analytic first-order update with distinct authored activation and release time constants. Only an accepted nonlinear solve and accepted geometric audits commit the activation, pose and time. A failure retains the prior state.

An effort change preserves pose, velocity, tissue coordinates and activation until the next accepted step. A mass change preserves those quantities and records

$$\Delta E_{\mathrm{external}}=\Delta m\left(\tfrac12 r_\perp^2\omega^2+gz_{\mathrm{grip}}\right).$$

This is external handling work in the point-mass model. It is not metabolic muscle work or a complete model of a person exchanging a dumbbell.

{{proof:upward-mass-event}}

The mechanical-work ledger reports active-potential work, passive/contact storage, gravity, joint kinetic energy, damping and the implicit kinetic defect separately. Its remaining defect includes **quasistatic tissue-relaxation loss and nonlinear joint sampling**. It must not be presented as pure floating-point error or exact conservation of a fully dynamic tissue system.

## Compare the same anatomy at the same pose

The naive comparison applies an authored longitudinal bone weight to the **same repaired reference nodes** at the **same joint angle**. Its deformation gradient is derived from that weight field and checked against independent quadratic interpolation. It reports local determinant and signed volume rather than merely showing a plausible surface. It supplies no muscle force, equilibrium or contact law. There is no separately modelled skin envelope in either view.

The reference rig also has a persistent source articulation limitation: the restricted radial-head/capitellum audit reports median gaps of about 5.80 mm at 0 degrees and 8.74 mm at 90 degrees. Those unsigned patch distances are not cartilage thickness or acceptable joint apposition. The source bones were not silently registered to close the gap. [Read the restricted patch-distance audit](data/anatomical-arm-v1/audit/radial-apposition-results.json).

## Accepted rest, rejected loading

[Open the anatomical apparatus viewer](anatomical-arm/index.html). It loads the accepted resting coordinates, recomputes the reduced force residual and audits the full boundary and routed axial paths. Three-dimensional rendering begins only when requested. Effort, mass, release, reset and trace export remain accessible through native controls and text readouts.

![Two copies of the same repaired reference anatomy at the same held elbow angle. Left: the equilibrated mechanical candidate, with gold axial tendon paths and teal shared guide scaffolds. Right: authored naive bone weights. Violet dumbbell glyphs are schematic point loads. No external skin is modelled.](assets/anatomical-arm-rest.png)

The current held rest has maximum free modal gradient **7.04 × 10⁻⁵ N**, zero audited transverse boundary crossings, zero routed axial-path violations and zero sampled body–bone or body–body penetration. Its minimum sampled body $J$ is approximately **0.99966**. The joint is held by an external support during this initialization; this is not a free loaded equilibrium. [Read the fresh rest recheck](data/anatomical-arm-v1/audit/arm-rest-recheck.json).

A 0.01 s step with effort 0.04 and a 0.5 kg point dumbbell reached the 120-iteration limit at **0.03408 N**, above the **0.0001 N** acceptance tolerance. A separate continuation attempt kept the original old state and step length fixed while increasing only the target effort. Its first quarter-load stage, effort 0.01, also stopped after 120 iterations, at **0.0003181 N**. A fresh independent evaluation reproduces both force residuals. It also finds 24 audited boundary-crossing pairs in the full-load candidate and 32 in the quarter-load candidate, with one axial tendon-path violation in each. Both numerical and geometric gates therefore reject these candidates. [Read the independent rejected-step recheck](data/anatomical-arm-v1/audit/arm-rejected-step-recheck.json). Intermediate candidates were never committed. These are observed solver and geometric failures, not evidence of a physical instability or a successful lift. [Inspect the loaded-step receipt](data/anatomical-arm-v1/audit/arm-trajectory-results.json) and [source-bound continuation result](data/anatomical-arm-v1/audit/activation-continuation-results.json).

## A small residual can miss a tendon crossing

An immutable earlier variant of the resting model converged to **9.17 × 10⁻⁵ N** and passed the body boundary checks. Yet one proximal long-biceps axial path entered and exited the source humerus through two distinct triangles. The interior interval along the path was **134.79 μm** and its midpoint lay **7.63 μm** inside the triangulated surface. All five material contact samples were outside; the nearest sample was about **1.893 mm** away.

This directly computed counterexample separates sampled contact from a full axial-segment audit. The interval is a path length inside the triangle mesh; it is **not cortical thickness**, a measured tendon shape or a clinical accuracy result. Its saved operator, geometry and routing inputs are immutable and hash checked. A fresh replay reproduces the converged force and rejected path. [Read the independent replay](data/anatomical-arm-v1/audit/rejected-rest-v1/replay.json).

The later weak proximal connective matrix and stronger reference routing clearance produce the accepted rest above. They remain authored changes with their own receipts; the older failure is preserved for comparison. The shared guide triangles themselves are interpolation scaffolds rather than resolved solids, so this candidate does not claim complete aponeurosis-solid contact.

The anatomical arm remains a research candidate until its actual coupled lift, release, compression and same-pose comparison have independently checked receipts and visual review. The source geometry, equations, failing material checks and compiled integer claims are available for inspection while that acceptance work continues.
