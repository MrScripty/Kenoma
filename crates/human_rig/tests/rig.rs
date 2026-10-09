#![allow(clippy::indexing_slicing)]
use human_core::{mannequin, GeneratedSkinMesh, SkinGraph, Vec3};
use human_rig::{bind_mannequin, deform_mannequin, BoundRig, RigError};
use human_surface::{HeadPose, SurfaceOptions};
use std::sync::OnceLock;
fn bound() -> &'static BoundRig {
    static RIG: OnceLock<BoundRig> = OnceLock::new();
    RIG.get_or_init(|| match bind_mannequin(&SurfaceOptions::default()) {
        Ok(r) => r,
        Err(e) => panic!("{e}"),
    })
}
fn ik(graph: &mut SkinGraph, [r, j, e]: [usize; 3], target: Vec3, pole: Vec3) {
    let root = graph.nodes[r].position;
    let joint = graph.nodes[j].position;
    let end = graph.nodes[e].position;
    let a = root.distance(joint);
    let b = joint.distance(end);
    let delta = target - root;
    let requested = delta.length();
    let direction = if requested > 1e-10 {
        delta / requested
    } else {
        (end - root).normalize()
    };
    let distance = requested.clamp((a - b).abs().max(1e-9 * a.max(b)), a + b);
    let mut bend = pole - root - direction * (pole - root).dot(direction);
    if bend.length() < 1e-9 {
        bend = joint - root - direction * (joint - root).dot(direction);
    }
    bend = bend.normalize();
    let along = (distance + (a - b) * (a + b) / distance) * 0.5;
    let height = (a * a - along * along).max(0.0).sqrt();
    graph.nodes[j].position = root + direction * along + bend * height;
    graph.nodes[e].position = root + direction * distance;
}
fn cases() -> Vec<(&'static str, SkinGraph)> {
    let mut hand = mannequin();
    ik(
        &mut hand,
        [4, 5, 6],
        Vec3::new(0.04, 1.22, 0.20),
        Vec3::new(0.62, 1.08, 0.30),
    );
    let mut arms = mannequin();
    ik(
        &mut arms,
        [4, 5, 6],
        Vec3::new(-0.18, 1.28, 0.24),
        Vec3::new(0.45, 0.95, 0.28),
    );
    ik(
        &mut arms,
        [7, 8, 9],
        Vec3::new(0.18, 1.18, 0.28),
        Vec3::new(-0.45, 0.94, 0.30),
    );
    let mut legs = mannequin();
    ik(
        &mut legs,
        [10, 11, 12],
        Vec3::new(-0.17, 0.14, 0.16),
        Vec3::new(0.16, 0.45, 0.36),
    );
    ik(
        &mut legs,
        [13, 14, 15],
        Vec3::new(0.18, 0.14, -0.06),
        Vec3::new(-0.16, 0.45, 0.22),
    );
    let mut deep = mannequin();
    ik(
        &mut deep,
        [4, 5, 6],
        Vec3::new(0.34, 1.38, 0.06),
        Vec3::new(0.70, 1.7, 0.20),
    );
    ik(
        &mut deep,
        [10, 11, 12],
        Vec3::new(0.17, 0.75, 0.15),
        Vec3::new(0.15, 0.40, 0.60),
    );
    vec![
        ("hand-on-torso", hand),
        ("crossed-arms", arms),
        ("crossed-legs", legs),
        ("deep-bends", deep),
    ]
}
fn valid_mesh(mesh: &GeneratedSkinMesh) {
    assert_eq!(mesh.positions.len(), mesh.normals.len());
    for (p, n) in mesh.positions.iter().zip(&mesh.normals) {
        assert!(p.is_finite() && n.is_finite());
        assert!((n.length() - 1.0).abs() < 1e-5);
    }
    let mut volume = 0.0;
    for &[a, b, c] in mesh.indices.as_chunks::<3>().0 {
        let [a, b, c] = [
            mesh.positions[a as usize],
            mesh.positions[b as usize],
            mesh.positions[c as usize],
        ];
        let area = (b - a).cross(c - a);
        assert!(area.length_squared() > 0.0);
        volume += a.as_dvec3().dot(b.as_dvec3().cross(c.as_dvec3())) / 6.0;
    }
    assert!(volume > 0.0, "overall outward winding");
}
#[test]
fn contacts_preserve_exact_topology_provenance_and_independent_rig() {
    let rig = bound();
    let original = rig.clone();
    for (name, pose) in cases() {
        let before = pose.clone();
        let start = std::time::Instant::now();
        let mesh = match deform_mannequin(rig, &pose, &HeadPose::default()) {
            Ok(m) => m,
            Err(e) => panic!("{name}: {e}"),
        };
        eprintln!(
            "{name}: {} vertices in {:?}",
            mesh.positions.len(),
            start.elapsed()
        );
        assert_eq!(mesh.indices, rig.mesh.indices);
        assert_eq!(mesh.positions.len(), rig.mesh.positions.len());
        assert_eq!(mesh.source_nodes, rig.mesh.source_nodes);
        assert_eq!(mesh.source_edges, rig.mesh.source_edges);
        valid_mesh(&mesh);
        assert_eq!(pose, before);
        let repeat = match deform_mannequin(rig, &pose, &HeadPose::default()) {
            Ok(m) => m,
            Err(e) => panic!("{e}"),
        };
        assert_eq!(mesh, repeat);
    }
    assert_eq!(*rig, original);
}
#[test]
fn rest_pose_roundtrips_exactly_and_weights_are_local() {
    let rig = bound();
    assert_eq!(
        deform_mannequin(rig, &rig.rest_graph, &HeadPose::default()),
        Ok(rig.mesh.clone())
    );
    assert_eq!(rig.validate(), Ok(()));
    for weights in &rig.weights {
        let active: Vec<_> = weights
            .bones
            .iter()
            .zip(weights.weights)
            .filter(|(_, w)| *w > 0.001)
            .map(|(b, _)| *b)
            .collect();
        // No rest vertex mixes an arm with its opposite arm or with leg bones.
        let right = active.iter().any(|b| (4..=5).contains(b));
        let left = active.iter().any(|b| (7..=8).contains(b));
        let leg = active.iter().any(|b| [10, 11, 13, 14].contains(b));
        assert!(!(right && left));
        assert!(!((right || left) && leg));
    }
}
#[test]
fn deep_joint_cross_sections_retain_radius() {
    let rig = bound();
    let poses = cases();
    let Some((_, pose)) = poses.last() else {
        panic!("missing deep pose")
    };
    let mesh = match deform_mannequin(rig, pose, &HeadPose::default()) {
        Ok(m) => m,
        Err(e) => panic!("{e}"),
    };
    for (joint, bones) in [(5, [4u16, 5u16]), (11, [10u16, 11u16])] {
        let mut rest_points = Vec::new();
        let mut pose_points = Vec::new();
        let mut rest_distances = Vec::new();
        let mut posed_distances = Vec::new();
        for (i, weights) in rig.weights.iter().enumerate() {
            let a: f32 = weights
                .bones
                .iter()
                .zip(weights.weights)
                .filter(|(id, _)| **id == bones[0])
                .map(|(_, w)| w)
                .sum();
            let b: f32 = weights
                .bones
                .iter()
                .zip(weights.weights)
                .filter(|(id, _)| **id == bones[1])
                .map(|(_, w)| w)
                .sum();
            if a > 0.35
                && b > 0.35
                && rig.mesh.positions[i].distance(rig.rest_graph.nodes[joint].position) < 0.11
            {
                rest_points.push(rig.mesh.positions[i] - rig.rest_graph.nodes[joint].position);
                pose_points.push(mesh.positions[i] - pose.nodes[joint].position);
                rest_distances
                    .push(rig.mesh.positions[i].distance(rig.rest_graph.nodes[joint].position));
                posed_distances.push(mesh.positions[i].distance(pose.nodes[joint].position));
            }
        }
        assert!(rest_distances.len() > 10);
        rest_distances.sort_by(f32::total_cmp);
        posed_distances.sort_by(f32::total_cmp);
        let n = rest_distances.len();
        let ratio = posed_distances[n / 2] / rest_distances[n / 2];
        eprintln!("joint {joint} midpoint skin radial ratio: {ratio}");
        assert!(
            (0.65..1.6).contains(&ratio),
            "joint {joint} radial collapse/bloat: {ratio}"
        );
        let tangent = |g: &SkinGraph| {
            ((g.nodes[joint].position - g.nodes[joint - 1].position).normalize()
                + (g.nodes[joint + 1].position - g.nodes[joint].position).normalize())
            .normalize()
        };
        let covariance = |points: &[Vec3], axis: Vec3| {
            let seed = if axis.x.abs() < 0.9 { Vec3::X } else { Vec3::Z };
            let x = axis.cross(seed).normalize();
            let y = axis.cross(x);
            let mean = points.iter().copied().sum::<Vec3>() / points.len() as f32;
            let mut xx = 0.0;
            let mut yy = 0.0;
            let mut xy = 0.0;
            for p in points {
                let a = (*p - mean).dot(x);
                let b = (*p - mean).dot(y);
                xx += a * a;
                yy += b * b;
                xy += a * b;
            }
            let trace = xx + yy;
            let discriminant = ((xx - yy) * (xx - yy) + 4.0 * xy * xy).sqrt();
            [
                (trace - discriminant) / (2.0 * points.len() as f32),
                (trace + discriminant) / (2.0 * points.len() as f32),
            ]
        };
        let rest = covariance(&rest_points, tangent(&rig.rest_graph));
        let posed = covariance(&pose_points, tangent(pose));
        let narrow = (posed[0] / rest[0]).sqrt();
        let broad = (posed[1] / rest[1]).sqrt();
        eprintln!(
            "joint {joint} projected crosssection radius ratios {narrow}/{broad}; area ratio {}",
            narrow * broad
        );
        assert!(narrow > 0.65 && broad < 1.6, "crosssection collapse/bloat");
    }
}
#[test]
fn head_limits_are_finite_fixed_topology() {
    let rig = bound();
    for yaw in [-120f32.to_radians(), 120f32.to_radians()] {
        for pitch in [-60f32.to_radians(), 60f32.to_radians()] {
            let mesh = match deform_mannequin(rig, &rig.rest_graph, &HeadPose { yaw, pitch }) {
                Ok(m) => m,
                Err(e) => panic!("{e}"),
            };
            valid_mesh(&mesh);
            assert_eq!(mesh.indices, rig.mesh.indices);
        }
    }
}
#[test]
fn malformed_rig_and_pose_rejected() {
    let rig = bound();
    let mut invalid = rig.clone();
    invalid.version = 2;
    assert_eq!(invalid.validate(), Err(RigError::InvalidRig));
    invalid = rig.clone();
    invalid.weights[0].weights[0] = f32::NAN;
    assert_eq!(invalid.validate(), Err(RigError::InvalidRig));
    invalid = rig.clone();
    invalid.weights[0].bones[0] = 16;
    assert_eq!(invalid.validate(), Err(RigError::InvalidRig));
    let mut pose = mannequin();
    pose.nodes[6].position.x += 0.1;
    assert_eq!(
        deform_mannequin(rig, &pose, &HeadPose::default()),
        Err(RigError::InvalidPose)
    );
    assert_eq!(
        deform_mannequin(
            rig,
            &mannequin(),
            &HeadPose {
                yaw: f32::NAN,
                pitch: 0.0
            }
        ),
        Err(RigError::InvalidPose)
    );
}
#[test]
fn versioned_binding_serialization_roundtrips() {
    let rig = bound();
    let json = match serde_json::to_string(rig) {
        Ok(s) => s,
        Err(e) => panic!("{e}"),
    };
    let decoded: BoundRig = match serde_json::from_str(&json) {
        Ok(s) => s,
        Err(e) => panic!("{e}"),
    };
    assert_eq!(*rig, decoded);
}

