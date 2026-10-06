# Article–code convention decisions before an independent release fixture

**Choose one declared mathematical system before selecting coefficients or releasing a series-coupled state.** The final article, the pinned prepublication implementation and the retained fixed-availability fixture expose different conventions. Source access and table verification do not make those systems interchangeable. This memo proposes bounded choices and checks; it runs no simulation, selects no human law or physical test, and changes no earlier source-bound document.

Prepared 2026-10-06. Primary identities are [van der Zee et al., PLOS Computational Biology 22:e1014748](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), its [original publisher PDF](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable), and [author repository revision 8c766dfb308051309193e7290ddd0bac3b726d11](https://github.com/timvanderzee/biophysical-muscle-model/commit/8c766dfb308051309193e7290ddd0bac3b726d11), dated July 8, before September publication. Inspected code facts and original file locations are recorded in [source-code-initialization-audit.md](source-code-initialization-audit.md); independent dimensional obligations are in [dimensional-contractile-mapping.md](dimensional-contractile-mapping.md).

The committed [original PLOS table visual audit](original-plos-table-visual-audit.md), commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`, identifies the exact publisher PDF and preserved Table 2/3 crops. The worker inspected original pixels and the parent independently opened both preserved table crops. This lane relies on that evidence rather than claiming its own pixel inspection. The two-state XB column and selected equation typography are verified. Earlier visual-blocker records remain historical receipts; no code fixture is relabeled a publication median. The audit preserves the printed thermal-width radical and cooperative kon unit discrepancies rather than silently correcting them.

## 1. Separate the three reproducibility claims

| Claim | What must be preserved | What can falsify it |
|---|---|---|
| Final-article equation implementation | Verified printed formulas, units, model-family definition and a declared equation-level resolution of any ambiguity | A flux, force transform, coordinate or normalization absent from the selected article equations |
| Exact pinned-code reproduction | Commit/tree/blob identities; selected discretized or moment branch; actual initializer, clipping, transforms, offsets, parameters and prescribed input | A changed branch or parameter, altered initialization, a missing implementation operation, or disagreement with the pinned program under identical inputs |
| Independent controlled fixture | Explicit independently implemented equations, input/protocol, source-informed parameters and all departures from article/code | Undeclared mixing of conventions, failed population/unit/work checks, or an unsupported claim to reproduce a measured trajectory |

Matching isometric force is insufficient for either exact-reproduction claim. A stationary state can conceal a missing attachment transfer, a force origin error or a different activation lag. Reproducing a published measured trajectory additionally needs the individual preparation/input data and its normalizer; a bundle of componentwise medians is not that preparation.

The retained 144-case fixed-M direct-CE packet remains its own independently declared equation fixture. Its results are unchanged. The proposed held-N operator supplies algebra without selected numerical coefficients; it is not an executed source replay or permission to run a release.

## 2. Population capacity: fixed availability or conserved detached heads

Let B=∫n dx, N be held available thin-site capacity, Q=∫(1+x)n dx, and J_B be the reaction contribution to Bdot. On an infinite domain, or with a separately accounted boundary flux:

\[
J_B=M f_1(N-B)-\int g n\,dx.
\]

**Alternative A: the retained fixed-M fixture.** Set M≡1 and use attachment f(x)(N−B). M is an availability factor, not a detached population alongside B. Its domain check is 0≤B≤N; it carries no claim that M+B=1. This choice preserves the old diagnostic and its baseline exactly as declared.

**Alternative B: the pinned source's two-state population.** With thick-filament fluxes disabled, R=0 and discretized initial B=0,M=1, the inspected source gives Mdot=−Bdot, hence M=1−B. Attachment becomes (1−B)f(x)(N−B). This keeps free heads and free sites distinct. The [held-calcium implicit derivation](source-two-state-implicit-derivation.md) provides a candidate positive backward-Euler operator and an analytic stationary root for this branch, without clipping or a settling loop. Its exact-arithmetic bound does not replace floating-point acceptance: independently reconstruct B_new from candidate masses and reject any B_new>N without clipping, renormalization or rounded replacement. The derivation records a cancellation-resistant W expression and separate residual checks; state/time remain unchanged until all gates pass.

**Recommended independent choice:** use B for a conserved attached population and M=1−B in a new held-N, two-state fixture. Keep N fixed throughout this first operator study, and state that source activation dynamics and series mechanics are absent. This choice uses the audited source population interpretation while retaining independently chosen numerical machinery. It is not an exact author-code trajectory replay.

**Falsifiable checks:** initialize nonzero admissible B and verify M+B=1; evaluate a state with nonzero J_B and verify Mdot=−J_B; at B=N verify Bdot≤0; at B=0 verify Bdot≥0. Compare analytic equilibrium with the computed bin moments without rescaling Q to one. The source moment initializer's B=.001,M=1 instead has conserved total 1.001; exact reproduction must preserve and disclose that path, while an independent simplex fixture should initialize consistently. Declining an imposed N below existing B is outside the held-N proof and requires a new capacity-transition rule.

## 3. Cooperative Eq. 13: printed dynamics or audited transfer dynamics

For clarity first consider R=0. Put S=1−B−M, J_1=a(Q)S and J_2=k_2 M. The extracted article Eq. 13 has Mdot=J_1−J_2. The inspected code includes Mdot=J_1−J_2−Bdot; with forcibly detached R it includes −(Bdot+Rdot). These are different transients. At Bdot=Rdot=0 they agree, so stationary comparison cannot resolve the convention.

For an article-only branch, preserve the literal verified equation and explicitly declare whether M is a phenomenological availability variable or a literal detached pool. For a code-population branch, retain the transfer term and S=1−B−M−R. **Do not silently repair the printed equation or drop the code transfer while claiming parity.** Defer cooperative release to a separate declared model: it is unnecessary for the held-N two-state operator.

**Falsifiable checks:** at a common state compute both right-hand sides; their difference must be exactly −(Bdot+Rdot) under common reaction/boundary definitions. For the transfer branch verify Sdot=−J_1+J_2. For the literal printed branch test its own boundary derivatives rather than imposing another branch's conservation identity. The [conditional population audit](cooperative-population-audit.md) shows that k2≥f1 O is a sufficient inward-boundary condition under nonnegative recruitment and the stated domain assumptions; the missing transfer does not by itself prove a violation for a reported parameter set. If recruitment uses signed Q, verify its permitted force domain separately.

## 4. Serial coordinate: physical γ or relative Γ

The article uses physical CE length and γphys=2Ns dps, with Δx=ΔLCE/γphys. The reproduction code uses relative input ε=ΔLCE/Lref and dimensionless Γ=s/(2dps), giving Δx=Γε. They are compatible only after declaring Lref=Ns s, so Γ=Lref/γphys. A direct comparison of the bare values of gamma is meaningless across these coordinate conventions.

**Recommended independent choice:** define the transport coordinate and its units once. A dimensionless kinetic operator can accept Δx directly and leave γphys unselected. A later dimensional series fixture must supply Lref, Ns, dps and the relative/physical conversion explicitly. No atlas centerline or Arm26 optimal-length input supplies the missing measured serial geometry.

**Falsifiable check:** prescribe a symbolic physical length increment and verify both mappings produce the same Δx when Lref=Ns s; verify dimensions and the transformed passive slopes. The inspected MAT's Γ=130 agrees with s=2.6 µm and a 10 nm stroke override, while its stored historical h=12 nm gives 108.33. These are source-version alternatives, not upper/lower uncertainty bounds. A replay cannot use stored h and Γ simultaneously as if they define the same coordinate.

## 5. PE softplus: article-shaped K=1 or code K=100

Let u=(LCE−LPE,0)/γphys be macroscopic CE displacement in the article's link-strain coordinate. Its displayed PE shape is cPE log(1+exp(u)), corresponding to sharpness one **in this coordinate**. The inspected code runtime below its linear cutoff uses

\[
F^{\rm code}_{\rm PE}(u)
=\frac{k_{\rm pe}}{K}\log(1+e^{Ku}).
\]

The inspected individual MAT has K=100; the fitting routine hardcodes K=1, and initialization uses a piecewise-linear PE. These are separate source paths. Code K is not an article coefficient named K, and 100 is not a publication median.

**Alternatives:** an article-shaped independent PE uses K=1 with a declared force prefactor and offset. A pinned runtime reproduction retains its actual K and linear-cutoff branch. A sharpness sensitivity varies K only as an authored modeling experiment. Do not choose a convenient intermediate K and call it measured.

**Falsifiable checks:** at u=0, code PE force is kpe ln2/K and its slope is kpe/2 before output scaling; slope at u is kpe/(1+exp(−Ku)). Matching article prefactor cPE requires cPE=Fscale kpe/K under the same dimensionless output convention. For physical CE length, multiply derivatives by 1/γphys and then by the independently verified SI force scale. If the physical softplus width is ℓ, K=γphys/ℓ; the single-link formula dps/ℓ applies to a different physical coordinate. Test the linear-cutoff value and slope as well. A nominal PE offset carries positive softplus force and is not a zero-force slack length.

**Recommended independent choice:** keep PE absent from the first held-N direct-CE operator. Before adding series mechanics, select one complete article-shaped or pinned-runtime law, including its initialization law and offset. Declare any law change used to make initialization and runtime consistent as an independent fixture choice.

## 6. Active force: raw moment or runtime positive transform

The article's normalized active force is Q/β. The inspected source runtime softens its raw active force, while output reports raw moments with Fscale; the approximate branch also clips. A raw output curve does not establish which force drove the series dynamics. Fscale=2 is algebraically compatible with β=.5 only under a common moment/normalizer; neither guarantees unit maximal isometric force.

**Alternatives:** an article-equation fixture uses raw Q/β. A pinned runtime replay keeps the actual softplus/clipping operations and reports both runtime and output force. An independent positive-force law uses an explicitly declared G(Q); it changes the model and its work/tangent interpretation.

**Falsifiable checks:** evaluate Q=0, a negative Q and a positive Q. Raw force is zero at Q=0; a softplus generally is not. For an unscaled raw argument the softplus derivative is 1/(1+exp(−KQ)); with output factors use the actual chain rule. Compare runtime/reporting moments at identical state, including the lowercase transport origin: a nonzero `lce0` causes a raw moment difference `lce0 B` in the inspected path. The inspected fixture's lowercase zero removes that particular discrepancy; uppercase `Lce0≈−10` is a passive onset and cannot be substituted.

**Recommended independent choice:** raw Q/β for the first declared equation fixture, with signed-force domain reported. If G is later selected for coupling, differentiate that same force in the series solve: its held-population slope is F0 G′(Q)B/γphys, not automatically F0 B/(βγphys). Compare the analytic residual derivative with a finite difference before any evolution. A source path that uses different force/tangent operations must be reproduced and disclosed, not silently made consistent under an exact-replay label.

## 7. Evidence-based values versus authored sensitivity

| Evidence class | What it can support | What it cannot support |
|---|---|---|
| Article table cells verified in the [committed pixel audit](original-plos-table-visual-audit.md) | Fixed nonhuman article inputs or a distinctly labeled componentwise-median fixture | Exact individual-fiber reproduction, joint parameter covariance, or human ranges |
| One pinned individual MAT and its field identity | That fixture's actual code values and historical/current coordinate discrepancy | Publication medians, fitted population intervals, or measured human coefficients |
| Rat preparation Ns=306±78 and reference sarcomere/length statistics | Conditional source-preparation serial-scale variability, with stroke assumption stated | A hard admissible interval, a whole human fascicle count, or an atlas map |
| Selected source-model dps, kCB and β | Explicit assumed reference-model scales | Independently measured human head density or stiffness |
| Varying K, Γ, passive offset, force transform or a fitted rate around a selected fixture | An authored sensitivity study with stated intervals and dimensionless units | A source confidence interval unless original uncertainty data identify that interval |
| Varying grid, strain extent or timestep | Numerical convergence evidence for the declared model/protocol | Anatomical, force-scale or constitutive calibration |

Do not interpret K∈[1,100] as an evidence-based uncertainty range: the endpoints arise from different code/article paths. Do not interpret the 108.33/130 coordinate alternatives as biological variation. Source-preparation means/SDs and independent fitted medians also cannot be combined into a synthetic specimen and called measured. Parameter-free algebra can be reviewed now; selecting values and sensitivity bounds is a separate recorded decision.

## 8. Decision receipt required before a release

Record a single manifest containing: target claim; article/code identities and verified rendering receipt; family and M convention; held/varying N protocol; density-versus-bin-mass measure; f/g sign and calcium units; transport coordinate and boundary rules; raw/transformed runtime and reported force; complete PE/SE laws and offsets; initialization path; force normalizer; and whether outputs are dimensionless, N or Pa.

For the next bounded mathematical step, choose **held N, O=1, conserved M=1−B, direct CE input and raw Q/β**, with independently implemented positive implicit kinetics and separately recorded source-informed rate inputs from the committed paper audit. This proposes a check of the new population operator without selecting PE, SE, physical γ, human force or area; it records no executed physical fixture and does not authorize a coupled release. A finite-series extension additionally requires initial force balance, complete force/tangent consistency, permitted compression domain, transport loss accounting and work balance; final-article/code parity remains its own claim to test.

A successful release would characterize one declared nonhuman or synthetic kinetic/circuit system. It would not erase the stationary fixed-activation saddle of the original continuum law, supply a descending overlap relation, qualify an anatomical arm, or establish in-vivo dynamic stability.
