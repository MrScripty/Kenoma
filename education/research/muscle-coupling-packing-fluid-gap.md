# Muscle coupling, cross-sections, packing, and fluids: evidence and teaching gaps

Research checkpoint: 2026-10-06. Coverage inspected at `05fd23cdb6a414415f1117fced93443aa9936c48`, the accepted connected-specimen endpoint repair. This note adds no solver, constitutive law, coefficient, acceptance limit, browser control, or book-release change. The accepted endpoint repair remains frozen. Arm-specific fibre-type, PCSA, shortening-velocity, and activation-time calibration belongs to the separate measured-property workstream.

The question is what an expanding muscle cross-section means. During a contraction, a larger outline does **not by itself establish more fibres, denser contractile packing, greater strength, separation between cells, or blood filling newly opened gaps**. Each interpretation requires a different measurement. The useful first distinction is between deforming existing material, changing the slice used to observe it, exchanging fluid, and growing tissue.

## Existing coverage and the missing explanation

| Existing source | What it already supplies | What remains to teach or qualify |
| --- | --- | --- |
| [Muscle physiology chapter](../book/chapters/04-muscle-physiology.md) | Excitation versus activation; line force versus spatial shape; a constant-volume cylinder intuition; spatially varying architecture. | Following a material bundle versus observing a fixed or oblique slice; why apparent area is not automatically a count or strength measurement. |
| [Measured fibre property map](measured-fibre-property-map.md) | Area and pennation conventions; assumed aggregation; fibre packing versus myosin packing; fluid and ECM mechanisms explicitly deferred. | A source-bound account of shear transfer, transverse restraint, fluid compartments, and time-dependent interpretation. Its arm-specific numerical extraction is outside this note. |
| [Progressive muscle labs](progressive-muscle-labs.md) | Geometry, local volume, shear, aggregation, force laws, dissipation, then anatomical coupling; unresolved displacement/pressure qualification. | An intermediate sequence that makes slice geometry and coupling understandable before biological parameter fitting. |
| [Serial specimen chapter](../book/chapters/09d-serial-specimen.md) | Two homogeneous blocks with a declared fixture and spacer. | A bilateral fixture is not an endomysial network or a continuous aponeurosis. |
| [Connected passive prototype](../AXISYMMETRIC_PROTOTYPE.md) | A connected finite-compliance passive continuum, local Jacobian and reaction checks, qualified end faces. | It has no active fibres, measured muscle architecture, vascular network, or interstitial transport. Its deformation is passive-material evidence only. |

The main gap is explanatory and evidential: connect these distinctions to primary studies while preserving the limits of the implemented teaching models. A new biological law is not required to close the explanation gap.

## Selected primary evidence and access limits

These are selected original experiments and original continuum studies, not a systematic review. Access was checked on the checkpoint date. “Abstract” means the original paper's abstract, not a secondary summary. No numerical result below is adopted as a Kenoma parameter. Species, preparation, loading, and observable matter when deciding whether a result can transfer.

