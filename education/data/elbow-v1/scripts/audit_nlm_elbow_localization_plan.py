#!/usr/bin/env python3
"""Offline audit of an unexecuted bounded NLM localization proposal."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'curation/nlm-elbow-localization-plan'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(external_root=None):
    plan = json.loads((EVIDENCE / 'plan.json').read_text())
    receipt = json.loads((EVIDENCE / 'metadata-request-receipt.json').read_text())
    source = Path(receipt['local_body_file'])
    if external_root:
        source = external_root / source.name
    raw = source.read_bytes()
    require(receipt['status'] == 200 and len(raw) == receipt['bytecount'] == 82328 and
            hashlib.sha256(raw).hexdigest() == receipt['sha256'] ==
            '67ffbe889c70cd6ede9c1581ba521f398bbe0aa40b6473f0783eac4b668d90bb',
            'Index differs from acquisition receipt')
    listing = dict(re.findall(r"href='(a_vm[0-9]+[.]png)'[^<]*</a></td>"
                              r"<td class='size'>([0-9]+)</td>", raw.decode()))
    assets = plan['assets']
    require(len(assets) == 11 and {a['id'] for a in assets} ==
            {f'a_vm{i}' for i in range(1595, 1606)}, 'Proposed finite set changed')
    require(all(a['specimen_id'] == 'nlm-visible-human-male' and
                a['series_id'] == 'male-original-color-PNG' for a in assets),
            'Specimen or series substitution')
    for a in assets:
        require(a['source_url'] == urllib.parse.urljoin(receipt['finalURL'], a['id'] + '.png')
                and a['listed_bytes'] == int(listing[a['id'] + '.png']),
                'Candidate is not bound to official listing')
        require(not a['raw_path_current_access_verified'] and a['max_body_bytes'] == 4194304,
                'Unmade raw request or changed per-image cap')
        if a['id'] != 'a_vm1600':
            require(not a['raw_payload_acquired'] and a['raw_sha256'] is None and
                    a['raw_path_http_status'] is None, 'New raw payload fabricated')
    anchor = next(a for a in assets if a['id'] == 'a_vm1600')
    expected_anchor = '570cf80f01c6d9beaefcc4b0670cf8c561e6785321b22f469c4ef4bafda93ac4'
    require(anchor['action'] == 'reuse_pinned_existing' and
            anchor['raw_sha256'] == expected_anchor and anchor['listed_bytes'] == 3450446,
            'Reused anchor changed')
    require(hashlib.sha256(Path(anchor['existing_local_path']).read_bytes()).hexdigest() ==
            expected_anchor, 'Existing raw anchor changed')
    new = sorted((a for a in assets if a['id'] != 'a_vm1600'), key=lambda a:a['fetch_order'])
    require([a['id'] for a in new] == [f'a_vm{i}' for i in
            [1599,1601,1598,1602,1597,1603,1596,1604,1595,1605]], 'Unbounded fetch order')
    budget = plan['budget']
    require(sum(a['listed_bytes'] for a in new) == budget['listed_new_image_bytes'] == 34472328
            and sum(a['listed_bytes'] for a in assets) ==
            budget['listed_series_bytes_including_reuse'] == 37922774,
            'Listed transfer arithmetic differs')
    require(budget['new_image_count'] == 10 and budget['reuse_count'] == 1 and
            budget['raw_transfer_cap_bytes'] == 41943040 and
            budget['free_space_floor_bytes'] == 1610612736 and
            budget['automatic_retries'] == 0 and budget['raw_downloads_this_checkpoint'] == 0,
            'Proposed budget or acquisition scope changed')
    contract = (ROOT / 'curation/nlm-arm-feasibility/segmentation-contract.json').read_bytes()
    require(hashlib.sha256(contract).hexdigest() == plan['contract_sha256'],
            'Original contract binding changed')
    geometry = plan['geometry_state']
    require(geometry['anatomical_laterality'] == 'unverified' and
            geometry['patient_affine_mm'] is None and
            not geometry['physical_section_adjacency_verified'] and
            not geometry['other_source_coordinates_applied'], 'Unsupported physical ROI geometry')
    require(plan['plan_status'].startswith('proposal_only') and
            not plan['tissue_masks_created'] and not plan['source_fusion_performed'] and
            not plan['clinical_validation'] and not plan['simulation_ready'] and
            plan['bodyparts43_full_archive_resolution_license_still_unresolved'],
            'Unexecuted proposal promoted to annotation or qualification')
    return {'verified': True, 'metadata_body_bytes': 82328, 'new_raw_images_acquired': 0,
            'proposed_new_images': 10, 'reused_images': 1,
            'listed_new_image_bytes': 34472328, 'proposed_raw_transfer_cap_bytes': 41943040,
            'anatomical_laterality': 'unverified', 'stage': 'proposal_only'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-root', type=Path, help='Moved index receipt body')
    args = parser.parse_args()
    print(json.dumps(audit(args.external_root), sort_keys=True))
