# Kenoma: arm proof of concept to an open whole-body system

The owner's objective is a complete open 3D anatomical dataset and mathematical simulation spanning **skeleton, ligaments, tendons, muscles, fat and cartilage**. The arm capstone is the proof of concept for trustworthy mechanics and data provenance. “The world's best open musculoskeletal dataset” is an aspiration, not a present performance claim. Completeness means individually identified tissues, explicit attachment/contact topology, reproducible reference states and uncertainty, rather than a rendered outer shape alone. This roadmap records the goal without replacing the immediate mechanics work with asset collection.

## Stages and exit gates

| Stage | Concrete deliverable | Exit gate before promotion |
|---|---|---|
| 0. Controlled mechanics closure (current) | Full-nodal finite-K comparator; explicit active/reference conventions; preserved successful and failed specimens | Independent force/pressure/work replay, positive geometry, stationary curvature assessment and matched refinement. The homogeneous comparator passes equilibrium but the original descending active branch retains negative curvature: [current result](mechanical-closure/full-p2-p1-results.md). Resolve reference/active-family assumptions next. |
| 1. Credible arm tissue envelope | Individually identified arm bones and muscle heads, tendons, ligaments, cartilage and fat where sources support them; explicit unresolved tissues; attachment and contact graph | Source-backed reference/fascicle mapping and material inputs; complete body/sheet/attachment force balance; whole-envelope geometry and contact checks. No skin until this envelope is credible. Missing cartilage/ligament/fat data must be listed, not fabricated. |
| 2. Loaded arm proof of concept | Self-consistent lift/release from one registered initial state, with tissue/bone interactions and load/support reactions | Unchanged residual and geometry gates at every accepted state; rejected candidates advance no state or time; matched-time spatial, quadrature and timestep refinement; work/energy/gravity/inertia accounting; validation against independently sourced arm measurements with uncertainty. Fit and validation sets remain distinct. |
| 3. Reproducible open arm release | Versioned anatomy, tissue identities, mesh transforms, mechanics configuration, validation fixtures and source/license manifests | Rebuildable from authorized source snapshots and documented transformations; original notices and derivative obligations retained; interoperable units/axes/IDs; independently reviewable evidence. Parent coordinates publication/Library and reviews. |
| 4. Region-by-region whole-body coverage | Reuse the arm schema and gates for shoulder/trunk, contralateral arm, pelvis/hip, knee/ankle/foot, spine/head and other supported regions | Each region reaches its declared anatomy and mechanics gates before integration. Publish a coverage matrix by named tissue, laterality, source and quality; a region cannot pass through an unlabeled proxy. Do not assume any one source provides all tissues or one consistent subject. |
| 5. Integrated whole-body simulation | Coupled skeletal coordinates and deformable tissues with compatible attachments, contact, loads, constitutive/rate assumptions and numerical controls | Cross-region reference registration and interface balance; no tissue mass double counting; global force/moment/work consistency; solver and mesh/time refinement; independently sourced multi-joint validation. Regional adequacy alone does not establish global qualification. |
| 6. Maintained benchmark dataset | Transparent open releases with comparative tasks, issue tracking and evolving uncertainty/coverage evidence | Publish reproducibility, completeness, geometry fidelity, mechanics accuracy and licensing compatibility benchmarks. Any superiority claim requires actual comparable evidence and a defined benchmark, not the aspiration itself. |

Stage 0 and the arm's failed gates retain priority. Whole-body expansion may prepare schemas and source reviews; it must not erase or relabel unqualified arm trajectories.

## Required record for each tissue and connection

Every anatomical entity needs a stable ID, anatomical name/synonyms, laterality, hierarchy, tissue class, geometry identity and source concept/segmentation labels. Skeleton and individual muscle heads remain distinct. Tendons, ligaments and cartilage surfaces/volumes are separately typed; fat compartments remain individually mapped where supported. A missing structure is an explicit coverage gap. Mixed sources retain their subject/model distinctions.

Each geometry records source dataset/version, specimen or authored-model identity, reference pose and joint coordinates, axis handedness, length/area/volume units, scale, registration transforms, original and transformed file hashes, surface/volume topology, simplification/remeshing history and quality evidence. A centerline is not a measured fascicle map; an atlas pose is not a validated stress-free tissue reference. Units and transforms must be machine-checkable before regional integration.

