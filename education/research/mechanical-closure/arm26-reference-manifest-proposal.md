# Versioned Arm26 educational reference manifest proposal

**Choose the official OpenSim Models Arm26 asset at commit `84b487c4e3245359a64381e01f01b9cf4772d457` as one coherent educational source family.** It already supplies all six requested actuators and is retained in Kenoma. The proposal preserves that asset's scalar inputs, body-local paths, wraps and joint definitions without combining them with Murray population means or atlas centerlines.

Proposal `kenoma.educational.arm26-reference.v1.proposal`, schema `1.0.0`, dated 2026-10-06. Research branch `research/arm26-reference-manifest`, base `1a63fb6be3d9d8131769856cbf9796c873ffa2ce`. Nothing here adopts parameters, loads a runtime model, activates a solver, evaluates paths/moment arms, or claims anatomical accuracy. The previous review remains unchanged.

## Source identity and license

The [official immutable XML](https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim) is **90,192 bytes**, SHA-256 **`e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9`**. A bounded ordinary HTTP read of the [commit-addressed raw asset](https://raw.githubusercontent.com/opensim-org/opensim-models/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim) returned 200 and matched the retained XML byte-for-byte. No model meshes were downloaded. GitHub API requests for tree/blob metadata returned proxy 403; no bypass was attempted. The repository tree is therefore null/unverified in this proposal. A computed Git blob hash is labeled computed, not independently returned by the upstream API.

Arm26 is credited to the **OpenSim Development Team (J. Reinbolt, A. Seth, A. Habib, S. Hamner), adapted from Kate Holzbaur's 2004-11-22 model**. Its embedded publication is Holzbaur, Murray and Delp (2005). Its embedded license is **CC BY 3.0**, preserved independently from OpenSim software licensing. Attribution, the source/license links, and the extraction/change description accompany this derivative metadata; the complete original notice remains in the unchanged XML. The [license deed](https://creativecommons.org/licenses/by/3.0/) permits sharing/adaptation with attribution and prohibits imposing additional restrictions. This proposal does not imply author endorsement.

The [machine-readable reference manifest](../../data/anatomical-arm-v1/review/arm26-reference-manifest/reference-manifest.json) contains the source bytes/hash, locators, separate evidence classes and uncertainty fields. [Source provenance](../../data/anatomical-arm-v1/review/arm26-reference-manifest/source-provenance.json) records successful and unsuccessful access and the absence of mesh acquisition.

## OpenSim context and limits of compatibility

The separate benchmark's published provenance at Kenoma commit **`0e89c60d03d3d6137e1ece686ecf942b83d05645`** pins OpenSim **4.5.2**, tag object `7fcf7c1009ca636a3e0a2d14745109d684072e2a`, peeled commit **`5bc7d3308eda742690f485ec060bfe725a349fa6`**, tree `19ea9bb15e9c43a3f7506966ea6ac0ca14002df1`. Only that worker's source manifest/protocol was inspected; its implementation and numerical cases were not reproduced. An unchanged [metadata snapshot](../../data/anatomical-arm-v1/review/arm26-reference-manifest/core-context-source-manifest.json) makes the provenance check local and self-contained; no implementation snapshot is added.

Arm26 declares OpenSim XML version **40000** and uses **Thelen2003Muscle**. The pinned core [header](https://raw.githubusercontent.com/opensim-org/opensim-core/5bc7d3308eda742690f485ec060bfe725a349fa6/OpenSim/Actuators/Thelen2003Muscle.h) declares that concrete class; its [registration source, line 57](https://raw.githubusercontent.com/opensim-org/opensim-core/5bc7d3308eda742690f485ec060bfe725a349fa6/OpenSim/Actuators/RegisterTypes_osimActuators.cpp) registers it. This establishes a traceable source-level type relationship, not successful runtime deserialization or dynamics. OpenSim core is **Apache-2.0**; it does not relicense Arm26's CC BY data.

No actuator is replaced with `Millard2012EquilibriumMuscle`. Reusing lengths/path geometry in that class would require a separate reviewed adapter, pennation/state initialization and constitutive choices. The benchmark's dimensional teaching scales are not substituted for this asset's values.

## Exact head mapping and model inputs

All numbers below are **model inputs**, with no uncertainty reported in the XML. Decimal precision is not a biological confidence interval. Name/entity correspondence is an ontology mapping, not a spatial registration. No atlas measurement is inferred.

| Source actuator | Distinct right-arm head | Atlas name correspondence | Optimal fiber length, m | Model tendon slack, m | Pennation at optimum, rad |
|---|---|---|---:|---:|---:|
| BIClong | Biceps long | FJ1478 | 0.1157 | 0.2723 | 0 |
| BICshort | Biceps short | FJ1512 | 0.1321 | 0.1923 | 0 |
| BRA | Brachialis | FJ1486 | 0.0858 | 0.0535 | 0 |
| TRIlong | Triceps long | FJ1479 | 0.1340 | 0.1430 | 0.20943951 |
| TRIlat | Triceps lateral | FJ1477 | 0.1138 | 0.0980 | 0.15707963 |
| TRImed | Triceps medial | FJ1480 | 0.1138 | 0.0908 | 0.15707963 |

The asset's published lineage uses **2.7 µm** normalization; the XML does not contain a sarcomere-length field. The manifest therefore binds that convention to the publication separately from each XML scalar. **2.8 µm** remains a separate Murray 2000 comparison convention. No renormalization is applied. The earlier [primary review](arm-reference-operating-lengths-primary-review.md) explains the specimen/normalization/slack distinctions; the printed Holzbaur table's rounding is not substituted for the pinned asset's precision.

## Fields kept separate

Every numeric record has a unit, evidence status, source locator and uncertainty object. Unknown is `null`, never an invented measurement or zero. Statuses distinguish measured, derived, model-assumed, derived-but-unevaluated and unknown; the numeric model fields in this proposal are model-assumed. No new measured biological value is asserted.

| Record | Proposed contents | Status / unresolved evidence |
|---|---|---|
| Atlas datum | Existing atlas hash/frame and authored bind angle **0.2841100888248933 rad** (~16.2783°) | Derived/authored geometry; biological unloading state and model registration unknown |
| Source pose | XML shoulder/elbow coordinate defaults both **0 rad** | Model default, not passive stress-free or active optimum |
| Educational comparison pose | Proposed source-coordinate shoulder elevation **0 rad**, elbow flexion **π/2 rad** | Explicit model assumption; no internal state, equilibration or path evaluation |
| Passive natural reference | Natural fascicle length, passive metric and reference prestress separately | Unknown for each head; a computational pose does not supply them |
| Fascicle reference | Contractile arc, sarcomere reference, reference pennation and optimal/reference stretch | Unknown. XML optimum and atlas guide are not measured reference fascicles |
| Active optimum | Exact source optimal length and scalar optimum pennation; lineage convention separately cited | Model-assumed; optimum does not fix passive recruitment |
| Tendon reference | Model slack distinct from geometric reference length, pose-dependent model length, reference strain and unloaded tensile area | Slack extracted; other fields unknown. Lumped slack is not drawn free tendon/aponeurosis length |
| Attachments/path | **32** ordered model points in named body frames; four wrap objects/seven path-wrap references; joint offsets/transforms | Model-assumed. First/last points are model origin/insertion; intermediate points are model routing, not measured fascia or atlas landmarks |
| Musculotendon path length | Pose-indexed `LMT`, unit **m**, bound to each source GeometryPath | Derived but unevaluated; separate from measured/reference fascicle and tendon lengths |
| Moment arms | Per head and coordinate, units **m** for derivative with respect to **rad**; definition `rj=−∂LMT/∂qj` | Derived but unevaluated. No population-average arm or unwrapped straight chord substituted |

Each path point retains its frame `/bodyset/base`, `/bodyset/r_humerus` or `/bodyset/r_ulna_radius_hand`. Wrap locations/radii/dimensions and body rotations remain source-local. Joint frame names repeat across joints, so the manifest preserves their joint-scoped locators rather than treating them as globally unique names. Mixed linear-function coefficients retain separate dimensionless gains and radian offsets; zero rotational constants remain radians. The declared ranges remain model ranges, not population observations or acceptance gates.

The selected asset has shoulder elevation and elbow flexion only. **Forearm rotation is not an independent coordinate**: ulna/radius/hand are one body. Do not label this welded arrangement measured neutral pronation/supination or import the full published upper-extremity pose definition without inspection. Other shoulder rotations are fixed by the source transforms; no independent scapular motion is supplied.

## Omitted structures and remaining gaps

Arm26 omits brachioradialis (atlas FJ1487), anconeus, pronators/supinator and other upper-limb muscles. It supplies no separate internal aponeurosis, external lacertus, fascia, free-tendon area or distributed contractile/series partition. Display-mesh references in the XML are retained provenance only; meshes, contact surfaces and anatomical coverage were not acquired or validated.

The concrete choice is this **six-actuator Arm26 asset**, not a hybrid expanded arm. Adding a seventh actuator or full forearm/shoulder motion would require a separately versioned source-family decision. The current seven-muscle atlas remains untouched.

For review, the smallest next step is to approve or revise this metadata source choice and its stated omissions. Physical integration remains blocked by matched atlas/reference fascicle/sarcomere observations, passive natural metrics/prestress, series dimensions/areas/prestrain, and model-to-atlas pose/frame registration. Numerical integration would separately need a reviewed runtime/path evaluation and any actuator adapter. No choice is justified by making a retained negative witness disappear.

## Validation performed

The [offline validator](../../data/anatomical-arm-v1/review/arm26-reference-manifest/validate_manifest.py) checks pinned source/atlas hashes, six unique head mappings, every extracted XML quantity, body/wrap references, typed units including mixed coefficients, explicit nulls, independent 2.7/2.8 µm conventions, and exact model/default coordinate provenance. It performs no geometric evaluation or dynamics. The [validation receipt](../../data/anatomical-arm-v1/review/arm26-reference-manifest/validation.json) records the checks and preserved baseline; [artifact hashes](../../data/anatomical-arm-v1/review/arm26-reference-manifest/artifact-manifest.json) bind the deliverables.

Reproduce from this worktree with `python education/data/anatomical-arm-v1/review/arm26-reference-manifest/validate_manifest.py`. This reads local evidence only; no dependency installation, network request or solver is involved.
