#![doc = include_str!("../README.md")]
// Dynamic indices are validated input bone/mesh IDs or canonical graph indices.
#![allow(clippy::indexing_slicing)]
use glam::{Quat, Vec3};
use human_core::{mannequin, GeneratedSkinMesh, SkinGraph};
use human_surface::{generate_mannequin_surface, HeadPose, SurfaceOptions};
use serde::{Deserialize, Serialize};

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
const MAX_VERTICES: usize = 300_000;
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct VertexWeights {
    pub bones: [u16; 8],
    pub weights: [f32; 8],
}
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct BoundRig {
    pub version: u32,
    pub rest_graph: SkinGraph,
    pub head_rest: HeadPose,
    pub mesh: GeneratedSkinMesh,
    pub weights: Vec<VertexWeights>,
}
#[derive(Clone, Debug, PartialEq, Eq, thiserror::Error)]
pub enum RigError {
    #[error("invalid or unsupported bound mannequin rig")]
    InvalidRig,
    #[error("pose must preserve the canonical graph topology and rest bone lengths; head angles must be finite")]
    InvalidPose,
    #[error("invalid deformed geometry")]
    InvalidGeometry,
    #[error("rest surface: {0}")]
    Surface(#[from] human_surface::SurfaceError),
}
fn smoothstep(t: f32) -> f32 {
    let t = t.clamp(0.0, 1.0);
    t * t * (3.0 - 2.0 * t)
}
fn proximity(graph: &SkinGraph, edge: usize, p: Vec3) -> f32 {
    let (a, b) = LINKS[edge];
    let a = &graph.nodes[a];
    let b = &graph.nodes[b];
    let delta = b.position - a.position;
    let t = ((p - a.position).dot(delta) / delta.length_squared()).clamp(0.0, 1.0);
    let radius =
        a.radii.min_element() + (b.radii.min_element() - a.radii.min_element()) * smoothstep(t);
    // Radius-aware distance avoids assigning shoulder skin to a distant thick
    // torso merely because the torso axis is long; no posed-space rebinding.
    (p - a.position - delta * t).length() / radius.max(0.02)
}
fn weights(graph: &SkinGraph, p: Vec3) -> Result<VertexWeights, RigError> {
    let head = graph.nodes[3].position;
    // Smooth neck transition with no guard/candidate discontinuity. The lower
    // jaw/neck connection blends while the cranium is rigidly head-controlled.
    let head_mix = smoothstep((p.y - (head.y - 0.22)) / 0.10);
    let mut result = VertexWeights {
        bones: [0; 8],
        weights: [0.0; 8],
    };
    let mut count = 0;
    if head_mix < 1.0 {
        for bone in 0..15 {
            // Compact C1 kernel: both value and derivative vanish at support.
            // No nearest-bone switching or top-N pruning. In canonical rest
            // space this narrow support excludes unrelated active limbs.
            let distance = proximity(graph, bone, p) / 1.65;
            if distance < 1.0 {
                if count >= 8 {
                    return Err(RigError::InvalidRig);
                }
                result.bones[count] = bone as u16;
                result.weights[count] = (1.0 - distance * distance).powi(2);
                count += 1;
            }
        }
        let total: f32 = result.weights.iter().sum();
        if total <= 0.0 {
            return Err(RigError::InvalidRig);
        }
        for weight in &mut result.weights {
            *weight = *weight / total * (1.0 - head_mix);
        }
    }
    if head_mix > 0.0 {
        if count >= 8 {
            return Err(RigError::InvalidRig);
        }
        result.bones[count] = 15;
        result.weights[count] = head_mix;
    }
    Ok(result)
}
/// Extract the connected neutral surface once, then bind up to eight local bones
/// per vertex. Weights and topology remain unchanged for every subsequent pose.
pub fn bind_mannequin(options: &SurfaceOptions) -> Result<BoundRig, RigError> {
    let rest_graph = mannequin();
    let head_rest = HeadPose::default();
    let mesh = generate_mannequin_surface(&rest_graph, &head_rest, options)?;
    let weights = mesh
        .positions
        .iter()
        .map(|p| weights(&rest_graph, *p))
        .collect::<Result<Vec<_>, _>>()?;
    Ok(BoundRig {
        version: 1,
        rest_graph,
        head_rest,
        mesh,
        weights,
    })
}
#[derive(Clone, Copy)]
struct DualQuat {
    real: Quat,
    dual: Quat,
}
impl DualQuat {
    fn rigid(rotation: Quat, translation: Vec3) -> Self {
        Self {
            real: rotation,
            dual: Quat::from_xyzw(translation.x, translation.y, translation.z, 0.0)
                * rotation
                * 0.5,
        }
    }
    fn blend(bones: &[Self; 16], weights: &VertexWeights) -> Result<Self, RigError> {
        let reference = bones[weights.bones[0] as usize].real;
        let mut real = Quat::from_xyzw(0.0, 0.0, 0.0, 0.0);
        let mut dual = real;
        for i in 0..8 {
            if weights.weights[i] == 0.0 {
                continue;
            }
            let bone = bones[weights.bones[i] as usize];
            let sign = if reference.dot(bone.real) < 0.0 {
                -1.0
            } else {
                1.0
            };
            real += bone.real * (weights.weights[i] * sign);
            dual += bone.dual * (weights.weights[i] * sign);
        }
        let length = real.length();
        if !length.is_finite() || length < 1e-6 {
            return Err(RigError::InvalidGeometry);
        }
        real /= length;
        dual /= length;
        dual = dual - real * real.dot(dual);
        Ok(Self { real, dual })
    }
    fn position(self, p: Vec3) -> Vec3 {
        let translation = (self.dual * self.real.conjugate()) * 2.0;
        self.real * p + Vec3::new(translation.x, translation.y, translation.z)
    }
}
impl BoundRig {
    /// Structural/numeric validation for a serialized rig. This does not certify
    /// externally edited meshes as originating from the canonical bind function.
    pub fn validate(&self) -> Result<(), RigError> {
        let n = self.mesh.positions.len();
        if self.version != 1
            || self.rest_graph != mannequin()
            || self.head_rest != HeadPose::default()
            || n == 0
            || n > MAX_VERTICES
            || self.mesh.normals.len() != n
            || self.weights.len() != n
            || self.mesh.source_nodes.len() != n
            || self.mesh.source_edges.len() != n
            || self.mesh.indices.is_empty()
            || !self.mesh.indices.len().is_multiple_of(3)
            || self.mesh.indices.len() > MAX_VERTICES * 12
        {
            return Err(RigError::InvalidRig);
        }
        if self
            .mesh
            .positions
            .iter()
            .any(|p| !p.is_finite() || p.abs().max_element() > 10.0)
            || self
                .mesh
                .normals
                .iter()
                .any(|p| !p.is_finite() || (p.length() - 1.0).abs() > 0.01)
            || self.mesh.indices.iter().any(|i| *i as usize >= n)
        {
            return Err(RigError::InvalidRig);
        }
        for weights in &self.weights {
            if weights.bones.iter().any(|i| *i >= 16)
                || weights
                    .weights
                    .iter()
                    .any(|w| !w.is_finite() || *w < 0.0 || *w > 1.0)
                || (weights.weights.iter().sum::<f32>() - 1.0).abs() > 1e-4
            {
                return Err(RigError::InvalidRig);
            }
        }
        for &[a, b, c] in self.mesh.indices.as_chunks::<3>().0 {
            if a == b
                || a == c
                || b == c
                || (self.mesh.positions[b as usize] - self.mesh.positions[a as usize])
                    .cross(self.mesh.positions[c as usize] - self.mesh.positions[a as usize])
                    .length_squared()
                    == 0.0
            {
                return Err(RigError::InvalidRig);
            }
        }
        Ok(())
    }
}
fn transforms(
    rig: &BoundRig,
    pose: &SkinGraph,
    head: &HeadPose,
) -> Result<[DualQuat; 16], RigError> {
    if pose.nodes.len() != 16
        || pose.edges != rig.rest_graph.edges
        || !head.yaw.is_finite()
        || !head.pitch.is_finite()
        || head.yaw.abs() > 1e6
        || head.pitch.abs() > 1e6
        || human_core::validate_skin_graph(pose).is_err()
    {
        return Err(RigError::InvalidPose);
    }
    if pose
        .nodes
        .iter()
        .zip(&rig.rest_graph.nodes)
        .any(|(p, r)| p.radii != r.radii || p.root != r.root)
    {
        return Err(RigError::InvalidPose);
    }
    let identity = DualQuat::rigid(Quat::IDENTITY, Vec3::ZERO);
    let mut result = [identity; 16];
    for (bone, (a, b)) in LINKS.into_iter().enumerate() {
        let rest_a = rig.rest_graph.nodes[a].position;
        let rest_b = rig.rest_graph.nodes[b].position;
        let pose_a = pose.nodes[a].position;
        let pose_b = pose.nodes[b].position;
        if ((pose_b - pose_a).length() - (rest_b - rest_a).length()).abs() > 0.0002 {
            return Err(RigError::InvalidPose);
        }
        let rotation =
            Quat::from_rotation_arc((rest_b - rest_a).normalize(), (pose_b - pose_a).normalize());
        result[bone] = DualQuat::rigid(rotation, pose_a - rotation * rest_a);
    }
    let rotation = Quat::from_rotation_y(head.yaw) * Quat::from_rotation_x(head.pitch);
    result[15] = DualQuat::rigid(
        rotation,
        pose.nodes[3].position - rotation * rig.rest_graph.nodes[3].position,
    );
    Ok(result)
}
/// Deform an immutable bound rest mesh. Exact index buffers/vertex IDs are kept;
/// contact never welds vertices, though unrelated surfaces may interpenetrate.
pub fn deform_mannequin(
    rig: &BoundRig,
    pose: &SkinGraph,
    head: &HeadPose,
) -> Result<GeneratedSkinMesh, RigError> {
    rig.validate()?;
    let bones = transforms(rig, pose, head)?;
    if *pose == rig.rest_graph && *head == rig.head_rest {
        return Ok(rig.mesh.clone());
    }
    // Remove rest tessellation bias before carrying the analytic smooth normal
    // into the posed field. Recomputing only triangle normals exposes the
    // marching-tetrahedra diagonal pattern even in unchanged regions.
    let mut rest_discrete = vec![Vec3::ZERO; rig.mesh.positions.len()];
    for &[a, b, c] in rig.mesh.indices.as_chunks::<3>().0 {
        let normal = (rig.mesh.positions[b as usize] - rig.mesh.positions[a as usize])
            .cross(rig.mesh.positions[c as usize] - rig.mesh.positions[a as usize]);
        for id in [a, b, c] {
            rest_discrete[id as usize] += normal;
        }
    }
    for (normal, analytic) in rest_discrete.iter_mut().zip(&rig.mesh.normals) {
        *normal = normal.try_normalize().unwrap_or(*analytic);
    }
    let mut mesh = rig.mesh.clone();
    let mut correction = Vec::with_capacity(mesh.positions.len());
    let mut fallback = Vec::with_capacity(mesh.positions.len());
    for (i, (p, weights)) in rig.mesh.positions.iter().zip(&rig.weights).enumerate() {
        let blend = DualQuat::blend(&bones, weights)?;
        let posed = blend.position(*p);
        if !posed.is_finite() {
            return Err(RigError::InvalidGeometry);
        }
        mesh.positions[i] = posed;
        fallback.push(blend.real * rig.mesh.normals[i]);
        correction.push(blend.real * (rig.mesh.normals[i] - rest_discrete[i]));
    }
    mesh.normals.fill(Vec3::ZERO);
    for &[a, b, c] in mesh.indices.as_chunks::<3>().0 {
        let normal = (mesh.positions[b as usize] - mesh.positions[a as usize])
            .cross(mesh.positions[c as usize] - mesh.positions[a as usize]);
        if !normal.is_finite() || normal.length_squared() == 0.0 {
            return Err(RigError::InvalidGeometry);
        }
        for id in [a, b, c] {
            mesh.normals[id as usize] += normal;
        }
    }
    for ((normal, fallback), correction) in mesh.normals.iter_mut().zip(fallback).zip(correction) {
        let discrete = normal.try_normalize().unwrap_or(fallback);
        *normal = (discrete + correction).try_normalize().unwrap_or(fallback);
    }
    Ok(mesh)
}
