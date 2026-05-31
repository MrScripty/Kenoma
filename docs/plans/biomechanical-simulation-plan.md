# Biomechanical Simulation Plan

Date: 2026-05-30
Status: Draft

## Purpose

This document describes an optional biomechanical simulation layer for the Human Mesh Bevy Runtime project. The core runtime remains focused on visual character generation:

1. Load a canonical fixed-topology base mesh.
2. Apply morph targets.
3. Fit/update a skeleton.
4. Apply pose transforms.
5. Skin and render the surface mesh in Bevy.

The biomechanical layer is a separate concern. It should add subject measurements, segment masses, joint constraints, center-of-mass diagnostics, rigid-body dynamics, optional muscle path simulation, and an advanced continuum tissue deformation track without blocking the visual mesh pipeline.

The immediate goal is not to simulate skin sliding over muscles. The first useful goal is a physically meaningful body model that can be inspected in Bevy and used for animation analysis, balance checks, pose plausibility diagnostics, and motion/tissue experiments. Later, the same model can become a source of deformation that supplements or replaces hand-authored blend shapes in selected body regions.

## Runtime Contract

The implementation stack for this plan is the Rust workspace plus Bevy 0.18 for visualization overlays. The biomechanical model, validation, kinematics, diagnostics, and numerical routines must remain framework-independent; Bevy integration must live behind the Bevy integration crate.

The canonical biomechanical data is `BiomechModelAsset` and related records described in this plan. The plan stores biomechanical parameters, state, trajectories, and analysis results in the `.human.sqlite` project database that Bevy can load and inspect.

## Self-Contained Implementation Contract

The first implementation should use the concrete models below.

Scope for the first implementable biomechanical layer:

- Subject measurements.
- Segment dimensions.
- Segment mass, center of mass, and approximate inertia.
- Joint hierarchy and joint limits.
- Center-of-mass and balance diagnostics.
- Simple muscle/tendon path geometry.
- Pose plausibility checks.
- Optional reduced soft-body experiments.

Out of scope for the first implementable layer:

- Full finite element analysis.
- Full optimal control.
- Full forward dynamics with contacts.
- Full Hill-type muscle equilibrium.
- Accurate skin sliding over muscles.

Coordinate conventions:

- Use the same model-space convention as the visual runtime.
- `+Y` is up.
- `+X` is character right.
- `+Z` is character forward.
- Use meters, kilograms, seconds, Newtons, and radians.
- Store all segment frames in model space after pose evaluation.

Numerical defaults:

```rust
const GRAVITY: Vec3 = Vec3::new(0.0, -9.80665, 0.0);
const MIN_SEGMENT_LENGTH: f32 = 0.01;
const MIN_SEGMENT_MASS: f32 = 0.001;
const JOINT_LIMIT_EPSILON_RAD: f32 = 1.0e-4;
const BALANCE_FOOT_MARGIN: f32 = 0.02;
```

## Build Contract

This section is normative. If it conflicts with background/context sections later in the document, this section wins.

### Normative Scope

The first biomechanical implementation must support:

- Loading a canonical `BiomechModelAsset`.
- Validating subject measurements, segments, joints, coordinates, muscles, and contacts.
- Deriving default subject measurements from height and mass.
- Computing segment mass, local COM, and approximate inertia.
- Evaluating articulated forward kinematics.
- Computing whole-body COM.
- Checking joint limits.
- Checking foot-support balance.
- Computing simple muscle path length.
- Computing finite-difference moment arms.
- Reporting structured diagnostics.
- Drawing biomechanical overlays in Bevy.

The first implementation does not need:

- full finite elements.
- full optimal control.
- full coupled multibody dynamics.
- external solver file formats.
- real-time tissue simulation.
- clinically accurate muscle models.

### Background Sections Are Non-Binding

Background context explains why certain concepts are useful, but it is not an implementation requirement. Implement the data types, algorithms, APIs, and tests in this build contract first.

### Persistent Storage Contract

Use the project `.human.sqlite` database as the only required disk format.

Required logical records:

- `biomech_models`: subject measurements, segments, joints, coordinates, muscle paths, contacts, tissue regions, materials, embeddings, and validation tolerances.
- `biomech_states`: current generalized coordinates, speeds, muscle activations, contact enablement, selected analysis options, and overlay/debug settings.
- `biomech_trajectories`: sampled pose/coordinate curves, activation curves, force curves, contact events, and diagnostics that Bevy can replay.
- `tissue_results`: optional reduced or offline tissue displacement fields, driver states, residuals, and provenance needed to decide whether the result is safe to apply.

These records store parameters and analysis results, not rendered meshes. Do not persist Bevy mesh buffers, skinned visual vertices, generated overlay geometry, temporary solver matrices, Jacobian workspaces, or frame-by-frame debug line lists as authoritative project state. Any cache must be disposable and keyed by the source asset hash plus state/options hash.

### Required Sample Assets

Add these files:

```text
assets/samples/biomech/minimal_biomech.human.sqlite
```

The minimal subject must include:

- height and mass.
- torso, left thigh, left shank, right thigh, right shank, left foot, right foot.
- at least one hinge joint.
- at least one Euler3 joint.
- two foot contact polygons or contact point sets.
- one two-point muscle path.
- one via-point muscle path.

### Public API

The `human_persistence` crate must expose biomechanical project load/save APIs equivalent to:

```rust
pub fn load_biomech_model_from_project(
    project: &HumanProjectStore,
    model_id: BiomechModelId,
)
    -> Result<BiomechModelAsset, BiomechLoadError>;

pub fn load_biomech_state_from_project(
    project: &HumanProjectStore,
    state_id: BiomechStateId,
)
    -> Result<BiomechStateAsset, BiomechLoadError>;

pub fn save_biomech_state_to_project(
    project: &mut HumanProjectStore,
    state: &BiomechStateAsset,
)
    -> Result<BiomechStateId, BiomechSaveError>;
```

The `human_core` or future `human_biomech` crate must expose framework-independent biomechanical APIs equivalent to:

```rust
pub fn validate_biomech_model(asset: &BiomechModelAsset) -> BiomechDiagnostics;

pub fn preprocess_biomech_model(asset: BiomechModelAsset)
    -> Result<BiomechModel, BiomechBuildError>;

pub fn derive_subject_measurements(input: PartialSubjectMeasurements) -> SubjectMeasurements;

pub fn compute_segment_mass_properties(
    subject: &SubjectMeasurements,
    profile: &SegmentProfile,
) -> Vec<BodySegment>;

pub fn evaluate_biomech_fk(model: &BiomechModel, state: &GeneralizedState) -> Vec<Mat4>;

pub fn compute_segment_coms(model: &BiomechModel, segment_global: &[Mat4]) -> Vec<Vec3>;

pub fn compute_whole_body_com(model: &BiomechModel, segment_global: &[Mat4]) -> Vec3;

pub fn check_joint_limits(model: &BiomechModel, state: &GeneralizedState) -> Vec<JointLimitViolation>;

pub fn evaluate_balance(
    model: &BiomechModel,
    segment_global: &[Mat4],
    contacts: &[ResolvedContact],
) -> BalanceDiagnostic;

pub fn muscle_path_length(path: &MusclePath, segment_global: &[Mat4]) -> f32;

pub fn finite_difference_moment_arm(
    model: &BiomechModel,
    state: &GeneralizedState,
    muscle: MuscleId,
    coordinate: CoordinateId,
) -> f32;
```

### Diagnostics Types

```rust
enum BiomechDiagnostic {
    InvalidSubjectMass { mass_kg: f32 },
    InvalidSubjectHeight { height_m: f32 },
    MissingSegment { name: String },
    DuplicateSegmentName { name: String },
    MissingJoint { name: String },
    DuplicateJointName { name: String },
    MissingCoordinate { name: String },
    DuplicateCoordinateName { name: String },
    SegmentMassClamped { segment: String, old: f32, new: f32 },
    SegmentLengthClamped { segment: String, old: f32, new: f32 },
    InertiaNotPositive { segment: String },
    JointParentMissing { joint: String, parent: String },
    JointChildMissing { joint: String, child: String },
    JointLimitInvalid { joint: String },
    JointLimitViolation { coordinate: String, value: f32, min: f32, max: f32 },
    MuscleSegmentMissing { muscle: String, segment: String },
    MusclePathTooShort { muscle: String },
    ContactSegmentMissing { contact: String, segment: String },
    NoSupportContacts,
    ComOutsideSupportPolygon { distance_m: f32 },
    NonFiniteCom,
    NonFiniteTransform { segment: String },
}
```

### Numeric Tolerances

```rust
const BIOMECH_POSITION_EPSILON: f32 = 1.0e-5;
const BIOMECH_MASS_EPSILON: f32 = 1.0e-5;
const BIOMECH_INERTIA_EPSILON: f32 = 1.0e-8;
const BIOMECH_COM_EPSILON: f32 = 1.0e-5;
const BIOMECH_MUSCLE_LENGTH_EPSILON: f32 = 1.0e-5;
const BIOMECH_MOMENT_ARM_EPSILON: f32 = 1.0e-3;
const BIOMECH_IK_RESIDUAL_EPSILON: f32 = 1.0e-3;
const BIOMECH_BALANCE_EPSILON: f32 = 1.0e-4;
```

### Required Dependencies

Preferred dependencies:

```text
glam = vector/matrix transforms
serde = derive
rusqlite = SQLite project persistence, preferably isolated to `human_persistence`
thiserror = structured errors
approx = numeric test assertions
nalgebra = optional only when damped least-squares IK or matrix solves are implemented
```

Do not add a physics engine or external solver dependency for the first implementation.

### Standards Compliance And Blast Radius

All implementation work for this plan must comply with the standards in `/media/jeremy/OrangeCream/Linux Software/repos/owned/developer-tooling/Coding-Standards/`. The required standards are `CODING-STANDARDS.md`, `TESTING-STANDARDS.md`, `DOCUMENTATION-STANDARDS.md`, `SECURITY-STANDARDS.md`, `DEPENDENCY-STANDARDS.md`, `PLAN-STANDARDS.md`, and the Rust-specific standards in `languages/Rust/`.

Architecture boundaries:

