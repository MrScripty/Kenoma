# Let forces move the elbow {#let-forces-move-the-elbow}

A pose slider answers where a segment is. A forward-dynamics model answers how it accelerates under the forces actually included. Laboratory 4 makes that distinction visible: the same schematic can either move under its actuator and gravity or remain at an explicitly prescribed angle with an external hold moment.

{{demo:elbow}}

## Define the hinge and gravity once

Use q = 0 for a downward-pointing forearm and positive q for flexion toward the right. The earlier lever's horizontal-zero angle is θ = q − π/2. A point at distance L from the hinge has position (L sin q, −L cos q). With a dumbbell mass m_d at L and a combined forearm/hand mass m_f at c, let

$$C=g(m_dL+m_fc),\qquad I=I_b+m_dL^2+m_fc^2.$$

The point-mass terms are explicit approximations; I_b is an authored residual inertia. Gravitational potential is −C cos q, so the gravity moment is −C sin q. At horizontal, using 5 kg, 0.35 m, 1.5 kg, 0.15 m and g = 9.81 m/s² gives −19.37475 N m. The fixture's inertia is 0.68125 kg m². These calculations include gravity once: there is no second gravity contribution hidden in a bias force.

Our equation is

$$I\ddot q=\tau_A+\tau_P-C\sin q-b\dot q.$$

It contains active muscle moment, passive muscle moment, gravity, and viscous hinge damping. It contains no tracking motor in forward mode and no tissue-contact force. The supported 0–135° interval is a chosen teaching domain, not a statement about a person's range of motion. If the next step leaves that interval, playback stops at the last admissible state; it does not invent a hard-stop collision or clamp velocity to zero.

## A changing path produces a changing moment arm

Put the synthetic origin at (0,o) and insertion at (s sin q, −s cos q). The straight path has length

$$l(q)=\sqrt{o^2+s^2+2os\cos q},\qquad r(q)=-\frac{dl}{dq}=\frac{os\sin q}{l(q)}.$$

The path transmits tension toward its origin. Taking the cross product of insertion position and that force gives the same signed moment rF. For positive flexion, shortening corresponds to dl/dt = −r q̇. Active power delivered to the hinge is τ_A q̇ = −F_A l̇. The numeric tests compare the analytic derivative with centered finite differences, compare it with the independent force cross product, and check this power relation over the supported interior angles. The geometry is a straight synthetic path; wrapping, attachment regions and forearm rotation are absent.

{{proof:virtual-power}}

This exact-integer proof checks the multiplication and sign contract once the derivative and rate relations are supplied. It does not prove the trigonometric derivative or its JavaScript implementation. The corresponding real product identity below retains those supplied geometric assumptions. The separate geometric checks remain necessary.

{{proof:virtual-real-power}}

## Excitation, activation, and force are different states

The control u is excitation in [0,1]. Activation a follows a first-order filter. With a constant input during one step,

$$\dot a=(u-a)/\tau,\qquad a(t+h)=u+(a(t)-u)e^{-h/\tau}.$$

The implementation uses τ = 0.05 s while excitation is at least the current activation, and 0.15 s otherwise. Both are illustrative choices. Release sets u to zero while retaining a, q and q̇. Force therefore decays rather than disappearing instantaneously. Changing excitation preserves the trajectory; changing the load, mode, initial angle or timestep starts a fresh experiment.

The exported trace has one row per step. A same-time excitation change refreshes the current row's input and instantaneous derived outputs, so an immediate download matches the display. Earlier rows remain intact; time, state and accumulated work do not advance. The current row's excitation applies to the next step. Intermediate input edits with zero elapsed time are not separate events.

The exact real-arithmetic update is a convex mixture of a and u with weight e^(−h/τ). The following checked contract concerns integer-weighted mixture numerators only. Neither the exponential implementation nor the physiological validity of those time constants is formally established.

{{proof:activation-bound}}

For this authored force law, define fiber length l_f = l − l_T with a rigid tendon segment of length l_T, normalized fiber length λ = l_f/l_opt, and extension δ = max(0,l_f − l_opt):

