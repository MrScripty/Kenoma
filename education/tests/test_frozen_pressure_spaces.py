"""Full-energy derivatives away from the affine identity; original Node parity."""
import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.linalg import cho_solve

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from frozen_pressure_spaces import FrozenOperator, SPACES, replay
from source_amplitude_p2_p1 import ExplicitBody, ANCHOR, model


class FrozenTests(unittest.TestCase):
    def setUp(self):
        self.m = model.mesh((4, 1, 1))

    def test_broken_affine_identity_is_full_tangent_with_prestress(self):
        for stretch in [1.01, 1.25]:
            x, _ = ExplicitBody(self.m, ANCHOR, 1.).analytic(stretch)
            broken = FrozenOperator(self.m, 'brokenP1'); point = FrozenOperator(self.m, 'pointwise')
            r = broken.evaluate(x, True); s = point.evaluate(x, True)
            self.assertLess(abs(r['energy']-s['energy']), 1e-12)
            np.testing.assert_allclose(r['g'], s['g'], atol=2e-9, rtol=1e-10)
            np.testing.assert_allclose(r['H'], s['H'], atol=1e-8, rtol=1e-12)
            self.assertGreater(broken.coupling(r)['nullity'], 0)

    def test_nonaffine_energy_force_and_complete_hessian(self):
        start, _, _ = ExplicitBody(self.m, ANCHOR, 1.).initial(1.25)
        rng = np.random.default_rng(12941)
        v = np.zeros(start.size); v[self.m['free']] = rng.normal(size=len(self.m['free']))
        v /= np.linalg.norm(v); v = v.reshape(start.shape)
        for space in SPACES:
            B = FrozenOperator(self.m, space); r = B.evaluate(start, True); h = 1e-7
            plus = B.evaluate(start+h*v); minus = B.evaluate(start-h*v)
            self.assertLess(abs((plus['energy']-minus['energy'])/(2*h)-r['g']@v.ravel()), 1e-6)
            Hv = r['H']@v.ravel()[self.m['free']]
            fd = (plus['g']-minus['g'])[self.m['free']]/(2*h)
            self.assertLess(np.linalg.norm(fd-Hv)/np.linalg.norm(Hv), 1e-4)
            q = replay(B, start, r, direction=v, surface=False)
            self.assertLess(abs(q['energyJ']-r['energy']), 1e-12)
            self.assertLess(np.max(abs(q['gradientN']-r['g'])), 2e-6)
            self.assertLess(np.linalg.norm(np.array(q['tangentActionNPerM'])[self.m['free']]-Hv)/np.linalg.norm(Hv), 1e-4)

    def test_broken_linearized_projection_and_no_optimizer(self):
        x, _ = ExplicitBody(self.m, ANCHOR, 1.).analytic(1.01)
        B = FrozenOperator(self.m, 'brokenP1'); r = B.evaluate(x, True)
        rng = np.random.default_rng(390); v = np.zeros(x.size); v[self.m['free']] = rng.normal(size=len(self.m['free']))
        v /= np.linalg.norm(v); v = v.reshape(x.shape)
        dF = np.einsum('eni,eqna->eqia', v[self.m['tets']], B.grad)
        dlog = np.einsum('eqia,eqia->eq', r['G'], dF)
        p = cho_solve(B.Mfactor, r['D']@v.ravel())
        self.assertLess(np.max(abs(dlog-p[B.pi]@B.L.T)), 1e-10)
        with self.assertRaisesRegex(RuntimeError, 'prohibits nonlinear solves'):
            B.newton(x)


if __name__ == '__main__':
    unittest.main()
