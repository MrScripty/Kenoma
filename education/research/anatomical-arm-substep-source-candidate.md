# Actual anatomical arm audit and transactional substep source candidate

9 October 2026. Baseline actual-arm source/data commit
`0b83819ad3fdaed7405c6bbe617bc01640eef914`. Its arm, worker, apparatus and
material bytes match the retained mobile successor. This audit reads existing
datasets/results only. No new material evaluations, physical fields, downloads,
numerical campaigns, browser resting rechecks or book changes were performed.

## Requirements versus current implementation

| Requirement | Actual retained implementation | Remaining limitation |
|---|---|---|
| Anatomical skeleton and named muscles | Shared-coordinate BodyParts3D humerus FJ3368, radius FJ3349 and ulna FJ3391; seven separate derived P2 bellies: brachialis FJ1486, biceps FJ1512/FJ1478, triceps FJ1480/FJ1477/FJ1479 and brachioradialis FJ1487. Each belly has 252 P2 tetrahedra and 585 nodes. | Seven-section/16-perimeter remesh and reference repairs are authored atlas-derived approximations. Axis registration requires anatomical review; shoulder/supination are fixed. Radial-crown/capitellum sampled median gaps span 5.801–9.553 mm over retained poses. No cartilage or hand mesh; grip is an authored extension. |
| Distributed bone attachments and connective architecture | Recorded source face IDs, barycentric anchors and area weights; disjoint triceps origin ownership; shared free biceps/triceps guide triangles, tensile fans/common distal branches, intramuscular sheets and weak transverse matrices. Brachialis/brachioradialis use distinct distal patches. | Attachment selections, 20% area fractions, sheet thickness, branch routing and fixed estimated scapular origins are authored. Three-node guide sheets and axial polylines are not resolved tendon/aponeurosis solids or measured pennation architecture. The cortex-offset route is frictionless/fixed-topology; finite-radius tendon contact is absent. |
| Effort and mass as primary controls | Native effort and point-mass sliders in the anatomical inspector; angle/activation/tension are outputs. Effort drives brachialis and both biceps, with 0.04/0.06 s activation/release constants. Triceps and brachioradialis remain attached/passive. Mass changes preserve state and record an external energy event; reset restores a source-bound rest cache. | One common flexor excitation, no extensor effort control or physiological recruitment model. Force–velocity multiplier is one; transient speeds are not physiological predictions. Current inspector range is 0–2 kg, not a clinical limit. |
| Tissue owns lifting torque | Active/passive continuum, tendon, interface and contact gradients supply the elbow generalized force. No independent scalar lifting torque is added. One implicit rigid elbow DOF shares the solve; Arm26 segment inertia/mass are mapped reference-model values and tissue mass is counted once. | Local quasistatic sag/inertia omitted. Rigid articulation is not cartilage compression or physiological joint loading. |
| Constitutive model | One objective isochoric matrix + log-J bulk + exponential tensile fibre potential; one fixed-activation force–length solve potential and matching Piola/Cauchy stress. Tensile tendon has slack, toe and linear regions. Authored mu=1 kPa, K=1 MPa, kf=20 kPa, b=6, tendon E=50 MPa/toe=0.03. Material guard remains J>1e-6. | No measured tissue calibration or physiological force–velocity. Historical Arm26 force fits use sigma0=3.59933/8.70839/20.3781 MPa; they are reference-model fits, not human validation. |
| Equilibrium, compression and convergence | 63 Galerkin coordinates/head, shared guides and scaled joint coordinate; analytic derivatives, Newton/CG, regularized preconditioning, energy-decreasing trials, geometry retraction and frozen contact-rule refinement. Original modal force gate is 1e-4 N. Retained 15-step reduced lift/release recheck passes its finite gates. | Full nodal equilibrium is not established. Frozen calibration 256-point reduced residuals are 0.132179/1.66242/0.674166 N; complete free nodal maxima are 64.067641/52.058855/54.223684 N, all above 1e-4 N. Local compression and displacement/integration resolution remain unresolved. |
| Supported contact/skin comparison | Actual atlas bone surfaces, repaired belly boundaries and finite transverse/axial-line audits; same repaired anatomy and q for naive bone-weight comparison. | Finite poses do not qualify grazing, coplanar, continuous motion, solid-sheet or finite-radius tendon contact. The weighting comparison is authored longitudinal weighting of the same tissue, not skin. No external skin/subcutaneous envelope exists. |

