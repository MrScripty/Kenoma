# Human Mesh Bevy Runtime Implementation Plan

Date: 2026-05-30
Status: Draft

## Related Plans

- [Biomechanical Simulation Plan](biomechanical-simulation-plan.md): optional subject measurements, segment masses, joint constraints, muscle paths, multibody dynamics concepts, predictive motion tooling, continuum tissue concepts, diagnostics, and persistent analysis assets. This is intentionally separate from the first visual mesh runtime.
- [Procedural Skin Graph Mesh Plan](procedural-skin-graph-plan.md): graph editing workflow where users extrude vertices and edges, assign radii, and generate a simple proxy/mannequin mesh around the graph. This is a separate procedural modeling path, not a fixed-topology morph target path.

## Armature And Deformation Design

This project uses a clean separation between rest armature data, pose evaluation, vertex-group weights, deformation systems, and authoring tools. It is not a muscle or tissue simulator.

Useful concepts:

- Explicit transform spaces:
  - bone/rest local space
  - armature/model rest space
  - pose/evaluated model space
  - channel/local pose-delta space
- A persistent rest skeleton that stores hierarchy, head/tail/roll, rest matrices, envelope settings, and optional curved-bone metadata.
- A per-character pose state that stores local transform inputs, evaluated local/channel matrices, evaluated global pose matrices, constraints or IK results, and cached deformation transforms.
- Sparse per-vertex weights keyed by vertex group or bone index.
- A deformation stage that consumes an already evaluated pose and does not own animation, constraints, UI state, or rig editing.
- A clear choice between linear blend skinning and dual-quaternion skinning.
- Authoring-time weight generation tools, such as envelope weighting and heat/Laplacian weighting, kept separate from runtime skinning.

Practical implementation for this project:

```rust
struct RestBone {
    name: String,
    parent: Option<BoneId>,
    head: Vec3,
    tail: Vec3,
    roll: f32,
    rest_local: Mat4,
    rest_global: Mat4,
    inverse_bind: Mat4,
    deform: bool,
}

struct PoseChannel {
    bone: BoneId,
    translation: Vec3,
    rotation: Quat,
    scale: Vec3,
    channel_matrix: Mat4,
    pose_global: Mat4,
    skin_matrix: Mat4,
}

struct ArmatureInstance {
    rest_bones: Vec<RestBone>,
    pose_channels: Vec<PoseChannel>,
    bone_name_to_id: HashMap<String, BoneId>,
}
```

The import path should build `RestBone` data from the canonical `SkeletonAsset` plus optional rig-shape endpoint fitting. The runtime should then evaluate `PoseChannel` data every frame or whenever pose input changes. Skinning should consume only `skin_matrix`, shaped vertices, and packed or full weights.

This gives us a useful runtime structure with clear local ownership of the modifier, UI, dependency graph, and file format assumptions.

## Goal

Build a Rust and Bevy 0.18 runtime/editor that can load canonical human character data, apply morph targets, fit or update a rig, use vertex weights, and pose/render the model in Bevy.

The first target is a reliable character runtime that proves the core deformation pipeline:

1. Load a fixed base mesh with stable vertex indices.
2. Apply sparse morph targets to produce a shaped mesh.
3. Load a skeleton definition from joint marker metadata.
4. Load and normalize per-bone vertex weights.
5. Pose the model with linear blend skinning.
6. Display and inspect the result in Bevy.

## Runtime Contract

The implementation stack for this plan is the Rust workspace plus Bevy 0.18 for the editor/runtime viewer. The core deformation crate must remain framework-independent; Bevy integration must live behind the Bevy integration crate.

The canonical asset model described in this plan is:

- `HumanModelAsset`
- `MeshAsset`
- `MorphTargetAsset`
- `SkeletonAsset`
- `WeightsAsset`
- `PoseClipAsset`

Bevy is the required consumer for the first implementation.

## Inputs

Expected source assets for the self-contained MVP:

- Base mesh: canonical `MeshAsset`.
- Morph targets: canonical `MorphTargetAsset`.
- Rig: canonical `SkeletonAsset`.
- Weights: canonical `WeightsAsset`.
- Poses/animation: canonical `PoseClipAsset`.
- Optional later assets: clothes, hair, proxy meshes, expressions, materials.

## Persistent Storage Contract

Use one canonical on-disk format for the first implementation: a SQLite database file.

Required file types:

- `.human.sqlite`: authoritative project database. It stores model-library assets, saved character state, graph assets, biomechanical assets, pose clips, migrations, and metadata needed to regenerate Bevy runtime meshes.

Required logical records inside `.human.sqlite`:

- `human_models`: canonical base topology, morph targets, skeleton, weights, and built-in pose clips. This is the only logical record in this plan that stores mesh topology, because morphs and weights need stable vertex ids.
- `human_states`: saved character state containing a reference to a model id, morph slider values, pose state, active pose clip/time, display/debug options, and optional authoring metadata.
- `pose_clips`: optional reusable pose or animation clips using the same pose-space conventions as the model asset.
- `project_metadata`: schema version, app version, project id, created/updated timestamps, and migration history.

The normal save path for a user-created character is a `human_states` row, not a mesh file. Loading state means:

1. Open the `.human.sqlite` project database.
2. Load the referenced `human_models` row.
3. Validate and preprocess the model.
4. Apply saved morph slider values from `human_states` to regenerate shaped positions.
5. Apply saved pose state or sampled pose clip.
6. Run skinning and upload the resulting buffers to a Bevy `Mesh`.

Generated meshes are cacheable but disposable. If a later cache is added, it must be keyed by a content hash of the model asset plus generation and pose state, and it must be safe to delete without data loss.

SQLite storage rules:

- Use migrations with monotonically increasing integer versions.
- Store scalar searchable metadata in typed columns.
- Store large homogeneous numeric arrays as little-endian `BLOB` values with explicit element type, count, and unit metadata.
- Store nested authoring structs either in normalized child tables or in versioned binary blobs owned by the persistence layer. Do not expose SQLite row layouts as core runtime structs.
- Use transactions for project save operations so a partial write cannot corrupt character state.
- Enable foreign keys and validate referential integrity on open.

## Self-Contained Implementation Contract

The implementation should begin from the canonical data and math rules below.

Coordinate conventions:

- Use a right-handed local model space.
- `+Y` is up.
- `+X` is character right.
- `+Z` is character forward.
- Store mesh vertices, bone endpoints, and poses in model space unless a field explicitly says otherwise.
- Use meters as conceptual units.
- Use radians for rotations.
- Use normalized quaternions for runtime rotations.

Matrix conventions:

- Use `glam::Mat4` and `glam::Vec3`.
- Conceptually treat transforms as column-vector transforms.
- Compose parent and child transforms as `global = parent_global * local`.
- Transform points with `mat.transform_point3(point)`.
- Transform directions/normals with `mat.transform_vector3(direction)`.
- Skinning matrix is `skin_matrix = posed_global * inverse_bind`.

Determinism requirements:

- Sort named assets by stable import order or explicit id.
- Convert names to dense ids at load time.
- Do not use string lookups in per-frame skinning.
- Clamp invalid numeric input and report diagnostics rather than panicking in editor builds.
- Unit tests should run without Bevy.

## Canonical Data Model

The MVP must load SQLite projects only. The core data model is still plain Rust structs. SQLite is the persistence layer, not the runtime model. Do not add any other file formats to the first implementation.

### Human Model Asset

```rust
struct HumanModelAsset {
    version: u32,
    asset_id: String,
    mesh: MeshAsset,
    morphs: Vec<MorphTargetAsset>,
    sliders: Vec<MorphSliderAsset>,
    skeleton: SkeletonAsset,
    weights: WeightsAsset,
    poses: Vec<PoseClipAsset>,
}
```

### Human State Asset

```rust
struct HumanStateAsset {
    version: u32,
    model_asset_id: String,
    morph_values: Vec<MorphSliderValue>,
    pose: PoseStateAsset,
    active_clip: Option<ActivePoseClipAsset>,
    viewport: HumanViewportStateAsset,
}

struct MorphSliderValue {
    slider: String,
    value: f32,
}

struct ActivePoseClipAsset {
    clip: String,
    time_s: f32,
    looping: bool,
}
```

Rules:

- Slider names are resolved to dense ids at load time.
- Missing slider values use the slider default and report an info diagnostic.
- Unknown slider names are ignored and reported as warnings.
- Pose state stores authoring inputs, not evaluated matrices.
- Derived mesh buffers are regenerated after load.

### Mesh Asset

```rust
struct MeshAsset {
    positions: Vec<[f32; 3]>,
    normals: Option<Vec<[f32; 3]>>,
    uvs: Option<Vec<[f32; 2]>>,
    indices: Vec<u32>,
}
```

