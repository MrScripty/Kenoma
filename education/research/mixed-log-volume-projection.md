# Mixed log-volume projection: bounded Lean research module

This branch adds `proofs/MixedLogVolume.lean` and a standalone checker. It does not register claims in the book, change a physical law, implement a mixed solver, or publish a lab. It starts from fetched main `041de5deed0d288f644017704d675b7f8c1b97a4`.

## Explicit model

The ambient space is `Fin n → ℝ`, including the zero-dimensional case. `Weights` supplies strictly positive real weights `wᵢ`. The declared inner product is

\[
\langle x,y\rangle_W=\sum_i w_i x_i y_i,
\qquad \|x\|_W^2=\sum_i w_i x_i^2.
\]

Lean proves symmetry, linearity through addition, subtraction and scalar multiplication, nonnegativity, and positive definiteness (`normSq x = 0 ↔ x = 0`). `normSq` denotes the squared norm directly; the proof does not introduce square roots. This is a positive diagonal quadrature metric, not a formalization of every possible dense positive-definite matrix.

`Projection W` supplies a real linear subspace `Q`, a real linear map `P`, and two proof obligations for **every** vector `g`: `P g ∈ Q` and `⟨p,g−P g⟩_W=0` for every `p∈Q`. Idempotence, weighted self-adjointness and `P g=g ↔ g∈Q` are derived. The module assumes a projector witness satisfying these obligations; it does not construct a projector from a mesh or certify a floating-point matrix. Strictly positive weights are essential for uniqueness. Uniqueness concerns the sampled pressure vector; uniqueness of basis coefficients additionally requires an injective evaluation map. A single constant scalar modulus `K>0` is required; heterogeneous pointwise moduli are outside this result.

For abstract `g` and admissible `p∈Q`, define

\[
L(p;g)=\langle p,g\rangle_W-\frac{\|p\|_W^2}{2K}.
\]

The central compiled theorem is square completion:

\[
L(p;g)=\frac K2\|P g\|_W^2-
\frac1{2K}\|p-KP g\|_W^2.
\]

It proves that the unique maximizing pressure is `p=K P g`, that the attained condensed energy is `K/2 ‖P g‖²_W`, and that every admissible pressure has objective no greater than this value. Weighted Pythagoras gives

\[
\frac K2\|g\|_W^2-\frac K2\|P g\|_W^2
=\frac K2\|(I-P)g\|_W^2\ge0.
\]

The gap vanishes exactly when `g∈Q`; condensed energy is nonnegative. For nested spaces `Q⊆R`, with the **same** weights, `K` and `g`, the condensed maximum increases monotonically. This follows by using the smaller-space optimizer as an admissible pressure in the larger space. It does not compare states re-equilibrated in different models.

## Connection to the numerical diagnostic

For a future finite quadrature diagnostic, `gᵢ=log Jᵢ` requires positive sampled `Jᵢ` and positive reference-volume weights. The local anatomical law in `web/anatomical-material.mjs` contains `K/2 (log J)²`; summing that term in the declared quadrature gives the pointwise energy above. The projection gap measures the part of the sampled log-volume vector absent from a chosen pressure space. It is an algebraic loss of energy at a fixed state, not an equilibrium defect or an anatomical pressure measurement.

The existing `tools/anatomical_pressure_space_audit.py` counts proposed pressure degrees of freedom against reduced displacement coordinates. Its rank obstruction in the strict mixed limit remains a separate diagnostic. This Lean module does not compute coupling rank, prove inf-sup stability, or prove that a reduced displacement field can realize all pressure modes. Finite pressure compliance and adequate displacement resolution still need their own checks.

The tissue block in `web/tissue.mjs` uses `K/2 (J−1)²`, a different law. On this fetched main, `ContinuumProperties.lean` contains four real kinematic identities and no volumetric-energy theorem. Neither those identities nor proofs from a separate `(J−1)²` lab certify the log-volume projection operator. No existing proof file is changed.

There are no derivative or Hessian declarations here. An energy gap that is nonnegative for every `g` does not establish a positive Hessian gap after nonlinear composition `g(x)=log J(x)` at an arbitrary unrepresented base state. No floating-point refinement, continuum integration, determinant positivity between sample points, constitutive calibration, stationarity, convergence, contact, or biological validity is proved.

This is a bounded foundation for progressive individual property labs: first test weighted pressure representation and the fixed-vector energy gap, then separately test a declared physical compression law and its numerical derivatives. It does not extend the anatomical solver or manufacture a solver theorem.

## Reproduce and inspect

Use the existing pinned official Lean installer, then the standalone source-build checker:

```bash
cd education
python3 tools/install_lean.py --directory .tools
python3 tools/check_mixed_volume_proofs.py --build-dependencies
python3 tools/check_mixed_volume_proofs.py
```

The checker verifies the existing mathlib lock, all eight transitive Git dependencies and pristine dependency sources. Dependency preparation uses the existing ProofWidgets bootstrap and two source-build jobs, with binary-cache downloads disabled. The fresh proof check treats warnings as errors, creates an `.olean`, audits every theorem's kernel dependencies, and rejects admissions and custom axioms. The only permitted foundational dependencies are mathlib/Lean's standard `propext`, `Quot.sound`, and `Classical.choice`.

Default fresh output is `.tools/mixed-volume-check/{receipt.json,lean-check.txt,MixedLogVolume.olean}`. `--output PATH` selects another evidence directory. A failed check removes the previous success receipt. The source and checker hashes, tested source commit, pinned toolchain/dependencies, exact command and transcript hash are recorded. Archived review evidence is under `research/mixed-volume-evidence/`; compiled binaries remain local generated artifacts. The original attempt to use the official binary cache received HTTP 403; no alternate endpoint or access bypass was used. All proof imports were subsequently built from pinned source.
