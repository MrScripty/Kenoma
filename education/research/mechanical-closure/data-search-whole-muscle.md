# Official matched whole-muscle data search

2026-10-06; additive search against frozen base label `306d0aba`. Companion: [whole-muscle-facts.json](../../data/anatomical-arm-v1/review/matched-calibration-data-search/whole-muscle-facts.json). No earlier evidence, simulation, symbolic check, Git operation or model was changed.

**Outcome:** this bounded search did not obtain an accessible official subject-level table pairing active whole-muscle force, area and reference geometry. The closest primary evidence is the human gracilis surgical series. Its reported maximal force and optimal fibre length have correction/inference stages, and its supporting spreadsheets were inaccessible. The passive study's accessible supplement supplies figures rather than a matched table. No numeric calibration or arm transfer is selected. This is a search result, not a claim that no such dataset exists anywhere.

## Inventory and field matrix

M = directly acquired measurement described by the original source; D = derived/corrected; A = assumption or literature input; U = unverified/not located. These labels describe the study, **not possession of its individual data**. A study may acquire paired measurements while publishing only a summary accessible to this audit.

| Required field | Binder-Markey 2023 | Persad 2021 passive | Persad 2022 protocol | Wang 2025 |
|---|---|---|---|---|
| Species/preparation | Human, living gracilis, surgical harvest | Human, living gracilis, surgical harvest | Human, same type of surgery | Human gracilis surgery |
| Force and unit | M tendon buckle; D maximal force | M passive tendon force, N | M calibrated tendon force, N | Active force reported; detailed correction U |
| Area/volume | M optical volume; D PCSA | D corrected volume/PCSA | Acquisition workflow | U in accessible abstract |
| Fibre length | D force–length FWHM inference | A fibre/muscle ratio | Workflow, no subject rows | D curve-width prediction |
| Sarcomere length | M fixed passive biopsy | M JC1/2/4; D JC3 | Fixed-biopsy workflow | Shortening estimated |
| Reference geometry | Measured lengths; inferred optimum | Measured slack lengths; assumed optimum | Defined acquisition | Patient normalization described |
| Activation/passive | Submaximal stimulation; correction; passive separately acquired | Passive experiment | Explicit stimulation/tare workflow | Full definition U |
| Measured muscle temperature | U | U | U | U |
| Matched individual rows obtained | No | No | No | No |

Original sources and exact locators:

