# Solve a spatial solid, then buy speed with a measured error {#continuum-reference}

The force chapter asks how a net force changes motion. The energy chapter asks whether a numerical update accounts for work. The tissue chapters add stored energy, compression and the distinction between a physical surface and a graphics baseline. Their affine block has one homogeneous deformation. We now give different material points different displacements, assemble their coupled force equations, and solve them. This is a spatial finite element calculation with a deliberately modest material law.

The lesson has two references. A polynomial displacement field supplies an **analytic continuum solution** for a static manufactured load. A tightly converged linear solve supplies a **discrete reference** for one implicit time step. They answer different questions. The games/film comparison spends a limited number of local compliant-constraint sweeps on the very same discrete implicit problem. It changes the solve accuracy, while preserving mesh, material energy, loads, mass approximation and supports.

All dimensions and parameters below are authored for teaching. The block is not a registered atlas part or a calibrated muscle. The existing actual-data package remains a separate evidence stream. No existing Lean declaration checks these floating-point calculations.

## Define the material and the system boundary

Material coordinates are $X=(x,y,z)$ in the reference cuboid

$$\Omega=[0,L]\times[0,W]\times[0,H_b],\qquad
L=0.04\,\mathrm{m},\quad W=H_b=0.02\,\mathrm{m}.$$

A point moves to $X+u(X)$. We retain only infinitesimal strain,

$$\epsilon=\tfrac12(\nabla u+\nabla u^T),\qquad
\sigma=\lambda\,\mathrm{tr}(\epsilon)I+2\mu\epsilon,$$

$$\Psi=\tfrac12\lambda\,[\mathrm{tr}(\epsilon)]^2+\mu\,\epsilon:\epsilon,
\qquad \mu=\frac{E}{2(1+\nu)},\quad
\lambda=\frac{E\nu}{(1+\nu)(1-2\nu)}.$$

Here $E=100000$ Pa, $\nu=0.25$ and $\rho=1000$ kg/m³, so $\lambda=\mu=40000$ Pa. Energy density has units J/m³, numerically equivalent to Pa. The material is homogeneous, passive, compressible, isotropic and linear. There is no fibre direction, activation, tendon, damping law, skin membrane, fascia interface, bone, friction or contact. The small-strain stress is the linearized physical stress in the common reference frame; it is not a nonlinear conversion between first Piola–Kirchhoff and Cauchy stresses.

The face $x=0$ is clamped in all three displacement components. The other five faces receive specified **dead tractions**: forces per reference area whose directions remain fixed as the block moves. A body force $b$ is force per reference volume, in N/m³. Positive traction and positive nodal force act **on the block**. The material's restoring nodal force is $-\nabla U$, while the support's reaction is also a force on the block. A force transmitted to a support or bone would have the opposite sign.

With $E>0$ and $-1<\nu<1/2$, this energy is positive on nonzero symmetric strain. Translations and infinitesimal rigid rotations have zero strain. The full free-body stiffness therefore has six rigid modes. The clamp removes them in this connected mesh. Do not make a static free body solvable by secretly pinning an arbitrary node or adding a numerical spring; those changes introduce a support and alter the physical problem.

Finite rotations are outside this constitutive approximation. For a rigid rotation $R$, the displacement gradient is $R-I$, whose symmetric part is generally nonzero. Thus this linear model falsely stores energy in a large rigid rotation. A focused test demonstrates that limit alongside the six infinitesimal null modes.

## Manufacture a nonuniform case with a known answer

Choose the static displacement

$$u^*(X)=(c x^2,0,0),\qquad c=0.25\,\mathrm{m}^{-1}.$$

The exact tip displacement is 0.0004 m, or 0.4 mm; the largest axial strain is $2cL=0.02$. Unlike the earlier affine block, its axial strain varies through space. Define $A=WH_b$ and $M_L=\lambda+2\mu=120000$ Pa. Direct differentiation gives

