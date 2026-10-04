#!/usr/bin/env python3
"""Reacquire missing document coverage without changing accepted source bytes."""
import datetime
import hashlib
import json
import pathlib
import sys
import fetch_sources as acquisition

ROOT = pathlib.Path(__file__).resolve().parents[1]


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def reacquire(output, release_directory=None):
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Use a new output directory outside the accepted data package')
    output.mkdir(parents=True, exist_ok=False)
    pins = json.loads((ROOT / 'audit/source_document_pins.json').read_text())
    acquisition.transferred = 0
    acquisition.log.clear()
    receipt = {'schema_version': 1, 'started_utc': utc(),
               'scope': 'Current reacquisition only; no original acquisition times or headers inferred.',
               'documents': [], 'provider_access': []}
    for pin in pins['documents']:
        item = {'path': pin['path'], 'expected_bytes': pin['bytes'],
                'expected_sha256': pin['sha256'], 'started_utc': utc()}
        try:
            if pin['acquisition_url']:
                item.update(method='http', url=pin['acquisition_url'])
                data = acquisition.fetch(pin['acquisition_url'], pin['byte_limit'])
                item['http_receipt'] = acquisition.log[-1].copy()
            elif release_directory is not None:
                item.update(method='local_release_file_verification',
                            release_filename=pin['release_filename'],
                            network_receipt_available=False)
                with (release_directory / pin['release_filename']).open('rb') as source:
                    data = source.read(pin['byte_limit'] + 1)
                if len(data) > pin['byte_limit']:
                    raise ValueError('Release document exceeds byte budget')
            else:
                item.update(result='manual_download_required',
                            release_folder_url=pin['release_folder_url'],
                            release_filename=pin['release_filename'],
                            reason='Original direct file URL was not recorded; acquire from the official release folder and rerun with --openarm-release-directory.')
                continue
            item.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            if len(data) != pin['bytes'] or item['sha256'] != pin['sha256']:
                raise ValueError('Byte identity differs from accepted pin; source not replaced')
            target = output / pin['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            item['result'] = 'verified_exact_bytes'
        except Exception as error:
            item.update(result='unavailable_or_pin_mismatch', error=f'{type(error).__name__}: {error}')
        finally:
            item['completed_utc'] = utc()
            receipt['documents'].append(item)
    # Probe a provider locator only to document access. Its HTML is never an
    # acquisition of either missing release document and cannot satisfy a pin.
    if release_directory is None:
        url = next(p['release_folder_url'] for p in pins['documents'] if p['source_id'] == 'openarm')
        probe = {'url': url, 'started_utc': utc(), 'scope': 'Provider folder access only; no document identity claim'}
        try:
            acquisition.fetch(url, 128000)
            probe.update(result='accessible', http_receipt=acquisition.log[-1].copy())
        except Exception as error:
            probe.update(result='unavailable', error=f'{type(error).__name__}: {error}')
        probe['completed_utc'] = utc()
        receipt['provider_access'].append(probe)
    receipt.update(completed_utc=utc(), downloaded_bytes=acquisition.transferred,
                   complete=all(p['result'] == 'verified_exact_bytes' for p in receipt['documents']))
    (output / 'document_reacquisition_log.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    parser.add_argument('--openarm-release-directory', type=pathlib.Path)
    args = parser.parse_args()
    receipt = reacquire(args.output, args.openarm_release_directory)
    print(json.dumps(receipt, indent=2))
    sys.exit(0 if receipt['complete'] else 1)
