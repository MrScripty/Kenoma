#![allow(clippy::indexing_slicing)]
use human_core::*;
use std::collections::BTreeMap;
fn edge() -> SkinGraph {
    SkinGraph {
        nodes: vec![
            SkinNode {
                position: Vec3::ZERO,
                radii: Vec2::splat(0.25),
                root: true,
            },
            SkinNode::new(Vec3::Y, Vec2::splat(0.25)),
        ],
        edges: vec![SkinEdge { a: 0, b: 1 }],
    }
}
fn assert_mesh(mesh: &GeneratedSkinMesh) {
    assert_eq!(mesh.positions.len(), mesh.normals.len());
    assert_eq!(mesh.positions.len(), mesh.source_nodes.len());
    assert_eq!(mesh.positions.len(), mesh.source_edges.len());
    for n in &mesh.normals {
        assert!(n.is_finite());
        assert!((n.length() - 1.).abs() < 1e-5);
    }
    let mut incidence = BTreeMap::<(u32, u32), (usize, i32)>::new();
    for t in mesh.indices.as_chunks::<3>().0 {
        let (a, b, c) = (t[0], t[1], t[2]);
        assert!(a != b && b != c && a != c);
        let p = mesh.positions[a as usize];
        let q = mesh.positions[b as usize];
        let r = mesh.positions[c as usize];
        assert!(p.is_finite() && q.is_finite() && r.is_finite());
        assert!((q - p).cross(r - p).length() > 1e-10);
        for (a, b) in [(a, b), (b, c), (c, a)] {
            let value = incidence.entry((a.min(b), a.max(b))).or_default();
            value.0 += 1;
            value.1 += if a < b { 1 } else { -1 };
        }
    }
    // Each component is closed and consistently wound, though hubs overlap tubes.
    assert!(incidence.values().all(|v| *v == (2, 0)));
}
#[test]
fn all_samples_are_valid_deterministic_and_source_preserving() -> Result<(), GraphError> {
    for (_, graph) in sample_graphs() {
        let before = graph.clone();
        let first = generate_skin_graph_mesh(&graph, &Default::default())?;
        assert!(!first.positions.is_empty());
        assert_mesh(&first);
        assert_eq!(
            first,
            generate_skin_graph_mesh(&graph, &Default::default())?
        );
        assert_eq!(graph, before);
    }
    Ok(())
}
#[test]
fn single_edge_golden_counts_indices_positions_and_outward_winding() -> Result<(), GraphError> {
    let mesh = generate_skin_graph_mesh(&edge(), &Default::default())?;
    // ceil(1 / (.25 * 1.25)) = 4 segments, 5 rings, 2 centers.
    assert_eq!(mesh.positions.len(), 42);
    assert_eq!(mesh.indices.len(), 240);
    assert_eq!(&mesh.indices[..6], &[8, 1, 0, 8, 2, 1]);
    assert_eq!(mesh.positions[0], Vec3::new(0., 0., 0.25));
    for t in mesh.indices.as_chunks::<3>().0 {
        let [a, b, c] = [
            mesh.positions[t[0] as usize],
            mesh.positions[t[1] as usize],
            mesh.positions[t[2] as usize],
        ];
        let center = (a + b + c) / 3.;
        let normal = (b - a).cross(c - a);
        let outward = if center.y == 0. {
            -Vec3::Y
        } else if center.y == 1. {
            Vec3::Y
        } else {
            Vec3::new(center.x, 0., center.z)
        };
        assert!(normal.dot(outward) > 0.);
    }
    assert_mesh(&mesh);
    Ok(())
}
#[test]
fn isolated_ellipsoid_has_outward_faces() -> Result<(), GraphError> {
    let graph = SkinGraph {
        nodes: vec![SkinNode::new(Vec3::ZERO, Vec2::new(0.2, 0.7))],
        edges: vec![],
    };
    let mesh = generate_skin_graph_mesh(&graph, &Default::default())?;
    for t in mesh.indices.as_chunks::<3>().0 {
        let (a, b, c) = (
            mesh.positions[t[0] as usize],
            mesh.positions[t[1] as usize],
            mesh.positions[t[2] as usize],
        );
        assert!((b - a).cross(c - a).dot((a + b + c) / 3.) > 0.);
    }
    Ok(())
}
#[test]
fn boundaries_and_recoverable_diagnostics() -> Result<(), GraphError> {
    assert_eq!(
        validate_skin_graph(&SkinGraph::default())?.diagnostics,
        vec![Diagnostic::EmptyGraph]
    );
    assert!(
        generate_skin_graph_mesh(&SkinGraph::default(), &Default::default())?
            .positions
            .is_empty()
    );
    let mut graph = edge();
    graph.edges[0].b = 8;
    assert_eq!(
        validate_skin_graph(&graph).err(),
        Some(GraphError::InvalidNode(8))
    );
    graph = edge();
    graph.edges[0].b = 0;
    assert_eq!(
        validate_skin_graph(&graph).err(),
        Some(GraphError::SelfEdge(0))
    );
    graph = edge();
    graph.edges.push(SkinEdge { a: 1, b: 0 });
    assert_eq!(
        validate_skin_graph(&graph).err(),
        Some(GraphError::DuplicateEdge(1))
    );
    for bad in [f32::NAN, f32::INFINITY, MAX_COORDINATE * 2.] {
        graph = edge();
        graph.nodes[0].position.x = bad;
        assert_eq!(
            validate_skin_graph(&graph).err(),
            Some(GraphError::InvalidValue(0))
        );
        graph = edge();
        graph.nodes[0].radii.x = bad;
        assert_eq!(
            validate_skin_graph(&graph).err(),
            Some(GraphError::InvalidValue(0))
        );
    }
    graph = edge();
    graph.nodes[0].radii.x = -2.;
    graph.nodes[1].position = Vec3::ZERO;
    let result = generate_skin_graph_mesh(&graph, &Default::default())?;
    assert!(result
        .diagnostics
        .contains(&Diagnostic::RadiusClamped { node: 0 }));
    assert!(result
        .diagnostics
        .contains(&Diagnostic::ZeroLengthEdge { edge: 0 }));
    assert_mesh(&result);
    Ok(())
}
#[test]
fn roots_are_deterministic_per_island() -> Result<(), GraphError> {
    let mut graph = edge();
    graph.nodes[0].root = false;
    graph.nodes.push(SkinNode::new(Vec3::X, Vec2::ONE));
    let result = validate_skin_graph(&graph)?;
    assert_eq!(result.islands[0].roots, vec![0]);
    assert_eq!(result.islands[1].roots, vec![2]);
    graph.nodes[0].root = true;
    graph.nodes[1].root = true;
    assert!(validate_skin_graph(&graph)?.diagnostics.contains(
        &Diagnostic::MultipleRootsInIsland {
            island: 0,
            roots: vec![0, 1]
        }
    ));
    apply_graph_command(&mut graph, &GraphCommand::MarkRoot { node: 1 })?;
    assert!(!graph.nodes[0].root && graph.nodes[1].root && graph.nodes[2].root);
    Ok(())
}
#[test]
fn options_bounds_and_frame_axes() -> Result<(), GraphError> {
    for axis in [
        Vec3::X,
        Vec3::Y,
        Vec3::Z,
        -Vec3::Y,
        Vec3::new(1., 2., 3.).normalize(),
    ] {
        let mut graph = edge();
        graph.nodes[1].position = axis;
        for sides in [0, 4, 8, 32, usize::MAX] {
            let options = SkinGraphGenerateOptions {
                ring_sides: sides,
                max_edge_segments: 1,
                ..Default::default()
            };
            let mesh = generate_skin_graph_mesh(&graph, &options)?;
            assert_eq!(mesh.positions.len(), sides.clamp(4, 32) * 2 + 2);
            for p in &mesh.positions[..sides.clamp(4, 32)] {
                assert!(p.dot(axis).abs() < 1e-6);
                assert!((p.length() - 0.25).abs() < 1e-6);
            }
            assert_mesh(&mesh);
        }
    }
    let options = SkinGraphGenerateOptions {
        target_segment_length_factor: 1e-30,
        max_edge_segments: usize::MAX,
        ..Default::default()
    };
    assert_eq!(
        generate_skin_graph_mesh(&edge(), &options)?.positions.len(),
        65 * 8 + 2
    );
    for factor in [0., -1., f32::NAN, f32::INFINITY] {
        let options = SkinGraphGenerateOptions {
            target_segment_length_factor: factor,
            ..Default::default()
        };
        assert_eq!(
            generate_skin_graph_mesh(&edge(), &options).err(),
            Some(GraphError::InvalidOptions)
        );
    }
    Ok(())
}
#[test]
fn loops_are_bounded_and_diagnosed() -> Result<(), GraphError> {
    let mut graph = edge();
    graph.nodes.push(SkinNode::new(Vec3::X, Vec2::splat(0.1)));
    graph
        .edges
        .extend([SkinEdge { a: 1, b: 2 }, SkinEdge { a: 2, b: 0 }]);
    let mesh = generate_skin_graph_mesh(&graph, &Default::default())?;
    assert!(mesh
        .diagnostics
        .iter()
        .any(|d| matches!(d, Diagnostic::LoopFrameApproximated { .. })));
    assert_mesh(&mesh);
    Ok(())
}
#[test]
fn commands_history_and_failed_rollback() -> Result<(), GraphError> {
    let mut graph = SkinGraph::default();
    let mut history = GraphHistory::default();
    let commands = [
        GraphCommand::AddNode {
            position: Vec3::ZERO,
            radii: Vec2::splat(0.1),
        },
        GraphCommand::ExtrudeNode {
            node: 0,
            offset: Vec3::Y,
        },
        GraphCommand::MoveNode {
            node: 1,
            position: Vec3::X,
        },
        GraphCommand::SetRadius {
            node: 1,
            radii: Vec2::new(0.2, 0.3),
        },
        GraphCommand::MarkRoot { node: 1 },
        GraphCommand::DeleteEdge { edge: 0 },
        GraphCommand::Connect { a: 0, b: 1 },
        GraphCommand::DeleteNode { node: 0 },
    ];
    let mut states = vec![graph.clone()];
    for command in &commands {
        history.apply(&mut graph, command)?;
        states.push(graph.clone());
    }
    for expected in states.iter().rev().skip(1) {
        assert!(history.undo(&mut graph)?);
        assert_eq!(&graph, expected);
    }
    assert!(!history.undo(&mut graph)?);
    for expected in states.iter().skip(1) {
        assert!(history.redo(&mut graph)?);
        assert_eq!(&graph, expected);
    }
    let before = graph.clone();
    for command in [
        GraphCommand::Connect { a: 0, b: 99 },
        GraphCommand::DeleteNode { node: 99 },
        GraphCommand::DeleteEdge { edge: 99 },
        GraphCommand::MoveNode {
            node: 0,
            position: Vec3::splat(f32::NAN),
        },
    ] {
        assert!(history.apply(&mut graph, &command).is_err());
        assert_eq!(graph, before);
    }
    Ok(())
}
#[test]
fn pose_rotates_only_branch_and_preserves_lengths() -> Result<(), GraphError> {
    let mut graph = mannequin();
    let before = graph.clone();
    let edit = apply_graph_command(
        &mut graph,
        &GraphCommand::RotateBranch {
            pivot: 4,
            child: 5,
            axis: Vec3::Z,
            radians: std::f32::consts::FRAC_PI_2,
        },
    )?;
    for id in 0..graph.nodes.len() {
        if id != 5 && id != 6 {
            assert_eq!(graph.nodes[id], before.nodes[id]);
        }
    }
    for edge in &graph.edges {
        let old = before.nodes[edge.a]
            .position
            .distance(before.nodes[edge.b].position);
        let new = graph.nodes[edge.a]
            .position
            .distance(graph.nodes[edge.b].position);
        assert!((old - new).abs() < 1e-6);
    }
    assert_ne!(graph.nodes[6], before.nodes[6]);
    assert_mesh(&generate_skin_graph_mesh(&graph, &Default::default())?);
    undo_graph_command(&mut graph, &edit)?;
    assert_eq!(graph, before);
    Ok(())
}
#[test]
fn ambiguous_pose_and_conflicting_undo_fail_atomically() -> Result<(), GraphError> {
    let mut graph = edge();
    let edit = apply_graph_command(
        &mut graph,
        &GraphCommand::SetRadius {
            node: 0,
            radii: Vec2::ONE,
        },
    )?;
    graph.nodes[1].root = true;
    assert_eq!(
        undo_graph_command(&mut graph, &edit).err(),
        Some(GraphError::HistoryConflict)
    );
    graph.nodes.push(SkinNode::new(Vec3::X, Vec2::ONE));
    graph
        .edges
        .extend([SkinEdge { a: 0, b: 2 }, SkinEdge { a: 2, b: 1 }]);
    let before = graph.clone();
    assert_eq!(
        apply_graph_command(
            &mut graph,
            &GraphCommand::RotateBranch {
                pivot: 0,
                child: 1,
                axis: Vec3::Y,
                radians: 1.
            }
        )
        .err(),
        Some(GraphError::AmbiguousBranch)
    );
    assert_eq!(graph, before);
    Ok(())
}
#[test]
fn malformed_mesh_returns_typed_error() {
    for indices in [vec![0], vec![0, 1, 2], vec![0, 0, 0]] {
        let mut mesh = GeneratedSkinMesh {
            positions: vec![Vec3::ZERO],
            indices,
            ..Default::default()
        };
        assert_eq!(
            recompute_normals(&mut mesh).err(),
            Some(GraphError::InvalidGeometry)
        );
    }
}
#[test]
fn excessive_axis_fails_without_changing_pose() {
    let mut graph = edge();
    let before = graph.clone();
    assert_eq!(
        apply_graph_command(
            &mut graph,
            &GraphCommand::RotateBranch {
                pivot: 0,
                child: 1,
                axis: Vec3::splat(f32::MAX),
                radians: 1.
            }
        )
        .err(),
        Some(GraphError::InvalidTransform)
    );
    assert_eq!(graph, before);
}
#[test]
fn multiple_roots_seed_frames_before_interior_nodes() -> Result<(), GraphError> {
    let mut graph = edge();
    graph.nodes.extend([
        SkinNode::new(Vec3::new(1., 2., 0.), Vec2::splat(0.25)),
        SkinNode {
            position: Vec3::new(2., 2., 1.),
            radii: Vec2::splat(0.25),
            root: true,
        },
    ]);
    graph
        .edges
        .extend([SkinEdge { a: 1, b: 2 }, SkinEdge { a: 2, b: 3 }]);
    let mesh = generate_skin_graph_mesh(&graph, &Default::default())?;
    let order: Vec<_> = mesh
        .source_edges
        .iter()
        .copied()
        .flatten()
        .fold(Vec::new(), |mut v, e| {
            if v.last() != Some(&e) {
                v.push(e);
            }
            v
        });
    assert_eq!(order, vec![0, 2, 1]);
    Ok(())
}
#[test]
fn ui_values_round_trip_and_drive_edit_generation() -> Result<(), Box<dyn std::error::Error>> {
    let mut graph: SkinGraph = serde_json::from_str(&serde_json::to_string(&mannequin())?)?;
    let command: GraphCommand = serde_json::from_str(
        r#"{"RotateBranch":{"pivot":4,"child":5,"axis":[0,0,1],"radians":0.8}}"#,
    )?;
    apply_graph_command(&mut graph, &command)?;
    let mesh = generate_skin_graph_mesh(&graph, &Default::default())?;
    let decoded: GeneratedSkinMesh = serde_json::from_str(&serde_json::to_string(&mesh)?)?;
    assert_eq!(mesh, decoded);
    Ok(())
}