$$F_A=F_0a\exp\left[-\left(\frac{\lambda-1}{w}\right)^2\right],\quad F_P=k_P\delta,\quad \tau_A=rF_A,\quad\tau_P=rF_P.$$

The bell curve, tension-only passive law, and their parameters are teaching choices. Force–velocity dependence and pennation are deliberately omitted. This is not an implementation of Millard's calibrated muscle curves or a prediction of human shortening speed. The rigid tendon removes fiber/tendon redistribution and tendon elastic energy. The original actuator comparison explains why compliant and rigid-tendon formulations answer different questions. [Millard et al.](#source-muscle)

| Parameter | Current value | Identification context |
|:--|:--|:--|
| Upper origin height o; forearm insertion distance s | 0.22 m; 0.06 m | Synthetic straight-path geometry |
| Tendon length l_T; optimal fiber length l_opt | 0.06 m; 0.20 m | Authored rigid-tendon/zero-pennation choices |
| Active force scale F₀; normalized width w | 1,200 N; 0.6 | Authored capacity and bell width; no human calibration |
| Passive stiffness k_P | 1,200 N/m | Authored fiber spring, not tissue modulus |
| Damping b; residual inertia I_b | 1.2 N m s/rad; 0.035 kg m² | Authored hinge parameters |
| Rise/fall times | 0.05 s / 0.15 s | Illustrative activation filter |

The red muscle belly is a one-way drawing following path length. Its transverse radius scales as sqrt(l_ref/l_f), an intuition for transverse expansion, not a spatial tissue solution. It adds no second active force, inertia, elastic energy, or contact response. The line actuator is the sole mechanical owner of active force.

## Lift, release, or prescribe a hold

**Try the pulse.** Click “Pulse current state / release.” It keeps the selected load, angle, time step, excitation and mode, continues the current activation and velocity, and releases excitation at the first step boundary at or after 0.30 additional simulated seconds. Use “Reset defaults” first to reproduce the default u = 0.6 forward experiment. Step, Play and Pulse start live 3D automatically; if WebGL fails, a prominent numerical-only notice identifies the static reference diagram. Watch initial gravity-driven lowering before activation builds, subsequent flexion, and continued motion during activation decay. A falling angle is not proof that the muscle is inactive; inspect activation and fiber velocity separately. Pause, single-step, and download the trace to inspect q, a, moments and work.

**Try an unassisted load change.** Increase the dumbbell mass and replay with the same excitation. The model may lower or leave its domain. No hidden motor raises a weak actuator to the requested pose. Reset clears state, camera, and stale input validation.

**Try the prescribed hold.** Select “Prescribed static hold,” vary q and excitation, then step activation. The bones stay fixed because the mode prescribes them. The displayed external hold moment is −(τ_A + τ_P + τ_g). It is an explicit support, not muscle-generated motion. Since q̇ = 0, the support and muscle deliver zero skeletal mechanical power in this fixture, while real muscle metabolism is outside the modeled system. Switching modes resets the experiment rather than injecting an unexplained constraint impulse.

## Mechanical work gives an independent diagnostic

The mechanical energy includes hinge kinetic energy, gravitational potential, and the passive fiber spring:

$$E=\tfrac12I\dot q^2-C\cos q+\tfrac12k_P\delta^2,\qquad
W_A=\int\tau_A\dot q\,dt,\qquad D=\int b\dot q^2\,dt.$$

For this continuous model, E − E₀ − W_A + D = 0. Activation is an externally driven state; its chemical energy is not part of E. Negative active work during active lengthening can occur and is retained with its sign. Gravity is already in E and is not added as external work a second time.

The implementation advances q, q̇, W_A and D using classical RK4 with the exact activation state evaluated at each stage. The passive-force kink can affect observed convergence; no blanket fourth-order result is claimed for every trajectory. An original 0.60 s pulse/release experiment produces the table below from the same pure module used by the browser. The residual is a numerical balance diagnostic, not biological validation.

{{elbow-experiment}}

The smallest-step trajectory supplies a numerical comparison, not a measured reference. Tests also check static gravitational moment, inertia, activation transients, path derivatives, signed power, replay, and the explicit stop/hold behaviors. Actual tendon compliance, co-contraction and coupled tissue forces belong to later stages.
