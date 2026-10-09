# Reading a moving body {#reading-a-moving-body}

A body can look convincing while its forces are wrong. A model can balance its forces while its surface looks wrong. Kenoma's educational book asks how to tell the difference, beginning with quantities that we can calculate and inspect before adding anatomy. The intended reader is a programmer, technical artist, or engineering student who wants to connect geometry, mechanics, computation, and evidence.

This edition develops force, torque, energy, anatomical evidence, and a force-driven schematic elbow with activation and a dumbbell load. Seven original resettable 3D laboratories progress through compliant tendon storage, a reduced continuum compression block, a worked tetrahedral FEM/compliant-solver comparison, and a spatial muscle-under-skin/contact strip at identical poses. An eighth, worker-backed experiment jointly solves deforming tissue, distributed tendons and a moving hinge. Its geometry is schematic; the requested anatomical lifting capstone remains under development. A separate evidence viewer contains ten actual atlas meshes, one recorded normalized human trial, and six published model actuator parameter sets. These are three independent evidence streams, not a calibrated person. Three progressive property lessons additionally measure prescribed tetrahedral deformation, compare isochoric volume with cross-section and exterior area, and expose uneven axial strain in a nonuniform bar. A fourth prescribed property lesson separates local from total volume conservation under uneven finite stretch. Three further property lessons add bulk/shear confinement, passive axial load/hold/release, and force-driven unequal 3D blocks with individually preserved volume. The printed edition contains the same explanations, static diagrams, data figures, worked values and original numerical experiments. Clinical or subject-specific prediction is not claimed or required to complete the teaching examples.

The content is an **educational extension**. The existing production plans in `docs/plans/` remain separate. A teaching experiment does not silently add a simulator requirement to the Bevy MVP, change its canonical storage format, or establish a production algorithm choice.

## Reading path: measure first, then add a law {#measurement-first-reading-path}

