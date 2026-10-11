# Research-book release qualification

## Fresh local source, proof and print qualification

The implementation was built in a clean isolated checkout of `b6ff7af9010e867e6f8361ef4c5652147efa8391`. The later `85107192d6459cae8d0054fe59f5f7889618f7ec` commit adds documentation and curated screenshots only: all **979 build-input hashes** match the fresh manifest, with zero missing or changed inputs. The generated build retains its actual `b6ff7af` revision; it is not relabelled as a later commit.

The original dependency process completed **1,910 modules** from the pinned pristine Lean/mathlib sources after the official cache endpoint returned HTTP 403. All module sources, compiled objects, logs, locked transitive revisions and the toolchain were checked and hashed. ProofWidgets JavaScript was rebuilt from its pinned source before compiling its Lean modules; the earlier release-cache attempt and replacement are documented separately. The unchanged source build was not restarted, and a second identical dependency traversal was avoided because the verified closure includes every book and mixed-volume import.

The unmodified `npm run build` passed, freshly compiling **115 book claims across 14 families**, **27 separate mixed-volume research declarations** and **six separate nonuniform-kinematics Real contracts**. Its 90-state symbolic/geometry/text audit and 1,010 structural/data/provenance checks passed. These remain distinct kinds of evidence; the data checks do not establish clinical validity or JavaScript refinement.

The unmodified `npm run pdf` produced **252 pages**. The actual-PDF print gate passed all 115 statements, 14 complete proof sources and 95 complete worked readings. The worked readings measure at least **10.5 pt**; the overall checked minimum is **10.391289710998535 pt**, above the unchanged 10-point floor. Browser and package qualification are recorded separately below.

| Fresh artifact | SHA-256 |
| --- | --- |
| Build manifest | `04190aa103b21cfbe98382a9f29bb544b93c2fdf0617cbb684473dd9b5158a5c` |
| New 252-page PDF | `8949a336625ad37c04d514c3d6b5d8b2eb219e5509523c5e777a6f46240d7ddd` |
| Print-readability receipt | `3a34ab3293e05d4dbf45e46d94a448165763ff3379065a829039a4199f973281` |
| Source/dependency verification receipt | `0bf732cebe85fb56de2b80d5875ef12b71067c7c80c4ce1028c710a108aa9b6a` |
| Consolidated source/proof/PDF evidence | `55a594643b9fc8b7fef38d0a2978142f0ba5b6377484ff63afe98bc2171a762b` |

The local artifact is under `/workspace/kenoma-release-a473bdc/education/dist/`; the directory name is historical, while its clean checkout and build manifest identify `b6ff7af`. Command logs and the consolidated `source-proof-pdf-summary.json` are in that checkout's ignored `education/.artifacts/teaching-qualification/`. The dependency receipt is in the primary checkout's corresponding `lean/dependencies.json`. Generated artifacts remain untracked.

## Current hosted scope

