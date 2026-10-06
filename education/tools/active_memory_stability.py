"""Parameter-free scalar stability calculation, not a muscle constitutive fit."""
import hashlib,json
from pathlib import Path
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/anatomical-arm-v1/review/active-stability-controls/memory-stability-symbolic.json'
if OUT.exists():raise RuntimeError('Preserve symbolic receipt')
s=sp.symbols('s');M,tau=sp.symbols('M tau',positive=True);c,km=sp.symbols('c k_memory',nonnegative=True);kr,ks=sp.symbols('k_relaxed k_series',real=True)
# M*xdd+c*xd+(kr+ks)*x+q=0; tau*qd+q=tau*km*xd.
operator=sp.Matrix([[M*s*s+c*s+kr+ks,1],[-tau*km*s,tau*s+1]])
polynomial=sp.expand(operator.det())
expected=M*tau*s**3+(M+c*tau)*s**2+(c+tau*(kr+ks+km))*s+kr+ks
assert sp.simplify(polynomial-expected)==0
coeff=sp.Poly(polynomial,s).all_coeffs()
margin=sp.expand(coeff[1]*coeff[2]-coeff[0]*coeff[3])
expectedMargin=M*c+M*tau*km+c*c*tau+c*tau*tau*(kr+ks+km)
assert sp.simplify(margin-expectedMargin)==0
K=sp.symbols('K_total',positive=True)
positiveMargin=sp.expand(margin.subs(kr,K-ks))
assert positiveMargin==M*c+M*tau*km+c*c*tau+c*tau*tau*(K+km)
# Marginal undamped/no-memory case factors into one relaxation pole and a neutral pair.
assert sp.factor(polynomial.subs({c:0,km:0}))==(s*tau+1)*(M*s**2+kr+ks)
receipt=dict(result='PASS_PARAMETER_FREE_LINEAR_MEMORY_STABILITY_IDENTITY',
 sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 equations=['M xdd + c xd + (k_relaxed+k_series)x + q = 0','tau qd + q = tau k_memory xd'],
 parameterDomain={'M':'positive mass, kg','tau':'positive time, s','c':'nonnegative viscous coefficient, N s/m','k_memory':'nonnegative Maxwell stiffness, N/m','k_relaxed':'signed relaxed tangent, N/m','k_series':'external end-separation stiffness, N/m'},
 characteristicPolynomial=str(polynomial),routhHurwitzMargin=str(margin),positiveTotalStiffnessMargin=str(positiveMargin),
 conclusions=['If k_relaxed+k_series<0, P(0)<0 and P(s) tends to positive infinity: at least one positive real root for every permitted M,c,tau,k_memory. Positive fast stiffness does not cure this long-time scalar instability.',
 'If k_relaxed+k_series>0 and c>0 or k_memory>0, all cubic coefficients and the Routh-Hurwitz margin are positive: this declared scalar system is asymptotically stable.',
 'If total relaxed stiffness is zero, a zero root remains. With positive total stiffness but c=k_memory=0, oscillatory roots are neutral, not asymptotically stable.'],
 limits=['No numerical physical coefficient selected; no simulated human response.',
 'Single scalar linearized mode only; no multiaxial/internal-variable or nonlinear stability theorem.',
 'Passive Maxwell memory is a thought experiment, not a validated contractile muscle law.',
 'An end-separation spring has zero action on the existing zero-cap interior witnesses.'])
with OUT.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