- `human_biomech` or the biomech module inside `human_core` owns biomechanical data types, validation, preprocessing, measurement derivation, mass-property math, kinematics, COM/balance diagnostics, muscle path math, and fixtures. It must not depend on Bevy, rendering, UI, file watchers, async runtimes, SQLite, or platform APIs.
- `human_persistence` owns SQLite database opening, migrations, project metadata, biomechanical load/save repositories, transaction boundaries, and conversion between database records and biomechanical asset structs.
- `human_bevy` owns overlays, debug drawing, resource/component wiring, system schedules, and synchronization from visual pose state into biomech state.
- App binaries are composition roots. They choose biomech plugins, overlay defaults, sample assets, and whether biomechanical diagnostics are active.
- Continuum experiments and optimizer tooling must be separate optional crates or modules. They must not become dependencies of the core biomech MVP.
- Biomech diagnostics read visual pose state through an explicit binding table. They must not mutate visual mesh vertices, morph weights, or the authoritative skeleton.

Rust API and safety rules:

- Use safe Rust by default with workspace lints set to deny unsafe code unless a later ADR explicitly narrows and justifies an unsafe or FFI module.
- Production code must not use `unwrap`, `expect`, unchecked indexing, or panics for recoverable runtime errors.
- Public APIs return typed errors such as `BiomechLoadError`, `BiomechValidationError`, or `BiomechBuildError`. Do not return `Result<T, String>`.
- Validate once at the asset boundary and convert to constrained internal types. Core biomech algorithms should accept validated/preprocessed models where possible.
- Numeric constants, anthropometric defaults, tolerances, unit scales, solver iteration counts, Bevy labels, and schedule labels must be named constants or typed config values.
- Public structs must use explicit units in field names or docs, for example `height_m`, `mass_kg`, `force_n`, `time_s`, `angle_rad`, `inertia_kg_m2`.
- Every directory under `src/` must include a local `README.md` before or in the same milestone that creates the directory.

Dependency rules:

- Prefer `std`, `glam`, `serde`, `rusqlite`, `thiserror`, and `approx` for the MVP.
- `nalgebra` is allowed only behind an optional feature for matrix solves such as damped least-squares IK. It must not be introduced for simple vector/matrix transforms already covered by `glam`.
- Do not add physics engines, FEM solvers, optimal-control frameworks, BLAS bindings, or FFI dependencies for the MVP.
- New dependencies require a dependency note or ADR covering purpose, owner crate, feature flags, alternatives considered, transitive risk, and removal path.

Verification gates:

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`
- `cargo test --workspace`
- `cargo test --workspace --doc`
- `cargo check --workspace --all-features`
- `cargo check --workspace --no-default-features` once public features exist

Required test coverage:

- Boundary validation tests for invalid mass/height, missing segments, duplicate names, invalid joint parent/child links, invalid limits, non-finite transforms, invalid muscle links, missing contacts, and negative dimensions.
- Golden fixture tests for derived measurements, segment mass fractions, segment COMs, inertia approximations, FK transforms, whole-body COM, balance reports, muscle lengths, and finite-difference moment arms.
- Unit tests for coordinate conventions, local-to-global transform order, support-polygon inclusion, distance-to-polygon edge, joint limit clamping/reporting, and mass normalization.
- Bevy integration smoke test that syncs one visual pose into biomech state, updates diagnostics, and draws overlays without mutating the visual mesh.
- Property or table-driven tests for mass fraction normalization, positive inertia, stable finite differences, and COM remaining finite for valid models.

Milestone write sets:

- Biomech schema and validation: `crates/human_core/src/biomech/types` or `crates/human_biomech/src/types`, validation modules, fixtures, and validation tests only.
- Measurement and mass properties: biomech measurement/mass modules, golden metric fixtures, and unit tests only.
- Kinematics and COM: biomech kinematics/diagnostics modules, FK/COM fixtures, and tests only.
- Joint limits and balance: limit/balance modules, balance fixtures, and tests only.
- Muscle path diagnostics: muscle modules, muscle fixtures, and tests only.
- Bevy overlays: `crates/human_bevy/src/biomech`, viewer app composition, and Bevy overlay smoke tests only.
- Documentation and ADR updates: `docs/plans`, `docs/adr`, crate READMEs, and module READMEs only.

Schema files, diagnostic enums, public facade exports, anthropometric constants, unit conventions, and fixture formats are shared contracts. Change them serially, update all downstream tests in the same change, and record the rationale. Parallel work must avoid overlapping writes to those files.

Before implementation, inspect git status. Do not mix unrelated dirty implementation files into a milestone. Documentation-only untracked files may remain uncommitted while planning, but implementation changes must be reviewable by logical slice.

Re-plan before continuing if any of these occur:

- The biomech schema, unit convention, or coordinate convention must change after tests depend on it.
- A physics engine, FEM solver, optimizer, BLAS/linear-algebra backend, unsafe block, or FFI boundary seems necessary.
- Biomech systems need to mutate visual mesh, morph, or skeleton state.
- A milestone needs to edit more than its planned write set.
- Clinical accuracy, real-time tissue deformation, contact dynamics, or predictive control becomes a near-term requirement.
- Non-project compatibility becomes a requirement instead of optional later validation.

### Bevy Integration Contract

Resources:

```rust
struct ActiveBiomechModel(pub Entity);
struct BiomechOverlaySettings {
    show_segments: bool,
    show_com: bool,
    show_joint_limits: bool,
    show_muscles: bool,
    show_contacts: bool,
}
```

Components:

```rust
struct BiomechInstance { model: Handle<BiomechModelAsset> }
struct BiomechState { q: Vec<f32>, qd: Vec<f32> }
struct BiomechDiagnosticsCache { diagnostics: PoseDiagnostics }
struct BiomechDirty;
```

Systems:

```text
load_biomech_assets
spawn_biomech_instance
sync_visual_pose_to_biomech_state
evaluate_biomech_fk_when_dirty
evaluate_biomech_diagnostics_when_dirty
draw_segment_overlays
draw_com_overlay
draw_muscle_paths
draw_contact_overlay
draw_joint_limit_warnings
```

Rules:

- Biomech systems read visual pose state through an explicit binding table.
- Biomech diagnostics must not mutate visual mesh vertices.
- Tissue or corrective morph experiments must be separate opt-in systems.

### Build Order Gates

1. Subject measurement derivation.
2. Segment mass properties.
3. Joint and coordinate validation.
4. Articulated FK.
5. Segment COM and whole-body COM.
6. Joint limit diagnostics.
7. Balance diagnostics.
8. Muscle path length.
9. Moment-arm finite differences.
10. Bevy overlays.
11. Advanced features: IK fitting, inverse dynamics, forward dynamics, muscle actuation, predictive motion, reduced tissue.

## Biomechanics MVP Data Model

### Subject Measurements

```rust
struct SubjectMeasurements {
    height_m: f32,
    mass_kg: f32,
    shoulder_width_m: f32,
    pelvis_width_m: f32,
    chest_depth_m: f32,
    pelvis_depth_m: f32,
    upper_arm_length_m: f32,
    forearm_length_m: f32,
    hand_length_m: f32,
    thigh_length_m: f32,
    shank_length_m: f32,
    foot_length_m: f32,
}
```

If only height and mass are available, derive missing lengths from simple proportions:

```text
shoulder_width = height * 0.23
pelvis_width = height * 0.17
chest_depth = height * 0.12
pelvis_depth = height * 0.10
upper_arm_length = height * 0.186
forearm_length = height * 0.146
hand_length = height * 0.108
thigh_length = height * 0.245
shank_length = height * 0.246
foot_length = height * 0.152
```

These are engineering defaults, not anatomical truth. They are enough to generate a deterministic model and can be replaced by measured inputs.

### Segment Profile Tables

Anthropometric defaults must be data assets, not hardcoded implementation details. A profile table defines how subject measurements become segment dimensions, masses, centers of mass, and inertia inputs.

```rust
struct SegmentProfileTable {
    name: String,
    entries: Vec<SegmentProfile>,
}

struct SegmentProfile {
    segment_name: String,
    length_source: SegmentLengthSource,
    radius_x_source: SegmentRadiusSource,
    radius_z_source: SegmentRadiusSource,
    mass_fraction: f32,
    com_fraction_from_proximal: f32,
    inertia_shape: InertiaShape,
}

enum SegmentLengthSource {
    Measurement { field: String },
    HeightScale { factor: f32 },
    RestLandmarks { proximal: LandmarkId, distal: LandmarkId },
}

enum SegmentRadiusSource {
    Measurement { field: String, circumference_to_radius: bool },
    HeightScale { factor: f32 },
    FractionOfLength { factor: f32 },
}

enum InertiaShape {
    Ellipsoid,
    Box,
    CapsuleApproximation,
}
```

Processing rules:

1. Resolve measured values first.
2. Fall back to rest landmarks if measurements are absent.
3. Fall back to height-scaled defaults if neither measured values nor landmarks are available.
4. Normalize all active segment `mass_fraction` values so total segment mass equals `subject.mass_kg`.
5. Report every fallback path in diagnostics so users know which metrics are measured and which are estimated.

### Segment Model

```rust
struct BodySegment {
    name: String,
    parent: Option<SegmentId>,
    joint: JointId,
    length_m: f32,
    radius_x_m: f32,
    radius_z_m: f32,
    mass_kg: f32,
    local_com: Vec3,
    inertia_local: Mat3,
}
```

Default body mass fractions:

```text
head_neck: 0.081
torso: 0.497
upper_arm_each: 0.028
forearm_each: 0.016
hand_each: 0.006
thigh_each: 0.100
shank_each: 0.0465
foot_each: 0.0145
```

The fractions sum to approximately `1.0`. Normalize them after loading so custom segment sets still match total subject mass.

Default center-of-mass fraction along each segment's local `+Y` axis from proximal joint to distal joint:

```text
head_neck: 0.50
torso: 0.50
upper_arm: 0.436
forearm: 0.430
hand: 0.506
thigh: 0.433
shank: 0.433
foot: 0.50
```

Approximate every segment as an ellipsoid or capsule-like cylinder for inertia. MVP can use a solid ellipsoid approximation:

```text
Ixx = 1/5 * mass * (radius_z^2 + length^2)
Iyy = 1/5 * mass * (radius_x^2 + radius_z^2)
Izz = 1/5 * mass * (radius_x^2 + length^2)
```

This is not exact for limbs, but it is deterministic and stable.

Physical consistency checks:

- Total segment mass must equal `subject.mass_kg` within `BIOMECH_MASS_EPSILON` after mass-fraction normalization.
- Every inertia tensor must be symmetric and positive definite.
- Every segment COM should lie inside or near the segment's approximation volume.
- Sampling valid joint-limit poses must keep all segment transforms finite.
- Any later generalized inertia or mass-matrix approximation must be positive definite for sampled valid poses. If it is not, report the sampled pose, coordinate values, and smallest eigenvalue.

### Joint Model

```rust
enum JointKind {
    Fixed,
    Hinge { axis: Vec3 },
    Ball,
    Euler3,
}

