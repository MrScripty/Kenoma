"""Independent held-N two-state bin operator, not an anatomical constitutive law.

Conserved free heads M=1-B; free sites q=N-B. No clipping, state reset,
nonlinear iteration, physical scale or time advancement occurs here.
"""
import math

import numpy as np

RESIDUAL_GATE = 1e-12
MASS_GATE = 2e-12


def _inputs(F, g, N, p=None):
    F, g = np.asarray(F, dtype=float), np.asarray(g, dtype=float)
    if F.ndim != 1 or F.size == 0 or g.shape != F.shape:
        raise ValueError('rates must be nonempty matching vectors')
    if not np.all(np.isfinite(F)) or not np.all(np.isfinite(g)):
        raise ValueError('nonfinite rates')
    if np.any(F < 0) or np.any(g <= 0):
        raise ValueError('negative attachment or nonpositive detachment')
    if not np.isfinite(N) or not 0 <= N <= 1:
        raise ValueError('capacity outside [0,1]')
    if p is not None:
        p = np.asarray(p, dtype=float)
        if p.shape != F.shape or not np.all(np.isfinite(p)) or np.any(p < 0):
            raise ValueError('invalid bin population')
        if math.fsum(p) > N:
            raise ValueError('old attached population exceeds capacity')
    return F, g, float(N), p


def _root(V, c, W):
    if not all(math.isfinite(z) and z >= 0 for z in (V, c, W)):
        raise ValueError('invalid root coefficients')
    b = 1 + V*c
    cross = 2*math.sqrt(V)*math.sqrt(W)
    disc = math.hypot(b, cross)
    denominator = .5*b + .5*disc
    if not all(math.isfinite(z) for z in (b, cross, disc, denominator)):
        raise ValueError('nonfinite root intermediate')
    return W/denominator


def rhs(p, N, F, g):
    B = math.fsum(p)
    return F*((1-B)*(N-B)) - g*p


def jacobian(p, N, F, g):
    B = math.fsum(p)
    return -np.diag(g) - np.asarray(F)[:, None]*(1+N-2*B)


def _candidate(p, q, N):
    if not np.all(np.isfinite(p)) or np.any(p < 0) or not math.isfinite(q):
        raise ValueError('nonfinite or negative candidate; no clipping')
    B = math.fsum(p)
    if not 0 <= B <= N or not 0 <= q <= N or 1-B < 0:
        raise ValueError('candidate exceeds strict population bounds')
    if abs(B+q-N) > MASS_GATE:
        raise ValueError('free-site accounting gate failed')


def equilibrium(F, g, N):
    F, g, N, _ = _inputs(F, g, N)
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            ratios = F/g
            I = math.fsum(ratios)
            q = _root(I, 1-N, N)
            p = ratios*(q*(1-N+q))
            _candidate(p, q, N)
            residual = rhs(p, N, F, g)
            scale = max(1., math.fsum(F), float(np.max(g))*N)
            if not math.isfinite(scale) or np.max(np.abs(residual))/scale > RESIDUAL_GATE:
                raise ValueError('equilibrium residual gate failed')
    except (FloatingPointError, OverflowError) as exc:
        raise ValueError('nonfinite equilibrium arithmetic') from exc
    return p


def step(p, N, F, g, h):
    F, g, N, p = _inputs(F, g, N, p)
    if not np.isfinite(h) or h <= 0:
        raise ValueError('invalid positive timestep')
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            hg, hF = h*g, h*F
            a = 1/(1+hg)
            B = math.fsum(p)
            # Positive accumulation retains the newly detached increment at saturation.
            W = (N-B) + math.fsum((hg/(1+hg))*p)
            V = math.fsum(a*hF)
            q = _root(V, 1-N, W)
            candidate = a*p + (a*hF)*(q*(1-N+q))
            _candidate(candidate, q, N)
            residual = candidate-p-h*rhs(candidate, N, F, g)
            scale = max(1., N, h*math.fsum(F), h*float(np.max(g))*N)
            if not math.isfinite(scale) or np.max(np.abs(residual))/scale > RESIDUAL_GATE:
                raise ValueError('full backward-Euler residual gate failed')
    except (FloatingPointError, OverflowError) as exc:
        raise ValueError('nonfinite step arithmetic') from exc
    return candidate
