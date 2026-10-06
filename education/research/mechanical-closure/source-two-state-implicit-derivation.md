# Held-calcium source two-state population: implicit-step derivation

New mathematical derivation, not an executed physical fixture or source-trajectory replay. No kinetic evolution, loading/release experiment or numerical parameter selection is performed here. All frozen packets remain unchanged.

The committed [original PLOS table visual audit](original-plos-table-visual-audit.md), commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`, identifies the original publisher PDF (5,532,793 bytes, SHA256 `20f16f9890d1ff1d65cb8e75d38f24e7c2b5a73779052825faa36f45a78531cf`) and preserved original Table 2/3 crops. The worker inspected the rendered pixels, and the parent independently opened both preserved table crops. This lane relies on that committed evidence rather than claiming its own pixel inspection. The two-state column, Gaussian form and detachment signs are verified; the audit separately preserves printed thermal-width and cooperative-calcium unit discrepancies. Earlier access failures remain historical evidence. Visual verification supplies no new physical experiment, SI calibration or article/code parity.

## Population convention recovered from pinned code

The [pinned implementation audit](source-code-initialization-audit.md) establishes, for the declared two-state branch with zero thick-filament on/off flux and zero forcibly detached population, M+B=1 under its discretized initial condition. At held thin-site capacity N, use bin masses pi and B=sum(pi):

```
pi' = Fi (1-B)(N-B) - gi pi,
M = 1-B,   0 <= B <= N <= 1.
```

Fi are integrated attachment rates and gi positive detachment rates in the selected strain measure. This differs from the frozen fixture's permanently held M=1. It retains separate free-head and available-site capacities; neither can be silently removed when calling the result the source branch.

## Equilibrium without a settling loop

Let I=sum(Fi/gi), q=N-B and c=1-N. Equilibrium gives pi*=Fi q(c+q)/gi and

```
I q² + (1+I c) q - N = 0,
q* = 2N / [(1+I c) + sqrt((1+I c)²+4I N)].
```

This rationalized positive root avoids cancellation. The other quadratic root is negative when I>0,N>0. The formula gives q* in [0,N], hence an admitted unique equilibrium for the held-input reduction. It supplies no cooperative-state or series-force equilibrium by itself. The force moment must be computed from the resulting distribution and selected force transformation; it is not reset to beta or unity.

## Positive backward Euler without clipping or iteration

For timestep h>0 define ai=1/(1+h gi), U=sum(ai pi_old), V=h sum(ai Fi), c=1-N, q=N-B_new. In exact arithmetic set W=N-U. Implicit equations reduce to

```
pi_new = ai [pi_old + h Fi q(c+q)],
V q² + (1+V c)q - W = 0,
q = 2W / [(1+V c) + sqrt((1+V c)²+4V W)].
```

When B_old is close to N and h is small, directly subtracting N-U loses significant digits. The algebraically equivalent, cancellation-resistant expression is

```
B_old = sum(pi_old),
W = (N-B_old) + sum([h gi/(1+h gi)] pi_old).
```

Compute the fractions directly rather than as `1-ai`; reject nonfinite products or sums. The admissible old-state gate requires independently reconstructed B_old<=N, so both contributions to W are nonnegative. The expression avoids subtracting nearly equal N and U but does not eliminate floating-point error, overflow or underflow; those remain checked conditions, not grounds for clipping.

For a valid old state, 0<=U<=B_old<=N. The denominator is positive, q>=0, and the scalar polynomial at q=N is nonnegative, so q<=N. Each pi_new is nonnegative without clipping, and **in exact arithmetic** sum(pi_new)=N-q, making M_new=1-B_new nonnegative. The V=0 limit is q=W. No nonlinear iteration is required by this algebraic operator.

The exact identity B_new=N-q is not a floating-point population receipt. Independently reconstruct `B_new=sum(pi_new)` from the candidate bin masses using the declared summation method. Before accepting a step, require finite values, every pi_new>=0, **strict B_new<=N**, M_new=1-B_new>=0 and q within [0,N]; also check the polynomial/bin-equation residuals and agreement with N-q under separately declared residual tolerances. A small residual does not waive the strict capacity gate. An independently reconstructed B_new>N, even by one representable increment, rejects the candidate. Do not replace it with N, round q or clip/renormalize the masses to make it pass. Preserve the old state/time on rejection; a documented recomputation or timestep refinement may produce a new candidate, which must pass the same gates.

This is a candidate mathematical discretization for a future independently declared experiment, **not** a verified implementation or source-trajectory replay. Floating-point state/force/work gates, remapping, series coupling, initial residuals, timestep/strain refinement and source normalization still need execution receipts. State/time must advance only after their gates pass.

Holding N is essential: a declining imposed N can fall below an already attached B, invalidating N-U>=0. The source noncooperative activation lag and occupied-site/cooperative rules therefore cannot be replaced by arbitrary capacity resets. Any varying-capacity implementation needs its own invariant-domain and input-transition checks. Force/density clipping in the inspected original code remains a separate source behavior rather than an acceptance shortcut.

The visual prerequisite is satisfied for the exact original file identified in the committed [visual audit](original-plos-table-visual-audit.md). Final-article/code parity, coherent coordinate/PE conventions and SI force/area calibration remain unresolved. This derivation changes none of those statuses and selects no human stiffness or anatomical compression law.
