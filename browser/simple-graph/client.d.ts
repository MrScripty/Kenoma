export type Vec3 = [number, number, number];
export type Vec2 = [number, number];
export interface SkinNode { position: Vec3; radii: Vec2; root: boolean }
export interface SkinGraph { nodes: SkinNode[]; edges: {a: number; b: number}[] }
export interface HeadPose { yaw: number; pitch: number }
export interface SurfaceOptions { cell_size: number }
export interface Options { ring_sides: number; target_segment_length_factor: number; max_edge_segments: number }
export type Command =
  | {AddNode: {position: Vec3; radii: Vec2}}
  | {MoveNode: {node: number; position: Vec3}}
  | {ExtrudeNode: {node: number; offset: Vec3}}
  | {Connect: {a: number; b: number}}
  | {SetRadius: {node: number; radii: Vec2}}
  | {DeleteNode: {node: number}}
  | {DeleteEdge: {edge: number}}
  | {MarkRoot: {node: number}}
  | {RotateBranch: {pivot: number; child: number; axis: Vec3; radians: number}};
export type Diagnostic = 'EmptyGraph'
  | {ZeroLengthEdge: {edge: number}}
  | {RadiusClamped: {node: number}}
  | {IslandRootGenerated: {island: number; node: number}}
  | {MultipleRootsInIsland: {island: number; roots: number[]}}
  | {LoopFrameApproximated: {edge: number}}
  | {BranchFallbackOverlap: {node: number}};
export interface Mesh {
  positions: Vec3[]; normals: Vec3[]; indices: number[];
  source_nodes: (number | null)[]; source_edges: (number | null)[];
  diagnostics: Diagnostic[];
}
export type Request = {version: 1; operation:
  | {type: 'mannequin'}
  | {type: 'generate'; graph: SkinGraph; options?: Options}
  | {type: 'surface'; graph: SkinGraph; head?: HeadPose; surface_options?: SurfaceOptions}
  | {type: 'edit'; graph: SkinGraph; commands: Command[]; options?: Options}
};
export type ErrorCode = 'invalid_request' | 'unsupported_version' | 'resource_limit'
  | 'invalid_node' | 'invalid_edge' | 'self_edge' | 'duplicate_edge' | 'invalid_value'
  | 'invalid_options' | 'invalid_transform' | 'ambiguous_branch' | 'invalid_geometry'
  | 'history_conflict' | 'serialization' | 'invalid_surface';
export type Response = {version: 1; ok: true; graph: SkinGraph; options: Options; mesh: Mesh; head?: HeadPose; surface_options?: SurfaceOptions}
  | {version: 1; ok: false; error: {code: ErrorCode; message: string}};
export interface SimpleGraph {request(value: Request): Response}
/** Initialization may reject on a fetch/compilation error; requests return envelopes. */
export function createSimpleGraph(options?: {wasmUrl?: string | URL}): Promise<SimpleGraph>;

/** Additive rig-v1 API. Handles belong to a single initialized WASM instance.
 * Bind once in neutral pose; deformation preserves rest indices and vertex IDs.
 * Release unused handles. The legacy Request/Response contracts are unchanged.
 */
export type RigBindRequest = {version: 1; operation: {type: 'rig_bind'; rig_version: 1; surface_options?: SurfaceOptions}};
export type RigDeformRequest = {version: 1; operation: {type: 'rig_deform'; rig_version: 1; rig_id: number; graph: SkinGraph; head?: HeadPose}};
export type RigReleaseRequest = {version: 1; operation: {type: 'rig_release'; rig_version: 1; rig_id: number}};
export type RigFailure = {version: 1; ok: false; error: {code: ErrorCode | 'invalid_rig' | 'unknown_rig' | 'unsupported_rig_version'; message: string}};
export type RigMeshResponse = {version: 1; ok: true; rig_version: 1; rig_id: number; graph: SkinGraph; head: HeadPose; options: Options; mesh: Mesh} | RigFailure;
export type RigReleaseResponse = {version: 1; ok: true; rig_version: 1; rig_id: number; released: true} | RigFailure;
export interface SimpleGraph {
  request(value: RigBindRequest | RigDeformRequest): RigMeshResponse;
  request(value: RigReleaseRequest): RigReleaseResponse;
}
