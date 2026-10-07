"""Document pins, current receipt scope and bounded non-destructive acquisition."""
import io
import json
import shutil
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1] / 'data/elbow-v1'
sys.path.insert(0, str(PACKAGE / 'scripts'))
import fetch_documents as documents
import fetch_sources as acquisition


class Response(io.BytesIO):
    status = 200
    def __init__(self, body, url):
        super().__init__(body)
        self.url = url
        self.headers = {'Content-Length': str(len(body)), 'X-Test-Fixture': 'not real network evidence'}
    def geturl(self):
        return self.url


class SourceDocuments(unittest.TestCase):
    def setUp(self):
        # HTTP fixtures must not depend on the host's current free space.
        # The production 1.5 GiB floor remains unchanged and is tested below.
        capacity = shutil._ntuple_diskusage(10 * 1024**3, 0, 10 * 1024**3)
        self.disk = patch.object(shutil, 'disk_usage', return_value=capacity)
        self.disk.start()
        self.addCleanup(self.disk.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.pins = json.loads((PACKAGE / 'audit/source_document_pins.json').read_text())['documents']
        self.by_url = {p['acquisition_url']:p for p in self.pins if p['acquisition_url']}
        self.release = self.directory / 'official-release-fixture'
        self.release.mkdir()
        for pin in self.pins:
            if pin['acquisition_url'] is None:
                (self.release / pin['release_filename']).write_bytes((PACKAGE / pin['path']).read_bytes())

    def response(self, request, **kwargs):
        pin = self.by_url[request.full_url]
        return Response((PACKAGE / pin['path']).read_bytes(), request.full_url)

    def test_all_document_identities_verified_local_receipts_not_claimed_as_http(self):
        with patch.object(acquisition.urllib.request, 'urlopen', side_effect=self.response):
            receipt = documents.reacquire(self.directory / 'output', self.release)
        self.assertTrue(receipt['complete'])
        self.assertEqual(len(receipt['documents']), 5)
        for item in receipt['documents']:
            self.assertEqual(item['sha256'], item['expected_sha256'])
            self.assertEqual(item['bytes'], item['expected_bytes'])
            self.assertLessEqual(item['started_utc'], item['completed_utc'])
            if item['method'] == 'http':
                self.assertIn('started_utc', item['http_receipt'])
            else:
                self.assertFalse(item['network_receipt_available'])
                self.assertNotIn('http_receipt', item)

    def test_mismatch_rejected_without_promoting_or_touching_accepted_source(self):
        before = (PACKAGE / self.pins[0]['path']).read_bytes()
        with patch.object(acquisition.urllib.request, 'urlopen', side_effect=lambda request, **kwargs: Response(b'wrong release bytes', request.full_url)):
            receipt = documents.reacquire(self.directory / 'output', self.release)
        self.assertFalse(receipt['complete'])
        self.assertEqual(receipt['documents'][0]['result'], 'unavailable_or_pin_mismatch')
        self.assertFalse((self.directory / 'output' / self.pins[0]['path']).exists())
        self.assertEqual((PACKAGE / self.pins[0]['path']).read_bytes(), before)

    def test_incomplete_provider_access_never_counts_as_document_acquisition(self):
        def fetch(request, **kwargs):
            if request.full_url in self.by_url:
                return self.response(request)
            return Response(b'provider folder HTML, not a release document', request.full_url)
        with patch.object(acquisition.urllib.request, 'urlopen', side_effect=fetch):
            receipt = documents.reacquire(self.directory / 'output')
        self.assertFalse(receipt['complete'])
        self.assertEqual([p['result'] for p in receipt['documents']][-2:], ['manual_download_required'] * 2)
        self.assertEqual(receipt['provider_access'][0]['result'], 'accessible')
        self.assertNotIn('http_receipt', receipt['documents'][-1])

    def test_output_cannot_overwrite_accepted_or_previous_acquisition(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            documents.reacquire(PACKAGE / 'audit/forbidden')
        output = self.directory / 'existing'
        output.mkdir()
        with self.assertRaises(FileExistsError):
            documents.reacquire(output)

    def test_download_caps_and_total_budget_remain_enforced(self):
        acquisition.transferred = 0
        with patch.object(acquisition.urllib.request, 'urlopen', return_value=Response(b'abcdef', 'fixture')):
            with self.assertRaisesRegex(RuntimeError, 'exceeds limit'):
                acquisition.fetch('https://example.invalid', 5)
        acquisition.transferred = acquisition.MAX_TOTAL
        with patch.object(acquisition.urllib.request, 'urlopen', return_value=Response(b'a', 'fixture')):
            with self.assertRaisesRegex(RuntimeError, 'budget exceeded'):
                acquisition.fetch('https://example.invalid', 5)
        acquisition.transferred = 0

    def test_actual_low_space_floor_still_rejects_before_network(self):
        with patch.object(shutil, 'disk_usage', return_value=shutil._ntuple_diskusage(10, 10, 0)), patch.object(acquisition.urllib.request, 'urlopen') as network:
            with self.assertRaisesRegex(RuntimeError, 'Preserve 1.5 GiB free-space floor'):
                acquisition.fetch('https://example.invalid', 5)
            network.assert_not_called()
