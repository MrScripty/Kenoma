# What does a pressure space miss? {#fixed-field-pressure-projection}

A spatial solve uses finite samples and a finite representation. Before changing a body or solving another equilibrium, hold the samples fixed and ask which part a smaller space can represent. This interlude studies that algebraic question. It does not select a new material law.

[Open the resettable pressure-projection laboratory](standalone/pressure-projection-lab.html). It is self-contained, works without WebGL, and offers actual sample-field, pressure-space and positive-scale controls. The full [proof guide](standalone/pressure-projection-proof-guide.md) maps the exact calculation to all 27 declarations below.

<div class="projection-interactive"><iframe title="Fixed-field weighted pressure projection controls" src="standalone/pressure-projection-lab.html" loading="lazy" style="width:100%;height:1900px;border:1px solid #bdc9cb"></iframe></div>

The authored reference is g=(-3/4,1/4,-1/4,3/4), weights w=(1,3,2,2), and K=8. These are normalized numbers, not measured pressures, reference volumes or joules. Q1 uses one shared value; Q2 uses a separate value for each pair; Q4 represents every sample independently. With groups G, the weighted mean is

\[
(Pg)_i=\frac{\sum_{j\in G}w_jg_j}{\sum_{j\in G}w_j},\qquad r=g-Pg.
\]

![Three prescribed sample vectors on a shared signed scale: g, Pg and g minus Pg. This is a discrete representation diagram, without body geometry.](assets/pressure-projection.svg)

| Space | Pg | Residual r | Full energy | Condensed energy | Unresolved gap |
|:--|:--|:--|--:|--:|--:|
| One shared value | (1/8,1/8,1/8,1/8) | (-7/8,1/8,-3/8,5/8) | 8 | 1/2 | 15/2 |
| Two group values | (0,0,1/4,1/4) | (-3/4,1/4,-1/2,1/2) | 8 | 1 | 7 |
| Four sample values | g | (0,0,0,0) | 8 | 8 | 0 |

The full, condensed and residual energies are respectively K/2 times the weighted squared norms of g, Pg and r. Every group has zero weighted residual sum, so r is orthogonal to every group-constant vector. Square completion of the objective

\[
L(p;g)=\langle p,g\rangle_W-\frac{\|p\|_W^2}{2K}
\]

shows that the unique maximizing sampled pressure vector is p*=KPg. Its attained value is the condensed energy. Weighted Pythagoras gives full minus condensed energy equal to residual energy. A larger nested space increases condensed energy at the **same g, weights and K**. It does not compare bodies re-equilibrated in different spaces.

Try refinement before editing a field. Then choose the already-paired or constant preset: extra modes recover nothing when the field is already represented. Changing K scales energies and p* together, while g, Pg and r stay fixed. Invalid entries retain the last valid case; Reset restores the exact default. Numerical checks compare the actual browser model with independent rational formulas; they do not prove floating-point refinement of Lean.

## Exact assumptions and interpretation

Lean uses Fin n -> Real, including the zero-dimensional case, strictly positive diagonal weights, a real linear subspace, and a supplied exact linear projector whose residual is weighted-orthogonal to that subspace. It assumes rather than constructs a mesh projector. Energy sign and maximizing-pressure results require one positive constant K. Uniqueness concerns a sampled vector; coefficient uniqueness additionally requires injective basis evaluation. Heterogeneous pointwise moduli are outside these results.

The samples remain abstract in Lean. Interpreting g as log J requires positive sampled J, declared quadrature and justified sampling. The anatomical research law's local log-volume penalty differs from the teaching tissue block's (J-1)^2 penalty. This lesson changes neither law. A fixed-vector nonnegative energy gap does not establish a Hessian gap after nonlinear composition, equilibrium, inf-sup stability, incompressibility, convergence, contact, continuum determinant positivity or anatomy validation. Pressure-space/displacement-resolution diagnostics and anatomical coupling still need their own evidence.

The unchanged standalone guide records its original checkpoint before book registration. This integration registers those same exact statements and preserves the complete source without altering its assumptions.

## Checked finite-vector statements

{{proof:projection-inner-comm}}

{{proof:projection-inner-add-right}}

{{proof:projection-inner-add-left}}

{{proof:projection-inner-sub-right}}

{{proof:projection-inner-sub-left}}

{{proof:projection-inner-smul-right}}

{{proof:projection-inner-smul-left}}

{{proof:projection-normSq-nonneg}}

{{proof:projection-normSq-eq-zero-iff}}

{{proof:projection-normSq-sub}}

{{proof:projection-normSq-smul}}

{{proof:projection-project-eq-self-iff}}

{{proof:projection-project-idempotent}}

{{proof:projection-inner-project}}

{{proof:projection-project-self-adjoint}}

{{proof:projection-optimizer-mem}}

{{proof:projection-square-completion}}

{{proof:projection-optimizer-value}}

{{proof:projection-objective-le-condensed}}

{{proof:projection-value-eq-iff-optimizer}}

{{proof:projection-unique-maximizer}}

{{proof:projection-pythagoras}}

{{proof:projection-pointwise-minus-condensed}}

{{proof:projection-condensed-nonneg}}

{{proof:projection-gap-nonneg}}

{{proof:projection-gap-zero-iff-represented}}

{{proof:projection-nested-energy-monotone}}
