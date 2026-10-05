# Measure deformation before choosing a muscle law

These progressive property lessons separate geometry, constitutive response and equilibrium. A shape that keeps its total volume can still have uneven local compression; a shape that looks muscular has not thereby passed a mechanical test. The anatomical capstone retains its failed cases and its force and geometry gates.

## 1. Measure a prescribed deformation

For reference vertices $X_i$ and current vertices $x_i$, each in metres, construct edge matrices $D_m=[X_1-X_0, X_2-X_0, X_3-X_0]$ and $D_s=[x_1-x_0,x_2-x_0,x_3-x_0]$. A nondegenerate, positively oriented reference is required. The affine deformation gradient, local volume ratio and Green strain are

$$F=D_sD_m^{-1},\qquad J=\det F,\qquad E_G=\frac12(F^TF-I).$$

Translation cancels from the edges. A rigid rotation has $E_G=0$; simple shear can have $J=1$ while $E_G\ne0$. Volume preservation does not mean absence of strain.

The independent measurement uses the oriented boundary triangles. For any common origin $o$, with outward face ordering,

$$V_{\partial}=\frac16\sum_{(a,b,c)}(a-o)\cdot[(b-a)\times(c-a)].$$

The browser computes this triangle sum without calling the determinant helper. It reports $V_{\partial}/V_{\partial,0}-J$, in dimensionless units, rather than assuming agreement. Negative signed volume or nonpositive $J$ rejects the candidate and retains the last valid displayed state. This four-node affine test does not certify curved P2 elements or a whole moving tissue envelope.

{{property:deformation}}

{{proof:volume-edge-translation}}

{{proof:volume-det-compose}}

## 2. Exact isochoric kinematics

Prescribe $F=\operatorname{diag}(\lambda,b,b)$ with positive dimensionless stretches. Then $J=\lambda b^2$. In the isochoric construction $b=1/\sqrt\lambda$, so $J=1$ in exact real arithmetic. The interactive controls also allow independent stretches, which need not preserve volume. This is a kinematic construction, not a minimization or a muscle contraction law.

For the rectangular reference, $L=\lambda L_0$, $A=b^2A_0$ and $AL=JV_0$. Cross-section area is the area normal to the axial direction, measured from two transverse edges. Exterior area is the sum of all boundary-triangle areas. They have the same units, square metres, but different mechanical meanings. Neither is automatically physiological cross-sectional area (PCSA). The independent boundary-volume measurement remains visible when the isochoric toggle is selected.

{{property:isochoric}}

{{proof:volume-diagonal}}

{{proof:volume-isochoric-sqrt}}

## 3. Nonuniform cross-section: a reduced axial oracle

Take a small-strain bar with length $L$ in metres, positive area $A(s)$ in square metres, constant modulus $E$ in pascals, no distributed axial load, and a tensile-positive resultant $N$ in newtons. Force balance gives $dN/ds=0$. The passive law gives $\epsilon(s)=N/[EA(s)]$, so

$$\Delta L=\int_0^L\epsilon(s)\,ds=N\int_0^L\frac{ds}{EA(s)}.$$

For linear **area** taper $A(s)=A_1[1+(r-1)s/L]$, the exact compliance is $L\ln(r)/[EA_1(r-1)]$, with limit $L/(EA_1)$ at $r=1$. Numerical midpoint integration is compared with that analytic integral. Linear area taper is a separate geometric assumption from a radius taper. The exterior surface influences surface traction and contact; it does not replace $A(s)$ in this axial law.

Add a separately declared uniform active-stress offset $a\sigma_0$, still under this reduced small-strain law: $\epsilon=N/(EA)-a\sigma_0/E$. With both ends fixed, $\int\epsilon ds=0$ determines the constant $N$. Two equal-length segments with $A_2=2A_1$ and $a\sigma_0/E=0.01$ give $N=(4/3)A_1a\sigma_0$, narrow strain $+1/300$ and wide strain $-1/300$. Local extension and compression coexist even though total length is fixed. This offset model has no force–length/velocity dependence, transverse equilibrium, pennation, ECM, fluid or anatomical calibration; it is not a complete active muscle model.

{{property:tapered}}

The executable oracle is [the tapered-bar module](web/tapered-bar.mjs). Tests check the logarithmic integral, refinement and the two-segment fixed-end case. Its scope is numerical evidence for this declared reduced law; the kinematic Lean claims above do not prove its mechanics.

## What the exact claims cover

The proposed real-number proof source targets edge translation invariance, determinant composition, the actual diagonal determinant and the positive square-root isochoric construction. These four declarations await fresh kernel compilation against the pinned mathlib dependency. They must not be displayed as checked proof cards until that succeeds. Separate numerical and browser tests cover the implemented controls and boundary measurements. Neither class of test validates measured biological parameters or resolves the capstone's local compression and full nodal stationarity failures.
