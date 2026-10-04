KENOMA ELBOW DATA CONTRIBUTION
Prepared 4 October 2026

This compact package supplies actual, openly licensed anatomy and recorded
biomechanical evidence for an educational elbow chapter. It contains three
independent evidence streams. They are NOT one calibrated subject or model.

1. Anatomical reference: ten BodyParts3D 4.0 right-arm surfaces, original OBJ
   plus JSON in metres. These are a constructed static adult-male atlas,
   obtained from the official 99%-polygon-reduced release. 13,852 vertices,
   20,218 triangles. This supplies real atlas geometry, not a fitted elbow rig.
2. Recorded evidence: one OpenArm Multisensor 2.0 participant/trial example.
   4,403 retained normalized samples over 85.904 s, and 172 half-second bins.
   Ultrasound-derived brachioradialis thickness, biceps brachii sEMG amplitude,
   and wrist-contact force are recorded at a fixed 90-degree elbow posture.
   Amplitudes are dimensionless; raw physical calibration is not established.
3. Model evidence: six Arm26 actuator parameter sets, extracted verbatim in
   numerical value from a pinned model XML. These are model parameters, not
   direct participant measurements or medically validated constants.

For the book author

- Use figures/bodyparts3d_right_arm.png or .svg for an anatomical overview.
- Use figures/openarm_recorded_trial.png or .svg to teach the distinction
  between thickness, electrical activity and net external force. Keep the
  muscle labels and normalization caveat. This is an original figure made
  from data, not a copied publisher figure.
- Use data/arm26_parameters.csv or .json for an explicitly labeled model
  parameter example; no brachioradialis actuator is present in Arm26.
- Figure captions and image alternative text are in FIGURE_CAPTIONS.txt.
- Cite the original sources and retain LICENSES_AND_ATTRIBUTION.txt. Every
  distributed payload has a hash and evidence category in provenance.json.

For the interactive elbow author

- data/bodyparts3d_right_arm_m.json contains per-part vertices_m and
  triangles_zero_based. Vertex units are SI metres. The source atlas axes
  are x toward anatomical left, y posterior, z superior. There is no
  centering, rig, joint center, rest binding, moment-arm field or animation.
  Original OBJ files are in sources/bodyparts3d and use millimetres.
- JSON and CSV recording columns have units in their names: _s is seconds;
  _1 is dimensionless SI unit one. Half-second bins use arithmetic,
  sample-weighted means and include the count and actual mean sample time.
  Do not turn the mean display into an assumed uniformly sampled raw signal.
- Show the measured trace as an evidence panel or independent recorded mode.
  Do not deform the atlas from this single thickness trace and call the
  result measured anatomy. Anatomical atlas and participant data are not
  registered, and the model's coordinates are not the atlas coordinates.
- A pose slider, muscle activation slider, fibre path, skin shell, crease,
  contact pressure, fat compression, tendon stretch or force-sharing result
  remains a schematic or model-derived addition unless separately validated.
  Pose alone does not uniquely identify activation. A 90-degree acquisition
  posture is not a measured angle trajectory.

Source and transformation details

BodyParts3D: ten ZIP members were fetched by small public HTTP byte ranges,
checked against the archive central directory, decompressed and CRC-checked.
Original bytes and historical notices are preserved. JSON conversion divides
positions by 1000 and changes face indices from one-based to zero-based.
No topology editing or geometry fitting was done. Normals are omitted from
the JSON; the OBJ files preserve their original contents. The official
coordinate diagram confirms source units and axes. Bounds and edge counts
are reported for inspection; they do not certify a simulation-ready mesh.

The old source OBJ comments say CC BY-SA 2.1 Japan. The current official
archive license and README were updated in February 2025 to CC BY 4.0.
This package records both facts, relies on that current official grant for
redistribution, and does not erase the old comments. See the cited license
page if a downstream institution requires its own rights review.

OpenArm: source time_series/2/trial_1b.p was inspected with a deliberately
narrow passive opcode reader. It never imports a pickle-named module or calls
a pickle-supplied callable, and never invokes pickle.load. Only known scalar
encodings are translated to ordinary numbers. Source archive/member hashes
are recorded. The original pickle is not distributed in this package.

The source analysis maps Processed[0] to ultrasound, [1] to sEMG, and [2] to
force. Startup calibration data use a different scale and are excluded.
The known trial-1b start rule yields index 1665. The retained Processed
values are already trial-calibrated and are used directly, not normalized
a second time. Zero refers to relaxed calibration and one to the calibration
contraction signal; values outside [0,1] are kept. Original study normalization
is (signal - relaxed mean)/(MVC mean - relaxed mean), not whole-trial min-max.

