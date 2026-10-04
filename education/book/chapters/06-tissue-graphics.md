# From line forces to tissue and rendered skin {#tissue-and-rendered-skin}

Laboratory 4 moves a rigid skeleton. Its red ellipsoid cannot tell us where tissue compresses. The next layer must introduce material deformation, interfaces and contact before it supplies forces or pressure. This chapter integrates the audited simulation and anatomy research into the progression. Laboratory 5 implements a bounded affine-block/contact proxy; the spatial skin/fascia and anatomical contact mechanisms described below still need their own solvers and validation.

## Deformation needs a reference configuration

Write a material point X in the reference shape and its current position x(X). The deformation gradient F = ∂x/∂X describes local changes; J = det F measures local volume ratio. A rigid rotation has F = R and J = 1, while stretch and shear change the local geometry. Volume preservation alone does not establish an appropriate tissue response or fiber architecture.

For a tetrahedral finite element, construct F from current and reference edge matrices, assign a material energy density Ψ(F, fibers), integrate that energy over the reference volume, and differentiate to obtain nodal forces. A six-edge spring network on the same tetrahedron is a different model. It does not become FEM by sharing the topology. Fiber directions, large deformation, incompressibility, boundary conditions, and inversion behavior each need an explicit choice.

First Piola–Kirchhoff stress P and Cauchy stress σ both have Pa units. They act in different configuration descriptions and satisfy σ = J⁻¹ P Fᵀ under the usual mapping. Confusing those measures is a configuration error, not a unit conversion. Local stress cannot be read from a skinning weight or inferred from a single silhouette.

An active continuum may add fiber-directed stress or use an active-strain decomposition. If it represents the same synthetic flexor as the line actuator, choose a single force owner: either its tissue reactions drive the joint, or the line drives the joint and the tissue is an explicitly one-way visualization. Adding both actuator moments for the same muscle doubles active work. Ryan and colleagues' original finite-element compression study examines how transverse loading changes muscle work and force; its simplified contracting blocks do not validate a human anterior elbow fold. [Original study](#source-compression)

## Skin, fascia and interfaces answer separate questions

The skin envelope, subcutaneous layer, deep fascia, muscle connective tissue and tendons differ in geometry, attachments, and loading. An attachment condition controls motion relative to a bone or neighboring layer. A sliding interface permits tangential relative motion under its stated law. Contact controls whether two surfaces may occupy the same region. A generic stiffness number cannot represent all three.

Material evidence must keep species, orientation, strain range, activation and loading context. The audited Takaza study is passive **porcine tensile** testing at different orientations; it is not transverse human-arm compression evidence. The forearm indentation estimates introduced earlier have their own layer and inverse-identification context. A shear-wave or effective indentation modulus should not silently become a universal large-strain Young's modulus.

The concave anterior elbow crease and convex posterior tissues have different deformation demands. Posterior fat-pad gliding is not an anterior skin-contact measurement. Similarly, a rigid-body joint reaction is a resultant, whereas cartilage or skin pressure requires a local contact area and a constitutive/contact model. Report “not modeled” for those absent outputs, rather than zero.

## Normal contact, friction and coupling

For a chosen gap g_n and compressive normal multiplier λ_n, ideal unilateral contact satisfies g_n ≥ 0, λ_n ≥ 0 and g_n λ_n = 0. A penalty method tolerates penetration and estimates force from a specified law; it requires a penalty/timestep sensitivity study. A constraint solver has its own iteration residual and tolerance. Friction adds a tangential law and dissipation and should not be confused with the normal condition.

Define a transferred force f as the force **on the bone** and −f on tissue. Match action/reaction, moment about a common origin, and power at the same interface velocity. If a model already includes the forearm's tissue mass in its segment inertia, adding massive tissue proxies requires redistributing that mass explicitly.

Near-volume preservation can cause lateral expansion when tissue flattens. It cannot by itself prevent surface intersection. Test compression, sliding, attachment, and volume separately before a coupled crease. Mesh refinement, timestep refinement and contact-tolerance studies answer different questions; none can replace an independent measured deformation field.

## Faster methods change the model or its solution

PBD projects geometric constraints after a prediction step. Its stiffness can vary with timestep and iteration count. XPBD introduces compliance scaled by timestep and accumulated multipliers to reduce that coupling, while finite iterations, nonlinearities and contact can still produce error. [Macklin et al.'s original XPBD paper](#source-xpbd)

Linear blend skinning (LBS) instead evaluates a weighted sum of bone transforms. It has no material energy, activation or contact reaction. Two equally weighted rotations about a common axis illustrate its volume artifact: in the rotated plane, averaging R(+φ) and R(−φ) yields cos φ times the identity. At φ = 60°, that plane's area scales by cos² φ = 0.25. This is an authored exact graphics counterexample, not a measurement of elbow skin.

Dual-quaternion skinning improves rotational interpolation and addresses familiar LBS deformation artifacts, but it does not introduce contact or a tissue constitutive law. Kavan and colleagues' original paper analyzes that approximation. Neither technique supplies pressure by itself. [Original paper](#source-dqs)

Reduced deformation bases, cached simulations and learned mappings can save computation by removing degrees of freedom or reusing prior solutions. Their domain needs testing on unseen poses and contact states. Compare the same geometry, load, material, boundary conditions and error measure before attributing a difference purely to solver speed. A medical/CAD analysis needs parameter identification, convergence and independently measured outputs; a game/film deformation may legitimately optimize visible shape and latency. No universal speed/accuracy ranking follows from the category name.

## Keep the pose in one place

If a detailed render surface follows a tissue proxy, embed it directly in the posed proxy, or add a displacement residual measured against its baseline at the **same current pose and coordinate frame**. Adding an unposed rest-relative displacement to an already skinned vertex applies part of the pose twice. Test this with a pure bone-motion sweep: a zero tissue residual must leave exactly the baseline surface.

For the eventual capstone, synchronize the actual q(t) from forward dynamics across the naive skinning and tissue views. Keep the base mesh and skeletal transforms identical. Show geometric distortion separately from detected intersection, contact gap separately from pressure, and each force owner separately from its visual shape. Laboratory 4 supplies the first trajectory and actuator telemetry for that comparison; compliant tissue and elbow compression still need implementation and validation.
