# Local volume preservation: a research extension for the mechanics book

Proposal, 2026-10-07. Numerical fields, laws, parameters and diagnostic results remain frozen at `19009142398ba6c0b7665fedb35e5398207eadb6`. This document adds no model, optimizer, refit, compiled theorem or book chapter. Owner-relayed independent review on 2026-10-07 ACKs its source/hash/arithmetic/parameter provenance, with the force-integration limits below. That ACK does not turn the prior geometry run's agent-owned full-raw/55-additional-certificate checks into independently replayed evidence; the [original review boundary](isolated-collapse-diagnostic-outcome-20261007.md) remains explicit.

## The book gap and a useful order

The current main book at `596df78f5cb652b4ac70917a82d8aa908b617056` is byte-identical, under `education/book/`, to this proposal's diagnostic base. Its order is in [book.json](../book/book.json). Extend the following progression only after separate review:

| Existing lesson | Proposed bridge | Preserved boundary |
|---|---|---|
| [Deformation properties](../book/chapters/09a-properties.md) | Distinguish volume measurement, imposed `J=1`, and a volume penalty | Prescribed geometry is not equilibrium |
| [Confinement](../book/chapters/09b-material-response.md) | Compare free sides and restrained sides in a homogeneous specimen | Its `(J−1)²` law stays unchanged |
| [Serial specimen](../book/chapters/09d-serial-specimen.md) | Reuse incompressible area/length bookkeeping | Two separate homogeneous blocks and a spacer; not a continuous muscle |
| [Spatial continuum](../book/chapters/10a-spatial-continuum.md) | Separate integration, approximation and solve errors | Existing small-strain compressible FEM stays unchanged |
| [Pressure projection](../book/chapters/10b-pressure-projection.md) | Interpret representation loss before introducing a physical mixed problem | Same fixed vector; no deformation or equilibrium claim |
| [Coverage](../book/chapters/13-coverage.md) | Retain explicit local-volume and full-force qualification gaps | No anatomical completion claim |

The separately accepted passive follow-on at `68393b1c16e626a51cb3d1fec7a44b99f59d04e6` is not included or revised here. It could later supply a connected passive specimen; this proposal does not promote any research apparatus to accepted curriculum.

## Four verified primary references

**Blemker, Pinsky and Delp (2005)**, *A 3D model of muscle reveals the causes of nonuniform strains in the biceps brachii*, DOI **10.1016/j.jbiomech.2004.04.009**. §2.1, Eq.9, p.660 uses `K/2 (ln J)²`; Table2 specifies muscle `K=10⁷ Pa`. §§2.2–2.4 describe geometry, boundary conditions and comparisons with human strains. This establishes an original muscle-model precedent for the penalty family, not transferability of its parameters, strain predictions or numerical resolution to Kenoma. [Author-hosted original PDF](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf).

**Pappas et al. (2002)**, *Nonuniform shortening in the biceps brachii during elbow flexion*, DOI **10.1152/japplphysiol.00843.2001**. Methods and Results, pp.2382–2386, report cine phase-contrast MRI in twelve humans during low-load elbow flexion. Spatial shortening measurements support testing heterogeneous deformation rather than assuming uniform fascicle strain. They are not measurements of bulk modulus or Kenoma's maximum isometric stress. [Author-hosted original PDF](https://nmbl.stanford.edu/publications/pdf/Pappas2002.pdf).

**Wakeling et al. (2020)**, published as *The Energy of Muscle Contraction. I. Tissue Force and Deformation During Fixed-End Contractions*, DOI **10.3389/fphys.2020.00813**. The inspected, versioned original manuscript has the earlier subtitle *during isometric contractions*: §§3.1.1–3.1.2, 3.2 and AppendixA distinguish a displacement/pressure/dilation FEM formulation, assigned muscle bulk modulus `10⁶ Pa`, and MRI/DTI observations in four women. Assigned `K` and maximum stress are numerical material choices; human images provide geometry/deformation evidence. The paper connects volumetric, base-material and fibre contributions to whole-muscle behavior, without validating Kenoma's field. [Versioned manuscript](https://arxiv.org/pdf/2001.01139v1), [published article](https://doi.org/10.3389/fphys.2020.00813).

