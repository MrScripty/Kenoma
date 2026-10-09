# Simple graph core

A separate, non-simulation graph-to-mesh system. No anatomical model, forces,
constitutive law, research engine or rendering framework is used.

```rust
use human_core::*;
let mut graph = mannequin();
let mut history = GraphHistory::default();
history.apply(&mut graph, &GraphCommand::RotateBranch {
    pivot: 4, child: 5, axis: Vec3::Z, radians: 0.8,
})?;
let mesh = generate_skin_graph_mesh(&graph, &SkinGraphGenerateOptions::default())?;
assert!(!mesh.indices.is_empty());
history.undo(&mut graph)?;
# Ok::<(), GraphError>(())
```

## UI-facing contract

`SkinGraph { nodes, edges }` is authoritative and serde serializable. Each node
has model-space `position: [x,y,z]`, `radii: [x,y]`, and `root: bool`; edges have
`a` and `b` node indices. Units are meters, right-handed, +Y up, +X character right,
+Z forward. No generated mesh is an editable or persistent asset.

Commands are serde's externally tagged values, e.g.
`{"MoveNode":{"node":5,"position":[0.6,1.3,0.0]}}` or
`{"RotateBranch":{"pivot":4,"child":5,"axis":[0,0,1],"radians":0.8}}`.
Send all edits through `GraphHistory::apply` or `apply_graph_command` and
regenerate after success. Selection stays in the host UI. IDs are source vector
indices; deletion compacts them, so clear or remap selection after deletion and
history changes. A rotation moves the component on the child's side of a cut
edge about the pivot; cyclic/ambiguous cuts return `AmbiguousBranch` atomically.
Moving a single node intentionally changes adjacent lengths (modeling);
rotating a branch preserves them (posing). There are no joint limits or IK.

Output `GeneratedSkinMesh` contains parallel positions, normals, source-node and
source-edge provenance, flat triangle indices and diagnostics. Mesh winding is
CCW viewed from outside. A renderer can copy the arrays into its own mesh
buffers. It does not need a solver, project database or this crate's internals.
`GraphError` is a typed fatal error; `Diagnostic` enumerates recoverable warnings
(empty input is informational). No generated mesh is returned after a fatal
error. Generation is deterministic for the same ordered input, options and
platform; cross-platform bit-identical trigonometry is not promised.

Options: ring sides clamp to 4–32; subdivisions clamp to 1–64; positive finite
spacing required. Defaults: 8 sides, 1.25 radius spacing factor, 64 segment cap.
Radius components below 0.01 are clamped in generated geometry and diagnosed;
authoring values are preserved. Coordinates/radius magnitudes must be <=1000.
Nodes, edges and generated vertices have explicit resource ceilings. Highly
collapsed geometry that cannot form finite nonzero faces fails with
`InvalidGeometry`, rather than exporting corrupt triangles.

## Geometry scope

Each edge produces a flat-capped tube. Isolated nodes and junctions get low-poly
ellipsoids. Frames propagate from roots. Junctions (including degree-two bends)
use overlapping closed components, with no weld/boolean union; this is suitable
for a reference mannequin, not watertight fabrication or simulation input.
Branch nodes report `BranchFallbackOverlap`. Loops use the first transported
frame and report approximation. UVs, loose-branch flags, generated armatures,
fixed-topology morphing, Bevy rendering and browser bindings are deferred.
SQLite persistence lives in `human_persistence`; the core compiles for WASM
without it. A compiled WASM target alone is not yet a JavaScript binding or GUI.

## Verification

From the repository root run `cargo test --workspace`,
`cargo clippy --workspace --all-targets --all-features -- -D warnings`,
`cargo fmt --all -- --check`, and `cargo check -p human_core --target wasm32-unknown-unknown`.
See `tests/graph.rs` for golden edge topology, surface validity, root/loop cases,
pose isolation, edit rollback, undo/redo and numeric boundary coverage.
