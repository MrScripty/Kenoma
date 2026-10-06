"""Independent original-law parity and mixed energy/tangent derivative checks."""
import json, subprocess, sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from full_p2_p1 import Body,mesh,PARAM,ACTIVATION,constitutive
ROOT=Path(__file__).resolve().parents[1]
def replay(data):
 p=subprocess.run(['node',str(ROOT/'tools/full-p2-p1-replay.mjs')],input=json.dumps(data),text=True,capture_output=True,check=True)
 return json.loads(p.stdout)
def serial(m): return {k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in m.items()}
class MixedTests(unittest.TestCase):
 def test_original_stress_and_true_fixed_pressure_tensor(self):
  F=np.array([[[1.07,.021,0],[-.012,.974,.004],[.006,0,.966]],[[1.25,.002,.004],[0,.8945,0],[.005,0,.8945]]]);p=np.array([270.,-400.])
  P,C,*_=constitutive(F,p,tangent=True)
  original=replay(dict(materialSamples=[dict(F=f.ravel().tolist(),p=float(q)) for f,q in zip(F,p)],material=PARAM,activation=ACTIVATION))
  np.testing.assert_allclose(P,np.array([r['P'] for r in original]).reshape(P.shape),atol=1e-8,rtol=1e-12)
  np.testing.assert_allclose(C,np.array([r['C'] for r in original]).reshape(C.shape),atol=1e-8,rtol=1e-12)
 def test_energy_gradient_condensed_tangent_and_replay(self):
  m=mesh((2,1,1));B=Body(m);x,_,_=B.initial(1.01);r=B.evaluate(x,True)
  rng=np.random.default_rng(492);v=np.zeros(x.size);v[m['free']]=rng.normal(size=len(m['free']));v/=np.linalg.norm(v);v=v.reshape(x.shape)
  h=1e-7;plus=B.evaluate(x+h*v);minus=B.evaluate(x-h*v)
  self.assertLess(abs((plus['energy']-minus['energy'])/(2*h)-r['g']@v.ravel()),1e-6)
  Hfd=(plus['g']-minus['g'])[m['free']]/(2*h);Hv=r['H']@v.ravel()[m['free']]
  self.assertLess(np.linalg.norm(Hfd-Hv)/np.linalg.norm(Hv),1e-6)
  original=replay(dict(mesh=serial(m),positionsM=x.tolist(),pressurePa=r['p'].tolist(),material=PARAM,activation=ACTIVATION,depth=2))
  np.testing.assert_allclose(r['g'],original['gradientN'],atol=2e-9,rtol=1e-10)
  np.testing.assert_allclose(r['b'],original['b'],atol=1e-18,rtol=1e-9)
  self.assertLess(abs(r['energy']-original['energyJ']),1e-12)
  self.assertEqual(original['surface']['crossingPairs'],0)
 def test_exact_patch_and_nonzero_pressure(self):
  B=Body(mesh((2,1,1)));_,x,a=B.initial(1.25);r=B.evaluate(x)
  self.assertLess(r['residual'],1e-8);self.assertLess(r['pointwiseRMS'],1e-12)
  np.testing.assert_allclose(r['p'],a['pressurePa'],atol=1e-8)
  self.assertTrue(np.isfinite(r['g']).all())
 def test_reject_inversion(self):
  B=Body(mesh((1,1,1)));x=B.m['X'].copy();x[:,0]*=-1
  with self.assertRaises(ValueError): B.evaluate(x)
if __name__=='__main__':unittest.main(verbosity=2)
