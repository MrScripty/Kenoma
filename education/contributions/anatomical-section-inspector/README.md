# Actual-bone attachment and material-section inspector

This unregistered anatomy development slice starts at exact source `756b8efb8ebe74aec4469a75443dd4cb51bc8a09`, sole parent `6a72e01b66e4d5724c8d6c74f98cf38a90b21e31`. It implements the regional geometry/observable prerequisite in the retained local-volume-redistribution plan and anatomical-capstone specification. It does not implement or execute their later virtual-work witness or re-equilibration campaign.

Three actual BodyParts3D bone surfaces retain the original shared coordinates and face IDs. Seven connected, uneven, atlas-derived P2 bellies retain the repaired reference geometry. Eight distributed attachment candidates expose their actual source faces, areas and weights. Authored fixed scapular estimates remain identified in the original attachment file; they are not measured landmarks or distributed anatomical tendon maps. The green overlay is a review aid, not a claim that an arbitrary selected patch belongs to the selected muscle; changing muscle automatically selects its declared distal patch.

For brachialis and both biceps heads, the viewer maps material sections through **saved** fully activated fixed-cap calibration positions. Their complete free nodal force gates failed: 64.067641, 52.058855 and 54.223684 N, respectively, versus the unchanged 0.0001 N criterion. The original adverse audit is included unchanged. Four other heads have reference geometry only. No renderer converts reduced residuals or fitted endpoint force to full stationarity.

The cut plane uses the body's authored reference axis and belly interval, distal to proximal. Straight reference P2 edges are required and independently checked; intersecting corner tetrahedra supplies barycentric material sections. The P2 order is corners 0–3, then edges (0,1), (0,2), (0,3), (1,2), (1,3), (2,3). The ten shape values are `Li(2Li−1)` and `4LiLj`. The saved current nodal positions are interpolated at the **same** material points. Coplanar shared faces are deduplicated. Nothing rescales a radius, welds bodies together, recentres individual atlas parts, changes a physical law, or imports the material/solver modules.

The mapped material surface may curve away from its original plane. Its triangular surface area is a tessellation approximation (4 or 8 subdivisions); projected width and depth use the fixed reference u/v axes and common scale. The area is not a current-space planar cross-section, local J, volume, PCSA, fibre strain, measurement, or equilibrium result. Original global volume ratio and minimum corner J are labelled retained audit values. `geometry-receipt.json` compares section tessellations at five stations per head, without material calls.

## Requirements advanced and still open

| Requirement | This slice | Remaining obligation |
| --- | --- | --- |
| Actual bones and shared attachment geometry | Original surfaces/face IDs, authored patch overlays and exact ownership data | Independent anatomical review, distributed tendon/aponeurosis architecture and fitted joint/boundary contract |
| Heterogeneous connected cross-sections | Seven uneven reference bellies; three mapped frozen P2 fields at selectable material stations | Resolved regional volume/strain observables and integration adequacy |
| Regional deformation distinct from global volume | Material surface area and projected dimensions are separate from retained volume/J | Full free-node force stationarity and independently qualified equilibrium experiments |
| Empirical data/provenance | 22 existing inputs, original OBJ notices, SI conversion record, license documents, adverse audit | Subject/protocol-matched geometry, architecture and volumetric material data |

The retained constants and force operator are unchanged. This feature has no optimizer, contact solve, material evaluation, quadrature generation, dependency/cache download, Lean run, anatomical campaign or book registration. Geometry/browser passes only qualify this inspector. Fresh Real proofs and whole-book/print qualification are not supplied. Continuous passive specimen, scalar tension/mass controller, anatomical completion and ongoing research sources remain outside accepted book coverage.

## Local build and verification

Only existing retained input bytes are read. `inputs.lock.json` pins full source commit, Git blob, SHA-256 and size for each. The builder refuses identity changes, input symlinks, changed source-face areas/centroids/weights, curved reference edges, missing attachment ownership, altered caps or hidden calibration failures. Outputs must be an explicit new absolute directory outside input data and the checkout.

Run build and test commands from this contribution's source directory. The generated preview is a standalone reader surface; build/test scripts are delivered in the separate source archive.

```bash
node build.mjs --data /absolute/retained/education/data --out /absolute/new/preview
node --test geometry.test.mjs
python browser_check.py --preview /absolute/new/preview --evidence /absolute/new/evidence
python check_export.py --preview /absolute/new/preview --download /absolute/new/evidence/downloaded-section.json --receipt /absolute/new/export-check.json
python -m http.server 8000 --directory /absolute/new/preview
```

Open `http://localhost:8000/`. Controls change muscle, candidate patch, atlas projection, material station, tessellation and recorded-field overlay. Reset restores the initial state. Download exports actual section sample positions and immutable model/source identity. All preview module, data and download URLs are relative; no external request is required. Serve modules through HTTP rather than a `file://` URL. Source license URLs are attribution references, not build dependencies.

`check_export.py` independently reconstructs barycentric coordinates from the exported Cartesian reference points and checks the recorded P2 current map, original material plane and surface-area sum without importing the JavaScript implementation. Shared reference faces use a 1e-10 m coordinate deduplication grid; other straight-edge/patch validation tolerances are explicit in the source. These finite floating-point checks are not formal geometry or physical validation.

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International. Original OBJ historical notices remain byte-for-byte preserved; the retained current grant and modification/provenance records are bundled. Arm26's CC BY 3.0 reference and credits remain in its original XML and the source-specific notices. No package-wide license supersedes component licenses.
