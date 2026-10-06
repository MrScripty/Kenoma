"""Curation regressions: prevent provenance loss and false tissue coverage."""
import copy
import hashlib
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / 'data/elbow-v1/scripts'
sys.path.insert(0, str(SCRIPTS))
import audit_source_inventory as audit
import reacquire_inventory_inputs as reacquire


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = audit.load(audit.CURATION / 'source-inventory.json')
        cls.coverage = audit.build(cls.manifest)

    def test_retained_coverage_reproduces_without_network(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('Offline audit attempted network')):
            self.assertEqual(audit.build(self.manifest), audit.load(audit.CURATION / 'coverage.json'))

    def test_pins_are_independent_of_bytes_under_test(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / 'input').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                audit.verify_pin(root, {'path': 'input', 'bytes': 7, 'sha256': hashlib.sha256(b'correct').hexdigest()})
            with self.assertRaisesRegex(ValueError, 'escapes repository'):
                audit.resolve_input(root, '../escape')

    def test_many_to_many_mapping_preserves_leaf_and_groups(self):
        mapping, names, reverse, count = audit.read_mapping(audit.REPO / self.manifest['owners']['concept_to_elements'])
        self.assertEqual(mapping['FMA37668'], {'FJ1486'})
        self.assertIn('FMA37348', reverse['FJ1486'])
        self.assertIn('FMA37668', reverse['FJ1486'])
        self.assertGreater(len(reverse['FJ1486']), 2)

    def reject_mutation(self, mutate, message):
        candidate = copy.deepcopy(self.manifest)
        mutate(candidate)
        with self.assertRaisesRegex(ValueError, message):
            audit.build(candidate)

    def test_uninspected_scapula_not_promoted_to_inspected_mesh(self):
        self.reject_mutation(lambda d: next(r for r in d['requirements'] if r['id'] == 'scapula').update(availability='individual_surface'), 'Uninspected')

    def test_group_not_promoted_to_leaf(self):
        def change(d):
            row = next(r for r in d['requirements'] if r['id'] == 'brachialis')
            row['concepts'] = [{'id': 'FMA37348', 'name': 'muscle of free upper limb'}]
        self.reject_mutation(change, 'Requirement identity')

    def test_source_bone_cannot_be_relabelled_as_cartilage(self):
        self.reject_mutation(lambda d: next(r for r in d['requirements'] if r['id'] == 'humerus').update(tissue='cartilage', name='right distal humeral articular cartilage'), 'Requirement identity')

    def test_completion_requirements_cannot_disappear(self):
        for identity in ['humeral_cartilage', 'annular_ligament', 'biceps_distal_tendon', 'subcutaneous_fat']:
            with self.subTest(requirement=identity):
                self.reject_mutation(lambda d: d.update(requirements=[r for r in d['requirements'] if r['id'] != identity]), 'completion set differs')

    def test_fabricated_missing_tissue_is_rejected(self):
        self.reject_mutation(lambda d: next(r for r in d['requirements'] if r['id'] == 'subcutaneous_fat').update(expected_elements=['FJ2810']), 'Concept/element relation differs')

    def test_candidate_license_not_automatically_cleared(self):
        self.reject_mutation(lambda d: d['sources'][1]['license'].update(clearance='attribution_only_cleared'), '4.3 clearance remains unresolved')

    def test_full_archive_hash_not_invented(self):
        self.reject_mutation(lambda d: d['sources'][0]['archive'].update(sha256='0' * 64), 'Archive license/hash scope differs')

    def test_cross_specimen_registration_not_inferred(self):
        self.reject_mutation(lambda d: d['sources'][0]['provenance'].update(registered_to_other_people=True), 'Cross-specimen')

    def test_required_input_cannot_lose_pin(self):
        self.reject_mutation(lambda d: d.update(input_pins=[p for p in d['input_pins'] if not p['path'].endswith('bodyparts_zip_central_directory.bin')]), 'Unpinned input')

    def test_reacquisition_refuses_changed_bytes(self):
        pin = {'bytes': 3, 'sha256': hashlib.sha256(b'old').hexdigest()}
        with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
            reacquire.accept_bytes(b'new', pin)
        with self.assertRaisesRegex(ValueError, 'length differs'):
            reacquire.accept_bytes(b'long', pin)

    def test_reacquisition_cannot_write_in_repository(self):
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            reacquire.reacquire(audit.CURATION / 'incoming', ['mapping'])

    def test_pin_mismatch_receipt_and_no_candidate_written(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / 'incoming'
            raw_receipt = {'final_url': reacquire.ITEMS['license'][1], 'headers': {'Set-Cookie': 'secret', 'Content-Length': '3'}, 'status': 200}
            def fake_fetch(*args):
                reacquire.acquisition.log.append(raw_receipt)
                return b'new'
            with patch.object(reacquire.acquisition, 'fetch', side_effect=fake_fetch):
                receipt = reacquire.reacquire(output, ['license'])
            self.assertFalse(receipt['complete'])
            self.assertEqual(receipt['items'][0]['result'], 'unavailable_or_pin_mismatch')
            self.assertNotIn('secret', (output / 'inventory_reacquisition_log.json').read_text())
            self.assertFalse((output / 'sources/bodyparts_license.html').exists())

    def test_exact_range_payload_is_written_only_after_verification(self):
        relative, url, byte_range = reacquire.ITEMS['end-record']
        data = (audit.ROOT / relative).read_bytes()
        def fake_fetch(request_url, limit, requested_range):
            self.assertEqual((request_url, limit, requested_range), (url, len(data), byte_range))
            reacquire.acquisition.log.append({'final_url': url, 'status': 206,
                'headers': {'Content-Range': f'bytes {byte_range}/142903898'}})
            return data
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / 'incoming'
            with patch.object(reacquire.acquisition, 'fetch', side_effect=fake_fetch):
                receipt = reacquire.reacquire(output, ['end-record'])
            self.assertTrue(receipt['complete'])
            self.assertEqual((output / relative).read_bytes(), data)

    def test_wrong_range_extent_rejected_even_when_bytes_match(self):
        relative, url, byte_range = reacquire.ITEMS['end-record']
        data = (audit.ROOT / relative).read_bytes()
        def fake_fetch(*args):
            reacquire.acquisition.log.append({'final_url': url, 'status': 206,
                'headers': {'Content-Range': f'bytes {byte_range}/999'}})
            return data
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / 'incoming'
            with patch.object(reacquire.acquisition, 'fetch', side_effect=fake_fetch):
                receipt = reacquire.reacquire(output, ['end-record'])
            self.assertFalse(receipt['complete'])
            self.assertIn('Range response differs', receipt['items'][0]['error'])
            self.assertFalse((output / relative).exists())

    def test_attachments_stay_authored_and_unsegmented(self):
        self.assertEqual(len(self.coverage['attachments']), 7)
        self.assertEqual(sum(row['proximal']['kind'] == 'fixed_estimated_origin' for row in self.coverage['attachments']), 3)
        for row in self.coverage['attachments']:
            self.assertFalse(row['independent_enthesis_measurement'])
            self.assertIsNone(row['separate_tendon_mesh'])
            self.assertEqual(row['distal']['evidence_class'], 'atlas_derived_authored_connected_surface_selection')


if __name__ == '__main__':
    unittest.main()
