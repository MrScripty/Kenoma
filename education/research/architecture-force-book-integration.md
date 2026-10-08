# Architecture-force source-only book integration

## Scope and source identity

This is an isolated source candidate based on the public PR12 tree
`97207365faaf17ecfb843a9b9422ef4ea5910bf1` at
`f6d6bde9974e9894bc5a527c80beef633fd5a1f6`. The local source snapshot has the same
tree under commit `bef7c3614351baa7bc6821cbb91c88ade9d45070`; commit identities
are not interchangeable. No existing branch, original contribution, anatomical
dataset, operator, calibration coefficient, trajectory or failure threshold is
changed. The thirteen original contribution files are bound in
`architecture-force-book-source.json` and retained byte-for-byte.

The canonical chapter is `book/chapters/09ab-architecture-force.md`, after
nonuniform volume and before material response. It reuses the qualified research
and adds the book's six proof-card slots and a static/default lab entry. The
contribution chapter is deliberately not registered directly in `book.json`,
because the legacy build special-cases contribution paths as continuum content.

The resulting source inventory is 27 chapters and 115 declarations in fourteen
Lean files: 30 integer and 85 Real. The historical nonuniform milestone remains
103 + 6 = 109. Its preserved acceptance composition and original proof identities
are unchanged; newly assembled book metadata records the current total and a
separate historical total. A registry count is not a fresh kernel result.

## Preserved mathematical and numerical boundaries

`proofs/ArchitectureForce.lean` is an exact copy. The book claim map preserves
all original IDs, theorem names, claims, domains, model-function references and
excluded conclusions. It adds explicit assumptions, full statements and display
links. The existing all-or-nothing Real checker now includes this family; a later
failure removes all stale Real receipts and emits no partial-family success.

The six statements concern only declared scalar material-cut force invariance,
two-group area weighting, one-time projection, projected group sums, telescoping
series balance and paired-force power. They do not establish Nanson's formula,
its geometric hypotheses, area integration, numerical refinement, constitutive
suitability, equilibrium or biological calibration. The seven symbolic checks
remain supplementary; they are not added to the Lean count.

Default authored values are reference contractile area 80 mm², current projected
area 100 mm², nominal stress 300 kPa, Cauchy stress 240 kPa, axial force 24 N and
tendon-directed force 20.78 N. Packing is applied once to a 100 mm² geometric
reference area; stretch is 0.8, J is 1, pennation is 30°, and force–length is held
at one. Projection is applied once. No acute fibre creation or bulge-force bonus
is inferred.

## Portable assembly and release gates

`tools/architecture_force_lab.py` performs bounded source assembly only. It
checks the preserved sources and supplied book receipt, copies the original
archive to `dist/contributions/architecture-force`, and assembles the reading
lab at `dist/architecture-force/index.html`. Model/control/style bytes remain
unchanged. Only assembled HTML gains initial no-JavaScript values, print-default
values and book/archive links. Every source and output is hash-bound; failure
removes the stale lab registration. It cannot generate a proof pass by itself.

The book's default table is text, available without WebGL or JavaScript and in
the manuscript/PDF. PDF links point back into the canonical chapter and evidence
section, and the new proof family receives the existing complete-source,
receipt and kernel-report appendices. Print gates require all 115 cards and
fourteen source appendices. The artifact checker additionally verifies lab
source closure, all six default quantities, actual chapter-bound PDF values and
complete architecture-force source.

`tests/architecture_force_book_browser.py` is prepared for a later authorized
full build. It follows the real book entry at desktop/mobile sizes, exercises
keyboard range bounds, the force–length checkbox and repeated Reset, verifies
local links and print defaults, and checks the no-JavaScript initial readout.
Five JPEG quality-85 captures are source-bound and still require visual review.
One source-only workflow line registers this check in the existing full-build
job; job conditions, publication rules and the bounded contribution job remain
unchanged. No workflow has been dispatched or run for this candidate.

## Validation performed and withheld

The source-only check set includes:

- The twelve preserved Node scalar/operator contracts
- Seven supplementary symbolic identities
- Fourteen focused source/assembly tests, using temporary synthetic proof
  receipts explicitly marked as test fixtures
- The existing five Real receipt-negative unit tests, with mocked compilation
- Twenty-five bounded contribution qualification-control unit tests
- The existing seventeen actual-PDF fixture readability tests, two theorem
  statement-extraction tests and one PDF-outline fixture test
- Syntax/source checks, exact source-write-set review and unchanged contribution
  and anatomy manifests

No mock receipt or printed unit-test message is fresh Lean evidence. The existing
standalone qualification at exact commit
`143ac8863cd8a5be736e2c455cac9605c2e20a1f` and
[run 37743673184](https://github.com/MrScripty/Kenoma/actions/runs/37743673184)
remains limited to that contribution. The original automatic receipt's pending
human-inspection marker remains untouched. No integrated browser or actual book
PDF pass is claimed by this source candidate.

The remaining decision is whether to authorize complete-book qualification.
`npm run build` is not render-only: it launches fresh oscillator, elbow, series,
spatial and material experiments, including the spatial 640-iteration case.
The full workflow contains additional anatomical research operations and live
coupling. Source preparation does not authorize those operations. Full proof
closure, the full build, integrated browser/PDF/render review and owner release
review remain held. Publication, merge, a ready-for-review transition and Pages
deployment are separate actions and have not occurred.

The anatomical capstone remains unfinished. In particular, source-bound force
bookkeeping cannot turn unresolved full-nodal stationarity, local compression or
model-reference stress fitting into physiological calibration. The required
next anatomical gate is still an equilibrated, locally admissible calibration
specimen with an adequate displacement/pressure space.
