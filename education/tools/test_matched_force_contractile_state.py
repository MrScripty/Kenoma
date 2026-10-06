"""Independent regressions for the explicit macro coupling, not an arm test."""
import unittest
import numpy as np
from scipy.linalg import expm

import matched_force_contractile_state as experiment
import continuous_strain_ce_reference as ce


class ContractileCouplingTests(unittest.TestCase):
    def test_actual_baseline_calibration_and_serial_force_fault(self):
        x, w = ce.gauss(-3., 3., 200)
        n, _ = experiment.stationary(x, w, ce.capacity(4.5))
        phi = ce.moments(n, x, w)[1]
        self.assertGreater(abs(phi-1.), .01)
        matched = experiment.active_stress(1.25, phi, phi)
        self.assertEqual(matched, 155000.*.5625)
        self.assertGreater(abs(.0004*(matched*130-matched)), 1e-4)

    def test_independent_nonsymmetric_matrix_exponential(self):
        # Small independent direct expm checks the similarity and sensitivity,
        # including conservation feedback; it is not the nonlinear reference solver.
        x, w = ce.gauss(-3., 3., 48)
        N = ce.capacity(4.5)
        n, m = experiment.stationary(x, w, N)
        J = -np.diag(ce.detachment(x))-(1+N-2*(w@n))*np.outer(ce.attachment(x), w)
        t = np.array([0., .008, .1, .2])
        response = experiment.sensitivities(x, w, N, t)
        for index, time in enumerate(t):
            direct = expm(J*time)@m
            np.testing.assert_allclose(response['density'][index], direct, rtol=1e-10, atol=1e-12)

    def test_envelope_slope_retained_in_relaxed_and_fast_law(self):
        self.assertEqual(experiment.envelope_prime(1.25), -3.)
        relaxed = experiment.SIGMA*experiment.envelope_prime(1.25)
        self.assertEqual(relaxed, -465000.)
        x, w = ce.gauss(-3., 3., 200)
        N = ce.capacity(4.5)
        n, _ = experiment.stationary(x, w, N)
        B, phi, _ = ce.moments(n, x, w)
        response = experiment.sensitivities(x, w, N, np.array([0., .2]))
        self.assertAlmostEqual(response['phi'][0], B/.5, places=12)
        fast = relaxed+experiment.SIGMA*.5625*130*response['phi'][0]/phi
        self.assertGreater(fast, 0.)
        # Erasing transport must reproduce the old negative slope.
        self.assertLess(relaxed+experiment.SIGMA*.5625*130*0./phi, 0.)


if __name__ == '__main__':
    unittest.main(verbosity=2)