[Hosted run 309](https://github.com/MrScripty/Kenoma/actions/runs/38176458524) was dispatched with `publish=false` at `a473bdc4411a380feac5b746949a64ecc23b4135`. Its **Rust/WASM and isolated-poser browser gate passed** in 407 seconds. At the report's 2026-10-11 22:30 UTC checkpoint, the original pinned proof-dependency step remained active; it was not restarted. The two production-source differences between that head and `b6ff7af` remove unsupported decorative arrow glyphs from `web/template.html` and `tools/teaching_sequences.py`; all Rust, poser, proof, scientific-kernel and JavaScript inputs are identical. The run also predates the two test adaptations below. Current HTML/PDF/browser evidence therefore binds the local corrected build, while unchanged-input hosted gates retain their actual source identity. This report does not claim a full hosted PASS. Subsequent status is available at the run link; a draft-PR contract check is also not a full hosted release qualification.

## Completed local browser and package qualification

The full post-build sequence passed all **28 stages**, retaining the two initial failures and their separately bound successful reruns. These stages cover original browser/mobile behavior; projection responsiveness, integration and negative controls; property/nonuniform/architecture labs; chapter examples and the reader; material, dissipative and serial controls and negative controls; proof/render inspection and capture reruns; anatomical/coupled/arm viewers; worker lifecycle; artifacts; and three print negative controls. Existing assertions, numerical thresholds and browser launch configurations remain in force. The coupled inspection was run against this exact main artifact to supply the native-page receipt required by the packager.

The reader exercised **95 desktop checkpoints at 1440 × 1000, eight phone checkpoints at 390 × 844 and eight narrow checkpoints at 320 × 844**, with manual/focus/wheel interruption, explicit resumption, queued-message replay, print/no-JavaScript reading and context-loss fallback. The standalone gate exercised **27 chapters × three widths = 81 views**, plus shared-dock selection and responsive disposal. The reader receipt's historical `PASS_RESEARCH_BOOK_PREVIEW_BROWSER` label describes interaction coverage only; its eight input hashes bind the freshly built site in this run. It is not used as a proof or package receipt.

The unchanged packager passed its proof, executable, browser, PDF and complete linked-resource checks, archive CRC verification and per-file byte comparison. The portable ZIP contains **1,145 files / 93,978,692 bytes**. It retains the actual `b6ff7af` build revision; the two later test sources are separately identified in the regression notes below. No scientific kernel or build input changed during these reruns, and the original build manifest and PDF hashes stayed unchanged.

| Final local evidence | SHA-256 |
| --- | --- |
| Gate execution ledger, including original failures and corrected reruns | `7c530d64af72fa03776b1c3545f4d591dff0d07d1179c0cf9f91a32906d534df` |
| Reader interaction receipt | `b03dbb6e8dd0bdd3f1a5a41757d4d9ef449176d29ac710855e36dcac622371be` |
| Release chapter-example receipt | `43f5b461dd055339f024232e81fbd98f9289c95869159a6ee69a32bd8488e8cf` |
| Material browser receipt | `aba240defb1f23ff4898585d7d7b27ac9b5f13aee5d935b92d0c95b4577a8322` |
| Artifact receipt | `00bd43592815be1c11d621f507a41dea85100423d5d8d0bca7756dfa3b4462f9` |
| Portable ZIP | `2ac21a00e12e94a9641283db0c8c9df1594301b6f0dc10d0a3ee650005de0f68` |
| Portable-package receipt | `7e977e3f170140ef51c9d6b01af10f121aca2575396e96d30256a7f9aeb13941` |

The gate ledger and command logs are under the isolated checkout's `.artifacts/teaching-qualification/browser-gates/`; current browser receipts are under `dist/`. The ZIP and its complete file-hash receipt are `.artifacts/downloads/kenoma-portable.zip` and `kenoma-portable.json`. Generated artifacts remain ignored. These are local software/book qualification results, not a hosted deployment or closure of the [scientific gaps](research-book-teaching-acceptance.md#remaining-scientific-qualification-gaps).

## Release-browser regression fixes

The full release run exposed an old book assertion in `chapter_examples_browser.py` that the preview intentionally does not execute. It expected an inline `.chapter-example-frame` and a chapter-button toggle. The reader now has one `.reading-example-frame`, explicit chapter selection and a responsive close control. Commit `3bd8461` updates those assertions, additionally waits for the exact child chapter and parent acknowledgment, and checks that closing removes the frame and hides the dock. All proof-card, anchor, nested-poser clipping, print and no-JavaScript assertions remain. The original failed log is retained; this test file is not one of the 979 build inputs, so the bounded rerun uses the unchanged built artifact and records the new test-source hash.

The material test also exposed Chromium's oversized-element capture path. At the release reader's narrower column, its existing responsive SVG stacks into a stable **614 × 1090.171875 px** scene, taller than the 1000 px test viewport; ten consecutive animation-frame samples had identical bounds. The preserved publication's **844 × 401.078125 px** scene captured normally. Both exported numerical states were identical, with no page errors. The direct screenshot timeout and both viewport captures are retained in `browser-gates/material-capture-probe/`; this is a capture diagnosis, not a changed solve or evidence of moving geometry. Commit `a367e3a` uses the existing bounded section-capture helper and binds its source hash. Its diagnostic capture passed in 0.292 seconds with the full scene, unchanged width, height and numerical state, and the original viewport restored. No numerical assertion, timeout or launch setting was relaxed.

## Teaching-source follow-up

The preview command in [the education README](../README.md#research-book-teaching-feature) now works from a shallow checkout with no pre-existing build directory. It reconstructs only the two pinned existing repository snapshots, verifies the publication's 1,102 files and 947 source inputs, and packages the current reader. A first clean-checkout test installed locked dependencies, fetched both missing commits, served the preview and inspected the actual force canvas/readouts without browser errors. An offline rebuild produced the same manifest. Missing offline objects, an existing output directory and changed canonical source were rejected. This is preview reproducibility, not a full release PASS.

The four requested screenshot comparisons are [committed documentation](../../docs/review/research-book-teaching/README.md), with source identities and exact image hashes. The additional [native anatomical portfolio capture](../../docs/review/research-book-teaching/portfolio-anatomy/README.md) records the existing held right-arm reference state and component attributions; no new motion step was run. Automated capture collections remain ignored and the generated-output guard is unchanged.

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

## Historical hosted status before the fresh run

At `f998586862b0c56e602ab6bdb6d2869693f84744`, GitHub returned **zero branch runs and zero commit check-runs**. The education workflow triggers pushes only on `main` and `education/**`; `feature/research-book-teaching` therefore requires a ready PR or an explicit `workflow_dispatch` with `publish=false` for full hosted qualification. No dispatch, merge or deployment was requested by this audit.

The latest successful full main book run, [37971771277 at `113446886a0e3191924573d37d23b7d91f5b05bb`](https://github.com/MrScripty/Kenoma/actions/runs/37971771277), predates the Rust/browser source and cannot qualify it. [PR15 run 38165657020](https://github.com/MrScripty/Kenoma/actions/runs/38165657020) passed draft contracts and the architecture contribution, with the full build skipped. [Main publication run 38006678689](https://github.com/MrScripty/Kenoma/actions/runs/38006678689) assembled already-preserved bytes; it was not a new build qualification.

The retained earlier gate covers the unchanged independent poser only. It is superseded for current Rust-source testing by run 309's successful individual gate; its preserved-binary identity remains separately relevant to the local build. The new reader, HTML/PDF and browser interactions have their own source-bound evidence above and in the final browser inventory.
