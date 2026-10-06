# Arm source inventory checkpoint

This lane inventories the sources needed to extend Kenoma's existing right-arm proof of concept. It adds no mechanics, geometry, book corrections or Lean claims. The inventory is incomplete by design where source evidence is missing; it is not a complete upper-limb dataset, a mathematical simulation, or clinical validation.

`source-inventory.json` records exact versions, license scope, specimen and coordinate provenance, existing owners, 29 input byte pins and 49 requirements. The separate pinned `requirements-v1.json` contract prevents relabeling tissue identity or silently deleting completion gaps. `coverage.json` is reproducible from those inputs. Each requirement retains its own mesh, concept, acquisition and attachment status. Read its `gap` field before using a member candidate.

## Verified coverage

| Requirement | FMA leaf | ELEMENT file | Evidence |
|---|---|---|---|
| Right humerus | FMA23130 | FJ3368 | Retained original OBJ, acquisition-time SHA-256 and inspected header |
| Right radius | FMA23464 | FJ3349 | Same |
| Right ulna | FMA23467 | FJ3391 | Same |
| Right brachialis | FMA37668 | FJ1486 | Same |
| Right biceps short head | FMA37684 | FJ1512 | Same |
| Right biceps long head | FMA37686 | FJ1478 | Same |
| Right triceps medial head | FMA37695 | FJ1480 | Same |
| Right triceps lateral head | FMA37697 | FJ1477 | Same |
| Right triceps long head | FMA37699 | FJ1479 | Same |
| Right brachioradialis | FMA38486 | FJ1487 | Same |
| Right clavicle | FMA13322 | FJ3362 | One mapped archive member; OBJ not acquired or inspected |
| Right scapula | FMA13395 | FJ3384 | Same; existing shoulder acquisition receipt reports failure |
| Right anconeus | FMA37705 | FJ1485 | One mapped archive member; OBJ not acquired or inspected |
| Right coracobrachialis | FMA37665 | FJ1488 | Same |
| Right forearm interosseous membrane | FMA23707 | FJ1476 | Same; not a substitute for elbow ligament segmentations |

The ten retained source meshes contain 13,852 vertices and 20,218 triangles. Their topology and coordinates are unchanged in this lane. They are constructed atlas surfaces; part-specific observed tissue provenance is unavailable. The retained [source package](../README.txt) and [attribution notice](../LICENSES_AND_ATTRIBUTION.txt) remain their owners.

The audit reconstructs all 2,234 ZIP directory entries from the pinned binary directory and compares them with its existing JSON representation. The inspected IS-A mapping has 29,549 relationship rows and 2,905 represented concepts. Those are three different counts. A compound concept reuses ELEMENT files; its rows are not new tissue meshes. `all_mapped_concepts` preserves every containing concept for each candidate, while an inspected OBJ header supplies its leaf concept. For example, FJ1486 belongs to the muscle group FMA37348 and to brachialis FMA37668; taking the first containing group would lose the leaf identity. Preserve `M` suffixes and bilateral identity; neither a name nor a suffix establishes how a part was observed.

## Tissue and attachment gaps

The 49 requirements divide into 10 confirmed individual surfaces, 5 uninspected single-member representations, 1 compound example, 3 related generic concepts, 1 whole-body skin representation needing regional segmentation, and 29 unmatched named requirements. Generic tendon, ligament and cartilage concepts provide members elsewhere in the body. They do not establish the required arm tissues. FJ2810 is a whole-body skin candidate; it supplies neither an inspected arm skin shell nor a fat layer.

Unresolved requirements include six proximal/distal tendon units; bicipital and internal aponeuroses; the ulnar collateral bundles, radial collateral, lateral ulnar collateral, annular and quadrate ligaments; elbow capsule; distal-humeral, radial-head and ulnar articular cartilage; subcutaneous/intermuscular fat and elbow fat pads; brachial/antebrachial fascia; measured entheses; and muscle fibre fields. Search names in the manifest are authored requirement labels, not newly verified FMA identifiers. “No matching mesh in inspected mapping” means exactly that: no absence claim about the full FMA ontology, PART-OF tree, other releases or the underlying images.

The existing attachment owner is [`attachments-apparatus.json`](../../anatomical-arm-v1/config/attachments-apparatus.json). The generated coverage records its seven muscle heads, eight named bone patches and three fixed origin estimates. Source-face indices and source binding are checked. The patches remain authored connected face selections awaiting anatomical review. The fixed biceps and long-triceps origins are atlas-tip estimates, with the owner's 15 mm authored uncertainty radius; they are not scapular landmark measurements. Tendon/aponeurosis region cuts, routing and shared apparatus geometry remain authored data belonging to the existing mechanics lane. Bone patches do not constitute measured enthesis footprints.

## Source and license scope

