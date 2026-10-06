# Skin must follow motion without losing the mechanics

The skeleton, muscles, surrounding soft tissue and visible skin are different representations with different jobs. A practical arm may use rigid bodies for bones, lines for musculotendon force, a volumetric proxy for tissue, a surface for contact and a detailed mesh for rendering. Correct coupling is the map that makes those representations agree about positions, forces and work.

## 1 Why linear blend skinning can collapse

For rest vertex **X**ᵢ, bone transforms **T**ⱼ(q), inverse bind transforms **B**ⱼ⁻¹ and normalized weights wᵢⱼ,

$$\mathbf x_i=\sum_j w_{ij}\,\mathbf T_j(\mathbf q)\mathbf B_j^{-1}\mathbf X_i,
\qquad w_{ij}\ge0,\quad\sum_jw_{ij}=1.$$

Use homogeneous coordinates for the affine transforms. At the bind pose, **T**ⱼ**B**ⱼ⁻¹ must be identity in the chosen convention. A rigid transform preserves lengths and volume. An average of rigid transforms generally does not.

An original local demonstration makes the failure quantitative. Blend identity with a rotation R_z(θ), with equal weights and a shared pivot. The linear part is

$$\mathbf A=\tfrac12(\mathbf I+\mathbf R_z(\theta)).$$

In the plane perpendicular to the axis, **A** is a rotation by θ/2 multiplied by cos(θ/2). Along the axis it leaves length unchanged. Consequently,

$$\det\mathbf A=\cos^2(\theta/2).$$

At θ = 90 degrees the transverse scale is about 0.707 and this affine patch has half its original volume. At 180 degrees the transverse plane collapses. This is an analytic property of this deliberately constructed blend, not a claimed percentage volume loss for a complete human elbow. Spatially varying weights contribute additional derivatives to the whole deformation, and ordinary elbow bending also involves different pivots and translations.

**Reader implementation exercise — unfinished in this edition.** Show a weighted cylindrical patch with a wireframe cross-section. Freeze the weights and move only the bones. Then highlight the inner elbow crease in the full arm and display the measured local triangle distortion and any actual intersections. Do not infer intersections from a dark crease in the shading.

