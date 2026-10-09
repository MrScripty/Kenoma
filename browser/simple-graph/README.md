# Simple posing scene editor and portable binding

This independent, non-simulation scene editor uses a depth-tested Three.js
viewport and the existing Rust/WASM graph generator. It supports multiple
characters, hand/foot IK targets, elbow/knee pole targets, root placement,
character turn, directional head yaw/pitch, per-character colors and undo/redo.
It imports no research solver. Scene persistence uses the isolated SQLite contract
below. The Kenoma book embeds this same editor alongside separately owned
educational/research adapters using the shared `browser/embedded` presentation.

## Posing and scene controls

Drag round hand/foot targets to pose a limb; diamond poles control its bend
plane. Select a control from **Handle** when it is hidden behind another control.
A selected handle also has axis arrows for movement at fixed world X/Y/Z.
Direct dragging uses the camera plane. Drag **Root** to move the whole character;
Select **Turn character** for its Y-axis rotation ring, or **Turn head** for local yaw/pitch rings. The integrated mannequin head uses a smooth forehead, jaw and chin silhouette. All posing uses scene handles: no sliders. With the canvas focused, arrow keys move a selected handle (Alt for depth); rotation handles use arrows for yaw/pitch. Shift makes smaller adjustments.

**+ Character**, character selection (dropdown or mesh picking), **Remove**, and
the color swatch operate independently per character. New characters use free
floor slots. Drag empty space to orbit, right-drag to pan, scroll to zoom; touch
supports handle dragging, orbit and two-finger camera gestures. **Frame** fits
the scene. **F** frames, **Delete** removes, **Ctrl/⌘ Z** undoes,
**Ctrl/⌘ Shift Z** redoes, and **Escape** cancels a drag. Help stays collapsed.

Edits have a 100-entry undo history. **Save** downloads a compact `.human.sqlite`
scene; **Open** restores characters, poses and colors as one undoable edit. Save
before reloading and Open afterward; there is no automatic storage. See the
[scene file contract](SCENE_FILES.md) for limits and embedding APIs. Animation is
not implemented. The `human_surface` crate creates the neutral connected body/head surface once;
`human_rig` binds it and deforms fixed topology as the pose changes. Touching or
crossed limbs retain their vertices and cannot fuse. Contact may interpenetrate:
this is an artistic rig without collision simulation. A dedicated worker performs
binding/deformation; handles update immediately while the latest mesh catches up.
See [rig API version1](RIG_API.md) for the additive consumer contract and limits.

## Headless kinematics and scene state

`rig.js` exports `solveTwoBone({root,joint,end,target,pole})` and `LIMBS`.
The analytic solver preserves both segment lengths and returns `{joint,end,
target,status}`. Status is `reachable`, `clamped-near` or `clamped-far`. Requested
unreachable handles remain where placed while the solved endpoint clamps to the
reach annulus. Collinear poles use the original bend plane, then a deterministic
perpendicular. This prevents NaNs; it does not promise continuity across an
exactly singular bend-plane switch. There are no joint limits, forces or physics.

`scene-state.js` exports `SceneModel(baseGraph)` for the canonical 16-node human.
Its frozen `state` snapshot contains version, characters, selectedId and nextId.
Characters own graph, rig, color, placement/yaw and head yaw/pitch. Graphs and rig
targets use local coordinates; the renderer applies placement and yaw to world
space. Actions (`dispatch`) are add/select/remove/color/placement/head/ik.
`beginGesture/commitGesture/cancelGesture` group atomic drag edits; `undo/redo`
restore snapshots. Selection alone does not create history. IDs never recycle.
The model solves from immutable rest lengths, rather than accumulating drift.
It is testable with Node and has no Three.js, browser, WASM or physics dependency.

## Build and serve

Prerequisites: Rust with `wasm32-unknown-unknown`, Python 3.11+ for build metadata,
and a `wasm-bindgen` CLI matching Cargo.lock (currently 0.2.129).

```sh
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli --version 0.2.129 --locked
browser/simple-graph/build.sh
python3 -m http.server 8000 --directory browser
```

Open `http://localhost:8000/simple-graph/`. `pkg/` is generated and ignored.
When copying the editor to a static site, retain `simple-graph/` (including
`pkg/` and `vendor/`) and its sibling `embedded/` directory. Serve over HTTP(S), with `.js` as JavaScript
and `.wasm` preferably as `application/wasm`. Relative imports work under a
GitHub Pages project subpath. No cross-origin-isolation headers or server API
are needed. An ordinary iframe can embed `index.html`; no parent messaging is
implemented. Building the book packages both directories; deployment remains
a separate operation. `simpleGraphEditor.dispose()` releases the editor when
a custom host unmounts it.

