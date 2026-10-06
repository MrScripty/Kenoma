"""Independent NumPy eigenvalues and reimplemented stress differences; no solve."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
base = root / 'data/anatomical-arm-v1'
stem = 'fixed-coefficient-loaded-acoustic' if '--loaded' in sys.argv else 'fixed-coefficient-acoustic-audit'
input_path = base / ('audit/' + stem + '.json')
out = base / ('audit/' + stem + '-recheck.json')
if out.exists():
    raise RuntimeError('Preserve existing independent replay')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
run = json.loads(input_path.read_text())
for p, h in run['sourceHashes'].items():
    assert sha(root / p) == h, 'Changed source ' + p

def stress(F, f, a, p):
    J = np.linalg.det(F)
    assert J > 1e-6
    G = np.linalg.inv(F).T
    d = F @ f
    lam = np.linalg.norm(d)
    n = d / lam
    t = (lam - 1) / p['activeWidth']
    fl = (1 - t*t)**2 if abs(t) < 1 else 0
    kpass = p['kf'] / p['b'] * np.expm1(p['b'] * max(lam - 1, 0))
    return (p['mu'] * J**(-2/3) * (F - np.sum(F*F)/3 * G)
            + p['bulk'] * np.log(J) * G
            + (kpass + a*p['sigma0']*fl) * np.outer(n, f))

rows = []
for row in run['rows']:
    w = row['worst']
    F, f, m, u, Q = [np.array(w[k]) for k in ['F', 'fibre', 'm', 'polarization', 'Q']]
    F, Q = F.reshape(3, 3), Q.reshape(3, 3)
    assert abs(np.linalg.norm(m)-1) < 1e-12
    assert abs(np.linalg.norm(u)-1) < 1e-12
    values, vectors = np.linalg.eigh((Q + Q.T)/2)
    eigen_error = abs(values[0]-w['minimumEigenvaluePa']) / max(1, abs(values[0]))
    assert eigen_error < 1e-9
    probes = []
    for h in [1e-6, 5e-7]:
        fd = np.column_stack([
            ((stress(F+h*np.outer(e, m), f, row['activation'], row['material'])
              - stress(F-h*np.outer(e, m), f, row['activation'], row['material'])) / (2*h)) @ m
            for e in np.eye(3)])
        error = np.linalg.norm(fd-Q) / max(1, np.linalg.norm(Q))
        assert error < 1e-4
        probes.append({'step': h, 'relativeFullAcousticMatrixError': float(error),
                       'minimumSymmetricFiniteDifferenceEigenvaluePa': float(np.linalg.eigvalsh((fd+fd.T)/2)[0])})
    assert abs(sum(w['rayleighPartsPa'].values())-w['minimumEigenvaluePa']) / max(1, abs(values[0])) < 1e-9
    rows.append({'name': row['name'], 'minimumEigenvaluePa': float(values[0]), 'relativeEigenvalueDifference': float(eigen_error), 'stressProbes': probes})
result = {'result': 'PASS_INDEPENDENT_FROZEN_ACOUSTIC_REPLAY', 'executionReceiptSHA256': sha(input_path),
          'verifierSHA256': sha(Path(__file__)), 'rows': rows,
          'limits': ['Independent stress and NumPy replay at saved worst points, not a repeated complete directional scan.',
                     'Finite tested directions and snapshots cannot establish strong ellipticity everywhere, global stability or envelope credibility.']}
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
