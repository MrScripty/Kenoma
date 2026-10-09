#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
# Keep generated JS glue and Rust ABI versions exactly matched.
version=$(python3 -c 'import tomllib; print(next(p["version"] for p in tomllib.load(open("Cargo.lock","rb"))["package"] if p["name"]=="wasm-bindgen"))')
if [[ "$(wasm-bindgen --version)" != "wasm-bindgen $version" ]]; then
  echo "Install matching glue generator: cargo install wasm-bindgen-cli --version $version --locked" >&2
  exit 1
fi
cargo build --locked -p human_wasm --release --target wasm32-unknown-unknown
wasm-bindgen --target web --out-dir browser/simple-graph/pkg target/wasm32-unknown-unknown/release/human_wasm.wasm
