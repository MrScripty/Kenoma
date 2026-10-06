"""Symbolic dimensional/series identities only. No loading/release execution."""
import hashlib
import json
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/dimensional-contractile-mapping'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
F0, beta, B, Ns, dps, sarc = sp.symbols('F0 beta B Ns dps sarc', positive=True)
gamma = 2*Ns*dps
Lref = Ns*sarc
kfast = F0*B/(beta*gamma)
assert sp.simplify(Lref/gamma - sarc/(2*dps)) == 0
assert sp.simplify(kfast * Lref/F0 - B*sarc/(2*beta*dps)) == 0
H, klink, Q = sp.symbols('H klink Q', positive=True)
Tcb = H*klink*dps*Q
assert sp.simplify(Tcb.subs(H,F0/(beta*klink*dps)) - F0*Q/beta) == 0
# Continuum stress units/convention: aligned homogeneous fascicle, no pennation.
Aref, lam, J = sp.symbols('Aref lam J', positive=True)
Acurrent = Aref*J/lam
nominal = Tcb/Aref
cauchy = Tcb/Acurrent
assert sp.simplify(cauchy - lam*nominal/J) == 0
# Series circuit with CE+parallel in parallel, positive series/parallel tangent.
Ks, Kp, vtotal, qkin, vce = sp.symbols('Ks Kp vtotal qkin vce', real=True)
force_rate_ce = F0/beta*(qkin+B*vce/gamma) + Kp*vce
force_rate_se = Ks*(vtotal-vce)
solution = sp.solve(force_rate_se-force_rate_ce,vce)[0]
expected = (Ks*vtotal-F0*qkin/beta)/(Ks+Kp+kfast)
assert sp.simplify(solution-expected) == 0
# Frozen kinetic reaction qkin=0 gives series-limited fast tangent.
kcombined = sp.simplify((force_rate_se.subs(vce,solution)/vtotal).subs(qkin,0))
assert sp.simplify(kcombined-Ks*(Kp+kfast)/(Ks+Kp+kfast)) == 0
# Moment conversion for code's uncentered elongation coordinate y=(1+x)*dps.
Q0, Q1centered = sp.symbols('Q0 Q1centered', real=True)
Q1absolute = dps*(Q0+Q1centered)
assert sp.simplify(H*klink*Q1absolute-H*klink*dps*(Q0+Q1centered)) == 0
record = dict(result='PASS_SYMBOLIC_DIMENSIONAL_AND_SERIES_BRIDGE',sourceSHA256=sha(Path(__file__)),
              derived=dict(gammaLength=str(gamma),lengthReference=str(Lref),relativeMotionToLinkStrain=str(sp.simplify(Lref/gamma)),
                           fastContractileTangent=str(kfast),cauchyFromNominal=str(sp.simplify(cauchy/nominal)),
                           contractileVelocity=str(solution),seriesLimitedFastTangent=str(kcombined)),
              sourceAssumptionIllustration=dict(dpsM=1e-8,sarcomereReferenceM=2.6e-6,
                    relativeMotionToLinkStrain=130.,NsReportedMean=306,NsReportedSD=78,
                    gammaAtReportedMeanM=6.12e-6,gammaSDPropagationM=1.56e-6,
                    meanPlusOrMinusSDIsNotRangeOrConfidenceInterval=True),
              limitations=['Symbolic identities conditional on aligned uniform fascicle/serial kinematics and independent calibration.',
                           'No heads density, force scale, area, human overlap, tendon law or stabilizing parameter selected.',
                           'No anatomical solve, kinetic evolution or controlled loading/release experiment executed.',
                           'The required original table visual check remains a separate execution gate.'])
OUT.mkdir(parents=True,exist_ok=True)
p=OUT/'symbolic-bridge.json'
if p.exists():
    raise RuntimeError('refusing to overwrite symbolic evidence')
p.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
