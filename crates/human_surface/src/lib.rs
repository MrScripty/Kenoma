#![doc = include_str!("../README.md")]
// All dynamic indices below derive from a validated canonical graph, bounded
// grid dimensions, or fixed tetrahedra. Bounds are established before extraction.
#![allow(clippy::indexing_slicing)]
use glam::{Quat, Vec3};
use human_core::{GeneratedSkinMesh, SkinGraph};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeSet, HashMap};

#[derive(Clone, Copy, Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct HeadPose {
    pub yaw: f32,
    pub pitch: f32,
}
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub struct SurfaceOptions {
    pub cell_size: f32,
}
impl Default for SurfaceOptions {
    fn default() -> Self {
        Self { cell_size: 0.016 }
    }
}
#[derive(Clone, Debug, PartialEq, Eq, thiserror::Error)]
pub enum SurfaceError {
    #[error("surface requires the canonical 16-node mannequin topology with positive radii and nonzero edges")]
    InvalidGraph,
    #[error("head angles must be finite; cell_size must be between 0.008 and 0.04 metres and resolve the thinnest limb")]
    InvalidOptions,
    #[error("surface exceeds the bounded grid or output budget")]
    ResourceLimit,
    #[error("surface extraction produced invalid geometry")]
    InvalidGeometry,
}
const LINKS: [(usize, usize); 15] = [
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
];
const MAX_GRID_POINTS: usize = 2_000_000;
const MAX_SURFACE_VERTICES: usize = 300_000;
const BLEND: f32 = 0.035;
fn smooth_min(a: f32, b: f32, k: f32) -> f32 {
    let h = ((k - (a - b).abs()) / k).max(0.0);
    a.min(b) - h * h * k * 0.25
}
#[derive(Clone, Copy)]
struct Capsule {
    a: Vec3,
    delta: Vec3,
    length_sq: f32,
    ra: f32,
    rb: f32,
    source: usize,
    bound_center: Vec3,
    bound_half: Vec3,
}
impl Capsule {
    fn distance(&self, p: Vec3) -> f32 {
        let t = ((p - self.a).dot(self.delta) / self.length_sq).clamp(0.0, 1.0);
        // Zero radius derivative at both ends makes the taper meet each round
        // cap with a continuous gradient (linear taper caused visible rings).
        let taper = t * t * (3.0 - 2.0 * t);
        (p - self.a - self.delta * t).length() - (self.ra + (self.rb - self.ra) * taper)
    }
}
struct Field {
    capsules: Vec<Capsule>,
    head_center: Vec3,
    inverse_head: Quat,
}
fn ellipsoid(p: Vec3, center: Vec3, radii: Vec3) -> f32 {
    let q = p - center;
    let k0 = (q / radii).length();
    let k1 = (q / (radii * radii)).length();
    if k1 < 1e-8 {
        -radii.min_element()
    } else {
        k0 * (k0 - 1.0) / k1
    }
}
impl Field {
    fn sample(&self, p: Vec3) -> f32 {
        self.sample_inner(p, true)
    }
    fn sample_inner(&self, p: Vec3, cull: bool) -> f32 {
        let mut d = f32::INFINITY;
        for capsule in &self.capsules {
            // The signed enclosing-box distance is a lower bound on capsule
            // distance. A primitive farther than the smooth-min band cannot
            // contribute; skip its square root without changing the field.
            let lower = ((p - capsule.bound_center).abs() - capsule.bound_half).max_element();
            if cull && lower > d + BLEND {
                continue;
            }
            d = smooth_min(d, capsule.distance(p), BLEND);
        }
        // Outside the .20 m enclosing sphere, each ellipsoid estimator is
        // >= .28*(distance-.20); subtract all smooth-union blend allowances.
        // L-infinity distance is a conservative cheaper bound on that radius.
        let head_lower = ((p - self.head_center).abs().max_element() - 0.20) * 0.28 - 0.025;
        if cull && (p - self.head_center).abs().max_element() > 0.20 && head_lower > d + BLEND {
            return d;
        }
        let h = self.inverse_head * (p - self.head_center);
        // One smooth human-like silhouette: rounded cranium, flatter forehead,
        // lower face and narrowed chin. +Z front; no eyes/nose/attached primitives.
        let mut head = ellipsoid(
            h,
            Vec3::new(0.0, 0.025, -0.022),
            Vec3::new(0.117, 0.151, 0.116),
        );
        head = smooth_min(
            head,
            ellipsoid(
                h,
                Vec3::new(0.0, 0.035, 0.045),
                Vec3::new(0.099, 0.109, 0.077),
            ),
            0.028,
        );
        head = smooth_min(
            head,
            ellipsoid(
                h,
                Vec3::new(0.0, -0.067, 0.040),
                Vec3::new(0.083, 0.091, 0.071),
            ),
            0.030,
        );
        head = smooth_min(
            head,
            ellipsoid(
                h,
                Vec3::new(0.0, -0.124, 0.042),
                Vec3::new(0.057, 0.043, 0.054),
            ),
            0.025,
        );
        smooth_min(d, head, 0.035)
    }
    fn normal(&self, p: Vec3, step: f32) -> Result<Vec3, SurfaceError> {
        let x = Vec3::X * step;
        let y = Vec3::Y * step;
        let z = Vec3::Z * step;
        Vec3::new(
            self.sample(p + x) - self.sample(p - x),
            self.sample(p + y) - self.sample(p - y),
            self.sample(p + z) - self.sample(p - z),
        )
        .try_normalize()
        .filter(|n| n.is_finite())
        .ok_or(SurfaceError::InvalidGeometry)
    }
    fn source(&self, p: Vec3) -> (Option<usize>, Option<usize>) {
        let mut nearest = (f32::INFINITY, None);
        for c in &self.capsules {
            let d = c.distance(p).abs();
            if d < nearest.0 {
                nearest = (d, Some(c.source));
            }
        }
        if (p - self.head_center).length() < 0.24 {
            (Some(3), None)
        } else {
            (None, nearest.1)
        }
    }
}
fn field(
    graph: &SkinGraph,
    head: &HeadPose,
    options: &SurfaceOptions,
) -> Result<Field, SurfaceError> {
    if graph.nodes.len() != 16
        || graph.edges.len() != 15
        || human_core::validate_skin_graph(graph).is_err()
    {
        return Err(SurfaceError::InvalidGraph);
    }
    let links: BTreeSet<_> = graph
        .edges
        .iter()
        .map(|e| (e.a.min(e.b), e.a.max(e.b)))
        .collect();
    if links != LINKS.into_iter().collect()
        || !graph.nodes[0].root
        || graph.nodes.iter().skip(1).any(|n| n.root)
        || graph
            .nodes
            .iter()
            .any(|n| n.radii.min_element() < 0.02 || n.radii.max_element() > 0.4)
    {
        return Err(SurfaceError::InvalidGraph);
    }
    if !head.yaw.is_finite()
        || !head.pitch.is_finite()
        || head.yaw.abs() > 1e6
        || head.pitch.abs() > 1e6
        || !options.cell_size.is_finite()
        || !(0.008..=0.04).contains(&options.cell_size)
        || graph
            .nodes
            .iter()
            .any(|n| options.cell_size > n.radii.min_element() * 0.7)
    {
        return Err(SurfaceError::InvalidOptions);
    }
    let mut capsules = Vec::new();
    for (source, edge) in graph.edges.iter().enumerate() {
        let a = &graph.nodes[edge.a];
        let b = &graph.nodes[edge.b];
        let delta = b.position - a.position;
        if delta.length_squared() < 1e-10 {
            return Err(SurfaceError::InvalidGraph);
        }
        // Narrow the segment entering the skull; the head field defines its shape.
        let radius = |id: usize| {
            if id == 3 {
                0.060
            } else {
                graph.nodes[id].radii.min_element()
            }
        };
        capsules.push(Capsule {
            a: a.position,
            delta,
            length_sq: delta.length_squared(),
            ra: radius(edge.a),
            rb: radius(edge.b),
            source,
            bound_center: (a.position + b.position) * 0.5,
            bound_half: delta.abs() * 0.5 + Vec3::splat(radius(edge.a).max(radius(edge.b))),
        });
    }
    // Three.js Euler YXZ with roll zero is yaw about Y then pitch about local X.
    let rotation = Quat::from_rotation_y(head.yaw) * Quat::from_rotation_x(head.pitch);
    Ok(Field {
        capsules,
        head_center: graph.nodes[3].position,
        inverse_head: rotation.conjugate(),
    })
}
fn iso_value(value: f32) -> f32 {
    if value.abs() < 1e-10 {
        1e-10
    } else {
        value
    }
}

