# Lift, release and compress a spatial arm {#spatial-capstone}

The final teaching scene brings deformation onto the arm itself. It combines the already tested excitation–activation, series tendon and rigid hinge with an actual spatial energy solve, a separate membrane and bone contact. Its paired view answers a narrower question than patient biomechanics: what changes when the same schematic arm pose is supported by a deforming mechanical model rather than skinning weights alone?

This is **one-way, quasistatic coupling**. The line actuator owns the moment that lifts the dumbbell. The pose q and activation a drive the spatial lesson; spatial reactions do not feed back into the hinge. There is no extra active moment added for the displayed volume. The spatial shape solve is massless: it omits its own gravity and inertia, while the hinge retains the stated forearm and dumbbell mass. Its instantaneous elastic energy is not added to hinge work accounting. The body is original teaching geometry, not a registration or remeshing of BodyParts3D. The spatial material is an authored edge/volume network, **not FEM**. The preceding continuum lesson implements genuine FEM and isolates its own solver comparison.

{{demo:spatial}}

## A volume, fibres, tendon spans and an independent skin

The bind volume has 81 vertices and 192 positively oriented tetrahedra in a 38 × 360 × 42 mm rectangular strip beside the bones. Each tetrahedron has a reference volume V₀. The boundary supplies a separate set of skin vertices, initially 4 mm farther out radially. Its triangles have their own in-plane edge energy. The top and bottom cross-sections follow the fixed upper and rotating lower segment. The interior is free to change shape; a fixed skinning transform does not determine those vertices.

Nine aligned upper-span fibre chains carry preferred shortening. Nine stiffer distal edges illustrate tendon spans. The rest of the edge network supplies passive shape resistance. A tendon edge here can store elastic energy and resist extension or compression; this simplified bilateral span is distinct from the **tension-only line tendon** that drives the hinge. It has no slack/toe-region law, pennation or clinical architecture. The end-to-end active span, the summed spatial fibre-chain path, and scalar line fibre length are different observables and are displayed separately. The centre path sums four actual deformed edge lengths; the mean averages all nine aligned chains.

Fascia is represented by compliant vector tethers between corresponding volume-boundary and skin vertices. Each tether's preferred 4 mm offset rotates with the authored pose field. It transmits force between its two vertices but has no anatomical layer thickness or sliding law. It is a constrained sheath approximation; the membrane has no bending energy, and skin–skin and skin–muscle self-contact are absent. These limitations matter when interpreting a fold.

| Component | Implemented law | Authored value | Unit |
|:--|:--|--:|:--|
| Passive tetrahedral-edge network | U = k(l−l₀)²/2 | 80 | N/m per edge |
| Active aligned edge | U = akₐ max(l−l₀(1−0.18a),0)²/2 | kₐ = 500 | N/m per edge |
| Spatial tendon span | U = k(l−l₀)²/2 | 1,200 | N/m per edge |
| Skin edge | U = k(l−l₀)²/2 | 12 | N/m per edge |
| Fascia vector tether | U = k‖x_skin−x_core−d(q)‖²/2 | 30 | N/m per tether |
| Volume resistance | U = κ(V−V₀)²/(2V₀) | 25,000 | Pa |
| Boundary sample contact | U = k min(g,0)²/2 | 12,000 | N/m per sample |
| Interior centroid contact | Same compliant gap penalty | 250 | N/m per sample |

The values are not measured human material parameters. Network response depends on topology and these per-edge coefficients. Refining the grid while retaining them would change the model. The continuum chapter's mesh-refinement evidence therefore cannot be transferred to this network. The ablation controls change the specified energy rather than silently retuning it.

For an edge i–j, length l = ‖xᵢ−xⱼ‖ and gap C = l−l_target, differentiating kC²/2 gives an equal/opposite central force pair. The tension-only active term takes C = max(l−l_target,0). Increasing a changes both its coefficient and target, so the preferred-length law is a phenomenological shape actuator rather than Hill's measured force–velocity relation. The original line model retains its own declared excitation, activation and tendon assumptions.

## Actual volume gradients and contact forces

A tetrahedron's signed current volume is

$$V=\frac16(\mathbf x_1-\mathbf x_0)\cdot[(\mathbf x_2-\mathbf x_0)\times(\mathbf x_3-\mathbf x_0)].$$

For example, ∂V/∂x₁ = [(x₂−x₀)×(x₃−x₀)]/6. The other two edge-vertex gradients follow by cyclic permutation; the gradient at vertex zero is their negative sum. Multiplying by κ(V−V₀)/V₀ supplies the energy gradient, and force is its negative. The implementation's derivatives are checked against central differences at perturbed geometries. Those numerical checks support the code; the following exact algebra establishes only the stated gradient-partition contract.

{{proof:element-resultant}}

The bone proxies are capsules: the upper radius is 21 mm, the forearm radius 19 mm, with 270 and 350 mm centerline lengths. For each sample, project onto the bounded centerline segment and subtract the radius from the distance. Positive g is clearance; negative g is penetration. A contacting sample receives **f** = −k g **n**, pointing out of the capsule. Separation gives zero force. The penalty is compliant, so a small negative gap is expected at finite force.

Boundary vertices and tetrahedron centroids are sampled. A centroid is the average of its four vertices, so its contact force is distributed with weights 1/4 to all four. This uses the transpose of the centroid-motion map. The exact numerator identity below explains why that transfer preserves virtual power coordinate by coordinate. It does not certify the distance calculation or floating-point arithmetic.

{{proof:centroid-transfer}}

The reported normal-force sum is the sum of the nonnegative magnitudes of these sample forces. It is not their vector resultant, a cartilage joint reaction, or pressure. There is no contact-area stress integration; the display deliberately reports pressure as absent. Fixed-node reactions are recovered from the full gradient. Their resultant plus the external sampled contact forces equals the negative unresolved free-node gradient sum. This is tested explicitly and shown as a force-balance defect.

