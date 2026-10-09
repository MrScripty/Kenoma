// Test indices come only from the generator's validated triangle buffers.
#![allow(clippy::indexing_slicing)]
use human_core::{mannequin, GeneratedSkinMesh, Quat, SkinGraph, Vec3};
use human_surface::{generate_mannequin_surface, HeadPose, SurfaceError, SurfaceOptions};
use std::collections::{BTreeMap, BTreeSet, VecDeque};
fn topology(mesh: &GeneratedSkinMesh) {
    let n = mesh.positions.len();
    assert_eq!(mesh.normals.len(), n);
    assert_eq!(mesh.source_nodes.len(), n);
    assert_eq!(mesh.source_edges.len(), n);
    let mut edges: BTreeMap<(u32, u32), (usize, i32)> = BTreeMap::new();
    let mut links = vec![Vec::new(); n];
    let mut volume = 0.0f64;
    let mut unique = BTreeSet::new();
    for (p, normal) in mesh.positions.iter().zip(&mesh.normals) {
        assert!(p.is_finite() && normal.is_finite());
        assert!((normal.length() - 1.0).abs() < 1e-5);
        assert!(
            unique.insert(p.to_array().map(f32::to_bits)),
            "duplicate spatial vertex"
        );
    }
    for triangle in mesh.indices.as_chunks::<3>().0 {
        let [a, b, c] = [triangle[0], triangle[1], triangle[2]];
        assert!(a != b && b != c && c != a);
        assert!((a.max(b).max(c) as usize) < n);
        let [pa, pb, pc] = [
            mesh.positions[a as usize],
            mesh.positions[b as usize],
            mesh.positions[c as usize],
        ];
        let area = (pb - pa).cross(pc - pa);
        assert!(area.length_squared() > 0.0, "degenerate triangle");
        let normal = mesh.normals[a as usize] + mesh.normals[b as usize] + mesh.normals[c as usize];
        assert!(area.dot(normal) > -1e-9, "inward gradient normal");
        volume += pa.as_dvec3().dot(pb.as_dvec3().cross(pc.as_dvec3())) / 6.0;
        for (u, v) in [(a, b), (b, c), (c, a)] {
            let entry = edges.entry((u.min(v), u.max(v))).or_default();
            entry.0 += 1;
            entry.1 += if u < v { 1 } else { -1 };
        }
        links[a as usize].push((b, c));
        links[b as usize].push((c, a));
        links[c as usize].push((a, b));
    }
    assert!(volume > 0.0, "outward winding");
    for (edge, (count, direction)) in &edges {
        assert_eq!(*count, 2, "edge {edge:?} not watertight");
        assert_eq!(*direction, 0, "edge {edge:?} inconsistent winding");
    }
    // Every vertex link must be exactly one cycle, not two closed sheets touching.
    for triangles in &links {
        assert!(!triangles.is_empty());
        let mut ring: BTreeMap<u32, Vec<u32>> = BTreeMap::new();
        for &(a, b) in triangles {
            ring.entry(a).or_default().push(b);
            ring.entry(b).or_default().push(a);
        }
        assert!(ring.values().all(|neighbors| neighbors.len() == 2));
        let Some(&start) = ring.keys().next() else {
            panic!("empty link")
        };
        let mut queue = VecDeque::from([start]);
        let mut visited = BTreeSet::new();
        while let Some(v) = queue.pop_front() {
            if visited.insert(v) {
                for next in &ring[&v] {
                    queue.push_back(*next);
                }
            }
        }
        assert_eq!(visited.len(), ring.len(), "disconnected vertex link");
    }
    let mut neighbors = vec![Vec::new(); n];
    for &(a, b) in edges.keys() {
        neighbors[a as usize].push(b as usize);
        neighbors[b as usize].push(a as usize);
    }
    let mut reached = BTreeSet::new();
    let mut queue = VecDeque::from([0]);
    while let Some(v) = queue.pop_front() {
        if reached.insert(v) {
            queue.extend(neighbors[v].iter().copied());
        }
    }
    assert_eq!(reached.len(), n, "surface has disconnected components");
}
fn mesh(graph: &SkinGraph, head: HeadPose) -> GeneratedSkinMesh {
    match generate_mannequin_surface(graph, &head, &SurfaceOptions::default()) {
        Ok(m) => m,
        Err(e) => panic!("{e}"),
    }
}
#[test]
fn canonical_is_welded_single_closed_vertex_manifold_and_deterministic() {
    let graph = mannequin();
    let original = graph.clone();
    let start = std::time::Instant::now();
    let a = mesh(&graph, HeadPose::default());
    eprintln!(
        "default surface: {} vertices, {} triangles, {:?}",
        a.positions.len(),
        a.indices.len() / 3,
        start.elapsed()
    );
    topology(&a);
    assert_eq!(graph, original);
    assert_eq!(a, mesh(&graph, HeadPose::default()));
}
fn rotate(graph: &mut SkinGraph, pivot: usize, indices: &[usize], q: Quat) {
    let origin = graph.nodes[pivot].position;
    for &id in indices {
        graph.nodes[id].position = origin + q * (graph.nodes[id].position - origin);
    }
}
#[test]
fn bent_shoulders_elbows_hips_knees_and_head_are_connected() {
    let mut graph = mannequin();
    rotate(&mut graph, 4, &[5, 6], Quat::from_rotation_z(0.65));
    rotate(&mut graph, 5, &[6], Quat::from_rotation_y(-1.1));
    rotate(&mut graph, 7, &[8, 9], Quat::from_rotation_y(0.6));
    rotate(&mut graph, 8, &[9], Quat::from_rotation_z(-1.5));
    rotate(&mut graph, 10, &[11, 12], Quat::from_rotation_x(-0.7));
    rotate(&mut graph, 11, &[12], Quat::from_rotation_x(1.4));
    rotate(&mut graph, 13, &[14, 15], Quat::from_rotation_z(-0.25));
    rotate(&mut graph, 14, &[15], Quat::from_rotation_x(0.55));
    topology(&mesh(
        &graph,
        HeadPose {
            yaw: 1.0,
            pitch: -0.35,
        },
    ));
}
#[test]
fn head_orientation_changes_integrated_silhouette_not_source_graph() {
    let graph = mannequin();
    let original = graph.clone();
    let neutral = mesh(&graph, HeadPose::default());
    let turned = mesh(
        &graph,
        HeadPose {
            yaw: 1.57,
            pitch: 0.65,
        },
    );
    topology(&turned);
    assert_ne!(neutral.positions, turned.positions);
    assert_eq!(graph, original);
    let top = neutral
        .positions
        .iter()
        .map(|p| p.y)
        .fold(f32::NEG_INFINITY, f32::max);
    assert!(top > 1.88 && top < 1.93);
    // Jaw narrows visibly below the cranium, not a spherical or block head.
    let width = |y: f32| {
        neutral
            .positions
            .iter()
            .filter(|p| (p.y - y).abs() < 0.01)
            .map(|p| p.x.abs())
            .fold(0.0f32, f32::max)
    };
    assert!(width(1.62) < width(1.76) * 0.9);
}
#[test]
fn invalid_input_and_grid_budgets_are_explicit_errors() {
    let graph = mannequin();
    for cell_size in [f32::NAN, 0.0, 0.001, 0.1] {
        assert_eq!(
            generate_mannequin_surface(&graph, &HeadPose::default(), &SurfaceOptions { cell_size }),
            Err(SurfaceError::InvalidOptions)
        );
    }
    assert_eq!(
        generate_mannequin_surface(
            &graph,
            &HeadPose {
                yaw: f32::NAN,
                pitch: 0.0
            },
            &SurfaceOptions::default()
        ),
        Err(SurfaceError::InvalidOptions)
    );
    let mut wrong = graph.clone();
    wrong.edges.pop();
    assert_eq!(
        generate_mannequin_surface(&wrong, &HeadPose::default(), &SurfaceOptions::default()),
        Err(SurfaceError::InvalidGraph)
    );
    let mut huge = graph.clone();
    huge.nodes[6].position = Vec3::splat(100.0);
    assert_eq!(
        generate_mannequin_surface(&huge, &HeadPose::default(), &SurfaceOptions::default()),
        Err(SurfaceError::ResourceLimit)
    );
    let mut zero = graph;
    zero.nodes[6].position = zero.nodes[5].position;
    assert_eq!(
        generate_mannequin_surface(&zero, &HeadPose::default(), &SurfaceOptions::default()),
        Err(SurfaceError::InvalidGraph)
    );
}
#[test]
fn coarser_resolution_stays_manifold() {
    let graph = mannequin();
    let result = generate_mannequin_surface(
        &graph,
        &HeadPose::default(),
        &SurfaceOptions { cell_size: 0.028 },
    );
    match result {
        Ok(mesh) => topology(&mesh),
        Err(e) => panic!("{e}"),
    }
}

#[test]
fn head_gizmo_limits_remain_closed_and_connected() {
    let graph = mannequin();
    for yaw in [-120.0_f32.to_radians(), 120.0_f32.to_radians()] {
        for pitch in [-60.0_f32.to_radians(), 60.0_f32.to_radians()] {
            topology(&mesh(&graph, HeadPose { yaw, pitch }));
        }
    }
}

#[test]
fn folded_and_fully_extended_ik_singularities_remain_connected() {
    for folded in [false, true] {
        let mut graph = mannequin();
        for [root, joint, end] in [[4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]] {
            let r = graph.nodes[root].position;
            let j = graph.nodes[joint].position;
            let e = graph.nodes[end].position;
            let a = r.distance(j);
            let b = j.distance(e);
            let direction = (e - r).normalize();
            graph.nodes[joint].position = r + direction * a;
            graph.nodes[end].position = r + direction * (a + if folded { -b } else { b });
        }
        topology(&mesh(&graph, HeadPose::default()));
    }
}
