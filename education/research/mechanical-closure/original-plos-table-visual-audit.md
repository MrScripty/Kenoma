# Original PLOS Tables 2/3: pixel verification obtained

**Actual original PDF pixels were rendered and inspected on 2026-10-06. The visual column prerequisite is satisfied for the file identified below.** The previously inferred two-state XB column association is confirmed, including the activation rows and blank cells. This additive audit leaves the earlier blocker receipt, frozen 144-case benchmark, mechanics, solver, book and proofs unchanged. It runs no controlled experiment and establishes no human force/area calibration or final-publication/code parity.

Source: van der Zee TJ, Simha SN, Milburn GN, Campbell KS, Ting LH, De Groote F (2026), [Cross-bridge model for predicting muscle short-range stiffness during movement](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), PLOS Computational Biology 22(9): e1014748. Research base: `7c8ec58ee8df051a387500b8555e9fac71b6569a`.

## Original identity and inspection

One ordinary GET to the [publisher printable PDF](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable) returned **HTTP 200**, `application/pdf`, **5,532,793 bytes**, with no redirect or retry. Requested and effective URLs are identical. Request limits were 25,165,824 bytes, 20 s connect and 60 s total. The response date was `2026-10-06 07:14:05 GMT`, ETag `CNjH6dHI5JYDEAE=`, Last-Modified `2026-09-10T17:45:56.361Z`. Network, secrets and proxy settings were unchanged; no denied route, challenge or alternate host was used.

Original PDF SHA-256:

```text
20f16f9890d1ff1d65cb8e75d38f24e7c2b5a73779052825faa36f45a78531cf
```

The file is a genuine 37-page PDF 1.4, 612×792 points per page. Printed publication date: September 1, 2026. PDF metadata creation/modification: September 4, 2026, 11:15:13/11:15:39 UTC. These identify the currently served file; they do not establish that a prior text-only retrieval had identical bytes. Raw PDF remains external at `/tmp/kenoma-plos-visual-20261006/journal.pcbi.1014748.pdf`.

Poppler `pdftoppm` 26.05.0 rendered full printed pages 21/22 at 160 dpi. Both actual PNG images were opened and visually inspected. PyMuPDF 1.26.6 then rendered original table crops at 216 dpi and context crops at 180 dpi; those images were inspected too. No table was redrawn. All image identities, render settings, row boundaries, displayed values and selected response metadata are in [receipt.json](plos-original-table-visual-evidence/receipt.json), SHA-256 `5fd9e711b4c4764a092f4fe225c4b26b86a497515c16c7013235b297447d5b48`.

Supporting checks passed: original PDF hash; exact re-render/hash agreement for all six preserved PNGs; positional text agreement with all 11 Table 2 value cells and all 84 Table 3 model cells (49 populated, 35 blank); and report-relative links. The positional check supplements actual pixel inspection.

Coordinates below are PDF points (1/72 inch), **top-left origin**, rectangles `[x0,y0,x1,y1]`; table-rule coordinates are rounded to 0.001 point. Printed page 21 is zero-based page 20; printed page 22 is zero-based page 21.

| Original evidence | Table body rectangle | Crop rectangle | Crop pixels | PNG SHA-256 |
|---|---|---|---|---|
| [Table 2 pixels](plos-original-table-visual-evidence/table-2-original.png), printed 21 | `[36,532.930,576,698.468]` | `[34,509,578,714]` | 1632×615 | `ddb2a72b9b4284cdbeec88f04cb73fbdb0373bbe3260477accaf38d6838caae3` |
| [Table 3 pixels](plos-original-table-visual-evidence/table-3-original.png), printed 22 | `[36,107.388,576,326.995]` | `[34,94,578,342]` | 1632×744 | `6613913b3fe735c021b6f73574af755c0b34c36ba177ecfd17693d9e82901fc5` |

## Transparent transcription

