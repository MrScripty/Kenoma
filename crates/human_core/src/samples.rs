use crate::*;
/// A deliberately schematic +Y-up human. Edge order and node IDs are stable.
/// Pelvis=0, chest=1, neck=2, head=3; arms=4..9; legs=10..15.
pub fn mannequin() -> SkinGraph {
    let points = [
        (0., 0.95, 0., 0.16),
        (0., 1.35, 0., 0.21),
        (0., 1.55, 0., 0.07),
        (0., 1.72, 0., 0.13),
        (0.32, 1.4, 0., 0.085),
        (0.58, 1.2, 0., 0.065),
        (0.79, 1.0, 0., 0.055),
        (-0.32, 1.4, 0., 0.085),
        (-0.58, 1.2, 0., 0.065),
        (-0.79, 1.0, 0., 0.055),
        (0.15, 0.85, 0., 0.10),
        (0.15, 0.48, 0., 0.075),
        (0.15, 0.08, 0.08, 0.065),
        (-0.15, 0.85, 0., 0.10),
        (-0.15, 0.48, 0., 0.075),
        (-0.15, 0.08, 0.08, 0.065),
    ];
    let nodes = points
        .into_iter()
        .enumerate()
        .map(|(id, (x, y, z, r))| SkinNode {
            position: Vec3::new(x, y, z),
            radii: Vec2::splat(r),
            root: id == 0,
        })
        .collect();
    let edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (1, 4),
        (4, 5),
        (5, 6),
        (1, 7),
        (7, 8),
        (8, 9),
        (0, 10),
        (10, 11),
        (11, 12),
        (0, 13),
        (13, 14),
        (14, 15),
    ]
    .into_iter()
    .map(|(a, b)| SkinEdge { a, b })
    .collect();
    SkinGraph { nodes, edges }
}
pub fn sample_graphs() -> Vec<(&'static str, SkinGraph)> {
    let node = |x, y| SkinNode::new(Vec3::new(x, y, 0.), Vec2::splat(DEFAULT_RADIUS));
    let make = |nodes: Vec<SkinNode>, edges: Vec<SkinEdge>| SkinGraph { nodes, edges };
    vec![
        ("isolated", make(vec![node(0., 0.)], vec![])),
        (
            "edge",
            make(
                vec![node(0., 0.), node(0., 1.)],
                vec![SkinEdge { a: 0, b: 1 }],
            ),
        ),
        (
            "bent-chain",
            make(
                vec![node(0., 0.), node(0., 1.), node(1., 2.), node(2., 2.)],
                vec![
                    SkinEdge { a: 0, b: 1 },
                    SkinEdge { a: 1, b: 2 },
                    SkinEdge { a: 2, b: 3 },
                ],
            ),
        ),
        (
            "branch",
            make(
                vec![node(0., 0.), node(0., 1.), node(1., 0.), node(-1., 0.)],
                vec![
                    SkinEdge { a: 0, b: 1 },
                    SkinEdge { a: 0, b: 2 },
                    SkinEdge { a: 0, b: 3 },
                ],
            ),
        ),
        ("missing-root", make(vec![node(0., 0.)], vec![])),
        ("mannequin", mannequin()),
    ]
    .into_iter()
    .map(|(name, mut graph)| {
        if name != "missing-root" {
            if let Some(first) = graph.nodes.first_mut() {
                first.root = true;
            }
        }
        (name, graph)
    })
    .collect()
}
