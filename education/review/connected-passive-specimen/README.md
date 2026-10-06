# Connected passive specimen: first bounded review milestone

The homogeneous free-lateral oracle, full energy/force/tangent assembly and one
connected passive radius-ratio-1.5 specimen now qualify at zero and ±10% end
displacement under the provisional engineering checks below. The interactive
prototype renders the actual solved connected Q2 geometry. This is finite
compliance with measured local/global volume change; it does not satisfy exact
volume-preserving equilibrium or establish buckling/anatomical stability.

The qualified material, assembly, proofs, controls and positive native test are
at source **39de7f1aaa2e8c4b9ecc981498853f4d703eb7b8** on
`education/connected-passive-specimen`. Source successor
**0354ed5951a59edc8d04405e2a5f5079ed19116b** changes only the negative-build runner
to copy the independent oracle inputs; both actual negative builds qualify at
that successor. Exact source SHA256 bindings are checked by each receipt and by
`verify_review.py`. Both commits have author and committer
`MrScripty <TheEnvironmentGuy@protonmail.com>`.

The seven frozen checkout heads remain clean and unchanged (`frozen-ref-check.json`).
PR8 and published lessons were not edited. Existing material calibration,
acceptance limits, proof-family counters and unfinished-capstone labels were not
changed. No full-book/PDF build, PR, publication, merge or deployment is claimed.
The prototype remains outside the book entry point and its CI acceptance lanes.

## Reproduce and inspect

The complete model/scope and rerun commands are in `../../AXISYMMETRIC_PROTOTYPE.md`.
To inspect these exact delivered bytes:

```sh
python3 education/review/connected-passive-specimen/verify_review.py
python3 -m http.server 8000 --directory education/review/connected-passive-specimen/preview
```

Open `http://127.0.0.1:8000` and press **Start interactive 3D**. The module worker
requires HTTP. `connected-passive-preview.zip` contains precisely the same 17
qualified standalone files; `portable-preview-record.json` records its 169335
bytes and SHA256 `96c041517db93a1eef2bde8885e127ef7c0d769cf4b28647996b0d1ded76ddac`.
It carries the local Real source, full transcript, checked statement receipt,
source/output manifest and third-party license; compiler dependency caches are
not bundled. It is not a full-book release.

## Evidence and scope

- **221/221 Node tests pass**, including 13 new material/assembly tests. These
  include directional energy/force/tangent differences at two scales, uniform
  free-lateral geometry/stress, full end-face axial constraints, free end radial
  motion, regular axis parity, actual shear/local J, connected watertight
  renderer, finite iteration caps, original-tangent linear residual and load
  continuation. Logs are under `tests/`.
- **Independent material oracle passes**: SymPy differentiates the complete
  five-component energy; mpmath independently solves the free-lateral energy
  derivative at 60 digits for homogeneous stretches 0.9, 1 and 1.1. It reuses
  neither the production gradient nor its scalar log-root equation. This gives
  side stretch/J `(1.0514903364797394, 0.995068734939248)` in compression and
  `(0.955812986200411, 1.0049363110482816)` in tension. `numerical/material-oracle.json`
  contains exact methods, values and source bindings.
- **23 bounded numerical cases converge**. `numerical/qualification.json` checks
  distinct axial/radial refinements through 16×8 cells (1024 free DOFs), fixed
  material probes, volume-weighted J differences, independent Gauss orders,
  complete free residual, both full side PN components away from corners,
  section resultants, reaction/energy derivatives at two steps, independently
  computed original-tangent spectra and finite Float32 rendering error.
- **Stored-map admissibility is bounded independently** using exact Fraction
  arithmetic on the binary node/displacement values and tensor Bernstein
  coefficients, with the common axis radial factor removed before bounding r/R.
  Every complete stored Q2 cell in the declared uniform/fine-taper cases has
  positive orientation/radius ratio/J above the runtime guard. This geometric
  bound is separate from physical J error and proves neither global injectivity
  nor floating-point equivalence. Its deliberately loose J bounds are not
  physical extrema.
- **Nine new local Real identities freshly pass** Lean 4.19.0 with the pinned
  official mathlib v4.19.0 commit and all eight pristine dependency pins. The
  only reported axioms are `propext`, `Classical.choice`, `Quot.sound`. Existing
  four kinematic declarations are also freshly checked by the pin helper. Full
  new statements, assumptions, limits and transcript are in `proofs/` and in
  the delivered prototype's expandable cards. This does not claim fresh
  compilation of all frozen lesson proof families.
- **20 actual Chromium 151.0.7922.173 cases pass**, including zero/±10% taper,
  independent uniform-cylinder controls, actual mesh changes, axis probes that
  do not solve/remesh, camera preservation, one-iteration warnings, unsupported
  input retention, worker-failure retention, latest-request cancellation,
  explicit reset, state export, real context loss/retry, emulated mobile layout
  without horizontal overflow and WebGL-unavailable numerical operation.
  The independent Python Q2 reconstruction checks the actual displayed vertices
  and local full stress. Actual WebGL2 GPU position/index buffers are read back
  and compared, with independent connected/oriented shell and signed-volume
  checks; three actual pose framebuffers differ. This is headless Chromium with
  SwiftShader, not physical mobile GPU qualification. Full receipt, raw states,
  exported state and inspected captures are under `browser/`.