struct JointLimit {
    min_rad: Vec3,
    max_rad: Vec3,
}

struct BiomechJoint {
    name: String,
    parent_segment: Option<SegmentId>,
    child_segment: SegmentId,
    kind: JointKind,
    rest_parent_to_joint: Mat4,
    rest_child_to_joint: Mat4,
    limit: JointLimit,
}
```

Default MVP limits:

```text
neck: [-45, -45, -60] to [45, 45, 60] degrees
shoulder: [-120, -90, -90] to [120, 120, 90] degrees
elbow hinge: 0 to 150 degrees
wrist: [-60, -45, -60] to [60, 45, 60] degrees
hip: [-120, -45, -45] to [45, 45, 45] degrees
knee hinge: 0 to 150 degrees
ankle: [-45, -30, -30] to [45, 30, 30] degrees
```

Store limits in radians in code. Degrees in docs are for readability.

### Pose Diagnostics

The first useful biomechanics system is diagnostic, not a solver.

```rust
struct PoseDiagnostics {
    whole_body_com: Vec3,
    segment_coms: Vec<Vec3>,
    total_mass_kg: f32,
    joint_limit_violations: Vec<JointLimitViolation>,
    balance: BalanceDiagnostic,
}
```

COM calculation:

```rust
fn whole_body_com(segment_global: &[Mat4], segments: &[BodySegment]) -> Vec3 {
    let mut weighted = Vec3::ZERO;
    let mut total = 0.0;
    for (global, segment) in segment_global.iter().zip(segments) {
        let com_world = global.transform_point3(segment.local_com);
        weighted += com_world * segment.mass_kg;
        total += segment.mass_kg;
    }
    weighted / total.max(MIN_SEGMENT_MASS)
}
```

Balance check:

1. Project COM onto the ground plane: `[com.x, 0, com.z]`.
2. Build a support polygon from foot contact points.
3. If the projected COM is inside the polygon, the pose is balanced.
4. If outside, report distance to polygon edge.
5. If no foot contacts exist, report `NoSupportContacts`.

MVP foot contact points can be four corners per foot:

```text
heel_left, heel_right, toe_left, toe_right
```

### Muscle Path MVP

Muscles are geometric paths, not force-producing actuators in the first version.

```rust
struct MusclePath {
    name: String,
    origin_segment: SegmentId,
    insertion_segment: SegmentId,
    points: Vec<MusclePoint>,
    rest_length_m: f32,
}

enum MusclePoint {
    SegmentLocal { segment: SegmentId, point: Vec3 },
    ViaPoint { segment: SegmentId, point: Vec3 },
}
```

Path length:

```rust
fn muscle_length(path: &MusclePath, segment_global: &[Mat4]) -> f32 {
    let mut world_points = Vec::new();
    for point in &path.points {
        match point {
            MusclePoint::SegmentLocal { segment, point } |
            MusclePoint::ViaPoint { segment, point } => {
                world_points.push(segment_global[segment.0].transform_point3(*point));
            }
        }
    }
    world_points.windows(2).map(|w| w[0].distance(w[1])).sum()
}
```

Moment-arm approximation for a joint coordinate:

```text
moment_arm = -(length(q + epsilon) - length(q - epsilon)) / (2 * epsilon)
```

Use this finite-difference approximation for diagnostics only. It is slow but simple and self-contained.

### Muscle Attachment Descriptors

Muscle attachment points should be authorable directly, but the asset format should also support parametric local descriptors so symmetric prototype muscles can be generated from segment dimensions.

```rust
struct MuscleAttachmentDescriptor {
    segment: SegmentId,
    length_fraction_from_proximal: f32,
    radial_angle_rad: f32,
    radial_x_scale: f32,
    radial_z_scale: f32,
    offset_m: Vec3,
}
```

Descriptor to segment-local point:

```text
y = segment.length_m * length_fraction_from_proximal
x = cos(radial_angle_rad) * segment.radius_x_m * radial_x_scale
z = sin(radial_angle_rad) * segment.radius_z_m * radial_z_scale
point_local = [x, y, z] + offset_m
```

Rules:

- Clamp `length_fraction_from_proximal` to `[0, 1]`.
- Clamp radial scales to non-negative values.
- Store the resolved point in diagnostics so generated attachment positions are inspectable.
- Mirrored left/right attachments should mirror the radial angle or local X coordinate through an explicit `BodySide` rule, not by string replacement.

### Muscle Length Surrogates

Finite-difference moment arms are sufficient for MVP diagnostics. A later fast path can store polynomial or table-based surrogates for muscle-tendon length over the coordinates a muscle spans.

```rust
struct MuscleLengthSurrogate {
    muscle: MuscleId,
    coordinates: Vec<CoordinateId>,
    basis: SurrogateBasis,
    coefficients: Vec<f32>,
    length_rms_error_m: f32,
    moment_arm_rms_error_m: f32,
}

enum SurrogateBasis {
    Polynomial { order: usize },
    RegularGrid { samples_per_axis: Vec<usize> },
}
```

Surrogate acceptance:

- Fit both length and `-d(length)/dq` samples.
- Store RMS error for length and moment arm.
- Do not use a surrogate for diagnostics if `length_rms_error_m` or `moment_arm_rms_error_m` exceeds the configured threshold.
- Keep the direct geometric path as the validation baseline.

### Optional Reduced Soft-Body Track

If a soft-body experiment is needed before a full continuum model, implement a small position-based dynamics layer instead of finite elements.

```rust
struct TissueParticle {
    position: Vec3,
    previous_position: Vec3,
    inverse_mass: f32,
}

struct DistanceConstraint {
    a: ParticleId,
    b: ParticleId,
    rest_length: f32,
    stiffness: f32,
}

struct AttachmentConstraint {
    particle: ParticleId,
    bone: BoneId,
    local_point: Vec3,
    stiffness: f32,
}
```

PBD update:

```text
for each particle:
    velocity = position - previous_position
    previous_position = position
    position += velocity + gravity * dt^2

repeat solver_iterations:
    project distance constraints
    project bone attachment constraints
    project collision/contact constraints later
```

This reduced model is not anatomy. It is a sandbox for testing how simulated displacements could drive surface offsets or corrective morphs.

## Design Boundary

The project should keep these models separate:

- `VisualHumanModel`: render mesh, morph targets, skeleton, skin weights, materials, poses.
- `BiomechHumanModel`: subject measurements, rigid segments, joints, mass properties, muscle paths, validation data.
- `DynamicsModel`: generalized coordinates, speeds, mobilizers, constraints, forces, contacts, and integration/assembly settings.
- `PredictiveMotionModel`: trajectories, controls, activation curves, force histories, contact events, and objective/constraint definitions.
- `ContinuumTissueModel`: volumetric tissue regions, materials, constraints, fiber fields, and deformation outputs.
- `BindingModel`: mappings between visual bones/landmarks and biomechanical segments/frames.

The visual model answers: what should the human look like?

The biomechanical model answers: what are the body segments, masses, joint frames, constraints, and muscle paths?

The dynamics model answers: how do those segments move under generalized coordinates, constraints, contacts, and forces?

The predictive motion model answers: what motion, controls, and muscle activations satisfy the biomechanical constraints and movement objective?

The continuum tissue model answers: how should internal tissue deform under pose, activation, loads, constraints, and material behavior?

The binding model answers: how do the coordinate systems and deformation results line up?

This separation prevents the biomechanics layer from making the renderer brittle. It also allows the project to support multiple biomechanical profiles without changing the core visual mesh importer.

## Deformation Philosophy

The visual runtime starts with a fixed-topology deformation model:

```text
morph sliders + skeleton pose
  -> vertex deltas + skinning
  -> visible surface mesh
```

The advanced biomechanics track adds a physical deformation model:

```text
pose + activation + constraints + material properties
  -> tissue simulation or reduced tissue model
  -> surface displacement
  -> render mesh update or baked corrective morph
```

These should coexist. Blend shapes are fast, easy to store, and compatible with Bevy rendering. Biomechanical simulation is slower and harder, but can produce deformations that are more physically meaningful. The practical target is a hybrid system where simulation can drive, generate, validate, or replace blend shapes for specific regions.

Early versions should keep blend shapes as the default deformation path. Continuum tissue simulation should be optional, region-limited, and initially offline or reduced.

Predictive motion sits beside both paths:

```text
subject model + joints + muscle-tendon units + contact + objective
  -> offline optimal control or trajectory optimization
  -> pose clips + activation curves + force/contact diagnostics
  -> Bevy playback, validation overlays, and optional corrective morph drivers
