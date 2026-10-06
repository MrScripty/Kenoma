# Reading a moving body {#reading-a-moving-body}

A body can look convincing while its forces are wrong. A model can balance its forces while its surface looks wrong. Kenoma's educational book asks how to tell the difference, beginning with quantities that we can calculate and inspect before adding anatomy. The intended reader is a programmer, technical artist, or engineering student who wants to connect geometry, mechanics, computation, and evidence.

This edition develops force, torque, energy, anatomical evidence, and a force-driven schematic elbow with activation and a dumbbell load. Seven original resettable 3D laboratories progress through compliant tendon storage, a reduced continuum compression block, a worked tetrahedral FEM/compliant-solver comparison, and a spatial muscle-under-skin/contact strip at identical poses. An eighth, worker-backed experiment jointly solves deforming tissue, distributed tendons and a moving hinge. Its geometry is schematic; the requested anatomical lifting capstone remains under development. A separate evidence viewer contains ten actual atlas meshes, one recorded normalized human trial, and six published model actuator parameter sets. These are three independent evidence streams, not a calibrated person. Three progressive property lessons additionally measure prescribed tetrahedral deformation, compare isochoric volume with cross-section and exterior area, and expose uneven axial strain in a nonuniform bar. The printed edition contains the same explanations, static diagrams, data figures, worked values and original numerical experiments. Clinical or subject-specific prediction is not claimed or required to complete the teaching examples.

The content is an **educational extension**. The existing production plans in `docs/plans/` remain separate. A teaching experiment does not silently add a simulator requirement to the Bevy MVP, change its canonical storage format, or establish a production algorithm choice.

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

Read the model label and the worked example first. Change one control, predict a result, and inspect the numerical output before interpreting the image. Step through time when needed; use Reset to return all physics parameters and the camera to defaults. The laboratories start paused and stop at a bounded step count. In the original laboratories, parameter changes reset time, except that the elbow's excitation can change during a trajectory: activation and velocity continue through release. The coupled fixture also preserves its tissue coordinates, angle, velocity, activation and time when effort or dumbbell mass changes. Its mass control records the external energy added or removed with the mass; it does not restart the trajectory.

Every scene has a text description and static illustration. If WebGL is unavailable, the controls and numerical results still work. All seven mechanics laboratories use original procedural **schematic teaching geometry**: their cylinders, spheres, blocks, grids and arrows are separate from anatomical measurements. The evidence viewer instead shows actual licensed static atlas surfaces, with their source labels, units and limitations. Neither the atlas nor the human-study summaries calibrates the schematic actuator.

## A useful question to carry forward

Imagine a forearm holding a dumbbell. Ask: what system did we isolate, what forces act on it, where do those forces act, and what energy enters or leaves it? These questions remain useful whether the next model is a rigid-body joint, a finite-element tissue mesh, or an animation rig. A more detailed surface cannot rescue an unspecified system boundary.

The property lessons use the same SI convention with prescribed positive stretches or an explicitly reduced small-strain axial law. They update a measured pose immediately and do not integrate time. Independent geometric measurements and midpoint-integration error remain visible; their exact kinematic claims do not prove a constitutive law or qualify the anatomical tissue envelope.
