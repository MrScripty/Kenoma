# Inspect real anatomy and recorded evidence {#actual-anatomical-data}

An atlas, a recorded human trial and an actuator model answer different questions. This chapter includes **actual licensed data bytes**, with their source-specific rights, transformations and hashes. None of the three evidence streams is registered to either of the others or to the teaching actuator. Looking more anatomical cannot turn a schematic force law into a validated physiological model.

## Ten static anatomical surfaces

![Two anterior-facing views of a straight right-arm atlas: humerus, radius and ulna alone, then seven selected muscle surfaces with keyed colors.](data/elbow-v1/figures/bodyparts3d_right_arm.png)

Ten BodyParts3D 4.0 right-arm surfaces preserve the original atlas pose: humerus, radius, ulna, brachialis, brachioradialis, both biceps heads and three triceps heads. The official 99%-polygon-reduced release supplies 13,852 vertices and 20,218 triangles. It is a constructed static adult-male reference atlas, rather than scanned geometry for the OpenArm participant. Rendering colors are explanatory. Source axes are x toward anatomical left, y posterior and z superior; original OBJ positions are in millimetres. The JSON divides positions by 1,000 and converts face indices to zero-based, with no topology editing, joint fitting or rigging.

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International. Changes: ten-part selection, SI conversion and original rendering. The original OBJ comments retain the historical CC BY-SA 2.1 Japan notices; the package also includes the current official archive's February 2025 CC BY 4.0 grant. [Source and rights record](#source-acquired-data)

The browser viewer centers and rotates the atlas **for display only**. It can show bones or individual named parts, and switch anterior, oblique and posterior views. It does not animate a guessed elbow axis. Polygon reduction and edge diagnostics do not establish a mesh suitable for medical contact calculations. No skin, fat, fascia, cartilage or tendon material field is provided.

## One recorded trial at a held posture

![Three aligned recorded curves over about 86 seconds: normalized brachioradialis thickness, biceps sEMG and wrist-contact force, with different amplitudes and profiles.](data/elbow-v1/figures/openarm_recorded_trial.png)

OpenArm Multisensor 2.0 participant code 2, trial 1b, was recorded with the right elbow held at 90° and the forearm supinated. The retained segment contains 4,403 preprocessed normalized samples over 85.903537 s. Ultrasound measures **brachioradialis thickness**; sEMG measures **biceps brachii electrical activity**; wrist-contact force is a net external signal. They are different quantities and, for ultrasound and sEMG, different muscles. The fixed acquisition posture is not a measured angle trajectory. Hallock et al. (2021), DOI 10.1109/TNSRE.2021.3133813; data CC BY 4.0. Changes: selected trial/segment, relative timestamps, display binning and original plot.

The source's retained `Processed` values are already trial-calibrated. Zero refers to relaxed calibration and one to its calibration contraction: (signal − relaxed mean)/(MVC mean − relaxed mean). The package does not normalize them again or clamp values outside [0,1]. Their amplitude unit is **one**, not metres, volts or newtons. Calibration to those physical units is not established, and sEMG is not labeled activation a or individual-muscle force.

The saved timestamps are irregular. The segment averages 51.243524 saved samples/s despite the protocol's nominal best-effort 1 kHz description. The display uses 172 half-second bins, each [start,end), with sample-weighted arithmetic means and the actual mean sample time; the last bin can be partial. Use original relative timestamps for subsequent analysis. These binned curves do not establish spectral behavior, latency, causality, population uncertainty or a universal force law.

{{evidence}}

[SI atlas JSON](data/elbow-v1/data/bodyparts3d_right_arm_m.json), [original recorded samples CSV](data/elbow-v1/data/openarm_s2_1b_normalized_samples.csv), [display bins CSV](data/elbow-v1/data/openarm_s2_1b_0p5s_bins.csv), [trial metadata](data/elbow-v1/data/openarm_s2_1b_metadata.json).

## Six source model actuators, with units

Arm26's six Thelen2003 actuator sets come from the pinned official OpenSim XML. These are **model parameters**, not direct participant measurements or clinical norms. Three parameters are displayed below; [the complete extracted JSON](data/elbow-v1/data/arm26_parameters.json) and [CSV](data/elbow-v1/data/arm26_parameters.csv) also retain pennation angle (rad), activation/deactivation time constants (s), units, source paths and coordinate bounds. There is no brachioradialis actuator in Arm26. Do not replace the schematic actuator with these values while retaining its unrelated geometry and then call the result calibrated.

| Arm26 actuator | Peak isometric parameter (N) | Optimal fiber length (m) | Tendon slack length (m) |
|:--|--:|--:|--:|
| TRIlong — triceps brachii long head | 798.52 | 0.134 | 0.143 |
| TRIlat — triceps brachii lateral head | 624.3 | 0.1138 | 0.098 |
| TRImed — triceps brachii medial head | 624.3 | 0.1138 | 0.0908 |
| BIClong — biceps brachii long head | 624.3 | 0.1157 | 0.2723 |
| BICshort — biceps brachii short head | 435.56 | 0.1321 | 0.1923 |
| BRA — brachialis | 987.26 | 0.0858 | 0.0535 |


OpenSim Development Team (Reinbolt, Seth, Habib and Hamner), adapted from Kate Holzbaur's model; CC BY 3.0. The complete source credit and licence remain in [unchanged model XML](data/elbow-v1/sources/arm26.osim). Changes: explicit numerical extraction into SI-labelled files. Official source revision is `84b487c4e3245359a64381e01f01b9cf4772d457`; XML SHA-256 is `e2224d0044eb393b05d64926c3fa1682c451a9adc7f510e5517ef9958d3d41b9`.

## What the checks establish

The exact 2,058,262-byte received package has SHA-256 `af02aaeb37d626f448a658183f764dc6cf68b979730c413ba31997f26062d169`. Its 992 checks pass again in this repository: source/payload hashes, atlas units and face bounds, six parameter sets against XML, finite strictly ordered recorded times, full bin accounting and independently recomputed means. The passive pickle reader rejects executable globals; no source pickle is bundled or executed. These are data/transformation checks, not biological validation. Archive directory/CRC evidence is preserved; a full BodyParts3D archive hash is deliberately not claimed because only selected members were acquired.

[Per-file provenance](data/elbow-v1/provenance.json), [licences and attribution](data/elbow-v1/LICENSES_AND_ATTRIBUTION.txt), [reproduction and limitations](data/elbow-v1/README.txt). Later anatomical simulation requires registered joint frames, attachment/path maps, material fields, boundary conditions and independent validation data. A single isometric thickness trace cannot supply all of those missing quantities.
