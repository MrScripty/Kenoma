# Arm reference map and operating lengths: primary-source review

The smallest defensible educational arm map keeps **geometry pose, passive material reference, fascicle reference length, and active optimum as separate records**. The reviewed sources provide head-specific architecture and model priors, but do not identify a stress-free material map, tendon prestrain, or unloaded tendon area for this atlas. A numerical reference chosen to remove a negative witness would remain an assumption.

Research-only review dated 2026-10-06, based on frozen commit `09e6698fdd1c20a7d44109f1209500f8d9122458`, tree `d59f6187445e57545a7e5b33a48b0a0324f8f4ea`, branch `research/arm-reference-operating-lengths`. This follows the parent's instruction to stop pressure diagnostics after its independent review of that volume-kernel witness. It makes no parameter, anatomy, solver, book, Lean, production, or clinical change. The separate reduced Millard benchmark is outside this review.

## Four references that must survive independently

| Record | Meaning and required metadata | What it cannot establish alone |
|---|---|---|
| Atlas/image pose | Asset/version/hash, tissue/head identity, spatial units/frame, joint angles, registration, acquisition or authored state | Unloaded tissue, sarcomere optimum, or zero passive stress |
| Passive stress-free reference | Natural length/metric of each passive constituent, unloading/preconditioning protocol; prestress if the computational pose differs | Active optimal length; a passive EMG reading does not establish zero internal stress |
| Fascicle reference length `Lf,ref` | Contractile arc at a declared pose and state; fascicle direction, curvature, pennation and excluded series tissue | Serial sarcomere count without a representative sarcomere measurement/hypothesis |
| Active optimum `Lopt`, `ls,opt` | Optimum convention or a measured active force–length optimum, preparation and temperature, conversion to the chosen reference | Passive recruitment/slack length or atlas pose |

Classification used below: **M** = measured observation; **D** = derived from observations and explicit assumptions; **E** = published model choice or proposed educational prior. A literature number does not become an atlas measurement by being entered in a file. `NR` means not reported/extracted in the accessible text, not a zero value. All table uncertainties retain the source's SD/CI meaning.

## Head-specific architecture: keep the two source families separate

[Murray, Buchanan and Delp (2000), Methods equations 1–4; Table 2, p. 947](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf): ten unembalmed limbs from nine cadavers, frozen/thawed, then architecture formalin-fixed; frozen postures included extension/~90° flexion. Ages NR. **D** optimum uses `Lopt = Lf,meas × 2.8 µm / ls,meas`. **D** equivalent tendon uses `LT = LMT − Lf cos(alpha)`; it is not measured slack length. Values below are mean (SD), **cm**.

| Head | Architecture n | D `Lopt` | D equivalent `LT` |
|---|---:|---:|---:|
| Biceps long | 6 | 12.8 (3.2) | 22.9 (1.6) |
| Biceps short | 8 | 14.5 (3.2) | 18.3 (2.5) |
| Brachialis | 9 | 9.9 (1.6) | 11.6 (1.3) |
| Triceps long | 9 | 12.7 (2.1) | 21.7 (2.9) |
| Triceps lateral | 8 | 9.3 (2.8) | 18.7 (1.8) |

No separate medial-triceps fascicle estimate is tabulated; lateral PCSA includes medial mass. Operating-range estimates assume inelastic tendon/aponeurosis and adopted sarcomere endpoints; they are not living measured trajectories.

[Holzbaur, Murray and Delp (2005), Methods pp. 831–833; Table 1, p. 832](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf): major-elbow architecture comes from the cadaver used for digitized bones, rather than Murray's population mean. Optimal lengths are renormalized to **2.7 µm**. Slack lengths are **selected** to match operating lengths/moments, not directly measured unloaded tendon. Table entries retain printed rounding; lengths **cm**, pennation **degrees**.

