# Fix total force or applied current-area pressure {#full-face-force-pressure}

The preceding lesson prescribed a transverse displacement. Here the loading condition determines that displacement: choose a fixed one-face compressive force $C$ in N, or a fixed current-area applied normal traction $q$ in Pa. [Open the full-face load laboratory](labs/full-face-load-pressure/index.html). The energy, material bounds and inner free-face criterion remain unchanged.

{{full-face-figure}}

## Two equations determine two transverse stretches

Fix the X stretch. The free stretch $b$ solves $P_{free}=0$ with the inherited 64-step inner solve and $10^{-5}$ Pa criterion. The selected stretch $h$ in 0.5–1 solves either $C=C_{target}$ or $q=q_{target}$. The outer solve uses 8, 32 or 64 bisections; its criteria are $10^{-8}$ N for force and $10^{-5}$ Pa for applied traction. **Both residuals must pass.**

The force and area definitions are

$$C=-P_{load}A_0,\quad A_{current}=A_0l_xb,\quad q=C/A_{current}=-\sigma_{load}.$$

The signed X end resultant is $N_x=P_xH_0D_0$. Cauchy stress is $\sigma_i=P_il_i/J$, positive in tension. The interface traction uses the opposite, compression-positive sign. The displayed $C/A_0$ is reference-area compression; it differs from current-area $q$.

The bracket update uses residual signs without assuming that force increases with compression throughout the domain. A target not bracketed by the endpoint values is refused, retaining the previous valid state. The two endpoint values do not prove a global attainable range, root uniqueness or stability.

## Change a specimen's breadth, not a contact patch

The breadth factor 0.5–2 changes the reference dimension along the **free** transverse axis. Every specimen is still loaded over a full face. This changes reference material volume, loading area and end area. It does not describe changing a localized contact footprint on one unchanged specimen.

At fixed current-area traction, the homogeneous stretches and stresses are independent of reference breadth. Doubling breadth doubles force, reference volume and stored energy because the specimen contains twice the material. At fixed total force, the area-dependent traction and solved deformation change. This is not extra physiological strength from bulging, fibre recruitment or PCSA.

## Predict before changing the loading mode

1. Reset in fixed-force mode. Export the actual default and note $C$, $q$, $h$, $b$, reference volume and both residuals.
2. Double reference breadth while keeping total force fixed. Force remains at its target, but the solved shape and current-area traction change.
3. Reset, choose fixed-pressure mode and compare breadth 1 with breadth 2. Stretches and stresses stay unchanged while force, energy and material amount double.
4. Choose eight outer bisections and read the actual failed criterion. Return to 64 to recover.
5. In fixed-force mode request 100 N when that target lies outside the displayed endpoint bracket. The lab refuses it and preserves the prior valid state; it does not extrapolate a deformation or declare equilibrium.

## Applied pressure is a boundary condition

Fixed current pressure is a follower surface traction. The implementation solves its force-balance equation directly. Adding $qV$ to the energy would load the intended free faces too and describe a different problem. X and the controlled direction still have bilateral grips; nonnegative compression targets do not turn this into unilateral contact or a detachment model.

This is an instantaneous passive elastic state. It has no active fibres, time history, viscosity, transport, fluid pressure, perfusion, localized footprint, anatomy or calibrated tissue response. Numerical stationarity in this reduced ansatz does not establish biological agreement.

The independent audit differentiates the energy and checks 618 admissible inverse states with a 70-digit two-variable solve; 30 generated target cases outside the declared controls are excluded and listed. These checks preserve every existing residual criterion. The preceding three conditional Std product identities are retained as source-only; this lesson adds no Lean declaration or proof attempt.
