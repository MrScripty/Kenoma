# Source-informed conserved-head CE step/reversal protocol

Declared before execution on 2026-10-06. **This separately bounded dimensionless kinetic prerequisite does not execute the requested finite-series loaded mechanical comparison.** SI force/area calibration and coherent series/passive initialization remain unresolved in the [calibration audit](calibration-source-reconciliation.md) and [convention memo](article-code-convention-decision.md). No production mechanics, anatomical coefficient, book equation or Lean statement changes. Frozen evidence, failures and the anatomical force gate1e-4 N remain unchanged.

## Selected source and departures

Use the original visually inspected PLOS [Tables 2/3 and equations](original-plos-table-visual-audit.md), additive audit commit `64ef2727ec694f5a85ccce0eabcb708f7fcf97b7`, publisher PDF SHA256 `20f16f9890d1ff1d65cb8e75d38f24e7c2b5a73779052825faa36f45a78531cf`. The table's noncooperative two-state column supplies componentwise medians f1=52/s, g1=4/s, g2=21.1/s, E2=-.6, nH=3.1, Ca50=.83µM. Fixed choices E1=2, beta=.5, dps=10nm and w=3nm give normalized w=.3. Preserve the printed reciprocal-width formula/unit discrepancies in the original audit; the normalized width here uses the explicit printed length values, not that radical.

No parameter from the inspected individual MAT is used. A componentwise median is not an observed specimen or a joint fit. Adopt the pinned discretized code's conserved two-state population M=1-B, while adopting the article's **raw** force Q/beta. This hybrid is explicitly an independently declared source-informed equation fixture, not exact article or pinned-code reproduction. Its [held-N positive operator](source-two-state-operator-protocol.md) has already passed independent vector-root qualification.

```
n_t = f(x)(1-B)(N-B) - g(x)n,
B = integral n dx, Q = integral (1+x)n dx,
f = 52 exp(-x²/(2*.3²))/(sqrt(2pi)*.3),
g = 4 exp(-2x) + 21.1 exp(+.6x),
N = 1/[1+(.83µM / 10^(6-pCa)µM)^3.1],
M=1-B, Fhat=Q/.5.
```

N is held fixed for each pCa throughout; the source5ms activation lag/cooperative recruitment are absent. Overlap is fixed one near the model reference. Direct CE input delta is in normalized link-strain x. No physical gamma, human sarcomere/fascicle count, specimen area, SI force/head capacity, tendon, PE or SE is selected. The force normalizer remains beta=.5; baseline force is reported, never reset to one. PE/SE are absent, so this experiment makes no whole-fiber length/force or series-stiffness claim.

## History and refinements

Initialize each grid/calcium condition at its OWN closed conserved-head equilibrium, with absolute full kinetic residual L1<=1e-10/s. At t=0 apply a direct-CE displacement delta; hold to t=.2s; apply -delta to return the prescribed CE length; hold to t=1s. Fixed delta=(+.001,-.001,+.0005,-.0005), pCa=(4.5,6.1), strain domain R=(2.4,3), dx=(.04,.02,.01), timestep h=(.004,.002,.001)s give **144 cases**. These small authored displacements are not measured waveforms or physiological ranges.

Matched samples are equilibrium/t=0-before and t=0-after, then .008,.02,.04,.1,.2-before,.2-after,.3,.5,1 seconds. Duplicate jump times have distinct states. Do not reset distributions at the reversal or mechanical solves; do not extend the terminal hold. Save every matched bin distribution, all grid/rate vectors, forces, attached fractions and elastic energies. State/time advance only after strict population bounds and full BE residual gates pass; the [operator's gates](source-two-state-operator-protocol.md) remain fixed. Terminal full kinetic residual L1 must be <=1e-10/s at1s, otherwise preserve the failed case without a longer hold.

## Transport and elastic-work ledger

Use conservative adjacent-bin upwind interpolation for |delta|<dx; escaped attached mass detaches into the implicit free-head pool, with signed force moment and elastic energy separately recorded at the escaped discrete destination center. No clipping or reattachment correction hides boundary loss. With Ehat=sum(.5(1+x)^2 pi)/beta, each jump must satisfy these discrete identities to absolute2e-12:

```
Delta Fhat = B*delta/beta - escapedMoment/beta,
Delta Ehat = Fhat_before*delta + B*delta²/(2beta)
             + B*|delta|*(dx-|delta|)/(2beta) - escapedEnergy/beta.
```

The positive third term is **interpolation work**, not physical elastic input work. Report it and its dx refinement, rather than claiming a closed physical work balance. Reaction-energy changes are supplied by the kinetic law; chemical-energy accounting is not modeled. The discrete ledger establishes internal arithmetic, not thermodynamic or anatomical credibility. Record mass accounting and moment/energy errors at both jumps.

## Independent matched-time reference

Independently implement grid/calcium, mp60 analytic equilibrium, RHS and transport. The saved initial state must agree with the independent equilibrium to maximum absolute2e-12 and have full RHS L1<=1e-10/s. Independently constructed grid/rate vectors must agree to maximum absolute difference divided by max(1,largest magnitude)<=1e-12. Integrate the original nonlinear BIN ODE with SciPy DOP853, rtol1e-11, atol1e-14, using two fixed max_step values .001 and .0005s. Each reference evolves its OWN distribution through both segments and its OWN reversal; no reset from BE states. Strict finite/nonnegative bins and B<=N must hold at its accepted solver nodes and all matched samples. No solver retry or clipping follows failure. Reference-resolution matched-state L1 difference must be <=1e-10 and force difference <=2e-10 before it serves as an accuracy reference.

Compare BE states/forces at identical physical times to the finer independent bin-ODE reference. Report absolute error and error normalized by the initial displacement perturbation, with timestep-halving ratios. Report bin/extent comparisons and interpolation work separately; a finite-bin reference does not prove continuous-strain convergence. Assess observed orders without changing pass gates or inventing a physiological error target. A small terminal residual alone does not qualify transients. Preserve raw failed cases and partial receipts before diagnosis.

All evidence belongs in the new `review/conserved-ce-trajectory/` packet. Precommit this protocol and runner before execution; retain raw logs, NPZ states, independent reference/audit, rendered summary and hash manifest. Passing this prerequisite does not erase stationary negative witnesses, compression/contact failure, source calibration uncertainty or the unqualified dense anatomical lift/release trajectory.