struct Grid {
    origin: Vec3,
    step: f32,
    nx: usize,
    ny: usize,
    nz: usize,
    values: Vec<f32>,
}
impl Grid {
    fn point(&self, id: usize) -> Vec3 {
        let x = id % self.nx;
        let y = (id / self.nx) % self.ny;
        let z = id / (self.nx * self.ny);
        self.origin + Vec3::new(x as f32, y as f32, z as f32) * self.step
    }
    fn id(&self, x: usize, y: usize, z: usize) -> usize {
        (z * self.ny + y) * self.nx + x
    }
    fn new(graph: &SkinGraph, field: &Field, step: f32) -> Result<Self, SurfaceError> {
        let mut low = Vec3::splat(f32::INFINITY);
        let mut high = Vec3::splat(f32::NEG_INFINITY);
        for (id, node) in graph.nodes.iter().enumerate() {
            let margin = if id == 3 {
                0.30
            } else {
                node.radii.max_element() + BLEND * 2.0
            };
            low = low.min(node.position - Vec3::splat(margin));
            high = high.max(node.position + Vec3::splat(margin));
        }
        // Non-integer offset avoids systematic iso-value/grid coincidences.
        low -= Vec3::new(1.371, 1.173, 1.619) * step;
        let size = (high - low) / step + Vec3::splat(3.0);
        if !size.is_finite() || size.max_element() > 2048.0 {
            return Err(SurfaceError::ResourceLimit);
        }
        let [nx, ny, nz] = size.ceil().as_uvec3().to_array().map(|v| v as usize);
        let count = nx
            .checked_mul(ny)
            .and_then(|v| v.checked_mul(nz))
            .filter(|n| *n <= MAX_GRID_POINTS)
            .ok_or(SurfaceError::ResourceLimit)?;
        let mut grid = Self {
            origin: low,
            step,
            nx,
            ny,
            nz,
            values: Vec::with_capacity(count),
        };
        for id in 0..count {
            let value = field.sample(grid.point(id));
            if !value.is_finite() {
                return Err(SurfaceError::InvalidGeometry);
            }
            grid.values.push(iso_value(value));
        }
        Ok(grid)
    }
}
struct Extractor<'a> {
    grid: &'a Grid,
    field: &'a Field,
    mesh: GeneratedSkinMesh,
    edges: HashMap<(usize, usize), u32>,
}
impl Extractor<'_> {
    fn vertex(&mut self, a: usize, b: usize) -> Result<u32, SurfaceError> {
        let key = (a.min(b), a.max(b));
        if let Some(id) = self.edges.get(&key) {
            return Ok(*id);
        }
        if self.mesh.positions.len() >= MAX_SURFACE_VERTICES {
            return Err(SurfaceError::ResourceLimit);
        }
        // Symmetric, globally welded edge interpolation. Tiny endpoint clearance
        // prevents f32 coincident vertices without changing signs or topology.
        let (a, b) = key;
        let va = self.grid.values[a];
        let vb = self.grid.values[b];
        let t = (va / (va - vb)).clamp(0.0001, 0.9999);
        let p = self.grid.point(a).lerp(self.grid.point(b), t);
        let normal = self.field.normal(p, self.grid.step * 0.2)?;
        let id =
            u32::try_from(self.mesh.positions.len()).map_err(|_| SurfaceError::ResourceLimit)?;
        let (node, edge) = self.field.source(p);
        self.mesh.positions.push(p);
        self.mesh.normals.push(normal);
        self.mesh.source_nodes.push(node);
        self.mesh.source_edges.push(edge);
        self.edges.insert(key, id);
        Ok(id)
    }
    fn triangle(&mut self, a: u32, b: u32, c: u32, outward: Vec3) -> Result<(), SurfaceError> {
        let pa = self.mesh.positions[a as usize];
        let pb = self.mesh.positions[b as usize];
        let pc = self.mesh.positions[c as usize];
        let normal = (pb - pa).cross(pc - pa);
        if !normal.is_finite() || normal.length_squared() == 0.0 {
            return Err(SurfaceError::InvalidGeometry);
        }
        if normal.dot(outward) < 0.0 {
            self.mesh.indices.extend([a, c, b]);
        } else {
            self.mesh.indices.extend([a, b, c]);
        }
        Ok(())
    }
    fn tetra(&mut self, ids: [usize; 4]) -> Result<(), SurfaceError> {
        let mut inside = Vec::with_capacity(4);
        let mut outside = Vec::with_capacity(4);
        for id in ids {
            if self.grid.values[id] < 0.0 {
                inside.push(id);
            } else {
                outside.push(id);
            }
        }
        if inside.is_empty() || outside.is_empty() {
            return Ok(());
        }
        let center = |set: &[usize]| {
            set.iter().map(|id| self.grid.point(*id)).sum::<Vec3>() / set.len() as f32
        };
        let outward = center(&outside) - center(&inside);
        if inside.len() == 1 || outside.len() == 1 {
            let (one, many) = if inside.len() == 1 {
                (&inside, &outside)
            } else {
                (&outside, &inside)
            };
            let a = self.vertex(one[0], many[0])?;
            let b = self.vertex(one[0], many[1])?;
            let c = self.vertex(one[0], many[2])?;
            self.triangle(a, b, c, outward)?;
        } else {
            let a = self.vertex(inside[0], outside[0])?;
            let b = self.vertex(inside[0], outside[1])?;
            let c = self.vertex(inside[1], outside[0])?;
            let d = self.vertex(inside[1], outside[1])?;
            self.triangle(a, b, c, outward)?;
            self.triangle(b, d, c, outward)?;
        }
        Ok(())
    }
}
/// Generate one indexed smooth surface, independent of rendering and research.
/// The source graph is never changed. Mesh IDs are deterministic for an exact
/// input but not stable across pose/resolution changes. +Y up, +Z head front.
pub fn generate_mannequin_surface(
    graph: &SkinGraph,
    head: &HeadPose,
    options: &SurfaceOptions,
) -> Result<GeneratedSkinMesh, SurfaceError> {
    let field = field(graph, head, options)?;
    let grid = Grid::new(graph, &field, options.cell_size)?;
    extract(&grid, &field)
}

