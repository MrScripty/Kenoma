export type Vec3 = [number, number, number];
export type Vec2 = [number, number];
export interface SkinNode { position: Vec3; radii: Vec2; root: boolean }
export interface SkinGraph { nodes: SkinNode[]; edges: {a: number; b: number}[] }
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
  | {type: 'edit'; graph: SkinGraph; commands: Command[]; options?: Options}
};
export type ErrorCode = 'invalid_request' | 'unsupported_version' | 'resource_limit'
  | 'invalid_node' | 'invalid_edge' | 'self_edge' | 'duplicate_edge' | 'invalid_value'
  | 'invalid_options' | 'invalid_transform' | 'ambiguous_branch' | 'invalid_geometry'
  | 'history_conflict' | 'serialization';
export type Response = {version: 1; ok: true; graph: SkinGraph; options: Options; mesh: Mesh}
  | {version: 1; ok: false; error: {code: ErrorCode; message: string}};
export interface SimpleGraph {request(value: Request): Response}
/** Initialization may reject on a fetch/compilation error; requests return envelopes. */
export function createSimpleGraph(options?: {wasmUrl?: string | URL}): Promise<SimpleGraph>;