Rules:

- `positions.len()` is the stable vertex count.
- `indices.len()` must be divisible by 3.
- Indices are triangles with counter-clockwise winding viewed from outside the mesh.
- If normals are missing, compute smooth vertex normals from triangles.
- Morph targets and weights refer to `positions` indices.

### Morph Target Asset

```rust
struct MorphTargetAsset {
    name: String,
    group: String,
    default_weight: f32,
    min_weight: f32,
    max_weight: f32,
    deltas: Vec<MorphDelta>,
}

struct MorphDelta {
    vertex: u32,
    delta: [f32; 3],
}
```

Rules:

- `deltas` must be sorted by vertex index after loading.
- Duplicate deltas for the same vertex are merged by addition and reported.
- Deltas referencing missing vertices are skipped and reported.
- Morph evaluation is linear:

```text
shaped[v] = base[v] + sum(delta[target, v] * weight[target])
```

### Morph Slider And Dependency Evaluation

The runtime should distinguish authored morph targets from user-facing sliders. A slider may drive one target directly, a positive/negative target pair, or a set of targets whose effective weights depend on subject factors such as height, age, build, or local edit direction.

Canonical slider data:

```rust
struct MorphSliderAsset {
    name: String,
    min_value: f32,
    max_value: f32,
    default_value: f32,
    targets: Vec<MorphTargetBinding>,
}

struct MorphTargetBinding {
    target: String,
    value_mode: MorphValueMode,
    dependency_factors: Vec<MorphFactorId>,
}

enum MorphValueMode {
    Direct,
    PositiveOnly,
    NegativeOnly,
}
```

Effective target weight:

```text
slider_component =
    Direct       -> value
    PositiveOnly -> max(value, 0)
    NegativeOnly -> max(-value, 0)

effective_weight[target] =
    slider_component * product(factor_value[f] for f in dependency_factors)
```

This rule supports direct sliders, positive/negative local targets, and macro-dependent targets without hardcoding target names or file layout assumptions.

Continuous macro factors should use piecewise-linear interpolation over authored anchors:

```text
factor(anchor_i) = 1 - alpha
factor(anchor_j) = alpha
alpha = clamp((value - anchor_i) / (anchor_j - anchor_i), 0, 1)
```

For multi-factor target bindings, multiply the active interpolation factors. Macro blends and local positive/negative controls then use the same math path.

### Morph Buffering

Interactive editing should not require rebuilding every target for every slider drag. Keep explicit mesh buffers:

```rust
struct MorphBuffers {
    base_positions: Vec<Vec3>,
    non_macro_positions: Vec<Vec3>,
    macro_positions: Vec<Vec3>,
    slider_work_positions: Vec<Vec3>,
    shaped_positions: Vec<Vec3>,
}
```

Update rules:

1. `base_positions` never changes after load.
2. `non_macro_positions` equals base plus all local/detail morphs that are not macro-dependent.
3. `macro_positions` accumulates macro-dependent target deltas.
4. `slider_work_positions` is a temporary copy that excludes the currently edited slider contribution.
5. `shaped_positions = non_macro_positions + macro_positions`.

When a local slider changes, update from `slider_work_positions + active_delta * new_weight`. When a macro factor changes, rebuild `macro_positions` from the effective target weights, then combine with `non_macro_positions`. This keeps live sliders responsive while still producing deterministic full rebuilds.

### Skeleton Asset

```rust
struct SkeletonAsset {
    bones: Vec<BoneAsset>,
    joint_markers: Vec<JointMarkerAsset>,
}

struct BoneAsset {
    name: String,
    parent: Option<String>,
    head: [f32; 3],
    tail: [f32; 3],
    roll: f32,
    deform: bool,
}

struct JointMarkerAsset {
    name: String,
    vertices: Vec<u32>,
}
```

Rules:

- Bone names must be unique.
- Parent names are resolved to dense `BoneId`s at load time.
- Parent bones must appear before children after preprocessing. If the input is unordered, topologically sort it.
- A bone's local `+Y` axis points from `head` to `tail`.
- A zero-length bone is invalid for deformation; keep it for hierarchy only if needed and report it.
- If `deform` is false, the bone can be animated but receives no skin weights.
- `joint_markers` is optional for static rigs but required for marker-based rig refitting.
- Marker vertex indices must refer to valid mesh vertices.
- A marker with no valid vertices is ignored and reported.

### Weights Asset

```rust
struct WeightsAsset {
    vertices: Vec<VertexWeightAsset>,
}

struct VertexWeightAsset {
    influences: Vec<BoneInfluenceAsset>,
}

struct BoneInfluenceAsset {
    bone: String,
    weight: f32,
}
```

Rules:

- `vertices.len()` must equal mesh vertex count.
- Bone names are resolved to dense `BoneId`s at load time.
- Duplicate influences for a vertex/bone pair are added together.
- Negative weights are clamped to zero and reported.
- Per-vertex weights are normalized so the sum is `1.0`.
- If a vertex has no valid positive weights, assign it to the root bone with weight `1.0` and report it.
- Store full influences for CPU validation and packed top-4 influences for GPU-compatible paths.

### Pose Clip Asset

```rust
struct PoseClipAsset {
    name: String,
    frames_per_second: f32,
    frames: Vec<PoseFrameAsset>,
}

struct PoseFrameAsset {
    root_translation: [f32; 3],
    bone_rotations: Vec<BoneRotationAsset>,
}

struct BoneRotationAsset {
    bone: String,
    rotation_xyzw: [f32; 4],
}
```

Rules:

- Missing bone rotations use identity.
- Quaternions are normalized on load.
- MVP clips do not need scale animation.
- Root translation is model-space translation applied to the root bone before child propagation.

## Build Contract

This section is normative. If it conflicts with older background/context text elsewhere in the plan, this section wins.

### Normative Scope

The first implementation must support:

- Loading the canonical `HumanModelAsset`.
- Validating canonical mesh, morph, skeleton, weight, and pose data.
- Applying sparse morph targets.
- Building rest skeleton matrices and inverse bind matrices.
- Evaluating rest-relative pose rotations.
- Normalizing full weights and packing top-4 weights.
- CPU skinning with full weights and packed weights.
- Producing diagnostics for invalid input and lossy packing.
- Rendering a sample asset in Bevy.

The first implementation does not need:

- BVH import.
- GPU skinning.
- DQS.
- IK.
- External mesh file output.
- attached clothes/proxy assets.

### Required Sample Assets

Add these files before implementation is considered testable:

```text
assets/samples/canonical_minimal/minimal.human.sqlite
```

`minimal.human.sqlite` must contain:

- 4 to 8 vertices.
- at least 2 triangles.
- 2 bones: root and child.
- one sparse morph target.
- one pose clip with identity pose and one non-trivial pose.
- weights that include at least one top-4-safe vertex and one vertex requiring normalization.
- one saved human state using non-default morph and pose parameters.
- expected shaped positions, rest-skin positions, and weight reports in fixture tables.

Expected output records must be generated once by hand or by a locked test fixture and then treated as golden data.

### Public API

The `human_persistence` crate must expose project load/save APIs equivalent to:

```rust
pub fn load_human_model_from_project(
    project: &HumanProjectStore,
    model_id: HumanModelId,
) -> Result<HumanModelAsset, HumanLoadError>;

pub fn load_human_state_from_project(
    project: &HumanProjectStore,
    state_id: HumanStateId,
) -> Result<HumanStateAsset, HumanLoadError>;

pub fn save_human_state_to_project(
    project: &mut HumanProjectStore,
    state: &HumanStateAsset,
) -> Result<HumanStateId, HumanSaveError>;
```

The `human_core` crate must expose framework-independent runtime APIs equivalent to:

```rust
pub fn validate_human_model(asset: &HumanModelAsset) -> HumanDiagnostics;

pub fn preprocess_human_model(asset: HumanModelAsset) -> Result<HumanModel, HumanBuildError>;

pub fn apply_morphs(base_positions: &[Vec3], morphs: &[MorphTarget], weights: &[f32]) -> Vec<Vec3>;

pub fn build_rest_skeleton(skeleton: &Skeleton, shaped_positions: Option<&[Vec3]>) -> RestSkeleton;

pub fn evaluate_pose(rest: &RestSkeleton, pose: &PoseState) -> Vec<Mat4>;

pub fn compute_skin_matrices(posed_global: &[Mat4], inverse_bind: &[Mat4]) -> Vec<Mat4>;

pub fn skin_positions_cpu(
    shaped_positions: &[Vec3],
    weights: &FullVertexWeights,
    skin_matrices: &[Mat4],
) -> Vec<Vec3>;

pub fn skin_normals_cpu(
    base_normals: &[Vec3],
    weights: &FullVertexWeights,
    skin_matrices: &[Mat4],
) -> Vec<Vec3>;

pub fn pack_top4_weights(weights: &FullVertexWeights) -> PackedWeightReport;
```

