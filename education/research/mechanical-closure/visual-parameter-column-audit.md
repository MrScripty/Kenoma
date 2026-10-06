# Original Table 2/3 visual column audit: blocked

**Original table pixels were not obtained or inspected. The explicit visual-verification prerequisite for the next coupled release experiment remains unmet.** Extracted-PDF equation/value verification survives; it is not upgraded to visually aligned table-cell verification. No authored table or reconstructed PDF substitutes for the publication.

The [blocker receipt](../../data/anatomical-arm-v1/review/source-visual/visual-parameter-column-receipt.json) preserves the native screenshot result and ordinary-route outcomes. Its SHA-256 is `feaf466d8407f0daf079f184c2eb20589f36f8d932593f2680eb31444944b2c3`. No local original manuscript PDF or original Table 2/3 image was downloaded, so there is no pixel-file path/hash to report.

## Ordinary source routes inspected

The [original PLOS article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748) loaded through the installed Search Service connector. Its ordinary Download PDF link produced the original 37-page [publisher PDF](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable) and 1320 extracted lines. Thus text access is successful; the remaining blocker concerns original rendering, rather than absence of all source evidence.

| Route | Actual result |
|---|---|
| Publisher Table 2/3 HTML figure pages | Tool accessibility errors; no original image |
| Publisher Table 2/3 PNG larger-image links | Text-only internal errors |
| Native Search Service screenshots, PDF pages 20/21 (zero based) | A `CallToolResult` containing one text block and **zero image blocks**; text contains references and literal `<<ImageDisplayed>>` placeholders |
| Native opening of those screenshot references | Original PDF extracted text, rather than screenshot pixels |
| Publisher Table 2/3 original TIFF links | Text-only internal errors |
| Ordinary [PMC article page](https://pmc.ncbi.nlm.nih.gov/articles/PMC13561430/) | Browser reCAPTCHA challenge; stopped without interacting with it |
| Actual author institutional repository Download PDF | Web timeout; ordinary shell request returned a tunnel 403 and was stopped |
| Complete authorized public author-repository tree | No original manuscript or Table 2/3 rendering present |

The native screenshot attempt returned only the keys `content` and `isError`, with `contentTypes=["text"]` and `imageContentBlockCount=0`. Its raw response is retained in the receipt. The references `turn625598view0` and `turn625598view1` identify screenshot requests; they do not establish visual inspection. Reopening them produced PDF text references `turn719652view0` and `turn719652view1`. The successful original PDF text reference is `turn346365view1`.

The author webpage's real publication link resolved to the [LIRIAS record](https://lirias.kuleuven.be/4442410). Its ordinary Download PDF link targets [the repository's deposited document](https://lirias.kuleuven.be/retrieve/3ee63ba9-239a-4ace-853b-9a6d825d224b). The connector's download attempt timed out; a standard unauthenticated shell request returned `Tunnel connection failed: 403 Forbidden`. No further shell retry, proxy change, header trick, credential, challenge response or signed-URL alteration followed that denial.

The initial authorized [recursive GitHub query using the main ref](https://api.github.com/repos/timvanderzee/biophysical-muscle-model/git/trees/main?recursive=1) returned identity `8c766dfb308051309193e7290ddd0bac3b726d11`; that SHA is the pinned **commit**, not the independently verified tree. A subsequent ordinary commit GET confirmed `commit.tree.sha=a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`. An independent [recursive read of that actual tree](https://api.github.com/repos/timvanderzee/biophysical-muscle-model/git/trees/a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20?recursive=1) returned the tree SHA `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`, with `truncated=false`, and the same rendered-file inventory. The only rendered documents/images were `Fig1.png`, `Data/data_processing_overview.png`, `Test/test_model.png` and supplemental `Reproduce/Model output/SRS/Approximated/FigS5.pdf`. None is the original Table 2/3 or manuscript. They were not repurposed as column-verification evidence. Image search supplied no usable original table image.

## What remains supported

The [source rendering evidence](source-rendering-evidence.md) and [independent numerical audit](two-state-independent-audit.md) retain successful original PDF extraction, rate/unit consistency, the inferred populated-row/header association, and the verified direct-CE numerical fixture. This new audit found no contradiction in those facts. It also found no actual pixel evidence that resolves the stricter column-alignment requirement. Source code reads and dimensional checks can strengthen the transcription record, but cannot satisfy an explicitly visual requirement by themselves.

The next ordinary path is an accessible original publisher/deposited PDF or original table image supplied through an authorized file route, followed by inspection of its pixels and preservation of its identity/hash. Until then, keep the coupled release experiment behind the stated visual prerequisite. No simulation, coefficient selection, old-file edit, production/book/Lean change or Git operation occurred in this audit.
