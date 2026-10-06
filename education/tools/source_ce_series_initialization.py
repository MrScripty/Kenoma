"""Algebra-only CE/PE/SE initialization, independently declared source-informed law.

No trajectory, release, fit, SI calibration, author code import, or old packet edit.
Execution requires a parent-owned protocol commit; --qualify is an explicit action.
Published median sigma/rho are used in declared normalized coordinates. PE kappa
has NO source-derived numeric default because Eq19 prefactor and Table3 units
require reconciliation. All qualification kappa/offsets are authored math probes.
Fast CE/parallel/whole tangents describe full-support held-population rigid moment
translation with no outflow; finite-domain jump escape is a separate reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

import mpmath as mp

SOURCE_DOI = "10.1371/journal.pcbi.1014748"
VISUAL_AUDIT_COMMIT = "64ef2727ec694f5a85ccce0eabcb708f7fcf97b7"
FORCE_ABS_GATE = mp.mpf("1e-12")
TANGENT_REL_GATE = mp.mpf("1e-8")


def scalar(value):
    """Decimal strings are preferred; do not silently repair nonfinite values."""
    out = mp.mpf(value)
    if not mp.isfinite(out):
        raise ValueError("finite scalar required")
    return out


def softplus(z):
    z = scalar(z)
    return max(z, mp.mpf("0")) + mp.log1p(mp.exp(-abs(z)))


def sigmoid(z):
    z = scalar(z)
    if z >= 0:
        return 1 / (1 + mp.exp(-z))
    a = mp.exp(z)
    return a / (1 + a)


@dataclass(frozen=True)
class SeriesParameters:
    """Fhat=T/F0, uCE=(LCE-LCEref)/gamma, eSE=(LSE-LSE0)/gamma.

    kappa: normalized FORCE prefactor, never a physical stiffness.
    u_pe0: PE rest offset in the uCE coordinate; arbitrary authored input.
    sigma: SE force prefactor /F0, rho: exponent per unit normalized extension.
    """
    kappa: object
    u_pe0: object
    sigma: object = "0.19"
    rho: object = "0.24"
    beta: object = "0.5"

    def values(self):
        k, p, s, r, b = map(scalar,
                            (self.kappa, self.u_pe0, self.sigma, self.rho, self.beta))
        if k < 0 or s <= 0 or r <= 0 or b <= 0:
            raise ValueError("require kappa>=0, sigma>0, rho>0, beta>0")
        return k, p, s, r, b


def passive_force(u_ce, parms):
    k, p, _, _, _ = parms.values()
    return k * softplus(scalar(u_ce) - p)


def passive_tangent(u_ce, parms):
    k, p, _, _, _ = parms.values()
    return k * sigmoid(scalar(u_ce) - p)


def series_force(e_se, parms):
    _, _, s, r, _ = parms.values()
    e = scalar(e_se)
    if e < 0:
        raise ValueError("nonnegative SE extension required")
    return s * mp.expm1(r * e)


def series_tangent(e_se, parms):
    _, _, s, r, _ = parms.values()
    e = scalar(e_se)
    if e < 0:
        raise ValueError("nonnegative SE extension required")
    return s * r * mp.exp(r * e)


def series_inverse(force_hat, parms):
    _, _, s, r, _ = parms.values()
    force_hat = scalar(force_hat)
    if force_hat < 0:
        raise ValueError("nonnegative force required for admissible SE extension")
    return mp.log1p(force_hat / s) / r


def validate_populations(B, N):
    B, N = scalar(B), scalar(N)
    M = 1 - B
    if not 0 <= B <= N <= 1 or not 0 <= M <= 1:
        raise ValueError("strict B/N/M domain failed; no tolerance, clipping or reset")
    return B, N, M


def source_capacity(pca):
    """Same held capacity as the source fixture: Ca in micromolar."""
    pca = scalar(pca)
    calcium = mp.power(10, 6-pca)
    capacity = 1/(1+mp.power(scalar("0.83")/calcium, scalar("3.1")))
    validate_populations("0", capacity)
    return calcium, capacity


def initialize(B, Q, N, parms, u_ce0="0", candidate=None):
    """Q=integral (1+x)n dx; preserve raw CE Q/beta and held populations.

    Fast CE/parallel/whole tangents use full-support rigid moment translation,
    with no outflow, not a derivative of truncated-domain jump transport.
    """
    B, N, M = validate_populations(B, N)
    Q, u = scalar(Q), scalar(u_ce0)
    if candidate is not None:
        candidate.update(B=B, N=N, M=M, Q=Q, u_ce0=u)
    _, _, _, _, beta = parms.values()
    ce = Q / beta
    pe = passive_force(u, parms)
    total = ce + pe
    if candidate is not None:
        candidate.update(B=B, N=N, M=M, Q=Q, u_ce0=u, force_ce=ce,
                         force_pe=pe, force_total=total)
    e = series_inverse(total, parms)
    se = series_force(e, parms)
    force_error = abs(se - ce - pe)
    if candidate is not None:
        candidate.update(e_se0=e, force_se=se, force_balance_abs=force_error)
    if force_error > FORCE_ABS_GATE:
        raise ValueError("fixed force-balance gate failed")
    fast_ce = B / beta
    fast_pe = passive_tangent(u, parms)
    fast_parallel = fast_ce + fast_pe
    fast_se = series_tangent(e, parms)
    fast_whole = fast_parallel * fast_se / (fast_parallel + fast_se)
    return dict(B=B, N=N, M=M, Q=Q, u_ce0=u, u_pe0=scalar(parms.u_pe0),
                force_ce=ce, force_pe=pe, force_total=total, force_se=se,
                e_se0=e, u_total0=u+e, force_balance_abs=force_error,
                fast_ce=fast_ce, fast_pe=fast_pe, fast_parallel=fast_parallel,
                fast_se=fast_se, fast_whole_series=fast_whole)


def source_stationary(N="1", radius="3", candidate=None):
    """Independent finite-domain conserved-M stationary integrals, no time solve.

    a=integral f/g; B=a*(1-B)*(N-B); positive smaller root.
    n=(1-B)*(N-B)*f/g. Domain matches the earlier CE source fixture.
    """
    N, R = scalar(N), scalar(radius)
    if not 0 <= N <= 1 or R <= 0:
        raise ValueError("require 0<=N<=1 and positive domain radius")
    f1, g1, g2, E1, E2, w = map(scalar, ("52", "4", "21.1", "2", "-0.6", "0.3"))

    def attachment(x):
        return f1 * mp.exp(-x*x/(2*w*w)) / (mp.sqrt(2*mp.pi)*w)

    def detachment(x):
        return g1*mp.exp(-E1*x) + g2*mp.exp(-E2*x)

    def fg(x):
        return attachment(x)/detachment(x)

    knots = [-R, -R/2, -R/4, mp.mpf("0"), R/4, R/2, R]
    a = mp.quad(fg, knots)
    if candidate is not None:
        candidate.update(N=N, radius=R, integral_f_over_g=a)
    c = 1 + a*(N+1)
    disc = c*c - 4*a*a*N
    B = 2*a*N/(c+mp.sqrt(disc))
    B, N, M = validate_populations(B, N)
    if candidate is not None:
        candidate.update(B=B, N=N, M=M)
    pref = M*(N-B)
    B_integrated = mp.quad(lambda x: pref*fg(x), knots)
    if candidate is not None:
        candidate.update(B_integrated=B_integrated)
    Q = mp.quad(lambda x: (1+x)*pref*fg(x), knots)
    if candidate is not None:
        candidate.update(Q=Q)
    second = mp.quad(lambda x: (1+x)**2*pref*fg(x), knots)
    variance = second/B-(Q/B)**2 if B else mp.mpf("0")
    population_balance = abs(B-a*M*(N-B))
    # Recompute free fractions from the independently integrated attached mass.
    kinetic_pref = (1-B_integrated)*(N-B_integrated)
    kinetic_max = max(abs(kinetic_pref*attachment(x)
                          -detachment(x)*pref*fg(x))
                      for x in mp.linspace(-R, R, 129))
    if candidate is not None:
        candidate.update(B=B, N=N, M=M, Q=Q, integral_f_over_g=a,
                         population_balance_abs=population_balance,
                         kinetic_residual_max_abs=kinetic_max,
                         attached_integral_abs=abs(B_integrated-B),
                         force_moment_variance=variance, radius=R)
    if (variance < 0 or abs(B_integrated-B) > FORCE_ABS_GATE
            or population_balance > FORCE_ABS_GATE or kinetic_max > FORCE_ABS_GATE):
        raise ValueError("stationary density/moment gate failed")
    return dict(B=B, N=N, M=M, Q=Q, integral_f_over_g=a,
                raw_force_ce=Q/scalar("0.5"),
                population_balance_abs=population_balance,
                kinetic_residual_max_abs=kinetic_max,
                kinetic_residual_sample_count=129,
                attached_integral_abs=abs(B_integrated-B),
                force_moment_variance=variance, radius=R)


def relative_error(actual, expected):
    expected = scalar(expected)
    if expected == 0:
        return abs(actual-expected)
    return abs(actual-expected)/abs(expected)


def _numeric_receipt(value):
    if isinstance(value, dict):
        return {k: _numeric_receipt(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_numeric_receipt(v) for v in value]
    if isinstance(value, mp.mpf):
        return mp.nstr(value, 55)
    return value


def new_receipt(protocol_commit):
    """Build a RUNNING receipt before any qualification calculation."""
    return dict(status="RUNNING",
                scope="algebra-only dimensionless initializer; no coupled trajectory",
                parent_protocol_commit=protocol_commit, precision_decimal_digits=60,
                runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_doi=SOURCE_DOI, visual_audit_commit=VISUAL_AUDIT_COMMIT,
                force_abs_gate="1e-12", tangent_relative_gate="1e-8",
                pe_kappa_status="unresolved source mapping; every numeric kappa here is authored",
                fast_tangent_scope="full-support held-population rigid moment translation; no outflow",
                authored_kappa_probes=["0", "0.002", "0.02"],
                authored_offset_probes=["-10", "0", "10"],
                expected_stationary_condition_count=3,
                expected_initializer_case_count=27,
                expected_invalid_input_rejection_count=56,
                expected_se_boundary_probe_count=4,
                stationary_condition_count=0, stationary_conditions=[],
                initializer_case_count=0, cases=[],
                invalid_input_rejection_count=0, invalid_input_rejections=[],
                se_boundary_probe_count=0, se_boundary_probes=[],
                physical_F0_gamma_area="symbolic/unselected",
                current_context=dict(phase="protocol-validation"),
                current_candidate=None, failure=None,
                export_semantics="exclusive new output; incremental checkpoints; preserve FAILED partial receipt")


def qualify(protocol_commit, receipt=None, on_update=None):
    """Authored algebra probes only. Call only after parent protocol pin.

    A caller-provided receipt retains completed and current partial probes on an
    exception. The CLI supplies exception/traceback capture and exclusive export.
    """
    if receipt is None:
        receipt = new_receipt(protocol_commit)

    def checkpoint(context=None, candidate=None, replace_candidate=False):
        if context is not None:
            receipt["current_context"] = context
        if replace_candidate:
            receipt["current_candidate"] = candidate
        if on_update is not None:
            on_update(receipt)

    checkpoint(dict(phase="protocol-validation"))
    if len(protocol_commit) != 40 or any(c not in "0123456789abcdef" for c in protocol_commit):
        raise ValueError("exact parent protocol commit required")
    with mp.workdps(60):
        stationary_conditions = receipt["stationary_conditions"]
        for pca in ("4.5", "6.1"):
            condition = "pCa_"+pca
            candidate = dict(condition=condition, pca=pca)
            context = dict(phase="stationary", condition=condition, pca=pca)
            checkpoint(context, candidate, True)
            calcium, N = source_capacity(pca)
            candidate.update(calcium_microM=calcium, N=N)
            checkpoint()
            stationary = source_stationary(N, candidate=candidate)
            stationary.update(condition=condition, pca=pca, calcium_microM=calcium)
            candidate.update(stationary)
            stationary_conditions.append(candidate)
            receipt["stationary_condition_count"] = len(stationary_conditions)
            checkpoint(dict(phase="stationary-complete", condition=condition), None, True)
        condition = "N1_normalization_audit"
        candidate = dict(condition=condition, N="1", pca=None, calcium_microM=None)
        checkpoint(dict(phase="stationary", condition=condition, N="1"), candidate, True)
        stationary = source_stationary("1", candidate=candidate)
        stationary.update(condition=condition, pca=None, calcium_microM=None)
        candidate.update(stationary)
        stationary_conditions.append(candidate)
        receipt["stationary_condition_count"] = len(stationary_conditions)
        checkpoint(dict(phase="stationary-complete", condition=condition), None, True)
        cases = receipt["cases"]
        h = mp.mpf("1e-15")
        for stationary in stationary_conditions:
            B, Q, N = (stationary[k] for k in ("B", "Q", "N"))
            for kappa in ("0", "0.002", "0.02"):
                for offset in ("-10", "0", "10"):
                    context = dict(phase="initializer", condition=stationary["condition"],
                                   kappa=kappa, authored_offset_probe=offset,
                                   B=B, Q=Q, N=N, M=stationary["M"])
                    candidate = dict(context)
                    checkpoint(context, candidate, True)
                    parms = SeriesParameters(kappa, offset)
                    rec = initialize(B, Q, N, parms, candidate=candidate)
                    candidate.update(rec)
                    u, e = rec["u_ce0"], rec["e_se0"]
                    fd_pe = (passive_force(u+h, parms)-passive_force(u-h, parms))/(2*h)
                    candidate["finite_difference_pe"] = fd_pe
                    fd_se = (series_force(e+h, parms)-series_force(e-h, parms))/(2*h)
                    candidate["finite_difference_se"] = fd_se
                    beta = scalar(parms.beta)
                    # Full-support held-population rigid moment translation:
                    # no kinetics or outflow; not truncated-domain jump transport.
                    fd_parallel = (((Q+B*h)/beta+passive_force(u+h, parms))
                                   -((Q-B*h)/beta+passive_force(u-h, parms)))/(2*h)
                    candidate["finite_difference_parallel"] = fd_parallel
                    errors = dict(pe=relative_error(fd_pe, rec["fast_pe"]),
                                  se=relative_error(fd_se, rec["fast_se"]),
                                  parallel=relative_error(fd_parallel, rec["fast_parallel"]))
                    candidate.update(kappa=scalar(kappa), tangent_relative_errors=errors)
                    checkpoint()
                    if any(v > TANGENT_REL_GATE for v in errors.values()):
                        raise ValueError("fixed tangent finite-difference gate failed")
                    candidate["inverse_abs"] = abs(series_inverse(rec["force_se"],parms)-e)
                    checkpoint()
                    if candidate["inverse_abs"] > FORCE_ABS_GATE:
                        raise ValueError("fixed inverse gate failed")
                    cases.append(candidate)
                    receipt["initializer_case_count"] = len(cases)
                    checkpoint(dict(context, phase="initializer-complete"), None, True)
        if len(cases) != 27:
            raise ValueError("declared 27-case initializer count failed")
        rejections = receipt["invalid_input_rejections"]

        def require_rejection(label, call, inputs):
            candidate = dict(case=label, inputs=inputs)
            checkpoint(dict(phase="invalid-input-rejection", case=label), candidate, True)
            try:
                result = call()
            except ValueError as error:
                candidate["reason"] = str(error)
                rejections.append(candidate)
                receipt["invalid_input_rejection_count"] = len(rejections)
                checkpoint(dict(phase="rejection-complete", case=label), None, True)
            else:
                candidate["unexpected_result"] = _numeric_receipt(result)
                raise ValueError("invalid input accepted: "+label)

        for B_bad, N_bad in (("-0.1", "1"), ("1.1", "1"), ("0.6", "0.5"), ("0", "1.1")):
            require_rejection("population_B="+B_bad+"_N="+N_bad,
                              lambda: validate_populations(B_bad, N_bad),
                              dict(B=B_bad, N=N_bad))
        base = dict(kappa="0.002", u_pe0="0", sigma="0.19", rho="0.24", beta="0.5")
        invalid_parameters = [("kappa", "-0.001")]
        invalid_parameters += [(field, value) for field in ("sigma", "rho", "beta")
                               for value in ("0", "-1")]
        invalid_parameters += [(field, value) for field in base
                               for value in ("nan", "inf", "-inf")]
        for field, value in invalid_parameters:
            values = dict(base, **{field: value})
            require_rejection("parameter_"+field+"="+value,
                              lambda: SeriesParameters(**values).values(), values)
        parms = SeriesParameters("0.002", "0")
        invalid_domains = [
            ("negative_SE_force", lambda: series_inverse("-1", parms), dict(force_hat="-1")),
            ("negative_SE_extension_force", lambda: series_force("-1", parms), dict(e_se="-1")),
            ("negative_SE_extension_tangent", lambda: series_tangent("-1", parms), dict(e_se="-1")),
            ("negative_initial_total_force", lambda: initialize("0.2", "-1", "1",
                                                               SeriesParameters("0", "0")),
             dict(B="0.2", Q="-1", N="1", kappa="0", u_pe0="0")),
            ("zero_radius", lambda: source_stationary(radius="0"), dict(radius="0")),
            ("negative_radius", lambda: source_stationary(radius="-1"), dict(radius="-1")),
        ]
        for label, call, inputs in invalid_domains:
            require_rejection(label, call, inputs)
        for value in ("nan", "inf", "-inf"):
            nonfinite_calls = [
                ("B", lambda: validate_populations(value, "1")),
                ("N", lambda: validate_populations("0", value)),
                ("Q", lambda: initialize("0.2", value, "1", parms)),
                ("uCE", lambda: initialize("0.2", "0.2", "1", parms, value)),
                ("force", lambda: series_inverse(value, parms)),
                ("extension", lambda: series_force(value, parms)),
                ("pCa", lambda: source_capacity(value)),
                ("radius", lambda: source_stationary(radius=value)),
            ]
            for field, call in nonfinite_calls:
                require_rejection("nonfinite_"+field+"="+value, call, {field: value})
        if len(rejections) != 56:
            raise ValueError("declared invalid-input rejection count failed")
        boundary_probes = receipt["se_boundary_probes"]
        for T in ("0", "1e-20", "1", "100"):
            candidate = dict(input_force=scalar(T))
            checkpoint(dict(phase="se-boundary-probe", input_force=T), candidate, True)
            parms = SeriesParameters("0.002", "0")
            candidate["inverse_extension"] = series_inverse(T, parms)
            candidate["result_force"] = series_force(candidate["inverse_extension"], parms)
            candidate["roundtrip_abs"] = abs(candidate["result_force"]-scalar(T))
            checkpoint()
            if candidate["roundtrip_abs"] > FORCE_ABS_GATE:
                raise ValueError("SE inverse boundary probe failed")
            boundary_probes.append(candidate)
            receipt["se_boundary_probe_count"] = len(boundary_probes)
            checkpoint(dict(phase="se-boundary-complete", input_force=T), None, True)
        receipt["status"] = "PASSED"
        checkpoint(dict(phase="complete"), None, True)
        return _numeric_receipt(receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualify", action="store_true")
    parser.add_argument("--protocol-commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.qualify or args.protocol_commit is None:
        parser.error("explicit --qualify and committed --protocol-commit are required")
    # Reserve the output before any qualification, including protocol validation.
    # Rewrites below are only checkpoints in this exclusively created new file.
    handle = None
    if args.output is not None:
        try:
            handle = args.output.open("x", encoding="utf-8")
        except OSError as error:
            parser.error("cannot exclusively create output before qualification: "+str(error))
    receipt = dict(status="RUNNING", parent_protocol_commit=args.protocol_commit,
                   current_context=dict(phase="receipt-initialization"),
                   current_candidate=None, failure=None)
    failed = False

    def export(current):
        payload = json.dumps(_numeric_receipt(current), indent=2)+"\n"
        if handle is not None:
            handle.seek(0)
            handle.write(payload)
            handle.truncate()
            handle.flush()
            os.fsync(handle.fileno())

    try:
        receipt.update(new_receipt(args.protocol_commit))
        export(receipt)
        qualify(args.protocol_commit, receipt=receipt, on_update=export)
    except BaseException as error:
        failed = True
        receipt["status"] = "FAILED"
        receipt["failure"] = dict(type=type(error).__name__, message=str(error),
                                  traceback=traceback.format_exc())
    finally:
        try:
            export(receipt)
            if handle is None:
                print(json.dumps(_numeric_receipt(receipt), indent=2))
        finally:
            if handle is not None:
                handle.close()
    if failed:
        print("Qualification failed; partial receipt retained: "+receipt["failure"]["message"],
              file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