The Bevy crate may wrap these APIs, but core tests must call them without starting a Bevy app.

### Diagnostics Types

Use structured diagnostics instead of strings:

```rust
enum HumanDiagnostic {
    MeshIndexOutOfRange { index_position: usize, vertex: u32, vertex_count: usize },
    TriangleIndexCountNotMultipleOfThree { index_count: usize },
    DuplicateMorphDelta { morph: String, vertex: u32 },
    MorphDeltaVertexOutOfRange { morph: String, vertex: u32, vertex_count: usize },
    DuplicateBoneName { name: String },
    MissingParentBone { bone: String, parent: String },
    BoneCycle { bone: String },
    ZeroLengthBone { bone: String },
    MarkerVertexOutOfRange { marker: String, vertex: u32, vertex_count: usize },
    WeightVertexCountMismatch { weights: usize, vertices: usize },
    WeightBoneMissing { vertex: u32, bone: String },
    NegativeWeightClamped { vertex: u32, bone: String, weight: f32 },
    DuplicateWeightMerged { vertex: u32, bone: String },
    UnweightedVertexAssignedToRoot { vertex: u32 },
    WeightPackingDroppedInfluence { vertex: u32, dropped_weight: f32 },
    PoseBoneMissing { clip: String, bone: String },
    PoseQuaternionRenormalized { clip: String, bone: String },
}
```

Diagnostics must have severities:

```rust
enum DiagnosticSeverity {
    Info,
    Warning,
    Error,
}
```

Errors prevent preprocessing. Warnings allow preprocessing with repair or fallback.

### Numeric Tolerances

Use these tolerances in tests unless a test states otherwise:

```rust
const POSITION_EPSILON: f32 = 1.0e-5;
const NORMAL_EPSILON: f32 = 1.0e-4;
const QUATERNION_EPSILON: f32 = 1.0e-5;
const MATRIX_EPSILON: f32 = 1.0e-5;
const WEIGHT_SUM_EPSILON: f32 = 1.0e-5;
const CPU_PACKED_SKIN_ERROR_WARN: f32 = 1.0e-3;
const CPU_PACKED_SKIN_ERROR_FAIL: f32 = 1.0e-2;
const IK_POSITION_EPSILON: f32 = 1.0e-3;
```

### Required Dependencies

Preferred dependencies:

```text
bevy = "0.18"
glam = version matched to Bevy where possible
serde = derive
rusqlite = SQLite project persistence, preferably isolated to `human_persistence`
thiserror = structured errors
bitflags = flags where needed
approx = numeric test assertions
```

Avoid adding heavier dependencies until a section specifically requires them.

### Standards Compliance And Blast Radius

All implementation work for this plan must comply with the standards in `/media/jeremy/OrangeCream/Linux Software/repos/owned/developer-tooling/Coding-Standards/`. The required standards are `CODING-STANDARDS.md`, `TESTING-STANDARDS.md`, `DOCUMENTATION-STANDARDS.md`, `SECURITY-STANDARDS.md`, `DEPENDENCY-STANDARDS.md`, `PLAN-STANDARDS.md`, and the Rust-specific standards in `languages/Rust/`.

Architecture boundaries:

- `human_core` owns canonical data types, validation, preprocessing, morph evaluation, skeleton math, pose evaluation, skinning math, diagnostics, and deterministic fixtures. It must not depend on Bevy, rendering, UI, file watchers, async runtimes, SQLite, or platform APIs.
- `human_persistence` owns SQLite database opening, migrations, project metadata, load/save repositories, transaction boundaries, and conversion between database records and `human_core` asset structs.
- `human_bevy` owns Bevy components, resources, asset loaders, plugin wiring, system schedules, debug overlays, and render mesh upload. It may call `human_core`; `human_core` must never call back into Bevy.
- App binaries are composition roots. They choose plugins, schedules, UI panels, feature flags, sample assets, and command-line options.
- SQLite project loaders must parse into canonical validated types. Internal runtime code must not branch on database row-layout quirks.
- Stateful flows must have a single owner. Pose state, morph slider state, and active asset selection each belong to one explicit Bevy resource or component set. Generated render meshes are derived data and never become the authoritative model.

Rust API and safety rules:

- Use safe Rust by default with workspace lints set to deny unsafe code unless a later ADR explicitly narrows and justifies an unsafe module.
- Production code must not use `unwrap`, `expect`, unchecked indexing, or panics for recoverable runtime errors.
- Public APIs return typed errors such as `HumanAssetError`, `HumanValidationError`, or `HumanRuntimeError`. Do not return `Result<T, String>`.
- Validate once at the asset boundary and convert to constrained internal types. Core algorithms should accept validated/preprocessed types where possible.
- Numeric constants, tolerances, axis conventions, unit scales, Bevy labels, and schedule labels must be named constants or typed config values, not inline literals.
- Public structs must use explicit units in field names or docs where ambiguity is possible, for example `height_m`, `mass_kg`, `angle_rad`, `translation_m`.
- Every directory under `src/` must include a local `README.md` before or in the same milestone that creates the directory.

Dependency rules:

- Prefer `std`, `glam`, `serde`, `rusqlite`, `thiserror`, `approx`, and Bevy-provided types where they are sufficient.
- New dependencies require a dependency note or ADR covering purpose, owner crate, feature flags, alternatives considered, transitive risk, and removal path.
- Heavy dependencies, GPU backends, physics engines, additional serialization stacks, and optimization libraries must be feature-gated and kept outside `human_core` unless they are part of a later accepted public contract.
- Shared dependencies used by more than one crate must be declared at workspace level.

Verification gates:

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`
- `cargo test --workspace`
- `cargo test --workspace --doc`
- `cargo check --workspace --all-features`
- `cargo check --workspace --no-default-features` once public features exist

Required test coverage:

- Boundary validation tests for malformed mesh indices, duplicate IDs, missing bones, invalid inverse bind matrices, invalid parent order, negative weights, NaNs, and out-of-range pose channels.
- Golden fixture tests for morph application, packed weights, rest skeleton transforms, posed skeleton transforms, skin matrices, skinned positions, and skinned normals.
- Bevy integration smoke test that loads the minimal fixture, inserts expected components/resources, and confirms mesh upload does not mutate canonical data.
- Property or table-driven tests for weight normalization, top-N influence packing, quaternion normalization, matrix multiplication order, and parent-child transform propagation.

Milestone write sets:

- Asset schema and validation: `crates/human_core/src/types`, `crates/human_core/src/validation`, sample fixtures, and validation tests only.
- Morph math: `crates/human_core/src/morph`, morph tests, and fixture expected outputs only.
- Skeleton and pose math: `crates/human_core/src/skeleton`, `crates/human_core/src/pose`, tests, and expected transform fixtures only.
- Skinning math: `crates/human_core/src/skinning`, tests, and fixture expected skinned vertices only.
- Bevy runtime: `crates/human_bevy/src`, viewer app composition, and Bevy integration tests only.
- Documentation and ADR updates: `docs/plans`, `docs/adr`, crate READMEs, and module READMEs only.

Schema files, diagnostic enums, public facade exports, and sample fixture formats are shared contracts. Change them serially, update all downstream tests in the same change, and record the rationale. Parallel work must avoid overlapping writes to those files.

Before implementation, inspect git status. Do not mix unrelated dirty implementation files into a milestone. Documentation-only untracked files may remain uncommitted while planning, but implementation changes must be reviewable by logical slice.

Re-plan before continuing if any of these occur:

- A public API or canonical schema must change after another crate depends on it.
- A new heavy dependency or unsafe block seems necessary.
- Bevy state ownership becomes split across multiple resources/systems.
- A milestone needs to edit more than its planned write set.
- The validation boundary moves deeper into runtime algorithms.
- Performance requirements force GPU skinning, parallelism, or cache redesign earlier than planned.

### Bevy Integration Contract

Resources:

```rust
struct ActiveHuman(pub Entity);
struct HumanAssetRegistry { handles: HashMap<String, Handle<HumanModelAsset>> }
struct HumanViewportSettings { show_skeleton: bool, show_weights: bool, show_markers: bool }
```

Components:

```rust
struct HumanInstance { model: Handle<HumanModelAsset> }
struct HumanMorphState { weights: Vec<f32> }
struct HumanPoseState { pose: PoseState }
struct HumanMeshDirty;
struct HumanSkeletonDirty;
```

Systems:

```text
load_human_assets
spawn_human_instance
update_morph_state
rebuild_shaped_mesh_when_dirty
evaluate_pose_when_dirty
skin_mesh_cpu_when_dirty
sync_mesh_to_bevy
draw_skeleton_gizmos
draw_weight_debug_overlay
```

Rules:

- UI changes update `HumanMorphState` or `HumanPoseState`, then mark dirty components.
- Core systems compute shaped/skinned buffers.
- Render sync writes into Bevy mesh assets.
- Do not perform string lookup in per-frame Bevy systems.

### Build Order Gates

Do not begin a later gate until the previous gate has passing unit tests:

1. Canonical asset load and validation.
2. Morph application.
3. Rest skeleton and inverse bind matrices.
4. Weight normalization and top-4 packing.
5. CPU full-weight skinning.
6. CPU packed-weight skinning comparison.
7. Bevy static render.
8. Bevy morph slider render.
9. Bevy pose render.
10. Advanced features: GPU skinning, DQS, IK, state persistence tooling.

## Non-Goals For The First Version

- No biomechanical muscle/fat/skin simulation.
- No automatic rigging of arbitrary meshes.
- No automatic high-quality skin weighting.
- No arbitrary topology changes after morph targets are loaded.
- No support for reordered vertex buffers unless a mapping layer is explicitly provided.

## Core Constraint

Morph targets and weights depend on stable vertex indices. The importer must preserve the canonical base mesh vertex order or generate a stable remapping table and apply it consistently to:

- positions
- normals
- morph target vertex indices
- skin weights
- joint marker vertex groups
- attached asset mappings

If this is not preserved, targets and weights will deform the wrong vertices.

## Proposed Repository Structure

```text
crates/
  human_core/
    src/
      character.rs
      mesh.rs
      morph.rs
      rig_shape.rs
      skeleton.rs
      weights.rs
      skinning.rs
      pose.rs
      topology.rs
      diagnostics.rs
      formats/
        bvh.rs
  human_persistence/
    src/
      sqlite_project.rs
      migrations.rs
      human_model_repo.rs
      human_state_repo.rs
      skin_graph_repo.rs
      biomech_repo.rs
  human_bevy/
    src/
      plugin.rs
      assets.rs
      render.rs
      gizmos.rs
      ui.rs
      systems.rs
  human_fit/
    src/
      lib.rs
      pose_fit.rs
      shape_fit.rs
