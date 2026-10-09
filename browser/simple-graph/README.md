# Portable simple graph browser binding

This is an independent static demo and JavaScript adapter for `human_core`, not
Kenoma/Rheon's final shared GUI. No solver, simulation, SQLite, CDN or rendering
framework is imported. `human_wasm` compiles the same tested core to WASM.

## Build and serve

Prerequisites: Rust with `wasm32-unknown-unknown`, Python 3.11+ for build metadata,
and a `wasm-bindgen` CLI matching Cargo.lock (currently 0.2.129).

```sh
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli --version 0.2.129 --locked
browser/simple-graph/build.sh
python3 -m http.server 8000 --directory browser/simple-graph
```

Open `http://localhost:8000/`. `pkg/` is generated and ignored; retain it when
copying the demo to a static site. Serve over HTTP(S), with `.js` as JavaScript
and `.wasm` preferably as `application/wasm`. Relative imports work under a
GitHub Pages project subpath. No cross-origin-isolation headers or server API
are needed. An ordinary iframe can embed `index.html`; no parent messaging is
implemented. This task does not publish or select a hosting repository.

For a custom host, copy `client.js`, `client.d.ts` and generated `pkg/` together;
the demo HTML/renderer is optional. Keep glue and WASM files from the same build.

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
protocol version 1 and an operation: `mannequin`, `generate`, or `edit`.
Generate/edit take the canonical graph; options are optional and default to the
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
validated again by Rust. No physics or animation loop runs in the binding.

Operation errors use `{version:1, ok:false, error:{code,message}}`; code is the
stable discriminator, message is explanatory. Success uses `ok:true` with
`graph`, `options`, `mesh`. Calls are synchronous after async initialization;
for large graphs, a host can initialize the same adapter in a module Worker.
Worker integration itself is not tested here. JSON copies are intentional for
this first portable boundary; typed-array/zero-copy performance work is deferred.
Determinism means repeated identical ordered input on the same platform, not
bit-identical native/browser trigonometry across all platforms.

## Actual browser verification

`tests/browser.mjs` starts its own local static server and embeds the demo under
`/preview/` in an iframe. It checks actual WASM fetch/initialization, source and
mesh counts, repeated generation, elbow isolation, edge lengths, finite buffers,
unit normals, failed batch rollback, non-finite/cyclic inputs, portable integer
bounds, slider/reset interactions, visible rendered pixels and browser errors.
It also checks that no external runtime requests occurred.

Use an installed Playwright package (tested with playwright-core 1.57.0) and
Chromium, then run:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright-core/index.mjs \
CHROMIUM=/usr/bin/chromium node browser/simple-graph/tests/browser.mjs
```

Without `PLAYWRIGHT_MODULE`, it imports `playwright` from normal Node resolution.
Output is ignored `test-output/kenoma-wasm-mannequin.png` plus a JSON receipt
containing source commit/dirty status, browser version, WASM SHA-256, posed-mesh
SHA-256 and the exact source/posed graphs. The screenshot renders actual generated
triangles with a graph overlay. The small Canvas painter renderer has no true
depth buffer and is a demonstration, not a final viewport or geometric proof.
Native tests independently check topology/winding. WASM compilation and browser
execution are separate verification steps.
