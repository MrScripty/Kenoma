# Scene files and embedding contract, version 1

**Save** downloads a new `scene.human.sqlite` source snapshot. **Open** replaces
the current scene after validating the complete file. Import is one undoable edit.
Save before reloading, then Open the file to restore your work. There is no
implicit autosave, account, server or browser-storage dependency.

This extends the original SQLite persistence design with a scene-owned namespace.
It does not change native `skin_graph_*` records or research records. Imports
read a private in-memory copy and leave the input file and unrelated tables
untouched. Export writes a new **scene-only** database; it is not a full-project
rewrite or an update to the imported file's other assets.

## What survives

Character IDs/names, colors, root position/yaw, head yaw/pitch, all limb targets
and poles, exact validated 16-node source poses, selected character and the next
ID counter. Generated meshes, rig bindings, renderer objects and undo history are
omitted. Camera view and selected gizmo are not stored; Open frames the scene.
The current session's ID allocator never decreases, even after importing an older
file or undoing an import. An imported next-ID counter may therefore be raised.

The limits are 64 characters, 4 MiB per SQLite file, 1 MiB UTF-8 source text and
finite source coordinates/angles within the existing ±1,000,000 model limits.
Names contain 1–128 characters; colors are six-digit hex. Duplicate IDs, missing
fields, unknown fields, invalid selection/counter, inconsistent poses and future
versions fail before mutation. Pose points must agree with canonical IK targets
within 1e-8; validated authored floats are retained exactly across round trips.

## SQLite container

Use these canonical table definitions (case and whitespace normalization are
accepted; other layouts require a future explicit migration):

```sql
CREATE TABLE skin_scene_schema (version INTEGER NOT NULL);
CREATE TABLE skin_scenes (id INTEGER PRIMARY KEY, record_version INTEGER NOT NULL, source_json TEXT NOT NULL);
```

There is exactly one schema row, `version=1`, and one scene row, `id=1` and
`record_version=1`. `source_json` is TEXT containing the internal source envelope
below. This is an internal record encoding, not a separate JSON project format.
The database-wide `user_version` is unused, as in native graph persistence.
Future container/record/source/rig versions are rejected without overwriting
anything; current version1 files remain supported. Older graph-only projects
without a posing scene produce a clear error and leave the current scene intact.

```js
{
  format: 'kenoma.scene-source', version: 1, rigVersion: 1,
  characters: [{
    id: 'character-1', name: 'Character 1', color: '#61b9b2',
    position: [0,0,0], yaw: 0, head: {yaw:0,pitch:0},
    rig: { /* rightArm, leftArm, rightLeg, leftLeg: {target:[x,y,z],pole:[x,y,z]} */ },
    pose: [ /* exactly16 source XYZ points */ ]
  }],
  selectedId: 'character-1', nextId: 2
}
```

## Additive host integration

The published WASM/rig-v1 operations remain unchanged. These renderer-independent
JavaScript APIs form the scene persistence boundary for consumers such as Rheon:

```js
import {exportScene,parseScene} from './scene-file.js';
import {createSceneArchive} from './scene-archive.js';
const archive = await createSceneArchive();
const bytes = archive.encode(exportScene(model.state));
// Later, after obtaining bytes from a local file:
const replacement = parseScene(archive.decode(bytes), model.baseGraph);
model.replaceScene(replacement); // revalidates; one atomic undo step
```

Load the vendored `vendor/sqljs/sql-wasm.js` classic script first, or pass an
initialized sql.js module as `createSceneArchive({SQL})`. Version1.14.2 is pinned
and shipped locally with its MIT license and WASM; no CDN is used. API reference:
[sql.js documentation](https://sql.js.org/documentation/).

`model.revision` is a monotonic session change counter; `model.gestureActive`
reports an active edit. `setupSceneFiles` in `scene-files-ui.js` wraps file input
and download controls. Its `loadFile(file)` returns a promise with `status` equal
to `loaded`, `cancelled`, `stale`, or `error`. It captures revision when the chooser
opens, checks it after asynchronous reads/decoding, and rejects intervening edits.
Newer Open requests invalidate older ones; cancelled reads never replace state.
Imports during active gestures are rejected without cancelling the gesture.

A host implementing its own UI must preserve this revision check before calling
`replaceScene`. Refresh its renderer afterward and await `renderer.whenIdle()`
when current geometry is needed. No cross-window messaging or automatic scene
storage is introduced.
