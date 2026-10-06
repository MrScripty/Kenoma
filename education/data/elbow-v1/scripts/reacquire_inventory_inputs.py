#!/usr/bin/env python3
"""Explicit, pinned metadata reacquisition using the existing elbow-v1 fetch owner."""
import argparse
import datetime
import hashlib
import json
import pathlib
from urllib.parse import urlparse

import audit_source_inventory as audit
import fetch_sources as acquisition

BASE = 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
ITEMS = {
    'mapping': ('sources/bodyparts_isa_element_parts.txt', BASE + 'isa_element_parts.txt', None),
    'directory': ('audit/bodyparts_zip_central_directory.bin', acquisition.URL, '142733851-142903875'),
    'end-record': ('audit/bodyparts_zip_end_record.bin', acquisition.URL, '142903876-142903897'),
    'license': ('sources/bodyparts_license.html', 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html', None),
    'readme': ('sources/bodyparts_README.html', BASE + 'README_e.html', None),
    'coordinate-system': ('sources/bodyparts_coordinate_system.png', 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20130619/coordinate_system.png', None),
    'release-note': ('sources/bodyparts_release_4.0.html', 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20130619/release_4.0_e.html', None),
}
SAFE_HEADERS = {'content-type', 'content-length', 'content-range', 'etag', 'last-modified', 'date'}


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def accept_bytes(data, pin):
    audit.require(len(data) == pin['bytes'], 'Candidate length differs from accepted pin')
    audit.require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'Candidate SHA-256 differs from accepted pin')


def reacquire(output, items):
    output = output.resolve()
    audit.require(not output.is_relative_to(audit.REPO), 'Use a new output directory outside the repository')
    audit.require(items and len(items) == len(set(items)) and set(items) <= set(ITEMS), 'Invalid or duplicate acquisition item')
    manifest = audit.load(audit.CURATION / 'source-inventory.json')
    audit.build(manifest)
    pins = {p['path']: p for p in manifest['input_pins']}
    output.mkdir(parents=True, exist_ok=False)
    acquisition.transferred = 0
    acquisition.log.clear()
    receipt = {'schema_version': 1, 'started_utc': utc(),
               'inventory_sha256': hashlib.sha256((audit.CURATION / 'source-inventory.json').read_bytes()).hexdigest(),
               'scope': 'Current bounded reacquisition of accepted metadata bytes only; no full archive or new source adoption.',
               'byte_budget': acquisition.MAX_TOTAL,
               'free_space_floor_bytes': 1536 * 1024**2,
               'license_id': 'CC-BY-4.0',
               'attribution': manifest['sources'][0]['license']['attribution'],
               'items': []}
    for name in items:
        relative, url, byte_range = ITEMS[name]
        pin = pins['education/data/elbow-v1/' + relative]
        item = {'item': name, 'url': url, 'range': byte_range,
                'expected_bytes': pin['bytes'], 'expected_sha256': pin['sha256'], 'started_utc': utc()}
        try:
            # Exact accepted length is also the response cap. Never request a
            # ZIP without a Range, and never relax a pin to match new bytes.
            audit.require(not url.endswith('.zip') or byte_range is not None, 'Full archive request forbidden')
            data = acquisition.fetch(url, pin['bytes'], byte_range)
            raw_receipt = acquisition.log[-1]
            item['http_receipt'] = {k: v for k, v in raw_receipt.items() if k != 'headers'}
            headers = {k.lower(): v for k, v in raw_receipt['headers'].items() if k.lower() in SAFE_HEADERS}
            item['http_receipt']['headers'] = headers
            final = urlparse(raw_receipt['final_url'])
            audit.require(final.scheme == 'https' and final.hostname == 'dbarchive.biosciencedbc.jp', 'Unexpected source redirect')
            if byte_range:
                audit.require(headers.get('content-range') == f'bytes {byte_range}/142903898', 'Range response differs from pinned archive extent')
            item.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            accept_bytes(data, pin)
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            item['result'] = 'verified_exact_bytes'
        except Exception as error:
            item.update(result='unavailable_or_pin_mismatch', error=f'{type(error).__name__}: {error}')
        finally:
            item['completed_utc'] = utc()
            receipt['items'].append(item)
            receipt.update(completed_utc=utc(), downloaded_bytes=acquisition.transferred,
                           complete=len(receipt['items']) == len(items) and all(i['result'] == 'verified_exact_bytes' for i in receipt['items']))
            (output / 'inventory_reacquisition_log.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=pathlib.Path, required=True, help='New directory outside the repository; never overwrite accepted inputs')
    parser.add_argument('--items', nargs='+', choices=sorted(ITEMS), default=list(ITEMS), help='Explicit accepted metadata items; defaults to all seven')
    args = parser.parse_args()
    result = reacquire(args.output, args.items)
    print(json.dumps({'complete': result['complete'], 'downloaded_bytes': result['downloaded_bytes'],
                      'results': {i['item']: i['result'] for i in result['items']},
                      'receipt': str(args.output / 'inventory_reacquisition_log.json')}, indent=2))
    raise SystemExit(0 if result['complete'] else 1)
