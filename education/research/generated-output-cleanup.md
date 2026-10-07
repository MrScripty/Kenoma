# Generated output cleanup

This cleanup starts at `596df78f5cb652b4ac70917a82d8aa908b617056`. It removes redundant generated downloads and capture collections from the current tracked tree, without rewriting Git history. The old blobs remain available at that immutable commit. A normal full clone will therefore still contain historical storage; checkout and source-distribution size are the gains claimed here.

## Retained inputs

The complete `data/elbow-v1/` reference package remains byte-for-byte unchanged: 50 files, 9,170,224 bytes. This includes original BodyParts3D meshes, Arm26 data, OpenArm normalized samples and source documentation, provenance, licenses, reacquisition receipts/scripts, and the existing illustrations. The reference package is excluded from generated-output cleanup and lossless originals are preserved.

All `data/anatomical-arm-v1/audit/` execution evidence and frozen source snapshots remain tracked. They occupy 201,791,331 bytes and current source-bound replay/tests still need them. Removing these archives would require a durable, verified fixture store and corresponding offline/clean-checkout acquisition support. Neither a new solve nor deleting the sole retained execution data is part of this cleanup. Unique historical JSON evidence is retained; removed duplicated traces still have an identical tracked copy. Authored Markdown, proof sources/maps, licenses, source snapshots and numerical law implementations remain.

## Outputs and regeneration

- Canonical book prose is `book/chapters/`, ordered by `book/book.json`; proof maps and complete sources remain in `proofs/`. The build still freshly compiles the pinned proofs. Actual-point PDF text/source/diagram gates remain mandatory for qualified builds.
- PDFs are generated in ignored `dist/`, downloadable as the separate `kenoma-print-downloads` workflow artifact. They are no longer committed. `npm run pdf` uses the existing renderer; proof/build/artifact checks still precede release qualification. The website and portable package retain their working PDF links.
- Portable ZIPs default to ignored `.artifacts/downloads/`. Runtime negative controls and browser captures go to ignored `.artifacts/` or `dist/`. The tracked-output guard rejects PDF/ZIP/compiled Lean objects, review screenshots and additional large generated collections.
- Packaging tests create a small temporary contract fixture instead of extracting a 58 MB historical release. It cannot pass the production current-book/proof/readability qualification. All damage controls remain; actual-point PDF unit tests also create their own real temporary PDFs.
- The projection limits regression creates an actual 11-point heading-only PDF and verifies rejection for missing full limits text; it does not depend on a committed PDF.
- Ordinary reader illustrations are emitted at JPEG quality 85. Protected reference originals, SVG diagrams and diagnostic captures retain their role and encoding. Diagnostic captures are build artifacts, not committed ordinary illustrations.
- Site data copying now uses `tools/anatomy-publication-files.json`: 63 files, 87,340,326 bytes instead of the entire 211,032,533-byte anatomy tree. Its closure includes reader links and currently required artifact-test inputs. This reduces publication copies by 123,692,207 bytes; it does not delete research source archives. Invalid or missing inputs fail before replacing a generated destination.

An optional historical editorial preview now accepts `--archive PATH`, defaulting to `.artifacts/inputs/kenoma-release-output-bound-portable.zip`. With the immutable object already available locally, recover that optional input using:

```bash
mkdir -p .artifacts/inputs
git show 596df78f5cb652b4ac70917a82d8aa908b617056:education/deliverables/release-output-bound/kenoma-release-output-bound-portable.zip > .artifacts/inputs/kenoma-release-output-bound-portable.zip
```

The retained delivery manifest still verifies its SHA-256. This is optional historical preview evidence, not an input to current unit tests or a newly qualified release. A shallow checkout without that old object needs explicit acquisition before invoking the optional historical tool.

## Qualification scope

Draft PRs run source and unit contracts without launching full research executions. Ready PRs and explicit builds retain the complete existing book, proof, browser, PDF and artifact qualification job; draft tests cannot establish those results. Publication still requires the existing explicit checked-main workflow input. No deployment, environment protection, credential, anatomical-completion claim or physical law is changed.

Local verification passed 208 JavaScript tests and 62 Python tests, including runtime packaging damage controls, actual-point PDF tests, output traversal/missing-input rejection and JPEG quantization checks. Source acquisition unit tests now mock disk space with their HTTP fixtures and independently test that the unchanged production 1.5 GiB floor rejects before network access. Full fresh Lean/book/PDF/research qualification remains necessary before a release; no blocked nonlinear author solve has been rerun.
