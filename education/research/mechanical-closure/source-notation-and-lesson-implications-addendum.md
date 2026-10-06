# Source notation and limits of the active-stability lesson

**Blemker's optimal fiber stretch is λofl; its λ* is a passive exponential-to-linear transition. The frozen repository comparator defines λ* for a different purpose: optimal length divided by reference length. Those symbols must be distinguished even where their numerical benchmark values coincide.** This addendum clarifies provenance and prospective lesson wording; it changes no frozen protocol, result, numerical receipt, material, book or Lean file.

Read with [reference-architecture-source-review.md](reference-architecture-source-review.md), [active-stability-controls-results.md](active-stability-controls-results.md), [full-p2-p1-results.md](full-p2-p1-results.md) and the frozen [local comparator protocol](protocol.md). Prepared 2026-10-06 from those records and the original source already inspected; no new simulation or Git operation was performed.

## Three stretch parameters with different meanings

[Blemker, Pinsky and Delp (2005), original Tables 1–2 and equations 5–8](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) use **λofl** for optimum fiber stretch and **λ*** for the passive-law transition to a linear branch. Table 2 assigns both muscle parameters 1.4, while the aponeurosis/fascia transition is 1.03. Equality of two chosen muscle values does not identify their roles. The source's normalized muscle force and scalar fiber stress relation are

\[
f_{\rm total}=f_{\rm passive}+a f_{\rm active},\qquad
\sigma_{\rm fiber}=\sigma_{\max} f_{\rm total}\lambda/\lambda_{\rm ofl}.
\]

Here λ is the source's deviatoric fiber stretch. Table 1 marks passive branch changes separately; an optimal-length normalization is not generally the passive linearization threshold. These are source-model definitions and parameter choices, not measured atlas physiology.

| Meaning | Original source / existing record | Unambiguous notation for future prose |
|---|---|---|
| Optimal stretch in Blemker's model | Source λofl | λofl when describing that source |
| Passive exponential-to-linear transition in Blemker's muscle or tendinous tissue | Source λ*, with tissue-specific values | λpassive-transition, with source λ* stated explicitly |
| Optimal contractile length relative to the repository's chosen material reference | Frozen comparator's locally defined λ*=Loptimal/Lreference | **λrefopt := Lf,opt/Lf,0**; this is a proposed prose label, not a renamed code variable |

The source review's λopt is an editorial label for optimum/reference stretch, not a transcription of Blemker's printed notation. In its original-source summary, λopt corresponds to source λofl. In its proposed specimen map, it corresponds to the proposed λrefopt. Future teaching should write those correspondences explicitly rather than imply that Blemker calls both λ*.

For the repository comparator, use

\[
q=\lambda_f/\lambda_{\rm refopt},\qquad
W_{\rm active}=a\sigma_0\lambda_{\rm refopt}\Phi(q),\qquad
\Phi'=f_L,
\]

when describing the full-stretch diagnostic. The isochoric comparator substitutes J−1/3 λf for λf and is a separately declared finite-J model. These are the frozen comparator's equations with an explanatory label substitution; they are not Blemker's full constitutive law. The comparator varied active normalization while retaining passive normalization. It therefore did not adopt the complete source passive law or calibrate an active/passive material reference.

The original 1.4 comparator value refers to Blemker's **λofl** benchmark. It remains a dimensionless model convention, distinct from Holzbaur's **1.4 MPa** model specific tension and from the inverse-fitted repository σ0. Future wording must identify which stress measure/area convention a force coefficient uses. None of those values supplies a same-subject sarcomere reference map.

## What a stationary fixed-activation saddle establishes

The active-stability record reports accepted stationary candidates under prescribed caps, fixed activation and the current instantaneous law, followed by negative physical curvature in allowed zero-cap interior directions at stretch 1.25. This is stronger evidence than a negative tangent at the earlier nonstationary atlas field: residual qualification makes the second variation meaningful at the accepted candidate. It establishes an unstable stationary point for that declared conservative solve potential and control. It does not establish physiological instability in a living arm.

To transfer such a statement to dynamics, declare the state, inertia, series compliance, activation input/controller, material rate law and boundary control, and linearize their coupled equations. For P(F,a,z), the fast fixed-a,z tangent PF differs from the relaxed derivative PF+Pz dz_eq/dF. An isometric force–length curve across prepared equilibria does not choose between them. If the instantaneous conservative tangent is retained with positive inertia, its negative direction implies an undamped growing linear mode; that conditional implication does not calibrate a real muscle's internal dynamics. Ordinary damping alone provides no certificate that negative stiffness has become stable.

A descending scalar force–length slope also does not classify every constrained tissue mode. Prescribed end length removes a global axial degree of freedom, while the documented interior witnesses remain admissible. An end-separation spring can affect the global coordinate but contributes no direct work to a zero-cap interior perturbation. A distributed passive architecture can change equilibrium or local matrix response; neither effect is already established by an anatomical diagram.

