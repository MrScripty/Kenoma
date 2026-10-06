# Bounded next NLM elbow-localization proposal

Courtesy of the U.S. National Library of Medicine.

This source-pinned proposal does not establish the most current/accurate NLM data or anatomical segmentation. NLM has not endorsed this work.

The next proposed source-image study is **`a_vm1595` through `a_vm1605`**, using the same official male original-color PNG series and reusing the already acquired `a_vm1600`. There are **ten new candidate images**, totaling **34,472,328 listed bytes**, with a **40 MiB transfer ceiling**, **4 MiB per-image cap** and **1.5 GiB free-space floor**. No new raw images were downloaded. Parent coordination and explicit approval of this finite acquisition are required before execution.

[`plan.json`](plan.json) records every exact candidate URL, listed length/date, proposed request order, the reused anchor hash, source-pixel windows, geometry unknowns, execution gates, stop conditions and expected localization deliverables. The [official abdomen index](https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/PNG_format/abdomen/index.html) returned HTTP 200, unchanged final URL, **82,328 bytes**, SHA-256 `67ffbe889c70cd6ede9c1581ba521f398bbe0aa40b6473f0783eac4b668d90bb`. Its receipt is [`metadata-request-receipt.json`](metadata-request-receipt.json). Listed dates are storage/index timestamps, not immutable source revisions or original acquisition dates. Listing presence does not verify a current raw-path response or file hash.

| Candidate | Listed bytes | Proposed action |
|---|---:|---|
| `a_vm1595` | 3,436,372 | New candidate |
| `a_vm1596` | 3,432,348 | New candidate |
| `a_vm1597` | 3,448,091 | New candidate |
| `a_vm1598` | 3,453,036 | New candidate |
| `a_vm1599` | 3,454,785 | New candidate |
| `a_vm1600` | 3,450,446 | Reuse exact acquired bytes |
| `a_vm1601` | 3,455,850 | New candidate |
| `a_vm1602` | 3,453,148 | New candidate |
| `a_vm1603` | 3,449,730 | New candidate |
| `a_vm1604` | 3,442,804 | New candidate |
| `a_vm1605` | 3,446,164 | New candidate |

The paired outward fetch order is **1599, 1601, 1598, 1602, 1597, 1603, 1596, 1604, 1595, 1605**. The complete eleven-image candidate set, including the reused anchor, has 37,922,774 listed bytes; only ten new files count against the proposed transfer. No retries or automatic expansion are proposed. Any access/security denial, unavailable asset, unexpected redirect/type/size, budget failure or source-geometry mismatch stops the affected acquisition pending review.

The proposal follows the inspected pixels. In `a_vm1600`, the approximate **display-right** window is columns `[1550,1895)` and rows `[200,655)`; it contains opposed curved bony profiles and pale interfaces that make it a useful elbow-level candidate. The **display-left** arm window is columns `[150,515)` and rows `[230,665)`. Review both sides. These are zero-based, half-open review seeds, not segmentation contours or certified anatomical ROI bounds. They do not identify patient right side. Existing `a_vm1450` and `a_vm1550` provide wider context but are not adjacent sections or registration anchors.

The finite eleven-level window tests local continuity and joint localization; it does not promise a complete upper-arm/elbow/forearm volume. Filename adjacency is established by the listing, while physical section positions, patient orientation, pixel-center convention and exact local spacing remain unverified. The official series' nominal 0.33 mm XY sampling and 1 mm section interval do not fill those gaps. PNG DPI and photographed plate labels do not supply patient coordinates.

After separately approved acquisition, retain untouched full-field PNGs externally, record actual response receipts/hashes, verify native encoding/CRC, inspect both image-side arms, and record per-image bounds, defects and uncertainty. Official orientation evidence and source-linked anatomical review must establish laterality before a reviewed right-arm ROI claim. Return a source-index localization decision and a separately budgeted next-region proposal. No named tissue masks, cross-specimen fusion, registration, material parameters or clinical/simulation qualification arise from this milestone.

The [4.3 investigation](../bodyparts43-resolution/README.md) remains unchanged: its full archive link/size, actual mesh resolution and exact live asset rights are unresolved. Neither BodyParts3D geometry nor CT header coordinates are applied to these NLM images.

Only the small index HTML was requested in this planning checkpoint; its raw body remains external at `/workspace/scratch/nlm-elbow-localization-plan-20261006/abdomen-index.body`. Original image and data receipts remain unchanged. Run the offline proposal audit from the repository root:

```sh
python3 education/data/elbow-v1/scripts/audit_nlm_elbow_localization_plan.py
```

`--external-root` supports relocating the index body. The audit verifies the listing byte pin, exact proposed source set/budget, existing anchor/contract binding and preserved nonclaims. It performs no requests or acquisitions. Validation results are recorded in `validation-checkpoint.json`.
