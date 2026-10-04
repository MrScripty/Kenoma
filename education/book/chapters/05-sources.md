# Sources and evidence boundaries {#sources-and-evidence-boundaries}

Sources below were opened and checked on 2026-10-04. The original mechanics explanations, worked examples, code, diagrams, and numerical experiment are produced for Kenoma. External source figures and anatomical assets have not been copied. The existing Apache-2.0 repository licence covers this original contribution; each future third-party asset must retain its own licence and attribution.

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

[Lean official installation documentation](https://lean-lang.org/install/) and the [official Lean 4.19.0 release](https://github.com/leanprover/lean4/releases/tag/v4.19.0). The project pins the version deliberately; it does not claim it is the newest release. Only the bundled standard library is imported. The successful kernel checks and their transitive-axiom reports are linked in each proof card and in the generated build evidence.

## What remains unverified

Anatomical measurements, asset licences, actual medical datasets, material parameters, muscle-force predictions, continuum tissue behavior, contact accuracy, patient-specific validity, and performance comparisons are not established by this first milestone. They belong to the next research and implementation stages. The browser tests establish behavior in the tested Chromium environment; they do not certify every browser, assistive technology, or medical application.