**deal.II step-44, official implementation**, v9.6.2 peeled commit **`6890ca740b6e51530ebb7ae7e4932977010ef2be`**. The introduction's “Neo-Hookean materials,” “Principle of stationary potential energy and the three-field formulation,” and “Discretization of governing equations” explain `u,p̃,J̃`, condensation and interpolation restrictions. The code's “Finite Element system” makes polynomial and quadrature orders separate inputs. Its volume energy is `κ/4 (J²−1−2 ln J)`, different from Kenoma's. It warns that its near-incompressible formulation still locks in the fully incompressible limit. This is a formulation/code reference, not a guarantee that arbitrary pressure/displacement spaces work. [Pinned introduction](https://raw.githubusercontent.com/dealii/dealii/6890ca740b6e51530ebb7ae7e4932977010ef2be/examples/step-44/doc/intro.dox), [pinned implementation](https://github.com/dealii/dealii/blob/6890ca740b6e51530ebb7ae7e4932977010ef2be/examples/step-44/step-44.cc).

All four were checked online on 2026-10-07. No cited human experiment supplies a directly measured volumetric stress–volume curve for this brachialis fixture. A justified physiological compressibility range remains missing. The observed collapse cannot decide that range.

## Keep the equations and pressure meanings explicit

For reference coordinates `X`, `F=I+∇X u`, `J=det F>0`, the existing research law has

\[
W_v(F)=\frac K2(\log J)^2,\qquad
P_v=K\log J\,F^{-T}.
\]

`W` is Pa = J/m³ of reference volume, `P` is Pa, integration weights are m³, and shape gradients are m⁻¹. Its authored `K=1 MPa`, `μ=0.001 MPa` and fitted `σ₀=3.599330734 MPa` are not measured human tissue properties. That stress came from a 45-mode, 32-point fit to the Arm26 BRA **model parameter** `987.26 N`; retain it as historical calibration evidence, not physiology. [Frozen provenance and diagnostic](isolated-collapse-diagnostic-outcome-20261007.md).

An algebraically equivalent full-pressure representation of the **same finite penalty** is

\[
\Pi(u,q)=\int_{\Omega_0}\left[W_{\rm other}(F)
+q\log J-\frac{q^2}{2K}\right]dV-\mathcal W_{\rm ext},
\quad q=K\log J.
\]

Here `q` is conjugate to log-volume: `P_v=q F⁻ᵀ`, volumetric Kirchhoff stress is `q I`, and Cauchy stress is `(q/J)I`. A convention taking compression-positive hydrostatic pressure gives `−q/J`. The tutorial's `p̃`, conjugate to `J−J̃`, is a different variable. Do not interchange them.

Restricting sampled `q` to a subspace changes the condensed penalty to `K/2 ‖P_Q g‖²_W`, with `g=log J`. The [existing 27 proofs](../proofs/MixedLogVolume.lean) establish the missing energy `K/2 ‖g−P_Qg‖²_W` at fixed samples. Thus fewer pressure modes can remove volume resistance; a mixed rewrite alone is not a remedy for collapse. Positive sampled `J` and positive weights do not certify determinant positivity between samples.

Exact incompressibility instead imposes local `J=1`, with an independent multiplier, for example `∫[W_iso+p(J−1)]dV−work`. In a finite pressure space its equation is only `∫r_h(J−1)dV=0` for all represented tests `r_h`. Equal-weight samples `J=(1−ε,1+ε)`, `0<ε<1`, satisfy a constant test despite local compression/dilation. Local constraints, weak constraints and finite penalties are different assumptions. A saddle problem is not joint minimization in displacement and pressure; space compatibility, conditioning and locking require their own evidence.

## Progressive laboratory proposal

1. **Affine volume bookkeeping.** Start with prescribed `F=diag(λ,b,b)`, `λ,b>0`: `J=λb²`, current area `A=A₀b²`. A volume-preserving toggle sets `b=λ⁻¹/²`; free transverse stretch remains an input otherwise. Show `J`, area and length before any force. Reuse the existing kinematic proof; no equilibrium label.
2. **One homogeneous material comparison.** In a separate future fixture, explicitly declare either a finite penalty or `J=1`, passive material, supports and side tractions. Derive and verify transverse equilibrium and reactions. Preserve both existing book laws; do not blend `(J−1)²` and `(log J)²`. Parameters remain authored. Activation and anatomical names are unnecessary for this first material test.
3. **Fixed-sample representation.** Reuse the accepted projection controls and proofs; add clearly labelled positive prescribed `J_i`, displaying `log J`, projection and unresolved gap. Include the weak-constraint counterexample. This remains algebra on fixed data, not a mixed FEM solve.
4. **Spatial resolution.** Only under a separately reviewed protocol, compare a simple passive block with declared mixed spaces, loads and integration rules; test affine patches, a manufactured solution, pressure modes and mesh refinement. A cap-adjacent passive fixture can then isolate boundary localization. Geometry guards and full force checks remain independent. This would be a new laboratory, not an anatomical capstone upgrade.

