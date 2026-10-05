# Finite-bulk research qualification

The separate Lab 5 extension now has a checked full-book Markdown/PDF and actual browser evidence. Tested source: `25718cb38327930e907c32499b03e46e0ada39a3`; tree: `7b128feb9ffe149715172c368e419402e3bf8c25`. This research lane extends the previously parked `5f67d4991decac35e7648d08ad8219cd3ad6b34f` feature. It does not change the frozen 29-claim release candidate.

At imposed height stretch 0.8, the existing Lab 5 material with shear modulus 1500 Pa and bulk modulus 50000 Pa gives free-side volume ratio 0.9939144716354632 and reaction 4.536371031795807 N. Confinement instead fixes volume ratio 0.8 and requires about 42.08871 N. Under the same 2 N load, free and confined height stretches are respectively about 0.899516 and 0.990389. These are homogeneous constitutive/boundary-condition comparisons, not anatomical measurements or a tissue-envelope qualification.

## Qualification evidence

- Fresh build compiled 33 Lean claims (12 mechanics, 2 transfer, 7 coupled, 4 arm algebra, 8 real kinematic/material claims), preserving the pinned Lean/mathlib sources. The four new material claims have their assumptions and limits printed in the book.
- Fresh compression numerical tests: 6 passed. Independent diagonal energy differences, geometric volume, volume-variable equilibrium, near-reference moduli and plate-work quadrature agree under the existing fixed gates. The parked feature's earlier full 134 Node / 16 Python results remain historical evidence, not a claim that those complete suites were rerun on this source.
- Fresh whole-book, property, compression and mobile/fault-recovery browser checks passed. Invalid/unsupported force inputs and zero-bulk force degeneracy retain the previous valid state.
- Fresh 94-page PDF passed artifact checks for source hashes, glyphs, page bounds and proof destinations. Selected pages 27–29, the mobile free-pressure proof card and the mobile free-displacement controls were visually reviewed. Property and compression render reruns removed a deliberately seeded stale page image and reported only fresh captures.
- Every current build input matched its recorded SHA-256 before copying the documents. Raw logs, proof receipts, browser receipts and captured images are retained in `data/compression-lab-v1/review/finite-bulk-qualification/`; the complete hash inventory is `evidence-manifest.json`.

## Preserved integration failures and bounded repairs

The first main-browser proof-count assertion failed without recording its actual count. A subsequent DOM diagnostic found 33 proof cards, and a later actual run passed the same count check before identifying a missing linked benchmark asset. The build now copies the source-bound compression benchmark into its linked output location. The property-only no-JavaScript image selector now uses `data-property` so it counts the three property lessons without counting the separate compression extension. The main count assertion reports actual/expected counts on failure. Those failed logs remain under `review/integration-failures/`.

The research property and compression inspectors use the already reviewed bounded render-output cleanup: remove owned stale PDF page images before capturing, and bind the receipt to the fresh capture list. No material law, residual tolerance, iteration cap, accepted arm state or anatomical solver changed during this qualification.

## Deliverables and remaining scope

`deliverables/finite-bulk-qualification/kenoma-mechanics.md` has SHA-256 `bf9d876657233771087a735a0619e18d822789960434494d9f3073c69f2e1864`; the PDF has SHA-256 `ac41f02afc1a36b32f9d59c4e8e2a1a5b6c810a9adfb6896b2b029a3ba370963`. Their source identity and qualification scope are recorded in `delivery-manifest.json`.

This lane predates the release candidate's later worker, replay-contract, cold-CI and executable-package repairs. No portable ZIP is presented as qualified. Any future integration must retain those release repairs and be checked separately by the owner. The capstone still uses its logarithmic volume penalty; Lab 5 uses its existing quadratic penalty. Their finite-compression responses differ, as the book states. The homogeneous fixture does not resolve volumetric locking, full nodal force balance, quadrature/timestep convergence or whole-envelope credibility. No skin or anatomical calibration is justified by these results.