Connections form an explicit graph: named origin/insertion entities, attachment patches and mapped coordinates, wrapping paths, tendon–muscle/aponeurosis continuity, ligament attachments, cartilage pairs and interfaces, fat/tissue envelope neighbors, contact/exclusion relationships and interface boundary conditions. Each graph edge carries provenance and uncertainty. Avoid implicit endpoint snapping or undocumented welds that change force paths. Boundaries, sheets and interfaces contribute to force/work accounting.

Each material/activation/rate input records the equation/code variable, units, stress and reference/current area convention, fiber/architecture reference, measured versus inverse-fitted versus reference-model versus authored status, species/tissue/specimen population, temperature/preparation, loading/rate/activation protocol, uncertainty and source location. Keep geometry provenance distinct from material provenance. In particular, **1.4 dimensionless optimal/reference stretch** and **1.4 MPa model specific tension** remain separate quantities. The existing [measured-property map](measured-fibre-property-map.md) supplies the detailed input ledger requirements; present fitted coefficients are not universal human tissue constants.

## Validation and uncertainty

Keep separate tests for source identity/units, geometry/topology, reference registration, constitutive behavior, attachments/contact, force/work balance, numerical convergence and empirical prediction. Controlled patch results qualify implementation only. At the arm stage retain complete terminal/failed-state fields and code/input hashes, not just a release-angle graph or generalized reaction target. At later stages use the same acceptance contract per region and at coupled interfaces.

Report the supported population/subject/model for each empirical comparator, measurement uncertainty and registration error. Distinguish parameter-identification data from held-out validation and compare predicted reaction, kinematics, tissue deformation and contact/strain outcomes only where measurements support them. OpenSim models can provide model cross-checks with version/parameter provenance; they are not automatically independent human validation or same-subject anatomy. Perform uncertainty/sensitivity studies only after the deterministic mechanics and geometry gates pass, so uncertainty cannot conceal numerical failure.

## Open-source and license gate

Prefer permissive, reusable sources with explicit redistribution and derivative rights. Verify the **original provider's license for the exact version and asset**, not a repository badge, community description or software license. Record required attribution, share-alike/noncommercial restrictions, data-versus-software scope, transformation obligations and a compatibility decision for the intended combined release. “Open,” downloadable, or public imagery does not by itself authorize arbitrary redistribution. Keep compatible layers and notices traceable; unresolved terms block incorporation/publication of that asset, not independent mechanics work.

The owner's prior discussion supplied these **leads only**; no coverage or licensing assertion is made here, and no new assets are incorporated:

| Lead | Question for original-source review |
|---|---|
| BodyParts3D / Anatomography | Verify exact source/version/license and per-tissue coverage; retain current arm provenance and notices. Does the chosen geometry support valid volumetric mechanics or only an anatomical surface reference? |
| University of Denver Visible Human lower-body segmentations | Identify original release, specimen, individual tissue labels, availability and redistribution/derivative terms. Do not infer whole-body coverage from “Visible Human.” |
| NLM Visible Human source imagery | Verify exact imagery access and data-use/license terms, specimen/units/reference, and whether new segmentations may be redistributed under the intended release license. |
| SPL Knee Atlas | Verify original asset release/license, subject/reference, tissue coverage, attachment/contact topology and supported validation scope. |
| Z-Anatomy | Verify original project/version, component-source provenance, data/software licenses, anatomical granularity and derivative obligations. |
| OpenSim | Verify chosen model/data/software release independently, numerical conventions and provenance; determine what constitutes a model comparator versus measured validation. |

Parent is collecting precise original-source details separately. Incorporation requires a reviewed source manifest and a tissue-level coverage decision. Broad downloading or asset counts are not a substitute for these gates.

## Immediate handoff

The [finite-K comparison](mechanical-closure/full-p2-p1-results.md) establishes a functioning stationary full-P2/P1 controlled operator while retaining a genuine active-dominated negative direction. The next mechanics decision needs source-backed reference architecture and an explicit active-law hypothesis, followed by controlled specimen validation before anatomy. The previous dense lift/release, bulk-compression failures and refinement gaps remain unqualified. Preserve them as the benchmark to be improved; do not add skin or whole-body qualification claims around them.
