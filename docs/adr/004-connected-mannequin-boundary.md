# Connected mannequin surface and gizmo-only controls

2026-10-09. Baseline 3e9bc5864f4eba54a8adedc1d9ae5e1071ee6a97.

The user explicitly replaces the old overlap-mesh requirement with a continuous
connected character surface, including joint/neck/head transitions. Also remove
all sliders and cartoon facial primitives. Preserve research separation.

Ownership established before edits:
- Surface worker: new crates/human_surface/** only, deterministic headless implicit
  surface extraction, integrated smooth head, topology/math tests and docs.
- UI worker: browser/simple-graph/{renderer.js,demo.js,index.html,editor.css} only.
  Gizmos for root translation/yaw, head yaw/pitch and existing IK/poles; accessible
  keyboard/touch handling. No slider replacement that reduces posing capability.
- Parent: Cargo workspace/lock and WASM adapter integration/client types, browser
  tests, docs, screenshots, commit/push. Own shared contracts serially.
- Independent review: read-only tests and audit after integration.
No education/research paths, solver dependencies, campaigns, permissions changes,
merges or deployment. Commit/push development branch is explicitly authorized.

Shared interface: new human_surface crate exports
`HeadPose {yaw:f32,pitch:f32}` and `SurfaceOptions {cell_size:f32}` (serde/default),
`generate_mannequin_surface(&SkinGraph,&HeadPose,&SurfaceOptions)` returning
Result<GeneratedSkinMesh,SurfaceError>. Surface is for the canonical 16-node human;
its model-space source graph remains authoritative. All cranial/jaw/chin/forehead
and neck geometry must be in the extracted indexed surface, no appended primitive
meshes. Head orientation is character-local, yaw then pitch as Three YXZ.

WASM operation: {type:'surface',graph,head:{yaw,pitch},surface_options?:{cell_size}}
returns ordinary success graph/options/mesh; surface errors use code
'invalid_surface'. Existing generate/mannequin/edit remain backward compatible.
Renderer sends surface requests for all characters and uploads ALL indices,
removing all old head-edge filtering and separate facial/head meshes. Mesh cache
key includes graph and head orientation. item.head can be an empty transform
anchor for controls; it must not contain independent render geometry.

Tradeoff disclosed: bounded implicit extraction changes generated topology as
poses change. Source vertex IDs remain stable; generated vertex IDs do not.
The continuous manifold requirement is tested explicitly, not inferred from one
mesh object. No silent reduction to disconnected meshes or hidden rough preview.
Performance measurements must accompany actual desktop/phone verification.

Integration handoff: after completing the four UI files, the UI worker was
assigned `tests/browser.mjs` and `tests/surface-topology.mjs`; the parent retained
`tests/browser-support.mjs`. Review remains read-only.
