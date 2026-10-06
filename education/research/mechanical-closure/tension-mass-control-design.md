# Target tension and lifted mass: bounded follow-on design

2026-10-06. **Design only; implementation waits for independent review of frozen benchmark `0e89c60d03d3d6137e1ece686ecf942b83d05645`, tree `1fe0842aaebbdd874ca25bd48bc95596f6587be9`.** No controller/continuum code, gain tuning, source-law change or new dynamics result is introduced. The [reproduced source protocol](millard-reference-benchmark-protocol.md), [results](millard-reference-benchmark-results.md) and [reference decision](constitutive-reference-decision.md) remain unchanged.

## First fixture and the two controls

Use one mass lifted vertically by the existing zero-pennation musculotendon actuator with a fixed origin above it. This separates tension and external inertia/gravity without claiming anatomical geometry. User inputs are **target tendon tension Fcmd in N** and **lifted mass m in kg**. The target is a command; measured tension Fmeas is initially the noiseless simulated output FT, explicitly labeled as such. Mass is constant during each run. Changing the mass control starts a new run with a disclosed initialization; changing m inside a moving run would require an attachment/momentum/energy protocol that is outside this design.

Let y be upward displacement from the starting position and w=dy/dt. Keep the source F0=100 N, lopt=.1 m, lslack=.2 m, vmax=10 optimal lengths/s, beta=.1, activation times .010/.040 s and amin=.01. These are the frozen benchmark's educational scales/source defaults, not fitted biceps properties. Use declared educational g=9.80665 m/s², no added external damping, pulley ratio, floor/contact, or hidden support force.

\[
l_{MT}(y)=L_0-y,\qquad l_T=L_0-y-l_f,\qquad
q=l_f/l_{opt},\quad s=l_T/l_{slack},\quad
v=\dot l_f/(v_{max}l_{opt}),
\]
\[
F_T=F_0 f_T(s),\qquad
F_0[a f_L(q)f_V(v)+f_P(q)+\beta v]=F_T,
\]
\[
\dot y=w,\qquad m\dot w=F_T-mg,\qquad
\dot l_f=v_{max}l_{opt}v.
\]

Activation follows the pinned source derivative, driven by excitation u, with its declared floor. Geometry determines tendon stretch and actual tension; force balance determines fiber velocity. Neither FT=Fcmd nor a=u is imposed. Fixed origin and positive upward y give positive load power FT*w; the musculotendon endpoint power is −FT*dlMT/dt=FT*w. This sign check must precede any visualization.

The source has massless fiber/tendon force equilibrium; only the external mass adds inertia here. Retain compliant tendon rather than directly applying Fcmd to the mass. General pennation, fiber lower-bound unilateral dynamics and slack/buckling events remain unqualified by the frozen benchmark. A follow-on run that reaches an unqualified event must stop at the last accepted state, identify the event and preserve its receipt. It must not invent support, reset velocity or advance an invalid root/state. Full release may encounter such an event; a bounded failure is an honest outcome.

## Prospective feedback and achievable limits

The smallest useful force servo is a **saturated PI controller with conditional integration**, because a proportional controller generally retains force error under changing fiber length. This is an authored educational controller, not a physiological neural-control claim. No numerical gains are selected here:

\[
e=(F_{cmd}-F_{meas})/F_0,\qquad
u_{raw}=u_b+k_p e+I,\qquad u=\operatorname{clip}(u_{raw},a_{min},1).
\]

Use dI/dt=ki*e except when u_raw>=1 and e>0, or u_raw<=amin and e<0; there set dI/dt=0. I, ub and kp are dimensionless excitation quantities; ki has units s−1. Initial I=0 and ub equals the declared preload activation. This explicitly prevents integrating further into saturation without pretending an unattainable target was reached. Measurement is ideal/noiseless with zero delay in the first fixture; sensor dynamics, controller sampling or delay would require additional declared states and checks.

Before implementation, select and preregister one gain pair and the controller's integration/event convention after the benchmark review. Evaluate the complete coupled linearization and finite perturbations at the declared operating states. At stationary u=a or controller saturation boundaries, assess the appropriate one-sided activation/anti-windup modes rather than assume a single smooth Jacobian. Preserve oscillation, instability, tracking error and saturation; do not change the constitutive branch to stabilize a controller. A feedback-stabilized response would be controller-specific evidence, not a constitutive repair. If no defensible gain choice is yet qualified, retain the design status rather than imply a working servo.

At zero fiber velocity the conditional stall interval is

\[
F_{stall}(q,a)=F_0[a f_L(q)+f_P(q)],\quad a\in[a_{min},1].
\]

Display its bounds as **state-dependent zero-velocity capacity**, not a universal force cap. Actual dynamic tension also depends on activation history, force–velocity response, passive stretch and tendon storage. F0=100 N does not bound every eccentric/passive force. Keep the original curve extrapolations and slopes; do not clip measured FT to Fcmd or F0. Tendon force cannot be made negative by a negative target; reject a negative command and retain the last valid command.

