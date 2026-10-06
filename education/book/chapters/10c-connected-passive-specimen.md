# A connected passive body: solve the shape {#connected-passive-specimen}

The [strain and volume lessons](#measure-deformation-before-choosing-a-muscle-law) measured prescribed geometry. The [serial specimen](#serial-specimen-volume) solved two separate homogeneous incompressible blocks with a spacer. The [projection interlude](#fixed-field-pressure-projection) compared a prescribed field with its weighted projection at one fixed state. Here the question changes: **when the ends of one connected passive body move, what axial and lateral deformation follows from its declared energy?**

This lesson uses the independently reviewed [repaired source 1c90c638](https://github.com/MrScripty/Kenoma/blob/1c90c63827abce0649286734ecd5fb6d1276c83e/education/AXISYMMETRIC_PROTOTYPE.md) and [evidence 05fd23cd](https://github.com/MrScripty/Kenoma/blob/05fd23cdb6a414415f1117fced93443aa9936c48/education/review/connected-end-face-repair/README.md). It is an axisymmetric finite-compliance mathematical specimen. It has no activation, tendon, anatomical calibration or muscle force–length/velocity controller. Its passive equilibrium does not establish an anatomical capstone.

## Declare the body and the loading

The reference length is $L_0=0.05\,\mathrm{m}$ and the small-end radius is $a_0=0.005\,\mathrm{m}$. Choose a uniform cylinder or a continuous linear radius taper

$$a(Z)=a_0\left(1+(\rho-1)Z/L_0\right),\qquad \rho\in\{1,1.5\}.$$

A radius ratio of 1.5 is an area ratio of 2.25. The connected specimen is obtained by revolving its meridional domain; it has no internal spacer or sliding junction between separate blocks. Its exact reference volume is

$$V_0=\frac{\pi L_0 a_0^2}{3}(1+\rho+\rho^2).$$

Every node on the complete lower and upper end faces has imposed axial displacement: zero below and $\epsilon L_0$ above, with $\epsilon=0$ or $\pm0.1$. End-face radial displacement remains free. Axis regularity gives $r=0$ and $z_R=0$. The tapered side has full natural Piola traction $PN=0$, where the unnormalized reference normal is $(1,0,-a')$. Both meridional traction components matter; a radial-only condition would be a different problem. Corner gradients remain a separate unresolved convergence question.

**End displacement is the input; reaction force is an output.** This is not the serial lesson's imposed-force experiment. There is no force controller attached to the specimen. The repaired source assigns end-face membership from mesh topology and constructs the exact closed reference endpoint. Its old three-cell bug could report convergence while failing to impose the upper displacement; the regression checks the whole face and independent compression/tension reactions rather than trusting a flag.

## One law for text, numerical state and displayed deformation

The unknowns are the connected radial and axial fields $r(R,Z)$ and $z(R,Z)$. In the cylindrical orthonormal basis,

$$F=\begin{bmatrix}r_R&0&r_Z\\0&r/R&0\\z_R&0&z_Z\end{bmatrix},\qquad J=\frac rR(r_Rz_Z-r_Zz_R).$$

On the symmetry axis, $r/R$ uses its regular limit $r_R$. The accepted stored-energy density and reference integral are exactly

$$W(F)=\frac\mu2\left(J^{-2/3}\operatorname{tr}(F^TF)-3\right)+\frac K2(\log J)^2,\qquad E=\int_{\Omega_{RZ}}W(F)\,2\pi R\,dR\,dZ,$$

with $\mu=1500\,\mathrm{Pa}$ and $K=30000\,\mathrm{Pa}$. The positive bulk modulus penalizes volume change; it does **not** impose $J=1$. Both displacement fields participate in the Q2 meridional finite-element solve. Full energy forces, the original constrained tangent and the actual axis-parity transformation are retained. There is no modified Hessian, mixed pressure, reduced ring equilibrium, volume projection or postsolve geometry correction. Material evaluations require positive hoop stretch, positive meridional determinant and $J>10^{-6}$.

{{connected-specimen}}

The static figure samples the actual solved side at the same fixed metre scale for all three poses. The interactive surface revolves the solved Q2 boundary. Its gray reference outline and camera scale stay fixed when the physical choice changes. Surface color interpolates sampled $J$; readouts and probes evaluate the actual field. The exported state contains the numerical configuration and current solution rather than an independently posed drawing.

## Read the controls as an experiment

Start with the uniform cylinder, zero end displacement and the complete solve. Choose compression, then tension. Compare the measured reaction and volume ratio with the independent homogeneous free-lateral oracle. Finite compliance gives approximately $V/V_0=0.995069$ in compression and $1.004936$ in tension for the uniform reference cases, rather than exact volume conservation. These are bounded oracle comparisons, not an anatomical law.

Next choose the taper. Inspect $J$, axial-line stretch, radial-line stretch and hoop stretch at several material coordinates. The local fields need not be uniform even though the end planes have a prescribed displacement. A probe edit changes only the measurement; it does not solve or remesh. Physics edits preserve the camera. Front and oblique views change only the view.

The native mesh menu remains **4×2, 8×4 and 16×8** Q2 cells. The worker assembles at quadrature order 7, displayed beside its values. Additional 3/6/12/24 axial-cell cases are explicitly qualification API cases, not hidden native-menu choices. Mesh differences, volume-weighted $J$ differences, force, energy and quadrature comparisons have separate receipts; a single residual does not summarize them.

Choose **one direct iteration** to inspect a deliberately nonconverged approximation at the requested displacement. Read the warning beside the current geometry and values. A genuine direct fine-compression initialization fails with an indefinite original tangent; continuation from rest reaches the bounded pose using that same tangent and stationarity criterion. Neither failure is relabeled as a successful direct solve. Unsupported requests and worker failures retain the preceding complete displayed state and warning. Reset explicitly requests the undeformed fine taper. Without WebGL, numerical controls and results remain available while the reference drawing stays labeled as static.

## Keep the evidence at its actual scope

The complete free-force residual is normalized by $\mu\pi a_0^2$, a positive scale even at zero load. The provisional stationarity target is $10^{-10}$. The Armijo energy comparison has its recorded roundoff allowance; final stationarity still uses the unmodified forces. A scaled tangent pivot spread is not a condition number. Independent eigenvalues address the constrained discrete tangent numerically, not continuum or nonaxisymmetric buckling stability.

Quadrature sensitivity remains visible. Reintegrating an order-5 stationary fine-taper state at order 3 gives scaled residuals around $1.38\times10^{-6}$ in compression and $1.26\times10^{-6}$ in tension, compared with approximately $10^{-14}$ at its assembly order. Those are reintegration diagnostics, **not** solved order-3 states or continuum error estimates. Independently solved quadrature cases are recorded separately. Coarse meshes keep their own comparisons; they do not inherit the finest-state result.

Exact-rational Bernstein bounds establish positivity for whole stored Q2 maps in the declared numerical cases. Actual browser qualification independently reconstructs the map and reads back GPU position/index buffers, including the repaired upper ring and worker trace endpoint. Wrong-radius and wrong-reaction rebuilt copies must fail these checks. This still does not prove global injectivity, floating-point refinement, continuum convergence, exact incompressibility, unrestricted stability, release dynamics, active muscle or anatomy. Corner and near-corner stress/$J$ convergence remains open.

## Nine local Real identities

These identities support the stated determinant, logarithmic storage and derivative, full side traction, force conversion and reference geometry. The four earlier kinematic helpers are reused without counting them again. None of these nine identities proves the nonlinear solver or renderer; every exact statement, assumption and limitation follows below, with the full source in its appendix.

{{proof:axis-real-axis-determinant}}

{{proof:axis-real-uniform-determinant}}

{{proof:axis-real-logarithmic-energy-nonnegative}}

{{proof:axis-real-logarithmic-energy-rest}}

{{proof:axis-real-logarithmic-energy-derivative}}

{{proof:axis-real-full-side-traction}}

{{proof:axis-real-uniform-force-conversion}}

{{proof:axis-real-profile-primitive-derivative}}

{{proof:axis-real-frustum-primitive-endpoints}}