$$\sigma^*(x)=\operatorname{diag}(2cM_Lx,\;2c\lambda x,\;2c\lambda x).$$

Static balance is $\nabla\cdot\sigma+b=0$. Therefore apply

$$b=(-2cM_L,0,0)=(-60000,0,0)\,\mathrm{N/m^3},\qquad t(X)=\sigma^*(X)n$$

on every unclamped face, using the outward normal $n$. This is an independently derived manufactured solution, rather than a curve fitted to a computed mesh. The $x=L$ face receives 2400 Pa in $+x$, a 0.96 N resultant. The body force totals −0.96 N. The $y$ and $z$ faces have outward, linearly varying normal tractions reaching 800 Pa; each positive side has a 0.32 N resultant and each negative side its opposite. Shear tractions are zero. The exact stress at $x=0$ is zero, so the exact support resultant is zero.

A zero resultant does not mean the load is absent: the body and boundary forces create a stressed, stretched solid. Nor does it require every computed clamped-node reaction to vanish on a coarse mesh. Local reaction artifacts are discretization errors; the global resultant closes the assembled force balance.

The exact stored energy follows from a one-dimensional integral over the cuboid:

$$U^*=\frac12 M_L\int_\Omega(2cx)^2\,dV
=\frac{2M_Lc^2AL^3}{3}=0.000128\,\mathrm{J}.$$

For the linear model with a load ramped proportionally from zero to its final value, external work is $\tfrac12f^Tu$, not $f^Tu$. The latter is final load dotted with displacement. It is twice the ramp work at static equilibrium with stationary zero-displacement supports. The distinction from work under a constant final load will matter for the dynamic step.

## Build actual tetrahedral finite elements

Split each coordinate interval into $n$ equal pieces. Divide every brick into six tetrahedra around its common body diagonal, using a consistent vertex ordering. Neighboring bricks share face triangulations. The mesh has $(n+1)^3$ nodes, $6n^3$ tetrahedra, and $12n^2$ exterior triangles. At $n=3$, it has 64 nodes and 162 tetrahedra; the clamp fixes 48 of the 192 displacement degrees of freedom.

For a tetrahedron with four reference vertices $X_a$, the displacement interpolation is

$$u_h(X)=\sum_{a=0}^3N_a(X)u_a,\qquad \sum_aN_a=1.$$

Each barycentric shape function $N_a$ is linear and its gradient $g_a=\nabla N_a$ is constant. Set

$$D_m=[X_1-X_0\; X_2-X_0\; X_3-X_0],\quad
V_e=\frac{\det D_m}{6}>0.$$

