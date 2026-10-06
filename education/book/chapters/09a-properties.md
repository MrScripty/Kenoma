# Measure deformation before choosing a muscle law {#measure-deformation-before-choosing-a-muscle-law}

These progressive property lessons separate geometry, constitutive response and equilibrium. A shape that keeps its total volume can still have uneven local compression; a shape that looks muscular has not thereby passed a mechanical test. The anatomical capstone retains its failed cases and its force and geometry gates.

Start here after [force](#force-changes-motion), [torque](#a-force-has-an-application-point) and [energy](#energy-reveals-numerical-error). First ask **what changed in the shape?** Then impose a simple volume relation. Finally introduce one axial force law to ask why different sections strain differently. No contact solver, anatomical mesh or finite-element assembly is needed for these three lessons. The [later material chapter](#from-a-spring-to-a-volume-of-tissue) adds energy, stress and equilibrium in three dimensions.

| Quantity | Units | How to read it here |
|:--|:--|:--|
| Reference/current positions $X,x$; length $L$ | m | Positions before/after an imposed change; distance along the bar |
| Cross-section $A$; boundary volume $V$ | m²; m³ | Area across the axial direction; volume enclosed by oriented faces |
| Stretch $\lambda,b$; volume ratio $J$ | dimensionless | Current/reference length or volume; one means unchanged |
| Deformation gradient $F$; strain $E_G,\epsilon$ | dimensionless | Local shape map; measures of deformation, not forces |
| Axial resultant $N$ | N | Total tensile force through a section, not stress at a point |
| Modulus $E$; active-stress offset $\sigma_0$ | Pa = N/m² | Parameters of the declared axial material law |
| Activation coefficient $a$ | dimensionless, 0–1 | Static multiplier of the authored stress offset, not an integrated activation trajectory |
| Compliance $C$ | m/N | Extension per applied force in the passive bar |

The symbol $F$ below is a deformation matrix, not the force vector of Laboratory 1. The bar's $E$ is a modulus, not energy in joules; $E_G$ denotes Green strain. Stretches and strains have no units: stretch 1.2 means 20% longer, while axial strain 0.01 means 1% extension in the small-strain bar. These static property lessons do not advance time, integrate activation or calculate metabolic energy.

## 1. Measure a prescribed deformation

**Question:** if we move the vertices ourselves, how do we measure stretch, shear and volume change? The reference tetrahedron has four vertices; its three edges from vertex zero are stored as the columns of $D_m$. The current edges form $D_s$. Multiplying by $D_m^{-1}$ removes the original edge scale, so $F$ maps a small reference edge to its current edge. You can begin with the numerical stretch and volume readouts before working through this matrix notation.

For reference vertices $X_i$ and current vertices $x_i$, each in metres, construct edge matrices $D_m=[X_1-X_0, X_2-X_0, X_3-X_0]$ and $D_s=[x_1-x_0,x_2-x_0,x_3-x_0]$. A nondegenerate, positively oriented reference is required. The affine deformation gradient, local volume ratio and Green strain are

$$F=D_sD_m^{-1},\qquad J=\det F,\qquad E_G=\frac12(F^TF-I).$$

Translation cancels from the edges. A rigid rotation has $E_G=0$; simple shear can have $J=1$ while $E_G\ne0$. Volume preservation does not mean absence of strain.

The independent measurement uses the oriented boundary triangles. For any common origin $o$, with outward face ordering,

$$V_{\partial}=\frac16\sum_{(a,b,c)}(a-o)\cdot[(b-a)\times(c-a)].$$

The browser computes this triangle sum without calling the determinant helper. It reports $V_{\partial}/V_{\partial,0}-J$, in dimensionless units, rather than assuming agreement. Negative signed volume or nonpositive $J$ rejects the candidate and retains the last valid displayed state. This four-node affine test does not certify curved P2 elements or a whole moving tissue envelope.

{{property:deformation}}

**Try and predict.** Set all three stretches to 1, shear and rotation to 0. The measured $J$ and boundary-volume ratio should both be 1, and Green strain should be zero. Change only translation X to 30 mm: it moves the tetrahedron but changes neither measurement. Next set axial stretch to 1.2: expect $J=1.2$. Restore unit stretches and set shear to 0.25: volume stays the same, but Green strain is nonzero. Rotation alone also keeps volume and strain unchanged; the components of $F$ can still change.

The controls prescribe the vertices. This lab measures $F$, $J$, Green strain and an independent boundary volume; it solves no forces, material energy, contact or equilibrium. A valid positive volume is a geometry check, not evidence of a realistic muscle response.

{{proof:volume-edge-translation}}

{{proof:volume-det-compose}}

## 2. Exact isochoric kinematics

**Question:** what lateral change would keep a rectangular block's volume exactly fixed while its axial length changes? *Isochoric* means constant volume. Here we impose the answer; no pressure or material stiffness chooses it.

Prescribe $F=\operatorname{diag}(\lambda,b,b)$ with positive dimensionless stretches. Then $J=\lambda b^2$. In the isochoric construction $b=1/\sqrt\lambda$, so $J=1$ in exact real arithmetic. The interactive controls also allow independent stretches, which need not preserve volume. This is a kinematic construction, not a minimization or a muscle contraction law.

For the rectangular reference, $L=\lambda L_0$, $A=b^2A_0$ and $AL=JV_0$. Cross-section area is the area normal to the axial direction, measured from two transverse edges. Exterior area is the sum of all boundary-triangle areas. They have the same units, square metres, but different mechanical meanings. Neither is automatically physiological cross-sectional area (PCSA). The independent boundary-volume measurement remains visible when the isochoric toggle is selected.

{{property:isochoric}}

**Try and predict.** At axial stretch $\lambda=0.8$, the 0.08 m reference length becomes 0.064 m. The imposed lateral stretch is $b=1/\sqrt{0.8}\approx1.11803$, so the reference cross-section 0.003 m² grows to 0.00375 m². Their product remains 0.00024 m³. Switch to independent stretches and set $b=1$: the same shortening now gives $J=0.8$. Read cross-section area and exterior area separately; they need not change by the same factor.

This volume-preserving motion is **prescribed kinematics**, not material-driven volume redistribution. The free-side compression example in [Laboratory 5](#tendon-tissue-coupling) later determines lateral stretch from a material law and boundary conditions, rather than imposing this square-root relation. Neither lesson specifies a complete deforming muscle.

{{proof:volume-diagonal}}

{{proof:volume-isochoric-sqrt}}

## 3. Nonuniform cross-section: a reduced axial oracle

**Question:** can one constant tensile force produce different strain along a bar? Here shape is no longer prescribed at every section. We assume a one-dimensional material law and axial balance, then calculate strain. Positive strain is extension; negative strain is compression. The coordinate $s$ runs along the reference bar; $N/A$ is axial stress in pascals. Larger area or modulus reduces passive strain at the same force.

Take a small-strain bar with length $L$ in metres, positive area $A(s)$ in square metres, constant modulus $E$ in pascals, no distributed axial load, and a tensile-positive resultant $N$ in newtons. Force balance gives $dN/ds=0$. The passive law gives $\epsilon(s)=N/[EA(s)]$, so

$$\Delta L=\int_0^L\epsilon(s)\,ds=N\int_0^L\frac{ds}{EA(s)}.$$

For linear **area** taper $A(s)=A_1[1+(r-1)s/L]$, the exact compliance is $L\ln(r)/[EA_1(r-1)]$, with limit $L/(EA_1)$ at $r=1$. Numerical midpoint integration is compared with that analytic integral. Linear area taper is a separate geometric assumption from a radius taper. The exterior surface influences surface traction and contact; it does not replace $A(s)$ in this axial law.

Add a separately declared uniform active-stress offset $a\sigma_0$, still under this reduced small-strain law: $\epsilon=N/(EA)-a\sigma_0/E$. With both ends fixed, $\int\epsilon ds=0$ determines the constant $N$. Two equal-length segments with $A_2=2A_1$ and $a\sigma_0/E=0.01$ give $N=(4/3)A_1a\sigma_0$, narrow strain $+1/300$ and wide strain $-1/300$. Local extension and compression coexist even though total length is fixed. This offset model has no force–length/velocity dependence, transverse equilibrium, pennation, ECM, fluid or anatomical calibration; it is not a complete active muscle model.

{{property:tapered}}

**Try and predict.** In passive mode, keep the default geometry and modulus and change force from 0.3 to 0.6 N: every strain and the total extension double. Doubling the modulus instead halves them. In active fixed-end mode, choose two equal-length segments and keep area ratio 2, activation 1 and active stress 1,000 Pa at modulus 100,000 Pa. The narrow section extends by $1/300$ and the wide section compresses by $1/300$, while their total length change is zero. Passive force is disabled in that mode because the fixed-end compatibility determines the reaction; active controls are disabled in passive mode.

This bar solves an axial resultant and axial strain under its stated assumptions. It does not determine lateral stretch, cross-section evolution, transverse stress, contact, three-dimensional fibre aggregation or muscle shape. The area profile is an input; neither zero net extension nor the active-stress offset supplies the missing transverse equilibrium. Refining midpoint cells improves the integral of this same reduced law, not its biological scope.

The illustrative 5% small-strain warning uses the true endpoint extrema of this monotone positive-area law, independent of midpoint display resolution. It is a warning about this approximation, not material validation.

The executable oracle is [the tapered-bar module](web/tapered-bar.mjs). Tests check the logarithmic integral, refinement and the two-segment fixed-end case. Its scope is numerical evidence for this declared reduced law; the kinematic Lean claims above do not prove its mechanics.

Continue with [anatomical evidence](#anatomy-is-evidence) before assigning these quantities to a named muscle. When you reach [tissue and rendered skin](#tissue-and-rendered-skin), reuse the measurements above while adding a material law and boundary forces. The [next material-response lesson](#compression-bulk-shear-confinement) adds bulk/shear and unilateral confinement controls. Measured fibre-to-muscle aggregation, force–length/velocity and dissipative load/hold/release lessons remain pending, as recorded in the [coverage chapter](#coverage-and-evidence).

## What the exact claims cover

The freshly checked real-number proof bundle establishes edge translation invariance, determinant composition, the actual diagonal determinant and the positive square-root isochoric construction. The four claims above are compiled from their displayed real definitions against pinned mathlib. The edge and matrix identities do not prove the oriented boundary-triangle oracle, and the isochoric identity does not prove a free-side material equilibrium. Separate numerical and browser tests cover the implemented controls and boundary measurements. Neither class of test validates measured biological parameters or resolves the capstone's local compression and full nodal stationarity failures.