```

This makes the optimizer a content and validation tool, not a required realtime dependency.

## Simulation Levels

The biomechanical system should be built in levels. Each level should be useful on its own.

## Level 0: Landmarks And Debug Overlays

This is the lowest-risk first step.

Inputs:

- Visual skeleton rest pose.
- Named body landmarks.
- Optional marker vertex groups.
- Optional manually authored landmark offsets.

Outputs:

- Joint frame gizmos.
- Segment axes.
- Centerline/spine landmarks.
- Muscle attachment landmarks.
- Measurement lines for height, limb length, shoulder width, pelvis width, and circumferences.

Implementation:

- Add Bevy gizmos for segment frames and landmark points.
- Add a diagnostics panel showing computed segment lengths and obvious invalid values.
- Store landmarks in asset files, not hardcoded Rust when possible.
- Use the visual skeleton as the initial source of truth for bone transforms.

Why this matters:

- It makes rig/biomech alignment visible early.
- It creates the debug infrastructure needed for later mass, joint, and muscle work.
- It avoids prematurely committing to a full physics implementation.

## Level 1: Anthropometric Subject Model

This level introduces user-entered body measurements as structured data.

Core type:

```rust
pub struct AnthropometricSubject {
    pub height_m: f32,
    pub mass_kg: f32,
    pub neck_circumference_m: Option<f32>,
    pub chest_depth_m: Option<f32>,
    pub pelvis_depth_m: Option<f32>,
    pub shoulder_width_m: Option<f32>,
    pub upper_arm_circumference_m: Option<f32>,
    pub forearm_circumference_m: Option<f32>,
    pub thigh_circumference_m: Option<f32>,
    pub calf_circumference_m: Option<f32>,
    pub hand_width_m: Option<f32>,
    pub hand_thickness_m: Option<f32>,
}
```

Derived output:

```rust
pub struct SegmentMetrics {
    pub segment: SegmentId,
    pub length_m: f32,
    pub radius_x_m: f32,
    pub radius_y_m: f32,
    pub mass_kg: f32,
    pub center_of_mass_local: Vec3,
    pub inertia_tensor_local: Mat3,
}
```

Practical implementation:

- Start with a small number of segments: pelvis, torso, head, upper arms, forearms, hands, thighs, shanks, feet.
- Derive lengths from skeleton rest pose where available.
- Use anthropometric measurements as overrides or validation constraints.
- Use published segment mass percentages as configurable tables.
- Approximate inertia from capsules, boxes, or ellipsoids.
- Report mismatches instead of silently forcing the visual mesh to match every measurement.

Important rule:

The subject model should not directly edit mesh vertices. It should drive diagnostics and optional fitting. Mesh shape changes remain controlled by morph targets.

## Level 2: Rigid-Body Biomechanical Skeleton

This level creates a dynamics-oriented body model.

Core types:

```rust
pub struct RigidBodySegment {
    pub id: SegmentId,
    pub parent_joint: Option<JointId>,
    pub child_joints: Vec<JointId>,
    pub rest_transform: Transform,
    pub mass_kg: f32,
    pub center_of_mass_local: Vec3,
    pub inertia_tensor_local: Mat3,
    pub collision_shape: SegmentCollisionShape,
}

pub struct BiomechJoint {
    pub id: JointId,
    pub parent: SegmentId,
    pub child: SegmentId,
    pub parent_frame: Transform,
    pub child_frame: Transform,
    pub degrees_of_freedom: JointDof,
    pub limits: JointLimits,
    pub model: JointModel,
}

pub enum JointModel {
    Fixed,
    Hinge { axis: Vec3 },
    Ball,
    Universal { axis_a: Vec3, axis_b: Vec3 },
    Slider { axis: Vec3 },
    Planar,
    Free,
    FunctionBased { coordinate_count: usize, functions: Vec<JointCoordinateFunction> },
}
```

Data flow:

1. Load visual skeleton rest pose.
2. Map visual bones to biomechanical segments.
3. Compute segment frames from rest pose and landmarks.
4. Apply subject-derived dimensions and mass properties.
5. Build joint constraints and joint limits.
6. Validate topology, transforms, masses, and inertia tensors.

Joint profiles:

- Ball joint: shoulder, hip.
- Hinge joint: elbow, knee, ankle/toe in early versions.
- Limited 3-axis joint: neck, wrist, spine segments.
- Fixed joint: helper frames and sensor frames.
- Function-based joint: later knee, shoulder, spine, or scapula models where translation/rotation is coupled to one or more coordinates.

Implementation choices:

- Keep the internal model engine-agnostic in `human_core` or a new `human_biomech` crate.
- Use Bevy only for visualization, interaction, and optional runtime execution.
- Store generalized-coordinate metadata separately from visual bone animation channels.

Validation:

- Total segment mass equals subject mass within tolerance.
- No negative or zero segment lengths.
- Inertia tensors are symmetric and positive definite.
- Joint frames are finite and reasonably aligned with segment axes.
- Segment center of mass lies inside or near the segment collision approximation.
- Left/right paired segments are symmetric unless asymmetry is explicitly provided.
- Function-based joints evaluate finite transforms across their supported coordinate ranges.
- Dynamics skeleton topology maps back to the visual rig without cycles or missing parent segments.

## Level 3: Muscle Attachment And Muscle Path Model

This level adds muscle geometry without yet requiring full muscle-force simulation.

Core types:

```rust
pub struct MuscleAttachment {
    pub segment: SegmentId,
    pub local_position: Vec3,
}

pub struct MusclePath {
    pub id: MuscleId,
    pub origin: MuscleAttachment,
    pub insertion: MuscleAttachment,
    pub via_points: Vec<MuscleAttachment>,
    pub obstacles: Vec<MusclePathObstacle>,
    pub side: BodySide,
    pub group: MuscleGroup,
}

pub enum MusclePathObstacle {
    ViaPoint(MuscleAttachment),
    WrappingSphere { segment: SegmentId, center_local: Vec3, radius_m: f32 },
    WrappingCylinder { segment: SegmentId, transform_local: Transform, radius_m: f32, half_length_m: f32 },
}
```

Practical implementation:

- Start with a small muscle set: biceps, triceps, quadriceps/rectus femoris, hamstrings/biceps femoris, gastrocnemius, tibialis anterior, erector spinae, rectus abdominis.
- Store attachment data in SQLite records.
- Author attachments relative to biomechanical segments, not mesh vertices.
- Render muscle paths as Bevy debug curves/tubes.
- Compute current muscle-tendon length from posed segment transforms.
- Compute moment-arm approximations later by finite differences or analytic joint geometry.
- Treat via points and wrapping surfaces as first-class path data, not only rendering helpers.
- Keep the first path solver simple: straight segments through via points, then add wrapping surfaces later.

What this does not do initially:

- It does not deform the visual skin.
- It does not bulge muscles under contraction.
- It does not simulate fascia, fat, or sliding tissue.

Why it is still useful:

- It gives visible biomechanical landmarks.
- It lets us inspect how pose affects muscle path length.
- It prepares the data model for future actuation or pose plausibility checks.
- It creates a path representation that later tooling can reuse for cable or muscle path systems.

## Level 4: Muscle-Tendon Actuation

This level introduces muscle forces. It should come after the rigid-body model and muscle paths are stable. It does not directly deform the skin. It produces forces, torques, activation signals, and diagnostics that can be consumed by rigid-body dynamics, continuum tissue simulation, or corrective morph generation.

Possible model:

```rust
pub struct MuscleTendonUnit {
    pub path: MusclePath,
    pub max_isometric_force_n: f32,
    pub optimal_fiber_length_m: f32,
    pub tendon_slack_length_m: f32,
    pub pennation_angle_rad: f32,
    pub activation: f32,
}
```

Runtime computations:

1. Calculate muscle path length from current segment transforms.
2. Estimate fiber/tendon state.
3. Compute force from activation, force-length, and force-velocity terms.
4. Convert line-of-action forces into joint torques.
5. Expose activation and force outputs to later tissue deformation systems.
6. Apply torques to a physics backend or use them as diagnostics.

Recommended scope:

- Start with quasi-static diagnostics.
- Avoid full forward dynamics until rigid-body validation and joint limits are dependable.
- Treat muscle constants as profile data, not hardcoded source code.

Output diagnostics:

- Muscle length.
- Normalized muscle length.
- Activation value.
- Estimated force.
- Estimated torque contribution per joint.
- Warnings for unrealistic stretch or compression.
- Optional generalized-force contribution if a dynamics backend is active.

## Level 5: Dynamics Assembly And IK Diagnostics

This level adds assembly: solving for generalized coordinates that satisfy constraints and best match observations. It can be implemented before full forward dynamics because it is useful for fitting and validation.

Core types:

```rust
pub struct AssemblyProblem {
    pub biomech_profile: BiomechProfileId,
    pub editable_coordinates: Vec<GeneralizedCoordinateId>,
    pub coordinate_limits: Vec<CoordinateLimit>,
    pub hard_constraints: Vec<AssemblyConstraint>,
    pub weighted_goals: Vec<AssemblyGoal>,
}

pub enum AssemblyGoal {
    MatchLandmark { landmark: LandmarkId, target_position: Vec3, weight: f32 },
    MatchSegmentOrientation { segment: SegmentId, target_rotation: Quat, weight: f32 },
    StayNearPose { pose: PoseId, weight: f32 },
}
```

Practical implementation:

- Start with diagnostics that evaluate constraint error for the current visual pose.
- Add a simple local solver only after the coordinate and joint-limit data is stable.
- Use assembly to fit landmarks, marker observations, or imported motion frames to the biomechanical skeleton.
- Keep solved coordinates separate from visual animation channels, then retarget back through bindings.
- Use this for validation and tooling before using it for realtime interaction.

Where this helps:

- Fitting a visual pose to a stricter biomechanical skeleton.
- Checking whether imported motion violates joint constraints.
- Solving small IK problems from landmarks or sensors.
- Producing cleaner input for offline dynamics or predictive-motion tooling.

## Level 6: Predictive Motion And Optimal Control

This level adds the concept that motion can be generated from a subject model, muscle-tendon actuators, contact, and objective functions. This should be treated as an offline or tool-mode feature first. It should not be required for posing or rendering a character in Bevy.

Core types:

```rust
pub struct MotionOptimizationProblem {
    pub subject: AnthropometricSubject,
    pub biomech_profile: BiomechProfileId,
    pub initial_state: BiomechState,
    pub bounds: MotionBounds,
    pub objective_terms: Vec<ObjectiveTerm>,
    pub constraints: Vec<MotionConstraint>,
    pub contacts: Vec<ContactModelId>,
}

pub struct MotionTrajectory {
    pub sample_rate_hz: f32,
    pub joint_positions: Vec<JointPoseFrame>,
    pub joint_velocities: Option<Vec<JointVelocityFrame>>,
    pub muscle_activations: Option<Vec<MuscleActivationFrame>>,
    pub muscle_forces: Option<Vec<MuscleForceFrame>>,
    pub contacts: Option<Vec<ContactEventFrame>>,
}

