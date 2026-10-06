---
title: Kenoma Mechanics of Moving Bodies
subtitle: An educational research book · Spatial mechanics, evidence and checked claims
lang: en
---


> Editorial review preview: chapter order and prose are regenerated from current source. Proof receipts and numerical evidence are reused unchanged from the archived edition; no fresh kernel, solver or release qualification is claimed. Not for publication.

# Reading a moving body {#reading-a-moving-body}

A body can look convincing while its forces are wrong. A model can balance its forces while its surface looks wrong. Kenoma's educational book asks how to tell the difference, beginning with quantities that we can calculate and inspect before adding anatomy. The intended reader is a programmer, technical artist, or engineering student who wants to connect geometry, mechanics, computation, and evidence.

This edition develops force, torque, energy, anatomical evidence, and a force-driven schematic elbow with activation and a dumbbell load. Seven original resettable 3D laboratories progress through compliant tendon storage, a reduced continuum compression block, a worked tetrahedral FEM/compliant-solver comparison, and a spatial muscle-under-skin/contact strip at identical poses. An eighth, worker-backed experiment jointly solves deforming tissue, distributed tendons and a moving hinge. Its geometry is schematic; the requested anatomical lifting capstone remains under development. A separate evidence viewer contains ten actual atlas meshes, one recorded normalized human trial, and six published model actuator parameter sets. These are three independent evidence streams, not a calibrated person. Three progressive property lessons additionally measure prescribed tetrahedral deformation, compare isochoric volume with cross-section and exterior area, and expose uneven axial strain in a nonuniform bar. The printed edition contains the same explanations, static diagrams, data figures, worked values and original numerical experiments. Clinical or subject-specific prediction is not claimed or required to complete the teaching examples.

The content is an **educational extension**. The existing production plans in `docs/plans/` remain separate. A teaching experiment does not silently add a simulator requirement to the Bevy MVP, change its canonical storage format, or establish a production algorithm choice.

## Reading path: measure first, then add a law {#measurement-first-reading-path}

