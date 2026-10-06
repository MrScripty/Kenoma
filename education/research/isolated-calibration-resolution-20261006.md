# Frozen isolated calibration diagnostic

This research branch starts at merged main `596df78f5cb652b4ac70917a82d8aa908b617056`, tree `8fb39d42575dc5593869315e46e80a64e828d7e3`. It adds a bounded diagnostic only. It does not alter the accepted book, browser operator, release candidate, historical audit bytes, constitutive laws, anatomy, material constants, fitted forces or deployment.

## Frozen experiment contract

The input manifest binds the three original fully activated fixed-end calibration poses and their existing authored atlas-derived P2 meshes, fibres, embedded sheets, reference-model targets and fitted stress scales. Distal/proximal cap membership remains explicit. Coordinates and all physical parameters stay fixed; no optimizer, force rematching, continuation, contact or time stepping is run. Existing local anatomy is used without downloads.

At each frozen pose, independently assemble the body energy gradient at 32, 256 and 2,048 positive points per element using the existing equations. Add the unchanged nodal sheet gradient. Compare the original 45 free modal coordinates with all 1,485 free nodal components. A twice-orthogonalized Euclidean projection onto normalized modal directions separates retained and omitted force directions without relying on arbitrary modal scaling. Its squared-norm fraction is a declared discrete force metric; it is not displacement error, continuum convergence, mixed stability or an enriched equilibrium solve.

Matched affine and rigid-motion controls, finite differences of the actual compressed-state potential and full nodal energy, exact dyadic P2 orientation signs, source hash checks and damaged-input rejection address specific numerical explanations. Constitutive components are independently evaluated in Pa and assembled in N. Force components may cancel and their norms do not establish physical causation.

The unchanged physical stationarity gate is **0.0001 N**. The historical **52–64 N** residuals are full free nodal residuals at these isolated original calibration poses. The historical **0.0173852 N** finer-quadrature residual belongs to a different coupled dense state at 0.10 s; it is preserved as a separately labeled contrast, not an isolated-fixture result.

## Reproduction

Commit the manifest, diagnostic helpers, runner and tests before running the diagnostic. The runner requires tracked source files and refuses changed inputs or an existing completed result. It writes only to `review/isolated-calibration-resolution-20261006/`.

```sh
cd education
node --test tests/isolated_calibration_diagnostic.test.mjs \
  tests/anatomical_compression_quadrature.test.mjs \
  tests/anatomical_integration_refinement.test.mjs \
  tests/anatomical_bernstein_orientation.test.mjs \
  tests/anatomical-material.test.mjs tests/anatomical-element.test.mjs
node --max-old-space-size=6144 --expose-gc tools/run-isolated-calibration-diagnostic.mjs
node tools/verify-isolated-calibration-diagnostic.mjs
```

## Completed bounded result

Qualified diagnostic source: **`401c306e1564be5dc82427193c159d1452f81787`**, directly parented by the frozen main commit above. The nine evaluations completed on Node v24.19.0 on 2026-10-06, 22:49:31–22:50:05 UTC. [Full results](../review/isolated-calibration-resolution-20261006/results.json) retain the free-node sets, normalized retained/omitted vectors, exact parameters, energies, derivatives and all input/implementation hashes. [Execution log](../review/isolated-calibration-resolution-20261006/run.log) preserves the run's progress and outcome. Separate files retain the complete exact orientation coefficients for [brachialis](../review/isolated-calibration-resolution-20261006/FJ1486-orientation.json), [short biceps](../review/isolated-calibration-resolution-20261006/FJ1512-orientation.json) and [long biceps](../review/isolated-calibration-resolution-20261006/FJ1478-orientation.json).

| Frozen fixture | Full nodal max, 32 points (N) | 256 points (N) | 2,048 points (N) | Free-vector L2 change, 256→2,048 | Omitted squared-force norm, 2,048 |
|---|---:|---:|---:|---:|---:|
| FJ1486 brachialis | 64.069017 | 64.067641 | 64.067543 | 0.006742% | 99.9999976% |
| FJ1512 short biceps | 51.325811 | 52.058855 | 52.114418 | 0.103364% | 99.9996469% |
| FJ1478 long biceps | 54.112782 | 54.223684 | 54.236597 | 0.058163% | 99.9998978% |

All **nine full nodal gates fail** the unchanged **0.0001 N** threshold. The three original 32-point reduced gates pass, with residuals 0.00000653447, 0.0000675401 and 0.0000942028 N. On reintegration, even their reduced residuals fail: 0.132179/1.662425/0.674166 N at 256 points and 0.143510/1.842602/0.739004 N at 2,048. The 256-point full maxima reproduce the historical audit exactly in this run. There is no new equilibrium or force match.

