# Reference fascicles and passive architecture before atlas mechanics

**Recommendation: prepare a bounded, explicitly assumed long-head biceps architecture benchmark and a separate specimen measurement specification. The accessible sources establish feasible measurements and force paths; they do not provide a measured local reference map or passive material closure for the current atlas BICshort.** Preserve the stationary negative witnesses in [active-stability-controls-results.md](active-stability-controls-results.md). A reference change chosen to move those witnesses off the descending branch would be another assumption, not a calibration result.

Research access checked 2026-10-06. This is a new research proposal, with no production/material edits, coefficient selection, simulation reruns or atlas ingestion. Read alongside [recommendation.md](recommendation.md), [full-p2-p1-results.md](full-p2-p1-results.md) and [measured-fibre-property-map.md](../measured-fibre-property-map.md).

## Primary evidence and its usable scope

### A. Paired cadaver fascicle and sarcomere measurements

[Murray, Buchanan and Delp (2000), original PDF, Methods equations 1–4 and Table 2](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf), studied ten human upper extremities from nine cadavers: frozen, thawed 36–48 h, dissected and formalin-fixed for architecture. Frozen postures included extension and approximately 90° flexion. Their normalization is

\[
L_{f,\mathrm{opt}}=L_{f,\mathrm{meas}}\frac{2.8\,\mu\mathrm m}{\ell_{s,\mathrm{meas}}}.
\]

The 2.8 µm optimum is a source-adopted convention. Ten normalized fascicles were averaged per muscle; laser diffraction sampled origin, middle and insertion, with reported repeatability equivalent to ±0.05 µm. Table 2 gives optimal fascicle lengths, mean (SD): long head **12.8 (3.2) cm**, architecture n=6; short head **14.5 (3.2) cm**, n=8. Their own-study ranges in Table 3 are 7.8–16.6 cm (long), 9.6–18.8 cm (short): sample limits, not required human intervals. These are estimates after normalization, not measured fascicle lengths in a declared living rest pose. Preparation, rigor, posture and missing diffraction data limit transfer. Their excursion calculation assumes inelastic tendon/aponeurosis. The paper explicitly distinguishes muscle belly, musculotendon and fascicle lengths and notes the homogeneous fascicle/fiber assumptions. It supports paired measurements; its means cannot normalize this atlas subject.

### B. Live fascicle measurements are feasible, but do not identify optimum

