#!/usr/bin/env python3
"""Offline, read-only source coverage audit; --write updates only curation/coverage.json."""
import argparse
import csv
import hashlib
import io
import json
import math
import pathlib
import re
import struct
import zipfile
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
CURATION = ROOT / 'curation'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text())


def resolve_input(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), 'Input path escapes repository')
    return path


def verify_pin(root, pin):
    path = resolve_input(root, pin['path'])
    require(path.stat().st_size == pin['bytes'], f"Size mismatch: {pin['path']}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    require(digest == pin['sha256'], f"SHA-256 mismatch: {pin['path']}")
    return path


def read_mapping(path):
    by_id = defaultdict(set)
    names = {}
    reverse = defaultdict(set)
    with path.open() as source:
        rows = list(csv.DictReader(source, delimiter='\t'))
    require(rows and set(rows[0]) == {'concept id', 'name', 'element file id'}, 'Unexpected mapping schema')
    for row in rows:
        concept, element = row['concept id'], row['element file id']
        require(re.fullmatch(r'FMA[0-9]+', concept) and re.fullmatch(r'FJ[0-9]+M?', element), 'Invalid mapping identifiers')
        require(concept not in names or names[concept] == row['name'], 'Inconsistent concept name')
        names[concept] = row['name']
        by_id[concept].add(element)
        reverse[element].add(concept)
    return by_id, names, reverse, len(rows)


def inspect_obj(path, expected_concept, expected_element):
    vertices, faces = [], []
    text = path.read_text()
    require(f'# Concept ID : {expected_concept}\n' in text, 'OBJ leaf concept differs from manifest')
    require(f'# File ID : {expected_element}\n' in text, 'OBJ element differs from manifest')
    require('# Compatibility version : 4.0\n' in text, 'OBJ is not Release 4.0')
    for line in text.splitlines():
        tokens = line.split()
        if not tokens:
            continue
        if tokens[0] == 'v':
            require(len(tokens) == 4, 'Expected three source vertex coordinates')
            vertex = [float(value) for value in tokens[1:]]
            require(all(math.isfinite(value) for value in vertex), 'Non-finite vertex')
            vertices.append(vertex)
        elif tokens[0] == 'f':
            require(len(tokens) == 4, 'Expected triangle; do not silently triangulate')
            faces.append([int(value.split('/')[0]) - 1 for value in tokens[1:]])
    require(vertices and faces, 'Empty source surface')
    require(all(0 <= index < len(vertices) for face in faces for index in face), 'Face index outside source vertices')
    return {
        'vertex_count': len(vertices), 'triangle_count': len(faces),
        'bounds_mm': [[min(v[i] for v in vertices) for i in range(3)],
                      [max(v[i] for v in vertices) for i in range(3)]],
        'obj_leaf_concept_id': expected_concept,
        'observed_tissue_segmentation': False,
        'simulation_ready': False,
        'historical_notice_retained': 'Attribution-Share Alike 2.1 Japan' in text,
    }, vertices, faces


def archive_entries(root):
    base = root / 'education/data/elbow-v1/audit'
    directory = (base / 'bodyparts_zip_central_directory.bin').read_bytes()
    end = (base / 'bodyparts_zip_end_record.bin').read_bytes()
    values = struct.unpack('<4s4H2LH', end)
    sig, disk, cd_disk, n1, n2, size, offset, comment = values
    require(sig == b'PK\x05\x06' and disk == cd_disk == comment == 0 and n1 == n2, 'Unsupported ZIP end record')
    require(len(directory) == size, 'ZIP directory length differs')
    synthetic = struct.pack('<4s4H2LH', sig, 0, 0, n1, n2, size, 0, 0)
    with zipfile.ZipFile(io.BytesIO(directory + synthetic)) as archive:
        entries = [{'filename': e.filename, 'compressed_bytes': e.compress_size,
                    'bytes': e.file_size, 'header_offset': e.header_offset,
                    'crc32': f'{e.CRC:08x}', 'compression': e.compress_type}
                   for e in archive.infolist()]
    require(len(entries) == n1, 'ZIP entry count differs')
    require(entries == load(base / 'bodyparts_archive_entries.json'), 'Archive JSON differs from original directory bytes')
    return {e['filename'].split('/')[-1][:-4]: e for e in entries}, offset + size + len(end)


def build(manifest, root=REPO):
    require(manifest['schema_version'] == 1, 'Unsupported inventory schema')
    require(manifest['clinical_validation'] is False and manifest['simulation_ready'] is False, 'Inventory cannot certify clinical or simulation readiness')
    sources = {source['id']: source for source in manifest['sources']}
    require(len(sources) == len(manifest['sources']), 'Duplicate source ID')
    atlas_source = sources['bodyparts3d-4.0-isa-99']
    require(atlas_source['license']['id'] == 'CC-BY-4.0' and atlas_source['archive']['sha256'] is None, 'Archive license/hash scope differs')
    require(atlas_source['provenance']['evidence_class'] == 'constructed_anatomical_reference_atlas', 'Reconstructed atlas cannot be promoted to observed specimen geometry')
    require(atlas_source['coordinates']['source_unit'] == 'mm' and atlas_source['coordinates']['derived_unit'] == 'm', 'Coordinate unit provenance differs')
    require(atlas_source['provenance']['registered_to_other_people'] is False, 'Cross-specimen registration cannot be inferred')
    require(sources['bodyparts3d-4.3-candidate']['license']['clearance'] == 'unresolved_for_exact_4.3_assets', '4.3 clearance remains unresolved')
    paths = [p['path'] for p in manifest['input_pins']]
    require(len(paths) == len(set(paths)), 'Duplicate input pin')
    for pin in manifest['input_pins']:
        verify_pin(root, pin)
    def owned(relative):
        require(relative in paths, f'Unpinned input: {relative}')
        return resolve_input(root, relative)
    owners = manifest['owners']
    for filename in ['bodyparts_zip_central_directory.bin', 'bodyparts_zip_end_record.bin']:
        owned('education/data/elbow-v1/audit/' + filename)
    owned(owners['archive_directory'])
    by_id, names, reverse, row_count = read_mapping(owned(owners['concept_to_elements']))
    entries, archive_size = archive_entries(root)
    require(archive_size == manifest['sources'][0]['archive']['bytes'], 'Archive total size differs')
    require(set(reverse) == set(entries), 'Mapping and archive element sets differ')
    members = load(owned(owners['source_member_pins']))
    local = {m['element file id']: m for m in members}
    require(len(local) == len(members), 'Duplicate source member')
    atlas = load(owned(owners['source_coordinates']))
    converted = {p['element_id']: p for p in atlas['parts']}
    require(set(converted) == set(local), 'Converted/source part sets differ')
    require(atlas['length_unit'] == 'm' and atlas['coordinate_axes'] == manifest['sources'][0]['coordinates']['axes'], 'Source coordinate contract differs')
    surfaces = {}
    for element, member in sorted(local.items()):
        relative = f'education/data/elbow-v1/sources/bodyparts3d/{element}.obj'
        path = owned(relative)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == member['sha256'], 'OBJ differs from acquisition-time pin')
        require(member['concept id'] in reverse[element], 'Acquisition leaf absent from mapping')
        require(all(member[k] == entries[element][k] for k in entries[element]), 'Member metadata differs from ZIP directory')
        summary, vertices, faces = inspect_obj(path, member['concept id'], element)
        part = converted[element]
        require(part['triangles_zero_based'] == faces, 'Source-to-SI face conversion differs')
        # Reproduce the existing owner's multiplication and its float rounding.
        require(part['vertices_m'] == [[v * 0.001 for v in vertex] for vertex in vertices], 'Source-to-SI coordinate conversion differs')
        surfaces[element] = summary | {'sha256': member['sha256'], 'bytes': member['bytes']}
    requirements = manifest['requirements']
    require(len({r['id'] for r in requirements}) == len(requirements), 'Duplicate requirement')
    contract = load(owned(owners['requirement_contract']))
    require(contract['schema_version'] == 1, 'Unsupported requirements contract')
    identities = {r['id']: {k: r[k] for k in ['name', 'tissue', 'scope', 'concepts']} for r in requirements}
    required = {r['id']: {k: r[k] for k in ['name', 'tissue', 'scope', 'concepts']} for r in contract['requirements']}
    require(len(required) == len(contract['requirements']), 'Duplicate contracted requirement')
    require(identities == required, 'Requirement identity or completion set differs from reviewed contract')
    coverage = []
    allowed = {'individual_surface', 'single_member_representation_uninspected', 'compound_representation', 'related_concept_only', 'no_matching_mesh_in_inspected_mapping', 'regional_segmentation_required'}
    for item in requirements:
        require(item['availability'] in allowed, 'Invalid coverage distinction')
        concepts = item['concepts']
        elements = set()
        for concept in concepts:
            require(names.get(concept['id']) == concept['name'], f"Concept identity differs: {item['id']}")
            elements.update(by_id[concept['id']])
        expected = set(item['expected_elements'])
        require(elements == expected, f"Concept/element relation differs: {item['id']}")
        if item['availability'] == 'individual_surface':
            require(len(elements) == 1 and concepts, 'Individual surface requires exactly one evidenced member')
            element = next(iter(elements))
            require(element in local, 'Uninspected single-member representation is not a confirmed individual surface')
            require(local[element]['concept id'] == concepts[0]['id'], 'Group concept substituted for leaf')
            require(item['name'] == names[concepts[0]['id']], 'Individual surface label differs from leaf identity')
        if item['availability'] == 'single_member_representation_uninspected':
            require(len(elements) == 1 and concepts and not elements.intersection(local), 'Uninspected member classification differs')
        if item['availability'] == 'compound_representation':
            require(len(elements) > 1, 'Compound example requires multiple members')
        if item['availability'] == 'no_matching_mesh_in_inspected_mapping':
            require(not elements and not concepts, 'Unmatched requirement has fabricated concept or geometry')
            aliases = {alias.casefold() for alias in item['query_names']}
            require(not aliases.intersection(name.casefold() for name in names.values()), 'Previously missing name now appears in mapping')
        covered = item['availability'] == 'individual_surface'
        coverage.append({
            'id': item['id'], 'name': item['name'], 'tissue': item['tissue'], 'scope': item['scope'],
            'availability': item['availability'], 'concepts': concepts,
            'individual_tissue_mesh_established': covered,
            'independent_attachment_geometry_established': False,
            'member_candidates': [entries[e] | {'element_id': e,
                'local_status': 'retained_hash_verified' if e in local else 'archive_directory_only_not_acquired',
                'sha256': local[e]['sha256'] if e in local else None,
                'all_mapped_concepts': sorted(reverse[e]),
                'inspection': surfaces.get(e)} for e in sorted(elements)],
            'gap': item['gap'], 'ontology_absence_claim': False,
        })
    attachment_doc = load(owned(owners['current_attachments']))
    source_digest = hashlib.sha256(owned(owners['source_coordinates']).read_bytes()).hexdigest()
    require(attachment_doc['source_sha256'] == source_digest, 'Attachment source binding differs')
    muscles = attachment_doc['muscles']
    require({m['element_id'] for m in muscles} == {r['expected_elements'][0] for r in requirements if r['scope'] == 'existing_poc' and r['tissue'] == 'muscle'}, 'Head coverage differs from existing owner')
    patches = attachment_doc['patches']
    attachment_rows = []
    for muscle in muscles:
        row = {'element_id': muscle['element_id'], 'name': muscle['name'],
               'independent_enthesis_measurement': False, 'separate_tendon_mesh': None}
        for end in ['proximal', 'distal']:
            source = muscle[end]
            result = {'kind': source['kind']}
            if source['kind'] == 'distributed_bone_patch':
                patch = patches[source['patch_id']]
                bone = patch['element_id']
                require(bone in converted, 'Attachment target is not a retained bone')
                indices = patch['triangle_indices_zero_based']
                require(len(indices) == len(set(indices)) and all(type(i) is int and 0 <= i < converted[bone]['triangle_count'] for i in indices), 'Invalid source-face attachment indices')
                require(patch['evidence_class'] == 'atlas_derived_authored_connected_surface_selection', 'Attachment promoted to observed anatomy')
                result.update(patch_id=source['patch_id'], bone_element_id=bone,
                              source_face_count=len(indices), evidence_class=patch['evidence_class'],
                              review_status=patch['review_status'])
            else:
                require(source['kind'] == 'fixed_estimated_origin', 'Unknown attachment kind')
                result.update(evidence_class=source['evidence_class'],
                              uncertainty_radius_m=source['uncertainty_radius_m'],
                              measured_scapular_landmark=False)
            row[end] = result
        attachment_rows.append(row)
    return {'schema_version': 1, 'source_inventory_canonical_sha256': hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'clinical_validation': False, 'simulation_ready': False,
            'cross_specimen_registration': False,
            'inspected_scope': 'Pinned Release 4.0 IS-A mapping, ZIP directory, ten original OBJ files and existing authored attachment manifest; not the complete FMA ontology or PART-OF archive.',
            'counts': {'mapping_rows': row_count, 'mapped_concepts': len(by_id),
                       'unique_archive_members': len(entries), 'retained_arm_members': len(local),
                       'retained_vertex_count': sum(s['vertex_count'] for s in surfaces.values()),
                       'retained_triangle_count': sum(s['triangle_count'] for s in surfaces.values()),
                       'requirements': len(requirements),
                       'coverage_statuses': dict(sorted(Counter(c['availability'] for c in coverage).items()))},
            'requirements': coverage, 'attachments': attachment_rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate only curation/coverage.json from reviewed pins')
    args = parser.parse_args()
    result = build(load(CURATION / 'source-inventory.json'))
    target = CURATION / 'coverage.json'
    if args.write:
        target.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    else:
        require(load(target) == result, 'Coverage is stale; review input changes before --write')
    print(json.dumps({'verified': True, **result['counts']}, sort_keys=True))


if __name__ == '__main__':
    main()
