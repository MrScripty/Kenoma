# Direct contractile-coordinate kinetic benchmark: predeclared protocol

Entry checkpoint: `8741bba2134ea51e9138061a0ebc0b6ba5e9a1b3`. Research successor only. Original mechanics, all old evidence, production/book/Lean equations and the two protected native-worker files remain frozen. This protocol is committed before execution. No anatomical coefficient or stabilizing parameter is selected.

## Source and experiment identity

Use the [original van der Zee et al. 2026 article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), equations 2–6, 11 and 22 and Tables 2–3, as a source-derived **nonhuman equation fixture**. Primary PDF extraction has been independently inspected; screenshot pixels were unavailable. Column association follows the populated rows/header ordering; no visual table certification or authors' code/data replay is claimed. See the separate source-rendering evidence and convention audit. No code/data revision is imported.

The declared reduction holds overlap and availability equal to one and recruitment capacity N fixed. It clamps the contractile coordinate directly and omits the source's fiber/series/parallel coupling, cooperative states and experimental histories. Link coordinate x and force Q/beta are dimensionless; rates use seconds. No Pa, N/m, human fiber length or temperature transfer is implied. Force is not reset to unity.

Fixture: f1=52/s, g1=4/s, g2=21.1/s, E1=2, E2=-.6, w=.3 (3 nm/10 nm), beta=.5, nH=3.1, Ca50=.83e-6 mol/L. Test pCa=4.5 and 6.1. Define

```
f(x)=f1 exp(-x²/(2w²))/(sqrt(2pi)w)
g(x)=g1 exp(-E1 x)+g2 exp(-E2 x)
N=1/(1+(Ca50/10^(-pCa))^nH)
n_t=f(x)d-g(x)n, d=N-integral(n dx)
F=integral((1+x)n dx)/beta.
```

## Discrete population, transport and time advancement

Uniform domains [-R,R], R=2.4 and 3.0; dx=.04,.02,.01. Exact Gaussian CDF differences give cell-integrated Fi; gi=g(xi) at cell centers. Arrays store bin masses pi, **not density samples**. State includes detached population d. Markov equations are pi'=Fi d-gi pi, d'=sum(gi pi)-sum(Fi)d. No rate renormalization, population clipping or solver iteration.

Initialize the independent discrete equilibrium Ih=sum(Fi/gi), d*=N/(1+Ih), pi*=d*Fi/gi. Also independently integrate f/g and x f/g over [-8,8] with absolute/relative quadrature tolerances 1e-12. Report Gaussian attachment truncation, quadrature error and baseline force; componentwise medians do not define an individually fitted fiber.

Instantaneous shifts delta=+.001,-.001,+.0005,-.0005 use center-mass translation: r=abs(delta)/dx; split each mass between its center (1-r) and the neighboring center r. Escaped r times edge mass transfers to d as an explicit artificial boundary detachment. The lost discrete moment uses the off-grid destination center. This is **not** the exact continuous partial-cell Gaussian-tail moment. Record mass and moment loss and their effect on the fast response. Extent refinement bounds this artifact; do not erase it by renormalization. Reject abs(delta)>=dx.

Hold the new coordinate and integrate kinetics for exactly 1 second using backward Euler dt=.004,.002,.001 s. With ai=1/(1+dt gi), the positivity-safe direct update is

```
d_new=[d_old+sum((1-ai)pi_old)]/[1+dt sum(ai Fi)]
pi_new=ai*(pi_old+dt Fi d_new).
```

Validate finite/nonnegative populations, 0<N<=1, and total mass before and after every step. Advance time only after the candidate passes. Reject invalid inputs; never clip, reset to equilibrium, extend the horizon, relax tolerances or add iterations after a failure. A failed run is retained and the declared experiment stops. This is a linear kinetic update, not accepted advancement of the anatomical arm.

## Independent predictions and refinement gates

Reference the identical finite-dimensional generator through SciPy's matrix exponential at matched times 0,.008,.02,.04,.1,.2,.5,1 s. This independently tests temporal discretization, not continuum strain-space convergence. Store complete matched-time states and scalar histories, including failures. Independently audit generator signs/column sums, detailed balance, synthetic boundary populations and rejected invalid states. Exact-semigroup conservation/positivity errors below numerical roundoff tolerance are reported; BE accepts no negative populations.

Fixed acceptance gates, chosen before execution:

* Every BE state is finite and nonnegative without clipping; mass error <=2e-12.
* Equilibrium kinetic residual l1 <=1e-10/s, independently calculated. Initial/immediate moment identities, including recorded discrete boundary loss, absolute error <=1e-12.
* Matrix-exponential reference total error <=2e-12, no component below -2e-14; report minimum rather than silently clipping it.
* At the fixed 1 s endpoint, kinetic residual l1 <=1e-10/s and absolute force difference from the original discrete equilibrium <=1e-10. Failure rejects relaxation qualification for this budget.
* For each extent/pCa/sign/amplitude, max matched-time force error relative to the exact generator decreases at each dt halving, with ratio .3–.8 when the larger error exceeds 1e-12. Finest temporal force error divided by abs(delta)*N/beta <=.05. These are temporal accuracy gates, not observational fit.
* At each extent, equilibrium force error against continuous quadrature decreases at each bin halving with ratio .2–.8 when the larger error exceeds 1e-12; finest relative error <=1e-4.
* At identical dx/pCa/delta/dt, max matched-time force difference between R=2.4 and 3.0 <=1e-8; escaped mass <=1e-10 and escaped normalized moment <=1e-10. These bound this benchmark's finite-domain artifact.

Report actual errors and refinement ratios even when passing. Preserve all failed receipts. Do not infer published-history reproduction, cooperative-model fitness, descending equilibrium, energy budget, dynamic continuum stability, human stiffness, anatomical nodal/quadrature/timestep convergence or a qualified dense lift/release. This fixed-overlap model has a unique same-input equilibrium: its relaxed incremental force is zero **by construction**. Positive fast response cannot be cited as a cure of the retained stationary negative arm-law witnesses.

## Bounded next decision

If kinetic/transport qualification passes, the next substantive candidate still requires a pinned individual-fiber source dataset/code revision, audited cooperative population convention, source series initialization and held-out movement histories. Physiological reference and objective 3D stress/state mapping remain separate blockers. Keep the production/book/Lean statement as an instantaneous fixed-activation model until those obligations are met; the successor research result documents what is held fixed rather than rewriting a physiological claim around a scalar success.