If actual FT<mg, acceleration is downward; a mass already moving upward may continue rising while slowing. If FT=mg, acceleration is zero, so existing velocity persists. If FT>mg, acceleration is upward, including when this initially brakes downward motion. A command Fcmd<=mg cannot initiate an upward acceleration from rest **if that tension is actually attained**. A command Fcmd>mg still does not guarantee lift when unavailable or delayed. Record actual tension, weight, saturation, error and motion separately. No compensating force or mass rescaling is allowed.

## Initialization and bounded protocols

For the primary mref=.5 kg run, construct a suspended rest state with q0=1, w0=0, a0=mref*g/F0=.04903325, s0=fT-inverse(mref*g/F0), and L0=lopt+lslack*s0. Independently verify fiber/tendon and external mass equilibrium. This differs explicitly from the frozen .05-activation case; it is a prospective fixture initialization, not a change to that receipt.

For mass-only comparisons (.25/.5/1 kg), reset to **the same** initial y,w,a,lf,L0 and tendon preload as that baseline. Other masses then start with a known imbalance, not a falsely labeled equilibrium. Do not re-fit activation or geometry when reporting the mass-only effect. A separately labeled equilibrated initialization for another mass is possible only if its own static balance/branch is verified; distinguish it from the matched-state comparison.

Durations below define first finite observation windows, not demonstrated response times. Fcmd is the scripted target; achieved tracking and motion are measured outcomes.

| Case | Command/load protocol | Expected implication and recorded outcome |
| --- | --- | --- |
| Baseline rest | m=.5 kg, target mg, 0–.05 s | With consistent initialization and zero error, remain at rest within residual/refinement budgets. |
| Step/lift | After baseline, target 1.2*mg for .05 s | Tension rises through feedback/activation/tendon dynamics. Upward acceleration follows only when actual FT>mg; measure displacement and delay. |
| Hold a force command | Set target mg for the next .05 s after the lift pulse | Even perfect force tracking does not stop upward velocity. Report continued travel, overshoot and force error. Do not label this a height hold. |
| Brake toward rest | From upward motion, target .8*mg until the first measured w=0 crossing or a .10 s timeout; then target mg | Below-weight actual tension can brake ascent. Returning the command at a velocity crossing does not guarantee settled tension or a lasting rest hold; retain subsequent drift and reversal. No velocity reset. |
| Lower | Separate run from baseline rest: target .8*mg for .05 s, then 1.2*mg to the first w=0 crossing or .10 s timeout; then mg | Below-weight tension initiates descent; above-weight tension can brake it. Do not prescribe lowering velocity independently. Record signed velocity and missed stopping conditions. |
| Release drive | Separate run, or after a documented lifted state: bypass the force servo and set u=amin for .10 s; freeze I during this mode | Activation decays over time; stored tendon/passive force persists. This is release of drive, not tendon detachment or instantaneous zero tension. Keep mass and mechanics connected. Log mode/I handling; restart of feedback requires its own initialization convention. |
| Insufficient requested force | Baseline m=.5 kg, target .6*mg for .05 s | Once actual force drops below weight, the load accelerates down. If it was moving up, initially it slows. Failure to lift is a valid result even if target tracking succeeds. |
| Unavailable target | Baseline m=.5 kg, target 1.2*Fstall,max(q0) for .05 s | Target exceeds initial zero-velocity capacity. Report saturation/error and subsequent actual motion; this does not assert that every dynamic instant is force-limited by that static value. |
| Mass-only test | Same initial material/kinematic state, constant 5 N target, independent .25/.5/1 kg runs for .05 s | Initial force is mref*g for all runs. Independent initial acceleration oracle is (mref*g−m*g)/m. Compare actual subsequent tracking/acceleration, not command-based animation. |

For a true rest hold both |w| and |FT−mg| must meet preregistered budgets for an observation window; a constant target alone is insufficient. User-selected height/speed tracking would add an outer motion controller and a third task specification, outside the two-control fixture. Scripted command stages above do not silently add such feedback.

Retain the descending fixture q0=1.10 as a separate comparison. Use the same source curves and physically consistent tendon preload/external weight or support declaration. Compare fixed activation with the proposed closed loop, and preserve the frozen force-loaded witness. The earlier 1.96334/s growth belongs to its massless fixed-force boundary condition; it is not the expected eigenvalue of the new inertial/feedback system. Positive or negative coupled modes require their actual state matrix and timestep evidence. Saturation can leave an unstable branch uncontrolled; no overlap or stiffness adjustment may hide that.

## Work/power ledger and validation

Define passive storage Ef=F0*lopt*integral(fP dq), ET=F0*lslack*integral(fT ds), kinetic energy K=.5*m*w² and gravitational energy Vg=mg*y. Source damping dissipation is D=F0*beta*v*dl_f/dt=F0*beta*vmax*lopt*v²>=0. Active mechanical input is Pact=−F0*a*fL*fV*dl_f/dt; it can be negative during active lengthening. With fixed origin and no external support/contact,

\[
\frac{d}{dt}(K+V_g+E_f+E_T)=P_{act}-D.
\]

