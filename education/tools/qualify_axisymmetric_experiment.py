"""Independent exact-rational geometry bounds and bounded engineering checks.

Observed mesh/quadrature differences are not certified continuum error bounds.
The targets below are provisional engineering criteria for this new specimen.
"""
from pathlib import Path
from fractions import Fraction as F
from math import comb,pi,sqrt
import hashlib,json,sys
import numpy as np
from scipy.linalg import eigvals_banded,cholesky_banded
ROOT=Path(__file__).resolve().parents[1]
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def coefficients(values):
    # Exact conversion of Q2 nodal values at 0,1/2,1 to Bernstein coefficients.
    a=[[values[j*3+i] for j in range(3)] for i in range(3)]
    for j in range(3):a[1][j]=2*a[1][j]-(a[0][j]+a[2][j])/2
    for i in range(3):a[i][1]=2*a[i][1]-(a[i][0]+a[i][2])/2
    return a
def derivative(a,axis):
    m,n=len(a)-1,len(a[0])-1
    if axis==0:return [[m*(a[i+1][j]-a[i][j]) for j in range(n+1)] for i in range(m)]
    return [[n*(a[i][j+1]-a[i][j]) for j in range(n)] for i in range(m+1)]
def product(a,b):
    m,n=len(a)-1,len(a[0])-1;p,q=len(b)-1,len(b[0])-1
    c=[[F(0) for _ in range(n+q+1)] for _ in range(m+p+1)]
    for i in range(m+1):
      for j in range(n+1):
        for k in range(p+1):
          for l in range(q+1):
            c[i+k][j+l]+=a[i][j]*b[k][l]*F(comb(m,i)*comb(p,k),comb(m+p,i+k))*F(comb(n,j)*comb(q,l),comb(n+q,j+l))
    return c
def determinant(r,z):
    a=product(derivative(r,0),derivative(z,1));b=product(derivative(r,1),derivative(z,0))
    return [[a[i][j]-b[i][j] for j in range(len(a[0]))] for i in range(len(a))]
def extrema(a):return min(x for row in a for x in row),max(x for row in a for x in row)
def geometry_bounds(case):
    nodes=case['nodes'];u=case['fullDisplacement'];bounds=[]
    for ids in case['cells']:
        rr=coefficients([F.from_float(nodes[i][0]) for i in ids]);zz=coefficients([F.from_float(nodes[i][1]) for i in ids])
        r=coefficients([F.from_float(nodes[i][0])+F.from_float(u[2*i]) for i in ids])
        z=coefficients([F.from_float(nodes[i][1])+F.from_float(u[2*i+1]) for i in ids])
        lo,hi=extrema(determinant(r,z));reflo,refhi=extrema(determinant(rr,zz))
        assert reflo>0 and lo>0,'Exact Bernstein orientation bound failed'
        if all(x==0 for x in rr[0]):
            assert all(x==0 for x in r[0]),'Radial symmetry axis moved'
            # Remove common reference radial parameter t before bounding r/R.
            r=[[F(2,i)*r[i][j] for j in range(3)] for i in [1,2]]
            rr=[[F(2,i)*rr[i][j] for j in range(3)] for i in [1,2]]
        rlo,rhi=extrema(r);Rlo,Rhi=extrema(rr)
        assert rlo>0 and Rlo>0,'Exact Bernstein radius ratio bound failed'
        lower=lo/refhi*rlo/Rhi;upper=hi/reflo*rhi/Rlo
        assert lower>F(1,1000000),'Stored Q2 map cannot certify runtime determinant guard'
        bounds.append((lower,upper))
    return {'cells':len(bounds),'lower_J_bound':float(min(x[0] for x in bounds)),'upper_J_bound':float(max(x[1] for x in bounds)),
      'method':'Exact Fraction arithmetic on binary input nodes/displacements; tensor Bernstein coefficient bounds, including removed common radial parameter on the axis',
      'scope':'Entire stored Q2 cell map orientation and positive radius/local determinant; not global injectivity, volume accuracy, stress accuracy or floating-point solver equivalence'}

