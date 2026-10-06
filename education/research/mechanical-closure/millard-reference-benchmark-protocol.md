# Bounded Millard source-reproduction protocol

Prospective protocol, 2026-10-06. This source-reproduction task is separate from physiological reference-pose calibration, continuum coupling and the book release. No inherited material, solver gate, frozen witness or book file is changed.

## Immutable source and license

Use official OpenSim core release **4.5.2**, annotated tag object `7fcf7c1009ca636a3e0a2d14745109d684072e2a`, peeled commit **`5bc7d3308eda742690f485ec060bfe725a349fa6`**, tree `19ea9bb15e9c43a3f7506966ea6ac0ca14002df1`. The ordinary public Git clone verified the tag object and commit. Initial raw-file requests used the tag-object SHA rather than the peeled commit and returned 404; they supplied no evidence. The complete clone supplies the pinned bytes. A browser open of the tag-object URL failed and was not retried or bypassed.

[Official pinned source](https://github.com/opensim-org/opensim-core/tree/5bc7d3308eda742690f485ec060bfe725a349fa6), [original paper](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf), and unchanged source snapshots with SHA-256 hashes in `education/data/millard-reference-v1/upstream/manifest.json` establish provenance. The relevant implementation is Apache-2.0; preserve upstream copyright headers, LICENSE.txt and NOTICE. The benchmark harness and Python translation are modified derivative implementations explicitly identified as such, not full OpenSim or a claim of running its model/integrator.

## Equations and units

For the selected zero-pennation, massless contractile-element case:

\[
l_{MT}=l_f+l_T,\quad q=l_f/l_{opt},\quad s=l_T/l_{slack},\quad v=\dot l_f/(v_{max}l_{opt}),
\]
\[
F_T=F_0 f_T(s),\quad
F_f=F_0[a f_L(q)f_V(v)+f_P(q)+\beta v],\quad F_f=F_T.
\]

Here lengths are m, forces N, times s, q/s/v/a and beta dimensionless, and vmax is in optimal fiber lengths/s. Positive v denotes lengthening. The derivative of q is vmax*v, not v. The general source multiplies fiber force by cos(pennation); this benchmark sets pennation to zero explicitly. It contains no fiber inertia or human-arm mechanics.

Activation is the original `MuscleFirstOrderActivationDynamicModel::calcDerivative`: clamp activation to [amin,1], then da/dt=(u−a)/tau with tau=tauA*(0.5+1.5*a) when u>a and tau=tauD/(0.5+1.5*a) otherwise. Excitation u and activation a are distinct. The experiment supplies excitation in [amin,1]; it does not rely on hidden excitation clamping.

All four curves are the upstream piecewise quintic Bezier constructions, including their endpoint linear extrapolation, not Gaussian/analytic approximations fitted to them. The C++ oracle extracts the unchanged factory/control-point function bodies from hash-verified source snapshots. Its small storage/evaluation shim is authored for this benchmark and is separately checked against Python evaluation. The Python construction is a disclosed translation. This is a source-kernel comparison, not independent validation of the paper's experimental data.

## Exact selected parameters and source safeguards

| Quantity | Selected value | Status |
| --- | --- | --- |
| F0, lopt, lslack, pennation | 100 N, 0.1 m, 0.2 m, 0 rad | Explicit educational dimensional scales, not biceps calibration |
| vmax | 10 optimal fiber lengths/s | `Muscle.cpp` default |
| beta | 0.1 | Damped-model source default; numerical/constitutive choice, not measured viscosity |
| tauA, tauD, amin, initial a | 0.010 s, 0.040 s, 0.01, 0.05 | Source defaults; no human physiological-temperature rate claim |
| Active FL | x0=0.4441, x1=0.73, x2=1, x3=1.8123, ascending slope=0.8616, curviness=1, floor=0 | Construction defaults with floor changed from 0.1 to 0 by source damped finalization |
| FV | endpoint slopes 0, near-concentric slope .25, isometric slope 5, near-eccentric slope .15, max eccentric factor 1.4, curviness .6/.9 | Source damped defaults; one source comment describes near-eccentric slope as a guess |
| Passive FL | zero-force strain 0, one-normal-force strain .7, low stiffness .2, high stiffness 2/.7, curviness .75 | Source defaults and fitted-default resolution |
| Tendon FL | strain at normalized force 1: .049; stiffness 1.375/.049; toe force 2/3; curviness .5 | Source defaults and fitted-default resolution; not atlas tendon calibration |

The implementation threshold for using damping is **beta >= .001**; header prose is not the sole authority. Damped finalization removes the active FL floor but does not automatically set the declared amin=.01 to zero. The undamped compliant configuration requires amin>=.01, enforces FL floor>=.1 and adjusts endpoint FV slopes; it is audited but not run in this first benchmark. Maximum pennation is acos(.1), and fiber shortening is subject to a unilateral lower-length constraint. Our zero-pennation cases stay above q=.4441; an attempted lower-bound state is rejected and recorded rather than silently advancing it. General pennation, slack/buckling transitions and the upstream initializer's Newton/velocity-sharing paths remain unqualified here.

The upstream initializer seeks fiber/tendon force equilibrium, with a nominal tolerance max(1e−8*F0,10*SignificantReal), starting tendon length at 1.01*lslack and allowing 200 iterations. Our held-length initialization instead constructs q=1 and inverts the monotone tendon curve at a=.05, then independently solves the nearby static force balance. This selects a known branch and does not claim to reproduce the entire upstream initialization algorithm.

## Cases and independent comparison

1. **Curve/activation kernel replay:** compare C++ original factory control points and source activation derivative with independently translated Python values/slopes, endpoint conditions and finite-difference derivatives. Sweep the descending FL branch without removing negative slopes.
2. **Held total length, compliant tendon:** initialize q=1, a=.05, and tendon strain from equilibrium. Keep lMT fixed. Excitation .05 through .05 s, .35 from .05 to .15 s, then .05 through .30 s. Activation, fiber length, actual tendon force and fiber velocity are outputs. Do not prescribe actual force in this case.
3. **Fixed external force on the descending branch:** set constant activation a=1; choose the stationary q=1.10 force from the original total active-plus-passive FL curves. Tendon strain follows that force. Apply ±1e−4 q perturbations and evolve for .05 s under the same external force, allowing total length to move. This is a massless force-loaded fixture, not target-force feedback or a loaded human arm. Retain instability if the actual derivative is negative. Compare the linear growth rate with a finite-difference dynamic derivative and perturbation evolution.
4. **Invalid state:** attempt q below the declared lower bound; preserve rejection. Never advance time/state after a failed velocity solve or invalid state.

The C++ harness uses explicit RK4 at .0001 and .00005 s, splitting exactly at excitation transitions. Python uses adaptive DOP853 and an independent stiff Radau replay, also splitting at transitions. Velocity inversion uses bounded root solves under the same force-balance equation; no iteration/tolerance tuning to hide failures. Dimensional gates: curve control-point/value error <=2e−12, derivative comparison <=2e−8, algebraic force residual <=1e−7 N, native fine/adaptive matched-time a and q differences <=2e−6, fine/coarse difference <=2e−6, and independent activation branch solution <=2e−8. These are declared engineering reproduction budgets, not physiological acceptance criteria. Preserve raw logs and failed comparisons.

Passive storage is the integral of the original passive fiber and tendon curves; active work is externally powered actuator work and beta contributes nonnegative dissipation. The held-length work-balance budget is **1e−5 J**; compare an independently integrated power history with endpoint storage, retaining coarse quadrature discrepancies. This is not an ATP/heat model or a proof of long-time stability.

Target tendon force is not implemented in this first deliverable. A future controller must map a target force to excitation with explicit feedback, saturation and delays; actual activation/force remain responses. No independent incompatible length/force/activation prescriptions are introduced.
