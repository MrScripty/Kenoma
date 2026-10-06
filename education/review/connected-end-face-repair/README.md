# Connected end-face and closed-endpoint repair

Source **1c90c63827abce0649286734ecd5fb6d1276c83e** on
`education/connected-end-face-repair` repairs a confirmed boundary-condition
bug in the additional accepted meshes. The frozen source and 120-file evidence
at **49bf8adf30e1b9bc192e0211f12dfafeb60ede94** remain unchanged. Its qualified
4/8/16-cell states are reproduced exactly by this successor. This branch adds
no PR, publication, merge, deployment or book integration.

With 3, 6, 12 or 24 axial cells, the old reference coordinate calculation gives
its last row Z=0.05000000000000001 m. Coordinate equality then omits every
prescribed upper axial displacement. The solver reports convergence and the
requested pose while the top face is actually fixed at zero displacement and
the loaded uniform-cylinder reaction is effectively zero. Default rendering on
these counts also evaluates a last ring outside the strict Z≤L domain. The same
rendering defect occurs for delivered counts 4/8/16 with allowed subdivision 3;
the shipped subdivision 8 avoided it.

The repair records the upper axial DOF IDs from mesh topology and assigns their
prescribed values explicitly. Reference nodes, revolved boundary rings, worker
surface sampling and trace sampling construct the final closed endpoint exactly
as the declared length. The strict physical-domain guard is unchanged. Material
energy/force/tangent, moduli, solver criteria, physical/geometry tolerances,
accepted mesh/render ranges, native control menu and capstone labels are
unchanged. There is no postsolve deformation or volume correction.

Five exact regression tests fail on copied unchanged frozen source and pass on
the successor. The frozen negative copy contains the actual old modules,
independent material oracle, exact new test bytes, transcript and input hashes.
Two tests require independent physical compression/tension reactions for a
three-cell uniform cylinder; they do not rely on convergence flags alone.
Another checks every imposed top-face DOF for all 31 accepted axial counts
2..32 and both signs. Endpoint tests exercise node sampling and every allowed
subdivision 1..16, including the separately failing delivered-count subdivision3.

Qualification at this source:

- **18/18 focused Node tests pass**: the original 13 plus five regressions. Their
  log includes the still-failing genuine direct fine-compression initialization
  and successful continuation under the original tangent. The prior 221-test
  full-suite result remains historical; a new full repository suite or book
  build is not claimed.
- **All 31 accepted axial counts assign complete end faces correctly**.
  **16 solved formerly affected cases** (3/6/12/24 × cylinder/taper × ±10%) pass
  complete cap assignment, strict reference/render endpoints, independent
  uniform-cylinder force/energy/J checks and exact-rational stored Q2 positivity.
  The unchanged provisional force/energy/material-point comparisons against
  frozen fine taper also pass. `numerical/affected-qualification.json` retains
  values and explicit limits; these are coarse-mesh observations, not new
  continuum error/stability claims.
- **All original 23 numerical cases requalify** with the unchanged checker.
  Every complete state, node, cell, displacement, probe, corner, section force
  and side traction matches frozen evidence exactly. Source bindings differ
  and elapsed timings vary. `frozen-preservation.json` identifies all identical
  fields and verifies original evidence hashes; no historical receipt was
  rewritten to claim the repaired source.
- **20 actual native-menu Chromium cases requalify** on the rebuilt successor,
  including 4/8/16 mesh controls, zero/±10% poses, independent uniform-cylinder
  checks, warning/state retention, reset/export, context loss/retry, mobile
  layout and numerical-only WebGL fallback. Actual position/index GPU buffers
  are read back and independently reconstructed.
- **16 additional actual worker/render API cases pass** with GPU readback,
  independent Q2 geometry and uniform force oracle. The extra counts are not
  added to the native menu. The harness explicitly labels its injected display
  options “qualification API”; screenshots are qualification captures, not a
  claim that the production menu exposes those counts. It checks top ring
  coordinates and worker trace endpoint exactly. `api-browser/` contains raw
  states, receipts and inspected three-cell compression/tension captures.
- **Nine unchanged local Real identities freshly compile** with official pinned
  Lean/mathlib and the existing four kinematic pin-helper claims. Formal source
  and claims are unchanged; no new solver/convergence/stability theorem is
  claimed. **Both actual rebuilt negative bundles are rejected** by the same
  independent native assertions. Previous negative evidence and the exact
  genuine failed compression source remain in the untouched frozen review.

The corrected three-cell uniform reactions are **−0.03882587443165155 N** in
compression and **+0.031642625793237636 N** in tension. Corresponding measured
V/V0 values are **0.9950687349392436** and **1.0049363110482792**, consistent with
the independently derived 60-digit free-lateral oracle. Every top axial DOF is
exactly εL (−0.005 or +0.005 m). The rendered current upper plane is 0.045 or
0.055 m, with reference endpoint exactly 0.05 m.

From the repository root, verify the complete evidence and serve its exact
standalone delivery:

```sh
python3 education/review/connected-end-face-repair/verify_review.py
python3 -m http.server 8000 --directory education/review/connected-end-face-repair/preview
```

The separate portable ZIP is recorded in `portable-preview-record.json`; its
files match this preview byte for byte and require HTTP for the module worker.
The original portable ZIP is unchanged. Large raw JSON is losslessly compressed
with original and compressed hashes in `compression-record.json`. Inventory
checks every current file plus the immutable historical review and original
source bindings at the frozen commit.

Rerun the affected cases with the new experiment/checker; original full numerical,
proof, build, native and negative commands remain in
`../../AXISYMMETRIC_PROTOTYPE.md`. The additional browser command is:

```sh
python3 education/tests/axisymmetric_end_faces_browser.py --preview /path/to/new-preview --out /path/to/fresh-api-evidence --oracle /path/to/material-oracle.json --legacy-experiment /path/to/delivered-experiment.json --affected-experiment /path/to/affected-experiment.json
```

Qualification uses actual headless Chromium/SwiftShader and an emulated mobile
viewport, not physical mobile GPU hardware. Finite compliance, unresolved corner
convergence, global injectivity and unrestricted/buckling stability limits are
unchanged. Parent review remains required before PR or book integration.
