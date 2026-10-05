# Anatomical capstone foundation — review candidate

This research package adds actual shared-coordinate atlas geometry, connected source-triangle attachment candidates, an interior-axis/apposition audit, authored belly remeshing, objective finite-strain laws, a jointly solved P2 tissue/tendon/hinge fixture and checked transfer/implicit-step algebra. It now also contains an in-progress seven-volume reduced P2 anatomical apparatus and actual closest-feature surface/axial-line contact. A complete accepted anatomical lift/release/compression trajectory remains to be established. The production simulator plans remain unchanged. The research book now presents the old strip as an intermediate and adds the coupled fixture, without claiming the anatomical capstone is complete.

Source surfaces and historical notices remain in `../elbow-v1`; no anatomy mesh is copied from an unlicensed source. BodyParts3D currently uses CC BY 4.0; retained original OBJ notices remain intact. Arm26's independent CC BY 3.0 terms and model-reference provenance remain intact. Neither dataset is registered to OpenArm participants. Optional shoulder mesh acquisition failed at the proxy before any bytes transferred; estimated fixed scapular origins can still be used as labeled authored assumptions.

## Reproduce from `education/`

Use the repository's pinned npm installation and official Lean 4.19.0. No additional dependencies or downloads are required.

```sh
npm run anatomy:geometry
LEAN=/path/to/lean-4.19.0/bin/lean npm run anatomy:proofs
npm run anatomy:inspect
node tools/anatomical-fixture-experiment.mjs
node tools/anatomical-bone-collision-audit.mjs
node tools/anatomical-apposition-audit.mjs
npm run anatomy:coupling
node --test tests/anatomical-*.test.mjs
python3 tests/anatomical_inspection.py
python3 tests/coupled_inspection.py
```

Serve `dist/` to inspect `anatomy-inspection/index.html`. The viewer has original atlas, authored region cuts and derived belly views, separate source parts, anterior/lateral/superior/oblique cameras, original-triangle picks, named patch highlights and a **bone-axis-only** angle diagnostic. Muscles stay in reference pose in that diagnostic; no simulated pose is implied. Text controls, source coordinates, classification notices, patch JSON, compiled proof source and receipts provide text alternatives.

## Review files

| File | Evidence and limits |
|---|---|
| `config/landmarks.json` | Actual original triangle/barycentric picks; canonical coordinates reconstructed from original doubles. Float32 rendering hits are retained separately. Authored uncertainty, not measured landmark error. |
| `config/attachments.json` | Eight named source-triangle patch candidates, seven named head attachments and explicit shared distal biceps architecture. Estimated fixed origins are not scapular measurements. The historical patch set remains available; the candidate uses exclusive origin ownership in `attachments-apparatus.json`. |
| `config/materials.json` | Units, evidence classes, targets and sensitivity factors. σ0=0.3 MPa remains a fixture placeholder. Separate fixed-end matching receipts explicitly record much larger fitted scales and failed medical-material acceptance. |
| `generated/arm-geometry.json` | Three distinct closed source bones; seven distinct 252-element, 585-node P2 belly meshes. Authored segmentation/remeshing and centreline fibre guides. No skin. |
| `audit/geometry-quality.json` | Closed/oriented source topology, source/belly volumes, reference positivity and remesh choices. Tests also check opposite internal-face orientation and closed render surfaces. Not a surface-accuracy certificate. |
| `audit/fixture-results.json` | Actual P2-block fixed-end, free/loaded shortening, release, refinement/quadrature and half/double bulk/material receipts. Includes residuals, volume, iterations and local timings. |
| `audit/bone-axis-intersections.json` | Exhaustive triangle-pair broad phase and transverse edge/face crossing tests at bind/0/30/60/90/120°. No crossings found for this candidate; coplanar, grazing, containment and tissue-contact checks remain. |
| `audit/proof-status.json`, `lean-check.txt` | Fresh Lean 4.19.0 kernel checks of two exact scaled-integer attachment-power identities. Precise implementation/test links, assumptions and limitations included. |
| `audit/interior-axis-fit.json`, `apposition-results.json` | Source articular regions, authored interior axis, explicit finite collision-constrained centre search, 25 tested poses and sampled articular distances. Cartilage and continuous motion are not certified. |
| `audit/coupling-results.json` | Jointly solved tissue/tendon/hinge pulse, mass event, three time steps, work defects and matched unchanged-material L-BFGS/Newton profiles. Engineering fixture only. |
| `audit/coupled-proof-status.json`, `coupled-lean-check.txt` | Seven additional compiled integer-numerator claims for angular momentum/work, nonnegative defects, mass events, toe storage and P2 partition. No float or biology validation. |

