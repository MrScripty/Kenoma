# Portable browser binding milestone

2026-10-09. Starts from `24b283c8078839223190beaa805523b30e36df5e`.

Before implementation, extend the written ownership boundary to new
`crates/human_wasm/`, `browser/simple-graph/`, root Cargo manifests/lockfile,
and this ADR only. Preserve the existing core and persistence implementation.
Do not edit education/research, import solvers, choose the shared GUI host,
change permissions, deploy, or push. This is an isolated binding/demo, not the
final shared GUI. SQLite is not a WASM dependency.

Use a versioned JSON request/response boundary. Graph and mesh values use the
core contract; calls return structured typed errors. A batch of commands is
applied to a private graph copy and returns graph+mesh only on complete success.
The JS facade rejects non-finite numeric values before JSON serialization can
silently turn them into null. Input size and batch length are bounded. Static
hosting needs only ES modules and a WASM file; no server API is required.

New dependency: `wasm-bindgen`, owned only by human_wasm, to provide supported
Rust/JS string and memory lifetime glue. Feature defaults suffice; a matching
CLI generates browser modules. Alternatives were unsafe handwritten WASM memory
exports or a duplicate JS geometry implementation; both increase correctness
risk. Its macro/build-time dependency graph is pinned by Cargo.lock. Remove it
by replacing this adapter, leaving core untouched. `serde`, `serde_json` and
core are otherwise existing dependencies. The demo uses built-in canvas APIs
and no CDN/rendering dependencies. Browser automation is a development-only
Playwright tool, not a runtime dependency.

## Verified result

The Rust export is `human_wasm::evaluate`; `browser/simple-graph/client.js` is the
portable ES-module facade, with matching `client.d.ts`. The demo renders the
actual returned triangle arrays using Canvas 2D and allows elbow-only posing.
It is a small software painter renderer, not a production depth-buffer viewport.
Native and WASM inputs share an explicit u32 ID/count contract before decoding
core usize values. Error envelopes have stable codes and no partial outputs.

Verified with Rust 1.99.0, wasm-bindgen 0.2.129, Playwright-core 1.57.0 and
Chromium 151.0.7922.173:

- Formatting, strict all-target/all-feature Clippy, all-feature and no-default
  workspace checks passed.
- Workspace tests passed: 24 integration tests and 1 doctest.
- Release wasm32 build and matching web glue generation passed.
- Actual browser execution passed 17 checks, including iframe/subpath embedding,
  mesh counts, deterministic generation, isolated posing, edge lengths, valid
  buffers, failed batch preservation, invalid inputs, interactive slider/reset,
  visible mesh pixels and no external runtime requests or page exceptions.
- Independent review reran all 17 browser checks and the 3 native adapter tests.
  Its joint-label and platform-integer findings were fixed and verified.
- No changes to core/persistence, original plans or education/research files.

The sample produces 820 vertices / 1536 triangles. Generated WASM SHA-256:
`4795d4cc2812ab1d4166fa7ecaf6a5e908a2ee2d5b0359c5fe33c348697f4410`.
Ignored test-output captures include a real screenshot and a JSON receipt with
source commit, dirty flag, exact source/posed graphs, browser version and mesh
hash. Generated pkg files are reproducible build outputs, not committed assets.

Remaining limitations: synchronous JSON copies (worker use is possible but not
verified), a minimal demo renderer, no final shared GUI or browser persistence,
no hosting-repository decision, and no deployment. None blocks the scoped binding.
