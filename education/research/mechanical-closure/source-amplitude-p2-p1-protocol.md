# Bounded source-amplitude P2/P1 experiment

Base `af9ad79d07106f46202588367f849366573fddf2`; independent author branch `education/source-amplitude-p2-p1`. Preserve earlier evidence, production mechanics, book/Lean and protected scope/figure files. No MMU request or calibration-record search belongs to this run.

## Bound amplitude and scope

[Krivickas2011, original Methods and Table1](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/expphysiol.2010.055269), [publisher PDF](https://physoc.onlinelibrary.wiley.com/doi/pdf/10.1113/expphysiol.2010.055269), printed pp541/543, reports TypeI corrected SF mean15.5, SD5.0, in N/cm². The selected amplitude is **15.5/(1e-4) = 155,000Pa**. [Source binding](../../data/anatomical-arm-v1/review/source-amplitude-p2-p1/primary-source-binding.json) records the exact table cell, original-page locations and conversion, with the earlier retained methods receipt hash. Fresh original HTML/PDF text was read; the screenshot response supplied no inspectable pixels.

Preparation: chemically skinned human vastus lateralis,15°C, pCa4.5, sarcomere setting2.75–2.85µm. Force is peak minus resting tension; SF includes an adopted20% swelling correction. Do not reapply that correction. The paper questions area-based normalization across fiber sizes. Neither a universal constant nor a population interval is inferred. No marginal-mean division creates a specimen.

Use this reported mean as a **composite educational peak nominal-stress amplitude**, with activation1 and reference F=I, J=1 where nominal/current stress coincide. This reference identification is authored; it does not register an atlas, reproduce the source force–length curve or validate human kinetics. No matched-specimen, whole-arm or clinical claim follows.

## Unchanged controls and explicit activation

Retain the existing **0.14×0.02×0.02m** block, axial fibers, **mu1000Pa, bulk1e6Pa, kf20000Pa, b6, optimumStretch1, activeWidth.5**, instantaneous active potential and force-velocity factor1. Only the declared experiment's peak amplitude/activation differ. The old8,708,387.370104775Pa/.01 inputs remain in their original receipts and in the equivalence control.

Use the existing coarse **4×1×1** P2/P1 block at independently prescribed axial stretches **1.01/1.25**,256-point integration, the same lateral-traction benchmark and10µm perturbed start, both complete caps held exactly. Reuse the original Newton method:80 nonlinear iterations,24 backtracking attempts, true tangent/linear residual and unchanged1e-4N force gate. No state/time trajectory is advanced. A wrapper changes activation explicitly in force, energy and tangent; both Python and original Node receive the same material/activation. Python's bound .01 default is not silently reused.

## Original gates and conditional refinement

Apply [the original P2/P1 gates](full-p2-p1-protocol.md): full free force<=1e-4N; independent32/256-point original-Node assembly difference<=2e-6N; reaction/virtual-work difference<=1e-3N; both pressure RMS<=1e-6; sampled .98<=J<=1.02; finite fields; held nodes exact; strict transverse boundary crossings0; analytic reaction agreement<=1%. Retain the original sampled-geometry/coplanar/containment limitations.

Only stationary cases receive a physical condensed spectrum. Check the lowest witness with independent original-Node full-gradient differences at1e-7/5e-8m, relative error<=1e-4. Probe pressure and geometry retain their original side-check gates; perturbations are derivative tests, not accepted physical advancement. A derivative failure marks curvature unqualified. Negative verified curvature is a result, not a solver rejection or a reason to retune.

Refine **only coarse cases passing stationarity and derivative gates** on the existing8×2×2 mesh, with all other settings unchanged. Compare matched-static fields/reactions/J under the original .5mm/1%/.005 gates and report pressure coupling/inf-sup trend. No timestep qualification is possible in these static cases. Re-evaluate activation0 at each accepted geometry, check its own stationarity/replay before reporting its spectrum, and retain failures.

## Activation-times-amplitude equivalence control

Use the preserved coarse1.25 equilibrium from `review/full-p2-p1/coarse-1.25.json`, not a new baseline solve. Its alpha=.01*8,708,387.370104775Pa. Compare its original material/.01 with155,000Pa and activation=alpha/155,000, holding every other input and geometry fixed. Compare direct P/C/energy, assembled gradient/Hessian and independent Node replay; compare stress/tangent and Hessian at relative1e-12 or better, with the original force/assembly gates. Preserve the original negative witness and its Rayleigh value. This control claims equivalence of the instantaneous law at matched alpha, not measured activation or a constitutive repair. No force target is refitted.

## Failure and evidence policy

Commit protocol, binding, runner, meaningful wrapper tests and renderer before execution. Requests, initial/terminal geometry, histories, probes, exceptions and rejected classifications are written exclusively into the new packet. No existing output is overwritten. Run both independent coarse requests even if one fails; skipped fine cases have explicit reasons. Export the latest evaluated candidate if an exception prevents a terminal return, labelled as a trial rather than an accepted state. The raw log captures any unexpected failure. No extra iterations, tolerance relaxation, smoothing or damping is allowed.

Report actual stationarity, derivative, curvature and matched-refinement outcomes. Render actual accepted-case results with source/educational limits, leaving rejected spectra absent. The smallest remaining model issue must follow from the measured outputs of this declared experiment. This protocol introduces no new physiological law or claim.