For a custom host, copy `client.js`, `client.d.ts` and generated `pkg/` together;
the editor HTML/renderer and headless rig modules are optional. Keep glue and WASM files from the same build.

```js
import {createSimpleGraph} from './simple-graph/client.js';
const generator = await createSimpleGraph(); // reject on init/network failure
const sample = generator.request({version: 1, operation: {type: 'mannequin'}});
if (!sample.ok) throw new Error(sample.error.message);
const posed = generator.request({version: 1, operation: {
  type: 'edit', graph: sample.graph,
  commands: [{RotateBranch: {pivot: 5, child: 6, axis: [0,0,1], radians: 0.8}}],
}});
if (posed.ok) uploadToYourRenderer(posed.mesh);
```

## Contract

`client.d.ts` describes the public request/response shape. Every request names
protocol version 1 and an operation: `mannequin`, `generate`, `edit`, or `surface`. The first three preserve the original general graph contract and overlapping primitive output. `surface` takes the canonical 16-node mannequin graph, optional `head: {yaw, pitch}` in radians and `surface_options: {cell_size}` (default 0.016 m). It returns a connected mannequin mesh plus the applied head/options, or `invalid_surface`. Head rotation is Qy(yaw) * Qx(pitch), about node 3, with +Z facing forward. See `crates/human_surface/README.md` for limits and topology guarantees.
Generate/edit take a general source graph; options are optional and default to the
core settings. Edit applies at most 128 commands to a private graph. On success
it returns the new graph, options and generated mesh. The caller's graph is
never mutated; failure returns no partial graph or mesh. Hosts can retain graph
snapshots for undo and send those snapshots back to regenerate.

Mesh arrays contain nested XYZ positions/normals, flat u32 triangle indices,
source provenance and recoverable diagnostics. Coordinates, winding, radii and
pose rules are the existing `human_core` contract. IDs/counts are unsigned
32-bit integers on both native and WASM targets. The Rust boundary rejects
requests over 2 MiB before parsing; core resource/geometry limits also apply.
The JS facade accepts plain JSON values and rejects non-finite numbers,
accessors, cyclic/repeated object references and undefined values. Numbers are
validated again by Rust. No physics loop runs in the binding. The additive rig operations retain explicit instance-local handles; see [rig API version1](RIG_API.md).

Operation errors use `{version:1, ok:false, error:{code,message}}`; code is the
stable discriminator, message is explanatory. Success uses `ok:true` with
`graph`, `options`, `mesh`. Calls are synchronous after async initialization;
for large graphs, a host can initialize the same adapter in a module Worker.
The editor worker integration is tested with real browser interactions and stale-result lifecycle cases. JSON copies are intentional for
this first portable boundary; typed-array/zero-copy performance work is deferred.
Determinism means repeated identical ordered input on the same platform, not
bit-identical native/browser trigonometry across all platforms.

## Dependencies and verification

Three.js 0.180.0 is independently pinned in package-lock.json and vendored under
`vendor/`, including its MIT license, for offline static serving. To refresh the
same pinned vendor files, run `npm ci` here and copy `build/three.module.js`,
`build/three.core.js`, `examples/jsm/controls/OrbitControls.js`,
`examples/jsm/controls/TransformControls.js` and `LICENSE` from node_modules/three.
There is no commercial rigging package, CDN runtime or research dependency.

From the repository root:

```sh
node --test browser/simple-graph/tests/rig.test.mjs browser/simple-graph/tests/scene.test.mjs
PLAYWRIGHT_MODULE=/absolute/path/to/playwright-core/index.mjs \
CHROMIUM=/usr/bin/chromium node browser/simple-graph/tests/browser.mjs
```

The tests use Playwright (tested with playwright-core 1.57.0) and Chromium. If
PLAYWRIGHT_MODULE is omitted, normal Node resolution imports `playwright`.
The browser suite starts its own local server and tests iframe/subpath embedding,
real WebGL, actual handle/gizmo dragging, scene isolation, picking, colors,
head direction, camera controls, keyboard history, cancellation, unreachable
inputs and phone/touch behavior. The original WASM contract remains tested too.

Ignored `test-output/` contains desktop and phone screenshots plus
`scene-editor-verification.json` with commit/dirty status, exact scene, browser
version, WASM hash and checks. Captures render actual WASM body buffers with
an integrated WASM head; no generated-image substitute is used. Native surface tests
independently establish connectivity, manifold topology, winding and normals. Browser screenshots are
visual evidence, not numerical proofs.
