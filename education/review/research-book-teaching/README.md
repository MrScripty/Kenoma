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
| Desktop, 1440 × 1000 | `before-kenoma-desktop-force.png` | `after-desktop-force-default.png` |
| Phone, 390 × 844 | `before-kenoma-phone-force.png` | `after-phone-force-default.png` |

Captures reside beside this README in the local checkout. `education/.artifacts/research-book-teaching/matched-screenshots.json` records their hashes and numerical readouts. The final browser gate also captures energy and pressure-projection steps at three widths. `evidence-review-v8/` contains six anatomy/coupled screenshots and its byte-bound receipt, covering historical rejection labels, provenance selection, poser edits and restoration of a fully visible scene after changing chapters.

## Regenerate

Use the normal qualified build when the pinned Lean/Rust prerequisites are available. For this bounded review, supply the already verified preserved publication directory:

```bash
cd education
npm ci
python3 tools/build_teaching_preview.py --preserved /path/to/verified-preserved-book /tmp/kenoma-teaching
python3 tests/research_book_browser.py /tmp/kenoma-teaching
python3 tests/chapter_examples_browser.py --preview /tmp/kenoma-teaching
python3 -m http.server 8000 --directory /tmp/kenoma-teaching
```

The preview verifies unchanged evidence/source bytes and explicitly labels its reused receipts and prior PDF. It runs no new scientific campaign, downloads no dataset and publishes nothing. The full-build CI sequence now includes the new research-book browser gate; it has not been run remotely for this feature.

## Scope left open

Fresh Lean/Rust compilation, a newly generated complete book/PDF and exact-head remote release qualification remain open. The preview does not close anatomical stationarity/calibration, compression/contact, continuum refinement, subject registration or implementation-proof gaps. Failed nonlinear iterates and historical rejections remain visible. Screenshot PR15 and its head `9739080116b658e6248816f4e4239c4fde95ca94` were inspected read-only and remain unchanged. No main merge or Pages deployment was performed.
