# Additive artistic rig API, version 1

Compatibility baseline: Kenoma `2eb92a5d0924b5f2cbf310597dbd7b399fab8692`.
The existing protocol version1 `mannequin`, `generate`, `edit`, and `surface`
operations retain their semantics. In particular, `surface` still performs a
smooth union, so callers using it directly still get pose-dependent topology.
The new operations below require both `version:1` and `rig_version:1`. Consumers
such as Rheon can opt in independently; there is no research-engine dependency.

```js
const bound = client.request({version: 1, operation: {
  type: 'rig_bind', rig_version: 1, surface_options: {cell_size: 0.016}
}});
if (!bound.ok) throw Error(bound.error.message);
const posed = client.request({version: 1, operation: {
  type: 'rig_deform', rig_version: 1, rig_id: bound.rig_id,
  graph: posedGraph, head: {yaw: 0.4, pitch: -0.1}
}});
// Upload posed.mesh when posed.ok. Preserve graph and pose as source state.
client.request({version: 1, operation: {
  type: 'rig_release', rig_version: 1, rig_id: bound.rig_id
}});
```

`rig_bind` extracts the canonical neutral mannequin and retains its bound mesh
in the initialized WASM instance. Its `surface_options` is optional. Success
returns `version`, `ok`, `rig_version`, `rig_id`, neutral `graph`, zero `head`,
legacy default `options`, and indexed `mesh`. The legacy `options` field does
not control rig generation; `surface_options` controls binding resolution.

`rig_deform` takes a handle, posed canonical graph, and optional head yaw/pitch
(default zero). Success has the same envelope with posed graph/head/mesh. Vertex
IDs, triangle indices and source provenance remain stable for that binding.
Bone lengths, node radii and canonical topology must be preserved. No anatomical
constraints, collision forces or contact simulation are applied. Contact can
interpenetrate but cannot weld unrelated vertices or change connectivity.

`rig_release` returns `{version:1,ok:true,rig_version:1,rig_id,released:true}`.
Handles are unsigned32-bit, monotonic, instance-local and not persistent IDs.
Reinitializing another WASM realm does not restore them. At most16 bindings and
750,000 total bound vertices are retained. Release unused bindings; the editor
shares one neutral binding among its independent character poses.

Errors use the existing `{version:1,ok:false,error:{code,message}}` envelope.
New codes are `unsupported_rig_version`, `unknown_rig`, and `invalid_rig`;
`resource_limit`, malformed-request and serialization errors remain applicable.
Invalid deformation does not change or invalidate a binding. Headless native
callers can use `human_rig::bind_mannequin` and `deform_mannequin` directly.

## Responsive host integration

Calls to the adapter itself are synchronous. The supplied editor initializes a
separate adapter inside `rig-worker.js`. `AsyncRigBridge` sends only source poses,
coalesces pending revisions, and rejects stale results after undo/removal/re-add.
Renderer handles update immediately; the last valid mesh remains visible until
the newest mesh arrives. Geometry may temporarily lag the handles under load.
No alternate low-quality mesh or remeshing is used during dragging.

`renderer.whenIdle()` awaits the latest geometry, or rejects on failure.
`renderer.pending` reports queued/in-flight work; a character's `graphKey` is its
requested pose and `meshKey` its displayed pose. A custom consumer may use these
modules or implement its own worker around the same versioned operations. Do
not share rig handles between WASM instances. There is no parent-window protocol,
biomechanics integration, persistence of the scene, or deployment in this change.
