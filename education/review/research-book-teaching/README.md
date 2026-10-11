# Research-book teaching review

This feature provides 95 worked checkpoints across 27 chapters, a shared desktop reading/laboratory layout, and collapsible phone chapter/example panels. The [acceptance inventory](../../research/research-book-teaching-acceptance.md) records each chapter's teaching repair and remaining scientific limits.

## Baseline and reference

The before screenshots render the checksum-verified preserved publication locally. The exact publication payload is `2fd337166c4d2ef624e6536769e03b9d83587332`; its preserved build-manifest SHA-256 is `415d3d15c6f9644660bd2dd3983367bb30548188080ab0fbf7de45c4b7ed6d02`. The assembler verified 1,102 preserved files and 947 source inputs. These are not claimed to be new screenshots captured from the live host: direct browser requests to the Kenoma/Rheon Pages hosts were blocked by the environment proxy.

Actual Rheon projection source was inspected through GitHub: `docs/education/style.css` blob `fbefeab297b357d1b6ee1991ba144af9f24eb666` and `labs.js` blob `79f98f8891226e24556c9ddfd5587740f70bcdd4`. Its paper/ink/teal colors, Georgia headings, compact controls and explicit illustration limits informed the reader. Baseline observations and capture metadata are retained locally in `education/.artifacts/research-book-teaching/before-browser.json`; generated screenshots and receipts are intentionally untracked.

## Validation

- `npm test`: 290 tests passed. Scientific kernels and all bounded chapter adapter endpoints were exercised.
- `npm run test:python`: 130 tests passed, including four new teaching-assembly checks. Proof-checker unit fixtures are synthetic tests; they are not fresh Lean evidence.
- The final force/energy glyph refinement passed 37 targeted foundation/adapter tests; the coupled rigid-carrier refinement passed 34 evidence/adapter tests.
- `git diff --exit-code` against starting main confirms no changes to canonical chapters, proof files, scientific datasets, Rust crates, the independent poser or licenses.
- `tools/check_generated_outputs.py` passes; screenshot collections and built artifacts remain untracked.

The new browser gate exercises every authored desktop checkpoint and representative first/last phone/narrow checkpoints, then checks manual state/focus retention, reset to the selected step, explicit scroll-follow resumption, rapid scroll interruption, keyboard/wheel orbit, hostile/unrelated sender rejection, compact claim disclosure, print/no-JavaScript text and WebGL context-loss fallback. It also replays a real queued scroll message after a manual edit: this reproduced a lost edit before the fix. Manual input now holds the child locally; only an explicit new follow generation can release it, and the dock labels only accepted selections. The existing GUI gate independently exercises all 27 topics and real controls at desktop, 390 px and 320 px, including embedded posing and disposal. Exact results and byte bindings are stored in the local receipts described below.

Final Chromium 151.0.7922.173 results against `/tmp/kenoma-teaching-v8`:

- Research-book gate: **PASS**, 95 desktop checkpoints at 1440 × 1000, eight phone checkpoints at 390 × 844 and eight narrow checkpoints at 320 × 844. All interaction assertions passed with zero page errors. Local `receipt.json` SHA-256: `a62553e6fd2ad3327d94cc11aa419d876a097c1289a689f0f1b3c8d7ad4f9ec3`; test source SHA-256: `738de45926819de45d545e0284603f4c84229ee6dcf36c5b9fde91ac4ce54466`.
- Standalone GUI gate: **PASS**, 27 chapters × three widths = 81 chapter/view checks. `/tmp/kenoma-teaching-v8/chapter-example-qa/receipt.json` SHA-256: `0a4fe6ec17cd54d3f279d33640a3f3a084c5a3d587a262fa1eb74ae531dd85dd`.
- Evidence/poser review: **PASS**, 20 grouped desktop/phone checks, including actual keyboard IK, 12,288-byte SQLite Save/Open, source selection and child scroll reset. Receipt: `evidence-review-v8/receipt.json`.
- The immediate manual-edit stress loop passed 15/15 transitions after the fix. The deterministic queued-message replay failed before the fix and passed afterward; replaying an old pause cannot cancel a new explicit resume.

## Screenshot comparisons

