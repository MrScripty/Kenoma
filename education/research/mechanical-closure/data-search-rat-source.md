# Rat source-family data search

**Accessible source-family records do not yet establish a same-specimen SI force/area/geometry/calibration bundle.** Three small observational MAT files were recovered and inspected; S1/S2 and OSF contents remain unverified because their normal published links failed. This is an evidence-access and field-linkage result, not proof that the authors never recorded the missing fields.

Read-only search dated 2026-10-06; [field-level receipt and inventory](../../data/anatomical-arm-v1/review/matched-calibration-data-search/rat-source-facts.json). Existing milestone `306d0aba` and all earlier packets were left untouched. No Git operation, symbolic calculation, model solve, author-code execution/import, or committed implementation/data copy occurred. Only this note and its JSON receipt were created.

## Official deposits and bounded inspection

The [2026 PLOS article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748) attributes experimental results to [S1 Data](https://doi.org/10.1371/journal.pcbi.1014748.s001) and [S2 Data](https://doi.org/10.1371/journal.pcbi.1014748.s002), both labelled ZIP. Each normal publisher click returned Internal Error. Archive entries and sizes were unavailable; no blind ZIP download followed. Its code link identifies the repository below. Article permission is CC BY; a separate supplemental manifest/license was not inspected.

The [original Horslen2023 acquisition paper](https://journals.biologists.com/jeb/article/226/18/jeb245456/329515/History-dependent-muscle-resistance-to-stretch) identifies its complete data/analysis deposit at the exact [published OSF view-only link](https://osf.io/3jy62/?view_only=4f09424a1c5d468798baa1cf8d673100). That normal click returned Internal Error; no token modification or other access workaround followed. The author-lab PDF link also returned Internal Error. OSF file inventory, license and specimen manifest remain unknown. The article is CC BY4.0; that does not verify the inaccessible deposit's file-level license.

The [official repository](https://github.com/timvanderzee/biophysical-muscle-model/tree/8c766dfb308051309193e7290ddd0bac3b726d11) was inventoried at commit `8c766dfb308051309193e7290ddd0bac3b726d11`, actual tree `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`. A fresh authorized API read of main returned that same July8 revision. The complete tree contains 89 MAT files: 3 under Data, 42 parameter fits and 44 model-output files, totaling 80,545,792 bytes. The largest, a 51,747,046-byte model-output file, was not downloaded. No LICENSE/COPYING-named file occurs in the complete tree.

The [Data README](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/README.md) distinguishes raw, reorganized, normalized and derived SRS levels; it says normalized time series were reviewer-supplied and derived SRS included in this revision. The repository is a July source snapshot, distinct from the September publication.

After inventorying exact sizes, ordinary pinned raw.githubusercontent.com reads recovered these files into `/tmp/rat-source-data-inventory-20261006`. Each read was capped at inventoried size plus one byte; exact size and Git blob SHA1 were verified. SHA256, parser inventories, shapes and finite/missing counts are in the receipt; full array payloads are retained only temporarily and are not redistributed. Total downloaded: 434,369 bytes. The GitHub connector's initial MAT failure was an unsupported UTF-8 format error, not a host access denial.

| Inspected file | Bytes / immutable blob | Actual fields and limits |
| --- | --- | --- |
| Data/force_pCa.mat | 923 / `49287cc837de16091987b619aa0c8f4b3076e3fb` | pCas(7), F0(11×7), Fmax(11); no IDs, geometry, gain, temperature or units |
| Data/SRS_data.mat | 31,483 / `1ee15118e2e741585702c0cb7867be57642e8efb` | F0, SRS_pre, SRS_post, th, SRSrel, F0s; derived arrays, no recorded trajectories/calibration |
| Data/active_trials.mat | 727 / `7b1ee00deddbde8504759692164ee3550113d1dc` | Aid(11×7), Fm(7×11); no embedded specimen manifest |
| Reproduce/Parameters/13Dec2017a/parms_biophysical_no_regular.mat | 401,236 / `cc28d2a9cf5cf441ae31c20528a5798b0d924d24` | bnds, newparms, optparms, out, redparms and opaque MATLAB workspace; historical fit inputs/output, not an admitted raw measurement archive |

Scipy's MAT reader parsed data and inert metadata only. Function handles were never evaluated. The 51,008-byte `__function_workspace__` payload in the sampled fit was not decoded; no assertion is made about hidden captured experimental arrays. Its newparms arrays ti/Cas/Lts/vts are prescribed inputs, while out.F/t and moment/force arrays are model output. Its saved Fmax=120 differs from force_pCa row2 Fmax=207.21964733022145; it is not accepted as a matched sensor-calibrated denominator.

## Field-level specimen linkage

The acquisition publication gives rat soleus, 11 permeabilized fibers from two female Sprague–Dawley rats, 22°C, a 2.6µm sarcomere target, recorded reference fiber length, 1kHz sampling and Aurora312/403 instruments. Those are cohort/procedure facts, not a recovered per-specimen calibration sheet. PLOS adds reference-length and sarcomere cohort summaries. Body-text searches did not recover diameter/CSA measurement descriptions; inaccessible underlying files could still contain them. [Horslen2023 Methods](https://journals.biologists.com/jeb/article/226/18/jeb245456/329515/History-dependent-muscle-resistance-to-stretch), [PLOS Methods](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748).

The exact processing blobs cited in the receipt use one consistent 11-label order: 12Dec2017a, 13Dec2017a, 13Dec2017b, 14Dec2017a, 14Dec2017b, 18Dec2017a, 18Dec2017b, 19Dec2017a, 6Aug2018a, 6Aug2018b, 7Aug2018a. This supports an index-to-fiber association under those scripts. The three data files have no embedded labels; individual animal membership and original acquisition-file identity are unverified.

| Required field | Recovered evidence | Admission consequence |
| --- | --- | --- |
| Force denominator | Fmax ranges 55.89757774227901–321.2740665983838; exactly equals each F0 row's maximum and pCa4.5 entry | Processed channel numbers recovered; newtons unverified |
| Force channel/gain calibration | calc_force_pCa extracts gain from original file_info_string, applies overrides, divides raw force by 1000/gain | Missing original channel convention, sensor calibration, gain records and zero/tare |
| CSA/reference configuration | No field in the three data files | No matched area or stress normalization admitted |
| Fiber/sarcomere lengths | determine_N_sarcomeres expects new_data.muscle_length and sarcomere_length in absent raw files | Expected fields do not establish recovered values; cohort means cannot replace specimen geometry |
| Temperature | Publication cohort context only | No per-trial temperature trace recovered; no cross-temperature borrowing |
| Activation | Actual pCas=[4.5,6.1,6.2,6.3,6.4,6.6,9]; normalized Fm and Aid | Chemical levels and relative activation available; bath/calcium calibration records unverified |
| Passive response | Eleven pCa9 F0 entries | Baseline numbers available; no matched passive time series or upstream tare convention |
| Series compliance | Historical fitted parameters | No independently measured apparatus/end-attachment compliance admitted |
| Force/length/time trajectories | Data README says external; no trajectories in the three data files | S1/S2/OSF inventory required before trajectory selection |

The [processing force chain](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L28) and [normalization](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/normalize_data.m#L154) do not themselves document SI conversion. Rat22°C source values remain separate from human15°C material.

## Preserved version caveats and smallest next step

The actual SRS_data.mat thresholds are [0,.05,.1,.25,.7,1.5]. The pinned [calc_data_SRS.m](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/calc_data_SRS.m#L151) actively uses [0,.05,.3,.7,1.2], writes SRS_data_DT10_new.mat and additionally saves SRSrel2, absent from the included MAT. That script is not proven the exact generator of the stored SRS dataset. Negative SRS values and missing entries were preserved, not filtered into an artificial pass.

The smallest **data recovery** is an ordinary accessible supplement/OSF file inventory plus one named fiber's unconditioned and conditioned trial pair, corresponding activation-reference and pCa9 records, and its geometry/calibration sheet. Keep acquisition ID, force-unit/gain/tare chain, reference length/sarcomere and area configuration linked to that same fiber. A dimensionless trajectory comparison can precede SI calibration only after its measurement/normalizer lineage is verified; the recovered SRS arrays alone do not supply a history.

If those calibration records do not exist, the smallest **new measurement** for a local active-force scale and frozen-response stiffness is one explicitly identified rat fiber at a fixed reference geometry and temperature, calibrated force/length channels, reference area measurement, baseline pCa9 and maximal/selected-activation holds, followed by a small length perturbation and relaxation recorded with the same channels. Record attachment/apparatus compliance or directly resolve the CE displacement. This local experiment would not identify an entire PE/SE nonlinear law or qualify an arm-scale constitutive model; that requires a separately declared range of passive/series measurements and further specimens. No such experiment or replay was executed here.
