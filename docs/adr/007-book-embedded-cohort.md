# Book and embedded GUI cohort

## Ownership and integration boundary

This branch integrates the reviewed 115-claim book candidate (PRs 11–13,
remote head `74b0e93230a09ffd51a3a250d9ba60a6364e9e87`) and the isolated
poser (`7eec7ef00c005ac3168e51cb93cb4b212fe31e36`). The CI-hook repair has
the same source bytes as the reviewed remote candidate. Local reconstruction
commits are not represented as new proof evidence.

Owned files: `browser/` presentation, book prose and references, educational
web adapters, build/qualification tools, tests and relevant workflow steps.
No changes to biomechanical constitutive laws, solver algorithms, research
acceptance thresholds, historical data, rejected evidence, or original Lean
theorem statements. The existing 115 declarations must be freshly checked
for the integrated build; browser manipulations are not additional proofs.

The simple poser keeps its own graph, Rust/WASM binding, worker and SQLite
contract. A shared viewport/presentation layer has no dependency on research
engines. Lesson adapters own their educational model and expose explicit
mount/reset/dispose lifecycles. Opening a chapter does not start a campaign.

## Reference and visual scope

The parent inspected the actual Rheon projection page in a cloud browser:
`https://mrscripty.github.io/Rheon/labs.html#projection`. Its WebGL fallback
was visible; no rendered-scene appearance was inferred. Verified DOM tokens:
paper #fafaf5, ink #18363d, muted #52676d, teal #067d91, rule #d8e1df,
viewport #e9f1ee and white cards; Georgia headings, system-ui body. Adapt
the rail and viewport/control split responsively. Poser controls stay gizmos.

## Chapter gap inventory

| Chapter | Existing presentation | Required shared-GUI view |
|---|---|---|
| Reading a moving body | None | Coordinates, units, illustrative mannequin |
| Force | 3D, reduced | Force vectors and balance |
| Torque | 3D, planar | Application point and moment axis |
| Energy | 3D and chart | Spring/mass motion and energy ledger |
| Deformation properties | SVG | Reference/current solid and determinant |
| Nonuniform volume | SVG | Existing mapped prism and local Jacobians |
| Architecture to force | Tables/controls | Fibres, material cuts and projected force |
| Material response | SVG | Existing reduced specimen and boundary assumptions |
| Dissipative response | SVG/chart | Existing specimen and finite work ledger |
| Serial specimen | 3D | Two separate homogeneous blocks |
| Anatomy as evidence | None | Source-aware atlas inspection |
| Actual anatomical data | 3D atlas | Geometry and separate provenance streams |
| Muscle physiology | None | Explicitly synthetic actuator/path |
| Force-driven elbow | 3D | Existing hinge and moment balance |
| Tissue and rendered skin | None | Independent artistic pose deformation |
| Tendon/tissue coupling | 3D | Existing reduced series model |
| Continuum fundamentals | None | Reference/current tetrahedron |
| Fast methods | None | Scoped reference/approximation comparison |
| Spatial continuum | 3D | Existing discretization/solver diagnostics |
| Pressure projection | Abstract 2D | Weighted sample vectors, not body pressure |
| Interfaces/skinning | None | Pose/attachment maps and explicit missing physics |
| Spatial arm capstone | 3D | Existing one-way quasistatic model |
| Coupled mechanics | Linked 3D | Existing fixture and work/residual diagnostics |
| Anatomical apparatus | Linked 3D | Preserved accepted/rejected states |
| Coverage/evidence | None | Models and evidence boundaries |
| Research path | None | Implemented/missing stages |
| Sources | None | Geometry, coordinate frames and provenance |

## Qualification and publication

Compact claim cards retain visible status, assumptions and limitations.
Keyboard-accessible expansion exposes exact statements and source/receipt
links. All 115 cards and fourteen full sources remain in the readable PDF.
Every chapter has a relevant 3D adapter with declared evidence class and
bounded inputs. Test real controls, mobile/desktop/subpath embedding,
switching/disposal, no-WebGL/no-JavaScript alternatives and print coverage.
Fresh integrated Lean, book, browser/PDF and CI evidence precede merging.
Pages publication remains a separate action. No unrelated physical campaign.
