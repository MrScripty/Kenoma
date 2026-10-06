# Fast solvers and what they approximate

Interactive performance can come from fewer unknowns, cheaper material laws, reusable linear algebra, looser convergence or less demanding collision handling. These choices have different consequences. A useful comparison holds the modeled problem fixed when testing a solver, and holds the solver tolerance fixed when testing a material. Otherwise a speed comparison may be measuring different physics.

## 1 Position based dynamics

Position based dynamics predicts positions and then corrects constraint violations. For a scalar equality C(**x**) = 0, inverse mass w_i and gradient **g**ᵢ = ∇ᵢC, a local mass-weighted correction has

$$\Delta\lambda=-\frac{C}{\sum_i w_i\|\mathbf g_i\|^2},
\qquad\Delta\mathbf x_i=w_i\mathbf g_i\Delta\lambda.$$

Distance, bending and volume conditions can share this projection structure. Applying corrections sequentially uses the newest positions, while parallel updates require an explicit accumulation or coloring strategy.

The original [Müller et al. paper](https://matthias-research.github.io/pages/publications/posBasedDyn.pdf) targets controllable, robust interactive animation. A finite projection budget leaves error. In ordinary PBD, apparent stiffness also depends on the time step and iteration count, so a value such as 0.8 is an algorithmic setting rather than a material modulus.

**Reader implementation exercise — unfinished in this edition.** Hang a short chain under gravity. Change the iteration count without changing its nominal stiffness. Plot its equilibrium extension. Then increase chain length; local information takes additional iterations to propagate through the constraints.

## 2 XPBD makes compliance explicit

Extended position based dynamics introduces compliance α and a total multiplier λ within the step. For the scalar elastic constraint energy U = C²/(2α), define α̃ = α/h². The update is

$$\Delta\lambda=
\frac{-C-\tilde\alpha\lambda}{\sum_i w_i\|\nabla_iC\|^2+\tilde\alpha},
\qquad\lambda\leftarrow\lambda+\Delta\lambda,
\qquad\Delta\mathbf x_i=w_i\nabla_iC\Delta\lambda.$$

For a distance constraint C = l−l₀, α = 1/k has units m/N. For C = J−1 and volumetric energy V₀κ(J−1)²/2, α = 1/(V₀κ). Constraint normalization therefore changes the required compliance. If C is multiplied by s, α must be multiplied by s² to represent the same energy.

The [XPBD paper](https://mmacklin.com/xpbd.pdf) derives an implicit compliant formulation and a constraint-force estimate. The corresponding nodal force estimate is ∇ᵢC·λ/h² under this convention. Its stiffness parameterization is much less entangled with solver settings than PBD's, but finite iteration count, changing gradients, integration error and contact approximation remain. “Iteration independent” must not be presented as exact convergence in one sweep.

::: {.keep-together}
**Original instructional pseudocode**

```text
advance_xpbd_substep(x, v, h):
    x_old = x
    v += h * inverse_mass * external_force
    x += h * v
    apply prescribed positions at the correct substep time
    initialize elastic multipliers to zero for this substep
    construct/update collision candidates using a declared strategy
    repeat solver_sweeps:
        for each elastic constraint:
            evaluate C, gradients and alpha / (h*h)
            update multiplier and all affected positions
        for each unilateral contact:
            perform projected multiplier update with lambda_normal >= 0
        solve attachments, friction and joints consistently
    v = (x - x_old) / h
    apply declared dissipative or impact velocity corrections
    report residuals, constraint-force estimates and failed contacts
```
:::

This is an original outline. Production implementations need robust gradients, moving boundary velocities, degenerate-configuration handling, consistent friction, and declared multiplier warm-starting. If multipliers are reset every iteration rather than every substep, the compliance formulation above is no longer being implemented.

For unilateral contact, clamp the *accumulated* normal multiplier, then apply only its change. A negative gap may require a repulsive correction, but a separating contact must not become attractive. When contact history, ordering or substep size changes, warm-starting requires deliberate handling and cannot be copied blindly from bilateral springs.

## 3 More substeps can help more than more sweeps

A long time step linearizes a large change. Several smaller steps refresh velocities, geometry and constraint directions. [Macklin et al., Small Steps](https://mmacklin.com/smallsteps.pdf), compares these choices within XPBD and reports improved behavior in its tested examples. This is a reason to benchmark both strategies, not a universal statement that one iteration is sufficient or that collision detection can be skipped between substeps.

**Reader implementation exercise — unfinished in this edition.** Fix a total constraint-evaluation budget and compare one large step with many sweeps against many small steps with fewer sweeps. Record deformation error, damping and runtime. Count collision detection separately; its cost and sampling frequency may change the result.

## 4 Projective dynamics reuses global structure

Projective dynamics writes a selected class of energies as squared distances to constraint sets. A simplified form is

$$\min_{\mathbf x,\{\mathbf p_i\}}
\frac{1}{2h^2}\|\mathbf x-\mathbf y\|_M^2
+\sum_i\frac{k_i}{2}\|\mathbf A_i\mathbf x-\mathbf p_i\|^2,
\qquad\mathbf p_i\in\mathcal C_i.$$

Holding **x** fixed gives independent local projections. Holding **p**ᵢ fixed gives

$$\left(\frac{\mathbf M}{h^2}+\sum_i k_i\mathbf A_i^T\mathbf A_i\right)\mathbf x
=\frac{\mathbf M\mathbf y}{h^2}+\sum_i k_i\mathbf A_i^T\mathbf p_i.$$

With constant h, masses, operators and weights, this global matrix can be factorized once and reused. Changes to them can require updating the factorization. Changing contact sets or moving hard constraints may alter the system unless the implementation uses a formulation that preserves the constant part.

[Bouaziz et al.](https://doi.org/10.1145/2601097.2601116) present the local/global method for a tailored energy class. It is not equivalent to applying arbitrary PBD projections in parallel. Nor does the prefactorization make every nonlinear constitutive law or contact model free. [Liu, Bouaziz and Kavan](https://arxiv.org/abs/1604.07378) extend the interpretation toward quasi-Newton treatment of more general hyperelastic energies.

::: {.keep-together}
**Original instructional pseudocode**

```text
precompute fixed global matrix and factorization
for each substep:
    form inertial prediction y
    initialize x from a consistent state
    repeat until tolerance or declared budget:
        in parallel: project each Ai*x onto its set Ci
        assemble right-hand side
        solve the prefactorized global system for x
        evaluate the original objective and residual
    reconstruct velocity and report convergence
```
:::

If a fixed sweep budget is used for responsiveness, expose its remaining residual. The visual plausibility of a stopped iterate is a different claim from a converged minimizer.

## 5 Reduced models remove possible motions

Represent deformation using r coordinates z instead of 3n vertex coordinates:

$$\mathbf x=\bar{\mathbf x}+\mathbf U\mathbf z,\qquad
\mathbf M_r=\mathbf U^T\mathbf M\mathbf U,\qquad
\mathbf f_r=\mathbf U^T\mathbf f.$$

A fixed basis can contain vibration modes, sampled deformations or other structured motions. Restricting motion to that subspace can substantially reduce the solve, but motions outside the basis cannot be recovered merely by tightening solver tolerances. Localized contact and new activation patterns can require modes the training examples never contained.

[Barbič and James](https://graphics.cs.cmu.edu/projects/stvk/) exploit the polynomial structure of reduced Saint Venant–Kirchhoff forces. Their independence from full mesh size concerns the precomputed reduced integration calculation, not every rendering, collision and preprocessing cost of a complete application. The material and basis limitations remain part of the result.

If the reference shape follows a rig, **x** = **x**_base(t)+**U**(t)**z**, velocities and accelerations include base-motion and basis-derivative terms. Ignoring them changes secondary-motion dynamics. A quasi-static pose-correction system can legitimately ignore inertia, but must be labeled that way.

**Reader implementation exercise — unfinished in this edition.** Train a reduced basis using bending and then press a small probe into the tissue at an unseen location. Display the full-space residual and deformation mismatch. This reveals why an attractive trained motion does not guarantee general contact behavior.

## 6 Shape matching and baked correctives occupy different places

Shape-matching methods fit local transforms to particle clusters and guide the particles toward those shapes. They are useful visual models with a different parameter-to-material relationship from calibrated continuum elasticity. [Müller et al.'s shape-matching paper](https://matthias-research.github.io/pages/publications/MeshlessDeformations_SIG05.pdf) is a primary starting point; verify the exact cluster and volume treatment in any implementation.

A corrective blend shape stores a deformation associated with a pose or control. It can faithfully replay a sampled simulation result while omitting force prediction, history and new contacts. A pose-only cache cannot distinguish two states with the same joint angles but different contact history, activation or loading unless those variables are included as inputs.

The fastest useful path for a game may combine rigging, correctives and small secondary dynamics. A film may accept a slower high-resolution solve for contact-rich shots. A CAD or biomedical question may instead prioritize identified parameters, convergence and uncertainty. Application category alone does not tell us the required solver; the measurable question does.

## 7 A fair comparison protocol

For every comparison, record geometry, mass, material energy, active model, boundary conditions, contacts, mesh, hardware, precision, integrator, h, iteration cap, convergence tolerance and collision settings. Separate preprocessing, simulation, collision, surface transfer and rendering time. Report median and tail latency over a named workload, with cold-start cost separately.

Compare matched-quality configurations. “Faster” at larger penetration, greater volume loss or looser residual is a tradeoff, not a free improvement. Do not reuse paper frame rates as browser targets. The book's interactive budget is an engineering target to measure on specified devices; it is not an established property of a method.

The next worked laboratory holds the material and discrete implicit target fixed while comparing PCG with compliant strain sweeps. Its measured errors and timings make the tradeoff concrete, rather than asking the reader to infer a universal ranking from the methods above.
