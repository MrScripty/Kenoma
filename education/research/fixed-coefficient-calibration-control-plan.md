# Next bounded calibration controls

This is a research plan, not an executed sweep or default change. Finish and independently replay the existing fine/interpolated trajectories first; preserve their failures and stop at that checkpoint. The teaching release, current coefficients, iteration limits and acceptance gates remain unchanged. No new sweep is executed in this closeout.

## Interpret the source targets correctly

The parent reports verified [Holzbaur, Murray and Delp (2005), methods pp. 832–833](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf): the inherited force parameters were derived using PCSA times **140 N/cm² = 1.4 MPa**, selected to match joint strength. They are model-derived whole-muscle targets, not directly measured individual-head forces. This executor's fresh manuscript read timed out; no fresh full-text verification is claimed. The retained Arm26 XML and its exact force/fiber-length/pennation values remain source-bound separately.

The atlas millimetre-to-metre conversion was confirmed by the parent's audit. The [local cross-model calculation](fiber-supplement/cross-model-capacity-checkpoint.md) and the [fiber/PCSA outline](fiber-supplement/calibration-constraints-outline.md) distinguish measured PCSA, inferred atlas-volume/Arm26-fiber-length area, geometric belly `V/L`, and effective fixture `F/sigma0`. The current coefficient multiplies a first-Piola active term. Operating active Cauchy stress also includes activation, the local force–length factor, stretch/J and orientation. The [forwarded calibration-state findings](fiber-supplement/calibration-review-followup.json) show strongly off-optimal local fiber stretches and stress transfer through passive fibers, sheets and bulk response; frozen denser arithmetic still fails equilibrium. These findings do not select a new coefficient.

## Minimal fixed-coefficient comparison

Choose one named biceps head initially. Retain that head's exact current `mu`, bulk, passive-fiber constants, `sigma0`, force–length window and activation law in every case. Do not inverse-fit a target. Match the prism's reference volume and length to the current modeled head's volume and declared geometric length; its analytic cross-section is `V0/L0`, not measured PCSA. Document fiber orientation and the precise normalization of length, area and virtual displacement. Compare equal approximation order and a declared comparable displacement resolution. Keep reference-volume restoration and cross-model fiber-length substitutions out of this first geometry comparison.

| First comparison | Geometry / support / apparatus | Question |
| --- | --- | --- |
| Prism versus tapered head | Same volume/length, declared axial fibers, matched idealized fixed-end support; sheets absent in both diagnostic fixtures | Does shape/displacement resolution alone redistribute local stretch and suppress the active force–length factor? |
| Support control on the tapered head | Same material, geometry and fibers; compare matched end-cap support with the existing authored attachment constraint | How much of the response comes from the support map and attachment-region strain? |
| Sheet control on the tapered head | Same support/material/geometry; compare the same fixture with and without the existing authored embedded sheets | How does the sheet load path alter stretch distribution and end-force transfer? |

Share common baseline cases rather than running a full factorial sweep. These are isolated diagnostic controls; removing a sheet or changing support is an explicitly labeled apparatus ablation, not a change to the arm defaults. Exclude bone contact initially to isolate the calibration mechanism. Preserve the actual-head fixture and every original failed state.

Start from the undeformed reference at zero activation and use a small predefined activation schedule common to the paired cases. Use accepted-state initialization, the existing solver and a fixed documented iteration limit no greater than the current control budget. A failed force/geometry state must not advance activation or state. No extra iterations, relaxed tolerances, coefficient adjustment, changed active window or retrospective schedule selection may rescue an unfavorable result. If a control needs a richer displacement/pressure space, isolate that as the next numerical comparison and retain the restricted-space failure first.

## Required evidence before interpreting a force

Save complete states, frozen rules, source hashes and raw failures. Freshly check reduced stationarity, independent projected full-P2 forces, full free-nodal residuals separately, determinants and finite geometry. Report the reference-volume-weighted distributions of stretch, active force–length factor, J and active Cauchy stress, including fractions outside the authored active window. Do not compare the peak coefficient with an unlabeled average stress.

Decompose the signed direct end reaction into active, passive fiber, matrix/volume and sheet contributions. Separately report axial virtual work using an explicitly defined, unit-normalized virtual displacement field, its reference/current configuration and the residual-dependent discrepancy from the end reaction. Active interior stress can transfer through other terms to the supported end; a zero direct active end contribution cannot be interpreted as absence of active muscle force. A frozen failed state may support derivative/field diagnostics but cannot qualify equilibrium or a calibration.

Only after accepted controls and matched resolution/integration evidence should a later plan consider replacing any law or fitting a coefficient. Such a change would require revised equations, book and applicable narrow Lean statements, independent material/derivative checks, re-solved calibration and loaded trajectories. The current **4.72138-degree / 7.40368-mm** trajectory discrepancy, **J approximately 0.712**, and full-nodal limitations remain unresolved. No skin follows from this plan.
