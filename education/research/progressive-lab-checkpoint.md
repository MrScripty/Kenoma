# Progressive labs: bounded author checkpoint

This author lane has produced three independently reviewable lessons: measured affine tetrahedral deformation, positive isochoric rectangular-block kinematics, and a nonuniform small-strain axial bar. The bar includes the requested equal-length two-area active fixed-end example. These additive modules preserve all anatomical body/contact operators and the running trajectories. The source chapter is not yet listed in the main book manifest.

Reproduce the current compact deliverable from `education/`:

```sh
node --test tests/continuum_properties.test.mjs tests/tapered_bar.test.mjs
python3 tools/build_property_preview.py
python3 tests/property_browser.py
```

The preview has SI readouts, explicit assumptions, an independent oriented boundary-triangle volume, area-times-length comparison, inversion/invalid-input rollback, actual refinement controls, reset, copy-state and deliberate result summaries. The small-strain bar is an axial oracle, not a calibrated active muscle. Static figures remain available with JavaScript disabled and in print. The preview explicitly labels the four proposed real claims as **pending**, with no checked proof cards. The existing 25 Std-only book claims are unchanged.

The native curriculum plan `libfile_7ea79b1aa3cc8191b436abdb7b066c46` was prepared twice using the supported Library resolved-reference materialization route. Both current-helper downloads returned `library file transfer failed: download failed`. Its bytes are not present and its supplied SHA-256 has not been verified. No alternative URL, permission bypass or upload was attempted. This does not block the explicit parent specification or the independently verified source map in `measured-fibre-property-map.md`.

## Exact next bounded milestone

Finish and fresh-check the **four real kinematic declarations**, then integrate these three lessons into the main Markdown/HTML/PDF book. The pinned official mathlib source build is already running; do not start a duplicate build. Its current process and progress are recorded in `data/property-labs-v1/review/first-milestone-checkpoint.json`.

`proofs/mathlib-lock.json` pins mathlib `v4.19.0`, commit `c44e0c8ee63ca166450922a373c7409c5d26b00b`, and its dependency manifest. The public binary cache returned HTTP 403. A two-job source build of the 1,500 transitive imports is progressing. `/tmp/kenoma-mathlib-source-build.txt` and `/tmp/kenoma-mathlib-source-logs/` retain the live build transcript and individual module logs. `tools/build_property_mathlib.py` is the reproducible source-build route for a fresh workspace, not a request to duplicate the live worker.

When the current build finishes, run `python3 tools/check_property_proofs.py`. Fix any actual theorem errors without admissions or proxy domains. Only a successful fresh invocation may produce checked claims. Then add the fifth bundle to `tools/build.py`, route `{{property:key}}` through `tools/property_labs.py`, generate the static figures through `tools/property-experiment.mjs`, include `09a-properties.md` in `book/book.json`, and add the property source/receipt/transcript to source appendices, downloads, PDF internal links and notices. Proof-card metadata must distinguish pinned mathlib from the unchanged Std-only bundles. Update count-dependent browser/artifact checks from all five receipts (29 claims if these four compile), and coordinate the `00-scope.md` count before editing it. Rebuild and inspect the whole book; this compact preview does not claim that integration is already complete.

The following bounded lesson is finite-bulk/shear and free/confined compression. Extend the earlier homogeneous block with separate moduli, energy/stress finite differences and an independent energy-minimization route for free lateral equilibrium. Preserve the difference between its `K/2*(J−1)^2` and the anatomical `K/2*(ln J)^2`. The unrun homogeneous anatomical benchmark is diagnostic only. Then use the measured-property source map to build the fibre-to-muscle aggregation lesson and the separate force–length/velocity and storage/dissipation lessons. Do not postpone simple property delivery for another anatomical solve.

## Preserved anatomical processes

The all-half trajectory, interpolated-initial-guess all-half trajectory, and release-third refinement remain active. Their original iteration limits, force/geometry gates and reject-without-advancement behavior are unchanged. Their optimizer-free replay monitor is also running, with a separate trigger waiting to build matched-time comparisons and figures after terminal receipts. No dense convergence or whole-envelope qualification is claimed. The pending workflow/artifact/final-inspection edits remain uncommitted until those receipts are terminal.


## Main-book integration completed on 2026-10-05

The historical pending status above describes the frozen first preview. Main-book source commit `3cd3c5fbf2b061058e1dc5d2305408951dd4b5ee` now contains the three lessons and all four freshly checked real claims. The complete edition has 21 chapters, 29 checked claims and 89 PDF pages. The corrected numerical suite passes all 128 tests, Python checks pass all 16 tests, and full-book/property desktop/mobile, print, source-hash, glyph and PDF-link checks pass. The endpoint-warning bug and its frozen failing case are recorded separately. The Library errors remain generic unclassified download failures, with no verified plan hash.

`deliverables/property-integration/` contains the coherent source-bound Markdown, PDF, full portable archive and delivery manifest. `data/property-labs-v1/review/main-integration/` retains raw tests and render evidence. The next bounded curriculum milestone is separate finite-bulk/shear and free/confined compression; the measured-property and subsequent rate/history lessons remain planned. The three old anatomical refinements remain active under their original gates. Parent retains review, merge, publication and Library delivery.
