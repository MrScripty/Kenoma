# Continuous-strain CE reference: pre-execution protocol

Declared 2026-10-06 on a successor of frozen milestone `154d805386bdbe8b2c950af3d883c2ae54c376a8`. Execute only after the failed-case export correction and its negative test pass and this protocol plus reference source are committed. Preserve all old source, states, failures, renders and thresholds. Production anatomy, lab/book claims and Lean remain unchanged.

## Precise model and input

Use the SAME independently declared conserved-head source-informed model as the [previous CE protocol](conserved-ce-trajectory-protocol.md): publication componentwise medians f1=52/s,g1=4/s,g2=21.1/s,E1=2,E2=-.6,w=.3,beta=.5,nH=3.1,Ca50=.83µM; held N=1/[1+(.83/10^(6-pCa))^3.1], overlap1, M=1-B and raw force Fhat=Q/beta. The [original PLOS pixel audit](original-plos-table-visual-audit.md) preserves parameter provenance and printed discrepancies. No individual-fit coefficients, physical force/area or human geometry are supplied.

On strain domain D=[-R,R], the density and moments are

```
n_t(x) = f(x)(1-B)(N-B) - g(x)n(x),
B = integral_D n(x) dx,
Fhat = integral_D (1+x)n(x) dx / beta,
Ehat = integral_D .5(1+x)^2 n(x) dx / beta.
```

n is density, not a bin mass; its point values need not be <=N. Require nonnegative finite densities and strict 0<=B<=N<=1. At a displacement delta use exact evaluation n_new(x)=n_old(x-delta) when BOTH x and x-delta lie in D, with zero outside that support. Escaped attached density detaches into the implicit free-head pool; no clipping, rescaling or reattachment correction follows. M=1-B and free sites N-B are distinct capacities.

Initialize at each quadrature's own stationary conserved-head state. At0s apply delta; hold to .2s; apply -delta; hold to1s, without a state reset. Match the 11 prior samples including both sides of0/.2s. Select R=(2.4,3), pCa=(4.5,6.1), delta=(+.001,-.001,+.0005,-.0005). These small displacements are authored mathematical probes, not measured waveforms.

## Continuous strain representation and independent translation

Use Gauss-Legendre quadrature with node counts **200,400,800**, separately for each D. Density evolves at the quadrature points, with B calculated ONLY from main nodes and weights. Attachment is pointwise Gaussian density, not Gaussian bin integrals. This is a continuous-strain function reference qualified by quadrature refinement; it is distinct from the retained midpoint-detachment/bin-remap model.

During the first segment evolve auxiliary densities at z=x+delta, with their OWN f(z),g(z), driven by the SAME main B. Initialize them from the exactly translated stationary function; keep z outside D identically zero. At reversal, their endpoint values give n_pre(x+delta) directly at the main nodes. No strain interpolation, finite-bin shift, BE reset or equilibrium reset supplies the reversal state. The second segment evolves that new main density.

Also evolve **32 fixed Gauss-Legendre points** in the reversal's escaping SOURCE strip, driven by the same main B. Their values provide independently integrated escaped mass, SIGNED target force moment and nonnegative elastic energy. The first jump's stationary escape integrals are evaluated independently with adaptive quadrature epsabs=epsrel=1e-12. Directly integrate loss rather than infer its sign from the subtraction of nearly equal total moments. Record quadrature accounting error separately.

## Fixed integration and acceptance criteria

For every parameter/domain/node-count condition integrate the original coupled density ODE with DOP853, rtol1e-11, atol1e-14, and TWO fixed max_step values .001 and .0005s. This gives **96 reference histories**: 16 domain/calcium/displacement groups ×3 node counts ×2 time resolutions. No retry, changed initial guess, longer terminal hold, clipping or altered tolerance follows a failure. The terminal time is exactly1s. Check strict finite/nonnegative main, auxiliary and escaping-strip densities and 0<=B<=N at ALL accepted solver nodes and all matched states.

Fixed gates, declared before the new run:

| Check | Gate |
|---|---:|
| Initial full kinetic residual, weighted L1 | <=1e-10/s |
| Initial quadrature moments versus independently adaptive stationary integrals | Absolute B,Fhat,Ehat difference <=1e-10 |
| Matched moments between max_step .001 and .0005 | B<=1e-10; Fhat,Ehat<=2e-10 absolute difference |
| Matched moments between successive node counts | B,Fhat,Ehat<=1e-9 absolute difference |
| Each jump mass, signed force and elastic-energy identity error | <=2e-12 absolute |
| Population bounds | Strict nonnegative density and B<=N, with no bound allowance |

For each exact translation, with directly evaluated escaped quantities already normalized where appropriate:

```
B_after + escapedMass = B_before,
Fhat_after-Fhat_before = B_before*delta/beta - escapedNormalizedMoment,
Ehat_after-Ehat_before = Fhat_before*delta + B_before*delta²/(2beta)
                         - escapedNormalizedElasticEnergy.
```

There is no interpolation-variance work term. A passing elastic jump ledger still supplies no chemical-energy or thermodynamic closure. Stationary reference force is reported without resetting it to1. No PE/SE or actual arm force solve occurs in this experiment; the anatomical force gate1e-4 N is unchanged.

## Evidence and comparison

Preserve original inputs, matched density fields and moments, quadrature nodes/weights, direct escape ledgers, accepted-time arrays, full accepted-state hashes/shapes, minima/bound diagnostics, raw logs, current failed candidate and admitted clock/state on any rejection. Use exclusive receipt creation. Compare retained BE/bin histories at IDENTICAL physical times to the 800-node/.0005s reference. Report time and bin-refinement errors after subtracting each model's own initial equilibrium, with normalization denominators explicit; those comparisons assess the old discretization rather than silently change its gates or results.

Save new evidence under `review/continuous-strain-ce/`, with a reviewed static figure and hash manifest. A passing reference closes a continuous-strain numerical prerequisite for this stated finite-domain model. It does not provide physical force/area calibration, body-temperature/human kinetics, a measured PE/SE circuit, anatomical compression/contact credibility or the unqualified dense loaded arm trajectory.
