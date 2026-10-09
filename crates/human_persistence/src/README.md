# Graph persistence

`lib.rs` owns versioned SQLite graph tables and atomic saves. Only graph source
and generation options are persisted. The core has no dependency on this crate.
The sample example creates the canonical `.human.sqlite` fixture and reports mesh
counts without writing generated meshes. No research database or asset is opened.
