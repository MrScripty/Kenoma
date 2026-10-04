# Spatial continuum reference contribution

Owned write set: **only this directory**. Integration is left to the book author;
no assembly, application, existing chapter or proof-registration changes are made.
Based on published `education/tendon-tissue` at
`19625dd9a96adbdb392674075afd972c28c27db0` in `MrScripty/Kenoma`.

`continuum.mjs` is a dependency-free browser/Node ES module. It implements genuine
constant-strain tetrahedral linear elasticity and a matched XPBD strain-mode
solver. Its geometry/material/load cases are synthetic educational fixtures.

```js
import {makeCase, solveReference, solveCompliant, diagnose}
  from './continuum.mjs';
const p = makeCase({n: 3}); // 64 nodes, 162 tets, 972 scalar strain constraints
const h = 0.0005;          // seconds; one implicit step from rest
const reference = solveReference(p, {h});
if (!reference.converged) throw new Error('reference solve failed');
const fast = solveCompliant(p, {h, sweeps: 5});
const metrics = diagnose(p, fast.u, {h});
// Vertex v is X_v + u_v; p.mesh.surface has outward triangles.
```

`solveReference(p)` without `h` solves the **static** problem. `continuumError`
compares a static result to the analytic continuum solution. `difference` compares
any two discrete results using the elastic norm, or the implicit objective norm
when given `{h}`. Never use the static quadratic solution as a dynamic reference.

Contribution files: `continuum.mjs`, `tests/continuum.test.mjs`, `generate.mjs`,
`data/reference.json`, `data/example.json`, `data/tables.md`, `data/provenance.json`,
`chapter.md`, `README.md`, `VALIDATION.md`, and `sources.json`. All generated files
are local contributions, not edits to the book build. Complete data/API and
integration instructions follow below.

Run from the repository root:

```sh
node --test education/contributions/continuum_reference/tests/*.test.mjs
node education/contributions/continuum_reference/generate.mjs
```

Apache-2.0 for this original code, prose and authored geometry, under the repository
licence. Primary papers are cited, not redistributed. No claim of clinical
calibration, anatomical validity, nonlinear rotation invariance or contact.

## Complete API and serialized data

The common `problem` returned by `makeCase(options)` contains precomputed element
matrices and strain modes as well as the mesh, loads, clamp and lumped masses.
Treat it as immutable after assembly. `makeCase` supports `n` (integer 1–12),
`kind` (`quadratic` or `affine`), `E` (Pa), `nu`, `rho` (kg/m³), `lengths` (three
positive metres), and `strain` (maximum exact axial strain, positive and <=0.05).
Defaults are the chapter's authored 40×20×20 mm block, 100 kPa, 0.25, 1000 kg/m³,
quadratic load and 0.02 exact maximum strain. Changing these options also changes
the manufactured compatible body force and boundary tractions; this is a bounded
fixture API, not an arbitrary-load simulation framework. The upper mesh bound
limits accidental synchronous browser work; it does not guarantee frame latency.

| Export | Arguments | Return / meaning |
|:--|:--|:--|
| `makeMesh` | `n=3, lengths=[.04,.02,.02]` | `nodes`, positive `tets`, outward `surface` triangles with unit normal and area, `n`, `lengths` |
| `materialMatrix` | `E, nu` | Lamé constants and engineering-strain `D`; accepts E>0 and -1<nu<0.5 |
| `element` | `nodes, tet, material` | V, B, 12×12 row-major K, shape gradients, global dofs and six compliant modes; rejects nonpositive volume |
| `makeCase` | options above | Common preassembled problem, `exact(X)` and `exactStrain(X)` |
| `applyStiffness` | `p, u` | Full K times displacement, before clamp elimination |
| `solveReference` | `p, {h=null,u0,v0,rtol=1e-10,atol=1e-12,maxIterations=10000}` | `u`, `h`, iterations, `converged`, residualN, targetN, stiffnessApplications and actual elementVisits; h=null static, h>0 one implicit step |
| `solveCompliant` | `p, {h=.0005,u0,v0,sweeps=5,reverse=false}` | `u`, h, sweeps, multipliers and constraintVisits; sweep cap 10000; zero sweeps returns force predictor |
| `diagnose` | `p, u, {h=null,u0,v0}` | Energies (J), max displacement (m), Frobenius max strain tensor norm, free residual (N), relative residual, reactions (N), resultants and balance (N), per-element strain and stress (Pa) |
| `continuumError` | `p, u` | Static polynomial-reference relativeL2, l2RmsM, relativeEnergy and energyNormSqrtJ; no transient reference implied |
| `difference` | `p, u, reference, {h=null}` | relativeObjectiveNorm (elastic norm for h=null, stiffness+inertia norm for h>0) and maxNodalM |

