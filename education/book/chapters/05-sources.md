# Sources and evidence boundaries {#sources-and-evidence-boundaries}

The foundation sources and the primary papers marked independently opened below were checked on 2026-10-04. Dataset references supplied by the incoming audit are explicitly distinguished. The original mechanics explanations, worked examples, code, diagrams, and numerical experiments are produced for Kenoma. No external publication figure is copied. The explicitly attributed data chapter redistributes licensed atlas meshes, extracted model parameters and a recorded normalized trial with their original provenance. The existing Apache-2.0 repository licence covers this original contribution; third-party data retains its own component licences and attribution, provided in the data package and notices.

## International units {#source-bipm}

Bureau International des Poids et Mesures. *The International System of Units*, 9th edition, English version 4.01 (2026), §2.3.4 and Tables 4-5. [Publisher page](https://www.bipm.org/en/publications/si-brochure), [DOI](https://doi.org/10.59161/AUEZ1291). Verified for the units of force, torque, energy, and the distinction between quantity and unit. Publisher page states CC BY 4.0; no brochure figure is redistributed here.

## Newton's laws {#source-force}

Peter Dourmashkin. *Chapter 7: Newton's Laws of Motion*, original MIT 8.01 course notes, updated course release 2022, §§7.3-7.4. [Primary notes PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter7.pdf). Verified for constant-mass net force and action-reaction pairs. This book supplies its own horizontal-force example and illustration. MIT OCW terms apply to source content; that content is cited, not redistributed as Kenoma Apache-2.0 material.

## Torque {#source-torque}

Peter Dourmashkin. *Chapter 17: Two Dimensional Rotational Dynamics*, original MIT 8.01 course notes, updated course release 2022, §17.1. [Primary notes PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter17.pdf). Verified for torque about an origin and the cross-product convention. The point-load lever and integer-coordinate proofs here are original examples.

## Energy and work {#source-energy}

Peter Dourmashkin. *Chapter 13: Energy, Kinetic Energy, and Work*, original MIT 8.01 course notes, updated course release 2022, §§13.2-13.6. [Primary notes PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter13.pdf). Verified for kinetic energy and the work-energy relation. The integrator derivation, oscillator implementation, and executed comparison are original work in this repository.

## Muscle model comparison {#source-muscle}

Matthew Millard, Thomas Uchida, Ajay Seth, and Scott L. Delp. “Flexing Computational Muscle: Modeling and Simulation of Musculotendon Dynamics.” *Journal of Biomechanical Engineering* 135(2):021005 (2013). DOI: [10.1115/1.4023390](https://doi.org/10.1115/1.4023390). [Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3705831/), §§2-4. Verified for activation/contraction separation, active/passive muscle components, and elastic versus rigid-tendon assumptions. No muscle curves, figures, benchmark data, or meshes from the paper are redistributed in this milestone.

## Formal toolchain {#source-lean}

[Lean official installation documentation](https://lean-lang.org/install/) and the [official Lean 4.19.0 release](https://github.com/leanprover/lean4/releases/tag/v4.19.0). The project pins the version deliberately; it does not claim it is the newest release. The original 25 declarations import the bundled standard library. The four additional real kinematic claims in `ContinuumProperties.lean` import [official mathlib v4.19.0](https://github.com/leanprover-community/mathlib4/tree/c44e0c8ee63ca166450922a373c7409c5d26b00b), with its exact commit and transitive dependency manifest pinned in `proofs/mathlib-lock.json`. The successful kernel checks and their transitive-axiom reports are linked in each proof card and in the generated build evidence.

## Human architecture {#source-architecture}

Wendy M. Murray, Thomas S. Buchanan and Scott L. Delp. “The isometric functional capacity of muscles that cross the elbow.” *Journal of Biomechanics* 33:943–952 (2000). [DOI](https://doi.org/10.1016/S0021-9290(00)00051-8), [author-hosted original PDF](https://research.me.udel.edu/buchanan/PDF_Files/Murray%2C%20Buchanan%2C%20Delp%2C%20JB%202000.pdf). Independently opened full text; Table 2 and §3 checked for the three reported study summaries. Human cadaver measurements and derived architecture estimates are distinguished. No source table image or participant-level data is copied.

## Forearm indentation {#source-indentation}

Jarkko T. Iivarinen, Rami K. Korhonen, Petro Julkunen and Jukka S. Jurvelin. “Experimental and computational analysis of soft tissue stiffness in forearm using a manual indentation device.” *Medical Engineering and Physics* 33:1245–1253 (2011). [DOI](https://doi.org/10.1016/j.medengphy.2011.05.015), [original abstract at PubMed](https://pubmed.ncbi.nlm.nih.gov/21696992/). Independently checked abstract, including nine subjects, layered inverse FE fitting, and 210/1.9 kPa resting estimates. Full publisher text was not independently read here; no additional material-law detail or raw observations are inferred.

## Contracting tissue under compression {#source-compression}

D. S. Ryan, S. Domínguez, S. A. Ross, N. Nigam and J. M. Wakeling. “The Energy of Muscle Contraction. II. Transverse Compression and Work.” *Frontiers in Physiology* 11:538522 (2020). [Original full text](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2020.538522/full), [DOI](https://doi.org/10.3389/fphys.2020.538522). Independently opened primary paper for its model scope and force/work mechanism. Computational evidence is kept separate from measured human elbow-contact data.

## Position-based compliance {#source-xpbd}

Miles Macklin, Matthias Müller and Nuttapong Chentanez. “XPBD: Position-Based Simulation of Compliant Constrained Dynamics.” ACM MIG (2016). [Author-hosted original paper](https://mmacklin.com/xpbd.pdf). Independently opened for compliance, timestep scaling and multiplier accumulation. No implementation or benchmark speed from this paper is reproduced as a Kenoma result.

## Geometric skinning {#source-dqs}

Ladislav Kavan, Steven Collins, Jiří Žára and Carol O'Sullivan. “Geometric Skinning with Approximate Dual Quaternion Blending.” *ACM Transactions on Graphics* 27(4) (2008). [Author-hosted original paper](https://users.cs.utah.edu/~ladislav/kavan08geometric/kavan08geometric.pdf). Independently opened for the geometric approximation and LBS artifacts. The book's two-rotation algebraic counterexample is original, and no tissue/contact guarantee is attributed to skinning.

## Dataset and model access {#source-data}

The incoming anatomy audit supplies the access/rights distinctions for [Visible Human](https://www.nlm.nih.gov/research/visible/visible_human.html), [OpenArm 2.0](https://simtk.org/frs/?group_id=1617), [OpenArm Multisensor research/code](https://github.com/lhallock/openarm-multisensor), [Quesada data](https://doi.org/10.5281/zenodo.11209324), [Arm26's model file](https://github.com/opensim-org/opensim-models/blob/master/Models/Arm26/arm26.osim), and the [current MoBL-ARMS package](https://simtk.org/frs/?group_id=657). These are audited research references; the accompanying data chapter now contains the verified licensed package described below. [BodyParts3D's official terms](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) were independently checked. Exact-package provenance and permissions are required before later redistribution. Incoming package hashes and access limitations are recorded in `education/research/integration-notes.md` in the source tree.

## Continuum background access record {#source-continuum}

Eftychios Sifakis and Jernej Barbič. *Finite Element Method Simulation of 3D Deformable Solids* (2015). [Author publication record](https://pages.cs.wisc.edu/~sifakis/) independently opened; it identifies the book and linked course. Full course notes were inaccessible in this execution environment, so this record verifies bibliographic identity only. No constitutive formula or performance result is attributed to unread notes. The affine block energy, stress derivative and equilibrium experiments are original Kenoma derivations; the independently opened Ryan paper above supplies compression-model context.

## Acquired package sources {#source-acquired-data}

BodyParts3D 4.0: Mitsuhashi et al., *Nucleic Acids Research* 37:D782–D785 (2009), [DOI](https://doi.org/10.1093/nar/gkn613). The exact package contains ten original official-archive OBJ members, SI JSON conversion, archive directory/CRC evidence and current official CC BY 4.0 grant. Historical CC BY-SA 2.1 Japan comments remain untouched.

OpenArm Multisensor 2.0: Hallock et al., *IEEE TNSRE* 29:2625–2634 (2021), [DOI](https://doi.org/10.1109/TNSRE.2021.3133813). The package provides one transformed normalized trial, source README/errata, pinned analysis revision, original archive/member hashes and CC BY 4.0 attribution. The package audit was read; the full source archive was not re-downloaded here.

Arm26: [official pinned XML](https://github.com/opensim-org/opensim-models/blob/84b487c4e3245359a64381e01f01b9cf4772d457/Models/Arm26/arm26.osim), official revision independently opened and byte hash checked against the packaged source. Embedded OpenSim Development Team/Kate Holzbaur credit and CC BY 3.0 notice are retained. The extraction checks all six actuator parameter sets against XML.

[Complete component licences and changes](data/elbow-v1/LICENSES_AND_ATTRIBUTION.txt), [per-file provenance](data/elbow-v1/provenance.json). This worker verified the supplied archive SHA-256, all manifested payloads, parameter extraction, atlas SI conversion and display-bin means. These checks validate bytes and transformations, not biological calibration.

## What remains unverified

Published architecture and fitted-modulus summaries above are verified within their stated sources and methods. The acquired package establishes the specific data and provenance described in the data chapter. The schematic actuator's biological calibration, anatomical continuum/contact accuracy, patient-specific validity and performance rankings are not established by this edition. The browser tests establish behavior in the tested Chromium environment; they do not certify every browser, assistive technology, or medical application.


## Geometric posing and the integrated proof boundary {#source-embedded-cohort}

Ladislav Kavan, Steven Collins, Jiří Žára and Carol O'Sullivan. “Geometric Skinning
with Approximate Dual Quaternion Blending.” *ACM Transactions on Graphics* 27(4)
(2008). DOI: [10.1145/1409625.1409627](https://doi.org/10.1145/1409625.1409627).
[Author-hosted full text](https://users.cs.utah.edu/~ladislav/kavan08geometric/kavan08geometric.pdf),
§§1–2 and 4, opened 2026-10-09. Supports geometric transformation blending and
its distinction from physical simulation, not anatomical validity or a guarantee
for Kenoma's particular rig. No paper figures or source assets are redistributed.

The architecture-to-force chapter retains its primary-source ledger. Murray,
Buchanan and Delp, *Journal of Biomechanics* 33 (2000), 943–952,
[author-laboratory full text](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf),
DOI [10.1016/S0021-9290(00)00051-8](https://doi.org/10.1016/S0021-9290(00)00051-8),
was re-opened 2026-10-09. The study concerns architecture and moment arms in
cadaveric elbow muscles; it does not calibrate this book's authored examples.
The original contribution's more detailed extraction and exclusions are retained.

The Lean project's [Axioms and Computation documentation](https://lean-lang.org/theorem_proving_in_lean4/Axioms-and-Computation/)
was opened 2026-10-09 for the distinction between kernel-checked declarations,
axiom dependencies and computation. The build still records the pinned Lean
4.19.0 toolchain, complete source hashes and actual dependency reports. This
citation does not establish JavaScript refinement or replace compilation.
