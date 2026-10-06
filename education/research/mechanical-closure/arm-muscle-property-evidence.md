# Bounded primary evidence for arm-muscle properties

Research review, 2026-10-06, branch `research/arm-muscle-property-evidence`, base `297828af89ac0818dcab1282513cb28c6219cfac` (tree `d54f63cae1b00f2f6008a6894b4c83ec7980c370`). This is a source table for parent review, not a parameter adoption. All 1,567 baseline tracked files, including failed cases, thresholds, anatomy, activation/solver code, book and Lean, are preserved byte-for-byte. [Provenance and numeric evidence](../../data/anatomical-arm-v1/review/arm-muscle-property-evidence/evidence.json) and [verification](../../data/anatomical-arm-v1/review/arm-muscle-property-evidence/verification.json) accompany this document. No solver or physiological calibration was run.

**M** means measured under the stated assay; **D** means derived from measurements and assumptions; **E** means an explicit reference-model input/default. A population result is at most a candidate prior for another person; it is never a measurement of the atlas subject. **Unknown** means unavailable in this bounded extraction, not zero and not proof that no study exists. SD, CI, biological heterogeneity and measurement/preparation uncertainty are distinct from numerical convergence tolerances. Disease history, training dose, temperature and specimen age remain NR wherever the row does not establish them; no disease-specific parameter is inferred.

## Head coverage

| Structure | Arm26 | Extracted human physiological evidence | Remaining physiological gaps |
|---|---|---|---|
| Biceps long | `BIClong` | D cadaver PCSA, head resolved (S1). Biceps diameter/group morphology exists but biopsy head unresolved (S2/S3) | Head-specific type mixture, fiber CSA, tension, velocity and activation/relaxation |
| Biceps short | `BICshort` | D cadaver PCSA, head resolved (S1); same unresolved-head caveat | Same gaps; no transfer of long-head values |
| Brachialis | `BRA` | D cadaver PCSA (S1); whole-flexor MRI/inverse-force framework includes it (S4) | Type/diameter/CSA/tension/rate/timing values not extracted |
| Triceps long | `TRIlong` | D cadaver PCSA (S1) | Lateral biopsy cannot fill this head's fiber or rate/timing fields |
| Triceps lateral | `TRIlat` | M lateral-biopsy MHC content and M/D single-fiber tension (S5); S1 lateral PCSA combines medial mass | Independently resolved PCSA; verified fiber-area units; shortening/lengthening and timing numbers |
| Triceps medial | `TRImed` | Included in S1's lateral+medial mass aggregate | Separate PCSA and all listed fiber/rate/timing measurements |
| Brachioradialis | **Absent** | D cadaver PCSA (S1); S4 includes its whole-muscle inverse-force framework | No seventh Arm26 actuator; fiber/rate/timing measurements not extracted |

These heads do not define a complete elbow model: forearm posture, muscle paths, antagonists and joint moment arms still matter. A reduced ForceSet's omissions cannot be repaired by treating neighboring heads as measured substitutes.

## Architecture: PCSA is distinct from anatomical section area

[S1: Murray, Buchanan & Delp (2000), Methods equations 1–4 and Table 2, printed p.947](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf). Ten human upper extremities/nine cadavers, both sexes; age, training, disease screening and assay temperature NR. Frozen/thawed 36–48 h, formalin-fixed architecture; posture differed between extension and approximately 90° flexion. **D** PCSA = mass/(1.06 g/cm³ × optimal fascicle length); optimum normalized to **2.8 µm** sarcomere length. Pennation cosine is a separate force/moment projection.

| S1 structure | D PCSA, cm², mean (SD) | SI area, m², mean (SD) | Architecture n / qualification |
|---|---:|---:|---|
| Biceps long | 2.5 (1.1) | 0.00025 (0.00011) | 6 |
| Biceps short | 2.1 (0.6) | 0.00021 (0.00006) | 8 |
| Brachialis | 5.4 (1.3) | 0.00054 (0.00013) | 9 |
| Triceps long | 4.3 (1.8) | 0.00043 (0.00018) | 9 |
| Triceps lateral **plus medial** | 10.5 (5.2) | 0.00105 (0.00052) | 8; medial mass included using lateral optimum |
| Triceps combined | 14.9 (6.7) | 0.00149 (0.00067) | Published combined estimate; no inferred medial subtraction |
| Brachioradialis | 1.2 (0.6) | 0.00012 (0.00006) | 10 |