[Original Table 2](https://doi.org/10.1371/journal.pcbi.1014748.t002) has columns Symbol, Meaning, Value, Reference. Their x boundaries are `36,80.162,461.699,514.205,576`. Row-specific y boundaries are in the receipt. Descriptions below are shortened; values, units, symbols and reference associations are preserved.

| Symbol | Description | Value as printed | Reference |
|---|---|---|---|
| dps | Stroke | 10 nm | [105] |
| kCB | Head stiffness | 0.5 pN/nm | [106,107] |
| w | Detached-head width | 3 nm | √(kCB/(kB·T)); [20,31], footnote 1 |
| E1 | Negative-strain detachment exponent | 2 | [31] |
| Γ1 | Forced detachment rate | 3000 s⁻¹ | [39], footnote 2 |
| φ1 | Reattachment rate | 1000 s⁻¹ | [39], footnote 2 |
| Noverlap | Accessible-site fraction | 1 | See text |
| koff | Thin deactivation | 80 s⁻¹ | [108], footnote 3 |
| k1 | Thick activation | 6.17 s⁻¹ | [20] |
| k2 | Thick deactivation | 200 s⁻¹ | [20] |
| β | Attached-head normalization fraction | 0.5 | [109] |

Caption footnotes give T=295 K and kB=1.380649×10⁻²³ m² kg s⁻² K⁻¹; footnote 2 describes rates approximately 200 times regular attachment/detachment rates; footnote 3 marks temperature correction. Table 2 is a shared fixed-parameter list, not a statement that each family enables every listed pathway. In particular, its k2=200 s⁻¹ must not override the noncooperative family switches.

[Original Table 3](https://doi.org/10.1371/journal.pcbi.1014748.t003) reports **medians across seven fibers**. The eight column boundaries are `36,93.678,172.539,224.089,281.863,344.533,428.539,512.545,576`. **∅ denotes a visually blank gray model cell, never zero.** The unit-column dash is retained separately as “–”. Displayed decimal precision is preserved.

| Parameter | Unit as printed | Hill (no SE) | Hill (with SE) | 2-state XB | 2-state XB coop | 3-state XB coop | 4-state XB coop |
|---|---|---:|---:|---:|---:|---:|---:|
| nH | – | 4.4 | 3.3 | 3.1 | ∅ | ∅ | ∅ |
| Ca50 | µM | 0.77 | 0.78 | 0.83 | ∅ | ∅ | ∅ |
| vmax | xps·s⁻¹ | 440 | 76 | ∅ | ∅ | ∅ | ∅ |
| ρ | (xps⁻¹) | ∅ | 0.21 | 0.24 | 0.30 | 0.24 | 0.26 |
| σ | F0 | ∅ | 0.19 | 0.19 | 0.02 | 0.2 | 0.15 |
| kPE | F0·(xps⁻¹) | 0.03 | 0.006 | 0.002 | 0.004 | 0.002 | 0.002 |
| f1 | s⁻¹ | ∅ | ∅ | 52.0 | 67.1 | 84.5 | 79.5 |
| g1 | s⁻¹ | ∅ | ∅ | 4.0 | 3.4 | 3.5 | 6.4 |
| g2 | s⁻¹ | ∅ | ∅ | 21.1 | 26.6 | 23.8 | 21.2 |
| E2 | – | ∅ | ∅ | −0.6 | −0.4 | −0.6 | −0.7 |
| kon | µM·s⁻¹ | ∅ | ∅ | ∅ | 41.4 | 44.4 | 43.9 |
| kc | – | ∅ | ∅ | ∅ | 15.4 | 3.8 | 4.0 |
| kF | (F̃CB,max)⁻¹ | ∅ | ∅ | ∅ | ∅ | 210 | 223 |
| xcrit | xps | ∅ | ∅ | ∅ | ∅ | ∅ | 2.5 |

The noncooperative **2-state XB** column occupies x=`281.863–344.533`. Its activation entries occupy y=`130.196–156.201`; rates f1/g1/g2 occupy y=`212.184–255.096`; E2 occupies y=`255.096–268.201`. Thus nH=3.1, Ca50=0.83 µM and the rate quartet 52.0,4.0,21.1,−0.6 belong to the same model column. Its series/passive entries are ρ=0.24, σ=0.19 and kPE=0.002, with the original units above. They are not SI stiffness coefficients or an individual fitted parameter set.

## Typography, units and version boundaries

Two source typography issues are now verified in pixels. Table 2 and [printed page 23](plos-original-table-visual-evidence/original-width-context.png), clip `[34,95,579,250]`, display **√(kCB/(kB·T))**, while stating w=3 nm. Dimensional analysis makes that displayed radical an inverse length, so it does not justify a length-valued thermal width. This report preserves it without silently reversing the fraction. Separately, Table 3 displays **kon in µM·s⁻¹**, with no inverse exponent on µM. If calcium is supplied in µM and the activation flux has units s⁻¹, dimensional consistency would instead require µM⁻¹·s⁻¹. That is an inference about a needed convention, not a corrected source transcription; the calcium/pCa convention must be declared before using the cooperative rates.

Full printed page 22 also visually confirms equations 3–6: x=(d−dps)/dps; F̃CB=B+Q1; Gaussian prefactor f1/(√(2π)·w) with exponent −x²/(2w²); and detachment Σgi exp(−xEi). Combining the table's dimensional width and stroke gives **normalized w=3/10=0.3** as our conversion. For the two-state table column, g(x)=4 exp(−2x)+21.1 exp(+0.6x) s⁻¹. This strengthens the publication transcription only.

The author [commit 8c766dfb308051309193e7290ddd0bac3b726d11](https://github.com/timvanderzee/biophysical-muscle-model/commit/8c766dfb308051309193e7290ddd0bac3b726d11) was independently reread and dated **2026-07-08T12:06:31Z**, preceding the article. Its tree identity from the checkpoint is `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`. Six code reads returned blob identities matching the checkpoint; the receipt lists them. Author code was neither executed nor redistributed.

| Convention | Publication observation | Pinned implementation / limit |
|---|---|---|
| Population transfer | [Printed p24 Eq13](plos-original-table-visual-evidence/original-population-context.png), clip `[34,292,579,458]`, displays dM/dt=k1(1+kF F̃CB)(1−B−M)−k2M. It omits the attachment-transfer derivative and R term. Prose sets k2=0 and initial M=1 for the noncooperative case. | [Discretized RHS lines 76–82](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L76) uses dM=J1−J2−(dB+dR), while [thick dynamics](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/myofilaments/ThickFilament_Dynamics.m#L4) has S=1−B−M−R. With two-state switches and B0=0,M0=1,R0=0, M=1−B. The frozen M=1 benchmark remains distinct. |
| Initialization | Tables give no state initialization or equilibrium-residual criterion. | [get_steady_state](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/get_steady_state.m#L3) prepares for 10 s. Discretized B0=0; moment B0=.001, with M0=1 for two-state. The latter initial M+B=1.001 distinction persists; no trajectory or residual was tested here. |
| Width and parameters | Fixed w=3 nm; inferred normalized w=.3; Table 3 values are medians. | The checkpoint's single MAT measurement has w=1/6 and f≈59.6098, not the article median. Those MAT facts were not remeasured in this audit. [complete_parms](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/complete_parms.m#L6) independently confirms the normalized Gaussian form. |
| Force normalization | [Printed p25 Eq22](plos-original-table-visual-evidence/original-series-context.png), clip `[34,94,579,715]`, shows FCE=F̃CB/β; [p26 prose](plos-original-table-visual-evidence/original-beta-context.png), clip `[34,94,579,165]`, assigns β=.5 and states a unit maximum. | The checkpoint fixture's Fscale=2 is algebraically consistent with 1/β for a common normalizer; it does not prove an equilibrated median fixture has unit force. The reread RHS softens runtime active force with log(1+exp(KF))/K. Source normalization ratios still supply no independently established SI sensor/area calibration. |
| Series and length | Printed p25 Eqs14–20 show Ff=FSE=FCE+FPE, Lf=LSE+LCE, γ=2N dps, PE softplus and SE exponential. Table 3 retains F0 and xps units. | [Fitting lines 344–347](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/reproduce_model_fitting.m#L344) give code Γ=.5·(2.6 µm)/(10 nm)=130 for relative-length input. It differs from dimensional γ. [get_PE](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/get_PE.m#L3) retains uppercase Lce0 and sharpness K; lowercase lce0 in the RHS is a distinct transport origin. A whole-fiber step is not a direct-CE step. |

The visual blocker is resolved for this exact original file. The active lane must still select an explicit article or pinned-code convention, parameter provenance, population initialization, activation dynamics, force normalization and series/length map under the existing [execution gates](controlled-release-execution-gates.md). The [dimensional mapping](dimensional-contractile-mapping.md) remains conditional; no human head capacity, area, SI force, tendon law or descending-overlap calibration follows from these pixels.

## Attribution and preservation

© 2026 van der Zee et al.; original article and all six preserved pixel crops are under the article's [Creative Commons Attribution license](http://creativecommons.org/licenses/by/4.0/). The publisher PDF p1 copyright notice and p2 continuation permit reuse with original author/source credit; the license link is embedded on p1. These crops retain original source pixels for checking table association and article/code differences. Rasterization and rectangular clipping are the only modifications. Attribution and source URL accompany them here and in the receipt. They are not covered by an implied relabeling under Kenoma's repository license. The full raw PDF is not committed.
