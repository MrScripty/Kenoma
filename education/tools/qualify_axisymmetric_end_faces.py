"""Independent oracle and unchanged physical criteria for repaired endpoint cases."""
from pathlib import Path
import argparse,hashlib,json,math
from qualify_axisymmetric_experiment import geometry_bounds
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b,absolute,relative=0):assert abs(a-b)<=absolute+relative*abs(b),(a,b)
def qualify(datafile,oraclefile,oldfile,out):
    data=json.loads(datafile.read_text());oracle=json.loads(oraclefile.read_text());old=json.loads(oldfile.read_text());assert oracle['status']=='PASS'
    assert all(sha(ROOT/n)==h for n,h in data['inputs'].items()) and all(sha(ROOT/n)==h for n,h in oracle['input_sha256'].items())
    assert [x['axialCells'] for x in data['assignmentAudit']]==list(range(2,33))
    for row in data['assignmentAudit']:
        assert row['referenceEndZ']==.05 and len(row['upperAxialDofs'])==3
        for face in row['faces']:assert all(v==0 for v in face['bottom']) and all(v==face['epsilon']*.05 for v in face['top'])
    results=[]
    for c in data['cases']:
        state=c['state'];d=state['diagnostics'];assert state['converged'] and state['reachedRequestedPose'] and state['epsilon']==c['epsilon']
        assert d['scaledMaxFreeResidual']<=1e-10 and abs(d['endBalanceN'])/d['forceScaleN']<1e-8
        assert math.copysign(1,d['rightReactionN'])==math.copysign(1,c['epsilon']) and abs(d['rightReactionN'])>.01
        nr=2*c['radialCells']+1
        assert all(c['fullDisplacement'][2*i+1]==0 for i in range(nr))
        assert all(c['fullDisplacement'][id]==c['epsilon']*.05 for id in c['upperAxialDofs'])
        for e in c['endpoints']:assert e['reference'][1]==.05;close(e['point']['z'],.05*(1+c['epsilon']),2e-15)
        for r in c['rendering']:
            assert r['referenceEndZ']==.05 and r['referenceMinZ']==0 and r['referenceMaxZ']==.05
            assert all(abs(z-.05*(1+c['epsilon']))<2e-15 for z in r['topAxialCoordinates'])
            close(r['capCenter'][2],.05*(1+c['epsilon']),2e-15)
            signal=abs(d['volumeRatio']-1);v0=d['energyScaleJ']/1500
            assert abs(r['boundaryVolumeM3']-d['volumeM3'])/v0<.1*signal
        error={}
        if c['ratio']==1:
            o=next(o for o in oracle['cylinders'] if o['lambda']==1+c['epsilon']);expected=math.pi*.005**2*o['nominal_axial_pa']
            close(d['rightReactionN'],expected,1e-12);close(d['volumeRatio'],o['J'],1e-12);close(d['energyJ'],math.pi*.005**2*.05*o['energy_density_pa'],1e-15)
            for p in c['probes']:
                close(p['r'],o['side_stretch']*p['R'],2e-12);close(p['z'],o['lambda']*p['Z'],2e-12);close(p['J'],o['J'],1e-12);close(p['cauchy']['rr'],0,2e-8)
            error={'independent_nominal_force_error_N':d['rightReactionN']-expected}
        else:
            f=next(x for x in old['cases'] if x['axialCells']==16 and x['radialCells']==8 and x['ratio']==1.5 and x['order']==7 and x['epsilon']==c['epsilon']);fd=f['state']['diagnostics']
            force=abs(d['rightReactionN']-fd['rightReactionN']);energy=abs(d['energyJ']-fd['energyJ']);point=max(abs(a['J']-b['J']) for a,b in zip(c['probes'],f['probes']))
            assert force<.01*abs(fd['rightReactionN']) and energy<.01*fd['energyJ'] and point<.1*fd['weightedRmsJDefect']
            error={'reaction_difference_N_from_frozen_fine':force,'energy_difference_J_from_frozen_fine':energy,'max_material_probe_J_difference_from_frozen_fine':point,'scope':'Observed differences on additional coarse radial meshes, not new continuum error/stability bounds'}
        results.append({'case':c['key'],'reaction_N':d['rightReactionN'],'volume_ratio':d['volumeRatio'],'scaled_residual':d['scaledMaxFreeResidual'],'geometry_bounds':geometry_bounds(c),'comparison':error})
    assert len(results)==16
    record={'status':'PASS','cases':results,'accepted_axial_count_assignment_cases':31,'source_input_sha256':data['inputs'],'checker_sha256':sha(Path(__file__)),'data_sha256':sha(datafile),'independent_oracle_sha256':sha(oraclefile),'frozen_fine_comparison_sha256':sha(oldfile),'scope':'Complete imposed cap membership, strict closed-domain reference/render endpoints, independent cylinder forces and full stored-map positivity on 16 formerly affected cases. Existing material, residual, physical and geometry tolerances unchanged.'}
    out.write_text(json.dumps(record,indent=2)+'\n');print('PASS 31 accepted counts and 16 affected solved cases, independent oracle, strict endpoints and positive Q2 maps')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('oracle',type=Path);p.add_argument('frozen_experiment',type=Path);p.add_argument('out',type=Path);a=p.parse_args();qualify(a.data,a.oracle,a.frozen_experiment,a.out)