fn extract(grid: &Grid, field: &Field) -> Result<GeneratedSkinMesh, SurfaceError> {
    let mut extractor = Extractor {
        grid,
        field,
        mesh: GeneratedSkinMesh::default(),
        edges: HashMap::new(),
    };
    // Conforming Freudenthal split: shared cube faces have identical diagonals.
    const TETRA: [[usize; 4]; 6] = [
        [0, 1, 3, 7],
        [0, 3, 2, 7],
        [0, 2, 6, 7],
        [0, 6, 4, 7],
        [0, 4, 5, 7],
        [0, 5, 1, 7],
    ];
    for z in 0..grid.nz - 1 {
        for y in 0..grid.ny - 1 {
            for x in 0..grid.nx - 1 {
                let ids = [
                    grid.id(x, y, z),
                    grid.id(x + 1, y, z),
                    grid.id(x, y + 1, z),
                    grid.id(x + 1, y + 1, z),
                    grid.id(x, y, z + 1),
                    grid.id(x + 1, y, z + 1),
                    grid.id(x, y + 1, z + 1),
                    grid.id(x + 1, y + 1, z + 1),
                ];
                let signs = ids.map(|id| grid.values[id] < 0.0);
                if signs.iter().all(|s| *s) || signs.iter().all(|s| !*s) {
                    continue;
                }
                for tetra in TETRA {
                    extractor.tetra(tetra.map(|i| ids[i]))?;
                }
            }
        }
    }
    if extractor.mesh.indices.is_empty() {
        return Err(SurfaceError::InvalidGeometry);
    }
    Ok(extractor.mesh)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn tapered_capsule_gradient_is_continuous_at_end_caps() {
        let capsule = Capsule {
            a: Vec3::ZERO,
            delta: Vec3::Y,
            length_sq: 1.0,
            ra: 0.10,
            rb: 0.20,
            source: 0,
            bound_center: Vec3::Y * 0.5,
            bound_half: Vec3::new(0.2, 0.7, 0.2),
        };
        let epsilon = 0.0001;
        for end in [0.0, 1.0] {
            let p = Vec3::new(0.18, end, 0.0);
            let left = (capsule.distance(p) - capsule.distance(p - Vec3::Y * epsilon)) / epsilon;
            let right = (capsule.distance(p + Vec3::Y * epsilon) - capsule.distance(p)) / epsilon;
            assert!((left - right).abs() < 0.002, "{left} != {right}");
        }
    }
    #[test]
    fn exact_iso_lattice_vertices_stay_welded_without_holes() -> Result<(), SurfaceError> {
        let graph = human_core::mannequin();
        let field = field(&graph, &HeadPose::default(), &SurfaceOptions::default())?;
        let mut grid = Grid {
            origin: Vec3::new(-1.0, 0.0, -1.0),
            step: 1.0,
            nx: 3,
            ny: 3,
            nz: 3,
            values: Vec::new(),
        };
        let mut ties = 0;
        for id in 0..27 {
            let value = (grid.point(id) - Vec3::Y).length() - 1.0;
            if value == 0.0 {
                ties += 1;
            }
            grid.values.push(iso_value(value));
        }
        assert_eq!(ties, 6);
        let mesh = extract(&grid, &field)?;
        let mut edges = std::collections::BTreeMap::new();
        let mut points = BTreeSet::new();
        for point in &mesh.positions {
            assert!(points.insert(point.to_array().map(f32::to_bits)));
        }
        for &[a, b, c] in mesh.indices.as_chunks::<3>().0 {
            for (u, v) in [(a, b), (b, c), (c, a)] {
                let count = edges.entry((u.min(v), u.max(v))).or_insert((0, 0));
                count.0 += 1;
                count.1 += if u < v { 1 } else { -1 };
            }
        }
        assert!(edges.values().all(|counts| *counts == (2, 0)));
        Ok(())
    }
    #[test]
    fn field_culling_preserves_samples_and_outward_normals() -> Result<(), SurfaceError> {
        let graph = human_core::mannequin();
        let field = field(
            &graph,
            &HeadPose {
                yaw: 1.1,
                pitch: -0.7,
            },
            &SurfaceOptions::default(),
        )?;
        for z in -9..10 {
            for y in -2..24 {
                for x in -13..14 {
                    let p = Vec3::new(x as f32 * 0.091, y as f32 * 0.087, z as f32 * 0.081);
                    assert_eq!(field.sample_inner(p, true), field.sample_inner(p, false));
                }
            }
        }
        let mesh = generate_mannequin_surface(
            &graph,
            &HeadPose {
                yaw: 1.1,
                pitch: -0.7,
            },
            &SurfaceOptions::default(),
        )?;
        for (p, n) in mesh.positions.iter().zip(&mesh.normals) {
            assert!(field.sample(*p + *n * 0.001) > field.sample(*p - *n * 0.001));
        }
        Ok(())
    }
}