apps/
  viewer/
    src/main.rs
assets/
  samples/
docs/
  plans/
```

Keep `human_core` independent of Bevy where practical. Bevy should be the viewport, UI, app shell, and renderer integration. Core deformation logic should remain testable without starting a Bevy app.

`human_fit` is a later optional crate for fitting pose and shape parameters to a target mesh. It should not be part of the MVP runtime path, but it belongs in the planned workspace because fitting is a natural extension once the forward model is deterministic and testable.

## Runtime Data Model

### Character

Owns the loaded base data and current mutable state:

- `base_positions: Vec<Vec3>`
- `base_normals: Vec<Vec3>`
- `indices: Vec<u32>`
- `shaped_positions: Vec<Vec3>`
- `skinned_positions: Vec<Vec3>`
- `morph_values: HashMap<MorphId, f32>`
- `rig_shape: RigShapeModel`
- `skeleton: Skeleton`
- `weights: VertexWeights`
- `pose: Pose`

### Morph Target

Store morphs in sparse form:

```rust
struct MorphTarget {
    name: String,
    deltas: Vec<(u32, Vec3)>,
}
```

The shaped mesh is computed as:

```text
shaped_position[v] = base_position[v] + sum(target_delta[v] * target_weight)
```

Keep targets sparse on disk and in editing state. Dense arrays are useful only for selected hot paths, batched validation, or runtime upload. A later optimizer may cache active targets into dense `Vec<Vec3>` buffers, but the canonical storage should remain sparse because most targets affect only part of the mesh.

Morph evaluation pseudocode:

```rust
fn apply_morphs(base: &[Vec3], targets: &[MorphTarget], weights: &[f32]) -> Vec<Vec3> {
    let mut shaped = base.to_vec();
    for (target, weight) in targets.iter().zip(weights) {
        if *weight == 0.0 {
            continue;
        }
        for (vertex, delta) in &target.deltas {
            shaped[*vertex as usize] += *delta * *weight;
        }
    }
    shaped
}
```

### Rig Shape Model

For shape-dependent rigs, treat rig fitting as the same blendshape problem as mesh shaping.

Instead of recomputing every bone head/tail by repeatedly averaging marker vertices after each shape update, precompute the effect of every morph target on every bone endpoint:

```rust
struct RigShapeModel {
    template_heads: Vec<Vec3>,
    template_tails: Vec<Vec3>,
    head_deltas: Vec<BoneEndpointTarget>,
    tail_deltas: Vec<BoneEndpointTarget>,
}

struct BoneEndpointTarget {
    target_id: MorphId,
    deltas: Vec<(BoneId, Vec3)>,
}
```

For each bone endpoint and target:

```text
endpoint_delta[target, bone] =
    average(target_delta[v] for v in endpoint_marker_vertices[bone])
```

Then runtime rig fitting becomes:

```text
rest_head[bone] = template_head[bone] + sum(endpoint_head_delta[target, bone] * target_weight)
rest_tail[bone] = template_tail[bone] + sum(endpoint_tail_delta[target, bone] * target_weight)
```

This makes mesh shaping and skeleton shaping consistent. The same coefficients that produce `shaped_positions` also produce `rest_heads`, `rest_tails`, and rest bone matrices.

Practical implementation:

1. Parse canonical joint marker vertex lists.
2. Parse all morph targets that can affect shape.
3. At import/preprocess time, compute and cache per-target head/tail endpoint deltas.
4. At runtime, update endpoint positions by weighted sums instead of scanning marker vertices.
5. Keep a slow direct-marker recompute path behind a debug flag to validate the cache.

This should become the default path once validated. The direct-marker averaging path remains useful for debugging imported data and for early bring-up.

### Skeleton

The skeleton is loaded from `SkeletonAsset` and contains:

- named joints
- joint marker vertex lists
- bones
- parent indices
- head and tail joint names
- rotation plane metadata
- source and weight-source metadata
- rest local/global transforms
- inverse bind matrices
- pose local/global transforms

Joint positions can be computed from the current shaped mesh by averaging marker vertices from canonical joint marker definitions.

For the MVP, direct marker averaging is acceptable. After the rig-shape cache is implemented, the skeleton should usually get endpoint positions from `RigShapeModel`. The skeleton still owns hierarchy, roll, parent indices, rest matrices, inverse bind matrices, and pose matrices.

Rest bone matrix construction:

```rust
fn bone_rest_global(head: Vec3, tail: Vec3, roll: f32) -> Mat4 {
    let y = (tail - head).normalize();
    let seed = if y.dot(Vec3::Y).abs() > 0.95 { Vec3::X } else { Vec3::Y };
    let mut x = seed.cross(y).normalize();
    let mut z = x.cross(y).normalize();

    if roll != 0.0 {
        let q = Quat::from_axis_angle(y, roll);
        x = q * x;
        z = q * z;
    }

    Mat4::from_cols(
        x.extend(0.0),
        y.extend(0.0),
        z.extend(0.0),
        head.extend(1.0),
    )
}

fn compute_rest_locals(rest_global: &[Mat4], parents: &[Option<BoneId>]) -> Vec<Mat4> {
    rest_global.iter().enumerate().map(|(bone, global)| {
        match parents[bone] {
            None => *global,
            Some(parent) => rest_global[parent].inverse() * *global,
        }
    }).collect()
}
```

Inverse bind matrices:

```rust
inverse_bind[bone] = rest_global[bone].inverse()
```

Rest-pose skinning identity check:

```text
posed_global = rest_global
skin_matrix = posed_global * inverse_bind
skin_matrix should be identity for every deforming bone
skinned_position should equal shaped_position within epsilon
```

Use this armature split as the runtime model:

- `RestBone`: imported or fitted rest data. This changes when shape sliders change enough to require rig refit.
- `PoseChannel`: per-instance pose data. This changes during animation, interactive posing, IK, or pose import.
- `SkinMatrices`: derived cache used by deformation. This changes after either rest data or pose data changes.

Do not let imported weights, morph targets, or UI state directly mutate skinning output. The path should be:

```text
morph coefficients -> shaped mesh + rest bone endpoints
rest bone endpoints -> rest_local/rest_global/inverse_bind
pose input -> pose_channels -> pose_global
pose_global + inverse_bind -> skin matrices
skin matrices + weights + shaped mesh -> skinned mesh
```

This makes rest-pose updates and pose updates testable as separate steps.

### Pose Parameterization

Define pose spaces explicitly so Bevy UI, saved pose state, clip playback, and future fitting code do not silently disagree.

Supported pose parameterizations:

- `RestRelative`: each bone parameter is a local delta from that bone's current rest pose.
- `RootRelative`: the root parameter is an absolute/root pose; child parameters are local deltas.
- `RootRelativeWorld`: root translation is interpreted in world/model space, while root rotation is applied relative to the root rest orientation.
- `Absolute`: every bone parameter is an absolute world/model-space bone pose.

Runtime storage should prefer `RestRelative` or `RootRelativeWorld`. Project loaders can convert from `Absolute` only when that space is explicitly marked in the SQLite pose record.

Practical implementation:

```rust
enum PoseSpace {
    RestRelative,
    RootRelative,
    RootRelativeWorld,
    Absolute,
}

