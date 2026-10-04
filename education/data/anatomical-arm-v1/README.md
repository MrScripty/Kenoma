# Anatomical capstone foundation — review candidate

This research package adds actual shared-coordinate atlas geometry, connected source-triangle attachment candidates, an interior-axis/apposition audit, authored belly remeshing, objective finite-strain laws, a jointly solved P2 tissue/tendon/hinge fixture and checked transfer/implicit-step algebra. It is **not yet a tissue-driven anatomical arm**. The production simulator plans remain unchanged. The research book now presents the old strip as an intermediate and adds the coupled fixture, without claiming the anatomical capstone is complete.

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
| `config/attachments.json` | Eight named source-triangle patch candidates, seven named head attachments and explicit shared distal biceps architecture. Estimated fixed origins are not scapular measurements. Mechanical aponeurosis/tendon apparatus remains to be implemented. |
| `config/materials.json` | Units, evidence classes, targets and sensitivity factors. σ0=0.3 MPa is a fixture placeholder, not yet a fixed-end match to Arm26. |
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

Review corrected patches, interior axis and apposition, source region cuts, concave remesh and fixed-origin estimates. Localize remesh outside depth and bone intrusion, then correct geometry rather than relaxing thresholds. Implement shared distal apparatus, weak transverse aponeurosis matrix and mechanically attached passive heads; match three active heads against documented fixed-end **model-reference** targets. The worker-backed engineering fixture already jointly solves tissue and q with state-preserving effort/mass controls; the actual arm must replace its synthetic anatomy and add surface contact. Then check static attachment paths, whole-surface intersections, loaded/released work and the anatomy-matched skinning comparison. Twenty-one narrow compiled claims are now included in the coherent research Markdown/Pages/PDF edition. The old scalar/strip is not presented as satisfying these gates.
