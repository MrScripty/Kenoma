#!/usr/bin/env python3
"""Offline audit of the bounded BodyParts3D follow-up; no network requests."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'curation/bodyparts43-resolution'


class Catalog(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.links, self.row, self.cell = [], [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = []
        if tag == 'a' and dict(attrs).get('href'):
            self.links.append(dict(attrs)['href'])

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data.strip())

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.row is not None:
            self.row.append(' '.join(s for s in self.cell or [] if s))
            self.cell = None
        if tag == 'tr' and self.row is not None:
            if self.row and self.row[0].isdigit():
                self.rows.append(self.row)
            self.row = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def audit(external_root=None):
    receipt = load('request-receipts.json')
    records = {r['id']: r for r in receipt['records']}
    require(len(records) == 9, 'Unexpected follow-up request set')
    require(sum(r['bytecount'] for r in records.values()) ==
            receipt['actual_followup_body_bytes'] == 4802368, 'Transfer total mismatch')
    bodies = {}
    for name, r in records.items():
        require(not r['network_settings_changed'], 'Transport settings changed')
        require(r['bytecount'] <= r['limit_bytes'] <= 8388608, 'Response cap exceeded')
        for key in ('requestURL', 'finalURL'):
            require(urllib.parse.urlparse(r[key]).hostname == 'lifesciencedb.jp',
                    'Unexpected host or NLM acquisition')
        path = Path(r['local_body_file'])
        if external_root:
            path = external_root / path.name
        bodies[name] = path.read_bytes()
        require(len(bodies[name]) == r['bytecount'] and
                hashlib.sha256(bodies[name]).hexdigest() == r['sha256'],
                'Body differs from receipt: ' + name)
    table = records['bp3d-43-object-table']
    require((table['status'], table['bytecount'], table['sha256']) ==
            (200, 4528437, 'cab10eda6338a6935d0216810eaba78dd049877df496323a0a4916d290dd8e3a'),
            'Catalog initial pin changed')
    catalog = Catalog()
    catalog.feed(bodies['bp3d-43-object-table'].decode())
    require(len(catalog.rows) == 13312 and not catalog.links, 'Catalog count/link claim differs')
    require(all(len(r) == 8 for r in catalog.rows), 'Catalog columns differ')
    summary = load('object-catalog-summary.json')
    require(len({r[1] for r in catalog.rows}) == summary['distinct_uploaded_object_ids'] == 13312,
            'Uploaded catalog count promoted or altered')
    require(len({r[1] for r in catalog.rows if r[2]}) ==
            summary['rows_with_representation_id'] == 3215, 'Representation row count changed')
    rows = {r[1]: r for r in catalog.rows}
    require(rows['FJ3368'][2:5] == rows['FJ6462'][2:5] ==
            ['BP23164', 'FMA23130', 'Right humerus'], 'Official identity differs')
    for r in summary['selected_arm_rows']:
        require(list(r.values()) == rows[r['object_id']], 'Selected catalog transcription differs')

    comparison = load('representative-arm-comparison.json')
    selection = json.loads(bodies['bp3d-humerus-pallet-selection'])
    require(selection['success'] and set(selection['art_ids']) == {'FJ3368', 'FJ6462'},
            'Selected export scope differs')
    require(comparison['documented_export']['selection_response'] == selection,
            'Selection transcription differs')
    require(records['bp3d-43-humerus-export-list-retry']['status'] == 500 and
            records['bp3d-43-humerus-export-list-retry']['sha256'] ==
            'd4c27813ea1fb79013f2129ed054c6526ca264e5f8c3249897ef6b6f3a414e3b',
            'Retry outcome lost')
    for r in comparison['documented_export']['observed_download_results']:
        actual = records[r['receipt_id']]
        require(actual['finalURL'] == r['finalURL'] == 'https://lifesciencedb.jp/bp3d/' and
                actual['status'] == r['status'] == 200 and
                actual['bytecount'] == r['bytecount'] == 84659,
                'Redirected HTML promoted to source export')
        require(b'<html ' in bodies[r['receipt_id']] and
                not zipfile.is_zipfile(Path(actual['local_body_file']) if not external_root else
                                      external_root / Path(actual['local_body_file']).name),
                'Unexpected geometry response')
        require(not r['zip_payload'] and not r['geometry_acquired'], 'False geometry acquisition')
    baseline = comparison['retained_40_baseline']
    raw = (ROOT / 'sources/bodyparts3d/FJ3368.obj').read_bytes()
    lines = raw.decode().splitlines()
    require(hashlib.sha256(raw).hexdigest() == baseline['sha256'] ==
            '85f5445a11ecb029b027db0b9b34933982836d442b19ff531d1ca35a3bc3a237',
            'Retained baseline changed')
    require(sum(l.startswith('v ') for l in lines) == baseline['vertex_records'] == 2233 and
            sum(l.startswith('f ') for l in lines) == baseline['face_records'] == 3784,
            'Baseline count mismatch')
    require(not comparison['live_43_sample']['geometry_resolution_verified'] and
            comparison['live_43_sample']['vertex_records'] is None and
            comparison['mesh_density_ratio_43_to_40'] is None and
            not comparison['full_collection_downloaded'], 'Unsupported resolution claim')
    require(summary['full_43_archive_url'] is None and
            summary['full_43_archive_size_bytes'] is None, 'Fabricated full archive')
    require(comparison['license_state']['exact_43_asset_rights'].startswith('unresolved'),
            'Exact rights relabeled')
    proposal = load('nlm-elbow-localization-proposal.json')
    require(proposal['additional_nlm_requests_in_this_followup'] == 0 and
            not proposal['proposal']['raw_acquisition_executed'] and
            proposal['proposal']['max_new_images'] == 10 and
            proposal['proposal']['proposed_transfer_cap_bytes'] == 41943040 and
            proposal['laterality'] == 'unverified', 'NLM scope or laterality changed')
    return {'verified': True, 'request_receipts': 9, 'followup_body_bytes': 4802368,
            'catalog_bytes': 4528437, 'catalog_rows': 13312,
            'retained_40_vertex_records': 2233, 'retained_40_triangles': 3784,
            'live_43_meshes_acquired': 0, 'live_43_geometry_resolution_verified': False,
            'additional_nlm_images': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-root', type=Path, help='Moved follow-up receipt bodies')
    args = parser.parse_args()
    print(json.dumps(audit(args.external_root), sort_keys=True))