Read [force](#force-changes-motion), [torque](#a-force-has-an-application-point) and [energy](#energy-reveals-numerical-error) for the rigid-body quantities and system boundary. Then use the [three property lessons](#measure-deformation-before-choosing-a-muscle-law) in order: measure an imposed deformation; construct prescribed volume preservation; calculate uneven strain under a reduced axial law. Their worked examples introduce length, area, volume, stretch, strain, force and stress before a contact or continuum solver is needed.

Next distinguish [anatomical evidence](#anatomy-is-evidence) from teaching assumptions, and follow the actuator into [elbow motion](#let-forces-move-the-elbow). The later [tissue](#tissue-and-rendered-skin), [tendon/compression](#tendon-tissue-coupling) and [continuum](#from-a-spring-to-a-volume-of-tissue) chapters add material energies, boundary conditions and force-driven deformation. Prescribed constant volume is not a solved material response, and the axial bar is not a full muscle. Spatial solver comparisons and the anatomical research apparatus come after those distinctions; their unfinished scope remains explicit.

## Three different kinds of evidence

A **physical assumption** describes the model: a constant force, a perfectly rigid lever, or an ideal spring. A **numerical check** compares the implemented arithmetic with a reference or studies its error. A **formal proof** establishes a precisely stated mathematical claim within its declared domain. Each can be useful; none automatically supplies the other two.

The 29 proof cards in this research edition are generated after checking `Mechanics.lean`, `AnatomicalTransfer.lean`, `CoupledMechanics.lean`, `AnatomicalArm.lean` and `ContinuumProperties.lean` with Lean 4.19.0. The original 25 declarations use integer domains and bundled Std; the four new kinematic declarations use real matrices and the positive real square-root construction with pinned mathlib v4.19.0. Each card reports its exact theorem, assumptions, source hash, implementation link and transitive axioms. A real-number identity does not establish floating-point equivalence, force equilibrium, anatomical validity or biological correctness. This distinction stays visible beside each claim.

The new coupled fixture adds a deforming quadratic-tetrahedron block, distributed tensile branches and an implicitly moving hinge whose tissue torque comes from those branches. It is an intermediate engineering experiment. The actual atlas arm, connected attachment patches and interior-axis diagnostics are available separately for review; shared anatomical tendons/aponeuroses and tissue contact are not yet accepted or complete. The earlier schematic strip retains its declared one-way coupling and is no longer presented as completion of the requested anatomical capstone.

## Coordinates and units

The original seven laboratories use a right-handed frame: x points right, y points up, and z points out of the page. Laboratories 1–5 solve planar motion or homogeneous block deformation and render them in a 3D scene. Laboratories 6–7 add genuine spatial degrees of freedom; each declares its constitutive and coupling limits. The coupled fixture instead uses +Z downward, so its gravitational potential is −mgz. The separate atlas assembly uses +X anatomical left, +Y posterior and +Z superior. Each viewer identifies its own frame. The scene can be viewed from the front or obliquely; changing the camera changes neither state nor results. A 3D rendering does not turn planar equations into a spatial biomechanical simulation.

Store physics in SI units and convert only at input and output. The International System of Units names the metre, kilogram, and second; force has unit newton, energy joule, and torque newton metre. Torque and energy share dimensions but represent different quantities. We write torque in N m to preserve that distinction. [BIPM, SI Brochure, §2.3.4](#source-bipm)

| Quantity | Symbol | Unit | Meaning in the laboratories |
|:--|:--|:--|:--|
| Position | x | m | A coordinate in a specified frame |
| Time | t | s | Simulated time, distinct from wall-clock playback |
| Mass | m | kg | Inertial mass, strictly positive in controls |
| Force | F | N | A vector acting on a specified body |
| Torque | τ | N m | A moment about a specified origin and axis |
| Energy | E | J | Scalar accounting for a defined system |
| Spring stiffness | k | N/m | Force per extension in the ideal linear spring |

## How to use a laboratory

Read the model label and the worked example first. Change one control, predict a result, and inspect the numerical output before interpreting the image. Step through time when needed; use Reset to return all physics parameters and the camera to defaults. The laboratories start paused and stop at a bounded step count. Laboratories 1–5 generally restart after parameter edits; excitation edits in the articulated lessons preserve the current activation and motion. Laboratory 7 retains its current hinge state and begins a new trace segment after parameter edits, with explicit pose/hold handling described [beside its controls](#read-the-controls-as-experiments). The three property lessons instead update a static imposed geometry or axial calculation without integrating time. The coupled fixture also preserves its tissue coordinates, angle, velocity, activation and time when effort or dumbbell mass changes. Its mass control records the external energy added or removed with the mass; it does not restart the trajectory.

Every scene has a text description and static illustration. If WebGL is unavailable, the controls and numerical results still work. All seven mechanics laboratories use original procedural **schematic teaching geometry**: their cylinders, spheres, blocks, grids and arrows are separate from anatomical measurements. The evidence viewer instead shows actual licensed static atlas surfaces, with their source labels, units and limitations. Neither the atlas nor the human-study summaries calibrates the schematic actuator.

## A useful question to carry forward

Imagine a forearm holding a dumbbell. Ask: what system did we isolate, what forces act on it, where do those forces act, and what energy enters or leaves it? These questions remain useful whether the next model is a rigid-body joint, a finite-element tissue mesh, or an animation rig. A more detailed surface cannot rescue an unspecified system boundary.

The property lessons use the same SI convention with prescribed positive stretches or an explicitly reduced small-strain axial law. They update a measured pose immediately and do not integrate time. Independent geometric measurements and midpoint-integration error remain visible; their exact kinematic claims do not prove a constitutive law or qualify the anatomical tissue envelope.

# Force changes motion {#force-changes-motion}

A force is not a displacement instruction. For constant mass in an inertial frame, the resultant external force determines acceleration. Doubling force doubles acceleration; doubling mass halves it. Newton's second law and the separation of action-reaction pairs are presented in Dourmashkin's original course notes, §§7.3-7.4. [Newton's laws](#source-force)

## Isolate the body before adding arrows

Consider a small object translated horizontally by an actuator. The schematic laboratory includes one constant horizontal net force. If we imagined gravity and a support, their vertical balance would be an additional assumption; this example simply solves the horizontal component. Do not mistake its missing contact solver for evidence that a support is physically correct.

For net force $F_x$, mass $m>0$, initial position $x_0=0$, and initial velocity $v_0=0$:

$$
 a_x=F_x/m,\qquad v_x(t)=a_x t,\qquad x(t)=\tfrac12 a_x t^2.
$$

**Text equation:** acceleration equals force divided by mass. Velocity equals acceleration times elapsed time. Position equals half acceleration times elapsed time squared, with both initial conditions zero.

This is an analytic solution, so the force laboratory does not accumulate time-integration error. JavaScript still evaluates floating-point arithmetic. We compare selected outputs with exact worked values using numerical tolerances; no theorem in this edition proves the JavaScript implementation.


### Laboratory 1 · Constant force

![A position marker moves along x. Position scale is fixed over the 0–2 s trajectory for the selected mass and force; grid spacing is reported below. Yellow force and violet velocity arrows use separate scales. Values retain SI units.](assets/force.svg)

Reference at t = 1 s: m = 2 kg, F = 4 N, x = 1 m, v = 2 m/s. The interactive starts at t = 0 s. Original schematic geometry.

**Model:** Analytic planar motion; constant net force; no contact or anatomy.

[Open this laboratory in the web edition](index.html#lab-force).


## Worked example

Set mass to 2 kg and force to 4 N. The acceleration is 2 m/s². At 1 s the position is 1 m and velocity 2 m/s. At 2 s the position is 4 m and velocity 4 m/s. A negative force produces negative position and velocity; the object accelerates along the negative x direction.

**Try:** keep force at 4 N, reset, and increase mass from 2 to 4 kg. At the same simulated time the position is half as large. Then set force to zero: position and velocity stay zero because the initial velocity is zero. A zero force would preserve a nonzero initial velocity in a different experiment.

## Equal and opposite forces belong to different bodies

If a tendon pulls a bone, the bone pulls back on the tendon. Those two forces cancel in a combined bone-plus-tendon system. They do not cancel on the isolated bone: only one member of that pair acts on it. This is why a diagram with every arrow drawn on a single object can be misleading.

For one scalar component, a pair $f$ and $-f$ sums to zero. That identity is enough to check bookkeeping once we have assumed an action-reaction pair. It does not prove that an actual biological interface follows our chosen constitutive law.


**Checked claim force-pair:** An equal and opposite scalar force pair cancels.

**Assumptions:** Exact integer forces in a common positive unit scale; the force pair is assumed.

```lean
theorem force_pair_cancels (f : Int) : f + (-f) = 0
```

**Limits:** Does not prove Newton's third law from biology or establish a system boundary.

Declaration: `Kenoma.force_pair_cancels`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


## Work offers a second calculation

A constant horizontal force does work $W=F_x\Delta x$. Starting from rest, the kinetic energy is $K=\tfrac12 m v_x^2$. Substituting the analytic solution gives $W=K$ in this ideal isolated horizontal model. For 4 N over 4 m, both are 16 J.

A negative force over a negative displacement also gives positive work. Force direction alone does not determine work's sign; the force-displacement relation does. The next chapter keeps track of the application point of that force, while the energy chapter studies what happens when we replace analytic solutions with time steps.

## Approximation boundary

This laboratory omits drag, friction, impacts, variable mass, deformation, actuator limits, and all anatomy. Its moving sphere is a marker for position, not a tissue particle whose radius or volume has medical meaning. Positions beyond the viewing window are reported numerically; the physical trajectory is not clamped to fit the image.

# A force has an application point {#a-force-has-an-application-point}

A force that passes through a pivot produces no moment about that pivot. The same force applied farther from the pivot can produce a larger moment. The laboratory introduces the moment of a force about a chosen origin; the definitions and axis convention are verified against Dourmashkin's rotational-dynamics notes, §17.1. [Rotational dynamics](#source-torque)

## A planar cross product

Let $\mathbf r=(r_x,r_y,0)$ point from the pivot to the application point, and $\mathbf F=(F_x,F_y,0)$ be the force on the lever. The component along z is:

$$
 \tau_z=(\mathbf r\times\mathbf F)_z=r_x F_y-r_y F_x.
$$

**Text equation:** torque around z equals x position times y force minus y position times x force. Positive torque is counterclockwise when viewed from positive z toward the origin.

In the schematic example a massless rigid lever of length $L$ supports a point load of mass $m$ at its tip. The angle $\theta$ is measured counterclockwise from the horizontal, not from a clinical elbow coordinate convention. Uniform gravity is $\mathbf F=(0,-mg,0)$, with **illustrative** $g=9.81$ m/s². Therefore:

$$
 \mathbf r=(L\cos\theta,L\sin\theta,0),\qquad \tau_z=-mgL\cos\theta.
$$

This is a posed lever. The slider prescribes its angle; no active muscle, torque controller, angular acceleration, or joint-contact force maintains the pose. A physical static hold would require an opposing moment supplied by some actuator and appropriate support forces.


### Laboratory 2 · Force and lever arm

![A rigid bar extends from a fixed pivot to a load. The yellow arrow points downward. The white projection marks the horizontal distance to the gravity line. This is a posed lever, not an active arm.](assets/torque.svg)

Default: m = 5 kg, L = 0.30 m, θ = 0°. Torque about z is -14.715 N m. Original schematic geometry; no anatomical measurements.

**Model:** Prescribed pose; massless rigid lever; point load; uniform illustrative gravity.

[Open this laboratory in the web edition](index.html#lab-torque).


## Worked values and the moment arm

At $m=5$ kg, $L=0.30$ m, and $\theta=0$°, gravity is 49.05 N downward and torque is -14.715 N m. At 90° the line of gravity passes through the pivot and the moment is zero within floating-point tolerance. At 120° the torque becomes positive because the load lies on the other side of the pivot's vertical line.

The perpendicular moment-arm magnitude is $d=|L\cos\theta|$. It is not generally the lever length. Its magnitude tells us how strongly gravity acts about this pivot, while the cross product retains direction.

**Try:** compare 0°, 60°, and 90°. Predict the torque ratio before moving the slider. At 60° the torque magnitude is half the horizontal value. Move from 89° to 91° and watch the sign change.

The exact worked arithmetic can be represented by 300 mm and -49050 mN. Multiplying those scales gives $10^{-6}$ N m per integer product unit. The following theorem checks the integer cross product; division by one million to obtain SI torque is an explicitly stated interpretation.


**Checked claim torque-example:** 300 mm crossed with -49050 mN gives -14715000 scaled torque units.

**Assumptions:** r=(300,0) mm; F=(0,-49050) mN; product scale 10^-6 N m.

```lean
theorem torque_worked_example : torque 300 0 0 (-49050) = -14715000
```

**Limits:** Only this exact arithmetic example is checked, not trigonometric slider states.

Declaration: `Kenoma.torque_worked_example`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: none; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


## Combining forces

Two forces at the same point contribute torques that add. We can either add their force vectors first or add the two moments. The identity is useful when assembling muscle and external-load contributions around a joint.


**Checked claim torque-linearity:** Planar torque is additive in applied force at a fixed point.

**Assumptions:** Exact integer planar coordinates and forces; shared positive length and force scales.

```lean
theorem torque_linear (rx ry fx fy gx gy : Int) :
    torque rx ry (fx + gx) (fy + gy) =
      torque rx ry fx fy + torque rx ry gx gy
```

**Limits:** No arbitrary real coordinates, JavaScript refinement or rounding bound is established.

Declaration: `Kenoma.torque_linear`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


It is unsafe to add torques computed around different origins without transforming them. If the new origin is at $\mathbf o$ relative to the old one, the position becomes $\mathbf r-\mathbf o$, and:

$$
 (\mathbf r-\mathbf o)\times\mathbf F
 =\mathbf r\times\mathbf F-\mathbf o\times\mathbf F.
$$


**Checked claim torque-origin:** Changing the torque origin subtracts origin cross force.

**Assumptions:** Exact integer planar coordinates and forces in common positive scales.

```lean
theorem torque_origin_shift (rx ry ox oy fx fy : Int) :
    torque (rx - ox) (ry - oy) fx fy =
      torque rx ry fx fy - torque ox oy fx fy
```

**Limits:** This is an algebraic identity, not a claim that torque is independent of origin.

Declaration: `Kenoma.torque_origin_shift`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


## Internal forces and couples

Equal and opposite forces can have zero resultant force and a nonzero resultant torque. Think of two forces acting along different parallel lines: they form a couple. Force cancellation alone is not enough to infer moment cancellation.

For a central pair between positions A and B, let the force at A be $k(\mathbf B-\mathbf A)$ and the force at B its negative. Their summed moment vanishes because both forces act along the joining line. The theorem checks this specifically for planar integer coordinates and integer k.


**Checked claim central-pair:** Equal opposite central forces produce zero summed planar torque.

**Assumptions:** Force at A is k(B-A); force at B is its negative; integer k and positions.

```lean
theorem central_pair_torque (ax ay bx byy k : Int) :
    torque ax ay (k * (bx - ax)) (k * (byy - ay)) +
      torque bx byy (-(k * (bx - ax))) (-(k * (byy - ay))) = 0
```

**Limits:** Noncentral pairs can form a couple. Tissue/contact models are not verified by this theorem.

Declaration: `Kenoma.central_pair_torque`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


This assumption should be inspected before applying it to a tissue model. A model that exchanges angular momentum through distributed stress or explicit bending moments needs the corresponding moment balance, not a point-force argument with missing terms.

## Connecting torque to energy

The point load has gravitational potential $U=mgL\sin\theta$ relative to its horizontal position. Differentiating with respect to angle in **radians** gives $\tau_z=-dU/d\theta$. A finite-difference numerical test checks this relation for the implemented lever. It does not establish a floating-point theorem. This independent calculation is valuable because it can reveal a sign convention or degree/radian conversion error.

# Energy reveals numerical error {#energy-reveals-numerical-error}

Energy accounting can expose a trajectory that looks smooth while gaining energy from its numerical update. The definitions of kinetic energy and work are verified against Dourmashkin's notes, §§13.2-13.6. [Energy and work](#source-energy) The numerical experiment below is original code and analysis in this repository; it is a synthetic oscillator experiment, not new biological data.

## An ideal oscillator with a reference solution

A mass attached to a linear spring has extension x and velocity v. There is no damping, gravity, contact, or active energy input. Its equation and total mechanical energy are:

$$
 m\ddot x=-kx,\qquad E=\tfrac12 mv^2+\tfrac12 kx^2.
$$

**Text equation:** mass times acceleration equals negative stiffness times extension. Energy equals half mass times velocity squared plus half stiffness times extension squared.

The default parameters are $m=1$ kg, $k=40$ N/m, $x_0=0.20$ m, and $v_0=0$ m/s. Initial energy is 0.80 J. The angular frequency is $\omega=\sqrt{k/m}$, and the reference trajectory is $x(t)=x_0\cos(\omega t)$, $v(t)=-\omega x_0\sin(\omega t)$.


### Laboratory 3 · Numerical energy

![A spring connects a wall to a mass marker. Extension is visually exaggerated and fitted to the view. The energy chart shows a solid numerical trace and a dashed initial-energy reference. Read numeric values when the chart rescales.](assets/energy.svg)

Initial state: m = 1 kg, k = 40 N/m, x = 0.20 m, v = 0 m/s, E = 0.80 J. Default symplectic Euler step h = 0.02 s. Original schematic geometry.

**Model:** Ideal undamped linear spring; fixed physics steps; 600-step playback limit.

[Open this laboratory in the web edition](index.html#lab-energy).


## Three ways to take a step

Let h be a positive time step in seconds, and $a_n=-kx_n/m$.

**Explicit Euler** updates both values from the old state:

$$
 x_{n+1}=x_n+h v_n,\qquad v_{n+1}=v_n+h a_n.
$$

**Symplectic Euler** updates velocity before position:

$$
 v_{n+1}=v_n+h a_n,\qquad x_{n+1}=x_n+h v_{n+1}.
$$

**Velocity Verlet** includes the new acceleration:

$$
 x_{n+1}=x_n+h v_n+\tfrac12 h^2 a_n,\qquad
 v_{n+1}=v_n+\tfrac12 h(a_n+a_{n+1}).
$$

The methods are implemented separately from rendering. Playback advances fixed simulation steps and reports their index and elapsed time; it never inserts the browser's frame duration into the physics formula. A parameter change starts a new trajectory. Reset reproduces the same sequence for a given method and step size.

## Why explicit Euler gains energy

Substitute the explicit update into the quadratic energy and expand. The mixed terms cancel, leaving:

$$
 E_{n+1}=\left(1+\frac{k}{m}h^2\right)E_n.
$$

For positive k, m, and h, every nonzero-energy step multiplies energy by a factor greater than one. Making h smaller delays the growth; it does not produce bounded energy over arbitrarily long time with fixed h. This is a paper-and-pencil derivation for the ideal oscillator. No Lean theorem in this edition checks that integrator identity.

For the other two methods, the linear oscillator's usual bounded regime is $h\sqrt{k/m}<2$. Even inside that regime, neither method preserves the exact physical energy at every step. The observed energy oscillates, and phase error accumulates. A stable picture and an accurate time history are different checks.

## Original reproducible experiment

Run each method with the same initial conditions over 12 simulated seconds. Compare h = 0.01, 0.02, and 0.05 s, measuring the maximum absolute relative energy deviation over **all** sampled steps and the final absolute position error against the analytic reference. No wall-clock speed claim is made. The table below is generated by executing `web/mechanics.mjs`, the same pure physics module used by the browser.

| Method | h (s) | Steps | Max relative energy deviation (%) | Final position error (m) |
|:--|--:|--:|--:|--:|
| explicit | 0.01 | 1200 | 1.194e+04 | 1.849 |
| explicit | 0.02 | 600 | 1.368e+06 | 23.11 |
| explicit | 0.05 | 240 | 8.595e+11 | 5848 |
| symplectic | 0.01 | 1200 | 3.266 | 0.004304 |
| symplectic | 0.02 | 600 | 6.752 | 0.01165 |
| symplectic | 0.05 | 240 | 18.78 | 0.0622 |
| verlet | 0.01 | 1200 | 0.09999 | 0.00122 |
| verlet | 0.02 | 600 | 0.4 | 0.005052 |
| verlet | 0.05 | 240 | 2.5 | 0.03887 |


The final position error can be small by phase coincidence; it should not be used alone to select a method. The energy maximum shows explicit Euler's growth even when a snapshot happens to cross the reference. Symplectic Euler has a larger oscillating energy deviation than Verlet for these settings. Both still require refinement studies for any intended application.

**Try:** reset with explicit Euler and h = 0.05 s. Step or play to see the energy increase. Reset with Verlet at the same h. Compare numeric energy with the dashed 0.80 J reference, then halve h and compare again. The plotted vertical range adapts to the computed energy; read its numeric maximum so that rescaling cannot disguise instability.

## A modest formal claim

With a nonnegative exact integer mass, the numerator $m(v_x^2+v_y^2)$ is nonnegative. With positive unit scales and the factor one half, it corresponds to nonnegative kinetic energy. That claim says nothing about conserving energy from one step to the next.


**Checked claim kinetic-sign:** The exact numerator m(vx²+vy²) of twice kinetic energy is nonnegative.

**Assumptions:** Integer mass m ≥ 0; integer velocity coordinates; positive SI scale factors.

```lean
theorem kinetic_numerator_nonnegative (m vx vy : Int) (hm : 0 ≤ m) :
    0 ≤ twiceKinetic m vx vy
```

**Limits:** The factor 1/2 and unit scales are interpreted in prose; no integrator conservation or biological validation.

Declaration: `Kenoma.kinetic_numerator_nonnegative`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


## Approximation boundary

The spring is linear at all extensions, including compression, and has no tensile-only constraint. It is therefore not a tendon model. An active muscle adds energy through a contraction law; a dissipative tissue removes energy; contact may exchange or dissipate energy. Before interpreting their energy residuals, include those terms and define the model's system boundary.

Before adding those material mechanisms, continue to [the three property lessons](#measure-deformation-before-choosing-a-muscle-law). They measure an imposed shape, construct constant-volume kinematics, and calculate nonuniform strain with one declared axial law. This separates geometric observations from the force and energy models that will later produce them.

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


### Property lab 1 · Measure deformation

![Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.](assets/property-deformation.svg)

Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.

[Open the interactive lesson](index.html#lab-property-deformation).


**Try and predict.** Set all three stretches to 1, shear and rotation to 0. The measured $J$ and boundary-volume ratio should both be 1, and Green strain should be zero. Change only translation X to 30 mm: it moves the tetrahedron but changes neither measurement. Next set axial stretch to 1.2: expect $J=1.2$. Restore unit stretches and set shear to 0.25: volume stays the same, but Green strain is nonzero. Rotation alone also keeps volume and strain unchanged; the components of $F$ can still change.

The controls prescribe the vertices. This lab measures $F$, $J$, Green strain and an independent boundary volume; it solves no forces, material energy, contact or equilibrium. A valid positive volume is a geometry check, not evidence of a realistic muscle response.

![Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.](assets/property-deformation.svg)

Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.

[Open the interactive lesson](index.html#lab-property-deformation).



**Checked claim volume-edge-translation:** Adding one real translation to all four vertices leaves the tetrahedral edge matrix unchanged.

**Assumptions:** Four real three-dimensional vertex vectors; the same translation acts on each vertex. A meaningful physical deformation gradient additionally requires a nondegenerate reference tetrahedron.

```lean
theorem edge_translation_invariant (v : Fin 4 → Fin 3 → ℝ) (t : Fin 3 → ℝ) :
    edgeMatrix (fun j i => v j i + t i) = edgeMatrix v
```

**Limits:** No floating-point equivalence, boundary triangulation, inversion detection, equilibrium or biological claim is established.

Declaration: `KenomaProperties.edge_translation_invariant`. Lean 4.19.0; pinned mathlib v4.19.0; commit c44e0c8ee63ca166450922a373c7409c5d26b00b; locked transitive dependencies; transitive axioms: propext, Classical.choice, Quot.sound; source SHA-256: 33945605131f1a0fc3568467cbc1026463867a8fa241fb25e2174c23a229f12e. [Full checked source](proofs/ContinuumProperties.lean); [receipt](property-proof-status.json).



**Checked claim volume-det-compose:** The determinant of a product of real 3 by 3 matrices is the product of their determinants.

**Assumptions:** Real square matrices; this supports F=Ds*inverse(Dm) with separately assumed invertible reference geometry.

```lean
theorem determinant_composition (A B : Matrix (Fin 3) (Fin 3) ℝ) :
    Matrix.det (A * B) = Matrix.det A * Matrix.det B
```

**Limits:** Does not certify JavaScript matrix multiplication/inversion, mesh orientation or boundary measurements.

Declaration: `KenomaProperties.determinant_composition`. Lean 4.19.0; pinned mathlib v4.19.0; commit c44e0c8ee63ca166450922a373c7409c5d26b00b; locked transitive dependencies; transitive axioms: propext, Classical.choice, Quot.sound; source SHA-256: 33945605131f1a0fc3568467cbc1026463867a8fa241fb25e2174c23a229f12e. [Full checked source](proofs/ContinuumProperties.lean); [receipt](property-proof-status.json).


## 2. Exact isochoric kinematics

**Question:** what lateral change would keep a rectangular block's volume exactly fixed while its axial length changes? *Isochoric* means constant volume. Here we impose the answer; no pressure or material stiffness chooses it.

Prescribe $F=\operatorname{diag}(\lambda,b,b)$ with positive dimensionless stretches. Then $J=\lambda b^2$. In the isochoric construction $b=1/\sqrt\lambda$, so $J=1$ in exact real arithmetic. The interactive controls also allow independent stretches, which need not preserve volume. This is a kinematic construction, not a minimization or a muscle contraction law.

For the rectangular reference, $L=\lambda L_0$, $A=b^2A_0$ and $AL=JV_0$. Cross-section area is the area normal to the axial direction, measured from two transverse edges. Exterior area is the sum of all boundary-triangle areas. They have the same units, square metres, but different mechanical meanings. Neither is automatically physiological cross-sectional area (PCSA). The independent boundary-volume measurement remains visible when the isochoric toggle is selected.


### Property lab 2 · Volume and cross-section

![Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.](assets/property-isochoric.svg)

Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.

[Open the interactive lesson](index.html#lab-property-isochoric).


**Try and predict.** At axial stretch $\lambda=0.8$, the 0.08 m reference length becomes 0.064 m. The imposed lateral stretch is $b=1/\sqrt{0.8}\approx1.11803$, so the reference cross-section 0.003 m² grows to 0.00375 m². Their product remains 0.00024 m³. Switch to independent stretches and set $b=1$: the same shortening now gives $J=0.8$. Read cross-section area and exterior area separately; they need not change by the same factor.

This volume-preserving motion is **prescribed kinematics**, not material-driven volume redistribution. The free-side compression example in [Laboratory 5](#tendon-tissue-coupling) later determines lateral stretch from a material law and boundary conditions, rather than imposing this square-root relation. Neither lesson specifies a complete deforming muscle.

![Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.](assets/property-isochoric.svg)

Authored 80 × 60 × 50 mm reference. Gray is reference; blue is prescribed geometry. This lesson imposes kinematics and does not solve force equilibrium.

[Open the interactive lesson](index.html#lab-property-isochoric).



**Checked claim volume-diagonal:** The real axial/lateral diagonal deformation diag(lambda,b,b) has determinant lambda × b × b.

**Assumptions:** Real stretches; physical use additionally requires lambda>0 and b>0. Unit determinant follows whenever the stated product equals one.

```lean
theorem axial_determinant (lambda b : ℝ) :
    Matrix.det (axialMatrix lambda b) = lambda * b * b
```

**Limits:** A kinematic identity; no force equilibrium, finite-bulk incompressibility, material response or biological correctness follows.

Declaration: `KenomaProperties.axial_determinant`. Lean 4.19.0; pinned mathlib v4.19.0; commit c44e0c8ee63ca166450922a373c7409c5d26b00b; locked transitive dependencies; transitive axioms: propext, Classical.choice, Quot.sound; source SHA-256: 33945605131f1a0fc3568467cbc1026463867a8fa241fb25e2174c23a229f12e. [Full checked source](proofs/ContinuumProperties.lean); [receipt](property-proof-status.json).



**Checked claim volume-isochoric-sqrt:** For real lambda>0, b=1/sqrt(lambda) is positive and diag(lambda,b,b) has unit determinant.

**Assumptions:** Positive real axial stretch and the exact real square-root construction.

```lean
theorem isochoric_sqrt_construction (lambda : ℝ) (hlambda : 0 < lambda) :
    0 < 1 / Real.sqrt lambda ∧
    Matrix.det (axialMatrix lambda (1 / Real.sqrt lambda)) = 1
```

**Limits:** Does not prove binary64 sqrt/division or measured browser volume is exact, and does not establish a passive or active equilibrium.

Declaration: `KenomaProperties.isochoric_sqrt_construction`. Lean 4.19.0; pinned mathlib v4.19.0; commit c44e0c8ee63ca166450922a373c7409c5d26b00b; locked transitive dependencies; transitive axioms: propext, Classical.choice, Quot.sound; source SHA-256: 33945605131f1a0fc3568467cbc1026463867a8fa241fb25e2174c23a229f12e. [Full checked source](proofs/ContinuumProperties.lean); [receipt](property-proof-status.json).


## 3. Nonuniform cross-section: a reduced axial oracle

**Question:** can one constant tensile force produce different strain along a bar? Here shape is no longer prescribed at every section. We assume a one-dimensional material law and axial balance, then calculate strain. Positive strain is extension; negative strain is compression. The coordinate $s$ runs along the reference bar; $N/A$ is axial stress in pascals. Larger area or modulus reduces passive strain at the same force.

Take a small-strain bar with length $L$ in metres, positive area $A(s)$ in square metres, constant modulus $E$ in pascals, no distributed axial load, and a tensile-positive resultant $N$ in newtons. Force balance gives $dN/ds=0$. The passive law gives $\epsilon(s)=N/[EA(s)]$, so

$$\Delta L=\int_0^L\epsilon(s)\,ds=N\int_0^L\frac{ds}{EA(s)}.$$

For linear **area** taper $A(s)=A_1[1+(r-1)s/L]$, the exact compliance is $L\ln(r)/[EA_1(r-1)]$, with limit $L/(EA_1)$ at $r=1$. Numerical midpoint integration is compared with that analytic integral. Linear area taper is a separate geometric assumption from a radius taper. The exterior surface influences surface traction and contact; it does not replace $A(s)$ in this axial law.

Add a separately declared uniform active-stress offset $a\sigma_0$, still under this reduced small-strain law: $\epsilon=N/(EA)-a\sigma_0/E$. With both ends fixed, $\int\epsilon ds=0$ determines the constant $N$. Two equal-length segments with $A_2=2A_1$ and $a\sigma_0/E=0.01$ give $N=(4/3)A_1a\sigma_0$, narrow strain $+1/300$ and wide strain $-1/300$. Local extension and compression coexist even though total length is fixed. This offset model has no force–length/velocity dependence, transverse equilibrium, pennation, ECM, fluid or anatomical calibration; it is not a complete active muscle model.


### Property lab 3 · Uneven axial strain

![Small-strain constant-modulus bar; no distributed axial load. Strain by axial position, with blue extension and red compression. Area controls an axial resultant, not a complete muscle law.](assets/property-tapered.svg)

Small-strain constant-modulus bar; no distributed axial load. Strain by axial position, with blue extension and red compression. Area controls an axial resultant, not a complete muscle law.

[Open the interactive lesson](index.html#lab-property-tapered).


**Try and predict.** In passive mode, keep the default geometry and modulus and change force from 0.3 to 0.6 N: every strain and the total extension double. Doubling the modulus instead halves them. In active fixed-end mode, choose two equal-length segments and keep area ratio 2, activation 1 and active stress 1,000 Pa at modulus 100,000 Pa. The narrow section extends by $1/300$ and the wide section compresses by $1/300$, while their total length change is zero. Passive force is disabled in that mode because the fixed-end compatibility determines the reaction; active controls are disabled in passive mode.

This bar solves an axial resultant and axial strain under its stated assumptions. It does not determine lateral stretch, cross-section evolution, transverse stress, contact, three-dimensional fibre aggregation or muscle shape. The area profile is an input; neither zero net extension nor the active-stress offset supplies the missing transverse equilibrium. Refining midpoint cells improves the integral of this same reduced law, not its biological scope.

The illustrative 5% small-strain warning uses the true endpoint extrema of this monotone positive-area law, independent of midpoint display resolution. It is a warning about this approximation, not material validation.

The executable oracle is [the tapered-bar module](web/tapered-bar.mjs). Tests check the logarithmic integral, refinement and the two-segment fixed-end case. Its scope is numerical evidence for this declared reduced law; the kinematic Lean claims above do not prove its mechanics.

Continue with [anatomical evidence](#anatomy-is-evidence) before assigning these quantities to a named muscle. When you reach [tissue and rendered skin](#tissue-and-rendered-skin), reuse the measurements above while adding a material law and boundary forces. Bulk/shear and confinement controls, measured fibre-to-muscle aggregation, force–length/velocity and dissipative load/hold/release lessons remain pending, as recorded in the [coverage chapter](#coverage-and-evidence).

## What the exact claims cover

The freshly checked real-number proof bundle establishes edge translation invariance, determinant composition, the actual diagonal determinant and the positive square-root isochoric construction. The four claims above are compiled from their displayed real definitions against pinned mathlib. The edge and matrix identities do not prove the oriented boundary-triangle oracle, and the isochoric identity does not prove a free-side material equilibrium. Separate numerical and browser tests cover the implemented controls and boundary measurements. Neither class of test validates measured biological parameters or resolves the capstone's local compression and full nodal stationarity failures.

# Anatomy is evidence, not a silhouette {#anatomy-is-evidence}

The previous laboratories isolate mechanics. An arm introduces three descriptions that must agree: rigid skeletal geometry, force-producing musculotendon paths, and deformable tissue. The humerus, radius and ulna are distinct bones. Elbow bending and forearm rotation are distinct motions; the biceps' distal attachment to the radius makes this separation important. Our next laboratory fixes forearm rotation and shoulder posture and replaces the elbow complex with one hinge. Its rods are teaching geometry, not segmented bones.

## Name the structures before assigning properties

The anterior volume includes biceps and the deeper brachialis; brachioradialis contributes a separate lateral path. The triceps heads provide extensor paths, and some muscles span the shoulder as well as the elbow. A single red actuator cannot identify their individual contributions. The chapter's synthetic flexor is deliberately called a **synthetic flexor**, rather than assigning its invented origin and insertion to a named anatomical muscle.

An attachment region, a segmented surface, a tendon guide point, and a fiber direction field are different data. The surface of a muscle does not tell us how its fascicles run or where a numerical routing point should be placed. An anatomical fascial expansion such as the bicipital aponeurosis also needs an attachment/interface model; drawing another cable is insufficient. The audited anatomy contribution supplies anatomical literature and distinctions, but no imported mesh in this edition establishes those features for our schematic.

## Published human numbers with their context

Murray, Buchanan and Delp examined ten human upper-extremity specimens. Measurements included architecture and tendon excursion; optimal fascicle lengths and physiological cross-sectional areas (PCSA) were then estimated. Their Table 2 gives the following study summaries. These are published biological estimates, **not this laboratory's defaults**, and no participant-level raw data are redistributed. [Original study, Table 2 and §3](#source-architecture)

| Reported quantity | Study summary | Interpretation |
|:--|:--|:--|
| Brachioradialis optimal fascicle length | 17.7 cm; SD 3.0 cm | Architecture estimate in the study specimens |
| Brachioradialis PCSA | 1.2 cm²; SD 0.6 cm² | Estimated parallel contractile area |
| Combined triceps PCSA | 14.9 cm²; SD 6.7 cm² | Aggregate reported for combined heads |

Convert 17.7 cm to 0.177 m and 1.2 cm² to 0.00012 m² before calculations. For a uniform architecture idealization, PCSA is volume divided by optimal fiber length. If maximum tendon-directed force is modeled as specific fiber tension times PCSA times cos(pennation), check whether the source already includes that cosine in its area convention. The segmented volume and PCSA do not themselves specify a maximum force: a specific-tension assumption is still needed.

Iivarinen and colleagues measured forearm indentation in nine healthy people, used ultrasound for tissue thickness, and fitted a layered hyperelastic model. Their resting effective moduli were **210 kPa for skin** and **1.9 kPa for adipose tissue**, equivalent to 210,000 Pa and 1,900 Pa. These are inverse-model values under that study's loading and layer assumptions. They are not universal tissue constants or an elbow-contact calibration. Neither value is inserted into the schematic hinge. [Original abstract and DOI](#source-indentation)

The distinction matters: a measured displacement, a parameter fitted from that displacement, and a new model's prediction are three separate objects. Testing the fitted model on its fitting observations is calibration. Testing on a reserved pose or load is a stronger check of generalization.

## A dataset must say what it observes

The audited research identifies several useful routes to actual data. The table records research-stage access, not completed integration into this executable.

| Resource | Observations or content | Boundary and licence evidence |
|:--|:--|:--|
| Visible Human | Cadaver cryosections, CT and MRI | Source images differ from derived segmentations; official public-domain access description |
| BodyParts3D | Reference anatomical geometry and anatomical identifiers | Official current archive CC BY 4.0; preserve exact acquired version and attribution |
| OpenArm 2.0 | Ultrasound-reconstructed biceps/arm volumes over poses and loads | Research audit: eleven participants, CC BY 4.0; registration and predicted-label quality need review |
| OpenArm Multisensor 2.0 | Ultrasound, EMG, force and task information | Research audit: CC BY 4.0; modalities concern different muscles; apply release errata |
| Quesada upper-limb dataset | EMG, kinematics and joint-torque time series | Research audit: CC BY-SA 4.0; torque is not measured individual muscle force |
| Arm26 | Educational OpenSim model with six actuators | Embedded model CC BY 3.0; educational geometry/actuators differ from this one-hinge model |

The following data chapter integrates a specific licensed Multisensor trial after a reviewed passive conversion, preserving normalized values and actual relative timestamps. Ordinary untrusted pickle deserialization is unsuitable; no pickle is bundled or executed here. The acquired atlas, recording and model parameters remain visibly separate from the published study summaries above and from the schematic actuator.

The current MoBL-ARMS package has a noncommercial restriction according to the audited provider page, conflicting with an older catalogue's MIT label. It is excluded. Apache-2.0 on Kenoma code does not relicense any dataset, model, mesh, scan, or paper figure. [Data access and licence sources](#source-data)

## Expertise follows the contribution

Murray, Buchanan and Delp's original architecture experiments are relevant to architecture and moment capacity. Millard, Uchida, Seth and Delp's actuator comparisons are relevant to musculotendon modeling. Wakeling, Ryan and colleagues' continuum work is relevant to force/deformation coupling. Hallock's OpenArm research is relevant to imaging-derived muscle deformation. These are source-based areas of contribution, not endorsements of Kenoma or claims that any author reviewed it.

No audited source supplies a complete, co-registered loaded curl with all bones, fibers, activation histories, skin self-contact and pressure. The book therefore keeps the evidence gap visible while building mechanisms that can later be compared with compatible measurements.

# Inspect real anatomy and recorded evidence {#actual-anatomical-data}

An atlas, a recorded human trial and an actuator model answer different questions. This chapter includes **actual licensed data bytes**, with their source-specific rights, transformations and hashes. None of the three evidence streams is registered to either of the others or to the teaching actuator. Looking more anatomical cannot turn a schematic force law into a validated physiological model.

## Ten static anatomical surfaces

![Two anterior-facing views of a straight right-arm atlas: humerus, radius and ulna alone, then seven selected muscle surfaces with keyed colors.](assets/atlas-print.svg){.evidence-figure}

Ten BodyParts3D 4.0 right-arm surfaces preserve the original atlas pose: humerus, radius, ulna, brachialis, brachioradialis, both biceps heads and three triceps heads. The official 99%-polygon-reduced release supplies 13,852 vertices and 20,218 triangles. It is a constructed static adult-male reference atlas, rather than scanned geometry for the OpenArm participant. Rendering colors are explanatory. Source axes are x toward anatomical left, y posterior and z superior; original OBJ positions are in millimetres. The JSON divides positions by 1,000 and converts face indices to zero-based, with no topology editing, joint fitting or rigging.

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International. Changes: ten-part selection, SI conversion and original rendering; this book's print derivative enlarges labels and reflows the legend without changing geometry. The original OBJ comments retain the historical CC BY-SA 2.1 Japan notices; the package also includes the current official archive's February 2025 CC BY 4.0 grant. [Source and rights record](#source-acquired-data)

The browser viewer centers and rotates the atlas **for display only**. It can show bones or individual named parts, and switch anterior, oblique and posterior views. It does not animate a guessed elbow axis. Polygon reduction and edge diagnostics do not establish a mesh suitable for medical contact calculations. No skin, fat, fascia, cartilage or tendon material field is provided.

## One recorded trial at a held posture

![Three aligned recorded curves over about 86 seconds: normalized brachioradialis thickness, biceps sEMG and wrist-contact force, with different amplitudes and profiles.](assets/recording-print.svg){.evidence-figure}

OpenArm Multisensor 2.0 participant code 2, trial 1b, was recorded with the right elbow held at 90° and the forearm supinated. The retained segment contains 4,403 preprocessed normalized samples over 85.903537 s. Ultrasound measures **brachioradialis thickness**; sEMG measures **biceps brachii electrical activity**; wrist-contact force is a net external signal. They are different quantities and, for ultrasound and sEMG, different muscles. The fixed acquisition posture is not a measured angle trajectory. Hallock et al. (2021), DOI 10.1109/TNSRE.2021.3133813; data CC BY 4.0. Changes: selected trial/segment, relative timestamps, display binning and original plot.

The source's retained `Processed` values are already trial-calibrated. Zero refers to relaxed calibration and one to its calibration contraction: (signal − relaxed mean)/(MVC mean − relaxed mean). The package does not normalize them again or clamp values outside [0,1]. Their amplitude unit is **one**, not metres, volts or newtons. Calibration to those physical units is not established, and sEMG is not labeled activation a or individual-muscle force.

The saved timestamps are irregular. The segment averages 51.243524 saved samples/s despite the protocol's nominal best-effort 1 kHz description. The display uses 172 half-second bins, each [start,end), with sample-weighted arithmetic means and the actual mean sample time; the last bin can be partial. Use original relative timestamps for subsequent analysis. These binned curves do not establish spectral behavior, latency, causality, population uncertainty or a universal force law.

The web edition provides a resettable static atlas viewer and a recorded-bin slider. The figures, source tables and downloads above and below provide the reading alternative.

[SI atlas JSON](data/elbow-v1/data/bodyparts3d_right_arm_m.json), [original recorded samples CSV](data/elbow-v1/data/openarm_s2_1b_normalized_samples.csv), [display bins CSV](data/elbow-v1/data/openarm_s2_1b_0p5s_bins.csv), [trial metadata](data/elbow-v1/data/openarm_s2_1b_metadata.json).

## Six source model actuators, with units

Arm26's six Thelen2003 actuator sets come from the pinned official OpenSim XML. These are **model parameters**, not direct participant measurements or clinical norms. Three parameters are displayed below; [the complete extracted JSON](data/elbow-v1/data/arm26_parameters.json) and [CSV](data/elbow-v1/data/arm26_parameters.csv) also retain pennation angle (rad), activation/deactivation time constants (s), units, source paths and coordinate bounds. There is no brachioradialis actuator in Arm26. Do not replace the schematic actuator with these values while retaining its unrelated geometry and then call the result calibrated.

| Arm26 actuator | Peak isometric parameter (N) | Optimal fiber length (m) | Tendon slack length (m) |
|:--|--:|--:|--:|
| TRIlong — triceps brachii long head | 798.52 | 0.134 | 0.143 |
| TRIlat — triceps brachii lateral head | 624.3 | 0.1138 | 0.098 |
| TRImed — triceps brachii medial head | 624.3 | 0.1138 | 0.0908 |
| BIClong — biceps brachii long head | 624.3 | 0.1157 | 0.2723 |
| BICshort — biceps brachii short head | 435.56 | 0.1321 | 0.1923 |
| BRA — brachialis | 987.26 | 0.0858 | 0.0535 |


OpenSim Development Team (Reinbolt, Seth, Habib and Hamner), adapted from Kate Holzbaur's model; CC BY 3.0. The complete source credit and licence remain in [unchanged model XML](data/elbow-v1/sources/arm26.osim). Changes: explicit numerical extraction into SI-labelled files. Official source revision is `84b487c4e3245359a64381e01f01b9cf4772d457`; XML SHA-256 is `e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9`.

## What the checks establish

The exact 2,058,262-byte received package has SHA-256 `af02aaeb37d626f448a658183f764dc6cf68b979730c413ba31997f26062d169`. Its 992 checks pass again in this repository: source/payload hashes, atlas units and face bounds, six parameter sets against XML, finite strictly ordered recorded times, full bin accounting and independently recomputed means. The passive pickle reader rejects executable globals; no source pickle is bundled or executed. These are data/transformation checks, not biological validation. Archive directory/CRC evidence is preserved; a full BodyParts3D archive hash is deliberately not claimed because only selected members were acquired.

[Per-file provenance](data/elbow-v1/provenance.json), [licences and attribution](data/elbow-v1/LICENSES_AND_ATTRIBUTION.txt), [reproduction and limitations](data/elbow-v1/README.txt). Later anatomical simulation requires registered joint frames, attachment/path maps, material fields, boundary conditions and independent validation data. A single isometric thickness trace cannot supply all of those missing quantities.

# Muscle pulls through a changing path

A muscle is not merely a red spring. An actuator model needs an input, internal state, force law, geometry and a clear statement of what it omits. Begin with a line of action because it makes loading understandable. Add a three-dimensional continuum only when the question requires internal deformation, local stress, broad attachments or contact.

The benchmark paper by [Millard, Uchida, Seth and Delp](https://pmc.ncbi.nlm.nih.gov/articles/PMC3705831/) compares equilibrium, damped-equilibrium and rigid-tendon models against numerical and biological tests. Its measured speedups belong to its hardware, integrators, tolerances and test actuators. They are not transferable frame-rate promises for an arm demo. Its central practical lesson here is to make tendon assumptions and numerical singularities explicit.

## 1 Excitation is not instantaneous force

Let u ∈ [0,1] be neural excitation and a ∈ [0,1] be activation. A deliberately simple teaching model is

$$\dot a=(u-a)/\tau.$$

For constant u and τ during a step, use the exact update

$$a_{n+1}=u+(a_n-u)e^{-h/\tau}.$$

This avoids the overshoot that a large explicit-Euler step can produce. Separate rise and fall constants can be added, with the switch rule specified. This first-order filter is an illustrative activation model; its time constants must be fitted or sourced before making quantitative physiological claims.

**Reader exercise.** Pulse u while plotting u, a and force. Keep length fixed first. Then move the endpoints without changing u to show that activation alone does not determine force.

## 2 A Hill-type actuator is a collection of functions

Define fiber length l_f, optimal fiber length l_opt, fiber velocity v_f = l̇_f and maximum isometric force F₀. Adopt positive v_f for lengthening. One model family has

$$F_f=F_0\left[a\,f_l(l_f/l_{opt})\,f_v(v_f/v_{scale})
+f_{pe}(l_f/l_{opt})+\beta(v_f/v_{scale})\right].$$

Here f_l is the active force-length curve, f_v the active force-velocity curve, f_pe passive force-length response and β a dimensionless damping coefficient under this normalization. Choose v_scale explicitly, often from optimal length times a maximum-shortening-rate parameter. A model that omits force-velocity effects must not claim to predict the load dependence of shortening speed.

For a toy first lesson, f_l can be a smooth bell curve and f_pe a tension-only polynomial. Label those curves as authored teaching functions. A Gaussian width is a design parameter, not a measured human constant. Later replace the toy law with a specified, tested musculotendon formulation and its published parameter conventions.

Concentric contraction means active shortening; eccentric contraction means active lengthening; isometric means fixed length of the specified quantity. Fixed joint angle does not necessarily imply fixed fiber length when a compliant tendon stretches. A motion label must say whether it refers to whole musculotendon length or fiber length.

## 3 Tendon and pennation add internal state

For a simple pennated actuator,

$$l_{MT}=l_T+l_f\cos\alpha,\qquad F_T=F_f\cos\alpha.$$

The equal-force relation assumes the massless equilibrium idealization of this model. A dynamic tendon or muscle-mass model requires its own momentum equations.

A tendon force law normally depends on normalized tendon length or strain and is tensile. A teaching spring can use F_T = k_T max(0,l_T−l_slack), while a research model should use a specified nonlinear curve, transition smoothing and fitted slack length. A tendon should not become a compressive strut just because its length falls below slack length.

If pennation is modeled using constant thickness h_f,

$$h_f=l_f\sin\alpha,\qquad
l_f\cos\alpha=\sqrt{l_f^2-h_f^2}.$$

Therefore

$$\dot l_{MT}=\dot l_T+\dot l_f/\cos\alpha.$$

The last term is not generally l̇_f cos α because α also changes. The model becomes poorly conditioned as cos α approaches zero; use a physiologically justified domain and explicit failure reporting.

A rigid-tendon approximation removes tendon stretch from the state. It can be useful, but it changes fiber operating lengths, velocities and stored elastic energy. It is a model simplification, not just a faster integrator. Do not switch tendon assumptions silently when moving from offline calculations to an interactive preview.

::: {.keep-together}
**Original equilibrium pseudocode**

```text
muscle_step(path_length, path_speed, excitation, old_state, h):
    advance activation with the specified activation dynamics
    establish admissible fiber-length and pennation bounds
    initialize tendon and fiber state consistently at the starting pose
    evaluate tendon tension from tendon length
    solve the chosen fiber/tendon equilibrium equation
        with safeguarded root finding and the model's velocity convention
    reject or reduce h on loss of admissibility or failed convergence
    return tendon tension, fiber state, stored energy, work and residual
```
:::

This is a solver contract, not an interchangeable formula for every Hill model. For a damped equilibrium formulation one may solve for fiber velocity and integrate fiber length. A fully implicit formulation may solve the next fiber length and velocity together. State which unknown is being solved and report the normalized force residual.

## 4 The signed moment arm comes from virtual work

For musculotendon length l_MT(**q**), positive tension F_T resists increasing length. Virtual work gives

$$\delta W=-F_T\,\delta l_{MT}
=-F_T\sum_j\frac{\partial l_{MT}}{\partial q_j}\delta q_j.$$

::: {.keep-together}
Thus

$$Q_j=-F_T\frac{\partial l_{MT}}{\partial q_j}
=r_jF_T,\qquad r_j=-\frac{\partial l_{MT}}{\partial q_j}.$$
:::

For a rotational q_j, r_j has units of metres. For a translational coordinate, the corresponding derivative has a different interpretation. For coupled coordinates, derivatives must follow the permitted motion, not move one geometrically dependent coordinate independently.

A line segment from an origin point to an insertion point is enough for the first example. Intermediate via points and wrapping surfaces avoid impossible paths through bones, but they introduce branches and possible changes in contact topology. A discontinuous path produces discontinuous moment arms. Plot l(q) and its derivative over the complete supported range before trusting the force curve.

**Reader exercise.** Move a synthetic insertion point farther from the elbow. Predict how tension changes for the same moment. Then compare a straight path with a wrapped path. Verify the analytic or automatic-differentiation moment arm against centred finite differences of path length.

## 5 One net moment does not identify individual muscle forces

If several muscles cross the hinge,

$$\tau_{net}=\sum_i r_iF_i+\tau_{passive}.$$

One measured net moment usually leaves multiple unknown tensions. A flexor and extensor can both increase their forces while leaving the net moment unchanged. An optimization criterion or motor-control assumption can select one solution, but that assumption is additional information, not a measurement.

The reference environment [OpenSim](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006223) supports musculoskeletal model construction and analyses. It is appropriate for independent comparisons when geometry, parameters, excitations, conventions and solver tolerances are matched. Agreement with another program is verification evidence; it is not automatically validation against a person.

## 6 A line actuator does not determine muscle shape

A line model supplies tension and length. It does not uniquely determine bulging, fascicle curvature, local strain, intermuscular pressure or skin sliding. An ellipsoid whose radius increases as its length decreases illustrates an approximate volume constraint, but that geometry is an authored visualization.

For a cylindrical illustration with volume V = πr²l, constant volume implies

$$r(l)=r_0\sqrt{l_0/l}.$$

Show this as a first intuition for lateral expansion, then show why a real muscle with nonuniform architecture cannot be inferred from that formula alone. [Blemker, Pinsky and Delp](https://pubmed.ncbi.nlm.nih.gov/15713285/) used a three-dimensional biceps model and compared local strains with measurements during low-load elbow flexion; their result motivates spatially varying fiber architecture instead of uniform shortening everywhere.

Three-dimensional active tissue can be coupled in either of two educational modes:

- **One-way visualization:** a line actuator drives joint mechanics; an explicitly approximate volume-preserving shape follows activation and length. No tissue reaction is claimed to affect the lift.
- **Mechanical tissue model:** active stress or active strain in a continuum produces tissue forces, contact and bone reactions. Its contribution is included exactly once in the coupled equations.

Adding a line-muscle torque and a second continuum actuator representing the same muscle can count active work twice. The model must declare which component supplies the mechanical action.

## 7 What would make the model credible

Check force-length and force-velocity curves separately before attempting a curl. Test a slack tendon, an isometric activation transient, passive stretch, constant-velocity shortening, constant-velocity lengthening and a return cycle. Check energy accounting for the passive parts and report active work separately. Vary time step and tolerances without retuning material parameters.

For biological validation, match the intended task and available independent observations: external torque, kinematics, fascicle/tendon behavior or deformation fields, with measurement uncertainty. Electromyography can inform activation timing, but it is not a direct tendon-force measurement. Reserve independent trials from calibration. A visually recognizable biceps contraction is an instructional success; it does not establish the accuracy of its predicted internal force.

Laboratories 4–5 implement the declared simplified line and series laws rather than all functions in the general Hill formulation above. Laboratory 7 adds a solved spatial preferred-shortening model, membrane and sampled bone contact under one-way coupling. The line remains the hinge force owner. This lets the reader separate excitation, actual active/passive force, tendon storage and shape, while preserving the stated force–velocity, pennation and architecture omissions.

# Let forces move the elbow {#let-forces-move-the-elbow}

A pose slider answers where a segment is. A forward-dynamics model answers how it accelerates under the forces actually included. Laboratory 4 makes that distinction visible: the same schematic can either move under its actuator and gravity or remain at an explicitly prescribed angle with an external hold moment.


### Laboratory 4 · Articulated elbow and activation

![The fixed upper segment joins a rotating forearm and dumbbell. Gold markers locate a synthetic flexor path. The red belly is an illustrative shape with no mechanical force of its own. The yellow arrow marks dumbbell gravity.](assets/elbow.svg)

Original schematic: q starts at 30° from downward, load 5 kg, excitation 0.6, activation 0, h = 0.005 s. Dimensions and actuator parameters are teaching choices, not anatomical measurements.

**Model:** Schematic one-hinge forward dynamics or prescribed hold; toy line muscle; rigid tendon; no force–velocity law or tissue/contact mechanics.

[Open this laboratory in the web edition](index.html#lab-elbow).


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


**Checked claim virtual-power:** The signed generalized-force power equals negative tension times path-rate under the chain-product assumption.

**Assumptions:** Exact integer force, path derivative dl and angular velocity omega in compatible positive SI scales; derivative and path-rate relations are assumed.

```lean
theorem virtual_power_identity (force dl omega : Int) :
    (-force * dl) * omega = -(force * (dl * omega))
```

**Limits:** Only multiplication/sign algebra is checked; calculus, the geometric derivative and browser arithmetic require separate numerical verification.

Declaration: `Kenoma.virtual_power_identity`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


This exact-integer proof checks the multiplication and sign contract once the derivative and rate relations are supplied. It does not prove the trigonometric derivative or its JavaScript implementation. That limitation is why the separate geometric checks remain necessary.

## Excitation, activation, and force are different states

The control u is excitation in [0,1]. Activation a follows a first-order filter. With a constant input during one step,

$$\dot a=(u-a)/\tau,\qquad a(t+h)=u+(a(t)-u)e^{-h/\tau}.$$

The implementation uses τ = 0.05 s while excitation is at least the current activation, and 0.15 s otherwise. Both are illustrative choices. Release sets u to zero while retaining a, q and q̇. Force therefore decays rather than disappearing instantaneously. Changing excitation preserves the trajectory; changing the load, mode, initial angle or timestep starts a fresh experiment.

The exported trace has one row per step. A same-time excitation change refreshes the current row's input and instantaneous derived outputs, so an immediate download matches the display. Earlier rows remain intact; time, state and accumulated work do not advance. The current row's excitation applies to the next step. Intermediate input edits with zero elapsed time are not separate events.

The exact real-arithmetic update is a convex mixture of a and u with weight e^(−h/τ). The following checked contract concerns integer-weighted mixture numerators only. Neither the exponential implementation nor the physiological validity of those time constants is formally established.


**Checked claim activation-bound:** A nonnegative integer-weighted mixture of bounded inputs has a bounded numerator.

**Assumptions:** Exact integer a and u in [0, scale]; weight w in [0, d]. For a normalized mixture, additionally d > 0.

```lean
theorem activation_weighted_bound (a u w d scale : Int)
    (ha0 : 0 ≤ a) (hau : a ≤ scale) (hu0 : 0 ≤ u) (huu : u ≤ scale)
    (hw : 0 ≤ w) (hwd : w ≤ d) :
    0 ≤ a * w + u * (d - w) ∧ a * w + u * (d - w) ≤ scale * d
```

**Limits:** Does not prove exp() bounds, floating-point activation, or physiological validity; the numerator is bounded by scale*d.

Declaration: `Kenoma.activation_weighted_bound`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


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

**Try the pulse.** Click “Lift / release pulse.” It resets the scenario, applies u = 0.6 for 0.30 simulated seconds, and then releases it. Watch initial gravity-driven lowering before activation builds, subsequent flexion, and continued motion during activation decay. A falling angle is not proof that the muscle is inactive; inspect activation and fiber velocity separately. Pause, single-step, and download the trace to inspect q, a, moments and work.

**Try an unassisted load change.** Increase the dumbbell mass and replay with the same excitation. The model may lower or leave its domain. No hidden motor raises a weak actuator to the requested pose. Reset clears state, camera, and stale input validation.

**Try the prescribed hold.** Select “Prescribed static hold,” vary q and excitation, then step activation. The bones stay fixed because the mode prescribes them. The displayed external hold moment is −(τ_A + τ_P + τ_g). It is an explicit support, not muscle-generated motion. Since q̇ = 0, the support and muscle deliver zero skeletal mechanical power in this fixture, while real muscle metabolism is outside the modeled system. Switching modes resets the experiment rather than injecting an unexplained constraint impulse.

## Mechanical work gives an independent diagnostic

The mechanical energy includes hinge kinetic energy, gravitational potential, and the passive fiber spring:

$$E=\tfrac12I\dot q^2-C\cos q+\tfrac12k_P\delta^2,\qquad
W_A=\int\tau_A\dot q\,dt,\qquad D=\int b\dot q^2\,dt.$$

For this continuous model, E − E₀ − W_A + D = 0. Activation is an externally driven state; its chemical energy is not part of E. Negative active work during active lengthening can occur and is retained with its sign. Gravity is already in E and is not added as external work a second time.

The implementation advances q, q̇, W_A and D using classical RK4 with the exact activation state evaluated at each stage. The passive-force kink can affect observed convergence; no blanket fourth-order result is claimed for every trajectory. An original 0.60 s pulse/release experiment produces the table below from the same pure module used by the browser. The residual is a numerical balance diagnostic, not biological validation.

| h (s) | Steps | Final q (°) | Final a | Active work (J) | Max balance residual (J) |
|--:|--:|--:|--:|--:|--:|
| 0.0100 | 60 | 69.01160 | 0.081000 | 11.348803 | 1.7e-05 |
| 0.0050 | 120 | 69.01146 | 0.081000 | 11.348776 | 8.53e-06 |
| 0.0025 | 240 | 69.01151 | 0.081000 | 11.348787 | 7.77e-07 |


The smallest-step trajectory supplies a numerical comparison, not a measured reference. Tests also check static gravitational moment, inertia, activation transients, path derivatives, signed power, replay, and the explicit stop/hold behaviors. Actual tendon compliance, co-contraction and coupled tissue forces belong to later stages.

# From line forces to tissue and rendered skin {#tissue-and-rendered-skin}

Laboratory 4 moves a rigid skeleton. Its red ellipsoid cannot tell us where tissue compresses. The next layer must introduce material deformation, interfaces and contact before it supplies forces or pressure. This chapter integrates the audited simulation and anatomy research into the progression. Laboratory 5 implements a bounded affine-block/contact proxy; Laboratories 6–7 implement the spatial FEM comparison and a separate schematic skin/fascia/contact model described in later chapters. Their stated limits distinguish working examples from anatomical prediction.

## Deformation needs a reference configuration

The earlier [property measurements](#measure-a-prescribed-deformation) already defined reference/current positions, dimensionless strain and volume ratio. There, the controls chose the vertices. Here the new question is what material energy and boundary forces should determine those positions. Reuse the measurements as checks; positive volume or a convincing outline is not a constitutive law.

Write a material point X in the reference shape and its current position x(X). The deformation gradient F = ∂x/∂X describes local changes; J = det F measures local volume ratio. A rigid rotation has F = R and J = 1, while stretch and shear change the local geometry. Volume preservation alone does not establish an appropriate tissue response or fiber architecture.

For a tetrahedral finite element, construct F from current and reference edge matrices, assign a material energy density Ψ(F, fibers), integrate that energy over the reference volume, and differentiate to obtain nodal forces. A six-edge spring network on the same tetrahedron is a different model. It does not become FEM by sharing the topology. Fiber directions, large deformation, incompressibility, boundary conditions, and inversion behavior each need an explicit choice.

First Piola–Kirchhoff stress P and Cauchy stress σ both have Pa units. They act in different configuration descriptions and satisfy σ = J⁻¹ P Fᵀ under the usual mapping. Confusing those measures is a configuration error, not a unit conversion. Local stress cannot be read from a skinning weight or inferred from a single silhouette.

An active continuum may add fiber-directed stress or use an active-strain decomposition. If it represents the same synthetic flexor as the line actuator, choose a single force owner: either its tissue reactions drive the joint, or the line drives the joint and the tissue is an explicitly one-way visualization. Adding both actuator moments for the same muscle doubles active work. Ryan and colleagues' original finite-element compression study examines how transverse loading changes muscle work and force; its simplified contracting blocks do not validate a human anterior elbow fold. [Original study](#source-compression)

## Skin, fascia and interfaces answer separate questions

The skin envelope, subcutaneous layer, deep fascia, muscle connective tissue and tendons differ in geometry, attachments, and loading. An attachment condition controls motion relative to a bone or neighboring layer. A sliding interface permits tangential relative motion under its stated law. Contact controls whether two surfaces may occupy the same region. A generic stiffness number cannot represent all three.

Material evidence must keep species, orientation, strain range, activation and loading context. The audited Takaza study is passive **porcine tensile** testing at different orientations; it is not transverse human-arm compression evidence. The forearm indentation estimates introduced earlier have their own layer and inverse-identification context. A shear-wave or effective indentation modulus should not silently become a universal large-strain Young's modulus.

The concave anterior elbow crease and convex posterior tissues have different deformation demands. Posterior fat-pad gliding is not an anterior skin-contact measurement. Similarly, a rigid-body joint reaction is a resultant, whereas cartilage or skin pressure requires a local contact area and a constitutive/contact model. Report “not modeled” for those absent outputs, rather than zero.

## Normal contact, friction and coupling

For a chosen gap g_n and compressive normal multiplier λ_n, ideal unilateral contact satisfies g_n ≥ 0, λ_n ≥ 0 and g_n λ_n = 0. A penalty method tolerates penetration and estimates force from a specified law; it requires a penalty/timestep sensitivity study. A constraint solver has its own iteration residual and tolerance. Friction adds a tangential law and dissipation and should not be confused with the normal condition.

Define a transferred force f as the force **on the bone** and −f on tissue. Match action/reaction, moment about a common origin, and power at the same interface velocity. If a model already includes the forearm's tissue mass in its segment inertia, adding massive tissue proxies requires redistributing that mass explicitly.

Near-volume preservation can cause lateral expansion when tissue flattens. It cannot by itself prevent surface intersection. Test compression, sliding, attachment, and volume separately before a coupled crease. Mesh refinement, timestep refinement and contact-tolerance studies answer different questions; none can replace an independent measured deformation field.

## Faster methods change the model or its solution

PBD projects geometric constraints after a prediction step. Its stiffness can vary with timestep and iteration count. XPBD introduces compliance scaled by timestep and accumulated multipliers to reduce that coupling, while finite iterations, nonlinearities and contact can still produce error. [Macklin et al.'s original XPBD paper](#source-xpbd)

Linear blend skinning (LBS) instead evaluates a weighted sum of bone transforms. It has no material energy, activation or contact reaction. Two equally weighted rotations about a common axis illustrate its volume artifact: in the rotated plane, averaging R(+φ) and R(−φ) yields cos φ times the identity. At φ = 60°, that plane's area scales by cos² φ = 0.25. This is an authored exact graphics counterexample, not a measurement of elbow skin.

Dual-quaternion skinning improves rotational interpolation and addresses familiar LBS deformation artifacts, but it does not introduce contact or a tissue constitutive law. Kavan and colleagues' original paper analyzes that approximation. Neither technique supplies pressure by itself. [Original paper](#source-dqs)

Reduced deformation bases, cached simulations and learned mappings can save computation by removing degrees of freedom or reusing prior solutions. Their domain needs testing on unseen poses and contact states. Compare the same geometry, load, material, boundary conditions and error measure before attributing a difference purely to solver speed. A medical/CAD analysis needs parameter identification, convergence and independently measured outputs; a game/film deformation may legitimately optimize visible shape and latency. No universal speed/accuracy ranking follows from the category name.

## Keep the pose in one place

If a detailed render surface follows a tissue proxy, embed it directly in the posed proxy, or add a displacement residual measured against its baseline at the **same current pose and coordinate frame**. Adding an unposed rest-relative displacement to an already skinned vertex applies part of the pose twice. Test this with a pure bone-motion sweep: a zero tissue residual must leave exactly the baseline surface.

For the spatial capstone, synchronize the actual q(t) from forward dynamics across the naive skinning and tissue views. Keep the base mesh and skeletal transforms identical. Show geometric distortion separately from detected intersection, contact gap separately from pressure, and each force owner separately from its visual shape. Laboratory 4 supplies the first trajectory and actuator telemetry for that comparison; Laboratory 7 adds the spatial volume, membrane, fascia-tether and sampled bone-contact solve with a synchronized baseline and measured defects.

# Store tendon energy and resist compression {#tendon-tissue-coupling}

Laboratory 4 used a rigid tendon and an illustrative belly. Laboratory 5 adds two physical mechanisms while preserving that earlier lesson: a massless series tendon/fiber equilibrium and a quasistatic tissue block whose reaction changes the hinge acceleration. The right-hand drawing is a synchronized graphics baseline at the **same q**, not another dynamics simulation.


### Laboratory 5 · Tendon, tissue and the same-pose skinning baseline

![Both schematic arms have the same angle. Left: red active/passive fiber and gold tensile tendon; enlarged teal tissue block between gold frictionless plates. Right: the identical bind block receives uniform 50/50 linear blend skinning and has no force model. Insets are enlarged eight times in world units; read SI values for actual dimensions.](assets/series.svg)

Static reference at q = 90°; interactive starts at q = 30°. Tendon stiffness 30,000 N/m, tissue shear modulus 1,500 Pa and bulk modulus 50,000 Pa are authored teaching choices. Surface is the block boundary, not a separately modeled skin layer.

**Model:** Schematic series actuator; quasistatic affine hyperelastic block with ideal plate contact; tissue reaction drives the hinge. No anatomical calibration, spatial FEM or separate skin/fascia law.

[Open this laboratory in the web edition](index.html#lab-series).


The tissue block's boundary is the rendered surface. There is no separate skin membrane, fascia layer, fiber architecture field or anatomical attachment map yet. The plate gap is an authored function of angle, rather than a distance measured from elbow meshes. This bounded proxy makes tendon stretch, elastic storage, compression and skinning volume loss measurable before anatomical detail is introduced.

## One-dimensional contraction can redistribute length at fixed endpoints

Let l be the synthetic musculotendon path from Laboratory 4, l_f the fiber length and l_T the tendon length. There is zero pennation and l = l_f + l_T. An active force source in parallel with a passive fiber spring supplies

$$F_A=aF_0,\qquad F_P=k_M\max(0,l_f-l_0),\qquad
F_T=k_T\max(0,l_T-l_{Ts}),\qquad F_T=F_A+F_P.$$

The active source is deliberately independent of fiber length and velocity in this lesson. It is a tensile teaching actuator, not a calibrated Hill model. This choice differs from Laboratory 4's bell-shaped active curve and is disclosed rather than attributing that change to tendon compliance alone. A rigid/compliant comparison **within Laboratory 5** changes only the tendon assumption. Millard and colleagues' original comparison motivates making tendon assumptions and internal state explicit; the formulas here are original simpler teaching laws. [Original actuator comparison](#source-muscle)

Write c_T = 1/k_T and Δ = l − l_Ts − l₀. The equilibrium is piecewise analytic. If Δ − c_T F_A ≤ 0, the passive spring is slack and F_T = F_A. Otherwise,

$$F_T=\frac{F_A+k_M\Delta}{1+k_Mc_T},\qquad
l_T=l_{Ts}+c_TF_T,\qquad l_f=l-l_T.$$

Both cases retain tensile tendon force. At zero activation and sufficiently short path, the tendon carries no force; a slack tendon is not a compressive strut. The rigid switch sets c_T = 0, so the tendon cannot store energy. The supported fiber domain is l_f ≥ 0.04 m; leaving it stops the teaching solve instead of extrapolating toward zero fiber length. This is an authored admissibility bound, not a physiological threshold.

For the passive-taut case set d = 1 + k_M c_T; in the passive-slack case d = 1. Differentiating the equilibrium gives

$$\dot l_f=\frac{\dot l-c_TF_0\dot a}{d},\qquad
\dot l_T=\dot l-\dot l_f.$$

Thus a held joint can have l̇ = 0 while fibers shorten and the tendon lengthens as activation rises. Release can lengthen an active fiber while the whole path remains fixed. “Isometric” must name the quantity that is held: joint angle, total path, or fiber length. The controls show all three length quantities and the fiber velocity.

**Try a fixed-end activation.** Choose prescribed hold, q = 90°, and step through activation. Compare rigid and compliant tendon after resetting the experiment. The generated 0.30 s fixture is:

| Tendon | a | Fiber length (m) | Tendon length (m) | Tendon energy (J) | Active work (J) |
|:--|--:|--:|--:|--:|--:|
| rigid | 0.598513 | 0.168035 | 0.060000 | 0.000000 | 0.000000 |
| compliant | 0.598513 | 0.144095 | 0.083941 | 8.597220 | 8.597216 |


All values belong to the authored schematic. At this pose the passive fiber spring is slack. The compliant case stores about 8.60 J in the tendon while the rigid case stores none. That energy does not come from motion of the prescribed skeleton: it comes from active fiber shortening. No metabolic efficiency or ATP consumption is modeled.

## Count active work at the fiber, not twice at the hinge

The passive stores are

$$U_M=\tfrac12k_M\max(0,l_f-l_0)^2,\qquad U_T=\tfrac12c_TF_T^2.$$

The hinge receives muscle power −F_T l̇. The active element delivers P_A = −F_A l̇_f. They differ because the passive fiber and tendon store or release energy. Indeed,

$$\dot U_M+\dot U_T=F_P\dot l_f+F_T\dot l_T,
\qquad P_A-(\dot U_M+\dot U_T)=-F_T\dot l.$$

The moment arm r = −dl/dq therefore still transmits τ_MT = r F_T, once. There is no second muscle-body actuator. Negative P_A during active lengthening is retained as signed mechanical work absorbed by this simple active source. The initial elastic state is included in E₀, so switching the initial pose does not silently erase a preload.

## A small continuum ansatz with an explicit material law

Compare this step with [prescribed isochoric kinematics](#exact-isochoric-kinematics): that lesson sets a transverse stretch to make $J=1$. Here the plate gap supplies one deformation constraint, while the material energy and free-side condition determine lateral expansion. Near-volume preservation is a result to measure, not a square-root motion rule imposed on the block. This homogeneous ansatz still cannot describe nonuniform three-dimensional muscle or layer motion.

The tissue proxy is one homogeneous block, reference width W = 0.08 m, height H = 0.06 m and depth D = 0.05 m. It deforms affinely with F = R(q/2) diag(t,h,t), where t is free lateral stretch and h is compression stretch. This is a **reduced continuum ansatz**, not a six-edge spring network, a tetrahedral FEM mesh, or a full arm tissue solve. Its homogeneous strain cannot describe folds, heterogeneous stress or local sliding. The rigid rotation R changes neither the following invariants nor energy.

Define J = t²h, I₁ = 2t² + h² and V₀ = WHD. The chosen hyperelastic energy is

$$U_B=V_0\left[\frac{\mu}{2}\left(J^{-2/3}I_1-3\right)+\frac{\kappa}{2}(J-1)^2\right].$$

The first term penalizes shape change and the second penalizes volume change. The default μ = 1,500 Pa and κ = 50,000 Pa are authored material values. They are not the skin/adipose estimates cited in the anatomy chapter. J remains positive in the supported model domain. The continuum framework relates an energy to its stress and forces; the bibliographic Sifakis/Barbič record and independently opened Ryan et al. compression research supply further-reading context, while this block solve and numerical experiments are Kenoma's own. [Continuum source record](#source-continuum), [compression study](#source-compression)

For stretches λ_i = (t,h,t), the diagonal first Piola components are

$$P_i=\mu J^{-2/3}\left(\lambda_i-\frac{I_1}{3\lambda_i}\right)
+\kappa(J-1)\frac{J}{\lambda_i}.$$

Free lateral faces require P_x = P_z = 0. For a compressed block, the implementation brackets t between h and 1/√h and bisects that scalar equation. It reports the remaining lateral stress residual. The hard plate constraint fixes h; this is not a penalty that merely makes penetration small. Removing bulk resistance sets κ = 0 and allows stress-free uniform contraction t = h, exposing large volume loss under the same imposed gap.

## Contact produces a force, pressure and generalized moment

The ideal opposed plates have gap

$$g(q)=0.085-0.055\sin(q/2)\ \mathrm{m}.$$

When g ≥ H, the block is unstressed with t = h = 1 and zero reaction. When g < H and contact is enabled, h = g/H and the lateral equilibrium supplies t. The normal force on either plate is N = −WD P_y, taken nonnegative. The current contact area is WD t², so this **uniform model plate pressure** is N/(WD t²). It is not a measured anterior-elbow or cartilage pressure.

The tissue resists closure. Its generalized hinge moment is

$$Q_B=N\frac{dg}{dq}=-\frac{dU_B}{dq}.$$

Because dg/dq is negative, the moment opposes flexion. Both plate reactions are represented by this one gap-coordinate work N ġ; adding twice that generalized moment would double-count the same interface work. There is no tissue inertia or extra mass. Its conservative reaction does feed back into the existing hinge, while the prescribed mode displays the external support needed to oppose it.

The diagnostics show clearance g − hH, penetration max(0,hH − g), normal force, and the complementarity product N(g − hH). The zero clearance in active contact is a consequence of this closed-form plate constraint. It supplies no collision guarantee for arbitrary meshes, trajectories or skin self-contact. Turning contact off leaves the unstressed block at its rest height and exposes overlap with the closing plates; its reaction is then zero.

## Compare a surface transformation at the identical angle

Both views start with the same reference block. The naive baseline assigns every vertex uniform weights 1/2 to identity and a rotation R(q) about the common hinge axis:

$$x_{LBS}=\tfrac12(X+R(q)X),\qquad J_{LBS}=\cos^2(q/2).$$

The renderer applies that transform to the actual bind-space vertices. It does not add a rest-relative displacement to an already posed surface. The physical block has its own affine deformation and shared bisector-frame orientation. Insets are translated and enlarged equally for display, and the reported volumes use physical dimensions. The comparison isolates constitutive/contact response versus a geometric transform; it is not a full, spatially weighted anatomical elbow-skin benchmark. [Original geometric skinning paper](#source-dqs)

| q (°) | Tissue J | LBS J | Normal force (N) | Model pressure (Pa) | Tissue moment (N m) |
|--:|--:|--:|--:|--:|--:|
| 30 | 1.000000 | 0.933013 | 0.0000 | 0.00 | 0.00000 |
| 60 | 0.998760 | 0.750000 | 0.7756 | 186.06 | -0.01847 |
| 90 | 0.992902 | 0.500000 | 5.5027 | 1064.75 | -0.10700 |
| 120 | 0.987771 | 0.250000 | 11.6373 | 1834.38 | -0.16001 |
| 135 | 0.985605 | 0.146447 | 14.9407 | 2159.30 | -0.15723 |


At 90°, the physical block retains about 99.29% of its reference volume, while this LBS fixture retains 50%. In this particular fixture the LBS surface remains separated from the plates; the lesson reports volume loss rather than inventing an intersection. Its force, stress and pressure outputs are “not modeled.” The teal block with contact disabled instead produces a genuine measurable overlap. These are distinct failure demonstrations.

## Close the full work balance and expose numerical cost

The hinge now obeys I q̈ = τ_MT + τ_g − b q̇ + Q_B. Total mechanical energy includes hinge kinetic energy, gravity, U_M, U_T and U_B. With W_A = ∫P_A dt and D = ∫b q̇² dt,

$$E-E_0-W_A+D=0$$

for the continuous forward model. In prescribed static hold q̇ = 0, the support performs no work, but fiber/tendon redistribution can still change E. Gravity is counted once through its potential and moment, and tissue work is exchanged between its store and the hinge, not added again as external energy.

The solver uses RK4 with exact constant-input activation at each stage. It locally bisects a step when trial stages cross the passive-fiber or plate-contact branch, up to eight levels. The visible event-subdivision count and exported accepted substep count disclose this extra work. This reduces branch-related work error; it does not prove general convergence or floating-point correctness. The generated pulse/release experiment is:

| h (s) | Final q (°) | Active work (J) | Max energy residual (J) | Event splits | Accepted substeps |
|--:|--:|--:|--:|--:|--:|
| 0.0100 | 66.746198 | 10.675645 | 7.99e-05 | 16 | 76 |
| 0.0050 | 66.746194 | 10.675732 | 1.14e-05 | 16 | 136 |
| 0.0025 | 66.746194 | 10.675721 | 8.46e-07 | 16 | 256 |


Independent checks cover series equilibrium and lengths, fixed-end fiber shortening and release lengthening, the rigid-tendon limit, energy/stress finite differences, the tissue moment versus an energy derivative, free-side stress residuals, contact complementarity, contact/volume ablations, LBS vertex geometry, replay, and timestep refinement. The existing Lean cards remain limited to their exact algebraic domains; none certifies this continuum solve or biology.

The following chapters implement spatial FEM and a separate on-arm skin/fascia/contact teaching model. Laboratory 7 completes the schematic same-pose capstone with its own one-way limits and measured defects. An anatomical extension would still need registered geometry, identified properties, routed attachment regions and robust surface self-contact; those clinical questions are separate from this completed teaching progression.

# From a spring to a volume of tissue {#from-a-spring-to-a-volume-of-tissue}

A spring connects a few points. A continuum assigns a deformation and a material response throughout a volume. This distinction matters when the question is where a muscle expands, how a patch of tissue is compressed, or which region carries stress. A visually dense surface mesh does not create a volumetric material model.

The [early property lessons](#measure-deformation-before-choosing-a-muscle-law) supplied geometric measurements and a reduced axial calculation. This chapter reuses $F$, $J$ and strain, then introduces a three-dimensional energy density, matching stress measures and equilibrium. The earlier bar's area profile was prescribed and its balance was axial only; a continuum model must also account for transverse response and boundary conditions. The homogeneous compression block in [Laboratory 5](#tendon-tissue-coupling) is one bounded example of that additional step.

The notation and elementary derivations below are self-contained. [Sifakis and Barbič's FEM course](https://viterbi-web.usc.edu/~jbarbic/femdefo/) is a bibliography lead; its full notes were inaccessible in the audit, so no formula below is attributed to unread course content. The proposed exercises are educational tests, not claimed reproductions of published biological experiments.

## 1 The deformation gradient records local shape change

Let **X** be a point in the reference body and **x** = φ(**X**,t) its current position. The deformation gradient is

$$\mathbf F=\partial\mathbf x/\partial\mathbf X.$$

A small reference segment d**X** becomes d**x** = **F**d**X**. The determinant J = det **F** is the local volume ratio. J = 1 means local volume preservation; J < 1 means volume loss; J ≤ 0 is a degenerate or inverted material element in the ordinary orientation-preserving solid model.

A pure rotation has **F** = **R**, J = 1 and no elastic strain. The Green strain

$$\mathbf E_G=\tfrac12(\mathbf F^T\mathbf F-\mathbf I)$$

vanishes for every rigid rotation. Small-strain elasticity uses ε = ½(∇**u**+∇**u**ᵀ), where **u** = **x**−**X**, and does not have that property for large rotations. Rotating a stiff element is therefore an excellent test of whether an implementation has confused a small-strain formula with a finite-deformation model.

**Reader exercise and extension.** The implemented [deformation lab](#lab-property-deformation) measures **F**, J and Green strain under rotation, stretch and shear; it has no stored-energy law or singular-value readout. As a separate extension, compute the singular values of **F**, select an objective material energy, and rotate an undeformed tetrahedron through 180 degrees: its constitutive energy should remain at the reference value. That extension is not an implemented property-lab control.

## 2 Energy and stress must use matching configurations

For hyperelastic material, stored energy is

$$U=\int_{\Omega_0}\psi(\mathbf F)\,dV_0.$$

The first Piola stress is **P** = ∂ψ/∂**F**, and the Cauchy stress is

$$\boldsymbol\sigma=J^{-1}\mathbf P\mathbf F^T.$$

**P** pairs with reference area and **F**. **σ** acts on current area. Plotting one while labeling it as the other creates an incorrect configuration interpretation despite compatible Pa units even when the color map looks smooth. Force is measured in N; stress in Pa = N/m². A nodal force is not a local stress sample.

For an isotropic example valid for J > 0, use a volumetric/deviatoric split,

$$\psi=\frac{\mu}{2}(J^{-2/3}I_1-3)+\frac{\kappa}{2}(J-1)^2,
\qquad I_1=\mathrm{tr}(\mathbf F^T\mathbf F).$$

Here μ is the small-strain shear modulus and κ the bulk modulus. Differentiation gives

$$\mathbf P=\mu J^{-2/3}\left(\mathbf F-\frac{I_1}{3}\mathbf F^{-T}\right)
+\kappa(J-1)J\mathbf F^{-T}.$$

At the identity, this stress vanishes. Under uniform scale **F** = s**I**, the isochoric term contributes no stress; the volume term governs the response. This yields an independently checkable material test before any mesh is assembled.

The illustrative energy is not a universal tissue law. Muscle can be anisotropic and active; tendon has strong directional response; skin can be heterogeneous, anisotropic and rate dependent. A material law must be selected and calibrated for the output being claimed.

## 3 Nearly incompressible does not mean impossible to squash

For small-strain isotropic constants,

$$\mu=\frac{E_Y}{2(1+\nu)},\qquad
\kappa=\frac{E_Y}{3(1-2\nu)}.$$

As Poisson's ratio ν approaches 0.5, the bulk modulus becomes large relative to the shear modulus. Tissue can flatten under a plate while expanding sideways and changing volume only slightly. “Compression” may mean shorter height under a contact load, rather than a large decrease in volume.

A compression experiment must therefore report at least plate displacement, reaction force, lateral expansion and volume ratio. A surface-height plot alone cannot distinguish compliant shear from spurious loss of volume.

Do not enter ν = 0.5 into the formula above. Exact incompressibility requires a different constrained or mixed formulation, commonly involving a pressure unknown. Low-order displacement-only elements can become artificially stiff through volumetric locking as incompressibility is approached. Reduced integration can introduce other modes unless stabilized. Increasing κ without checking element formulation and convergence is not a reliable fix.

## 4 Build one tetrahedral element

Let a rest tetrahedron have points **X**₀…**X**₃ and current points **x**₀…**x**₃. Define

$$\mathbf D_m=[\mathbf X_1-\mathbf X_0\;\mathbf X_2-\mathbf X_0\;\mathbf X_3-\mathbf X_0],$$

$$\mathbf D_s=[\mathbf x_1-\mathbf x_0\;\mathbf x_2-\mathbf x_0\;\mathbf x_3-\mathbf x_0],\qquad
\mathbf F=\mathbf D_s\mathbf D_m^{-1}.$$

With positive rest orientation, V₀ = det **D**ₘ/6. Element energy is Uₑ = V₀ψ(**F**). The force columns on vertices 1, 2 and 3 are

$$[\mathbf f_1\;\mathbf f_2\;\mathbf f_3]
=-V_0\mathbf P\mathbf D_m^{-T},\qquad
\mathbf f_0=-(\mathbf f_1+\mathbf f_2+\mathbf f_3).$$

This formula follows by differentiating the element energy with respect to the current vertex positions. It conserves total internal force by construction. For an objective energy, the internal net torque also vanishes up to numerical error.

::: {.keep-together}
**Original teaching pseudocode**

```text
precompute each tetrahedron:
    require positive, well-conditioned rest volume
    save inverse(Dm), rest volume and material/fiber data
    distribute density * rest volume into the declared mass matrix

evaluate internal forces:
    clear assembled forces and energy
    for each tetrahedron:
        Ds = current edge matrix
        F = Ds * inverse(Dm)
        evaluate J and reject an inadmissible configuration
        evaluate energy density and first Piola stress
        force_columns = -rest_volume * P * transpose(inverse(Dm))
        scatter columns to vertices 1, 2, 3
        scatter their negative sum to vertex 0
        accumulate rest_volume * energy_density
```
:::

Six edge springs over a tetrahedron are a spring network. They do not become FEM by having the same four vertices. Their stiffness depends on topology and chosen springs, and no independent bulk response follows automatically. A separate volume constraint changes that model again. Those are useful lessons if named accurately.

## 5 Choose a material for its behavior and domain

**Linear elasticity** is an excellent first derivative test and small-deformation reference. It is inappropriate for large rigid rotations without an additional treatment.

**Co-rotational elasticity** extracts a local rotation and models strain in a rotated frame. It makes large motion with relatively small local strain easier to handle. Its common volume term is not the same as an exact determinant-based volume penalty, so its behavior under large compression needs testing.

**Saint Venant–Kirchhoff elasticity** uses nonlinear Green strain with a quadratic energy. It is convenient for derivation and reduced polynomial force models, but can behave poorly in severe compression and inversion.

**Neo-Hookean and richer hyperelastic laws** provide other finite-deformation responses. “Neo-Hookean” is a family label: the exact energy, parameter mapping, valid J range and inversion handling must be specified.

[Smith, de Goes and Kim](https://www.tkim.graphics/NEO/StableNeoHookean2018.pdf) develop a particular stable neo-Hookean energy and Hessian treatment for flesh animation. Their tests highlight deficiencies of common co-rotational volume response at large deformation. Robustness to an inverted element is different from preventing inversion, and neither proves biological accuracy. Do not silently replace an ordinary logarithmic or split neo-Hookean formula with that paper's material while keeping the same label and parameters.

## 6 Fibers introduce directional behavior

Store a unit reference fiber direction **a**₀. Its stretch is λ_f = ‖**F****a**₀‖ and its current unit direction is **a** = **F****a**₀/λ_f. A passive fiber energy ψ_f(λ_f) can resist extension preferentially along that direction. A tension-only fiber term should not accidentally resist compression as if every fiber were a rigid rod.

Two active formulations illustrate distinct assumptions.

**Active stress:** add a current stress

$$\boldsymbol\sigma_a=s_a(a,\lambda_f,\dot\lambda_f)\,\mathbf a\otimes\mathbf a,$$

and convert it consistently through **P**ₐ = J**σ**ₐ**F**⁻ᵀ. Its supplied power must be recorded; do not assume an arbitrary active-stress law derives from a conservative elastic energy.

**Active strain:** change the locally preferred deformation. For a synthetic volume-preserving contraction tensor,

$$\mathbf F_a=\lambda_a\mathbf a_0\otimes\mathbf a_0
+\lambda_a^{-1/2}(\mathbf I-\mathbf a_0\otimes\mathbf a_0),\quad 0<\lambda_a\le1.$$

Set **F**ₑ = **F****F**ₐ⁻¹ and evaluate an elastic energy in **F**ₑ. At fixed activation,

$$\mathbf P=\frac{\partial\psi_e}{\partial\mathbf F_e}\mathbf F_a^{-T}.$$

Activation changes the energy landscape and can do work. This is a teaching construction, not an assertion that an active-strain model and a Hill actuator produce identical force histories. Its mapping from activation to λ_a requires calibration.

The early [Teran et al. skeletal-muscle simulation](https://graphics.stanford.edu/papers/fvm_sig03/) demonstrates a directional hyperelastic tissue approach and a geometric force interpretation. [Blemker and Delp's architecture study](https://pubmed.ncbi.nlm.nih.gov/15981866/) motivates representing broad attachments and spatially varying fiber trajectories. Use those papers as motivation and provenance, not as a license to substitute arbitrary fiber fields and call the result validated muscle.

## 7 Solve equilibrium or dynamics deliberately

A quasistatic solve seeks force balance at each imposed pose. It omits inertia and is useful for slowly posed deformation, but it cannot predict vibration or impact timing. A dynamic solve adds mass and inertia, and needs initial velocities and a time integrator. Heavy damping can approximate a settling process but introduces another timescale.

For implicit dynamics, compute the residual and tangent, solve a Newton or quasi-Newton step, and use a line search or trust strategy that respects admissibility. Positive-definite Hessian projection changes the search direction; if the original objective and residual are retained and converged, it need not change the target stationary point. Stopping early still changes the result. State tolerances and residuals rather than simply reporting that the solver finished.

## 8 Tests before an anatomical mesh

1. Compare analytic forces with centred finite differences of energy over several perturbation sizes.
2. Apply rigid translations and rotations; check unchanged energy and transformed forces.
3. Apply uniform affine deformation to a mesh patch; verify consistency of deformation gradients and expected boundary reactions.
4. Stretch and shear blocks with controlled boundaries; compare with the chosen material law.
5. Compress a block at several κ/μ ratios and mesh resolutions; measure locking, volume change and reaction force.
6. Repeat at smaller time steps and tighter solver tolerances before increasing mesh detail.
7. For active material, compare active work, boundary work, kinetic energy, stored energy and dissipation.

An anatomical surface should be the final demanding example, not the first occasion on which an element's force formula is tested.

# Fast solvers and what they approximate

Interactive performance can come from fewer unknowns, cheaper material laws, reusable linear algebra, looser convergence or less demanding collision handling. These choices have different consequences. A useful comparison holds the modeled problem fixed when testing a solver, and holds the solver tolerance fixed when testing a material. Otherwise a speed comparison may be measuring different physics.

## 1 Position based dynamics

Position based dynamics predicts positions and then corrects constraint violations. For a scalar equality C(**x**) = 0, inverse mass w_i and gradient **g**ᵢ = ∇ᵢC, a local mass-weighted correction has

$$\Delta\lambda=-\frac{C}{\sum_i w_i\|\mathbf g_i\|^2},
\qquad\Delta\mathbf x_i=w_i\mathbf g_i\Delta\lambda.$$

Distance, bending and volume conditions can share this projection structure. Applying corrections sequentially uses the newest positions, while parallel updates require an explicit accumulation or coloring strategy.

The original [Müller et al. paper](https://matthias-research.github.io/pages/publications/posBasedDyn.pdf) targets controllable, robust interactive animation. A finite projection budget leaves error. In ordinary PBD, apparent stiffness also depends on the time step and iteration count, so a value such as 0.8 is an algorithmic setting rather than a material modulus.

**Reader exercise.** Hang a short chain under gravity. Change the iteration count without changing its nominal stiffness. Plot its equilibrium extension. Then increase chain length; local information takes additional iterations to propagate through the constraints.

## 2 XPBD makes compliance explicit

Extended position based dynamics introduces compliance α and a total multiplier λ within the step. For the scalar elastic constraint energy U = C²/(2α), define α̃ = α/h². The update is

$$\Delta\lambda=
\frac{-C-\tilde\alpha\lambda}{\sum_i w_i\|\nabla_iC\|^2+\tilde\alpha},
\qquad\lambda\leftarrow\lambda+\Delta\lambda,
\qquad\Delta\mathbf x_i=w_i\nabla_iC\Delta\lambda.$$

For a distance constraint C = l−l₀, α = 1/k has units m/N. For C = J−1 and volumetric energy V₀κ(J−1)²/2, α = 1/(V₀κ). Constraint normalization therefore changes the required compliance. If C is multiplied by s, α must be multiplied by s² to represent the same energy.

The [XPBD paper](https://mmacklin.com/xpbd.pdf) derives an implicit compliant formulation and a constraint-force estimate. The corresponding nodal force estimate is ∇ᵢC·λ/h² under this convention. Its stiffness parameterization is much less entangled with solver settings than PBD's, but finite iteration count, changing gradients, integration error and contact approximation remain. “Iteration independent” must not be presented as exact convergence in one sweep.

::: {.keep-together}
**Original instructional pseudocode**

```text
advance_xpbd_substep(x, v, h):
    x_old = x
    v += h * inverse_mass * external_force
    x += h * v
    apply prescribed positions at the correct substep time
    initialize elastic multipliers to zero for this substep
    construct/update collision candidates using a declared strategy
    repeat solver_sweeps:
        for each elastic constraint:
            evaluate C, gradients and alpha / (h*h)
            update multiplier and all affected positions
        for each unilateral contact:
            perform projected multiplier update with lambda_normal >= 0
        solve attachments, friction and joints consistently
    v = (x - x_old) / h
    apply declared dissipative or impact velocity corrections
    report residuals, constraint-force estimates and failed contacts
```
:::

This is an original outline. Production implementations need robust gradients, moving boundary velocities, degenerate-configuration handling, consistent friction, and declared multiplier warm-starting. If multipliers are reset every iteration rather than every substep, the compliance formulation above is no longer being implemented.

For unilateral contact, clamp the *accumulated* normal multiplier, then apply only its change. A negative gap may require a repulsive correction, but a separating contact must not become attractive. When contact history, ordering or substep size changes, warm-starting requires deliberate handling and cannot be copied blindly from bilateral springs.

## 3 More substeps can help more than more sweeps

A long time step linearizes a large change. Several smaller steps refresh velocities, geometry and constraint directions. [Macklin et al., Small Steps](https://mmacklin.com/smallsteps.pdf), compares these choices within XPBD and reports improved behavior in its tested examples. This is a reason to benchmark both strategies, not a universal statement that one iteration is sufficient or that collision detection can be skipped between substeps.

**Reader exercise.** Fix a total constraint-evaluation budget and compare one large step with many sweeps against many small steps with fewer sweeps. Record deformation error, damping and runtime. Count collision detection separately; its cost and sampling frequency may change the result.

## 4 Projective dynamics reuses global structure

Projective dynamics writes a selected class of energies as squared distances to constraint sets. A simplified form is

$$\min_{\mathbf x,\{\mathbf p_i\}}
\frac{1}{2h^2}\|\mathbf x-\mathbf y\|_M^2
+\sum_i\frac{k_i}{2}\|\mathbf A_i\mathbf x-\mathbf p_i\|^2,
\qquad\mathbf p_i\in\mathcal C_i.$$

Holding **x** fixed gives independent local projections. Holding **p**ᵢ fixed gives

$$\left(\frac{\mathbf M}{h^2}+\sum_i k_i\mathbf A_i^T\mathbf A_i\right)\mathbf x
=\frac{\mathbf M\mathbf y}{h^2}+\sum_i k_i\mathbf A_i^T\mathbf p_i.$$

With constant h, masses, operators and weights, this global matrix can be factorized once and reused. Changes to them can require updating the factorization. Changing contact sets or moving hard constraints may alter the system unless the implementation uses a formulation that preserves the constant part.

[Bouaziz et al.](https://doi.org/10.1145/2601097.2601116) present the local/global method for a tailored energy class. It is not equivalent to applying arbitrary PBD projections in parallel. Nor does the prefactorization make every nonlinear constitutive law or contact model free. [Liu, Bouaziz and Kavan](https://arxiv.org/abs/1604.07378) extend the interpretation toward quasi-Newton treatment of more general hyperelastic energies.

::: {.keep-together}
**Original instructional pseudocode**

```text
precompute fixed global matrix and factorization
for each substep:
    form inertial prediction y
    initialize x from a consistent state
    repeat until tolerance or declared budget:
        in parallel: project each Ai*x onto its set Ci
        assemble right-hand side
        solve the prefactorized global system for x
        evaluate the original objective and residual
    reconstruct velocity and report convergence
```
:::

If a fixed sweep budget is used for responsiveness, expose its remaining residual. The visual plausibility of a stopped iterate is a different claim from a converged minimizer.

## 5 Reduced models remove possible motions

Represent deformation using r coordinates z instead of 3n vertex coordinates:

$$\mathbf x=\bar{\mathbf x}+\mathbf U\mathbf z,\qquad
\mathbf M_r=\mathbf U^T\mathbf M\mathbf U,\qquad
\mathbf f_r=\mathbf U^T\mathbf f.$$

A fixed basis can contain vibration modes, sampled deformations or other structured motions. Restricting motion to that subspace can substantially reduce the solve, but motions outside the basis cannot be recovered merely by tightening solver tolerances. Localized contact and new activation patterns can require modes the training examples never contained.

[Barbič and James](https://graphics.cs.cmu.edu/projects/stvk/) exploit the polynomial structure of reduced Saint Venant–Kirchhoff forces. Their independence from full mesh size concerns the precomputed reduced integration calculation, not every rendering, collision and preprocessing cost of a complete application. The material and basis limitations remain part of the result.

If the reference shape follows a rig, **x** = **x**_base(t)+**U**(t)**z**, velocities and accelerations include base-motion and basis-derivative terms. Ignoring them changes secondary-motion dynamics. A quasi-static pose-correction system can legitimately ignore inertia, but must be labeled that way.

**Reader exercise.** Train a reduced basis using bending and then press a small probe into the tissue at an unseen location. Display the full-space residual and deformation mismatch. This reveals why an attractive trained motion does not guarantee general contact behavior.

## 6 Shape matching and baked correctives occupy different places

Shape-matching methods fit local transforms to particle clusters and guide the particles toward those shapes. They are useful visual models with a different parameter-to-material relationship from calibrated continuum elasticity. [Müller et al.'s shape-matching paper](https://matthias-research.github.io/pages/publications/MeshlessDeformations_SIG05.pdf) is a primary starting point; verify the exact cluster and volume treatment in any implementation.

A corrective blend shape stores a deformation associated with a pose or control. It can faithfully replay a sampled simulation result while omitting force prediction, history and new contacts. A pose-only cache cannot distinguish two states with the same joint angles but different contact history, activation or loading unless those variables are included as inputs.

The fastest useful path for a game may combine rigging, correctives and small secondary dynamics. A film may accept a slower high-resolution solve for contact-rich shots. A CAD or biomedical question may instead prioritize identified parameters, convergence and uncertainty. Application category alone does not tell us the required solver; the measurable question does.

## 7 A fair comparison protocol

For every comparison, record geometry, mass, material energy, active model, boundary conditions, contacts, mesh, hardware, precision, integrator, h, iteration cap, convergence tolerance and collision settings. Separate preprocessing, simulation, collision, surface transfer and rendering time. Report median and tail latency over a named workload, with cold-start cost separately.

Compare matched-quality configurations. “Faster” at larger penetration, greater volume loss or looser residual is a tradeoff, not a free improvement. Do not reuse paper frame rates as browser targets. The book's interactive budget is an engineering target to measure on specified devices; it is not an established property of a method.

The next worked laboratory holds the material and discrete implicit target fixed while comparing PCG with compliant strain sweeps. Its measured errors and timings make the tradeoff concrete, rather than asking the reader to infer a universal ranking from the methods above.

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

Color by element stress or nodal displacement error with a common stated scale. Element stress is piecewise constant and discontinuous across faces; averaging it onto a smooth visual surface is an additional rendering operation, not a more accurate stress solve. Draw the clamp and the prescribed body/face loads, and provide a text summary with force residual, reaction, energy, and model limits. A static manufactured solution whose support resultant is zero should still show its balanced applied loads.

Useful controls are mesh resolution, compliant sweep count, and step size, with Reset reproducing the same state. Reassemble once after a mesh/material change; do not rebuild the element matrices every animation frame. The supplied example uses only 64 vertices and 162 tetrahedra. Larger meshes can be computed by a Web Worker if needed; this contribution does not certify main-thread latency. Check `converged` before presenting a discrete reference and keep an unconverged finite-sweep result labeled approximate.

`README.md` documents array layout, exports, commands and integration. `sources.json` records exactly which primary texts and sections were opened. `data/provenance.json` and the source-bound test receipt identify the executed code. The inaccessible Sifakis/Barbič course notes remain bibliography-only in the parent audit; no unread formula is imported here. All tables and geometry in this contribution are original generated teaching artifacts, and the existing book assembly and proof registry are left to their owners.



### Laboratory 6 · Matched spatial FEM and compliant solve

![Left: converged discrete FEM reference. Right: a finite compliant strain solve for the identical implicit step, or analytic nodal samples in static mode. Both use the same mesh, camera and visible displacement magnification. Gray outlines show the bind block; the gold edge marks the x = 0 clamp. Orange arrows show six representative applied nodal loads on a common normalized length scale; distributed body and face loads are specified in the chapter.](assets/continuum.svg)

Authored 40 × 20 × 20 mm fixture, E = 100 kPa, ν = 0.25, n = 3, h = 0.0005 s, five compliant sweeps. Displacements in this illustration are magnified 50×; numerical errors and energies are unscaled SI quantities.

**Model:** Linear constant-strain tetrahedra; authored isotropic material; manufactured static load or one implicit step from rest. Small-strain model, no contact or muscle.

[Open the interactive laboratory](index.html#lab-continuum).


![Left: converged discrete FEM reference. Right: a finite compliant strain solve for the identical implicit step, or analytic nodal samples in static mode. Both use the same mesh, camera and visible displacement magnification. Gray outlines show the bind block; the gold edge marks the x = 0 clamp. Orange arrows show six representative applied nodal loads on a common normalized length scale; distributed body and face loads are specified in the chapter.](assets/continuum.svg)

Authored 40 × 20 × 20 mm fixture, E = 100 kPa, ν = 0.25, n = 3, h = 0.0005 s, five compliant sweeps. Displacements in this illustration are magnified 50×; numerical errors and energies are unscaled SI quantities.

**Model:** Linear constant-strain tetrahedra; authored isotropic material; manufactured static load or one implicit step from rest. Small-strain model, no contact or muscle.

[Open the interactive laboratory](index.html#lab-continuum).



**Checked claim compliance-denominator:** A nonnegative inverse-mass quadratic plus strictly positive regularization has a positive scalar denominator.

**Assumptions:** Exact integer w ≥ 0, gradient g, alpha > 0 in common positive scales.

```lean
theorem compliant_denominator_positive (w g alpha : Int)
    (hw : 0 ≤ w) (ha : 0 < alpha) : 0 < w * (g * g) + alpha
```

**Limits:** A one-coordinate special case supporting the compliant solver denominator; finite precision, material assembly, time scaling and iterative accuracy are not proved.

Declaration: `Kenoma.compliant_denominator_positive`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).

# Skin must follow motion without losing the mechanics

The skeleton, muscles, surrounding soft tissue and visible skin are different representations with different jobs. A practical arm may use rigid bodies for bones, lines for musculotendon force, a volumetric proxy for tissue, a surface for contact and a detailed mesh for rendering. Correct coupling is the map that makes those representations agree about positions, forces and work.

## 1 Why linear blend skinning can collapse

For rest vertex **X**ᵢ, bone transforms **T**ⱼ(q), inverse bind transforms **B**ⱼ⁻¹ and normalized weights wᵢⱼ,

$$\mathbf x_i=\sum_j w_{ij}\,\mathbf T_j(\mathbf q)\mathbf B_j^{-1}\mathbf X_i,
\qquad w_{ij}\ge0,\quad\sum_jw_{ij}=1.$$

Use homogeneous coordinates for the affine transforms. At the bind pose, **T**ⱼ**B**ⱼ⁻¹ must be identity in the chosen convention. A rigid transform preserves lengths and volume. An average of rigid transforms generally does not.

An original local demonstration makes the failure quantitative. Blend identity with a rotation R_z(θ), with equal weights and a shared pivot. The linear part is

$$\mathbf A=\tfrac12(\mathbf I+\mathbf R_z(\theta)).$$

In the plane perpendicular to the axis, **A** is a rotation by θ/2 multiplied by cos(θ/2). Along the axis it leaves length unchanged. Consequently,

$$\det\mathbf A=\cos^2(\theta/2).$$

At θ = 90 degrees the transverse scale is about 0.707 and this affine patch has half its original volume. At 180 degrees the transverse plane collapses. This is an analytic property of this deliberately constructed blend, not a claimed percentage volume loss for a complete human elbow. Spatially varying weights contribute additional derivatives to the whole deformation, and ordinary elbow bending also involves different pivots and translations.

**Reader exercise.** Show a weighted cylindrical patch with a wireframe cross-section. Freeze the weights and move only the bones. Then highlight the inner elbow crease in the full arm and display the measured local triangle distortion and any actual intersections. Do not infer intersections from a dark crease in the shading.

[Ladislav Kavan and colleagues' dual-quaternion work](https://users.cs.utah.edu/~ladislav/kavan07skinning/kavan07skinning.html) is an important alternative baseline. Blending rigid transforms through dual quaternions avoids the simple linear-matrix collapse demonstrated above. It does not enforce tissue constitutive response, global volume conservation or self-collision. It can still produce unwanted bulging, pose-dependent geometry and contact failures.

## 2 Geometry needs a collision definition

A contact model needs to specify what touches what, where the boundary lies, and whether thickness is included. Candidate pairs may include tissue-bone, muscle-muscle, skin-skin and skin-object. A signed-distance field can cheaply provide a gap to a rigid bone proxy, but its voxel resolution, sign convention and interpolation error matter. It does not by itself detect every triangle-triangle self-intersection of the skin.

For a gap g ≥ 0, an ideal frictionless normal contact has

$$g\ge0,\qquad\lambda_n\ge0,\qquad g\lambda_n=0.$$

At separation the normal reaction vanishes; at contact it can be compressive but not adhesive. Adhesion is a different model. With Coulomb friction,

$$\|\boldsymbol\lambda_t\|\le\mu_f\lambda_n,$$

with stick/slip conditions and dissipation defined consistently. μ_f is a friction coefficient, not the shear modulus μ. Normal and tangential multipliers must share compatible units and normalization before applying a friction cone.

Penalties, complementarity solvers, projection and barriers are alternative numerical treatments. A finite penalty usually permits some penetration; making it stiff can worsen conditioning or restrict explicit time steps. Discrete endpoint tests can miss objects passing through each other between frames. Continuous collision detection examines the swept motion and must be paired with a response that preserves feasibility.

[Incremental Potential Contact](https://ipc-sim.github.io/) combines barrier-based contact with conservative collision handling in a variational implicit framework. Its intersection/inversion-free claims rely on its stated feasible-start and algorithmic conditions. Do not apply that guarantee to an arbitrary log penalty, an intersecting initial mesh or a few endpoint projection sweeps. It also does not establish that a tissue law or friction coefficient is biologically correct.

**Reader exercise.** Push two soft pads together, then slide one. Plot normal force, tangential force, contact area and dissipated work. Repeat with contact disabled. This separates the material's deformation from the contact algorithm that prevents overlapping bodies.

## 3 Skin and flesh are not necessarily glued together

A render mesh embedded in tetrahedra with barycentric coordinates follows a coarse volume, but embedding alone supplies no separate skin mechanics. A membrane or shell layer can have its own in-plane and bending response. Sliding relative to the underlying tissue requires a declared interface model rather than every skin vertex being welded to its nearest muscle particle.

At one extreme, hard attachment transfers all components of motion. At another, frictionless contact permits tangential slip while preventing normal penetration. Between them are compliant attachments, friction and spatially varying connective constraints. Use a small sliding patch experiment before choosing the arm's interface assumptions.

[Pai et al., The Human Touch](https://www.cs.ubc.ca/research/HumanTouch/HumanTouchSIGGRAPH2018.pdf), measures contact behavior and fits a phenomenological sliding thick-skin model. Its measurement pipeline is evidence for identifying response from data rather than assigning one arbitrary “flesh stiffness” everywhere. The paper does not supply universally valid tissue parameters for every person, body region, activation state or loading rate.

## 4 Force transfer follows the transpose of motion transfer

Suppose a proxy's positions **x** generate contact-surface positions **y** = **E****x**, using a fixed linear embedding. Then

$$\dot{\mathbf y}=\mathbf E\dot{\mathbf x},\qquad
\mathbf f_x=\mathbf E^T\mathbf f_y.$$

The transpose is not a software convenience. It ensures

$$\mathbf f_y^T\dot{\mathbf y}=\mathbf f_x^T\dot{\mathbf x}.$$

For a nonlinear map **y** = Φ(**q**), the corresponding generalized force is **Q** = (∂Φ/∂**q**)ᵀ**f**_y. This is the same virtual-work principle that produced the muscle moment arm.

For a tissue attachment at point **p** on a rigid body, the body receives the opposite force to the tissue and the moment (**p**−**c**)×**f**. If the bone is prescribed, record the boundary reaction and its work even though the solver does not move the bone in response.

**Reader exercise.** Couple a rigid paddle to a deformable block. Push on the block, then on the paddle. The same attachment must transmit reactions in both directions in a two-way simulation. Turning off the reaction path demonstrates the difference between coupled mechanics and one-way visual following.

## 5 Avoid counting the pose twice

A dangerous displacement transfer is

```text
render = already_skinned_surface + (simulated_current_tissue - unposed_rest_tissue)
```

The simulated tissue already includes bone motion, so the subtraction includes pose displacement. Adding it to an already posed surface counts that motion twice.

There are two clean teaching choices.

**Direct embedding:** compute the visible surface from the current simulated volume, **x**_render = **E x**_sim, with any detail offset transported in a well-defined local frame.

**Residual embedding:** evaluate a simulation base state and a skinning base state at exactly the same current pose. Transfer only the extra deformation,

$$\mathbf x_{render}=\mathbf x_{skin}
+\mathbf E(\mathbf x_{sim}-\mathbf x_{base}).$$

The mapping's reference space, rotations, scale and time must agree. If a weighted residual or local-frame rotation is used, specify it and test rigid-motion invariance. Nearest-particle reassignment during motion can cause discontinuities; use a documented fixed embedding when topology permits it.

The decisive test is a zero-deformation pose sweep: disable gravity and secondary forces, make the proxy match its posed base exactly, and rotate the skeleton. The residual must be zero and the rendered surface must match its intended base, without drift or doubled motion.

## 6 Partitioned and monolithic systems

A partitioned method alternates skeleton, muscle, tissue and contact updates. It is modular and may be adequate for weak coupling, but delayed reactions can inject energy or make stiff attachments unstable. Subiterations and a joint residual can improve it. A monolithic solve includes the coupled unknowns in one system, which can better enforce consistency but is more demanding to formulate and solve.

Laboratory 7 implements explicitly one-way tissue response. Two-way extensions require force-transfer and energy tests before interpreting the coupled result. A full model may use different time steps for activation, multibody dynamics and tissue, but exchanges must have defined interpolation, sample times and work accounting. A high-frequency tissue loop cannot repair a sign error in the lower-frequency joint reaction.

The production example in [McAdams et al.](https://la.disneyresearch.com/publication/efficient-elasticity-for-character-skinning-with-contact-and-collisions/) demonstrates skeleton-driven volumetric elasticity with contact and collisions. It is evidence that contact-aware flesh is a distinct computational problem beyond skin weights. Its art-directed skeleton and character examples are not subject-specific medical validation.

## 7 Compression tests for the final arm

In the elbow's inner fold, bending brings opposing skin patches together. A useful deformation should redistribute tissue, develop contact where warranted and avoid visible crossing. The display must distinguish these quantities:

- geometric overlap of nonadjacent triangles;
- signed gap to bone and external-object proxies;
- local J values and total volume change;
- tissue height reduction and lateral displacement;
- contact reaction and material stress in their correct units;
- solver residual and iteration budget.

Do not color every red contact patch as “high pressure.” Pressure requires a defined force-to-area measure or continuum stress; a multiplier, penetration depth or collision flag is not automatically pressure. A contact-free image proves only that no visible overlap was noticed from that camera. The verification system must examine the complete geometry.

Laboratory 7 now implements a separate skin membrane, discrete fascia tethers and compliant sampled contact on the arm itself. Its one-way coupling, absent sliding/self-contact, and sampled-gap limitations are explicit. It transfers centroid contact forces with barycentric weights, while the paired baseline is posed exactly once. The following chapter reports actual residuals and penetration for that implementation.

# Lift, release and compress a spatial arm {#spatial-capstone}

This intermediate teaching scene brings deformation onto a schematic strip around an arm. It combines the already tested excitation–activation, series tendon and rigid hinge with a spatial energy solve, a separate membrane and sampled bone contact. Its paired view asks what changes when the same schematic pose receives mechanical deformation rather than skinning weights alone. It does not satisfy the requested anatomical lifting capstone. The following [coupled tissue chapter](#coupled-tissue-mechanics) replaces the independent force path in an initial engineering fixture; the complete anatomical apparatus and contact remain under development.

This is **one-way, quasistatic coupling**. The line actuator owns the moment that lifts the dumbbell. The pose q and activation a drive the spatial lesson; spatial reactions do not feed back into the hinge. There is no extra active moment added for the displayed volume. The spatial shape solve is massless: it omits its own gravity and inertia, while the hinge retains the stated forearm and dumbbell mass. Its instantaneous elastic energy is not added to hinge work accounting. The body is original teaching geometry, not a registration or remeshing of BodyParts3D. The spatial material is an authored edge/volume network, **not FEM**. The preceding continuum lesson implements genuine FEM and isolates its own solver comparison.


### Laboratory 7 · Muscle under skin and elbow contact

![Left: coral deformable volume, red active fibre spans, gold tendon span, mint separate skin membrane and yellow contact samples on a schematic articulated arm. Right: the identical bind volume and skin, posed once with linear blend skinning at the identical hinge angle. Bones and dumbbells have identical poses; geometry uses SI coordinates and a common viewing scale.](assets/spatial.svg)

Compression fixture: q = 90°, activation 0.6, 640-iteration cap. Mechanical minimum volume ratio 0.736; same-pose LBS minimum 0.171. Sampled penetration 0.0283 mm versus 9.75 mm. This original schematic is not registered to the real atlas.

**Model:** Authored 3D edge/volume energy, separate skin membrane and fascia tethers; finite quasistatic sampled bone contact; one-way hinge → shape. Not FEM, patient anatomy or medical pressure.

[Open the interactive laboratory](index.html#lab-spatial).


## A volume, fibres, tendon spans and an independent skin

The bind volume has 81 vertices and 192 positively oriented tetrahedra in a 38 × 360 × 42 mm rectangular strip beside the bones. Each tetrahedron has a reference volume V₀. The boundary supplies a separate set of skin vertices, initially 4 mm farther out radially. Its triangles have their own in-plane edge energy. The top and bottom cross-sections follow the fixed upper and rotating lower segment. The interior is free to change shape; a fixed skinning transform does not determine those vertices.

Nine aligned upper-span fibre chains carry preferred shortening. Nine stiffer distal edges illustrate tendon spans. The rest of the edge network supplies passive shape resistance. A tendon edge here can store elastic energy and resist extension or compression; this simplified bilateral span is distinct from the **tension-only line tendon** that drives the hinge. It has no slack/toe-region law, pennation or clinical architecture. The end-to-end active span, the summed spatial fibre-chain path, and scalar line fibre length are different observables and are displayed separately. The centre path sums four actual deformed edge lengths; the mean averages all nine aligned chains.

Fascia is represented by compliant vector tethers between corresponding volume-boundary and skin vertices. Each tether's preferred 4 mm offset rotates with the authored pose field. It transmits force between its two vertices but has no anatomical layer thickness or sliding law. It is a constrained sheath approximation; the membrane has no bending energy, and skin–skin and skin–muscle self-contact are absent. These limitations matter when interpreting a fold.

| Component | Implemented law | Authored value | Unit |
|:--|:--|--:|:--|
| Passive tetrahedral-edge network | U = k(l−l₀)²/2 | 80 | N/m per edge |
| Active aligned edge | U = akₐ max(l−l₀(1−0.18a),0)²/2 | kₐ = 500 | N/m per edge |
| Spatial tendon span | U = k(l−l₀)²/2 | 1,200 | N/m per edge |
| Skin edge | U = k(l−l₀)²/2 | 12 | N/m per edge |
| Fascia vector tether | U = k‖x_skin−x_core−d(q)‖²/2 | 30 | N/m per tether |
| Volume resistance | U = κ(V−V₀)²/(2V₀) | 25,000 | Pa |
| Boundary sample contact | U = k min(g,0)²/2 | 12,000 | N/m per sample |
| Interior centroid contact | Same compliant gap penalty | 250 | N/m per sample |

The values are not measured human material parameters. Network response depends on topology and these per-edge coefficients. Refining the grid while retaining them would change the model. The continuum chapter's mesh-refinement evidence therefore cannot be transferred to this network. The ablation controls change the specified energy rather than silently retuning it.

For an edge i–j, length l = ‖xᵢ−xⱼ‖ and gap C = l−l_target, differentiating kC²/2 gives an equal/opposite central force pair. The tension-only active term takes C = max(l−l_target,0). Increasing a changes both its coefficient and target, so the preferred-length law is a phenomenological shape actuator rather than Hill's measured force–velocity relation. The original line model retains its own declared excitation, activation and tendon assumptions.

## Actual volume gradients and contact forces

A tetrahedron's signed current volume is

$$V=\frac16(\mathbf x_1-\mathbf x_0)\cdot[(\mathbf x_2-\mathbf x_0)\times(\mathbf x_3-\mathbf x_0)].$$

For example, ∂V/∂x₁ = [(x₂−x₀)×(x₃−x₀)]/6. The other two edge-vertex gradients follow by cyclic permutation; the gradient at vertex zero is their negative sum. Multiplying by κ(V−V₀)/V₀ supplies the energy gradient, and force is its negative. The implementation's derivatives are checked against central differences at perturbed geometries. Those numerical checks support the code; the following exact algebra establishes only the stated gradient-partition contract.


**Checked claim element-resultant:** A tetrahedral volume-force contribution has zero resultant when its four coordinate gradients sum to zero.

**Assumptions:** Exact integer coordinate gradients g1,g2,g3, g0 = −(g1+g2+g3), and a common scalar force factor.

```lean
theorem element_gradient_resultant (g1 g2 g3 scale : Int) :
    scale * (-(g1 + g2 + g3)) + scale * g1 + scale * g2 + scale * g3 = 0
```

**Limits:** The analytic volume derivative, JavaScript implementation, torque, attachments and contact require separate checks. This is the partition algebra used in spatial.mjs.

Declaration: `Kenoma.element_gradient_resultant`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


The bone proxies are capsules: the upper radius is 21 mm, the forearm radius 19 mm, with 270 and 350 mm centerline lengths. For each sample, project onto the bounded centerline segment and subtract the radius from the distance. Positive g is clearance; negative g is penetration. A contacting sample receives **f** = −k g **n**, pointing out of the capsule. Separation gives zero force. The penalty is compliant, so a small negative gap is expected at finite force.

Boundary vertices and tetrahedron centroids are sampled. A centroid is the average of its four vertices, so its contact force is distributed with weights 1/4 to all four. This uses the transpose of the centroid-motion map. The exact numerator identity below explains why that transfer preserves virtual power coordinate by coordinate. It does not certify the distance calculation or floating-point arithmetic.


**Checked claim centroid-transfer:** Equal centroid barycentric weights transfer nodal power with the transpose of the point-motion map.

**Assumptions:** Exact integer scalar force and four velocity coordinates. Both sides are numerators with a shared division by four in physical interpretation.

```lean
theorem centroid_contact_power (force v0 v1 v2 v3 : Int) :
    force * (v0 + v1 + v2 + v3) =
      force * v0 + force * v1 + force * v2 + force * v3
```

**Limits:** No division or floating-point equality is proved. Applies coordinatewise to the fixed centroid sample; no nonlinear moving embedding or biological claim.

Declaration: `Kenoma.centroid_contact_power`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


The reported normal-force sum is the sum of the nonnegative magnitudes of these sample forces. It is not their vector resultant, a cartilage joint reaction, or pressure. There is no contact-area stress integration; the display deliberately reports pressure as absent. Fixed-node reactions are recovered from the full gradient. Their resultant plus the external sampled contact forces equals the negative unresolved free-node gradient sum. This is tested explicitly and shown as a force-balance defect.

These samples are not a complete surface collision test. A triangle can intersect between vertices, or a moving surface can pass through a bone between poses, without a sampled negative gap. No continuous collision detection, self-contact or intersection-free guarantee is claimed. Contact-off removes the penalty and exposes geometric penetration; it does not make a zero-force overlapping state into valid contact.

## A deterministic finite quasistatic solve

At each requested q,a pair, initialize from a smooth authored pose field R_z(w(X)q)X, where w rises linearly from zero at y = 120 mm to one at y = −120 mm. The ends match their rigid transforms. The mechanical solve then minimizes the sum of the listed energies over free coordinates, using limited-memory BFGS with eight stored update pairs and an Armijo backtracking line search. Failed or poorly conditioned curvature updates are discarded; a non-descent search direction resets to scaled negative gradient.

Sufficient-decrease backtracking has a classical gradient-method basis; its convergence conclusions require stated regularity assumptions. Our bounded nonconvex solve does not inherit those guarantees. [Armijo, 1966, original paper](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-s.pdf)

An accepted trial must have minimum tetrahedral J = V/V₀ greater than 0.01 and satisfy sufficient objective decrease. This is an implemented guard, not a proof of mesh injectivity, global convergence or feasible contact. It can reject a search step even while the residual remains large. The solver exposes its iteration cap, energy-evaluation count, maximum free force and L2 residual; an unconverged iterate stays labeled approximate. A residual criterion of 2 × 10⁻⁵ N per free coordinate is used for local stopping.


**Checked claim armijo-decrease:** An accepted sufficient-decrease step cannot increase the exact scaled objective.

**Assumptions:** Exact integer old/new energy, nonnegative scaled step coefficient, nonpositive directional slope and the stated Armijo acceptance inequality.

```lean
theorem accepted_energy_nonincrease (oldE newE coefficient slope : Int)
    (hc : 0 ≤ coefficient) (hs : slope ≤ 0)
    (accept : newE ≤ oldE + coefficient * slope) : newE ≤ oldE
```

**Limits:** Does not prove gradients, direction generation, line-search termination, global convergence, float bounds or biological validity. The spatial solver tests its actual accepted energies separately.

Declaration: `Kenoma.accepted_energy_nonincrease`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd. [Full checked source](proofs/Mechanics.lean); [receipt](proof-status.json).


Floating-point evaluation can change the line-search path across JavaScript runtimes, so exact cross-browser identity of the finite iterate is not promised. Reset remains deterministic in the same runtime.

The original worked compression fixture holds q = 90°, a = 0.6. These values are generated by executing the same module that the browser imports. They measure iteration sensitivity on one fixed grid and model; they are not continuum mesh convergence or a calibrated compression experiment.

| Iteration cap | Min J | Mean J | Sampled penetration (mm) | Max free force (N) | Normal-force sum (N) | Elastic/contact energy (J) |
|--:|--:|--:|--:|--:|--:|--:|
| 80 | 0.641972 | 0.952176 | 5.885464 | 2.646656 | 18.061333 | 0.434460 |
| 160 | 0.564813 | 0.949176 | 2.275902 | 0.363654 | 10.866792 | 0.399996 |
| 320 | 0.654225 | 0.950691 | 0.457096 | 0.443769 | 6.907939 | 0.377119 |
| 640 | 0.736345 | 0.960015 | 0.028284 | 0.014492 | 0.735085 | 0.318567 |


At 640 iterations, minimum J is 0.736345 and total mean J is 0.960015. Tissue flattens and moves laterally while total volume changes by 3.998%. Maximum sampled penetration is 0.028284 mm, versus 9.750000 mm for skinning. Maximum free-force defect is 0.014492 N. These values are generated in v24.19.0; they are not cross-runtime bit-identity claims. A small sampled gap does not prove the material law correct, and a residual alone does not establish a contact-free surface.

At the straight pose, activation 0.6 shortens the measured upper centreline span from 180 mm to about 170.77 mm while mean J remains about 0.9993. Releasing activation returns the quasistatic solution toward its passive state. The browser's prescribed-hold mode lets a reader isolate that deformation from bone motion. During the default lift/release pulse, the arm reaches roughly 67° by 0.6 s and subsequently lowers below its starting angle by 0.9 s; its spatial active span lengthens again. Activation persists after excitation becomes zero; the line fibre and spatial span can subsequently stretch as the load lowers the arm. A contracting actuator can carry tensile force while lengthening; “active” does not mean every fibre is getting shorter at every instant.

## The naive skinning view is evaluated once at the same pose

The right-hand baseline uses exactly the same bind vertices, skin topology, joint pivot, bones and q as the mechanical side:

$$\mathbf x_{LBS}=(1-w)\mathbf X+w\mathbf R_z(q)\mathbf X.$$ 

There is no added rest-relative displacement and no second skeletal transform. Because w varies with position, the full-arm J is measured from the transformed tetrahedra rather than taken from the uniform-blend cos²(q/2) formula. The 90° fixture has minimum J ≈ 0.171 and mean J ≈ 0.718. These are actual values for this schematic strip, not human elbow volume loss. Both meshes retain the same camera and SI display scale; the skinning baseline has no force or pressure model.

The interactive pose domain is 0–100°. This keeps the mechanical initialization in its checked teaching range; it is not an anatomical range-of-motion limit. Outside it, the underlying strip and pose field can invert cells or trap the local solver near its J guard. The rigid hinge pauses at its last admissible pose rather than inventing an impact response.

## Read the controls as experiments

Start the 3D scene, then use **Lift / release pulse** for the force-driven 5 kg dumbbell example. The fixed physics step is independent of wall-clock playback; the spatial solve can slow playback. **Release excitation** changes only the input at the current time, and the exported current row is refreshed immediately. Activation and pose advance on the next step. **Reset** reconstructs the same state and deterministic shape solve.

Use **90° compression fixture** to compare the mechanical mesh with the same-pose baseline. Disable contact and observe the increase in sampled penetration. Lower volume stiffness and inspect volume loss. Turn off skin/fascia to see which shape restrictions those discrete layers contribute. Disable the spatial shortening law to isolate pose/contact from activation; the line actuator still owns the hinge force. Increase the iteration cap and compare energy and residual together, since a low residual does not identify a globally unique minimum.

Parameter edits pause playback and retain current activation, time, pose, velocity and accumulated hinge work/dissipation while recomputing tissue from the deterministic initialization. An angle edit explicitly sets that pose with zero velocity and clears a domain halt; entering prescribed hold stops motion at the current pose. Each non-excitation edit begins a new exported trace segment at the current step/time. Its accumulated hinge work includes earlier steps; spatial energies remain instantaneous. Only **Reset**, **Lift / release pulse**, and **90° compression fixture** deliberately initialize a new physical state.

`spatial-experiment.json` retains the meshes, paired coordinates, contact samples, iteration study, activation comparison, ablations and lift/release sample states. `web/spatial.mjs` is the source of those numbers. The chapter is an original reproducible computational teaching experiment. Published muscle-compression and skin-identification studies motivate which outputs to ask for; their physiological results are not being copied onto this schematic model. [Ryan et al., original contracting-muscle compression study](#source-compression), [Pai et al., original soft-tissue contact identification study](https://www.cs.ubc.ca/research/HumanTouch/HumanTouchSIGGRAPH2018.pdf)

A fully coupled medical arm would require the spatial reactions to drive the bones through a consistent interface, an identified anisotropic active law, force/velocity/pennation and rate effects where needed, tendon slack and architecture, sliding layers, robust surface contact and uncertainty analysis. Those are extensions of this declared educational model. They are not a prerequisite for understanding and checking the present one-way comparison, and they are not added to Kenoma's production MVP by this book.

# Coupled tissue mechanics: a checked intermediate {#coupled-tissue-mechanics}

The preceding strip experiment separates spatial deformation from the line actuator that turns its hinge. That separation is useful for studying skinning, but it does not meet the requested anatomical lifting capstone. This chapter introduces a replacement force path: deforming tissue pulls distributed tendons, those tendons pull an actual rotating attachment map, and the same objective determines tissue coordinates and joint motion together. The first working experiment is a rectangular engineering fixture. Its results do not transfer to a human arm by renaming its parts.

[Open the resettable coupled 3D fixture](coupled-fixture/index.html). Effort and weight mass are its two primary controls. Numerical state, residuals, activation, fibre stretch, tendon torque and work defect remain readable without starting WebGL. The solver runs in a worker; fixed steps advance only after convergence. Skin is absent while the whole-arm tissue envelope is under review.

## Source anatomy and the interior axis

The separate [source inspection](anatomy-inspection/index.html) retains the actual shared-coordinate BodyParts3D humerus, radius, ulna and seven individual muscle surfaces. Derived belly cuts, fibre guides and mechanical patches remain authored estimates. Each patch records original triangle identifiers, outward normals, area weights and an edge-connected region. Broad humeral origins are surface bands rather than small terminal picks. The radial-tuberosity patch is on the medial side; the brachioradialis patch is on the lateral distal radius. These selections still require anatomical review. Original dataset notices remain with the data, alongside the current [official BodyParts3D licence](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html).

![Actual three-bone and seven-muscle BodyParts3D source assembly in its shared atlas bind coordinates; cyan marks the authored interior axis. Muscles have distinct source surfaces; there is no skin.](assets/atlas-assembly-bind.png)

BodyParts3D, © The Database Center for Life Science, current CC BY 4.0; original OBJ notices retained. This source view is not a deformed mechanical solution or an accepted anatomical rig.

The previous surface-pick hinge opened the articulation. The replacement fits an interior axis to connected articular source regions, then evaluates a finite grid of nearby centres against bone-surface crossings. Its centre in atlas metres is (-0.211000, -0.070235, 1.044410), direction (-0.954743, 0.103123, 0.278982), and atlas bind angle 16.2783°. No individual part is independently recentered or registered. Twenty-five tested poses, every 5° from 0° through 120°, have no transverse humerus/ulna or humerus/radius triangle crossing. This is finite sampled evidence, not continuous collision certification or a measured functional axis.

At 90°, the sampled ulnar articular face-centroid distances to the continuous humeral triangle surface have area-weighted median 4.082 mm and 95th percentile 7.923 mm. The nearest tested source vertex is 0.717 mm away. These are distances without cartilage; they are not universal medical tolerances, global triangle-pair minima, or an assertion of anatomical acceptance. Full records are in [apposition-results.json](data/anatomical-arm-v1/audit/apposition-results.json) and [interior-axis-fit.json](data/anatomical-arm-v1/audit/interior-axis-fit.json).

The final arm still needs an explicit shared biceps distal apparatus, tendon/aponeurosis transfer, distributed origins, corrected remesh/bone clearances and tissue contact. A whole belly cap will not be anchored to one patch centroid. Published architecture research provides a reason to model aponeuroses and curved fibres explicitly; it does not identify our atlas-derived guides as measured fascicles. [Blemker, Pinsky and Delp, original 3D biceps study](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf)

The reference-only [remesh discrepancy audit](data/anatomical-arm-v1/audit/remesh-discrepancy.json) localizes defects rather than treating closed positive cells as anatomical accuracy. For brachialis, 53 of 1,008 positive quadrature samples lie outside the source: 5.258% by point count but 2.029% by reference-volume weight. Maximum sampled outside depth is 1.434 mm. Forty-six samples lie inside a bone, reaching 1.908 mm depth. The medial triceps has 30 bone-intruding samples, reaching 2.473 mm. Boundary triangle tests also detect crossings that quadrature containment misses. These are uncorrected defects and prevent acceptance of the current bellies for the anatomical arm. Longitudinal-bin and original-triangle records support correction near attachments and bone clearances; no tolerance is relaxed to hide them.

The audit also finds crossings in the original full atlas muscle surfaces. Of the 46 bone-intruding brachialis samples, 27 lie outside the original muscle surface and 19 remain inside it. Thus both remesh approximation and source assembly clearance need attention. Full source surfaces and trimmed belly surfaces cover different regions, so their crossing counts cannot be subtracted as an accuracy norm. A licensed anatomical atlas is valuable evidence; it is not automatically a mechanically admissible CAD assembly.

## One energy supplies each tissue force

At each positive quadrature point define deformation gradient $F$, volume ratio $J=\det F>0$, normalized reference fibre direction $f_0$, stretch $\lambda=\lVert Ff_0\rVert$, current direction $n=Ff_0/\lambda$, and $e=\max(\lambda-1,0)$. The authored passive density is

$$W_{pas}=\frac{\mu}{2}(J^{-2/3}\operatorname{tr}(F^T F)-3)+\frac K2(\ln J)^2+\frac{k_f}{b^2}[\exp(be)-1-be].$$

At fixed activation use exactly one active solve potential,

$$U_{act}=a\sigma_0\int_1^\lambda f_L(s)\,ds,\qquad f_L(s)=\max(0,1-((s-1)/0.5)^2)^2.$$

This active potential is a device for differentiating force during a fixed-activation solve. It is not passive storage or metabolic energy. With $I_1=\operatorname{tr}(F^TF)$, the first Piola stress is

$$P=\mu J^{-2/3}(F-\tfrac13 I_1F^{-T})+K\ln J\,F^{-T}+[\tfrac{k_f}{b}(\exp(be)-1)+a\sigma_0f_L(\lambda)]\,n\otimes f_0.$$

The Cauchy stress is $PF^T/J$. No second preferred-length force or independent scalar lifting muscle is added. The fixture uses $\mu=1$ kPa, $K=1$ MPa, $k_f=20$ kPa, $b=6$, optimal reference stretch one and placeholder $\sigma_0=0.3$ MPa. These are engineering assumptions, not measured human properties. Force-velocity is fixed to one; activation time constants 0.04 s on and 0.06 s off are authored. Dynamic shortening speed is not a physiological prediction.

Ten-node quadratic tetrahedra interpolate displacement. Four-point positive quadrature is the live fixture choice; 32-point positive subdivided quadrature is the reference profile. The exact shape-weight numerator identity below explains rational partition of unity under a common denominator. Irrational quadrature locations and floating-point evaluation remain separate numerical checks.


**Checked claim quadratic-partition:** Four corner and six midside shape-weight numerators sum to the squared common barycentric denominator.

**Assumptions:** Exact integer barycentric numerators sum to d; rational interpretation requires d>0. Corner numerators are 2*l_i^2-d*l_i and edge numerators 4*l_i*l_j.

```lean
theorem quadratic_partition_numerator (l0 l1 l2 l3 d : Int)
    (normalized : l0+l1+l2+l3=d) :
    2*(l0*l0+l1*l1+l2*l2+l3*l3) - d*(l0+l1+l2+l3) +
      4*(l0*l1+l0*l2+l0*l3+l1*l2+l1*l3+l2*l3) = d*d
```

**Limits:** No claim about irrational quadrature values, geometry, gradients, floating-point evaluation or anatomical fidelity is established.

Declaration: `Kenoma.Coupled.quadratic_partition_numerator`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).


## Distributed tendon traction and its torque

For each branch, $\epsilon=l/L_0-1$. Nominal stress is zero in compression, $E\epsilon^2/(2\epsilon_{toe})$ in the positive toe region, and $E(\epsilon-\epsilon_{toe}/2)$ above it. Force is $A_0$ times nominal stress. Integrating gives the positive toe storage

$$U_{toe}=A_0L_0\frac{E\epsilon^3}{6\epsilon_{toe}}.$$

The fixture has nine cap nodes receiving positive geometric area weights, total tendon reference area 30 mm², initial branch length 50 mm, $E=50$ MPa and $\epsilon_{toe}=0.03$. All are authored. Tendons transmit tension only. They are a distributed axial network, not a full transverse aponeurosis solid.


**Checked claim tendon-toe-storage:** The tensile toe-branch stored-energy numerator is nonnegative for nonnegative reference area, length, Young modulus and strain.

**Assumptions:** Exact nonnegative integer numerator factors in compatible scales. Physical interpretation additionally requires positive toe denominator.

```lean
theorem tendon_toe_energy_numerator_nonnegative (area length young strain : Int)
    (ha : 0 ≤ area) (hl : 0 ≤ length) (hy : 0 ≤ young) (he : 0 ≤ strain) :
    0 ≤ area*length*young*strain*strain*strain
```

**Limits:** No continuity, constitutive derivative, other branch, material calibration or floating-point accuracy is proved.

Declaration: `Kenoma.Coupled.tendon_toe_energy_numerator_nonnegative`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).


A rotating bone attachment is $p(q)=O+R(q-q_{ref})(X-O)$, with derivative $B=\hat e\times(p-O)$. If $f$ is force on that bone, its generalized torque is $Q=B^Tf$. Opposite node and bone forces arise from differentiating the very same branch energy. Independent differences test both the energy gradient and the rigid derivative.


**Checked claim attachment-transpose-power:** The exact one-DOF attachment transpose preserves three-coordinate power.

**Assumptions:** Integer B, force and angular velocity in compatible positive scales; the velocity mapping B*omega is assumed.

```lean
theorem attachment_transpose_power (b0 b1 b2 f0 f1 f2 omega : Int) :
    dot3 b0 b1 b2 f0 f1 f2 * omega =
      dot3 f0 f1 f2 (b0*omega) (b1*omega) (b2*omega)
```

**Limits:** Does not prove the geometric derivative, floating-point equality, solver convergence, anatomical axis, material response or biology.

Declaration: `Kenoma.Anatomical.attachment_transpose_power`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 9c733f15d8b9016646bc024764595bb750041dd84cb0db4c0f0d896d4be423c8. [Full checked source](proofs/AnatomicalTransfer.lean); [receipt](transfer-proof-status.json).



**Checked claim paired-attachment-work:** Transferred equal-opposite attachment powers cancel the assumed potential-rate expression.

**Assumptions:** Integer coordinate quantities in compatible positive scales; potential-rate expression and force pairing are supplied, not derived.

```lean
theorem paired_attachment_work (b0 b1 b2 f0 f1 f2 v0 v1 v2 omega : Int) :
    dot3 (-f0) (-f1) (-f2) v0 v1 v2 +
      dot3 b0 b1 b2 f0 f1 f2 * omega +
      dot3 f0 f1 f2 (v0-b0*omega) (v1-b1*omega) (v2-b2*omega) = 0
```

**Limits:** No real calculus, rounding bound, finite-element convergence, anatomy or biological validation is established.

Declaration: `Kenoma.Anatomical.paired_attachment_work`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 9c733f15d8b9016646bc024764595bb750041dd84cb0db4c0f0d896d4be423c8. [Full checked source](proofs/AnatomicalTransfer.lean); [receipt](transfer-proof-status.json).


## Joint and tissue are solved together

With tissue quasistatic, angular inertia $I$, fixed step $h$, old velocity $\omega_n$, and documented damping $D$, minimize over tissue positions $x$ and joint angle $q$:

$$\Phi(x,q)=\frac{I}{2h^2}(q-q_n-h\omega_n)^2+U_{pas}(x)+U_{act}(x,a_{next})+U_{tendon}(x,q)+V_g(q)+\frac{D}{2h}(q-q_n)^2.$$

The fixture uses downward-positive world $z$, so $V_g=-g(mz_{grip}+m_{segment}z_{COM})$. Its authored segment mass is 0.1 kg, segment inertia 0.0025 kg m² and damping 0.002 N m s. Dumbbell inertia is $m\lVert B_{grip}\rVert^2$. Tissue mass is not counted again as nodal inertia or local sag. The angle domain [-0.2, 2.1] rad is a synthetic diagnostic domain; a rejected solve preserves the previous state rather than clamping the angle into a hidden support force.

Stationarity in $q$, with $\omega_{n+1}=(q-q_n)/h$, yields

$$I\frac{\omega_{n+1}-\omega_n}{h}=Q_{tendon}+Q_g-D\omega_{n+1}.$$


**Checked claim implicit-impulse:** The assumed implicit momentum equation has the implemented tissue/gravity/damping torque signs.

**Assumptions:** Exact integer quantities in compatible common scales; the stationarity/momentum equation is supplied.

```lean
theorem impulse_balance (inertia oldVelocity newVelocity h tissue gravity damping : Int)
    (stationary : inertia * (newVelocity-oldVelocity) =
      h * (tissue+gravity-damping*newVelocity)) :
    inertia * (newVelocity-oldVelocity) + h*damping*newVelocity =
      h*tissue+h*gravity
```

**Limits:** Does not derive the gradient, verify Newton convergence, or refine floating-point code.

Declaration: `Kenoma.Coupled.impulse_balance`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).


Newton steps use the analytic directional derivative of the unchanged Piola stress and branch Hessian. Truncated conjugate gradients use a reference-elasticity Cholesky preconditioner for this small fixture. Indefinite search systems receive explicitly recorded solver regularization; this does not add a material energy. Determinant-invalid trials are rejected. Armijo sufficient decrease chooses accepted search steps, without promising global convergence of this nonconvex problem. [Armijo, original paper](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-s.pdf)

The stopping target is maximum normalized-coordinate gradient $10^{-6}$ J; tissue displacements are normalized by reference block length and angle is in radians. The receipt separately reports the maximum free nodal vector norm in N and the joint residual in N m. Objective-call counts include rejected determinant trials; post-solve diagnostic calls are separate. A finite linear solve can stop short of its requested tolerance, but the nonlinear residual must pass before time and activation advance.

## Lift, release and work that remains unresolved

![Computed angle and activation for the actual coupled P2 fixture; effort drops at 0.28 seconds and the angle subsequently falls.](assets/coupled-pulse.svg)

The first reproducible pulse starts at $q=0$, $a=0$, 0.5 kg and $h=0.04$ s. Effort is 0.25 for seven steps, then zero for five steps. Tissue-generated tendon torque raises the lever; after release activation decays and the lever lowers. The authored route changes its moment-arm sign at some larger angles. That behaviour is part of this synthetic fixture, not an accepted human attachment path. [Full pulse, state coordinates and step refinement](data/anatomical-arm-v1/audit/coupling-results.json)

![Native rendering after seven loaded steps: coral is the actual P2 tissue boundary, gold shows nine distributed tendons, blue is the hinged rigid lever and violet is the point mass.](assets/fixture-loaded.png)

![The same coupled engineering fixture after five released-effort steps; activation and angle fall while the tissue coordinates remain part of the joint solve.](assets/fixture-released.png)

Original schematic fixture geometry, rendered at the actual solved coordinates. No skin, anatomical attachments or contact are represented in these two images.

For angular motion the exact identity is

$$I(\omega_{n+1}-\omega_n)\omega_{n+1}=\Delta(\tfrac12 I\omega^2)+\tfrac12 I(\omega_{n+1}-\omega_n)^2.$$


**Checked claim kinetic-increment:** Twice the joint kinetic increment plus twice its implicit kinetic defect equals twice the end-velocity inertial work.

**Assumptions:** Exact integer inertia and old/new angular velocities; positive common physical scales interpret numerator factors of two.

```lean
theorem kinetic_increment_identity (inertia oldVelocity newVelocity : Int) :
    inertia*(newVelocity*newVelocity-oldVelocity*oldVelocity) +
      inertia*(newVelocity-oldVelocity)*(newVelocity-oldVelocity) =
      2*(inertia*(newVelocity-oldVelocity)*newVelocity)
```

**Limits:** Only angular kinetic algebra; no tissue potential, metabolic work or whole-system conservation claim.

Declaration: `Kenoma.Coupled.kinetic_increment_identity`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).


Combining it with the assumed angular stationarity equation gives the angular endpoint-work identity. It does not supply conservation of the nonlinear tissue potentials.


**Checked claim implicit-angular-work:** The assumed implicit momentum equation gives the joint angular work balance including damping and implicit kinetic defect.

**Assumptions:** Exact integer quantities in compatible scales; the implemented angular stationarity relation is supplied.

```lean
theorem implicit_kinetic_work_balance
    (inertia oldVelocity newVelocity h tissue gravity damping : Int)
    (stationary : inertia*(newVelocity-oldVelocity) =
      h*(tissue+gravity-damping*newVelocity)) :
    inertia*(newVelocity*newVelocity-oldVelocity*oldVelocity) +
      inertia*(newVelocity-oldVelocity)*(newVelocity-oldVelocity) =
      2*h*tissue*newVelocity + 2*h*gravity*newVelocity -
      2*h*damping*newVelocity*newVelocity
```

**Limits:** Does not prove full tissue/joint energy conservation. Nonlinear endpoint-work defects are measured separately.

Declaration: `Kenoma.Coupled.implicit_kinetic_work_balance`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).



**Checked claim implicit-dissipation:** The angular implicit kinetic and damping defect numerator is nonnegative under nonnegative inertia, step and damping.

**Assumptions:** Integer inertia, h and damping are nonnegative; velocities arbitrary; positive common scales and factors of two.

```lean
theorem implicit_dissipation_numerator_nonnegative
    (inertia h damping oldVelocity newVelocity : Int)
    (hi : 0 ≤ inertia) (hh : 0 ≤ h) (hd : 0 ≤ damping) :
    0 ≤ inertia*((newVelocity-oldVelocity)*(newVelocity-oldVelocity)) +
      2*h*damping*(newVelocity*newVelocity)
```

**Limits:** No total-energy monotonicity under activation, nonlinear potentials, external mass changes or solver errors follows.

Declaration: `Kenoma.Coupled.implicit_dissipation_numerator_nonnegative`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).


The implementation computes active mechanical work as minus the fixed-$a_{next}$ active-potential change between old and new geometry. It separately records passive tissue, tendon, gravity and angular kinetic energy, damping work, angular implicit dissipation, and their nonlinear endpoint-work defect. Changing activation supplies an external input; an active potential is never booked as passive storage. Runs at 0.04, 0.02 and 0.01 s retain the observed work defects. An exact proof of the angular algebra does not erase those defects.

| h (s) | Peak q (°) | Final q (°) | Sum nonlinear work defect (J) | Max momentum residual (N m) |
|--:|--:|--:|--:|--:|
| 0.04 | 38.5817 | 22.1126 | 1.131333 | 1.49e-07 |
| 0.02 | 44.2745 | 25.3993 | 0.697006 | 1.46e-07 |
| 0.01 | 48.1601 | 28.2517 | 0.387944 | 2.94e-07 |


The angular trajectory still changes materially with step refinement. The decreasing work defect is an observed trend over these runs, not a demonstrated asymptotic rate or convergence certificate.

Changing mass preserves pose, velocity, tissue, activation and elapsed time. At that instant it adds an external energy event

$$\Delta E_{mass}=\Delta m(\tfrac12\lVert B_{grip}\rVert^2\omega^2-gz_{grip}).$$


**Checked claim mass-event-work:** At fixed pose and velocity, changing point-mass inertia and downward-positive gravitational potential gives the recorded external mass-event work numerator.

**Assumptions:** Exact integer fixed pose/velocity, delta mass and squared grip radius; I changes by deltaMass*radiusSquared; fixture z is downward-positive.

```lean
theorem mass_event_work_numerator (oldInertia deltaMass radiusSquared velocity g z : Int) :
    (oldInertia+deltaMass*radiusSquared)*velocity*velocity -
      oldInertia*velocity*velocity - 2*g*z*deltaMass =
      deltaMass*(radiusSquared*velocity*velocity-2*g*z)
```

**Limits:** State preservation, real geometry, signs for other world conventions and browser arithmetic need independent checks.

Declaration: `Kenoma.Coupled.mass_event_work_numerator`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab. [Full checked source](proofs/CoupledMechanics.lean); [receipt](coupled-proof-status.json).


Matched profiles retain the same passive/active law, $K$, 32-point quadrature and nonlinear residual target for L-BFGS and Newton at two mesh resolutions. The measured timing and final-length differences are evidence for this fixture only. Dense Cholesky does not establish that seven atlas bellies will run at interactive speed. Remaining anatomy, contact, work-refinement and mobile checks must be resolved before this intermediate can replace the requested anatomical capstone.

| Mesh | Solver | Objective calls | HVP calls | Time (s) | Loaded length (mm) | Max nodal force (N) |
|:--|:--|--:|--:|--:|--:|--:|
| 6 P2 tets / 27 nodes | lbfgs | 698 | 0 | 2.099 | 100.349055 | 6.88e-06 |
| 6 P2 tets / 27 nodes | newton | 13 | 222 | 0.526 | 100.349050 | 6.63e-07 |
| 48 P2 tets / 125 nodes | lbfgs | 1439 | 0 | 38.431 | 99.127531 | 8.11e-06 |
| 48 P2 tets / 125 nodes | newton | 12 | 341 | 4.177 | 99.127568 | 5.2e-06 |


These are one local run per case. Timing is illustrative; final state and residual are the comparison contract. HVP means analytic Hessian-vector product. Post-solve reaction diagnostics are outside the objective-call counter.

# Build an anatomical apparatus that can fail a check {#anatomical-apparatus}

The synthetic block in the previous chapter isolates coupling. The anatomical candidate instead connects **seven separate atlas-derived muscle volumes**, the humerus, radius and ulna, and two shared distal apparatuses. Its architecture is authored from source surfaces. It is not a measured tendon or fascicle segmentation, a subject-specific arm, or a clinically validated model.

The candidate keeps the source bones in their original shared coordinates. It repairs local intrusions of the derived belly reference volumes by recorded transverse ring translations, then reconstructs every quadratic midside node. The largest correction is 7.4132 mm in the medial triceps. Prism shape and reference volume are preserved to the reported numerical tolerance. The repair audit checks positive cell orientation, positive 32-point volume quadrature and finite boundary crossings. This geometric repair is separate from a constitutive law or a solved contact response.

[Inspect the complete reference-repair receipt](data/anatomical-arm-v1/audit/reference-repair.json). The original atlas and original remesh remain in the package, so a reader can reconstruct the before-and-after result.

## From a volume to a distributed attachment

Each head has 63 Galerkin displacement coordinates: seven longitudinal hats multiplied by a constant and two transverse affine features, in three displacement directions. Those coordinates act on the quadratic tetrahedron nodes and on 32 positive quadrature points per tetrahedron. This retains a volumetric energy and non-affine deformation while making the browser experiment smaller. A small reduced residual establishes equilibrium only in these 63 modes; it does not establish full nodal FEM convergence.

Both biceps heads meet the **same nine free distal guide coordinates**. Both contribute force to a common three-node sheet, which also receives the common distal tendon force from the radial-tuberosity face samples. All three triceps heads similarly meet one common apparatus ending on the olecranon patch. The weak transverse matrix and tensile fan laws are explicit approximations. Common distal branch area totals 20% of its candidate insertion patch. Each head fan totals 20% of the smaller of its cap area and that already scaled common area divided by head count; these fractions are authored, not measured tendon areas. They do not turn one free triangle into a resolved anatomical aponeurosis solid.

Within the biceps volumes, authored proximal-posterior and distal-anterior strips transmit axial force through embedded barycentric points. Their thickness, inset, transverse matrix and tensile properties are recorded engineering choices. The architectural motivation is the primary three-dimensional muscle study by [Blemker, Pinsky and Delp (2005)](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf); the present geometry and material law are not a reproduction of that study.

Broad humeral origins use individual source-patch faces and nearest points on the associated belly boundary. The previously shared medial/lateral triceps origin faces have exclusive ownership in the candidate configuration. This partition is an authored septum surrogate, not a measured anatomical border. The estimated proximal fans also have a weak connective-matrix boundary, using the recorded 1 kPa matrix scale, an authored 1 mm local interface thickness and a finite rest offset. This boundary compliance is separate from the routed tendon length. This authored restraint supports matrix compression when the separate axial tendon is slack; it is not a resolved tendon matrix or a measured attachment. Estimated scapular origins retain a 15 mm uncertainty radius and remain labelled estimates. They are not measured coracoid, supraglenoid or infraglenoid landmarks.


**Checked claim shared-guide-balance:** A supplied zero resultant at one shared biceps guide component makes the common distal force equal the negative sum of the two head, matrix and contact contributions.

**Assumptions:** Exact signed integer force-component numerators in a compatible scale; interpolated headA, headB, distal, matrix and contact contributions are supplied; their equilibrium is assumed.

```lean
theorem shared_guide_force_balance
    (headA headB distal matrix contact : Int)
    (equilibrium : headA+headB+distal+matrix+contact=0) :
    distal = -(headA+headB+matrix+contact)
```

**Limits:** Does not derive interpolation/geometry, verify the floating-point residual, prove Newton convergence or validate an anatomical aponeurosis.

Declaration: `Kenoma.Arm.shared_guide_force_balance`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 843f04f8e8f5c81a902d6816f0136726d006be6574aff5245360b8c2006ef025. [Full checked source](proofs/AnatomicalArm.lean); [receipt](arm-proof-status.json).


## A tendon path has one total length

A straight branch may cut through cortex even when both ends are outside bone. The reference routing tool therefore checks every axial segment against the closed source bones and adds authored frictionless polyline guides where needed. It records any estimated-origin projection separately and rejects corrections outside the established uncertainty radius. The source bone surfaces are unchanged.

For path points $x_0,\ldots,x_n$, use one total length and one integrated tensile law:

$$L=\sum_{i=0}^{n-1}\|x_{i+1}-x_i\|,\qquad W_t=W_t(L;L_0,A_0),\qquad T=\frac{\partial W_t}{\partial L}.$$

Every leg carries the same $T$. A fixed guide carries a support reaction and has zero prescribed-motion work. A guide attached to a rotating forearm bone contributes its force through the exact point Jacobian to elbow torque. The objective gradient and Hessian include all legs and the second derivative of rotating attachment points. The code never substitutes an independent scalar muscle torque for these attachment forces.

The fixed guide topology is a substantial limitation: it does not simulate sliding tendon wrapping, friction, finite tendon radius or measured retinacula. Finite line-contact quadrature and the complete segment audit are separate checks. A later pose that cuts cortex fails the acceptance gate. Passing the reference path audit alone is insufficient for a dynamic lift.

## Force matching exposes a material limitation

The fixed-end matching experiment equilibrates 45 interior modes at full activation; both end rings remain fixed. It matches the independently sourced Arm26 model-reference actuator forces within $10^{-4}$ relative error. These are actuator-model targets, not measured forces of the atlas subject. The fresh recheck recomputes the forces with the current operators.

| Head | Model-reference force (N) | Fitted stress scale (MPa) | Minimum local $J$ | Global volume ratio |
|---|---:|---:|---:|---:|
| Brachialis | 987.26 | 3.59933 | 0.59490 | 1.04781 |
| Biceps short | 435.56 | 8.70839 | 0.63832 | 1.02382 |
| Biceps long | 624.30 | 20.37812 | 0.63460 | 1.02796 |

These fitted scales and large local volume losses **do not establish medically credible material properties**. A nearly preserved global volume can coexist with substantial local compression. The shear, bulk and passive-fibre laws were kept at their recorded teaching values; the matching routine did not silently raise the bulk modulus to hide this result. A coupled pose using these scales must report its local $J$, force residual and contact checks. The numerical target match is an educational stress test, not a biological validation.

[Fresh fixed-end recheck](data/anatomical-arm-v1/audit/modal-fixed-end-recheck.json) · [Full fitting history](data/anatomical-arm-v1/audit/modal-fixed-end-results.json).

## Joint dynamics, release and an external mass event

The atlas frame has **+Z superior**, so gravitational potential is $+mgz$. Segment mass and inertia come from the pinned Arm26 rigid-segment model; their mapping to the atlas grip direction is authored. Local tissue sag is omitted. Segment tissue mass is counted once in the rigid segment rather than added again as separate deformable-body mass.

For a step of length $h$, solve tissue, shared guides and the joint coordinate together in the incremental potential:

$$\Phi(x,q)=W_{\mathrm{body}}+W_{\mathrm{tendon}}+W_{\mathrm{interface}}+W_{\mathrm{contact}}+V_g(q)+\frac{I}{2h^2}(q-q_n-h\omega_n)^2+\frac{d}{2h}(q-q_n)^2+W_{\mathrm{stop}}(q).$$

The declared end-stop energy acts outside 0–120 degrees; it is not a hidden pose clamp. Activation follows an analytic first-order update with distinct authored activation and release time constants. Only an accepted nonlinear solve and accepted geometric audits commit the activation, pose and time. A failure retains the prior state.

An effort change preserves pose, velocity, tissue coordinates and activation until the next accepted step. A mass change preserves those quantities and records

$$\Delta E_{\mathrm{external}}=\Delta m\left(\tfrac12 r_\perp^2\omega^2+gz_{\mathrm{grip}}\right).$$

This is external handling work in the point-mass model. It is not metabolic muscle work or a complete model of a person exchanging a dumbbell.


**Checked claim upward-mass-event:** At unchanged pose and velocity, the point-mass inertia and upward-positive gravitational potential increments give the external mass-event energy numerator.

**Assumptions:** Exact integer quantities in compatible common scales; squared grip radius is fixed and inertia changes by deltaMass times that radius squared. Factors of two represent the kinetic denominator.

```lean
theorem upward_mass_event_work_numerator
    (oldInertia deltaMass radiusSquared velocity g z : Int) :
    (oldInertia+deltaMass*radiusSquared)*velocity*velocity -
      oldInertia*velocity*velocity + 2*g*z*deltaMass =
      deltaMass*(radiusSquared*velocity*velocity+2*g*z)
```

**Limits:** Does not establish browser state preservation, numerical equality, actual anatomical geometry or handling of a physical dumbbell.

Declaration: `Kenoma.Arm.upward_mass_event_work_numerator`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Quot.sound; source SHA-256: 843f04f8e8f5c81a902d6816f0136726d006be6574aff5245360b8c2006ef025. [Full checked source](proofs/AnatomicalArm.lean); [receipt](arm-proof-status.json).


The mechanical-work ledger reports active-potential work, passive/contact storage, gravity, joint kinetic energy, damping and the implicit kinetic defect separately. Its remaining defect includes **quasistatic tissue-relaxation loss and nonlinear joint sampling**. It must not be presented as pure floating-point error or exact conservation of a fully dynamic tissue system.

## Compare the same anatomy at the same pose

The naive comparison applies an authored longitudinal bone weight to the **same repaired reference nodes** at the **same joint angle**. Its deformation gradient is derived from that weight field and checked against independent quadratic interpolation. It reports local determinant and signed volume rather than merely showing a plausible surface. It supplies no muscle force, equilibrium or contact law. There is no separately modelled skin envelope in either view.

The reference rig also has a persistent source articulation limitation: the restricted radial-head/capitellum audit reports median gaps of about 5.80 mm at 0 degrees and 8.74 mm at 90 degrees. Those unsigned patch distances are not cartilage thickness or acceptable joint apposition. The source bones were not silently registered to close the gap. [Read the restricted patch-distance audit](data/anatomical-arm-v1/audit/radial-apposition-results.json).

## Historical accepted rest and rejected loading

[Open the anatomical apparatus viewer](anatomical-arm/index.html). It loads the accepted resting coordinates, recomputes the reduced force residual and audits the full boundary and routed axial paths. Three-dimensional rendering begins only when requested. Effort, mass, release, reset and trace export remain accessible through native controls and text readouts.

![Two copies of the same repaired reference anatomy at the same held elbow angle. Left: the equilibrated mechanical candidate, with gold axial tendon paths and teal shared guide scaffolds. Right: authored naive bone weights. Violet dumbbell glyphs are schematic point loads. No external skin is modelled.](assets/anatomical-arm-rest.png)

The original held rest has maximum free modal gradient **7.04 × 10⁻⁵ N**, zero audited transverse boundary crossings, zero routed axial-path violations and zero sampled body–bone or body–body penetration. Its minimum sampled body $J$ is approximately **0.99966**. The joint is held by an external support during this initialization; this is not a free loaded equilibrium. [Read the fresh rest recheck](data/anatomical-arm-v1/audit/arm-rest-recheck.json).

Before contact refinement, a 0.01 s step with effort 0.04 and a 0.5 kg point dumbbell reached the 120-iteration limit at **0.03408 N**, above the **0.0001 N** acceptance tolerance. A separate continuation attempt kept the original old state and step length fixed while increasing only the target effort. Its first quarter-load stage, effort 0.01, also stopped after 120 iterations, at **0.0003181 N**. A fresh independent evaluation reproduces both force residuals. It also finds 24 audited boundary-crossing pairs in the full-load candidate and 32 in the quarter-load candidate, with one axial tendon-path violation in each. Both numerical and geometric gates therefore reject these candidates. [Read the independent rejected-step recheck](data/anatomical-arm-v1/audit/arm-rejected-step-recheck.json). Intermediate candidates were never committed. These are observed solver and geometric failures, not evidence of a physical instability or a successful lift. [Inspect the loaded-step receipt](data/anatomical-arm-v1/audit/arm-trajectory-results.json) and [source-bound continuation result](data/anatomical-arm-v1/audit/activation-continuation-results.json).

## A small residual can miss a tendon crossing

An immutable earlier variant of the resting model converged to **9.17 × 10⁻⁵ N** and passed the body boundary checks. Yet one proximal long-biceps axial path entered and exited the source humerus through two distinct triangles. The interior interval along the path was **134.79 μm** and its midpoint lay **7.63 μm** inside the triangulated surface. All five material contact samples were outside; the nearest sample was about **1.893 mm** away.

This directly computed counterexample separates sampled contact from a full axial-segment audit. The interval is a path length inside the triangle mesh; it is **not cortical thickness**, a measured tendon shape or a clinical accuracy result. Its saved operator, geometry and routing inputs are immutable and hash checked. A fresh replay reproduces the converged force and rejected path. [Read the independent replay](data/anatomical-arm-v1/audit/rejected-rest-v1/replay.json).

The later weak proximal connective matrix and stronger reference routing clearance produce the accepted rest above. They remain authored changes with their own receipts; the older failure is preserved for comparison. The shared guide triangles themselves are interpolation scaffolds rather than resolved solids, so this candidate does not claim complete aponeurosis-solid contact.

## Resolve contact between material samples

A zero sampled penetration cannot overrule an intersecting triangle or axial segment. The two saved loading failures remain unchanged regression inputs: 24 brachialis/humerus crossing pairs and one common biceps tendon/ulna violation in each. The quarter-load candidate also has eight brachialis/short-biceps crossings, giving 32 total boundary-crossing pairs. The archived execution operators reproduce their original residuals. They are rejected coordinates, never accepted initial states.

The revised solver partitions each intersecting edge or axial leg at its source-surface entry and exit parameters. It queries each open interval midpoint and retains an interior point as a **material witness**. Muscle-side witnesses split the associated reference triangle; reciprocal bone-side witnesses split the bone triangle. Positive centroid and vertex quadrature weights preserve each original face's reference area. The same two-sided material cuts apply between two deforming muscle surfaces. A crossed tendon leg gains a material knot and positive trapezoidal side-area weights. Its one total-length tensile law, routing topology, insertion locations and rest length remain unchanged. Insertion endpoints remain exempt from the line penalty, while the full segment audit still checks every leg.

These partitions change only **between** nonlinear solves. A Newton gradient, Hessian and Armijo line search use one frozen material rule. Each candidate is audited again; a moved crossing generates another witness and another solve. Six refinement retries are allowed. Reaching the limit rejects the candidate. The force tolerance remains **0.0001 N**, the authored bone gap remains **0.15 mm**, and the full transverse surface and tendon-path gates remain mandatory. The muscle/muscle gap remains **0.30 mm**. No collision tolerance was widened. An extended fourth load increment also converged to **5.99 × 10⁻⁵ N** but had six brachialis/short-biceps crossings while every surface contact sample remained outside. The geometry gate rejected it. Its coordinates and operators remain a regression; the two-sided muscle witnesses now expose those crossings.


**Checked claim contact-area-partition:** Reference-area child shares preserve the parent area numerator when their sum equals the parent scale.

**Assumptions:** Exact integer compatible area/share scales; the geometric partition supplies a+b+c=scale. Positive child areas are checked numerically.

```lean
theorem contact_partition_area_numerator (area a b c scale : Int)
    (partition : a + b + c = scale) :
    area*a + area*b + area*c = area*scale
```

**Limits:** Does not prove the triangulation, positive floating-point weights, geometric clearance, continuous collision detection, Newton convergence or biological contact.

Declaration: `Kenoma.Arm.contact_partition_area_numerator`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext; source SHA-256: 843f04f8e8f5c81a902d6816f0136726d006be6574aff5245360b8c2006ef025. [Full checked source](proofs/AnatomicalArm.lean); [receipt](arm-proof-status.json).


A longer loaded state also exposed a corner in the body/body contact potential: two faces were equally close, and selecting just one normal could not supply balanced contact. The new outside-feature transition uses a **1 μm authored regularization width**, not a penetration tolerance. For unsigned feature distances $d_i$, compute

$$u=\min_{w_i\ge0,\;\sum_i w_i=1}\left[\sum_i w_i d_i+\frac{\varepsilon}{2}\left(\sum_i w_i^2-1\right)\right].$$

An isolated closest feature is unchanged. Near a tie, positive weights blend its gradients and include the derivative of the weights in the Hessian. Every triangle remains a distinct feature, including coincident shared-edge distances: merging features according to the current closest edge would change the simplex and introduce an energy jump. A saved cold-load edge transition tests independent energy differences across that change. The envelope satisfies $u\le d$, where $d$ is the exact unsigned minimum. The penalty gap is $u$ outside and $u-2d$ inside, so the regularized gap is never greater than the original signed gap. This strengthens contact; acceptance still queries the original signed distance and full triangles/segments. Inside-feature switches and continuous motion are not certified. The interrupted single-feature run and its loaded corner are retained in the audit package.


**Checked claim conservative-contact-gap:** A supplied lower unsigned distance envelope gives a gap no greater than the exact outside distance or the negative inside distance.

**Assumptions:** Exact integer distance numerators in compatible SI scales; the bound u<=d is supplied.

```lean
theorem conservative_contact_gap (distance envelope : Int)
    (bound : envelope <= distance) :
    envelope <= distance ∧ envelope - 2*distance <= -distance
```

**Limits:** Does not prove the numerical simplex solver, floating-point bounds, signed-distance queries, derivative correctness, Newton convergence or collision clearance.

Declaration: `Kenoma.Arm.conservative_contact_gap`. Lean 4.19.0; mathlib not used; bundled Std only; transitive axioms: propext, Classical.choice, Quot.sound; source SHA-256: 843f04f8e8f5c81a902d6816f0136726d006be6574aff5245360b8c2006ef025. [Full checked source](proofs/AnatomicalArm.lean); [receipt](arm-proof-status.json).


The exact integer claim checks the area-partition numerator given the partition shares. It does not prove the geometric cut, floating-point weights, solver convergence or collision clearance. Regression tests separately check positive child areas, area conservation, activation of both previously missed contact types, analytic derivatives and serialized rule replay. Rules are stored with accepted states. A rejected step restores the old rule as well as leaving pose, activation, velocity and time unchanged.

A changed quadrature rule can change stored penalty energy at the old coordinates. The step receipt therefore reports `referenceQuadratureUpdateJ` separately. That numerical model-change event is not active muscle work. The existing work defect still includes quasistatic tissue-relaxation loss and nonlinear joint sampling; a small impulse residual does not establish energy conservation.

## Independently replayed loaded lift and release

The [saved 0.5 kg experiment](data/anatomical-arm-v1/audit/contact-lift-release-results.json) prepares a held rest with the witnessed rule, repeats the original 0.01 s, effort 0.04 load, then takes four further 0.03 s loading increments and ten 0.03 s release increments. Effort becomes zero at 0.13 s; activation decays with the recorded release time constant. Archived failed and previously accepted coordinates supply nonlinear initial guesses only. The old accepted state still defines inertia and activation. The primary experiment allows 240 Newton iterations per frozen rule; saved cold-start failures remain rejected rather than establishing universal convergence.

The [independent replay](data/anatomical-arm-v1/audit/contact-lift-release-recheck.json) invokes no optimizer. It freshly evaluates every saved force residual, full triangle and axial-path audit, activation update, joint impulse and mechanical-work ledger. All **15 accepted steps** have zero audited transverse boundary crossings, zero tendon-path violations and zero sampled bone, muscle or tendon penetration. The largest step residual is **8.88 × 10⁻⁵ N**, below the unchanged **0.0001 N** gate.

| Recorded event | Accepted time (s) | Elbow flexion (degrees) | Angular velocity (rad/s) |
|---|---:|---:|---:|
| Held initialization | 0.00 | 16.2783 | 0.0000 |
| End of commanded loading | 0.13 | 23.5813 | 1.7610 |
| Release peak | 0.34 | 39.3253 | 0.0049 |
| Final released state | 0.43 | 33.5261 | −1.6610 |

![Replayed elbow angle, activation and effort, force residual against the original gate, and minimum sampled body determinant for the 0.5 kg loaded lift and release. The dotted line marks release of commanded effort; every recorded pose passes full finite surface and axial-path audits.](assets/anatomical-contact-trajectory.png)

The arm rises **7.3030 degrees** during commanded loading, continues upward while activation decays, and falls **5.7992 degrees** from its peak during release. Final activation is **0.0002591**. The original viewer cache also succeeds on the first loaded step without a supplied coordinate guess: **3.93 × 10⁻⁵ N**, zero audited crossings and axial-path violations, with its stored rule independently replayed. Its 198 total Newton iterations span three frozen contact rules; the 120-iteration budget applies separately to each rule. The replayed nonlinear work defect reaches **2.4340 J** in magnitude; it is reported rather than forced to vanish. These CPU solves are not real-time browser performance evidence.

The smallest sampled body $J$ over the loaded/released states is **0.73754**. That substantial local compression, the fitted stress scales and the source articulation gaps remain visible limitations. A passing reduced trajectory does not establish full nodal convergence, finite-radius tendon clearance, coplanar or continuous-motion collision safety, measured anatomy or medical validity. The authored naive comparison continues to use exactly the same repaired reference anatomy and joint pose; it is not an independent mechanical solution.

A [finer-release comparison](data/anatomical-arm-v1/audit/contact-fine-release-recheck.json) starts from the same accepted 0.16 s state and uses 0.01 s increments. It was deliberately interrupted after **22 accepted steps**, at 0.38 s, rather than completing the requested 27 steps. The accepted prefix reverses, but differs from the primary 0.03 s schedule by as much as **3.2884 degrees** at their matched times through 0.37 s. This is observed timestep sensitivity with adaptive material rules, not evidence of timestep convergence or an accuracy bound. Its exact base, executed source hashes and interrupted receipt are retained.


## Compression and integration sensitivity at the saved poses

A subsequent [source-bound compression audit](data/anatomical-arm-v1/audit/anatomical-compression-sensitivity.json) independently assembles the full P2 body potential and projects its nodal gradients into the existing Galerkin modes. The original 32-point result agrees within **1.30 × 10⁻¹¹ N** in projected body gradients. All seven heads at the held pose and all 15 accepted states are evaluated with 4/32 integration; five selected poses additionally use positive 256-point integration and element-corner determinant queries. Saved coordinates, activation, fitted stress scales and contact rules are unchanged.

At the most compressed loading state, **0.10 s**, the minimum $J$ is **0.73754** at the original 32 points, **0.72527** at 256 points and **0.71234** at element corners. The frozen total reduced residual with 256-point body integration is **0.14451 N**, exceeding the unchanged **0.0001 N** gate. All four selected dynamic states fail that gate under 256-point integration at their frozen coordinates; the held state passes. This exposes integration sensitivity. It neither accepts a new trajectory nor establishes quadrature or full nodal convergence; the original replay remains acceptance under its declared 32-point potential.

Halving/doubling the authored 1 MPa bulk modulus at the same most compressed coordinates gives residuals of **14.3162/28.6325 N**. Geometry and $J$ remain unchanged. These are unbalanced parameter perturbations, not calibrated materials or re-equilibrated compression predictions.

### Re-equilibrating one increment with denser body integration

A separate [256-point loading comparison](data/anatomical-arm-v1/audit/anatomical-dense-step-recheck.json) re-solves the 0.07–0.10 s increment with the exact original old state, effort, activation law and joint inertia. The original 32-point target is a starting guess. Body integration changes; the 460-dimensional Galerkin space, material parameters, Newton algorithm, contact law and acceptance thresholds do not. Geometric witnesses can update the contact rule between frozen solves.

The dense result passes fresh evaluation and independent full P2 body-gradient assembly: the total reduced residual is **0.00009006 N**, below **0.0001 N**, with zero transverse surface crossings, zero tendon-path violations and zero sampled contact penetrations. Its joint angle differs from the original target by **0.001299 degrees**; its largest reduced-coordinate change is **0.12457 mm**. These are observations for this increment, not accuracy bounds for the full lift/release.

Denser integration and re-equilibration leave substantial compression visible. The minimum sampled $J$ is **0.72548**, and the minimum corner $J$ is **0.71263**. In the short biceps head, about **1.715%** of the integrated reference volume has $J<0.9$, despite a global volume ratio of **0.99886**. Near-preservation of total volume therefore does not establish local incompressibility. The old state belongs to the original 32-point trajectory; this comparison is not a self-consistent 256-point trajectory or quadrature-convergence proof. The controlled bulk and displacement-space comparisons below address part of that follow-up. Full nodal, timestep, articulation and finite-geometry limitations remain open. The conditional exact proofs do not certify these floating-point samples.

### Diagnosing the local compression

The [localization receipt](data/anatomical-arm-v1/audit/anatomical-compression-localization.json) identifies the worst corner at short-biceps proximal node 98. About **1.602%** of the head's reference volume has sampled $J<0.9$ in the proximal sixth, despite that region's mean $J=1.01369$. For the unchanged constitutive law, the matrix has zero mean Cauchy stress, while

$$s_{\mathrm{volume}}=\frac{K\log J}{J},\qquad s_{\mathrm{active}}=\frac{a\sigma_0 f(\lambda)\lambda}{3J}.$$

The active potential uses full fibre stretch $\lambda=\lVert Ff_0\rVert$ and therefore contributes mean stress under dilation. At the worst corner, the bulk/active contributions are **−475.4/+71.1 kPa**; passive fibre stress is zero. This is a stress identity of the authored law, not measured tissue pressure or proof of local hydrostatic balance. The active term alone does not explain the compression. The original [Blemker et al. study](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) supplies an architecture-dependent continuum reference; its geometry, parameters and validation do not transfer to this fixture. [Ryan et al. (2020), discussion](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full) use 1 MPa in a different formulation and identify uncertainty in muscle volumetric constitutive behavior. A literature bulk value does not calibrate this authored envelope.

Four separately accepted dense loading increments supply the common old state for [half/double-bulk re-solves](data/anatomical-arm-v1/audit/anatomical-bulk-step-0.5-recheck.json). Both comparisons pass the original force and finite geometry gates. The minimum corner $J$ becomes **0.60941** at 0.5 MPa and **0.81657** at 2 MPa. Even the higher modulus leaves substantial local volume loss; these single changed-material increments are not calibrated trajectories.

An [additional 2048-point frozen check](data/anatomical-arm-v1/audit/anatomical-further-integration.json) gives residual **0.017385 N** at the accepted 256-point 0.10 s state, above **0.0001 N**. That state is rejected under the finer rule. [Selected nodal energy probes](data/anatomical-arm-v1/audit/anatomical-nodal-probe.json), including apparatus and contact energy, also give nonzero derivatives in directions orthogonal to the 63 retained tissue modes; the largest magnitude is about **1.984 N**, stable across two perturbation sizes. These probes expose missing stationary directions but do not assemble a full nodal residual. Further integration and a better resolved displacement field remain necessary before the whole tissue envelope can be called credible. No constitutive equation, proof contract or skin layer is changed by these diagnostics.

A [controlled enriched increment](data/anatomical-arm-v1/audit/anatomical-enriched-step-recheck.json) adds six short-biceps coordinates from two excluded proximal nodal shapes and retains the same dense old state, constitutive law and acceptance gates. Fresh independent force projection passes at **0.000087287 N**, with zero queried crossings, routing violations and sampled penetrations. Minimum sampled/corner $J$ worsen to **0.53786/0.47046**, while the head's global volume ratio stays **0.99887**. Selected displacement enrichment therefore exposes greater local compression, rather than resolving it. This single increment does not qualify an enriched trajectory, full nodal stationarity or physiological tissue behavior.

The [excluded-force decomposition](data/anatomical-arm-v1/audit/anatomical-nodal-force-components.json) locates the unbalanced virtual work at the original dense 63-coordinate state. In the largest missing direction at proximal node 98, bulk contributes **−1.972 N** to a total **−1.984 N**. In its global z direction, active-body work contributes **−1.383 N**, partly opposed by routed tendon forces. Contact contributions stay below **0.000858 N** across the six probes. Thus the unresolved stationarity involves bulk and active forces outside the retained tissue field. The component audit uses independent body virtual work and two perturbation sizes, retaining the original potential and reference geometry.

![Bulk, active and apparatus virtual work outside the retained short-biceps field](data/anatomical-arm-v1/review/dense-qualification/force-components/nodal-force-components.svg)

The stacked components and total markers evaluate the same accepted state. Each direction is a unit nodal shape projected off the retained displacement field; the plotted values are scalar energy derivatives, rather than isolated nodal traction vectors.

An [independent audit of the original fixed-end calibration poses](data/anatomical-arm-v1/audit/anatomical-fixed-end-compression.json) locates compression before whole-arm contact: brachialis, short biceps and long biceps have queried corner $J$ of **0.55924, 0.61581 and 0.61000**, despite global volume ratios above one. Their original 32-point force matches pass. At unchanged coordinates, 256-point free reduced residuals become **0.13218, 1.66242 and 0.67417 N**, all above **0.0001 N**. These fits remain numerical fixtures; they are not qualified calibration inputs for credible whole-arm muscle mechanics. Calibration stationarity, displacement-field adequacy and local material response must be resolved first. Contact cleanup or choosing a bulk modulus cannot establish those prerequisites.

A [complete nodal-force diagnostic of those frozen calibration states](data/anatomical-arm-v1/audit/anatomical-calibration-nodal.json) retains both full source cap node sets and the original body/sheet potential. It finds maximum free nodal force components of **64.07, 52.06 and 54.22 N**, respectively, outside the original field. Independent sheet projection and two perturbation sizes cross-check the assembly. It evaluates all 495 free P2 nodes per head without solving or refitting. Thus the calibration's missing stationarity is directly demonstrated before contact, rather than inferred from the arm's trajectory alone. Frozen nodal cap reactions also differ from the reduced boundary-coordinate reactions; neither is an equilibrated full nodal force fit.

### A self-consistent denser trajectory

The [256-point trajectory replay](data/anatomical-arm-v1/audit/anatomical-dense-trajectory-recheck.json) now qualifies **15 accepted increments through 0.43 s** under the declared reduced potential. Each implicit step uses its own accepted dense old coordinates, velocity, activation and time; original 32-point poses supply starting guesses only. Independent full P2 body-force projection agrees within **1.06 × 10⁻¹¹ N**, and the maximum total implicit residual is **0.000090006 N**, below the unchanged **0.0001 N** gate. Every accepted pose passes the finite surface, path, contact-sample and corner checks. Temporal lineage, active work, contact-rule energy events, impulse and work-defect bookkeeping also replay.

This dense trajectory lifts and reverses from **39.335738 to 33.534951 degrees**. Minimum queried corner $J$ over its states is still **0.712025**. It is a self-consistent reduced-model lift/release, with unresolved compression and finer-integration sensitivity; it does not qualify full nodal, mesh, quadrature, timestep or physiological convergence. Skin remains absent.

Its nonlinear work defect is **−2.433857 J** on the first increment and sums to **−4.395738 J** over the 15 increments. Independent replay verifies this recorded defect and the separate contact-rule energy events; it does not establish energy conservation. Quasistatic tissue relaxation and nonlinear joint sampling remain part of the defect. Agreement of independently assembled body energies is an assembly check, not a bound on this physical or temporal approximation.

![Dense trajectory and compression diagnostics](data/anatomical-arm-v1/review/dense-qualification/coarse/dense-qualification.svg)

The source-bound figure plots independently replayed accepted states and force residuals. The regional compression panel uses the earlier dense comparison from the original 32-point old state. The bulk and added-coordinate panel uses the common accepted dense old state. Similar joint angles and near-unity mean volumes do not establish a credible local tissue envelope.

An [exact-sign P2 geometry audit](data/anatomical-arm-v1/audit/anatomical-trajectory-orientation-summary.json) further checks all **29,988 elements** across the dense held pose, its 15 accepted states and the enriched comparison. Nodal positions reconstructed in binary64 from the saved reduced coordinates are treated as exact dyadic rationals. Every reference and current P2 Jacobian determinant has strictly positive degree-three Bernstein coefficients, computed with integer arithmetic; positivity therefore holds throughout each stored element interpolant. This closes the between-sample orientation gap for these geometries. It does not certify contact between surfaces, continuous motion, full nodal equilibrium or credible compression. The [complete coefficient archive](data/anatomical-arm-v1/audit/anatomical-trajectory-orientation-full.json.gz) is retained losslessly. This is a computational geometry certificate, separate from the compiled Lean claims.

![Accepted short-biceps envelopes and proximal detail](data/anatomical-arm-v1/review/dense-qualification/envelope/dense-envelope.svg)

This direct P2 node view uses common physical limits within each row and does not amplify displacements. The proximal detail is a geometric zoom. The two accepted 0.10 s comparisons start from the same dense old state; the enriched comparison adds only six short-biceps coordinates. Similar rendered surfaces can conceal a large change in the worst local determinant. The [source-bound node export](data/anatomical-arm-v1/audit/anatomical-dense-envelope.json) and render hashes accompany the figure.

# What the experiments establish {#coverage-and-evidence}

The original requested subjects appear below with their working example, evidence and remaining model boundary. The table distinguishes an implemented teaching question from a clinical claim. All geometry in Laboratories 1–7 is authored and schematic; the actual-data viewer retains its independent atlas and recording provenance.

| Subject | Working chapter / example | Check or evidence | Boundary |
|:--|:--|:--|:--|
| Force, coordinates and units | Force; Lab 1 | Analytic motion; exact pair cancellation | Constant planar net force |
| Skeleton, torque and rigid dynamics | Torque; Labs 2, 4 | Exact torque example; moment-arm derivative, energy/timestep tests | One fixed upper segment and hinge |
| Energy and numerical accuracy | Energy; Lab 3 | Three integrators against analytic oscillator | Ideal linear spring |
| Deformation, volume and area measurements | Early property labs 1–2 | Independent boundary volume and area × length; real kinematic identities | Prescribed geometry; no material equilibrium |
| Nonuniform axial strain | Early property lab 3 | Logarithmic compliance oracle, midpoint refinement and fixed-end compatibility | Input area profile; no transverse equilibrium or full muscle law |
| Active contraction and release | Elbow; Labs 4, 5, 7 | Continuous activation, lift/release traces; line fibre and spatial spans | Authored activation and force laws; no measured velocity law |
| Passive stretching and tendon | Tendon/tissue; Labs 5, 7 | Series equilibrium, storage/work and spatial span diagnostics | Scalar tension-only tendon and separately labeled bilateral spatial span |
| Anatomical/medical data | Anatomy and actual-data viewer | Primary architecture/indentation sources; 992 licensed-data checks | Static atlas, normalized trial and model parameters stay independent |
| Soft volumes and FEM | Continuum mechanics; Lab 6 | True BᵀDB tetrahedra, patch tests and analytic mesh refinement | Linear, small strain, no contact |
| Faster game/film methods | Fast methods; Lab 6 | Matched implicit target; error, residual and measured cost | Timing tied to stated environment; finite sweeps are approximate |
| Separate skin and fascia | Interfaces; Lab 7 | Independent membrane energy and fascia tethers; ablation | No bending, sliding or skin self-contact |
| Elbow tissue compression/contact | Spatial capstone; Lab 7 | Capsule gaps, sample forces, local J, residual and contact-off comparison | Compliant sampled bone contact; no pressure/CCD guarantee |
| Naive skin weighting | Labs 5, 7 at shared q | Actual transformed bind vertices and measured cell volumes | Force-free geometry; no anatomical accuracy claim |
| Anatomical missed contact | Anatomical apparatus | Saved muscle/bone and tendon/bone failures; positive-area geometric witnesses; derivative and frozen-rule replay checks | Reduced stationary model, finite transverse triangles and axial paths; no CCD or finite tendon radius |
| Formal claims | Visible cards and complete Lean appendix | 29 fresh kernel-checked declarations across five source files | 25 integer contracts and four real kinematic identities; no floating-point/biological validation |

The continuum solver's static manufactured solution independently assesses spatial discretization. Its matched implicit reference assesses the algebraic error of a faster solver at the same physical step. The capstone's iteration study instead measures a nonconvex spring/volume model at one mesh. These are different error questions, and their percentages must not be combined into a single “accuracy” badge.

The numerical tests verify derivatives, units, default fixtures, activation continuity, force/energy bookkeeping, deterministic resets and the stated ablations. The browser checks verify that the user can reach those results through controls, view the paired scenes and export the current state. The PDF uses the same canonical text and static solved-geometry illustrations. Neither a passing test count nor a convincing image is a medical validation claim.

## Reproduce and inspect the source

The downloadable portable edition includes `build-manifest.json`, the complete checked Lean source/receipt and the original licensed data notices. `spatial-experiment.json` contains the capstone's coordinates and diagnostics; `contributions/continuum_reference/data/reference.json` contains the continuum refinement and matched-cost results. Each contribution's stated runtime and source hashes remain attached to its results.

For a medical or CAD prediction, specify the target output before increasing mesh complexity. Obtain compatible observations, identify parameters and their uncertainty, check boundary/loading assumptions, and distinguish model error from solve error. For game or film use, specify visible defects and permitted latency, then compare the chosen reduced model against its relevant reference. A one-way posed demonstration can be a useful finished teaching example while those application-specific questions remain open.

The progressive property sequence currently implements measured tetrahedral deformation, exact isochoric kinematics and the nonuniform small-strain bar. Independent boundary-volume and area-times-length checks accompany the first two lessons; the bar uses a logarithmic compliance oracle and midpoint refinement. Bulk/shear and confinement controls, measured fibre-to-muscle aggregation, force–length/velocity and dissipative load/hold/release remain planned. None is silently inserted into the anatomical solver.

# From a lever to an arm {#from-a-lever-to-an-arm}

The book provides a bounded teaching progression: rigid motion and energy; [prescribed deformation and volume measurements, then nonuniform axial strain](#measure-deformation-before-choosing-a-muscle-law); anatomical/data evidence; active elbow and series tendon; homogeneous continuum compression; spatial continuum accuracy/cost; interfaces; and a spatial arm-under-skin comparison. These working examples keep their model boundaries visible. They do not require subject calibration and do not establish clinical accuracy. Bulk/shear/confinement, measured fibre aggregation, force–length/velocity and dissipative property lessons remain pending, alongside the unfinished anatomical capstone. This closing chapter describes how to extend the implemented educational result responsibly.

## Add anatomy with provenance

An anatomical dataset needs a source, version, specimen or subject description, coordinate system, segmentation conventions, units, and permission to redistribute each included file. A citation to a paper does not grant a licence to its meshes or scans. A reusable data record should distinguish measured values, fitted model parameters, and illustrative defaults.

Before adding bone meshes or medical images, verify the relevant dataset terms at the asset level. Store permitted source metadata and derived-file provenance, including hashes and any required attribution. Schematic geometry may teach a force path, but it must not be labelled an anatomical measurement. The data chapter demonstrates these records for its licensed atlas and research trial, without patient-specific calibration.

## Add muscles and tendons with a constitutive model

An active muscle develops tensile force according to a model of activation, fiber length, shortening or lengthening velocity, and passive stretch. A contracting muscle need not shorten: it can hold length or lengthen under load. Millard and colleagues explicitly separate excitation, activation dynamics, muscle force, and tendon equilibrium in their primary model-comparison paper. Their equilibrium, damped-equilibrium, and rigid-tendon variants have different accuracy and computational tradeoffs. [Millard et al., 2013, §§2-4](#source-muscle)

A tendon can stretch beyond slack length while transmitting force. Replacing it with an inextensible connection changes the model and must be labelled. The implemented line actuator supplies a route from joint angle to musculotendon path length and moment arm, plus a force law and an activation state. A colored bulge driven directly by an animation slider does not supply those mechanics.

## Add surface and contact as separate mechanisms

Skin weights interpolate transforms. A surface mesh can move with its bones without representing forces, volume constraints, fascia attachments, or tissue contact. A continuum or particle model must introduce its own degrees of freedom, material law, boundary conditions, and solver. Matching one pose is insufficient to validate those choices.

Elbow compression requires an explicit collision/contact model and a definition of which tissues contact. Joint reaction force from a multibody model is a net load resultant; local cartilage pressure additionally needs geometry, contact area, and tissue mechanics. The book must keep those outputs distinct.

## Medical and CAD analysis versus visual approximation

| Intended question | Evidence required | A useful comparison |
|:--|:--|:--|
| How much load reaches a joint? | Anatomical paths, inertial parameters, forces, motion, sensitivity | Rigid-body inverse/forward dynamics with stated inputs |
| Where does tissue compress? | Geometry, material data, contacts, boundary conditions, convergence | Continuum analysis and independently measured deformation |
| Does a posed surface look plausible? | Mesh and pose comparison, artist-visible defects | Linear blend skinning, corrective shapes, reduced tissue models |
| Does a reduced model run faster? | Same workload, hardware, error metric, timing method | Accuracy-cost curves, not a universal speed ranking |

This table describes research requirements, not completed validations or algorithm rankings. CAD geometry alone does not establish a tissue material law. A faster game or film model can be a good choice for an image reference while remaining unsuitable for a medical load prediction.

## Capstone acceptance contract

The arm-and-dumbbell teaching sequence implements these mechanisms progressively, with matched states in each comparison:

1. A rigid skeleton and external load establish coordinates, gravity, and torque balance.
2. Muscle paths and activation produce a controlled lift; release reduces excitation and reveals subsequent dynamics.
3. Tendon and passive-muscle stretch show compliance and stored energy.
4. Skin/fascia and soft tissue add visible deformation and defined attachment constraints.
5. Elbow contact reports gaps, penetration/residuals, reaction resultants, and any justified local pressure output separately.
6. A naive linear-blend-skinning surface runs at the same skeletal poses for comparison. It has no muscle-force or contact-pressure output.

For each stage, publish resettable inputs, numerical diagnostics, a static explanation, citations, and approximation labels. Compare ablations with the same task and pose/motion inputs. Do not claim the schematic first lever is a calibrated arm or that its gravity torque predicts compression.

## Publishing architecture

The canonical chapters are listed in `book/book.json` and assembled into one Markdown book. Small build directives insert laboratories, generated experiment results, and checked proof cards. `tools/build.py` emits the assembled Markdown and an HTML edition through Pandoc with native MathML. Local bundled JavaScript supplies interaction without a runtime CDN. `tools/render_pdf.py` prints the same HTML using static diagrams and print styles; controls and WebGL canvases are excluded from print.

The assembled edition uses Pandoc and the browser runtime to keep the reproducible path compact. There is no separate hand-maintained prose for PDF and web, and no hand-maintained proof success flag.

GitHub Actions checks proofs, runs equation tests, builds the book, and tests the browser before preparing an artifact. The foundation's exact-head workflow succeeded and was independently reviewed. A separate manually requested deployment job can publish an artifact after review. The workflow does not enable Pages, change repository settings, or publish this milestone automatically. This descendant's hosted build and any later deployment require their own verification.

# Sources and evidence boundaries {#sources-and-evidence-boundaries}

The foundation sources and the primary papers marked independently opened below were checked on 2026-10-04. Dataset references supplied by the incoming audit are explicitly distinguished. The original mechanics explanations, worked examples, code, diagrams, and numerical experiments are produced for Kenoma. No external publication figure is copied. The explicitly attributed data chapter redistributes licensed atlas meshes, extracted model parameters and a recorded normalized trial with their original provenance. The existing Apache-2.0 repository licence covers this original contribution; third-party data retains its own component licences and attribution, provided in the data package and notices.

## International units {#source-bipm}

Bureau International des Poids et Mesures. *The International System of Units*, 9th edition, English version 4.01 (2026), §2.3.4 and Tables 4-5. [Publisher page](https://www.bipm.org/en/publications/si-brochure), [DOI](https://doi.org/10.59161/AUEZ1291). Verified for the units of force, torque, energy, and the distinction between quantity and unit. Publisher page states CC BY 4.0; no brochure figure is redistributed here.

## Newton's laws {#source-force}

Peter Dourmashkin. *Chapter 7: Newton's Laws of Motion*, original MIT 8.01 course notes, updated course release 2022, §§7.3-7.4. [Primary notes PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter7.pdf). Verified for constant-mass net force and action-reaction pairs. This book supplies its own horizontal-force example and illustration. MIT OCW terms apply to source content; that content is cited, not redistributed as Kenoma Apache-2.0 material.

## Torque {#source-torque}

Peter Dourmashkin. *Chapter 17: Two Dimensional Rotational Dynamics*, original MIT 8.01 course notes, updated course release 2022, §17.1. [Primary notes PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter17.pdf). Verified for torque about an origin and the cross-product convention. The point-load lever and integer-coordinate proofs here are original examples.

## Energy and work {#source-energy}

Peter Dourmashkin. *Chapter 13: Energy, Kinetic Energy, and Work*, original MIT 8.01 course notes, updated course release 2022, §§13.2-13.6. [Primary notes PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter13.pdf). Verified for kinetic energy and the work-energy relation. The integrator derivation, oscillator implementation, and executed comparison are original work in this repository.

## Muscle model comparison {#source-muscle}

Matthew Millard, Thomas Uchida, Ajay Seth, and Scott L. Delp. “Flexing Computational Muscle: Modeling and Simulation of Musculotendon Dynamics.” *Journal of Biomechanical Engineering* 135(2):021005 (2013). DOI: [10.1115/1.4023390](https://doi.org/10.1115/1.4023390). [Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3705831/), §§2-4. Verified for activation/contraction separation, active/passive muscle components, and elastic versus rigid-tendon assumptions. No muscle curves, figures, benchmark data, or meshes from the paper are redistributed in this milestone.

## Formal toolchain {#source-lean}

[Lean official installation documentation](https://lean-lang.org/install/) and the [official Lean 4.19.0 release](https://github.com/leanprover/lean4/releases/tag/v4.19.0). The project pins the version deliberately; it does not claim it is the newest release. The original 25 declarations import the bundled standard library. The four additional real kinematic claims in `ContinuumProperties.lean` import [official mathlib v4.19.0](https://github.com/leanprover-community/mathlib4/tree/c44e0c8ee63ca166450922a373c7409c5d26b00b), with its exact commit and transitive dependency manifest pinned in `proofs/mathlib-lock.json`. The successful kernel checks and their transitive-axiom reports are linked in each proof card and in the generated build evidence.

## Human architecture {#source-architecture}

Wendy M. Murray, Thomas S. Buchanan and Scott L. Delp. “The isometric functional capacity of muscles that cross the elbow.” *Journal of Biomechanics* 33:943–952 (2000). [DOI](https://doi.org/10.1016/S0021-9290(00)00051-8), [author-hosted original PDF](https://research.me.udel.edu/buchanan/PDF_Files/Murray%2C%20Buchanan%2C%20Delp%2C%20JB%202000.pdf). Independently opened full text; Table 2 and §3 checked for the three reported study summaries. Human cadaver measurements and derived architecture estimates are distinguished. No source table image or participant-level data is copied.

## Forearm indentation {#source-indentation}

Jarkko T. Iivarinen, Rami K. Korhonen, Petro Julkunen and Jukka S. Jurvelin. “Experimental and computational analysis of soft tissue stiffness in forearm using a manual indentation device.” *Medical Engineering and Physics* 33:1245–1253 (2011). [DOI](https://doi.org/10.1016/j.medengphy.2011.05.015), [original abstract at PubMed](https://pubmed.ncbi.nlm.nih.gov/21696992/). Independently checked abstract, including nine subjects, layered inverse FE fitting, and 210/1.9 kPa resting estimates. Full publisher text was not independently read here; no additional material-law detail or raw observations are inferred.

## Contracting tissue under compression {#source-compression}

D. S. Ryan, S. Domínguez, S. A. Ross, N. Nigam and J. M. Wakeling. “The Energy of Muscle Contraction. II. Transverse Compression and Work.” *Frontiers in Physiology* 11:538522 (2020). [Original full text](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full), [DOI](https://doi.org/10.3389/fphys.2020.538522). Independently opened primary paper for its model scope and force/work mechanism. Computational evidence is kept separate from measured human elbow-contact data.

## Position-based compliance {#source-xpbd}

Miles Macklin, Matthias Müller and Nuttapong Chentanez. “XPBD: Position-Based Simulation of Compliant Constrained Dynamics.” ACM MIG (2016). [Author-hosted original paper](https://mmacklin.com/xpbd.pdf). Independently opened for compliance, timestep scaling and multiplier accumulation. No implementation or benchmark speed from this paper is reproduced as a Kenoma result.

## Geometric skinning {#source-dqs}

Ladislav Kavan, Steven Collins, Jiří Žára and Carol O'Sullivan. “Geometric Skinning with Approximate Dual Quaternion Blending.” *ACM Transactions on Graphics* 27(4) (2008). [Author-hosted original paper](https://users.cs.utah.edu/~ladislav/kavan08geometric/kavan08geometric.pdf). Independently opened for the geometric approximation and LBS artifacts. The book's two-rotation algebraic counterexample is original, and no tissue/contact guarantee is attributed to skinning.

## Dataset and model access {#source-data}

The incoming anatomy audit supplies the access/rights distinctions for [Visible Human](https://www.nlm.nih.gov/research/visible/visible_human.html), [OpenArm 2.0](https://simtk.org/frs/?group_id=1617), [OpenArm Multisensor research/code](https://github.com/lhallock/openarm-multisensor), [Quesada data](https://doi.org/10.5281/zenodo.11209324), [Arm26's model file](https://github.com/opensim-org/opensim-models/blob/master/Models/Arm26/arm26.osim), and the [current MoBL-ARMS package](https://simtk.org/frs/?group_id=657). These are audited research references; the accompanying data chapter now contains the verified licensed package described below. [BodyParts3D's official terms](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) were independently checked. Exact-package provenance and permissions are required before later redistribution. Incoming package hashes and access limitations are recorded in `education/research/integration-notes.md` in the source tree.

## Continuum background access record {#source-continuum}

Eftychios Sifakis and Jernej Barbič. *Finite Element Method Simulation of 3D Deformable Solids* (2015). [Author publication record](https://pages.cs.wisc.edu/~sifakis/) independently opened; it identifies the book and linked course. Full course notes were inaccessible in this execution environment, so this record verifies bibliographic identity only. No constitutive formula or performance result is attributed to unread notes. The affine block energy, stress derivative and equilibrium experiments are original Kenoma derivations; the independently opened Ryan paper above supplies compression-model context.

## Acquired package sources {#source-acquired-data}

BodyParts3D 4.0: Mitsuhashi et al., *Nucleic Acids Research* 37:D782–D785 (2009), [DOI](https://doi.org/10.1093/nar/gkn613). The exact package contains ten original official-archive OBJ members, SI JSON conversion, archive directory/CRC evidence and current official CC BY 4.0 grant. Historical CC BY-SA 2.1 Japan comments remain untouched.

OpenArm Multisensor 2.0: Hallock et al., *IEEE TNSRE* 29:2625–2634 (2021), [DOI](https://doi.org/10.1109/TNSRE.2021.3133813). The package provides one transformed normalized trial, source README/errata, pinned analysis revision, original archive/member hashes and CC BY 4.0 attribution. The package audit was read; the full source archive was not re-downloaded here.

Arm26: [official pinned XML](https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim), official revision independently opened and byte hash checked against the packaged source. Embedded OpenSim Development Team/Kate Holzbaur credit and CC BY 3.0 notice are retained. The extraction checks all six actuator parameter sets against XML.

[Complete component licences and changes](data/elbow-v1/LICENSES_AND_ATTRIBUTION.txt), [per-file provenance](data/elbow-v1/provenance.json). This worker verified the supplied archive SHA-256, all manifested payloads, parameter extraction, atlas SI conversion and display-bin means. These checks validate bytes and transformations, not biological calibration.

## What remains unverified

Published architecture and fitted-modulus summaries above are verified within their stated sources and methods. The acquired package establishes the specific data and provenance described in the data chapter. The schematic actuator's biological calibration, anatomical continuum/contact accuracy, patient-specific validity and performance rankings are not established by this edition. The browser tests establish behavior in the tested Chromium environment; they do not certify every browser, assistive technology, or medical application.

# Checked source appendix: Mechanics {#checked-source-appendix}

Compilation establishes only the stated exact domain.

```lean
import Std

/-!
Exact integer-coordinate identities. Interpret coordinates with fixed, positive
SI scale factors; no floating-point or biological correctness is claimed.
Only Lean's bundled standard library is required.
-/
namespace Kenoma

def torque (rx ry fx fy : Int) : Int := rx * fy - ry * fx

theorem force_pair_cancels (f : Int) : f + (-f) = 0 := by omega

theorem torque_linear (rx ry fx fy gx gy : Int) :
    torque rx ry (fx + gx) (fy + gy) =
      torque rx ry fx fy + torque rx ry gx gy := by
  simp only [torque, Int.mul_add]
  omega

theorem torque_origin_shift (rx ry ox oy fx fy : Int) :
    torque (rx - ox) (ry - oy) fx fy =
      torque rx ry fx fy - torque ox oy fx fy := by
  simp only [torque, Int.sub_mul]
  omega

theorem central_pair_torque (ax ay bx byy k : Int) :
    torque ax ay (k * (bx - ax)) (k * (byy - ay)) +
      torque bx byy (-(k * (bx - ax))) (-(k * (byy - ay))) = 0 := by
  simp only [torque, Int.mul_sub, Int.mul_neg, Int.mul_assoc]
  simp only [Int.mul_left_comm ax k, Int.mul_left_comm ay k,
    Int.mul_left_comm bx k, Int.mul_left_comm byy k,
    Int.mul_comm ax byy, Int.mul_comm ay bx, Int.mul_comm bx byy, Int.mul_comm ax ay]
  omega

def twiceKinetic (m vx vy : Int) : Int := m * (vx * vx + vy * vy)

theorem kinetic_numerator_nonnegative (m vx vy : Int) (hm : 0 ≤ m) :
    0 ≤ twiceKinetic m vx vy := by
  have square (v : Int) : 0 ≤ v * v := by
    rw [← Int.natAbs_mul_self' v]
    exact Int.ofNat_zero_le _
  exact Int.mul_nonneg hm (Int.add_nonneg (square vx) (square vy))

-- Exact scaled worked example: r=(300,0) mm, F=(0,-49050) mN.
-- Product scale is 10^-6 N m; result is -14.715 N m.
theorem torque_worked_example : torque 300 0 0 (-49050) = -14715000 := by decide

-- The weights are integers. This is a convex-combination numerator contract,
-- not a theorem about exp(), the RK4 code, or a physiological activation law.
theorem activation_weighted_bound (a u w d scale : Int)
    (ha0 : 0 ≤ a) (hau : a ≤ scale) (hu0 : 0 ≤ u) (huu : u ≤ scale)
    (hw : 0 ≤ w) (hwd : w ≤ d) :
    0 ≤ a * w + u * (d - w) ∧ a * w + u * (d - w) ≤ scale * d := by
  have hdw : 0 ≤ d - w := by omega
  constructor
  · exact Int.add_nonneg (Int.mul_nonneg ha0 hw) (Int.mul_nonneg hu0 hdw)
  · calc
      a * w + u * (d - w) ≤ scale * w + scale * (d - w) :=
        Int.add_le_add (Int.mul_le_mul_of_nonneg_right hau hw)
          (Int.mul_le_mul_of_nonneg_right huu hdw)
      _ = scale * d := by simp only [Int.mul_sub]; omega

theorem virtual_power_identity (force dl omega : Int) :
    (-force * dl) * omega = -(force * (dl * omega)) := by
  simp only [Int.neg_mul, Int.mul_assoc]

-- A volume element uses g0 = -(g1+g2+g3), coordinate by coordinate.
-- The derivative formula itself is tested numerically, not proved here.
theorem element_gradient_resultant (g1 g2 g3 scale : Int) :
    scale * (-(g1 + g2 + g3)) + scale * g1 + scale * g2 + scale * g3 = 0 := by
  simp only [Int.mul_neg, Int.mul_add]
  omega

-- The actual centroid-contact distribution uses four equal barycentric weights.
-- This numerator identity supports the motion/force transpose contract.
theorem centroid_contact_power (force v0 v1 v2 v3 : Int) :
    force * (v0 + v1 + v2 + v3) =
      force * v0 + force * v1 + force * v2 + force * v3 := by
  simp only [Int.mul_add]

-- A regularized scalar constraint denominator is positive under these inputs.
-- h^2 scaling and the construction of the real gradients remain assumptions.
theorem compliant_denominator_positive (w g alpha : Int)
    (hw : 0 ≤ w) (ha : 0 < alpha) : 0 < w * (g * g) + alpha := by
  have square : 0 ≤ g * g := by
    rw [← Int.natAbs_mul_self' g]
    exact Int.ofNat_zero_le _
  have term := Int.mul_nonneg hw square
  omega

-- Scaled Armijo sufficient decrease, with nonnegative step coefficient.
-- This checks the acceptance contract, not L-BFGS or nonconvex convergence.
theorem accepted_energy_nonincrease (oldE newE coefficient slope : Int)
    (hc : 0 ≤ coefficient) (hs : slope ≤ 0)
    (accept : newE ≤ oldE + coefficient * slope) : newE ≤ oldE := by
  have product : coefficient * slope ≤ 0 := by
    have positive := Int.mul_nonneg hc (show 0 ≤ -slope by omega)
    simp only [Int.mul_neg] at positive
    omega
  omega

end Kenoma

#print axioms Kenoma.force_pair_cancels
#print axioms Kenoma.torque_linear
#print axioms Kenoma.torque_origin_shift
#print axioms Kenoma.central_pair_torque
#print axioms Kenoma.kinetic_numerator_nonnegative
#print axioms Kenoma.torque_worked_example
#print axioms Kenoma.activation_weighted_bound
#print axioms Kenoma.virtual_power_identity

#print axioms Kenoma.element_gradient_resultant
#print axioms Kenoma.centroid_contact_power
#print axioms Kenoma.compliant_denominator_positive
#print axioms Kenoma.accepted_energy_nonincrease
```

## Proof check receipt {#proof-check-receipt}

Fresh successful invocation: `lean -DwarningAsError=true proofs/Mechanics.lean`. Toolchain: Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release). Checked declarations: 12. Source SHA-256: `6b45c1d9a32fbd0cf6e034d3e4d15d26dc720215afe6845bbbb9d7de07bff2fd`. Claim-map SHA-256: `e5aee4e575fd3325ea676b0234801b31c9003b46943b3f13dc84ee987298e7b6`. Dependencies: mathlib not used; bundled Std only. This receipt does not validate floating-point implementation, biological parameters or anatomy.

## Kernel dependency report {#kernel-dependency-report}

```text
'Kenoma.force_pair_cancels' depends on axioms: [propext, Quot.sound]
'Kenoma.torque_linear' depends on axioms: [propext, Quot.sound]
'Kenoma.torque_origin_shift' depends on axioms: [propext, Quot.sound]
'Kenoma.central_pair_torque' depends on axioms: [propext, Quot.sound]
'Kenoma.kinetic_numerator_nonnegative' depends on axioms: [propext]
'Kenoma.torque_worked_example' does not depend on any axioms
'Kenoma.activation_weighted_bound' depends on axioms: [propext, Quot.sound]
'Kenoma.virtual_power_identity' depends on axioms: [propext]
'Kenoma.element_gradient_resultant' depends on axioms: [propext, Quot.sound]
'Kenoma.centroid_contact_power' depends on axioms: [propext]
'Kenoma.compliant_denominator_positive' depends on axioms: [propext, Quot.sound]
'Kenoma.accepted_energy_nonincrease' depends on axioms: [propext, Quot.sound]
```


# Checked source appendix: AnatomicalTransfer {#transfer-source-appendix}

Compilation establishes only the stated exact domain.

```lean
import Std

/- Exact scaled integer algebra for a three-coordinate, one-DOF transfer.
   Positive common scales are assumed. Geometry, derivatives, browser arithmetic,
   material behavior and biological correctness require separate evidence. -/
namespace Kenoma.Anatomical

def dot3 (a0 a1 a2 b0 b1 b2 : Int) : Int := a0*b0+a1*b1+a2*b2

-- The implemented attachment has velocity B * omega and torque dot(B, force).
theorem attachment_transpose_power (b0 b1 b2 f0 f1 f2 omega : Int) :
    dot3 b0 b1 b2 f0 f1 f2 * omega =
      dot3 f0 f1 f2 (b0*omega) (b1*omega) (b2*omega) := by
  simp only [dot3, Int.add_mul, Int.mul_assoc,
    Int.mul_left_comm b0 f0, Int.mul_left_comm b1 f1, Int.mul_left_comm b2 f2]

-- If dU/dt = force dot (nodeVelocity - B*omega), transferred forces cancel it.
theorem paired_attachment_work (b0 b1 b2 f0 f1 f2 v0 v1 v2 omega : Int) :
    dot3 (-f0) (-f1) (-f2) v0 v1 v2 +
      dot3 b0 b1 b2 f0 f1 f2 * omega +
      dot3 f0 f1 f2 (v0-b0*omega) (v1-b1*omega) (v2-b2*omega) = 0 := by
  simp only [dot3, Int.neg_mul, Int.mul_sub, Int.add_mul, Int.mul_assoc,
    Int.mul_left_comm b0 f0, Int.mul_left_comm b1 f1, Int.mul_left_comm b2 f2]
  omega

end Kenoma.Anatomical
#print axioms Kenoma.Anatomical.attachment_transpose_power
#print axioms Kenoma.Anatomical.paired_attachment_work
```

## Proof check receipt {#transfer-proof-receipt}

Fresh successful invocation: `lean -DwarningAsError=true proofs/AnatomicalTransfer.lean`. Toolchain: Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release). Checked declarations: 2. Source SHA-256: `9c733f15d8b9016646bc024764595bb750041dd84cb0db4c0f0d896d4be423c8`. Claim-map SHA-256: `893e0689eda0e0f194d20bc9ae8d6ff097c23666ba6d4711366848e428fc2afa`. Dependencies: mathlib not used; bundled Std only. This receipt does not validate floating-point implementation, biological parameters or anatomy.

## Kernel dependency report {#transfer-kernel-report}

```text
'Kenoma.Anatomical.attachment_transpose_power' depends on axioms: [propext]
'Kenoma.Anatomical.paired_attachment_work' depends on axioms: [propext, Quot.sound]
```


# Checked source appendix: CoupledMechanics {#coupled-source-appendix}

Compilation establishes only the stated exact domain.

```lean
import Std

/- Exact integer numerators for the implemented implicit joint step and controls.
   Compatible positive scales, force mappings and stationarity are supplied.
   These declarations establish no floating-point, anatomical or biological claim. -/
namespace Kenoma.Coupled

theorem impulse_balance (inertia oldVelocity newVelocity h tissue gravity damping : Int)
    (stationary : inertia * (newVelocity-oldVelocity) =
      h * (tissue+gravity-damping*newVelocity)) :
    inertia * (newVelocity-oldVelocity) + h*damping*newVelocity =
      h*tissue+h*gravity := by
  simp only [Int.mul_add, Int.mul_sub, Int.mul_assoc] at stationary ⊢
  omega

theorem kinetic_increment_identity (inertia oldVelocity newVelocity : Int) :
    inertia*(newVelocity*newVelocity-oldVelocity*oldVelocity) +
      inertia*(newVelocity-oldVelocity)*(newVelocity-oldVelocity) =
      2*(inertia*(newVelocity-oldVelocity)*newVelocity) := by
  simp only [Int.mul_sub, Int.sub_mul, Int.mul_assoc,
    Int.mul_comm oldVelocity newVelocity]
  omega

theorem implicit_kinetic_work_balance
    (inertia oldVelocity newVelocity h tissue gravity damping : Int)
    (stationary : inertia*(newVelocity-oldVelocity) =
      h*(tissue+gravity-damping*newVelocity)) :
    inertia*(newVelocity*newVelocity-oldVelocity*oldVelocity) +
      inertia*(newVelocity-oldVelocity)*(newVelocity-oldVelocity) =
      2*h*tissue*newVelocity + 2*h*gravity*newVelocity -
      2*h*damping*newVelocity*newVelocity := by
  rw [kinetic_increment_identity, stationary]
  simp only [Int.mul_add, Int.mul_sub, Int.add_mul, Int.sub_mul, Int.mul_assoc]

theorem implicit_dissipation_numerator_nonnegative
    (inertia h damping oldVelocity newVelocity : Int)
    (hi : 0 ≤ inertia) (hh : 0 ≤ h) (hd : 0 ≤ damping) :
    0 ≤ inertia*((newVelocity-oldVelocity)*(newVelocity-oldVelocity)) +
      2*h*damping*(newVelocity*newVelocity) := by
  have square (v : Int) : 0 ≤ v*v := by
    rw [← Int.natAbs_mul_self' v]
    exact Int.ofNat_zero_le _
  exact Int.add_nonneg
    (Int.mul_nonneg hi (square (newVelocity-oldVelocity)))
    (Int.mul_nonneg (Int.mul_nonneg (Int.mul_nonneg (by decide) hh) hd)
      (square newVelocity))

-- z is downward-positive in this authored block fixture, so V = -m*g*z.
theorem mass_event_work_numerator (oldInertia deltaMass radiusSquared velocity g z : Int) :
    (oldInertia+deltaMass*radiusSquared)*velocity*velocity -
      oldInertia*velocity*velocity - 2*g*z*deltaMass =
      deltaMass*(radiusSquared*velocity*velocity-2*g*z) := by
  simp only [Int.add_mul, Int.mul_sub, Int.mul_assoc]
  have commute : deltaMass*(2*(g*z)) = 2*(g*(z*deltaMass)) := by ac_rfl
  rw [commute]
  omega

theorem tendon_toe_energy_numerator_nonnegative (area length young strain : Int)
    (ha : 0 ≤ area) (hl : 0 ≤ length) (hy : 0 ≤ young) (he : 0 ≤ strain) :
    0 ≤ area*length*young*strain*strain*strain := by
  exact Int.mul_nonneg
    (Int.mul_nonneg (Int.mul_nonneg
      (Int.mul_nonneg (Int.mul_nonneg ha hl) hy) he) he) he

-- Common barycentric denominator d: corner numerators 2*l_i²-d*l_i;
-- midside numerators 4*l_i*l_j; their total is d² when sum(l_i)=d.
theorem quadratic_partition_numerator (l0 l1 l2 l3 d : Int)
    (normalized : l0+l1+l2+l3=d) :
    2*(l0*l0+l1*l1+l2*l2+l3*l3) - d*(l0+l1+l2+l3) +
      4*(l0*l1+l0*l2+l0*l3+l1*l2+l1*l3+l2*l3) = d*d := by
  rw [← normalized]
  simp only [Int.mul_add, Int.add_mul, Int.mul_comm l1 l0,
    Int.mul_comm l2 l0, Int.mul_comm l3 l0, Int.mul_comm l2 l1,
    Int.mul_comm l3 l1, Int.mul_comm l3 l2]
  omega

end Kenoma.Coupled
#print axioms Kenoma.Coupled.impulse_balance
#print axioms Kenoma.Coupled.kinetic_increment_identity
#print axioms Kenoma.Coupled.implicit_kinetic_work_balance
#print axioms Kenoma.Coupled.implicit_dissipation_numerator_nonnegative
#print axioms Kenoma.Coupled.mass_event_work_numerator
#print axioms Kenoma.Coupled.tendon_toe_energy_numerator_nonnegative
#print axioms Kenoma.Coupled.quadratic_partition_numerator
```

## Proof check receipt {#coupled-proof-receipt}

Fresh successful invocation: `lean -DwarningAsError=true proofs/CoupledMechanics.lean`. Toolchain: Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release). Checked declarations: 7. Source SHA-256: `84c4e1ad43e792d0fd530996e4814102fc3d31c1c5b3a689bf4ce6c060a4c2ab`. Claim-map SHA-256: `79ea43a2ed7f73ab8fad8eaa66e87cc4ad71af9a80d0d236ce012445ccbbe0e3`. Dependencies: mathlib not used; bundled Std only. This receipt does not validate floating-point implementation, biological parameters or anatomy.

## Kernel dependency report {#coupled-kernel-report}

```text
'Kenoma.Coupled.impulse_balance' depends on axioms: [propext, Quot.sound]
'Kenoma.Coupled.kinetic_increment_identity' depends on axioms: [propext, Quot.sound]
'Kenoma.Coupled.implicit_kinetic_work_balance' depends on axioms: [propext, Quot.sound]
'Kenoma.Coupled.implicit_dissipation_numerator_nonnegative' depends on axioms: [propext]
'Kenoma.Coupled.mass_event_work_numerator' depends on axioms: [propext, Quot.sound]
'Kenoma.Coupled.tendon_toe_energy_numerator_nonnegative' depends on axioms: [propext]
'Kenoma.Coupled.quadratic_partition_numerator' depends on axioms: [propext, Quot.sound]
```


# Checked source appendix: AnatomicalArm {#arm-source-appendix}

Compilation establishes only the stated exact domain.

```lean
import Std

/- Exact numerator algebra for the atlas-frame arm. Stationarity and compatible
   scales are assumptions. This file certifies no floating-point mechanics,
   anatomical architecture, tissue calibration or biological prediction. -/
namespace Kenoma.Arm

-- The atlas world has +Z superior, hence V = +m*g*z.
theorem upward_mass_event_work_numerator
    (oldInertia deltaMass radiusSquared velocity g z : Int) :
    (oldInertia+deltaMass*radiusSquared)*velocity*velocity -
      oldInertia*velocity*velocity + 2*g*z*deltaMass =
      deltaMass*(radiusSquared*velocity*velocity+2*g*z) := by
  simp only [Int.add_mul, Int.mul_add, Int.mul_assoc]
  have commute : deltaMass*(2*(g*z)) = 2*(g*(z*deltaMass)) := by ac_rfl
  rw [commute]
  omega

-- One shared guide component after interpolation: two head contributions,
-- the common distal apparatus, weak matrix and contact. Repeat for each component.
theorem shared_guide_force_balance
    (headA headB distal matrix contact : Int)
    (equilibrium : headA+headB+distal+matrix+contact=0) :
    distal = -(headA+headB+matrix+contact) := by
  omega

-- Exact scaled reference-area partition; geometry supplies the shares.
theorem contact_partition_area_numerator (area a b c scale : Int)
    (partition : a + b + c = scale) :
    area*a + area*b + area*c = area*scale := by
  rw [← Int.mul_add, ← Int.mul_add, partition]

-- A supplied conservative unsigned envelope also gives conservative signed
-- gaps on either side. Numerical construction/geometry is checked separately.
theorem conservative_contact_gap (distance envelope : Int)
    (bound : envelope <= distance) :
    envelope <= distance ∧ envelope - 2*distance <= -distance := by
  omega

end Kenoma.Arm
#print axioms Kenoma.Arm.upward_mass_event_work_numerator
#print axioms Kenoma.Arm.shared_guide_force_balance

#print axioms Kenoma.Arm.contact_partition_area_numerator

#print axioms Kenoma.Arm.conservative_contact_gap
```

## Proof check receipt {#arm-proof-receipt}

Fresh successful invocation: `lean -DwarningAsError=true proofs/AnatomicalArm.lean`. Toolchain: Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release). Checked declarations: 4. Source SHA-256: `843f04f8e8f5c81a902d6816f0136726d006be6574aff5245360b8c2006ef025`. Claim-map SHA-256: `a56d39ba3dfe805189ca13ef91f696b99b2762e7258e6b22246b81eba36baa83`. Dependencies: mathlib not used; bundled Std only. This receipt does not validate floating-point implementation, biological parameters or anatomy.

## Kernel dependency report {#arm-kernel-report}

```text
'Kenoma.Arm.upward_mass_event_work_numerator' depends on axioms: [propext, Quot.sound]
'Kenoma.Arm.shared_guide_force_balance' depends on axioms: [propext, Quot.sound]
'Kenoma.Arm.contact_partition_area_numerator' depends on axioms: [propext]
'Kenoma.Arm.conservative_contact_gap' depends on axioms: [propext, Classical.choice, Quot.sound]
```


# Checked source appendix: ContinuumProperties {#property-source-appendix}

Compilation establishes only the stated exact domain.

```lean
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Data.Real.Sqrt

/-!
Real-valued kinematic identities. These do not prove floating-point refinement,
surface mesh correctness, equilibrium, material selection or biological validity.
Mathlib and its dependency manifest are pinned separately from the Std-only work.
-/
namespace KenomaProperties

def edgeMatrix (v : Fin 4 → Fin 3 → ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  fun i j => v j.succ i - v 0 i

theorem edge_translation_invariant (v : Fin 4 → Fin 3 → ℝ) (t : Fin 3 → ℝ) :
    edgeMatrix (fun j i => v j i + t i) = edgeMatrix v := by
  apply Matrix.ext
  intro i j
  simp [edgeMatrix]

theorem determinant_composition (A B : Matrix (Fin 3) (Fin 3) ℝ) :
    Matrix.det (A * B) = Matrix.det A * Matrix.det B := by
  exact Matrix.det_mul A B

def axialMatrix (lambda b : ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  Matrix.diagonal ![lambda, b, b]

theorem axial_determinant (lambda b : ℝ) :
    Matrix.det (axialMatrix lambda b) = lambda * b * b := by
  simp [axialMatrix, Matrix.det_diagonal, Fin.prod_univ_succ, mul_assoc]

theorem isochoric_sqrt_construction (lambda : ℝ) (hlambda : 0 < lambda) :
    0 < 1 / Real.sqrt lambda ∧
    Matrix.det (axialMatrix lambda (1 / Real.sqrt lambda)) = 1 := by
  constructor
  · exact one_div_pos.mpr (Real.sqrt_pos.mpr hlambda)
  · rw [axial_determinant]
    calc
      lambda * (1 / Real.sqrt lambda) * (1 / Real.sqrt lambda) =
          lambda * (Real.sqrt lambda * Real.sqrt lambda)⁻¹ := by
        simp only [one_div, mul_assoc, mul_inv]
      _ = 1 := by
        rw [Real.mul_self_sqrt hlambda.le]
        exact mul_inv_cancel₀ (ne_of_gt hlambda)

end KenomaProperties

#print axioms KenomaProperties.edge_translation_invariant
#print axioms KenomaProperties.determinant_composition
#print axioms KenomaProperties.axial_determinant
#print axioms KenomaProperties.isochoric_sqrt_construction
```

## Proof check receipt {#property-proof-receipt}

Fresh successful invocation: `lake env lean -DwarningAsError=true proofs/ContinuumProperties.lean (from pinned mathlib workspace)`. Toolchain: Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release). Checked declarations: 4. Source SHA-256: `33945605131f1a0fc3568467cbc1026463867a8fa241fb25e2174c23a229f12e`. Claim-map SHA-256: `481b28474107cfcc8096b3364e140d842fc7751bacd45f19ffc4de35c033e4f3`. Dependencies: pinned mathlib v4.19.0; commit c44e0c8ee63ca166450922a373c7409c5d26b00b; locked transitive dependencies. This receipt does not validate floating-point implementation, biological parameters or anatomy.

## Kernel dependency report {#property-kernel-report}

```text
'KenomaProperties.edge_translation_invariant' depends on axioms: [propext, Classical.choice, Quot.sound]
'KenomaProperties.determinant_composition' depends on axioms: [propext, Classical.choice, Quot.sound]
'KenomaProperties.axial_determinant' depends on axioms: [propext, Classical.choice, Quot.sound]
'KenomaProperties.isochoric_sqrt_construction' depends on axioms: [propext, Classical.choice, Quot.sound]
```
