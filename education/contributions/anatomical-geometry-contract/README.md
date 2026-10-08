# Consumable anatomical geometry contract

This unregistered development slice connects the retained actual anatomy geometry to a model-facing observer and attachment adapter. It starts at inspector `02478c1895ca409a3c23cec480f2f2397b18676a`, parent `756b8efb8ebe74aec4469a75443dd4cb51bc8a09`; the registered book remains unchanged. It implements regional geometry observables and existing attachment-point maps without importing mechanics/model preparation, which would invoke the held material/quadrature path.

`prepareGeometryContract` supplies six nonempty, connected source ring-band regions for each of the seven actual atlas-derived repaired P2 bellies; membership partitions all 252 elements exactly once, and adjacent bands share actual material faces. It preserves reference repair and segmentation inputs, existing cap-node samples, original source-bone patch face/barycentric/area-weight maps, attachment ownership and all 585 authored routing polylines. No attachment landmark, material parameter, tendon radius or stress area is supplied or invented.

`evaluateGeometry` consumes complete physical nodal positions per body, and optionally complete positions for existing patch samples. It returns regional signed material volumes/ratios, area/width/depth at each region's middle material section, existing weighted cap-point positions and the lengths/paths of retained tendon routes. This is an executable geometry connection, not a force or reduced-coordinate model constructor. Four bodies without saved calibration positions remain reference-only in the supplied frozen example.

`observeApparatusPositions` directly accepts the existing `evaluateApparatus(...).positions` record shape: seven `{elementId, nodesM}` rows. It requires complete unique body identity and routes those physical Cartesian positions to the observer. The existing mechanics evaluator is never imported or invoked here. This supplies a concrete connection for an eventual model run, instead of requiring a solver to recompute or reinterpret anatomy measurements.

The P2 map is ten-node quadratic. Its parent Jacobian is affine and determinant cubic. `p2-volume.mjs` expands the determinant's monomial coefficients, then integrates each `xi^i eta^j zeta^k` as `i!j!k!/(i+j+k+3)!`. Subtracting the first position removes translation cancellation before expansion. This is exact polynomial integration in real arithmetic, evaluated in binary64; it generates no material quadrature or constitutive samples. The **signed algebraic integral** does not certify positive orientation everywhere, lack of folds, true enclosed volume or equilibrium. Even positive regional volume cannot exclude severe local compression or inverted elements. Cross-section surface area remains a tessellation approximation and is not J, PCSA or a current-space planar section.

The cap points retain the existing apparatus's three-node weighted sample maps. Their geometric face areas are reference data, not new force magnitudes or imposed supports. Body/patch endpoint ownership is bound only when an original route endpoint uniquely matches an existing source sample within 1e-12 m. Shared and estimated endpoints without such identities remain explicit source-indexed literals. No ownership is inferred from a branch group name. Original repair offsets are retained; mapped endpoints follow supplied sample positions with that same offset, while stored guides and unresolved literal endpoints remain fixed. This is a **partial kinematic adapter**, not sliding-wrap/contact mechanics or a complete shared-aponeurosis DOF connection. Supplied fields can violate geometry/clearance; only finite dimensions are checked. No updated route clearance is claimed.

The routing record's original `anatomical-distance.mjs` hash is `93e191f675afa9e2bb2a2a067cb3054512713d3de1e38eb9087f381a7554acc7`, retained at `611c0554ccb98b04673e5903643f2f01af87d099`. The inspector baseline's current distance source has a different hash `e11826c97f160220fda68f72cbe5e73f35f9527edcf4a4d58100c467cb50940a`. The manifest preserves each historical routing implementation identity separately. Original and current distance code are not executed; the exported routes are historical authored geometry without fresh clearance qualification.

## Local use

Run from the source contribution directory. Inputs are explicit retained local data, verified against 23 Git blobs/SHA-256/size entries; five original recipe dependencies have separate immutable source bindings. Outputs must be a new absolute directory outside retained data and the source checkout.

```bash
node build.mjs --data /absolute/retained/education/data --out /absolute/new/contract
KENOMA_GEOMETRY_OUTPUT=/absolute/new/contract node --test contract.test.mjs
```

The output includes portable executable modules under `adapter/`, with the exact sibling section-geometry dependency and no external packages. Consumer example from the output directory, using physical Cartesian metres without solving:

```js
import {evaluateGeometry} from './adapter/anatomical-geometry-contract/contract.mjs';
const reference = evaluateGeometry(contract, {fieldLabel: 'reference geometry'});
const observed = evaluateGeometry(contract, {
  bodyPositionsById: {FJ1486: savedBrachialisPositions},
  fieldLabel: 'saved nonstationary geometry'
});
// observed.bodies[0].regions, observed.bodies[0].caps, observed.routes
```

The original frozen fields remain failed full-nodal force checks: 64.067641, 52.058855 and 54.223684 N versus unchanged 0.0001 N. Every evaluation is labelled `GEOMETRY_ONLY_NO_FORCE_EVALUATION`. Recorded failures remain attached as historical evidence; they are not newly measured forces for an arbitrary supplied field. No field is accepted as physical deformation, full nodal equilibrium or anatomical validation. Fine-window/outside236 callbacks and material/solver/Real/full-book builds do not run.

An eventual mechanics implementation can consume these regional identities and source-point maps, but still needs independently reviewed architecture/boundary ownership, a complete shared/tendon DOF map, qualified integration and force stationarity. Subject/protocol-matched anatomy and volumetric material measurements remain unavailable. This contribution does not register a lesson or claim anatomical completion.

Original licensed inputs and notices are copied unchanged. BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International. Historical OBJ comments, current retained grant, modification/provenance record, source-specific licenses and Arm26 credits are preserved. The mathematical/kinematic adapter does not change their evidential status.

## Area definitions retained for downstream consumers

The machine-readable `quantitySemantics`, patch/cap `areaKind`, and regional `sectionAreaKind` distinguish insertion footprint surface area, authored belly-cap face area, mapped muscle material-slice area, tendon cross-sectional area (CSA), and physiological cross-sectional area (PCSA). The last two are unavailable here. The original apparatus uses authored20% insertion/cap fractions (with a further20% head-fan factor) as tendon A0 inputs; this adapter exports no A0 and supplies no measurement-based replacement. Its shared triceps olecranon patch does not distinguish deep muscular from superficial tendinous insertion footprints. Population study values alone cannot identify this atlas's source faces, landmarks, tendon cross-sections or PCSA; incoming cohort references stay separate from the executable contract and physical laws.

`quantityDefinitions` separates reference from current tendon CSA and names method, frame, SI conversion and unavailable specimen-specific evidence. Each source patch carries its deterministic curved-triangle method, original source record, bone identity and unresolved head/tissue ownership. Each regional section carries body identity, original basis, material station, resolution and reference/current field labels; it is a transported material slice rather than a perpendicular-current-fibre slice. Source-specific cohort DOI links are comparison pointers, not registered measurement values, landmarks or licensed source meshes. No new display panel is added.

The [compression backlog](compression-lab-backlog.md) records the supplied research audit without duplicating existing area/PCSA lessons. `physicalAssumptions` travels with the contract and observables: local J, fibre-normal area, pressure, fluid transport, perfusion and force remain unavailable. Directional transverse loading and optional explicitly sealed/drained transport are proposed mechanisms, not implemented labs. No universal compression penalty, bulging capacity bonus or mixed-species material value is introduced. Patch contexts also expose exact existing source-declared attachment body IDs and sides; these declarations do not partition measured head/tissue footprints.