`u0` and `v0` default to zero and must be node-major finite arrays in metres and
m/s of exactly 3×node-count entries. The clamped entries must be zero. Each solve
allocates a new result; neither mutates its inputs or carries history across
calls. To advance a further implicit step, pass the previous displacement and
`v=(u_new-u_old)/h` to either solver. This capability is tested for a nonzero state;
a full transient trajectory or anatomical time integration is not validated.

`diagnose` must receive the **same h and initial state** as the solve. For static
mode it reports zero kinetic energy and no numerical step dissipation. Its
`loadDotDisplacementJ` always means final f dot u, not step work. Static ramp work
is one half of that value; step work is f dot (u_new-u_old). Reactions are force
**on the block**, retained only at fixed coordinates. `balanceN` is external plus
reaction minus inertia; a finite-sweep nonzero defect is algebraic error, not an
extra physical load. Stress is computed from strain at the reported u; finite
XPBD multipliers need not yet match those constitutive forces.

`data/example.json` (schemaVersion 1) contains a directly renderable n=3 mesh:
`nodes[v]=[x,y,z]`, `tetrahedra[e]=[v0,v1,v2,v3]`, and
`surface[f]={tri:[v0,v1,v2],normal:[nx,ny,nz],area}` with outward winding. A vector
coordinate is `u[3*v+d]`, where d=0,1,2 for x,y,z. The serialized `fixed` entries
are 0/1 and apply per coordinate. `massKgPerDof` repeats each physical nodal mass
three times; sum one coordinate per node for total mass. `forceN` includes loads
at fixed coordinates so reactions can be recovered. JSON arrays replace typed
arrays; convert with `Float64Array.from()` if helpful.

The example contains `exactStaticU` (nodal analytic samples), a `static` FEM state,
an `implicit` PCG state, and seven `compliant` states indexed by sweep count.
Each solved state contains unscaled u, scalar diagnostics, per-element stress and
strain, and clamped reactions. Stress order is xx,yy,zz,xy,yz,zx; strain order is
xx,yy,zz,gamma_xy,gamma_yz,gamma_zx. The `parameters`, `hSeconds`, units and layout
are serialized with the mesh. The implicit and compliant states all start at
rest; `exactStaticU` is not their transient target. Stress color averaging is a
renderer choice and does not change the piecewise constant element field.

`data/reference.json` contains full-precision static refinement, the matched
implicit comparison, timestep/mesh solver sensitivities and raw timing samples.
`data/tables.md` is its generated human-readable counterpart. The source-bound
`data/test-receipt.json` records the actual focused test invocation and output;
`data/provenance.json` records payload SHA-256 and byte counts. Regeneration runs
the focused tests and fails if they fail. Timing values and UTC receipts vary;
numerical fixtures are deterministic in the recorded runtime. Browser/platform
bit-for-bit floating-point identity is not promised.

## Integration by the book author

1. Import `continuum.mjs` into the browser lesson and use the same options and h
   in both solvers. No extra npm package is needed. Copy/import the contribution
   with relative paths appropriate to the book build's source/output layout.
2. Reassemble after changing mesh/material/case; solve after changing h/sweeps.
   Check `reference.converged`. Display `diagnose` and `difference` against that
   matched discrete reference. Keep static continuum error a separate display.
3. Draw `p.mesh.surface` at X+u; use identical cameras and an explicitly labeled
   display magnification for both states. Do not inject these synthetic forces
   into the elbow or relabel this mesh as anatomical skin. Draw clamps and loads.
4. Add `chapter.md` to the book's chapter sequence and retain its ordinary
   Markdown equations/tables/citations. It has no custom demo or proof markers
   and is not registered in `book/book.json`. The generated evidence between
   comment markers is refreshed by `generate.mjs`, so HTML/PDF readers can see
   the same numbers without the live renderer.
5. Register this contribution's test command in the author's validation workflow
   when integrating. The existing `npm test` glob will not discover it as-is.
   Nothing in this branch changes the application, assembly, proof registry,
   existing chapter files, dependency lockfile or CI workflow.

The write set is limited to the files listed above plus `data/test-receipt.json`.
`VALIDATION.md` describes checked behavior and remaining limits. `sources.json`
contains primary-source access records, including the inaccessible course-notes
limit. Original authored code, prose and geometry retain the repo's Apache-2.0
licence; cited research/data retains its own rights and is not redistributed here.
