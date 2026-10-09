use crate::*;
use std::collections::{BTreeSet, VecDeque};

/// Fatal structural errors are typed; recoverable conditions are diagnostics.
/// Neither validation nor generation mutates the source graph.
pub fn validate_skin_graph(graph: &SkinGraph) -> Result<GraphValidation, GraphError> {
    if graph.nodes.len() > MAX_NODES || graph.edges.len() > MAX_EDGES {
        return Err(GraphError::ResourceLimit);
    }
    let mut diagnostics = Vec::new();
    if graph.nodes.is_empty() {
        diagnostics.push(Diagnostic::EmptyGraph);
    }
    for (id, node) in graph.nodes.iter().enumerate() {
        if !node.position.is_finite()
            || !node.radii.is_finite()
            || node.position.abs().max_element() > MAX_COORDINATE
            || node.radii.abs().max_element() > MAX_COORDINATE
        {
            return Err(GraphError::InvalidValue(id));
        }
        if node.radii.min_element() < MIN_RADIUS {
            diagnostics.push(Diagnostic::RadiusClamped { node: id });
        }
    }
    let mut unique = BTreeSet::new();
    let mut valid_edges = Vec::new();
    for (id, edge) in graph.edges.iter().enumerate() {
        let a = graph.node(edge.a)?;
        let b = graph.node(edge.b)?;
        if edge.a == edge.b {
            return Err(GraphError::SelfEdge(id));
        }
        if !unique.insert((edge.a.min(edge.b), edge.a.max(edge.b))) {
            return Err(GraphError::DuplicateEdge(id));
        }
        if a.position.distance(b.position) < ZERO_EDGE_EPSILON {
            diagnostics.push(Diagnostic::ZeroLengthEdge { edge: id });
        } else {
            valid_edges.push(id);
        }
    }
    // Authoring connectivity includes zero-length edges. Geometry skips them.
    let mut remaining: BTreeSet<_> = (0..graph.nodes.len()).collect();
    let mut islands = Vec::new();
    while let Some(seed) = remaining.first().copied() {
        let mut nodes = component(graph, seed, None);
        nodes.sort_unstable();
        for node in &nodes {
            remaining.remove(node);
        }
        let mut roots: Vec<_> = nodes
            .iter()
            .copied()
            .filter(|id| graph.nodes.get(*id).is_some_and(|n| n.root))
            .collect();
        if roots.is_empty() {
            roots.push(seed);
            diagnostics.push(Diagnostic::IslandRootGenerated {
                island: islands.len(),
                node: seed,
            });
        } else if roots.len() > 1 {
            diagnostics.push(Diagnostic::MultipleRootsInIsland {
                island: islands.len(),
                roots: roots.clone(),
            });
        }
        islands.push(GraphIsland {
            nodes: std::mem::take(&mut nodes),
            roots,
        });
    }
    Ok(GraphValidation {
        diagnostics,
        islands,
        valid_edges,
    })
}
pub fn find_graph_islands(graph: &SkinGraph) -> Result<Vec<GraphIsland>, GraphError> {
    Ok(validate_skin_graph(graph)?.islands)
}
pub(crate) fn component(graph: &SkinGraph, seed: NodeId, excluded: Option<EdgeId>) -> Vec<NodeId> {
    let mut seen = BTreeSet::from([seed]);
    let mut queue = VecDeque::from([seed]);
    while let Some(node) = queue.pop_front() {
        for (id, edge) in graph.edges.iter().enumerate() {
            if Some(id) == excluded {
                continue;
            }
            let neighbor = if edge.a == node {
                Some(edge.b)
            } else if edge.b == node {
                Some(edge.a)
            } else {
                None
            };
            if let Some(next) = neighbor {
                if seen.insert(next) {
                    queue.push_back(next);
                }
            }
        }
    }
    seen.into_iter().collect()
}
