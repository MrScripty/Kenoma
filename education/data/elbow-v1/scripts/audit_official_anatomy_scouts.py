#!/usr/bin/env python3
"""Offline receipt/PNG integrity and scope audit; never downloads or creates labels."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import urllib.parse
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'curation/official-anatomy-scouts'
APPROVED = {'www.nlm.nih.gov', 'data.lhncbc.nlm.nih.gov',
            'dbarchive.biosciencedbc.jp', 'lifesciencedb.jp'}
SCOUTS = {
    'a_vm1450': (3561524, 'f357fbbcc43c0195e2994d187e63094216e02a4894ad94b2adf0dce9af4ba444'),
    'a_vm1550': (3467492, '74546104c4c14b3b8a0a018f7c0284928d9d3e036ec2a46018e3e3c8553347ad'),
    'a_vm1600': (3450446, '570cf80f01c6d9beaefcc4b0670cf8c561e6785321b22f469c4ef4bafda93ac4'),
}


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def png_integrity(data):
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'Not a PNG')
    offset, chunks, compressed = 8, [], bytearray()
    while offset < len(data):
        require(offset + 12 <= len(data), 'Truncated PNG chunk')
        size = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 8 + size
        require(end + 4 <= len(data), 'Truncated PNG payload')
        payload = data[offset + 8:end]
        crc = struct.unpack_from('>I', data, end)[0]
        require(zlib.crc32(kind + payload) & 0xffffffff == crc, 'PNG CRC mismatch')
        chunks.append(kind)
        if kind == b'IHDR':
            require(struct.unpack('>IIBBBBB', payload) == (2048, 1216, 8, 2, 0, 0, 0),
                    'Unexpected source dimensions or PNG encoding')
        if kind == b'IDAT':
            compressed.extend(payload)
        offset = end + 4
        if kind == b'IEND':
            break
    require(chunks[0] == b'IHDR' and chunks[-1] == b'IEND' and offset == len(data),
            'Unexpected PNG chunk layout')
    decoder = zlib.decompressobj()
    expected = (2048 * 3 + 1) * 1216
    pixels = decoder.decompress(bytes(compressed), expected + 1)
    require(len(pixels) == expected and decoder.eof and not decoder.unused_data,
            'Unexpected decoded PNG scanline size')
    require(all(pixels[row * (2048 * 3 + 1)] in range(5) for row in range(1216)),
            'Invalid PNG row filter')


def audit(external_root=None):
    receipts = load('request-receipts.json')
    records = receipts['records']
    require(len({r['id'] for r in records}) == len(records), 'Duplicate receipt ID')
    for r in records:
        for key in ('requestURL', 'finalURL'):
            require(urllib.parse.urlparse(r[key]).hostname in APPROVED,
                    'Unexpected network destination')
        if r['local_body_file']:
            path = Path(r['local_body_file'])
            if external_root:
                path = external_root / path.name
            data = path.read_bytes()
            require(len(data) == r['bytecount'], f"Receipt size mismatch: {r['id']}")
            require(hashlib.sha256(data).hexdigest() == r['sha256'],
                    f"Receipt hash mismatch: {r['id']}")
        else:
            require(r['bytecount'] == 0, 'Unread body has fabricated payload')
    image_records = {r['id']: r for r in records if r['id'] in SCOUTS}
    require(set(image_records) == set(SCOUTS), 'Unexpected scout set')
    for name, (size, digest) in SCOUTS.items():
        r = image_records[name]
        require((r['status'], r['bytecount'], r['sha256']) == (200, size, digest),
                'Scout differs from initial successful receipt')
        path = Path(r['local_body_file'])
        png_integrity((external_root / path.name if external_root else path).read_bytes())
    require(sum(r['bytecount'] for r in image_records.values()) == 10479462,
            'Unexpected image transfer total')
    require(receipts['scout_budget_bytes'] == 12582912, 'Scout budget changed')
    require(receipts['scout_transferred_bytes'] == 10479462, 'Incorrect transfer report')

    state = load('source-image-review.json')
    contract_bytes = (ROOT / 'curation/nlm-arm-feasibility/segmentation-contract.json').read_bytes()
    contract = json.loads(contract_bytes)
    targets = {r['inventory_requirement_id'] for r in contract['labels'] + contract['nonvoxel_targets']}
    require(state['contract_sha256'] == hashlib.sha256(contract_bytes).hexdigest(),
            'Annotation contract binding changed')
    require(state['specimen_id'] == 'nlm-visible-human-male', 'Specimen changed')
    require(state['stage'] == 'source_image_review' and state['source_images_imported'],
            'Source review stage incorrect')
    require(len(state['input_assets']) == 3, 'Unexpected input assets')
    for a in state['input_assets']:
        r = image_records[a['id']]
        require((a['bytes'], a['sha256'], a['source_url']) ==
                (r['bytecount'], r['sha256'], r['requestURL']), 'Source sidecar binding differs')
    require(state['image_geometry']['patient_affine_mm'] is None, 'Unsupported affine')
    require(state['region']['laterality'] == 'unverified' and
            state['region']['bounds_columns_rows_slices'] is None, 'Unsupported right ROI')
    require(not state['tissue_masks_imported'] and state['voxel_label_artifact'] is None,
            'Unsupported mask import')
    require(not state['clinical_validation'] and not state['simulation_ready'],
            'Unsupported qualification')
    require(len(state['annotations']) == 45 and
            {a['inventory_requirement_id'] for a in state['annotations']} == targets,
            'Missing or duplicated required targets')
    require(all(a['status'] == 'not_assessed' and a['evidence_kind'] == 'none' and
                a['annotation_artifact'] is None for a in state['annotations']),
            'Pixel scouts promoted to named tissue annotations')

    opts = load('bodyparts3d-options.json')
    require(opts['full_43_archive_url'] is None and opts['full_43_archive_size_bytes'] is None
            and not opts['full_43_geometry_resolution_verified'], 'Unsupported full 4.3 claim')
    require(not opts['full_mesh_archive_downloaded'], 'Unexpected full archive acquisition')
    mapping_record = next(r for r in records if r['id'] == 'bp3d-43-concept-map')
    path = Path(mapping_record['local_body_file'])
    if external_root:
        path = external_root / path.name
    with zipfile.ZipFile(path) as archive:
        require(archive.namelist() == ['FMA2Obj.txt'], 'Unexpected metadata ZIP member')
        info = archive.getinfo('FMA2Obj.txt')
        require(info.file_size == 605737 and info.CRC == 0xe2ccf5fb, 'Mapping ZIP metadata changed')
        data = archive.read(info)  # zipfile checks actual uncompressed CRC.
    require(hashlib.sha256(data).hexdigest() == opts['mapping']['sha256'], 'Mapping hash changed')
    rows = [l.split('\t') for l in data.decode().splitlines() if l and not l.startswith('#')]
    require(len(rows) == 5614 and len({r[0] for r in rows}) == 4528 and
            len({part for r in rows for part in r[2].split('+')}) == 3210, 'Mapping count changed')
    require([r for r in rows if r[0] == 'FMA23130'] == opts['mapping']['right_humerus'],
            'Official many-to-many identity lost')
    require(opts['license_state']['exact_43_asset_rights'].startswith('unresolved'),
            'Exact asset rights relabeled')
    stopped = {r['id']: r for r in records if r.get('route_stopped')}
    require(stopped['bp3d-humerus43-export-list']['status'] == 500, 'Export failure omitted')
    require(stopped['bp3d-43-object-metadata']['bytecount'] == 0, 'Over-cap body read')
    require(not load('runtime-state.json')['configVersionRuntimeVerified'],
            'Runtime config identity falsely claimed')
    return {'verified': True, 'receipt_count': len(records), 'scout_images': 3,
            'scout_bytes': 10479462, 'native_dimensions_columns_rows': [2048, 1216],
            'png_crc_and_scanline_integrity': True, 'schema_stage': state['stage'],
            'anatomical_laterality': 'unverified', 'unassessed_targets': 45,
            'named_tissue_masks': 0, 'full_43_geometry_resolution_verified': False,
            'mesh_archives_downloaded': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-root', type=Path,
                        help='Directory containing preserved receipt bodies after moving external files')
    args = parser.parse_args()
    print(json.dumps(audit(args.external_root), sort_keys=True))
