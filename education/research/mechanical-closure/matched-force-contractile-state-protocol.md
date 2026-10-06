# Matched-force contractile state: pre-execution protocol

Declared 2026-10-06 from frozen `dc9f22cbc8e0b04fceb062a6e0e7ab0bb8db6d16`. This independent author lane leaves the separate 1.01 pressure diagnosis, production equations, book, Lean, old evidence and anatomy unchanged. Commit this protocol before implementing or executing the coupling. No new arm solve, nonlinear block trajectory or physical clock advancement is authorized by this experiment.

## Diagnosis and falsifiable hypothesis

The accepted coarse 1.25 state has residual 9.659460896e-5 N and independently checked gradient derivatives. Its unit held-cap negative witness decomposes into matrix +62.727890, passive fiber +2283.431169, active axial force–length −11844.433632, active orientation +2.166818, pressure prestress −4.043136 and weak volume +22.704697 N/m, summing to −9477.446195 N/m. The finite P1 mode is **not** pointwise volume preserving. This identifies the descending force–length term in the stated model, rather than a sign, serial-force multiplier or held-cap error. It does not establish a physiological instability.

Hypothesis: exact strain transport of a carried continuous contractile density adds fast response at identical initial stress; reaction subsequently relaxes that response. It need not repair the long-time negative mode. Retain the original force–length envelope and its derivative throughout. The known stationary reaction distribution is independent of macroscopic length, so the relaxed limit must reproduce the original law. A reset/no-transport control must retain the old negative witness.

## Explicit coupling and initialization

Reuse the already qualified [continuous density model and its fixed gates](continuous-strain-ce-protocol.md), never a source-code runtime or the discarded finite-bin model. Read its immutable 96-history archive, selecting only R=3, pCa=4.5, 200/400/800 nodes, displacements ±.001/±.0005 and max steps .001/.0005 s (24 histories). Use initial, immediate jump and first hold samples at .008, .02, .04, .1 and .2 s; no rerun or extended hold. Preserve each quadrature's own stationary `n*=alpha f/g`, capacity N, raw B*, phi*, E*. Do not set raw phi* to one.

```
phi(n) = integral (1+x)n / beta; beta=.5
p_active(lambda,n) = sigma0 fL(lambda) phi(n)/phi*
sigma0 = 155000 Pa; lambda0=1.25
fL(lambda) = [1-((lambda-1)/.5)^2]^2 on |(lambda-1)/.5|<1
delta = Gamma (lambda-lambda0); Gamma=130
```

Gamma is an **educational kinematic gain**, using the previously derived illustrative 2.6 micrometre/(2×10 nm) relation, not measured human serial architecture. It multiplies strain, never force. The macro scale explicitly calibrates the existing initial nominal stress without altering raw density normalization. The unchanged block is L0=.14 m, A0=.0004 m², V0=.000056 m³. No physical head count is inferred. Each integration point initially has its own existing lambda and n*, so the entire frozen nodal force field matches exactly. Material-point probes use homogeneous lambda0 and its original transverse stretch; transverse stretch is held fixed during these tiny axial probes. Passive matrix, passive fiber and finite bulk response remain unchanged.

At a jump carry the original exact translated density with endpoint escape detachment. During holds use the retained reaction histories. This new **multiplicative macro coupling** is a composite educational hypothesis, not a fitted physiological overlap/recruitment law. The existing fL has not been fitted to the source's strain domain or sarcomere lengths.

## Independent algorithmic derivative

Differentiate the conserved reaction at its own stationary distribution:

```
m(0) = -d n*/dx
Jreaction = -diag(g) - (1+N-2B*) f w^T
m(t) = exp(Jreaction t) m(0)
sphi(t) = sum w(1+x)m(t)/beta
dp_active/dlambda = sigma0 [fL'(lambda0) + fL(lambda0) Gamma sphi(t)/phi*]
```

Compute the exponential independently by a symmetric similarity and eigendecomposition, not the retained nonlinear DOP853 integrator. Compare with central differences of the actual ±delta nonlinear retained histories, for both amplitudes and both time resolutions. Check the exponentially small finite-domain endpoint correction and report it. Independently verify the original passive derivative by central differences. This is an endpoint step/hold algorithmic response, not the fixed-density material tangent, a stored-energy Hessian or a stability certificate for the powered system.

