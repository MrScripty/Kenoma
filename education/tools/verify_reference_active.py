"""NumPy plane eigenvalues and independent stress differences, no solve."""
import hashlib
import json
from pathlib import Path
import numpy as np

root=Path(__file__).resolve().parents[1]
base=root/'data/anatomical-arm-v1'
path=base/'audit/mechanical-closure-reference-active.json'
out=base/'audit/mechanical-closure-reference-active-recheck.json'
if out.exists():
    raise RuntimeError('Preserve independent replay')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(path.read_text())
for p,h in r['sourceHashes'].items():
    assert sha(root/p)==h,(p,h)

def stress(F,f,a,p,opt,iso):
    J=np.linalg.det(F)
    G=np.linalg.inv(F).T
    d=F@f
    lam=np.linalg.norm(d)
    n=d/lam
    scale=J**(-1/3) if iso else 1
    s=scale*lam/opt
    t=(s-1)/p['activeWidth']
    fl=(1-t*t)**2 if abs(t)<1 else 0
    kpass=p['kf']/p['b']*np.expm1(p['b']*max(lam-1,0))
    passive=p['mu']*J**(-2/3)*(F-np.sum(F*F)/3*G)+p['bulk']*np.log(J)*G+kpass*np.outer(n,f)
    active=a*p['sigma0']*fl*scale*(np.outer(n,f)-(lam/3*G if iso else 0))
    return passive+active

rows=[]
for x in r['rows']:
    F=np.array(x['F']).reshape(3,3)
    f=np.array(x['fibre'])
    m=np.array(x['constrained']['m'])
    u=np.array(x['constrained']['polarization'])
    Q=np.array(x['constrained']['Q']).reshape(3,3)
    g=np.linalg.inv(F).T@m
    assert abs(g@u)<1e-12
    _,_,V=np.linalg.svd(g.reshape(1,3))
    B=V[1:].T
    reduced=B.T@((Q+Q.T)/2)@B
    value=np.linalg.eigvalsh(reduced)[0]
    error=abs(value-x['constrained']['valuePa'])/max(1,abs(value))
    assert error<1e-8
    Qfull=np.array(x['full']['Q']).reshape(3,3)
    assert abs(np.linalg.eigvalsh((Qfull+Qfull.T)/2)[0]-x['full']['valuePa'])/max(1,abs(x['full']['valuePa']))<1e-8
    p=x['material'];a=x['activation'];opt=x['optimalStretch'];iso=x['isochoric'];P=stress(F,f,a,p,opt,iso);D=np.outer(u,m)
    checks=[]
    for probe in x['stressProbes']:
        h=probe['step'];signed=probe['signedOneSidedStep']
        if signed is not None:
            fd=(stress(F+signed*D,f,a,p,opt,iso)-P)/signed@m
        else:
            fd=(stress(F+h*D,f,a,p,opt,iso)-stress(F-h*D,f,a,p,opt,iso))/(2*h)@m
        relative=np.linalg.norm(fd-Q@u)/max(1,np.linalg.norm(Q@u))
        assert relative<1e-4,(x['savedState'],x['normalization'],iso,relative)
        assert max(abs(np.linalg.det(F+h*D)-np.linalg.det(F)),abs(np.linalg.det(F-h*D)-np.linalg.det(F)))<1e-12*max(1,np.linalg.det(F))
        checks.append({'step':h,'derivativeType':probe['derivativeType'],'relativeVectorError':float(relative),'rayleighPa':float(u@fd)})
    rows.append({'savedState':x['savedState'],'normalization':x['normalization'],'isochoric':iso,'constrainedValuePa':float(value),'relativeEigenDifference':float(error),'stressProbes':checks})
result={'result':'PASS_INDEPENDENT_FROZEN_REFERENCE_CONSTRAINT_REPLAY','executionReceiptSHA256':sha(path),'verifierSHA256':sha(Path(__file__)),'rowCount':len(rows),'maximumStressDifferenceRelative':max(p['relativeVectorError'] for x in rows for p in x['stressProbes']),'rows':rows,'limits':['Saved selected points only; no new full-quadrature search, physical equilibrium or state advancement.','Explicit one-sided derivatives at passive cutoff establish no two-sided physical tangent.']}
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