The original fixed-end fits, rejected steps, dense/enriched failures and S4
results retain their own scopes. S4 passes finite integration comparisons on a
16-element patch at two fixed fields; 236 outside-patch elements, true error,
stationarity and anatomical completion remain unqualified. Its pass does not
upgrade the 32-point calibration or the reduced whole-arm trajectory.

## Concrete implementation

The specification already calls out absent automatic step subdivision. This
candidate implements it in the **actual anatomical arm API and CPU worker**, not
as another viewer or residual diagnostic. `anatomical-arm-substeps.mjs` coordinates
the existing stepper without replacing any tissue law, solve objective, force
threshold, attachment or geometry gate. The original step body remains
byte-identical after its internal function rename.

`stepAnatomicalArm` accepts optional `subdivisionDepth` from zero to four; the
worker forwards that option, defaulting to zero. A refused interval may be tried
as two sequential halves. Every accepted leaf runs the original solver and its
original finite geometry/force gates. Both halves must succeed before the whole
requested interval is committed. A late refusal discards provisional coordinates,
time, activation, mechanical work, history and contact-rule changes. Contact
snapshots use the existing structured-clone recipe interface. Unknown exceptions
are terminal and do not authorize subdivision retries.

Depth four limits a request to 31 attempted solves and 16 accepted leaves; depth
zero performs one attempt. This is a solve-attempt bound, not a bound on all
material callbacks or a runtime guarantee. Accepted leaf receipts remain ordered
and visible in `substepIntegration`; the original last-step receipt and state
history remain available. Custom full-step warm starts remain usable at depth
zero; subdivided intervals require the current-state warm start. Invalid effort,
duration and subdivision depth refuse before changing contact state.

This is **SOURCE_UNIT_TESTED_NOT_NUMERICALLY_VALIDATED**. No actual recovery,
time convergence or anatomical acceptance has been demonstrated. Default browser
behavior remains a single attempt; no new slider, automatic campaign, publication
or numerical allowance is introduced. Source provenance for any later run must
include the new helper alongside the changed arm/worker modules.

Sixteen tests use metadata callbacks only, including the actual public wrapper
compiled in isolation with injected callbacks. They do not import the original
arm/material/element/solver modules or evaluate an atlas sample. Tests cover
whole/half/nested intervals, late failure/exception rollback, contact-rule
restoration, history/work preservation, attempt bounds, bad inputs, warm-start
behavior and source-byte preservation of the original solve and worker statements.

## Missing prerequisites and bounded validation proposal

The primary scientific correction still starts with isolated calibration:
implement and independently review a resolved displacement/integration solver
(and, if justified, a stable displacement/pressure formulation), then obtain
stationary locally admissible calibration states under justified material
parameters before refitting or claiming credible attached-arm behavior. The
existing full P2 topology and retained nodal-force operators supply a starting
point, but a validated resolved solver/coupling is not supplied by the reduced
stepper or the fixed-state projection proofs. No material retuning was chosen.

Measured/refined tendon/aponeurosis surfaces and fibre architecture are absent;
the current engineering apparatus must retain its authored labels. Reviewed
shoulder landmarks would be needed for measured-origin claims, although the
specification permits estimated fixed origins for its engineering milestone.
External skin requires a supported surrounding-tissue/subcutaneous envelope and
interfaces; the present seven exposed bellies cannot supply it. No cylinders or
invented skin surface were substituted.

**Future validation only:** first independent source review and mock-worker
message/rollback tests, with zero material calls, owned RSS <=1 GB, wall <=60 s,
output/transcript <=1 MiB. A later numerical experiment should be separately
preregistered on one retained arm interval with depth one (maximum three attempted
solves/two accepted leaves), fixed original materials/gates, no refit and no
trajectory campaign. Require explicit field/material-callback counters and a
closed output inventory before authorization; proposed ceilings are 16 evaluated
trial fields, 4,000,000 material callbacks, owned RSS 1 GB, shared cgroup 16 GB,
wall 240 s, output 16 MiB and transcript 1 MiB. Count every initial/repeated,
Hessian and rejected-trial evaluation; reaching a limit must roll back the whole
interval and preserve failure receipts. These proposed counter/cap controls are
not implemented or authorized by this candidate. A control comparison with two
explicit half steps and independent force/geometry/work recheck is a separate
future scope, not part of the proposed one-interval allowance. Even numerical
recovery would only qualify reduced-step execution, not the open scientific gates.

Run only the metadata tests for this source candidate:

```bash
node --test education/tests/anatomical-arm-substeps.test.mjs
```
