# What the experiments establish {#coverage-and-evidence}

The original requested subjects appear below with their working example, evidence and remaining model boundary. The table distinguishes an implemented teaching question from a clinical claim. All geometry in Laboratories 1–7 is authored and schematic; the actual-data viewer retains its independent atlas and recording provenance.

| Subject | Working chapter / example | Check or evidence | Boundary |
|:--|:--|:--|:--|
| Force, coordinates and units | Force; Lab 1 | Analytic motion; exact pair cancellation | Constant planar net force |
| Skeleton, torque and rigid dynamics | Torque; Labs 2, 4 | Exact torque example; moment-arm derivative, energy/timestep tests | One fixed upper segment and hinge |
| Energy and numerical accuracy | Energy; Lab 3 | Three integrators against analytic oscillator | Ideal linear spring |
| Deformation, volume and area measurements | Early property labs 1–2 | Independent boundary volume and area × length; real kinematic identities | Prescribed geometry; no material equilibrium |
| Nonuniform axial strain | Early property lab 3 | Logarithmic compliance oracle, midpoint refinement and fixed-end compatibility | Input area profile; no transverse equilibrium or full muscle law |
| Bulk/shear stiffness and lateral confinement | Early property lab 4 | Energy derivatives, independent reduced root, SI wall reactions, residual/feasibility tests and zero-bulk counterexample | Homogeneous elastic ansatz; no spatial shape, global optimality or biological validation |
| Active contraction and release | Elbow; Labs 4, 5, 7 | Continuous activation, lift/release traces; line fibre and spatial spans | Authored activation and force laws; no measured velocity law |
| Passive stretching and tendon | Tendon/tissue; Labs 5, 7 | Series equilibrium, storage/work and spatial span diagnostics | Scalar tension-only tendon and separately labeled bilateral spatial span |
| Anatomical/medical data | Anatomy and actual-data viewer | Primary architecture/indentation sources; 992 licensed-data checks | Static atlas, normalized trial and model parameters stay independent |
| Soft volumes and FEM | Continuum mechanics; Lab 6 | True BᵀDB tetrahedra, patch tests and analytic mesh refinement | Linear, small strain, no contact |
| Faster game/film methods | Fast methods; Lab 6 | Matched implicit target; error, residual and measured cost | Timing tied to stated environment; finite sweeps are approximate |
| Separate skin and fascia | Interfaces; Lab 7 | Independent membrane energy and fascia tethers; ablation | No bending, sliding or skin self-contact |
| Elbow tissue compression/contact | Spatial capstone; Lab 7 | Capsule gaps, sample forces, local J, residual and contact-off comparison | Compliant sampled bone contact; no pressure/CCD guarantee |
| Naive skin weighting | Labs 5, 7 at shared q | Actual transformed bind vertices and measured cell volumes | Force-free geometry; no anatomical accuracy claim |
| Anatomical missed contact | Anatomical apparatus | Saved muscle/bone and tendon/bone failures; positive-area geometric witnesses; derivative and frozen-rule replay checks | Reduced stationary model, finite transverse triangles and axial paths; no CCD or finite tendon radius |
| Unequal 3D blocks and local volume | Property lab 6 | Energy derivative, force root/order, independent mesh volume and actual 3D controls | Separate homogeneous incompressible blocks with ideal bilateral fixtures; no continuous taper or unrestricted stability |
| Fixed-field weighted projection | Projection interlude | 27 exact declarations; independent rational projections and real browser controls | Same field, positive diagonal weights and one constant K; no equilibrium or deformation |
| Uneven local stretch | Nonuniform-volume property lesson | Prescribed map, independently accepted model/geometry audit and six scoped Real contracts | Derivative/integration/mesh/floating-point refinement and force equilibrium remain separate obligations |
| Architecture to force | Material-cut, parallel-group and series-section lab | Twelve preserved Node contracts, seven supplementary symbolic identities and six original Real contracts | Authored geometry/stress examples; Nanson premises, numerical refinement, equilibrium and biological calibration remain separate |
| Formal claims | Visible cards and complete Lean appendix | 115 registered declarations across fourteen source files; fresh full-book check required | 30 integer contracts and eighty-five real claims; no floating-point/biological validation |

The continuum solver's static manufactured solution independently assesses spatial discretization. Its matched implicit reference assesses the algebraic error of a faster solver at the same physical step. The capstone's iteration study instead measures a nonconvex spring/volume model at one mesh. These are different error questions, and their percentages must not be combined into a single “accuracy” badge.

