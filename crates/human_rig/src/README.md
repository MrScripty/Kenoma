# Implementation boundary

`lib.rs` owns rest-space skin weights, typed/versioned serialization contracts,
bound-rig validation, rigid bone transforms and dual-quaternion deformation.
Surface extraction is invoked only by `bind_mannequin`. Pose deformation preserves
the rest topology and performs no field union or posed-space rebinding.

Dynamic indices are allowed locally after graph, bone and mesh validation.
Rendering, worker scheduling, WASM handle lifecycle, scene history, collision
simulation and research code belong outside this crate.
