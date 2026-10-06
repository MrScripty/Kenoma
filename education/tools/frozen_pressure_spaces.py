"""Research-only complete finite-K operators; no optimizer or stabilization.

Mixed: E=W0+K/2 b.T M^-1 b; g=P0+pG; H=Hfixed(p)+K D.T M^-1 D.
Pointwise: E=W0+K/2 integral(logJ)^2; C=Cfixed(K logJ)+K G outer G.
Both fixed-pressure C and pointwise C retain -p G_rb G_sa prestress.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.linalg import cho_factor, cho_solve, eigh, solve

from full_p2_p1 import Body
from source_amplitude_p2_p1 import ANCHOR, ORIGINAL_CONSTITUTIVE, parameters
from run_full_p2_p1 import serial

ROOT = Path(__file__).resolve().parents[1]
SPACES = ['continuousP1', 'brokenP1', 'pointwise']


class FrozenOperator(Body):
    def __init__(self, mesh, space, depth=2, material=ANCHOR, activation=1.):
        assert space in SPACES
        super().__init__(mesh, depth)
        self.space = space; self.material = dict(material); self.activation = activation
        self.Mlocal = np.einsum('qi,qj,eq->eij', self.L, self.L, self.w)
        if space == 'brokenP1':
            self.pi = np.arange(4*len(mesh['tets'])).reshape(-1, 4)
            n = self.pi.size
            self.M = self.assemble(self.Mlocal, self.pi, self.pi, n, n).toarray()
            self.Mfactor = cho_factor(self.M)

    def newton(self, *args, **kwargs):
        raise RuntimeError('Frozen-field comparison prohibits nonlinear solves')

    def evaluate(self, x, hessian=False):
        X = x[self.m['tets']]
        F = np.einsum('eni,eqna->eqia', X, self.grad)
        J = np.linalg.det(F)
        if not np.isfinite(J).all() or np.any(J <= 1e-6):
            raise ValueError('Original positive finite geometry guard')
        log = np.log(J); K = self.material['bulk']
        if self.space == 'pointwise':
            p = K*log; pq = p; b = None; weak = None; D = None
        else:
            local = np.einsum('qi,eq,eq->ei', self.L, log, self.w)
            b = np.zeros(len(self.M)); np.add.at(b, self.pi, local)
            p = K*cho_solve(self.Mfactor, b); pq = p[self.pi]@self.L.T
            weak = b-self.M@p/K
        with parameters(self.material):
            P, C, E, J, G, lam = ORIGINAL_CONSTITUTIVE(F, pq, activation=self.activation, tangent=hessian)
        local_g = np.einsum('eqia,eqna,eq->eni', P, self.grad, self.w).reshape(-1, 30)
        g = np.zeros(x.size); np.add.at(g, self.di, local_g)
        dlog = np.einsum('eqia,eqna->eqni', G, self.grad).reshape(len(X), len(self.L), 30)
        if self.space != 'pointwise':
            local_D = np.einsum('qi,eqa,eq->eia', self.L, dlog, self.w)
            D = self.assemble(local_D, self.pi, self.di, len(self.M), x.size)
        H = None; R = None
        if hessian:
            # Construct the pointwise operator directly from its own energy Hessian;
            # never obtain it by modifying a mixed matrix or eigenvalues.
            if self.space == 'pointwise':
                C += K*np.einsum('eqia,eqjb->eqiajb', G, G)
            local_H = np.array([np.einsum('qna,qiajb,qmb,q->nimj', self.grad[e], C[e], self.grad[e],
                                        self.w[e], optimize=True).reshape(30, 30) for e in range(len(X))])
            free = self.m['free']
            H = self.assemble(local_H, self.di, self.di, x.size, x.size)[free][:, free].toarray()
            if self.space != 'pointwise':
                Df = D[:, free].toarray()
                H += K*Df.T@cho_solve(self.Mfactor, Df)
            local_R = np.einsum('eqa,eqb,eq->eab', dlog, dlog, self.w)
            R = self.assemble(local_R, self.di, self.di, x.size, x.size)[free][:, free].toarray()
        mismatch = log-pq/K
        corners = np.linalg.det(np.einsum('eni,eqna->eqia', X, self.cornergrad))
        energy = np.sum(E*self.w)+(np.sum(.5*K*log*log*self.w) if self.space == 'pointwise' else .5*p@b)
        return dict(g=g, p=p, pq=pq, b=b, D=D, H=H, R=R, F=F, G=G, J=J, lam=lam,
                    energy=float(energy), residual=float(np.linalg.norm(g[self.m['free']])),
                    weakRMS=0. if weak is None else float(np.sqrt(max(0, weak@cho_solve(self.Mfactor, weak)/self.volume))),
                    pointwiseRMS=float(np.sqrt(np.sum(mismatch*mismatch*self.w)/self.volume)),
                    Jmin=float(min(J.min(), corners.min())), Jmax=float(max(J.max(), corners.max())),
                    meanVolumeChange=float(np.sum((J-1)*self.w)/self.volume),
                    localVolumeRMS=float(np.sqrt(np.sum((J-1)**2*self.w)/self.volume)))

    def pressure_direction(self, state, v):
        if self.space == 'pointwise':
            return None
        return self.material['bulk']*cho_solve(self.Mfactor, state['D']@v.ravel())

    def coupling(self, state):
        free = self.m['free']; A = self.A[free][:, free].toarray()
        if self.space == 'pointwise':
            # Formal quadrature pressure space, not actual penalty unknowns.
            # Nonzero eigenvalues of W^.5 J A^-1 J.T W^.5 are those of
            # A^-1/2 (integral dlog.T dlog) A^-1/2, without a huge q*q matrix.
            values = eigh(state['R'], A, eigvals_only=True)
            count = self.w.size
            cutoff = max(values)*1e-10; positive = values[values > cutoff]
            nulls = count-len(positive)
            return dict(pressureSpace='FORMAL_QUADRATURE_PRESSURE_SPACE_ONLY', actualFinitePressureUnknownCount=0,
                        pressureCount=count, rank=len(positive), nullity=nulls,
                        positiveDimensionlessEigenvalues=positive, nodalGramEigenvaluesIncludingNulls=values,
                        zeroPressureEigenvalueMultiplicity=nulls, betaIncludingNulls=0. if nulls else float(np.sqrt(values[0])),
                        smallestPositiveBeta=float(np.sqrt(positive[0])), relativeRankThreshold=1e-10,
                        massMinimumEigenvalueM3=float(self.w.min()), massMaximumEigenvalueM3=float(self.w.max()), massPositive=True,
                        convention='reference H1 seminorm; quadrature L2 mass; compressed complete pressure spectrum includes null multiplicity; not an inf-sup claim for a penalty formulation')
        D = state['D'][:, free].toarray()
        S = D@solve(A, D.T, assume_a='pos')
        values, vectors = eigh(S, self.M)
        cutoff = max(values)*1e-10; rank = int(np.sum(values > cutoff)); nulls = len(values)-rank
        mass_values = eigh(self.M, eigvals_only=True)
        constant = np.ones(len(values)); c = D.T@constant
        output = dict(pressureSpace=self.space, pressureCount=len(values), rank=rank, nullity=nulls,
                      dimensionlessEigenvaluesIncludingNulls=values, betaIncludingNulls=0. if nulls else float(np.sqrt(max(0, values[0]))),
                      smallestPositiveBeta=float(np.sqrt(values[values > cutoff][0])), relativeRankThreshold=1e-10,
                      massMinimumEigenvalueM3=float(mass_values[0]), massMaximumEigenvalueM3=float(mass_values[-1]), massPositive=bool(mass_values[0] > 0),
                      constantPressureCouplingSquared=float(c@solve(A, c, assume_a='pos')/(constant@self.M@constant)),
                      convention='reference H1 displacement seminorm; full pressure mass; all free lateral DOFs; no gauge or null mode removed')
        if nulls:
            z = vectors[:, 0]; dz = D.T@z
            output.update(nullPressureWitness=z, nullWitnessMassNorm=float(z@self.M@z),
                          nullWitnessScaledCouplingSquared=float(dz@solve(A, dz, assume_a='pos')))
        return output

    def decomposition(self, state, v):
        dF = np.einsum('eni,eqna->eqia', v[self.m['tets']], self.grad)
        with parameters(self.material):
            _, C, *_ = ORIGINAL_CONSTITUTIVE(state['F'], state['pq'], activation=self.activation, tangent=True)
        fixed = float(np.einsum('eqia,eqiajb,eqjb,eq->', dF, C, dF, self.w))
        lam = state['lam']; n = state['F'][..., :, 0]/lam[..., None]
        df = dF[..., :, 0]; longitudinal = np.sum(n*df, axis=-1)
        transverse = np.sum(df*df, axis=-1)-longitudinal**2
        p = self.material; u = (lam-1)/p['activeWidth']
        curve = np.where(abs(u) < 1, (1-u*u)**2, 0.)
        prime = np.where(abs(u) < 1, -4*u*(1-u*u)/p['activeWidth'], 0.)
        active = float(np.sum(self.w*self.activation*p['sigma0']*(prime*longitudinal**2+curve/lam*transverse)))
        passive_k = p['kf']/p['b']*np.expm1(p['b']*np.maximum(lam-1, 0))
        passive_prime = np.where(lam > 1, p['kf']*np.exp(p['b']*(lam-1)), 0.)
        passive = float(np.sum(self.w*(passive_prime*longitudinal**2+passive_k/lam*transverse)))
        invd = np.einsum('eqai,eqib->eqab', np.linalg.inv(state['F']), dF)
        geometric = float(-np.sum(self.w*state['pq']*np.einsum('eqab,eqba->eq', invd, invd)))
        dlog = np.einsum('eqia,eqia->eq', state['G'], dF)
        if self.space == 'pointwise':
            volume = float(p['bulk']*np.sum(self.w*dlog*dlog)); unresolved = 0.
        else:
            db = state['D']@v.ravel(); coeff = cho_solve(self.Mfactor, db)
            volume = float(p['bulk']*db@coeff)
            unresolved = float(np.sqrt(np.sum(self.w*(dlog-coeff[self.pi]@self.L.T)**2)/self.volume))
        return dict(matrixNPerM=fixed-active-passive-geometric, passiveFiberNPerM=passive,
                    activeNPerM=active, pressurePrestressNPerM=geometric, volumeConstraintNPerM=volume,
                    unresolvedDirectionalLogJRMSPerM=unresolved, totalNPerM=fixed+volume,
                    convention='complete physical tangent; Euclidean nodal normalization; no positive shift or dropped prestress')


def replay(body, x, state, depth=2, direction=None, surface=True):
    payload = dict(mesh=body.m, positionsM=x, pressureSpace=body.space, pressurePa=None if body.space == 'pointwise' else state['p'],
                   material=body.material, activation=body.activation, depth=depth, surface=surface)
    if direction is not None:
        payload.update(direction=direction, directionalPressurePa=body.pressure_direction(state, direction))
    process = subprocess.run(['node', str(ROOT/'tools/frozen-pressure-replay.mjs')], input=json.dumps(serial(payload)),
                             text=True, capture_output=True, check=True)
    return json.loads(process.stdout)