Read [force](#force-changes-motion), [torque](#a-force-has-an-application-point) and [energy](#energy-reveals-numerical-error) for the rigid-body quantities and system boundary. Then use the [three property lessons](#measure-deformation-before-choosing-a-muscle-law) in order: measure an imposed deformation; construct prescribed volume preservation; calculate uneven strain under a reduced axial law. Their worked examples introduce length, area, volume, stretch, strain, force and stress before a contact or continuum solver is needed. Continue with [bulk/shear confinement](#compression-bulk-shear-confinement), then [load/hold/release](#dissipative-load-hold-release) to distinguish recoverable storage from viscous loss in the passive axial bar. Then compare [unequal blocks under one force](#serial-specimen-volume), where a declared incompressible material law determines the local stretches and current areas. This separate-block prerequisite does not complete the requested connected continuous specimen with varying cross section, coupled local axial/lateral deformation and volume; that demonstration is not included or established in this edition.

Next distinguish [anatomical evidence](#anatomy-is-evidence) from teaching assumptions, and follow the actuator into [elbow motion](#let-forces-move-the-elbow). The later [tissue](#tissue-and-rendered-skin), [tendon/compression](#tendon-tissue-coupling) and [continuum](#from-a-spring-to-a-volume-of-tissue) chapters add material energies, boundary conditions and force-driven deformation. Prescribed constant volume is not a solved material response, and the axial bar is not a full muscle. The [fixed-field projection interlude](#fixed-field-pressure-projection) follows the spatial continuum comparison and precedes interfaces and coupling. Its 27 exact finite weighted-vector statements concern representation at one prescribed state. Spatial solver comparisons and the anatomical research apparatus come after those distinctions; their unfinished scope remains explicit.

## Three different kinds of evidence

A **physical assumption** describes the model: a constant force, a perfectly rigid lever, or an ideal spring. A **numerical check** compares the implemented arithmetic with a reference or studies its error. A **formal proof** establishes a precisely stated mathematical claim within its declared domain. Each can be useful; none automatically supplies the other two.

The 115 proof cards in this research edition are generated only after checking fourteen source files with Lean 4.19.0: `Mechanics.lean`, `AnatomicalTransfer.lean`, `CoupledMechanics.lean`, `AnatomicalArm.lean`, `ContinuumProperties.lean`, `MaterialResponse.lean`, `MaterialResponseReal.lean`, `MechanicsReal.lean`, `ActuatorConstitutiveReal.lean`, `DissipativeBarReal.lean`, `SerialSpecimenReal.lean`, `MixedLogVolume.lean`, `NonuniformIsochoric.lean` and `ArchitectureForce.lean`. Thirty declarations use integer domains and bundled Std, including five narrow material-response contracts; eighty-five quantify reals with pinned mathlib v4.19.0. These comprise four kinematic identities, five constrained specimen algebra identities, three force/torque/power identities, eleven activation/Gaussian/guarded-series results, eleven local standard-linear-solid energy/relaxation results, twelve homogeneous neo-Hookean serial-block identities, derivatives and ordering results, 27 finite weighted-vector projection results, six declared-gradient/interval/algebraic-cell nonuniform-volume contracts and six scalar architecture-force bookkeeping contracts. The actuator results include real derivatives and conditional nonlinear root existence/uniqueness; the compressible confinement specimen's constitutive derivatives and equilibrium obligations, continuous actuator-mechanics work balances and numerical refinement remain unfinished. Each card reports its exact theorem, assumptions, source hash, implementation link and transitive axioms. The stated real results do not establish floating-point equivalence, general force equilibrium, anatomical validity or biological correctness. This distinction stays visible beside each claim.

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

Read the model label and the worked example first. Change one control, predict a result, and inspect the numerical output before interpreting the image. Step through time when needed; use Reset to return all physics parameters and the camera to defaults. The laboratories start paused and stop at a bounded step count. Laboratories 1–5 start a new experiment after a non-excitation parameter edit; excitation edits in Laboratories 4–5 retain activation, velocity and time. Laboratory 6 recomputes a static or single-step comparison rather than integrating a trajectory. Laboratory 7 retains current activation, time, pose, velocity and accumulated hinge work/dissipation across parameter edits, then recomputes the spatial shape deterministically. Its angle control explicitly sets pose with zero velocity and clears a domain halt; entering prescribed hold stops motion at the current pose. Reset and the 90° compression fixture deliberately initialize its state. See each laboratory's trace policy before comparing experiments. The first four property lessons update static imposed geometry, an axial calculation or a homogeneous material equilibrium without integrating time. The fifth follows a finite SLS load/hold/unload/recovery protocol; each parameter edit explicitly starts a new experiment and clears its internal-state and energy history. The sixth property lesson recomputes a static, force-driven two-block assembly without changing the requested force; it exposes each finite root residual. The coupled fixture also preserves its tissue coordinates, angle, velocity, activation and time when effort or dumbbell mass changes. Its mass control records the external energy added or removed with the mass; it does not restart the trajectory.

Every scene has a text description and static illustration. If WebGL is unavailable, the controls and numerical results still work. All seven mechanics laboratories use original procedural **schematic teaching geometry**: their cylinders, spheres, blocks, grids and arrows are separate from anatomical measurements. The evidence viewer instead shows actual licensed static atlas surfaces, with their source labels, units and limitations. Neither the atlas nor the human-study summaries calibrates the schematic actuator.

## A useful question to carry forward

Imagine a forearm holding a dumbbell. Ask: what system did we isolate, what forces act on it, where do those forces act, and what energy enters or leaves it? These questions remain useful whether the next model is a rigid-body joint, a finite-element tissue mesh, or an animation rig. A more detailed surface cannot rescue an unspecified system boundary.

The property lessons use the same SI convention with prescribed positive stretches or an explicitly reduced small-strain axial law. The first four update a prescribed geometry or static equilibrium; the fifth integrates an internal viscous strain under its stated axial law, and the sixth solves two separate incompressible homogeneous blocks and independently measures their 3D geometry. Independent geometric measurements and midpoint-integration error remain visible; their exact kinematic claims do not prove a constitutive law or qualify the anatomical tissue envelope.

The architecture-force integration is a source candidate, not a newly qualified full-book release. Its chapter and portable lab connect reference/current area, nominal/Cauchy stress, projection, parallel aggregation and series exchange. The historical nonuniform-volume total was 103 + 6 = 109; this source registry adds six for 115. The preserved standalone qualification does not establish complete-book proof closure, integrated browser/PDF acceptance or anatomical calibration. All example counts, areas, stresses and control ranges are authored.


## Read the model before moving it {#shared-gui-scope}

Every chapter now has an example in the shared Kenoma embedded GUI. The label
above each view distinguishes illustrative geometry, prescribed kinematics,
analytic bookkeeping, a numerical demonstration, and recorded evidence. Orbiting
a model does not increase its physical dimension or validate its parameters.
An algebraic statement can be kernel-checked while its browser implementation,
mesh approximation and biological interpretation remain separate obligations.

The simple human poser is an independent artistic system: a graph, generated
surface and pose rig with gizmo controls and local SQLite scene files. It has
no tissue forces or contact response. Educational model adapters share only
presentation components with it. The research apparatus retains its original
laws, acceptance criteria and failed-state evidence.

Checked cards show their claim, assumptions and limits immediately. Expand a
card for its exact statement, source and compilation receipt. The complete Lean
appendices are also collapsible on screen; the PDF retains all statements and
full sources. A GUI badge never substitutes for the source-bound kernel receipt.
