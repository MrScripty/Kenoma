"""Regression: recorded accurate probes qualify without changing equilibrium gates."""
import hashlib
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from source_amplitude_p2_p1_v2 import OLD, original_scope


class ScopeTest(unittest.TestCase):
    def test_original_derivative_scope_qualifies_retained_probes_only(self):
        path = OLD/'coarse-1.25.json'
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        record = json.loads(path.read_text())
        self.assertTrue(record['stationaryAccepted'])
        self.assertFalse(record['spectrum']['derivativeGatesPass'])
        corrected = original_scope(record['spectrum'])
        self.assertTrue(corrected['derivativeGatesPass'])
        self.assertEqual(corrected['classification'], 'NEGATIVE_STATIONARY_DIRECTION')
        self.assertEqual(corrected['lowestEigenvaluesNPerM'], record['spectrum']['lowestEigenvaluesNPerM'])
        rejected = json.loads((OLD/'coarse-1.01.json').read_text())
        self.assertFalse(rejected['stationaryAccepted'])
        self.assertGreater(rejected['replays']['256']['pointwisePressureRMS'], 1e-6)
        self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
