# From a spring to a volume of tissue {#from-a-spring-to-a-volume-of-tissue}

A spring connects a few points. A continuum assigns a deformation and a material response throughout a volume. This distinction matters when the question is where a muscle expands, how a patch of tissue is compressed, or which region carries stress. A visually dense surface mesh does not create a volumetric material model.

The [early property lessons](#measure-deformation-before-choosing-a-muscle-law) supplied geometric measurements and a reduced axial calculation. This chapter reuses $F$, $J$ and strain, then introduces a three-dimensional energy density, matching stress measures and equilibrium. The earlier bar's area profile was prescribed and its balance was axial only; a continuum model must also account for transverse response and boundary conditions. The homogeneous compression block in [Laboratory 5](#tendon-tissue-coupling) is one bounded example of that additional step.

The notation and elementary derivations below are self-contained. [Sifakis and Barbič's FEM course](https://viterbi-web.usc.edu/~jbarbic/femdefo/) is a bibliography lead; its full notes were inaccessible in the audit, so no formula below is attributed to unread course content. The proposed exercises are educational tests, not claimed reproductions of published biological experiments.

## 1 The deformation gradient records local shape change

Let **X** be a point in the reference body and **x** = φ(**X**,t) its current position. The deformation gradient is

$$\mathbf F=\partial\mathbf x/\partial\mathbf X.$$

A small reference segment d**X** becomes d**x** = **F**d**X**. The determinant J = det **F** is the local volume ratio. J = 1 means local volume preservation; J < 1 means volume loss; J ≤ 0 is a degenerate or inverted material element in the ordinary orientation-preserving solid model.

A pure rotation has **F** = **R**, J = 1 and no elastic strain. The Green strain

$$\mathbf E_G=\tfrac12(\mathbf F^T\mathbf F-\mathbf I)$$

vanishes for every rigid rotation. Small-strain elasticity uses ε = ½(∇**u**+∇**u**ᵀ), where **u** = **x**−**X**, and does not have that property for large rotations. Rotating a stiff element is therefore an excellent test of whether an implementation has confused a small-strain formula with a finite-deformation model.

**Reader exercise and extension.** The implemented [deformation lab](#lab-property-deformation) measures **F**, J and Green strain under rotation, stretch and shear; it has no stored-energy law or singular-value readout. As a separate extension, compute the singular values of **F**, select an objective material energy, and rotate an undeformed tetrahedron through 180 degrees: its constitutive energy should remain at the reference value. That extension is not an implemented property-lab control.

## 2 Energy and stress must use matching configurations

For hyperelastic material, stored energy is

$$U=\int_{\Omega_0}\psi(\mathbf F)\,dV_0.$$

The first Piola stress is **P** = ∂ψ/∂**F**, and the Cauchy stress is

$$\boldsymbol\sigma=J^{-1}\mathbf P\mathbf F^T.$$

**P** pairs with reference area and **F**. **σ** acts on current area. Plotting one while labeling it as the other creates an incorrect configuration interpretation despite compatible Pa units even when the color map looks smooth. Force is measured in N; stress in Pa = N/m². A nodal force is not a local stress sample.

For an isotropic example valid for J > 0, use a volumetric/deviatoric split,

$$\psi=\frac{\mu}{2}(J^{-2/3}I_1-3)+\frac{\kappa}{2}(J-1)^2,
\qquad I_1=\mathrm{tr}(\mathbf F^T\mathbf F).$$

Here μ is the small-strain shear modulus and κ the bulk modulus. Differentiation gives

$$\mathbf P=\mu J^{-2/3}\left(\mathbf F-\frac{I_1}{3}\mathbf F^{-T}\right)
+\kappa(J-1)J\mathbf F^{-T}.$$

At the identity, this stress vanishes. Under uniform scale **F** = s**I**, the isochoric term contributes no stress; the volume term governs the response. This yields an independently checkable material test before any mesh is assembled.

The illustrative energy is not a universal tissue law. Muscle can be anisotropic and active; tendon has strong directional response; skin can be heterogeneous, anisotropic and rate dependent. A material law must be selected and calibrated for the output being claimed.

## 3 Nearly incompressible does not mean impossible to squash

For small-strain isotropic constants,

$$\mu=\frac{E_Y}{2(1+\nu)},\qquad
\kappa=\frac{E_Y}{3(1-2\nu)}.$$

As Poisson's ratio ν approaches 0.5, the bulk modulus becomes large relative to the shear modulus. Tissue can flatten under a plate while expanding sideways and changing volume only slightly. “Compression” may mean shorter height under a contact load, rather than a large decrease in volume.

A compression experiment must therefore report at least plate displacement, reaction force, lateral expansion and volume ratio. A surface-height plot alone cannot distinguish compliant shear from spurious loss of volume.

Do not enter ν = 0.5 into the formula above. Exact incompressibility requires a different constrained or mixed formulation, commonly involving a pressure unknown. Low-order displacement-only elements can become artificially stiff through volumetric locking as incompressibility is approached. Reduced integration can introduce other modes unless stabilized. Increasing κ without checking element formulation and convergence is not a reliable fix.

## 4 Build one tetrahedral element

Let a rest tetrahedron have points **X**₀…**X**₃ and current points **x**₀…**x**₃. Define

$$\mathbf D_m=[\mathbf X_1-\mathbf X_0\;\mathbf X_2-\mathbf X_0\;\mathbf X_3-\mathbf X_0],$$

$$\mathbf D_s=[\mathbf x_1-\mathbf x_0\;\mathbf x_2-\mathbf x_0\;\mathbf x_3-\mathbf x_0],\qquad
\mathbf F=\mathbf D_s\mathbf D_m^{-1}.$$

With positive rest orientation, V₀ = det **D**ₘ/6. Element energy is Uₑ = V₀ψ(**F**). The force columns on vertices 1, 2 and 3 are

$$[\mathbf f_1\;\mathbf f_2\;\mathbf f_3]
=-V_0\mathbf P\mathbf D_m^{-T},\qquad
\mathbf f_0=-(\mathbf f_1+\mathbf f_2+\mathbf f_3).$$

This formula follows by differentiating the element energy with respect to the current vertex positions. It conserves total internal force by construction. For an objective energy, the internal net torque also vanishes up to numerical error.

::: {.keep-together}
**Original teaching pseudocode**

```text
precompute each tetrahedron:
    require positive, well-conditioned rest volume
    save inverse(Dm), rest volume and material/fiber data
    distribute density * rest volume into the declared mass matrix

evaluate internal forces:
    clear assembled forces and energy
    for each tetrahedron:
        Ds = current edge matrix
        F = Ds * inverse(Dm)
        evaluate J and reject an inadmissible configuration
        evaluate energy density and first Piola stress
        force_columns = -rest_volume * P * transpose(inverse(Dm))
        scatter columns to vertices 1, 2, 3
        scatter their negative sum to vertex 0
        accumulate rest_volume * energy_density
```
:::

Six edge springs over a tetrahedron are a spring network. They do not become FEM by having the same four vertices. Their stiffness depends on topology and chosen springs, and no independent bulk response follows automatically. A separate volume constraint changes that model again. Those are useful lessons if named accurately.

## 5 Choose a material for its behavior and domain

**Linear elasticity** is an excellent first derivative test and small-deformation reference. It is inappropriate for large rigid rotations without an additional treatment.

**Co-rotational elasticity** extracts a local rotation and models strain in a rotated frame. It makes large motion with relatively small local strain easier to handle. Its common volume term is not the same as an exact determinant-based volume penalty, so its behavior under large compression needs testing.

**Saint Venant–Kirchhoff elasticity** uses nonlinear Green strain with a quadratic energy. It is convenient for derivation and reduced polynomial force models, but can behave poorly in severe compression and inversion.

**Neo-Hookean and richer hyperelastic laws** provide other finite-deformation responses. “Neo-Hookean” is a family label: the exact energy, parameter mapping, valid J range and inversion handling must be specified.

[Smith, de Goes and Kim](https://www.tkim.graphics/NEO/StableNeoHookean2018.pdf) develop a particular stable neo-Hookean energy and Hessian treatment for flesh animation. Their tests highlight deficiencies of common co-rotational volume response at large deformation. Robustness to an inverted element is different from preventing inversion, and neither proves biological accuracy. Do not silently replace an ordinary logarithmic or split neo-Hookean formula with that paper's material while keeping the same label and parameters.

## 6 Fibers introduce directional behavior

Store a unit reference fiber direction **a**₀. Its stretch is λ_f = ‖**F****a**₀‖ and its current unit direction is **a** = **F****a**₀/λ_f. A passive fiber energy ψ_f(λ_f) can resist extension preferentially along that direction. A tension-only fiber term should not accidentally resist compression as if every fiber were a rigid rod.

Two active formulations illustrate distinct assumptions.

**Active stress:** add a current stress

$$\boldsymbol\sigma_a=s_a(a,\lambda_f,\dot\lambda_f)\,\mathbf a\otimes\mathbf a,$$

and convert it consistently through **P**ₐ = J**σ**ₐ**F**⁻ᵀ. Its supplied power must be recorded; do not assume an arbitrary active-stress law derives from a conservative elastic energy.

**Active strain:** change the locally preferred deformation. For a synthetic volume-preserving contraction tensor,

$$\mathbf F_a=\lambda_a\mathbf a_0\otimes\mathbf a_0
+\lambda_a^{-1/2}(\mathbf I-\mathbf a_0\otimes\mathbf a_0),\quad 0<\lambda_a\le1.$$

Set **F**ₑ = **F****F**ₐ⁻¹ and evaluate an elastic energy in **F**ₑ. At fixed activation,

$$\mathbf P=\frac{\partial\psi_e}{\partial\mathbf F_e}\mathbf F_a^{-T}.$$

Activation changes the energy landscape and can do work. This is a teaching construction, not an assertion that an active-strain model and a Hill actuator produce identical force histories. Its mapping from activation to λ_a requires calibration.

The early [Teran et al. skeletal-muscle simulation](https://graphics.stanford.edu/papers/fvm_sig03/) demonstrates a directional hyperelastic tissue approach and a geometric force interpretation. [Blemker and Delp's architecture study](https://pubmed.ncbi.nlm.nih.gov/15981866/) motivates representing broad attachments and spatially varying fiber trajectories. Use those papers as motivation and provenance, not as a license to substitute arbitrary fiber fields and call the result validated muscle.

## 7 Solve equilibrium or dynamics deliberately

A quasistatic solve seeks force balance at each imposed pose. It omits inertia and is useful for slowly posed deformation, but it cannot predict vibration or impact timing. A dynamic solve adds mass and inertia, and needs initial velocities and a time integrator. Heavy damping can approximate a settling process but introduces another timescale.

For implicit dynamics, compute the residual and tangent, solve a Newton or quasi-Newton step, and use a line search or trust strategy that respects admissibility. Positive-definite Hessian projection changes the search direction; if the original objective and residual are retained and converged, it need not change the target stationary point. Stopping early still changes the result. State tolerances and residuals rather than simply reporting that the solver finished.

## 8 Tests before an anatomical mesh

1. Compare analytic forces with centred finite differences of energy over several perturbation sizes.
2. Apply rigid translations and rotations; check unchanged energy and transformed forces.
3. Apply uniform affine deformation to a mesh patch; verify consistency of deformation gradients and expected boundary reactions.
4. Stretch and shear blocks with controlled boundaries; compare with the chosen material law.
5. Compress a block at several κ/μ ratios and mesh resolutions; measure locking, volume change and reaction force.
6. Repeat at smaller time steps and tighter solver tolerances before increasing mesh detail.
7. For active material, compare active work, boundary work, kinetic energy, stored energy and dissipation.

An anatomical surface should be the final demanding example, not the first occasion on which an element's force formula is tested.
