# Validation and boundaries

Source context fetched from `https://github.com/MrScripty/Kenoma.git`:
`education/tendon-tissue` resolved to
`19625dd9a96adbdb392674075afd972c28c27db0`, the exact requested published commit.
The immutable source tree identity is also recorded in `data/provenance.json`.
No AGENTS.md or SKILL.md exists in this checkout or its workspace instruction
directories; the existing education authoring/validation instructions and audited
research integration notes were read. Only this new contribution directory is
edited. No dependency installation/upgrade or proof registry change is needed.

## Focused numerical checks

Run from repository root:

```sh
node --test education/contributions/continuum_reference/tests/continuum.test.mjs
node education/contributions/continuum_reference/generate.mjs
```

The generator executes the same focused tests and records stdout, exit status,
Node/V8/OS/CPU metadata and exact source/test hashes. Eleven tests pass in the
recorded Node 24.19.0 executor:

- Conforming tetrahedron volumes, outward triangles and independently integrated
  total physical lumped mass.
- Unit tetrahedron gradients, symmetry, tensor-based affine strain energy,
  engineering shear convention and energy/force finite differences.
- Six infinitesimal rigid null modes and a finite-rotation counterexample.
- Affine manufactured patch on three meshes: exact displacements/stress,
  support-force sign, energy, static ramp work and balance.
- Quadratic manufactured equilibrium from analytic divergence and traction,
  volume-quadrature normalization, and mesh refinement at n=2,4,8.
- An independently coded pivoted dense elimination versus PCG for a tiny
  implicit system, plus explicitly unsuccessful capped iteration output.
- Exact energy equivalence of the six compliant strain modes and full FEM.
- Finite-sweep error convergence to the matched PCG implicit target, fixed
  coordinates, deterministic replay and finite-order sensitivity.
- Finite-sweep timestep dependence, with convergence to each step's own target.
- Nonzero-state implicit work/dissipation identity, inertia and reaction signs,
  and matching compliant evolution.
- Zero-load equilibrium, invalid parameter/vector domains and degenerate element
  rejection.

Tests execute the delivered module. The manufactured displacement/load and
closed-form integrals are derived independently of FEM, not read from generated
fixtures. The dense solve independently checks the solver against the assembled
matrix; it does not independently validate the material/discretization. The
unit-tetrahedron tensor energy and manufactured fields address those parts.
No test or existing Lean theorem proves JavaScript floating-point refinement.

## Generated evidence

`reference.json` reports static n=1,2,4,8,12 refinement, full precision errors,
reactions/force balance and solve tolerances. Displacement relative L2 decreases
from about 55.0% to 2.36%; energy norm decreases from about 43.1% to 4.13%.
Algebraic residuals near 1e-11 N do not imply continuum accuracy. The mesh remains
synthetic; no anatomical or observed displacement field is validated.

The matched n=3, h=0.0005 s comparison uses the same linear tetrahedra, material
energy, dead loads, lumped mass and fixed coordinates for both solvers. Five
compliant sweeps yield about 0.92% objective-norm error against the discrete PCG
reference, with a separate force residual. Fifty sweeps approach that reference
but cost more in the recorded run. See generated tables for the actual timing
samples and setup/diagnostic exclusions; no universal benchmark is claimed.
Changing h or the mesh changes finite-sweep error; the generated sensitivity
cases deliberately expose this. Step sensitivity is not temporal convergence.

`example.json` provides renderable mesh/connectivity, force/mass/clamp arrays,
static and implicit reference fields, and finite-sweep fields with unscaled SI
diagnostics. The generator fails on an unconverged PCG result. The receipt binds
tests to their exact module/test hashes; the provenance manifest hashes all
source/evidence payloads except itself (avoiding circular hashes). There is no
hosted CI, browser/WebGL, PDF, assembled-book, clinical or Lean receipt in this
contribution. Integrating author should run their own renderer/build checks.

## Applicability limits

Linear isotropic compressible elasticity, small displacement gradients, no
finite-rotation objectivity, no inversion prevention, no anatomical geometry or
attachments, no active muscle/tendon, no viscosity, no layers/fascia, no contact,
no pressure field, no measured calibration. Near incompressibility can lock this
displacement-only element and worsen conditioning. Geometry/material changes
beyond the authored fixtures need additional verification. This is a spatial
FEM teaching reference, not a clinical solver or general simulator.

## Primary source provenance

`sources.json` records original papers/course notes and inspected sections. Ryan,
XPBD and Iivarinen are linked to the existing audit and independently reopened.
Teran's original tetrahedral/energy paper, Shewchuk's PCG notes, Baraff's implicit
notes and Mitchell's preliminary surgical simulator were independently opened.
Iivarinen was checked at original-abstract level only. The Sifakis/Barbič course
notes timed out and supply no verified constitutive formulas here. No paper PDF,
figure, third-party mesh, participant data or fitted medical coefficient is
redistributed. No Library transfer is required to use the published Git source;
this task does not alter any sharing or permission setting.
