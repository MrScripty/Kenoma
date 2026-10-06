#!/usr/bin/env python3
"""Independent invariants for units, activation branches and source provenance."""
import unittest
import numpy as np
from scipy.integrate import solve_ivp
from millard_reference_benchmark import Curve,build_curves,activation_rhs,exact_activation
from millard_source_oracle import verified_source

class ReferenceCases(unittest.TestCase):
    def test_source_pin_and_bytes(self):
        m=verified_source();self.assertEqual(m['commit'],'5bc7d3308eda742690f485ec060bfe725a349fa6');self.assertEqual(len(m['files']),12)
    def test_activation_closed_form_both_branches(self):
        for a0,u in [(.05,.35),(.35,.05),(.01,1.)]:
            sol=solve_ivp(lambda t,y:[activation_rhs(y[0],u)],[0,.1],[a0],rtol=1e-11,atol=1e-13,dense_output=True)
            for t in [.001,.01,.05,.1]:self.assertAlmostEqual(sol.sol(t)[0],exact_activation(a0,u,t),delta=2e-10)
    def test_passive_tendon_and_velocity_normalizations(self):
        c={n:Curve(r) for n,r in build_curves().items()}
        self.assertAlmostEqual(c['active'].value(1),1,delta=1e-13)
        self.assertEqual(c['passive'].value(.9),0);self.assertEqual(c['tendon'].value(.9),0)
        self.assertAlmostEqual(c['passive'].value(1.7),1,delta=1e-13);self.assertAlmostEqual(c['tendon'].value(1.049),1,delta=1e-13)
        for v,y in [(-1,0),(0,1),(1,1.4)]:self.assertAlmostEqual(c['velocity'].value(v),y,delta=1e-13)
    def test_descending_total_derivative_retained(self):
        c={n:Curve(r) for n,r in build_curves().items()};total=lambda q:c['active'].value(q)+c['passive'].value(q)
        finite_difference=(total(1.1+1e-5)-total(1.1-1e-5))/2e-5
        self.assertLess(finite_difference,0);self.assertAlmostEqual(finite_difference,c['active'].value(1.1,True)+c['passive'].value(1.1,True),delta=2e-8)
    def test_activation_not_instant_excitation_or_force(self):
        self.assertGreater(activation_rhs(.05,.35),0);self.assertEqual(activation_rhs(.05,.05),0)
        a=exact_activation(.05,.35,.001);self.assertTrue(.05<a<.35)

if __name__=='__main__':unittest.main(verbosity=2)
