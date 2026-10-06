"""Independent symbolic energy derivatives and high-precision cylinder oracle."""
from pathlib import Path
import hashlib,json,subprocess,sys
import mpmath as mp
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
mp.mp.dps=60
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def qualify():
    inputs={n:digest(ROOT/n) for n in ['web/axisymmetric-material.mjs','tools/qualify_axisymmetric_material.py']}
    vectors=[[1.07,.031,-.021,.965,1.01],[.92,-.06,.04,1.06,.98],[1,0,0,1,1]]
    program="import {axisymmetricMaterial as m,uniformCylinderOracle as o} from './web/axisymmetric-material.mjs';console.log(JSON.stringify({material:"+json.dumps(vectors)+".map(v=>({v,...m(v)})),cylinders:[.9,1,1.1].map(x=>o(x))}));"
    actual=json.loads(subprocess.check_output(['node','--input-type=module','-e',program],cwd=ROOT,text=True))
    a,b,c,d,h=sp.symbols('a b c d h',real=True);v=[a,b,c,d,h]
    J=h*(a*d-b*c);I=sum(x*x for x in v)
    W=sp.Rational(1500,2)*(J**sp.Rational(-2,3)*I-3)+sp.Rational(30000,2)*sp.log(J)**2
    wf=sp.lambdify(v,W,'mpmath');gf=sp.lambdify(v,[sp.diff(W,x) for x in v],'mpmath')
    hf=sp.lambdify(v,[[sp.diff(W,x,y) for y in v] for x in v],'mpmath')
    errors=[]
    def check(x,y,label,absolute,relative=2e-12):
        error=abs(mp.mpf(x)-y);bound=absolute+relative*abs(y)
        if error>bound:raise AssertionError(f'{label}: {error} > {bound}')
        return float(error)
    for row in actual['material']:
        vv=[mp.mpf(str(x)) for x in row['v']];expected_g=gf(*vv);expected_h=hf(*vv)
        errors.append({'v':row['v'],'energy_absolute_error_pa':check(row['energyPa'],wf(*vv),'independent symbolic energy',1e-10),
          'gradient_max_absolute_error_pa':max(check(x,y,'independent symbolic gradient',2e-9) for x,y in zip(row['gradient'],expected_g)),
          'tangent_max_absolute_error_pa':max(check(row['tangent'][i][j],expected_h[i][j],'independent symbolic tangent',2e-8) for i in range(5) for j in range(5))})
    def scalar(lam,side):
        j=lam*side**2
        return mp.mpf(750)*(j**(-mp.mpf(2)/3)*(lam**2+2*side**2)-3)+mp.mpf(15000)*mp.log(j)**2
    cylinders=[]
    for row in actual['cylinders']:
        lam=mp.mpf(str(row['lambda']));guess=1/mp.sqrt(lam)
        side=mp.findroot(lambda x:mp.diff(lambda y:scalar(lam,y),x),(guess*mp.mpf('.98'),guess*mp.mpf('1.02')))
        j=lam*side**2;nominal=mp.diff(lambda x:scalar(x,side),lam)
        check(row['b'],side,'independent free-lateral energy root',2e-14)
        check(row['J'],j,'independent homogeneous finite volume',3e-14)
        check(row['nominalAxialPa'],nominal,'independent axial energy derivative',2e-9)
        check(row['energyDensityPa'],scalar(lam,side),'independent homogeneous energy',2e-10)
        lateral_derivative=mp.diff(lambda x:scalar(lam,x),side)
        curvature=mp.diff(lambda x:scalar(lam,x),side,2)
        assert abs(lateral_derivative)<mp.mpf('1e-45') and curvature>0
        cylinders.append({'lambda':float(lam),'side_stretch':float(side),'J':float(j),'volume_change':float(j-1),'nominal_axial_pa':float(nominal),'energy_density_pa':float(scalar(lam,side)),'lateral_energy_derivative_pa':float(lateral_derivative),'lateral_scalar_curvature_pa':float(curvature)})
    assert all(digest(ROOT/n)==value for n,value in inputs.items())
    return {'status':'PASS','method':'Symbolic differentiation of the five-component energy, independently coded 60-digit free-lateral root of restricted energy derivative; no reused production gradient or log-root equation','material':errors,'cylinders':cylinders,'input_sha256':inputs,'scope':'Local passive derivatives and homogeneous cylinder only; no assembled equilibrium, spatial refinement, stability, renderer or anatomy qualification'}
if __name__=='__main__':
    record=qualify();out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
