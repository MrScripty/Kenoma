#!/usr/bin/env python3
"""Offline validation of the NLM metadata-only milestone; never imports images/masks."""
import argparse
import hashlib
import json
import pathlib

import audit_source_inventory as inventory

ROOT = inventory.CURATION / 'nlm-arm-feasibility'
SPECIMEN = 'nlm-visible-human-male'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(manifest, contract, state):
    require = inventory.require
    require(manifest['schema_version'] == contract['schema_version'] == state['schema_version'] == 1, 'Unsupported milestone schema')
    require(manifest['specimen_id'] == contract['specimen_id'] == state['specimen_id'] == SPECIMEN, 'Single male specimen contract differs')
    source_path = inventory.REPO / 'education/data/elbow-v1/curation/source-inventory.json'
    require(manifest['inventory_owner'] == contract['inventory_owner'] == str(source_path.relative_to(inventory.REPO)), 'Existing inventory owner differs')
    require(manifest['inventory_file_sha256'] == contract['inventory_file_sha256'] == digest(source_path), 'Existing inventory byte binding differs')
    inventory.build(inventory.load(source_path))
    original = inventory.load(inventory.CURATION / 'requirements-v1.json')['requirements']
    required = {r['id']: r for r in original if r['scope'] != 'ontology_example'}
    labels = contract['labels']
    targets = labels + contract['nonvoxel_targets']
    require(len(targets) == len({t['id'] for t in targets}) == len(required), 'Incomplete or duplicate segmentation target set')
    require({t['id'] for t in targets} == set(required), 'Segmentation target set differs from inventory')
    for target in targets:
        expected = required[target['id']]
        require(target['inventory_requirement_id'] == target['id'], 'Target was remapped to another requirement')
        require(all(target[k] == expected[k] for k in ['name', 'tissue']), 'Target label/tissue identity differs')
        expected_type = 'surface_footprint_or_landmark' if target['tissue'] == 'attachment' else 'vector_field' if target['tissue'] == 'field' else 'uint16_voxel_label'
        require(target['representation'] == expected_type, 'Measured field/attachment cannot become a tissue voxel class')
    reserved = {'unknown_unassessed': 0, 'reviewed_background': 1, 'artifact_exclusion': 65534, 'ambiguous_tissue': 65535}
    require(contract['reserved_values'] == reserved, 'Unknown/background/artifact/ambiguity must remain distinct')
    values = [label['value'] for label in labels]
    require(len(values) == len(set(values)) and all(type(v) is int and 2 <= v < 65534 for v in values), 'Invalid or overlapping label values')
    require(state['contract_sha256'] == digest(ROOT / 'segmentation-contract.json'), 'Annotation contract binding differs')
    require(state['stage'] == 'metadata_only', 'Image/label import is not demonstrated by this checkpoint')
    require(state['input_assets'] == [] and state['source_images_imported'] is False and state['tissue_masks_imported'] is False, 'Unavailable source rasters/masks cannot be declared imported')
    require(state['voxel_label_artifact'] is None and state['uncertainty_artifact'] is None, 'Metadata-only state cannot contain invented masks')
    require(all(v is None for v in state['image_geometry'].values()), 'Cryosection geometry is not established by CT header or nominal sampling')
    region = state['region']
    require(region['status'] == 'not_localized' and region['laterality'] == 'unverified' and region['bounds_columns_rows_slices'] is None and region['source_asset_ids'] == [] and region['localization_evidence'] is None, 'Arm ROI cannot be localized without source pixels/orientation')
    annotations = state['annotations']
    require(len(annotations) == len(required) and {a['inventory_requirement_id'] for a in annotations} == set(required), 'Missing or duplicate annotation status')
    for annotation in annotations:
        require(annotation['status'] == 'not_assessed' and annotation['evidence_kind'] == 'none', 'Unseen boundary or atlas prior cannot become observed anatomy')
        require(annotation['source_asset_ids'] == [] and annotation['annotation_artifact'] is None and annotation['interpolation_status'] == 'none', 'Metadata-only annotation cannot imply source-pixel support')
        require(all(annotation[k] is None for k in ['annotator', 'reviewer', 'boundary_evidence', 'uncertainty']), 'Do not invent annotation review or uncertainty evidence')
    require(state['clinical_validation'] is False and state['simulation_ready'] is False, 'Curation cannot certify clinical/simulation readiness')
    require(manifest['acquired_source_bytes'] == 0 and manifest['source_images_imported'] is False and manifest['tissue_masks_imported'] is False and manifest['localized_region'] is None, 'Milestone exceeds observed access evidence')
    terms = manifest['terms']
    require(terms['required_attribution'] == 'Courtesy of the U.S. National Library of Medicine', 'Required NLM attribution differs')
    require(terms['terms_url'] == 'https://www.nlm.nih.gov/databases/download/terms_and_conditions.html' and terms['checkpoint_notice'], 'NLM terms/version notice missing')
    candidates = manifest['scout_candidates']
    require(len(candidates) == 3 and len({c['id'] for c in candidates}) == 3, 'Bounded scout set differs')
    for candidate in candidates:
        require(candidate['specimen_id'] == SPECIMEN and candidate['url'].startswith('https://data.lhncbc.nlm.nih.gov/public/Visible-Human/Male-Images/PNG_format/'), 'Candidate source/specimen changed')
        require(candidate['raw_sha256'] is None and candidate['source_byte_status'] == 'not_acquired', 'Unacquired candidate has an invented content pin')
    plan = manifest['bounded_next_acquisition']
    total = sum(c['listed_bytes'] for c in candidates)
    require(plan['total_scout_bytes'] == total <= plan['transfer_budget_bytes'] <= 12 * 1024**2 and all(0 < c['listed_bytes'] <= plan['per_image_limit_bytes'] <= 4 * 1024**2 for c in candidates), 'Scout budget exceeded')
    require(plan['full_volume_download'] is False and plan['scout_count'] == 3, 'Full volume acquisition is out of scope')
    header = manifest['header_observation']
    require(header['raw_sha256'] is None and header['cryosection_affine'] is None and header['pixel_center_convention'] is None, 'Transcribed CT metadata cannot supply raw identity or cryosection geometry')
    # The corner span covers 512 nominal samples, not a demonstrated 511
    # center-to-center interval. Preserve the convention ambiguity.
    span = abs(header['first']['top_right_RAS_mm'][0] - header['first']['top_left_RAS_mm'][0])
    require(span == header['matrix'][0] * header['pixel_size_mm'][0], 'Header nominal span/sampling transcription differs')
    return {'verified': True, 'specimen_id': SPECIMEN, 'stage': 'metadata_only',
            'voxel_label_classes': len(labels), 'nonvoxel_targets': len(contract['nonvoxel_targets']),
            'unassessed_targets': len(annotations), 'planned_scout_bytes': total,
            'source_images_imported': False, 'tissue_masks_imported': False,
            'localized_region': None, 'clinical_validation': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result = verify(inventory.load(ROOT / 'feasibility.json'),
                    inventory.load(ROOT / 'segmentation-contract.json'),
                    inventory.load(ROOT / 'annotation-state.json'))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
