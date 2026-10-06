"""Guard metadata-only feasibility against fabricated observation or source mixing."""
import copy
import pathlib
import sys
import unittest
from unittest.mock import patch

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / 'data/elbow-v1/scripts'
sys.path.insert(0, str(SCRIPTS))
import audit_nlm_arm_feasibility as audit


class NLMFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = [audit.inventory.load(audit.ROOT / name) for name in
                      ['feasibility.json', 'segmentation-contract.json', 'annotation-state.json']]

    def reject(self, mutate, message):
        inputs = copy.deepcopy(self.inputs)
        mutate(*inputs)
        with self.assertRaisesRegex(ValueError, message):
            audit.verify(*inputs)

    def test_metadata_audit_is_offline_and_reports_no_import(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected network')):
            result = audit.verify(*self.inputs)
        self.assertEqual(result['unassessed_targets'], 45)
        self.assertEqual(result['voxel_label_classes'], 40)
        self.assertFalse(result['source_images_imported'])
        self.assertIsNone(result['localized_region'])

    def test_specimen_substitution_rejected(self):
        self.reject(lambda m, c, s: s.update(specimen_id='nlm-visible-human-female'), 'Single male specimen')

    def test_candidate_specimen_substitution_rejected(self):
        self.reject(lambda m, c, s: m['scout_candidates'][0].update(specimen_id='TARO'), 'Candidate source/specimen')

    def test_fat_not_merged_with_fascia(self):
        self.reject(lambda m, c, s: next(t for t in c['labels'] if t['id'] == 'subcutaneous_fat').update(name='fat and fascia', tissue='fascia'), 'Target label/tissue')

    def test_cartilage_gap_cannot_disappear(self):
        self.reject(lambda m, c, s: c.update(labels=[t for t in c['labels'] if t['id'] != 'humeral_cartilage']), 'Incomplete or duplicate')

    def test_unknown_is_not_background(self):
        self.reject(lambda m, c, s: c['reserved_values'].update(unknown_unassessed=1), 'must remain distinct')

    def test_vector_field_is_not_tissue_label(self):
        self.reject(lambda m, c, s: next(t for t in c['nonvoxel_targets'] if t['id'] == 'muscle_fibres').update(representation='uint16_voxel_label'), 'cannot become a tissue voxel')

    def test_mask_import_not_invented(self):
        self.reject(lambda m, c, s: s.update(tissue_masks_imported=True), 'cannot be declared imported')

    def test_roi_not_invented(self):
        self.reject(lambda m, c, s: s['region'].update(status='reviewed_roi', laterality='right', bounds_columns_rows_slices=[[0,10],[0,10],[0,1]]), 'ROI cannot be localized')

    def test_nominal_sampling_is_not_cryo_affine(self):
        self.reject(lambda m, c, s: s['image_geometry'].update(patient_affine_mm=[[0.33,0,0,0],[0,0.33,0,0],[0,0,1,0],[0,0,0,1]]), 'Cryosection geometry is not established')

    def test_atlas_prior_not_relabelled_as_observed(self):
        self.reject(lambda m, c, s: s['annotations'][0].update(status='reviewed_image_annotation', evidence_kind='authored_prior'), 'atlas prior cannot become observed')

    def test_measurement_uncertainty_not_invented(self):
        self.reject(lambda m, c, s: s['annotations'][0].update(uncertainty={'boundary_error_mm':0.165}), 'Do not invent')

    def test_unacquired_bytes_do_not_get_pin(self):
        self.reject(lambda m, c, s: m['scout_candidates'][0].update(raw_sha256='0'*64), 'invented content pin')

    def test_header_not_promoted_to_cryo_geometry(self):
        self.reject(lambda m, c, s: m['header_observation'].update(cryosection_affine='copied_from_ct'), 'cannot supply raw identity or cryosection')

    def test_required_version_notice_preserved(self):
        self.reject(lambda m, c, s: m['terms'].update(checkpoint_notice=''), 'terms/version notice missing')

    def test_scout_budget_enforced(self):
        self.reject(lambda m, c, s: m['bounded_next_acquisition'].update(transfer_budget_bytes=1024), 'Scout budget exceeded')


if __name__ == '__main__':
    unittest.main()
