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

## Historical accepted rest and rejected loading

[Open the anatomical apparatus viewer](anatomical-arm/index.html). It loads the accepted resting coordinates, recomputes the reduced force residual and audits the full boundary and routed axial paths. Three-dimensional rendering begins only when requested. Effort, mass, release, reset and trace export remain accessible through native controls and text readouts.

![Two copies of the same repaired reference anatomy at the same held elbow angle. Left: the equilibrated mechanical candidate, with gold axial tendon paths and teal shared guide scaffolds. Right: authored naive bone weights. Violet dumbbell glyphs are schematic point loads. No external skin is modelled.](assets/anatomical-arm-rest.png)

The original held rest has maximum free modal gradient **7.04 × 10⁻⁵ N**, zero audited transverse boundary crossings, zero routed axial-path violations and zero sampled body–bone or body–body penetration. Its minimum sampled body $J$ is approximately **0.99966**. The joint is held by an external support during this initialization; this is not a free loaded equilibrium. [Read the fresh rest recheck](data/anatomical-arm-v1/audit/arm-rest-recheck.json).

Before contact refinement, a 0.01 s step with effort 0.04 and a 0.5 kg point dumbbell reached the 120-iteration limit at **0.03408 N**, above the **0.0001 N** acceptance tolerance. A separate continuation attempt kept the original old state and step length fixed while increasing only the target effort. Its first quarter-load stage, effort 0.01, also stopped after 120 iterations, at **0.0003181 N**. A fresh independent evaluation reproduces both force residuals. It also finds 24 audited boundary-crossing pairs in the full-load candidate and 32 in the quarter-load candidate, with one axial tendon-path violation in each. Both numerical and geometric gates therefore reject these candidates. [Read the independent rejected-step recheck](data/anatomical-arm-v1/audit/arm-rejected-step-recheck.json). Intermediate candidates were never committed. These are observed solver and geometric failures, not evidence of a physical instability or a successful lift. [Inspect the loaded-step receipt](data/anatomical-arm-v1/audit/arm-trajectory-results.json) and [source-bound continuation result](data/anatomical-arm-v1/audit/activation-continuation-results.json).

## A small residual can miss a tendon crossing

An immutable earlier variant of the resting model converged to **9.17 × 10⁻⁵ N** and passed the body boundary checks. Yet one proximal long-biceps axial path entered and exited the source humerus through two distinct triangles. The interior interval along the path was **134.79 μm** and its midpoint lay **7.63 μm** inside the triangulated surface. All five material contact samples were outside; the nearest sample was about **1.893 mm** away.

This directly computed counterexample separates sampled contact from a full axial-segment audit. The interval is a path length inside the triangle mesh; it is **not cortical thickness**, a measured tendon shape or a clinical accuracy result. Its saved operator, geometry and routing inputs are immutable and hash checked. A fresh replay reproduces the converged force and rejected path. [Read the independent replay](data/anatomical-arm-v1/audit/rejected-rest-v1/replay.json).

The later weak proximal connective matrix and stronger reference routing clearance produce the accepted rest above. They remain authored changes with their own receipts; the older failure is preserved for comparison. The shared guide triangles themselves are interpolation scaffolds rather than resolved solids, so this candidate does not claim complete aponeurosis-solid contact.

## Resolve contact between material samples

A zero sampled penetration cannot overrule an intersecting triangle or axial segment. The two saved loading failures remain unchanged regression inputs: 24 brachialis/humerus crossing pairs and one common biceps tendon/ulna violation in each. The quarter-load candidate also has eight brachialis/short-biceps crossings, giving 32 total boundary-crossing pairs. The archived execution operators reproduce their original residuals. They are rejected coordinates, never accepted initial states.

