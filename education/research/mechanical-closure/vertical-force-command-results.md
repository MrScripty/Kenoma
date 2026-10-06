# Bounded vertical force-command lab: review packet

Ten default trajectories pass the preregistered RK4 refinement, DOP853/Radau replay, force closure, component/combined work and momentum checks through their declared endpoints. Two presets stop conservatively at an opposing antiwindup switching surface. They have passing common sampled prefixes, **not qualified full trajectories**. This is a separate educational scalar fixture; it does not repair, calibrate or qualify the whole-arm tissue envelope.

Branch: `education/vertical-force-command-lab`. Tested source commit: `39f7cd741ffb5d6736510da6ddaec912964dd106`; tree: `a71929fde790cf784ff3e87e46e223f3eeb22e71`. [Protocol](vertical-force-command-protocol.md) and its fixed gains kp=.4, ki=8/s were committed in `78501f4` before case execution. [Diagnostics](vertical-force-reference-diagnostics.md) distinguish the preserved failures and subsequent implementation corrections. The final evidence-only commit contains this report and the hash-bound packet.

## Numerical evidence

| Case | Qualified comparison extent | RK4 fine last accepted time (s) | Tracking classification |
| --- | --- | --- | --- |
| baseline | full | 0.300000 | met |
| pulse | full | 0.300000 | window-invalid-command-change |
| lower | full | 0.300000 | met |
| release | full | 0.300000 | not-applicable |
| high | common samples through 0.105 s | 0.105400 | window-not-reached |
| mass-025 | full | 0.300000 | missed |
| mass-05 | full | 0.300000 | missed |
| mass-1 | common samples through 0.261 s | 0.262000 | window-not-reached |
| desc-fixed-plus | full | 0.150000 | not-applicable |
| desc-fixed-minus | full | 0.150000 | not-applicable |
| desc-pi-plus | full | 0.150000 | met |
| desc-pi-minus | full | 0.150000 | met |

The reported comparison extents are **stored common accepted timestamps**, without interpolation/extrapolation across failures. The high case's independent last accepted times are .105130659806 s (DOP853) and .105139259069 s (Radau), while RK4 retains .105400 s. For mass-1 they are .261977613789 s, .261972026445 s and .262000 s. The unmatched terminal tails are not independently qualified. These conservative failure times depend on trial size and are not exact localized switching-event times. Full high/mass-1 continuation remains blocked.

Across the twelve full/prefix comparisons, maximum errors are y=3.8237944e−9 m, w=1.0198148e−7 m/s, activation=1.9658029e−8, q=3.6022262e−8, and FT=9.4026708e−6 N, below the unchanged gates 1e−6 m, 1e−5 m/s, 2e−6 a/q and 1e−4 N. The largest directed brake-event disagreement is 2.799071e−8 s against 2e−6 s. The pulse brake is armed by prior positive actual motion and crosses at .230988183594 s; no velocity reset occurs. Initial zero velocity is never counted as a successful brake.

Maximum endpoint component/combined work error is 2.456967e−9 J against 1e−5 J. Eight-point Gaussian quadrature on every actual accepted Radau dense polynomial independently reevaluates power and force: maximum component error 2.546297e−13 J and impulse error 3.609077e−13 N*s, against 1e−5 J and 1e−7 N*s. The first 1 ms history-Hermite approximation failed high-case impulse at 2.427873e−6 N*s; its receipt remains preserved. No accuracy gate, constitutive assumption, gain or velocity-root iteration budget changed to turn a failure into a pass.

The audit receipt has 15 passing checks: twelve case comparisons/balances, two one-sided descending-mode calculations and the weight-command motion observation. The JS source/model test has eight passing checks; the browser has ten. Frozen native curve values/slopes match with maximum errors 9.603429e−15 / 6.625811e−13 against 2e−12 / 2e−8. Tracking labels are numerical sampled-history observations, not a continuous-time tracking proof or stability certificate. The closed pulse tracking window [.13,.15] includes its scheduled braking transition at .15, so the preregistered invalidation rule applies; the window was not moved to claim success.

## Physical interpretation and remaining blocker

