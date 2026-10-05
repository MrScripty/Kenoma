# Frozen volume-penalty comparison

The saved, freshly replayed 256-point coarse trajectory has minimum corner determinant `0.7120247523019865` at 0.07 s. Its accepted reduced residual does not establish full nodal equilibrium or credible local compression. This diagnostic compares the two existing volume penalties at that determinant without solving or changing a state.

The implementation sources are [`muscleMaterial`](../web/anatomical-material.mjs) and [`blockEnergy` / `blockStress`](../web/tissue.mjs). Their declared volume densities are respectively

\[
W_{\log}(J)=\frac K2(\ln J)^2,\qquad W_{\mathrm{quad}}(J)=\frac K2(J-1)^2.
\]

For energy per reference volume, the volumetric Cauchy mean is \(dW/dJ\), so compression-positive restoring pressures are \(-K\ln J/J\) and \(K(1-J)\). Both have tangent bulk modulus \(K\) at the reference state; their finite responses differ. These are derivations of the repository's authored fixture laws, not new measured tissue parameters or attribution of these exact laws to a biological study.

The comparison uses pure isotropic dilation \(F=J^{1/3}I\), zero activation and six fixed determinants from 0.6 to 1. For compressed dilation the arm's isochoric matrix and tension-only passive fibre energies vanish within roundoff. Only this diagnostic supplies the same authored \(K=10^6\) Pa and \(\mu=1000\) Pa to both existing functions; neither implementation's defaults change. The independent formula checks actual Cauchy stresses to \(10^{-7}\) Pa, and centered energy differences at two fixed increments check pressures to \(10^{-3}\) Pa. Maximum finite-difference disagreement across all six rows is `2.8140726499259472e-5` Pa.

At the saved corner determinant:

| Quantity | Logarithmic arm penalty | Quadratic Lab 5 penalty |
| --- | ---: | ---: |
| Volume energy density (J/m³) | 57678.5491 | 41464.8716 |
| Compression-positive bulk pressure (Pa) | 477009.5458 | 287975.2477 |

The logarithmic/quadratic energy ratio is `1.391022010678341`; the pressure ratio is `1.6564255075014587`. Therefore replacing the logarithmic penalty with the quadratic penalty at the same \(K,J\) reduces bulk resistance in this isolated comparison. This result cannot identify the cause of the arm's volume loss, which still requires spatial mode/full-force, quadrature and timestep diagnosis. Actual anisotropic arm points also carry matrix, fibre, active and constraint contributions that are absent from this pure-dilation fixture.

Run `node tools/compare-volume-penalties.mjs <new-output-path>` from `education/`. The tool refuses to overwrite an existing receipt and never invokes the optimizer. Raw output and the source-bound six-row receipt are preserved in `data/compression-lab-v1/review/volume-penalty-comparison/`. There is no constitutive assumption, book equation, Lean statement, parameter calibration, tolerance, iteration cap, state/time or skin change in this milestone.
