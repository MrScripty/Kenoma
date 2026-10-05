# What the experiments establish {#coverage-and-evidence}

The original requested subjects appear below with their working example, evidence and remaining model boundary. The table distinguishes an implemented teaching question from a clinical claim. All geometry in Laboratories 1–7 is authored and schematic; the actual-data viewer retains its independent atlas and recording provenance.

| Subject | Working chapter / example | Check or evidence | Boundary |
|:--|:--|:--|:--|
| Force, coordinates and units | Force; Lab 1 | Analytic motion; exact pair cancellation | Constant planar net force |
| Skeleton, torque and rigid dynamics | Torque; Labs 2, 4 | Exact torque example; moment-arm derivative, energy/timestep tests | One fixed upper segment and hinge |
| Energy and numerical accuracy | Energy; Lab 3 | Three integrators against analytic oscillator | Ideal linear spring |
| Active contraction and release | Elbow; Labs 4, 5, 7 | Continuous activation, lift/release traces; line fibre and spatial spans | Authored activation and force laws; no measured velocity law |
| Passive stretching and tendon | Tendon/tissue; Labs 5, 7 | Series equilibrium, storage/work and spatial span diagnostics | Scalar tension-only tendon and separately labeled bilateral spatial span |
| Anatomical/medical data | Anatomy and actual-data viewer | Primary architecture/indentation sources; 992 licensed-data checks | Static atlas, normalized trial and model parameters stay independent |
| Soft volumes and FEM | Continuum mechanics; Lab 6 | True BᵀDB tetrahedra, patch tests and analytic mesh refinement | Linear, small strain, no contact |
| Faster game/film methods | Fast methods; Lab 6 | Matched implicit target; error, residual and measured cost | Timing tied to stated environment; finite sweeps are approximate |
| Separate skin and fascia | Interfaces; Lab 7 | Independent membrane energy and fascia tethers; ablation | No bending, sliding or skin self-contact |
| Elbow tissue compression/contact | Spatial capstone; Lab 7 | Capsule gaps, sample forces, local J, residual and contact-off comparison | Compliant sampled bone contact; no pressure/CCD guarantee |
| Naive skin weighting | Labs 5, 7 at shared q | Actual transformed bind vertices and measured cell volumes | Force-free geometry; no anatomical accuracy claim |
| Anatomical missed contact | Anatomical apparatus | Saved muscle/bone and tendon/bone failures; positive-area geometric witnesses; derivative and frozen-rule replay checks | Reduced stationary model, finite transverse triangles and axial paths; no CCD or finite tendon radius |
| Formal claims | Visible cards and complete Lean appendix | 25 fresh kernel-checked declarations across four source files | Exact integer contracts, not floating-point/biological validation |

The continuum solver's static manufactured solution independently assesses spatial discretization. Its matched implicit reference assesses the algebraic error of a faster solver at the same physical step. The capstone's iteration study instead measures a nonconvex spring/volume model at one mesh. These are different error questions, and their percentages must not be combined into a single “accuracy” badge.

The numerical tests verify derivatives, units, default fixtures, activation continuity, force/energy bookkeeping, deterministic resets and the stated ablations. The browser checks verify that the user can reach those results through controls, view the paired scenes and export the current state. The PDF uses the same canonical text and static solved-geometry illustrations. Neither a passing test count nor a convincing image is a medical validation claim.

## Reproduce and inspect the source

The downloadable portable edition includes `build-manifest.json`, the complete checked Lean source/receipt and the original licensed data notices. `spatial-experiment.json` contains the capstone's coordinates and diagnostics; `contributions/continuum_reference/data/reference.json` contains the continuum refinement and matched-cost results. Each contribution's stated runtime and source hashes remain attached to its results.

For a medical or CAD prediction, specify the target output before increasing mesh complexity. Obtain compatible observations, identify parameters and their uncertainty, check boundary/loading assumptions, and distinguish model error from solve error. For game or film use, specify visible defects and permitted latency, then compare the chosen reduced model against its relevant reference. A one-way posed demonstration can be a useful finished teaching example while those application-specific questions remain open.