pub enum ObjectiveTerm {
    MinimizeMuscleActivation { weight: f32 },
    MinimizeMetabolicEnergy { weight: f32 },
    MinimizeJointAcceleration { weight: f32 },
    TrackReferenceMotion { weight: f32, clip: MotionClipId },
    MatchTargetSpeed { speed_mps: f32, weight: f32 },
}
```

Practical implementation:

- Start with trajectory import and playback before building an optimizer.
- Support importing a project-native trajectory format first.
- Store joint trajectories, activation curves, force curves, and contact events as assets.
- Map imported joint names through rig profiles instead of assuming visual bone names match biomechanical model names.
- Use the trajectory to drive the visual skeleton through the same pose/skinning path as any other animation clip.
- Draw activation, force, and contact overlays in Bevy while the clip plays.
- Add validation that flags joint-limit violations, invalid contact timing, impossible speeds, and missing muscle mappings.
- Allow trajectories to store generalized coordinates in addition to visual bone transforms.
- Support imported external-solver diagnostics such as generalized speeds, accelerations, reaction forces, and constraint residuals as optional data streams.

Polynomial surrogate path:

1. Sample muscle-tendon lengths and moment arms from an anatomy dataset.
2. Fit polynomial or table-based functions over relevant joint coordinates.
3. Store those coefficients as project assets.
4. Use them for fast path-length, velocity, and torque diagnostics.
5. Compare surrogate output against golden samples before trusting it in an optimizer.

Optimizer path:

1. Define a small problem first, such as a 2D leg, elbow flexion, or squat-like lower-body motion.
2. Use bounded joint positions, velocities, muscle activations, and muscle forces as state.
3. Add collocation, shooting, or another direct transcription method only in an offline crate or external tool.
4. Save the solved trajectory in `biomech_trajectories`.
5. Keep Bevy responsible for playback and inspection, not nonlinear optimization.

What this does not do initially:

- It does not replace hand-authored pose controls.
- It does not replace the animation system.
- It does not deform the surface mesh by itself.
- It does not require realtime muscle simulation.

Where this is useful:

- Generating physically plausible gait and exercise clips.
- Validating whether a pose sequence violates joint limits or muscle capacity.
- Producing muscle activation curves that can drive corrective morphs.
- Testing contact timing, center-of-mass behavior, and balance.

## Level 7: Continuum Tissue Deformation

This level adds the concept that body deformation can be produced by simulated tissue volumes instead of only by blend shape deltas. It should be considered advanced and optional.

This is the first level where biomechanical simulation can become an alternative to hand-authored blend shapes.

Core types:

```rust
pub struct VolumetricTissueMesh {
    pub nodes: Vec<Vec3>,
    pub elements: Vec<TissueElement>,
    pub regions: Vec<TissueRegion>,
}

pub struct TissueRegion {
    pub id: TissueRegionId,
    pub name: String,
    pub material: MaterialModelId,
    pub element_set: Vec<ElementId>,
}

pub enum TissueElement {
    Tet4([NodeId; 4]),
    Tet10([NodeId; 10]),
    Hex8([NodeId; 8]),
}

pub enum MaterialModel {
    LinearElastic { youngs_modulus_pa: f32, poisson_ratio: f32 },
    NeoHookean { shear_modulus_pa: f32, bulk_modulus_pa: f32 },
    AnisotropicFiber { matrix: MaterialModelId, fiber_field: FiberFieldId },
    ActiveMuscle { passive: MaterialModelId, activation_source: MuscleId },
    TendonLike { fiber_field: FiberFieldId },
}

pub struct FiberField {
    pub id: FiberFieldId,
    pub samples: FiberFieldSamples,
}

pub enum BoundaryCondition {
    BoneAttachment(BoneAttachment),
    PrescribedMotion(PrescribedMotion),
    SlidingContact(SlidingContact),
    PressureLoad(PressureLoad),
}
```

Data flow:

1. Select a body region, such as upper arm, shoulder, abdomen, thigh, or face.
2. Build or load a volumetric mesh for that region.
3. Partition the volume into tissue regions such as muscle, fat, tendon, and skin-support tissue.
4. Bind parts of the volume to bones using boundary conditions.
5. Add fiber directions for anisotropic muscle and tendon behavior.
6. Drive the region from pose, muscle activation, or external constraints.
7. Solve a tissue deformation step.
8. Transfer the solved displacement to the visible surface mesh.

Practical implementation:

- Start with local regions, not the whole body.
- Prefer offline or reduced simulation before attempting real-time runtime simulation.
- Use simple material models first, such as linear elastic or neo-Hookean tissue approximations.
- Add anisotropic fiber models after the volume and binding pipeline is validated.
- Add active muscle materials only after passive deformation behaves predictably.
- Keep tissue simulation state separate from visual morph target state.

Important non-goals:

- Do not require a volumetric tissue mesh for the basic character runtime.
- Do not try to tetrahedralize every generated character during the first implementation.
- Do not treat a finite element solver as a replacement for skeleton posing.
- Do not make all surface vertices depend on simulation. Most vertices should still use the faster visual path.

Where this is useful:

- Elbow/upper-arm bulging and crease behavior.
- Shoulder and chest deformation under arm motion.
- Abdomen and torso soft-tissue motion.
- Breast and glute deformation.
- Face and neck soft-tissue deformation.
- Offline generation of physically informed corrective morphs.

## Level 8: Surface Embedding And Displacement Transfer

This level defines how simulated tissue deformation affects the visible mesh.

Core types:

```rust
pub struct SurfaceEmbedding {
    pub render_vertex: VertexId,
    pub tissue_element: ElementId,
    pub barycentric_or_shape_weights: Vec<f32>,
}

pub struct TissueSimulationResult {
    pub node_displacements: Vec<Vec3>,
    pub element_stress: Option<Vec<Mat3>>,
    pub element_strain: Option<Vec<Mat3>>,
    pub convergence: SimulationConvergence,
}

pub enum SurfaceTransferMode {
    DirectDisplacement,
    WeightedRegionDisplacement,
    CorrectiveMorphBake,
    DiagnosticOnly,
}
```

Transfer process:

1. Bind each affected render vertex to a point inside a tissue element.
2. Solve or evaluate the tissue model.
3. Interpolate the tissue node displacements at the embedded point.
4. Apply that displacement to the render vertex, either directly or as a generated morph delta.
5. Blend with standard skinning and visual morphs according to a region mask.

Design constraints:

- Store embedding data as assets so it can be regenerated and tested.
- Keep region masks explicit. A tissue simulation should only affect vertices that were intentionally bound.
- Preserve the base visual topology and vertex order.
- Support diagnostic overlays that show embedded vertices, failed bindings, and displacement magnitude.
- Allow the transfer to produce baked morph targets for fast runtime use.

Failure handling:

- If a render vertex cannot be embedded, leave it on the standard visual path and report it.
- If a simulation fails to converge, keep the last valid result or fall back to the baked morph.
- If displacement exceeds a region threshold, flag it as invalid instead of corrupting the render mesh.

## Level 9: Corrective Morph Baking From Simulation

This level uses biomechanical simulation to generate fixed-topology deformation data.

This is the most practical way to use continuum tissue concepts without requiring real-time finite element simulation.

Bake process:

1. Define a set of driver states: joint angles, pose combinations, muscle activations, or subject measurements.
2. For each driver state, solve a tissue deformation problem or reduced tissue approximation.
3. Transfer the tissue displacement to the visual surface mesh.
4. Store the resulting vertex deltas as a corrective morph target.
5. At runtime, evaluate the corrective morph from the same drivers.

Example:

- Elbow flexion plus biceps activation generates a biceps bulge and elbow crease morph.
- Knee flexion generates knee crease and calf displacement morphs.
- Shoulder abduction generates deltoid, pectoralis, and armpit correction morphs.
- Torso bend generates abdomen compression and back stretch morphs.

Runtime model:

```text
current pose + activation values
  -> corrective morph weights
  -> generated vertex deltas
  -> standard Bevy mesh update path
```

This keeps runtime rendering simple while allowing the source of the corrective shapes to be physically informed.

## Level 10: Real-Time Reduced Tissue Models

This level is optional research. It tries to approximate continuum deformation cheaply enough for interactive use.

Possible approaches:

- Coarse tetrahedral cages around selected regions.
- Position-based dynamics for soft tissue.
- Shape-matching clusters.
- Modal deformation bases generated offline.
- Neural or regression models trained from offline simulation outputs.
- Runtime interpolation over a precomputed pose/activation sample set.

Recommended path:

- Start with baked corrective morphs.
- Add reduced models only for regions where baked morphs are insufficient.
- Keep the reduced model deterministic and bounded.
- Make every reduced model optional per body region.

## Coordinate Systems And Binding

The biomechanics layer needs explicit coordinate conversion.

Required spaces:

- Mesh/object space: base mesh vertex coordinates.
- Visual skeleton rest space: visual rig rest transforms.
- Visual pose space: current animated bone transforms.
- Biomechanical segment local space: segment COM, inertia, landmarks, attachments.
- Tissue rest space: undeformed volumetric tissue node coordinates.
- Tissue current space: solved or reduced tissue node coordinates after deformation.
- Material/fiber local space: per-element directions for anisotropic tissue behavior.
- World space: Bevy scene transforms.

Binding data:

```rust
pub struct SegmentBinding {
    pub segment: SegmentId,
    pub visual_bone: BoneId,
    pub segment_to_bone_rest: Transform,
    pub landmark_bindings: Vec<LandmarkBinding>,
}

pub struct TissueBinding {
    pub tissue_region: TissueRegionId,
    pub driving_segments: Vec<SegmentId>,
    pub bone_attachments: Vec<BoneAttachment>,
    pub surface_embeddings: Vec<SurfaceEmbedding>,
}
```

Binding rules:

- A biomechanical segment can map to one visual bone, multiple visual bones, or a helper frame.
- Segment transforms should be computed from rest-pose data and stable landmark definitions.
- Tissue bindings should be defined per region so local simulations do not accidentally affect the whole body.
- Surface embeddings should be regenerated whenever the tissue mesh or visual topology changes.
- Bindings should be serializable and testable.
- No code should assume visual bone names are universal; use rig profiles.

## Data Assets

Suggested asset files:

```text
assets/biomech/
  profiles/
    default_biomech_profiles.human.sqlite
  samples/
    walking_analysis.human.sqlite
    elbow_flexion_tissue.human.sqlite
