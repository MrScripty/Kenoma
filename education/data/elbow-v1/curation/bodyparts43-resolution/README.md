# BodyParts3D 4.3 bounded resolution follow-up

The official 4.3 object catalog is now acquired, but **a full-resolution 4.3 mesh/archive URL, byte size and measured polygon density remain unverified**. The earlier 4 MiB metadata cap has been raised to the parent-authorized 8 MiB; the original checkpoint and its receipts remain unchanged.

The catalog returned HTTP 200 with **4,528,437 bytes**, SHA-256 `cab10eda6338a6935d0216810eaba78dd049877df496323a0a4916d290dd8e3a`. Its body was read in chunks of at most 64 KiB under the 8 MiB ceiling and the existing 1.5 GiB free-space floor. All nine follow-up requests together read 4,802,368 bytes. Raw responses remain external in `/workspace/scratch/bodyparts43-resolution-20261006/`; none is included in this branch.

## What is downloadable and what remains unknown

The [official object catalog request](https://lifesciencedb.jp/bp3d/get-info.cgi?version=4.3&tree=isa&cmd=upload-all-list&md_id=1&mv_id=6&mr_id=1&ci_id=1&cb_id=5&bul_id=3&load=1) lists original OBJ filenames and IDs. It contains 13,312 uploaded-object entries, including entries with no representation in the requested version. 3,215 rows have representation IDs. All 3,210 object IDs referenced by the separately acquired 4.3 relation map appear in those rows; five represented catalog IDs are absent from that map. These catalog/mapping counts are not counts of downloaded meshes. The catalog has **no download hrefs, file byte sizes, vertex counts, face counts or reduction rates**. See [`object-catalog-summary.json`](object-catalog-summary.json) for the exact selected arm records and scope.

The official editor JavaScript documents **selected-object/pallet export**: a POST to `download-pallet-art_file.cgi` resolves a selection, then a form POST to `download.cgi` submits the returned representation and object ID arrays, `type=art_file`, the scoped form's `all_downloads=1` flag and a timestamp filename. This identifies a supported selected-object export workflow; it does not establish an unreduced geometry guarantee, a complete 4.3 archive, its size or the output format when export succeeds. The [official information page](https://lifesciencedb.jp/bp3d/info_en/index.html) also describes custom map OBJ export. No all-model selection or complete collection download was attempted.

For right humerus `FMA23130`, representation `BP23164` is associated with:

| Object ID | Original filename in the official table |
|---|---|
| `FJ3368` | `130402_bone_r.humerus.obj` |
| `FJ6462` | `FJ6462_140129_bone_r.humerus.obj` |

The normal pallet-selection API succeeded and returned those two object IDs, plus representation IDs `BP21795` and `BP23164`. The list endpoint's single permitted retry used `BP23164` confirmed by the catalog and the documented `lng=ja` parameter. It still returned **HTTP 500**, 528 bytes, with the same error-body checksum as the original attempt. That listing route was stopped.

The separate documented `download.cgi` workflow returned editor HTML rather than mesh data. An object-only form, a form with its representation ID, and finally the exact UI recipe using the API's complete humerus selection and its numeric timestamp filename all ended at `https://lifesciencedb.jp/bp3d/`, HTTP 200, **84,659 bytes of HTML** each. These are preserved as failed artifact exports, not successful geometry downloads. No further requests to that export route were made, and no 403/security block, mirror, credential change or proxy bypass was used. Request bodies, final URLs, lengths and checksums are in [`request-receipts.json`](request-receipts.json).

The retained **4.0, 99%-reduced `FJ3368`** baseline has **2,233 vertex records and 3,784 triangular face records**, 256,564 bytes, SHA-256 `85f5445a11ecb029b027db0b9b34933982836d442b19ff531d1ca35a3bc3a237`. Exact live 4.3 counts and a density ratio are null because no OBJ was acquired. A shared FJ identifier or original filename is not proof of identical bytes, higher resolution or matching coordinates. See [`representative-arm-comparison.json`](representative-arm-comparison.json).

The [official archive download page](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html) still supplies 4.0 reduced archives, not a verified full 4.3 archive. Verified older alternatives and exact HEAD sizes remain in the [previous options checkpoint](../official-anatomy-scouts/bodyparts3d-options.json). Its 142,903,898-byte reduced ZIP is 4.0. The less-reduced 3.0 option is 547,270,545 bytes and is still 95%-reduced; neither is full-resolution 4.3.

The [live license](https://lifesciencedb.jp/bp3d/info_en/license/index.html) says CC BY-SA 2.1 Japan and points to archive details; the [archive license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) says CC BY 4.0. **Exact 4.3 live asset rights remain unresolved**, and the conflict is retained. No raw catalog, mapping, source geometry or license notice was relabeled or published.

## Separate NLM proposal and validation

[`nlm-elbow-localization-proposal.json`](nlm-elbow-localization-proposal.json) separately records the source-pixel anchor and next bounded proposal: official laterality/orientation evidence, then `a_vm1595` through `a_vm1605`, reusing acquired `a_vm1600`; at most ten new images, 4 MiB each and 40 MiB total. Candidate URLs/sizes, continuity and physical spacing need verification and parent coordination before acquisition. Patient laterality remains unverified. This follow-up made no NLM requests, added no raw images and created no masks.

Run the offline follow-up audit from the repository root:

```sh
python3 education/data/elbow-v1/scripts/audit_bodyparts43_resolution.py
```

The audit checks every new receipt body, the pinned catalog and selected identities, HTML-versus-geometry distinction, actual retained baseline counts, preserved rights conflict and unexecuted NLM scope. `--external-root` supports relocated follow-up bodies. Validation results and rejection checks are in `validation-checkpoint.json`. The original scout audit still passes, and all tracked files present in commit `b4cee16` remain unchanged. This follow-up is limited to new reviewable evidence/tooling; PRs/releases and further acquisitions remain with the parent.
