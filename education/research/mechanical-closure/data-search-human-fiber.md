# Human isolated-fiber data search

Research-only evidence, 2026-10-06. Existing packet `306d0aba` and all earlier files are preserved. No numerical experiment, symbolic check, simulation, author-code execution, Git mutation, large archive download, or author contact was performed.

The search found a small, licensed institutional archive with a human subset and unusually clear acquisition methods. Its contents remain inaccessible in this environment. **No human specimen has yet supplied an inspected, matched force–area–geometry record with a verified passive correction.** This is a bounded search result, not evidence that no suitable public dataset exists.

## Field matrix

“Methods” means described acquisition, not a recovered row. “Unknown” means unverified, not necessarily absent from the experiment.

| Original source | Force/stress | Area convention | Reference geometry | Preparation, activation, temperature | Passive/baseline convention | Same-specimen downloadable rows |
| --- | --- | --- | --- | --- | --- | --- |
| Degens, Bobbert & Scholz 2025; MMU dataset | Methods: Po in µN, specific tension N/cm² | Diameter in air; assumed circle | SL 2.53–2.69 µm; FL range 0.70–3.97 mm | Skinned; pCa 4.5; 15°C | Not explicit in inspected Methods | Archive advertised; contents and identifiers unverified |
| Lassche et al. 2020; Dryad | Specific-force study advertised | Unknown from accessible landing | Unknown | Human VL/TA, FSHD/control | Passive-force findings advertised; correction unknown | Only two supplementary kinetics/Hillslope tables advertised; file denied |
| Gejl et al. 2021 | Calibrated transducer; mN and kN/m² | Three diameters at slack, cylinder assumption; no swelling correction | Force at 120% slack; absolute SL unknown | Chemically skinned human triceps/VL; pCa 4.7; 22.1°C | 60 s passive plateau; subtraction unspecified | Author-request only; separate plotted points cannot establish row pairing |
| Gohlke et al. 2024 | Tension = force/CSA; raw-force units not verified | Width/depth at four sites; assumed ellipse | Active SL 2.6 µm; passive SL measured during ramps | Permeabilized human titinopathy/control; 15°C | Relaxing passive protocol described; active subtraction unspecified | Supplement unreadable; raw matched records unverified |
| Jeon et al. 2019 | mN and kN/m² | Width/depth and ellipse | SL 2.5 µm; exposed FL reported | Skinned human VL; pCa 4.5; 15°C | Peak minus unloaded-shortening baseline; not a separately demonstrated passive tare | Article reports aggregate results/correlations; recoverable labeled rows not found |

Sources and precise reading locations follow. The companion [human-fiber-facts.json](../../data/anatomical-arm-v1/review/matched-calibration-data-search/human-fiber-facts.json) distinguishes article evidence from archive evidence and records stopped access routes.

## Strongest bounded archive candidate

