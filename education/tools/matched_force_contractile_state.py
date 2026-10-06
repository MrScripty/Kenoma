#!/usr/bin/env python3
"""Bounded, matched-force macro coupling of immutable qualified CE histories.

Research only. No ODE integration, nonlinear equilibrium solve or history advance.
Independent symmetric exponential verifies algorithmic endpoint sensitivities.
"""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import numpy as np
import scipy
from numpy.polynomial import Polynomial
from scipy.integrate import quad
from scipy.linalg import cho_solve, eigh

import continuous_strain_ce_reference as ce
import full_p2_p1 as model
from run_full_p2_p1 import serial
from source_amplitude_p2_p1 import ANCHOR, ExplicitBody, parameters

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT/'data/anatomical-arm-v1/review'
OUT = REVIEW/'matched-force-contractile-state'
PROTOCOL = ROOT/'research/mechanical-closure/matched-force-contractile-state-protocol.md'
PROTOCOL_COMMIT = '455f012'  # Resolved and independently checked before execution.
SIGMA, GAMMA, LAMBDA = 155000., 130., 1.25
AREA, VOLUME = .0004, .000056
INDICES = np.array([1, 2, 3, 4, 5, 6])
TIMES = np.array([0., .008, .02, .04, .1, .2])
CHECKS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    with (OUT/name).open('x') as f:
        json.dump(serial(data), f, indent=2, allow_nan=False)
        f.write('\n')


def gate(name, measured, limit, **details):
    check = dict(name=name, measured=float(measured), limit=float(limit),
                 passed=bool(np.isfinite(measured) and measured <= limit), **details)
    CHECKS.append(check)
    return check['passed']


def relative(a, b):
    return float(np.linalg.norm(np.asarray(a)-b)/max(1., np.linalg.norm(b)))


def envelope(lam):
    u = (np.asarray(lam)-1)/.5
    return np.where(abs(u) < 1, (1-u*u)**2, 0.)


def envelope_prime(lam):
    u = (np.asarray(lam)-1)/.5
    return np.where(abs(u) < 1, -4*u*(1-u*u)/.5, 0.)


def active_stress(lam, phi, baseline):
    return SIGMA*envelope(lam)*phi/baseline


def stationary(x, w, N):
    f, g = ce.attachment(x), ce.detachment(x)
    I = ce.summed(w*f/g)
    n = ce.coefficient(I, N)*f/g
    gp = -8*np.exp(-2*x)+12.66*np.exp(.6*x)
    # Exact derivative of the stationary FUNCTION, not of nodal interpolation.
    m0 = n*(x/.3**2+gp/g)
    return n, m0


def reaction(n, x, w, N):
    B = ce.summed(w*n)
    return ce.attachment(x)*(1-B)*(N-B)-ce.detachment(x)*n


def sensitivities(x, w, N, times):
    n, m0 = stationary(x, w, N)
    B = ce.summed(w*n)
    f, g = ce.attachment(x), ce.detachment(x)
    coefficient = 1+N-2*B
    z = np.sqrt(f*w)
    symmetric = -np.diag(g)-coefficient*np.outer(z, z)
    scale = np.sqrt(f/w)
    eigen, vectors = eigh(symmetric)
    amplitudes = vectors.T@(m0/scale)
    m = (vectors@(np.exp(np.outer(eigen, times))*amplitudes[:, None])).T*scale
    phi = m@(w*(1+x)/ce.BETA)
    energy = m@(w*.5*(1+x)**2/ce.BETA)
    # Two independent implementations of J action, before exponential evolution.
    direct = -g*m0-coefficient*f*ce.summed(w*m0)
    similarity = scale*(symmetric@(m0/scale))
    return dict(n=n, m0=m0, density=m, phi=phi, energy=energy,
                JActionRelativeError=relative(similarity, direct),
                reactionEigenvalueRange=[float(eigen[0]), float(eigen[-1])])


