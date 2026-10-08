"""Own six symbolic identities and exactly 24 independent rational state audits.

No optimizer, simulation, fit, download or dependency installation. SymPy
results are separate from Lean kernel status and JavaScript behavior.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,json,subprocess
import sympy as s
from paths import HERE,checked_output,source_hashes

def run(output,model=None):
    output=checked_output(output)
    K1,K2,CL,CR,CRp=s.symbols('K1 K2 CL CR CRp',positive=True)
    d,u,v=s.symbols('d u v',real=True)
    E,A,L,G,As,h,z=s.symbols('E A L G As h z',nonzero=True)
    us=CR*d/(K1+CR);vs=K2*d/(K2+CL)
    ke=K1*CR/(K1+CR)+K2*CL/(K2+CL)
    U=K1*u*u/2+K2*(d-v)**2/2+CL*v*v/2+CR*(d-u)**2/2
    identities={
      'material_resultants':[E*A/L*z-A*E*z/L,G*As/h*z-As*G*z/h],
      'stationary_solution':[K1*us-CR*(d-us),K2*(d-vs)-CL*vs],
      'matched_end_resultants':[K1*us+CL*vs-ke*d,K2*(d-vs)+CR*(d-us)-ke*d],
      'energy_completion_unique_minimum':[U-ke*d*d/2-(K1+CR)*(u-us)**2/2-(K2+CL)*(v-vs)**2/2],
      'transfer_stiffness_bounds':[K1+K2-ke-K1*K1/(K1+CR)-K2*K2/(K2+CL)],
      'interface_stiffness_difference':[ke.subs(CR,CRp)-ke-K1*K1*(CRp-CR)/((K1+CRp)*(K1+CR))],
    }
    symbolic={name:all(s.factor(expr)==0 for expr in rows) for name,rows in identities.items()}
    if not all(symbolic.values()):raise RuntimeError('Symbolic identity failure')
    # Independent differentiation is numerical/symbolic evidence, not a Lean claim.
    gradient=[s.factor(s.diff(U,u)-(K1*u-CR*(d-u))),s.factor(s.diff(U,v)-(CL*v-K2*(d-v)))]
    if gradient!=[0,0]:raise RuntimeError('Independent potential gradient failure')
    cases=[dict(K1=k1,K2=k2,CL=cl,CR=cr,delta=delta*1e-6)
           for delta in [0,1,2] for k1,k2 in [(100,100),(50,200)]
           for cl,cr in [(0,0),(100,100),(0,100),(25,400)]]
    model=(model or HERE/'model.mjs').resolve()
    actual=json.loads(subprocess.check_output(['node','--input-type=module','-e',
      "import {equilibrium} from "+json.dumps(model.as_uri())+";const cases="+json.dumps(cases)+";console.log(JSON.stringify(cases.map(equilibrium)));"],cwd=HERE,text=True))
    rows=[]
    for p,r in zip(cases,actual):
        k1,k2,cl,cr=(F(p[x]) for x in ['K1','K2','CL','CR']);delta=F(str(p['delta']))
        # Reciprocal-compliance branch forces use a route distinct from the JS displacement formulas.
        qr=F(0) if cr==0 else delta/(1/k1+1/cr)
        ql=F(0) if cl==0 else delta/(1/k2+1/cl)
        ref={'u':qr/k1,'v':delta-ql/k2,'upperForceN':qr,'lowerForceN':ql,
             'leftExchangeN':ql,'rightExchangeN':qr,'leftPullN':qr+ql,'rightPullN':qr+ql,
             'externalLeftForceN':-qr-ql,'externalRightForceN':qr+ql,
             'energyJ':(qr+ql)*delta/2}
        errors={key:abs(r[key]-float(value)) for key,value in ref.items()}
        for key,value in ref.items():
            if errors[key]>1e-12*max(1e-9,abs(float(value))):
                raise RuntimeError(f'Independent rational case failed: {p} {key}')
        rows.append({'input':p,'rational_reference':{k:str(v) for k,v in ref.items()},'absolute_errors':errors})
    assert len(rows)==24
    receipt={'status':'passed','symbolic_identities':symbolic,'symbolic_identity_count':6,
      'independent_potential_gradient':True,'closed_form_cases':rows,'case_count':24,
      'source_sha256':source_hashes(),'audited_model':str(model),'audited_model_sha256':__import__('hashlib').sha256(model.read_bytes()).hexdigest(),'performs_lean_compilation':False,
      'scope':'Original discrete linear guided model; no continuum equilibrium, measured tissue, calibration or trajectory qualification.'}
    (output/'algebra-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Six symbolic identities and exactly 24 rational closed-form state comparisons passed; no Lean status asserted.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--model',type=Path,help='Read-only alternate actual model for explicit damage tests')
    a=p.parse_args();run(a.output,a.model)
