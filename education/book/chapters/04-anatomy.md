# Anatomy is evidence, not a silhouette {#anatomy-is-evidence}

The previous laboratories isolate mechanics. An arm introduces three descriptions that must agree: rigid skeletal geometry, force-producing musculotendon paths, and deformable tissue. The humerus, radius and ulna are distinct bones. Elbow bending and forearm rotation are distinct motions; the biceps' distal attachment to the radius makes this separation important. Our next laboratory fixes forearm rotation and shoulder posture and replaces the elbow complex with one hinge. Its rods are teaching geometry, not segmented bones.

## Name the structures before assigning properties

The anterior volume includes biceps and the deeper brachialis; brachioradialis contributes a separate lateral path. The triceps heads provide extensor paths, and some muscles span the shoulder as well as the elbow. A single red actuator cannot identify their individual contributions. The chapter's synthetic flexor is deliberately called a **synthetic flexor**, rather than assigning its invented origin and insertion to a named anatomical muscle.

An attachment region, a segmented surface, a tendon guide point, and a fiber direction field are different data. The surface of a muscle does not tell us how its fascicles run or where a numerical routing point should be placed. An anatomical fascial expansion such as the bicipital aponeurosis also needs an attachment/interface model; drawing another cable is insufficient. The audited anatomy contribution supplies anatomical literature and distinctions, but no imported mesh in this edition establishes those features for our schematic.

## Published human numbers with their context

Murray, Buchanan and Delp examined ten human upper-extremity specimens. Measurements included architecture and tendon excursion; optimal fascicle lengths and physiological cross-sectional areas (PCSA) were then estimated. Their Table 2 gives the following study summaries. These are published biological estimates, **not this laboratory's defaults**, and no participant-level raw data are redistributed. [Original study, Table 2 and §3](#source-architecture)

| Reported quantity | Study summary | Interpretation |
|:--|:--|:--|
| Brachioradialis optimal fascicle length | 17.7 cm; SD 3.0 cm | Architecture estimate in the study specimens |
| Brachioradialis PCSA | 1.2 cm²; SD 0.6 cm² | Estimated parallel contractile area |
| Combined triceps PCSA | 14.9 cm²; SD 6.7 cm² | Aggregate reported for combined heads |

Convert 17.7 cm to 0.177 m and 1.2 cm² to 0.00012 m² before calculations. For a uniform architecture idealization, PCSA is volume divided by optimal fiber length. If maximum tendon-directed force is modeled as specific fiber tension times PCSA times cos(pennation), check whether the source already includes that cosine in its area convention. The segmented volume and PCSA do not themselves specify a maximum force: a specific-tension assumption is still needed.

Iivarinen and colleagues measured forearm indentation in nine healthy people, used ultrasound for tissue thickness, and fitted a layered hyperelastic model. Their resting effective moduli were **210 kPa for skin** and **1.9 kPa for adipose tissue**, equivalent to 210,000 Pa and 1,900 Pa. These are inverse-model values under that study's loading and layer assumptions. They are not universal tissue constants or an elbow-contact calibration. Neither value is inserted into the schematic hinge. [Original abstract and DOI](#source-indentation)

The distinction matters: a measured displacement, a parameter fitted from that displacement, and a new model's prediction are three separate objects. Testing the fitted model on its fitting observations is calibration. Testing on a reserved pose or load is a stronger check of generalization.

## A dataset must say what it observes

The audited research identifies several useful routes to actual data. The table records research-stage access, not completed integration into this executable.

| Resource | Observations or content | Boundary and licence evidence |
|:--|:--|:--|
| Visible Human | Cadaver cryosections, CT and MRI | Source images differ from derived segmentations; official public-domain access description |
| BodyParts3D | Reference anatomical geometry and anatomical identifiers | Official current archive CC BY 4.0; preserve exact acquired version and attribution |
| OpenArm 2.0 | Ultrasound-reconstructed biceps/arm volumes over poses and loads | Research audit: eleven participants, CC BY 4.0; registration and predicted-label quality need review |
| OpenArm Multisensor 2.0 | Ultrasound, EMG, force and task information | Research audit: CC BY 4.0; modalities concern different muscles; apply release errata |
| Quesada upper-limb dataset | EMG, kinematics and joint-torque time series | Research audit: CC BY-SA 4.0; torque is not measured individual muscle force |
| Arm26 | Educational OpenSim model with six actuators | Embedded model CC BY 3.0; educational geometry/actuators differ from this one-hinge model |

The research package verified a Multisensor time-series archive, but its raw bytes have not been integrated here. Its pickle serialization needs a reviewed conversion path; ordinary untrusted deserialization is unsuitable. A README or study abstract is not a substitute for an actual inspected trial. Our edition contains the numerical study summaries above, with citations, but no claim that it has analyzed the released medical time series.

The current MoBL-ARMS package has a noncommercial restriction according to the audited provider page, conflicting with an older catalogue's MIT label. It is excluded. Apache-2.0 on Kenoma code does not relicense any dataset, model, mesh, scan, or paper figure. [Data access and licence sources](#source-data)

## Expertise follows the contribution

Murray, Buchanan and Delp's original architecture experiments are relevant to architecture and moment capacity. Millard, Uchida, Seth and Delp's actuator comparisons are relevant to musculotendon modeling. Wakeling, Ryan and colleagues' continuum work is relevant to force/deformation coupling. Hallock's OpenArm research is relevant to imaging-derived muscle deformation. These are source-based areas of contribution, not endorsements of Kenoma or claims that any author reviewed it.

No audited source supplies a complete, co-registered loaded curl with all bones, fibers, activation histories, skin self-contact and pressure. The book therefore keeps the evidence gap visible while building mechanisms that can later be compared with compatible measurements.
