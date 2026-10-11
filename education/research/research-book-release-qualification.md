# Research-book release qualification

## Teaching-source follow-up

The preview command in [the education README](../README.md#research-book-teaching-feature) now works from a shallow checkout with no pre-existing build directory. It reconstructs only the two pinned existing repository snapshots, verifies the publication's 1,102 files and 947 source inputs, and packages the current reader. A first clean-checkout test installed locked dependencies, fetched both missing commits, served the preview and inspected the actual force canvas/readouts without browser errors. An offline rebuild produced the same manifest. Missing offline objects, an existing output directory and changed canonical source were rejected. This is preview reproducibility, not a full release PASS.

The four requested screenshot comparisons are [committed documentation](../../docs/review/research-book-teaching/README.md), with source identities and exact image hashes. Automated capture collections remain ignored and the generated-output guard is unchanged.

An actual PDF check found that the new worked observations printed at 9 points. The teaching print styles now use 10.5-point labels/observations to stay above the existing 10-point measured floor, including Chromium's fractional rounding. The checker now requires every complete worked reading, including its expected observation, to survive printing at the point floor; its new negative controls reject undersized and missing observations. The preserved-evidence preview rendered all 95 complete readings at a measured minimum of 10.5 points. This preliminary print check does not replace the full book/proof/artifact gates below.

## Retained Rust and independent-poser evidence

The Rust/poser evidence is retained from a successful **individual gate**, not a successful full-book run or a fresh local compilation. At the audited feature head `f998586862b0c56e602ab6bdb6d2869693f84744`, all **79 tracked files** under `crates/` and `browser/`, including tests, plus `Cargo.toml` and `Cargo.lock`, are byte-identical to reported head `5c4b4fbe495a3ad362293569ca4b83d28d1aa9dc` of [hosted run 306](https://github.com/MrScripty/Kenoma/actions/runs/37991146412). GitHub reports **success** for its [“Build and test the isolated poser and its browser ABI” step](https://github.com/MrScripty/Kenoma/actions/runs/37991146412/job/114025610899). The overall run **failed** later in “Check mechanics and build checked proofs and book”; its publication receipt identifies mobile screenshot capture as the failure. No full-suite PASS follows from this reuse.

The unchanged gate ran these commands from `education/`:

```sh
rustup toolchain install 1.90.0 --profile minimal --target wasm32-unknown-unknown
rustup default 1.90.0
cargo install wasm-bindgen-cli --version 0.2.129 --locked
../browser/simple-graph/build.sh
cargo test --locked --workspace
npm ci --prefix ../browser/simple-graph --ignore-scripts --no-audit --no-fund
npm --prefix ../browser/simple-graph test
export PLAYWRIGHT_MODULE="$(python3 -c 'from pathlib import Path; import playwright; print(Path(playwright.__file__).parent / "driver/package/index.mjs")')"
export CHROMIUM="$(python3 -c 'from playwright.sync_api import sync_playwright; p=sync_playwright().start(); print(p.chromium.executable_path); p.stop()')"
node ../browser/simple-graph/tests/browser.mjs
node ../browser/simple-graph/tests/rig-browser.mjs
node ../browser/simple-graph/tests/scene-files-browser.mjs
```

`build.sh` enforces the Cargo.lock glue-generator version, then runs `cargo build --locked -p human_wasm --release --target wasm32-unknown-unknown` and `wasm-bindgen --target web --out-dir browser/simple-graph/pkg target/wasm32-unknown-unknown/release/human_wasm.wasm`. The identical hosted step text has SHA-256 `6821eab7144dd908a71eb5ca6dab9ca6d3cfee9892fac656fdd9d819132ecc8b`.

The detailed per-file source/hash comparison is an external audit receipt at `/tmp/kenoma-rust-reuse-f998586.json`, SHA-256 `615623b7c3e540ac8d14fbbf8159093161c4d963e82b7dddf2b23d72a2d1d291`. Reproducible source bindings are:

| Bound input | Identity |
| --- | --- |
| `crates/` Git tree, both commits | `e0b8eb0cac0ad9508fc78bf8f8a393db537aad9c` |
| `browser/` Git tree, both commits | `136cab9252ad80be0efe83f06b86dfabf11cb7ad` |
| `Cargo.toml` SHA-256 | `43029e0ae1b78a66c79d52a5f04db43ab169a7e3e9460114eaa0611f4f087bea` |
| `Cargo.lock` SHA-256 | `9298d2f19cd490f001a1aafd43884889b9768bb9fcd97477063811970867b9d4` |
| Preserved build manifest SHA-256 | `415d3d15c6f9644660bd2dd3983367bb30548188080ab0fbf7de45c4b7ed6d02` |
| Preserved `human_wasm_bg.wasm` SHA-256 | `6dc365e45ea54659b41386125c9df02a19b209056df82a5a7df70e41994084bf` |
| Preserved `human_wasm.js` SHA-256 | `d9d204fcefeb966970a1112997820a0e1b18c491c4fb30c705f06a1ee5971666` |

All **62 non-generated GUI source bindings** in that preserved manifest match the current source; all four preserved WASM/package files match their recorded hashes. The manifest identifies build source `ae000b59f309dcf6357922ad1af459d86efd4e8c`, and the preserved publication receipt binds it to merged source `dc8b692e9f85c8ed8e84562789ba73df5e3c62b6`. This separately justifies reuse of those exact binary bytes. It does **not** claim that the preserved binary was downloaded from hosted run 306, or establish compiler reproducibility.

GitHub job metadata was readable, but both run-log and job-log download endpoints returned `Forbidden`. Consequently this audit does not invent test counts or an actual PR merge-checkout SHA from unavailable logs. Local `cargo`, `rustc`, `rustup` and `browser/simple-graph/pkg` were absent. No redundant toolchain installation or source-identical Rust rerun was performed.

## Hosted status at the audited feature head

At `f998586862b0c56e602ab6bdb6d2869693f84744`, GitHub returned **zero branch runs and zero commit check-runs**. The education workflow triggers pushes only on `main` and `education/**`; `feature/research-book-teaching` therefore requires a ready PR or an explicit `workflow_dispatch` with `publish=false` for full hosted qualification. No dispatch, merge or deployment was requested by this audit.

The latest successful full main book run, [37971771277 at `113446886a0e3191924573d37d23b7d91f5b05bb`](https://github.com/MrScripty/Kenoma/actions/runs/37971771277), predates the Rust/browser source and cannot qualify it. [PR15 run 38165657020](https://github.com/MrScripty/Kenoma/actions/runs/38165657020) passed draft contracts and the architecture contribution, with the full build skipped. [Main publication run 38006678689](https://github.com/MrScripty/Kenoma/actions/runs/38006678689) assembled already-preserved bytes; it was not a new build qualification.

The retained gate covers the unchanged independent poser only. The new chapter adapters, worked sequences, responsive reader, generated HTML/PDF, and their browser interactions require their own final-source evidence. The final hosted run and its exact source SHA remain to be recorded after source changes finish.
