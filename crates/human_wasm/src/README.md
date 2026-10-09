# Portable binding

`lib.rs` owns versioned JSON request decoding, resource bounds, command batches,
error mapping and the wasm-bindgen export. It invokes only human_core. Native
tests exercise the same function compiled to WASM; real browser tests exercise
the generated module and JS facade separately.
