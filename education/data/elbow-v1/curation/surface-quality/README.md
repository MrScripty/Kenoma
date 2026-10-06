# Quality of the ten retained arm surfaces

All ten assets can serve as **reduced reconstructed atlas visual references**.
None is established as a volumetric simulation input. This audit leaves every
original OBJ, SI coordinate array, landmark, attachment and mechanics file unchanged.
It performs no acquisitions, automatic repairs or anatomical reconstruction.

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution
4.0 International. Original historical OBJ notices are preserved. The exact
version, current archive license, TARO-derived provenance and missing tissue
inventory remain owned by [`../source-inventory.json`](../source-inventory.json).
This is Release 4.0 IS-A at 99% polygon reduction, not direct segmentation of an
observed arm and not clearance of exact 4.3 assets.

## Measured file diagnostics

[`quality.json`](quality.json) binds these results to the existing inventory and
[`input-contract.json`](input-contract.json). The inventory audit verifies OBJ leaf
FMA/FJ identities, acquisition-time SHA-256, original triangle arrays and exact
existing `position_mm * 0.001` conversion. Bounds, extents, areas, edge lengths,
topology and component face IDs are in the machine-readable evidence.

| Source asset | Raw boundary edges | Exact-coordinate component face counts | Coincident triangle excess | Strict transverse self-crossing pairs |
|---|---:|---|---:|---:|
| FJ3368 right humerus | 564 | 3784 | 0 | 0 |
| FJ3349 right radius | 132 | 672 | 0 | 0 |
| FJ3391 right ulna | 198 | 834 | 0 | 0 |
| FJ1486 brachialis | 742 | 1738, 2, 2, 2, 2 | 4 | 8 |
| FJ1512 short biceps head | 1294 | 1842, 2, 2, 2, 2, 2, 2, 2 | 7 | 9 |
| FJ1478 long biceps head | 638 | 1416, 8, 2 | 1 | 0 |
| FJ1480 medial triceps head | 378 | 830, 2 | 1 | 0 |
| FJ1477 lateral triceps head | 826 | 2602, 2, 2 | 2 | 0 |
| FJ1479 long triceps head | 576 | 1586, 2 | 1 | 0 |
| FJ1487 brachioradialis | 1776 | 4874 | 0 | 0 |

All ten have raw index seams and multiple raw face-connected components. An
**in-memory exact-coordinate diagnostic** merges identical XYZ positions with
zero tolerance; it does not modify or save a mesh. After that diagnostic all ten
have zero boundary/nonmanifold edges, no vertex fan defects, no zero-area triangles,
and no orientation-parity contradictions. Each has one principal component with
Euler characteristic 2 and a positive component-relative signed-volume diagnostic.

However, six muscle assets also contain **17 zero-volume closed shell components**.
Sixteen are coincident triangle pairs; long biceps additionally has an eight-face
zero-volume component. Opposite coincident triangles can satisfy the edge-closure
and orientation tests while enclosing no solid. The exact small-component source
faces and coincidence groups are retained in `quality.json`; none was removed.
The geometry owner's world-origin winding convention reports eight changes in
short biceps and two in lateral triceps, all in zero-volume shells. Their positive
volume sign is not meaningful. No principal component requires a winding change
under this diagnostic. Translation-stable component volumes expose zero shells;
neither volume formula proves geometric embedding.

The existing [`anatomical-bone-collision-audit.mjs`](../../../../tools/anatomical-bone-collision-audit.mjs)
strict transverse segment/triangle predicate was ported to a read-only NumPy
batch implementation. Exhaustive AABB candidate testing finds eight brachialis
and nine short-biceps triangle pairs; every detected pair is recorded. It finds
no transverse crossings for the three bone pairs in **original atlas coordinates**.
Coplanar overlaps, tangencies, endpoint/edge crossings, nesting, incident-face
foldovers and full muscle/bone assembly intersections remain unqualified.
Fixed SI numerical margins are disclosed. **Zero detected crossings is not full
self-intersection clearance or a watertight embedded-solid certificate.** No
qualified complete self-intersection tool was available in the existing workflow.

## Coordinates, landmarks and attachment coverage

