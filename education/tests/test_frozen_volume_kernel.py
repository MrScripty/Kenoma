"""Kernel representation and independent physical derivatives, no sign target."""
import json
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from frozen_pressure_spaces import ROOT, FrozenOperator, replay
from frozen_volume_kernel import maps, restrict, kernel_basis, volume_metrics
from run_frozen_volume_admissibility import volume_replay


class VolumeKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        packet = ROOT/'data/anatomical-arm-v1/review/frozen-pressure-space-comparison'
        mesh = json.loads((packet/'coarse-mesh.json').read_text())['mesh']
        cls.m = {k: np.array(v) if isinstance(v, list) else v for k, v in mesh.items()}
        request = json.loads((packet/'coarse-1.25-request.json').read_text())
        archived = json.loads((packet/'coarse-1.25-assembled.json').read_text())
        cls.x = np.array(archived['positionsM'])
        cls.body = FrozenOperator(cls.m, 'pointwise', material=request['material'], activation=request['activation'])
        cls.state = cls.body.evaluate(cls.x, True)
        broken = FrozenOperator(cls.m, 'brokenP1', material=request['material'], activation=request['activation'])
        cls.T, cls.Q, cls.D = maps(cls.body, cls.state, broken, broken.evaluate(cls.x))
        cls.kernel = restrict(cls.state['H'], cls.T, cls.Q)
        cls.Z = cls.kernel['basis']
        cls.v = np.zeros(cls.x.size)
        cls.v[cls.m['free']] = cls.kernel['lowestFreeDirection']
        cls.v = cls.v.reshape(cls.x.shape)

    def test_all_rows_and_independent_pointwise_kernel(self):
        self.assertEqual(self.T.shape[0], 4*len(self.m['tets']))
        self.assertGreater(self.kernel['redundantRowCount'], 0)
        self.assertEqual(self.kernel['rank'], self.kernel['directPointMapRank'])
        self.assertEqual(self.kernel['displacementKernelDimension'], len(self.m['free'])-self.kernel['rank'])
        self.assertLess(self.kernel['momentDirectGramRelativeDifference'], 1e-12)
        self.assertLess(self.kernel['directMomentKernelProjectorDifferenceFrobenius'], 1e-10)
        self.assertLess(self.kernel['basisOrthogonalityErrorFrobenius'], 1e-10)
        self.assertLess(np.linalg.norm(self.Q@self.Z)/np.linalg.norm(self.Q), 1e-12)
        metrics = volume_metrics(self.body, self.state, self.x, self.v, self.T, self.Q)
        self.assertEqual(metrics['maximumHeldCapVariationM'], 0)
        self.assertAlmostEqual(metrics['euclideanNodalNorm'], 1)
        self.assertLess(metrics['directionalLogJRMSPerM']/np.linalg.norm(self.T, 2), 1e-12)

    def test_redundant_row_rotation_keeps_physical_restriction(self):
        rng = np.random.default_rng(2981)
        rotation, _ = np.linalg.qr(rng.normal(size=(len(self.T), len(self.T))))
        rotated_Z, _, rank = kernel_basis(rotation@self.T)
        self.assertEqual(rank, self.kernel['rank'])
        self.assertLess(np.linalg.norm(rotated_Z@rotated_Z.T-self.Z@self.Z.T), 1e-10)
        np.testing.assert_allclose(np.linalg.eigvalsh(rotated_Z.T@self.state['H']@rotated_Z),
                                   self.kernel['fullRestrictedEigenvaluesNPerM'], atol=1e-7, rtol=1e-10)

    def test_full_material_tangent_and_volume_observer(self):
        vf = self.v.ravel()[self.m['free']]
        full_action = self.state['H']@vf
        original = replay(self.body, self.x, self.state, direction=self.v, surface=False)
        independent_action = np.array(original['tangentActionNPerM'])[self.m['free']]
        self.assertLess(np.linalg.norm(self.Z.T@(independent_action-full_action))/np.linalg.norm(self.Z.T@full_action), 1e-4)
        decomposition = self.body.decomposition(self.state, self.v)
        observer = volume_replay(self.body, self.x, self.v, 2)
        for key, value in observer['rayleigh'].items():
            self.assertAlmostEqual(value, decomposition[key], delta=1e-7)
        self.assertLess(observer['directionalLogJRMSPerM']/np.linalg.norm(self.T, 2), 1e-12)
        # The positive volume penalty vanishes; the full prestress is retained.
        self.assertLess(abs(decomposition['volumeConstraintNPerM']), 1e-12)
        self.assertGreater(abs(decomposition['pressurePrestressNPerM']), 1e-8)
        self.assertAlmostEqual(decomposition['totalNPerM'], float(vf@full_action), delta=1e-7)


if __name__ == '__main__':
    unittest.main()
