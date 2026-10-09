//! Additive rig-v1 handles. Existing stateless surface operations are unchanged.
use crate::{failure, HeadPose, SkinGraph, SkinGraphGenerateOptions, SurfaceOptions};
use human_core::GeneratedSkinMesh;
use human_rig::{bind_mannequin, deform_mannequin, BoundRig};
use serde::Serialize;
use std::{cell::RefCell, collections::BTreeMap};
const MAX_RIGS: usize = 16;
const MAX_BOUND_VERTICES: usize = 750_000;
struct Registry {
    next: u32,
    rigs: BTreeMap<u32, BoundRig>,
}
thread_local! { static REGISTRY: RefCell<Registry> = const { RefCell::new(Registry { next: 1, rigs: BTreeMap::new() }) }; }
#[derive(Serialize)]
struct RigSuccess<'a> {
    version: u32,
    ok: bool,
    rig_version: u32,
    rig_id: u32,
    graph: &'a SkinGraph,
    head: HeadPose,
    options: SkinGraphGenerateOptions,
    mesh: &'a GeneratedSkinMesh,
}
fn success(rig_id: u32, graph: &SkinGraph, head: HeadPose, mesh: &GeneratedSkinMesh) -> String {
    serde_json::to_string(&RigSuccess {
        version: 1,
        ok: true,
        rig_version: 1,
        rig_id,
        graph,
        head,
        options: Default::default(),
        mesh,
    })
    .unwrap_or_else(|e| failure("serialization", e))
}
fn version_error(version: u32) -> Option<String> {
    (version != 1).then(|| failure("unsupported_rig_version", "Expected rig_version 1"))
}
pub(super) fn bind(version: u32, options: SurfaceOptions) -> String {
    if let Some(error) = version_error(version) {
        return error;
    }
    REGISTRY.with(|cell| {
        let mut registry = cell.borrow_mut();
        if registry.rigs.len() >= MAX_RIGS || registry.next == u32::MAX {
            return failure(
                "resource_limit",
                "Rig handle budget exhausted; release unused rigs",
            );
        }
        let rig = match bind_mannequin(&options) {
            Ok(rig) => rig,
            Err(e) => return failure("invalid_rig", e),
        };
        let used: usize = registry.rigs.values().map(|r| r.mesh.positions.len()).sum();
        if used + rig.mesh.positions.len() > MAX_BOUND_VERTICES {
            return failure("resource_limit", "Bound rig vertex budget exhausted");
        }
        let id = registry.next;
        let response = success(id, &rig.rest_graph, HeadPose::default(), &rig.mesh);
        registry.next += 1;
        registry.rigs.insert(id, rig);
        response
    })
}
pub(super) fn deform(version: u32, id: u32, graph: SkinGraph, head: HeadPose) -> String {
    if let Some(error) = version_error(version) {
        return error;
    }
    REGISTRY.with(|cell| {
        let registry = cell.borrow();
        let Some(rig) = registry.rigs.get(&id) else {
            return failure(
                "unknown_rig",
                "Unknown or released rig_id in this WASM instance",
            );
        };
        match deform_mannequin(rig, &graph, &head) {
            Ok(mesh) => success(id, &graph, head, &mesh),
            Err(e) => failure("invalid_rig", e),
        }
    })
}
pub(super) fn release(version: u32, id: u32) -> String {
    if let Some(error) = version_error(version) {
        return error;
    }
    REGISTRY.with(|cell| {
        if cell.borrow_mut().rigs.remove(&id).is_none() {
            return failure(
                "unknown_rig",
                "Unknown or released rig_id in this WASM instance",
            );
        }
        serde_json::json!({"version":1,"ok":true,"rig_version":1,"rig_id":id,"released":true})
            .to_string()
    })
}
