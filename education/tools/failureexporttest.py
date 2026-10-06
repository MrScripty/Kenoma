#!/usr/bin/env python3
"""Two predeclared diagnostic rejections; no full packet rerun or physical failure."""
import argparse
import ast
import difflib
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/anatomical-arm-v1/review/conserved-ce-failure-export'
FIXTURE = dict(R=2.4,dx=.04,pCa=4.5,delta=.001,h=.004)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(x):
    return ast.dump(x, include_attributes=False)


def static_parity(original, revised):
    a, b = ast.parse(original.read_text()), ast.parse(revised.read_text())
    fa = {n.name:n for n in a.body if isinstance(n, ast.FunctionDef)}
    fb = {n.name:n for n in b.body if isinstance(n, ast.FunctionDef)}
    unchanged = ['capacity','attachment','detachment','grid','validate','force','energy']
    for name in unchanged:
        assert dump(fa[name]) == dump(fb[name]), 'helper equation/gate changed: '+name
    projected = ast.parse(revised.read_text())
    shift = next(n for n in projected.body if isinstance(n, ast.FunctionDef) and n.name == 'shift')
    shift.args.args = shift.args.args[:-2]
    shift.args.defaults = []
    shift.body = [n for n in shift.body if not (isinstance(n, ast.If)
                  and isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
                  and n.test.left.id == 'progress')]
    assert dump(fa['shift']) == dump(shift), 'projected transport math/gates differ'
    # The kinetic calls remain exactly the original expressions; wrappers only export diagnostics.
    def calls(node, name):
        return sorted(dump(n) for n in ast.walk(node) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name) and n.func.id == name)
    for name in ['step','rhs']:
        assert calls(fa['run_case'],name) == calls(fb['run_case'],name), 'kinetic call changed: '+name
    def thresholds(node):
        return sorted(n.comparators[0].value for n in ast.walk(node)
                      if isinstance(n, ast.Compare) and len(n.comparators) == 1
                      and isinstance(n.comparators[0], ast.Constant)
                      and isinstance(n.comparators[0].value, float)
                      and n.comparators[0].value in (1e-10,1e-12))
    assert thresholds(fa['run_case']) == thresholds(fb['run_case']), 'kinetic residual gate changed'
    for name in ['PARAM','TIMES']:
        def assignment(tree):
            return next(n for n in tree.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
        assert dump(assignment(a)) == dump(assignment(b)), 'parameter/event change: '+name
    return dict(unchangedHelperASTs=unchanged,projectedShiftEquationAndGateASTIdentical=True,
                kineticStepAndRHSCallASTsIdentical=True,residualThresholdsIdentical=True,
                parametersAndEventTimesIdentical=True,
                changeScope='Progress snapshots, export helper, phases, equivalent scalar terminal diagnostic and new output identity')


def close(a,b,tolerance=2e-12):
    assert abs(float(a)-float(b)) <= tolerance, (a,b)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol-commit',required=True)
    args = parser.parse_args()
    assert len(args.protocol_commit) == 40 and all(c in '0123456789abcdef' for c in args.protocol_commit)
    original = ROOT/'tools/conserved_ce_trajectory.py'
    revised = ROOT/'tools/conserved_ce_trajectory_v2.py'
    protocol = ROOT/'research/mechanical-closure/conserved-ce-failure-export-protocol.md'
    OUT.mkdir(parents=True,exist_ok=True)
    if any((OUT/n).exists() for n in ['test-summary.json','test-execution.log','terminal-rejection.json','reversal-rejection.json']):
        raise FileExistsError('preserve existing failure-export test evidence')
    spec = importlib.util.spec_from_file_location('failure_export_v2',revised)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    summary = dict(result='RUNNING',scope='Intentional diagnostic failures only, not physical model failures',
                   originalExecutedCommit='b21ee8c252d4160a367fa7b21a9adf8c57a1dcaf',
                   protocolCommit=args.protocol_commit,fixture=FIXTURE,
                   sourceHashes={str(p.relative_to(ROOT)):sha(p) for p in
                                 [original,revised,protocol,Path(__file__),ROOT/'tools/source_two_state_operator.py']},
                   noRetries=True,noFullPacketRerun=True,tests=[],unexpectedFailures=[])
    log = []
    original_text, revised_text = original.read_text(), revised.read_text()
    (OUT/'original-to-v2.diff').write_text(''.join(difflib.unified_diff(
        original_text.splitlines(True),revised_text.splitlines(True),
        fromfile='frozen/conserved_ce_trajectory.py',tofile='new/conserved_ce_trajectory_v2.py')))

    def test(kind):
        x,F,g = runner.grid(FIXTURE['R'],FIXTURE['dx'])
        N = runner.capacity(FIXTURE['pCa'])
        p0 = runner.equilibrium(F,g,N)
        progress = {}
        stored = dict(x=x,F=F,g=g,initialState=p0)
        record = dict(result='EXPECTED_INJECTED_DIAGNOSTIC_REJECTION',injectedFailure=True,
                      physicalModelFailure=False,fixture=FIXTURE,N=N,sourceHashes=summary['sourceHashes'],
                      protocolCommit=args.protocol_commit,cases=[],failures=[])
        original_rhs, original_force, original_step = runner.rhs, runner.force, runner.step
        count = dict(operatorCalls=0,injections=0)
        step_states = []

        def tracked_step(p,N,F,g,h):
            count['operatorCalls'] += 1
            out = original_step(p,N,F,g,h)
            step_states.append((p.copy(),out.copy()))
            return out

        def injected_rhs(p,N,F,g):
            out = original_rhs(p,N,F,g)
            if progress.get('phase') == 'terminal-candidate-validation':
                assert progress['candidateTimeSeconds'] == 1.
                count['injections'] += 1
                out = out.copy()
                out[0] += 1e-6
            return out

        def injected_force(p,x):
            out = original_force(p,x)
            if progress.get('phase') == 'reversal-validation' and p is progress.get('candidateState'):
                count['injections'] += 1
                out += 1e-8
            return out

        runner.step = tracked_step
        if kind == 'terminal':
            runner.rhs = injected_rhs
        else:
            runner.force = injected_force
        observed = None
        try:
            runner.run_case(p0,N,x,F,g,FIXTURE['dx'],FIXTURE['delta'],FIXTURE['h'],progress)
        except Exception as exc:
            observed = exc
            runner.export_failure(record,stored,FIXTURE,progress,traceback.format_exc())
            record['observedException'] = dict(type=type(exc).__name__,message=str(exc))
        finally:
            runner.rhs,runner.force,runner.step = original_rhs,original_force,original_step
            record['counts'] = count.copy()
            np.savez_compressed(OUT/(kind+'-rejection.npz'),**stored)
            (OUT/(kind+'-rejection.json')).write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')

        # Check the actual on-disk failure export, not only the in-memory progress object.
        reread = json.loads((OUT/(kind+'-rejection.json')).read_text())
        with np.load(OUT/(kind+'-rejection.npz'),allow_pickle=False) as npz:
            arrays = {k:npz[k] for k in npz.files}
        assert isinstance(observed,ValueError), 'missing or unexpected rejection'
        assert len(reread['failures']) == 1
        failed = reread['failures'][0]
        diag = failed['progressDiagnostics']
        assert failed['stateClockAdvancedOnRejection'] is False
        for key in ['failedLastAdmittedState','failedCandidateState','failedMatchedStates',
                    'failedMatchedTimesSeconds','failedOperatorInputState','loadingBeforeState','loadingAfterState']:
            assert key in arrays, 'missing exported array '+key
        runner.validate(arrays['failedLastAdmittedState'],N)
        runner.validate(arrays['failedCandidateState'],N)
        for state in arrays['failedMatchedStates']:
            runner.validate(state,N)

        def verify_ledger(event):
            before,after = arrays[event+'BeforeState'],arrays[event+'AfterState']
            ledger = diag[event]
            delta = ledger['delta']
            B = math.fsum(before)
            beta = runner.PARAM['beta']
            mass = math.fsum(after)+ledger['escapedMass']-B
            force_prediction = B*delta/beta-ledger['escapedNormalizedMoment']
            interpolation = B*abs(delta)*(FIXTURE['dx']-abs(delta))/(2*beta)
            energy_prediction = original_force(before,x)*delta+B*delta**2/(2*beta)+interpolation-ledger['escapedNormalizedElasticEnergy']
            force_error = original_force(after,x)-original_force(before,x)-force_prediction
            energy_error = runner.energy(after,x)-runner.energy(before,x)-energy_prediction
            close(mass,0.)
            close(force_error,0.)
            close(energy_error,0.)
            close(ledger['interpolationWork'],interpolation)
            close(ledger['forceIdentityError'],abs(force_error))
            close(ledger['energyIdentityError'],abs(energy_error))
            return dict(massError=abs(mass),forceError=abs(force_error),energyError=abs(energy_error))

        ledger_checks = {'loading':verify_ledger('loading')}
        if kind == 'terminal':
            assert str(observed) == 'fixed-horizon terminal kinetic residual failed'
            assert count == dict(operatorCalls=250,injections=1)
            assert diag['acceptedSteps'] == 249
            close(diag['acceptedTimeSeconds'],.996,tolerance=1e-15)
            assert diag['candidateTimeSeconds'] == 1.
            assert diag['terminalCandidateKineticResidualL1PerSecond'] > 1e-10
            assert float(np.sum(np.abs(original_rhs(arrays['failedCandidateState'],N,F,g)))) <= 1e-10
            assert arrays['failedMatchedStates'].shape == (10,len(x))
            assert not np.any(arrays['failedMatchedTimesSeconds'] == 1.)
            assert diag['loading'] is not None and diag['reversal'] is not None
            ledger_checks['reversal'] = verify_ledger('reversal')
            assert np.array_equal(arrays['failedLastAdmittedState'],arrays['failedOperatorInputState'])
            accepted_step_states = step_states[:-1]
        else:
            assert str(observed) == 'transport moment/work/accounting gate failed'
            assert count == dict(operatorCalls=50,injections=2)
            assert diag['acceptedSteps'] == 50 and diag['acceptedTimeSeconds'] == .2
            assert arrays['failedMatchedStates'].shape == (7,len(x))
            assert np.array_equal(arrays['failedLastAdmittedState'],arrays['failedMatchedStates'][-1])
            assert np.count_nonzero(arrays['failedMatchedTimesSeconds'] == .2) == 1
            assert diag['loading'] is not None and diag['reversal'] is None
            assert 'reversalAfterState' not in arrays
            candidate_ledger = diag['candidateJumpLedger']
            assert candidate_ledger['forceIdentityError'] > 2e-12
            assert candidate_ledger['energyIdentityError'] <= 2e-12
            assert candidate_ledger['headAccountingError'] <= 2e-12
            assert diag['candidateJumpEvent'] == 'reversal'
            assert np.array_equal(arrays['failedLastAdmittedState'],arrays['failedJumpBeforeState'])
            accepted_step_states = step_states

        admitted = [p0,arrays['loadingAfterState']]+[p for _,p in accepted_step_states]
        if kind == 'terminal':
            admitted.append(arrays['reversalAfterState'])
        expected_min = min(float(np.min(p)) for p in admitted)
        expected_max_B = max(math.fsum(p) for p in admitted)
        scale = max(1.,N,FIXTURE['h']*math.fsum(F),FIXTURE['h']*float(np.max(g))*N)
        expected_max_residual = max(float(np.max(np.abs(after-before-FIXTURE['h']*original_rhs(after,N,F,g))))/scale
                                    for before,after in accepted_step_states)
        close(diag['allStepMinimumPopulation'],expected_min)
        close(diag['allStepMaximumB'],expected_max_B)
        close(diag['allStepNormalizedBEResidualMax'],expected_max_residual)
        return dict(name=kind,passed=True,expectedRejection=reread['observedException'],counts=count,
                    acceptedSteps=diag['acceptedSteps'],lastAdmittedTimeSeconds=diag['acceptedTimeSeconds'],
                    matchedPrefixCount=len(arrays['failedMatchedStates']),admittedLedgerChecks=ledger_checks,
                    exportedAcceptedDiagnostics=dict(minimumPopulation=diag['allStepMinimumPopulation'],
                      maximumB=diag['allStepMaximumB'],normalizedBEResidualMax=diag['allStepNormalizedBEResidualMax']),
                    jsonSHA256=sha(OUT/(kind+'-rejection.json')),npzSHA256=sha(OUT/(kind+'-rejection.npz')))

    try:
        summary['staticEquationAndGateParity'] = static_parity(original,revised)
        log.append('PASS static equation/gate parity; complete original-to-v2 diff retained')
        for kind in ['terminal','reversal']:
            try:
                item = test(kind)
                summary['tests'].append(item)
                log.append('PASS expected '+kind+' rejection/export: '+json.dumps(item))
            except Exception as exc:
                failure = dict(name=kind,passed=False,exception=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
                summary['tests'].append(failure)
                summary['unexpectedFailures'].append(failure)
                log.append('FAIL '+kind+' test: '+traceback.format_exc())
        summary['result'] = 'PASS_INTENTIONAL_FAILURE_EXPORT_TESTS' if not summary['unexpectedFailures'] else 'FAIL_FAILURE_EXPORT_TESTS'
    except Exception:
        summary['result'] = 'FAIL_STATIC_FAILURE_EXPORT_AUDIT'
        summary['unexpectedFailures'].append(dict(traceback=traceback.format_exc()))
        log.append(traceback.format_exc())
    finally:
        summary['sourceDiffSHA256'] = sha(OUT/'original-to-v2.diff')
        log.append(summary['result'])
        (OUT/'test-summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
        (OUT/'test-execution.log').write_text('\n'.join(log)+'\n')
    print(json.dumps(summary,indent=2))
    return 0 if summary['result'] == 'PASS_INTENTIONAL_FAILURE_EXPORT_TESTS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