- **Two actually rebuilt negative bundles are rejected** with unchanged native
  assertions. The 5% radius adapter corruption reaches real rendered 3D and
  fails independent Q2-vertex comparison. The corrupted reaction worker reaches
  the real numerical browser state and fails the independent offline reaction
  comparison before 3D starts. `negatives/` retains mutated modules, actual
  bundles/manifests and failure transcripts. No GPU readback is claimed for the
  rejected cases; that check belongs to the positive native lane.

The positive browser uses the first experiment whose exact input hashes already
match source 39de7f1. A fresh final numerical run reproduces every complete solved
state object identically; elapsed timings differ. Both raw experiments are
preserved, and their respective hashes are used by the native/numerical receipts.
The proof and material receipts from the two runs are byte-identical. Large raw
JSON is losslessly gzipped, with every original/compressed hash and size in
`compression-record.json`. Inventory and portable verification check every byte.

## Finest taper results

Reference length is 0.05 m, small-end radius 0.005 m; radius ratio is 1.5 and
area ratio 2.25. Exact reference frustum volume is **6.2177354602298e−6 m³**.
Fixed illustrative passive moduli are μ=1500 Pa, K=30000 Pa (K/μ=20).
Complete end faces prescribe axial displacement; radial DOFs remain free.
Axis constraints and the full normal `(1,0,−a′)` are stated in the source/page.

| Quantity | −10% compression | +10% tension |
| --- | ---: | ---: |
| Right end reaction (N) | −0.0585093297647513 | 0.0471632754175177 |
| Stored energy (J) | 0.000140530882998407 | 0.000121743994339564 |
| Integrated V/V0 | 0.995306577099282 | 1.004646992822435 |
| Volume-weighted RMS(J−1) | 0.004810875130937 | 0.004813308259747 |
| Quadrature J min/max | 0.991082792678 / 0.997514749145 | 1.002471524691 / 1.008879419069 |
| Declared noncorner cut-force variation / μAmin | 0.000404648248161 | 0.000403788444601 |
| Declared noncorner full side traction / μ | 0.000110210032359 | 0.000117952352029 |

These extrema are quadrature samples, not whole-body extrema. Residual scale
μAmin=0.11780972450961726 N and energy scale μV0 are positive at zero load.
The maximum complete free-force residual must be ≤1e−10 of that fixed force
scale; its actual finest values are approximately 1.3e−14 and 7.9e−15.
Both reaction-energy derivative steps agree within 1e−8 of the force scale.

Provisional targets require observed material-point and whole-body weighted J
differences below 10% of the physical RMS J signal, successive 8×4→16×8 reaction
and energy differences below 1%, independent quadrature J differences below 1%
of the signal, declared noncorner PN and cut-force errors below 1e−3 of their
positive scales, and finest finite Float32 volume error below 10% of the global
volume-change signal (zero-load error <2e−4 V0). All pass here. They are observed
engineering checks, not rigorous continuum error estimates or inherited lesson
acceptance limits. Conditioning is defined as the eigenvalue ratio of the
Jacobi-scaled original constrained tangent; independent numerical values are
about 9336 at rest, 8673 in compression and 9904 in tension. Original-tangent
scaled Cholesky and linear residuals are retained separately.

## Genuine failure and remaining limits

`failures/direct-fine-compression.json` records the rejected direct final-pose
axial-only initial guess on 16×8/order5 compression: zero accepted Newton steps,
original free tangent fails a positive Cholesky pivot, `converged=false`.
`failures/direct-source/` preserves the exact matching material/core bytes.
Continuation from rest resolves this bounded loading path using the same
energy, forces, original tangent and force criterion; the failed attempt is not
relabelled success. The one-iteration diagnostic remains visibly nonconverged
with its actual residual, energy, volume and geometry.

Earlier material-harness, strict Lean compile, native-harness and negative-copy
attempt transcripts are retained under `failures/`; none count as qualification.
The first native harness was edited during its run and failed on restoring the
Worker constructor; that attempt has no complete source-bound success receipt.
The final unchanged harness checks its own hash before/after and passes all 20
cases. The first negative-copy attempt failed before native checks because it
omitted an oracle-input script; the corrected actual bundles supply all inputs
and fail only at their intended independent physical assertions.

Corner and near-corner gradient/stress/J convergence remains unresolved and is
recorded separately in the numerical experiment. Natural free-side traction is
checked at declared noncorner points, not asserted exact everywhere. Numerical
constrained axisymmetric tangent positivity is not continuum, buckling or
unrestricted 3D stability. Finite volume compliance cannot satisfy exact local
incompressibility. Mixed pressure, active fibres/muscle, anatomical calibration,
additional shape/material sweeps and capstone completion remain outside this
milestone. Parent review is required before any PR or book integration.
