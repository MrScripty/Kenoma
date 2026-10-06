"""Additive failure-export instrumentation; frozen trajectory math/gates retained."""
import hashlib
import json
import math
import platform
import subprocess
import traceback
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import ndtr

from source_two_state_operator import equilibrium, step, rhs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/conserved-ce-failure-export'
PARAM = dict(f1=52., g1=4., g2=21.1, E1=2., E2=-.6, w=.3,
             beta=.5, nH=3.1, Ca50MicroM=.83)
TIMES = np.array([0., 0., .008, .02, .04, .1, .2, .2, .3, .5, 1.])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def capacity(pca):
    return 1/(1+(PARAM['Ca50MicroM']/10**(6-pca))**PARAM['nH'])


def attachment(x):
    return PARAM['f1']*np.exp(-np.asarray(x)**2/(2*PARAM['w']**2))/(np.sqrt(2*np.pi)*PARAM['w'])


def detachment(x):
    return PARAM['g1']*np.exp(-PARAM['E1']*np.asarray(x))+PARAM['g2']*np.exp(-PARAM['E2']*np.asarray(x))


def grid(R, dx):
    count = int(round(2*R/dx))
    edges = np.linspace(-R, R, count+1)
    assert abs(edges[1]-edges[0]-dx) < 1e-14
    x = .5*(edges[:-1]+edges[1:])
    lo, hi = edges[:-1]/PARAM['w'], edges[1:]/PARAM['w']
    cells = np.where(lo >= 0, ndtr(-lo)-ndtr(-hi), ndtr(hi)-ndtr(lo))
    F, g = PARAM['f1']*cells, detachment(x)
    assert np.all(F > 0) and np.all(g > 0)
    return x, F, g


def validate(p, N):
    if not np.all(np.isfinite(p)) or np.any(p < 0) or not 0 <= math.fsum(p) <= N <= 1:
        raise ValueError('strict population gate failed; no clipping/reset')


def force(p, x):
    return float(np.dot(1+x, p)/PARAM['beta'])


def energy(p, x):
    return float(np.dot(.5*(1+x)**2, p)/PARAM['beta'])


def shift(p, N, x, dx, delta, progress=None, event=None):
    validate(p, N)
    if not np.isfinite(delta) or not 0 < abs(delta) < dx:
        raise ValueError('invalid single-bin displacement')
    r = abs(delta)/dx
    candidate = (1-r)*p
    if delta > 0:
        candidate[1:] += r*p[:-1]
        lost, escaped_x = r*p[-1], x[-1]+dx
    else:
        candidate[:-1] += r*p[1:]
        lost, escaped_x = r*p[0], x[0]-dx
    if progress is not None:
        progress.update(candidateState=candidate, candidateJumpEvent=event,
                        jumpBeforeState=p.copy(), candidateJumpLedger=None)
    validate(candidate, N)
    B = math.fsum(p)
    escaped_force_moment = float((1+escaped_x)*lost/PARAM['beta'])
    escaped_energy = float(.5*(1+escaped_x)**2*lost/PARAM['beta'])
    force_prediction = B*delta/PARAM['beta']-escaped_force_moment
    rigid_work = force(p, x)*delta+.5*B*delta**2/PARAM['beta']
    interpolation_work = B*abs(delta)*(dx-abs(delta))/(2*PARAM['beta'])
    energy_prediction = rigid_work+interpolation_work-escaped_energy
    rec = dict(delta=float(delta), escapedMass=float(lost), escapedDestinationCenter=float(escaped_x),
               escapedNormalizedMoment=escaped_force_moment, escapedNormalizedElasticEnergy=escaped_energy,
               fastHeldPopulationSlope=B/PARAM['beta'], forceIncrement=force(candidate,x)-force(p,x),
               discreteForcePrediction=force_prediction,
               forceIdentityError=abs(force(candidate,x)-force(p,x)-force_prediction),
               energyChange=energy(candidate,x)-energy(p,x), rigidTranslationWork=rigid_work,
               interpolationWork=interpolation_work, discreteEnergyPrediction=energy_prediction,
               energyIdentityError=abs(energy(candidate,x)-energy(p,x)-energy_prediction),
               headAccountingError=abs(math.fsum(candidate)+lost-B))
    if progress is not None:
        progress['candidateJumpLedger'] = rec.copy()
    if max(rec['forceIdentityError'],rec['energyIdentityError'],rec['headAccountingError']) > 2e-12:
        raise ValueError('transport moment/work/accounting gate failed')
    return candidate, rec