```

Profile database contents:

- Segment list.
- Segment-to-bone bindings.
- Joint definitions.
- Default joint limits.
- Generalized coordinate definitions.
- Mobilizer/joint-model definitions.
- Constraint and assembly goal definitions.
- Mass percentage table.
- Inertia approximation strategy.
- Muscle attachment sets.
- Optional tissue region definitions.
- Optional tissue material definitions.
- Optional fiber fields.
- Optional surface embeddings.
- Optional generated corrective morph metadata.
- Optional motion trajectories, activation curves, force curves, and contact events.
- Optional moment-arm and muscle-length surrogate coefficients.
- Optional optimization objective and constraint definitions.
- Validation tolerances.

The project should also avoid baking solver-specific assumptions into the asset layout. The asset model should describe tissue regions, materials, constraints, and embeddings.

The same rule applies to motion optimization. The project should own generic trajectory, activation, force, contact, objective, and constraint data.

The same rule also applies to dynamics. The project should own generic segment, joint, coordinate, constraint, force, cable, contact, and assembly-goal data.

## Bevy Integration

The Bevy integration should be an inspection and runtime layer over engine-agnostic data.

Components:

```rust
pub struct BiomechModelHandle(pub Handle<BiomechProfile>);
pub struct BiomechSegmentEntity(pub SegmentId);
pub struct BiomechJointEntity(pub JointId);
pub struct BiomechMuscleEntity(pub MuscleId);
pub struct DynamicsStateEntity(pub DynamicsStateId);
pub struct AssemblyGoalEntity(pub AssemblyGoalId);
pub struct MotionTrajectoryEntity(pub MotionTrajectoryId);
pub struct ContactEventEntity(pub ContactEventId);
pub struct TissueRegionEntity(pub TissueRegionId);
pub struct SurfaceEmbeddingEntity(pub TissueRegionId);
```

Systems:

- Load biomechanical profile assets.
- Build segment/joint entities from a visual character.
- Update biomechanical segment transforms from visual pose transforms.
- Evaluate dynamics coordinate mappings and joint constraint diagnostics.
- Evaluate assembly/IK diagnostics for landmarks, orientations, and trajectory frames.
- Load trajectory assets and retarget joint curves through rig profiles.
- Play trajectory clips through the normal visual pose/skinning path.
- Draw segment axes, COM points, joint limits, and muscle paths.
- Draw muscle activation, force, center-of-mass, and contact overlays during trajectory playback.
- Draw tissue regions, fiber directions, embedded vertices, and displacement magnitude overlays.
- Evaluate reduced tissue models for enabled regions.
- Apply direct tissue displacement or generated corrective morph deltas to the visual mesh.
- Run validation after morph or pose changes.
- Save biomechanical model, state, trajectory, and tissue-result records in `.human.sqlite`.

UI:

- Subject measurement editor.
- Segment table showing length, mass, COM, inertia validity.
- Joint table showing current angle, limits, and warnings.
- Dynamics table showing generalized coordinates, speeds, constraint residuals, and state validity.
- Muscle table showing current path length and normalized length.
- Motion table showing current clip, speed, phase, contact state, activation range, and validation warnings.
- Tissue table showing region, material, node/element count, driver state, and convergence status.
- Toggle overlays for skeleton, COM, collision approximation, landmarks, muscles, trajectory traces, contact events, tissue volumes, fiber fields, embedded vertices, and displacement fields.

## Dynamics Solver Boundary

The Bevy app must remain able to load, pose, skin, and render a character without C++ dynamics libraries or offline solver installations.

Project-owned abstractions:

- Rigid-body segment definitions.
- Generalized coordinate definitions.
- Mobilizer or joint-model descriptors.
- Constraint descriptors.
- Force descriptors.
- Cable or muscle path descriptors.
- Contact descriptors.
- Assembly goal descriptors.
- Dynamics state histories.
- Solver diagnostic reports.

Possible implementations behind those abstractions:

- Diagnostic-only dynamics with no solver.
- A simple in-project kinematic evaluator.
- Project-owned trajectory result assets for inverse-dynamics-like diagnostics, forward-dynamics experiments, and assembly checks.
- Hand-authored or generated dynamics result streams as trajectory diagnostics.

The practical first implementation is data modeling and diagnostics. Full multibody integration should come later, and likely outside the core runtime. Any solver experiment should read project assets and write solved result assets.

## Predictive Motion Boundary

The visual runtime must remain able to load, pose, skin, and render a character without optimization or simulation stacks.

Project-owned abstractions:

- Motion trajectories.
- Joint state histories.
- Muscle activation histories.
- Muscle force histories.
- Contact event histories.
- Objective descriptors.
- Constraint descriptors.
- Moment-arm and muscle-length surrogate descriptors.
- Validation reports.

Possible implementations behind those abstractions:

- Project-owned trajectory assets generated by tools or authored by users.
- Hand-authored or captured animation clips with biomechanical diagnostics.
- A simple in-project trajectory checker.
- A small offline Rust optimizer for limited problems.
- A small optimizer tool that reads project assets and writes solved trajectories.

The practical first implementation is load/playback/validate. Optimization should come later, and only in a tooling layer. A solved trajectory should become normal project data that Bevy can replay and inspect.

## Internal Dynamics Snapshot Assets

Internal dynamics snapshots are SQLite records that capture the simplified rigid-body view of the biomechanical model for diagnostics and replay.

Snapshot data:

- Links from `RigidBodySegment`.
- Joints from `BiomechJoint`.
- Mass and inertia from `SegmentMetrics`.
- Collision geometry from simple segment approximations.
- Muscle attachment frames as fixed helper frames or project metadata.
- Optional diagnostic shapes for Bevy overlays.

Non-goals for early dynamics snapshots:

- Saving the skinned visual surface.
- Saving deforming muscle meshes.

Validation:

- Round-trip the `biomech_states` or snapshot fixture through the project SQLite loader.
- Check link/joint counts.
- Check total mass.
- Check inertial values exist and are finite.
- Check parent/child topology is connected.

## Advanced Dynamics Result Assets

Advanced dynamics result assets store high-fidelity analysis outputs in SQLite records. They keep advanced dynamics concepts such as complex mobilizers, muscle paths, marker fitting, and musculoskeletal analysis separate from the live visual runtime.

Input data:

- Rigid bodies from `RigidBodySegment`.
- Mobilizers from `BiomechJoint` and `JointModel`.
- Generalized coordinate names, ranges, and defaults.
- Mass, center of mass, and inertia from `SegmentMetrics`.
- Constraints and prescribed motions where supported.
- Muscle/cable paths from `MusclePath`, via points, and wrapping obstacles.
- Contact geometry from simplified segment or foot contact profiles.
- Marker/landmark frames for IK and assembly.
- Motion trajectories for analysis or replay.

Result data:

- Solved generalized coordinates and speeds.
- Segment transforms.
- Joint reaction forces.
- Inverse dynamics torques.
- Contact forces and contact events.
- Muscle-tendon lengths, moment arms, activations, and forces.
- Constraint residuals and solver diagnostics.

Non-goals for early advanced result assets:

- Full automatic conversion of visual mesh geometry to biomechanical bodies.
- Requiring a dynamics solver in the Bevy runtime.
- Treating tool-specific names as canonical project IDs.

## Continuum Solver Boundary

The project should not try to become a general scientific finite-element package.

Project-owned abstractions:

- Volumetric tissue regions.
- Material model descriptors.
- Fiber fields.
- Boundary conditions.
- Muscle activation drivers.
- Surface embeddings.
- Simulation result fields.

Possible implementations behind those abstractions:

- Diagnostic-only deformation with no solver.
- Offline baked results generated by a separate tool.
- A simple in-project linear or quasi-static solver for small regions.
- A reduced-order runtime solver.
- An offline tissue result writer if this becomes useful later.

This boundary keeps the plan focused. The Bevy runtime should never require a scientific FE solver just to load, pose, and render a character.

## Testing Strategy

Minimum self-contained fixture:

```text
subject:
  height = 1.80 m
  mass = 80.0 kg
segments:
  torso mass fraction = 0.50, length = 0.60 m
  left_thigh mass fraction = 0.10, length = 0.44 m
  left_shank mass fraction = 0.0465, length = 0.44 m
pose:
  all joints identity
expected:
  total mass after normalization = 80.0 kg
  every inertia diagonal is positive
  no joint limit violations
  whole-body COM is finite
  identity pose keeps every segment frame equal to its rest frame
```

A second fixture should place two feet on the ground with a support polygon and verify:

- COM projection inside polygon reports `Balanced`.
- COM projection outside polygon reports `Unbalanced` and a positive distance.
- Missing contacts report `NoSupportContacts`.

Unit tests:

- Anthropometric measurement conversion.
- Circumference-to-radius calculations.
- Segment mass percentage totals.
- Inertia tensor positive-definiteness.
- Joint limit validation.
- Joint model and generalized-coordinate validation.
- Function-based joint evaluation across sample coordinates.
- Assembly goal parsing and residual calculation.
- Segment binding lookup.
- Muscle path length in simple known poses.
- Muscle path via-point and wrapping-obstacle validation.
- Muscle-length and moment-arm surrogate evaluation against known samples.
- Motion trajectory parsing and name mapping.
- Contact event parsing.
- Tissue region parsing.
- Fiber field normalization.
- Boundary condition binding to segments.
- Surface embedding interpolation in known tetra/hex elements.
- Corrective morph bake metadata validation.

Golden tests:

- A canonical subject produces stable segment metrics.
- A canonical rig produces stable biomechanical frames.
- A canonical dynamics profile produces stable coordinate and joint-model mappings.
- Dynamics snapshot persistence produces stable link/joint topology.
- Advanced dynamics result assets produce stable body, coordinate, marker, and muscle path mappings.
- A canonical tissue region produces stable embedding and displacement transfer output.
- A canonical baked corrective morph produces stable vertex deltas.
- A canonical trajectory maps to the expected visual rig channels.
- A canonical activation curve produces stable diagnostics.

Interactive tests:

- Load a visual character.
- Toggle biomechanical overlays.
- Change height/mass values.
- Confirm diagnostics update without corrupting the visual mesh.
- Pose the model and confirm segment/muscle overlays follow.
- Toggle dynamics diagnostics and confirm generalized-coordinate and constraint warnings update.
- Play a loaded trajectory and confirm the visual skeleton, muscle overlays, and contact overlays stay synchronized.
- Toggle a tissue region overlay and confirm it follows the driving skeleton.
- Apply a baked corrective morph and confirm it affects only the intended region.

## Advanced Self-Contained Biomechanics Specs

These features are not required for the first useful biomechanics layer. They define implementable models for dynamics, muscle actuation, inverse kinematics, predictive motion, and reduced tissue deformation.

### Articulated Forward Kinematics

The dynamics and diagnostics layers need their own segment kinematics independent of the visual skeleton.

```rust
struct GeneralizedState {
    q: Vec<f32>,
    qd: Vec<f32>,
}