## What evidence should decide the next experiment?

The [frozen diagnostic](../review/isolated-collapse-diagnostic-20261007/diagnostic-summary.json) finds actual corner `J≈1.301×10⁻⁶` at element247 beside the proximal fixed cap, versus `0.09139` at its nearest original point. The corner's active stress is zero; local matrix/volume resistance opposes collapse while broader relaxation permits descent. Incident-patch refinement changes the final full-free gradient by up to `0.61577 N`, despite energy differences near `10⁻⁶ J`. Successive refined full-free maxima still differ by `0.14279974 N`, over 1,400 unchanged force gates; even stabilization of the deepest corner contribution cannot qualify the rest of the integral. Omitted force outside the fixed 46-space reaches `140.50001 N` in L2, but this is an unconverged saved-field diagnostic, not a converged equilibrium-error estimate. The in-space residual also remains large. These observations demonstrate unresolved integration and representation; they neither establish a resolved equilibrium nor identify a replacement material. No unit-error or external-load explanation was verified; assigning a single constitutive cause remains a hypothesis.

**First propose fixed-field integration qualification:** keep the exact control and last-valid nodal fields, all parameters and supports. Declare a bounded rule family, component-wise full nodal gradients/reactions and saved-direction derivatives, actual determinant certificates, total call ceiling and refusal rule. Retain every full component vector, rule/weight inventory and directional derivative for independent replay. Refine the entire incident patch, including all remaining coarse regions, and check the rest of the body. Require successive vector differences and an independent integration strategy to satisfy a preregistered force budget stricter than the unchanged `10⁻⁴ N` gate **and a directional-derivative budget in joules**, separately for components and totals. For a fixed saved nodal increment `δu`, `|Δg·δu|≤‖Δg‖∞‖δu‖₁` gives a consistent force-to-work budget; directly check the derivative as well. No threshold is assigned by this proposal and no run is authorized here. Stable energy or scalar maxima alone are insufficient.

**Then review displacement resolution:** with qualified integration, inspect full free residual and its component outside each declared nested displacement space at the same saved fields. If representation remains dominant, propose one bounded enrichment experiment with the unchanged law and geometry safeguards. Then assess full and projected stationarity, reactions, local `J` and a consistent tangent in the declared sequence. Restricted stationarity or matched target force alone cannot qualify it. More arbitrary modes and smaller line-search fractions are not qualification evidence.

**Before changing constitutive assumptions:** require an identified empirical compressibility target and uncertainty, reviewed boundary/fibre assumptions, a consistent energy–stress–tangent derivation, and passive patch/manufactured/refinement evidence for the proposed spaces. Finite-dimensional coupling rank is necessary but not an inf-sup proof. Weak mean-volume balance does not bound local `J`. No arbitrary bulk increase or selected pressure formulation is justified by the current evidence. Compare model choices under frozen loads and geometry before any refit; only then reassess the historical stress calibration against independent deformation and force observables. No anatomical completion follows from this sequence.

## Limited next Lean statements

Reuse `isochoric_sqrt_construction` and the 27 projection declarations. Worth proposing, but **not proved or compiled here**:

- For a finite set of positive weights and `K>0`, `K/2 Σw_i g_i²≤E` implies `|g_i|≤√(2E/(K w_i))`. This explains why tiny weights permit large sampled log-volume variation; no continuum coercivity conclusion.
- For `0<ε<1`, the two positive determinant samples above have zero weighted mean `J−1` but neither equals one. This is a finite counterexample to local preservation from one mean constraint.
- With nonnegative Bernstein basis values and positive reference coefficients, a rational determinant represented by those coefficient ratios lies between their minimum and maximum. Attainment at a pure corner needs an additional endpoint identity. This could formalize the diagnostic's exact finite certificate, without certifying mesh injectivity or floating-point code.

Equilibrium existence, uniqueness, mixed inf-sup stability, optimizer convergence, physiology and anatomical completion remain outside these proposed statements. The complete source typography and actual-point diagram gates would still apply to any later book inclusion; this Markdown research proposal does not claim a new book/PDF/browser qualification.