struct Pose {
    space: PoseSpace,
    local_or_absolute: Vec<Mat4>,
}
```

Add conversion functions:

```text
pose_to_global(rest_poses, pose, parents) -> global_poses
global_to_pose(rest_poses, global_poses, target_space) -> Pose
```

Tests should verify that converting a pose through each supported space and back keeps skinned vertices within a small epsilon.

Absolute pose conversion must be explicit because fitted poses, imported animation, and editor gizmos often produce global bone matrices. Conversion rule:

```text
absolute_global[bone] = supplied global/model-space bone matrix
skin_matrix[bone] = absolute_global[bone] * inverse(rest_global[bone])

rest_relative_local[root] =
    inverse(rest_global[root]) * absolute_global[root]

rest_relative_local[child] =
    inverse(rest_local[child]) *
    inverse(absolute_global[parent]) *
    absolute_global[child]
```

After conversion, extract rotation with orthonormalization, normalize the quaternion, and keep translation only for the root unless the pose space explicitly supports per-bone translation. Report a diagnostic if an absolute matrix contains non-uniform scale or shear.

MVP pose evaluation should support rest-relative local rotations first:

```rust
fn evaluate_pose(
    rest_local: &[Mat4],
    parents: &[Option<BoneId>],
    local_rotation: &[Quat],
    root_translation: Vec3,
) -> Vec<Mat4> {
    let mut posed_global = vec![Mat4::IDENTITY; rest_local.len()];

    for bone in 0..rest_local.len() {
        let delta = Mat4::from_quat(local_rotation[bone].normalize());
        let mut local = rest_local[bone] * delta;
        if parents[bone].is_none() {
            local = Mat4::from_translation(root_translation) * local;
        }
        posed_global[bone] = match parents[bone] {
            None => local,
            Some(parent) => posed_global[parent] * local,
        };
    }

    posed_global
}
```

This convention means a local rotation is applied after the bone's rest local transform. If later tests show this is unintuitive for animation import, add a conversion layer rather than changing the runtime convention silently.

### Weights

The canonical weights asset maps:

```text
bone name -> [(vertex index, weight)]
```

Runtime processing:

1. Build per-vertex total weight.
2. Clamp negative weights to zero and report them.
3. Merge duplicate bone/vertex entries.
4. Drop weights less than or equal to `1.0e-4`.
5. Normalize every vertex's remaining weights.
6. Assign fully unweighted vertices to the root bone.
7. For GPU skinning, keep the top 4 influences per vertex and renormalize.
8. For CPU validation, keep the full influence set.

Store two representations:

- `FullVertexWeights`: arbitrary number of influences per vertex, used for CPU validation and quality baseline.
- `PackedVertexWeights4`: top-4 influences per vertex, used for Bevy/GPU paths.

The packer must sort influences by descending weight, keep the top 4, renormalize, and report dropped weight per vertex. This gives a concrete quality diagnostic instead of silently losing deformation fidelity.

Map vertex group or weight names to pose bones by name at import time:

1. Parse `WeightsAsset` as bone-name keyed weights.
2. Resolve every bone name to `BoneId`.
3. Store missing-bone links as import diagnostics.
4. Convert name-keyed weights to dense `BoneId` indices before runtime.
5. Keep sparse full weights for CPU validation.
6. Keep packed top-4 weights for GPU/Bevy paths.

Runtime skinning should never perform string lookups. Name matching is an import/preprocess concern.

Weight normalization pseudocode:

```rust
fn normalize_weights(weights: &mut Vec<(BoneId, f32)>, root: BoneId) {
    const MIN_WEIGHT: f32 = 1.0e-4;

    for (_, weight) in weights.iter_mut() {
        if *weight < 0.0 {
            *weight = 0.0;
        }
    }
    weights.retain(|(_, w)| *w > MIN_WEIGHT);
    weights.sort_by_key(|(bone, _)| *bone);

    let mut merged = Vec::new();
    for (bone, weight) in weights.drain(..) {
        if let Some((last_bone, last_weight)) = merged.last_mut() {
            if *last_bone == bone {
                *last_weight += weight;
                continue;
            }
        }
        merged.push((bone, weight));
    }

    let sum: f32 = merged.iter().map(|(_, w)| *w).sum();
    if sum <= 0.0 {
        *weights = vec![(root, 1.0)];
    } else {
        *weights = merged.into_iter().map(|(b, w)| (b, w / sum)).collect();
    }
}
```

If weight normalization changes a vertex by more than `WEIGHT_SUM_EPSILON`, report the pre-normalization sum in diagnostics. If more than four influences are present, the packed representation must record both `dropped_weight` and `dropped_count` so the editor can flag vertices that may deform differently on the GPU path.

Top-4 packing pseudocode:

```rust
fn pack_top4(full: &[(BoneId, f32)]) -> PackedWeights4 {
    let mut sorted = full.to_vec();
    sorted.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

    let mut joints = [0u16; 4];
    let mut weights = [0.0f32; 4];
    for (slot, (bone, weight)) in sorted.iter().take(4).enumerate() {
        joints[slot] = bone.0 as u16;
        weights[slot] = *weight;
    }

    let kept: f32 = weights.iter().sum();
    if kept > 0.0 {
        for weight in &mut weights {
            *weight /= kept;
        }
    }

    PackedWeights4 { joints, weights, dropped_weight: 1.0 - kept }
}
```

### Topology And Rig Variants

Model creation can support rig and topology variants such as default, no toes, game-engine, optional eyes/tongue, and reduced topology. For this Rust project, variants should be treated as import profiles:

```rust
struct CharacterImportProfile {
    topology: TopologyProfile,
    rig: RigProfile,
    include_eyes: bool,
    include_tongue: bool,
    remove_bones: Vec<String>,
    triangulate: bool,
    remove_unattached_vertices: bool,
}
```

MVP profile:

- one canonical topology
- one default rig
- no vertex removal
- no topology reduction

Later profiles:

- game-engine rig
- third-party animation-service rig profile
- no-toes rig
- no-expression rig
- triangulated topology profile
- reduced topology profile

Every profile must produce a stable remapping report showing how original vertex indices map to runtime vertex indices. If targets or weights use original vertices, remapping must be explicit and tested.

## Deformation Pipeline

### Armature Evaluation Boundary

Follow a strict separation between pose evaluation and deformation:

1. Rest skeleton evaluation produces `rest_global` and `inverse_bind`.
2. Pose evaluation produces `pose_global`.
3. Deformation cache generation produces `skin_matrix`.
4. Mesh skinning applies `skin_matrix` to shaped vertices using weights.

The skinning code should not know whether a pose came from:

- manual editor rotation
- BVH import
- a keyframed animation clip
- an IK solver
- a future fitting solver
- a future biomechanical motion source

It should receive evaluated matrices and weights only.

### Shape Update

Triggered when a slider or preset changes.

1. Reset `shaped_positions` to `base_positions`.
2. Apply all active morph target deltas.
3. Apply the same active morph coefficients to `RigShapeModel` endpoint deltas.
4. Recompute skeleton rest transforms and inverse bind matrices from shaped endpoints.
5. Recompute normals if CPU rendering path needs them.
6. Recompute attached asset positions, if attached assets are enabled.
7. Mark Bevy mesh buffers dirty.

Debug validation path:

1. Recompute joint endpoints by averaging marker vertices on `shaped_positions`.
2. Compare those endpoints against `RigShapeModel` endpoint output.
3. Report max and mean endpoint error.
4. Fail tests if a known sample exceeds tolerance.

Posed edit preview is a separate editor feature. The canonical update path always applies morphs in rest/model space and then reapplies pose. If an editor offers live target painting or slider preview on an already posed character, the implementation must either rebuild through the canonical rest-space path or transform the preview delta through the current weighted skinning transform before displaying it. Preview-space deltas must not be saved as canonical morph deltas unless they are converted back to rest/model space.

### Attached Asset Weight Transfer

Attached meshes such as simple clothing, hair cards, or proxy geometry should not require hand-authored weights for every prototype. Support an optional barycentric binding from attached vertices to base mesh vertices:

```rust
struct AttachedVertexBinding {
    attached_vertex: u32,
    base_vertices: [u32; 3],
    barycentric_weights: [f32; 3],
}
```

Weight transfer:

```text
attached_weight[bone] =
    sum(base_weight[base_vertex_i, bone] * barycentric_weight_i)
