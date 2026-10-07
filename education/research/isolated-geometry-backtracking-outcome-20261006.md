# Geometry-aware implementation: structural preflight outcome

Separate branch `research/isolated-geometry-backtracking-20261006` starts from `71f48f0e41021c2a39b335d68bcc1800f8fb3f48`. Frozen implementation/protocol source: **`14c0ac1db9161bcca6c89f6b8a2ba8553fb288bb`**. Author: MrScripty `<TheEnvironmentGuy@protonmail.com>`.

The [structural receipt](../review/isolated-geometry-backtracking-20261006/structural-preflight.json) reports `PASS_STRUCTURAL_ADMISSIBILITY_PREFLIGHT_NO_SOLVE`; [test log](../review/isolated-geometry-backtracking-20261006/tests.log) records **11 passed,0 failed**. Syntax checks pass. All previous experiment/source/evidence hashes match. There were **zero constitutive evaluations, zero Newton iterations, zero nonlinear solves and zero brachialis optimizer trials**. Prescribed fixture-direction controller tests use synthetic callback energies only.

| Geometry query | Whole-path unchanged guard |
|---|---|
| Original frozen45 initialization | Certified |
| Archived initial45 → archived control45 | Certified |
| Archived control45 → last valid46 | Certified |
| Last valid46 → archived refused full trial | Unsupported/rejected |
| Last valid46 → newly rounded archived quarter-coordinate endpoint | Certified |

Every certified real-data path checks all20,160 guarded space×time controls across252 elements. The quarter endpoint is freshly reconstructed by the existing response-position function from rounded coordinates, with digest `eab0da6537a1c1fd3fcef459df8375dfbbb266ca7b40c9bbe7e97beb273c724e`. Its fresh path polynomial digest is `5889c3a12505352155487de2423edfe9c419aee205dfe89702821e3755643ce1`. This result proves geometric room only; it evaluates no material energy/force, selects no future Newton step, and establishes neither Armijo acceptance nor equilibrium. The archived cutoff is not used by the implementation.

The [protocol](isolated-geometry-backtracking-20261006.md) and [manifest](isolated-geometry-backtracking-20261006-inputs.json) define a complete paired rerun from the **same original45 initialization**. The45 rerun must reproduce the archived control coordinates and nodal field exactly before46 begins. Then the implementation uses the **exact archived once-selected direction**, checks its ordering/zero cap trace, rank46 and agreement with the same-rule control omitted gradient, and never reselects it. The preflight verifies those original geometry/basis identities without evaluating new gradients.

The [controller](../tools/isolated-geometry-backtracking.mjs) recompiles every newly rounded candidate's whole-path certificate before its material callback. Unsupported geometry is retained as a rejection and bounded fraction reduction. The unchanged21 fractions, initial0.2 mm nodal bound and Armijo constant are enforced. Raw Newton coordinate/nodal vectors, scaling, scaled vectors, rounded increments, fresh certificate hashes/witnesses and rejection reasons are recorded. A numerical/domain failure after certification remains fatal, without further halving. Tests explicitly demonstrate those behaviors, endpoint-positive/interior-inverted damage rejection, unchanged1e-6 guard, cap/nonfinite refusal and bounded Armijo exhaustion.

The [future runner](../tools/run-isolated-geometry-response.mjs) preserves the potential/material/quadrature/input bytes and full-nodal force gates. It checks positive projected tangent even at a projected stopping state, retains the original60-iteration ceiling, and reports independent full-nodal audits, projected/added residuals, energy components, J, cap reactions and last valid field. The frozen structural receipt and original numerical preflight are mandatory prerequisites; it refuses changed/uncommitted source or evidence overwrite.

The old `REFUSED_BOUNDED_RESPONSE` evidence remains unchanged. Its full-nodal and projected46 failures remain failures. A passing structural preflight does not clear those physical gates. Target987.26 N and old achieved fit987.2744117188512 N remain correctly distinguished. No force refit, extra modes, anatomical completion, stability or convergence claim is made.

**No nonlinear execution has occurred.** Independent review and subsequent explicit experiment authorization remain the next boundary. No PR, merge, publication/deployment, existing-branch mutation, environment-protection or credential change was performed. Repository publication consists only of this new research branch for review.