| Head | D/model `Lopt` | E tendon slack | Model pennation |
|---|---:|---:|---:|
| Biceps long | 11.6 | 27.2 | 0 |
| Biceps short | 13.2 | 19.2 | 0 |
| Brachialis | 8.6 | 5.4 | 0 |
| Triceps long | 13.4 | 14.3 | 12 |
| Triceps lateral | 11.4 | 9.8 | 9 |
| Triceps medial | 11.4 | 9.1 | 9 |

The model's neutral shoulder has vertical humerus; neutral axial rotation is defined with elbow 90° and sagittal forearm. Elbow 0° is full extension; forearm positive rotation is pronation. Its elbow/shoulder specific tension is **140 N/cm² = 1.4 MPa**, a model choice.

**Derived convention check:** for the same measured fascicle/sarcomere pair, switching 2.8 → 2.7 µm multiplies `Lopt` by `27/28 = 0.964285714` (−3.5714%). At fixed volume, PCSA increases by `28/27 − 1 = 3.7037%`. This conversion does not reconcile different specimens, pathways, or selected slack lengths. Do not combine a Murray equivalent tendon with a Holzbaur optimum and call the resulting pair measured or coherent.

## Live observations, preparation and pose

| Primary source / access | Population and preparation | Pose and quantity | Classification / limitation |
|---|---|---|---|
| [Adkins et al. 2021, PNAS, Methods; Fig. 5; equations 4–6](https://www.pnas.org/doi/full/10.1073/pnas.2008597118), full primary text | 8 chronic-stroke participants recruited (3 F/5 M, 60±9 y), one excluded; 4 unimpaired (2 F/2 M, 62±6 y). Live long-head biceps, passive SHG + EFOV ultrasound | Seated: source says **85° shoulder adduction**, 10° horizontal shoulder flexion, **25° elbow flexion**, mid-prosupination, wrist/fingers 0°. Fascicle and sarcomere measures share the pose; MRI is separately supine | M paired local `Lf`, `ls`; D `Ns=Lf/ls`, `Lopt=Ns×2.7 µm`. One matched pose, not a healthy multi-pose operating curve. Passive protocol does not establish zero stress |
| [Adkins et al. 2022, Frontiers, Methods/Discussion](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.817334/full), full primary text | 14 participants across variability subsets; biceps across-image subset 15 limbs: 7 nonparetic stroke limbs + both arms of 4 unimpaired participants | Seated/passive; source says **85° shoulder abduction**, elbow **extended 25°**, wrist 0°. SHG field 82×82 µm | M uncertainty approximately **0.25 µm**, anatomy + random error; not the ~0.02 µm computational phantom accuracy. Authors estimate ~7–8% uncertainty in optimal fascicle length/PCSA from sarcomere uncertainty alone |
| [Nelson, Dewald and Murray 2016, abstract/figure descriptions](https://pubmed.ncbi.nlm.nih.gov/27083062/), primary abstract only | 11 healthy humans, both arms, passive EFOV ultrasound | Anterior long-head biceps and distal lateral triceps; three elbow postures, exact angles not extracted | M fascicle length varies with posture. ICC biceps .92–.95; triceps .81–.92. No paired sarcomere optimum or material-reference metric extracted |

**Unresolved source wording:** the 2021 adduction versus 2022 abduction descriptions cannot be silently made identical. Exact protocol reproduction needs the figure/supplement or author clarification of the coordinate convention. The DOI containing `2021` does not date the Frontiers publication: it was published **8 February 2022**. Its biceps subset reuses observations associated with 2021, so it is not independent replication. The 2022 **3.04–3.97 µm** range pools biceps and FCU and is not a biceps-only prior. Neither stroke outcomes nor nonparetic arms should be relabeled as a healthy atlas calibration.

## Joint moment arms require the complete pose

Murray 2000 Table 2: **cm**, mean (SD), neutral forearm. Averages: flexors **20–120°**, triceps **30–120°** elbow flexion.

| Muscle path | n | D peak arm | D range-average arm |
|---|---:|---:|---:|
| Biceps common path | 10 | 4.7 (0.4) | 3.7 (0.3) |
| Brachialis | 9 | 2.6 (0.3) | 2.1 (0.3) |
| Triceps common path | 10 | 2.3 (0.3) | 2.0 (0.2) |

Triceps sign is negative for positive flexion; paths are not head-resolved.

[Murray, Delp and Buchanan (1995), primary abstract](https://pubmed.ncbi.nlm.nih.gov/7775488/) measured two anatomical specimens: flexion/extension arms varied at least **30% over 95°**; biceps peak flexion arm was greater in supination and occurred with a more extended elbow. Full trajectory, specimen demographics and uncertainty were not extracted. [Jarrett et al. (2012; epub 2011), primary abstract](https://pubmed.ncbi.nlm.nih.gov/21813298/) separated distal biceps heads in six cadavers at **90° elbow flexion**, with forearm pronated/neutral/supinated: long and short heads had different pose-dependent leverage. A common-path simplification is therefore an educational modeling choice.

For a proposed signed convention, define `rj = −∂LMT/∂qj`, joint angles in **radians** and lengths in **m**. Then tensile generalized torque is `tauj = T rj`; source signs and angle units must be transformed explicitly. Elbow-only sampling is insufficient for biarticular biceps/triceps long head: retain shoulder pose and scapular convention, as well as forearm rotation, with every path observation. A constant population-average moment arm cannot determine the atlas tendon path or reference fiber operating length.

## Tendon, aponeurosis and area evidence

| Primary source / specimen / pose | M/D/E quantity and units | What remains unidentified |
|---|---|---|
| [Asakawa et al. 2002, Methods/Results; Table 2](https://nmbl.stanford.edu/publications/pdf/Asakawa2002b.pdf): 12 living unimpaired right arms, 10 M/2 F, age 30 (7) y; MRI ≤10° elbow flexion, shoulder angle NR | M long-head belly **20±2 cm**, internal distal aponeurosis **7±1 cm**; D aponeurosis/belly **34±4%**, SD. MRI spacing 10 mm. Ultrasound extension versus 90° flexion at 5% MVC mixes pose and load | Internal aponeurosis is not external lacertus. No unloaded sheet metric, thickness, tendon slack or reference prestrain established |
| Jarrett 2012: six cadavers; elbow 90°, three forearm positions; demographics/preparation details NR in abstract | M insertion **footprints**: long head **59±15 mm²**, short **94±44 mm²** | Attachment footprint is not tensile tendon cross-sectional area `AT,ref`; no slack or zero-force prestrain extracted |
| [Keener et al. 2010, primary abstract](https://pubmed.ncbi.nlm.nih.gov/20056450/): 36 elbows/23 cadavers; pose/demographics NR in abstract | M distal triceps mean tendon width **23.7 mm**, central insertion thickness **6.8 mm**; insertion width/length **20.9/13.4 mm** | Multiplying width and insertion thickness does not establish a tensile CSA: landmarks and irregular section differ. No unloaded area/length or stress-free metric extracted |
| [Ocran et al. 2025, primary abstract](https://pubmed.ncbi.nlm.nih.gov/39746286/): 8 fresh-frozen external bicipital aponeuroses, age 82±12 y, 5 F | M biaxial protocol: ~7×7 mm samples, ten preconditioning cycles at 9% strain, testing to 12%, rate 1%/s | Protocol strain is not in vivo reference prestrain. Numeric modulus, thickness, temperature and area convention are unextracted; external sheet is not Asakawa's internal structure |
| Proposed arm reference record | E slack lengths may come from a coherent published model; `AT,ref`, sheet thickness and `epsilonT,ref` remain **unknown** here | No reviewed matched-subject dataset closes these fields for all six target heads, or for the atlas |

PCSA is muscle volume divided by normalized fascicle length; it is not tendon CSA, insertion footprint, or an arbitrary mesh-face area. A series tendon and a distributed aponeurosis also need distinct geometry/reference records even if a reduced model lumps their compliance.

## Verify the continuum and amplitude conventions before transferring them

[Blemker, Pinsky and Delp (2005), equations 1–3, p. 658; Tables 1–2](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf) use **deviatoric invariants** and `lambda = sqrt(bar(I4))`. Translation into standard finite-deformation notation gives

\[
\bar C=J^{-2/3}F^T F,\qquad
\bar\lambda_f=\sqrt{a_0^T\bar C a_0}=J^{-1/3}|Fa_0|.
\]

This equation is our notation translation, not a claim that the paper prints that full identity. **E** muscle optimum is dimensionless **1.4**. Its passive muscle law is zero below its optimum; tendinous axial recruitment is at stretch 1, with toe/linear transition **1.03**. Those are constitutive assumptions, not a measured atlas stress-free pose or physiological prestrain. Reporting tissue strain relative to the long configuration is also distinct from selecting a natural material reference. At finite `J`, full and deviatoric stretches differ; equality at `J=1` does not authorize silently exchanging conventions.

[Krivickas et al. (2011), Methods and Table 1](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/expphysiol.2010.055269) supply the retained educational amplitude: Type I **15.5 (5.0) N/cm² = 155000 (50000) Pa**, mean (SD), swelling-corrected. Preparation: chemically skinned **vastus lateralis**, **15°C**, sarcomere setting **2.75–2.85 µm**, maximal activation pCa 4.5; peak minus resting force divided by elliptical bath-measured CSA, with swelling correction already applied. The Type I analysis comprises 113 people/1863 fibers. This is **M/D** fiber-preparation evidence, not human biceps whole-muscle calibration, and not a physiological bound on biceps stress. A numerical acceptance tolerance cannot be inferred from this SD.

## Smallest proposed educational map

This is a metadata and identifiability proposal; none of the following values is installed in a model.

| Field | Proposed first educational record | Evidence status / uncertainty |
|---|---|---|
| Tissue identities | Separate biceps long/short, brachialis, triceps long/lateral/medial; retain brachioradialis separately if the seven-muscle arm is used | Head-specific provenance; do not duplicate lateral architecture as a medial measurement |
| Atlas datum | Retain current BodyParts3D asset hashes, meters, +X anatomical left/+Y posterior/+Z superior and authored elbow bind angle **16.2783°** | Existing geometry datum; no biological unloading interpretation |
| Comparison pose `qref` | **E** elbow 90° flexion, forearm neutral, shoulder elevation/axial rotation neutral under a fully stated coordinate definition | Proposed reproducible kinematic comparison; neither atlas bind pose nor Adkins' measurement pose. Shoulder fixation matters for long heads |
| Contractile path | `gamma_i(X)`, `a0(X)`, contractile arc `Lf,ref`, spatial sampling and pennation; exclude external tendon and aponeurosis from that arc | Unknown measured fascicles for this atlas; authored centerline guides are educational geometry |
| Optimum family | If numeric priors are needed, choose **one** coherent published model asset + pose/path conventions, using its 2.7 µm normalization; keep Murray 2.8 µm population results as a separate comparison family | Holzbaur table is a candidate E prior, not a selected parameter set; exact asset release/hash still required |
| Passive reference | Separate recruitment length and natural metric per muscle, tendon, aponeurosis and fascia; permit prestress at `qref` | Unknown. Zero activation and zero prestress would be separate E assumptions |
| Series geometry | `LMT(qref)`, `LT,ref`, `LT,slack`, reference tendon strain, reference area; separate internal/external aponeurosis | Unknown matched closure; do not substitute equivalent tendon, footprint, PCSA or arbitrary face area |
| Output qualification | Pose-indexed length/stretch and volume with numerical error, source variability and assumption sensitivity recorded separately | Educational interpretation only; no physiological validation or accepted numerical threshold inferred |

Repository context is recorded in [the capstone specification](../anatomical-capstone-specification.md), [existing architecture review](reference-architecture-source-review.md), and [anatomy context addendum](anatomy-reference-context-addendum.md). The existing atlas arc **0.14385179 m** and Arm26 BICshort input **0.1321 m** have different meanings; their ratio is not a sarcomere normalization. The pending BodyParts3D 4.3 review does not authorize a source/reference switch here.

For a continuous serial-fiber/co-deformation **hypothesis**, use a paired contractile reference observation:

\[
N_s\simeq L_{f,\mathrm{ref}}/\ell_{s,\mathrm{ref}},\qquad
L_{\mathrm{opt}}=N_s\ell_{s,\mathrm{opt}},\qquad
\lambda_{\mathrm{opt}}=L_{\mathrm{opt}}/L_{f,\mathrm{ref}},\qquad
s=\frac{\lambda_f}{\lambda_{\mathrm{opt}}}
=\lambda_f\frac{\ell_{s,\mathrm{ref}}}{\ell_{s,\mathrm{opt}}}.
\]

The full geometric choice is `lambda_f=|F a0|`; source reproduction using deviatoric stretch must declare the different `J` dependence. A representative fascicle average does not identify a local sarcomere field or fibers that terminate within fascicles. Serial count, optimum convention, passive recruitment, and any finite-strain pre-reference transform must remain separately identifiable.

In a straight, single-path projection **hypothesis**, series closure is

\[
L_{MT}=L_T+L_f\cos\alpha,\qquad
L_{T,\mathrm{ref}}=L_{T,\mathrm{slack}}(1+\epsilon_{T,\mathrm{ref}}),\qquad
\frac{L_{f,\mathrm{ref}}}{L_{\mathrm{opt}}}
=\frac{L_{MT,\mathrm{ref}}-L_{T,\mathrm{slack}}(1+\epsilon_{T,\mathrm{ref}})}
 {L_{\mathrm{opt}}\cos\alpha_{\mathrm{ref}}}.
\]

This is an identifiability relation, not a new tendon implementation. It cannot be applied to an arbitrary atlas centerline without its contractile/series partition. Setting `epsilonT,ref=0` adds an assumption; setting `Lf,ref=Lopt` additionally selects an operating state. Neither follows from the image pose. Distributed curved architecture requires the corresponding path/field description rather than this one-dimensional closure.

For first-order sensitivity, `delta s/s ≈ delta lambda_f/lambda_f + delta ls,ref/ls,ref − delta ls,opt/ls,opt`; correlated measurement errors require covariance, not independent SD addition. Group SDs above are not subject-specific confidence intervals. The ~7–8% sarcomere-related uncertainty excludes fascicle segmentation, pose/registration, series extension and reference-state uncertainty. Keep these separate from residual/discretization tolerances and from constitutive model discrepancy.

## Decision and smallest next step

Review the four-record metadata contract and select a single versioned path/reference family before adding a force–length normalization to anatomy. Keep `Lf,ref`, passive natural metric, reference prestrain and tendon area marked unknown wherever they are unobserved. A fully physical atlas-specific map remains blocked by those missing measurements; a fully declared synthetic map can still support progressive educational verification without claiming calibration.

For the first physical operating-length comparison, the smallest useful evidence addition is same-subject, same-long-head **paired fascicle and sarcomere observations at two declared passive poses**, with registered contractile/series partitions and a stated tendon load/reference protocol. It would test pose dependence and normalization without assuming the biceps is optimal at either pose. This is a proposed observation specification, not a clinical protocol or authorization to collect data. Other heads and spatial fields would still require evidence.

No simulation was run for this source review. All existing receipts, gates and negative witnesses are preserved. See [source access ledger](../../data/anatomical-arm-v1/review/arm-reference-operating-lengths/source-access-ledger.json) and [preservation/verification receipt](../../data/anatomical-arm-v1/review/arm-reference-operating-lengths/verification.json).
