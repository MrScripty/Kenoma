# Independent scene editor milestone

2026-10-09. Baseline binding commit `6b3964c6d5717deee07fe04f2f5401b3eff7380a`.

Written ownership boundary before editing: preserve human_core, human_persistence,
human_wasm, client.js and their interfaces. New pure JavaScript kinematics and
scene state live under browser/simple-graph, separate from the renderer and
usable headlessly. The renderer continues to request meshes from the existing
WASM graph contract. No research imports, forces, simulation, deployment or push.

Worker ownership:
- Rig/math: rig.js, scene-state.js, tests/rig.test.mjs, tests/scene.test.mjs.
- Scene/render/UI: index.html, demo.js, editor.css, renderer.js, package manifests,
  vendor dependencies and local .gitignore entries only.
- Parent: browser automation, documentation, integration corrections after worker
  handoff, screenshots and Library deliverables.
- Independent reviewer: read-only review/tests after integration.

Shared scene contract:
`SceneModel(baseGraph)` starts with one character. `state` is a read-only snapshot:
`{version:1,characters,selectedId,nextId}`. Each character is
`{id,name,color,position:[x,y,z],yaw,head:{yaw,pitch},graph,rig}`. Graph positions
and IK targets/poles are character-local meters; placement/yaw transforms them
into scene space. All rotations are radians. Rig keys are rightArm,leftArm,
rightLeg,leftLeg; entries expose `{target,pole,status}`. Pose changes only the
corresponding middle/end nodes and preserve both rest lengths.

`dispatch(action)` accepts {type:'add'}, {type:'select',id}, {type:'remove',id},
{type:'color',id,color}, {type:'placement',id,position?,yaw?},
{type:'head',id,yaw?,pitch?}, {type:'ik',id,limb,target?,pole?}.
`beginGesture`, `commitGesture`, `cancelGesture`, `undo`, `redo` group drag edits
into one history entry. State must remain independent between characters and
invalid actions must not partially mutate it. No character-count-based IDs.

IK exports `solveTwoBone({root,joint,end,target,pole})` returning
`{joint,end,target,status}` and `LIMBS` mapping names to [root,joint,end] indices.
Use bounded analytic kinematics with deterministic fallback planes for singular
or unreachable inputs; no physical/anatomical interpretation.

The view uses real depth-tested 3D rendering, picking, orbit/pan/zoom and movable
handles. Visible UI is compact: toolbar, viewport, essential selected-character
controls and error feedback. Help is collapsed. Directional stylized head geometry
belongs to the view and has yaw/pitch orientation state; it is not anatomical mesh
replacement in the core. Browser tests must cover desktop and phone layouts.

Dependency decision: Three.js (MIT, already used by education, but independently
installed here) is permitted solely for viewport rendering, orbit and transform
controls. No education imports or shared dependency state. Vendor local runtime
modules plus their license for self-contained static serving; no CDN needed.
No commercial rigging dependency or new legal acceptance is introduced.

## Completed and reviewed

Implemented compact viewport-first desktop/phone UI, a real Three.js WebGL
viewport with depth testing, ray picking, OrbitControls and translation gizmos.
Hands/feet have IK targets, elbows/knees have pole handles, root movement and
character yaw use independent placement, and heads have recognizable face/back
cues plus orientation controls. The shaded grid floor is presentation only.
Per-character materials, source graphs and rig state are independent. Add/remove,
posing, color and orientation edits have bounded undo/redo; direct/gizmo drags
form one history transaction. IDs do not recycle and new characters find free
floor slots. Optional explanatory content stays under Help.

The existing Rust graph/core, SQLite adapter, WASM adapter and JS client remain
unchanged. Rendering continues to consume the same WASM-produced body buffers;
it omits the original head-edge surface and adds a stylized presentation head.
Kinematics are pure JS analytic geometry in rig.js, not a solver/physics import.

Independent review findings corrected before completion:

- Sparse vectors/radii could bypass Array.every checks: dense validation now
  rejects them atomically; selection-only gestures preserve history.
- Axis Escape could commit reset roundoff: cancellation suppresses gizmo events
  while restoring the exact scene snapshot.
- Nonowner touches could corrupt direct/axis drag lifetimes: shared pointer
  ownership now gates all down/move/up/cancel events before vendor listeners.

Verification:

- 15 rig/state tests pass, including 3000 deterministic numerical solves,
  singular/inner/outer reach boundaries, length preservation, immutable rest
  lengths, isolated character state, repeated add/remove, sparse inputs,
  rollback, gesture grouping and undo/redo.
- 49 real Chromium 151 browser checks pass: iframe/subpath loading, WASM
  contract regressions, WebGL/depth/grid/head rendering, actual IK/pole/root/axis
  drags, picking, independent colors/poses, add/remove, head facing, orbit/pan/
  zoom, keyboard history, exact Escape rollback, singular/unreachable targets,
  desktop1440x900, phone390x844, direct/axis multi-touch ownership and phone undo.
  Phone viewport height is609px with no horizontal overflow.
- Independent review reran all49 browser checks and15 rig/state tests, confirmed
  the fixes and reported no remaining blockers.
- Unchanged Rust workspace:24 integration tests and1 doctest pass; formatting
  and strict all-target/all-feature Clippy pass. JS syntax and first-party diff
  checks pass. Vendored three.core.js retains one upstream space-before-tab
  warning at line48480 so the dependency stays byte-identical to the package.
- All five vendored Three.js files exactly match locked three@0.180.0, including
  its MIT license. No permission/credential/security setting changes.

Remaining limits: in-memory scene only (reload loses it); no scene save/import,
animation, joint limits, finger/facial rigs or anatomical accuracy. Exact pole
singularities have deterministic fallback, not guaranteed continuous bend-plane
orientation. The body remains overlap geometry, not a welded surface. The shared
biomechanics GUI, its repository placement and public hosting are separate work.
No research campaign, push or deployment occurred.