These local captures compare the same force inputs: 4 N, 2 kg and 1 s. The old viewer exposes displacement at a fixed one-second time; the new viewer makes elapsed time explicit. Camera placement and marker size are presentation choices, with their scales declared in the new laboratory.

| View | Preserved publication | Teaching reader |
|:--|:--|:--|
| Desktop, 1440 × 1000 | [Before](../../../docs/review/research-book-teaching/before-kenoma-desktop-force.png) | [After](../../../docs/review/research-book-teaching/after-desktop-force-default.png) |
| Phone, 390 × 844 | [Before](../../../docs/review/research-book-teaching/before-kenoma-phone-force.png) | [After](../../../docs/review/research-book-teaching/after-phone-force-default.png) |

The four requested comparison images and their [capture provenance](../../../docs/review/research-book-teaching/captures.json) are committed under `docs/review/research-book-teaching/`. Automated capture collections remain ignored. The browser gate also captures energy and pressure-projection steps at three widths. Local `evidence-review-v8/` contains six anatomy/coupled screenshots and its byte-bound receipt, covering historical rejection labels, provenance selection, poser edits and restoration of a fully visible scene after changing chapters.

The separately requested [anatomical portfolio capture](../../../docs/review/research-book-teaching/portfolio-anatomy/README.md) records the existing right-arm viewer at its stored, held resting state, with three atlas bones, seven derived muscle volumes and authored tendon routes. Its native camera orbit leaves time, activation and recorded steps unchanged; no new motion solve is claimed. Exact served hashes, component attribution and the link to PR15's unchanged two-character poser image accompany the PNG.

## Regenerate

Use the normal qualified build when the pinned Lean/Rust prerequisites are available. This bounded preview starts from a fresh checkout with Node 22+, Python 3.12 and Git; no preexisting `/tmp` artifacts are required:

```bash
cd education
npm ci --cache .artifacts/npm-cache --no-audit --no-fund
python3 tools/build_teaching_preview.py .artifacts/research-book-preview
python3 -m http.server 8000 --bind 127.0.0.1 --directory .artifacts/research-book-preview
```

Open <http://127.0.0.1:8000/>. The builder reads the checked-in publication descriptor, fetches missing immutable Git commits only from the official Kenoma repository into ignored `.artifacts/teaching-preview-inputs`, and exports the exact canonical baseline before running the publication assembler. The current modified worktree is never used as the baseline. Every preserved file and source input is checked before current teaching assets are packaged. Temporary snapshots are removed; Git objects remain available for `--offline` reuse. Use a new output path for another build, `--cache PATH` for external staging, or `--preserved PATH` for an already verified local artifact.

With the browser-test prerequisites installed, run `python3 tests/research_book_browser.py .artifacts/research-book-preview` and `python3 tests/chapter_examples_browser.py --preview .artifacts/research-book-preview`. The preview manifest records publication commits and verification hashes. It explicitly labels reused proof receipts, recorded solver results, poser WASM and the prior PDF; it runs no new scientific campaign, downloads no new medical dataset and publishes nothing. The full-build CI sequence includes the research-book browser gate; it has not been run remotely for this feature.

The reconstruction command was exercised from a shallow checkout containing neither pinned historical commit, with freshly installed locked dependencies and the pending preview tooling applied. Both immutable commits were fetched successfully; the assembler verified 1,102 preserved files and 947 source inputs. An offline rebuild produced an identical preview manifest. Local HTTP serving and the force example's actual WebGL/numerical state passed. Missing offline objects, an existing output directory and changed canonical prose were rejected. The local record is `education/.artifacts/research-book-teaching/preview-reproduction.json`; these are packaging and browser smoke checks, not new scientific qualification.

## Scope left open

Fresh Lean/Rust compilation, a newly generated complete book/PDF and exact-head remote release qualification remain open. The preview does not close anatomical stationarity/calibration, compression/contact, continuum refinement, subject registration or implementation-proof gaps. Failed nonlinear iterates and historical rejections remain visible. Screenshot PR15 and its head `9739080116b658e6248816f4e4239c4fde95ca94` were inspected read-only and remain unchanged. No main merge or Pages deployment was performed.
