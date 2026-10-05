"""Analyze frozen reduced operators; no optimizer or acceptance change."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.linalg import eigh,solve

root=Path(__file__).resolve().parents[1]
out=root/'data/anatomical-arm-v1/review/dense-release-rejection'
target=out/'spectrum.json'
assert not target.exists(),'Preserve existing spectrum'
frozen=json.loads((out/'frozen.json').read_text());n=frozen['ndof'];j=frozen['jointIndex']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={'tools/dense_rejection_spectrum.py':sha(Path(__file__)),'frozen.json':sha(out/'frozen.json')};results={}
for name in ['rejected-native','coarse-native']:
    hp=out/(name+'-hessian.f64');gp=out/(name+'-gradient.f64')
    H=np.fromfile(hp,dtype='<f8').reshape(n,n);g=np.fromfile(gp,dtype='<f8')
    assert np.isfinite(H).all() and np.isfinite(g).all()
    symmetry=float(np.max(np.abs(H-H.T)));relative=symmetry/max(float(np.max(np.abs(H))),1)
    assert relative<1e-12
    H=(H+H.T)/2
    lam,V=eigh(H,driver='evd');scale=np.sqrt(np.maximum(np.abs(np.diag(H)),1e-12))
    normalized=H/scale[:,None]/scale[None,:];scaled=eigh(normalized,eigvals_only=True,driver='evd')
    residual=float(np.max(np.abs(H@V-V*lam)))/max(float(np.max(np.abs(H))),1)
    assert residual<1e-12
    modes=[]
    for k in range(3):
        v=V[:,k]
        modes.append({'eigenvalueNPerM':float(lam[k]),'jointFraction':float(v[j]**2),'bodyFractions':{b['id']:float(np.sum(v[b['offset']:b['offset']+b['count']]**2)) for b in frozen['bodyOffsets']}})
    shifted=[]
    for shift in [.001,1.,1000.,10000.]:
        A=H+shift*np.eye(n);d=solve(A,-g,assume_a='sym');linear=float(np.max(np.abs(A@d+g)))
        shifted.append({'shiftNPerM':shift,'minimumShiftedEigenvalueNPerM':float(lam[0]+shift),'positiveDefinite':bool(lam[0]+shift>0),'maximumCoordinateDirectionM':float(np.max(np.abs(np.delete(d,j)))),'jointDirectionRad':float(d[j]/.1),'gradientDotDirectionJ':float(g@d),'linearResidualN':linear,'unshiftedNewtonResidualN':float(np.max(np.abs(H@d+g)))})
    results[name]={'symmetryErrorNPerM':symmetry,'relativeSymmetryError':relative,'relativeEigenResidual':residual,'minimumEigenvalueNPerM':float(lam[0]),'maximumEigenvalueNPerM':float(lam[-1]),'negativeEigenvaluesBelowMinus1eMinus6':int(np.sum(lam<-1e-6)),'scaledMinimumEigenvalue':float(scaled[0]),'scaledMaximumEigenvalue':float(scaled[-1]),'scaledNegativeEigenvaluesBelowMinus1eMinus10':int(np.sum(scaled<-1e-10)),'minimumModes':modes,'frozenShiftedDirections':shifted}
    inputs[hp.name]=sha(hp);inputs[gp.name]=sha(gp)
receipt={'schema':1,'result':'PASS_FROZEN_REDUCED_SPECTRUM','numpy':np.__version__,'sourceHashes':inputs,'rows':results,'limits':['Objective Hessians in the existing 460-coordinate space; no full-nodal/mesh stability certification.','Negative reduced curvature can occur away from a local minimum; it is not by itself proof of infeasible contact or physiological buckling.','Shifted directions are frozen algebraic diagnostics, not line searches, accepted states or new solver regularization.','Native coarse and rejected fine operators have different physical poses/history; identical-pose h dependence is recorded separately in frozen.json.']}
target.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
