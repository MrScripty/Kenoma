# One force, unequal stretches, and local volume {#serial-specimen-volume}

**Question:** can blocks of the same material carry the same force, stretch by
different amounts, and each preserve volume? The [reduced axial bar](#measure-deformation-before-choosing-a-muscle-law)
already demonstrates uneven strain from an input area profile, including local
extension and compression under fixed ends. It predicts no lateral deformation.
This lesson adds a different, explicitly three-dimensional specimen and a
constitutive law whose force, current area and local volume agree.

## Two blocks and an explicit interface

Use two separate, homogeneous rectangular blocks in axial series. Each has a
square reference section and reference length $L_0=0.025$ m. Their reference areas
are $A_1=0.0003$ m² and $A_2=rA_1$, with default $r=2$. Ideal **bilateral axial
traction fixtures** transmit signed force and permit tangential sliding at the
loading faces. They can pull or push; ordinary frictionless compression platens
alone could not provide the tensile case. A massless spacer has fixed length
0.012 m. Its positions move with the block ends.

The two blocks may therefore change lateral size independently. The gold fixture
connection is excluded from material volume. This is an assembly of separate
blocks, not a continuous stepped or tapered solid with an unmodeled material
interface. The solved deformation is homogeneous within each block. Buckling,
shear localization and the preferred deformation among unrestricted 3D fields
are outside this homogeneous model.

With no body load, the intervening massless fixture balances the two opposing
axial resultants, so $N_1=N_2=N$. Positive $N$ is tension and negative $N$ is
compression. The equilibrium equation uses **reference** area for nominal stress,
and current area for Cauchy stress; these are different stress measures.

## Material response and the volume constraint

Each block is an incompressible isotropic neo-Hookean solid with authored shear
parameter $\mu=1500$ Pa. Its energy per reference volume is

$$W(F)=\frac\mu2(I_1-3),\qquad J=\det F=1.$$

Incompressibility is a **local material constraint**. It is not a finite bulk
penalty, and constant force does not establish it. The earlier
[bulk/shear confinement lesson](#compression-bulk-shear-confinement) retains its
different finite-bulk law and boundary conditions. The material framework and
the role of incompressibility pressure are described by
[A. F. Bower, *Applied Mechanics of Solids*, §§3.5.4–3.5.6](https://solidmechanics.org/Text/Chapter3_5/Chapter3_5.php).
The following homogeneous reduction and assembly are the model used here.

For axial stretch $\lambda_i>0$ and equal transverse stretches $b_i>0$,

$$F_i=\operatorname{diag}(\lambda_i,b_i,b_i),\qquad
J_i=\lambda_i b_i^2=1,\qquad b_i=\lambda_i^{-1/2}.$$

The full Cauchy stress is $\sigma_i=-p_iI+\mu B_i$, where $B_i=F_iF_i^T$.
Free lateral faces require $\sigma_{yy}=\sigma_{zz}=0$, giving
$p_i=\mu b_i^2=\mu/\lambda_i$. This $p_i$ is an **incompressibility multiplier**,
not measured axial plate pressure. At rest it is $\mu$, while the complete stress
tensor is zero. The resulting axial Cauchy and nominal stresses are

$$\sigma_{xx,i}=\mu(\lambda_i^2-\lambda_i^{-1}),\qquad
P_i=\frac{\sigma_{xx,i}}{\lambda_i}
=\mu(\lambda_i-\lambda_i^{-2}),\qquad N=A_iP_i.$$

The executable root solves this last equation separately for both blocks. It
does not assign stretches from a visual taper. The reduced energy and its
derivative use the same material law:

$$W(\lambda)=\frac\mu2(\lambda^2+2/\lambda-3)
=\frac{\mu}{2\lambda}(\lambda-1)^2(\lambda+2),\qquad
\frac{dW}{d\lambda}=P(\lambda).$$

Thus $U_i=A_iL_0W(\lambda_i)$, and differentiating with respect to current block
length $L_i=L_0\lambda_i$ gives $dU_i/dL_i=A_iP_i=N$. The response is elastic and
history-free; no time integration, activation or viscous loss is added.

## Solve, measure, and compare

For positive stretch and $\mu>0$,

$$\frac{dP}{d\lambda}=\mu(1+2/\lambda^3)>0.$$

The force curve is strictly increasing, with zero force at $\lambda=1$.
The narrower section has larger nominal tensile stress and larger stretch for
$N>0$. With $N<0$ it has more negative stress and smaller stretch: it compresses
more. Both blocks have the same material; this difference comes from geometry.

The current geometry is calculated from the solved stretches:

$$L_i=L_0\lambda_i,\qquad A_{i,\mathrm{current}}=A_i b_i^2=A_i/\lambda_i,
\qquad V_i=A_iL_0,\qquad
\sigma_{xx,i}=N/A_{i,\mathrm{current}}.$$

The 3D meshes use these actual lengths, widths and depths without displacement
magnification. Gray wire outlines mark the reference blocks; the camera uses a
shared physical scale across parameter edits. Front/oblique views change the
camera, not the model. Exported vertices drive a separate closed-triangle volume
measurement. Measured cross-sectional edges, length and boundary volume are
reported beside $J_i$; the volume oracle does not simply return one.

![Solved default tension, rest and compression at one physical scale. Dashed outlines are reference blocks; the moving gold spacer is excluded from material volume.](assets/property-serial.svg)

{{serial:assembly}}

Default forces, areas, stretches and independent measured volumes are generated
from the same executable law:

{{serial-table}}

**Try and predict.** Reverse $N$ from +0.1 to -0.1 N. Both blocks shorten and widen,
and the narrower block has the larger compression. Set $N=0$: both stretches,
areas and lengths return to their reference values, and stress and energy vanish.
Set $r=1$: equal material and area give equal stretches. Reverse the ratio to
$r=0.5$: block 2 becomes the narrow section and now strains more. Increase only
$\mu$: at the same force the stretches move closer to one. Reference length
changes total extension, volume and energy, but does not change local stress or
stretch at fixed area and force.

**Local-volume counterexample.** The test button constructs an unused candidate
with unchanged axial stretches but local volume ratios 1.10 and $1-0.10/r$.
Their reference-volume-weighted total is still one. Nevertheless, each block
violates $J_i=1$, and its free-side traction no longer vanishes. The candidate is
rejected and the prior solved mesh and state remain visible. A correct total
volume cannot hide a violation of this local material law.

Controls bound $500\le\mu\le5000$ Pa, $0.0003\le A_1\le0.001$ m²,
$0.5\le r\le4$, $-0.1\le N\le0.1$ N, and $0.01\le L_0\le0.04$ m.
Every target force lies within the fixed positive bracket $0.6\le\lambda\le1.75$:
at the smallest $A_i\mu=0.075$ N its endpoint forces are approximately
-0.163333 and +0.106760 N. Bisection uses a visible 8–64 iteration cap.
The force criterion is $|A_iP_i-N|\le10^{-10}$ N for **each** block. Eight iterations
can leave a valid positive-volume shape with unequal approximate resultants;
the UI reports each computed resultant and residual, rather than calling it
shared-force equilibrium. Restore 48 or 64 and compare. Invalid edits retain the
prior valid specimen; Reset restores the authored defaults and reference camera.

## Exact real claims and independent implementation checks

Twelve declarations below quantify the actual real homogeneous law. They prove
the energy factor, sign and zero state; its derivative; stress identities and
signs; strict monotonicity and conditional positive-root uniqueness; area-times-
length volume; and same-force ordering for unequal areas in tension and
compression. Root existence, numerical bisection, pressure elimination, the
matrix/mesh volume measurement and JavaScript arithmetic are not certified by
these declarations. The real kinematic identities in the first property lessons
remain separate.

{{proof:serial-real-energy-factor}}
{{proof:serial-real-energy-sign}}
{{proof:serial-real-energy-zero}}
{{proof:serial-real-energy-derivative}}
{{proof:serial-real-stress-identities}}
{{proof:serial-real-stress-sign}}
{{proof:serial-real-stress-difference}}
{{proof:serial-real-stress-monotone}}
{{proof:serial-real-root-unique}}
{{proof:serial-real-volume}}
{{proof:serial-real-tension-order}}
{{proof:serial-real-compression-order}}

Independent numerical checks solve the cubic equation
$\lambda^3-[N/(A_i\mu)]\lambda^2-1=0$, sum tetrahedral volumes from the actual mesh,
differentiate the stored energy, and verify the complete stress and current-area
conversions. Actual browser controls must also verify the displayed 3D geometry,
solver status, local-volume rejection and fallbacks. These obligations cannot be
replaced by a scope label. The lesson makes no claim about measured muscle,
continuous fibre aggregation or the unfinished anatomical capstone.
