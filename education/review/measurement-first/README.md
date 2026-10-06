# Measurement-first progression: successor review

Source checkpoint: `4e81139d6c6bf4695de7d82b0ba771e187d34e76`, directly after frozen hotfix `b941a43e5df06173365ddc4ff050d0542ab74fe2`. Branch: `education/measurement-first-progression`. PR7 and the anatomical research branch were not changed.

## Order and rationale

The canonical `book/book.json` now places the existing `09a-properties.md` chapter immediately after force, torque and energy. The rest of the chapter sequence is retained. Filename numbering is not the reading order.

Readers first measure prescribed deformation, then impose volume preservation, then calculate nonuniform strain using a reduced axial law. Only afterward do anatomy/actuation, tissue and contact, constitutive mechanics and spatial solvers enter the progression. This gives beginners length/area/volume/stretch/strain measurements before asking a material/contact solver to determine a shape.

The source adds a units/symbol table, questions and executable worked examples, and explicit scope for each property lab. Constant-volume geometry is imposed rather than obtained from material equilibrium. The bar solves axial balance and fixed-end compatibility with an input area profile; it does not solve transverse deformation or full muscle physiology. Later tissue/compression/continuum introductions link back to these distinctions. The opening roadmap, energy transition, coverage table and closing research path agree with the manifest.

Existing source citations and heading anchors are preserved. The unavailable energy/singular-value extension is explicitly distinguished from the implemented deformation controls. Bulk/shear/confinement, measured fibre aggregation, force–length/velocity and dissipative property lessons remain pending; anatomical/capstone limitations remain explicit.

## Completed checks and actual inspection

- Python suite: 18 passed (`python-tests.txt`). The new PDF-outline regression checks label correction, identical destinations including object references, pixel-identical rendered pages and an unchanged second pass.
- New worked examples were checked against the unchanged executable property modules: translation and unit/shear/stretch measurements; 0.8 axial stretch gives length 0.064 m, section 0.00375 m² and volume 0.00024 m³; doubling passive load doubles strain, doubling modulus halves it; the two-segment fixed-end case gives ±1/300 strain and zero net extension.
- All existing external/source citation links and archived heading anchors were checked for preservation.
- Real Chromium checked identical canonical Markdown/HTML/TOC order, unique fragment targets, all local assets/downloads, 29 proof cards, seven mechanics labs, three property labs, desktop/mobile overflow, static print alternatives and absence of JavaScript errors. See `render/receipt.json`.
- The actual 91-page PDF outline agrees with the chapter manifest. The property chapter starts on page 11, anatomy on page 17 and continuum material mechanics on page 34. All six property-chapter pages (11–16), the opening roadmap and the later continuum bridge were inspected. Equations, figures, units, scope notes and paragraph transitions are readable. Page captures are in `render/`.
- Chromium omitted spaces at two wrapped heading boundaries in its PDF outline even with normalized HTML. The production PDF renderer now repairs only whitespace-equivalent labels using actual HTML headings, without changing destinations or page appearance. This is a navigation repair, not a numerical model change.

No equations, material values, physical solvers, UI controller code or proof declarations changed in this successor. The code/prose commit was saved before the reported disconnect; actual shell access was confirmed and completed tests were not repeated afterward.

## Deliverables and qualification boundary

The [review PDF](../../deliverables/measurement-first-editorial-review/kenoma-mechanics.pdf) and [generated Markdown](../../deliverables/measurement-first-editorial-review/kenoma-mechanics.md) use the same revised canonical prose and order. The PDF is labeled **Editorial review preview · Not for publication** on every page. Markdown is a companion to the regenerated book assets; this small handoff is not a new portable website archive.

The review builder verifies the archived portable book's delivery hash and canonical chapter hashes, and checks that reused proof receipts still bind to current unchanged proof/claim sources. It regenerates current prose, HTML, controls and app bytes while preserving historical experiment/proof content. `editorial-preview-manifest.json` identifies the source base at rendering time; `delivery-receipt.json` binds every preview input to the later committed source checkpoint above. These are historical proof checks, not fresh Lean compilation or fresh release/solver qualification. The checkout did not contain the pinned Lean/mathlib workspace.

Reproduce in new output directories from `education/`:

```sh
python3 tools/build_editorial_preview.py /tmp/kenoma-editorial-book
python3 tests/editorial_progression.py /tmp/kenoma-editorial-book /tmp/kenoma-editorial-review
```

Fresh exact-head release CI and parent review remain required. Parent should coordinate any successor PR/publication after the hotfix; nothing was merged, deployed or presented as biological validation.
