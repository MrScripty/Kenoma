# Fixed-field pressure projection: standalone proof guide

Open `pressure-projection-lab.html` from this directory, or serve `education/` and visit `/standalone/pressure-projection-lab.html`. The HTML is self-contained and requires no book build, WebGL, network assets, or scientific dataset. This is a numerical-approximation lesson, not a deforming-body equilibrium or incompressibility simulation. No production law or publication registration is changed.

## A transparent finite example

There are four prescribed real samples `g=(g₁,g₂,g₃,g₄)`, positive relative weights `w=(1,3,2,2)`, and one positive constant algebraic scale `K`. All values and energies in the lab are normalized; weights are not physical reference volumes and the readouts are not pressure measurements or joules. Field edits prescribe another fixed case. Only the pressure space changes during refinement.

The three spaces are nested:

- `Q₁`: all four entries share one value.
- `Q₂`: entries 1–2 share one value and entries 3–4 share another.
- `Q₄`: each entry is independent, so the entire sample vector is represented.

For each selected group `G`, define

\[
(Pg)_i = \frac{\sum_{j\in G} w_j g_j}{\sum_{j\in G}w_j}\quad(i\in G),
\qquad r=g-Pg.
\]

This specifies the actual operator used by the page. It is linear for fixed groups and weights, and its values lie in the corresponding group-constant subspace. Each group has `Σwⱼrⱼ=0`; consequently `⟨q,r⟩_W=0` for every group-constant `q∈Q`. Reprojecting a group-constant vector returns that vector. These calculations explain the exact projector obligations. This guide does not add a new Lean instantiation or prove JavaScript refinement of real arithmetic.

The page independently evaluates

\[
E_{full}=\frac K2\sum_i w_i g_i^2,\quad
E_{cond}=\frac K2\sum_i w_i(Pg)_i^2,\quad
E_{res}=\frac K2\sum_i w_i r_i^2.
\]

The gap card uses `Efull−Econd`; the residual calculation uses the actual `r` values. Their difference is shown as a browser arithmetic diagnostic. The table also displays `p*=KPg` and evaluates `⟨p*,g⟩_W−‖p*‖²_W/(2K)` directly. It is an algebraic mixed variable, not an anatomical pressure measurement.

## Exact default reference

For `g=(-3/4,1/4,-1/4,3/4)` and `K=8`, `Σwᵢgᵢ²=2`, so `Efull=8` at every level.

| Space | Exact `Pg` | Exact `r` | `Econd` | Gap `Efull−Econd = Eres` |
|---|---|---|---:|---:|
| One shared value | `(1/8,1/8,1/8,1/8)` | `(-7/8,1/8,-3/8,5/8)` | `1/2` | `15/2` |
| Two pair values | `(0,0,1/4,1/4)` | `(-3/4,1/4,-1/2,1/2)` | `1` | `7` |
| Four sample values | `g` | `(0,0,0,0)` | `8` | `0` |

Refinement first recovers the weighted pair means, then the variation within each pair. A field already constant within pairs is recovered at `Q₂`; a constant field is recovered at `Q₁`. More degrees of freedom do not change an already represented field. The positive `K` control scales every energy and `p*` together; it does not alter `g`, `Pg`, or `r`.

## Connection to the 27 Lean statements

All names below belong to `KenomaMixedVolume` in the unchanged [MixedLogVolume.lean](../proofs/MixedLogVolume.lean). The lab is separate from the main proof-card registrations.

| Role in this lesson | Exact declarations |
|---|---|
| Weighted bilinearity and symmetry | `inner_comm`, `inner_add_right`, `inner_add_left`, `inner_sub_right`, `inner_sub_left`, `inner_smul_right`, `inner_smul_left` |
| Positive-definite squared weighted norm and expansions | `normSq_nonneg`, `normSq_eq_zero_iff`, `normSq_sub`, `normSq_smul` |
| Exact projector algebra | `project_eq_self_iff`, `project_idempotent`, `inner_project`, `project_self_adjoint` |
| Admissible unique maximizing pressure vector and attained energy | `optimizer_mem`, `square_completion`, `optimizer_value`, `objective_le_condensed`, `value_eq_iff_optimizer`, `unique_maximizer` |
| Energy decomposition, nonnegativity and zero-gap representation | `pythagoras`, `pointwise_minus_condensed`, `condensed_nonneg`, `gap_nonneg`, `gap_zero_iff_represented` |
| Refinement at the same state and metric | `nested_energy_monotone` |

The foundation retains Lean 4.19.0 and mathlib commit `c44e0c8ee63ca166450922a373c7409c5d26b00b`. The supplied independent qualification is [hosted run 37461515558](https://github.com/MrScripty/Kenoma/actions/runs/37461515558), artifact `11413941584`, at checker successor `1828dfbc1f8441137c962ae47a1db31bac376a76`. That is a kernel qualification of the exact proof module and checker, not a certification of this new browser lab. The original proof/evidence and qualified checker remain frozen.

## Interpretation and placement proposed for review

`g` remains abstract in Lean. Calling the authored entries “log-volume samples” does not establish a continuum deformation: an actual `gᵢ=log Jᵢ` interpretation needs positive `Jᵢ`, declared quadrature and justified sampling. A local log-volume penalty also differs from the existing tissue block's `(J−1)²` law. This lab selects no new law and changes neither implementation.

The Lean result assumes an exact linear projector in the chosen positive metric. It establishes uniqueness of the sampled pressure **vector**; arbitrary coefficient uniqueness also requires injective basis evaluation. The toy's group coefficients are independent by construction, but this says nothing about another pressure basis. The energy ordering holds at the **same** field, weights and `K`; it is not re-equilibrated stability, an inf-sup certificate, incompressibility, or a positive Hessian gap after nonlinear composition. No solver, continuum, floating-point, muscle, or anatomical validity guarantee is claimed.

Proposed curriculum position: a short numerical-approximation interlude after introducing a local volumetric penalty and weighted sampling, immediately before pressure-space/displacement-resolution diagnostics and anatomical coupling. It complements the progressive physical-property labs without replacing their kinematics, bulk/shear, serial, axisymmetric, or SLS lessons. No chapter order, main book, PR 8, SLS, serial or axisymmetric registration is edited; parent review owns placement.

## Reproduce the independent lab checks

```bash
python3 education/standalone/pressure-projection-lab-check.py
```

The checker compares the actual browser model against independent rational closed-form projections, tests real controls and rollback, holds `g` fixed across refinement, and checks desktop/mobile, print and no-JavaScript behavior. It records browser version, exact source hashes, screenshots and a source-bound receipt under `education/.tools/pressure-projection-lab-review/`. These sampled implementation checks remain distinct from the universal exact Lean algebra. No site is released.