The controller law remains the declared conditional PI with excitation limits, source activation lag, explicit tendon compliance and no load damping, rest servo or height support. At the high-command upper surface, raw-excitation derivatives in integrating/frozen branches are +9.08932366/−.14187599 per second. At the mass-1 lower surface they are −.01785643/+.24899415. Both point toward the switching surface. Original adaptive replay stalls and original later RK4/slack continuation are retained; they cannot establish a classical continuation. The conservative guard rejects the crossing trial and retains the prior full state/time. Completing these two trajectories requires a separately declared, reviewed continuation/controller protocol, not more iterations or relaxed tolerances.

For the nominal descending state q=1.1, a=.5, the source static fiber slope is −366.057032727 N/m. Both source activation branches retain a numerical zero mode (~1e−13/s) and a positive real mode: 1.23647403566/s (activation) or 1.24031455134/s (deactivation). The corrected characteristic polynomial and invariant I+ki*m*w/F0 are in the protocol. No all-negative-eigenvalue acceptance or finite-PI stabilization claim is made. Finite fixed/PI perturbation plots demonstrate their own finite responses, not full asymptotic stability.

During the pulse's weight-command phase at .14 s, Fcmd=mg=4.903325 N, actual FT=4.861053893 N and w=.0147289058 m/s upward. A weight command has not stopped the load. Even exact FT=mg gives zero acceleration, not zero existing velocity. Release sets excitation to the source floor; activation lag and stored force remain. Target tension cannot directly animate position.

The separate whole-arm result remains unqualified: the 0.5 kg reduced lift/release has 15 accepted 32-point steps and real reversal 39.32529→33.52606 degrees; the isolated 256-point increment is not a self-consistent dense trajectory. Corner J≈.712631, the finer-prefix matched-time angle gap≈3.2884 degrees and full nodal/quadrature/timestep convergence remain unresolved. No skin or whole-tissue credibility claim follows from this scalar packet.

## Review deliverables and reproducibility

Open [the standalone interactive HTML](../../data/vertical-force-command-v1/review/vertical-force-lab.html) locally. It embeds the actual solver, pinned curve controls and protocol; it requires no network or external library. Mass/force controls rerun integrated dynamics, a history cursor reads accepted states, invalid requests preserve the previous display, and stopped cases expose failure/retained time separately. The last-state cursor includes fractional terminal times. Descending cases compute a companion fixed/PI trajectory from the same perturbed initialization.

Raw evidence lives in [the review directory](../../data/vertical-force-command-v1/review/): `validation.json`, `model-tests.json`, `browser-check.json`, `preservation-check.json`, `execution.json`, four histories per case, raw command logs and desktop/mobile PNGs. `pre-surface-guard/` preserves all earlier receipts including unqualified RK4 continuations. Initial module launch errors, Radau diagnostic-column overflow, interrupted/stalled replays and the failed coarse history-quadrature audit remain in the packet. The exact within-mode Jacobian prevents the diagnostic-only finite-difference overflow; it does not smooth the controller switching law.

Reproduce from the repository root with the commands in `execution.json`. Use OPENBLAS_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1. Run the Node cases and model tests, Python DOP853 and Radau `--quadrature`, `audit_vertical_force.py`, `build_vertical_force_page.py`, then `vertical_force_browser.py` with Chromium/Playwright. The final manifest binds authored sources, raw data, report, HTML, logs and renders (excluding itself). Dependencies and exact tested source SHA/tree are recorded in the execution receipt.

All 1557 files tracked at frozen design `41573e4581d2ab0b1054840ece57cd6239de69f3`, including the 51 frozen benchmark manifest bindings, remain byte-identical. The source benchmark `0e89c60d03d3d6137e1ece686ecf942b83d05645` and all original licensing/source evidence are preserved. Protected proof-count/layout files were not edited. Parent retains PR/review/merge, book/site release and Library delivery.

Source attribution: original [Millard et al. (2013), Flexing Computational Muscle](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf), [official OpenSim 4.5.2 source commit](https://github.com/opensim-org/opensim-core/tree/5bc7d3308eda742690f485ec060bfe725a349fa6), and the immutable [local source/curve manifest](../../data/millard-reference-v1/upstream/manifest.json). This implementation reuses original curve control points and reconstructs their kernels; it is not the full OpenSim runtime, an anatomical reference model or biological calibration.
