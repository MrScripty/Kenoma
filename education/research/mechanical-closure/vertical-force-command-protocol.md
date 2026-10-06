# Vertical force-command lab: preregistered successor

Design and budgets are committed before cases run. The frozen benchmark `0e89c60d03d3d6137e1ece686ecf942b83d05645` and frozen design `41573e4581d2ab0b1054840ece57cd6239de69f3` remain byte-for-byte unchanged. This supersedes the design's conditional suggestion of possible feedback stabilization. It is a finite force-command lab, not a height/rest servo, human calibration, continuum repair or release of the book/site.

## Scope correction and equations

Keep the pinned Millard curves/parameters and scalar geometry from [the frozen design](tension-mass-control-design.md): lMT=L0−y, lT=L0−y−lopt*q, FT=F0*fT(lT/lslack), m*dw/dt=FT−mg, dy/dt=w. Fiber force equilibrium is F0*[a*fL(q)*fV(v)+fP(q)+beta*v]=FT; dq/dt=vmax*v. The source activation derivative receives excitation u. States are y,w,a,q,I; work/momentum integrals are diagnostic accumulators, not extra physical forces.

**One continuous-time gain pair:** kp=.4 (dimensionless), ki=8 s−1. No gain search or adjustment follows observed trajectories. e=(Fcmd−FT)/F0, uraw=ub+kp*e+I, u=clip(uraw,.01,1). Conditional integration freezes I when at an excitation limit and error pushes further into saturation; otherwise dI/dt=ki*e. ub is the declared initial activation and I(0)=0. Drive release bypasses the servo with u=.01 and freezes I. Excitation limits, activation lag and tendon extension remain explicit.

At a taut unsaturated stationary weight-command state, define kt=dFT/dlT>0, kf=dFstatic/dlf, b=dFfiber/d(lfdot)>0, ca=dFfiber/da>0 and the relevant source activation branch time tau>0. The linearized characteristic polynomial is lambda*Q(lambda), with

\[
Q=bm\tau\lambda^4+[bm+m\tau(k_f+k_t)]\lambda^3
+[bk_t\tau+m(k_f+k_t)+c_a k_p k_t m/F_0]\lambda^2
+[bk_t+k_fk_t\tau+c_a k_i k_t m/F_0]\lambda+k_fk_t.
\]

For kf<0, Q(0)<0 and its leading coefficient is positive, so there is a positive real mode for finite PI gains. The unsaturated invariant I+ki*m*w/F0 is constant when Fcmd=mg, giving a zero mode. Assess the appropriate one-sided activation/saturation modes; full-system asymptotic stability and all-negative-eigenvalue acceptance are explicitly rejected. Saturation at a=1 can obstruct requested compensation. Retain zero/growing modes and finite perturbation outcomes without modifying the descending law.

## Inputs and initialization

Mathematical inputs require finite m>0 and finite Fcmd>=0. The qualified UI/run range is **m=.1–10 kg, Fcmd=0–150 N**; reject nonfinite, negative, zero mass and out-of-range requests without replacing them with clipped valid inputs. Source F0=100 N is not a universal dynamic/passive force ceiling. Mass changes restart the run; no moving-load attachment/mass-switch mechanics is implied. Educational g=9.80665 m/s², fixed origin, zero pennation, no added load damping/contact/support.

Baseline initialization uses mref=.5 kg, q0=1, a0=mref*g/F0=.04903325, w0=y0=I0=0, s0=fT-inverse(mref*g/F0), L0=.1+.2*s0. Mass-only runs keep this same initial geometry/actuator state; other masses begin with a declared force imbalance. For descending comparisons use q0=1.10, a0=.5, FT0=F0*[a0*fL(q0)+fP(q0)], L0=.1*q0+.2*fT-inverse(FT0/F0), and mdesc=FT0/g for the equilibrium comparison. Apply +/-1e−4 q perturbations while keeping endpoint position and L0 fixed; altered tendon preload is reported, not silently re-equilibrated. Fixed-activation and PI runs share each initial perturbation and mass. UI edits may move that initialization out of equilibrium and must say so.

## Scripts, tracking window and event priority

End time .30 s except descending comparisons .15 s. Commands are piecewise constant, splitting exactly at scheduled changes. UI target changes re-run the selected finite script; selected mass and force remain visible. Script presets disclose which stages use weight-relative commands rather than the editable pulse target.

| Case | Default target and phases |
| --- | --- |
| Baseline/constant | Default mg at m=.5 kg throughout .30 s; editable target permits constant-force exploration. |
| Pulse → weight → brake | mg until .05; editable peak target (default 1.2*mg) .05–.10; mg .10–.15; .8*mg brake from .15 until an armed positive-to-nonpositive velocity crossing or .25 timeout; mg thereafter. |
| Lower → brake | mg until .05; editable lowering target (default .8*mg) .05–.10; 1.2*mg brake from .10 until an armed negative-to-nonnegative crossing or .20 timeout; mg thereafter. |
| Release drive | mg until .05; u=.01, I frozen, through .30. Force is an output; a zero-force target is not asserted. |
| High command | mg until .05; editable target default 120 N through .15; mg thereafter. Label above initial zero-velocity capacity or unreached within the window, never universally impossible. |
| Mass-only | Common baseline actuator/material state and constant 5 N target; default masses .25/.5/1 kg. |
| Descending fixed activation / PI | mdesc and constant weight target; a=.5 fixed for control or PI from the same initial perturbation; .15 s. No force-clamp or massless eigenvalue is substituted for this inertial system. |

