# Two-state source convention audit

The proposed direct-CE-clamp baseline is a consistent fixed-capacity kinetic model **if its population measure and finite-domain boundary rule are explicitly declared**. The equilibrium and fast-force formulas follow from that model. They do not by themselves define a mass-conserving finite-domain implementation, reproduce the source fiber trajectory, or qualify descending-branch mechanics.

This audit inspected the [original 2026 PLOS article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), Methods: “Cross-bridge cycling,” “Thin filament activation,” “Interface with elastic elements,” and “Solution methods based on discretization,” alongside the [local source review](contractile-state-source-review.md). The publisher HTML prose loaded. Its native equation/table images and printable/manuscript endpoints were unavailable in this audit; a shell PDF request returned a tunnel 403 and was stopped. No source directory, challenge, or access restriction was bypassed. Exact table entries and rendered equations below are therefore distinguished from independently readable primary-source conventions.

## What the readable primary Methods establishes

The paper defines the attached fraction by `∫n dx`, labels f1 as Gaussian area and w as standard deviation, and centers normalized link elongation on a 10 nm power stroke. Its force is the sum of zeroth and first moments. It describes negative-strain detachment with E1=2, increasing detachment at large positive strain, fixed overlap at optimum, and CE force scaling by β=.5. Tables 2–3 contain fixed parameters and fitted medians across seven fibers. These source conventions are independently readable in the [primary Methods](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748).

In particular, the integral definition makes n a density with respect to normalized strain dx. Calling a sampled value n(xi) a “fraction per bin” and then summing it without weights changes the measure. The correct alternatives are density samples with quadrature weights, or actual bin masses. The inspected source implementation was not obtained, so this audit does not certify the authors' stored-array convention or claim their code makes that error.

## Formula and parameter checks

The review proposes

```text
f(x)=f1 exp(−x²/(2w²))/(sqrt(2π)w)
g(x)=g1 exp(−E1 x)+g2 exp(−E2 x)
N=1/[1+10^(nH[pCa+log10(Ca50/(1 mol/L))])].
```

The f normalization is consistent with the source's area convention: its full-line integral is f1. With E1 positive and E2 negative, the first g term grows toward negative x and the second grows toward positive x, matching the source's described detachment directions. Positive g1,g2 make g strictly positive. The pCa expression is dimensionally consistent only when Ca50 is converted to mol/L before taking its numerical logarithm. Equivalently, with `[Ca]=10^(-pCa) mol/L`, `N=1/[1+(Ca50/[Ca])^nH]`. These are algebraic consistency checks on the review's transcription; exact equation-image parity was not independently obtained.

| Proposed two-state fixture item | Value | Audit status |
|---|---:|---|
| f1 | 52 s−1 | Review's Table 3 transcription; exact table cell not independently rendered |
| g1, g2 | 4, 21.1 s−1 | Same limitation |
| E1 | 2 | Independently confirmed in readable primary prose |
| E2 | −0.6 | Review's Table 3 transcription; sign yields the described positive-strain growth |
| Power stroke | 10 nm | Independently confirmed in readable primary prose |
| Width | 3 nm, hence w=.3 | Review's fixed-table transcription; division by the 10 nm stroke is correct |
| β | .5 | Independently confirmed in readable primary prose; dimensionless force normalization |
| nH | 3.1 | Review's Table 3 transcription; exact table cell not independently rendered |
| Ca50 | .83 μM = .83×10−6 mol/L | Review's Table 3 transcription; conversion is correct |

Because x is dimensionless, f has units s−1 when written as a density per unit normalized strain; conceptually its measure is still essential. The integrated per-bin attachment rate has units s−1. E1,E2,w,β,N and nH are dimensionless. `Q/β` is normalized force, not stress, stiffness in N/m, or force in N. The physical elongation convention corresponding to the proposed moment force is `elongation=stroke×(1+x)`.

Setting O=M=1 and holding the sigmoid N fixed deliberately removes cooperative dynamics and fiber series equilibrium. In this reduced model M=1 is a fixed availability factor; it should not also be counted as an independent detached population in addition to the capacity `N−B`. The conserved accessible population is N. The remainder `1−N` may be treated as a fixed unavailable pool for this declared abstraction. This is a mathematical reduction under held inputs, not a three-pool conservation certificate for the cooperative source equations.

## Equilibrium and the required measure

For fixed domain Ω and no transport,

```text
∂t n=f(x)d−g(x)n,   B=∫Ω n dx,   d=N−B.
```

Integrating gives `Bdot=FΩ(N−B)−∫Ωg n dx`, where `FΩ=∫Ω f dx`. Only on the full line is `FΩ=f1`; finite Gaussian truncation must be reported, rather than hidden by rate renormalization.