Derivation: **dEf/dt+dET/dt=FT*dlMT/dt+Pact−D**, while **d(K+Vg)/dt=−FT*dlMT/dt**. These sum to the ledger above. Use these separate identities as the sign oracle. Controller error/integral state is informational, not an extra mechanical energy source. This remains actuator mechanical work accounting, not ATP, heat or physiological efficiency. Any future support, stop, brake, pulley or changing load must add its work/impulse explicitly.

Before implementation preregister dimensional gates for force residual, mass equation, tracking, motion, event timing and energy. Retain the frozen source reproduction gates unchanged. Proposed new engineering starting budgets are mass-equation residual <=1e−7 N; independently integrated ledger error <=1e−5 J; and successive timestep-pair differences <=1e−6 m in y, <=1e−5 m/s in w, <=2e−6 in a/q and <=1e−4 N in FT at matched times. These are prospective, not results or biological thresholds. A tracking diagnostic |FT−Fcmd|<=.01*mg over the specified observation window is separate from numerical acceptance. Report transient errors and saturation even when it passes; misses do not justify changing physical or numerical gates. A force-scale-only tolerance of .01*F0 would exceed the .2*mg command margin at m=.5 kg and therefore cannot qualify lift or hold here. Motion classification always uses actual FT−mg and w.

Verify (1) source kernels/frozen receipts; (2) static initialization; (3) independent mass acceleration and ideal prescribed-force kinematics as **separate analytic oracles**, not a shortcut replacing the actuator, plus the independently integrated momentum identity m*[w(tf)−w(t0)]=integral(FT−mg)dt; (4) passive tendon/fiber storage signs and damping; (5) coupled ODE comparison with independent integration and step-halving, split at command/mode changes; (6) event-time refinement and no invalid state/time advance; (7) full coupled one-sided linearizations/finite perturbations, including the descending branch; (8) command/mass independence and saturation/release behavior. Preserve unsuccessful holds/lifts and both coarse/adaptive work receipts. Numeric controller gains and code remain deferred until review returns.

## Visualization that matches the equations

The smallest meaningful future view is a **vertical fixture with a mass block, fiber segment and compliant tendon spring**, accompanied by synchronized plots of target/actual tension and weight; excitation/activation/saturation; height/velocity; and work/energy residual. Move the block from integrated y, draw tendon extension from s and fiber length from q. Arrows use actual FT and mg; motion direction uses w, not the sign of the force command. Label all lengths as a schematic scalar actuator, not tissue geometry. Show the active FL operating point and descending branch, plus event/rejection/status markers.

Use two controls: target tension in N and mass in kg, with mass changes explicitly restarting the run. Show a history cursor and distinct force-hold/rest-hold status. Target motion cannot animate the mass. Until the controller and load equations are implemented and verified, this is a design specification only; do not fabricate trajectories, a working widget or an anatomical arm/skin render.

## Elbow extension and reference-lane handoff

A one-DOF elbow needs more than the two controls. With an independent signed angle theta in radians, fixed shoulder/forearm configuration and constant total inertia J in kg*m², work consistency requires

\[
r_m(\theta)=-dL_{MT}/d\theta,\quad
J\ddot\theta=r_m(\theta)F_T-\partial V_g/\partial\theta,
\quad -F_T\dot L_{MT}=r_m F_T\dot\theta.
\]

J includes forearm/hand inertia and the attached mass contribution; Vg includes their actual heights. For a simple hinge, absolute musculotendon length at a reference angle plus a consistent moment-arm function, hinge axis/angle convention, mass location, segment centers of mass/inertias and fixed neighboring poses are necessary. A constant educational moment arm and LMT(theta)=Lref−r*(theta−theta_ref) can define a declared toy lever; it cannot claim biceps mechanics. Tendon reference/slack lengths and the source fiber optimum must remain consistent with Lref. Muscle force is generally not mg: load and muscle moment arms differ. Configurational geometry and generalized coordinates matter in the original [Sherman, Seth and Delp (2013) abstract/figures](https://pubmed.ncbi.nlm.nih.gov/25905111/). Its PMC full text presented a browser challenge during this check and was not retried; the simple-hinge formulas here are a direct virtual-work derivation, not a claimed full-text extraction.

**Division of work:** this control lane owns only the synthetic fixture, signal/state definitions, boundary work and prospective tests. The separate reference-manifest lane owns paired reference/optimal fascicle information, reference pose/stress state, anatomical paths, slack/prestrain and their provenance/uncertainty. Request a future interface containing LMT(theta_ref), angle/pose conventions, consistent r(theta) or LMT(theta), and the provenance/status of the source lengths; segment/load geometry and inertia also need their own declared source. Do not re-search, populate or infer these anatomical values here. Keep the first vertical fixture independent of that handoff. Parent coordinates review and any later integration/publication.

The source actuator remains the [pinned OpenSim implementation](https://github.com/opensim-org/opensim-core/tree/5bc7d3308eda742690f485ec060bfe725a349fa6) and [Millard et al. original paper](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf); all added load/controller equations are explicitly educational design choices.