| Source and original study | Evidence used here | Access and limit |
| --- | --- | --- |
| [Trotter and Purslow (1992), *Functional morphology of the endomysium in series fibered muscles*](https://pubmed.ncbi.nlm.nih.gov/1608046/), DOI `10.1002/jmor.1052120203` | Cat biceps femoris morphology and geometrical reasoning: overlapping, short tapered myofibres and endomysial collagen organization compatible with transfer through shear. | Abstract read. Structural support for a load path, not a measured universal fraction of lateral force or a human-arm modulus. |
| [Smith, Fowler-Gerace and Lieber (2011), *Muscle extracellular matrix applies a transverse stress on fibers with axial strain*](https://pubmed.ncbi.nlm.nih.gov/21450292/), DOI `10.1016/j.jbiomech.2011.03.009` | Individual fibres and ECM-containing bundles were dimensionally tracked during axial strain. Single-fibre volume was approximately conserved; bundle volume decreased with stretch, implicating transverse ECM loading. | Abstract and figure captions read; PMC full text challenged access. The record also links a finite-strain/Poisson-ratio comment and an author-name erratum. Do not turn this short study into a universal bundle compressibility law. |
| [Azizi and Roberts (2009), *Biaxial strain and variable stiffness in aponeuroses*](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/jphysiol.2009.173690), DOI `10.1113/jphysiol.2009.173690` | Biplanar fluoroscopy of turkey lateral gastrocnemius in situ: active loading produced longitudinal and transverse aponeurosis strain; longitudinal stiffness varied with transverse strain. Passive loading had a different strain pattern. | Publisher abstract read; full-text fetch failed. Supports a sheet with biaxial mechanics, not transplantation of turkey stiffness to human biceps. |
| [Sleboda and Roberts (2017), *Incompressible fluid plays a mechanical role in the development of passive muscle tension*](https://pubmed.ncbi.nlm.nih.gov/28123108/), DOI `10.1098/rsbl.2016.0630` | A fluid-filled physical model and osmotic volume manipulation in isolated bullfrog semimembranosus linked fluid volume and collagen-like restraint to passive force. | Abstract and figure captions read. Osmotic soaking and a physical analogue are not evidence that normal contraction fills muscle with blood. |
| [Sleboda and Roberts (2020), *Internal fluid pressure influences muscle contractile force*](https://pubmed.ncbi.nlm.nih.gov/31879350/), DOI `10.1073/pnas.1914433117` | A pneumatic cuff applied during isolated bullfrog semimembranosus contraction changed isometric force. The response was negative at shorter lengths and positive at longer lengths; reinforcing-fibre physical models reproduced the qualitative sign change. | Abstract and figure captions read; PMC challenged access. Published in the 2020 volume, online December 2019. External cuff loading is not a direct measurement of every internal fluid compartment. |
| [Lutjemeier et al. (2005), *Muscle contraction-blood flow interactions during upright knee extension exercise in humans*](https://pubmed.ncbi.nlm.nih.gov/15557016/), DOI `10.1152/japplphysiol.00219.2004` | Continuous femoral-artery Doppler during rhythmic knee extension and early recovery: contraction-induced flow impedance and relaxation-related enhancement had workload-dependent net effects. | Abstract read. Blood **flow** in a supplying artery does not measure intramuscular blood **volume**, interstitial water, or cell spacing. |
| [Damas et al. (2016), *Early resistance training-induced increases in muscle cross-sectional area are concomitant with edema-induced muscle swelling*](https://link.springer.com/article/10.1007/s00421-015-3243-4), DOI `10.1007/s00421-015-3243-4` | Vastus lateralis ultrasound area, echo intensity, function and damage markers during a training study suggested early area gain was not purely hypertrophy. | Publisher abstract read; subscription preview. Swelling was inferred with accompanying measures, not partitioned into blood, interstitial and intracellular volumes. No universal waiting period follows from this protocol. |
| [Blemker, Pinsky and Delp (2005), *A 3D model of muscle reveals the causes of nonuniform strains in the biceps brachii*](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf), DOI `10.1016/j.jbiomech.2004.04.009` | An original anisotropic continuum with along-/cross-fibre shear, a spatial fibre-direction field, and aponeurosis/fascia regions was compared with regional low-load human biceps MR strain data. Architecture variations changed predicted strain distributions. | Full paper read, especially §§2.1–2.4 and discussion. Quasi-static elastic, simplified architecture and limited comparison; not individual-cell or perfusion validation. |
| [Ryan et al. (2020), *The Energy of Muscle Contraction. II. Transverse Compression and Work*](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full), DOI `10.3389/fphys.2020.538522` | Original three-dimensional continuum simulations: longitudinal force under transverse loading depended on muscle length, pennation and loading direction; internal model pressure did not simply equal the applied transverse load. | Full paper read, especially methods and discussion. Model results and comparisons with cited experiments must be distinguished. Its volume-energy pressure is not a resolved vascular or interstitial pressure field. |

Further primary leads were identified but **not audited for their methods/results here**: [Passerieux et al. (2007), perimysial continuity from myofibres to tendons](https://pubmed.ncbi.nlm.nih.gov/17433715/) (`10.1016/j.jsb.2007.01.022`; bibliographic identity verified, readable paper/abstract unavailable); [Sharafi and Blemker (2010), fibre/fascicle micromechanics](https://pubmed.ncbi.nlm.nih.gov/20846654/) (`10.1016/j.jbiomech.2010.07.020`); and [Spyrou, Agoras and Danas (2017), Voigt-type muscle homogenization](https://pubmed.ncbi.nlm.nih.gov/27884495/) (`10.1016/j.jtbi.2016.11.018`; both latter identities verified in Ryan's references, retrieval unavailable). [Raiteri et al. (2016), three-dimensional tibialis anterior geometry](https://pmc.ncbi.nlm.nih.gov/articles/PMC4974924/) (`10.7717/peerj.2260`) is already summarized in the measured-property map; current full-text retrieval failed, so that summary is not promoted into a newly audited claim. These are retrieval gaps, not contradictory evidence.

## How coupling permits relative deformation

“Fibres move relative to each other” needs a mechanical definition. Endomysium surrounds individual muscle cells; perimysium organizes connective tissue around fascicles. Relative axial displacement across neighboring material paths produces **shear deformation** in their connecting material. Bonded material can sustain that shear while remaining continuous. It need not mean frictionless sliding, cell detachment, or empty gaps opening between cylinders.

The cat endomysium morphology studied by [Trotter and Purslow](https://pubmed.ncbi.nlm.nih.gov/1608046/) supports shear transfer between overlapping fibres. It does not establish that every fibre in every muscle ends inside a fascicle. Perimysial continuity and the cellular attachment chain need further primary-method audit before teaching a detailed universal network or assigning its stiffness. The present evidence supports introducing a coupled composite and measuring relative strain, with the precise load partition left open.

A useful continuum consequence is that longitudinal stress can vary along a fibre direction when interface shear transfers load into or out of that path. This is a force-balance argument, not an added contractile source. A comparison between coupled and disconnected paths must specify the changed interface law and preserve the same external pose/load and activation; otherwise its force difference cannot be attributed to coupling alone.

Aponeuroses add another distinction: a sheet-like attachment surface can stretch transversely as well as along the muscle. [Azizi and Roberts](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/jphysiol.2009.173690) measured that distinction between active and passive loading. A single axial spring cannot represent all those sheet strains. This motivates eventual explicit sheet geometry or a justified reduced law; it does not justify silently renaming the serial fixture as an aponeurosis.

## What a changing cross-section counts

The following identities are **ideal geometric derivations**, not measurements of living muscle or new model equations.

Consider the same straight, parallel bundle containing `n` fibres, each spanning length `L`. Suppose its total material volume `V` and each fibre volume `V_f` remain constant, shortening is homogeneous, and no material or fluid crosses the chosen bundle boundary. Its cross-section perpendicular to the fibres satisfies

\[
A_{\rm bundle}=V/L,\qquad A_f=V_f/L,\qquad
\phi=\frac{nA_f}{A_{\rm bundle}}=\frac{nV_f}{V}.
\]

On shortening, the bundle and its fibre profiles become larger, `n` stays fixed, and the cell area fraction `phi` stays fixed. Profiles per unit bundle area `n/A_bundle` decrease. Thus “larger”, “more fibres”, “more profiles per unit area”, and “higher contractile area fraction” are different statements. Nonuniform shortening, different compartment changes, terminating fibres, or boundary exchange invalidate this simple cancellation and require their own measurements.

For a material surface in a general deformation, the area-vector transformation is

\[
d\mathbf a=J F^{-T}\mathbf N\,dA,\qquad J=\det F>0.
\]

This follows from transforming the two tangent vectors spanning the surface. A material plane initially normal to a fibre can become oblique to the current fibre under shear. Consequently, `A_current = J A_reference / fibre_stretch` is valid for a suitable homogeneous axial/transverse stretch with the section remaining normal to the fibres; it is **not a general formula for any advected plane under shear**.

A fixed spatial imaging plane does not follow the same material. Moving, curved or terminating fibres can cross it differently during deformation. Its profile count can change without creating or destroying fibres. Even for a straight circular fibre, a transverse intersection by a plane with unit normal `m` has ideal profile area

\[
A_{\rm profile}=A_{\perp}/|\mathbf f\cdot\mathbf m|,
\]

where `f` is the unit fibre direction. This assumes a straight prism/cylinder over the intersection, away from its ends; it fails as a useful bounded-section approximation near a parallel cut. Obliquity inflates a profile, so comparing raw image areas or counts without cut-angle and sampling conventions can misidentify packing changes.

These observations also explain why an anatomical slice area differs from physiological cross-sectional area. The measured-property workstream owns the precise PCSA convention and arm data. Here the requirement is to record whether an area belongs to a tracked material bundle, a current perpendicular fibre section, a fixed anatomical plane, or an estimated reference aggregation.

## Why bulging does not grant extra strength

Within the ideal bundle, increasing current cross-sectional area by shortening has not added contractile material. Force and stress must use consistent area measures. If `T` is a fibre force, then current stress is `T/A_f`, while nominal stress is `T/A_f,0`. Substituting the larger current area into a maximum-force formula whose stress was calibrated per reference area changes the model's meaning. The force–length, activation, orientation and loading assumptions still apply. A larger visual outline alone provides none of those measurements.

Compression is also different from uniform volume reduction. A nearly volume-preserving body can flatten in one direction, widen in another, rotate fibres and redistribute stress. [Sleboda and Roberts' cuff experiment](https://pubmed.ncbi.nlm.nih.gov/31879350/) shows why the effect on axial force has no universal positive sign. [Ryan et al.](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full) provide a continuum example in which direction and architecture also matter. Neither result licenses an automatic strength multiplier for bulging or confinement.

## Fluid compartments, compressibility, and time

Blood occupies vessels. Interstitial fluid lies outside cells and outside vascular lumens. Intracellular water lies within muscle cells. Fibre-profile packing, ECM volume fraction, subcellular myofilament spacing, and the volumes of these fluid compartments are separate observables. A visible surface or a single tissue-volume number cannot partition them.

The two Sleboda studies above support a mechanical interaction between fluid and structural restraint: the [passive osmotic experiment](https://pubmed.ncbi.nlm.nih.gov/28123108/) manipulated water content, while the [active cuff experiment](https://pubmed.ncbi.nlm.nih.gov/31879350/) manipulated external loading. They do not establish that fibres routinely separate and the resulting spaces fill with blood during a contraction. [Lutjemeier et al.](https://pubmed.ncbi.nlm.nih.gov/15557016/) instead measured flow impedance during contraction alongside relaxation-related flow enhancement. Increased perfusion over a cycle must not be confused with increased blood volume at each instant.

Near-incompressibility is a useful short-time mechanical approximation, not a proof that every muscle region and fluid compartment has constant volume. [Smith et al.](https://pubmed.ncbi.nlm.nih.gov/21450292/) observed a distinction between single fibres and ECM-containing bundles. Likewise, near-constant total body volume does not prove local `J=1`: local increases and decreases can cancel. Constituents may resist intrinsic compression yet move across a specimen boundary; drainage can then change the apparent tissue volume without strongly compressing water itself. This last statement is a mass-balance distinction, not a transport coefficient extracted from the cited experiments.

| Observation/time context | Interpretation to distinguish | Required evidence beyond an outline |
| --- | --- | --- |
| Within a contraction or mechanical loading cycle | Deformation of existing cells/ECM; fibre rotation; local redistribution and transient pressure. | Tracked material motion, local volume/strain, loading and activation history; compartment measurements if making a fluid claim. |
| Repeated contractions and recovery | Perfusion, vascular volume, and water exchange may evolve on different time scales. | Time-resolved flow **and** volume/compartment observations; boundary conditions and recovery protocol. No universal time constant is supplied here. |
| After unfamiliar loading, over subsequent measurements | Swelling can contribute to larger measured area. | Standardized timing plus measures capable of separating swelling from persistent tissue growth. [Damas et al.](https://link.springer.com/article/10.1007/s00421-015-3243-4) show why area alone is insufficient even early in a training study. |
| Longitudinal training/adaptation | Hypertrophy denotes tissue/cell growth, requiring material addition rather than a reversible deformation of fixed mass. | Repeated standardized morphology and composition measurements. Acute bulging proves neither hypertrophy nor increased fibre number; fibre-number changes are not resolved by this note. |

A single-phase finite bulk penalty penalizes local volume change. Its conjugate pressure-like quantity can enforce or approximate a volume constraint. That quantity is not automatically capillary pressure, interstitial pressure, or perfusion. A multiphase model would additionally require fluid mass conservation, exchange/transport laws, compartment definitions, and boundary conditions. No primary muscle transport protocol or permeability calibration has been qualified in this checkpoint, so a poroelastic extension remains a research proposal.

## A continuum can model muscle without simulating every fibre

[Blemker et al.](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) demonstrate one route: spatial fibre directions and effective responses to fibre stretch and shear, with distinct surrounding structures. A finite element represents an averaged tissue region rather than one muscle cell. Curved architecture and spatial deformation can be represented without enumerating all fibres.

For a future model, the averaging scale and target observables should determine the detail. An anisotropic single-phase continuum might target regional deformation and integrated reactions. Explicit aponeurosis/tendon regions can supply sheet and attachment mechanics. Representative microstructure calculations could inform effective properties, with assumptions and uncertainty reported. Individual-cell spacing, microscopic lattice behavior, cell-by-cell load partition, and fluid-compartment transport need additional information; they cannot be recovered uniquely from a fitted bulk response.

This is a modeling strategy, not qualification of Kenoma's passive prototype as living muscle. Mechanical verification would still require consistent stress/energy accounting, admissible local geometry, resolved stationarity and reactions, and convergence. Biological validation would require independent measurements under the actual preparations and loading protocols being claimed.

## Proposed teaching progression and evidence gates

These are future research exercises, not implemented or qualified labs. They refine the existing progression without changing its equations or acceptance limits.

1. **Track a marked bundle and compare cuts.** Use an ideal kinematic display with the same labelled fibres, a material surface, and fixed/oblique planes. Report fibre count, profile area, area fraction and angle separately. Check the identities above under their stated assumptions before adding force.
2. **Introduce coupled shear paths.** Compare two bonded fascicle-like regions with a clearly declared disconnected-interface ablation. Hold external pose/load and activation fixed. Show relative displacement, interface traction, reaction balance and work; do not infer cell detachment from shear. Obtain primary preparation-specific interface evidence before fitting a biological stiffness.
3. **Add an attachment sheet and confinement.** Separate axial from transverse sheet strain and compare passive versus eventual active loading. Show that width, thickness and fibre angle need not change together. Anisotropic sheet data and boundary-condition measurements must precede calibration; animal aponeurosis results motivate questions, not human-arm constants.
4. **Compare local and total volume.** Build on the verified passive continuum to show local `J`, whole volume and reaction observables. Teach separately what finite bulk compliance means. A drained/undrained fluid exercise requires audited mass-balance/transport evidence and a separate solver qualification before implementation.
5. **Treat perfusion and growth as separate extensions.** A vascular-flow exercise needs an explicit vessel/flow model and measured protocol; interstitial transport needs its own compartments. A growth exercise needs changing material mass/composition and longitudinal evidence. Neither can be represented merely by a larger current radius or a packing slider.

Remaining evidence gaps are quantitative lateral load partition, the full perimysial/cellular attachment chain, preparation-specific transverse/shear properties, biaxial aponeurosis calibration, reliable local-versus-whole volume measurements, and fluid exchange/perfusion observables with matching time histories. Full methods for the abstract-only sources and the inaccessible primary leads must be audited before extraction. No clinical inference, coefficient transfer, or biological acceptance claim is made by this note.
