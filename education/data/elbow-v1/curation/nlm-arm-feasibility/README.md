# NLM male arm segmentation feasibility

Courtesy of the U.S. National Library of Medicine.

This feasibility checkpoint does not establish the most current/accurate NLM data or anatomical segmentation. NLM has not endorsed this work.

The practical next step is a small, same-specimen image localization study. Official metadata establishes available image series and three bounded scout candidates. Source-raster access is blocked here, so the checkpoint has **no imported image, localized arm ROI, tissue mask, observed boundary or registration transform**. It preserves inventory checkpoint `e7a4ffc` unchanged and uses its requirement identifiers. No mechanics, book or proof files are modified.

## What is established

The selected specimen is `nlm-visible-human-male`, the original NLM male cadaver image dataset. It is separate from TARO, the female dataset and every model/recording source in the [existing inventory](../README.md). Exact source-image revisions will be identified by acquired bytes, not by a directory timestamp.

| Male series | Documented nominal sampling | Current evidence |
|---|---|---|
| Original axial color cryosections | 2048 × 1216 RGB; 0.33 mm XY, 1 mm sections | Official metadata; no raster inspected |
| Digitized 70 mm color film | 4096 × 2700 RGB; 0.17 mm XY, same 1 mm sections | Official metadata; no sample acquired |
| CT | 512 × 512; 1 mm sections | Normal/frozen series listed; two frozen-CT headers inspected via delegated web reading |
| MRI | 256 × 256; 4 mm intervals; head/neck axial, remainder longitudinal | Official metadata; arm-specific protocol/coverage unverified |

