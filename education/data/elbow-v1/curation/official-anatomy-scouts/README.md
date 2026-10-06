# Official network and anatomy scout checkpoint

Courtesy of the U.S. National Library of Medicine.

This pinned source-image review does not establish the most current/accurate NLM data or anatomical segmentation. NLM has not endorsed this work.

The fresh environment can acquire the three authorized official male scouts. All returned HTTP 200 at their original URLs. Their sizes total **10,479,462 bytes**, below the 12 MiB image-transfer ceiling. Raw PNGs and upstream document/mapping bodies remain outside the repository in `/workspace/scratch/anatomy-network-20261006/`; they are not included in this branch or published. No additional source image, complete volume, full mesh archive or tissue mask was acquired.

## Runtime and receipt evidence

The expected published configuration is `cecfgver_6ac49b02aa8481948c90ba6be3abaf74`, as supplied by the parent. The runtime has no exposed configuration-version attestation; this checkpoint verifies actual access, not the configuration ID or the complete effective allowlist. No network, credential or proxy setting was changed. Ordinary requests inherited the existing environment and accessed only the four approved anatomy hosts. The inherited proxy transport is distinct from a public proxy or bypass.

[`request-receipts.json`](request-receipts.json) records request method, URL, final URL, HTTP status, timestamps, actual body length and SHA-256, plus response headers with unsolicited cookie values omitted. All four approved hosts yielded HTTP 200 on relevant pages or assets. The NLM thorax directory URL returned HTTP 403 after successful CONNECT, with an 11,543-byte upstream HTML response; that listing was not retried. The independently authorized image paths returned HTTP 200. This differs from the earlier failed proxy CONNECT receipts.

| Scout | Actual bytes | SHA-256 |
|---|---:|---|
| `a_vm1450` | 3,561,524 | `f357fbbcc43c0195e2994d187e63094216e02a4894ad94b2adf0dce9af4ba444` |
| `a_vm1550` | 3,467,492 | `74546104c4c14b3b8a0a018f7c0284928d9d3e036ec2a46018e3e3c8553347ad` |
| `a_vm1600` | 3,450,446 | `570cf80f01c6d9beaefcc4b0670cf8c561e6785321b22f469c4ef4bafda93ac4` |

The existing bounded `scripts/fetch_sources.py` helper acquired these scouts with a 4 MiB per-image cap, 12 MiB total cap and 1.5 GiB free-space floor. This did not run that helper's archive-acquisition entry point or replace accepted source files. The independent official metadata requests read 2,814,206 body bytes in total; their largest accepted body was the 2,404,733-byte public editor JavaScript. Each later metadata request was capped at 4 MiB or less. The over-cap metadata response was closed without reading its body.

## What the source pixels establish

All three source files decode as **2048 columns × 1216 rows, 8-bit RGB, noninterlaced PNG**. PNG chunk CRCs and decompressed scanline lengths pass. Source-byte checksums identify these exact acquisitions; they are initial observations rather than preexisting immutable source revision guarantees.

Both image sides contain arm cross-sections. `a_vm1450` shows thoracic anatomy and broad bone, muscle and peripheral fat-like regions in the lateral arms. `a_vm1550` shows upper abdominal anatomy and similar gross arm boundaries. `a_vm1600` is a useful elbow-level candidate: its display-right arm has multiple opposed curved bony profiles and pale intervening rims/interfaces. These observations follow inspection of the original images and unmodified pixel crops, not filenames alone. See [`pixel-observations.json`](pixel-observations.json) for approximate image-side review windows, artifact observations and limitations.

