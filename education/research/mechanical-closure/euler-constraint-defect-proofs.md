# Local Euler constraint-defect algebra: Lean proof scope

This separate proof lane formalizes the mathematical identity underlying the
three archived rejected predictors. It leaves the held numerical-policy proposal
at `a522899d089d4249bf20e27b2545723b41d3f2f2` unchanged and executes no revised
policy or trajectory. The completed first-sliding matrix at
`455641c0aa9b4a9ad4b68e50fc1b6f5746180226` remains nine of twelve and unqualified.
This branch starts from the separately completed scalar-proof branch
`9547246e10269ea0c2613cc9cef848323f700ef6`; all its evidence is preserved.

The [Lean source](../../proofs/EulerConstraintDefect.lean) uses exact real
rationals for the actual lower source surface:

```
FT(s) = 100 f(s),     e(r,s) = (r−100 f(s))/100,
H(s,I) = 1/100 − [ub + (2/5)e(r,s) + I],
s = (L0−y−q/10)/(1/5),     y_dot=w, q_dot=10v,
s_dot = −5(w+v),     I_dot = (2/5) slope s_dot = −2 slope(w+v).
```

r and ub are constant parameters in these statements. The earlier approved
Filippov mixed-rate result gives I_dot=−d on the surface. With the supplied
tendon slope identified with f'(s), kt=500 f'(s) and d=.4 kt(w+v)/100,
that rate is exactly the I_dot above. These are the unchanged equations in
[the scalar engine](../../tools/run_filippov_bounded_experiment.py),
[the independent field](../../tools/vertical_force_reference.py) and the
[earlier scalar Lean proof](../../proofs/FilippovConvexWeight.lean).

For **any** function f:ℝ→ℝ and supplied real slope, Lean proves:

```
H(s+τ s_dot, I+τ (2/5) slope s_dot) − H(s,I)
  = (2/5)[f(s+τ s_dot) − f(s) − slope (τ s_dot)].
```

The arbitrary-function identity itself assumes no differentiability. Its
source-coordinate corollary substitutes the actual Euler y/q/I expressions.
The increment statement retains arbitrary finite entry H; a separate corollary
assumes exactly H(s,I)=0. Neither rewrites a floating-point entry residual to zero.
The symbolic normal rate `(2/5) slope s_dot−I_dot` is zero for the supplied rate.
Calling this the geometric directional derivative additionally requires the
external assumption that slope is the actual derivative of f at s; this packet
does **not** prove HasDerivAt, the derivative of the source kernel or its C2
regularity. It formalizes the scalar cancellation and remainder algebra.

Lean also proves the conditional bound: if the supplied pointwise inequality

```
|f(s+τ s_dot)−f(s)−slope (τ s_dot)| ≤ (M/2)(τ s_dot)^2
```

holds, then the absolute constraint increment is at most
`(M/5) τ² s_dot²`. The inequality is an explicit hypothesis, not an admitted
lemma or a verified OpenSim curvature bound. In a usual Taylor interpretation
M≥0 bounds the second derivative on the relevant interval. This packet does
not derive that interpretation from C2 assumptions. Its conditional statement
needs only the displayed inequality and exact real algebra.

For the explicit example f(s)=A s²+D s+E with supplied slope=2As+D,
the remainder is exactly Aδ², so Lean proves the exact defect
`(2/5) A τ² s_dot²`. If A>0, τ≠0, s_dot≠0 and entry H=0, the symbolic normal
rate still cancels while the Euler predictor has strictly positive H. This
exhibits a quadratic constraint defect without claiming the actual parametric
quintic tendon curve is quadratic. No concrete archived binary64 defect magnitude
is certified by these real-number theorems.

The [claim inventory](../../proofs/euler-constraint-defect-claims.json) names all
ten declarations. A fresh kernel checker uses pinned Lean 4.19.0 and mathlib
`c44e0c8ee63ca166450922a373c7409c5d26b00b`, treats warnings as errors, rejects
admissions/custom axioms/unchecked execution, and prints each declaration's real
axiom dependencies. The source and claim inventory must match the source-freeze
commit before the final compiler receipt is issued. Audit tests are receipt
negative controls; they are separate from actual compilation.

The original mechanics context remains [Millard et al., 2013](https://doi.org/10.1115/1.4023390)
and the pinned [OpenSim tendon-curve factory](https://github.com/opensim-org/opensim-core/blob/5bc7d3308eda742690f485ec060bfe725a349fa6/OpenSim/Actuators/MuscleFunctionFactory.cpp),
with its retained notices and original kernel snapshots. The Filippov tangent
selection context is [Dieci–Lopez, §2.1](https://epubs.siam.org/doi/10.1137/080724599).
[Hairer's original notes, p.4](https://www.unige.ch/~hairer/poly_geoint/week2.pdf)
state the first-integral directional-derivative criterion; this packet's Euler
defect and explicit quadratic example are independently proved algebra rather
than a quoted integrator-convergence theorem.

These local claims establish no accepted-state or internal-stage admissibility,
floating-point correctness, event localization, RK order, timestep convergence,
ODE existence/residence/stability, work/impulse validity, hidden-root exclusion,
bulk/compression behavior or anatomical-envelope credibility. They do not approve
the held policy, close either older raw-review gap, change the book proof count,
or authorize book adoption, a merge, deployment, skin or any new numerical run.
