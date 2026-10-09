# Uneven stretch and local volume {#nonuniform-local-volume}

The previous property lesson measured homogeneous deformations. Now prescribe a smooth deformation along one reference prism: neighbouring material sections can stretch differently while each point preserves its volume. This is an imposed geometric map, with no force balance, passive material response, activation or anatomical prediction. It is a different construction from the later serial specimen, whose two separate homogeneous blocks are joined by a spacer.

## A complete gradient, including shear {#nonuniform-complete-gradient}

Let the material coordinate satisfy $0\le S\le L_0$, with $L_0>0$, mean stretch $m>0$ and dimensionless uneven-stretch amplitude $-1<a<1$. The reference section is a regular 16-sided polygon of circumradius 15 mm; the reference length is 120 mm. Define

$$\lambda(S)=m[1+a(2S/L_0-1)],\qquad x(S)=m[(1-a)S+aS^2/L_0].$$

The transverse coordinates are $y=b(S)Y$ and $z=b(S)Z$, with $b(S)=1/\sqrt{\lambda(S)}$ under local compensation and $b=1$ otherwise. Differentiating the map gives

$$F=\begin{bmatrix}\lambda&0&0\\b'Y&b&0\\b'Z&0&b\end{bmatrix},\qquad J=\det F=\lambda b^2.$$

The actual stretch gradient is $\lambda'=2ma/L_0$, with units of inverse length. Under compensation, $b'=-\lambda'/(2\lambda^{3/2})$. The off-axis terms describe shear; dropping them would misstate the gradient even though its determinant would agree. The displayed engineering strain $\lambda-1$ refers to the centerline, not every surface fibre.

Positivity makes the axial map strictly increasing, and positive transverse scaling makes the map injective. The ordinary change-of-variables argument then gives continuum volume conservation when $J=1$. These differentiation, injectivity and integration arguments are separately audited mathematical reasoning. The Lean declarations below prove properties of the **declared matrix**, positive stretch on the stated interval and an algebraic straight-cell error formula; they do not formally prove those analytic arguments or the mesh implementation.

## Compare local and total conservation {#nonuniform-local-total}

{{nonuniform-lab}}

At $m=1$, $a=0.4$, local compensation gives endpoint stretches 0.6 and 1.4, while $J=1$ throughout. Disable compensation: the total continuum volume ratio still equals one, but the local Jacobian ranges from 0.6 to 1.4. Expansion and contraction cancel globally. Total volume alone cannot establish local incompressibility.

The closed three-dimensional boundary mesh and its displayed longitudinal section use the same vertices and fixed millimetre scale. Signed boundary-triangle volumes are independently compared with regular-polygon/frustum volumes. Straight cells approximate a curved exact map: their measured volume is slightly excessive under nonuniform compensation and approaches the continuum result as cells are refined. The controls report this nonzero discrepancy explicitly.

For positive endpoint ratio $r=\sqrt{\lambda_1/\lambda_0}$, the independently derived straight-cell ratio is

$$R(r)=\frac{(1+r^2)(1+1/r+1/r^2)}6,\qquad R(r)-1=\frac{(r-1)^2(r^2+3r+1)}{6r^2}\ge0.$$

This identity explains the discrepancy. Its Lean proof concerns the algebraic expression; it does not certify triangle orientation, topology, floating-point arithmetic or convergence of a numerical implementation.

## Six scoped Real contracts {#nonuniform-real-contracts}

{{proof:nonuniform-gradient-determinant}}

{{proof:nonuniform-positive-stretch}}

{{proof:nonuniform-pointwise-compensation}}

{{proof:nonuniform-nonuniform-isochoric}}

{{proof:nonuniform-straight-cell-error}}

{{proof:nonuniform-straight-cell-volume-bound}}

## Accepted source and remaining dependencies {#nonuniform-evidence-boundaries}

Independent acceptance applies to exact source `15c624c32378b9c773a3d0c25a65150804b68c90`, following mathematical, model, browser and PDF review of `8fd21a3177242fde3dca2a3dffa1c5f4c0350bdd`. Their sole difference corrects the browser receipt's description of the six Real contracts. The complete original contribution and its claim inventory are preserved unchanged. The book registry adds display metadata and copies the exact Lean source; all original 103 proof identities and anatomy references remain unchanged. [Source composition and independent acceptance](nonuniform/composition.json) accompany the portable edition.

This lesson supplies no material law or equilibrium solve. New continuous passive-specimen, scalar tension/mass controller and anatomical-capstone sources remain excluded. The next anatomical dependency is displacement-space and material/pressure coupling adequacy at isolated matched-pose fixtures, against retained local compression and full-nodal residual failures, before force rematching or new trajectories. Prescribed local volume conservation does not resolve that dependency or establish anatomical completion.