| Source | Exact status in this checkpoint |
|---|---|
| BodyParts3D Release 4.0, IS-A 99% polygon-reduced archive | Accepted source. Release note dated 2013-05-16; archive update 2013-06-19. Current official archive grant is CC BY 4.0. Original OBJ BY-SA 2.1 Japan comments are preserved. |
| BodyParts3D 4.3 / 4.3i | Candidate. Exact assets and attribution-only license scope unresolved. Live and archive notices differ. No candidate meshes acquired. |
| NLM Visible Human male (1994) and female (1995) | Separate public-domain image sources. No image volume acquired or image revision selected; tissue segmentation and arm registration remain required. |
| Denver lower-body lead | User-supplied assessment, not independently version/license-audited here. Lower-body coverage and combined fat/fascia or fat/skin labels do not establish a tissue-distinct arm. |
| Arm26 / OpenArm | Existing independent model parameters / recorded signals. Neither supplies missing tissue geometry or registration to the atlas. |

The [official Release 4.0 download](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html), [current license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) and [archive README](https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html) define the accepted archive scope. The license attribution is retained in the inventory and existing attribution notice. The archive's total size is 142,903,898 bytes. No full archive SHA-256 is asserted: only directory ranges and selected members were acquired. `LATEST` and dated locators are not immutable content identifiers; the retained byte pins control identity.

BodyParts3D derives from a male-volunteer TARO MRI framework supplemented by anatomical reconstruction; it is separate from the NLM cadavers. See the original [construction paper](https://doi.org/10.1093/nar/gkn613) and [project's modelling discussion](https://lifesciencedb.jp/bp3d/info_en/index.html). Source positions are millimetres; the existing SI conversion multiplies by 0.001, preserving source origin and axes: x left, y posterior, z superior. The coordinate diagram is retained and pinned. Exact volunteer acquisition pose and calibrated joint angles are not established; the static atlas pose is not a measured motion trajectory.

The [live version description](https://lifesciencedb.jp/bp3d/info_en/index.html) distinguishes OBJ decimal updates, coordinate changes at integer versions, and concept-relation updates. The 4.3i figure of 3,899 is a concept count. Its [live license notice](https://lifesciencedb.jp/bp3d/info_en/license/index.html) states BY-SA 2.1 Japan while linking to the archive's current BY 4.0 notice. This discrepancy does not settle the terms for exact 4.3 assets. The delegated audit's third-party mirror is a lead, not an adopted official source or evidence of full-resolution quality.

The [NLM source page](https://www.nlm.nih.gov/research/visible/visible_human.html) describes public-domain cryosection, CT and MRI images from separate male and female cadavers. Image access is not a license grant for unrelated third-party segmentations. Never mix these people, TARO, OpenArm participants or Arm26 model evidence into one observed anatomy.

## Reproduce without network

From the repository root, using Python 3.10 or later and the standard library:

```sh
python3 education/data/elbow-v1/scripts/audit_source_inventory.py
python3 -m unittest discover -s education/tests -p test_arm_source_inventory.py -v
```

Default audit mode is read-only and fails for changed pins, mismatched mapping/directory/OBJ identity, altered SI conversion, fabricated missing geometry, bad attachment references or stale coverage. It makes no network requests. `source_inventory_canonical_sha256` hashes sorted compact JSON, rather than the formatting of the inventory file. After reviewing intentional manifest changes, regenerate only the curation coverage:

```sh
python3 education/data/elbow-v1/scripts/audit_source_inventory.py --write
```

Existing input pins were recorded from the exact base commit named in the inventory; original acquisition-time member and metadata receipts remain independent evidence. The new requirements contract has its own explicitly authored pin origin. Replacing an input requires a reviewed provenance change and new pins; `--write` never repins input bytes.

## Explicit acquisition

The new metadata reacquisition command delegates network work to the existing `scripts/fetch_sources.py` helper. It requests only seven pinned small inputs or explicit ZIP ranges, preserves the helper's 30 MiB total ceiling and 1.5 GiB free-space floor, sanitizes receipt headers, and verifies exact lengths and SHA-256 before writing candidates. It refuses existing destinations and any output under this repository. It does not fetch an entire archive, adopt new meshes, overwrite accepted sources or run during builds.

```sh
python3 education/data/elbow-v1/scripts/reacquire_inventory_inputs.py \
  --output /tmp/kenoma-arm-source-incoming \
  --items mapping directory end-record license readme coordinate-system release-note
```

[`reacquisition-checkpoint.json`](reacquisition-checkpoint.json) preserves the executed current attempt: all seven requests failed at the proxy with 403 tunnel responses, zero payload bytes transferred, and exit status 1. This is an access blocker, not an upstream missing-data result. Existing source bytes were not replaced. Web inspection of current source notices is distinct from raw-byte acquisition. The official parts index was web-readable but its raw acquisition was also unavailable; it is not a pinned input here.

Reuse the existing shoulder and subset acquisition owners for later mesh work. Before adopting additional members, bind directory identity, exact member hashes, release/coordinate/leaf identifiers, current license evidence and retained historical notices. An unacquired member has `sha256: null`; its directory CRC is not a substitute for an independently accepted content pin. A later complete upper-limb inventory must add all shoulder, forearm, hand and wrist structures and tissue-distinct segmentation evidence.