Only after the material-point gates pass, assemble the additional axial response on the **same frozen** 189-free-DOF block at 256 quadrature points. Check its quadratic form against direct quadrature on the original witness, retain the old force–length term and condensed weak-pressure operator, and report lowest sampled eigenvalues and old-witness projections at each hold time and analytic relaxed limit. Do not call this a new coupled nonlinear field trajectory or spectral convergence result.

## Energy channels

Set C=sigma0/phi* and `Ulink=V0 C fL Ehat/Gamma`. This is elastic storage **inside an actively powered subsystem**. At fixed geometry report separately:

```
Pattachment = V0 C fL/Gamma integral [.5(1+x)^2/beta] f(1-B)(N-B)
PdetachmentRemoval = V0 C fL/Gamma integral [.5(1+x)^2/beta] g n
dUlink/dt = Pattachment - PdetachmentRemoval
```

Attachment input is not a complete ATP chemical-power model; detachment removal is not proven heat dissipation. No passive dissipation law is introduced. At the first jump, idealized full-support transport followed by endpoint detachment gives phi(s)=phi*+B*s/beta and E(s)=E*+phi*s+B*s²/(2beta). Integrate mechanical work `V0 C/Gamma integral fL(lambda0+s/Gamma) phi(s) ds` and signed envelope/recruitment work `V0 C/Gamma integral d[fL]/ds E(s) ds` independently as polynomials. Subtract the directly archived escaped elastic energy scaled by the endpoint envelope. This event bookkeeping is not a continuous moving-boundary reaction path. Report passive stored energy separately; independently integrate passive axial work along the fixed-transverse path. No global passivity or thermodynamic closure claim follows.

## Fixed acceptance and negative controls

| Check | Unchanged or predeclared gate |
|---|---:|
| Frozen initial full force | <=1e-4 N; exact field change <=2e-6 N |
| Initial macro force compared with original | <=1e-4 N |
| Independent scalar algorithmic/passive central derivative | relative <=1e-4, denominator max(1 Pa, abs(reference)) |
| Retained initial RHS and adaptive moments | <=1e-10/s; <=1e-10 absolute |
| Matched time moments | B<=1e-10; phi,E<=2e-10 absolute |
| Matched quadrature moments | <=1e-9 absolute |
| Density/population | strict finite n>=0 and 0<=B<=N; no clipping |
| Archived exact jump identities | <=2e-12 absolute |
| New jump energy/work identity and passive work | <=2e-12 after dividing by V0 C/Gamma and V0 respectively |
| Hold energy rate identity | relative <=1e-12, denominator max(1 W, absolute channel powers) |
| Reaction sensitivity independent initial derivative | relative <=1e-12 |
| Finite-domain sensitivity correction | absolute phi derivative <=1e-10 |
| Witness decomposition / new assembled quadratic form | absolute <=1e-8 N/m |
| Reset/no-transport relaxed operator | max absolute difference <=1e-12 from old operator |

Require the intentionally incorrect Gamma force multiplier to fail the original 1e-4 N force gate. Preserve the old amplitude-equivalence and passive controls by binding their immutable receipts. Preserve all old force, pressure, geometry, contact and derivative gates as inherited initial-state evidence; this experiment neither reclassifies nor advances those histories. No more iterations, relaxed tolerances, state resets or endpoint extensions after a failure. Export failed measurements and classification before stopping dependent block work.

## Sources and claim limits

The [original Van der Zee et al. article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), [source pixel/notation audit](original-plos-table-visual-audit.md), [dimensional mapping](dimensional-contractile-mapping.md), and [continuous reference results](continuous-strain-ce-results.md) bind the source-informed rates and mathematical state. [Krivickas et al. original article](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/expphysiol.2010.055269) and [the amplitude binding](source-amplitude-p2-p1-protocol.md) supply the stated human single-fiber mean stress anchor. Rat 22°C kinetics and human 15°C amplitude are explicitly composite, not matched-specimen validation. [Gordon, Huxley and Julian's original force–length study](https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1966.sp007909) motivates distinguishing equilibrated overlap from transient response but supplies no parameter map here.

Save exclusive new receipts, source/archive hashes, raw verification output and inspected static renders. Neither a fast positive response nor passing this bounded coupling qualifies anatomical compression, contact, dense lift/release convergence, in vivo stability or clinical behavior.