[Ladislav Kavan and colleagues' dual-quaternion work](https://users.cs.utah.edu/~ladislav/kavan07skinning/kavan07skinning.html) is an important alternative baseline. Blending rigid transforms through dual quaternions avoids the simple linear-matrix collapse demonstrated above. It does not enforce tissue constitutive response, global volume conservation or self-collision. It can still produce unwanted bulging, pose-dependent geometry and contact failures.

## 2 Geometry needs a collision definition

A contact model needs to specify what touches what, where the boundary lies, and whether thickness is included. Candidate pairs may include tissue-bone, muscle-muscle, skin-skin and skin-object. A signed-distance field can cheaply provide a gap to a rigid bone proxy, but its voxel resolution, sign convention and interpolation error matter. It does not by itself detect every triangle-triangle self-intersection of the skin.

For a gap g ≥ 0, an ideal frictionless normal contact has

$$g\ge0,\qquad\lambda_n\ge0,\qquad g\lambda_n=0.$$

At separation the normal reaction vanishes; at contact it can be compressive but not adhesive. Adhesion is a different model. With Coulomb friction,

$$\|\boldsymbol\lambda_t\|\le\mu_f\lambda_n,$$

with stick/slip conditions and dissipation defined consistently. μ_f is a friction coefficient, not the shear modulus μ. Normal and tangential multipliers must share compatible units and normalization before applying a friction cone.

Penalties, complementarity solvers, projection and barriers are alternative numerical treatments. A finite penalty usually permits some penetration; making it stiff can worsen conditioning or restrict explicit time steps. Discrete endpoint tests can miss objects passing through each other between frames. Continuous collision detection examines the swept motion and must be paired with a response that preserves feasibility.

[Incremental Potential Contact](https://ipc-sim.github.io/) combines barrier-based contact with conservative collision handling in a variational implicit framework. Its intersection/inversion-free claims rely on its stated feasible-start and algorithmic conditions. Do not apply that guarantee to an arbitrary log penalty, an intersecting initial mesh or a few endpoint projection sweeps. It also does not establish that a tissue law or friction coefficient is biologically correct.

**Reader implementation exercise — unfinished in this edition.** Push two soft pads together, then slide one. Plot normal force, tangential force, contact area and dissipated work. Repeat with contact disabled. This separates the material's deformation from the contact algorithm that prevents overlapping bodies.

## 3 Skin and flesh are not necessarily glued together

A render mesh embedded in tetrahedra with barycentric coordinates follows a coarse volume, but embedding alone supplies no separate skin mechanics. A membrane or shell layer can have its own in-plane and bending response. Sliding relative to the underlying tissue requires a declared interface model rather than every skin vertex being welded to its nearest muscle particle.

At one extreme, hard attachment transfers all components of motion. At another, frictionless contact permits tangential slip while preventing normal penetration. Between them are compliant attachments, friction and spatially varying connective constraints. Use a small sliding patch experiment before choosing the arm's interface assumptions.

[Pai et al., The Human Touch](https://www.cs.ubc.ca/research/HumanTouch/HumanTouchSIGGRAPH2018.pdf), measures contact behavior and fits a phenomenological sliding thick-skin model. Its measurement pipeline is evidence for identifying response from data rather than assigning one arbitrary “flesh stiffness” everywhere. The paper does not supply universally valid tissue parameters for every person, body region, activation state or loading rate.

## 4 Force transfer follows the transpose of motion transfer

Suppose a proxy's positions **x** generate contact-surface positions **y** = **E****x**, using a fixed linear embedding. Then

$$\dot{\mathbf y}=\mathbf E\dot{\mathbf x},\qquad
\mathbf f_x=\mathbf E^T\mathbf f_y.$$

The transpose is not a software convenience. It ensures

$$\mathbf f_y^T\dot{\mathbf y}=\mathbf f_x^T\dot{\mathbf x}.$$

For a nonlinear map **y** = Φ(**q**), the corresponding generalized force is **Q** = (∂Φ/∂**q**)ᵀ**f**_y. This is the same virtual-work principle that produced the muscle moment arm.

For a tissue attachment at point **p** on a rigid body, the body receives the opposite force to the tissue and the moment (**p**−**c**)×**f**. If the bone is prescribed, record the boundary reaction and its work even though the solver does not move the bone in response.

**Reader implementation exercise — unfinished in this edition.** Couple a rigid paddle to a deformable block. Push on the block, then on the paddle. The same attachment must transmit reactions in both directions in a two-way simulation. Turning off the reaction path demonstrates the difference between coupled mechanics and one-way visual following.

## 5 Avoid counting the pose twice

A dangerous displacement transfer is

```text
render = already_skinned_surface + (simulated_current_tissue - unposed_rest_tissue)
```

The simulated tissue already includes bone motion, so the subtraction includes pose displacement. Adding it to an already posed surface counts that motion twice.

There are two clean teaching choices.

**Direct embedding:** compute the visible surface from the current simulated volume, **x**_render = **E x**_sim, with any detail offset transported in a well-defined local frame.

**Residual embedding:** evaluate a simulation base state and a skinning base state at exactly the same current pose. Transfer only the extra deformation,

$$\mathbf x_{render}=\mathbf x_{skin}
+\mathbf E(\mathbf x_{sim}-\mathbf x_{base}).$$

The mapping's reference space, rotations, scale and time must agree. If a weighted residual or local-frame rotation is used, specify it and test rigid-motion invariance. Nearest-particle reassignment during motion can cause discontinuities; use a documented fixed embedding when topology permits it.

The decisive test is a zero-deformation pose sweep: disable gravity and secondary forces, make the proxy match its posed base exactly, and rotate the skeleton. The residual must be zero and the rendered surface must match its intended base, without drift or doubled motion.

## 6 Partitioned and monolithic systems

A partitioned method alternates skeleton, muscle, tissue and contact updates. It is modular and may be adequate for weak coupling, but delayed reactions can inject energy or make stiff attachments unstable. Subiterations and a joint residual can improve it. A monolithic solve includes the coupled unknowns in one system, which can better enforce consistency but is more demanding to formulate and solve.

Laboratory 7 implements explicitly one-way tissue response. Two-way extensions require force-transfer and energy tests before interpreting the coupled result. A full model may use different time steps for activation, multibody dynamics and tissue, but exchanges must have defined interpolation, sample times and work accounting. A high-frequency tissue loop cannot repair a sign error in the lower-frequency joint reaction.

The production example in [McAdams et al.](https://la.disneyresearch.com/publication/efficient-elasticity-for-character-skinning-with-contact-and-collisions/) demonstrates skeleton-driven volumetric elasticity with contact and collisions. It is evidence that contact-aware flesh is a distinct computational problem beyond skin weights. Its art-directed skeleton and character examples are not subject-specific medical validation.

## 7 Compression tests for the final arm

In the elbow's inner fold, bending brings opposing skin patches together. A useful deformation should redistribute tissue, develop contact where warranted and avoid visible crossing. The display must distinguish these quantities:

- geometric overlap of nonadjacent triangles;
- signed gap to bone and external-object proxies;
- local J values and total volume change;
- tissue height reduction and lateral displacement;
- contact reaction and material stress in their correct units;
- solver residual and iteration budget.

Do not color every red contact patch as “high pressure.” Pressure requires a defined force-to-area measure or continuum stress; a multiplier, penetration depth or collision flag is not automatically pressure. A contact-free image proves only that no visible overlap was noticed from that camera. The verification system must examine the complete geometry.

Laboratory 7 now implements a separate skin membrane, discrete fascia tethers and compliant sampled contact on the arm itself. Its one-way coupling, absent sliding/self-contact, and sampled-gap limitations are explicit. It transfers centroid contact forces with barycentric weights, while the paired baseline is posed exactly once. The following chapter reports actual residuals and penetration for that implementation.
