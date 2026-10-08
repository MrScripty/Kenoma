# Connect fibre architecture to force without inventing strength

The unresolved anatomical requirement is a source-bound map from fibre architecture and measured force to the active continuum coefficient. Kenoma currently fits model-reference actuator forces while its calibration states retain unresolved stationarity and compression. That fit must not be renamed physiological specific tension.

This lesson supplies the missing bookkeeping prerequisite: distinguish fibre number from fibre area, parallel groups from sections in series, nominal from Cauchy stress, and projected from unprojected PCSA. It does not repair the continuum solve or supply a new anatomical dataset. All lab numbers are authored examples, not calibration inputs.

## Retain the failed calibration evidence

At [PR11 commit 0bed56a](https://github.com/MrScripty/Kenoma/blob/0bed56a86e771b2187e1590e760357f31ec3ef37/education/book/chapters/15-anatomical-apparatus.md), the fixed-end fits use approximately 3.60, 8.71, and 20.38 MPa for brachialis, short biceps, and long biceps. The source documents corner volume ratios near 0.56–0.62 and free nodal force components of 64.07, 52.06, and 54.22 N at those frozen calibration states. A successful reduced force match is therefore not an equilibrated full-nodal material calibration.

No fit, material coefficient, calibration state, accepted trajectory, proof manifest, reference asset, or failure threshold is changed by this contribution. Resolving local compression and full displacement/pressure stationarity remains an upstream gate. The analytic examples below cannot overrule it.

## Decide which area a measurement describes

For a declared parallel reference bundle with volume V₀ in m³, representative fibre length Lf₀ in m, and contractile volume fraction φ₀, the idealization Acontractile₀ = φ₀ V₀ / Lf₀ gives area in m². It requires a meaningful representative length and fraction. A tapered whole belly, distributed fibre terminations, varying orientations, or nonuniform packing need a spatial integration and load-path model; inserting their total volume into this formula does not establish those conditions.

PCSA definitions must travel with the values. [Murray, Buchanan and Delp (2000), Methods and Table 2](https://research.me.udel.edu/buchanan/PDF_Files/Murray,%20Buchanan,%20Delp,%20JB%202000.pdf) computes PCSA from volume divided by optimal fascicle length, then uses the pennation cosine separately in moment capacity. Its elbow architecture study used ten upper extremities from nine cadavers, with exclusions and different sample counts by muscle. In contrast, [Ward and Lieber (2005), equation 1](https://muscle2.ucsd.edu/pubs/pdf/Ward_JB_2005a.pdf) includes the cosine in PCSA. A projection included in an imported area must not be multiplied again.

Use three explicit metadata fields before combining a force and area:

- area convention: fibre-normal or already tendon-projected
- stress basis: contractile area or an effective whole-muscle area
- configuration: reference/optimal or current, with the stated stretch and volume ratio

An effective whole-muscle specific tension may already include noncontractile fractions through its area definition. Multiplying it by φ₀ again double-counts that reduction. Conversely, a single-fibre measurement does not automatically define a whole-muscle effective stress. A smallest fibre diameter is not a measured circular cross-sectional area, and a fibre count fraction is not an area fraction.

## Sum parallel fibre groups by area

For group k with Nk fibres, reference fibre area ak₀, nominal axial stress Pk, and current tendon-direction cosine ck, use

    A₀ = Σk Nk ak₀
    T = Σk Pk Nk ak₀
    Ttendon = Σk Pk Nk ak₀ ck

This is a declared independent parallel-force decomposition. It omits passive matrix force, pressure traction, lateral exchange between groups, and curved aponeurosis geometry. It cannot infer recruitment or force–velocity properties from fibre typing alone.

Two synthetic groups with equal counts of 50,000 and areas of 1,000 and 2,000 µm² have area shares 1/3 and 2/3. At nominal stresses of 100 and 300 kPa, total area is 150 mm² and force is 35 N. The count-average stress gives 30 N and is the wrong weighting for this example. Different angles likewise require force-weighted projections, not an unqualified average angle.

[Mattiello-Sverzut and Martins (2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9925190/) assessed isokinetic elbow performance in 32 volunteers; usable biceps morphology samples came from 26 participants (9, 8, and 9 across the three age groups). Fibre subtypes and smaller diameters describe that morphology subset, not all 32 participants. The study supports keeping type and size distinct; it does not provide a subject-matched spatial packing map for the atlas. [Bottinelli et al. (1996)](https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1996.sp021617) reports type- and temperature-dependent single skinned-fibre mechanics. Its 12 °C load-clamp protocol is not a body-temperature whole-biceps calibration. Neither paper's parameters are imported here.

## Track the same material cut during shortening

Let F be a locally homogeneous orientation-preserving deformation gradient, J = det F > 0, f₀ a reference unit fibre, λ = |F f₀| > 0, and f = F f₀ / λ. For a reference cut normal to f₀ with area A₀, the current oriented area vector is a = J F⁻ᵀ f₀ A₀. Its projection normal to the current fibre is

    A⊥ = a · f = J A₀ / λ.

A⊥ is a projected material-cut area. In a shear-free straight bundle it is the familiar orthogonal cross-sectional area. With shear, the actual deformed cut may be oblique and have a different surface area. The formula is not a global statement about an anatomical imaging plane or a curved heterogeneous belly. Spatially varying F requires local integration.

The existing active law in [anatomical-material.mjs](https://github.com/MrScripty/Kenoma/blob/0bed56a86e771b2187e1590e760357f31ec3ef37/education/web/anatomical-material.mjs) differentiates a full-stretch potential. With p = aactivation σ₀ fL(λ), its active first Piola tensor is p f ⊗ f₀, and its active Cauchy tensor is (p λ/J) f ⊗ f. Thus

    σfibre = p λ / J
    Tactive = σfibre A⊥ = p A₀.

Both p and σfibre have units Pa, but they divide force by different areas. The lab calls the scalar p “nominal stress P” and keeps it fixed initially. With A₀ = 80 mm², p = 300 kPa, J = 1 and λ = 0.8, A⊥ grows to 100 mm² and σfibre falls to 240 kPa. Axial force stays 24 N. At 30° pennation the projected component is about 20.78 N. There is no fibre-count increase and no extra bulge multiplier.

Holding Cauchy stress fixed instead would produce a different force as area changes. That is a different constitutive prescription, not a universal strength bonus. Enabling the existing authored fL curve in the lab explicitly changes p and therefore force. In the anatomical model, activation, length, passive stresses, pressure and attachments jointly matter; this calculation is only its active material-cut identity.

[Raiteri, Cresswell and Lichtwark (2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4974924/) examined human tibialis anterior with three-dimensional ultrasound and found spatial shape and architectural changes during isometric contraction. It motivates regional rather than uniform geometry. It is neither biceps anatomy nor proof of exact local J = 1. The volume controls here are prescribed and have no biological acceptance range.

## Follow a variable cross section through a series load path

Under a one-dimensional static section resultant convention, a cell between cuts i and i+1 obeys

    Ti+1 − Ti + Qi = 0,

where Qi is net axial force from lateral or external loading on that cell. With no lateral load or inertia, axial force is the same at every cut. A 100–200–100 mm² reference-area sequence carrying 30 N therefore has nominal section stresses of 300–150–300 kPa. A thicker middle section does not manufacture an additional end force.

If one assigns 300 kPa independently to each cut, the resulting 30–60–30 N sequence needs −30 N and +30 N lateral forces in the two intervening cells. Such exchange could belong to a resolved ECM/matrix path, but it must be represented and balanced. It cannot be inferred from the taper alone. The scalar sequence is a necessary force-balance example, not a compatible displacement field, three-dimensional equilibrium, shear-stress solution, or material fit.

Internal paired forces cancel in the whole-body resultant. Their power does not generally vanish: q v₁ + (−q) v₂ = q(v₁−v₂). An ECM coupling can store or dissipate energy when adjacent points move differently. A no-slip tie, compliant bond, frictional slip and damage law are distinct constitutive choices; none is supplied by the arithmetic identity.

[Huijing and Baan (2003)](https://pubmed.ncbi.nlm.nih.gov/12571138/) found differing proximal/distal tendon forces in maximally active rat extensor muscles with connective tissues retained and controlled relative length changes. This is evidence for additional force paths, not a human-biceps coupling coefficient. [Zhang and Gao (2012)](https://pubmed.ncbi.nlm.nih.gov/22682257/) used a two-dimensional fibre/endomysium model to study shear transfer and tapered fibre ends. Its model supports the need to declare interface mechanics; it does not calibrate Kenoma's matrix.

## Density and fluid mechanics remain separate inputs

Mass density maps volume to mass, not area directly to force. Ward and Lieber's fixation/hydration experiment reported preparation-dependent human muscle density and warned of PCSA errors from mismatched assumptions. Their fixed-tissue results are not live biceps density measurements. A later mass-based estimate must retain species, tissue preparation, hydration and the density uncertainty rather than silently treating 1,060 kg/m³ as universal.

[Sleboda and Roberts (2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6983394/) applied a pressure cuff during isolated bullfrog semimembranosus contractions. The effect on measured force changed with muscle length, and physical ECM analogues helped interpret the result. The experiment does not identify a human biceps pressure law or a unique mechanism. It does show why fluid–matrix interactions cannot be represented by “more blood equals more strength.”

Intracellular/interstitial fluid, blood inside vessels, solid-matrix stress, incompressibility pressure and measured intramuscular pressure are different quantities. The original [cat fast/slow muscle pressure and perfusion study](https://pubmed.ncbi.nlm.nih.gov/6542507/) varied perfusion conditions and examined isometric endurance. Its experimental scope requires vascular boundary conditions and timescale-dependent physiology; a bulk penalty contains neither. No numerical perfusion, permeability, ECM bonding, blood-volume or edema parameter is imported in this lesson. Exercise pump and chronic growth are not acute material-area transformations.

For a future coupled fluid model, record the conserved constituents, fluid pressure definitions, permeability and boundary conditions, vascular compartments, compressibility assumptions, and the drain/undrain time scale. Validation must distinguish local from global volume, and conservation from accurate geometry. A shared external skin/fat envelope must enclose the assembled tissues and obey its own interface/contact conditions; seven separately expanding bellies do not define it.

## Verification and next acceptance gate

The contribution tests scalar units and transformations, the explicit PCSA/packing conventions, heterogeneous sums, taper equilibrium and lateral force balance. A separate contract test compares the active-stress map against the unchanged repository material operator, including shear and rigid rotation cases. Twelve Node tests pass. Seven SymPy identities check declared algebra separately, including the cofactor projection and exchange-power identity; symbolic simplification is not a Lean kernel proof.

Six contracts in `ArchitectureForce.lean` also compile under the pinned Lean 4.19.0 toolchain and mathlib revision, with warnings treated as errors. They establish the declared scalar material-cut force identity, two-group area weighting, one-time projection, projected group sum, telescoping series balance, and paired-force power identity. They do not prove the geometric premises, Nanson's formula, arbitrary-group numerical implementation, equilibrium, or biological suitability. `claims.json` states these boundaries. The six contribution contracts are not registered in the book's existing 109 checked declarations; independent review and book integration remain separate gates.

The original private-review browser attempt was blocked by refusal of the local preview. Subsequent bounded hosted checks in [run 37743673184](https://github.com/MrScripty/Kenoma/actions/runs/37743673184), at exact commit `143ac8863cd8a5be736e2c455cac9605c2e20a1f`, passed `education/tests/architecture_force_browser.py` in real Chromium at 1280×1000 desktop and 393×852 mobile sizes, including the no-JavaScript fallback. The recorded agent visual review passed all five JPEG quality-85 captures of this analytic lab. Owner release review, full-book integration and anatomical acceptance remain separate; full-book build and deployment were skipped. The automated receipt's `pending human inspection` marker remains unchanged, and later source heads require their own hosted qualification.

The next anatomical implementation gate is still an equilibrated, locally admissible calibration specimen with an adequate displacement/pressure space. Only after that gate should a source-bound architecture dataset be mapped into σ₀ or a replacement law. Every proposed parameter should carry the source, specimen/protocol, area/stress convention, units, uncertainty, transformation and destination equation. Independent attachment, tendon, cartilage, fat and shared-skin validation remain necessary for the full anatomical arm goal.