struct Coordinate {
    joint: JointId,
    axis_local: Vec3,
    min_rad: f32,
    max_rad: f32,
    default_rad: f32,
}
```

Each joint maps one or more coordinates to a local transform:

```rust
fn joint_transform(joint: &BiomechJoint, coordinates: &[Coordinate], q: &[f32]) -> Mat4 {
    match joint.kind {
        JointKind::Fixed => Mat4::IDENTITY,
        JointKind::Hinge { axis } => {
            let angle = q[joint.coordinate_start];
            Mat4::from_quat(Quat::from_axis_angle(axis.normalize(), angle))
        }
        JointKind::Euler3 => {
            let rx = q[joint.coordinate_start + 0];
            let ry = q[joint.coordinate_start + 1];
            let rz = q[joint.coordinate_start + 2];
            Mat4::from_quat(
                Quat::from_rotation_x(rx) *
                Quat::from_rotation_y(ry) *
                Quat::from_rotation_z(rz)
            )
        }
        JointKind::Ball => {
            // MVP stores ball joints as Euler3 coordinates for simplicity.
            unimplemented!()
        }
    }
}
```

Segment global transform:

```text
segment_global[child] =
    segment_global[parent]
    * joint.rest_parent_to_joint
    * joint_transform(q)
    * inverse(joint.rest_child_to_joint)
```

Validation:

- Identity `q` produces rest segment transforms.
- A one-hinge chain rotates the child by the expected angle.
- Joint limit clamping keeps every coordinate inside `[min_rad, max_rad]`.

### Inverse Kinematics For Biomech Landmarks

Use damped least squares for landmark fitting.

Objective:

```text
minimize sum_i || landmark_world_i(q) - target_i ||^2
```

Numerical Jacobian:

```rust
fn numerical_jacobian(model: &BiomechModel, q: &[f32], targets: &[LandmarkTarget]) -> DMatrix {
    let eps = 1.0e-4;
    let base = landmark_residuals(model, q, targets);
    let mut j = DMatrix::zeros(base.len(), q.len());
    for c in 0..q.len() {
        let mut q2 = q.to_vec();
        q2[c] += eps;
        let r2 = landmark_residuals(model, &q2, targets);
        for r in 0..base.len() {
            j[(r, c)] = (r2[r] - base[r]) / eps;
        }
    }
    j
}
```

Damped least-squares update:

```text
dq = inverse(J^T J + lambda^2 I) * J^T * residual
q_next = clamp(q - step_scale * dq, limits)
```

Defaults:

```rust
const IK_DAMPING: f32 = 1.0e-2;
const IK_STEP_SCALE: f32 = 0.5;
const IK_MAX_ITERATIONS: usize = 32;
const IK_TOLERANCE_M: f32 = 1.0e-3;
```

Validation:

- One hinge fitted to one target converges when target is reachable.
- Unreachable targets stop at the nearest joint-limit pose.
- Residual decreases or the solver stops with `NoProgress`.

### Inverse Dynamics Approximation

Full rigid-body dynamics can be delayed. A useful self-contained approximation is quasi-static inverse dynamics.

For each pose:

1. Compute segment global transforms.
2. Compute segment COM world positions.
3. Apply gravity force at each segment COM:

```text
F_g = mass * gravity
```

4. For each joint, accumulate torque from child subtree weights:

```text
torque_world += (com_world - joint_world).cross(F_g)
```

5. Project torque onto each joint coordinate axis:

```text
coordinate_torque = torque_world.dot(axis_world)
```

This ignores acceleration and contact, but it provides useful effort diagnostics.

Validation:

- A vertical segment aligned with gravity produces near-zero hinge torque.
- A horizontal segment produces torque approximately `mass * g * length_to_com`.
- Mirrored left/right limbs produce mirrored torque signs.

### Forward Dynamics MVP

If forward dynamics is needed, implement a simple semi-implicit Euler system for independent coordinates first.

```rust
struct CoordinateDynamics {
    inertia: f32,
    damping: f32,
    stiffness: f32,
}
```

Update:

```text
torque_total = user_torque + muscle_torque + passive_torque - damping * qd - stiffness * (q - q_rest)
qdd = torque_total / inertia
qd += qdd * dt
q += qd * dt
q = clamp(q, limits)
```

This is not full coupled multibody dynamics. It is a stable interactive approximation for exploratory tools.

Defaults:

```rust
const DYNAMICS_DT: f32 = 1.0 / 120.0;
const DEFAULT_COORDINATE_INERTIA: f32 = 1.0;
const DEFAULT_COORDINATE_DAMPING: f32 = 2.0;
const DEFAULT_COORDINATE_STIFFNESS: f32 = 0.0;
```

Validation:

- With zero torque and damping, coordinate velocity remains constant.
- With damping, velocity decays.
- Joint limits clamp and zero velocity when crossed.

### Hill-Lite Muscle Actuator

This is a simplified muscle actuator for diagnostics and animation tooling, not a clinical model.

```rust
struct MuscleActuator {
    path: MusclePath,
    max_force_n: f32,
    optimal_length_m: f32,
    tendon_slack_length_m: f32,
    activation: f32,
}
```

Length terms:

```text
normalized_length = muscle_length / optimal_length
force_length = exp(-((normalized_length - 1.0) / width)^2)
active_force = activation * max_force * force_length
passive_force = max(0, normalized_length - 1)^2 * passive_scale * max_force
total_force = active_force + passive_force
```

Defaults:

```rust
const MUSCLE_FORCE_LENGTH_WIDTH: f32 = 0.45;
const MUSCLE_PASSIVE_SCALE: f32 = 0.05;
```

Convert muscle force to joint torque using moment arm:

```text
torque = moment_arm * total_force
```

Validation:

- Activation `0` produces no active force.
- Activation `1` at optimal length produces approximately `max_force`.
- Moment arm sign changes when the muscle path changes sides of a joint axis.

### Predictive Motion MVP

Avoid full optimal control at first. Implement a small shooting optimizer over pose keyframes.

Goal:

```text
minimize:
    target_error_weight * sum ||end_effector(frame) - target(frame)||^2
  + smoothness_weight * sum ||q(frame+1) - 2q(frame) + q(frame-1)||^2
  + effort_weight * sum ||q(frame) - q_rest||^2
  + limit_penalty_weight * sum joint_limit_penalty(q(frame))
```

Finite-difference gradient:

```rust
fn finite_difference_gradient(problem: &MotionProblem, x: &[f32]) -> Vec<f32> {
    let eps = 1.0e-4;
    let base = objective(problem, x);
    let mut grad = vec![0.0; x.len()];
    for i in 0..x.len() {
        let mut x2 = x.to_vec();
        x2[i] += eps;
        grad[i] = (objective(problem, &x2) - base) / eps;
    }
    grad
}
```

Gradient descent with backtracking:

```text
for iteration:
    grad = finite_difference_gradient(x)
    step = initial_step
    while objective(x - step * grad) > objective(x):
        step *= 0.5
        if step < min_step: stop
    x = clamp_to_joint_limits(x - step * grad)
```

This is slow but self-contained and useful for short clips, pose transitions, and tests.

Validation:

- One-coordinate target reaches a known angle.
- Smoothness penalty reduces abrupt frame-to-frame changes.
- Limit penalty prevents optimization from leaving valid joint bounds.

### Reduced Tissue PBD Details

The earlier PBD scaffold needs exact constraint projection.

Distance constraint projection:

```rust
fn project_distance(particles: &mut [TissueParticle], c: &DistanceConstraint) {
    let pa = particles[c.a.0].position;
    let pb = particles[c.b.0].position;
    let delta = pb - pa;
    let len = delta.length();
    if len < 1.0e-8 {
        return;
    }
    let wa = particles[c.a.0].inverse_mass;
    let wb = particles[c.b.0].inverse_mass;
    let wsum = wa + wb;
    if wsum <= 0.0 {
        return;
    }
    let correction = delta * ((len - c.rest_length) / len) * c.stiffness;
    particles[c.a.0].position += correction * (wa / wsum);
    particles[c.b.0].position -= correction * (wb / wsum);
}
```

Attachment projection:

```rust
fn project_attachment(particles: &mut [TissueParticle], c: &AttachmentConstraint, bone_global: Mat4) {
    let target = bone_global.transform_point3(c.local_point);
    let p = &mut particles[c.particle.0];
    p.position = p.position.lerp(target, c.stiffness.clamp(0.0, 1.0));
}
```

Surface displacement transfer:

```text
for each render vertex:
    find nearest tissue particle or precomputed embedding
    displacement = particle.position - particle.rest_position
    render_position = skinned_position + displacement * weight
