# Independent conserved-head direct-CE trajectory audit

**All fixed independent-reference and strict population gates passed for 144 histories and 48 distinct reference groups.** This is a dimensionless, source-informed direct-CE step/reversal prerequisite. It is not the finite-series loaded mechanical comparison, a published measured trajectory reproduction, a human force law or a continuum stability qualification.

Executed once on 2026-10-06 under precommitted protocol/runner/auditor commit `b21ee8c252d4160a367fa7b21a9adf8c57a1dcaf`, using [the declared protocol](../../../../research/mechanical-closure/conserved-ce-trajectory-protocol.md) and [independent auditor](../../../../tools/audit_conserved_ce_trajectory.py). The source packet reports `PASS_CONSERVED_CE_HISTORY_GATES`; this separate [audit receipt](independent-audit.json) reports `PASS_INDEPENDENT_REFERENCE_AND_STRICT_POPULATION_GATES`. The one-shot process returned exit code 0, and its [raw log](independent-audit.log) records normal completion. No retry, clipping, source change, extra hold, changed solver tolerance or additional reference resolution was used.

## Reference and population checks

The auditor independently constructed Gaussian bin rates, midpoint detachment, held calcium capacity, mp60 analytic equilibrium, the original coupled bin ODE and both center-bin remaps. Each DOP853 reference shifted its own equilibrium at t=0 and its own evolved distribution at t=.2; it never reset from a backward-Euler state. Both segments retained the declared terminal t=1 s. Two fixed max-step values (.001/.0005 s) used rtol=1e−11 and atol=1e−14.

All **144,240 accepted reference nodes**, all matched reference states and every saved subject matched state passed finite/nonnegative-bin and independently summed B≤N gates. The smallest accepted reference population was 1.22933625e-26; no invalid-state witness was generated. The initial source equilibrium's maximum original-RHS L1 residual was 1.09515511e-14/s against 1e−10/s, and maximum bin difference from independent mp60 equilibrium was 3.46944695e-18 against 2e−12. Independent grid/rate differences passed their normalized 1e−12 gates.

The two fixed reference resolutions differed by at most **1.82812252e-16 in matched state L1** and **2.64456633e-16 in force**, against gates 1e−10 and 2e−10. These measure reference resolution for the finite-bin ODE; they are not confidence intervals or continuous-strain error bounds.

## Matched-time backward-Euler errors

State error is the largest matched-time L1 difference from the finer reference. Force error uses Q/beta with beta=.5. Each normalized state error divides by ||p(0+)−p(0−)||1; each normalized force error divides by |F(0+)−F(0−)| for its own case. Percentages and absolute maxima can come from different cases. [The postprocessing receipt](independent-audit-assessment.json) retains all 144 normalization denominators/results without evolving any trajectory.

| Timestep (s) | Max state L1 error | Max force error | Max state error / initial shift L1 | Max force error / initial force increment |
|---:|---:|---:|---:|---:|
| 0.004 | 2.63189565e-05 | 1.98042783e-05 | 1.90455% | 1.99322% |
| 0.002 | 1.343148e-05 | 1.00835271e-05 | 0.971957% | 1.01503% |
| 0.001 | 6.78628033e-06 | 5.08814315e-06 | 0.491083% | 0.512226% |

State-error timestep-halving ratios span 0.505224411–0.510334822; force-error ratios span 0.50459954–0.509594692. Ratios near .5 support observed first-order time accuracy for this protocol. No response-error pass threshold was invented after execution. Initial and terminal residual checks alone would not establish this transient accuracy.

## Finite-bin and extent diagnostics

For dx=.04→.02→.01, pairwise **total** matched reference force differences have maximum 2.23875536e-05; their second/first difference ratios span 0.263087023–0.275355758. These include each grid's baseline equilibrium force difference.

After subtracting each reference's own preloading equilibrium force, the pairwise response differences have maximum 2.39746879e-06, with ratios 0.482702349–0.521993301, approximately first order. This separate calculation prevents the baseline's near-quadratic refinement from being mistaken for second-order transient response convergence. The protocol's interpolation-work term remains an authored discretization effect, separately recorded by the source packet; this audit supplies no physical chemical-energy closure.

The largest matched force difference between R=2.4 and R=3 at common dx/input was 8.8817842e-16. This is a two-extent diagnostic for these small shifts, not a proof on an unbounded strain domain.

## Preserved identities and limits

[Independent reference NPZ](independent-reference.npz) contains all matched reference distributions and accepted **time** arrays, 3,195,534 bytes. Full accepted-population arrays were checked but not archived: the JSON receipt records their canonical little-endian float64 SHA-256, shape, byte count, minimum population and minimum/maximum B. The full source matched distributions remain in [matched-states.npz](matched-states.npz). No production, old packet or source-bound research file changed; no Git operation occurred in this lane.

| Artifact | SHA-256 |
|---|---|
| [summary.json](summary.json) | `6d4b7b9be2e163039b92db52b56c659c46c976d3172a727e99ed7bdf882b2cfa` |
| [matched-states.npz](matched-states.npz) | `b2be81c2243d6df40678614dcaee8886b083507263668e08b173014ab0d15e88` |
| [independent-audit.json](independent-audit.json) | `f2811ae9576e07c97a5a89e0872ee531e2980cfcd8e1f3357c350c21e27c0fcb` |
| [independent-audit.log](independent-audit.log) | `a9d63ef671f9d34a404d00cd1e943d63fcdf60ba35a0b810acf397947cbdb679` |
| [independent-reference.npz](independent-reference.npz) | `aa1335b374736c86bb3d35d61c3e1f7915a65edee34bf6b820702de37f0226de` |

The preserved negative continuum witnesses, anatomical geometry/residual failures, source-version distinctions and missing SI force/area and compliant-series calibration remain unresolved. This audit qualifies the declared finite-bin reference and population gates and measures numerical transient errors; it does not qualify an anatomical loading/release trajectory.