```

After transfer, merge duplicate bone influences, drop small weights using the same `1.0e-4` threshold, normalize, and pack top-4 weights if the attached asset uses the GPU-compatible path. If an attached vertex has no valid binding, assign it to the nearest base vertex by distance and report a warning.

### Pose Update

Triggered when pose data changes or animation advances.

1. Parse or convert pose data into the selected `PoseSpace`.
2. Convert pose parameters to local/channel transforms.
3. Evaluate the hierarchy from parent to child to produce global bone poses.
4. Compute skin matrices:

```text
skin_matrix[bone] = global_pose[bone] * inverse_bind[bone]
```

5. Skin mesh on CPU for the MVP, or upload joint matrices for GPU skinning later.

The kinematic tree can be evaluated sequentially for the MVP. Later, group bones by propagation depth so independent bones at the same depth can be processed in parallel. Each group contains bones whose parents have already been evaluated.

### CPU Skinning MVP

Use CPU skinning first because it is easier to validate:

```text
skinned_position[v] = sum((skin_matrix[b] * shaped_position[v]) * weight[v,b])
```

Then write updated positions into the Bevy `Mesh` asset.

This is acceptable for the first version because the base human mesh is roughly editor-scale, not crowd-scale.

Use `FullVertexWeights` for the CPU validation path. This gives a high-quality baseline before top-4 packing or GPU skinning is introduced.

The CPU path should support two validation modes:

- `FullWeightsLbs`: use every imported influence. This is the baseline result.
- `PackedWeightsLbs`: use top-4 influences. This matches the future GPU path.

Every sample character should report max and mean positional error between these modes for at least rest pose and one non-trivial pose.

CPU skinning pseudocode:

```rust
fn skin_positions(
    shaped: &[Vec3],
    weights: &[Vec<(BoneId, f32)>],
    skin_matrices: &[Mat4],
) -> Vec<Vec3> {
    let mut out = vec![Vec3::ZERO; shaped.len()];
    for vertex in 0..shaped.len() {
        let mut p = Vec3::ZERO;
        for (bone, weight) in &weights[vertex] {
            p += skin_matrices[bone.0].transform_point3(shaped[vertex]) * *weight;
        }
        out[vertex] = p;
    }
    out
}
```

Normal skinning pseudocode:

```rust
fn skin_normals(
    normals: &[Vec3],
    weights: &[Vec<(BoneId, f32)>],
    skin_matrices: &[Mat4],
) -> Vec<Vec3> {
    let mut out = vec![Vec3::Y; normals.len()];
    for vertex in 0..normals.len() {
        let mut n = Vec3::ZERO;
        for (bone, weight) in &weights[vertex] {
            n += skin_matrices[bone.0].transform_vector3(normals[vertex]) * *weight;
        }
        out[vertex] = if n.length_squared() > 1.0e-12 { n.normalize() } else { Vec3::Y };
    }
    out
}
```

### GPU Skinning Later

After CPU correctness is proven:

- Pack top 4 joints into a mesh attribute.
- Pack top 4 weights into a mesh attribute.
- Upload joint matrices to Bevy's skinned mesh path or a custom material/shader.
- Keep morph target application CPU-side when sliders change.
- Use GPU only for per-frame pose animation.

### Dual Quaternion Skinning Later

DQS can reduce volume loss and twisting artifacts around shoulders, hips, elbows, and wrists.

Plan:

1. Keep LBS as the baseline because it is simple, stable, and maps directly to Bevy mesh skinning inputs.
2. Add DQS as an optional CPU validation path after MVP.
3. Compare LBS and DQS visually on twist-heavy poses.
4. Only add GPU DQS if it materially improves deformation quality for our target content.

This is a quality option, not a blocker for the first useful prototype.

### Envelope And Heat Weighting Tools Later

Two useful authoring-side weighting ideas:

- Envelope weighting: compute bone influence from distance to a bone segment with head/tail radii and falloff.
- Heat/Laplacian weighting: solve a mesh-based diffusion problem to assign smoother automatic weights.

These should not replace canonical authored weights in the MVP. They are useful later as repair and authoring tools:

1. Diagnose unweighted vertices or missing bone weights.
2. Generate temporary fallback weights for experimental rigs.
3. Smooth or repair imported weights in selected regions.
4. Compare authored weights against generated weights to find suspicious regions.

Keep these tools offline or editor-only. Runtime character playback should use precomputed weights.

## Diagnostics And Validation Tools

The runtime should include explicit diagnostics for shape, rig, and skinning quality.

### Weight Diagnostics

Report:

- max influences per vertex before packing
- max influences per vertex after packing
- total dropped weight per vertex
- vertices assigned to root because they had no weights
- bones with no weighted vertices
- weights referencing missing bones

### Rig Shape Diagnostics

Report:

- endpoint error between direct marker averaging and rig-shape cache
- bones with zero or near-zero length
- bones with invalid parent links
- bones with unstable orientation because head-tail direction is degenerate

For degenerate orientation cases, define a fallback axis or fallback rotation, then test continuity under tiny shape perturbations.

### Self-Intersection Diagnostics

Self-intersection is not part of the MVP deformation path, but it is useful in an editor. Add a later diagnostic mode:

1. Triangulate the current mesh.
2. Build rough collision masks from dominant bone influence groups.
3. Skip triangle pairs that are expected to be adjacent or part of the same body region.
4. Report candidate intersections for bad poses or extreme morphs.

This can be CPU first. GPU acceleration is optional.

### Golden Reference Dumps

Create canonical golden dumps from the project's own fixtures:

- rest vertices
- active morph coefficients
- shaped vertices
- bone heads/tails
- rest bone matrices
- posed bone matrices
- skinned vertices

The Rust implementation should compare against those dumps before we trust the Bevy viewport.

## Bevy Integration

Implement a `HumanRuntimePlugin` with systems for:

- loading character assets
- updating morph state from UI
- rebuilding shaped mesh buffers
- updating skeleton transforms
- applying pose/animation
- drawing skeleton gizmos
- drawing joint markers for debugging
- syncing final mesh data into Bevy render assets

Initial app controls:

- load sample character
- morph sliders for a small target subset
- reset shape
- toggle skeleton display
- apply rest pose
- apply one test pose
- play/pause one BVH animation after BVH support lands
- choose pose parameterization for debug display
- toggle full-weight CPU skinning versus packed-weight skinning once both exist
- show rig endpoint error overlay after rig-shape cache lands

## Milestones

### Milestone 0: Repository Scaffold

- Create Cargo workspace.
- Add `human_core`, `human_bevy`, and `apps/viewer`.
- Add Bevy 0.18 dependency.
- Add `serde`, `rusqlite`, and math dependencies as needed.
- Add minimal CI commands later: format, clippy, test.

### Milestone 1: Canonical Model Load

- Load a known `.human.sqlite` project without changing vertex order.
- Preserve metadata needed for joint marker groups.
- Display static base mesh in Bevy.
- Add a diagnostic that reports vertex count and known joint marker groups.

### Milestone 2: Morph Targets

- Load sparse morph targets from the `human_models` records in `.human.sqlite`.
- Apply one target to the base mesh.
- Add a slider UI for target weight.
- Add tests for sparse delta application.
- Validate against canonical fixture output for a known slider value.

### Milestone 3: Skeleton Loader And Direct Rig Fitting

- Parse canonical `SkeletonAsset`.
- Build bone hierarchy.
- Compute joint positions from shaped mesh marker vertices.
- Compute bone rest transforms and inverse bind matrices.
- Add `RestBone`, `PoseChannel`, and `ArmatureInstance` data structures.
- Define and test bone/rest local, armature/model rest, pose/model, and channel/local transform spaces.
- Draw skeleton lines/gizmos in Bevy.

### Milestone 4: Rig Shape Cache

- Precompute template bone heads/tails from marker vertices.
- Precompute per-target bone head/tail deltas.
- Update rest endpoints using active morph coefficients.
- Keep direct marker averaging as validation path.
- Add endpoint-difference diagnostics.
- Add tests for equivalence between direct marker averaging and cached endpoint deltas.

### Milestone 5: Weight Loader

- Parse canonical `WeightsAsset`.
- Resolve bone-name keyed weights to `BoneId` at import time.
- Normalize per-vertex weights.
- Assign unweighted vertices to root.
- Keep full CPU weights and packed top-4 GPU weights.
- Report dropped weight from top-4 packing.
- Add validation reports:
  - max influences per vertex
  - unweighted vertex count
  - total weight error per vertex
  - missing bone links

### Milestone 6: CPU Skinning

- Apply rest pose and confirm no visible deformation.
- Apply a simple manually-authored pose.
- Skin mesh on CPU using full weights.
- Add optional packed-weight CPU skinning and compare with full-weight output.
- Keep pose evaluation and mesh deformation as separate systems.
- Add a debug mode that shows per-bone skin matrices and dominant vertex influences.
- Recompute normals or transform normals.
- Add debug views for problematic vertices.

### Milestone 7: Pose Parameterizations And BVH Support

- Implement `RestRelative`, `RootRelative`, `RootRelativeWorld`, and `Absolute` pose spaces.
- Add conversion tests between pose spaces.
- Parse a minimal BVH file.
- Map BVH joint names to skeleton bone names.
- Apply frame 0 as static pose.
- Add playback loop.
- Add root motion handling as a separate toggle.

### Milestone 8: Bevy Editor UX

- Add organized panels for shape, rig, pose, diagnostics.
- Add skeleton visibility controls.
- Add selected bone/joint inspection.
- Add current vertex/weight debug inspection.
- Add save/load for character state.

### Milestone 9: State Persistence

- Save current character parameters into a `human_states` record in `.human.sqlite`.
- Load a saved `human_states` record, resolve its model id, regenerate shape and pose, and upload the resulting mesh to Bevy.
- Add round-trip tests proving morph values, pose inputs, active clip time, and viewport options survive serialization.
- Add a debug-only in-memory mesh snapshot path for tests; it is not a persistent user file.

### Milestone 10: Attached Assets

- Load clothes/proxy meshes.
- Support explicit `vertexboneweights_file` where available.
- Otherwise approximate asset weights from base mesh barycentric mappings.
- Skin assets with the same skeleton.
- Add intersection and fit diagnostics later.

### Milestone 11: Alternative Rigs And Topologies

- Add import profiles for optional eyes/tongue and no-toes variants.
- Add game-engine or third-party animation-service rig profiles if source data is available.
- Add topology profiles only if they preserve or explicitly remap canonical vertex ids.
- Require vertex remapping reports for any topology that removes or reorders vertices.
- Validate all profiles with morph, rig-shape, and skinning tests.

### Milestone 12: Diagnostics And Fitting

- Add self-intersection diagnostics for posed/shaped meshes.
- Add shape/pose golden dumps for comparison against canonical fixtures.
- Add an optional `human_fit` crate for fitting pose and shape parameters to target vertices.
- Keep fitting offline/tooling-focused; do not block runtime/editor stability on it.

### Milestone 13: Advanced Authoring Tools

- Add envelope-weight preview for selected bones.
- Add a weight repair mode for unweighted or weakly weighted vertices.
- Add optional heat/Laplacian weighting research prototype if imported weights are insufficient for custom rigs.
- Add structural checks for skeleton hierarchy, inverse bind matrices, and top-4 weights.
- Evaluate dual-quaternion skinning on twist-heavy test poses and decide whether it is worth adding to GPU runtime.

## Testing Strategy

Minimum self-contained fixture:

```text
vertices:
  0: [-0.5, 0.0, 0.0]
  1: [ 0.5, 0.0, 0.0]
  2: [ 0.0, 1.0, 0.0]
  3: [ 0.0, 2.0, 0.0]