The gradients of $N_1,N_2,N_3$ are the rows of $D_m^{-1}$; $g_0=-g_1-g_2-g_3$. Equivalently, the deformation gradient would be $F=I+\sum_a u_ag_a^T$. Teran and colleagues give the constant-strain tetrahedral construction and energy-derived forces in their original nonlinear flesh-simulation paper (§§3–6). The implementation here specializes that construction to a small-strain quadratic material; it does not implement their inversion handling or collision solver. [Original paper](https://pages.cs.wisc.edu/~sifakis/papers/quasistatics_sca_2005.pdf)

Store the strain vector as

$$e=(\epsilon_{xx},\epsilon_{yy},\epsilon_{zz},
\gamma_{xy},\gamma_{yz},\gamma_{zx})^T,\qquad \gamma_{ij}=2\epsilon_{ij}.$$

For vertex $a$, the three columns of the $6\times12$ matrix $B_e$ are

$$B_a=\begin{bmatrix}
g_{ax}&0&0\\0&g_{ay}&0\\0&0&g_{az}\\
g_{ay}&g_{ax}&0\\0&g_{az}&g_{ay}\\g_{az}&0&g_{ax}
\end{bmatrix},\qquad e=B_eu_e.$$

The $6\times6$ matrix $D$ has $\lambda+2\mu$ on the three normal diagonals, $\lambda$ on their off-diagonals, and $\mu$ on the three engineering-shear diagonals. Engineering shear is essential here: substituting $\epsilon_{xy}$ for $\gamma_{xy}$ without changing $D$ gives the wrong energy and stress. The stress vector order is $(\sigma_{xx},\sigma_{yy},\sigma_{zz},\sigma_{xy},\sigma_{yz},\sigma_{zx})$.

Because strain is constant in this element,

$$U_e=\tfrac12 V_e u_e^TB_e^TDB_eu_e,
\qquad K_e=V_eB_e^TDB_e,\qquad f_{\mathrm{int},e}=-K_eu_e.$$

This uses a volume integral and a material strain energy. It is not a network of springs on the tetrahedron's six edges. Sharing vertices accumulates each element's forces into a global vector; it does not count the same material volume twice.

As a small arithmetic check, the first $n=1$ tetrahedron is $(0,0,0)$, $(L,0,0)$, $(L,W,0)$, $(L,W,H_b)$. Its volume is $2.6666667\times10^{-6}$ m³, and its gradients in m⁻¹ are

$$g_0=(-25,0,0),\quad g_1=(25,-50,0),\quad
g_2=(0,50,-50),\quad g_3=(0,0,50).$$

Before solving the quadratic case, use the simpler affine patch $u=(0.02x,0,0)$ and its own compatible constant boundary tractions, with zero body force. The four axial displacements are $(0,0.0008,0.0008,0.0008)$ m. Multiplication by $B$ gives axial strain 0.02 and zero shear. Stress is $(2400,800,800,0,0,0)$ Pa; the element stores 0.000064 J. Its material force on node 0 has $+0.16$ N axial component. Over all six tetrahedra, stored energy is 0.000384 J and the external clamped-face reaction is −0.96 N in $x$. The analytic patch test checks displacement, stress, energy, support sign and ramp work on several meshes.

## Integrate loads and solve the assembled problem

For a constant body force, the consistent nodal load from one tetrahedron is $V_eb/4$. For a surface triangle,

$$f_a^{\mathrm{surface}}=\int_{\Gamma_e}N_a(X)t(X)\,dA.$$

The manufactured traction varies linearly in $x$, so multiplying it by $N_a$ gives a quadratic polynomial. The code integrates it with the degree-two, three-point triangle rule at barycentric coordinates $(2/3,1/6,1/6)$ and permutations, each weighted by one third of the triangle area. Uniformly distributing the resultant of a varying traction would change the assembled load.

Assembly adds $K_e$ and the loads at shared nodes. Eliminate clamped degrees of freedom, retaining their loads for reaction recovery. All prescribed displacements in this lesson are zero, so there is no nonzero-Dirichlet correction to the right-hand side. Solve

$$K_{ff}u_f=f_f,\qquad u_c=0.$$

The implementation stores small element matrices and evaluates global matrix-vector products by scattering their contributions; it does not form a global dense matrix. A Jacobi-preconditioned conjugate gradient solve uses the diagonal of $K_{ff}$. The stopping condition is a **freshly recomputed** free-degree residual,

$$\|K_{ff}u_f-f_f\|_2\leq
\max(10^{-12}\,\mathrm{N},\;10^{-10}\|f_f\|_2).$$

If only the recursively updated residual passes, the code recomputes it and restarts when necessary. The default iteration cap is 10000. A failed solve returns `converged:false`; integration must not label that result a reference. Shewchuk's original notes explain the quadratic minimum, PCG, diagonal preconditioning and residual checks (§§3, 11–12, Appendix B3). The particular tolerances and fixtures here are authored. [Original notes](https://www.cs.cmu.edu/~quake-papers/painless-conjugate-gradient.pdf)

Recover reactions using the **full** assembled system:

$$r_c=(Ku-f)_c.$$

At free nodes, $(Ku-f)_f$ is an error residual, not a support reaction. The sum of external loads plus clamped reactions should vanish within the accumulated free residual. Because the clamp has zero velocity, it does no work despite supporting force. The module exposes individual reactions, their resultant, the balance defect, stored energy, strain and stress.

```text
for each tetrahedron:
    compute positive reference volume and shape gradients
    construct engineering-strain B and material D
    store K_e = V B^T D B
    scatter body force and mass
for each exterior triangle except the clamp:
    integrate N_a times prescribed traction
solve free degrees with PCG and a recomputed residual
recover fixed reactions from the uneliminated equations
```

## Separate spatial error from solve error

A linear tetrahedron cannot reproduce $x^2$ exactly. Even a tiny algebraic residual can accompany an inaccurate spatial approximation. Measure the displacement error over the entire reference volume, rather than just the tip or mesh nodes:

$$\eta_{L^2}=\frac{(\int_\Omega\|u_h-u^*\|^2dV)^{1/2}}
{(\int_\Omega\|u^*\|^2dV)^{1/2}},\qquad
\eta_E=\frac{(\int_\Omega (e_h-e^*)^TD(e_h-e^*)dV)^{1/2}}
{(\int_\Omega e^{*T}De^*dV)^{1/2}}.$$

`l2RmsM` divides the squared displacement integral by the volume before taking the square root; it has metres as units. The undivided displacement integral's square root would have units m^(5/2), so it must not be labeled a displacement in metres. The energy norm has units $\sqrt{\mathrm{J}}$; it is not stored energy itself.

The code integrates these polynomial errors with a Duffy transformation of a four-point Gauss rule in each of three coordinates. Its Jacobian is $(1-r)^2(1-s)$ and it scales by $6V_e$. This integrates the quartic displacement-error square exactly up to floating-point roundoff. Independent tests verify its analytic normalization: the exact RMS displacement is $cL^2/\sqrt5$, and the exact energy-norm denominator is $\sqrt{2U^*}$.

The generated table below shows displacement error decreasing from about 55% at $n=1$ to 2.36% at $n=12$, while the free residual remains around $10^{-11}$ N or smaller. The measured displacement orders approach two and the energy orders approach one on these meshes; coarse rows do not establish asymptotic order. At $n=3$, the static stored energy is approximately 0.00012494 J, close to 0.000128 J despite a 20.9% relative displacement-field error. A single global energy value can conceal a spatially inaccurate field.

## Give both solvers the same implicit target

For the speed comparison, use the quadratic case's **same** mesh and constant loads, but start with $u_n=v_n=0$ and take one backward-Euler step of $h=0.0005$ s. Each element contributes $\rho V_e/4$ to each of its four nodal masses. The mass is lumped, and the three coordinate entries for a node repeat that same nodal mass; adding all three entries would triple-count physical mass.

With frozen loads and no damping law, the equations are

$$v_{n+1}=\frac{u_{n+1}-u_n}{h},\qquad
M\frac{v_{n+1}-v_n}{h}=f-Ku_{n+1}+r,$$

and the free solve becomes

$$(K+M/h^2)u_{n+1}=f+(M/h^2)(u_n+h v_n).$$

Equivalently, set $y=u_n+h v_n+h^2M^{-1}f$ on free nodes and minimize

$$\Phi(u)=\tfrac1{2h^2}(u-y)^TM(u-y)+\tfrac12u^TKu,\qquad u_c=0.$$

The dense solve in the focused tests uses independently coded pivoted Gaussian elimination for a tiny system; it agrees with PCG. Backward Euler evaluates elastic forces at the new displacement. Baraff's original notes introduce that implicit choice and its treatment of stiffness. [Original course notes](https://www.cs.cmu.edu/~baraff/sigcourse/notese.pdf)

This step is not static equilibrium and its small final displacement is not the continuum static solution. Nor does unconditional stability for this linear positive-definite system imply temporal accuracy. This contribution provides spatial convergence and algebraic convergence/sensitivity evidence; it does not certify a continuous transient trajectory or timestep convergence of anatomical motion.

Backward Euler also dissipates energy numerically. With $T=\tfrac12v^TMv$, a converged step satisfies the independently derived identity

$$T_{n+1}+U_{n+1}-T_n-U_n
=f^T(u_{n+1}-u_n)-D_{\mathrm{BE}},$$

$$D_{\mathrm{BE}}=\tfrac12(v_{n+1}-v_n)^TM(v_{n+1}-v_n)
+\tfrac12(u_{n+1}-u_n)^TK(u_{n+1}-u_n)\geq0.$$

Here work uses the constant load over the actual displacement increment. This is distinct from the half-load static ramp. A test covers nonzero initial displacement and velocity with the clamp respected. Numerical dissipation is reported separately from a physical damping mechanism; none is added here.

For this step the reaction is

$$r_c=[Ku+(M/h^2)(u-u_n-hv_n)-f]_c.$$

The global check is external force plus support reaction minus inertia. At a finite inaccurate iterate that balance may fail; the defect is shown rather than folded into an invented support.

## Use compliant constraints without changing the material

The compliant solver follows the XPBD local update with accumulated multipliers and timestep-scaled compliance. Macklin, Müller and Chentanez derive its energy and implicit formulation and the Gauss–Seidel update in their original paper (Algorithm 1, §4, equations 5–9 and 16–18). [Original XPBD paper](https://mmacklin.com/xpbd.pdf)

For this lesson, derive a transparent modal decomposition of the **same** $D$. In engineering-strain coordinates, its orthonormal modes are

$$q_0=(1,1,1,0,0,0)/\sqrt3,\quad
q_1=(1,-1,0,0,0,0)/\sqrt2,\quad
q_2=(1,1,-2,0,0,0)/\sqrt6,$$

and the three unit vectors for engineering shear. Their eigenvalues are $d_0=3\lambda+2\mu$, $d_1=d_2=2\mu$, and $d_3=d_4=d_5=\mu$. For each tetrahedron and mode, define

$$C_j(u)=q_j^TB_eu_e=g_j^Tu_e,\quad k_j=V_ed_j,\quad
\alpha_j=1/k_j,\qquad U_e=\sum_{j=0}^5\tfrac12k_jC_j^2.$$

The constraints $C_j$ are dimensionless strain components; $g_j$ has units m⁻¹, $k_j$ has units J, and $\alpha_j$ has units J⁻¹. A test compares this energy to $\tfrac12u^TKu$ for a field with normal and shear strain. We therefore compare two solution algorithms for one FEM energy, rather than attributing an edge-network model difference to solver speed.

With inverse nodal mass $w_a=1/m_a$ at free coordinates and zero at the clamp, initialize $u=y$ and every multiplier $\ell_j=0$. Use $\widetilde\alpha_j=\alpha_j/h^2$. Each local update is

$$\Delta\ell_j=\frac{-C_j(u)-\widetilde\alpha_j\ell_j}
{g_j^TM^{-1}g_j+\widetilde\alpha_j},\qquad
u\leftarrow u+M^{-1}g_j\Delta\ell_j,\qquad
\ell_j\leftarrow\ell_j+\Delta\ell_j.$$

The multiplier $\ell_j$ has units J·s² and is distinct from the material Lamé parameter $\lambda$. At convergence, $\ell_j/h^2=-k_jC_j$; multiplying by $g_j$ gives the modal restoring nodal force in N. At finite sweeps this constitutive relation has a defect. The reported stresses and reactions are recomputed from the material energy at the current displacement, rather than advertised as converged multiplier forces.

```text
predict free displacements with current u, v and frozen external force
zero all per-element mode multipliers for this step
repeat the requested number of sweeps, in fixed element/mode order:
    for every scalar strain mode:
        evaluate C at the current displacement
        compute delta multiplier including alpha/h^2 and accumulated multiplier
        update free displacements and that multiplier
recompute material energy, force residual and support reactions
compare with the matched PCG result
```

Because the gradients are constant, the update preserves $M(u-y)=G^T\ell$ on free coordinates. The converged constraint equations $Gu+\widetilde\alpha\ell=0$ then imply the same $(K+M/h^2)$ system. This is an algebraic argument for this **linear** fixture, not a guarantee for arbitrary nonlinear/contact XPBD. Finite sweeps retain error, and reversing order changes finite-sweep results. The module resets multipliers per call and uses no warm start or relaxation parameter.

## Read accuracy and cost together

For $A_h=K+M/h^2$, compare the finite-sweep displacement $u_s$ to the tightly solved discrete result $u_r$ using

$$\eta_\Phi=\frac{\sqrt{(u_s-u_r)^TA_h(u_s-u_r)}}{\sqrt{u_r^TA_hu_r}}.$$

This measures the quadratic objective error in a stiffness-and-inertia weighted norm. It is neither a pointwise stress error nor a percentage anatomical error. Also show maximum nodal displacement error in metres and the relative free force residual. Those quantities have different interpretations and tolerances.

For the recorded $n=3$, $h=0.0005$ s case, one sweep is quick but has about 20% objective-norm error. Five sweeps bring that error below 1%; ten bring it below 0.05%. Fifty approach the matched discrete answer to about $3\times10^{-11}$ relative objective norm and cost more than PCG in the recorded run. Thus a visibly or numerically acceptable approximation can save work, while solving to reference accuracy can erase that advantage.

The timings below belong to Node 24.19.0, V8 13.6.233.17-node.51 on this shared virtualized Linux x86-64 executor reporting an Intel Xeon Platinum 8573C. Each method has eight warmups and 31 single-call samples with alternating measurement order. Median and 10th–90th percentile samples are shown; raw samples are retained. Solves use a preassembled case; per-call allocation, validation and multiplier reset are included. Diagnostics, error integration and rendering are excluded. Shared case assembly constructs both representations and is timed separately. This is not an end-to-end production comparison against an optimized sparse FEM package, a GPU XPBD implementation or a browser frame-rate benchmark. Element visits and scalar constraint visits perform different amounts of work and cannot be compared as equal operations.

The step sensitivity table changes $h$ while comparing each row to its own converged implicit target. Five sweeps' error rises substantially with $h$. At $h=0.005$ s it exceeds 100% and its strain norm exceeds the intended small-strain lesson range. The mesh sensitivity table also shows error rising with resolution at a fixed sweep budget. Neither compliance scaling nor a material parameter gives finite iterations exact timestep or iteration independence. These failures should remain visible in a renderer.

<!-- BEGIN GENERATED EVIDENCE -->
### Executed evidence

Generated by `generate.mjs` by executing `continuum.mjs`. All cases are authored; no measurements of human tissue. Full precision, raw timing samples, parameters and source hashes: `reference.json`. Renderer geometry/fields: `example.json`.

## Static spatial convergence against the quadratic continuum solution

| n per direction | nodes / tets | PCG iterations | relative displacement L2 | relative energy norm | observed L2 order | free residual (N) |
|---:|:---|---:|---:|---:|---:|---:|
| 1 | 8 / 6 | 7 | 5.502e-1 | 4.306e-1 | — | 3.919e-15 |
| 2 | 27 / 48 | 30 | 3.085e-1 | 2.246e-1 | 0.83 | 3.865e-11 |
| 4 | 125 / 384 | 82 | 1.471e-1 | 1.185e-1 | 1.07 | 2.153e-11 |
| 8 | 729 / 3072 | 171 | 4.944e-2 | 6.131e-2 | 1.57 | 1.156e-11 |
| 12 | 2197 / 10368 | 254 | 2.355e-2 | 4.127e-2 | 1.83 | 9.087e-12 |

## Same discrete implicit step, n=3, h=0.0005 s, from rest

| method / sweeps | work count | relative objective-norm error | max nodal error (m) | relative free force residual | median solve (ms) | p10–p90 (ms) |
|:---|---:|---:|---:|---:|---:|:---|
| PCG, 24 iterations | 4212 element visits | reference | reference | 3.723e-11 | 2.126 | 2.038–2.559 |
| compliant, 0 | 0 constraint visits | 1.355e+0 | 1.011e-4 | 1.650e+0 | unmeasured predictor | — |
| compliant, 1 | 972 constraint visits | 2.007e-1 | 1.895e-5 | 2.970e-1 | 0.191 | 0.184–0.249 |
| compliant, 2 | 1944 constraint visits | 1.122e-1 | 6.731e-6 | 1.583e-1 | 0.257 | 0.238–0.311 |
| compliant, 5 | 4860 constraint visits | 9.212e-3 | 7.448e-7 | 1.606e-2 | 0.425 | 0.402–0.490 |
| compliant, 10 | 9720 constraint visits | 4.248e-4 | 2.920e-8 | 6.530e-4 | 0.729 | 0.705–0.971 |
| compliant, 20 | 19440 constraint visits | 1.775e-6 | 1.706e-10 | 3.290e-6 | 1.351 | 1.305–1.592 |
| compliant, 50 | 48600 constraint visits | 2.866e-11 | 2.179e-15 | 4.992e-13 | 3.396 | 3.228–3.939 |

Element and scalar-constraint visits perform different work. Assembly median 8.031 ms; diagnostic median 0.581 ms, separate from solve times. v24.19.0, V8 13.6.233.17-node.51, linux 6.18.44, x64, INTEL(R) XEON(R) PLATINUM 8573C, 5 visible logical CPUs. Single thread, virtualized shared host; these timings are not universal benchmarks or browser-frame rates.

## Five sweeps with different implicit steps

Each row uses its own matched PCG target; changing h changes the physical discrete-time solution. This is solver sensitivity, not a temporal convergence experiment.

| h (s) | relative objective-norm error | max nodal error (m) | max strain tensor norm |
|---:|---:|---:|---:|
| 0.0005 | 9.212e-3 | 7.448e-7 | 7.226e-3 |
| 0.001 | 2.462e-1 | 3.555e-5 | 9.753e-3 |
| 0.002 | 5.263e-1 | 6.912e-5 | 1.462e-2 |
| 0.005 | 1.704e+0 | 8.328e-4 | 5.742e-2 |

## Five sweeps with different meshes, h=0.0005 s

Each row uses its own matched PCG target. This isolates algebraic solver error, separately from static continuum discretization error.

| n | nodes / tets | relative objective-norm error | relative free residual |
|---:|:---|---:|---:|
| 1 | 8 / 6 | 4.277e-7 | 4.389e-7 |
| 2 | 27 / 48 | 1.037e-3 | 1.212e-3 |
| 3 | 64 / 162 | 9.212e-3 | 1.606e-2 |
| 4 | 125 / 384 | 4.778e-2 | 6.754e-2 |

<!-- END GENERATED EVIDENCE -->

## Where medical, CAD and graphics techniques fit

A well-converged continuum discretization can provide interior displacement, strain, stress, energy and boundary reactions under explicit material and boundary assumptions. It can support sensitivity studies and inverse identification when compatible observations are available. CAD-style stress analysis similarly needs a meaningful geometry, load path and quantity of interest. A small linear element is useful for learning those relationships and for modest deformation in a valid reference frame; it is not an automatic high-accuracy anatomical analysis.

Approaching incompressibility requires special attention. As $\nu\to1/2$, the bulk response grows without bound relative to shear. A displacement-only linear tetrahedron can become overly constrained and show volumetric locking, while the linear system becomes poorly conditioned. Shrinking a residual tolerance does not cure a poor approximation space. A mixed displacement/pressure formulation, appropriate element family or another verified treatment requires its own implementation and tests; none is smuggled into this fixture. Sliver elements, nonuniform material and new attachment maps also change conditioning and convergence.

The repository's audited Ryan study uses a 3D nearly incompressible fibre-reinforced active/passive muscle model with pennation and transverse loading. Its coupling mechanisms are substantially richer than our passive isotropic model. It supplies motivation for spatial energy and load-direction questions, not coefficients or validation for this block. [Original study, Materials and Methods](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full)

The already audited Iivarinen study identifies layered forearm properties through indentation and inverse FE fitting in nine subjects. Its original abstract does not make our authored 100 kPa modulus a measured forearm value, and fitted effective properties require their study context. [Original abstract](https://pubmed.ncbi.nlm.nih.gov/21696992/)

Mitchell and colleagues' preliminary local-flap surgical simulator illustrates that interactive FEM and medical teaching can coexist. Their Discussion distinguishes interactive demonstration from patient-specific prediction and highlights tissue-property and rate issues. A method's application label therefore does not establish predictive accuracy; the target output and evidence still matter. [Original paper, Discussion](https://pages.cs.wisc.edu/~sifakis/papers/surgery_simulator_JRS.pdf)

For a games/film lesson, a limited compliant solve can offer useful deformation at lower measured solve cost when its error is acceptable. This comparison preserves the constitutive model to isolate that tradeoff. Other practical graphics methods may change both the model and the solve: edge networks, shape matching, reduced bases, cached deformation or geometric skinning each need their own matched-case disclosure. A force-free skinning transform cannot become a source of contact pressure merely because it resembles this block's boundary.

The next anatomical contribution would require registered geometry, material and fibre fields, attachments, finite-strain objectivity, contact/self-contact, active-force ownership, and validation against compatible observations. Accurate predictions also require uncertainty analysis of loads and parameters, not just mesh refinement. Here the anatomy data, active elbow, affine proxy and new spatial fixture remain separate systems with explicit boundaries.

## A renderer can make the differences legible

Show the reference mesh, the static exact field, the static FEM field and the two **matched implicit-step** results with clearly labeled modes. The static and dynamic views must not share an “accuracy” label. Render a vertex directly as $X_v+u_v$. If displaying magnified deformation, expose the magnification and retain unscaled SI diagnostics; it is a display transform, not physics. Use identical camera and magnification in paired views.

Color by element stress or nodal displacement error with a common stated scale. Laboratory 6 now provides both diagnostics: element von Mises stress uses a fixed 0–4,000 Pa scale, and nodal displacement error uses a fixed 0–0.5 mm scale in both views and across sweep/mesh/step changes. Blue, purple and red denote the lower endpoint, midpoint and upper endpoint. Any values exceeding the range are clipped visibly and reported numerically. The implicit reference has zero error against itself; the finite compliant field is compared against that same converged target. Static mode compares both nodal fields against the sampled exact static displacement. Stress for those sampled fields is evaluated on the P1 elements, so it is the piecewise-constant stress of their interpolants, not the exact continuous stress at every surface point. Clamp forces reported for those fields are their discrete fixed-node residuals, on the block, with free-node residuals separately labeled. Element stress is piecewise constant and discontinuous across faces; averaging it onto a smooth visual surface is an additional rendering operation, not a more accurate stress solve. Draw the clamp and the prescribed body/face loads, and provide a text summary with force residual, reaction, energy, and model limits. A static manufactured solution whose support resultant is zero should still show its balanced applied loads.

Useful controls are mesh resolution, compliant sweep count, and step size, with Reset reproducing the same state. Reassemble once after a mesh/material change; do not rebuild the element matrices every animation frame. The supplied example uses only 64 vertices and 162 tetrahedra. Larger meshes can be computed by a Web Worker if needed; this contribution does not certify main-thread latency. Check `converged` before presenting a discrete reference and keep an unconverged finite-sweep result labeled approximate.

`README.md` documents array layout, exports, commands and integration. `sources.json` records exactly which primary texts and sections were opened. `data/provenance.json` and the source-bound test receipt identify the executed code. The inaccessible Sifakis/Barbič course notes remain bibliography-only in the parent audit; no unread formula is imported here. All tables and geometry in this contribution are original generated teaching artifacts, and the existing book assembly and proof registry are left to their owners.