def passive(lam, transverse, tangent=False):
    F = np.diag([lam, transverse, transverse])[None]
    J = float(np.linalg.det(F)[0])
    p = ANCHOR['bulk']*np.log(J)
    with parameters(ANCHOR):
        P, C, E, _, G, _ = model.constitutive(F, np.array([p]), activation=0., tangent=tangent)
    energy = float(E[0]+ANCHOR['bulk']/2*np.log(J)**2)
    axial_tangent = None if C is None else float(C[0, 0, 0, 0, 0]+ANCHOR['bulk']*G[0, 0, 0]**2)
    return float(P[0, 0, 0]), energy, axial_tangent, J


def jump_energy(run, transverse):
    delta = run['delta']
    B, phi, E = run['loading']['beforeMoments']
    lam = LAMBDA+delta/GAMMA
    p = Polynomial([LAMBDA, 1/GAMMA])
    curve = (1-((p-1)/.5)**2)**2
    force = Polynomial([phi, B/ce.BETA])
    elastic = Polynomial([E, phi, B/(2*ce.BETA)])
    mechanical = (curve*force).integ()(delta)
    recruitment = (curve.deriv()*elastic).integ()(delta)
    loss = envelope(lam)*run['loading']['escapedElasticEnergy']
    change = envelope(lam)*run['loading']['afterMoments'][2]-envelope(LAMBDA)*E
    scale = VOLUME*SIGMA/phi/GAMMA
    identity = abs(change-mechanical-recruitment+loss)
    _, before, _, _ = passive(LAMBDA, transverse)
    _, after, _, J = passive(lam, transverse)
    work, error = quad(lambda v: passive(v, transverse)[0], LAMBDA, lam,
                       epsabs=1e-12, epsrel=1e-12)
    passive_error = abs(after-before-work)
    gate(run['name']+': jump energy/work', identity, 2e-12)
    gate(run['name']+': passive work', passive_error, 2e-12)
    gate(run['name']+': positive band geometry', 0. if .98 <= J <= 1.02 else 1., 0.)
    return dict(delta=delta, macroStretchChange=delta/GAMMA,
                activeMechanicalWorkJ=float(scale*mechanical),
                signedEnvelopeRecruitmentWorkJ=float(scale*recruitment),
                activeLinkStorageChangeJ=float(scale*change),
                endpointDetachmentRemovalJ=float(scale*loss),
                normalizedActiveIdentityError=float(identity),
                passiveStorageChangeJ=VOLUME*(after-before), passiveWorkJ=VOLUME*work,
                passiveWorkDensityIdentityErrorPa=passive_error,
                passiveWorkDensityQuadratureErrorEstimatePa=error)


def source_run_checks(run, states, x, w):
    N = run['N']
    gate(run['name']+': immutable initial RHS', run['initialWeightedRHSL1PerSecond'], 1e-10)
    gate(run['name']+': immutable initial adaptive moments',
         max(run['initialAdaptiveMomentAbsoluteDifferences']), 1e-10)
    for jump in ['loading', 'reversal']:
        gate(run['name']+': immutable '+jump+' identities', max(run[jump]['identityAbsoluteErrors']), 2e-12)
    moment = np.array([ce.moments(n, x, w) for n in states])
    gate(run['name']+': archived moments replay', np.max(abs(moment-run['matchedMoments'])), 2e-12)
    strict = np.all(np.isfinite(states)) and np.min(states) >= 0 and np.all(moment[:, 0] <= N)
    strict = strict and all(s['minimumDensity'] >= 0 and 0 <= s['mainBRange'][0] <= s['mainBRange'][1] <= N
                            for s in run['segments'])
    gate(run['name']+': strict populations', 0. if strict else 1., 0.)
    return moment


