# Conserved two-state operator qualification protocol

Declared before execution on 2026-10-06, after original-table audit commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`. This is a parameter-free mathematical implementation check of the [held-N derivation](source-two-state-implicit-derivation.md), using abstract synthetic rate vectors. It does not evolve a loading/release history, choose physiological parameters, reproduce author code, couple series elements or revise production mechanics, book equations or Lean statements. Earlier evidence is frozen.

The [original pixel audit](original-plos-table-visual-audit.md) closes table association for publisher PDF SHA256 `20f16f9890d1ff1d65cb8e75d38f24e7c2b5a73779052825faa36f45a78531cf`. Publication medians and an individual-fit code fixture remain separate. The [convention memo](article-code-convention-decision.md) and [calibration audit](calibration-source-reconciliation.md) record the remaining choices and unknown SI force/area chain. None is silently supplied here.

## Mathematical system

For bin masses pi, B=sum(pi), held capacity N in [0,1], free heads M=1-B and free sites q=N-B:

```
pi' = Fi (1-B)(N-B) - gi pi.
```

Fi are nonnegative integrated attachment rates, gi positive detachment rates. The independently implemented closed equilibrium and backward-Euler operator are in `education/tools/source_two_state_operator.py`. Full RHS residuals are accumulated independently from reconstructed bin populations; the reduced quadratic alone is insufficient. The operator performs no time advancement. A caller may advance state/time only after it returns an admitted candidate.

Input and candidate checks require finite matching vectors, nonnegative individual bin masses, and **strict sum(pi)<=N<=1**. Declining capacity below the OLD attached population is rejected before any detachment step, even if the putative new state could fit. There is no clipping, renormalization, head reset or tolerance allowance on this bound. The free-site accounting error |sum(pi)+q-N| must be <=2e-12. Full BE residual infinity norm divided by max(1,N,h sum(Fi),h max(gi)N) must be <=1e-12; record its unscaled value too. This numerical population residual is distinct from the unchanged anatomical force gate 1e-4 N. Nonfinite arithmetic is rejected.

## Independent references and fixed cases

Use mpmath at 60 decimal digits to solve the original coupled vector BE equations from the OLD state, with analytic full Jacobian, tolerance 1e-45 and maximum 20 Newton steps. No retries, changed starts, extra iterations or relaxed tolerance after failure. The reference root must itself have nonnegative bins, sum(pi)<=N, and pass its full residual gate. Compare candidate and reference states with maximum absolute error <=2e-12. A solver failure remains a preserved reference failure.

Two abstract rate vectors are declared, with units s^-1 solely to make h seconds consistent:

1. Fi=(.7,1.3,4.2), gi=(.05,2,100).
2. Seven geometrically spaced Fi from .001 to100 and gi from .02 to10000.

For each use N=(1e-6,.2,1), initial B/N=(0,.3,1), and h=(1e-12,.001,.1,1): **72 single-step cases**. At saturation put all old mass in the first bin. At .3 capacity distribute by weights1..nbins normalized. Store all original inputs, computed/reference states and raw residuals, including any failures.

Also check zero attachment, N=0, sparse mass, bin permutation, a tiny-I equilibrium, equilibrium vector residuals, the continuous Jacobian against central numerical differences, and the nearly saturated small-step cancellation witness. For that independent Jacobian check use 60-digit arithmetic, centered perturbation 1e-20 and absolute error gate 1e-25; the RHS is quadratic in populations. Reject negative individual mass, overcapacity OLD state (including a capacity-drop witness), invalid N/rates/h, nonfinite inputs, incompatible shapes and coefficient overflow. Finite rates and h do not guarantee finite h*gi, h*Fi, root coefficients or residual scaling: reject a nonfinite intermediate before admitting a candidate. These checks probe coupling, admissibility and numerical arithmetic; they do not qualify a continuous strain distribution or physiological trajectory.

## Evidence and interpretation

Write raw execution log, JSON cases and an independent audit note under `education/data/anatomical-arm-v1/review/source-two-state-operator/`. Do not overwrite existing receipts. Hash-bind protocol, implementation, source audit and resulting evidence. Preserve failures before diagnosing any implementation defect. No physiological release follows automatically from a passing operator check. A separately declared dimensionless direct-CE experiment can use it only after choosing its parameter provenance, initialization, boundary transport and normalization. A dimensional circuit additionally needs a coherent PE/SE law, series force/tangent consistency and source calibration or clearly authored sensitivity; anatomical coupling still requires complete compression/contact and matched-time spatial/timestep evidence.
