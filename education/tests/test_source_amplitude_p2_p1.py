"""Test explicit activation and matched-alpha invariance, not solver duplication."""
import sys
import unittest
import json
from decimal import Decimal
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from source_amplitude_p2_p1 import ExplicitBody, ANCHOR, BASE, model


class ActivationTests(unittest.TestCase):
    def test_bound_primary_cell_converts_to_selected_amplitude(self):
        path = Path(__file__).resolve().parents[1]/'data/anatomical-arm-v1/review/source-amplitude-p2-p1/primary-source-binding.json'
        binding = json.loads(path.read_text())
        self.assertEqual(binding['table_binding']['cell'], '15.5 (5.0)')
        self.assertEqual(Decimal(binding['table_binding']['mean_decimal']) / Decimal('0.0001'), Decimal('155000'))
        self.assertEqual(ANCHOR['sigma0'], binding['unit_conversion']['selected_Pa'])

    def test_explicit_full_activation_reaches_bound_reference_force(self):
        mesh = model.mesh((1, 1, 1))
        body = ExplicitBody(mesh, ANCHOR, 1.)
        x, reference = body.analytic(1.)
        state = body.evaluate(x)
        force = -state['g'].reshape(-1, 3)[mesh['X'][:, 0] == 0, 0].sum()
        self.assertAlmostEqual(force, 62., places=10)
        self.assertAlmostEqual(reference['capForceN'], 62., places=10)
        self.assertLess(state['residual'], 1e-10)
        self.assertEqual(model.PARAM, BASE)

    def test_matched_alpha_preserves_full_operator(self):
        mesh = model.mesh((1, 1, 1))
        alpha = .01*BASE['sigma0']
        original = ExplicitBody(mesh, BASE, .01)
        matched = ExplicitBody(mesh, ANCHOR, alpha/ANCHOR['sigma0'])
        x, _ = original.analytic(1.25)
        r, s = original.evaluate(x, True), matched.evaluate(x, True)
        for key in ['g', 'H', 'p']:
            self.assertLess(np.linalg.norm(r[key]-s[key])/max(1, np.linalg.norm(r[key])), 1e-12)
        self.assertAlmostEqual(r['energy'], s['energy'], places=12)
        self.assertEqual(model.PARAM, BASE)


if __name__ == '__main__':
    unittest.main()