Original axes are +X anatomical left, +Y posterior and +Z superior. Scaling mm to
m is the only applied coordinate transform. No translation, centering, rotation,
joint fitting or pose normalization occurs. Exact MRI acquisition pose and calibrated
joint angles are unknown. The existing fitted axis, bind angle and authored grip
extension are included for traceability but are **not applied** and are not observed
specimen pose. These assets must not be combined with the NLM cadaver or OpenArm
participant as one observed anatomy.

Eleven existing authored bone landmarks reconstruct from original face indices
and barycentrics within 1e-12 m. All eight authored bone patches have verified
source-face areas and sample positions and are connected after exact-coordinate
welding. Brachialis' ulna patch has two raw index components because of a seam;
raw and welded connectivity are explicitly distinct. All seven muscle head
attachment mappings reuse `attachments-apparatus.json`. Three proximal shoulder
origins remain atlas-tip estimates with **authored**, unmeasured 15 mm uncertainty.
Landmark uncertainty radii are likewise authored. Surface-pick review remains
pending; coordinate consistency is not anatomical validation.

No independent enthesis extent, separate tendon/aponeurosis surface, measured
fibre map, material compartment, ligament, cartilage or fat boundary is established.
The inventory's original missing-data distinctions remain unchanged. Bone/muscle
mesh closure does not supply those structures. Reduced source-to-bone gaps are
not measured tendon lengths or cartilage thicknesses. Existing belly cuts and
apparatus routing are authored derivatives owned by the mechanics lane.

## Actual visual inspection

[`individual-surfaces.png`](individual-surfaces.png) was rendered from unchanged
original triangles and inspected in this session. All ten show faceted outer
surfaces; the small-component markers locate issues that silhouette inspection
alone can miss. Individual panels use their own scales, and marker size does not
represent anatomical extent. [`atlas-and-landmarks.png`](atlas-and-landmarks.png)
shows X-Z and Y-Z static projections and original bone picks/patches. Overlapping
projections and transparent rendering limit depth interpretation. The historical
radial tuberosity candidate is displayed under its original label, not promoted
to the replacement patch or a validated attachment. No rendering establishes
anatomical accuracy, internal compartments or a calibrated pose.

## Required work before volume meshing

The bones and brachioradialis are the simplest **surface-reference candidates**:
one principal closed component and no detected strict transverse self-crossings.
They still require a documented derivative index weld, robust embedding/nesting
and interface checks, anatomical boundary review and a defensible material/reference
state. Bone outer shells do not define cortical thickness, marrow or trabecular
compartments. Brachioradialis' closed envelope does not identify belly/tendon cuts.

For the other six muscle heads, review every zero-volume shell against provenance
before choosing whether a separately versioned derivative may omit a source
artifact. For brachialis and short biceps, inspect the reported transverse pairs
and resolve intersecting boundaries from source evidence. No joins, hole fills,
smoothing, fragment deletion or replacement anatomy are authorized by this audit.
If anatomy cannot be recovered, retain the gap. Volume meshing alone does not
recover tendon, enthesis, fibre architecture or missing tissue interfaces.

The bounded local audit is complete. New source work remains blocked by the
recorded direct proxy CONNECT failures; no denied route was retried. NLM sample
localization and actual tissue observability remain unassessed, and 4.3 exact-asset
license clearance remains unresolved. Further planning documents cannot resolve
those access/evidence gaps.

## Reproduce offline

From the repository root, using installed NumPy and the repository's Matplotlib:

```sh
python3 -m unittest discover -s education/tests -p test_arm_surface_quality.py -v
python3 education/data/elbow-v1/scripts/audit_arm_surface_quality.py
MPLCONFIGDIR=/tmp/kenoma-surface-mpl XDG_CACHE_HOME=/tmp/kenoma-surface-cache python3 education/data/elbow-v1/scripts/render_arm_surface_quality.py
```

The default audit is read-only and requires equality with committed `quality.json`.
`--write` updates only that output after verifying existing pins; it never repins
inputs or runs owner builders. Rendering writes only these two PNGs and its receipt.
[`render-checkpoint.json`](render-checkpoint.json) binds the source, numeric evidence,
renderer, runtime versions and image SHA-256. [`validation-checkpoint.json`](validation-checkpoint.json)
records tests and review. Pixel identity can vary with fonts/rendering libraries;
the numerical quality evidence and input hashes are the geometry contract.
