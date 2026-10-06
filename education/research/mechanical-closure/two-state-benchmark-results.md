# Direct-clamp cross-bridge population: bounded numerical result

**All 144 predeclared cases passed without changing rates, gates, timestep budget or horizon.** This qualifies the declared fixed-capacity kinetic/center-mass-transport implementation on six strain-space grids. It demonstrates the difference between positive fast elastic response and same-input relaxed response. It is not a replacement arm law, a published fiber-history reproduction or a qualified anatomical lift/release trajectory.

Entry: `8741bba2134ea51e9138061a0ebc0b6ba5e9a1b3`. [Protocol](two-state-benchmark-protocol.md) committed at `4c9406b` before implementation/execution; source implementation committed at `947ce95`; first raw results committed at `47ec7e2`. The exact execution SHA and source hashes are in [summary.json](../../data/anatomical-arm-v1/review/two-state-kinetics/summary.json). Original evidence and fixed-activation negative witnesses remain intact. Production/book/Lean and native-worker files were not changed.

## What was tested

The [original van der Zee et al. 2026 study](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748) supplies a nonhuman, near-optimum equation fixture. Here overlap/availability are held at one and calcium-dependent capacity is fixed. It omits series/parallel coupling and cooperative state evolution. Rates, Gaussian normalization, coordinate/force measure and concentration conversion are disclosed in the [source rendering evidence](source-rendering-evidence.md) and [independent convention audit](two-state-source-convention-audit.md). Original PDF extraction was readable; screenshot pixels and pinned authors' code were unavailable. Table-column association follows populated-row/header ordering, rather than inspected visual cell alignment. No individual fitted fiber or measured history is reproduced.

There are two domains (±2.4, ±3), three bin widths (.04/.02/.01), pCa4.5/6.1, four signed shifts (±.001/±.0005) and three timesteps (.004/.002/.001 s): 144 cases. Complete populations at eight identical times through 1 s are preserved in [matched-states.npz](../../data/anatomical-arm-v1/review/two-state-kinetics/matched-states.npz). Bin arrays contain actual masses, with Gaussian cell-integrated attachment rates and midpoint detachment rates. Backward Euler uses the direct positivity-safe mass formula and accepts a candidate before advancing time. There is no optimizer, clipping, terminal reset or extension of the one-second budget.

An independent matrix exponential references each finite-dimensional Markov generator. This is independent temporal evidence for the same strain grid, not a proof of continuous transport accuracy. Exact continuous equilibrium quadrature references spatial refinement. Center-mass remapping returns escaped mass to the detached pool and records its off-grid **discrete** moment; that moment is not represented as the exact continuous partial-cell tail force.

## Raw numerical evidence

| Quantity over the declared cases | Measured value | Predeclared gate |
|---|---:|---:|
| Worst all-step population mass error | 3.7747583e−14 | 2e−12 |
| Minimum BE population | 1.3854191e−26 | ≥0, without clipping |
| Worst fixed-1-s kinetic residual, l1 | 9.3472452e−13/s | 1e−10/s |
| Worst 1-s force difference from original equilibrium | 5.4622973e−14 | 1e−10 |
| Worst matrix-exponential mass error | 8.6597396e−15 | 2e−12 |
| Finest-bin relative equilibrium force error | 1.6869213e−6 | 1e−4 |
| Bin-halving equilibrium-error ratios | .2500092–.2500370 | .2–.8 |
| Timestep-halving matched-force-error ratios | .5046001–.5095384 | .3–.8 |
| Worst finest-timestep force error / (abs(delta) N/beta) | .00339239 | .05 |
| Worst matched-time force difference between extents | 7.3718809e−14 | 1e−8 |
| Largest escaped attached mass | 5.9176462e−18 | 1e−10 |
| Largest absolute escaped normalized discrete moment | 4.0476700e−17 | 1e−10 |

