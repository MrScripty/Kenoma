# Cooperative population and series initialization audit

Research-only follow-up, 2026-10-06. The parent owns protocol source `4c9406b` and the bounded direct-clamp two-state equation fixture. This audit changes no existing packet, implementation, source equation or Git state. It supplies mathematical implications of the inspected equations, not new simulations or an allegation about the authors' implementation.

**Finding:** the displayed cooperative equation does not explicitly subtract attachment flux from the detached ON variable. That leaves a population interpretation question, but **does not demonstrate a population-bound failure with the source's reported rates**. A sufficient invariant-domain condition is available below. Exact source-code interpretation, initial distribution, force renormalization and series resting lengths remain unverified.

## What the original source actually exposes

The [original 2026 PLoS article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), Methods, equations 2, 12–13 and 22, describes M as the ON/disordered-relaxed fraction, B as attached fraction, and uses `1−B−M` in its thick-filament state equation. Its [publisher PDF](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable), printed pp. 21–26, provides the extracted equations and tables documented in [the rendering evidence](source-rendering-evidence.md). Equation 22 uses `FCE=Q/β`, with β=0.5. The text says the noncooperative reduction sets M initially to one and k2 to zero. It does not supply a complete explicit initial density or series-offset initialization in the inspected main Methods. Searches for initialization, initialized and initial conditions found no such section.

