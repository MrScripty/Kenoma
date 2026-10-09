use crate::validation::component;
use crate::*;
use serde::{Deserialize, Serialize};

/// Node IDs are vector indices; deletion compacts them. UIs must refresh selection
/// after deletion/undo. Rotation is in model space, in radians, around the pivot.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum GraphCommand {
    AddNode {
        position: Vec3,
        radii: Vec2,
    },
    MoveNode {
        node: NodeId,
        position: Vec3,
    },
    ExtrudeNode {
        node: NodeId,
        offset: Vec3,
    },
    Connect {
        a: NodeId,
        b: NodeId,
    },
    SetRadius {
        node: NodeId,
        radii: Vec2,
    },
    DeleteNode {
        node: NodeId,
    },
    DeleteEdge {
        edge: EdgeId,
    },
    MarkRoot {
        node: NodeId,
    },
    RotateBranch {
        pivot: NodeId,
        child: NodeId,
        axis: Vec3,
        radians: f32,
    },
}
#[derive(Clone, Debug)]
pub struct GraphEdit {
    before: SkinGraph,
    after: SkinGraph,
}
/// Apply on a copy, validate, and commit only on success.
pub fn apply_graph_command(
    graph: &mut SkinGraph,
    command: &GraphCommand,
) -> Result<GraphEdit, GraphError> {
    validate_skin_graph(graph)?;
    let mut next = graph.clone();
    match *command {
        GraphCommand::AddNode { position, radii } => {
            next.nodes.push(SkinNode::new(position, radii))
        }
        GraphCommand::MoveNode { node, position } => next.node_mut(node)?.position = position,
        GraphCommand::SetRadius { node, radii } => next.node_mut(node)?.radii = radii,
        GraphCommand::ExtrudeNode { node, offset } => {
            if !offset.is_finite() || offset.length() < ZERO_EDGE_EPSILON {
                return Err(GraphError::InvalidTransform);
            }
            let source = next.node(node)?.clone();
            next.edges.push(SkinEdge {
                a: node,
                b: next.nodes.len(),
            });
            next.nodes
                .push(SkinNode::new(source.position + offset, source.radii));
        }
        GraphCommand::Connect { a, b } => next.edges.push(SkinEdge { a, b }),
        GraphCommand::DeleteEdge { edge } => {
            if edge >= next.edges.len() {
                return Err(GraphError::InvalidEdge(edge));
            }
            next.edges.remove(edge);
        }
        GraphCommand::DeleteNode { node } => {
            next.node(node)?;
            next.nodes.remove(node);
            next.edges.retain(|e| e.a != node && e.b != node);
            for e in &mut next.edges {
                if e.a > node {
                    e.a -= 1;
                }
                if e.b > node {
                    e.b -= 1;
                }
            }
        }
        GraphCommand::MarkRoot { node } => {
            next.node(node)?;
            for id in component(&next, node, None) {
                next.node_mut(id)?.root = id == node;
            }
        }
        GraphCommand::RotateBranch {
            pivot,
            child,
            axis,
            radians,
        } => {
            let origin = next.node(pivot)?.position;
            next.node(child)?;
            if !axis.is_finite()
                || axis.length_squared() < ZERO_EDGE_EPSILON
                || !radians.is_finite()
            {
                return Err(GraphError::InvalidTransform);
            }
            let cut = next
                .edges
                .iter()
                .position(|e| (e.a == pivot && e.b == child) || (e.b == pivot && e.a == child))
                .ok_or(GraphError::AmbiguousBranch)?;
            let branch = component(&next, child, Some(cut));
            if branch.contains(&pivot) {
                return Err(GraphError::AmbiguousBranch);
            }
            let unit_axis = axis.try_normalize().ok_or(GraphError::InvalidTransform)?;
            let rotation = Quat::from_axis_angle(unit_axis, radians);
            for id in branch {
                let n = next.node_mut(id)?;
                n.position = origin + rotation * (n.position - origin);
            }
        }
    }
    // Commands maintain one root per island, choosing the lowest existing root.
    for island in find_graph_islands(&next)? {
        if let Some(root) = island.roots.first().copied() {
            for id in island.nodes {
                next.node_mut(id)?.root = id == root;
            }
        }
    }
    validate_skin_graph(&next)?;
    let edit = GraphEdit {
        before: graph.clone(),
        after: next.clone(),
    };
    *graph = next;
    Ok(edit)
}
pub fn undo_graph_command(graph: &mut SkinGraph, edit: &GraphEdit) -> Result<(), GraphError> {
    if *graph != edit.after {
        return Err(GraphError::HistoryConflict);
    }
    *graph = edit.before.clone();
    Ok(())
}
/// Snapshot history is deliberately simple and bounded; external mutations are detected.
#[derive(Default)]
pub struct GraphHistory {
    undo: Vec<GraphEdit>,
    redo: Vec<GraphEdit>,
}
impl GraphHistory {
    pub fn apply(
        &mut self,
        graph: &mut SkinGraph,
        command: &GraphCommand,
    ) -> Result<(), GraphError> {
        let edit = apply_graph_command(graph, command)?;
        if self.undo.len() == 128 {
            self.undo.remove(0);
        }
        self.undo.push(edit);
        self.redo.clear();
        Ok(())
    }
    pub fn undo(&mut self, graph: &mut SkinGraph) -> Result<bool, GraphError> {
        let Some(edit) = self.undo.last() else {
            return Ok(false);
        };
        undo_graph_command(graph, edit)?;
        if let Some(edit) = self.undo.pop() {
            self.redo.push(edit);
        }
        Ok(true)
    }
    pub fn redo(&mut self, graph: &mut SkinGraph) -> Result<bool, GraphError> {
        let Some(edit) = self.redo.last() else {
            return Ok(false);
        };
        if *graph != edit.before {
            return Err(GraphError::HistoryConflict);
        }
        *graph = edit.after.clone();
        if let Some(edit) = self.redo.pop() {
            self.undo.push(edit);
        }
        Ok(true)
    }
}