```

Validation:

- A two-particle distance constraint returns to rest length within tolerance.
- A fully stiff attachment follows the bone exactly.
- Zero inverse-mass particles do not move.

### Linear Tetrahedral Tissue Prototype

If a finite-element-like prototype is needed, start with linear tetrahedra and quasi-static springs rather than a nonlinear solver.

```rust
struct TetraElement {
    vertices: [ParticleId; 4],
    rest_edges: [(usize, usize, f32); 6],
    stiffness: f32,
}
```

Treat each tetra edge as a distance constraint in PBD. This does not compute true stress/strain, but it preserves simple volume-like structure better than isolated surface springs.

Optional volume constraint:

```text
V = dot(p1 - p0, cross(p2 - p0, p3 - p0)) / 6
C = V - rest_volume
```

Use finite differences to approximate gradients for each tetra vertex if implementing volume projection. This can be added later after distance constraints are stable.

Finite-element concept contract:

- `nodes` store rest and current positions.
- `elements` store node ids and a material id.
- A material point evaluates deformation gradient `F`, volume ratio `J = det(F)`, stress, and optional tangent stiffness.
- Boundary conditions attach nodes or element regions to bones, prescribe motion, apply pressure, or constrain sliding.
- Fiber fields are unit vectors in material/rest space and are transformed by `F` during evaluation.
- Surface transfer reads solved node displacements through precomputed embeddings and never changes visual topology.

The first finite-element-like prototype may approximate this with PBD constraints, but the asset model should still use these concepts so later offline solvers or reduced models have a stable contract.

Validation:

- Rest tetra has zero constraint error.
- Stretching one vertex increases edge constraint error.
- Volume constraint reduces collapse in a simple compression test.

### Contact Diagnostics

MVP contact is diagnostic, not a full contact solver.

Foot contact:

```rust
struct ContactPoint {
    segment: SegmentId,
    local_point: Vec3,
    radius: f32,
}
```

Ground contact check:

```text
world = segment_global * local_point
penetration = max(0, radius - world.y)
in_contact = penetration > 0
```

Approximate normal force for diagnostics:

```text
normal_force = ground_stiffness * penetration - damping * vertical_velocity
normal_force = max(0, normal_force)
```

Smooth diagnostic contact for finite-difference tooling:

```text
smooth_penetration = softplus(radius - world.y, beta)
normal_force = ground_stiffness * smooth_penetration
             - damping * vertical_velocity * smoothstep_contact
normal_force = max(0, normal_force)
```

Use the hard `max` form for simple overlays and the smooth form for any finite-difference objective, gradient check, or trajectory tool. Friction should also use bounded smooth slip speed:

```text
slip_speed = sqrt(dot(v_tangent, v_tangent) + epsilon)
friction_dir = -v_tangent / slip_speed
```

Validation:

- Contact point above ground has zero penetration.
- Contact point below ground reports positive penetration.
- Contact overlay follows segment transforms.

### Persistent Biomech SQLite

Use SQLite records for biomechanical models, states, trajectories, and tissue results.

```rust
struct BiomechModelAsset {
    version: u32,
    asset_id: String,
    subject: SubjectMeasurements,
    segments: Vec<BodySegmentAsset>,
    joints: Vec<BiomechJointAsset>,
    coordinates: Vec<CoordinateAsset>,
    muscles: Vec<MusclePathAsset>,
    contacts: Vec<ContactPointAsset>,
}

struct BiomechStateAsset {
    version: u32,
    model_asset_id: String,
    coordinates: Vec<CoordinateStateAsset>,
    muscle_activations: Vec<MuscleActivationAsset>,
    contacts: Vec<ContactStateAsset>,
    analysis_options: BiomechAnalysisOptionsAsset,
}
```

Rules:

- Names must be unique within segments, joints, coordinates, and muscles.
- All name links are resolved to dense ids at load time.
- Units are meters, kilograms, seconds, radians, and Newtons.
- SQLite save/load should round-trip without changing names or numeric values outside serialization tolerance.
- State records reference model assets by project id and store coordinate/activation/contact parameters, not evaluated transforms or overlay meshes.

## Milestones

## Milestone B0: Biomech Document And Boundaries

- Keep biomechanics as an optional plan separate from the visual mesh MVP.
- Define terminology, levels, and non-goals.
- Do not add runtime dependencies yet.

## Milestone B1: Landmarks And Segment Debugging

- Define segment IDs and landmark IDs.
- Bind a small set of segments to the visual skeleton.
- Draw joint frames, segment axes, and COM placeholders in Bevy.
- Add diagnostics for missing or invalid bindings.

## Milestone B2: Anthropometric Metrics

- Add `AnthropometricSubject`.
- Derive `SegmentMetrics`.
- Add mass distribution and inertia approximations.
- Add validation for total mass, dimensions, COM, and inertia.

## Milestone B3: Biomechanical Skeleton

- Build `RigidBodySegment` and `BiomechJoint` data from profile assets.
- Add joint limits and pose diagnostics.
- Compare current visual pose against biomechanical joint constraints.

## Milestone B4: Muscle Paths

- Add basic muscle attachment profiles.
- Draw muscle paths as debug geometry.
- Compute muscle path lengths under pose.
- Add warnings for unrealistic lengths.

## Milestone B5: Actuation Experiments

- Add simple muscle activation values.
- Estimate forces and joint torques.
- Use results for diagnostics first.
- Defer full forward dynamics until the model is well validated.

## Milestone B6: Dynamics Coordinates And Assembly Diagnostics

- Define generalized coordinate and joint-model data types.
- Add function-based joint descriptors for future advanced joints.
- Add constraint and assembly goal descriptors.
- Evaluate coordinate limits and constraint residuals for the current pose.
- Add diagnostics for visual-rig-to-dynamics-skeleton mapping errors.
- Keep this diagnostic-only at first.

## Milestone B7: Predictive Motion Load And Playback

- Define trajectory, activation, force, contact, objective, and constraint data types.
- Load one trajectory fixture from `.human.sqlite`.
- Retarget trajectory joints through rig profiles.
- Play the trajectory through the existing pose/skinning path.
- Draw activation, force, COM, and contact overlays where data exists.
- Add diagnostics for missing channels, invalid units, joint-limit violations, and contact timing.

## Milestone B8: Moment-Arm Surrogates And Motion Diagnostics

- Define a data format for muscle-length and moment-arm surrogate coefficients.
- Add tests against known sample data.
- Compute fast muscle length, velocity, and moment-arm diagnostics during pose or trajectory playback.
- Use diagnostics to validate imported motion clips before attempting optimization.

## Milestone B9: Offline Optimization Experiment

- Prototype one limited offline optimization problem outside the Bevy runtime.
- Start with a small joint/muscle set before full-body gait.
- Save solved joint curves, activation curves, force curves, and contacts into `biomech_trajectories`.
- Keep all optimizer dependencies out of the core runtime.

## Milestone B10: Advanced Dynamics Result Experiment

- Build one small dynamics model from segments, joints, coordinates, and markers.
- Include one or two muscle/cable paths if the path data is available.
- Save solved coordinate or inverse-dynamics diagnostics as result assets.
- Keep solver experiments optional and outside the Bevy runtime.

## Milestone B11: Continuum Tissue Model Design

- Define tissue region, material model, fiber field, boundary condition, and simulation result data types.
- Add asset parsing for one local tissue region.
- Bind the region to existing biomechanical segments.
- Draw tissue nodes, elements, region masks, and fiber directions as debug overlays.
- Keep this diagnostic-only at first.

## Milestone B12: Surface Embedding And Transfer

- Define `SurfaceEmbedding` assets.
- Bind selected visual mesh vertices to one local tissue region.
- Implement interpolation from tissue node displacement to render vertex displacement.
- Add diagnostics for missing embeddings, invalid weights, and excessive displacement.
- Prove that a disabled or failed tissue region leaves the standard visual mesh path untouched.

## Milestone B13: Corrective Morph Baking

- Define driver states for one region, such as elbow flexion and biceps activation.
- Generate or load a simulated displacement result for those driver states.
- Transfer the displacement to visual vertex deltas.
- Save the deltas as a corrective morph target.
- Evaluate the generated morph at runtime using the existing morph pipeline.

## Milestone B14: Reduced Tissue Runtime Experiments

- Prototype one cheap reduced tissue model for a local region.
- Compare its output against baked morphs or offline simulation results.
- Keep it optional and region-scoped.
- Do not allow this milestone to block the base visual runtime.

## Milestone B15: Dynamics Snapshot Persistence

- Save links, joints, mass, inertia, and simple collision geometry as SQLite diagnostics.
- Reload and validate the generated snapshot file.
- Keep visual mesh data out of the snapshot.

## Open Questions

- Which physics backend should be used for optional dynamics, if any?
- Should the project use marker groups, skeleton bones, or custom landmarks as the primary segment source?
- How much asymmetry should the subject measurement model support?
- Should anthropometric fitting adjust only the biomechanical model, or should it also suggest visual morph slider values?
- What license policy should be used for external muscle and anatomy assets?
- Which dynamics snapshot is most useful first: balance, inverse-dynamics diagnostics, contact diagnostics, or assembly diagnostics?
- Should the dynamics skeleton support function-based joints in the first dynamics milestone, or should those be deferred until after simple hinge/ball/slider joints work?
- What is the minimum useful dynamics result asset: coordinate curves, IK/assembly residuals, inverse dynamics, or full forward dynamics?
- Should muscle wrapping surfaces be represented early, or should initial muscle paths use only straight segments and via points?
- Which trajectory data should be supported first in `biomech_trajectories`: generic joint curves, activation curves, force curves, or contact events?
- Should the first predictive-motion target be walking, squat, arm curl, reach, or another smaller motion?
- Should optimizer work happen in Rust or another tooling language?
- What minimal moment-arm surrogate accuracy is acceptable before using it for diagnostics or optimization?
- Which body region is the best first continuum tissue target: upper arm, shoulder, abdomen, face, or breast/glute tissue?
- Should local volumetric tissue meshes be authored manually, generated from the visual surface, or loaded from external tools?
- What is the minimum material model that produces useful deformation beyond blend shapes?
- Should simulated deformations drive runtime vertices directly, or should they always bake into corrective morph targets first?
- How should standard skinning, visual morphs, and tissue displacement be ordered and blended?
- What diagnostics are needed to prevent tissue simulation output from damaging the visual mesh?

## Recommendation

Do not make biomechanical simulation part of the first visual runtime milestone. The visual runtime already has enough risk: stable topology, morph target application, rig fitting, skin weights, and pose/skinning correctness.

Add biomechanics after the visual skeleton and pose pipeline are working. Start with landmarks, segment metrics, mass diagnostics, and overlays. Then add rigid-body structure, muscle paths, and activation diagnostics.

Use multibody concepts to shape the rigid-body and dynamics design: segments, generalized coordinates, mobilizers, constraints, assembly goals, contact forces, and cable paths.

Use predictive-motion concepts for a later tooling path: trajectory import, activation curves, force diagnostics, contact events, moment-arm surrogates, and offline optimal-control experiments. The Bevy app should consume solved motion data, not solve full nonlinear gait problems interactively.

For deformation beyond blend shapes, use continuum-tissue concepts as the conceptual model: volumetric tissue, material properties, fiber fields, constraints, and surface displacement transfer. The practical first implementation should bake simulated or reduced tissue deformation into corrective morph targets, then reuse the existing fast visual pipeline at runtime.
