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

The sufficient slope estimate is `F0/(w*l0)`. It is deliberately looser than the
runtime's `F0*sqrt(2/e)/(w*l0)` estimate. Consequently the root theorems require
the stronger explicit condition `c*F0/(w*l0)<1`. At the actual teaching constants
`F0=1200`, `w=0.6`, `l0=0.2`, the conservative coefficient is `10000 N/m`, below
each supported tendon stiffness `15000`, `30000`, and `60000 N/m`. This does not
establish monotonicity for every custom input allowed by the sharper code guard.

The source import closure contains 1882 modules, sharing 1473 with the existing
1500-module matrix/square-root closure; the combined closure is 1909 modules.
`additional-import-modules.txt` records the 409 required additional modules.
The dependency builder adds exactly the five source imports and retains the
same official mathlib commit, dependency lock, bootstrap, no-cache behavior and
two-job limit. Its per-module logs use a separate `real-mathlib-source-logs`
directory so the original dependency-build logs remain available.

At this checkpoint the Lean declarations are **proposed, uncompiled**.
`actuator-real-claims.json` is descriptive metadata without a status field; it
cannot supply checked evidence. An additive source build waits for the original
official dependency build to complete before using its shared pinned workspace.
No claim card or release gate is integrated on this branch yet.

Remaining obligations include the sharper global slope constant, root existence
and numerical root residuals, binary64/transcendental refinement, event splitting,
continuous mechanical work/energy balance, fractional-power material derivatives,
and empirical validation. The proposed proofs do not discharge those obligations.
