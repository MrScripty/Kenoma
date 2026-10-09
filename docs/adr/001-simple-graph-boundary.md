# Simple graph milestone: ownership and interfaces

2026-10-09. Baseline: `596df78`; branch: `feat/simple-skin-graph`.

## Inventory before implementation

`README.md:4-11` identifies three separate tracks. The original non-simulation
designs are `docs/plans/procedural-skin-graph-plan.md` (graph model) and
`docs/plans/implementation-plan.md` (fixed topology morph/rig runtime).
Remote `main` was checked with `git ls-remote` on 2026-10-09 and matched
`596df78f5cb652b4ac70917a82d8aa908b617056`. This audit makes no claim about
unpublished work in other environments. At that baseline there are no Cargo manifests, `crates/`, graph assets, graph
commands, graph persistence or graph generator. Neither planned runtime is
implemented. `education/web/spatial.mjs:19` generates an educational spatial
specimen; `education/web/spatial.mjs:54` solves it. The two-bone skinning example
at `education/web/tissue.mjs:4` is not the planned editable graph or general
morph runtime. `education/web/anatomical-solver.mjs:3` is a numerical optimizer.
These are separate educational/research implementations, not completion of the
simple-tool plans.

## Written ownership boundary (established before code edits)

This milestone owns new root Cargo workspace files, `crates/human_core/`,
`crates/human_persistence/`, `assets/samples/skin_graph/`, and this ADR only.
It must not modify `education/`, existing plans, workflows, research data,
solver code, numerical thresholds, citations or artifacts. No dependencies
on those systems. No research campaigns, public push, merge or deployment.
Biomechanics owner: cloud thread `01a11158-716f-77a5-ac2c-c28e22eaa03c`.

`human_core` owns graph data, validation, diagnostics, editing/undo, generation
and a simple human sample. It has no UI, Bevy, SQLite, filesystem or physics
dependency. `human_persistence` owns its own versioned graph tables in SQLite;
it saves source parameters only, never mesh buffers. The future UI consumes
serializable graph commands and generated positions/normals/triangle indices
with source provenance. Source node IDs, not generated vertex IDs, drive edits.

## Scope and implementation decisions

Implement the headless foundation first: graph validation and roots, bounded
ring subdivision, transported frames, flat caps, overlap hubs, smooth normals,
atomic commands with undo/redo, branch rotation for posing, SQLite round trips,
canonical samples and a runnable headless example. Follow the original coordinate
conventions and use typed errors. Branch overlaps are intentionally not a welded
manifold. Correct outward winding takes precedence over the plan's ring-quad
pseudocode (whose order is inward for its stated frame cross product).

The browser GUI repository (Rheon or Kenoma) is pending root clarification.
Bevy picking/rendering and the separate fixed-topology morph/rig pipeline are
not claimed implemented in this milestone. No new anatomy or physics is needed.
Branch pose edits rotate a selected graph component around a pivot and preserve
edge lengths; ambiguous cycle cuts must fail rather than move unrelated nodes.

No AGENTS.md or local .agents skills were present. The plan's absolute external
Coding-Standards directory is unavailable in this environment. Its in-document
Rust safety, ownership, documentation and testing rules are followed; compliance
with the unavailable external documents cannot be independently verified.

## Dependency note

Use `glam` for vector/frame arithmetic, `serde` for a UI-facing value contract,
`thiserror` for typed errors, and `rusqlite` only in persistence. These are
explicitly preferred by the original plan. `glam` enables serde; `serde` enables
derive; rusqlite uses bundled SQLite for reproducible native builds. Alternatives
are hand-written math/errors/serialization and system SQLite; these increase
maintenance or platform variation. Transitive risks are procedural macros and
the bundled native SQLite compilation, isolated from the core. Removal paths:
replace public vector serialization at an adapter boundary, implement errors
manually, or replace only persistence. Pin the resolved graph with Cargo.lock.
Core remains suitable for a later WASM adapter; SQLite stays outside it.

## Milestone implementation refinements

The initial geometry uses independently capped tubes plus ellipsoid overlap
hubs at degree-two bends as well as branch nodes. Tubes start at the node center
instead of offsetting branch rings: this avoids reversed tubes on short edges
and makes every component independently closed. This is a deliberate documented
simplification, not a manifold or welded chain implementation. Roots still seed
transported frames; loop approximation is diagnosed. Unsupported advanced modes
are omitted from the options contract instead of accepted and silently ignored.

`serde_json` is additionally used only by persistence to encode the plan's
`generation_options_blob`; it is also a core dev-dependency for UI-contract tests.
It has no core runtime or research dependency. Its alternative is a handwritten
versioned codec; replace that adapter if a different blob representation is needed.

Independent read-only review found large-axis rotation, multi-root traversal,
future-record overwrite and multi-query snapshot issues. All four were corrected
and regression tests added. The reviewer confirmed outward winding and separation
from research. Final verification results are recorded in the completion report.

## Verified completion (2026-10-09)

Implemented source references:

- `crates/human_core/src/types.rs`: graph, generation options, typed diagnostics,
  resource bounds and serializable generated buffers.
- `crates/human_core/src/validation.rs`: boundary validation and island roots.
- `crates/human_core/src/edit.rs`: graph commands, branch posing, atomic rollback,
  conflict-detecting undo/redo.
- `crates/human_core/src/generate.rs`: ring tubes, caps, transported frames,
  overlap hubs, provenance and area-weighted normals.
- `crates/human_core/src/samples.rs`: schematic human and canonical small graphs.
- `crates/human_persistence/src/lib.rs`: atomic SQLite source storage and snapshot
  reads, version checks and validation.
- Crate READMEs: executable usage and serialized UI contract.

Passed with Rust 1.99.0:

- `cargo fmt --all -- --check`
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`
- `cargo test --workspace` (21 integration tests and 1 doctest)
- `cargo test --workspace --doc`
- `cargo check --workspace --all-features`
- `cargo check --workspace --no-default-features`
- `cargo check -p human_core --target wasm32-unknown-unknown`
- Canonical sample creation example; human output: 820 vertices, 1536 triangles.
- Independent read-only review and independent rerun of the workspace tests.

No existing tracked file was changed. No research test/campaign was run because
there is no dependency on or change to that subsystem. Bevy/browser rendering,
JavaScript/WASM bindings, loose-branch flags, full morph/rig runtime and GUI
placement are still open. This completes the scoped headless minimum, not all
features of either original design. No public push or deployment is authorized.