[Nelson, Dewald and Murray (2016), original abstract and figure descriptions](https://pubmed.ncbi.nlm.nih.gov/27083062/) measured anterior long-head biceps fascicles and distal lateral-head triceps fascicles with extended-field-of-view ultrasound in both limbs of eleven healthy humans at three passive elbow postures. Biceps reliability ICC was .92–.95. The 4.5 cm transducer window was shorter than the biceps fascicles. The abstract supports a measurement route, not a full 3D map, sarcomere normalization or active reference state; exact posture details need full-protocol extraction before use.

### C. Live sarcomere sampling has anatomical and experimental uncertainty

[Adkins, Fong, Dewald and Murray (2022), original full text, Methods, Results and Discussion](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.817334/full) used second-harmonic-generation microendoscopy in human long-head biceps and flexor carpi ulnaris. Fourteen participants entered different variability comparisons. The across-image biceps set comprised 15 limbs: seven nonparetic stroke limbs plus both limbs of four unimpaired participants. Imaging was passive and seated; biceps posture was shoulder abduction 85°, elbow “extended 25°” in the source's wording, wrist neutral. Preserve that convention rather than silently translating it to a different angle definition.

The field of view was 82×82 µm. Total uncertainty was approximately **0.25 µm**, including anatomical variability and random error; computational phantom accuracy was approximately 0.02 µm. These are different quantities. The authors estimate roughly 7–8% uncertainty in optimal fascicle length/PCSA from sarcomere uncertainty alone. Small cohorts, one posture/state per muscle and sampling away from the inner tendon limit spatial extrapolation. This establishes a feasible local observation method; it supplies no same-subject map for the atlas. Its cited data repository was not readable in this audit, so no individual paired measurements were extracted.

### D. Internal aponeurosis geometry is measurable and posture-dependent

[Asakawa, Pappas, Drace and Delp (2002), original PDF, Methods, Results and Table 2](https://nmbl.stanford.edu/publications/pdf/Asakawa2002b.pdf) examined twelve living unimpaired humans (ten men, two women). MRI near full elbow extension (≤10° flexion) measured long-head belly **20±2 cm** and distal internal aponeurosis **7±1 cm**, occupying **34±4%** of belly length; these are group mean/SD. Axial spacing was 10 mm, limiting length resolution. Ultrasound insertion angles were measured in distal 0–2 and 2–4 cm regions; extension versus 90° flexion against 5% MVC load mixed posture and force changes.

| Region | Extension angle mean (SD), observed range | Flexion/load angle mean (SD), observed range |
|---|---|---|
| Anterior, distal 0–2 cm | 17 (4)°, 11–24° | 21 (4)°, 16–30° |
| Posterior, distal 0–2 cm | 14 (3)°, 8–18° | 18 (4)°, 12–24° |

These are insertion angles relative to the aponeurosis, not a uniform angle relative to the muscle axis. They constrain an assumed architecture family; they do not measure sarcomeres, passive sheet thickness, stiffness or the atlas short head.

### E. Regional shortening offers an architecture validation observable

[Pappas et al. (2002), original PDF, abstract, Methods and Results](https://nmbl.stanford.edu/publications/pdf/Pappas2002.pdf) used cine phase-contrast MRI in twelve living humans during repeated elbow flexion against 5% and 15% MVC loads. Anterior shortening averaged approximately 21%; distal centerline shortening was 7.3%/3.7%, versus midportion 26.3%/28.2% for the two loads. These are regional tissue-motion observations under that protocol, not direct local sarcomere stretch or a load-independent material law. They give an independent regional observable for an eventual architecture experiment. A homogeneous block or a different posture cannot claim agreement by matching only the total shortening.

### F. Original continuum architecture benchmark and stress convention

[Blemker, Pinsky and Delp (2005), original PDF, equations 2, 4–8, Tables 1–2 and sections 2.2–2.4](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) modeled an idealized, axisymmetric human long head with spline fascicles, proximal/distal aponeuroses and external fascia. The 15 cm model underwent 4 cm quasistatic lengthening at 15% activation. Using deviatoric fiber stretch λ, its constitutive structure includes

\[
W_{\rm iso}=G_1 B_1^2+G_2 B_2^2+W_3(\lambda,a),\qquad
\lambda W_{3,\lambda}=\sigma_{\rm fiber},
\]
\[
\sigma_{\rm muscle}=\sigma_{\max}(f_{\rm passive}+a f_{\rm active})\lambda/\lambda_{\rm opt}.
\]

For tendinous tissue, Table 1 uses zero axial stress at λ≤1, **L1[exp(L2(λ−1))−1]** in the toe region, then a C1 linear continuation. Table 2 assigns muscle G1=G2=500 Pa, σmax=0.3 MPa, λopt=1.4; aponeurosis/fascia G1=G2=50 kPa, L1=2.7 MPa, L2=46.4, transition stretch 1.03. These are reference-model parameters, not same-specimen measured coefficients. Architectural variants isolate uniform lengths, length variation, curvature, aponeurosis compliance and fascia. Fascia changed anterior strain distributions; this was not a stability test. **Dimensionless λopt=1.4 is distinct from Holzbaur's 1.4 MPa specific tension.**

### G. The external bicipital aponeurosis is a distinct force path

[Ocran et al. (2025), original abstract](https://pubmed.ncbi.nlm.nih.gov/39746286/) tested human bicipital aponeurosis connecting distal tendon to antebrachial fascia: eight fresh-frozen specimens, age 82±12 years, five female, five right. Approximately 7×7 mm samples came from proximal/middle/distal regions, with collagen orientation retained. Biaxial testing used ten preconditioning cycles at 9% strain, 1%/s, followed by loading to 12% at 1%/s. Linear-region modulus was greater longitudinally. The readable abstract provides no numerical modulus, tissue thickness, test-temperature or full stress/area convention; those remain unextracted. This supports an anisotropic calibration protocol, not a replacement constant. The external lacertus/bicipital aponeurosis must not be conflated with D's internal distal aponeurosis.

[Snoeck et al. (2014), original abstract](https://pubmed.ncbi.nlm.nih.gov/24414231/) studied dissections/sections from fifty human cadavers and observed a deep lacertus layer throughout. Morphology did not significantly correlate with upper-limb morphometrics. Preparation and numerical geometry are unextracted from the abstract. Scaling a lacertus sheet from arm circumference alone is therefore unsupported.

### H. Neighboring-muscle interaction is evidence of a path, not a spring constant

[Yoshitake et al. (2018), original abstract](https://pubmed.ncbi.nlm.nih.gov/29776820/) measured shear-wave responses in living biceps/brachialis in thirteen healthy young men under passive supination/neutral/pronation and elbow positions of 100°/160° in their convention. Regional neighboring-muscle responses changed with forearm rotation, supporting mechanical interaction. Elastography measurements alone do not supply absolute transferred force, a network stiffness, a universal coupling fraction or the required constitutive shear coefficients.

## Explicit reference map: proposed derivation, not extracted human parameters

For a material fascicle path γi in a measured reference pose, define its arc length Lf,0,i and unit tangent a0(X). Keep tendon/aponeurosis portions outside that contractile arc. If the path represents a continuous serial fiber with a representative sarcomere length ℓs,0,i, the declared homogenization assumptions give

\[
N_{s,i}\simeq L_{f,0,i}/\ell_{s,0,i},\qquad
L_{f,\rm opt,i}\simeq N_{s,i}\ell_{s,\rm opt},\qquad
\lambda_{\rm opt,i}=L_{f,\rm opt,i}/L_{f,0,i}.
\]

This is A's normalization generalized symbolically. It assumes fascicle/fiber correspondence, unchanged serial sarcomere number and a representative serial sarcomere length. Fascicles with intrafascicularly terminating fibers need a different load-sharing/serial model. A global fascicle average also does not identify a pointwise sarcomere field.

For an explicit local co-deformation hypothesis, with full material fiber stretch λf(X)=|F a0(X)|, define

\[
q(X)=\frac{\ell_s(X)}{\ell_{s,\rm opt}}
\simeq\lambda_f(X)\frac{\ell_{s,0}(X)}{\ell_{s,\rm opt}}
=\frac{\lambda_f(X)}{\lambda_{\rm opt}(X)}.
\]

Only paired geometry/sarcomere observations and the declared homogenization hypothesis can turn this into a constitutive normalization. Using isochoric stretch instead would be a separately declared finite-J convention. An architecture average plus an unrelated population sarcomere average is a synthetic prior, not a measured local field. The source-adopted optimal sarcomere convention also needs its own uncertainty and force–length validation.

The reference *image pose* need not be a stress-free *passive material state*. Tendon slack length, muscle passive recruitment/rest length and fascia rest metric must be measured or explicitly assumed independently of the active optimum. Setting q=1 or passive stress=0 everywhere at an imaging pose would add unverified constraints. If images are taken under active load, their activation/internal state, series extension and prestress enter the reference reconstruction.

Preserve the existing facts: Arm26 BICshort **0.1321 m** is a model input; the atlas-authored arc **0.14385179 m** is geometry. Their ratio does not measure sarcomere stretch, and selecting it as λopt would silently equate the arc with a contractile fascicle in a specified pose. The fitted **8.708387 MPa** coefficient remains inverse fitted, not inferred from these geometry sources.

For measurement uncertainty, q=λf ℓs,0/ℓs,opt gives the first-order relation

\[
\delta q/q\simeq\delta\lambda_f/\lambda_f+
\delta\ell_{s,0}/\ell_{s,0}-\delta\ell_{s,\rm opt}/\ell_{s,\rm opt}.
\]

Use covariance or interval propagation appropriate to the actual measurements; do not assume independent errors or treat group SD as a patient confidence interval. Spatial registration, probe depth and fascicle-path errors belong in this budget too. C's uncertainty estimate is a warning against claiming sub-percent physiological normalization from geometrically precise splines.

## Smallest bounded architecture experiment

The immediate artifact can be a **controlled long-head-inspired virtual specimen**, explicitly synthetic. It is separate from the qualified 0.14×0.02×0.02 m block and from the atlas short head. Keep the existing block/state/control witnesses as immutable baseline evidence. A future simulation requires its own predeclared protocol; none is run here.

1. Declare a reference pose, full versus isochoric fiber stretch, reference length distribution, passive rest metrics, activation/internal state and all units before constructing geometry. Choose either a published-model reproduction using F's own conventions, or a new same-specimen measurement route. Do not describe a hybrid as a reproduction.
2. Use D's internal-aponeurosis fraction and regional insertion-angle observations only as declared population-informed geometry bounds. Record source SD and observed angle ranges separately. No source supplies the complete proximal sheet, 3D fascicle endpoints/curvature, sheet thickness or external fascia attachments; any resulting interpolation is authored. BICshort transfer is excluded.
3. Connect continuous muscle–aponeurosis–tendon regions or explicitly declared interfaces, with deformable passive degrees of freedom and traction/work continuity. Distinguish intramuscular matrix shear, internal aponeuroses, free tendons, enclosing fascia and lacertus-to-forearm paths. Fixed targets or arbitrary zero-length attachments do not qualify these paths.
4. Keep the contractile law/reference convention fixed while adding one force path at a time; keep passive paths fixed while varying the measured/assumed reference map. A matched-force comparison requires an independently fixed force/stress calibration and a declared held internal state. Do not re-fit σ0 to recover the previous generalized reaction.
5. Apply the existing full force, pressure, positive-J and reaction/work gates before interpreting any spectrum. Then report regional fascicle lengths, insertion angles, internal-sheet strain and transverse/shear response, as well as cap force. An eventual source-protocol comparison should use E's regional observable with its original loading/posture and uncertainty; a new synthetic fixture only demonstrates mechanism.
6. Retain original negative directions and scan the actual local constrained tangent. For finite discrete modes report physical normalization and mesh dependence; a converged finite specimen with no sampled negative mode is not a material ellipticity theorem.

### Why a complete passive path is necessary but cannot be presumed to cure the witness

This is a mechanical inference from the retained witness, not a finding of F or G. The local acoustic quadratic form at a material point depends on that point's constitutive tangent and held state. An end spring or an external sheet contributes no direct local tangent inside an unchanged muscle region. A virtual displacement supported strictly inside that region also produces no direct boundary-sheet work. Consequently those supports cannot change the same tested local rank-one curvature at the same F,a,z. They may redistribute equilibrium and move operating stretches, constrain finite specimen modes, or couple through intramuscular material that actually changes the local tangent. Each is a distinct hypothesis requiring requalification.

Thus distributed passive architecture is required for credible force transmission; **it is not evidence that remote supports restore strong ellipticity of the unchanged instantaneous law**. If the active interior witness persists after matched-state passive closure, the contractile/internal-state problem remains. Increasing bulk stiffness cannot repair its strict volume-admissible rank-one path, as the existing diagnostic already establishes. Adding local matrix reinforcement or a nonlocal internal length changes the constitutive model and requires source-backed calibration; it cannot be hidden as geometry.

## Missing data before a specimen-backed constitutive mapping

| Required field | Why it is needed | Current status |
|---|---|---|
| Identified muscle head, subject/specimen, shoulder/elbow/forearm pose and contraction state | Biceps length depends on multiple joints and state | No same-specimen atlas mapping |
| Registered contractile fascicle paths/endpoints and local sarcomere observations in that pose | Defines a0, Lf,0 and q; resolves tendon versus muscle arc | A–C establish methods; paired atlas measurements absent |
| Optimal sarcomere/force–length convention and uncertainty | Converts measured lengths to force-generating reference | Source conventions available; current subject not calibrated |
| Passive muscle rest/recruitment state and longitudinal/transverse/shear response | Separates active optimum from passive storage | Not established by architecture images |
| Internal/external sheet area/thickness, collagen direction, rest metric and interfaces | Determines distributed stiffness and traction continuity | D gives partial geometry; full force-path data missing |
| Free-tendon slack/reference lengths, area and force–extension behavior | Determines series state and compliance | Arm26 inputs are reference-model parameters |
| Biaxial/shear, rate, hysteresis and preparation/temperature records for relevant passive tissue | Prevents transfer of unrelated material constants | G supplies a protocol, not extracted numeric closure |
| Neighboring fascia/attachment geometry and load-sharing measurements | Determines lateral boundary interaction | H establishes interaction; quantitative closure missing |
| Contractile fast/relaxed held states and time evolution | Distinguishes isometric branch slope from transient stiffness | Remains the current active-mechanics blocker |

No accessible source in this review supplies all these fields for one upper-arm specimen. The feasible near-term outcome is a transparent architecture benchmark plus a measurement specification, followed by constitutive-state qualification before atlas integration. No arm phenotype, stabilizing coefficient, sheet thickness, optimal/reference stretch or universal coupling fraction is selected here.

## Access record

Original Stanford-hosted Murray/Asakawa/Pappas/Blemker PDFs and the original Frontiers Adkins article were readable. Nelson/Ocran/Snoeck/Yoshitake primary abstracts were readable; abstract-only limitations are retained. Direct Ocran publisher and Snoeck2021 DOI requests returned internal errors; no full-text result from those requests is claimed. PMC requests for Adkins and Nelson returned browser challenges and were abandoned; the separate public publisher article and primary abstracts were used. Adkins's referenced repository DOI returned an internal error, so no repository files or individual measurements are claimed. No payment, authentication, access bypass or network setting changes occurred.
