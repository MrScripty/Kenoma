//! Versioned, host-independent WASM/JSON adapter for the simple graph core.
mod rig_protocol;
use human_core::*;
use human_surface::{generate_mannequin_surface, HeadPose, SurfaceOptions};
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

pub const PROTOCOL_VERSION: u32 = 1;
pub const MAX_REQUEST_BYTES: usize = 2 * 1024 * 1024;
pub const MAX_COMMANDS: usize = 128;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    version: u32,
    operation: Operation,
}
#[derive(Deserialize)]
#[serde(tag = "type", rename_all = "snake_case", deny_unknown_fields)]
enum Operation {
    Mannequin,
    RigBind {
        rig_version: u32,
        #[serde(default)]
        surface_options: SurfaceOptions,
    },
    RigDeform {
        rig_version: u32,
        rig_id: u32,
        graph: SkinGraph,
        #[serde(default)]
        head: HeadPose,
    },
    RigRelease {
        rig_version: u32,
        rig_id: u32,
    },
    Surface {
        graph: SkinGraph,
        #[serde(default)]
        head: HeadPose,
        #[serde(default)]
        surface_options: SurfaceOptions,
    },
    Generate {
        graph: SkinGraph,
        #[serde(default)]
        options: SkinGraphGenerateOptions,
    },
    Edit {
        graph: SkinGraph,
        commands: Vec<GraphCommand>,
        #[serde(default)]
        options: SkinGraphGenerateOptions,
    },
}
#[derive(Serialize)]
struct Success {
    version: u32,
    ok: bool,
    graph: SkinGraph,
    options: SkinGraphGenerateOptions,
    mesh: GeneratedSkinMesh,
    #[serde(skip_serializing_if = "Option::is_none")]
    head: Option<HeadPose>,
    #[serde(skip_serializing_if = "Option::is_none")]
    surface_options: Option<SurfaceOptions>,
}
#[derive(Serialize)]
struct Failure<'a> {
    version: u32,
    ok: bool,
    error: ErrorInfo<'a>,
}
#[derive(Serialize)]
struct ErrorInfo<'a> {
    code: &'a str,
    message: String,
}
fn failure(code: &str, message: impl ToString) -> String {
    // Serializing strings/bools/integers is infallible; retain a valid envelope
    // rather than panic if the serializer ever changes.
    serde_json::to_string(&Failure {
        version: PROTOCOL_VERSION,
        ok: false,
        error: ErrorInfo { code, message: message.to_string() },
    }).unwrap_or_else(|_| String::from(r#"{"version":1,"ok":false,"error":{"code":"serialization","message":"Cannot encode response"}}"#))
}
fn graph_failure(error: GraphError) -> String {
    let code = match error {
        GraphError::InvalidNode(_) => "invalid_node",
        GraphError::InvalidEdge(_) => "invalid_edge",
        GraphError::SelfEdge(_) => "self_edge",
        GraphError::DuplicateEdge(_) => "duplicate_edge",
        GraphError::InvalidValue(_) => "invalid_value",
        GraphError::InvalidOptions => "invalid_options",
        GraphError::ResourceLimit => "resource_limit",
        GraphError::InvalidTransform => "invalid_transform",
        GraphError::AmbiguousBranch => "ambiguous_branch",
        GraphError::InvalidGeometry => "invalid_geometry",
        GraphError::HistoryConflict => "history_conflict",
    };
    failure(code, error)
}
// IDs/counts have a u32 wire contract on both native and wasm32 hosts.
// Check before deserializing the core's platform-sized usize fields.
fn portable_integers(value: &serde_json::Value) -> bool {
    match value {
        serde_json::Value::Object(fields) => fields.iter().all(|(name, value)| {
            if matches!(
                name.as_str(),
                "node"
                    | "edge"
                    | "a"
                    | "b"
                    | "pivot"
                    | "child"
                    | "ring_sides"
                    | "max_edge_segments"
            ) {
                value.as_u64().is_some_and(|n| u32::try_from(n).is_ok())
            } else {
                portable_integers(value)
            }
        }),
        serde_json::Value::Array(values) => values.iter().all(portable_integers),
        _ => true,
    }
}
/// All input and operation failures return `{version:1,ok:false,error:{code,message}}`.
/// Success returns authoritative graph/options plus disposable mesh buffers.
#[wasm_bindgen]
pub fn evaluate(request_json: &str) -> String {
    if request_json.len() > MAX_REQUEST_BYTES {
        return failure("resource_limit", "Request exceeds 2 MiB");
    }
    let value: serde_json::Value = match serde_json::from_str(request_json) {
        Ok(value) => value,
        Err(error) => return failure("invalid_request", error),
    };
    if !portable_integers(&value) {
        return failure(
            "invalid_request",
            "IDs and counts must be unsigned 32-bit integers",
        );
    }
    let request: Request = match serde_json::from_value(value) {
        Ok(value) => value,
        Err(error) => return failure("invalid_request", error),
    };
    if request.version != PROTOCOL_VERSION {
        return failure("unsupported_version", "Expected protocol version 1");
    }
    let (mut graph, options, commands, surface) = match request.operation {
        Operation::RigBind {
            rig_version,
            surface_options,
        } => return rig_protocol::bind(rig_version, surface_options),
        Operation::RigDeform {
            rig_version,
            rig_id,
            graph,
            head,
        } => return rig_protocol::deform(rig_version, rig_id, graph, head),
        Operation::RigRelease {
            rig_version,
            rig_id,
        } => return rig_protocol::release(rig_version, rig_id),
        Operation::Mannequin => (
            mannequin(),
            SkinGraphGenerateOptions::default(),
            Vec::new(),
            None,
        ),
        Operation::Surface {
            graph,
            head,
            surface_options,
        } => (
            graph,
            SkinGraphGenerateOptions::default(),
            Vec::new(),
            Some((head, surface_options)),
        ),
        Operation::Generate { graph, options } => (graph, options, Vec::new(), None),
        Operation::Edit {
            graph,
            options,
            commands,
        } => (graph, options, commands, None),
    };
    if commands.len() > MAX_COMMANDS {
        return failure("resource_limit", "At most 128 commands per request");
    }
    for command in commands {
        if let Err(error) = apply_graph_command(&mut graph, &command) {
            return graph_failure(error);
        }
    }
    let generated = if let Some((head, surface_options)) = &surface {
        match generate_mannequin_surface(&graph, head, surface_options) {
            Ok(mesh) => Ok(mesh),
            Err(error) => return failure("invalid_surface", error),
        }
    } else {
        generate_skin_graph_mesh(&graph, &options)
    };
    let mesh = match generated {
        Ok(mesh) => mesh,
        Err(error) => return graph_failure(error),
    };
    let (head, surface_options) = surface.unzip();
    match serde_json::to_string(&Success {
        version: PROTOCOL_VERSION,
        ok: true,
        graph,
        options,
        mesh,
        head,
        surface_options,
    }) {
        Ok(response) => response,
        Err(error) => failure("serialization", error),
    }
}