We subtract Times[1665] and omit absolute timestamps, calibration extrema,
demographics, surveys and images. The original anonymous participant code 2
is retained only for provenance. A 0.5 s display bin is [start,end), with the
final bin possibly partial. Recorded Times are irregular: this retained
example averages about 51.24 saved samples/s despite the protocol's nominal
best-effort 1 kHz collection description. Use the saved timestamps. We do
not claim exact reproduction of the paper's processing or statistics.

Arm26: source revision 84b487c4e3245359a64381e01f01b9cf4772d457,
Models/Arm26/arm26.osim, is byte-identical to the checked official file.
The Git blob hash is 2ff458149668bb2f0de24572f80658f8dd9db1d9. Only six
self-described SI parameter types and coordinate bounds are extracted.
Coordinates' model bounds are not clinical normal ranges of motion.

Reproduction

Python 3 standard library is sufficient for data extraction and validation.
NumPy and Matplotlib are used only by make_figures.py. They are not bundled.

From this package directory:
  python3 scripts/prepare_data.py
  python3 scripts/make_figures.py
  python3 scripts/validate_package.py

To independently re-extract the source OpenArm trial, download the exact
10,269,052-byte archive using the public URL in its metadata, verify SHA-256,
then run:
  python3 scripts/prepare_data.py --openarm-archive /path/to/time_series.zip

To re-fetch the atlas, fetch_sources.py obtains only metadata and directory
ranges; fetch_atlas_subset.py retrieves the ten named members. Each fetch
has a size cap and a free-space floor. These use the official archive URL;
if bytes change, compare provenance hashes before adopting a new version.
The exact archive was 142,903,898 bytes. Its full-file hash is NOT claimed,
since the complete archive was deliberately not downloaded.

Document acquisition coverage (review repair)

audit/download_log.json is the unchanged historical BodyParts3D metadata
receipt. Its coverage is ZIP-directory ranges, the mapping, license and
archive README; it contains NO OpenArm or Arm26 request receipts. Atlas
member receipts and independent download-time byte pins are in
audit/bodyparts_subset_download_log.json and bodyparts_subset_members.json.
Do not interpret regenerated provenance.json as independent source identity.
Validation hashes actual Arm26 bytes against the pinned constant, actual OBJ
bytes against download-time member pins, and checks complete vertex counts
and 3-coordinate shapes before comparing every mm-to-m conversion.

The additional coordinate PNG, release-4.0 HTML, Arm26 XML and OpenArm
release README/errata have explicit accepted-byte pins and acquisition
locators in audit/source_document_pins.json. Their original network receipts
were not supplied. The original OpenArm data-release notices are distinct
from the analysis repository's README; do not substitute that README.

Reacquire these five documents without replacing the accepted package:
  python3 scripts/fetch_sources.py --documents --output /new/external/directory

This retains the 30 MiB transfer ceiling, 128,000-byte per-document limits
and 1.5 GiB free-space floor. A candidate is written only after exact size
and SHA-256 verification. Current timestamps, response headers, errors and
verification results are recorded in the new output directory; existing
output directories and destinations inside this package are refused.

For OpenArm, obtain readme.md and errata.md from the official release folder
listed in the pins, then append --openarm-release-directory /path/to/release.
Those files are size-limited and hash-verified locally. This does not invent
a direct download URL or an original HTTP receipt. Network byte receipt and
local file verification are explicitly different acquisition methods.

audit/document_reacquisition_log.json records the actual current attempt:
Arm26 matched the pinned bytes; the two BodyParts3D document requests and
OpenArm release-folder access were unavailable here (403 proxy tunnel
responses). The two OpenArm files still require manual official acquisition.
No unavailable or mismatched upstream bytes replace any original source.
An incomplete run returns exit status 1 and leaves its partial receipt.
These access gaps remain explicit, rather than claiming full reacquisition.

The original contribution's 992 checks and 40-payload byte inventory remain
historical facts. The repaired package has additional shape checks and audit
payloads; its current check count and inventory are reported by the scripts.

Limits

Educational and research material only. No clinical validation, diagnosis,
injury threshold, individualized treatment recommendation, or safety
certification is supplied. Atlas errors and strong polygon reduction remain.
No skin/fat/fascia/cartilage/contact mechanics dataset is included. A single
recorded trial does not establish a population relationship or explain how
three-dimensional tissue deforms through a range of motion. BodyParts3D,
OpenArm and Arm26 are separate sources and must stay visibly distinct.