def negative_mode(body, x, state, witness):
    F = np.einsum('eni,eqna->eqia', x[body.m['tets']], body.grad)
    dF = np.einsum('eni,eqna->eqia', witness[body.m['tets']], body.grad)
    lam = np.linalg.norm(F[..., :, 0], axis=-1)
    n = F[..., :, 0]/lam[..., None]
    dlambda = np.sum(n*dF[..., :, 0], axis=-1)
    transverse = np.sum(dF[..., :, 0]**2, axis=-1)-dlambda**2
    p = state['p'][body.pi]@body.L.T
    A = np.einsum('eqia,eqaj->eqij', np.linalg.inv(F), dF)
    dp = np.einsum('qi,eq,eq->ei', body.L, np.trace(A, axis1=-2, axis2=-1), body.w)
    db = np.zeros(body.m['nv'])
    np.add.at(db, body.pi, dp)
    prestress = -np.sum(body.w*p*np.einsum('eqij,eqji->eq', A, A))
    weak = ANCHOR['bulk']*db@cho_solve(body.Mfactor, db)
    active_axial = np.sum(body.w*SIGMA*envelope_prime(lam)*dlambda**2)
    active_orientation = np.sum(body.w*SIGMA*envelope(lam)/lam*transverse)
    k = ANCHOR['kf']/ANCHOR['b']*np.expm1(ANCHOR['b']*(lam-1))
    kp = ANCHOR['kf']*np.exp(ANCHOR['b']*(lam-1))
    passive_fiber = np.sum(body.w*(kp*dlambda**2+k/lam*transverse))
    vector = witness.ravel()[body.m['free']]
    rayleigh = vector@state['H']@vector
    matrix = rayleigh-active_axial-active_orientation-passive_fiber-prestress-weak
    # Also compare full fixed-p quadrature against condensed nodal assembly.
    with parameters(ANCHOR):
        C = model.constitutive(F, p, activation=1., tangent=True)[1]
    independent = np.einsum('eqia,eqiajb,eqjb,eq->', dF, C, dF, body.w)+weak
    gate('Independent frozen Rayleigh assembly', abs(rayleigh-independent), 1e-8)
    return dict(matrix=matrix, passiveFiber=passive_fiber,
                activeForceLengthAxial=active_axial, activeOrientationTension=active_orientation,
                pressurePrestress=prestress, weakVolumeResponse=weak,
                total=rayleigh, independentQuadrature=independent,
                logJDirectionalRMSPerM=float(np.sqrt(np.sum(body.w*np.trace(A, axis1=-2, axis2=-1)**2)/body.volume))), lam, n, dlambda


def block_response(body, x, state, witness, response, phi0):
    diagnosis, lam, n, dlambda = negative_mode(body, x, state, witness)
    free = body.m['free']
    v = witness.ravel()[free]
    records = []
    for time, derivative in zip(list(TIMES)+[None], list(response)+[0.]):
        extra = SIGMA*envelope(lam)*GAMMA*derivative/phi0
        gradients = np.einsum('eqi,eqn->eqni', n, body.grad[..., 0]).reshape(len(lam), -1, 30)
        local = np.einsum('eqi,eqj,eq,eq->eij', gradients, gradients, extra, body.w)
        assembled = body.assemble(local, body.di, body.di, x.size, x.size)[free][:, free].toarray()
        projection = float(v@assembled@v)
        independent = float(np.sum(body.w*extra*dlambda**2))
        gate(f'Block {time}: added response quadratic form', abs(projection-independent), 1e-8)
        operator = state['H']+assembled
        lowest = eigh(operator, subset_by_index=[0, 2], eigvals_only=True)
        if time is None:
            gate('Relaxed/reset exact original operator', np.max(abs(operator-state['H'])), 1e-12)
        records.append(dict(timeSeconds=time, endpoint='analytic relaxed' if time is None else 'step/hold',
                            addedOldWitnessResponseNPerM=projection,
                            oldWitnessResponseNPerM=float(v@operator@v),
                            lowestSampledEigenvaluesNPerM=lowest,
                            quadraticFormAbsoluteDifferenceNPerM=abs(projection-independent)))
    return dict(diagnosisNPerM=diagnosis, responses=records,
                classification='POWERED_ENDPOINT_RESPONSE_OPERATOR; NOT_STORED_ENERGY_HESSIAN',
                sameFrozenPositions=True, newNonlinearSolve=False, physicalHistoryAdvanced=False)