The 120 mm engineering block carries 36 N at fixed ends for a=0.1. At a=0.05 it shortens to 70.468 mm freely and 99.723 mm against 12 N; release returns to 120.000 mm. These are results of the authored constitutive fixture, **not measurements or calibrated muscle predictions**. All recorded solves converged under their stated residuals. Release required 3975 accepted iterations, and the refined 32-point case is substantially slower: this does not demonstrate an interactive performance budget. Four-point/refined-quadrature length differences and mesh sensitivity are explicit in the receipt; they do not prove the absence of locking in arbitrary anatomical meshes.

## Next acceptance gates

Review corrected patches, interior axis and apposition, source region cuts, concave remesh and fixed-origin estimates. Localize remesh outside depth and bone intrusion, then correct geometry rather than relaxing thresholds. Implement shared distal apparatus, weak transverse aponeurosis matrix and mechanically attached passive heads; match three active heads against documented fixed-end **model-reference** targets. The worker-backed engineering fixture already jointly solves tissue and q with state-preserving effort/mass controls; the actual arm must replace its synthetic anatomy and add surface contact. Then check static attachment paths, whole-surface intersections, loaded/released work and the anatomy-matched skinning comparison. Twenty-three narrow compiled claims are now included in the coherent research Markdown/Pages/PDF edition. The old scalar/strip is not presented as satisfying these gates.

## Actual-arm apparatus candidate

The additive candidate uses `generated/arm-reference.json`, `config/attachments-apparatus.json` and a reproducible `config/apparatus-routing.json`. Original atlas, remesh and historical attachment files are preserved. There are 63 Galerkin displacement coordinates per head, two shared nine-coordinate distal apparatuses and one jointly solved rigid elbow angle: 460 generalized coordinates total. Source-patch faces drive distributed interfaces and insertion fans. Biceps internal strips, tendon areas, fixed frictionless routing guides and transverse sheet laws are authored approximations, not anatomical segmentations.

The fixed-end recheck in `audit/modal-fixed-end-recheck.json` matches the independent Arm26 actuator-model targets. Fitted scales of 3.60–20.38 MPa and full-activation minimum local J of 0.595–0.638 prevent a medical-material validation claim. Recorded teaching bulk/shear properties remain unchanged. The radial patch audit separately exposes several-millimetre gaps.

Reproduce the candidate prerequisites:

```sh
node tools/repair-anatomical-reference.mjs
node tools/partition-anatomical-origins.mjs
node tools/anatomical-radial-apposition.mjs
node tools/verify-anatomical-matches.mjs
node tools/build-anatomical-routes.mjs
LEAN=/path/to/lean-4.19.0/bin/lean python3 tools/check_arm_proofs.py
node --test tests/anatomical_*.test.mjs
```

Routing uses the total length of each polyline in one integrated tendon law, with equal leg tension, explicit guide reactions and exact rotating-guide derivatives. Routes have fixed topology; this is not a sliding tendon-wrap model. Resting and stepping routines reject failed reduced force residuals, finite whole-boundary crossings, axial-path crossings and sampled penetration. They preserve the accepted state on failure. The five-point axial contact quadrature does not replace the segment audit.

The two new Lean claims establish exact integer-numerator algebra for an upward-positive mass-energy event and a **supplied** shared-guide equilibrium. They do not prove numerical state preservation, equilibrium, float correctness or biological fidelity; independent tests and receipts are linked from the book.

## Actual apparatus acceptance checkpoint

The current held rest passes a fresh source-bound reduced equilibrium and finite-pose body/path recheck. A loaded step at effort 0.04, mass 0.5 kg and h=0.01 s fails the 120-iteration force gate. A quarter-load continuation stage also fails. No anatomical lift/release trajectory is accepted. Shared guide triangles are interpolation scaffolds, not resolved contact solids.

Recheck the cache with `node education/tools/verify-anatomical-arm-rest.mjs`; independently replay the preserved earlier tendon intrusion with `node education/tools/replay-rejected-arm-v1.mjs`. Build the accessible resting-state viewer with `node education/tools/build-anatomical-arm-inspector.mjs`. The portable continuation rerun tool is `education/tools/anatomical-activation-continuation.mjs`; its temporary output does not overwrite the historical receipt.
