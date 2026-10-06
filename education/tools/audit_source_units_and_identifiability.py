"""Exact conditional units/topology audit of smooth elastic forms; no calibration or solve.

The PE identity applies to the fitting/soft branch, not the complete piecewise
runtime approximation. Abstract sigma/rho map to code kse0/kse conditionally;
published coefficient parity is not asserted.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import traceback

import sympy as sp


@dataclass(frozen=True)
class Dimension:
    mass: int = 0
    length: int = 0
    time: int = 0

    def __mul__(self, other):
        return Dimension(self.mass+other.mass,self.length+other.length,self.time+other.time)

    def __truediv__(self, other):
        return Dimension(self.mass-other.mass,self.length-other.length,self.time-other.time)

    def power(self, exponent):
        return Dimension(self.mass*exponent,self.length*exponent,self.time*exponent)


ONE=Dimension()
LENGTH=Dimension(length=1)
FORCE=Dimension(mass=1,length=1,time=-2)
AREA=LENGTH.power(2)
STRESS=FORCE/AREA
STIFFNESS=FORCE/LENGTH
ENERGY=FORCE*LENGTH


def require_dimension(actual,expected):
    if actual != expected:
        raise ValueError(f'dimension {actual} does not equal required {expected}')


def exponential_dimension(argument):
    require_dimension(argument,ONE)
    return ONE


def run(receipt):
    C,ell,k,K,sigma,rho,lo,u0,L,Lse,Lse0=sp.symbols(
        'C ell k K sigma rho Lorigin u0 L Lse Lse0',positive=True)
    old,new,eps=sp.symbols('Gamma_old Gamma_new epsilon',positive=True)
    Ns,dps,sarc,Lref,H,kcb,B,Q,E0,lam,J,A0,V,lf,angle=sp.symbols(
        'Ns dps sarc Lref H kCB B Q E0 lambda J A0 V lf_opt alpha',positive=True)

    def passed(label,actual,expected):
        receipt['currentCheck']=label
        residual=sp.simplify(actual-expected)
        if residual != 0:
            receipt['failedExpression']=str(residual)
            raise ValueError('exact symbolic identity failed: '+label)
        receipt['passedIdentities'].append(label)

    gamma=2*Ns*dps
    passed('serial geometry gives relative-coordinate ratio',
           (Lref/gamma).subs(Lref,Ns*sarc),sarc/(2*dps))
    u=(L-lo)/ell
    pe=C*k/K*sp.log(1+sp.exp(K*(u-u0)))
    se=C*sigma*(sp.exp(rho*(Lse-Lse0)/ell)-1)
    passed('PE derivative converts to N per metre',sp.diff(pe,L),
           C*k/ell/(1+sp.exp(-K*(u-u0))))
    passed('SE derivative converts to N per metre',sp.diff(se,Lse),
           C*sigma*rho/ell*sp.exp(rho*(Lse-Lse0)/ell))
    pe_old=C*k/K*sp.log(1+sp.exp(K*(old*eps-u0)))
    pe_new=pe_old.subs({k:k*old/new,K:K*old/new,old:new,u0:u0*new/old},simultaneous=True)
    passed('smooth PE curve invariant under coordinated re-expression',pe_new,pe_old)
    se_old=C*sigma*(sp.exp(rho*old*eps)-1)
    se_new=se_old.subs({rho:rho*old/new,old:new},simultaneous=True)
    passed('full SE curve invariant under coordinated re-expression',se_new,se_old)
    passed('PE asymptotic slope conversion',sp.limit(sp.diff(pe,L),L,sp.oo),C*k/ell)
    width=ell/K
    passed('PE physical argument has declared smoothing width',K*(u-u0),
           (L-(lo+ell*u0))/width)
    T=H*kcb*dps*Q
    Acurrent=A0*J/lam
    passed('Cauchy from nominal force area',T/Acurrent,lam/J*(T/A0))
    passed('equal force from nominal and current stress',(T/Acurrent)*Acurrent,(T/A0)*A0)
    pcsa=V/lf
    fcsa=pcsa*sp.cos(angle)
    stress=sp.Symbol('specific_tension',positive=True)
    passed('pennation projection occurs once',stress*fcsa,stress*pcsa*sp.cos(angle))
    # In this block L is a physical length increment, not an absolute length.
    # E0=integral .5*(1+x)**2*n dx; Q=integral (1+x)*n dx; B=integral n dx.
    # Populations held, uniform serial strain, full support and no boundary loss.
    delta=L/gamma
    energy=2*Ns*H*kcb*dps**2*(E0+Q*delta+B*delta**2/2)
    translated_force=H*kcb*dps*(Q+B*delta)
    passed('serial link energy derivative is transmitted force',sp.diff(energy,L),translated_force)
    passed('held-head fast CE slope',sp.diff(translated_force,L),H*kcb*B/(2*Ns))
    assert len(receipt['passedIdentities'])==12

    require_dimension(LENGTH/ONE,LENGTH)
    require_dimension(FORCE/LENGTH,STIFFNESS)
    require_dimension(FORCE/AREA,STRESS)
    require_dimension(STIFFNESS*LENGTH.power(2),ENERGY)
    exponential_dimension((ONE*LENGTH)/LENGTH)
    require_dimension(FORCE*ONE/ONE,FORCE)
    require_dimension(FORCE*ONE/LENGTH,STIFFNESS)
    receipt['validDimensions']=['physical gamma length','force slope N/m','stress Pa',
        'serial link energy J','normalized SE exponent','PE force prefactor N','PE slope N/m']
    errors=[('Gamma substituted for physical gamma in exponent',lambda:exponential_dimension(LENGTH/ONE)),
        ('Eq19 physical stiffness used as force prefactor without length',lambda:require_dimension(STIFFNESS*ONE,FORCE)),
        ('dimensional inverse-length rho used with normalized extension',lambda:exponential_dimension((ONE/LENGTH)*(LENGTH/LENGTH))),
        ('force treated as stress without area',lambda:require_dimension(FORCE,STRESS))]
    for label,check in errors:
        receipt['currentCheck']=label
        try:
            check()
        except ValueError as error:
            receipt['intendedDimensionRejections'].append(dict(label=label,error=str(error)))
        else:
            raise ValueError('dimension misuse was accepted: '+label)
    assert len(receipt['intendedDimensionRejections'])==4
    wrong_serial=sp.simplify(Ns*translated_force-sp.diff(energy,L))
    wrong_pennation=sp.simplify(stress*pcsa*sp.cos(angle)**2-stress*fcsa)
    assert wrong_serial != 0 and wrong_pennation != 0
    receipt['dimensionallyValidMechanicalCounterexamples']=[
        dict(label='multiply transmitted force by serial count',residual=str(wrong_serial)),
        dict(label='apply pennation cosine twice',residual=str(wrong_pennation))]
    head_stiffness=sp.Rational(1,2)*sp.Rational(1,10**12)/sp.Rational(1,10**9)
    stroke=sp.Rational(1,10**8)
    head_force=head_stiffness*stroke
    reference_sarc=sp.Rational(26,10**7)
    Gamma=reference_sarc/(2*stroke)
    assert head_force==sp.Rational(5,10**12) and Gamma==130
    receipt['sourceAssumptionUnitIllustrations']=dict(headStiffnessNPerM=str(head_stiffness),
        assumedStrokeM=str(stroke),assumedHeadForceN=str(head_force),
        sourceReferenceSarcomereM=str(reference_sarc),conditionalGamma=str(Gamma),
        status='source model/coordinate illustrations; no individual or human force calibration')
    receipt['conditionalDerivedMap']=dict(forceMultiplier='C=Fref*Fscale [N]',
        internalLengthScale='ell=Lref/Gamma [m]',PEForcePrefactor='C*kpe/K [N]',
        PEWidth='ell/K [m]',PEAsymptoticSlope='C*kpe/ell [N/m]',
        SEForcePrefactor='C*sigma [N]',SEExponentPerMetre='rho/ell [1/m]',
        elasticScope='smooth PE fitting/soft branch; not complete piecewise runtime parity',
        SECodeNames='conditional sigma=kse0, rho=kse; no published coefficient parity',
        headForce='H*kCB*dps*Q [N]; no serial-count force multiplier',
        nominalToCauchy='Cauchy=(lambda/J)*nominal; area convention required')
    receipt['currentCheck']=None
    receipt['result']='PASS_EXACT_CONDITIONAL_UNIT_AND_TOPOLOGY_AUDIT'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol-commit',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    receipt=dict(result='RUNNING',protocolCommit=args.protocol_commit,
        sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        method='exact SymPy identities and integer SI dimension exponents; no floating reference comparisons',
        sympyVersion=sp.__version__,passedIdentities=[],intendedDimensionRejections=[],
        physicalCalibrationSelected=False,kineticOrAnatomicalSolveExecuted=False,
        missingPhysicalInputs=['same-preparation reference force/stress and denominator',
            'paired area and configuration if converting stress to force',
            'individual reference length/serial geometry',
            'passive/tare convention and version-compatible PE/SE parameters'])
    # Reserve only a new receipt before the audit; preserve partial checks on error.
    with args.output.open('x') as handle:
        try:
            if len(args.protocol_commit)!=40 or any(c not in '0123456789abcdef' for c in args.protocol_commit):
                raise ValueError('full precommitted protocol identity required')
            run(receipt)
        except BaseException as error:
            receipt['result']='FAIL_EXACT_CONDITIONAL_UNIT_AND_TOPOLOGY_AUDIT'
            receipt['failure']=dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc())
            raise
        finally:
            json.dump(receipt,handle,indent=2);handle.write('\n');handle.flush()
            print(json.dumps(receipt))


if __name__=='__main__':
    main()
