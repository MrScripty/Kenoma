# Source-first educational reading pipeline

The new reader builds from fixed Git objects and committed sources, without previous generated-output snapshots. Existing scientific workflows are unchanged.

## Fixed inputs and setup

`book/source-first-reading.json` records exact commits and trees for the historical published edition (`596df78…`), the 115-declaration registered baseline (`6a72e01…`) and the sanitized research (`f9dbda9…`). The historical expanded Markdown and 208-page PDF are recovered from their exact Git objects and checked against the historical portable manifest. The current candidate binds each selected source by commit, blob, SHA-256 and size.

The scoped renderer uses Node 24.19.0, Python 3.12.14, pinned packages in `reading-requirements.lock`, Chromium 151.0.7922.173, and the declared Liberation/DejaVu fonts. Each run seals actual executable and font hashes. Pandoc 3.1.11.1 is supported locally; the manual Ubuntu 24.04 workflow uses the official [Pandoc 3.1.3+ds-2 package](https://packages.ubuntu.com/noble/pandoc). These are recorded rendering environments, not a promise of byte-identical PDFs across environments. Every output must pass fresh qualification.

The workflow installs rendering/audit dependencies and the fixed historical static bundler dependencies with `npm ci --ignore-scripts` in an isolated directory. It does not run the project npm build, Lean, contribution builders or anatomical experiments. Existing dependency source locks remain unchanged, including two explicitly reported editorial differences in the full-face lock.

## Build from a clean checkout

Fetch the advertised prerequisite refs listed below, verify their exact commit/tree identities against `book/source-first-reading.json`, checkout the candidate, and install the declared setup. The builder uses the fixed Git objects even if an advertised ref later moves.

| Prerequisite | Advertised ref | Fixed commit |
|:--|:--|:--|
| Historical edition | `main` | `596df78f5cb652b4ac70917a82d8aa908b617056` |
| Registered baseline | `review/architecture-force-book-20261008` | `6a72e01b66e4d5724c8d6c74f98cf38a90b21e31` |
| Research sources | `handoff/kenoma-source-through-ba11-20261008` | `f9dbda932264cb0ce1023b0204efe6e4057ed983` | Outputs and caches belong outside Git. The Playwright-managed Chromium is the default; an already installed supported binary can be selected explicitly with `KENOMA_READING_CHROMIUM`. No sandbox bypass is requested.

```sh
export PYTHONDONTWRITEBYTECODE=1
export XDG_CACHE_HOME=/tmp/kenoma-reading-cache
python3 education/tools/source_first_reading.py seal /tmp/reading-inputs.json
python3 education/tools/source_first_reading.py build /tmp/reading-inputs.json /tmp/reading-output
python3 education/tools/preserve_legacy_pages.py inventory /tmp/legacy-inventory.json
```

The builder recovers the full historical book, composes six additions and exactly five permitted synthetic controls, runs fifteen model tests plus the independent bounded symbolic/high-precision audits, cleans method prose, regenerates runtime byte inventories, embeds declared fonts, renders PDFs and qualifies the reader. Public output is `reader/`; raw evidence stays in local `private/` and `build-evidence/`. Only the sanitized `ci-diagnostics/` subset is uploaded by the manual workflow. Actions artifact visibility follows repository access and is not described as private.

Qualification checks actual controls, rollback/reset/export, failed/recovered residuals, damaged runtime refusal, desktop/mobile layouts, no-JavaScript defaults, local links, complete new Lean source in PDF, print readability, historical numeric preservation and public privacy. No historical checked label becomes fresh proof evidence. Network reachability is separately marked UNRUN.

The expanded reader's frozen formal labels are 30 Std reported passed, 85 Real UNRUN, and nine additional statements UNRUN. No proof receipts are imported into that reader. Its anatomy HELD/UNRUN label describes the pinned inputs and release execution, not the latest research result. Later results enter a public status note only after their actual evidence has been transferred and bound to fixed identities. Biological calibration remains unestablished.

## Preserve the complete Pages root

Pages replaces an entire artifact. The functional contract in `book/functional-pages.json` preserves known reader/inspector URLs, runtime dependencies, reference data and cited genuine receipts. The strict `preserve_legacy_pages.py` route remains available for historical exact-byte recovery, but is no longer the publication route.

The old 1,231-file portable manifest describes qualification revision `142806…`; it is not verified deployed `596df78` bytes. Source inspection recovered 971 originals and identified 32 presentation paths plus 228 missing historical review artifacts. None of the 228 has a direct reader/runtime link in inspected sources; 183 appear in public JSON bookkeeping. They are listed as unavailable, never regenerated as historical evidence. Current live-root completeness remains unverified.

`functional_pages.py` exports exact `596df78` sources, archives all 971 original records privately, and reconstructs the 32 core paths using pure SVG/XML formatters, stored-result plotting, inspector templates, Pandoc and six esbuild bundles. Generated presentation has new source/setup/output bindings. Ordinary new raster images use JPEG85; the existing scientific plot PNG and bundle license TXT URLs remain compatible assets. Scientific source/data/receipts retain exact bytes. Historical operational records containing environment paths or stale packaging assertions receive explicit public availability records pointing to immutable originals; the originals are never changed or discarded.

The historical successful Actions deployment and old qualification manifest have distinct identities. A source-based known-URL reconstruction is not evidence of having read the live site.

With the pinned static dependencies installed outside Git:

```sh
python3 education/tools/functional_pages.py seal /tmp/functional-inputs.json \
  --node-modules /tmp/static-dependencies/node_modules
python3 education/tools/functional_pages.py build /tmp/functional-inputs.json \
  /tmp/reading-output/reader /tmp/functional-output \
  --node-modules /tmp/static-dependencies/node_modules
```

Public output is `functional-output/pages/`; original records and raw construction/qualification evidence remain outside the public root in `private/`. A final public manifest binds the exact file set and hashes. Closure includes entry/reader HTML, fragments, styles, static images, six bundle graphs, explicit array/template fetches and worker/download dependencies. Missing required resources fail qualification.

Long display equations receive token-preserving print alternatives from the fixed canonical formatter. These alternatives are saved in the public HTML while the original screen MathML remains intact. Print qualification reloads that actual file with JavaScript disabled, checks every cloned token and verifies the A4 output has no clipped text. Input verification rederives the historical inventory from fixed Git evidence and refuses altered classifications, source sets or dependency bytes.

Production startup gating precedes imports. Elementary force/lever/spring/hinge controls, prescribed geometry, default closed-form SLS and read-only atlas views are permitted. Material/series/serial/spatial/continuum models require an explicit archived-laboratory selection; arm/coupled inspectors require an explicit load. Qualification does not visit those opt-in routes or start their workers. Their runtime qualification remains UNRUN, while their canonical code and required URLs remain available. Static bundling does not establish numerical acceptance.

## Manual workflow

`reading-edition.yml` runs only on manual dispatch. Its default builds and qualifies the reader and complete functional root without deployment. It uploads public outputs and sanitized diagnostics, never the raw private archive. Assembly and qualification must succeed before any optional Pages upload/deployment. Original scientific workflows are unchanged.

Every candidate requires clean-checkout qualification and source review. Hosted workflow execution, merging and deployment are separate gates; creating or pushing a source branch does not execute them.
