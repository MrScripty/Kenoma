"""Frozen held-cap full P2 spectrum; no optimizer, fitted state or advancement."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.linalg import eigh

root = Path(__file__).resolve().parents[1]
base = root / 'data/anatomical-arm-v1'
path = base / 'audit/fixed-coefficient-full-p2-operator.json'
out = base / 'audit/fixed-coefficient-full-p2-spectrum.json'
if out.exists():
    raise RuntimeError('Preserve frozen spectrum')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
r = json.loads(path.read_text())
assert r['result'] == 'PASS_SOURCE_BOUND_FROZEN_FULL_P2_OPERATOR'
for p, h in r['sourceHashes'].items():
    assert sha(root/p) == h, 'Changed source '+p
for b in r['binaries'].values():
    assert sha(base/b['file']) == b['sha256']
elements = np.array(r['elements'], dtype=int)
local = np.fromfile(base/r['binaries']['elements']['file'], dtype='<f8').reshape(-1,30,30)
ids = (3*elements[:,:,None]+np.arange(3)[None,None,:]).reshape(-1,30)
row_ids = np.broadcast_to(ids[:,:,None], local.shape).reshape(-1)
col_ids = np.broadcast_to(ids[:,None,:], local.shape).reshape(-1)
ndof = 3*r['nodeCount']
H = coo_matrix((local.reshape(-1),(row_ids,col_ids)),shape=(ndof,ndof)).tocsr()
held = np.array(sorted(3*n+d for n in r['heldNodes'] for d in range(3)))
free = np.setdiff1d(np.arange(ndof),held)
assert len(held)==270 and len(free)==1485
symmetry = float(abs(H-H.T).max())
assert symmetry < 1e-6
B = np.zeros((ndof,126))
for n, modes in enumerate(r['nodeModes']):
    for m in modes:
        for d in range(3):
            B[3*n+d,m['base']+d] += m['value']
reduced_free = np.array(r['reducedFreeCoordinates'])
Bf = B[:,reduced_free]
assert abs(Bf[held]).max() < 1e-12
projected = Bf.T @ (H @ Bf)
original = np.fromfile(base/r['binaries']['reduced']['file'],dtype='<f8').reshape(90,90)
projection_error = float(np.max(np.abs(projected-original)))
relative_projection_error = float(np.linalg.norm(projected-original)/np.linalg.norm(original))
assert projection_error < 2e-6 and relative_projection_error < 1e-9
Hfree = H[free][:,free].toarray()
values,vectors = eigh((Hfree+Hfree.T)/2,subset_by_index=[0,5],driver='evr')
direction = np.zeros(ndof)
direction[free] = vectors[:,0]
eigen_residual = float(np.linalg.norm(H @ direction - np.where(np.isin(np.arange(ndof),free),values[0]*direction, (H@direction))))
relative_eigen_residual = float(np.linalg.norm(Hfree@vectors[:,0]-values[0]*vectors[:,0])/max(1,abs(values[0])))
assert relative_eigen_residual < 1e-8
g = np.array(r['independentNodalGradientN']).reshape(-1)
restricted_values = np.linalg.eigvalsh((original+original.T)/2)
result = {'schema':1,'result':'PASS_SOURCE_BOUND_FROZEN_FULL_P2_SPECTRUM',
          'sourceHashes': {str(path.relative_to(root)):sha(path),str(Path(__file__).relative_to(root)):sha(Path(__file__))},
          'binaryHashes':r['binaries'], 'fullComponents':ndof,'heldComponents':len(held),'freeComponents':len(free),
          'maximumGlobalAsymmetryNPerM':symmetry, 'maximumRestrictedHessianDifferenceNPerM':projection_error,
          'relativeRestrictedHessianDifference':relative_projection_error,
          'sixSmallestEigenvaluesNPerM':values.tolist(), 'minimumRestrictedEigenvalueNPerM':float(restricted_values[0]),
          'minimumEigenvalueNPerM':float(values[0]),'relativeEigenResidual':relative_eigen_residual,
          'direction':direction.reshape(-1,3).tolist(), 'directionNorm':float(np.linalg.norm(direction)),
          'maximumHeldDirection':float(abs(direction[held]).max()),'fullGradientDirectionalDerivativeN':float(g@direction),
          'maximumFreeNodalComponentN':float(abs(g[free]).max()),
          'limits':['Frozen accepted restricted state with unbalanced full nodal gradient; no relaxation or physical time advancement.',
                    'Body-only finite P2 held-cap tangent. Local spectrum cannot establish the complete arm/contact dynamic stability.']}
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['direction','sourceHashes','binaryHashes']},indent=2))
