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

Proposed files: `continuum.mjs`, `tests/continuum.test.mjs`, `generate.mjs`,
`data/reference.json`, `data/example.json`, `data/tables.md`, `data/provenance.json`,
`chapter.md`, `README.md`, `VALIDATION.md`, and `sources.json`. All generated files
will be local contributions, not edits to the book build. Full data/API and
integration instructions will be included here with the completed evidence.

Run from the repository root:

```sh
node --test education/contributions/continuum_reference/tests/*.test.mjs
node education/contributions/continuum_reference/generate.mjs
```

Apache-2.0 for this original code, prose and authored geometry, under the repository
licence. Primary papers are cited, not redistributed. No claim of clinical
calibration, anatomical validity, nonlinear rotation invariance or contact.
