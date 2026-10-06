# Connected passive specimen review prototype

This separate prototype leaves the published lessons, material calibration,
existing acceptance limits and capstone labels unchanged. It is one connected
axisymmetric Q2 meridional finite-element specimen, with an actual revolved
boundary sampled from the solved displacement field. It is not active muscle or
an anatomically calibrated model, and finite compliance does not enforce exact
local volume preservation.

The only physical specimen choices are the homogeneous cylinder and one linear
radius taper, ratio 1.5 (area ratio 2.25), with reference length 0.05 m and small
radius 0.005 m. Shear modulus is 1500 Pa, bulk modulus 30000 Pa. End displacement
is zero or ±0.005 m. Every node on each complete end face has prescribed axial
displacement; end-face radial DOFs remain free. Radial motion is zero on the axis
and the axial field is even there. The free tapered side uses the full natural
Piola traction condition with normal proportional to (1, 0, −a′).

In the cylindrical orthonormal basis, F has entries
`[[r_R,0,r_Z],[0,r/R,0],[z_R,0,z_Z]]`, with the regular axis limit for r/R.
The stored energy is `mu/2*(J^(-2/3)*tr(FᵀF)-3)+K/2*(log J)^2`.
Assembly explicitly uses `2*pi*R` reference volume weighting, full energy forces
and the original tangent. Axis parity constraints are reduced by their actual
linear transformation. No modified Hessian, mixed pressure, volume projection,
postsolve volume correction or reduced ring equilibrium is used. The solver
requires positive hoop stretch, meridional determinant and J > 1e-6 at its
material evaluations. The independent rational Bernstein checker separately
bounds J for the entire stored Q2 maps in its declared cases; it does not prove
global injectivity or floating-point solver equivalence.

A genuine direct fine-mesh compression attempt has an indefinite initial
original tangent and fails. Small load increments from the rest state reach the
requested bounded poses without changing the tangent or stationarity criterion.
The one-iteration control deliberately displays a direct approximation at the
actual requested end displacement, including its nonconvergence warning.
Failed worker or unsupported controls retain the preceding complete displayed
state and warning. Explicit reset requests the undeformed fine taper. Physics
controls preserve camera pose; probe controls neither solve nor remesh.

Residual normalization is the maximum complete free nodal force divided by
`mu*pi*a0^2`, with a provisional target of 1e-10. This force scale and the energy
scale `mu*V0` remain positive at zero load. The original scaled tangent pivot
spread is not called a condition number. Independent SciPy eigenvalues qualify
the constrained discrete tangent numerically; this is not a continuum or
nonaxisymmetric stability theorem. An Armijo energy comparison includes a
reported roundoff allowance `64*Number.EPSILON*mu*V0`; final stationarity still
uses the unmodified force residual.

Numerical targets are provisional engineering checks for this new prototype,
not changes to the frozen lesson limits. The experiment records separate axial
and radial refinements, successive meshes, independent quadrature, sixteen
fixed material probes, volume-weighted J differences, both side traction
components, section resultants, reaction/energy derivatives at two steps,
original-tangent spectra and actual finite Float32 tessellation volumes. Corner
and near-corner gradients remain separate unresolved evidence. Observed
refinement differences do not certify an exact continuum error bound. Nine
fresh local Real identities support determinants, logarithmic storage, traction,
force conversion and reference geometry; they do not prove the solver,
convergence, renderer, global injectivity, anatomy or buckling stability.

From `education/`, with the existing pinned dependencies available:

```sh
node --test tests/axisymmetric_material.test.mjs tests/axisymmetric_specimen.test.mjs
python3 tools/qualify_axisymmetric_material.py /tmp/axis-material.json
node tools/axisymmetric-experiment.mjs /tmp/axis-experiment.json
python3 tools/qualify_axisymmetric_experiment.py /tmp/axis-experiment.json /tmp/axis-numerical.json
python3 tools/check_axisymmetric_proofs.py /tmp/axis-proofs
python3 tools/build_axisymmetric_preview.py /tmp/axis-preview --proof-directory /tmp/axis-proofs
python3 tests/axisymmetric_browser.py --preview /tmp/axis-preview --out /tmp/axis-browser --oracle /tmp/axis-material.json --experiment /tmp/axis-experiment.json
python3 tools/qualify_axisymmetric_negatives.py --out /tmp/axis-negatives --proof-directory /tmp/axis-proofs --oracle /tmp/axis-material.json --experiment /tmp/axis-experiment.json
python3 -m http.server 8000 --directory /tmp/axis-preview
```

Use fresh output directories. The standalone builder requires matching fresh
proof source/claim hashes and the official mathlib lock. Browser qualification
uses installed Playwright, Chromium, NumPy and actual WebGL2 buffer readback. It
covers software WebGL and an emulated mobile viewport; it does not claim physical
mobile hardware qualification. SymPy/mpmath independently derive the material
and homogeneous free-lateral oracle, and SciPy supplies independent matrix
checks. The two negative copies actually rebuild a wrong-radius renderer and a
wrong-reaction worker; the unchanged native oracles must reject both.

This milestone is for review only. No published book entry, full-book PDF,
release, draft PR, deployment or merge is authorized by this prototype workflow.
