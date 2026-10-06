# Pre-execution continuous-strain CE internal audit

**The declared density model, ghost translation, reversal escape moments and matched-event construction are mathematically consistent. No equation defect was found in this read-only review.** The three initial reporting observations below were subsequently resolved by source-owner changes and statically rechecked before execution. Numerical population, jump, time and quadrature gates remain unexecuted in this lane.

Reviewed 2026-10-06: [continuous_strain_ce_reference.py](../../tools/continuous_strain_ce_reference.py) and the [pre-execution protocol](continuous-strain-ce-protocol.md). The future precommitted source/protocol revision must be recorded by the execution receipt; this review does not invent that pending commit identity. No reference/test/simulation or Git command was run, no numerical source was edited, and no old 144/72-case packet was rerun.

## Density and conserved populations

Main densities n(xi) are integrated with main Gauss weights wi to obtain B=Σwi ni. Pointwise Gaussian attachment is a rate density; it is correctly distinct from the old integrated cell attachment Fi and old attached bin masses pi. Point values need not be below N. The admission check requires finite nonnegative values for every main, ghost and edge density, and bounds only the main integrated attached fraction by N.

The RHS uses main-only B in the shared factor (1−B)(N−B), while each main/auxiliary point has its own f and g. Ghost/edge fields sample the same density function rather than add extra head population. Including their values in B would double count that function; the implementation does not do so. The stationary coefficient q(1−N+q), with I=∫f/g and the admitted positive quadratic root q, correctly supplies n*=q(1−N+q)f/g. The weighted original RHS and independently adaptive stationary moments are checked separately from that scalar construction.

## Translation, boundaries and both jump ledgers

After the initial displacement δ, the main state is n*(x−δ) on its translated support. The ghost coordinate z=x+δ has loaded density n*(z−δ)=n*(x), masked where z lies outside D. Its own f(z),g(z) and the same main B evolve that function value through the first hold. Values outside D stay zero because both their initial density and attachment input are zero. At reversal, the evolved ghost endpoint is therefore the required n_pre(x+δ) at each main node. No strain interpolation or backward-Euler reset is inserted.

For the reversal displacement h=−δ, the 32 edge points lie in its escaping **source** strip: the right strip for h>0 and left strip for h<0. They evolve their own source-coordinate densities with shared main feedback. Their translated destination is edge_x+h=edge_x−δ. The call evaluating moments at that destination correctly gives escaped mass, signed force moment and nonnegative elastic energy. The initial jump independently integrates its stationary source strip with destination q+δ.

Consequently B_after+escapedMass=B_before, ΔFhat=B_before δ/β−escapedNormalizedMoment, and ΔEhat=Fhat_before δ+B_before δ²/(2β)−escapedNormalizedElasticEnergy are the correct exact-translation identities. The escaped force moment must retain its sign; the implementation does. There is no interpolation-variance work term. Boundary loss increases both implicit M=1−B and free-site capacity N−B; it is not immediately reattached or erased by normalization.

“Exact translation” here means evaluating the transported function without a strain interpolator. Main/edge/adaptive integrals and the shared B remain numerical quadrature approximations until their declared gates pass. Fixed 32-point edge integration is not itself an analytic integral or a separate edge-node refinement study. Even a passing jump-energy identity supplies no chemical-energy closure.

## Solver admission and event clock

The first segment is exactly 0→.2 s and the second .2→1 s. Main output order is equilibrium0-before, translated0-after, .008,.02,.04,.1,.2-before,.2-after,.3,.5,1: 11 states with distinct jump sides. Auxiliary samples correctly contain loaded0 and the five first-segment samples through .2-before. Requested samples use temporal dense output, not strain interpolation.

After each low-level DOP853 step, the driver checks the proposed accepted node and every matched dense sample crossed in that interval before updating the external admitted state/clock or any prefix. If a matched sample fails, the solver's internally advanced attempted state is separate from the externally admitted prior node. Normal DOP853 embedded trial/error control is retained; it is not an external restart after a population or ledger failure. The loop contains no retry, changed input, clipped state or longer horizon.