**The dominant discrete discrepancy is in displacement directions omitted by the current free basis.** The original 32-point poses already have large gradients in those directions despite their small reduced residuals. Normalization prevents small modal amplitudes from creating an apparent near-equilibrium; the decomposition is invariant to column rescaling. Refinement from 256 to 2,048 points changes the maximum free vector component by at most 0.007109/0.088846/0.046692 N respectively, while the full nodal residuals remain tens of N. Quadrature matters at the stringent force gate, but this comparison does not support quadrature error as an explanation that eliminates the large full nodal residual. No quadrature convergence or spatial convergence is established.

## Orientation, local compression and evaluation controls

All **756/756** stored P2 elements have strictly positive exact dyadic Bernstein coefficients for both reference and current Jacobian determinants. This excludes element inversion of these particular stored interpolants. It does not establish global injectivity, anatomical fidelity or a lower bound near incompressibility for J. Worst queried corners remain severely compressed while total volume has increased:

| Fixture | Minimum corner J | Global current/reference volume | Reference volume sampled with J<0.9, 2,048 points | Corner witness (element, corner, node; all free nodes) |
|---|---:|---:|---:|---|
| FJ1486 | 0.559236 | 1.047812 | 10.793993% | 191, 2, 90 |
| FJ1512 | 0.615812 | 1.023817 | 18.094259% | 209, 1, 93 |
| FJ1478 | 0.609997 | 1.027956 | 20.883702% | 203, 2, 92 |

The J<0.9 measure is a positive-quadrature diagnostic, not an exact compressed-volume measure. Coordinates, cap membership, activation and materials were never changed. The compression witnesses store full F, fibre direction, reference/current positions, fibre stretch and stress components in SI units.

All **25 focused tests pass**, including matched affine volume/energy/force invariance across all three quadratures, full gradient covariance under a rigid rotation and translation, independent component-energy derivatives, actual sheet energy derivatives and damaged-byte/changed-gate rejection. Runtime controls reproduce the original energy-gradient projection within **9.28×10⁻¹¹ N**, hold cap displacement/free-mode leakage below **10⁻¹² m / dimensionless**, and recover each historical 256-point full residual with zero recorded difference. Independently assembled component sums differ from the actual total gradient by at most **8.53×10⁻¹³ N**. Two full nodal energy perturbation sizes give at most **2.44×10⁻⁶ N** error. The compressed-corner Piola-energy derivatives give at most **0.004989 Pa** absolute error and **4.53×10⁻⁹** relative maximum error. These controls do not reveal a force-assembly, constitutive-derivative, orientation-sign or embedded-sheet evaluation error large enough to account for the tens-of-N discrepancy. They do not prove the constitutive law physically valid or exclude all implementation errors.

A [separate verification receipt](../review/isolated-calibration-resolution-20261006/verification.json) checks all 19 input/implementation byte identities against both the working files and qualified source commit, freshly recomputes all 756 exact orientation certificates, and independently checks saved free-vector norms, projected modal residuals, orthogonality, quadrature deltas and physical gate outcomes. Four damaged-result controls are rejected: a false equilibrium pass, a changed force gate, altered omitted force and an incorrect qualified source identity. This arithmetic/orientation replay is distinct from solving equilibrium or establishing numerical convergence.

At 256 points, the matrix contribution's free-force L2 norm is only 0.460/0.669/0.747 N. Bulk, passive fibre and active terms have norms 169–350 N, with additional biceps sheet norms 95.927 and 112.007 N; they interact and cancel. At each largest total free component, brachialis is primarily active (+58.079 N) plus bulk (+5.974 N), while short and long biceps have large passive-fibre terms (−41.610 and −72.791 N) alongside bulk (−10.980 and −15.886 N) and partially opposing active terms (+2.824 and +34.497 N). No single component norm establishes the cause of compression. At the compressed corner witnesses, bulk mean Cauchy stresses are −1.039248/−0.787274/−0.810333 MPa, and active mean stresses are +1.219678/+0.431577/+0.617086 MPa. Passive fibre stress is zero at these compressed fibre stretches; the isochoric matrix's mean stress is roundoff zero. These are evaluations of the unchanged authored law, not measured pressure or hydrostatic equilibrium.

## Remaining gate and scope

Before any force rematching, the next numerical experiment must admit genuinely new displacement directions under the same cap constraints and independently test full nodal stationarity, local J, tangent behavior and quadrature sensitivity. This diagnostic neither performs that solve nor establishes that enrichment alone will cure compression. Authored geometry, fibre architecture, load transfer and the constitutive assumptions still need separate investigation. Stress scales remain fitted to a reference model, and source-specific experimental conditions and measured architecture remain incomplete.

The retained **0.0173851553295 N** result is still a failed 2,048-point reintegration gate at a **different coupled dense 0.10 s state**, whose 256-point reduced residual was **0.0000900055773 N**. It is not directly interchangeable with any value in the isolated table. [Its original source evidence](../data/anatomical-arm-v1/audit/anatomical-further-integration.json) is unchanged and hash-bound by the manifest.

No force tuning, constitutive change, new anatomy, enriched equilibrium solve, physiological calibration, anatomical capstone completion, unrestricted stability, global injectivity or converged solution is claimed. The accepted book and release paths remain untouched. This branch has no PR or deployment.
