use glam::{Vec2, Vec3};
use serde::{Deserialize, Serialize};

pub const MIN_RADIUS: f32 = 0.01;
pub const DEFAULT_RADIUS: f32 = 0.25;
pub const ZERO_EDGE_EPSILON: f32 = 1.0e-5;
pub const MAX_NODES: usize = 4096;
pub const MAX_EDGES: usize = 8192;
pub const MAX_VERTICES: usize = 1_000_000;
/// Bounded model domain avoids overflow and loss of ring precision in f32.
pub const MAX_COORDINATE: f32 = 1000.0;
pub type NodeId = usize;
pub type EdgeId = usize;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SkinNode {
    pub position: Vec3,
    pub radii: Vec2,
    pub root: bool,
}
impl SkinNode {
    pub fn new(position: Vec3, radii: Vec2) -> Self {
        Self {
            position,
            radii,
            root: false,
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SkinEdge {
    pub a: NodeId,
    pub b: NodeId,
}
#[derive(Clone, Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct SkinGraph {
    pub nodes: Vec<SkinNode>,
    pub edges: Vec<SkinEdge>,
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SkinGraphGenerateOptions {
    pub ring_sides: usize,
    pub target_segment_length_factor: f32,
    pub max_edge_segments: usize,
}
impl Default for SkinGraphGenerateOptions {
    fn default() -> Self {
        Self {
            ring_sides: 8,
            target_segment_length_factor: 1.25,
            max_edge_segments: 64,
        }
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Diagnostic {
    EmptyGraph,
    ZeroLengthEdge { edge: EdgeId },
    RadiusClamped { node: NodeId },
    IslandRootGenerated { island: usize, node: NodeId },
    MultipleRootsInIsland { island: usize, roots: Vec<NodeId> },
    LoopFrameApproximated { edge: EdgeId },
    BranchFallbackOverlap { node: NodeId },
}
#[derive(Clone, Debug, PartialEq, Eq, thiserror::Error)]
pub enum GraphError {
    #[error("invalid node {0}")]
    InvalidNode(NodeId),
    #[error("invalid edge {0}")]
    InvalidEdge(EdgeId),
    #[error("self edge {0}")]
    SelfEdge(EdgeId),
    #[error("duplicate edge {0}")]
    DuplicateEdge(EdgeId),
    #[error("non-finite or out-of-domain node {0}")]
    InvalidValue(NodeId),
    #[error("invalid generation options")]
    InvalidOptions,
    #[error("graph or generated mesh exceeds resource budget")]
    ResourceLimit,
    #[error("invalid pose rotation or extrusion")]
    InvalidTransform,
    #[error("pose cut must be an edge that separates the branch from its pivot")]
    AmbiguousBranch,
    #[error("invalid or degenerate generated geometry")]
    InvalidGeometry,
    #[error("history no longer matches the graph")]
    HistoryConflict,
}
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct GraphIsland {
    pub nodes: Vec<NodeId>,
    pub roots: Vec<NodeId>,
}
#[derive(Clone, Debug)]
pub struct GraphValidation {
    pub diagnostics: Vec<Diagnostic>,
    pub islands: Vec<GraphIsland>,
    pub valid_edges: Vec<EdgeId>,
}
/// Parallel buffers; CCW triangles in right-handed +Y-up model space.
#[derive(Clone, Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct GeneratedSkinMesh {
    pub positions: Vec<Vec3>,
    pub normals: Vec<Vec3>,
    pub indices: Vec<u32>,
    pub source_nodes: Vec<Option<NodeId>>,
    pub source_edges: Vec<Option<EdgeId>>,
    pub diagnostics: Vec<Diagnostic>,
}
impl SkinGraph {
    pub(crate) fn node(&self, id: NodeId) -> Result<&SkinNode, GraphError> {
        self.nodes.get(id).ok_or(GraphError::InvalidNode(id))
    }
    pub(crate) fn node_mut(&mut self, id: NodeId) -> Result<&mut SkinNode, GraphError> {
        self.nodes.get_mut(id).ok_or(GraphError::InvalidNode(id))
    }
}
