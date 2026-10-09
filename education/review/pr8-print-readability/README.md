# PR8 print readability repair

Qualified source: `0b4dc6a2cfa4fd4ff2b3decd08718c35ad5510e2`, tree `9ab47d3db430e31e50943f747b9630caef57ced0`, branch `education/pr8-print-readability`. Base: frozen PR8 `e8fa239e3c01468cee86615e1f306dd6659999fa`. This directory is an evidence successor; it does not alter the frozen PR8, SLS or serial-specimen branches.

The fresh local PDF is [build/kenoma-mechanics.pdf](https://raw.githubusercontent.com/MrScripty/Kenoma/596df78f5cb652b4ac70917a82d8aa908b617056/education/review/pr8-print-readability/build/kenoma-mechanics.pdf), SHA-256 `2475b4dccf078c3bd6aa825c0748d7cd515c1c726cb283845cbe59944f6cffa2`, 153 pages. Actual PDF measurements pass for all 53 theorem statements and card fields, nine complete Lean sources, 22 chapter prose samples and 119 diagnostic figure labels. Instructional prose/code minimum: **10.5 pt**. The three diagnostic figure minima are **11.829055, 10.845686 and 10.853540 pt**. Mathematical superscripts and identified footer glyphs are separately recorded; code receives no size exemption. All portable baseline link target sets remain present. More pages are intentional.

## Reproduced cause and scope

The frozen author PDF has 79 pages and measured prose/theorem sizes of approximately 6.995/4.555 pt. Its A4 print layout has 658 px available width, but the Lab5 multi-equation row occupies approximately 940.42 px. The resulting approximately 0.6995 scale explains the reproduced local global reduction. Additional long coupled/apparatus potentials overflow. Nested `pre` 7.4 pt and `code` 0.88 em styles compound the proof reduction.

The repair sets explicit print sizes, wraps code, reflows only overflowing display MathML at top-level boundaries, and reserves readable figure/legend/caption space. All 113 original display MathML elements and their TeX annotations remain unchanged; the three overflowing equations clone every token in order and keep nested expressions indivisible. The PDF renderer activates print media and checks horizontal bounds before writing a PDF. Failed rendering removes stale PDF/receipt outputs. No plain `beforeprint` hook was added: a separate synthetic screen-media experiment showed that Chromium can fire this event before print styles activate. Complete native Ctrl+P output is not qualified by this work.

All book prose, proof sources/maps, physical modules, anatomical audit data, material calibration, physical equations, numerical acceptance limits and unfinished-capstone labels are unchanged. The nodal figure renderer now uses the existing exact archived-byte transition helper for the historical contact replay receipt already enumerated in `tools/release-source-transition.json`; it does not accept unbound input bytes. SVG IDs/date metadata are stable under the same installed renderer, and re-rendering unchanged inputs reproduced identical output bytes.

The parent separately inspected the previous hosted 94-page artifact from run `37432920837`, artifact `11401844876`, and supplied its 8.03/5.23 pt findings. This worker did not download or inspect that hosted PDF: connector file transfer exceeded 32 MiB, and the executor's authorized transient download returned HTTP 403. Consequently, this evidence does not attribute the entire hosted/local difference to one scale factor or assert all hosted input bytes match. The new source run [37449270673](https://github.com/MrScripty/Kenoma/actions/runs/37449270673) was still compiling pinned dependencies at the recorded snapshot; no hosted qualification is claimed.

## Qualification

- 179 Node tests and 52 Python tests pass, including 20 new actual-PDF/layout tests. The historical 29-card package fixture explicitly fails the new gate before its old corruption contract is isolated; no readability PASS is invented for that old PDF.
- All 53 declarations were freshly checked using pinned Lean/mathlib inputs. The fresh manifest binds 867 inputs and 181 executable outputs; 850 existing build input hashes are unchanged, 15 render/packaging inputs changed and two print tools were added.
- All 12 native browser, mobile, property/material, render, subpage, worker and artifact lanes pass with unchanged manifest bytes. This includes the existing actual Lab7 state-preserving/active-shape controls.
- The actual-point gate is mandatory in CI, artifact validation and packaging. It recomputes measurements and compares saved receipts, rather than trusting a claimed minimum.
- Three additional full-build negative controls pass: missing readability receipt and forged PDF binding are rejected by packaging; a source-preserving 9 pt code PDF with a rebound hash is rejected on actual theorem/source glyph sizes.
- Root inspected the actual new force plot, envelope plot, long theorem card and wrapped Lean code. An independent reviewer inspected all three repaired diagnostic figure layouts and confirmed preserved MathML tokens/quantities. This is not a claim that every page was visually inspected.

Raw bindings, logs, screenshots, proof receipts, negative-control runner/results and source continuity are included here. The first external negative runner caught the intended 9 pt failure but used the wrong error-message assertion; its failure log is retained, and the corrected unchanged-font control subsequently passes.

Portable archive: `/workspace/kenoma-pr8-print-readable-portable.zip`, **73,247,760 bytes**, **1,039 files**, SHA-256 `49530ef9179d9dbd3f0cb1ef3aa48cc2417674ed1e9ea1e8a72dc5f4aa484604`. Its receipt is [portable-bundle.json](portable-bundle.json). Packaging validates before and after ZIP creation, then verifies CRC, file inventory and every archived hash.

No PR was created, merged or deployed. [draft-pr.md](draft-pr.md) is prepared for parent coordination; hosted artifact qualification remains pending.
