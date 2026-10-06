#!/usr/bin/env python3
"""Offline original-surface diagnostics. Never write or repair source geometry.

Exact-coordinate topology and orientation follow build-anatomical-geometry.mjs.
Transverse crossings port anatomical-bone-collision-audit.mjs, with its limits.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import pathlib

import numpy as np

import audit_source_inventory as inventory

REPO = inventory.REPO
OUT = inventory.CURATION / 'surface-quality'


def pin(path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(REPO)), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def topology(vertices, faces):
    """Diagnostics on unchanged indices; no smoothing or tolerance merge."""
    vertices = np.asarray(vertices, dtype=float)
    faces = [list(t) for t in faces]
    inventory.require(vertices.ndim == 2 and vertices.shape[1] == 3 and
                      np.isfinite(vertices).all(), 'Invalid vertices')
    inventory.require(all(len(t) == 3 and all(type(i) is int and 0 <= i < len(vertices)
                      for i in t) for t in faces), 'Invalid triangle indices')
    edges = defaultdict(list)
    incident = defaultdict(set)
    for f, t in enumerate(faces):
        for i, a in enumerate(t):
            b = t[(i + 1) % 3]
            edges[tuple(sorted((a, b)))].append((f, a < b))
            incident[a].add(f)
    adjacent = [set() for _ in faces]
    orientation_adjacent = [[] for _ in faces]
    for uses in edges.values():
        for f, _ in uses:
            adjacent[f].update(g for g, _ in uses if g != f)
        if len(uses) == 2:
            (f, a), (g, b) = uses
            orientation_adjacent[f].append((g, a == b))
            orientation_adjacent[g].append((f, a == b))
    components = []
    remaining = set(range(len(faces)))
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        queue = [start]
        for f in queue:
            for g in sorted(adjacent[f]):
                if g in remaining:
                    remaining.remove(g)
                    queue.append(g)
        components.append(sorted(queue))
    nonmanifold_vertices = []
    for v, fan in incident.items():
        # Face fan connectivity around this vertex, not whole surface adjacency.
        links = defaultdict(set)
        for f in fan:
            for b in faces[f]:
                if b != v:
                    uses = edges[tuple(sorted((v, b)))]
                    links[f].update(g for g, _ in uses if g in fan and g != f)
        unseen = set(fan)
        fans = 0
        while unseen:
            fans += 1
            stack = [unseen.pop()]
            while stack:
                for g in links[stack.pop()]:
                    if g in unseen:
                        unseen.remove(g)
                        stack.append(g)
        if fans > 1:
            nonmanifold_vertices.append(v)
    triangle_points = vertices[np.asarray(faces, dtype=int)]
    areas = np.linalg.norm(np.cross(triangle_points[:, 1] - triangle_points[:, 0],
                                   triangle_points[:, 2] - triangle_points[:, 0]), axis=1) / 2
    duplicate = Counter(tuple(sorted(t)) for t in faces)
    results = []
    for component in components:
        selected = set(component)
        c_edges = {e: uses for e, uses in edges.items() if any(f in selected for f, _ in uses)}
        c_vertices = sorted({v for f in component for v in faces[f]})
        closed = all(len(uses) == 2 for uses in c_edges.values())
        flip = {}
        contradictions = set()
        for start in component:
            if start in flip:
                continue
            flip[start] = False
            queue = [start]
            for f in queue:
                for g, change in orientation_adjacent[f]:
                    expected = flip[f] != change
                    if g not in flip:
                        flip[g] = expected
                        queue.append(g)
                    elif flip[g] != expected:
                        contradictions.add(tuple(sorted((f, g))))
        original_volume = float(sum(np.dot(vertices[faces[f][0]], np.cross(
            vertices[faces[f][1]], vertices[faces[f][2]])) / 6 for f in component))
        consistent_volume = float(sum((-1 if flip[f] else 1) * np.dot(
            vertices[faces[f][0]], np.cross(vertices[faces[f][1]], vertices[faces[f][2]])) / 6
            for f in component))
        if consistent_volume < 0:
            flip = {f: not value for f, value in flip.items()}
        manifold = not set(c_vertices).intersection(nonmanifold_vertices) and closed
        valid_volume = manifold and not contradictions and not any(areas[f] == 0 for f in component)
        # Translation-stable volume exposes planar two-face shells hidden by
        # cancellation around the atlas world origin. Owner winding diagnostics
        # above deliberately retain the owner's original convention.
        origin = vertices[c_vertices[0]]
        relative_volume = float(sum((-1 if flip[f] else 1) * np.dot(
            vertices[faces[f][0]] - origin, np.cross(vertices[faces[f][1]] - origin,
                                                     vertices[faces[f][2]] - origin)) / 6
            for f in component))
        coincident = defaultdict(list)
        for f in component:
            coincident[tuple(sorted(faces[f]))].append(f)
        duplicate_groups = [ids for ids in coincident.values() if len(ids) > 1]
        chi = len(c_vertices) - len(c_edges) + len(component)
        results.append({
            'first_source_face_zero_based': component[0], 'face_count': len(component),
            'source_faces_if_small_component_zero_based': component if len(component) <= 16 else None,
            'vertex_count': len(c_vertices), 'edge_count': len(c_edges),
            'bounds_m': [vertices[c_vertices].min(axis=0).tolist(), vertices[c_vertices].max(axis=0).tolist()],
            'area_m2': float(sum(areas[component])), 'euler_characteristic': chi,
            'closed_vertex_manifold': manifold, 'orientation_contradictions': len(contradictions),
            'genus_if_closed_orientable_manifold': (2 - chi) / 2 if manifold and not contradictions else None,
            'original_signed_volume_m3': original_volume,
            'component_relative_signed_volume_diagnostic_m3': relative_volume if valid_volume else None,
            'exact_zero_component_relative_volume': relative_volume == 0 if valid_volume else None,
            'coincident_triangle_source_face_groups': duplicate_groups,
            'consistent_positive_signed_volume_diagnostic_m3': abs(consistent_volume) if valid_volume else None,
            'faces_requiring_orientation_change': sum(flip.values()) if valid_volume else None,
            'positive_volume_winding_sign_meaningful': valid_volume and relative_volume != 0,
            'orientation_change_source_face_indices_zero_based': sorted(f for f, value in flip.items() if value) if valid_volume else None,
            'volume_caveat': 'Signed enclosed-volume diagnostic only; self-intersection and nesting not cleared.'})
    lengths = [float(np.linalg.norm(vertices[a] - vertices[b])) for a, b in edges]
    return {'vertex_count': len(vertices), 'face_count': len(faces), 'edge_count': len(edges),
            'unused_vertex_count': len(vertices) - len(incident),
            'boundary_edges': sum(len(v) == 1 for v in edges.values()),
            'nonmanifold_edges': sum(len(v) > 2 for v in edges.values()),
            'nonmanifold_vertex_count': len(nonmanifold_vertices),
            'same_direction_two_face_edges': sum(len(v) == 2 and v[0][1] == v[1][1] for v in edges.values()),
            'exact_zero_area_triangles': int(sum(areas == 0)),
            'duplicate_triangle_excess': sum(n - 1 for n in duplicate.values()),
            'area_m2': float(sum(areas)), 'triangle_area_range_m2': [float(min(areas)), float(max(areas))],
            'edge_length_range_m': [min(lengths), max(lengths)],
            'face_connected_components': results,
            'closed_edge_manifold': all(len(v) == 2 for v in edges.values())}


def exact_weld(vertices, faces):
    keys = {}
    unique = []
    mapping = []
    for vertex in vertices:
        key = tuple(vertex)
        if key not in keys:
            keys[key] = len(unique)
            unique.append(vertex)
        mapping.append(keys[key])
    return unique, [[mapping[i] for i in t] for t in faces], mapping


def crossing(a, b, triangles):
    """Vectorized existing strict segment/interior predicate in SI metres.

    Constants copied from anatomical-bone-collision-audit.mjs. This intentionally
    excludes coplanarity, grazing, segment endpoints and triangle edges.
    """
    d = b - a
    e1, e2 = triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
    h = np.cross(d, e2)
    den = np.einsum('ij,ij->i', e1, h)
    allowed = np.abs(den) >= 1e-15
    safe_den = np.where(allowed, den, 1)
    s = a - triangles[:, 0]
    cross_s = np.cross(s, e1)
    u = np.einsum('ij,ij->i', s, h) / safe_den
    v = np.sum(d * cross_s, axis=1) / safe_den
    l = np.einsum('ij,ij->i', e2, cross_s) / safe_den
    return allowed & (u > 1e-8) & (v > 1e-8) & (u + v < 1 - 1e-8) & (l > 1e-8) & (l < 1 - 1e-8)


def transverse_pairs(vertices_a, faces_a, vertices_b=None, faces_b=None):
    self_test = vertices_b is None
    va, fa = np.asarray(vertices_a, dtype=float), np.asarray(faces_a, dtype=int)
    vb, fb = (va, fa) if self_test else (np.asarray(vertices_b, dtype=float), np.asarray(faces_b, dtype=int))
    a, b = va[fa], vb[fb]
    blo, bhi = b.min(axis=1), b.max(axis=1)
    count = candidates = skipped = 0
    examples = []
    for i, tri in enumerate(a):
        mask = np.all(blo <= tri.max(axis=0), axis=1) & np.all(bhi >= tri.min(axis=0), axis=1)
        if self_test:
            mask[:i + 1] = False
            incident = np.any(np.isin(fb, fa[i]), axis=1)
            skipped += int(sum(mask & incident))
            mask &= ~incident
        indices = np.flatnonzero(mask)
        candidates += len(indices)
        if not len(indices):
            continue
        targets = b[indices]
        found = np.zeros(len(indices), dtype=bool)
        for k in range(3):
            found |= crossing(tri[k], tri[(k + 1) % 3], targets)
            # Reverse-direction segments against the first triangle, batched.
            found |= crossing(targets[:, k], targets[:, (k + 1) % 3], np.broadcast_to(tri, targets.shape))
        hits = indices[found].tolist()
        count += len(hits)
        examples.extend([[i, j] for j in hits][:max(0, 12 - len(examples))])
    return {'aabb_candidate_pairs_tested': candidates, 'incident_candidate_pairs_excluded': skipped,
            'transverse_crossing_triangle_pairs': count, 'first_source_face_pairs_zero_based': examples,
            'full_self_intersection_clearance': 'not_assessed',
            'limits': 'Strict transverse crossings only, fixed SI thresholds. Coplanar overlaps, touching, nesting and incident-face foldovers excluded. Zero is not a clearance.'}


def validate_landmarks(document, parts):
    rows = []
    for name, pick in document['landmarks'].items():
        part = parts[pick['element_id']]
        face = part['triangles_zero_based'][pick['triangle_zero_based']]
        inventory.require(face == pick['vertex_indices_zero_based'], 'Landmark source indices differ')
        weights = pick['barycentric']
        inventory.require(len(weights) == 3 and all(0 <= w <= 1 for w in weights)
                          and abs(sum(weights) - 1) < 1e-12, 'Invalid barycentric landmark')
        point = [sum(weights[j] * part['vertices_m'][v][d] for j, v in enumerate(face)) for d in range(3)]
        error = math.dist(point, pick['atlas_position_m'])
        inventory.require(error < 1e-12, 'Landmark coordinate differs from source interpolation')
        rows.append({'id': name, 'element_id': pick['element_id'], 'triangle_zero_based': pick['triangle_zero_based'],
                     'position_m': point, 'source_coordinate_reconstruction_error_m': error,
                     'evidence_class': pick['evidence_class'], 'review_status': pick['review_status'],
                     'authored_uncertainty_radius_m': pick['uncertainty_radius_m'],
                     'uncertainty_is_measured': False})
    return rows


def build():
    contract = inventory.load(OUT / 'input-contract.json')
    for item in contract['pins']:
        inventory.verify_pin(REPO, item)
    manifest = inventory.load(inventory.CURATION / 'source-inventory.json')
    coverage = inventory.build(manifest)
    atlas = inventory.load(REPO / manifest['owners']['source_coordinates'])
    parts = {p['element_id']: p for p in atlas['parts']}
    existing = inventory.load(REPO / 'education/data/anatomical-arm-v1/audit/geometry-quality.json')
    previous = {b['element_id']: b for b in existing['bones']}
    previous.update({m['element_id']: m for m in existing['muscles']})
    rows = []
    for part in atlas['parts']:
        print('Auditing', part['element_id'], flush=True)
        vertices, faces = part['vertices_m'], part['triangles_zero_based']
        unique, welded, mapping = exact_weld(vertices, faces)
        raw, diagnostic = topology(vertices, faces), topology(unique, welded)
        raw_components = raw.pop('face_connected_components')
        raw['face_connected_component_count'] = len(raw_components)
        raw['face_connected_component_sizes'] = [c['face_count'] for c in raw_components]
        components = diagnostic['face_connected_components']
        cross = transverse_pairs(unique, welded)
        old = previous[part['element_id']]
        old_quality = old if 'closed_components' in old else old['quality']
        expected_count = old_quality.get('closed_components', old_quality.get('whole_source_closed_components'))
        expected_flips = old_quality.get('flipped_faces', old_quality.get('source_faces_reoriented'))
        flips = sum(c['faces_requiring_orientation_change'] or 0 for c in components)
        volume = sum(c['consistent_positive_signed_volume_diagnostic_m3'] or 0 for c in components)
        inventory.require(len(components) == expected_count and flips == expected_flips,
                          'Exact-weld/orientation disagrees with existing geometry owner')
        inventory.require(abs(volume - old.get('volume_m3', old.get('source_volume_m3'))) < 1e-12,
                          'Source signed volume disagrees with existing geometry owner')
        bad = cross['transverse_crossing_triangle_pairs'] > 0
        rows.append({'element_id': part['element_id'], 'concept_id': part['concept_id'], 'name': part['name'],
                     'source_obj': str((inventory.ROOT / part['source_obj']).relative_to(REPO)),
                     'source_sha256': part['source_sha256'], 'bounds_m': part['bounds_m'],
                     'extent_m': [b - a for a, b in zip(*part['bounds_m'])],
                     'original_index_topology': raw, 'exact_coordinate_topology_diagnostic': diagnostic,
                     'exact_coordinate_duplicate_vertex_count': len(vertices) - len(unique),
                     'diagnostic_merge_tolerance_m': 0, 'geometry_written_or_repaired': False,
                     'watertightness': {'original_indices_closed': raw['closed_edge_manifold'],
                                        'exact_coordinate_closed_edges': diagnostic['closed_edge_manifold'],
                                        'embedded_solid_certificate': False,
                                        'limits': 'Topological closure only. Coincident/zero-volume components and transverse crossings are reported separately; robust embedding/nesting clearance remains unresolved.'},
                     'self_intersection': cross,
                     'existing_geometry_owner_agreement': True,
                     'visual_reference': 'available_reduced_reconstructed_atlas',
                     'volumetric_simulation_input_ready': False,
                     'required_work': ['Document an explicit derived index weld at exactly identical coordinates; original OBJ remains unchanged.']
                     + (['Review disconnected components individually; establish anatomical identity before retaining, removing or joining any fragment.'] if len(components) > 1 else [])
                     + (['Review reported source-face winding changes in a separately versioned derivative.'] if flips else [])
                     + (['Resolve coincident triangles and zero-volume shell components through source review; edge closure alone is insufficient. Preserve every source face until a documented derivative decision.'] if any(c['exact_zero_component_relative_volume'] or c['coincident_triangle_source_face_groups'] for c in components) else [])
                     + (['Investigate positive transverse crossings at reported source faces; no automated anatomical repair.'] if bad else [])
                     + ['Resolve complete self-intersection/nesting/assembly clearance with a qualified method.',
                        'Review reduced reconstructed boundaries and missing tissue interfaces; surface closure does not establish anatomical accuracy.',
                        'Specify cortical/internal or muscle/tendon compartments, material fields, reference state and attachments before any volume meshing.']})
    landmarks = inventory.load(REPO / 'education/data/anatomical-arm-v1/config/landmarks.json')
    inventory.require(landmarks['source_sha256'] == hashlib.sha256((REPO / manifest['owners']['source_coordinates']).read_bytes()).hexdigest(), 'Landmark source binding differs')
    landmark_rows = validate_landmarks(landmarks, parts)
    attachment_doc = inventory.load(REPO / manifest['owners']['current_attachments'])
    patches = []
    for name, patch in attachment_doc['patches'].items():
        part = parts[patch['element_id']]
        faces = [part['triangles_zero_based'][i] for i in patch['triangle_indices_zero_based']]
        diagnostic = topology(part['vertices_m'], faces)
        unique, welded, _ = exact_weld(part['vertices_m'], faces)
        patch_welded = topology(unique, welded)
        inventory.require(abs(diagnostic['area_m2'] - patch['area_m2']) < 1e-12, 'Patch area differs from source')
        for sample in patch['anchor_samples']:
            face = part['triangles_zero_based'][sample['triangle_zero_based']]
            # These owner samples retain raw source indices. Do not substitute
            # exact-welded render indices or reorder nonuniform barycentrics.
            inventory.require(face == sample['vertex_indices_zero_based'], 'Attachment sample indices differ from original source')
            inventory.require(abs(sum(sample['barycentric']) - 1) < 1e-12 and all(0 <= w <= 1 for w in sample['barycentric']), 'Invalid attachment sample barycentrics')
            point = [sum(sample['barycentric'][j] * part['vertices_m'][v][d] for j, v in enumerate(face)) for d in range(3)]
            inventory.require(math.dist(point, sample['position_m']) < 1e-12, 'Attachment sample source interpolation differs')
        patches.append({'id': name, 'element_id': patch['element_id'],
                        'source_face_count': len(faces), 'area_m2': diagnostic['area_m2'],
                        'original_index_face_connected_components': len(diagnostic['face_connected_components']),
                        'exact_coordinate_face_connected_components': len(patch_welded['face_connected_components']),
                        'sample_count': len(patch['anchor_samples']), 'source_sample_coordinates_verified': True,
                        'evidence_class': patch['evidence_class'], 'review_status': patch['review_status'],
                        'measured_enthesis': False, 'limits': patch['limits']})
    # Static source-coordinate diagnostic only: no candidate rig or fitted frame applied.
    bone_pairs = []
    bone_ids = {r['expected_elements'][0] for r in manifest['requirements']
                if r['scope'] == 'existing_poc' and r['tissue'] == 'bone'}
    bones = [part for part in atlas['parts'] if part['element_id'] in bone_ids]
    inventory.require(len(bones) == 3, 'Expected the existing three evidenced bones')
    for i, a in enumerate(bones):
        for b in bones[i + 1:]:
            bone_pairs.append({'elements': [a['element_id'], b['element_id']],
                               'transverse': transverse_pairs(a['vertices_m'], a['triangles_zero_based'], b['vertices_m'], b['triangles_zero_based'])})
    return {'schema_version': 1, 'source_inventory_sha256': pin(inventory.CURATION / 'source-inventory.json')['sha256'],
            'input_contract_sha256': pin(OUT / 'input-contract.json')['sha256'],
            'coordinates': manifest['sources'][0]['coordinates'], 'provenance': manifest['sources'][0]['provenance'],
            'reference_pose': {'applied_transform': 'Uniform mm to m scaling only; no translation, rotation, centering or fitted joint pose.',
                               'calibrated_joint_angles': None, 'existing_fitted_frame': existing['frame'],
                               'frame_applied_in_this_audit': False,
                               'frame_is_observed_specimen_pose': False},
            'parts': rows, 'bone_pair_intersections_in_original_atlas_pose': bone_pairs,
            'landmarks': landmark_rows, 'attachment_patches': patches,
            'muscle_attachment_coverage': coverage['attachments'],
            'missing_tissues': [r['id'] for r in coverage['requirements'] if r['scope'] != 'ontology_example' and not r['individual_tissue_mesh_established']],
            'full_self_intersection_clearance': 'not_assessed', 'simulation_ready': False, 'clinical_validation': False,
            'all_tissue_interface_and_assembly_clearance': 'not_assessed',
            'raw_surfaces_modified': False,
            'intersection_predicate': {'owner': 'education/tools/anatomical-bone-collision-audit.mjs',
                                       'implementation': 'Read-only NumPy port of strict crossing, original atlas pose; self-pairs exclude incident faces.',
                                       'determinant_threshold_m3': 1e-15, 'strict_barycentric_and_segment_margin': 1e-8,
                                       'full_robust_self_intersection_tool_qualified': False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write only curation/surface-quality/quality.json')
    args = parser.parse_args()
    result = build()
    if args.write:
        (OUT / 'quality.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    else:
        inventory.require(result == inventory.load(OUT / 'quality.json'), 'Quality evidence differs; investigate inputs before regeneration')
    print(json.dumps({'surfaces': len(result['parts']), 'raw_surfaces_modified': False,
                      'simulation_ready': False, 'full_self_intersection_clearance': 'not_assessed'}))


if __name__ == '__main__':
    main()
