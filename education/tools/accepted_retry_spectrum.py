"""Inspect the reduced operator at the independently accepted retry endpoint."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.linalg import eigh
root=Path(__file__).resolve().parents[1];out=root/'data/anatomical-arm-v1/review/dense-release-rejection';target=out/'accepted-retry-spectrum.json';assert not target.exists(),'Preserve spectrum'
meta=json.loads((out/'accepted-retry-hessian.json').read_text());matrix=out/'accepted-retry-hessian.f64';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(matrix)==meta['matrixSHA256'];n=meta['ndof'];H=np.fromfile(matrix,dtype='<f8').reshape(n,n);sym=float(np.max(np.abs(H-H.T)));assert sym/max(float(np.max(np.abs(H))),1)<1e-12;H=(H+H.T)/2;lam=eigh(H,eigvals_only=True,driver='evd');scale=np.sqrt(np.maximum(np.abs(np.diag(H)),1e-12));scaled=eigh(H/scale[:,None]/scale[None,:],eigvals_only=True,driver='evd')
receipt={'result':'PASS_FROZEN_ACCEPTED_RETRY_SPECTRUM','minimumEigenvalueNPerM':float(lam[0]),'maximumEigenvalueNPerM':float(lam[-1]),'negativeEigenvaluesBelowMinus1eMinus6':int(np.sum(lam<-1e-6)),'scaledMinimumEigenvalue':float(scaled[0]),'scaledMaximumEigenvalue':float(scaled[-1]),'sourceHashes':{'tools/accepted_retry_spectrum.py':sha(Path(__file__)),'accepted-retry-hessian.json':sha(out/'accepted-retry-hessian.json'),'accepted-retry-hessian.f64':sha(matrix)},'scope':'Frozen reduced objective at one endpoint; no global/full-nodal/physiological stability or convergence certification.'};target.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