def run_case(p0, N, x, F, g, dx, delta, dt, progress=None):
    progress = {} if progress is None else progress
    progress.update(acceptedTimeSeconds=0.,acceptedSteps=0,lastAdmittedState=p0,
                    phase='initial-validation',matchedStates=[p0],matchedTimesSeconds=[0.],
                    loading=None,reversal=None,candidateState=None,candidateJumpLedger=None,
                    allStepMinimumPopulation=float(np.min(p0)),allStepMaximumB=math.fsum(p0),
                    allStepNormalizedBEResidualMax=0.)
    validate(p0,N)
    initial_residual = float(np.sum(np.abs(rhs(p0,N,F,g))))
    progress['initialKineticResidualL1PerSecond'] = initial_residual
    if initial_residual > 1e-10:
        raise ValueError('initial equilibrium residual failed')
    progress['phase'] = 'loading-validation'
    p, loading = shift(p0,N,x,dx,delta,progress,'loading')
    saved = [p0.copy(),p.copy()]
    progress.update(lastAdmittedState=p,phase='kinetics',matchedStates=saved,
                    matchedTimesSeconds=[0.,0.],loading=loading.copy(),
                    loadingBeforeState=p0.copy(),loadingAfterState=p.copy(),
                    candidateState=None,candidateJumpLedger=None,candidateJumpEvent=None,
                    jumpBeforeState=None)
    reversal = None
    checkpoints = {.008,.02,.04,.1,.2,.3,.5,1.}
    indices = {int(round(t/dt)) for t in checkpoints}
    if any(abs(round(t/dt)*dt-t) > 1e-13 for t in checkpoints):
        raise ValueError('unmatched sampling clock')
    maximum_residual = 0.
    minimum = min(float(np.min(p0)),float(np.min(p)))
    maximum_B = max(math.fsum(p0),math.fsum(p))
    progress.update(allStepMinimumPopulation=minimum,allStepMaximumB=maximum_B)
    accepted_time = 0.
    scale = max(1.,N,dt*math.fsum(F),dt*float(np.max(g))*N)
    for i in range(1,int(round(1/dt))+1):
        progress.update(phase='operator-candidate',attemptedStepIndex=i,
                        candidateTimeSeconds=i*dt,operatorInputState=p.copy(),candidateState=None)
        try:
            candidate = step(p,N,F,g,dt)
        except Exception as exc:
            progress.update(phase='operator-rejection',operatorException=dict(
                type=type(exc).__name__,message=str(exc)),operatorInternalCandidateAvailable=False)
            raise
        progress['candidateState']=candidate
        progress['phase']='step-residual-validation'
        residual = float(np.max(np.abs(candidate-p-dt*rhs(candidate,N,F,g))))
        progress['candidateNormalizedBEResidual'] = residual/scale
        if residual/scale > 1e-12:
            raise ValueError('independent full step residual gate failed')
        if i == int(round(1/dt)):
            progress['phase']='terminal-candidate-validation'
            terminal_candidate_residual = float(np.sum(np.abs(rhs(candidate,N,F,g))))
            progress['terminalCandidateKineticResidualL1PerSecond'] = terminal_candidate_residual
            if terminal_candidate_residual > 1e-10:
                progress['phase']='terminal-candidate-residual'
                raise ValueError('fixed-horizon terminal kinetic residual failed')
        # Neither state nor clock advances before all step gates pass.
        p = candidate
        accepted_time = i*dt
        progress.update(acceptedTimeSeconds=accepted_time,acceptedSteps=i,lastAdmittedState=p,
                        candidateState=None,phase='kinetics')
        minimum = min(minimum,float(np.min(p)))
        maximum_B = max(maximum_B,math.fsum(p))
        maximum_residual = max(maximum_residual,residual/scale)
        progress.update(allStepMinimumPopulation=minimum,allStepMaximumB=maximum_B,
                        allStepNormalizedBEResidualMax=maximum_residual)
        if i in indices:
            saved.append(p.copy())
            progress['matchedTimesSeconds'].append(accepted_time)
        if i == int(round(.2/dt)):
            progress['phase']='reversal-validation'
            before_reversal = p
            candidate, reversal = shift(p,N,x,dx,-delta,progress,'reversal')
            p = candidate
            progress.update(lastAdmittedState=p,phase='kinetics',reversal=reversal.copy(),
                            reversalBeforeState=before_reversal.copy(),reversalAfterState=p.copy(),
                            candidateState=None,candidateJumpLedger=None,candidateJumpEvent=None,
                            jumpBeforeState=None)
            saved.append(p.copy())
            progress['matchedTimesSeconds'].append(accepted_time)
            minimum = min(minimum,float(np.min(p)))
            maximum_B = max(maximum_B,math.fsum(p))
            progress.update(allStepMinimumPopulation=minimum,allStepMaximumB=maximum_B)
    progress['phase']='terminal-residual'
    terminal_residual = float(np.sum(np.abs(rhs(p,N,F,g))))
    progress['terminalKineticResidualL1PerSecond'] = terminal_residual
    if terminal_residual > 1e-10:
        raise ValueError('fixed-horizon terminal kinetic residual failed')
    assert accepted_time == 1. and len(saved) == len(TIMES) and reversal is not None
    states = np.asarray(saved)
    rec = dict(N=N,acceptedSteps=int(round(1/dt)),acceptedTimeSeconds=accepted_time,
               initialKineticResidualL1PerSecond=initial_residual,
               terminalKineticResidualL1PerSecond=terminal_residual,
               allStepMinimumPopulation=minimum,allStepMaximumB=maximum_B,
               allStepNormalizedBEResidualMax=maximum_residual,
               matchedForces=[force(z,x) for z in states],
               matchedElasticEnergies=[energy(z,x) for z in states],
               matchedB=[math.fsum(z) for z in states],loading=loading,reversal=reversal)
    return states,rec