def run():
    protocol_commit = subprocess.check_output(['git', 'rev-parse', PROTOCOL_COMMIT], cwd=ROOT, text=True).strip()
    committed = subprocess.check_output(['git', 'show', protocol_commit+':education/research/mechanical-closure/matched-force-contractile-state-protocol.md'], cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest() == digest(PROTOCOL)
    source = REVIEW/'continuous-strain-ce/summary.json'
    archive = REVIEW/'continuous-strain-ce/matched-densities.npz'
    baseline = REVIEW/'source-amplitude-p2-p1-v2/coarse-1.25-reclassification.json'
    mesh_path = REVIEW/'source-amplitude-p2-p1/coarse-mesh.json'
    old = json.loads(source.read_text())
    assert old['result'] == 'PASS_CONTINUUM_QUADRATURE_TIME_AND_TRANSLATION_GATES'
    assert old['sourceSHA256'] == digest(ROOT/'tools/continuous_strain_ce_reference.py')
    assert old['matchedDensitiesSHA256'] == digest(archive)
    inputs = [source, archive, baseline, mesh_path, ROOT/'tools/continuous_strain_ce_reference.py',
              ROOT/'tools/full_p2_p1.py', ROOT/'tools/source_amplitude_p2_p1.py', PROTOCOL,
              REVIEW/'source-amplitude-p2-p1/primary-source-binding.json',
              REVIEW/'source-amplitude-p2-p1/summary.json',
              REVIEW/'matched-force-contractile-state/frozen-mode-inspection.json']
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    hashes['tools/matched_force_contractile_state.py'] = digest(Path(__file__))
    save('request.json', dict(protocolCommit=protocol_commit, sourceHashes=hashes,
                             sigma0Pa=SIGMA, kinematicGain=GAMMA, lambda0=LAMBDA,
                             newODEIntegration=False, newNonlinearSolve=False, physicalHistoryAdvanced=False))
    base = json.loads(baseline.read_text())
    assert base['stationaryAccepted'] and base['derivativeGatesPass']
    m = {k: np.asarray(v) for k, v in json.loads(mesh_path.read_text())['mesh'].items()}
    body = ExplicitBody(m, ANCHOR, 1.)
    x = np.asarray(base['terminalPositionsM'])
    witness = np.asarray(base['spectrum']['witnessDirection'])
    state = body.evaluate(x, True)
    gate('Original frozen initial force', state['residual'], 1e-4)
    gate('Original frozen initial gradient reproduction', np.max(abs(state['g']-base['terminal']['fullGradientN'])), 2e-6)
    # With n=n*, phi/phi*=1 at EVERY integration point, P and g are algebraically identical.
    gate('Initial matched macro field gradient change', 0., 2e-6)
    transverse = base['analytic']['transverseStretch']
    passive_P, passive_E, passive_C, _ = passive(LAMBDA, transverse, True)
    initial_force = AREA*(passive_P+SIGMA*envelope(LAMBDA))
    gate('Initial force versus original analytic', abs(initial_force-base['analytic']['capForceN']), 1e-4)
    gate('Intentional Gamma force multiplier rejected',
         0. if abs(AREA*SIGMA*envelope(LAMBDA)*(GAMMA-1)) > 1e-4 else 1., 0.)
    selected = [r for r in old['runs'] if r['R'] == 3 and r['pCa'] == 4.5]
    assert len(selected) == 24
    npz = np.load(archive, allow_pickle=False)
    fields, run_results, sensitivity_records, tangent_checks = {}, [], {}, []
    for r in selected:
        name = r['name']
        xn, wn = npz[name+'_x'], npz[name+'_weights']
        densities = npz[name+'_matchedDensity']
        moments = source_run_checks(r, densities, xn, wn)
        fields[(r['count'], r['delta'], r['maxStepSeconds'])] = moments
        B0, phi0, E0 = moments[0]
        count = r['count']
        if count not in sensitivity_records:
            s = sensitivities(xn, wn, r['N'], TIMES)
            gate(f'{count}: reaction similarity action', s['JActionRelativeError'], 1e-12)
            gate(f'{count}: initial stationary density', np.max(abs(s['n']-densities[0])), 1e-12)
            # Source finite-domain translation endpoint correction, directly evaluated.
            edge_x = np.array([-3., 3.])
            I = ce.summed(wn*ce.attachment(xn)/ce.detachment(xn))
            edge_n = ce.coefficient(I, r['N'])*ce.attachment(edge_x)/ce.detachment(edge_x)
            edge_correction = ((1+3)*edge_n[1]-(1-3)*edge_n[0])/ce.BETA
            expected = B0/ce.BETA-edge_correction
            gate(f'{count}: finite-domain endpoint correction', abs(edge_correction), 1e-10)
            gate(f'{count}: independent initial transport derivative', relative(s['phi'][0], expected), 1e-12)
            for h in [1e-7, 5e-8]:
                fd = (reaction(s['n']+h*s['m0'], xn, wn, r['N'])-
                      reaction(s['n']-h*s['m0'], xn, wn, r['N']))/(2*h)
                Jm = -ce.detachment(xn)*s['m0']-(1+r['N']-2*B0)*ce.attachment(xn)*ce.summed(wn*s['m0'])
                gate(f'{count}: independent reaction derivative h={h}', relative(fd, Jm), 1e-4)
            sensitivity_records[count] = dict(sphi=s['phi'], senergy=s['energy'], phi0=phi0,
                B0=B0, E0=E0, N=r['N'], reactionEigenvalueRange=s['reactionEigenvalueRange'],
                finiteDomainPhiDerivativeEndpointCorrection=float(edge_correction))
        scale = VOLUME*SIGMA/phi0/GAMMA*envelope(LAMBDA+r['delta']/GAMMA)
        energy_records = []
        for index, t in zip(INDICES, TIMES):
            n = densities[index]
            B = moments[index, 0]
            weights_E = wn*.5*(1+xn)**2/ce.BETA
            attachment = scale*ce.summed(weights_E*ce.attachment(xn)*(1-B)*(r['N']-B))
            removal = scale*ce.summed(weights_E*ce.detachment(xn)*n)
            rate = scale*ce.summed(weights_E*reaction(n, xn, wn, r['N']))
            gate(name+f': hold rate ledger at {t}', abs(rate-attachment+removal)/max(1., attachment, removal), 1e-12)
            energy_records.append(dict(timeSeconds=t, attachmentElasticInputW=attachment,
                                      detachmentElasticRemovalW=removal, activeLinkStorageRateW=rate,
                                      activeLinkStorageJ=scale*moments[index, 2]))
        initial_scale = VOLUME*SIGMA/phi0/GAMMA*envelope(LAMBDA)
        initial_weights_E = wn*.5*(1+xn)**2/ce.BETA
        initial_input = initial_scale*ce.summed(initial_weights_E*ce.attachment(xn)*(1-B0)*(r['N']-B0))
        initial_removal = initial_scale*ce.summed(initial_weights_E*ce.detachment(xn)*densities[0])
        gate(name+': initial powered stationary ledger', abs(initial_input-initial_removal), 1e-12)
        run_results.append(dict(name=name, initialRawMoments=moments[0],
                                calibrationMultiplier=1/phi0, initialMacroForceN=initial_force,
                                initialAttachmentInputW=initial_input, initialDetachmentRemovalW=initial_removal,
                                jump=jump_energy(r, transverse), holds=energy_records))
    for count in [200, 400, 800]:
        s = sensitivity_records[count]
        active_derivative = SIGMA*(envelope_prime(LAMBDA)+envelope(LAMBDA)*GAMMA*s['sphi']/s['phi0'])
        s['activeEndpointTangentPa'] = active_derivative
        s['totalEndpointTangentPa'] = passive_C+active_derivative
        for step in [.001, .0005]:
            for delta in [.001, .0005]:
                plus, minus = fields[count, delta, step], fields[count, -delta, step]
                lp, lm = LAMBDA+delta/GAMMA, LAMBDA-delta/GAMMA
                pp, pm = passive(lp, transverse)[0], passive(lm, transverse)[0]
                passive_fd = (pp-pm)/(2*delta/GAMMA)
                gate(f'{count}, {step}, {delta}: passive derivative', relative(passive_fd, passive_C), 1e-4)
                fd = (pp+active_stress(lp, plus[INDICES, 1], s['phi0'])-
                      pm-active_stress(lm, minus[INDICES, 1], s['phi0']))/(2*delta/GAMMA)
                analytic = s['totalEndpointTangentPa']
                errors = abs(fd-analytic)/np.maximum(1., abs(analytic))
                gate(f'{count}, {step}, {delta}: endpoint tangent', max(errors), 1e-4)
                tangent_checks.append(dict(count=count, maxStepSeconds=step, delta=delta,
                                           finiteDifferencePa=fd, analyticPa=analytic,
                                           relativeErrors=errors))
        for delta in [.001, -.001, .0005, -.0005]:
            d = abs(fields[count, delta, .001]-fields[count, delta, .0005])
            gate(f'{count}, {delta}: time B', d[:, 0].max(), 1e-10)
            gate(f'{count}, {delta}: time phi/E', d[:, 1:].max(), 2e-10)
    for low, high in [(200, 400), (400, 800)]:
        for delta in [.001, -.001, .0005, -.0005]:
            for step in [.001, .0005]:
                gate(f'{low}->{high}, {delta}, {step}: quadrature moments',
                     abs(fields[low, delta, step]-fields[high, delta, step]).max(), 1e-9)
    material_pass = all(c['passed'] for c in CHECKS)
    block = None
    if material_pass:
        s = sensitivity_records[800]
        block = block_response(body, x, state, witness, s['sphi'], s['phi0'])
    result = dict(result='PASS_BOUNDED_MATCHED_FORCE_COUPLING' if all(c['passed'] for c in CHECKS) else 'FAIL_FIXED_GATE',
                  protocolCommit=protocol_commit, sourceHashes=hashes, scope='EDUCATIONAL COMPOSITE; NO ARM VALIDATION',
                  environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  physicalHistoryAdvanced=False, newODEIntegration=False, newNonlinearSolve=False,
                  timesSeconds=TIMES, initialMacroForceN=initial_force, originalFrozenResidualN=state['residual'],
                  passivePointTangentPa=passive_C, passivePointStoredEnergyJ=VOLUME*passive_E,
                  sigma0Pa=SIGMA, kinematicGain=GAMMA, runs=run_results,
                  sensitivity=sensitivity_records, tangentChecks=tangent_checks, checks=CHECKS, block=block,
                  energyLimit='Attachment elastic input and detachment removal are not full ATP/heat accounting; powered subsystem is not passive.',
                  relaxedActiveTangentPa=SIGMA*envelope_prime(LAMBDA),
                  relaxedTotalPointTangentPa=passive_C+SIGMA*envelope_prime(LAMBDA))
    save('summary.json', result)
    print(json.dumps(dict(result=result['result'], gates=len(CHECKS), failed=[c for c in CHECKS if not c['passed']],
                         initialMacroForceN=initial_force, tangentChecks=len(tangent_checks),
                         block=block), default=lambda a: np.asarray(a).tolist(), indent=2), flush=True)
    return result['result'] == 'PASS_BOUNDED_MATCHED_FORCE_COUPLING'


if __name__ == '__main__':
    import traceback
    try:
        passed = run()
    except Exception as error:
        if not (OUT/'failure.json').exists():
            save('failure.json', dict(exceptionType=type(error).__name__, message=str(error),
                                     traceback=traceback.format_exc(), checks=CHECKS,
                                     physicalHistoryAdvanced=False, noStateAdmission=True))
        raise
    raise SystemExit(0 if passed else 1)
