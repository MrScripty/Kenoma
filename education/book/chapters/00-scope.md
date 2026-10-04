# Reading a moving body {#reading-a-moving-body}

A body can look convincing while its forces are wrong. A model can balance its forces while its surface looks wrong. Kenoma's educational book asks how to tell the difference, beginning with quantities that we can calculate and inspect before adding anatomy. The intended reader is a programmer, technical artist, or engineering student who wants to connect geometry, mechanics, computation, and evidence.

This edition develops force, torque, energy, anatomical evidence, and a force-driven schematic elbow with activation and a dumbbell load. The web edition contains four 3D laboratories; the printed edition contains the same explanations, default-state diagrams, worked values, and original numerical experiments. Source-grounded chapters explain anatomy, tissue, contact and graphics approximations. Published human-study summaries are distinguished from the executable's authored parameters. Raw anatomical dataset integration, compliant tendon/tissue mechanics and the complete contact/skinning capstone remain pending. This edition does not contain a patient-specific model or clinical validation.

The content is an **educational extension**. The existing production plans in `docs/plans/` remain separate. A teaching experiment does not silently add a simulator requirement to the Bevy MVP, change its canonical storage format, or establish a production algorithm choice.

## Three different kinds of evidence

A **physical assumption** describes the model: a constant force, a perfectly rigid lever, or an ideal spring. A **numerical check** compares the implemented arithmetic with a reference or studies its error. A **formal proof** establishes a precisely stated mathematical claim within its declared domain. Each can be useful; none automatically supplies the other two.

The proof cards in this edition are generated after checking `Mechanics.lean` with Lean 4.19.0. Their integer-coordinate domain supports exact arithmetic and explicit fixed unit scales without adding a large mathematics dependency. The cards report the theorem, assumptions, source hash, and transitive axioms. They do not assert arbitrary-real theorems, floating-point equivalence, or biological correctness. This distinction stays visible beside the claim it qualifies.

## Coordinates and units

Use a right-handed frame: x points right, y points up, and z points out of the page. The laboratories solve planar motion in the xy plane and render that plane in a 3D scene. The scene can be viewed from the front or obliquely; changing the camera changes neither state nor results. A 3D rendering does not turn planar equations into a spatial biomechanical simulation.

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

Read the model label and the worked example first. Change one control, predict a result, and inspect the numerical output before interpreting the image. Step through time when needed; use Reset to return all physics parameters and the camera to defaults. The laboratories start paused and stop at a bounded step count. Parameter changes reset time rather than mixing trajectories from different models, except that the elbow's excitation can change during a trajectory: activation and velocity continue through release.

Every scene has a text description and static illustration. If WebGL is unavailable, the controls and numerical results still work. The image remains a teaching diagram with no imported anatomical geometry; the human-study summaries in the anatomy chapter are separate from its parameter choices. There are no imported anatomy assets in this milestone: all cylinders, spheres, grids, and arrows are original procedural **schematic teaching geometry**.

## A useful question to carry forward

Imagine a forearm holding a dumbbell. Ask: what system did we isolate, what forces act on it, where do those forces act, and what energy enters or leaves it? These questions remain useful whether the next model is a rigid-body joint, a finite-element tissue mesh, or an animation rig. A more detailed surface cannot rescue an unspecified system boundary.