triangles:
  [0, 1, 2]
  [1, 0, 3]
bones:
  root: parent none, head [0,0,0], tail [0,1,0], roll 0
  child: parent root, head [0,1,0], tail [0,2,0], roll 0
weights:
  vertices 0,1,2 -> root 1.0
  vertex 3 -> child 1.0
morph:
  move_top: vertex 3 delta [0,0.5,0]
pose:
  root identity, child identity
```

Expected results:

- Applying `move_top` at weight `1.0` moves vertex `3` to `[0,2.5,0]`.
- Rest-pose skinning returns every shaped vertex unchanged within `1.0e-5`.
- Top-4 packing drops `0.0` weight for every vertex in this fixture.
- A child rotation of 90 degrees around `+Z` moves vertex `3` around the child bone head while root-only vertices remain root-skinned.

Unit tests:

- target parsing
- sparse morph application
- rig-shape endpoint delta generation
- canonical skeleton parsing
- joint position averaging
- canonical weight parsing
- weight normalization
- top-4 packing
- skin matrix calculation
- pose parameterization conversion
- armature rest/pose/channel space conversion
- rest-pose skinning identity check
- degenerate bone orientation fallback

Golden tests:

- load a known canonical sample
- apply known morph weights
- compare selected vertex positions to a golden dump
- compare joint positions to a golden dump
- compare rig-shape cached endpoints to direct marker endpoints
- compare full-weight CPU skinning to packed-weight CPU skinning and report error
- compare Rust output to canonical golden output for one neutral shape and one posed shape

Visual tests:

- rest pose should match shaped mesh with no deformation
- skeleton should line up with body landmarks
- single-bone rotations should affect expected regions
- left/right limbs should deform symmetrically

## Advanced Self-Contained Runtime Specs

These features are not required for the first useful prototype. Do not add them until the MVP path is covered by tests.

### Dual Quaternion Skinning

Purpose:

- Reduce volume loss during twist-heavy rotations.
- Keep linear blend skinning as the compatibility baseline.
- Allow per-character or per-region selection between LBS and DQS.

Data type:

```rust
struct DualQuat {
    real: Quat,
    dual: Quat,
}
```

Build a unit dual quaternion from rotation `r` and translation `t`:

```rust
fn dual_quat_from_rotation_translation(r: Quat, t: Vec3) -> DualQuat {
    let real = r.normalize();
    let t_quat = Quat::from_xyzw(t.x, t.y, t.z, 0.0);
    let dual = mul_quat(t_quat, real) * 0.5;
    DualQuat { real, dual }
}
```

Quaternion multiplication must follow the same convention everywhere. If using `glam::Quat`, wrap multiplication in a helper and test it with identity, 90-degree rotation, and pure translation cases.

Convert a skin matrix to a dual quaternion:

1. Extract rotation from the upper-left 3x3 matrix.
2. Orthonormalize the rotation if scale/shear is present.
3. Extract translation from the matrix translation column.
4. Build `DualQuat`.

DQS accumulation:

```rust
fn blend_dual_quats(influences: &[(DualQuat, f32)]) -> DualQuat {
    let mut real = Quat::from_xyzw(0.0, 0.0, 0.0, 0.0);
    let mut dual = Quat::from_xyzw(0.0, 0.0, 0.0, 0.0);
    let mut baseline: Option<Quat> = None;

    for (dq, weight) in influences {
        let mut r = dq.real;
        let mut d = dq.dual;
        if let Some(baseline) = baseline {
            if quat_dot(baseline, r) < 0.0 {
                r = -r;
                d = -d;
            }
        } else {
            baseline = Some(r);
        }
        real += r * *weight;
        dual += d * *weight;
    }

    normalize_dual_quat(DualQuat { real, dual })
}
```

Dual quaternion normalization:

```rust
fn normalize_dual_quat(dq: DualQuat) -> DualQuat {
    let len = quat_length(dq.real).max(1.0e-8);
    DualQuat {
        real: dq.real / len,
        dual: dq.dual / len,
    }
}
```

Transforming a point:

```rust
fn transform_point_dq(dq: DualQuat, p: Vec3) -> Vec3 {
    let r = dq.real.normalize();
    let d = dq.dual;
    let rotated = r * p;
    let translation_quat = (d * r.conjugate()) * 2.0;
    let t = Vec3::new(translation_quat.x, translation_quat.y, translation_quat.z);
    rotated + t
}
```

Validation:

- A pure translation DQ moves `[1,2,3]` by exactly the translation within epsilon.
- A pure rotation DQ matches matrix rotation within epsilon.
- A single influence with weight `1.0` matches matrix skinning when the matrix contains only rotation and translation.
- Two opposite-signed quaternions for the same transform blend correctly after sign correction.

### GPU Skinning

Purpose:

- Move per-frame vertex deformation from CPU to GPU after CPU correctness is proven.
- Keep CPU skinning as the baseline validation path.

Mesh attributes:

```text
ATTRIBUTE_JOINT_INDEX: u16x4 or u32x4
ATTRIBUTE_JOINT_WEIGHT: f32x4
ATTRIBUTE_POSITION_BASE: f32x3
ATTRIBUTE_NORMAL_BASE: f32x3
```

Joint buffer:

```rust
struct GpuJoint {
    skin_matrix: Mat4,
}
```

Vertex shader LBS formula:

```wgsl
let m0 = joints[joint_indices.x].skin_matrix;
let m1 = joints[joint_indices.y].skin_matrix;
let m2 = joints[joint_indices.z].skin_matrix;
let m3 = joints[joint_indices.w].skin_matrix;

