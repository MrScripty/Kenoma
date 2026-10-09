# Let an unloaded transverse direction respond {#directional-passive-compression}

The earlier material lesson lets two lateral stretches remain equal. Now fix the longitudinal length independently and prescribe compression in one transverse direction. The other transverse direction responds to the material law. This is a solved passive homogeneous block, not an imposed volume-preserving map, spatial bulging, active muscle or anatomy.

Read the material and architecture lessons first. [Open the unequal-transverse laboratory](labs/directional-compression/index.html). Its reference dimensions are 80 × 60 × 50 mm. Gray is the reference and blue is the solved diagonal shape; numerical lengths and forces use SI units. The diagram is a projection of the actual eight deformed block corners.

{{directional-figure}}

## An energy, three stresses and one free face

For positive stretches $l_x,l_y,l_z$, set $J=l_xl_yl_z$ and $I_1=l_x^2+l_y^2+l_z^2$. The existing isotropic teaching energy is extended to an arbitrary positive diagonal deformation:

$$U=V_0[\mu(J^{-2/3}I_1-3)/2+K(J-1)^2/2].$$

Its stress conjugate to each stretch is

$$P_i=\mu J^{-2/3}(l_i-I_1/(3l_i))+K(J-1)J/l_i.$$

The X stretch is prescribed in 0.8–1.2. Choose Y or Z as the controlled direction, with stretch $h$ in 0.5–1. The remaining transverse stretch $b$ solves $P_{free}=0$. X and the selected transverse faces have **bilateral displacement grips**: they can push or pull. The remaining faces have zero normal traction. There is no unilateral contact, friction, shear or buckling calculation.

With $c=l_xh$ and $S=l_x^2+h^2$, the free-face stress reduces to

$$P_{free}=\mu c^{-2/3}(2b^{1/3}-Sb^{-5/3})/3+Kc(cb-1).$$

Its derivative is positive on the stated domain for $\mu,c,S,b>0$ and $K\ge0$. The fixed bracket is 0.1–4. Bisection uses the inherited criterion $|P_{free}|\le10^{-5}$ Pa. A failed criterion stays visible. This scalar solution does not establish unrestricted three-dimensional stability.

## Resultant force is not pressure

The signed longitudinal end force is $N_x=P_xH_0D_0$, positive in tension. On **one** controlled transverse face, $C=-P_{load}A_0$ is positive in compression. Opposite faces have opposite vector reactions; their magnitudes are not added. Current-area normal traction is $q=C/A_{current}=-P_{load}l_{load}/J$. It is an applied surface load, not fluid, vascular or measured intramuscular pressure.

Switching Y and Z permutes the isotropic stretch/stress solution. The different reference face areas change resultant forces. This geometric difference does not establish muscle anisotropy. The comparison end force at $h=1$ uses the same prescribed X stretch; its signed change follows the energy rather than an inserted compression penalty.

## Predict, solve and challenge the boundary condition

1. Reset. Compare the two unequal transverse stretches and read the free-face residual.
2. Switch Y to Z. Predict equal energy and current-area traction, but a 1.2 ratio in full-face compression resultants from the reference dimensions. Verify those quantities independently.
3. Reset, choose eight bisections and read **FAILED**. Return to 64 and check recovery; an iteration count alone is not acceptance.
4. Set X stretch to 1.2 and controlled stretch to 1. The displayed negative compression resultant requires a grip that can pull. Compression-only contact could not supply it.
5. Export the displayed state. It includes stretches, areas, signs, equations, residuals and the authored, uncalibrated status.

All moduli and dimensions are teaching inputs, not fitted muscle data. $K=0$ retains the original energy's degenerate dilation response. There are no active fibres, perfusion, fluid mass balance, sealed/drained transport or empirical compression penalty.

## What was checked, and what was not

The source audit independently differentiates the energy symbolically and compares 54 scalar states with 70-digit roots. Model tests check equal-lateral recovery, energy differences, signed resultants, volume, permutation, failed residuals and invalid controls. These numerical checks are separate from Lean.

The exact [AreaLoadContracts.lean](sources/contributions/directional-compression-lab/AreaLoadContracts.lean) contains three **unregistered, source-only** identities over an arbitrary type with explicit associative/commutative multiplication assumptions. Candidate compilation and axiom reports are **UNRUN**. They do not instantiate real multiplication, certify this energy or root algorithm, or validate a physical specimen.

{{conditional-source}}
