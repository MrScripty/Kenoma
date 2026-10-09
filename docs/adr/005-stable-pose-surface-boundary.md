# Stable pose surface and responsive deformation

Baseline: published 2eb92a5d0924b5f2cbf310597dbd7b399fab8692.

Acceptance cases established before implementation:
- Hand against torso and arms crossing in front: preserve exact rest indices,
  vertex count and connectivity, with no new welds between contacting surfaces.
- Crossed legs and deeply bent elbows/knees: finite outward normals and nonzero
  triangles, with joint cross sections retained rather than collapsing to a line.
- Neutral and existing posing controls remain deterministic, headless and isolated.
- Actual mouse/touch dragging must update handles without waiting for extraction;
  stale geometry results cannot overwrite newer poses, undo or removed characters.
- Preserve the published v1 surface operation and consumer contracts. Introduce
  additive explicitly versioned rig contracts, never silently change old semantics.

Bounded strategy to investigate: extract a connected neutral surface once, bind
it to the canonical artistic rig, then deform fixed topology per pose. Prefer
volume-preserving blended rigid transforms over remeshing. Touching surfaces may
interpenetrate (there is no collision simulation), but must not fuse. This is a
small artistic rig, not anatomical research or a general-purpose auto-rigger.
If robust joint deformation requires a major replacement, report before expanding.

Ownership before edits:
- rig_math worker: new crates/human_rig/** only, binding/deformation contracts,
  tests and documentation. Must coordinate shared API before integration.
- scene_ui worker: browser/simple-graph/renderer.js plus new async worker/bridge
  files; responsiveness and stale-result lifecycle tests. Do not edit core/adapter.
- parent: workspace manifest/lock, human_wasm adapter, TypeScript contract,
  integration tests/docs/commit/push and browser acceptance coordination.
- independent reviewer: read-only geometry, asynchronous lifecycle and verification.
No changes to education/research, physics, campaigns, security, deployment or main.

Baseline reproduced with the published WASM and `tests/contact-cases.mjs`:
neutral has46,728vertices and Euler characteristic2. Hand-on-torso changes to
45,466vertices and Euler characteristic0, demonstrating an added welded loop.
Crossed arms change to41,008vertices. Full surface requests cost210–328ms in
this diagnostic desktop run (includes JavaScript topology bookkeeping). The
correction must retain the neutral index buffer for every acceptance pose.

Integration ownership handoff: scene_ui additionally owns the existing
`tests/browser.mjs` adaptation; parent owns `tests/rig-browser.mjs` and
`tests/contact-cases.mjs`. Browser acceptance additionally requires pointer
handler and mesh-application p95 below50ms in the reference Chromium run.
The initial implementation passed these at7.8ms and29.6ms respectively, but
visual review found facet/seam shading from discrete normal reconstruction.
Correct normal smoothing before final acceptance; fixed-topology geometry is
not by itself sufficient visual evidence.