## Weak pressure restriction and strict local volume admissibility

The projected finite-element test uses ker D, where D is the discrete P1 log-J coupling linearized at the held state. For a direction v, Dv=0 means the first variation of the sampled/integrated volume constraint vanishes against that pressure space. It does not enforce pointwise J=1 or preserve the nonlinear discrete constraint at finite displacement. A finite-step exactly constrained path generally needs higher-order correction, and its stability calculation must use the appropriate constrained/Lagrangian second variation. The reported projection remains a useful bounded diagnostic, not an exact continuum incompressibility proof.

The strict local witness is different. At one homogeneous material state, let H=u⊗m and impose u·F−T m=0. The determinant identity gives

\[
\det(F+\varepsilon H)=J\bigl(1+\varepsilon\,u\cdot F^{-T}m\bigr)=J.
\]

The straight rank-one path therefore preserves that state's volume exactly. It preserves J, which is near one in the finite-K comparator; it does not magically replace that state by one with J exactly one. Any volumetric potential depending only on J is constant on this path. The negative checked curvature is a concrete local admissible counterexample for the held material state. A positive minimum over a finite angular scan would not prove positivity over all directions/states. The local path is also not an assembled finite-body displacement satisfying every boundary condition; the independent global zero-cap witnesses provide the finite-specimen evidence.

## Geometry gates and two-grid checks have bounded scope

Positive corner/integration determinants and sampled 0.98≤J≤1.02 establish the declared finite sampling gates. Zero strict transverse boundary-crossing pairs establishes the checked crossing predicate on the represented facets. These checks do not certify positivity throughout curved quadratic elements or global injectivity of their exact image. Coplanar overlaps, containment and unsampled curved intersections remain outside those predicates. Near-unity sampled J does not exclude remote self-overlap. A stronger claim needs appropriate element-wide determinant bounds and global curved-boundary/injectivity analysis.

The two homogeneous coarse/fine grids pass the predeclared reaction, position, sampled-J and pressure-coupling checks. This supports implementation/patch consistency for those controls. Full pressure rank and two positive scaled inf-sup estimates do not prove a refinement-family inf-sup lower bound. Euclidean nodal Hessian eigenvalues also change normalization with mesh size, so their magnitudes are not a continuum spectrum convergence result. The controls supply no nonuniform atlas, contact, timestep or loaded-trajectory convergence. The nonsmooth passive cutoff at stretch one remains **UNASSESSED_PASSIVE_CUTOFF**, rather than inheriting a stability claim from its equilibrium shortcut.

## Prospective book and Lean wording

The following are proposed statements and proof obligations for a later evidence-backed revision. They are not edits or claims that the present Lean development proves new theorems.

| Lesson | Proposed wording / obligation |
|---|---|
| 01-force | A state can satisfy the declared free-force and reaction/work tolerances and still be a saddle. State the boundary control before discussing stability. |
| 03-energy | At fixed activation the active solve potential defines the comparator's conservative tangent; it is not automatically passive stored energy. Positive curvature requires a declared admissible variation space. |
| 04-muscle-physiology | Separate an isometric force–length relation from fast and relaxed incremental response. Define λofl, λpassive-transition and λrefopt separately; label measured, reference-model, fitted and authored quantities. |
| 09-continuum-medical | Distinguish discrete first-order weak volume restrictions, strict local determinant-preserving rank-one paths and exact finite-body incompressibility. A negative verified direction disproves the relevant positivity claim; a finite positive scan is not a theorem. |
| 10-fast-methods | A positive solver/preconditioner matrix is an algorithmic property; physical tangent qualification uses the actual model derivative. Two successful patch grids do not certify a stable element family or anatomical convergence. |
| 14-coupled-mechanics | Distinguish global series springs from distributed force paths and held from evolving contractile states. Dynamic stability requires the coupled Jacobian and actual control law. |
| 15-anatomical-apparatus | Require a declared specimen pose/reference map, passive rest metrics and force paths before interpreting atlas strain as sarcomere strain. Sampled geometry gates do not establish curved global injectivity. |

For future formalization, a determinant lemma can prove constant J along an exactly constrained rank-one matrix path; a conditional second-variation result can classify an exact stationary conservative state on a declared constraint space. Neither theorem should silently assume the numerical candidate is exactly stationary, that rounded vectors exactly satisfy their constraint, or that quadrature samples prove element-wide/global geometry. Formalized bounds or explicitly declared numerical hypotheses would be needed to bridge those gaps. Numerical receipts, human calibration and dynamic-model validation remain evidence obligations outside such algebraic statements.

The permissible conclusion remains narrow: the current instantaneous law has verified active-driven negative curvature at qualified controlled stationary states, including the strict local volume-admissible witness. The source notation correction changes its interpretation ledger, not its numbers or sign. Reference architecture, constitutive/internal-state calibration and nonuniform anatomical qualification remain unresolved.