#[test]
fn compact_weights_are_continuous_and_contact_edges_do_not_spike() {
    let rig = bound();
    let dense = |weights: &human_rig::VertexWeights| {
        let mut values = [0.0f32; 16];
        for (bone, w) in weights.bones.iter().zip(weights.weights) {
            values[*bone as usize] += w;
        }
        values
    };
    let all_weights: Vec<_> = rig.weights.iter().map(dense).collect();
    let mut max_gradient = 0.0f32;
    for &[a, b, c] in rig.mesh.indices.as_chunks::<3>().0 {
        for (a, b) in [(a, b), (b, c), (c, a)] {
            let (a, b) = (a as usize, b as usize);
            let length = rig.mesh.positions[a].distance(rig.mesh.positions[b]);
            let difference: f32 = all_weights[a]
                .iter()
                .zip(all_weights[b])
                .map(|(x, y)| (x - y).abs())
                .sum();
            max_gradient = max_gradient.max(difference / length);
        }
    }
    eprintln!("maximum adjacent weight L1 gradient: {max_gradient}/m");
    assert!(max_gradient < 100.0, "weight seam");
    for (name, pose) in cases() {
        let mesh = match deform_mannequin(rig, &pose, &HeadPose::default()) {
            Ok(m) => m,
            Err(e) => panic!("{e}"),
        };
        let mut stretch = Vec::new();
        for &[a, b, c] in rig.mesh.indices.as_chunks::<3>().0 {
            for (a, b) in [(a, b), (b, c), (c, a)] {
                let (a, b) = (a as usize, b as usize);
                stretch.push(
                    mesh.positions[a].distance(mesh.positions[b])
                        / rig.mesh.positions[a].distance(rig.mesh.positions[b]),
                );
            }
        }
        stretch.sort_by(f32::total_cmp);
        let max = stretch[stretch.len() - 1];
        let p99 = stretch[stretch.len() * 99 / 100];
        eprintln!("{name}: maximum edge stretch {max}, p99 {p99}");
        assert!(max < 6.0 && p99 < 3.0, "deformation seam/spike: {name}");
    }
}