Anatomical right/left is still unverified. The visible photographic plate labels are not the URL suffixes; no plate-to-slice coordinate rule is inferred. The 0.33 mm XY and 1 mm section interval are [NLM's nominal original-color series specifications](https://www.nlm.nih.gov/research/visible/getting_data.html), not an established asset-specific patient affine. PNG display DPI is not patient sampling. The scouts are separated source sections, not a contiguous three-slice volume.

The [`source-image-review.json`](source-image-review.json) sidecar conforms to the existing NLM segmentation schema and pins its existing contract. It advances only to `source_image_review` with the three external source images. All 45 named tissue/measurement targets remain unassessed; there are no masks, invented registration, reviewed right-arm bounds, cartilage thicknesses, fibre fields or clinical/simulation qualification. Gross visual contrast does not identify named fine connective tissues. Preserve the unknown/ambiguous states already owned by the contract.

The next proposed step is official orientation evidence, then a localization window around `a_vm1600`: `a_vm1595` through `a_vm1605`, reusing the already acquired `a_vm1600`. The proposal caps ten new images at 4 MiB each and 40 MiB total, with the same free-space floor. Candidate locators, actual sizes, continuity, section spacing and availability must be verified before parent authorization. No such acquisition was performed. This window tests elbow localization; it is not a promised complete elbow/forearm ROI. A reviewed ROI manifest and another explicit budget are required before importing a larger contiguous block.

[NLM's overview](https://www.nlm.nih.gov/research/visible/visible_human.html) describes the source images as public domain. Its [linked terms](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html) require attribution, avoidance of implied endorsement and current data or a conspicuous version/accuracy notice. These claims do not supply rights in unrelated segmentations or BodyParts3D.

## BodyParts3D 4.3: verified options and remaining gaps

[`bodyparts3d-options.json`](bodyparts3d-options.json) preserves the precise version records, downloadable mapping, archive headers, license statements and failed export request.

The [official live version endpoint](https://lifesciencedb.jp/bp3d/get-version.cgi?tg_id=1&lng=en) reports `4.3` with object set `4.3`, renderer `4.3.1403311232`, FMA3.0 and a beta/under-inspection comment. It reports `4.3i` with the same named object set `4.3`, renderer `4.3.1601121842` and FMA3.2.1-inference. The [official information page](https://lifesciencedb.jp/bp3d/info_en/index.html) explains that “i” concerns added ontology relations. Its 3,899 represented-concept claim is not a mesh count or a resolution measurement. Matching object-set names do not independently establish byte identity of every mesh.

The official concept-to-object export for 4.3 returned a **92,926-byte metadata ZIP**, not geometry. Its sole `FMA2Obj.txt` member is 605,737 bytes and passes ZIP CRC (`e2ccf5fb`) and SHA-256 verification. Its headers declare data version 4.3, object set 4.3 and FMA3.0. It contains 5,614 relation rows: 3,899 IS-A and 1,715 PART-OF, 4,528 distinct FMA IDs across those trees and 3,210 distinct referenced object IDs. These are counts of mapping records/references, not acquired or inspected meshes.

Both official relations map `FMA23130` (right humerus) to **`FJ3368+FJ6462`**. The live 4.3 and 4.3i records agree. `FJ3368` is referenced by multiple broader FMA concepts, so a first-containing FMA search is not a valid leaf identity rule. Preserve all official many-to-many relations. The `get-contents.cgi` responses contain populated records alongside `success:false`; that application flag is preserved, and the downloadable mapping independently confirms the identities. No third-party mirror was acquired or treated as full-resolution evidence.

The documented selective OBJ list for `BP23164` returned **HTTP 500**, with a 528-byte error body. That export route was stopped without retry, alternate download endpoint or bypass. The complete object metadata table advertised 4,528,437 bytes, above the 4 MiB cap; its body was not read. That HTML length is not a mesh archive size.

The [current official download page](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html) and its latest directory list Release 4.0 reduced OBJ ZIPs. Older official directories also offer 95%-reduced meshes. Ordinary HEAD requests confirm these options:

| Official option | Exact archive bytes from HEAD | Direct download |
|---|---:|---|
| 4.0 IS-A, 99% polygon reduction | 142,903,898 | [isa_BP3D_4.0_obj_99.zip](https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_BP3D_4.0_obj_99.zip) |
| 3.0, 95% polygon reduction | 547,270,545 | [BodyParts3D_3.0_obj_95.zip](https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip) |
| 2.0, 95% polygon reduction | 512,266,980 | [BodyParts3D_2.0_obj_95.zip](https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20100816/BodyParts3D_2.0_obj_95.zip) |

“99% reduction” describes removal of polygons, not retention of 99%. The older 95% options are less reduced, but they are neither 4.3 nor unreduced originals. No archive body was fetched; HEAD empty-body hashes are explicitly not archive checksums. The retained 4.0 surface-quality audit remains separate.

**A full/high-resolution 4.3 archive URL, size and actual vertex/triangle density remain unverified.** No such option appeared in the official download/latest listings inspected here. The live site's version number does not establish geometric resolution or accuracy. The failed selective export and bounded metadata refusal prevent a representative exact-4.3 geometry measurement in this checkpoint. This is a scoped finding, not a proof that no full archive exists anywhere.

The [live license page](https://lifesciencedb.jp/bp3d/info_en/license/index.html) names CC BY-SA 2.1 Japan and refers to the archive for details, while the [archive license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) names CC BY 4.0. **Exact live 4.3 asset rights remain unresolved**; neither claim is erased or automatically applied to the other asset/version. Raw mapping/document bodies stay external alongside the sample images.

## Offline verification and handoff

From the repository root:

```sh
python3 education/data/elbow-v1/scripts/audit_official_anatomy_scouts.py
```

Use `--external-root /path/to/preserved/directory` after moving the external bodies. The audit validates receipt bodies, the initial image byte pins, PNG CRC/scanline integrity, contract/sidecar bindings, official ZIP CRC/mappings and preserved nonclaims. It performs no network requests and writes no images or labels. JSON Schema validation and the historical metadata feasibility audit/tests are recorded in `validation-checkpoint.json`.

This successor is on a separate data branch based on NLM feasibility commit `327940f71c6c143fa91773dd75cbea6a33346304`; inventory `e7a4ffc` and surface-quality `9193962` remain their existing owners. Historical metadata-only files remain unchanged. Mechanics, labs, proofs, PRs and releases are outside this branch's scope. Parent coordination is required before further image acquisition or raw publication.