The revised solver partitions each intersecting edge or axial leg at its source-surface entry and exit parameters. It queries each open interval midpoint and retains an interior point as a **material witness**. Muscle-side witnesses split the associated reference triangle; reciprocal bone-side witnesses split the bone triangle. Positive centroid and vertex quadrature weights preserve each original face's reference area. The same two-sided material cuts apply between two deforming muscle surfaces. A crossed tendon leg gains a material knot and positive trapezoidal side-area weights. Its one total-length tensile law, routing topology, insertion locations and rest length remain unchanged. Insertion endpoints remain exempt from the line penalty, while the full segment audit still checks every leg.

These partitions change only **between** nonlinear solves. A Newton gradient, Hessian and Armijo line search use one frozen material rule. Each candidate is audited again; a moved crossing generates another witness and another solve. Six refinement retries are allowed. Reaching the limit rejects the candidate. The force tolerance remains **0.0001 N**, the authored bone gap remains **0.15 mm**, and the full transverse surface and tendon-path gates remain mandatory. The muscle/muscle gap remains **0.30 mm**. No collision tolerance was widened. An extended fourth load increment also converged to **5.99 × 10⁻⁵ N** but had six brachialis/short-biceps crossings while every surface contact sample remained outside. The geometry gate rejected it. Its coordinates and operators remain a regression; the two-sided muscle witnesses now expose those crossings.

{{proof:contact-area-partition}}

A longer loaded state also exposed a corner in the body/body contact potential: two faces were equally close, and selecting just one normal could not supply balanced contact. The new outside-feature transition uses a **1 μm authored regularization width**, not a penetration tolerance. For unsigned feature distances $d_i$, compute

$$u=\min_{w_i\ge0,\;\sum_i w_i=1}\left[\sum_i w_i d_i+\frac{\varepsilon}{2}\left(\sum_i w_i^2-1\right)\right].$$

An isolated closest feature is unchanged. Near a tie, positive weights blend its gradients and include the derivative of the weights in the Hessian. Every triangle remains a distinct feature, including coincident shared-edge distances: merging features according to the current closest edge would change the simplex and introduce an energy jump. A saved cold-load edge transition tests independent energy differences across that change. The envelope satisfies $u\le d$, where $d$ is the exact unsigned minimum. The penalty gap is $u$ outside and $u-2d$ inside, so the regularized gap is never greater than the original signed gap. This strengthens contact; acceptance still queries the original signed distance and full triangles/segments. Inside-feature switches and continuous motion are not certified. The interrupted single-feature run and its loaded corner are retained in the audit package.

{{proof:conservative-contact-gap}}

The exact integer claim checks the area-partition numerator given the partition shares. It does not prove the geometric cut, floating-point weights, solver convergence or collision clearance. Regression tests separately check positive child areas, area conservation, activation of both previously missed contact types, analytic derivatives and serialized rule replay. Rules are stored with accepted states. A rejected step restores the old rule as well as leaving pose, activation, velocity and time unchanged.

A changed quadrature rule can change stored penalty energy at the old coordinates. The step receipt therefore reports `referenceQuadratureUpdateJ` separately. That numerical model-change event is not active muscle work. The existing work defect still includes quasistatic tissue-relaxation loss and nonlinear joint sampling; a small impulse residual does not establish energy conservation.

## Independently replayed loaded lift and release

The [saved 0.5 kg experiment](data/anatomical-arm-v1/audit/contact-lift-release-results.json) prepares a held rest with the witnessed rule, repeats the original 0.01 s, effort 0.04 load, then takes four further 0.03 s loading increments and ten 0.03 s release increments. Effort becomes zero at 0.13 s; activation decays with the recorded release time constant. Archived failed and previously accepted coordinates supply nonlinear initial guesses only. The old accepted state still defines inertia and activation. The primary experiment allows 240 Newton iterations per frozen rule; saved cold-start failures remain rejected rather than establishing universal convergence.

The [independent replay](data/anatomical-arm-v1/audit/contact-lift-release-recheck.json) invokes no optimizer. It freshly evaluates every saved force residual, full triangle and axial-path audit, activation update, joint impulse and mechanical-work ledger. All **15 accepted steps** have zero audited transverse boundary crossings, zero tendon-path violations and zero sampled bone, muscle or tendon penetration. The largest step residual is **8.88 × 10⁻⁵ N**, below the unchanged **0.0001 N** gate.

