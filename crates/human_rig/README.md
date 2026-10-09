# Stable mannequin rig

Version-1 `BoundRig` stores the canonical connected rest surface, immutable source
skeleton, and up to eight normalized bone influences per vertex. `bind_mannequin` extracts
that surface once. `deform_mannequin` applies blended dual-quaternion rigid
transforms without extracting a surface again. There is no simulation or physics.
The existing `human_surface` operation and all research modules remain unchanged.

Indices, vertex IDs, weights and provenance are identical in every posed output.
Hands against the body, crossed arms and crossed legs cannot acquire new welds.
They may interpenetrate: there is no collision detection or contact response.

Weights are computed only in canonical rest space using a compact C1 kernel
whose value and derivative vanish outside 1.65 times the local bone radius.
There is no nearest-bone switching, top-N pruning or posed-space rebinding.
The support excludes opposite active limbs; torso/clavicle/hip attachment bones
can legitimately share influences. Unused slots are zero and skipped.
Bone IDs 0–14 follow canonical graph edge order; bone 15
orients the head around node 3 (+Z front, yaw then local pitch/YXZ). Dual-quaternion
blending avoids the linear-blend joint-volume collapse. It is an artistic rig,
not anatomical tissue, general-purpose automatic rigging or collision handling.

Only canonical topology, unchanged radii and unchanged bone lengths are accepted.
Head yaw/pitch are character-local radians. Pose inputs and rest binding are never
mutated. `BoundRig::validate` rejects unsupported versions and malformed numeric
buffers/weights; it is not provenance certification of an externally edited mesh.
Normals combine deformed area-weighted normals with a rotated analytic-rest
correction, preserving the original smooth field shading in unchanged regions.

Tests cover hand-on-torso, crossed arms/legs, deep elbow/knee bends, and head
limits ±120° yaw / ±60° pitch. Exact indices, vertex count and source provenance
remain unchanged. Tests also check adjacent weight continuity, triangle validity,
unit normals, independent immutable inputs, serialization, local influences and
joint cross sections. At the deep-bend fixtures, projected elbow cross-section
area retains about 68% of rest and knee about 93%; neither collapses to a line.
DQ blending is not exact volume conservation: extreme bends can compress, bulge,
fold or self-intersect. No collision or contact correction is claimed.

The default bound mesh has 46,728 vertices / 93,452 triangles. Native release pose
deformation including validation, buffer cloning and normals measured
about 8 ms here with normal-bias correction, versus rest extraction around
0.2 seconds. This excludes WASM JSON conversion, worker transport and rendering; browser measurements are separate.
The normal correction is `normalize(posedDiscrete + rotate(restAnalytic −
restDiscrete))`, with rotated analytic normals as a cancellation fallback. It
retains geometric bend/stretch cues without exposing marching-tetrahedron normal
bias. This is smooth shading, not an exact analytic differential of skinning;
tiny sharply folded triangles can disagree with the smoothed vertex normals
(measured opposite-facing area fraction at most 0.000012 in the contact fixtures).
