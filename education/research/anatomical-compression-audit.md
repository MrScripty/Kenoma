# Frozen-pose anatomical compression and integration audit

Base accepted implementation: `e3f546712bceee543993f798b13da97efc88d849`. The source-bound primary lift/release remains a 32-point reduced-model result. This audit continues the next numerical gap without changing its material law, saved coordinates, contact recipes, thresholds or fitted stress scales.

`tools/anatomical-compression-audit.mjs` independently assembles the original ten-node P2 element body potentials and projects their nodal gradients into the same Galerkin modes. All seven heads at all 16 saved poses (held plus 15 steps) are checked with 4/32 integration. The held pose, first load, most compressed load, release peak and final release also use positive 256-point integration and element-corner determinant queries. Independent 32-point energy agrees within 4.09e-14 J; projected gradients agree within 1.30e-11 N. These agreement measurements validate this diagnostic against the existing body operator, not global mesh convergence.

| Saved event | Time (s) | Minimum J, 32 points | Minimum J, 256 points | Minimum corner J | Frozen total reduced residual, 256 points (N) |
|---|---:|---:|---:|---:|---:|
| Held | 0.00 | 0.999658 | 0.999654 | 0.999641 | 0.00007891 |
| First load | 0.01 | 0.864437 | 0.852068 | 0.839337 | 0.032883 |
| Most compressed load | 0.10 | 0.737540 | 0.725274 | 0.712345 | 0.144508 |
| Release peak | 0.34 | 0.966748 | 0.964519 | 0.962290 | 0.004916 |
| Final release | 0.43 | 0.977443 | 0.976029 | 0.974306 | 0.003137 |

The force gate remains **0.0001 N**. All four selected dynamic states fail that gate if their body integration is changed to 256 points while coordinates remain frozen; the held state passes. This exposes integration sensitivity and additional sampled local compression. It does not invalidate the recorded acceptance under its declared 32-point potential, establish a converged 256-point equilibrium, or prove positivity between samples.

At the most compressed pose, halving/doubling the authored 1 MPa bulk modulus at fixed coordinates gives total reduced residuals of 14.3162/28.6325 N. The same geometric J values remain unchanged. This is an unbalanced parameter perturbation, not a recalibrated material, a new accepted state or an estimate of how a re-equilibrated arm compresses. Tendon/contact, joint inertia, gravity, end-stop and damping terms remain those of the original incremental objective.

## Reproduce and review

From `education/`:

```sh
node --test tests/anatomical_compression_quadrature.test.mjs
node tools/anatomical-compression-audit.mjs
```

The four tests check nested positive weights/reference measure, affine energy and independent nodal energy differences, exact fixed-geometry bulk decomposition, and the actual compressed atlas pose's energy/gradient/determinant. `data/anatomical-arm-v1/audit/anatomical-compression-sensitivity.json` binds the executed auditor and base inputs by SHA-256. The operator and execution logs are preserved under `review/anatomical-compression/`.

## Re-equilibrated same-old-state comparison

`tools/anatomical-dense-step.mjs` re-solves just the 0.07–0.10 s loading increment with 256 positive integration points per P2 element. The exact 32-point old coordinates, velocity, activation, mass and contact recipe are retained. The old target is a nonlinear starting guess. `tools/anatomical-dense-quadrature.mjs` builds the denser body operator in tools; the original viewer/operator files and source-bound lift/release stay byte-identical. Displacement modes, material parameters, Newton/Armijo algorithm, contact law, force tolerance and finite geometry gates are unchanged. Body integration is frozen throughout; contact witnesses refine only between Newton solves.

The solve takes 15 accepted Newton iterations across two frozen contact rules. Its dense reduced residual falls from the original target's 0.144508 N to **0.0000900553 N**. A no-optimizer replay independently assembles full P2 body gradients, projects them and replaces the modal body forces in the total incremental gradient; its residual is **0.0000900553 N**, below the original **0.0001 N** gate. Every boundary triangle and tendon path participates in the same finite gates: zero transverse surface crossings, zero path violations and zero sampled contact penetrations.

The new joint angle differs by **0.001299 degrees**, and the maximum reduced-coordinate change is **0.12457 mm**. Minimum sampled/corner J are **0.725476/0.712631**. The short biceps head's integrated global volume ratio is **0.998864**, but **1.71534%** of its reference volume has sampled J below 0.9. Local compression persists. These quantities are not global determinant bounds or nodal displacement-error estimates.

```sh
node --test tests/anatomical_dense_quadrature.test.mjs
# Optional reproduction of the nonlinear experiment (several minutes):
node --max-old-space-size=8192 tools/anatomical-dense-step.mjs
# Fresh replay of the stored result, with no optimizer:
node --max-old-space-size=8192 tools/verify-anatomical-dense-step.mjs
```

The additional tests compare dense modal assembly with independent full P2 energy/gradients and check energy directional differences, gradient directional differences and Hessian symmetry at actual compressed coordinates. Source-bound execution, old/target/new coordinates, contact recipes, iteration trace and solver receipt are in `audit/anatomical-dense-step.json`; the independent replay is in `audit/anatomical-dense-step-recheck.json`. CI replays the stored experiment rather than rerunning the nonlinear solve.

## Remaining acceptance work

A self-consistent higher-quadrature trajectory, further integration refinement, re-equilibrated bulk sensitivity and enriched or full nodal convergence remain open. The new increment starts from a 32-point old state; it does not replace the primary trajectory. These body nodal gradients are not a full nodal force-balance audit: attachment/contact forces have not been assembled into an enriched solve. Corner and interior determinant queries remain finite checks. Compression, the interrupted release's **3.2884-degree** timestep difference, source articulation gaps, omitted finite tendon radius, coplanar cases and continuous-motion collision limits are explicit. No physiological, medical or numerical convergence claim is added.