#[test]
fn arm_pose_preserves_analytic_head_and_unaffected_leg_shading() {
    let rig = bound();
    let cases = cases();
    let pose = &cases[0].1;
    let posed = match deform_mannequin(rig, pose, &HeadPose::default()) {
        Ok(mesh) => mesh,
        Err(e) => panic!("{e}"),
    };
    let mut checked = 0;
    for (i, p) in rig.mesh.positions.iter().enumerate() {
        if p.y > 1.64 || p.y < 0.80 {
            assert!(p.distance(posed.positions[i]) < 1e-6);
            assert!(
                rig.mesh.normals[i].distance(posed.normals[i]) < 1e-4,
                "unchanged smooth normal at {p:?}"
            );
            checked += 1;
        }
    }
    assert!(checked > 1000);
}

#[test]
fn corrected_normals_are_finite_unit_and_follow_surface_winding() {
    let rig = bound();
    for (name, pose) in cases() {
        let mesh = match deform_mannequin(rig, &pose, &HeadPose::default()) {
            Ok(m) => m,
            Err(e) => panic!("{e}"),
        };
        valid_mesh(&mesh);
        let mut opposite_area = 0.0;
        let mut total_area = 0.0;
        for &[a, b, c] in mesh.indices.as_chunks::<3>().0 {
            let geometric = (mesh.positions[b as usize] - mesh.positions[a as usize])
                .cross(mesh.positions[c as usize] - mesh.positions[a as usize]);
            let average =
                mesh.normals[a as usize] + mesh.normals[b as usize] + mesh.normals[c as usize];
            total_area += geometric.length();
            if geometric.dot(average) < 0.0 {
                opposite_area += geometric.length();
            }
        }
        eprintln!(
            "{name}: opposite shading-normal area fraction {}",
            opposite_area / total_area
        );
        assert!(
            opposite_area / total_area < 0.001,
            "normals face against winding"
        );
    }
}