def qualify(path):
    data=json.loads(path.read_text())
    for n,h in data['inputs'].items():assert digest(ROOT/n)==h,'Stale numerical experiment input '+n
    cases={c['key']:c for c in data['cases']}
    for c in cases.values():
        d=c['state']['diagnostics'];assert c['state']['converged'] and c['state']['reachedRequestedPose']
        assert d['scaledMaxFreeResidual']<=1e-10 and d['forceScaleN']>0 and d['energyScaleJ']>0
        assert abs(d['endBalanceN'])/d['forceScaleN']<1e-8
        assert abs(c['integratedReferenceVolumeM3']/c['referenceVolumeM3']-1)<5e-13
    # Reference volume uses radius ratio1.5, hence area ratio2.25.
    expected=pi*.05*.005**2*(1+1.5+1.5**2)/3
    assert abs(cases['16:8:7:0.1:1.5']['referenceVolumeM3']/expected-1)<2e-15
    geometry={key:geometry_bounds(cases[key]) for key in data['uniform']+['16:8:7:-0.1:1.5','16:8:7:0.1:1.5','16:8:7:0:1.5']}
    loaded=[]
    for epsilon in [-.1,.1]:
        fine=cases[f'16:8:7:{epsilon}:1.5'];d=fine['state']['diagnostics'];signal=d['weightedRmsJDefect'];global_signal=abs(d['volumeRatio']-1)
        assert signal>1e-3 and global_signal>1e-3,'Finite volume compliance signal unexpectedly absent'
        comparisons=[x for x in data['spatial'] if x['epsilon']==epsilon]
        for x in comparisons:
            assert x['volumeWeightedRmsJDifference']<.1*signal
            assert x['maxMaterialProbeJDifference']<.1*signal
        primary=next(x for x in comparisons if x['coarse']==f'8:4:5:{epsilon}:1.5')
        assert primary['reactionDifferenceN']<.01*abs(d['rightReactionN'])
        assert primary['energyDifferenceJ']<.01*d['energyJ']
        cut_error=max(abs(p['resultantN']-d['rightReactionN']) for p in fine['cuts'])/d['forceScaleN']
        assert cut_error<1e-3,'Fine reference-cut force variation exceeds provisional target'
        side=max(sqrt(sum(t*t for t in p['nominalTractionPa'])) for p in fine['sideTractions'])/1500
        assert side<1e-3,'Fine full PN side traction exceeds provisional target at declared noncorner probes'
        loaded.append({'epsilon':epsilon,'reference':fine['key'],'finite_volume_signal_rms':signal,'global_volume_change':d['volumeRatio']-1,'successive_8x4_to_16x8':primary,'scaled_cut_force_variation':cut_error,'max_declared_noncorner_side_traction_over_mu':side,
          'corner_limit':'Corner and near-corner gradients are recorded separately. Changing quadrature-point extrema do not establish converged pointwise corner stress/J or global stability.'})
    quadrature=[]
    for record in data['quadrature']:
        epsilon=record['epsilon'];fine=cases[f'16:8:7:{epsilon}:1.5'];signal=fine['state']['diagnostics']['weightedRmsJDefect']
        by={r['order']:r for r in record['reevaluations']}
        assert by[7]['scaledMaxFreeResidual']<1e-8 and by[9]['scaledMaxFreeResidual']<1e-8
        assert abs(by[7]['volumeRatio']-by[9]['volumeRatio'])<.01*signal
        assert abs(by[7]['energyJ']-by[9]['energyJ'])<1e-8*fine['state']['diagnostics']['energyScaleJ']
        c3=cases[f'16:8:3:{epsilon}:1.5'];c7=fine
        probe_difference=max(abs(a['J']-b['J']) for a,b in zip(c3['probes'],c7['probes']))
        assert probe_difference<.01*signal
        quadrature.append({'epsilon':epsilon,'independent_3_to_7_solution_probe_J_difference':probe_difference,'reevaluations':record['reevaluations'],'note':'Order3 reintegration of an order5 stationary state has an observable residual; order7/9 agreement is checked independently.'})
    for row in data['reactionDerivative']:
        assert row['plusConverged'] and row['minusConverged']
        assert abs(row['energyDerivativeN']-row['assembledReactionN'])<1e-8*.11780972450961726
    render=[]
    for epsilon in [0,-.1,.1]:
        rows=[x for x in data['rendering'] if x['epsilon']==epsilon];best=next(x for x in rows if x['azimuth']==256 and x['axialSubdivisions']==8)
        relative_error=abs(best['actualFloat32VolumeM3']-best['integratedVolumeM3'])/best['exactReferenceVolumeM3']
        if epsilon==0:assert relative_error<2e-4
        else:
            signal=abs(cases[f'16:8:7:{epsilon}:1.5']['state']['diagnostics']['volumeRatio']-1)
            assert relative_error<.1*signal
        coarse=next(x for x in rows if x['azimuth']==64 and x['axialSubdivisions']==8)
        assert relative_error<abs(coarse['actualFloat32VolumeM3']-coarse['integratedVolumeM3'])/coarse['exactReferenceVolumeM3']/10
        render.append({'epsilon':epsilon,'finest_uploaded_Float32_volume_error_over_reference':relative_error,'finest':best,'note':'Actual finite polygon error remains present; no postsolve or render volume correction.'})
    conditioning=[]
    for row in data['conditioning']:
        n,w=row['n'],row['width'];H=np.array(row['originalBandTangent']).reshape(n,w+1);scale=np.sqrt(H[:,0]);ab=np.zeros((w+1,n))
        for j in range(n):
            for k in range(min(w,n-1-j)+1):ab[k,j]=H[j+k,k]/(scale[j+k]*scale[j])
        cholesky_banded(ab,lower=True,check_finite=True)
        smallest=float(eigvals_banded(ab,lower=True,select='i',select_range=(0,0))[0]);largest=float(eigvals_banded(ab,lower=True,select='i',select_range=(n-1,n-1))[0])
        assert smallest>0 and largest>smallest
        conditioning.append({'epsilon':row['epsilon'],'free_dofs':n,'original_tangent_independent_SciPy_scaled_Cholesky':'PASS','jacobi_scaled_smallest_eigenvalue':smallest,'jacobi_scaled_largest_eigenvalue':largest,'jacobi_scaled_spectral_condition_number':largest/smallest,'scope':'Numerical original constrained discrete tangent at this state; no continuum or nonaxisymmetric stability theorem'})
    return {'status':'PASS_BOUNDED_ENGINEERING_CHECKS','experiment_sha256':digest(path),'source_input_sha256':data['inputs'],'checker_sha256':digest(Path(__file__)),'reference_volume_m3':expected,'radius_ratio':1.5,'area_ratio':2.25,'material_ratio_K_over_mu':20,'loaded':loaded,'quadrature':quadrature,'reaction_energy_derivatives':data['reactionDerivative'],'rendering':render,'geometry_admissibility':geometry,'conditioning':conditioning,'targets':'Provisional new-specimen engineering targets, supported here by observed independent checks. Mesh/quadrature differences are not rigorous continuum error estimates. Existing lesson acceptance limits are unchanged.','zero_load_normalization':'Force scale mu*pi*a0² and energy scale mu*V0 remain positive at zero reaction; no division by zero load.','scope':'Uniform and one connected passive taper at zero/±10%; finite compliance, all admissible Q2 free force components, no mixed pressure, exact incompressibility, active muscle, anatomy, unrestricted stability or release qualification'}

if __name__=='__main__':
    path=Path(sys.argv[1]);out=Path(sys.argv[2]);out.unlink(missing_ok=True)
    record=qualify(path);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n')
    print(record['status']);print(json.dumps({'loaded':record['loaded'],'conditioning':record['conditioning'],'geometry':record['geometry_admissibility']},indent=2))
