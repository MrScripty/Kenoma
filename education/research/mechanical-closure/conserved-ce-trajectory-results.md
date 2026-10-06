# Conserved-head CE reversal: numerical prerequisite qualified, physical coupling pending

**All 144 declared dimensionless CE histories passed their fixed population, step-residual, initialization, terminal and discrete jump-ledger gates.** Independent original-bin-ODE references passed at both fixed resolutions. This advances a self-consistent conserved contractile-state implementation; it does **not** qualify the anatomical lift/release, resolve bulk compression, select a human force scale or execute the conditional finite-series comparison.

The [precommitted protocol](conserved-ce-trajectory-protocol.md), runner and independent audit are pinned to `b21ee8c252d4160a367fa7b21a9adf8c57a1dcaf`. The [original PLOS pixel audit](original-plos-table-visual-audit.md), commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`, supplies the publication median column. Its source is [van der Zee et al. (2026), Cross-bridge model for predicting muscle short-range stiffness during movement](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748). No individual MAT coefficient was mixed in. This is an independent hybrid of the audited code's conserved M=1-B branch and the article's raw Q/beta force, with held N, overlap1 and no PE/SE. Exact article/code replay remains a separate claim.

## Gate evidence

| Check | Worst observed | Fixed gate |
|---|---:|---:|
| Initial full kinetic residual L1 | 1.158e-14 /s | 1e-10 /s |
| Terminal full kinetic residual L1 at1s | 8.754e-11 /s | 1e-10 /s |
| Full BE residual, normalized as declared | 6.467e-18 | 1e-12 |
| Smallest admitted population | 1.229e-26 | Strictly nonnegative |
| Jump force identity error | 4.309e-16 | 2e-12 |
| Jump elastic-energy identity error | 3.252e-16 | 2e-12 |
| Escaped attached mass, either jump | 4.439e-18 | Explicit accounting, no clipping |
| Independent reference resolution state L1 difference | 1.829e-16 | 1e-10 |
| Independent reference resolution force difference | 2.645e-16 | 2e-10 |

The histories contain **84,000 accepted BE steps**, with 11 matched states per case including both sides of each jump. The independent audit covers 48 shared reference groups, both max-step values and **144,240 accepted reference nodes**. It evolves its own reversal state and checks strict nonnegative bins and B<=N at all accepted nodes and matched times. No failure, clipping, reset, longer hold, retry or changed iteration/tolerance budget occurred. No solver work was used to erase an anatomical failure.

The original M=1 benchmark remains frozen and distinct. For the newly conserved M=1-B law at N=1, the continuous stationary integrals on [-3,3] give B=.4993502931 and normalized raw force **.9883483646**. This is not reset to one; the old fixed-M value1.3177970777 remains valid for its declared abstraction. The change follows the population convention, not an SI force calibration or fit to stability.

## Matched-time refinement and work limits

At BE timestep .001s the maximum matched state L1 error is **6.7863e-6**, or **.4911% of the initial distribution perturbation**. Maximum force error is **5.0881e-6 in normalized force**, or **.5123% of the initial force jump**. These percentages are response-error normalizations, not percentages of total muscle force and not acceptance thresholds. State error-halving ratios .5052–.5103 and force ratios .5046–.5096 support first-order time convergence over the declared family.

Raw total-force strain-bin pair differences shrink by .2631–.2754, partly reflecting the equilibrium baseline. After subtracting EACH grid's own equilibrium force, matched transient pair differences shrink by **.4827–.5220**. Thus the transport response remains approximately first order in strain-bin width. Source-bin refinement cannot be advertised as second-order transient convergence merely because its stationary or total force is more accurate. Extent changes from R2.4 to3 produce at most8.882e-16 matched force difference; this bounds that finite-domain comparison, not an independently continuous-strain transient error.

Upwind center-mass interpolation has a positive variance contribution to elastic energy. Across both jumps it equals1.969–1.997% of absolute rigid translation work at dx=.04, .959–.986% at .02, and **.454–.481% at .01**. The discrete energy identity passes while this numerical work persists. It is explicitly reported rather than counted as physical elastic input. A continuous transport reference or a separately qualified transport discretization remains necessary for a physical work claim; chemical-energy accounting is also absent.

The [rendered figure](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/conserved-ce-refinement.pdf) summarizes the history and differences. Curves join the matched samples; the reference evolves continuously between them. The [PNG](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/conserved-ce-refinement.png), [raw runner log](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/execute.log), [summary](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/summary.json), [BE distributions](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/matched-states.npz), [independent log](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/independent-audit.log), [independent reference](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/independent-reference.npz), [independent audit note](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/independent-audit-note.md) and [response/work analysis](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/refinement-analysis.json) preserve the underlying evidence.

## What still blocks the loaded mechanical goal

The original-table visual prerequisite is now satisfied. The [calibration reconciliation](calibration-source-reconciliation.md) still lacks the linked specimen's raw sensor-to-N chain, area convention, upstream passive subtraction and force-reference denominator. The [convention memo](article-code-convention-decision.md) also leaves a complete PE/SE law, rest offsets and initializer to be selected coherently before series coupling. Componentwise medians, historical individual-fit fields, code K=100 and fitting/article K=1 cannot silently define one measured circuit. An authored dimensionless circuit would require a new explicit protocol and would remain a sensitivity model.

The [closeout log](../../data/anatomical-arm-v1/review/conserved-ce-trajectory/closeout-validation.log) records seven passing read-only evidence checks. The frozen dimensional-mapping checker reproduces its historical `sourceVisualPrerequisiteSatisfied=false` receipt; the additive original-table audit supplies the current satisfied status. Earlier blocker records are preserved with their original meaning rather than rewritten.

The original stationary volume-preserving negative directions and geometric/residual failures are unchanged. A positive held-population CE slope does not establish coupled continuum stability or repair them. Human serial/fascicle/overlap and tendon mapping remain unqualified; no anatomical constitutive replacement is justified here. Full nodal/quadrature/timestep convergence, compression/contact credibility and the self-consistent dense arm trajectory are still outstanding. Skin remains excluded.

The [internal implementation review](conserved-ce-trajectory-internal-audit.md) also identifies a latent reporting limitation: if a future runner case fails late, admitted distributions/clock and matched prefix survive, but locally accumulated jump ledgers/running diagnostics are not fully exported with the failed witness. No case failed in this frozen packet, so no actual ledger was lost. Correct that export in a new version before using this runner for a new coupled failure-prone experiment; do not rewrite this executed source or its receipts.

Production mechanics, lab/book equations and Lean statements remain frozen because this packet implements a separately declared mathematical prerequisite. Pre-hold ancestor `7c8ec58ee8df051a387500b8555e9fac71b6569a` retains its historical Jeremy metadata. New commits use the verified owner **MrScripty <TheEnvironmentGuy@protonmail.com>**, with author and committer rechecked before each commit; no history rewrite or force push occurred.