These specifications and lossless PNG availability are described by [NLM's acquisition page](https://www.nlm.nih.gov/research/visible/getting_data.html) and [overview](https://www.nlm.nih.gov/research/visible/visible_human.html). Nominal sampling does not establish a file-specific affine, registration or tissue visibility.

The [1356](https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/radiological/frozenCTHeaders/c_vm1356.fro.txt) and [1357 frozen-CT headers](https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/radiological/frozenCTHeaders/c_vm1357.fro.txt) report exam 32, series 4; supine/head-first axial imaging; 0.9375 mm XY and 1 mm scan spacing. Their RAS centers are `(0,0,-370)` and `(0,0,-371)` mm. Filename suffixes differ from scanner image numbers 357/358. The first header's corner span is 480 mm, which is 512 nominal samples; its pixel-center convention is unresolved. No affine is invented from this ambiguity. The local numbering relationship is not a universal rule or a cryosection coordinate system.

`feasibility.json` retains the header-field transcription as a delegated web observation, with `raw_sha256: null`. It is not a byte-verified header or a CT-image import. No arm-specific visual observation was made. Same specimen and section spacing do not prove alignment between pre-freeze CT, frozen CT, MRI and cryosections. Source preparation, displacement, registration error, arm pose and cutting artifacts require further evidence.

## A bounded acquisition and localization recipe

The [thorax](https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/PNG_format/thorax/index.html) and [abdomen listings](https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/PNG_format/abdomen/index.html) give these exact candidate assets:

| Scout | Official relative path within `Male-Images/` | Listed bytes |
|---|---|---:|
| a_vm1450 | `PNG_format/thorax/a_vm1450.png` | 3,561,524 |
| a_vm1550 | `PNG_format/abdomen/a_vm1550.png` | 3,467,492 |
| a_vm1600 | `PNG_format/abdomen/a_vm1600.png` | 3,450,446 |

These are anatomical-level candidates to inspect, not verified upper-arm/elbow/forearm slices. Listing dates do not identify original scan dates or immutable revisions. The scout plan totals 10,479,462 bytes with a 12 MiB transfer ceiling, 4 MiB per image and the existing 1.5 GiB free-space floor. It is not an executed download or an instruction to retry the blocked routes automatically.

When official access is available:

1. Use the existing `elbow-v1/scripts/fetch_sources.py` bounded helper in an explicit acquisition step, writing a new external directory. Obtain only the three scouts and relevant official geometry documents. Preserve source bytes, URLs, response receipts, lengths and SHA-256. Initial discovery hashes are observations; review them before accepting new pins. Never replace accepted inputs silently.
2. Verify actual PNG dimensions, color/bit encoding and source identity. Establish image orientation and right-side anatomy from source documentation and source pixels. Retain index-space geometry until origin and pixel-center convention are established. Do not apply BodyParts3D coordinates or the CT header to the cryosections.
3. Localize the humerus, elbow joint and proximal forearm in the male source. Record exact source slices and pixel bounding boxes. If these scouts do not bracket the desired anatomy, record that result and plan a different small same-specimen scout set; do not call the current set an elbow ROI.
4. Separately budget a small contiguous elbow block only after localization. Record explicit slice identities, actual section spacing, field of view, cutting defects and missing sections. Derive a complete ROI manifest before any region import. A three-scout set is not a 3D segmentation volume.
5. Begin image annotation with gross bone, muscle, skin and fat where source boundaries are visible. Then assess each named fine connective/cartilage structure individually. Leave unsupported interfaces unknown; fill no gap with an atlas prior or a different person.

Source-raster access and localization are the blockers that prevent a demonstrated minimal image/label import in this checkpoint. An importer is not presented as tested against authentic images when none were obtained.

## Labels and uncertainty

`segmentation-contract.json` binds **40 voxel classes and 5 nonvoxel targets** to all 45 non-example requirements in the existing inventory. Generic ontology examples are excluded. Separate fat, fascia, skin, tendon, ligament, cartilage, bone and muscle classes preserve the requested tissue distinctions. Attachment footprints/landmarks and fibre vector fields remain separate measurement targets; a categorical voxel label cannot supply either measurement.

Reserved uint16 values are `0` unknown/unassessed, `1` reviewed background, `65534` artifact/exclusion and `65535` ambiguous tissue. Every tissue has a different code. Unknown must never mean empty background. `annotation-state.json` currently has no raster artifacts and all 45 targets are `not_assessed`.

`segmentation-schema.json` is a prospective JSON Schema for sidecars, not an anatomical acceptance test. It distinguishes source assets, geometry, laterality, region, annotators, reviewers, boundary evidence, uncertainty and interpolation. Its later image stages remain undemonstrated. The standard-library audit specifically validates this metadata-only checkpoint and rejects claims of image import or observed annotations.

The following assessments are **resolution-based planning inferences**, not findings from inspected pixels:

| Required boundaries | Feasibility gate |
|---|---|
| Gross bone/muscle/skin and visible fat compartments | Plausible initial candidates if actual contrast, side and continuity support them. Separate subcutaneous/intermuscular fat and fat pads need individual review. |
| Tendons, ligament bundles, aponeuroses, fascia and capsule | Require visible interfaces and traceable anatomical course across sections. Bright connective tissue alone cannot establish a named structure. Record partial-volume, ambiguous or unresolved regions. |
| Elbow articular cartilage | Assess joint-level source slices for a distinct layer against bone and joint space. Better XY film sampling does not improve 1 mm section spacing. No thickness or separability is asserted here. |
| Enthesis architecture and muscle fibre fields | Remain measurement gaps; nominal image sampling is insufficient evidence for their quantitative reconstruction. |

Quality gates are authored curation criteria: verify byte identity/series and right side; preserve native sampling; mark missing sections and reconstruction; collect source-linked anatomical review; retain disagreement and uncertainty maps; report registration residuals before combining modalities. Later mask checks should assess exclusivity, coordinate bounds and continuity, with sensitivity to plausible boundary changes. Voxel size or half a voxel is not a certified boundary-error estimate. None of these gates establishes clinical or simulation readiness.

## Access, reuse and reproduction

[`access-checkpoint.json`](access-checkpoint.json) records the root worker's three bounded direct metadata requests that failed at the proxy with 403 tunnel errors before payload. Delegated metadata probes also reported proxy failure; their request logs are not reconstructed here. The receipt does not fabricate upstream HTTP statuses or original timestamps/headers. Browser listings were readable, but image opens provided locators without inspectable raster pixels or hashes. No archive 403 route was retried or bypassed, and no specimen was substituted.

NLM describes the VHP images as public domain. Its [access page](https://www.nlm.nih.gov/research/visible/getting_data.html) links the replacement [Terms and Conditions](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html): use the conspicuous attribution above, avoid implied endorsement, and maintain current redistributed data or provide a conspicuous version/accuracy notice. NLM disclaims warranties and the linked terms include a hold-harmless provision. These statements do not determine rights in unrelated third-party segmentations. NLM acknowledges the body donors; no additional VHP-specific ethical-reuse condition was found on the inspected pages, and no independent consent assessment is claimed.

From the repository root, Python 3.10+ standard library:

```sh
python3 education/data/elbow-v1/scripts/audit_nlm_arm_feasibility.py
python3 -m unittest discover -s education/tests -p test_nlm_arm_feasibility.py -v
```

The audit checks the unchanged source inventory, complete target identities, separate label codes, missing-data states, specimen, bounded candidate plan and absence of unsupported observations. It performs no network requests and writes no images or labels. Optional external JSON Schema tools may validate sidecar structure; source evidence and the curation quality gates remain necessary.