- [Binder-Markey et al., 2023, DOI10.1113/JP284092](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/JP284092): Methods, Intraoperative measurements, Eq.1, Muscle volume calculation, Patient-specific optimal fibre length calculation, Specific tension calculation; Data availability/Supporting Information. The article advertises a 48.3KB StatisticalSummary.xlsx containing figure/result data; its prior403 route was **not retried**. PubMed's official record lists Wiley/Ovid and no PMC full-text link. Specific tension remains an inferred whole-muscle normalizer because maximal force is activation-corrected and fibre length is functionally inferred. No cohort stress is converted into an individual's force. Article marked Open Access; exact reusable data license not verified in accessible text.
- [Persad et al., 2021, DOI10.1242/jeb.242722](https://journals.biologists.com/jeb/article/224/17/jeb242722/272026/In-vivo-human-gracilis-whole-muscle-passive-stress): Methods, Intraoperative data, PCSA, Optimal fiber length calculation, Data processing. Force calibration accounts for tendon thickness; volume includes density/skin-paddle correction. Architecture uses literature pennation and fibre/muscle ratio. Passive force is normalized to an **assumed** active tension, not a measured maximum. Its [official two-page supplement](https://journals.biologists.com/jeb/article-supplement/272026/pdf/jeb242722supp/) contains S1 harvested MTU imagery and S2/S3 species plots; no matched table was found in it. Main text points to S3 for calibration, whereas inspected supplemental text identifies S3 as log-transformed plots. This does not supply per-subject calibration coefficients. Eq.1 and Table2 are images without inspected pixels; their cells/formula are not transcribed. Copyright notice is present; a dataset reuse license was not established.
- [Persad et al., 2022, DOI10.1038/s41598-022-09861-y](https://www.nature.com/articles/s41598-022-09861-y): Buckle force transducer calibration, Intraoperative measurement, Procedure, Data availability, Code availability, Rights and permissions. Calibration includes zeroing and a force/voltage slope, corrected for tendon thickness. This is a procedure, not an accessible row dataset: raw data and LabVIEW code are available on request. Article explicitly CC BY4.0, subject to its third-party credit lines; this does not establish the license of unreceived patient data.
- [Wang et al., 2025, DOI10.1113/JP288322](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/JP288322): Abstract, Key points, Data availability/Supporting Information. The full route redirected to the abstract. Nineteen patients' curves are described; curve width predicts serial geometry and shortening includes tendon-compliance estimation. Data are available on reasonable request. The distinct 49.4KB StatisticalSummary.xlsx was inventoried first, then its official link attempted once;403 prevented content inspection. Its subject-row contents and reuse license remain unknown.

No patient identities or subject IDs were inferred between these publications. The overlapping surgical setting does not prove row correspondence, nor that the later series is an independent replicate of the earlier one.

## Access decisions and download limits

The inventory preceded the one newly attempted spreadsheet retrieval. Only the advertised small Wang spreadsheet was selected for that bounded attempt; no body imaging, archive, or broad data download was requested. Its403 ended that route. The Persad supplement was inspected through the ordinary browser PDF reader; no binary was deposited. No specimen record was downloaded.

Additional normally attempted routes were closed without substitutes:

- Original [Ates et al. direct spastic-gracilis force paper](https://www.clinbiomech.com/article/S0268-0033%2812%2900214-8/fulltext) returned403. No values, geometry or reusable-data claim was adopted from it.
- An official PMC entry for a related modelling paper, `PMC12912294`, presented a browser/reCAPTCHA check. The route was stopped; no redirect, challenge handling or alternative access method followed.
- The original specific-tension review publisher route, DOI10.1152/japplphysiol.00296.2024, returned an internal fetch error. It was not used as primary measurement evidence.

Search-result snippets, ResearchGate and other secondary mirrors were not used to recover denied data. Normal availability of article prose or an advertised spreadsheet name is not confirmation that its contents are downloaded, licensed or sufficient for calibration.

## Smallest admissible study unit

**Current admissible numeric specimen: none.** The smallest prospective unit is one identified gracilis muscle measured at the four documented postures in one procedure, with linked calibration, activation, passive force and geometry records. It would reproduce that study's observational and inferred quantities under its own preparation. It would not be a human-arm material law or a compatible calibration of the rat22°C kinetic medians.

Before choosing such a unit, an official accessible record must supply a persistent anonymous specimen key; measured force in newtons or raw voltage with its actual zero/gain/thickness calibration; measured passive baseline and stimulation metadata; paired volume and its corrections; posture-specific MTU/slack/tendon geometry; biopsy sarcomere measurements with interpolation/fixation labels; the fibre-length and PCSA conventions; actual temperature or an explicit unknown; and reusable-data terms. If maximal force is corrected or optimal length inferred, preserve that distinction in every output.

A measured active tendon force could identify a study-specific force scale at its recorded posture and activation. Conversion to a stress normalizer requires that specimen's linked area and projection/reference convention. A corrected maximum divided by an inferred PCSA identifies an inferred whole-muscle normalizer, not a directly measured local Cauchy stress. A passive-only specimen supplies no measured active cross-bridge scale.

No multiplication of cohort means, pairing of cadaver area with living force, reverse engineering of figure symbols into specimen IDs, or merging of separate publication cohorts is admissible. No contact request was sent and no numerical calibration was selected. The exact remaining blocker is accessible, licensed, linked subject records with the declared fields—not a missing algebraic conversion.