The completed-run design has 16 domain/calcium/displacement groups ×3 main node counts ×2 temporal resolutions=96 histories. Moment comparisons use identical event times; bin masses and point densities are not subjected to an invented common nodal L1 norm. Each model's own initial equilibrium is subtracted for response comparisons, with normalization denominators recorded. Finite-bin comparison errors add no retuned response pass threshold.

## Failure reporting review

Passed loading and reversal ledger dictionaries are placed in `CONTEXT['admittedLedgers']` at admission and copied by `preserve_context`. On a late failure, they are serialized with initial verification, the current candidate, last admitted state/clock, attempted solver step and both segment prefixes when present. Thus the earlier completed-runner partial-ledger gap is addressed in this design. Completed histories are retained separately in the outer record/archive.

Three pre-execution reporting observations were sent to the parent:

- Initialize current R/count/pCa/δ/max_step metadata at `run` entry. In the reviewed initial version these inputs entered `initialVerification` only after the initial/adaptive checks passed; an early failure therefore lacked an explicit current-run identity in its receipt.
- A `solver.step()` return with failed status is captured. An exception raised directly by `solver.step()` or `dense_output()` needs a local current-attempt snapshot, or an explicit unavailable-current-candidate marker, to avoid labeling stale candidate context as the new failed attempt.
- The protocol says exclusive receipt creation. The reviewed initial version had an existence preflight followed by overwrite-capable file writes. Literal exclusive output handles would enforce the declared contract.

At the initial review, these observations did not establish an actual numerical failure or authorize a gate change, and their correction had not yet been verified. Their subsequent static resolution is recorded additively below. The eventual execution source hash and receipts must identify the committed implementation.

## Additive static resolution before precommit

After the original review above, the reference owner reported the instrumentation fixes ready. The audit lane re-read the changed sections on 2026-10-06, without executing the source, a test or a simulation. This subsection records that subsequent correction while preserving the earlier pre-execution observations.

- `run` now initializes `CONTEXT['currentRun']` immediately after clearing context, before grid construction or early gates. It includes R, count, pCa, displacement and max_step. `preserve_context` copies this identity into the failure witness, and the final serializer retains it as metadata.
- Both `solver.step()` and `solver.dense_output()` now have local exception handlers calling `snapshot_solver_exception`. That helper clears stale candidate context, captures the current stored solver time/state and available evaluation count, records the exception/stage, and explicitly marks the hidden failed internal trial unavailable. It distinguishes a dense-output stage's available accepted-node proposal from an internal failed trial. It does not advance the external admitted state/clock or prefix. The outer failure serializer writes the attempted-state array only when present.
- Before any history kernel, `ExitStack` reserves the archive with mode `xb` and receipt with mode `x`. Final output uses those reserved handles and closes them after writing/flushing; an acquisition failure closes acquired handles and raises before histories execute. This enforces literal exclusive creation rather than relying solely on the retained preflight existence check.

Static resolution of all three reporting observations is confirmed. These changes add identity/snapshot/output instrumentation; the reviewed density equations, translation/escape construction, admission order and numerical gates remain unchanged. The future execution receipt must pin the committed corrected source. No numerical pass result is implied by this static verification.

The parent then changed the outer orchestration exception handler from `Exception` to `BaseException`. A final read confirms that handled `KeyboardInterrupt`/`SystemExit` now enter the same context-preservation/failed-receipt path before `finally` writes the reserved archive and receipt. This is interruption reporting, not a retry or numerical gate change; it cannot guarantee receipts after an uncatchable process kill. The corrected source SHA-256 inspected at this final check is `8f67cb3c84379ca1f1d6363e5f75d3e606113e120d17cf459240a9d944e0017e`. The run remains unexecuted at this final static review.

The reference remains a finite-domain, source-informed direct-CE numerical prerequisite. SI force/area calibration, physical series/passive initialization, anatomical compression/contact and dense loaded human trajectories remain separate tasks. All earlier source-version distinctions and negative witnesses remain intact.
