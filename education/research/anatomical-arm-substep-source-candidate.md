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

Depth four limits a request to 31 attempted solves and 16 accepted leaves. Depth
zero bypasses the transaction and calls the original step with the original state
and options, returning the original result and propagating its exceptions. This is a solve-attempt bound, not a bound on all
material callbacks or a runtime guarantee. Accepted leaf receipts remain ordered
and visible in `substepIntegration`; the original last-step receipt and state
history remain available. Custom full-step warm starts remain usable at depth
zero; subdivided intervals require the current-state warm start. Opt-in invalid effort,
duration and subdivision depth refuse before changing contact state. Default
domain behavior, including legacy coercible inputs, is preserved.

This is **SOURCE_UNIT_TESTED_NOT_NUMERICALLY_VALIDATED**. No actual recovery,
time convergence or anatomical acceptance has been demonstrated. Default browser
behavior remains a single attempt; no new slider, automatic campaign, publication
or numerical allowance is introduced. Source provenance for any later run must
include the new helper alongside the changed arm/worker modules.

Twenty-two tests use metadata callbacks only, including the actual public wrapper
compiled in isolation with injected callbacks. They do not import the original
arm/material/element/solver modules or evaluate an atlas sample. Tests cover
whole/half/nested intervals, late failure/exception rollback, contact-rule
restoration of every actual mutable contact recipe field, complete state/history/
mass-event preservation, attempt bounds, bad opt-in inputs, warm-start behavior,
exact default state/options/result aliases, original exception propagation, actual
worker message shape and source-byte preservation of the original solve and worker
statements. Derived-sample rebuild callbacks in the contact test use metadata only;
the actual rebuild mathematics is source-reviewed, not executed on atlas samples.

Independent review of parent `b43195077d8fd4ef9238c718e85657346e5f83cd`
found default-path cloning, exception conversion and extra operations/message
properties. This successor corrects those findings with a depth-zero bypass and
conditional worker forwarding/metadata. The helper itself is unchanged. Contact
rollback restores numerical recipe values and rebuilt sample values, not replaced
array/Map identities. State rollback returns the exact caller state. Transient
worker progress messages cannot be recalled and do not commit state/history. An
arbitrary externally supplied onIteration callback can cause effects outside this
transaction; the actual worker callback only posts scalar progress. Capture/restore
requires a valid recipe. No additional persistent physical solver writes were found.

The normal inspector build still correctly refuses the changed arm/worker hashes
against historical rest evidence. No historical hash rebinding or guard bypass is
provided. A fresh source-bound recheck is necessary before numerical/browser use.

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

**Future validation proposal only — not executed or authorized.** Replace the
parent's 16-field proposal: it was too small even for the retained load receipt's
229 objective evaluations. Four separate, sequential process invocations are the
minimum proposed control/replay set; no sweep, trajectory, refit or extra interval
is authorized by this document. Abort the entire set if run A refuses.

All inputs are immutable Git blobs at
`0b83819ad3fdaed7405c6bbe617bc01640eef914`, with SHA-256:

| Input under education/data/anatomical-arm-v1/ | SHA-256 |
|---|---|
| generated/arm-reference.json | `1b80c1d3d9f2eb4370cd298f58f5e9c582625574f27072f6d3a1ea898ce4c036` |
| config/attachments-apparatus.json | `070fee738e73e127e334ee5cbe680cb622f100396ad0728eb9df6723c2232389` |
| config/apparatus-routing.json | `b8580e8158e17730b65b64d0fdbe0f1cbbafc76235b9a5f0c2b01020818cd93f` |
| audit/modal-fixed-end-results.json | `b0eeecdade262b682279d9ebeb7a8147a4525a992976a85afc0ce5e63270d8b4` |
| audit/arm-rest-results.json | `8dc23d896adce4b428f39cb172d76f3c74c828f49c2007c66155e45e8ea359c7` |
| audit/arm-rest-recheck.json (prior evidence only) | `3d1159de78088207320d3b19b17ffc83cb08a531781e26715c8167dd7efbecab` |

Use exactly the 460 frozen coordinates and scalar values in the original rest
state: q=0.2841100888248933 rad, omega=0, activation=0, effort=0, mass=0.5 kg,
time=0, step=0, work=0, empty history/massEvents. It has no contactRule; use the
unchanged initial contact recipe prepared from the pinned geometry/routing data.
Copy the exact original parameters/contactParameters, without overrides. Retain
subdivided32 quadrature, 63 modes/head and the existing material fits. Every run
constructs its own fresh model; no state or contact cache flows between runs.

| Run | Exact action | Maximum attempted solves | Configuration evaluation ceiling | Wall ceiling |
|---|---|---:|---:|---:|
| A | Fresh held-rest check at the frozen coordinates, activation 0, hessian=false; no optimizer | 0 | 1 | 60 s |
| B | Actual public step, effort=0.04, h=0.01 s, maxIterations=120, default depth zero | 1 | 512 | 240 s |
| C | Same frozen input/options, explicit subdivisionDepth=1 | 3 | 512 | 240 s |
| D | Two explicit original/default steps of h=0.005 s, effort=0.04, maxIterations=120; second starts from first accepted state | 2 | 512 | 240 s |

Count EVERY entry to the actual configuration/evaluateApparatus path: prior
fields, repeated coordinates, Hessian objectives, rejected/partially evaluated
trials, accepted fields, quadrature-event evaluations and independent replay
checks. The ceiling is cumulative per process across all attempts/replays; it is
not per half step. No memoized repeat is free. The full set is at most 6 attempted
solves and 1,537 configuration entries. Bound source-controlled Newton work at
120 iterations per frozen rule, seven rules, 40 backtracks, 14 shifted-PCG
attempts and 300 PCG iterations; the tighter configuration ceiling stops a run
before the nominal 33,607-objective-evaluation per-solve maximum.

