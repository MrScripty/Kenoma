# Contractile and series state: primary-source review

Research only, inspected **2026-10-06** on `education/active-stability-controls`. No coefficient, reference convention, production law, book equation or Lean obligation is changed. No new simulation is claimed. Read with the [controlled witnesses](active-stability-controls-results.md), [passive-memory limitation](active-memory-stability.md) and [rate-source ledger](rate-source-addendum.md).

**The smallest defensible next step is a source-equation replay of attached cross-bridge strain and series force balance, with a cooperative three-state model as the first substantive skeletal-history candidate. Neither is a demonstrated repair of the arm's descending-branch local instability.** A two-state attached/detached model is a useful falsifiable baseline, not a sufficient physiological closure. Persistent force enhancement and millisecond tension recovery are separate obligations.

The unchanged active fixture remains stationary at stretch 1.25 but has negative full-nodal curvature (approximately −4294/−3034 N/m) and a strict volume-admissible local witness (−47538.9 Pa); matched zero-activation controls are positive. Those receipts remain evidence about the original instantaneous local law. No source below identifies model stretch 1.25 with a human sarcomere length.

## Primary evidence and held-state distinctions

| Original source and inspected access | Preparation / protocol | Supported distinction and limit |
|---|---|---|
| [Gordon, Huxley & Julian 1966, J Physiol 184:170–192](https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1966.sp007909), publisher abstract | Frog single fibers; precautions for local sarcomere uniformity during isometric tetani | Plateau at 2.05–2.2 μm and descending tension above it. Across separately prepared equilibria, overlap and attached populations can differ. No transient stiffness law or human reference map. |
| [Ford, Huxley & Simmons 1981, J Physiol 311:219–249](https://pubmed.ncbi.nlm.nih.gov/6973625/), original abstract initially readable | Frog tibialis anterior; tetanus at 0–1°C; selected-segment length feedback; 2.0–3.2 μm sarcomeres; 0.2 ms completed steps | Instantaneous stiffness and early recovery after releases scale approximately with developed tension. Their delay-line analysis includes apparatus response, inertia, fluid, passive mechanics, tendon and contractile apparatus. Quick stretch was not matched satisfactorily. The series/apparatus correction matters; a release result is not a universal linear stretch law. |
| [Campbell & Moss 2000, J Physiol 525:531–548](https://pubmed.ncbi.nlm.nih.gov/10835052/), original abstract | Permeabilized rabbit psoas segments under sarcomere length control; paired triangular stretches/releases; varied interval and calcium | Prior movement reduces the initial stretch response; recovery depends on the inter-movement interval. Initial stiffness scales with developed tension over pCa 6.3–4.5. These are same-length history comparisons, not an isometric force–length sweep. |
| [Edman, Elzinga & Noble 1982, J Gen Physiol 80:769–784](https://pubmed.ncbi.nlm.nih.gov/6983564/), original abstract | Rana temporaria tibialis anterior fibers, 0.8–3.8°C, tetani up to 8 s; stretch versus isometric control; diffraction and segment clamps | Slowly decaying post-stretch enhancement persisted during contraction. All measured segments elongated; clamped segments still enhanced force. This preparation's enhancement occurred on the descending limb. This finite observation window does not establish a different infinite-time equilibrium or identify a molecular mechanism. |
| [Campbell, Hatfield & Campbell 2011, PLoS Comput Biol 7:e1002156](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002156), full original article | Strain-dependent detached / pre-stroke / post-stroke populations; heterogeneous serial half-sarcomeres; baseline parameters from permeabilized rabbit psoas at 15°C | Individual lengths are solved by interconnection force balance at prescribed total length. Standard comparison: 50 half-sarcomeres, activation over 1 s, another 1 s hold, 8% stretch at 0.1 initial lengths/s versus activation at final length; enhancement measured 6 s after stretch. Heterogeneity produces slow internal redistribution. This is a mechanism hypothesis, not proof that heterogeneity is necessary or stabilizes a continuum. |
| [van der Zee et al. 2026, PLoS Comput Biol 22:e1014748](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), published September 1; full original PDF | Eleven permeabilized rat soleus fibers, 22°C; seven modeled; stretch–shorten–stretch histories | Cooperative three-state model outperformed simpler candidates for history-dependent stiffness. Near optimum, overlap was fixed to one and force–length dependence omitted. Tables 2–3, equations 1–6/12–23 and supplements supply replay inputs; no descending-branch validation. |

The original observations discriminate four experiments: (1) prepared isometric force versus length, (2) rapid perturbation of an already attached population, (3) recovery and force/stiffness after a specified movement history, and (4) prescribed total length with evolving internal/series lengths. Combining their plotted slopes into one instantaneous stress derivative loses that distinction. This is the inference motivating the candidate, not a measured human constitutive identity.

## Smallest explicit baseline and next candidate

For a transparent distribution baseline, use a contractile coordinate `l`, a signed attached-link elongation `y`, attached density `n(y,t)`, recruitment capacity `C`, nonnegative attachment/detachment rates `f,g`, link stiffness `k>0`, and link-strain transport speed `v=α ldot` with an explicitly calibrated geometric factor α. A deliberately simplified kinetic/transport hypothesis is

```text
∂t n + v ∂y n = f(y; input,l)[C(input,l) − ∫n dy] − g(y; input,l)n
Tcb = k ∫(y + d)n(y,t) dy
```

Here `d` fixes the power-stroke/reference offset; `input` must mean calcium or a separately justified activation variable. These equations are a declared baseline abstraction, not a verbatim transcription of Huxley 1957 or a chosen human law. Its capacity convention and rate units require explicit normalization. If `C` varies, a recruitment rule is also required; it cannot be silently treated as conserved total heads. Use fixed capacity for the first held-input replay. Define boundary fluxes in strain space and initial distributions.

[Campbell 2014's original equations 1–4](https://rupress.org/jgp/article/143/3/387/43232/Dynamic-coupling-of-regulated-binding-sites-and) provide an inspectable related formulation: active force integrates attached-link force; isometric attached/detached fluxes use strain-dependent rates; available sites have their own calcium-driven equation with occupied-site protection. The paper links GPL code and tutorials in its supplement. **Its fitted validation is cardiac**, including rat myocardial preparations and a living rat myocyte. It supplies inspectable mathematical conventions, not skeletal or human-arm parameter evidence.

For the substantive skeletal candidate, the 2026 paper's core equations, with `B=∫n dx`, `Q=∫(1+x)n dx`, `N=N_on`, `O=N_overlap`, are:

```text
r(x) = M f(x)(N−B) − g(x)n(x)
Ndot = kon [Ca](O−N)(1+kc N/O) − koff(N−B)(1+kc(O−N)/O)
Mdot = k1(1+kF Q)(1−B−M) − k2 M
FCE = Q/β
Ffiber = FSE = FCE + FPE;  Lfiber = LSE + LCE
```

`x` is centered, normalized link strain; `M` is the detached ON fraction; OFF is the remaining population. Kinetic change `r` and geometric translation must both be retained. Gaussian `f`, double-exponential `g`, and the serial/parallel equations are located in the [original PDF, printed pp. 21–26](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable). This equation locator is preferable to inventing rate values or equating dimensionless β with a continuum stress.

There is a specific implementation check before replay: if `M` is interpreted literally as a detached population, attachment and detachment also transfer heads between `M` and `B`. With `OFF=1−B−M`, the displayed equations imply `OFFdot=−Bdot−Mdot`; that must preserve nonnegative OFF. Determine from the pinned source whether `M` is instead a phenomenological availability factor, whether additional fluxes are included, and what population bounds are enforced. Do not silently add a transfer term or call the excerpt a fully audited mass-conserving three-pool scheme. This is an unresolved equation/convention check, not a demonstrated error in the authors' code.

**Our bounded recommendation:** replay the full strain distribution before adopting a Gaussian moment approximation. Then compare an explicitly normalized two-state baseline against the cooperative candidate under the same source protocol. The additional states encode a falsifiable hypothesis: calcium input can remain held while attached population and filament availability evolve. Do not append this force to the existing `a σ0 fL(λ)` term without declaring which contribution it replaces; that would risk counting contractile force twice.

The [authors' public repository](https://github.com/timvanderzee/biophysical-muscle-model) advertises two-, three- and four-state implementations coupled to series and parallel elements, with `Test`, `Reproduce`, `Fitting` and `Data` directories. Its README still points to a preprint. The directory overview was inspected; an immutable revision and source-file parity were **not** obtained here. The original journal equations should govern a later benchmark, followed by a pinned code/data manifest. No executable or model output was imported into Kenoma.

### Concrete first equation-only benchmark

Implement the two-state reduction first, with **contractile length clamped directly**, `O=M=1`, fixed calcium and fixed sigmoid `N`. This is an independently specified mathematical subprotocol using the published rates, not reproduction of a published fiber trajectory or its series spring. From the same original equations/tables:

```text
f(x) = f1/(sqrt(2π) w) exp(−x²/(2w²))
g(x) = g1 exp(−E1 x) + g2 exp(−E2 x)
N = 1/[1 + 10^(nH(pCa + log10(Ca50 in mol/L)))]
```

Use Table 3's two-state medians `f1=52 s−1`, `g1=4 s−1`, `g2=21.1 s−1`, `E2=−0.6`, `nH=3.1`, `Ca50=0.83 μM`; Table 2 gives `E1=2`, `β=0.5`, stroke `10 nm` and width `3 nm`, hence normalized `w=0.3`. Test `pCa=4.5` and `6.1`. These are source-derived nonhuman fixture inputs; medians need not reproduce any particular fitted fiber.

Our proposed benchmark sequence and exact independent predictions are:

1. At each fixed pCa, integrate `I=∫f/g dx`; initialize `B*=NI/(1+I)` and `n*(x)=N f(x)/[(1+I)g(x)]`. Verify the kinetic residual vanishes and the numerical integral of `n*` equals `B*`. This independently constructs isometric equilibrium without settling a time integrator.
2. Apply a mathematical instantaneous CE strain shift `Δx=±10−3`, then `±5×10−4`, translating the distribution, with calcium/sites held. These are numerical differential probes, not experimental amplitudes or tuned material coefficients. For force `Q/β`, the immediate exact change is `ΔFCE=B*Δx/β`; attached fraction remains `B*` on an infinite strain domain.
3. Clamp the new CE position and integrate only attachment/detachment until the kinetic residual returns below a predeclared tolerance. Since this two-state reduction has no overlap change, its unique distribution returns to `n*` and its relaxed incremental CE force returns to zero. Validate that result rather than adding the old descending `fL`. No relaxation time is invented: the two published strain-dependent rates govern recovery.
4. Independently differentiate/integrate the population equation: `Bdot=f1(N−B)−∫g n dx` on an infinite domain. Bound `0≤B≤N≤1`; detached capacity is `N−B`. With finite strain boundaries include actual transport flux and quantify lost mass. Refine extent, bins and timestep; compare the immediate slope and final force to these independent predictions.

Force here is dimensionless, x is dimensionless and rates are s−1; report seconds and normalized force, not Pa, N/m or human stiffness. `Ca50` must be converted to mol/L inside the pCa sigmoid. Gaussian width must be divided by the stroke length; inserting `3` instead of `0.3` changes the experiment. β is the source normalization convention: verify the computed maximal-isometric force instead of forcibly renormalizing it to one.

The series-coupled source benchmark follows only after pinning a coherent individual-fiber parameter/data set and its force scale, measured serial count, resting lengths and initialization. The source CE/PE/SE topology and parameter tables alone do not identify those offsets or an entire measured input record. Thus the concrete first benchmark tests kinetic/transport correctness and fast-versus-relaxed distinction; it does **not** qualify series state, descending force–length, persistent enhancement or three-dimensional stability. A claim that it does would be rejected by construction.

## What a fast tangent actually holds fixed

This derivation belongs to the declared baseline above. Let a sufficiently fast length perturbation change the link elongation by `δy=α δl`, while attachment/detachment and recruitment have negligible elapsed time. The density translates geometrically:

```text
n_new(y) = n_old(y−α δl)
δTcb = α k (∫n_old dy) δl
Kcb,fast = α k B > 0     if α>0 and B>0.
```

The held object is the set of attached heads and their biochemical/recruitment state. Freezing `n` numerically in the spatial strain coordinate while also failing to translate links would incorrectly erase stiffness. Conversely, resetting `n` to its isometric equilibrium at every mechanical iteration erases memory and reverts to a relaxed response. In a reference-material-coordinate formulation, attachment labels remain fixed while their elastic strains change. Declare which representation is implemented.

At isometry the baseline kinetic equilibrium obeys `f(C−B)=gn`. If `g>0`, define `I=∫f/g dy`; then `B=C I/(1+I)` and `n_eq=(C−B)f/g`. Its equilibrated force may fall as overlap capacity falls, despite the positive fast elastic term. The sign and magnitude must be computed for the actual `f,g,C` and reference convention. This algebra is not a reconstruction of frog data or a guarantee for the cooperative equations.

The frozen and relaxed tangents must therefore be reported separately. For state evolution `zdot=G(F,z,input)` and stress `P(F,z,input)`, with nonsingular `G_z`, a stationary branch gives

```text
dz_eq/dF = −G_z^−1 G_F
Crelaxed = P_F − P_z G_z^−1 G_F
Cfast = P_F                  (material/internal labels held)
```

The dynamic response instead uses `δzdot=G_F δF+G_z δz`, including the actual series/geometry constraints. A singular state Jacobian, multiple equilibria, continuing internal redistribution or hysteresis prevents casual use of the stationary-branch formula. Report those possibilities as outcomes rather than selecting a favorable branch.

## Series state changes the force path

For a general explicit CE/PE/SE candidate define `Tseries=Ts(L−l)` and `Tseries=Tcb(l,z)+Tp(l)`. Thus a fixed total length `L` still permits contractile `l` to move. With a positive local series tangent `Ks=Ts′` and frozen local contractile/parallel tangent `Kc`, a scalar fast perturbation gives

```text
δT = Ks(δL−δl) = Kc δl
Ktotal,fast = Ks Kc/(Ks+Kc)       when Ks+Kc ≠ 0.
```

This calculation is our local circuit inference. It is not evidence that a particular human tendon has such stiffness. It also exposes a failure: if the **relaxed** internal `Kc` becomes negative, fixed total length does not itself forbid an unstable internal exchange; its exchange stiffness is `Ks+Kc`. A positive end-to-end fast response does not decide that condition.

Distributed serial half-sarcomeres introduce several `l_i`, several `z_i`, common connection force and `Σl_i=L`. This differs physically from a single spring attached only to the arm caps. Test the zero-total-length exchange modes and passive pathways. The 2011 hypothesis supplies a source-supported way for finite-time force history to arise through internal redistribution, but it cannot be substituted for a tissue-level strong-ellipticity result. Reproducing an elevated tension after several seconds is not proving eventual equilibrium stability.

Any candidate that retains the original negative relaxed local law and merely adds passive fading memory remains subject to the [existing positive-real-root obstruction](active-memory-stability.md). A Hill force–velocity relation, ordinary damping, or positive quick stiffness alone does not demonstrate removal of that obstruction. A claimed repair must identify which relaxed local/spatial force path changes, or which actual active feedback supplies stabilization.

## Missing parameters and references before anatomy

| Item | What must be identified / what would invalidate an import |
|---|---|
| Reference and geometry | Reference fascicle and sarcomere lengths, optimal-length convention, serial count, pennation and mapping from continuum fiber stretch to link transport. A dimensionless fixture stretch does not supply these. |
| Active density and force scale | Heads/links per area, preparation force normalization, and conversion to stress/work in the chosen reference. Link force in pN, normalized fiber force, Pa and N/m cannot be interchanged. |
| Kinetics | Attachment/detachment functions, offsets, recruited pools, calcium convention, thin/thick rates and cooperation. Obtain specimen/fiber-type/temperature evidence; table entries need unit checks against equations. No time constant is selected from a different preparation. |
| Series and parallel paths | Slack/rest lengths, force–extension curves, anatomical versus attachment compliance, and distributed architecture. A fitted fiber-attachment spring is not automatically tendon or aponeurosis. |
| Descending branch | A source-tested overlap law and prepared-state protocol outside optimum. Reintroducing overlap changes the candidate and requires requalification. Merely multiplying the new frozen stress by the old instantaneous `fL` may preserve the offending physical derivative. |
| History | Separate transient stiffness reduction, persistent post-stretch enhancement, and shortening depression. A unique relaxing state may reproduce one and fail another. Spatial heterogeneity or activation-dependent passive structure requires its own original-source parameters and observations. |
| Energetics | ATP/input power convention, attached-link storage, passive storage and dissipation. Mechanical work need not be supplied by a conservative active potential; an active reaction model needs an energy budget. |

The 2026 paper's tables can define a **nonhuman source replay**. They do not close any entry above for the atlas arm. Its medians across fitted fibers are not an independently measured human coefficient set. Use source inputs unchanged for reproduction; keep parameter-identification experiments separate from numerical qualification.

## Rejection tests to predeclare

1. **Source parity:** pin article version, code revision, data hashes, exact rate units and initial conditions. Check population bounds, conservation/recruitment convention and transport sign. Failure to reproduce a published benchmark with those inputs rejects the implementation before anatomical use.
2. **Fast versus prepared slope:** at matched force and geometry, perturb with biochemical labels held and geometric link strains updated; separately relax states at each length. Compare force changes and state derivatives by independent finite differences. Reject a model that obtains a positive fast tangent by silently freezing the physical length dependence or resetting history.
3. **Controlled source histories:** replay paired stretch–shorten–stretch protocols at held calcium, multiple amplitudes and recovery intervals; retain training/test separation. Report full force trajectories and stiffness ratios, not only the favorable first slope. A two-state model failing submaximal history is a rejected baseline, not a reason to retune the arm.
4. **Rapid release and stretch:** separate immediate force, early recovery, later recovery and asymmetry. Resolve source apparatus/series assumptions. A model with instantaneous power stroke has not thereby validated the measured early redistribution of attached biochemical states; add pre/post-stroke states only after this test exposes a need.
5. **Persistent force history:** compare activation at final length against active ramp-and-hold ending there. Monitor local/series lengths and every internal population. Vary hold duration; reject an assertion of steady enhancement when the candidate only has a finite slow transient. Segment-controlled observations must remain a challenge for any purely global nonuniformity explanation.
6. **Series exchange:** apply the same overall displacement with different declared series properties, and introduce zero-sum internal-length perturbations. Solve the coupled internal-state Jacobian; reject claims based only on end reaction stiffness.
7. **Numerical independence:** refine timestep, strain-domain extent/bin width and state tolerances; compare a full distribution with any moment reduction. Verify equilibrium force constraints and mechanical work. Do not use a positive algorithmic matrix as a physical tangent receipt.
8. **Continuum gate after scalar qualification:** define a three-dimensional objective stress/state mapping and passive/deactivated response, then revisit the saved full-nodal and strict volume-admissible witnesses at matched configuration and force. Include transverse/shear modes and coupled dynamic poles. Reject a claim of arm stabilization that only passes a scalar axial test or excludes the existing interior directions.

These are proposed future rejection tests. None has been run in this review.

## Access and evidentiary boundaries

The Huxley 1957 original publisher endpoint returned 403; the [Huxley–Simmons 1971 Nature page](https://www.nature.com/articles/233533a0) exposed metadata/abstract and subscription preview only. Their detailed equations were not recovered or treated as verified. Zahalak 1981's [original DOI](https://doi.org/10.1016/0025-5564(81)90014-6) was identified, but its full equations were not inspected; no named distribution-moment closure is adopted on reputation alone. The 2026 original PDF supplies a modern explicitly inspectable distribution formulation instead.

PMC pages returned browser challenges; several publisher/full-text links failed. Ford's initial original abstract was readable through search, whereas a later direct PubMed request returned only a footer. Edman 1982 and Campbell–Moss 2000 original abstracts were readable. Original PLoS articles and Campbell 2014's journal text/PDF were readable. The Leonard–Herzog 2010 publisher endpoint returned 403; no detailed result from that inaccessible page is used here. Public GitHub overview loaded, but directory links failed and a read-only shell request to GitHub's API hit a tunnel 403. No challenge, subscription or network restriction was bypassed; no credential, paid service or external reviewer was used.

**Decision:** proceed first with a pinned, nonhuman distribution/series benchmark and reject the two-state baseline if it fails the declared histories. The cooperative three-state model is the smallest next candidate supported by the inspected skeletal comparison. Keep the pre/post-stroke serial model as a separate early-recovery/persistent-history hypothesis. Neither establishes a replacement three-dimensional relaxed law, anatomical reference mapping, or long-time stability. Those remain explicit blockers before production, lesson or Lean changes.
