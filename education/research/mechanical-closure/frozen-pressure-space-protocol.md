# Frozen pressure-space operator comparison

Entry commit12485b3d1b0b630b505bf35e4acc4934270ab3e0; separate branch
research/frozen-pressure-space-comparison. Use the existing4x1x1 and8x2x2
P2 meshes, affine patches at stretch1.01/1.25,155000Pa peak amplitude,
activation1, and all other unchanged coefficients and cap constraints.
Only the existing scalar transverse-traction construction is used; no
full-block nonlinear solve, new reference fit, stabilization or alteredK.

The continuous and elementwise discontinuous P1 models both use
Pi=integral[W0+p logJ-p^2/(2K)]dV0. Assemble their complete respective mass
M, b=integral Q logJ and D=db/du; eliminate p=K M^-1 b. Thus energy is
W0+K/2 b^T M^-1 b, force is integral[P0+p F^-T]:gradN and Hessian is
Hfixed(p)+K D^T M^-1 D. Hfixed retains the pressure prestress term
-p G_rb G_sa and every matrix/passive/active term. The original pointwise
energy is independently assembled as W0+K/2 integral(logJ)^2, with full
Cfixed(K logJ)+K G outer G. The original Node muscleMaterial and
materialTensor independently assemble pointwise energy, force and tangent
actions. Mixed Node assembly adjusts pressure and includes exact dp;
weak directional moments check that elimination independently.

At an affine patch, G is constant and P2 variations give elementwise-linear
delta(logJ). Broken P1 should therefore recover the pointwise tangent;
measure the full matrix difference rather than insert that identity into
the implementation. The equivalence need not extend to nonaffine fields.
Unit tests include nonaffine frozen derivative probes and preserve prestress.

Use256 positive points for base operators and independent32/256-point
original Node replay. Keep original force1e-4N, assembly2e-6N, reaction/work
1e-3N, weak/local compatibilityRMS1e-6, sampled0.98<=J<=1.02, exact caps,
zero strict boundary crossings and analytic cap reaction1% gates. Derivative
checks use original1e-7/5e-8m steps and relative1e-4 tangent-action gate,
with assembly/weak-pressure and geometry/crossing checks. Pointwise
compatibility at nonstationary probes is recorded, not a stationary gate.
Original unit-test energy replay1e-12J and directional energy-gradient1e-6N
checks are retained. No gate is changed to force a comparison to pass.

Record positive mass eigenvalues, full coupling rank and scaled spectrum
including all pressure nulls, using the reference H1 seminorm and pressure
L2 mass. Never remove a gauge automatically. Broken P1 may have pressure
nulls despite positive mass and finite-K solvability. The pointwise energy
has no actual finite pressure unknowns; report its formal quadrature-space
mass/Gram spectrum with zero-mode multiplicity explicitly, without calling
it an incompressible mixed inf-sup result. Use the original1e-10 relative
rank cutoff, preserve raw roundoff-sign eigenvalues, and report beta including
nulls separately from the smallest positive singular value.

Record full energy/force/pressure/tangent differences, lowest eigenvectors,
complete matrix/passive/active/pressure-prestress/volume Rayleigh terms,
cross-operator Rayleigh values, nonlinear derivative probes, geometry,
reaction/work and independent quadrature evidence. Negative curvature and
rank failures remain results. No positivity repair or tangent-only operator.
Write requests/assembled fields before optional diagnostics, refuse overwrite,
and bind all original receipts and source hashes. No production/main/book/Lean
change, physical history advancement, anatomy, locking, incompressible
stability or nonlinear convergence claim follows. Stop after comparison.