[S4: Kawakami et al. (1994), original abstract](https://link.springer.com/article/10.1007/BF00244027): four men; age/training/temperature NR in accessed abstract. Serial MRI supplied anatomical area/volume; PCSA used volume divided by estimated fiber length (literature fiber/muscle-length ratio). Triceps maximal anatomical area was comparable to summed flexors while its derived PCSA was **1.9×** theirs. Force inferred from joint torque and moment arms is an inverse estimate; head sharing and absolute tension/velocity values require full Methods/tables. None is adopted here.

An anatomical cross-section is an image-plane intersection; PCSA approximates parallel contractile architecture under its stated length convention. Neither equals one microscopic fiber's CSA. `V/Lopt` without a declared architecture/packing convention is not a fiber census. Pennation projection must not be counted twice if a source already embeds it in its area or effective tension definition.

## Fiber morphology, mixtures and tension

| Source / tissue scale | Quantitative evidence and uncertainty | Conditions and transfer limits |
|---|---|---|
| [S2: Mattiello-Sverzut & Martins (2023), Methods/Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC9925190/); biopsy fibers | M smallest Type 2A diameter: female **50.6 µm**, 95% CI **49.5–51.8**; male **64.2 µm**, CI **62.9–65.6** | Human medium-distal biceps, head unresolved; 32 recruited/26 usable (14 M/12 F), age 34.1±8 y, recreational activity; competitive athletes excluded. Frozen 5 µm sections, histochemical mATPase typing, ≥100 fibers for diameter. These cells come from the frozen repository's prior primary-table audit; current Methods were reread, but Table 2 could not be reread after a browser challenge. No circular CSA inferred. |
| [S3: Maeo et al. (2024), original abstract, Figs.3–4 captions](https://pubmed.ncbi.nlm.nih.gov/38875487/); whole biceps MRI plus biopsy/subcellular samples | Trained versus untrained: M maximal anatomical area **+70%**, mean fiber area **+29%**; D fiber-number estimate **+34%**. No absolute typed area or mixture digitized | 16 trained men (5.9±3.5 y training)/13 untrained men; head, age, temperature and detailed preparation not extracted. Cross-sectional comparison; fiber number estimated from area ratios, not counted across a whole muscle. Captions distinguish mixtures by number versus area. Full text access limited. |
| [S5: Gejl et al. (2021), Methods, Results MHC distribution, Fig.1](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.682943/full); homogenate and single fibers | M homogenate MHC I **39±6%**, MHC II **61±6%** (SD). M/D maximum specific force: I **90±43 kPa**, II **127±55 kPa**; force **0.66±0.28 mN / 1.08±0.42 mN**, respectively | Distal lateral triceps; eight elite male skiers, 24±4 y. Chemically skinned, **22.1°C**, pCa4.7, force at 120% straightened slack length; sarcomere length unmeasured. Cylindrical CSA from three slack-length diameters, no swelling correction. Fig.1 n=28 I/60 II; hybrids/IIx excluded, force outliers omitted. Table1's rendered area unit is unresolved, so absolute CSA is withheld. Data overlap earlier reports; no independent replication claim. |

S2 diameter is a minimum section diameter, not cell spacing or filament packing. S2 biopsied the nonpreferred arm and tested torque in the preferred arm; joint torque is not a matched single-fiber force measurement. Its histochemical labels are retained rather than silently mapped to a different MHC nomenclature.

S5's homogenate gel densitometry measures **MHC protein content**; interpreting it as histological fiber-count or occupied-area fractions would require additional information. Analyzed fiber counts are selected assay samples, not mixture estimates. The published Table1 text renders CSA as “mm²” with values 7619/8807; plausibility is insufficient to silently replace its unit with µm². The source's force/stress statements are recorded as reported, with that denominator-unit limitation. Their absolute CSA cells remain unknown.

Transient shortening/bulging and an oblique section do not demonstrate new fibers or a capacity increase. In a simple reference parallel-fiber idealization, `Acontractile,0 = phi0 V0/Lf,0`, with separately justified packing fraction `phi0`. A count estimate additionally needs representative fiber areas and orientations. If whole-muscle effective tension already includes noncontractile fractions, applying `phi0` again double counts. A local continuum stress coefficient requires configuration and stress-measure mapping before comparison to measured force/area.

## Speed and activation/relaxation

| Primary source / scale | Verified scope | Missing numerical or convention fields |
|---|---|---|
| [S6: Harridge et al. (1996), original abstract](https://link.springer.com/article/10.1007/s004240050215) | Seven young men; triceps brachii plus two leg muscle groups. Electrically evoked whole-muscle isometric responses, biopsy MHC/ATPase; chemically skinned single fibers. Assays include twitch time to peak torque, rate of torque development, unloaded shortening velocity and tension-rise rate | Head, exact age/training, temperature, length/velocity normalization, absolute arm timing/speed and uncertainty unavailable in subscription preview. No numeric timing transferred |
| [S7: Bottinelli et al. (1996), original abstract](https://physoc.onlinelibrary.wiley.com/doi/10.1113/jphysiol.1996.sp021617) | Human skinned fibers: 67 load-clamp force–velocity/57 slack-test fibers at 12°C; temperature groups 12–22°C. Reported Vmax Q10 **5.88**. Historical MHC “IIB” label retained | Muscle origin not established in accessed abstract; not arm calibration. Exact velocity units, age/training, CSA convention, absolute speed and uncertainty not extracted |

Whole-muscle angular velocity, fascicle velocity, single-fiber velocity and sarcomere velocity are different observables. Tendon compliance and geometry mediate their relation. Slack-test unloaded `Vo`, fitted force–velocity `Vmax`, and power-optimal speed are different quantities; load and length must accompany each. Controlled eccentric lengthening speed is not a unique intrinsic “maximum speed,” and an eccentric force multiplier does not define one. No measured arm lengthening-speed limit is supplied by this review.

Twitch time to peak, tension-rise rate, half-relaxation after stimulation, excitation-to-activation dynamics and relaxation after mechanical loading cannot share one time constant by definition. Temperature, stimulation, fatigue and preparation must accompany any measured timing. S6 is a precise full-text acquisition target, not license to replace the unknown cells with remembered ranges.

## Reference-model inputs, separately labeled

[S8: pinned official Arm26 XML](https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim), byte-identical to local `education/data/elbow-v1/sources/arm26.osim`, SHA256 `e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9`. All six Thelen actuators explicitly specify:

| Quantity | E Arm26 input | E pinned Thelen class default / interpretation |
|---|---:|---|
| `max_contraction_velocity` | 10 optimal fiber lengths/s | XML unit declaration; dimensional normalization uses the selected optimum, not biopsy length |
| `activation_time_constant` | 0.010 s = 10 ms | 0.015 s = 15 ms |
| `deactivation_time_constant` | 0.040 s = 40 ms | 0.050 s = 50 ms |
| `Flen` | 1.8 dimensionless | 1.4; normalized lengthening-force parameter, not speed |

[S9: OpenSim core 4.5.2, peeled commit `5bc7d3308eda742690f485ec060bfe725a349fa6`](https://github.com/opensim-org/opensim-core/tree/5bc7d3308eda742690f485ec060bfe725a349fa6). [`Thelen2003Muscle.cpp`](https://github.com/opensim-org/opensim-core/blob/5bc7d3308eda742690f485ec060bfe725a349fa6/OpenSim/Actuators/Thelen2003Muscle.cpp), lines131–138 passes properties to the activation subcomponent; lines185–190 define defaults; line512 scales velocity by `max_contraction_velocity × optimal_fiber_length`. [`MuscleFirstOrderActivationDynamicModel.cpp`](https://github.com/opensim-org/opensim-core/blob/5bc7d3308eda742690f485ec060bfe725a349fa6/OpenSim/Actuators/MuscleFirstOrderActivationDynamicModel.cpp), lines78–86 implements `da/dt=(u−a)/tau`, after activation clamping. For increasing activation, `tau=tauA(0.5+1.5a)`; otherwise `tau=tauD/(0.5+1.5a)`. Therefore the input constants are not a fixed observed twitch rise/relaxation time. Only source inspection was performed; runtime model loading was not qualified.

[S10: Holzbaur et al. (2005), Methods/Table1](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf) uses a **2.7 µm** optimal sarcomere convention and **140 N/cm² = 1.4 MPa** elbow/shoulder model specific tension. This reference-model choice is distinct from S1's cadaver convention and S5's fiber assay. The retained **155000 Pa** educational Type I amplitude originates in skinned vastus lateralis at 15°C, not an arm calibration; its provenance remains in the [existing primary review](arm-reference-operating-lengths-primary-review.md). Neither source justifies changing a numerical acceptance gate.

## Bounded outcome and next step

The review establishes traceable architecture, unresolved-head biceps morphology, lateral-head triceps mixture/tension, and exact Arm26 rate inputs. It does **not** establish a matched head-specific arm dataset spanning mixture, fiber CSA, optimal length, force, concentric/eccentric velocity and activation/relaxation. All selected biological numerical observations are human; animal findings in source references were not imported as human measurements. No atlas packing, fiber count, optimum, material state or strength was inferred.

The smallest justified next step is to obtain S6's full primary protocol/tables through normal authorized access and resolve S5 Table1's area unit, while retaining unknown fields until verified. For a later model fit, choose one anatomical head and one preparation with paired area/length/force/rate observations, then define the mapping to the constitutive coefficient before adopting parameters. Broad survey searches were stopped after returning irrelevant results; challenged/subscription content was not bypassed. The source ledger distinguishes fresh primary reads from prior repository audits. Numerical failures and thresholds remain unchanged.