The [public repository overview](https://github.com/timvanderzee/biophysical-muscle-model) was readable and points to Test/Reproduce/Fitting/Data. An ordinary public commit-history URL was tried once in this follow-up and failed. Previously blocked directory/API routes were not retried. No immutable code revision or source implementation was obtained; no source file was imported. Thus nothing below claims to describe code clipping, hidden flux terms, runtime normalization or actual initial arrays.

## Displayed equations and explicit assumptions

Use the already inspected notation, with `O=N_overlap`, `N=N_on`, `B=∫n dx`, `Q=∫(1+x)n dx`. Define `Dg=∫g n dx` and `a(Q)=k1(1+kF Q)`. The displayed mathematical model implies, on an infinite strain domain or with zero boundary flux,

```text
r(x) = M f(x)(N−B) − g(x)n(x)
J := Bdot = M f1(N−B) − Dg,         ∫f dx = f1
Ndot = kon [Ca](O−N)(1+kc N/O)
       − koff(N−B)(1+kc(O−N)/O)
Mdot = a(Q)(1−B−M) − k2 M
```

The transport contribution to B is zero only with the stated boundary condition. Finite-domain flux must be retained. These equations are transcribed from the inspected extraction; full visual/code parity remains qualified by the rendering evidence.

For this audit assume O is fixed with `0<O≤1`; f,g are nonnegative and integrable as required; rates kon,koff,k1,k2,kc are nonnegative; and `a(Q)≥0`. The last condition is a real domain restriction: a signed Q from sufficiently compressed attached links can make `1+kFQ` negative. No force clipping or alternative recruitment formula is assumed.

## Literal detached-pool interpretation versus availability factor

If M is a literal detached ON pool and U is a literal detached OFF pool, the obvious conservation identity is `U=1−B−M`. Ordinary attachment ON→attached and detachment attached→ON would transfer net J out of M, giving

```text
Mdot_literal = aU − k2M − J
Udot_literal = −aU + k2M.
```

These are **our stoichiometric comparison equations**, not a correction adopted into the source model. The displayed source instead yields

```text
Udot_displayed = −J − aU + k2M.
```

That bookkeeping effectively puts net attachment/detachment into the inferred OFF remainder. Alternatively M may be a phenomenological availability variable whose interaction with attached density is not a literal three-pool reaction network. The accessible equations/prose alone do not settle the intended microscopic interpretation. Do not silently add `−J`, substitute `M=1−B`, or relabel a pool to make it look conservative.

At a true kinetic stationary state J=0, the two M equations coincide. Matching only isometric force or stationary populations cannot distinguish them. A transient test with nonzero J can: hold the same density, N, M and Q and compare Mdot. Their difference is exactly `−J`. This is a falsifiable model-definition distinction; it is not evidence that the source code uses either version.

## Conditional invariant-domain proof

Consider the domain

```text
n(x)≥0,  0≤B≤N≤O≤1,  M≥0,  U:=1−B−M≥0.
```

With nonnegative recruitment a(Q) and the rate assumptions above:

1. At n(x)=0, the kinetic injection `M f(x)(N−B)` is nonnegative. Translation preserves density positivity on an infinite domain.
2. At N=O, Ndot=`−koff(O−B)≤0`. At N=B, `J=−Dg≤0`, while Ndot is nonnegative; therefore `(N−B)dot≥0`. The available-site bound is inward-pointing.
3. At M=0, Mdot=`a(Q)(1−B)≥0` because B≤1.
4. At U=0, the recruitment term vanishes and

```text
Udot = k2 M − J
     = M[k2−f1(N−B)] + Dg
     ≥ M[k2−f1 O].
```

Consequently **k2≥f1 O is sufficient** to make the OFF boundary inward-pointing for the displayed equations. Together these boundary checks establish a conditional invariant-domain result for regular solutions under the stated assumptions. They do not prove numerical positivity for an arbitrary discretization, bounds under nonzero strain-boundary flux, or invariance when a(Q) becomes negative.

The source tables list k2=200 s−1 and the three-state median f1=84.5 s−1 with O=1. Those values satisfy this sufficient boundary condition; 200 is larger than 84.5. Accordingly it would be incorrect to report that omitted explicit attachment transfer **must** produce a simplex violation for that fixture. It remains a reaction-interpretation question and a numerical regression to test, not a demonstrated source-parameter failure.

For the unrestricted model class, a concrete counterexample exists: n=0, B=0, N=O=1, M=1, U=0 gives `Udot=k2−f1`. Any f1>k2 makes the displayed equation leave the proposed population domain immediately. This is a parameter-class counterexample, not a claim about the reported specimen or fitted inputs. Similarly, if a(Q)<0 at M=0 and B<1, Mdot is negative. A declared signed-force domain or validated nonnegative recruitment function is therefore necessary.

The two-state noncooperative reduction uses M=1 as an availability factor alongside B>0. Then `1−B−M=−B`, so M cannot simultaneously be interpreted as a distinct conserved detached fraction in that reduction. Its availability convention is consistent with the parent limiting its validation to `0≤B≤N`; it should not impose the three-pool simplex on the two-state fixture.

There is a second precise reduction check: setting k2=0 and merely initializing M=1 does not freeze M if the displayed cooperative equation remains active. It gives `Mdot=−a(Q)B` once B>0. Maintaining M identically one therefore also requires disabling that state equation, an explicit model-family branch, or a different variable convention. The parent declares M frozen and thus removes this ambiguity from its bounded two-state experiment; unavailable source code prevents asserting how the authors implement that reduction.

## Stationary density and force normalizer

For a direct-clamped isometric cooperative state with M,N constant, g>0 and no transport, define

```text
I = ∫f/g dx,       H = ∫(1+x)f/g dx.
n*(x) = M N f(x)/[(1+M I)g(x)]
B* = M N I/(1+M I),      Q* = M N H/(1+M I).
```

These are our independent algebraic stationary-density formulas. A cooperative initial state additionally requires Ndot=0 and Mdot=0 with Q=Q*. Because recruitment/site activation is nonlinear, solve and report all admissible roots or declare a branch-selection protocol; do not assume a unique state or set the two-state density as an equilibrated cooperative density.

The source force convention `FCE=Q/β` makes the computed maximal isometric force equal one **only if** the actual stationary Q equals β under the normalization used. β described as attached fraction B does not automatically imply this because `Q=B+∫x n dx`. A nonzero mean centered strain changes the force per attached head. Nor do independently assembled parameter medians necessarily preserve the normalization of an individual fitted fiber.

Therefore record B*, Q*, Q*/β and the mean attached strain independently. Do not replace β with a computed Q* or introduce an extra force scale merely to force unit isometric force without declaring that different experiment. The inspected source also distinguishes empirical normalization by measured maximal isometric force from its model equation; exact code-level calibration between them remains unavailable.

## Series initialization: what can be derived without pretending to replay a fiber

For known attached density n, hence known TCE under the displayed strain-coordinate convention, the series/parallel circuit requires

```text
R(l) = Ts(L−l) − Tp(l) − TCE = 0.
```

For positive local series and parallel slopes, `R′(l)=−Ks−Kp<0`, so a root is unique on any declared admissible interval if endpoint residuals bracket it. This is an initialization root check; it does not prove coupled transient or relaxed stability. It treats n as the state supplying TCE. If initialization changes l while holding attached material labels instead of the strain-coordinate density, link translation must also change TCE, and the derivative must include that elastic contribution.

The source uses an exponential SE and a softplus PE. The PE carries positive force at its nominal resting offset, rather than an exactly zero force cutoff. Series compression can make the exponential SE force negative. Thus neither `l=rest` nor an unqualified zero-force initial guess is necessarily a balanced state. Declare the permitted compression domain and reject any root outside it.

Rest/slack offsets, force normalization and total length must be supplied consistently. In dimensionless variables the series solve depends on the combined reference offset `(L−LPE,0−LSE,0)/γ`; gamma maps fiber length to cross-bridge strain. Knowing just the fitted SE/PE slopes does not identify those offsets or the reference state. Initializing every fiber with guessed offsets would create a new fixture rather than reproducing the authors' input.

No exact original initial array, initial M/N, relaxation duration, series resting offsets or per-fiber force scale was recovered in this audit. The source text's explicit M=1 initial statement applies to the noncooperative reduction only. The parent direct-CE fixture therefore remains the currently reviewable source-equation experiment; it is not expanded to cooperative/series dynamics on these incomplete inputs.

## Required next checks and bounded outcome

Before adopting a cooperative implementation, pin an ordinary publicly readable code revision or clearly label an equation-only implementation. Resolve whether code M is availability or population, whether its derivative contains additional fluxes, whether Q/recruitment is clipped, and how maximal force and initial arrays are obtained. Test the boundary derivatives above separately from timestep refinement. For series initialization, require the actual offsets/input units and a root receipt at the declared initial state.

This audit narrows the earlier convention concern: a blanket simplex-failure claim is rejected by the conditional bound and reported rate comparison. Microscopic stoichiometry, signed-force recruitment domain, exact normalization and source initialization remain open. It establishes no descending force–length, human coefficient, spatial continuum or long-time stability closure. No source access restriction was bypassed, no service was installed, and no author or reviewer was contacted.
