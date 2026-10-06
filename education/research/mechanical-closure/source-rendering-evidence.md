# Source rendering evidence for the two-state contractile benchmark

Recorded 2026-10-06. This new file distinguishes successful original-source **PDF text extraction**, mathematical interpretation and unresolved visual/code verification. It does not alter the [earlier review](contractile-state-source-review.md), original law, simulation packets, books or Git history. No new simulation or parameter fit was run.

The original source is [van der Zee et al., PLoS Computational Biology 22:e1014748, September 1, 2026](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748). The successful [publisher printable PDF](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable) returned 37 pages and 1320 extracted lines during this research turn. No local PDF was downloaded, no cache path was identified, and no blocked route was retried for this follow-up. Web screenshot calls returned references without inspectable image blocks; **there was no visual inspection of rendered equation pixels**.

## Access receipts available to the parent/auditor

These internal references are tool-access receipts, not public citation links. They identify the already successful reads and are included to let the team locate the evidence without repeating failed requests.

| Successful reference | Printed pages / extracted lines | Content read |
|---|---|---|
| `turn89view0` | Original 37-page printable PDF, 1320 lines | Whole-document extraction and publication identity |
| `turn95view0` | Printed 21–23; especially lines 557–663 | Equations 1–6, Table 2 and Table 3 |
| `turn95view1` | Printed 22–24; especially lines 645–766 | Table 3 tail, equations 7–13 and overlap restriction |
| `turn95view2` | Printed 23–26; especially lines 706–833 | Equations 12–23, series/parallel interface, β |
| `turn91view2` | Extracted lines 587–658 | A second locator showing the same Table 2/3 extraction |

The screenshots `turn93view0` through `turn93view3` corresponded to zero-based PDF pages 20, 23, 24 and 25 but exposed no readable images to this agent. They must not be cited as visual verification. Shell GitHub requests failed at the network tunnel; neither source code nor an immutable revision was imported.

## Verified extracted entries and remaining interpretation

| Item | Successful original PDF extraction | Status |
|---|---|---|
| Strain coordinate | Printed 22, equation 3, lines 606–609: `x=(d−dps)/dps` | Extracted formula read; confirms normalized, centered coordinate. |
| Gaussian attachment | Printed 22, equation 5, lines 624–630: `f1`, radical `2π`, `w`, and exponential with exponent `−x²/(2w²)`; surrounding prose identifies `f1` as surface area and `w` as standard deviation. | Negative quadratic exponent and stated meaning verified in text. Fraction/radical typography was not visually inspected. The normalized prefactor `f1/(sqrt(2π)w)` follows independently from the stated area and standard deviation. |
| Detachment | Printed 22, equation 6, lines 631–635: sum over `i=1,2` of `gi exp(−x Ei)` | Extracted minus sign read; no screenshot/code parity. With E2 negative, the second exponential grows for positive x; the first with E1 positive grows for negative x. |
| Table 2 | Printed 21, lines 587–604: stroke 10 nm, width 3 nm, E1=2, β=0.5 | Values extracted. Width-to-normalized-strain conversion gives `w=3/10=0.3`; this conversion is our dimensional inference, not an extra source coefficient. |
| Table 3, two-state rates | Printed 22, lines 636–658: f1 row `52.0,67.1,84.5,79.5`; g1 row `4.0,3.4,3.5,6.4`; g2 row `21.1,26.6,23.8,21.2`; E2 row `−0.6,−0.4,−0.6,−0.7` | Values and signs extracted. Their mapping to the four XB columns uses table ordering: two-state XB, two-state cooperative XB, three-state cooperative XB, four-state cooperative XB. Blank table cells were not preserved in the flattened extraction. |
| Table 3, static activation | Same table: nH row `4.4,3.3,3.1`; Ca50 row `0.77,0.78,0.83`, units μM | Values extracted. Mapping to the first three columns uses ordering: Hill without SE, Hill with SE, two-state XB. This mapping is inferred from the table header and the different cooperative activation equation, with no visual cell alignment. |
| pCa sigmoid | Printed 23, equation 11, lines 701–708: `Non=Noverlap/[1+10^(nH(pCa+log10(Ca50)))]` | Extracted signs read. Concentration units inside the logarithm require a consistency check; code parity was not inspected. |
| β convention | Printed 25–26, equation 22, lines 808–811: `FCE=FhatCB/β`; β described as fraction attached during maximal isometry, assigned 0.5 | Extracted denominator and convention read. Exact maximal-force normalization of an independently assembled median fixture remains a mathematical check; it is not guaranteed merely by the prose assertion. |

The provisional **source-derived median fixture** therefore uses f1=52 s−1, g1=4 s−1, g2=21.1 s−1, E1=2, E2=−0.6, normalized w=0.3, β=0.5, nH=3.1 and Ca50=0.83 μM. Numerical entries were read successfully, but column mapping and full formula typography remain less strongly verified than a visually aligned table or pinned implementation. It must not be described as an exactly reproduced individual-fiber fit.

## Independent consistency checks before computation

For a Gaussian with standard deviation w and area f1, elementary integration requires

```text
∫ [f1/(sqrt(2π)w)] exp(−x²/(2w²)) dx = f1.
```

This rejects a missing width normalization regardless of PDF rendering. The attachment rate integrated over normalized strain is s−1; x, w, E1 and E2 are dimensionless. Mixing w=3 nm directly with dimensionless x would fail that unit convention. The dimensional thermal-width expression in the PDF extraction is not reliable enough to audit its fraction/radical arrangement; use the explicitly extracted width value and coordinate definition, and do not claim the thermal formula was visually verified.

For detachment, the inferred implemented function should be checked on both sides of zero:

```text
g(x)=4 exp(−2x)+21.1 exp(+0.6x)  [s−1].
```

Both rates remain positive. Replacing the second term with `exp(−0.6x)` would reverse the sign of the extracted E2 contribution. This is a sign check, not a physiological calibration.

Because pCa is the negative logarithm of calcium concentration expressed in mol/L, consistency with the reported half-activation concentration requires `Ca50=8.3×10−7 mol/L` in the sigmoid. Then `pCa50=−log10(8.3×10−7)≈6.081`, and the static activation equals one half at that pCa. Inserting the bare number `0.83` with the same pCa convention instead shifts half-activation by six decades. This unit conversion is our mathematical inference; it still needs checking against the authors' actual implementation. Calcium unit conventions for the cooperative kon parameter need their own audit and are not imported into the two-state benchmark.

The candidate's source mechanics were evaluated near optimum with overlap fixed to one. Consequently a direct-CE equilibrium/step replay checks state evolution and fast versus relaxed response only. It cannot replay descending force–length or establish human/arm stability. No Blemker reference parameter is used here; any later optimal-stretch reference should distinguish `lambda_ofl` from the passive-linear transition `lambda*` even where a source assigns both the same number.

## Evidence threshold

The available evidence supports an explicitly disclosed **equation-only implementation with provisional table-column interpretation**, followed by population, unit, analytic-equilibrium and translation checks. It does not support claiming verified source-code parity, visually verified equation typography, an immutable implementation pin, reproduction of a published measured trajectory, or a human coefficient set. If exact table-cell verification is a precondition for execution, that remains blocked pending a readable ordinary publisher rendering or legitimately available pinned source; no access bypass is authorized or attempted.
