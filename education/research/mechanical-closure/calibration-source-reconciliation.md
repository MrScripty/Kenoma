# Physical calibration source reconciliation

**Physical force calibration remains incomplete.** The original acquisition paper identifies the instrument and describes stress measurements, while the pinned processing code exposes gain correction and dimensionless normalization. Neither provides, in the material inspected here, the specimen-specific chain from stored raw values to newtons and a declared section area. No human coefficient, SI force scale or passive offset is selected.

This new audit uses original [van der Zee et al. (2026), Methods](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), its original acquisition reference [Horslen et al. (2023), Materials and Methods](https://doi.org/10.1242/jeb.245456), and read-only author code pinned to commit `8c766dfb308051309193e7290ddd0bac3b726d11`. It supplements [source-code-initialization-audit.md](source-code-initialization-audit.md) and [dimensional-contractile-mapping.md](dimensional-contractile-mapping.md). No simulations, parameter fitting, code imports, binary redistribution, old-file edits or Git mutations occurred.

The committed [original PLOS Table 2/3 visual audit](original-plos-table-visual-audit.md), commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`, establishes actual original-pixel inspection and satisfies the visual column prerequisite for its identified publisher PDF. Its [receipt](plos-original-table-visual-evidence/receipt.json) and preserved [Table 2](plos-original-table-visual-evidence/table-2-original.png) and [Table 3](plos-original-table-visual-evidence/table-3-original.png) crops are the table-transcription evidence. The parent also inspected those crops. This calibration audit does not repeat that work or reselect medians; the sensor, area and passive-convention uncertainties below remain unresolved.

## What the original experiments establish

The 2023 apparatus description names Aurora Scientific motor 312 and force transducer 403, SLControl acquisition, and 1 kHz sampling/length updates. Microscopy established 2.6 µm mean sarcomere length, used as assumed optimum; each fiber's recorded reference length scaled later movements. Experiments maintained 22°C. Isometric activation was characterized by mean stress over 0.9 s, divided by pCa 4.5 stress. The inspected Methods do not specify diameter, cross-sectional-area geometry, sensor calibration constants or stored-channel units. The conditioning-transient subtraction described later isolates a test stretch; it is not a passive-baseline subtraction. [Original acquisition paper, apparatus/activation/outcome-measures sections](https://doi.org/10.1242/jeb.245456).

The 2026 Methods report reference length 0.8±0.2 mm, microscopy sarcomere length 2.60±0.05 µm, and serial count \(N_s=306\pm78\), all mean±SD for this rat preparation. The text calls count experimental; code estimates it as fiber length divided by sarcomere length. Empirical traces are scaled to their pCa-matched isometric trial, then divided by maximum isometric force at pCa 4.5. No passive subtraction is specified there. Stroke 10 nm, cross-bridge stiffness 0.5 pN/nm and attached fraction 0.5 are model assumptions, while PE rest length/stiffness and SE coefficients are fitted. These are source-preparation facts and modeling choices, not human calibration. [Original 2026 article, Experimental data, Data processing, Cross-bridge cycling, Elastic interface and Fitted parameters](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748).

## What the pinned processing actually does

The existing [parameter facts](source-code-parameter-facts.json) pin commit `8c766dfb308051309193e7290ddd0bac3b726d11` and tree `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`. It predates final publication; this audit makes no final-publication code-parity claim.

| Processing step | Inspected operation | What remains unknown |
|---|---|---|
| Acquisition-channel conversion | Read recording gain from two characters of `file_info_string`; divide stored `new_data.force` by 1000 and gain | Whether the incoming channel is voltage, force or already stress; upstream tare/area conversion |
| Isometric reference | Average initial samples; median across trials of the same pCa; \(F_{\max}=\max F_0\) across measured pCas | Whether upstream values have already had slack or passive force removed |
| Run-down/reference scaling | Trace/pre-stretch mean × matching \(F_0/F_{\max}\) | Physical magnitude erased by the ratios |
| Relative length | \((L-\bar L_{\rm pre})/\bar L_{\rm pre}\) | Absolute geometry must be retained separately |
| Serial count | Read `muscle_length` and `sarcomere_length`, correct entries above \(10^{-5}\) by dividing by 10, compute their ratio | Individual source metadata and validity of that stated typo correction |

Source locators: [reorganize_data.m:40](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/reorganize_data.m#L40), [calc_force_pCa.m:50](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L50), [calc_force_pCa.m:87](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L87), [calc_force_pCa.m:108](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L108), [normalize_data.m:151](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/normalize_data.m#L151), [determine_N_sarcomeres.m:15](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/determine_N_sarcomeres.m#L15).

None of those operations explicitly subtracts the pCa 9 reference. The normalized pCa 9 condition can therefore remain nonzero in this processing path. This is a statement about inspected arithmetic; it does not prove that upstream acquisition/Matlab conversion lacked a tare or passive subtraction. The old initialization audit's kPa axis observation remains a label, not a recovered physical calibration.

The serial-count script targets a local transformed-raw-data folder, rather than supplying the individual geometry records. Its count is a length ratio, not a literal count of individually resolved sarcomeres along the entire specimen. Published sample mean/SD cannot assign \(N_s\) to the inspected 7Aug2018a fit. Likewise the fit's saved \(\gamma=130\) converts relative fiber length to normalized link coordinates; it does not identify specimen reference length or macroscopic \(\ell_\gamma=2N_s d_{\rm ps}\). The previously recorded historical \(h=12\) nm versus current \(\gamma=130\)/10 nm inconsistency remains unresolved by this calibration audit.

## Why passive conventions matter

Let a physical reference measurement be \(T_0=T_{\rm active,0}+T_{\rm passive,0}\). If the processed denominator is total \(T_0\), its maximal total normalized force is one and its active contribution is

\[
\widehat T_{\rm active,0}=1-\frac{T_{\rm passive,0}}{T_0}.
\]

If the denominator is passive-subtracted active force instead, adding a separately calibrated PE has a different normalization. These are independent algebraic alternatives; the inspected sources do not establish which upstream channel convention supplies the saved files.

Thus a statement that maximal normalized CE force equals one cannot by itself determine the maximal normalized **total** force when a nonzero PE is added. Record the actual pre-stretch passive value and denominator definition before imposing either constraint. A zero-load/slack instrument baseline is also distinct from passive tension at the reference length.

Likewise a reported stress requires its area convention. Conversion \(T=\sigma A\) must specify measured specimen area and configuration. No measured reference or current area for these eleven specimens was recovered here, so neither \(F_{\max}\) MAT numbers nor the fitted PE/SE coefficients become N, Pa or human tissue constants.

## Public data and access boundaries

The 2026 publisher explicitly advertises S1/S2 Data as two ZIP supplements of short-range-stiffness data: [S1 Data](https://doi.org/10.1371/journal.pcbi.1014748.s001), [S2 Data](https://doi.org/10.1371/journal.pcbi.1014748.s002). Their existence and labels are verified; their raw-channel/calibration contents were not inspected in this lane.

The 2023 paper advertises its complete dataset, R software and analysis notes through [the exact published OSF link](https://osf.io/3jy62/?view_only=4f09424a1c5d468798baa1cf8d673100). An ordinary link read returned an internal error, so public availability is asserted by the article while actual raw/calibration contents remain unverified here. No inventory or archive download was duplicated.

The pinned [Data README](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/README.md#L9) describes Level 3 time series as reviewer-supplied and Level 4 SRS data as included, with an intention to publish more later. That July-era note does not override September publisher supplements or prove that raw acquisition metadata are absent from those supplements. Distinguish the pinned repository revision from the final publication data package.

The acquisition paper refers detailed methods to Campbell (2006) and Campbell–Moss (2002). Original publisher routes returned errors/403; the 2006 PMC route presented a browser challenge, and inspection stopped. Search-index excerpts suggest older preparations used a circular area estimate, but they do not establish area measurements for the 2023 dataset and no numerical area from those older specimens is imported. The original [SLControl methods paper](https://doi.org/10.1152/ajpheart.00295.2003) full-text route returned 403. Manufacturer documentation listed no readable 403 calibration entry in the retrieved page. No access challenge, authentication boundary or network restriction was bypassed.

## Calibration classification and completion condition

| Quantity | Present status |
|---|---|
| Rat preparation temperature, reference geometry mean/SD | Measured/reported source facts |
| Individual \(N_s\), reference fiber length and section area for the inspected fit | Unknown in inspected data |
| 10 nm stroke, single-head stiffness, maximal attached fraction | Assumed/model normalization choices |
| Kinetic rates, activation sigmoid, PE/SE parameters | Fitted values or source-specific fixed choices; retain source family/units |
| Raw sensor-to-N conversion, stress area convention, upstream zero/passive subtraction | Unknown |
| Whole human force/head capacity/area, body-temperature kinetics | No source calibration supplied |

A physical replay becomes reviewable only when the same specimen's raw unit metadata, sensor/gain calibration, reference geometry and area, tare/passive convention, and pCa reference denominator are linked to the exact waveform and parameter file. Until then, parameter-free dimensional identities and explicitly dimensionless source-equation fixtures remain useful; a tuned SI release input would not close the evidence gap.

Additional pinned blobs inspected in this lane: `reorganize_data.m` = `2259a7aaae4e7822ff685d1b809150a43089dfca`; `determine_N_sarcomeres.m` = `ade7652c32dd5d17c93892d88c9eb133684a8c6b`. The normalization and pCa-processing blob hashes are recorded in the existing initialization audit. Original Methods were read as publisher HTML; no table-column or pixel claim is made here.