These samples are not a complete surface collision test. A triangle can intersect between vertices, or a moving surface can pass through a bone between poses, without a sampled negative gap. No continuous collision detection, self-contact or intersection-free guarantee is claimed. Contact-off removes the penalty and exposes geometric penetration; it does not make a zero-force overlapping state into valid contact.

## A deterministic finite quasistatic solve

At each requested q,a pair, initialize from a smooth authored pose field R_z(w(X)q)X, where w rises linearly from zero at y = 120 mm to one at y = −120 mm. The ends match their rigid transforms. The mechanical solve then minimizes the sum of the listed energies over free coordinates, using limited-memory BFGS with eight stored update pairs and an Armijo backtracking line search. Failed or poorly conditioned curvature updates are discarded; a non-descent search direction resets to scaled negative gradient.

An accepted trial must have minimum tetrahedral J = V/V₀ greater than 0.01 and satisfy sufficient objective decrease. This is an implemented guard, not a proof of mesh injectivity, global convergence or feasible contact. It can reject a search step even while the residual remains large. The solver exposes its iteration cap, energy-evaluation count, maximum free force and L2 residual; an unconverged iterate stays labeled approximate. A residual criterion of 2 × 10⁻⁵ N per free coordinate is used for local stopping.

{{proof:armijo-decrease}}

Floating-point evaluation can change the line-search path across JavaScript runtimes, so exact cross-browser identity of the finite iterate is not promised. Reset remains deterministic in the same runtime.

The original worked compression fixture holds q = 90°, a = 0.6. These values are generated by executing the same module that the browser imports. They measure iteration sensitivity on one fixed grid and model; they are not continuum mesh convergence or a calibrated compression experiment.

{{spatial-experiment}}

At 640 iterations, the minimum J is about 0.736 and total mean J about 0.960. Some tissue flattens and moves laterally while the model permits roughly 4% total volume change. The maximum sampled penetration is about 0.0283 mm, versus 9.75 mm in the skinning baseline. The maximum free-force defect remains about 0.0145 N. Those are separate diagnostics: a small sampled gap does not prove the material law correct, and a residual alone does not establish a contact-free surface.

At the straight pose, activation 0.6 shortens the measured upper centreline span from 180 mm to about 170.77 mm while mean J remains about 0.9993. Releasing activation returns the quasistatic solution toward its passive state. The browser's prescribed-hold mode lets a reader isolate that deformation from bone motion. During the default lift/release pulse, the arm reaches roughly 67° by 0.6 s and subsequently lowers below its starting angle by 0.9 s; its spatial active span lengthens again. Activation persists after excitation becomes zero; the line fibre and spatial span can subsequently stretch as the load lowers the arm. A contracting actuator can carry tensile force while lengthening; “active” does not mean every fibre is getting shorter at every instant.

## The naive skinning view is evaluated once at the same pose

The right-hand baseline uses exactly the same bind vertices, skin topology, joint pivot, bones and q as the mechanical side:

$$\mathbf x_{LBS}=(1-w)\mathbf X+w\mathbf R_z(q)\mathbf X.$$ 

There is no added rest-relative displacement and no second skeletal transform. Because w varies with position, the full-arm J is measured from the transformed tetrahedra rather than taken from the uniform-blend cos²(q/2) formula. The 90° fixture has minimum J ≈ 0.171 and mean J ≈ 0.718. These are actual values for this schematic strip, not human elbow volume loss. Both meshes retain the same camera and SI display scale; the skinning baseline has no force or pressure model.

The interactive pose domain is 0–100°. This keeps the mechanical initialization in its checked teaching range; it is not an anatomical range-of-motion limit. Outside it, the underlying strip and pose field can invert cells or trap the local solver near its J guard. The rigid hinge pauses at its last admissible pose rather than inventing an impact response.

## Read the controls as experiments

Start the 3D scene, then use **Lift / release pulse** for the force-driven 5 kg dumbbell example. The fixed physics step is independent of wall-clock playback; the spatial solve can slow playback. **Release excitation** changes only the input at the current time, and the exported current row is refreshed immediately. Activation and pose advance on the next step. **Reset** reconstructs the same state and deterministic shape solve.

Use **90° compression fixture** to compare the mechanical mesh with the same-pose baseline. Disable contact and observe the increase in sampled penetration. Lower volume stiffness and inspect volume loss. Turn off skin/fascia to see which shape restrictions those discrete layers contribute. Disable the spatial shortening law to isolate pose/contact from activation; the line actuator still owns the hinge force. Increase the iteration cap and compare energy and residual together, since a low residual does not identify a globally unique minimum.

`spatial-experiment.json` retains the meshes, paired coordinates, contact samples, iteration study, activation comparison, ablations and lift/release sample states. `web/spatial.mjs` is the source of those numbers. The chapter is an original reproducible computational teaching experiment. Published muscle-compression and skin-identification studies motivate which outputs to ask for; their physiological results are not being copied onto this schematic model. [Ryan et al., original contracting-muscle compression study](#source-compression), [Pai et al., original soft-tissue contact identification study](https://www.cs.ubc.ca/research/HumanTouch/HumanTouchSIGGRAPH2018.pdf)

A fully coupled medical arm would require the spatial reactions to drive the bones through a consistent interface, an identified anisotropic active law, force/velocity/pennation and rate effects where needed, tendon slack and architecture, sliding layers, robust surface contact and uncertainty analysis. Those are extensions of this declared educational model. They are not a prerequisite for understanding and checking the present one-way comparison, and they are not added to Kenoma's production MVP by this book.