There are exactly 7*252*32=56,448 muscle-point calls per complete configuration,
585 routed tendon branches plus 48 internal aponeurosis branches (633
`tendonMaterial` calls), and at most 56,448 additional `materialTensor` calls
when Hessian=true. Charge partial evaluations too. Per B/C/D process cap
muscleMaterial=28,901,376, tendonMaterial=324,096, materialTensor=28,901,376.
Run A cap muscleMaterial=56,448, tendonMaterial=633, materialTensor=0. Count
these three callback classes separately; tendonSegment is the wrapper of the
same tendonMaterial call, not an additional constitutive evaluation. Analytic
Hessian-vector products do not re-evaluate material; bound them separately at
3,528,840 per attempted solve (including adaptive-agreement products), hence
21,173,040 over six attempts. Contact/tree/audit work remains subject to wall and
memory ceilings even though it is not a material callback.

Each process: owned peak RSS <=1 GiB, observed shared cgroup usage <=16 GiB,
output <=4 MiB and stdout/stderr <=256 KiB. Sequential aggregate: wall <=780 s,
output <=16 MiB, transcript <=1 MiB. Include all descendants and staging/temp
files. Abort on unavailable monitoring or inadequate scratch space. Proposed
closed output inventory: manifest.json, rest-recheck.json, default.json,
adaptive-depth1.json, explicit-halves.json, comparison.json, resource-receipt.json
and transcript.log under one new private output directory; receipts embed
accepted leaf states/contact rules and bounded traces, never full per-trial
Hessians. Each run's 4 MiB allowance includes its manifest/resource contribution.
Never truncate a scientifically required payload into a success; oversized
results are resource refusals. Preserve every old source, receipt and inventory.

Before numerical authorization, a separate source-reviewed execution harness
must implement these counters, an external wall/RSS/output watchdog and the
closed inventory. Instrument only the future isolated run copy through a
hash-recorded loader/call interposition; do not rewrite laws, current sources,
thresholds, caches or environment protections. A latched budget exception must
be a non-RangeError so the existing Newton backtrack catch cannot swallow it.
It must terminate retries and discard all provisional state/contact/history.
Supervisor kill/refusal is RESOURCE_INCONCLUSIVE, never solver failure or a
passing rollback test. Persist input snapshots outside the worker and verify
unchanged input identities after each refusal. The present source contains
solve-attempt bounds only; no claim that these resource caps are already active.
Pin the exact reviewed successor commit, all transitive module hashes including
the new helper, the execution harness/loader/watchdog hashes, Node version and
these input hashes in the future manifest BEFORE import/evaluation. This proposal
is not run-ready until that harness is reviewed. No downloads or dependencies
are needed for the proposed CPU run.

Keep all existing acceptance criteria: finite gradient max <=1e-4 N (joint held
out only for rest), original material domain J>1e-6, original Armijo/Newton
criteria, zero finite transverse crossing pairs, accepted routing and zero
sampled bone/soft penetration. Replay also requires zero sampled tendon
penetration as the existing independent trajectory verifier does. Check finite
activation/time/velocity lineage at 1e-14 and recomputed residual, impulse/work,
quadrature-event and energy receipts at 1e-9 using the existing verifier formulas.
For each accepted leaf independently evaluate four hessian=false configurations
(prior old rule, old state at final rule, old state at final activation, final
state), all charged to that run's 512 ceiling. Keep the joint inertial/gravity/
stop/damping term in the residual. Report nonlinear work defect; do not require
it to vanish or hide the reference-quadrature event. No anatomy, continuum,
force-velocity or physiological qualification follows. Do not run the old
verifier unchanged: its fixed output paths would overwrite retained evidence.

Evidence interpretation is preregistered. Parent mock tests only establish
transaction logic, not numerical recovery. The retained load receipt at
`audit/viewer-cache-load-results.json` has SHA
`f1b0bfc8ab97ec8daaee533488b3098fd38535802c28ec6c25bfbdc5ecb3d07f`;
its 229 objective evaluations use a predecessor contact-refinement hash. The
15-step contact trajectory receipt SHA is
`a74bd8fa9fd7bc3745ed42c32af75fc44692408d081b2070ceeefa63a0db35a9`;
its first load completed in about 96.6 s but its contact module also predates the
current derivative operator. Fresh finite-state rechecks support the retained
states' reduced gates, not a matched failed solve on this successor. The old
rejected load SHA
`713c4aee49e5d8856e154b728b6cc127aa3a2383e83aa5720013cdf4060650ca`
uses earlier arm/contact source and cannot be claimed as the matched B failure.
Thus this chosen minimal interval is a safety/control test, not a known failure
recovery test. Do not search new intervals when B passes.

If B completes with an ordinary unchanged solver refusal, while C completes the
same duration through two accepted halves and D independently reproduces their
state/contact/history/work values and all original/replay gates, this supports
substepping as a remedy for this one reduced interval only. If B and C accept on
the first whole attempt, compare their scientific state/receipt values exactly;
that supports default compatibility but establishes no remedy. D may differ
from whole-step B through time discretization and is reported, not forced to
match. If completed halves refuse, numerical recovery is refuted for this
interval at depth one; a rollback or same-half replay mismatch refutes source
correctness. Any cap/exception, failed rest gate or missing full receipt is
inconclusive for remedy and ends this set. No restart or raised ceiling follows.

Run only the metadata tests for this source candidate:

```bash
node --test education/tests/anatomical-arm-substeps.test.mjs
```
