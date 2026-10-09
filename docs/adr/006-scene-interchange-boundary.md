# Versioned scene source interchange

Baseline136f4947c7ef9bd2d4fe5cff09086489b0cb501d. Implement explicit local scene
file export/import for the existing browser authoring editor. This follows the
native persistence principles: versioned source records, validated atomic
replacement, no generated geometry/history. It does not replace the native
SQLite project format or add research persistence, accounts or external storage.
The original plans (implementation-plan.md:106,173) require SQLite files.
A versioned source envelope is stored inside a dedicated SQLite scene table;
JSON is an internal record encoding, not another user project-file format.
The browser vendors a local SQLite WASM adapter without research dependencies. Reload restoration uses a saved file;
automatic browser storage is outside this bounded change.

Ownership established before edits:
- rig_math: new scene-file.js and scene-file.test.mjs, plus scene-state.js atomic
  replace integration; pure headless parsing/validation/source reconstruction.
- scene_ui: new scene-files-ui.js and minimal index.html/editor.css controls;
  file selection/download, cancellation/stale-read lifecycle. Coordinate API.
- parent: SQLite scene-archive.js adapter/vendor, demo integration, public
  embedding docs/types, browser acceptance tests,
  independent review coordination, commit/push/remote verification.
- reviewer: read-only. No renderer, WASM, research, deployment or security changes.

Acceptance: multiple character IDs/names/colors/placement/head/IK targets+poles,
selection and next-ID allocation round-trip; regenerated pose equality; repeated
save/load after page reload; empty scene; unknown/future versions and malformed,
overlarge, duplicate-ID, invalid-vector/transform data rejected without mutation.
Cancelled/stale asynchronous file reads preserve current edits. A valid import
is one undoable replacement; no partial character updates. Compact Save/Open
controls work on desktop and phone without sliders or large explanation panels.
