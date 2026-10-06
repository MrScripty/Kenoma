# Matched mechanical calibration: data admission decision

Research-only milestone, 2026-10-06, based on preserved commit `306d0aba8e024086b9f4d04cc4d74f137b8b443a`. **No inspected specimen meets the complete force–area–reference geometry–condition–passive correction requirement. No physical calibration, constitutive replacement or new arm trajectory is selected.** This bounded search identifies acquisition targets and missing fields; it does not establish that suitable data do not exist.

## Provenance matrix

Each row keeps original preparation and measured, derived and unknown quantities separate. An advertised archive is not an inspected specimen. The linked lane reports retain original-paper locators, file inventories, exact access outcomes and reuse qualifications.

| Candidate / official acquisition | Evidence actually obtained | Calibration linkage still missing | Permitted next use |
| --- | --- | --- | --- |
| Human/bonobo MMU [10.23634/MMU.00640738](https://repository.mmu.ac.uk/articles/dataset/A_comparison_of_the_force-velocity_relationship_of_bonobo_and_human_fibres/32616549) | Official indexed metadata advertises 34.64 kB, CC BY 4.0; original methods specify human skinned fibers at 15°C | Actual files/rows/IDs, sensor calibration, passive convention; reconcile diameter measured in air with force measurement configuration | First small human archive to inspect when ordinary access works; no values admitted now |
| Rat source family [pinned repository](https://github.com/timvanderzee/biophysical-muscle-model/tree/8c766dfb308051309193e7290ddd0bac3b726d11), [published OSF acquisition link](https://osf.io/3jy62/?view_only=4f09424a1c5d468798baa1cf8d673100) | Four hash-verified MAT files, 434,369 bytes; three observational files contain processed force denominators, activation and derived SRS; rat22°C procedure documented | Embedded SI force/gain/zero, area, individual length/sarcomeres, raw histories and acquisition IDs; repository data license unverified | Recover one source-family acquisition/calibration bundle before replay or SI scale selection |
| Rabbit Altman2015 [Dryad jf35g](https://doi.org/10.5061/dryad.jf35g) | Original methods plus 18-file inventory; untreated relaxed/activated pairs advertised; 5°C | Actual pair, channel units/gain/zero, paired area/length record, passive correction; native files roughly 326–333 MB each | One declared pair with its calibration/geometry; no mass download or cross-species kinetics transfer |
| Haeger2020 [Dryad tht76hdwp](https://doi.org/10.5061/dryad.tht76hdwp) | Archive describes needle-stiffness calibration and displacement-to-force chain; small table/track inventory | Actual needle/track join, preparation, area/reference geometry, activation, temperature and passive convention | Inspect small calibration table and one actual preparation track; no model input from template alone |
| Living human gracilis [Binder-Markey2023](https://doi.org/10.1113/JP284092), [Persad2022 protocol](https://doi.org/10.1038/s41598-022-09861-y) | Original acquisition/correction procedures; passive supplement figures; no subject table obtained | Same anonymous subject calibration/activation/passive/volume/geometry rows, temperature and reusable-data terms | Study-specific tendon-force/inferred-PCSA reconstruction; no direct local Cauchy-stress or arm validation claim |

Companion reports: [human fiber](data-search-human-fiber.md), [rat source](data-search-rat-source.md), [animal candidates](data-search-animal-candidates.md), [whole muscle](data-search-whole-muscle.md). Other screened leads remain in those inventories rather than being silently discarded.

## Smallest justified calibration experiment

The first conditional experiment is **one identified human fiber from the small MMU archive**, with its actual force, area or diameter, segment length, sarcomere length and acquisition conditions joined on one persistent record. Before any fit:

1. Preserve official file version, hash, license and specimen key. Establish force units and the actual sensor calibration/zero lineage; a transducer model number alone is insufficient.
2. Identify the configuration of area measurement, its geometric assumptions and any swelling correction. Keep diameter in air separate from area in the bath. Establish whether reported force includes passive tension and which baseline was subtracted; do not infer a tare from the activation protocol.
3. Reconstruct that specimen's reported stress from its measured force and compatible area, using documented conversions and source rounding. Accept only a discrepancy explained by those records. Missing pairing, incompatible configurations or unexplained units stop the experiment.
4. Only then select a declared reference-state amplitude experiment with a compatible human model. One amplitude observation does not identify kinetics, cross-bridge count, serial compliance, passive/series nonlinear laws or bulk response. It does not validate a whole human arm.

No numerical inputs are chosen now: file contents, calibration/tare and matched configuration are unverified. This is an evidence blocker, not an approval requirement. If the archive contains only summary force–velocity results, retain those observations at their supported scope and record absent fields explicitly.

The source-family alternative is one named rat fiber's original active/passive reference and conditioned/unconditioned histories, joined to that fiber's force calibration and geometry. The normal acquisition entry points are the exact published OSF link above and PLOS [S1 Data](https://doi.org/10.1371/journal.pcbi.1014748.s001)/[S2 Data](https://doi.org/10.1371/journal.pcbi.1014748.s002). Their inventories remain inaccessible here. Apparatus/attachment compliance or directly measured CE displacement is necessary before interpreting a perturbation as local CE stiffness. Do not assign published rat kinetics to a human or rabbit amplitude observation.

## Verification and preserved limits

The new read-only verifier [verify_matched_calibration_data.py](../../tools/verify_matched_calibration_data.py) checks the four temporary binaries against immutable source hashes and the committed field summaries. It parses numeric observational data only; the sampled fit receives an inventory-only check, and its opaque workspace/function handles are not decoded or evaluated. It preserves missing/negative entries and checks the denominator relationship without assigning SI units. No author implementation or raw arrays are redistributed.

Predeclared checks are exact byte size, SHA256 and Git blob SHA1; exact MAT field/shape/class inventories; equality of observational shape/type/finite/missing/range summaries; Fmax row-maximum/pCa4.5 identities; stored-threshold consistency and the retained generator-version mismatch. The verification records its environment and command, produces a raw log and JSON receipt, and fails if any check is false. A source-text claim about the generator remains the earlier pinned read-only audit's evidence, rather than being reconstructed from the binary.

Ordinary host denials, proxy-tunnel403 and browser challenges terminated their routes; unsupported binary-format/tool errors are identified separately. No network/credential settings were changed and no contact request was sent. No render is needed for this data-inventory milestone; previous render and numerical evidence remain untouched.

The arm qualification remains unchanged: accepted reduced trajectories and one dense increment do not constitute a self-consistent dense trajectory; compression, matched-time differences and full nodal/quadrature/timestep convergence remain unresolved. Replacing missing metrology with more symbolic checks, solver iterations or looser gates would not advance that qualification.