The numerical tests verify derivatives, units, default fixtures, activation continuity, force/energy bookkeeping, deterministic resets and the stated ablations. The browser checks verify that the user can reach those results through controls, view the paired scenes and export the current state. The PDF uses the same canonical text and static solved-geometry illustrations. Neither a passing test count nor a convincing image is a medical validation claim.

The material-response lesson now has five checked real algebra identities for constrained volume, bulk-energy sign and zero conditions, an assumed complementarity implication and virtual-work factorization. Its five integer cards remain separate arithmetic evidence. That specimen's real constitutive derivatives, equilibrium existence/uniqueness and global optimality remain **unfinished**. Three real force/torque/power identities retain their supplied force-pair and geometric assumptions; they do not derive path rates. Eleven actuator claims establish the exact exponential activation bound/constant-input derivative, Gaussian force/derivative/slope bounds, and the series residual's conditional existence, uniqueness, lower-end rejection and positive branch denominator. These results concern the stated real functions and guards; finite-precision refinement, solver termination, implicit velocity at the passive kink and continuous work/energy balances remain unfinished formal obligations. The four real kinematic identities address their stated geometry only.

The chain, equal-cost substep, reduced-basis/probe, sliding-pad and two-way paddle exercises in the fast-methods and interfaces chapters are **unfinished implementation exercises**, with no corresponding interactive controls in this edition. Their theoretical instructions do not establish an implemented demonstration. Laboratory 7's explicitly one-way edge/volume experiment addresses its own stated same-pose question; it does not implement those two-way or sliding exercises.

## Reproduce and inspect the source

The downloadable portable edition includes `build-manifest.json`, the complete checked Lean source/receipt and the original licensed data notices. `spatial-experiment.json` contains the capstone's coordinates and diagnostics; `contributions/continuum_reference/data/reference.json` contains the continuum refinement and matched-cost results. Each contribution's stated runtime and source hashes remain attached to its results.

For a medical or CAD prediction, specify the target output before increasing mesh complexity. Obtain compatible observations, identify parameters and their uncertainty, check boundary/loading assumptions, and distinguish model error from solve error. For game or film use, specify visible defects and permitted latency, then compare the chosen reduced model against its relevant reference. A one-way posed demonstration can be a useful finished teaching example while those application-specific questions remain open.

The progressive property sequence currently implements measured tetrahedral deformation, exact isochoric kinematics and the nonuniform small-strain bar. Independent boundary-volume and area-times-length checks accompany the first two lessons; the bar uses a logarithmic compliance oracle and midpoint refinement. The next [material-response lesson](#compression-bulk-shear-confinement) implements bulk/shear and unilateral confinement controls with visible signed residuals and wall feasibility. [Dissipative load/hold/release](#dissipative-load-hold-release) adds passive axial creep, relaxation and an independent energy ledger. [Unequal blocks under one force](#serial-specimen-volume) adds consistent local strain, current area and independent 3D volume for a two-block incompressible assembly. A force-driven continuous specimen with varying cross section and material coupling of local axial/lateral response is outside this edition. The accepted prescribed nonuniform-volume map and separate-block prerequisite do not establish that material/equilibrium coverage. The [architecture-to-force lesson](#architecture-to-force) now supplies analytic area-weighted aggregation, nominal/Cauchy stress conversion, one-time pennation projection and series exchange. Measured fibre-to-muscle aggregation and physiological force–length/velocity calibration remain planned. None is silently inserted into the anatomical solver.

This candidate excludes new continuous passive-specimen, scalar tension/mass controller and anatomical capstone implementations. Those coverage gaps remain open. Fixed-field projection adds no physical deformation or anatomical completion claim.

The source-only architecture-force integration preserves the independently qualified thirteen-file contribution and all anatomical datasets. Its local lab closure and six exact source registrations still require full-book proof, control, print and release qualification. The historical 109-declaration milestone is not retroactively relabelled as a 115-declaration pass.


## Interactive coverage is separate from proof coverage {#interactive-coverage}

The canonical 27 chapters each have a registered 3D example in the same embeddable
GUI. Several views render lower-dimensional mathematics in a three-dimensional
scene. Source and evidence links accompany every adapter; related checked claims
remain explicitly scoped. The 115 declarations across fourteen sources are the
integrated mathematical inventory, not 115 proofs of the GUI, its floating-point
geometry, or physiological correctness. Atlas and apparatus views retain their
different provenance, and the rejected apparatus trajectory remains a rejection.
