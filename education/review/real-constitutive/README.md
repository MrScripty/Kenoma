# Constitutive Real proof checkpoint

This isolated successor starts at reviewed source/evidence commit
`96f2e1d4afa2d2fec3d296c8283679a61e26d9be`. It changes no browser equations,
material calibration, solver acceptance limits, or frozen deliverable.

`proofs/ActuatorConstitutiveReal.lean` states the actual exponential activation
update and Gaussian force–length function in `web/elbow.mjs`, shared by the
compliant series actuator. The eight declarations cover activation invariance
and its exact constant-input differential equation; force sign and amplitude;
the exact Gaussian slope; and a sufficient real monotonicity/uniqueness result
for the series residual including its tension-only passive term.

The checked sharp slope estimate is `F0*sqrt(2/exp(1))/(w*l0)`, matching the
actual JavaScript guard with Euler's constant represented as the exact real
`exp(1)`. Its elementary proof applies `x+1<=exp(x)` at `x=2*z^2-1`, multiplies
by a positive exponential factor, and bounds the square before taking the
real square root. The monotonicity and root uniqueness statements require the
same guard `c*F0*sqrt(2/exp(1))/(w*l0)<1` and include the passive kink through
monotone addition, without assuming the passive law is differentiable there.
The earlier explicitly uncompiled conservative proposal is retained in commit
`f03dabd` for comparison; it has not supplied checked evidence.

The extended combined source import closure contains 1909 modules, including
the existing 1500-module matrix/square-root closure.
`additional-import-modules.txt` records the 409 required additional modules.
The dependency builder adds exactly the five new source imports (the square-root import is already present) and retains the
same official mathlib commit, dependency lock, bootstrap, no-cache behavior and
two-job limit. Its per-module logs use a separate `real-mathlib-source-logs`
directory so the original dependency-build logs remain available.

The first genuine eight-claim source checkpoint is `06ee82f`.
All eight declarations freshly passed Lean 4.19.0 with `-DwarningAsError=true`.
The only reported axioms are `propext`, `Classical.choice`, and `Quot.sound`.
The unchanged four real kinematic claims were rechecked as part of the same
qualification. The combined official source build completed all 1909 modules
without modifying the lock, source dependencies, or gates.

`qualification-8/` preserves the exact checked source, metadata, raw Lean
transcripts, and computed source-bound receipt including every locked package
revision and pristine status. `dependency-source-build.log` records complete
source-build progress. The descriptive canonical manifest contains no manual
status fields. The review-only `qualify.py` records the actual command and
fail-closed qualification procedure used in this worktree; the coordinating
worker owns integration with the book's ordinary build checker.

No new browser render, full book build, publication, or empirical qualification
is claimed on this isolated branch. Those gates remain the parent's combined
integration responsibility.

Remaining obligations include root existence
and numerical root residuals, binary64/transcendental refinement, event splitting,
continuous mechanical work/energy balance, fractional-power material derivatives,
and empirical validation. The proposed proofs do not discharge those obligations.
