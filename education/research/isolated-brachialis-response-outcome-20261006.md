# Paired response stopped on actual trial inversion

The authorized smallest response attempted FJ1486 brachialis only, with the same **2,048-point rule**, geometry/fibres, activation1, fitted sigma0, original material potential/tangent, complete fixed caps and empty sheet model in both45/46 spaces. It performed no force rematching, parameter fitting or mesh alteration. **No46-mode equilibrium completed.** The attempt stopped at its registered geometry gate and was not restarted.

Frozen protocol/preflight: `f50e1cecfa420fa06d1a953b15764030ec97269f` (protocol source `b14ac8ee41ff5ceafb848ffdd02e1466918453c5`). Response operator/runner source: `0f0b33f68085159c7598e6b9f312c705979c763a`. Passing numerical preflight before nonlinear execution: `c288ce19d2fdb8ea07c01cf2b153391003f0b970`. Raw refusal evidence: `155dbefd088dbe6c0e3995692b0cec02c6384de2`. Stored-state reporting/localization source: `df027f8031c40b19471839212aabdb578655e913`. All commits use repo-local MrScripty <TheEnvironmentGuy@protonmail.com>.

[Protocol](isolated-enrichment-protocol-20261006.md), [preflight](../review/isolated-brachialis-response-20261006/preflight.json), [raw execution receipt](../review/isolated-brachialis-response-20261006/results.json), [run log](../review/isolated-brachialis-response-20261006/execute.log), [metric summary](../review/isolated-brachialis-response-20261006/response-summary.json) and [refused-trial geometry](../review/isolated-brachialis-response-20261006/refused-trial-geometry.json) are portable repository-relative links. Numerical results and the compact summaries are each below1MiB for independent Contents API review. The reporting pass evaluates the already stored last valid iterate; it performs no further optimizer step. The refused trial receives geometry arithmetic only, with no constitutive evaluation.

## Same-rule control and bounded response

The fine-rule45-mode control required one Newton step. It passed the unchanged projected0.0001N gate while retaining a large **full free-node failure**. One normalized cap-zero negative omitted-gradient direction was then frozen from **that control**, not from the earlier32-point fit. Exact dyadic rank is46; directional derivatives and two tangent-difference probes pass. Its initial direct and relaxed curvatures were positive,54,015.623 and44,501.727N/m.

| Quantity | Same-rule45-mode projected equilibrium | First valid46-mode optimization step |
|---|---:|---:|
| Projected maximum (N) | 0.0000582008, pass | 343.385937, fail |
| Full1,485-component free maximum (N) | 64.066837, fail | 53.595915, fail |
| Full free L2 norm (N) | 379.531980 | 349.338833 |
| Fixed-activation solve potential (J) | −33.48083148 | −33.74999714 |
| Minimum queried corner J | 0.559423903 | 0.427391682 |
| Direct added-direction curvature (N/m) | 54,015.623 | 65,833.141 |
| Relaxed added-direction curvature (N/m) | 44,501.727 | 56,633.410 |
| Exact orientation-certified elements | 252/252 | 252/252 |

The first46-mode optimization step has added coefficient0.000743315809m; its maximum physical nodal increment was bounded at0.2mm by the same solver rule used for both spaces. It lowers potential by **0.269165658J**, decreases the full maximum by10.470923N, and **worsens local compression** by lowering corner J by0.132032221. Its added-direction residual still has magnitude343.385937N, so it is not even a46-mode projected equilibrium. The tangent at this partial iterate remains positive in the46-dimensional space; that does not guarantee valid subsequent geometry or full-space stability.

Potential changes are matrix +0.000187062J, volume −0.084309517J, passive fibre −0.014605449J and active solve potential −0.170437754J. Linear virtual work at the45-mode control for this displacement is −0.282112118J. These fixed-activation potential calculations do not establish physiological work, dissipation or an energy-conservation ledger.

Full nodal distal axial reaction changes **605.119313→620.052417N**; proximal axial reaction changes **−765.658973→−785.701242N**. The original boundary-translation axial conjugates are different: distal **987.268308→980.269811N**, proximal **−987.268309→−981.034785N**. These nonstationary full nodal fields do not supply a physical force match. Target987.274412N and sigma0 stay unchanged; no quantity is fitted to restore that target.

## Refusal and preserved failures

The next Newton trial could certify249/252 elements. Subsequent geometry-only localization shows more than an inconclusive sufficient certificate: it has **negative queried determinants**, minimum sampled J **−0.708052180** and corner J **−0.837360573**. The exact stored current P2 determinant's pure-corner Bernstein numerators are negative at:

| Element | Corner | Global node | Queried corner J | Exact current corner numerator sign |
|---|---:|---:|---:|---|
| 247 | 0 | 92 | −0.837360573 | Negative |
| 250 | 0 | 93 | −0.709783529 | Negative |
| 251 | 0 | 93 | −0.468992033 | Negative |

At a tetrahedral corner the corresponding Bernstein basis function is1 and the other functions vanish. Its denominator is positive. The existing exact dyadic certificate therefore provides negative current Jacobian witnesses at these stored corners; their reference Jacobians are positive. This is **actual local inversion of the stored trial**, not merely a negative interior Bernstein coefficient. All complete coefficients and refused coordinates remain in the geometry receipt. The solver refused the trial before material evaluation, recorded both its trial refusal and stop reason, and left the original physical state unadvanced. No gate was loosened and no smaller-step retry or new solve followed.

The six structural tests, three new operator tests, frozen-state preflight, direction/rank/derivative controls and valid-state orientation/tangent checks pass. The45-mode control passes only its projected force gate. Every full free-node gate remains failed at **0.0001N**; the partial46 projected gate and next-trial geometry gate fail. Lower potential and reduced full residual do not qualify local compression, full equilibrium or anatomy.

This is one **refused response experiment**, not a convergence series or anatomical calibration. The full-P2/nested sequence is specified but unexecuted. The known256→2,048 changes still exceed the absolute force threshold by71×/888×/467× across the three historical fixtures. The historical0.0173851553295N is a different coupled0.10s state **and a different460-coordinate generalized incremental-gradient metric**, never a full free-node comparison. That correction is an explicit successor; all original evidence and failed gates are unchanged. Main, diagnosis, protocol and published208/221-page candidates were not modified, and no PR, publication or deployment was performed. Further nonlinear work requires review of this refusal and a newly declared protocol.
