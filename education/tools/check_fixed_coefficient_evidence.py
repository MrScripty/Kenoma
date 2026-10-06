"""Read-only evidence and protected-scope validation; no simulation/test replay."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repo = root.parent
base = root/'data/anatomical-arm-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bindings = 0
for p in (base/'review').rglob('*manifest.json'):
    r = json.loads(p.read_text())
    for n,h in r.get('sha256',r.get('files',{})).items():
        h = h['sha256'] if isinstance(h,dict) else h
        candidates = [root/n,repo/n,p.parent/n]
        assert any(q.is_file() and sha(q)==h for q in candidates),(p,n)
        bindings += 1
source_bindings = 0
audits = 0
for p in (base/'audit').glob('fixed-coefficient-*.json'):
    r = json.loads(p.read_text())
    assert r['result'].startswith(('PASS_','REJECTED_')),(p,r['result'])
    assert r.get('live') is None, 'Nonterminal physical execution '+str(p)
    for n,h in r.get('sourceHashes',{}).items():
        assert sha(root/n)==h,(p,n)
        source_bindings += 1
    audits += 1
for receipt,renderer in [('current-preconditioner-render-receipt.json','current_preconditioner_figure.py'),('acoustic-render-receipt.json','material_tangent_figure.py'),('full-p2-render-receipt.json','full_p2_curvature_figure.py'),('full-p2-render-receipt-v2.json','full_p2_curvature_figure_v2.py')]:
    r = json.loads((base/'review/fixed-coefficient-controls'/receipt).read_text())
    assert sha(root/'tools'/renderer)==r['rendererSHA256']
    for n,h in {**r['inputs'],**r['outputs']}.items():
        assert sha(root/n)==h,(receipt,n)
changed = subprocess.check_output(['git','diff','--name-only','93c395dccecb949654f8e1a0db7c6b68092a620c'],cwd=repo,text=True).splitlines()
assert all(p.startswith(('education/tools/','education/tests/','education/research/','education/data/anatomical-arm-v1/audit/','education/data/anatomical-arm-v1/review/')) for p in changed)
assert not any(p in changed for p in ['education/book/chapters/00-scope.md','education/tools/contact_trajectory_figure.py'])
subprocess.run(['git','merge-base','--is-ancestor','08f5f3b7fd4b987d3f049c13fdf4338bfaa2928e','HEAD'],cwd=repo,check=True)
print(json.dumps({'result':'PASS_FIXED_COEFFICIENT_EVIDENCE_CLOSEOUT','preservedManifestBindings':bindings,'sourceBoundAuditReceipts':audits,'currentAuditSourceBindings':source_bindings,'newRendererReceiptsChecked':4,'protectedScopeFilesUntouched':True,'productionBookLeanUntouched':True,'requestedAuditCommitIsAncestor':True},indent=2))
