"""Independent symbolic derivatives and high-precision roots; no anatomy imports."""
import argparse,json,subprocess,pathlib
import sympy as s
import mpmath as mp

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=pathlib.Path,required=True);a=parser.parse_args();assert not a.out.exists()
 x,y,z,mu,K,V0=s.symbols('x y z mu K V0',positive=True);J=x*y*z;I=x*x+y*y+z*z
 U=V0*(mu/s.Integer(2)*(J**(-s.Rational(2,3))*I-3)+K/s.Integer(2)*(J-1)**2)
 checks=[]
 for l in [x,y,z]:
  P=mu*J**(-s.Rational(2,3))*(l-I/(3*l))+K*(J-1)*J/l
  assert s.simplify(s.diff(U,l)/V0-P)==0;checks.append('exact energy derivative for '+str(l))
 b,c,S=s.symbols('b c S',positive=True)
 P=mu/s.Integer(3)*c**(-s.Rational(2,3))*(2*b**s.Rational(1,3)-S*b**(-s.Rational(5,3)))+K*c*(c*b-1)
 derivative=mu/s.Integer(9)*c**(-s.Rational(2,3))*(2*b**(-s.Rational(2,3))+5*S*b**(-s.Rational(8,3)))+K*c*c
 assert s.simplify(s.diff(P,b)-derivative)==0;checks.append('positive free-stress derivative for mu,c,S,b>0 and K>=0')
 here=pathlib.Path(__file__).resolve().parent;url=(here/'model.mjs').as_uri()
 script="import {specimen,DEFAULTS} from "+json.dumps(url)+";let rows=[];for(const direction of ['Y','Z'])for(const axialStretch of [.8,1,1.2])for(const heightStretch of [.5,.8,1])for(const bulk of [0,50000,250000])rows.push(specimen({...DEFAULTS,direction,axialStretch,heightStretch,bulk}));console.log(JSON.stringify(rows));"
 rows=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],text=True));mp.mp.dps=70;max_error=0
 for row in rows:
  p=row['parameters'];xx,hh,kk,mm=[mp.mpf(str(p[k]))for k in ['axialStretch','heightStretch','bulk','mu']];cc=xx*hh;ss=xx**2+hh**2
  def residual(bb):return mm/3*cc**(-mp.mpf(2)/3)*(2*bb**(mp.mpf(1)/3)-ss*bb**(-mp.mpf(5)/3))+kk*cc*(cc*bb-1)
  root=mp.findroot(residual,(mp.mpf('.1'),mp.mpf('4')),solver='ridder',tol=mp.mpf('1e-55'),maxsteps=200)
  got=mp.mpf(str(row['state']['stretches'][row['freeAxis']]));error=abs(root-got);max_error=max(max_error,float(error));assert error<mp.mpf('2e-14')
 a.out.write_text(json.dumps({'result':'PASS_INDEPENDENT_SYMBOLIC_AND_HIGH_PRECISION_REFERENCE','symbolicChecks':checks,'referenceStates':len(rows),'referenceMethod':'70-digit Ridders root of independently rearranged scalar stress','maximumStretchDifference':max_error,'scope':'same authored reduced law; no biological validation or unrestricted stability proof'},indent=2)+'\n')
 print(a.out.read_text())
if __name__=='__main__':main()
