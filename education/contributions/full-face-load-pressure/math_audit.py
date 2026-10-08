"""Independent high precision equations from the unchanged energy; no anatomy."""
import argparse,json,pathlib,subprocess
import mpmath as mp
import sympy as sp
mp.mp.dps=70
xx,hh,bb,mm,kk=sp.symbols('x h b mu K',positive=True)
JJ=xx*hh*bb;WW=mm/2*(JJ**(-sp.Rational(2,3))*(xx**2+hh**2+bb**2)-3)+kk/2*(JJ-1)**2
derived=sp.lambdify((xx,hh,bb,mm,kk),(sp.diff(WW,hh),sp.diff(WW,bb)),'mpmath')
parser=argparse.ArgumentParser();parser.add_argument('--model',type=pathlib.Path,required=True);parser.add_argument('--out',type=pathlib.Path,required=True);a=parser.parse_args()
program="""import {solveComparison,evaluateAt,DEFAULTS} from MODEL;
const rows=[],excluded=[];
for(const direction of ['Y','Z'])for(const axialStretch of [.8,1,1.2])for(const bulk of [0,50000,250000])for(const mu of [500,1500,5000])for(const breadthFactor of [.5,1,2])for(const h of [.55,.65]){
const p={...DEFAULTS,direction,axialStretch,bulk,mu,breadthFactor},known=evaluateAt(p,h);
for(const mode of ['force','pressure']){const key=mode==='force'?'forceN':'pressurePa',target=mode==='force'?known.compressionResultantN:known.contactPressurePa;if(target<0||target>(mode==='force'?100:100000)){excluded.push({direction,axialStretch,bulk,mu,breadthFactor,h,mode,target});continue;}rows.push(solveComparison({...p,mode,[key]:target}));}}
console.log(JSON.stringify({rows,excluded}));""".replace('MODEL',json.dumps(a.model.resolve().as_uri()))
generated=json.loads(subprocess.check_output(['node','--input-type=module','-e',program],text=True));rows=generated['rows'];maximum=mp.mpf(0);energy_error=mp.mpf(0);stress_error=mp.mpf(0)
for row in rows:
 p=row['parameters'];s=row['state'];x=mp.mpf(str(p['axialStretch']));mu=mp.mpf(p['mu']);K=mp.mpf(p['bulk']);loaded=row['loadedAxis'];free=row['freeAxis'];dims=list(map(lambda v:mp.mpf(str(v)),s['referenceDimensionsM']));V0=mp.fprod(dims);A0=mp.fprod(v for i,v in enumerate(dims)if i!=loaded);target=mp.mpf(str(row['solve']['target']))
 def energy(h,b):
  J=x*h*b;I1=x*x+h*h+b*b
  return V0*(mu/2*(J**(-mp.mpf(2)/3)*I1-3)+K/2*(J-1)**2)
 def equations(h,b):
  Pload,Pfree=derived(x,h,b,mu,K);C=-Pload*A0
  return Pfree/(mu+K),((C if p['mode']=='force'else C/(A0*x*b))-target)/max(mp.mpf(1),abs(target))
 hs=mp.mpf(str(s['stretches'][loaded]));bs=mp.mpf(str(s['stretches'][free]))
 try:h,b=mp.findroot(equations,(hs*mp.mpf('.99'),bs*mp.mpf('1.01')),tol=mp.mpf('1e-55'),maxsteps=30)
 except ValueError:
  print(json.dumps({'failedParameters':p,'target':str(target),'initialEquationResiduals':list(map(str,equations(hs,bs)))}),flush=True);raise
 assert mp.mpf('.5')<=h<=1 and b>0
 maximum=max(maximum,abs(h-hs),abs(b-bs));energy_error=max(energy_error,abs(energy(hs,bs)-mp.mpf(str(s['energyJ']))))
 stress_error=max(stress_error,abs(mp.diff(lambda z:energy(z,bs),hs)/V0-mp.mpf(str(s['nominalStressPa'][loaded]))))
 assert row['solve']['converged'] and abs(s['freeResidualPa'])<=1e-5
 assert abs(s['volumeDisagreement'])<1e-12
assert maximum<mp.mpf('1e-11')and energy_error<mp.mpf('1e-12')and stress_error<mp.mpf('1e-8')
result={'result':'PASS_INDEPENDENT_ENERGY_DERIVED_INVERSE_ROOTS','states':len(rows),'excludedOutsideDeclaredTargetDomain':generated['excluded'],'precisionDecimalDigits':70,'maximumStretchDifference':float(maximum),'maximumEnergyDifferenceJ':float(energy_error),'maximumLoadedStressDifferencePa':float(stress_error),'method':'Independent SymPy differentiation of stored energy and 70-digit mpmath two-variable solve; JS used only for target/initial perturbation, no source stress/root reuse','scope':'bounded passive full-face fixed force/current pressure; no biological or unrestricted stability validation'}
a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
