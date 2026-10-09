use crate::*;
use std::collections::{BTreeMap, BTreeSet, VecDeque};

fn perpendicular(tangent: Vec3, previous: Option<Vec3>) -> Vec3 {
    if let Some(previous) = previous {
        if let Some(n) = (previous - tangent * previous.dot(tangent)).try_normalize() {
            return n;
        }
    }
    let seed = if tangent.dot(Vec3::Y).abs() > 0.95 {
        Vec3::X
    } else {
        Vec3::Y
    };
    seed.cross(tangent).normalize()
}
impl GeneratedSkinMesh {
    fn vertex(
        &mut self,
        p: Vec3,
        node: Option<NodeId>,
        edge: Option<EdgeId>,
    ) -> Result<u32, GraphError> {
        if !p.is_finite() {
            return Err(GraphError::InvalidGeometry);
        }
        if self.positions.len() >= MAX_VERTICES {
            return Err(GraphError::ResourceLimit);
        }
        let id = u32::try_from(self.positions.len()).map_err(|_| GraphError::ResourceLimit)?;
        self.positions.push(p);
        self.source_nodes.push(node);
        self.source_edges.push(edge);
        Ok(id)
    }
    fn triangle(&mut self, a: u32, b: u32, c: u32) {
        self.indices.extend([a, b, c]);
    }
}
fn pairs(ring: &[u32]) -> impl Iterator<Item = (u32, u32)> + '_ {
    ring.iter()
        .copied()
        .zip(ring.iter().copied().cycle().skip(1))
        .take(ring.len())
}
fn bridge(mesh: &mut GeneratedSkinMesh, a: &[u32], b: &[u32]) {
    for ((a0, a1), (b0, b1)) in pairs(a).zip(pairs(b)) {
        mesh.triangle(a0, a1, b1);
        mesh.triangle(a0, b1, b0);
    }
}
fn cap(
    mesh: &mut GeneratedSkinMesh,
    ring: &[u32],
    center: Vec3,
    node: NodeId,
    start: bool,
) -> Result<(), GraphError> {
    let c = mesh.vertex(center, Some(node), None)?;
    for (a, b) in pairs(ring) {
        if start {
            mesh.triangle(c, b, a);
        } else {
            mesh.triangle(c, a, b);
        }
    }
    Ok(())
}
fn ellipsoid(
    mesh: &mut GeneratedSkinMesh,
    node: &SkinNode,
    id: NodeId,
    sides: usize,
) -> Result<(), GraphError> {
    let r = node.radii.max(Vec2::splat(MIN_RADIUS));
    let scale = Vec3::new(r.x, r.y, (r.x + r.y) * 0.5);
    let top = mesh.vertex(node.position + Vec3::Y * r.y, Some(id), None)?;
    let bottom = mesh.vertex(node.position - Vec3::Y * r.y, Some(id), None)?;
    let mut previous: Vec<u32> = Vec::new();
    let latitude_count = (sides / 2).max(3);
    for latitude in 1..latitude_count {
        let theta = std::f32::consts::PI * latitude as f32 / latitude_count as f32;
        let mut ring = Vec::new();
        for side in 0..sides {
            let phi = std::f32::consts::TAU * side as f32 / sides as f32;
            let unit = Vec3::new(
                theta.sin() * phi.cos(),
                theta.cos(),
                theta.sin() * phi.sin(),
            );
            ring.push(mesh.vertex(node.position + unit * scale, Some(id), None)?);
        }
        if previous.is_empty() {
            for (a, b) in pairs(&ring) {
                mesh.triangle(top, b, a);
            }
        } else {
            bridge(mesh, &previous, &ring);
        }
        previous = ring;
    }
    for (a, b) in pairs(&previous) {
        mesh.triangle(bottom, a, b);
    }
    Ok(())
}
/// Flat-capped edge tubes and ellipsoid overlap hubs. Branches and bends are
/// intentionally overlapping components, not a boolean-unioned manifold.
/// Output order is stable for the same ordered asset and options.
pub fn generate_skin_graph_mesh(
    graph: &SkinGraph,
    options: &SkinGraphGenerateOptions,
) -> Result<GeneratedSkinMesh, GraphError> {
    let validation = validate_skin_graph(graph)?;
    if !options.target_segment_length_factor.is_finite()
        || options.target_segment_length_factor <= 0.0
        || options.max_edge_segments == 0
    {
        return Err(GraphError::InvalidOptions);
    }
    let sides = options.ring_sides.clamp(4, 32);
    let max_segments = options.max_edge_segments.min(64);
    let mut mesh = GeneratedSkinMesh {
        diagnostics: validation.diagnostics,
        ..Default::default()
    };
    let mut degrees = BTreeMap::<NodeId, usize>::new();
    for id in &validation.valid_edges {
        let e = graph.edges.get(*id).ok_or(GraphError::InvalidEdge(*id))?;
        *degrees.entry(e.a).or_default() += 1;
        *degrees.entry(e.b).or_default() += 1;
    }
    for (id, node) in graph.nodes.iter().enumerate() {
        let degree = degrees.get(&id).copied().unwrap_or(0);
        if degree != 1 {
            ellipsoid(&mut mesh, node, id, sides)?;
            if degree >= 3 {
                mesh.diagnostics
                    .push(Diagnostic::BranchFallbackOverlap { node: id });
            }
        }
    }
    let valid: BTreeSet<_> = validation.valid_edges.into_iter().collect();
    let mut visited = BTreeSet::new();
    let mut frames = BTreeMap::new();
    // Include all nodes after roots so skipped zero edges cannot hide geometry.
    let seeds = validation.islands.iter().flat_map(|island| {
        std::iter::once(island.roots.clone()).chain(island.nodes.iter().map(|id| vec![*id]))
    });
    for seeds in seeds {
        let mut queue: VecDeque<_> = seeds.into();
        while let Some(from) = queue.pop_front() {
            for (id, edge) in graph.edges.iter().enumerate() {
                if !valid.contains(&id) || visited.contains(&id) {
                    continue;
                }
                let to = if edge.a == from {
                    edge.b
                } else if edge.b == from {
                    edge.a
                } else {
                    continue;
                };
                visited.insert(id);
                let a = graph.node(from)?;
                let b = graph.node(to)?;
                let delta = b.position - a.position;
                let tangent = delta.normalize();
                let normal = perpendicular(tangent, frames.get(&from).copied());
                let binormal = tangent.cross(normal).normalize();
                if frames.contains_key(&to) {
                    mesh.diagnostics
                        .push(Diagnostic::LoopFrameApproximated { edge: id });
                }
                frames.entry(from).or_insert(normal);
                frames.entry(to).or_insert(normal);
                queue.push_back(to);
                let ra = a.radii.max(Vec2::splat(MIN_RADIUS));
                let rb = b.radii.max(Vec2::splat(MIN_RADIUS));
                let average = (ra.x + ra.y + rb.x + rb.y) * 0.25;
                let count = ((delta.length() / (average * options.target_segment_length_factor))
                    .ceil() as usize)
                    .clamp(1, max_segments);
                let mut previous = Vec::new();
                for segment in 0..=count {
                    let t = segment as f32 / count as f32;
                    let center = a.position.lerp(b.position, t);
                    let radii = ra.lerp(rb, t);
                    let mut ring = Vec::new();
                    for side in 0..sides {
                        let angle = side as f32 / sides as f32 * std::f32::consts::TAU;
                        let p = center
                            + normal * (radii.x * angle.cos())
                            + binormal * (radii.y * angle.sin());
                        let node = if segment == 0 {
                            Some(from)
                        } else if segment == count {
                            Some(to)
                        } else {
                            None
                        };
                        ring.push(mesh.vertex(p, node, Some(id))?);
                    }
                    if segment == 0 {
                        cap(&mut mesh, &ring, a.position, from, true)?;
                    } else {
                        bridge(&mut mesh, &previous, &ring);
                    }
                    if segment == count {
                        cap(&mut mesh, &ring, b.position, to, false)?;
                    }
                    previous = ring;
                }
            }
        }
    }
    recompute_normals(&mut mesh)?;
    Ok(mesh)
}
/// Rebuild area-weighted smooth normals, rejecting malformed or collapsed faces.
pub fn recompute_normals(mesh: &mut GeneratedSkinMesh) -> Result<(), GraphError> {
    if !mesh.indices.len().is_multiple_of(3) {
        return Err(GraphError::InvalidGeometry);
    }
    let mut normals = vec![Vec3::ZERO; mesh.positions.len()];
    for &[a, b, c] in mesh.indices.as_chunks::<3>().0 {
        let p = |id: u32| {
            mesh.positions
                .get(id as usize)
                .copied()
                .ok_or(GraphError::InvalidGeometry)
        };
        let face = (p(b)? - p(a)?).cross(p(c)? - p(a)?);
        if !face.is_finite() || face.length_squared() <= 1.0e-20 {
            return Err(GraphError::InvalidGeometry);
        }
        for id in [a, b, c] {
            *normals
                .get_mut(id as usize)
                .ok_or(GraphError::InvalidGeometry)? += face;
        }
    }
    for n in &mut normals {
        *n = n.try_normalize().ok_or(GraphError::InvalidGeometry)?;
    }
    mesh.normals = normals;
    Ok(())
}