Since g>0, equilibrium satisfies `n*=d*f/g`. With `IΩ=∫Ω f/g dx`, the exact formulas are

```text
d*=N/(1+IΩ),   B*=N IΩ/(1+IΩ),
n*(x)=N f(x)/[(1+IΩ)g(x)].
```

Thus the review's full-line prediction is correct. The same formulas hold on a fixed finite domain using that domain's actual integral; a quadrature implementation must use its discrete integral consistently.

For bin masses pi, define positive rates `Fi=∫cell_i f dx` and declared detachment rates gi. A mass-conserving finite-dimensional Markov reduction is

```text
pidot=Fi d−gi pi,
d′=Σgi pi−(ΣFi)d,
d+Σpi=N.
```

Here d′ is the time derivative of detached population d. Off-diagonal transition rates are nonnegative and every column of the generator sums to zero. Nonnegative initial populations remain nonnegative. Positive Fi,gi give a unique equilibrium with `Ih=ΣFi/gi`, `pi*=N Fi/[(1+Ih)gi]`. If density samples ni are stored instead, `pi=wi ni` and `Fi=wi f(xi)` for positive quadrature weights wi. A plain rate `f(xi)` applied to a bin mass is wrong by a measure factor.

This establishes conservation for the proposed kinetic reduction. It does not establish conservation for an unspecified interpolation/remapping method.

## Translation, boundary flux, and relaxed force

Let `Q=∫(1+x)n dx`. On the full line, translating attached links by Δx gives `nnew(x)=nold(x−Δx)`, preserves B, and yields `Qnew=Qold+BΔx`. Consequently the immediate increment is exactly `BΔx/β`. Translation toward positive x increases force under this convention. Merely keeping the Eulerian density unchanged would erase the mechanical link strain increment.

On a finite fixed interval, a translated Gaussian-tail distribution exits the interval. Let A be the old-coordinate set whose translated points leave it. With no incoming population,

```text
Bnew=B−∫A nold(y)dy,
Qnew−Qold=BΔx−∫A(1+y+Δx)nold(y)dy.
```

The full-line immediate formula therefore has a measurable boundary correction. Simply discarding outgoing mass breaks `d+B=N`. Returning it to d can preserve the numerical Markov population, but represents artificial boundary detachment and changes the immediate force. Retaining escaped bins or expanding the represented domain preserves their moment instead. Reflecting or periodic transport introduces different force conventions and must not silently substitute for strain translation. At nonzero transport speed v, the integrated attached equation includes `−[vn]left^right`; the detached or exterior pool needs the corresponding declared flux rule.

A fixed-grid, fixed-domain kinetic model after the shift returns to its same unique n* if N, f,g and domain are unchanged. Its relaxed force increment is then zero, even if an explicitly tracked boundary detachment occurred. A moving or translated finite domain instead changes IΩ and the equilibrium moment; its relaxed force need not be exactly unchanged. Refining extent and tracking outgoing mass/moment are necessary to recover the full-line prediction. The proposed benchmark must therefore specify its finite-domain transport rule before calling itself conservative or claiming exact immediate/relaxed limits.

## β does not permit silent force renormalization

As a conditional static check of the review's listed functions and medians, independent quadrature over [−8,8] gives `I=1.992220371317` and `∫x f/g dx=−.020650740710`. At N=1 these imply `B*=.665800016073` and `FCE*=1.317797077720` with β=.5. At pCa=4.5, `N=.999987435748` and `FCE*=1.317780520585`; at pCa=6.1, `N=.466007594329` and `FCE*=.614103446001`. Absolute quadrature error estimates were below 1e-12. These are equation-consistency calculations, not a time integration or source trajectory reproduction.

The median parameter bundle does not, under the review's proposed convention, automatically make maximal isometric force exactly one. Componentwise medians are not an individual fitted fiber. An implementation must report the predicted baseline and retain β=.5; rescaling it to one would change the declared source-derived fixture. Exact source equation/table verification remains necessary before interpreting any discrepancy as a source inconsistency.

## Decision before benchmark

The analytical predictions are consistent under a declared density measure, fixed accessible capacity, and explicit boundary handling. The review correctly limits the direct CE clamp to a kinetic/transport test and excludes descending qualification and source series-coupled trajectory reproduction. A positive immediate strain response and zero relaxed length response in this baseline make those exclusions essential.

Before execution, pin the exact primary equation/table rendering or an accessible immutable source transcription; record whether arrays hold densities or masses; use integrated bin attachment rates; declare transport and boundary detachment/exterior handling; and compare both lost mass and lost force moment under extent/bin refinement. The remaining independent-source blocker is exact rendered parity for the Gaussian denominator, exponential signs, sigmoid, and unrendered table medians. No anatomical coefficient, reference map, time constant, old receipt, production file, or Git state was changed by this audit.