The [MMU dataset](https://repository.mmu.ac.uk/articles/dataset/A_comparison_of_the_force-velocity_relationship_of_bonobo_and_human_fibres/32616549), DOI **10.23634/MMU.00640738**, is described as contractile properties of human and bonobo single fibers: 34.64 kB, CC BY 4.0, legacy deposit 2025-07-21, current posting 2026-06-09, collection date 2007. These facts were visible in the official landing's search-indexed content; the live landing did not render. No filename, checksum, columns, or row count was recovered.

The [original article](https://onlinelibrary.wiley.com/doi/full/10.1002/jez.70015), Methods §2, identifies 85 human VL fibers from young men, previously published by Gilliver et al. 2009, measured with the same equipment and solutions as the comparison specimens. It identifies the Aurora 403A force transducer, but does not supply its calibration coefficient or explicitly define passive subtraction. Reported human Table 2 values are group means ± SEM; they are not calibration specimens. The article's archive link establishes provenance, not proof that the deposited records contain every requested field.

## Other original-source evidence and usability

The [Lassche Dryad record](https://datadryad.org/dataset/doi:10.5061/dryad.04gq02h), “Data files” and “Usage notes,” advertises one **18.59 kB Supplemental tables.docx** covering cross-bridge cycling kinetics and Hillslope. [Dryad terms](https://datadryad.org/terms), permission/usage clauses, permit dataset reuse and describe a copyright waiver; website metadata has a separate CC BY 4.0 convention. The exact item-specific license badge was not independently extracted. The sole file returned 403. The linked [original Neurology article](https://doi.org/10.1212/WNL.0000000000008977) also returned 403. Neither file contents nor acquisition metrology was inferred from the abstract.

The [Gejl original article](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.682943/full), “Muscle Fiber Preparation and Cross-Sectional Area,” “Force Recordings,” and “Data availability statement,” provides the matrix conventions and says raw data are available upon request. Its article license is CC BY; that does not expose or license an unretrieved private dataset. The HTML Table 1 area heading renders as mm² with values around thousands; this search neither resolves that display nor adopts numeric areas. No supplement was listed in the inspected HTML.

The [Gohlke original article](https://academic.oup.com/hmg/article/33/23/2003/7758269), “Muscle mechanics” and Figures 7–8 captions, provides useful active/passive metrology. Passive dimensions are taken at slack, while active dimensions are remeasured at 2.6 µm. The distinction matters when matching stress to area. Supplementary Material failed to render. A reuse license and specimen-level file inventory were not verified; no patient/control plotted value was digitized or generalized.

The [Jeon original publication, DOI 10.12965/jer.1938336.168](https://pmc.ncbi.nlm.nih.gov/articles/PMC6732543/), “Measurements of single fiber contractile properties in vitro” and Figures 3–4, was readable as primary indexed text. It uses an unloaded-shortening baseline to address force drift. Article reuse is CC BY-NC 4.0. That supports a bounded metrology example, but aggregate figures do not provide an identifiable joint force/area/reference row.

The [Kalakoutis original 2023 article](https://journals.physiology.org/doi/full/10.1152/ajpcell.00525.2022) returned 403 and its PMC route displayed a browser challenge; both were stopped. The Hinks original human residual-force study's PMC route also challenged. These are access exclusions, not negative data findings. No alternative route was used to defeat a denial or challenge.

## Archive exclusion established before download

[Zenodo 15278114](https://zenodo.org/records/15278114), “Description” and “Files,” is associated with critical-illness myopathy, but advertises molecular-dynamics inputs/topologies/trajectories/analysis: three 16 GB archives, 48 GB total, plus a 1.1 kB README. This is not an advertised measured human force–CSA table. No archive was downloaded, and its blank rendered license field was not filled by assuming a default.

## Smallest justified next experiment

**Present disposition: no SI calibration experiment.** The smallest conditional next step is an archive integrity and metrology audit of one human fiber from the small MMU deposit, when ordinary authorized access succeeds. This must precede any parameter selection:

1. Inspect the inventory/license and a bounded table; preserve file hash/version and human/fiber identifier. Match Po, CSA or underlying diameter, specific tension, FL and actual SL on the same record, with missing fields explicit.
2. Establish sensor force units/calibration and whether Po removes passive tension, unloaded baseline, both, or neither. Keep any reference-area convention and swelling correction separate. Confirm that archive rows use the article's activation, preparation and temperature.
3. Check the source's reported per-fiber stress against its force and area with the documented conversions and rounding. Reject missing identity, incompatible states/areas, unexplained units or discrepancy. Never multiply cohort mean stress by cohort mean area to manufacture a measured force.
4. Only after a reviewed protocol, test a single declared normalized reference state's force scale against that specimen's measured active force. A rat kinetic fixture is not the matching human variant; changing amplitude cannot validate its human kinetics, head count, series geometry, descending force–length response, or whole-arm stability.

If the archive has only force–velocity summaries without FL/SL, calibration records or passive conventions, preserve it as an amplitude/area observation and do not run calibration. The missing concrete inputs are a deidentified same-fiber row, force calibration/tare recipe, area state/metrology, reference segment/sarcomere geometry, and documented activation/temperature/preparation. Research and ordinary bounded inspection are authorized; the experiment is blocked by unverified evidence. No author contact was attempted.
