# Local real serial-block material proof checkpoint

This source studies a homogeneous incompressible neo-Hookean block with axial
stretch `lambda>0`, energy per reference volume
`W=mu/2*(lambda^2+2/lambda-3)`, and nominal axial stress
`P=mu*(lambda-1/lambda^2)`. The series comparison assumes separate blocks with
the same `mu`, joined through ideal massless fixed-length axial fixtures that
allow lateral sliding and transmit a common axial force. It does not model a
continuous stepped-solid interface.

Source/map commit: `00754d63f7a483ed9b2c17b6314b6483ec256777`.
Source SHA256: `b0b4ccb250f7a10561c66fc32def5aad4f3ec900eeb3575a3e8bd4aacf0f3fbe`.
Map SHA256: `bc9f43e657a1612866611c903c0c768f580881c35ca8788aaf07d4937cbc010e`.

The fresh strict kernel run checked twelve declarations in
[`SerialSpecimenReal.lean`](../../proofs/SerialSpecimenReal.lean):

- Exact energy factorization, nonnegative energy, and zero energy iff `lambda=1`.
- The exact derivative `HasDerivAt W P lambda`.
- Factored nominal stress and the identity `sigma=lambda*P`.
- Tensile/zero/compressive nominal stress iff stretch is above/equal/below one.
- Exact stress-difference factorization, strict monotonicity on positive
  stretches, and uniqueness of a positive homogeneous force root.
- Exact volume identity `(A/lambda)*(L*lambda)=A*L` under the imposed geometric
  formulas.
- Strict unequal-area stretch ordering under the same tensile or compressive
  force, with equal force and positive homogeneous roots assumed explicitly.

The [claim map](../../proofs/serial-specimen-real-claims.json) has explicit
assumptions and limits and no manually assigned checked status.
[`qualification.json`](qualification.json) records twelve freshly computed
statuses, source/map hashes, actual command, Lean version, and pristine mathlib
and package identities. [`lean-check.txt`](lean-check.txt) contains the actual
strict transcript. All twelve axiom reports contain only `propext`,
`Classical.choice`, and `Quot.sound`. The run also freshly checked the unchanged
four real kinematic property declarations; their receipt and transcript are
included separately.

The pins remain Lean `4.19.0`, mathlib
`c44e0c8ee63ca166450922a373c7409c5d26b00b`, manifest SHA256
`5c6421b650bc87a2427a892a39e5522dc44543ca4ac1bd6e9f08d536c044a752`,
and the eight locked git packages. No upstream source, configuration, manifest,
dependency revision, or historical receipt changed.

One additive official source module was needed for the reciprocal derivative:
`Mathlib.Analysis.Calculus.Deriv.Inv`. Its recursive source closure contains
1776 modules; the other closure modules were already compiled. The command
`lake --no-cache build Mathlib.Analysis.Calculus.Deriv.Inv` built that single new
module successfully, without downloading a binary cache. Cold integration must
add this import root to the new lesson branch's existing guarded source builder;
the frozen source-builder configurations remain unchanged in this checkpoint.

With the pinned tool environment and that import provisioned, reproduce:

```
python3 education/review/serial-specimen-real/qualify.py
```

The review runner removes the prior success receipt first, invokes the unchanged
fail-closed property checker, and compiles the new source with
`lake --no-cache env lean -DwarningAsError=true`. It checks input hashes and each
axiom report before recording success. Ordinary book-checker integration,
visible cards, runtime implementation, and browser qualification remain with
the parent worker.

These local real proofs do not establish root existence or a runtime bracket,
bisection refinement, matrix pressure/traction equations, `det(F)`, mesh-volume
integration, global multiaxial stability, a continuous interface, bulk-penalty
calibration, or anatomical validity. No runtime or rendered result is claimed.