The temporal errors decrease approximately at first order and equilibrium force errors approximately at second order. This is evidence for the specified numerical operators and selected grid family. It does not turn a negligible extent difference into a claim of source-history or anatomical mesh convergence. The original rates and normalization remain unchanged.

Independent equilibrium quadrature gives I=1.992220371316941 and first-moment integral −.020650740709578, with absolute error estimates 9.41e−13 and 6.38e−13. At maximal capacity N=1, B=.665800016073 and normalized baseline force is **1.317797077720**, not one. Componentwise medians and the declared beta=.5 do not force an individually calibrated unit-force state. No extra force renormalization was introduced.

On the finest grid at pCa4.5 the baseline force is 1.317778297593 and the immediate +.001-shift force slope is 1.331581719447 per dimensionless link-coordinate shift; at pCa6.1 those values are .614102410057 and .620534990289. Both signed/amplitude probes verify the analytic fast moment increment, including recorded boundary correction. These are normalized quantities, not human stiffness in N/m.

The [execution log](../../data/anatomical-arm-v1/review/two-state-kinetics/execute.log), summary and complete states preserve the first run. No kinetic case failed. The earlier active packet's symbolic assertion failure/correction and all older geometric/residual failures remain retained. This result does not replace those histories.

## Interpretation and next blocker

With fixed input, rates and domain, this two-state model has a unique equilibrium. Translating an attached population gives an immediate force change; subsequent kinetics returns it to the same distribution and force. The zero relaxed force increment is therefore a structural prediction of this abstraction, not evidence that a physiological descending branch has become stable. It also cannot represent a persistent history-dependent equilibrium merely by retaining a finite transient.

The [cooperative population audit](cooperative-population-audit.md) narrows a real definition question. The displayed cooperative equation's OFF-boundary condition is inward under nonnegative recruitment when k2≥f1 O; the reported k2=200/s and three-state f1=84.5/s satisfy that sufficient bound. Omission of an explicit transfer term is consequently not a demonstrated source-parameter population failure. Its microscopic interpretation and noncooperative model-family branch still need code parity. Merely setting k2=0 and initializing M=1 does not freeze the displayed cooperative M equation; this benchmark explicitly freezes M as part of its separate reduction.

The next substantive replay is blocked on an immutable individual-fiber implementation/data pin, exact cooperative-state convention, actual initial distribution/force normalization and series/rest offsets. No accessible source supplies a same-specimen human atlas reference map or objective 3D contractile-state mapping. An equation-only cooperative experiment could be authored, but choosing missing initial/series/reference values would create another synthetic fixture. It would not complete the anatomical objective.

The [reference/architecture review](reference-architecture-source-review.md) gives a measurement specification and bounded long-head virtual-specimen proposal. It does not transfer population architecture to atlas BICshort. The [notation/lesson addendum](source-notation-and-lesson-implications-addendum.md) distinguishes Blemker source optimal stretch lambda_ofl from passive transition lambda*, and proposes bounded future book/Lean language. No current published statement or proof was rewritten around this scalar success.

The retained fixed-activation negative directions remain stationary saddles of the declared potential. They do not alone prove in-vivo or coupled active-dynamical instability. Weak P1 pressure admissibility, strict local constant-J directions, sampled determinant/crossing gates, stable mesh-family claims and anatomical/timestep convergence remain distinct obligations. Bulk/compression closure and a self-consistent dense loaded lift/release remain unqualified; skin remains deferred.

## Render

The [PNG](../../data/anatomical-arm-v1/review/two-state-kinetics/two-state-kinetics.png) and [PDF](../../data/anatomical-arm-v1/review/two-state-kinetics/two-state-kinetics.pdf) plot bound numerical receipts without rerunning the experiment. The source and output hashes are in [render-receipt.json](../../data/anatomical-arm-v1/review/two-state-kinetics/render-receipt.json). Visual inspection checked legibility, labels, units and the explicit scope limitation. The independent numerical audit and final evidence closure are separate receipts; their success does not broaden the biological claim.