let p = vec4(base_position, 1.0);
let skinned =
    (m0 * p) * weights.x +
    (m1 * p) * weights.y +
    (m2 * p) * weights.z +
    (m3 * p) * weights.w;
```

Normal shader formula:

```wgsl
let n = vec4(base_normal, 0.0);
let skinned_normal =
    (m0 * n).xyz * weights.x +
    (m1 * n).xyz * weights.y +
    (m2 * n).xyz * weights.z +
    (m3 * n).xyz * weights.w;
normal = normalize(skinned_normal);
```

Rules:

- Weights must be normalized before upload.
- Missing influences use joint `0` and weight `0`.
- If all four weights become zero due to bad data, replace with root weight `1.0`.
- The CPU and GPU paths must share the same packed top-4 data.

Validation:

- Render a rest pose and compare CPU positions to a readback or debug CPU shader equivalent.
- Compare CPU full-weight, CPU packed-weight, and GPU packed-weight bounds.
- Report max error between CPU full-weight and CPU packed-weight before enabling GPU as default.

### Inverse Kinematics

Purpose:

- Let users pose limbs interactively.
- Keep IK separate from skinning. IK writes pose channels, and skinning consumes evaluated pose matrices.

MVP solver: cyclic coordinate descent.

Data:

```rust
struct IkChain {
    end_effector: BoneId,
    target_position: Vec3,
    bones: Vec<BoneId>, // ordered from end effector parent toward root
    iterations: usize,
    tolerance: f32,
}
```

CCD algorithm:

```rust
fn solve_ccd(chain: &IkChain, pose: &mut PoseState, skeleton: &Skeleton) {
    for _ in 0..chain.iterations {
        evaluate_pose_globals(pose, skeleton);
        let end_pos = end_effector_position(chain.end_effector, pose, skeleton);
        if end_pos.distance(chain.target_position) < chain.tolerance {
            break;
        }

        for bone in &chain.bones {
            let joint_pos = bone_head_position(*bone, pose, skeleton);
            let end_vec = (end_pos - joint_pos).normalize_or_zero();
            let target_vec = (chain.target_position - joint_pos).normalize_or_zero();
            if end_vec.length_squared() == 0.0 || target_vec.length_squared() == 0.0 {
                continue;
            }

            let axis = end_vec.cross(target_vec);
            let dot = end_vec.dot(target_vec).clamp(-1.0, 1.0);
            let angle = dot.acos();
            if axis.length_squared() < 1.0e-10 || angle.abs() < 1.0e-5 {
                continue;
            }

            let world_delta = Quat::from_axis_angle(axis.normalize(), angle);
            apply_world_rotation_to_local_pose(*bone, world_delta, pose, skeleton);
            clamp_joint_limits(*bone, pose, skeleton);
            evaluate_pose_globals(pose, skeleton);
        }
    }
}
```

Joint limit behavior:

- Store local Euler or swing/twist limits per bone.
- After applying an IK delta, convert the local rotation to the configured limit representation.
- Clamp to min/max.
- Convert back to a normalized quaternion.
- Report when clamping prevents the target from being reached.

Validation:

- Two-bone planar arm reaches a reachable target within tolerance.
- Solver stops gracefully when target is unreachable.
- Joint limits prevent impossible elbow/knee bending.
- Skinning result changes only through pose channels, not IK-specific deformation code.

### Animation Clip Runtime

Canonical internal animation format:

```rust
struct AnimationClip {
    name: String,
    seconds_per_frame: f32,
    bone_tracks: Vec<BoneTrack>,
}

struct BoneTrack {
    bone: BoneId,
    translations: Vec<Vec3>, // optional, root usually only
    rotations: Vec<Quat>,
    scales: Vec<Vec3>,       // optional, default one
}
```

Sampling:

```rust
fn sample_rotation(track: &BoneTrack, time: f32, clip: &AnimationClip) -> Quat {
    let frame = time / clip.seconds_per_frame;
    let i0 = frame.floor() as usize;
    let i1 = (i0 + 1).min(track.rotations.len() - 1);
    let t = frame.fract();
    track.rotations[i0].slerp(track.rotations[i1], t).normalize()
}
```

Looping:

- If looping is enabled, wrap sample time by clip duration.
- If not looping, clamp to the first or last frame.

Blending two clips:

```rust
rotation = rotation_a.slerp(rotation_b, blend_weight)
translation = translation_a.lerp(translation_b, blend_weight)
scale = scale_a.lerp(scale_b, blend_weight)
```

Validation:

- Sampling frame-exact times returns exact frame rotations.
- Sampling halfway between two frames produces expected slerp.
- Looping wraps without discontinuity for clips authored to loop.

### Bevy Mesh Upload Contract

Purpose:

- Convert canonical runtime results into Bevy mesh assets.
- Keep generated render buffers derived from model and state assets.
- Avoid treating a rendered mesh as persistent character data.

Uploaded data:

- Mesh positions, normals, uvs, indices.
- Top-4 joint indices and weights.
- Skeleton nodes in parent-before-child order where Bevy skinning needs them.
- Inverse bind matrices.
- Optional debug overlays for joints, weights, and markers.

Rules:

- Joint ids in mesh attributes must match the runtime skin joint order.
- Use the canonical `inverse_bind` from the runtime skeleton.
- Upload current skinned positions when using CPU skinning.
- Upload shaped positions plus skinning attributes when using Bevy/GPU skinning.
- Validate every vertex has normalized top-4 weights before GPU upload.
- Never save Bevy mesh buffers as the authoritative character file.

Acceptance test:

- Load the minimum `.human.sqlite` fixture and one saved `human_states` record.
- Regenerate the shaped and posed model.
- Upload to a Bevy `Mesh`.
- Confirm vertex count, index count, joint count, inverse bind count, and weights match the canonical preprocessed model.

### Weight Repair And Generation

Purpose:

- Fix incomplete or experimental weights without relying on external auto-weighting code.

Envelope weighting for one bone:

```rust
fn bone_capsule_weight(p: Vec3, head: Vec3, tail: Vec3, radius: f32, falloff: f32) -> f32 {
    let axis = tail - head;
    let len2 = axis.length_squared();
    if len2 <= 1.0e-10 {
        return 0.0;
    }
    let t = ((p - head).dot(axis) / len2).clamp(0.0, 1.0);
    let closest = head + axis * t;
    let d = p.distance(closest);
    if d <= radius {
        1.0
    } else if d >= radius + falloff {
        0.0
    } else {
        let x = (d - radius) / falloff;
        1.0 - x * x
    }
}
```

Weight generation:

1. For each vertex, compute capsule weight for every deform bone.
2. Drop weights below `1.0e-4`.
3. Normalize remaining weights.
4. If no weights remain, assign nearest bone by point-to-segment distance.
5. Run top-4 packing diagnostics.

Optional smoothing:

```text
for each smoothing iteration:
    new_weight[v,b] = lerp(weight[v,b], average_neighbor_weight_for_bone, smoothing_factor)
    normalize vertex weights
```

Validation:

- A vertex on a bone segment gets weight `1.0` before normalization.
- A vertex outside radius plus falloff gets weight `0.0`.
- Smoothing preserves per-vertex weight sum of `1.0`.

## Main Risks

- Mesh import or preprocessing reorders or splits vertices in a way that breaks target indices.
- More than 4 influences per vertex lose quality when packed for GPU.
- Canonical asset coordinate conventions differ from Bevy render conventions.
- Bone roll/orientation is easy to get subtly wrong.
- Degenerate bone directions can create unstable orientations or NaNs.
- Rest-pose recalculation after morph edits may invalidate cached inverse bind data if not handled carefully.
- Alternative topologies can break target and weight indices unless remapping is explicit.
- Clothes/proxy fitting is a separate hard problem and should not block the core runtime.

## Early Validation Checklist

- Vertex count matches canonical mesh metadata.
- Known joint marker names are present.
- Applying a head/arm/torso target moves the expected region.
- Skeleton gizmo aligns with body landmarks.
- Rig-shape cached endpoints match direct marker endpoints within tolerance.
- Rest pose skinning returns positions close to shaped positions.
- A simple arm raise affects shoulder, upper arm, forearm, and hand with plausible falloff.
- Full-weight and packed-weight skinning differences are measured and visible in diagnostics.
- Saved SQLite character state reloads and regenerates the same shaped and posed buffers within tolerance.

## Definition Of Done For First Useful Prototype

- A Bevy viewer opens a canonical human character.
- Sliders can change at least 10 morph targets.
- The skeleton updates after shape changes.
- The skeleton can update from the rig-shape cache, with direct marker validation available.
- A test pose can be applied.
- CPU skinning produces a visibly correct posed mesh.
- Diagnostics report weight and skeleton health.
- The current character parameters can be saved and reloaded, and the shaped/posed mesh is regenerated for inspection.