| Recorded event | Accepted time (s) | Elbow flexion (degrees) | Angular velocity (rad/s) |
|---|---:|---:|---:|
| Held initialization | 0.00 | 16.2783 | 0.0000 |
| End of commanded loading | 0.13 | 23.5813 | 1.7610 |
| Release peak | 0.34 | 39.3253 | 0.0049 |
| Final released state | 0.43 | 33.5261 | −1.6610 |

![Replayed elbow angle, activation and effort, force residual against the original gate, and minimum sampled body determinant for the 0.5 kg loaded lift and release. The dotted line marks release of commanded effort; every recorded pose passes full finite surface and axial-path audits.](assets/anatomical-contact-trajectory.png)

The arm rises **7.3030 degrees** during commanded loading, continues upward while activation decays, and falls **5.7992 degrees** from its peak during release. Final activation is **0.0002591**. The original viewer cache also succeeds on the first loaded step without a supplied coordinate guess: **3.93 × 10⁻⁵ N**, zero audited crossings and axial-path violations, with its stored rule independently replayed. Its 198 total Newton iterations span three frozen contact rules; the 120-iteration budget applies separately to each rule. The replayed nonlinear work defect reaches **2.4340 J** in magnitude; it is reported rather than forced to vanish. These CPU solves are not real-time browser performance evidence.

The smallest sampled body $J$ over the loaded/released states is **0.73754**. That substantial local compression, the fitted stress scales and the source articulation gaps remain visible limitations. A passing reduced trajectory does not establish full nodal convergence, finite-radius tendon clearance, coplanar or continuous-motion collision safety, measured anatomy or medical validity. The authored naive comparison continues to use exactly the same repaired reference anatomy and joint pose; it is not an independent mechanical solution.

A [finer-release comparison](data/anatomical-arm-v1/audit/contact-fine-release-recheck.json) starts from the same accepted 0.16 s state and uses 0.01 s increments. It was deliberately interrupted after **22 accepted steps**, at 0.38 s, rather than completing the requested 27 steps. The accepted prefix reverses, but differs from the primary 0.03 s schedule by as much as **3.2884 degrees** at their matched times through 0.37 s. This is observed timestep sensitivity with adaptive material rules, not evidence of timestep convergence or an accuracy bound. Its exact base, executed source hashes and interrupted receipt are retained.


## Compression and integration sensitivity at the saved poses

A subsequent [source-bound compression audit](data/anatomical-arm-v1/audit/anatomical-compression-sensitivity.json) independently assembles the full P2 body potential and projects its nodal gradients into the existing Galerkin modes. The original 32-point result agrees within **1.30 × 10⁻¹¹ N** in projected body gradients. All seven heads at the held pose and all 15 accepted states are evaluated with 4/32 integration; five selected poses additionally use positive 256-point integration and element-corner determinant queries. Saved coordinates, activation, fitted stress scales and contact rules are unchanged.

At the most compressed loading state, **0.10 s**, the minimum $J$ is **0.73754** at the original 32 points, **0.72527** at 256 points and **0.71234** at element corners. The frozen total reduced residual with 256-point body integration is **0.14451 N**, exceeding the unchanged **0.0001 N** gate. All four selected dynamic states fail that gate under 256-point integration at their frozen coordinates; the held state passes. This exposes integration sensitivity. It neither accepts a new trajectory nor establishes quadrature or full nodal convergence; the original replay remains acceptance under its declared 32-point potential.

Halving/doubling the authored 1 MPa bulk modulus at the same most compressed coordinates gives residuals of **14.3162/28.6325 N**. Geometry and $J$ remain unchanged. These are unbalanced parameter perturbations, not calibrated materials or re-equilibrated compression predictions. Re-equilibrated quadrature/material sensitivity and an enriched nodal solve remain open acceptance work. The existing timestep, articulation and finite-geometry limitations continue to apply.