Tracking windows are **[.03,.05] baseline**, **[.13,.15] pulse weight stage**, **[.25,.30] lower post-brake**, **[.13,.15] high command**, **[.25,.30] mass-only**, **[.10,.15] descending PI**. Release and fixed activation have no tracking-quality acceptance. Require the entire window accepted and max |FT−Fcmd|<=.01*mg to label tracking met. A truncated window is not reached, not passed. Force-command changes within a window invalidate that window definition. Numerical validity, tracking quality and actual motion are separate statuses; poor tracking/failed lift/instability does not make a numerically valid trajectory invalid.

Brake arming requires actual prior velocity in the intended direction with magnitude >1e−5 m/s during the brake phase. Starting at w=0 cannot count as braking success. Locate the next directed zero crossing after arming without resetting w or any mechanical state. At coincident events, priority is: (1) invalid input/state/intermediate stage, root/residual or unqualified domain; (2) qualifying directed crossing; (3) brake timeout; (4) scheduled transition/end. At a crossing exactly at timeout, record crossing. Timeout is a recorded outcome and switches to weight command without promising rest. After crossing, continued drift/reversal remains visible.

Every RK/ODE stage checks finite state, a within source bounds (roundoff allowance 1e−12 only), q>.4441, taut s>1 and positive tendon length. Slack/lower-length transitions are not qualified by the frozen benchmark. Failures terminate, retain the last accepted time and full state, and save the failed stage/time/reason separately. Do not shrink steps opportunistically to pass a domain/root failure, project a state, advance to a failed trial, or synthesize a continuation. Explicit event localization uses at most 32 bisections and a 1e−7 s time bracket; an invalid localization trial also terminates from the last accepted state. Source velocity inversion bracket is [-10,10], at most 64 safeguarded iterations, and dimensional residual <=1e−7 N; a failed bracket/residual is fatal.

## Numerical and work acceptance

Primary RK4 uses fixed .0002/.0001 s step pairs, split at scheduled/detected events. Independent DOP853 and Radau use rtol=1e−9, atol=1e−11, maximum step .0005 s, and preserve their own last accepted states on failed intermediate trials. Compare common accepted time histories only; terminal failure locations are bounded by retained/failed times and not claimed as exact event solutions.

Predeclared gates: curve values <=2e−12 and derivatives <=2e−8 against frozen native kernels; algebraic force residual <=1e−7 N; matched-time RK refinement/independent replay errors <=1e−6 m y, <=1e−5 m/s w, <=2e−6 a/q, <=1e−4 N FT. Located brake event differences <=2e−6 s. Independent momentum impulse error <=1e−7 N*s. Component passive-storage, load kinetic+potential work, and combined ledger errors each <=1e−5 J. Do not relax gates after results; preserve all failed checks. The source reconstruction and event logic must be tested in the browser, not merely screenshot-tested.

Component identities: dEf=Fp*dl_f; dET=FT*(dlMT−dl_f); d(K+Vg)=−FT*dlMT. Pact=−Fact*dl_f/dt and D=F0*beta*vmax*lopt*v²>=0; total d(K+Vg+Ef+ET)/dt=Pact−D. Use endpoint curve-integral storage independent of accumulated stage powers, plus independently integrated dense-replay power/momentum. Report active work, damping, tendon/fiber storage and load energy separately; no ATP/heat claim. Additional root/integration tolerances serve these fixed physical budgets rather than change them.

Browser output is a schematic vertical mass/actuator/tendon, moved only by accepted integrated y/q/s, with target/actual force/weight; excitation/activation/saturation; motion; signed power and energy error. A history cursor exposes actual values and the stopped state. The force slider cannot directly animate height. Force=weight with nonzero w is persistent motion, not a rest/height servo. Show source FL operating point/descending branch, growing/zero-mode scope, and high-command/truncated/failed statuses. No anatomical arm, skin or fabricated dynamics.

## Review and provenance

Frozen source: [official OpenSim commit](https://github.com/opensim-org/opensim-core/tree/5bc7d3308eda742690f485ec060bfe725a349fa6), [original Millard paper](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf), and local hash-bound source kernels. Controller, mass fixture and UI are explicitly educational additions. Gain choice is declared, not experimentally calibrated or selected for eigenvalue signs. Reference-manifest/anatomical research remains in its separate lane; no moment-arm/reference data are inferred here. Parent handles independent review, book/site and Library delivery.
