# WASM adapter

`evaluate(&str) -> String` is both a native-testable Rust API and a wasm-bindgen
export. See `browser/simple-graph/README.md` and `client.d.ts` for protocol version
1 and static hosting instructions. This crate depends on human_core and human_surface, not SQLite
or research code. All graph mutations occur on request-local state. Errors are
structured response envelopes; transport initialization errors belong to the JS
host. Unit coverage is in `tests/protocol.rs`; the actual compiled-module test is
`browser/simple-graph/tests/browser.mjs`.