def export_failure(record, stored, current_case, progress, exception_text):
    """Preserve admitted diagnostics and available rejected candidates separately."""
    arrays = {'lastAdmittedState':'failedLastAdmittedState',
              'matchedStates':'failedMatchedStates', 'candidateState':'failedCandidateState',
              'operatorInputState':'failedOperatorInputState', 'jumpBeforeState':'failedJumpBeforeState',
              'loadingBeforeState':'loadingBeforeState', 'loadingAfterState':'loadingAfterState',
              'reversalBeforeState':'reversalBeforeState', 'reversalAfterState':'reversalAfterState'}
    for key, target in arrays.items():
        if progress.get(key) is not None:
            stored[target] = np.asarray(progress[key]).copy()
    if progress.get('matchedTimesSeconds') is not None:
        stored['failedMatchedTimesSeconds'] = np.asarray(progress['matchedTimesSeconds'])
    diagnostics = {k:v for k,v in progress.items() if k not in arrays}
    record['failures'].append(dict(traceback=exception_text,
        acceptedCompletedCases=len(record['cases']),case=current_case,
        lastAdmittedTimeSeconds=progress.get('acceptedTimeSeconds'),
        phase=progress.get('phase'),stateClockAdvancedOnRejection=False,
        progressDiagnostics=diagnostics,
        archivedArrays={k:target for k,target in arrays.items() if target in stored}))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'summary.json').exists() or (OUT/'matched-states.npz').exists():
        raise RuntimeError('refusing to overwrite an existing trajectory receipt')
    refs=['tools/conserved_ce_trajectory_v2.py','tools/conserved_ce_trajectory.py','tools/source_two_state_operator.py',
          'research/mechanical-closure/conserved-ce-trajectory-protocol.md',
          'research/mechanical-closure/conserved-ce-failure-export-protocol.md',
          'research/mechanical-closure/original-plos-table-visual-audit.md',
          'research/mechanical-closure/plos-original-table-visual-evidence/receipt.json']
    record=dict(result='RUNNING',scope='Dimensionless source-informed direct-CE prerequisite; no series/arm solve',
                executionCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                sourceHashes={p:sha(ROOT/p) for p in refs},parameters=PARAM,matchedTimesSeconds=TIMES.tolist(),
                environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                grids=[],cases=[],failures=[])
    stored={'matchedTimesSeconds':TIMES}
    progress={}
    current_case=None
    try:
        I,ie=quad(lambda z:float(attachment(z)/detachment(z)),-3,3,epsabs=1e-12,epsrel=1e-12)
        J,je=quad(lambda z:float(z*attachment(z)/detachment(z)),-3,3,epsabs=1e-12,epsrel=1e-12)
        q=2/(1+np.sqrt(1+4*I))
        record['continuousHeldN1Equilibrium']=dict(I=I,J=J,errorEstimates=[ie,je],q=q,B=I*q*q,
                                                  rawNormalizedForce=(I+J)*q*q/PARAM['beta'])
        assert max(ie,je)<1e-10
        for R in [2.4,3.]:
            for dx in [.04,.02,.01]:
                key=f'R{R:g}-dx{dx:g}'
                x,F,g=grid(R,dx)
                stored[key+'_x'],stored[key+'_F'],stored[key+'_g']=x,F,g
                record['grids'].append(dict(name=key,R=R,dx=dx,bins=len(x)))
                for pca in [4.5,6.1]:
                    N=capacity(pca)
                    p0=equilibrium(F,g,N)
                    for delta in [.001,-.001,.0005,-.0005]:
                        for dt in [.004,.002,.001]:
                            name=f'{key}-pCa{pca:g}-delta{delta:g}-dt{dt:g}'
                            current_case=dict(name=name,grid=key,pCa=pca,N=N,delta=delta,dt=dt)
                            progress={}
                            states,rec=run_case(p0,N,x,F,g,dx,delta,dt,progress)
                            rec.update(name=name,grid=key,pCa=pca,delta=delta,dt=dt)
                            stored[name]=states
                            record['cases'].append(rec)
                            print('PASS',name,'terminalResidual',rec['terminalKineticResidualL1PerSecond'],flush=True)
                (OUT/'summary.json').write_text(json.dumps(record,indent=2)+'\n')
        record['result']='PASS_CONSERVED_CE_HISTORY_GATES'
    except Exception:
        record['result']='FAILED_CONSERVED_CE_HISTORY_GATES'
        export_failure(record,stored,current_case,progress,traceback.format_exc())
        raise
    finally:
        np.savez_compressed(OUT/'matched-states.npz',**stored)
        (OUT/'summary.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':
    main()
