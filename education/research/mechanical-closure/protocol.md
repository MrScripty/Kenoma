# Minimal reference/constraint diagnostic, before a new arm model

Entry checkpoint: **0075a8df7da0efb828ba2e7b6eaebb24243d738f**. Work on separate branch **education/mechanical-closure-diagnosis**; earlier evidence, production mechanics, published book and Lean stay frozen. No peak-stress fitting, bulk increase, positive surrogate tangent, damping addition or physical trajectory rerun.

The first prototype changes only a separately labeled *diagnostic active potential*. Retain the original passive stress/tangent and all fixed material coefficients. Let lambda=|F f0|, lambda*=Loptimal/Lreference, and fL be the original quartic curve. Compare:

**Wactive(full)=a sigma0 lambda* Phi(lambda/lambda*)**, and

**Wactive(iso)=a sigma0 lambda* Phi(J^-1/3 lambda/lambda*)**, with Phi'=fL.

Use lambda*=1 (current authored assumption), 1.4 (Blemker 2005 Table 2 benchmark, not an atlas-subject estimate), and **per-head Arm26 optimal fiber length / repaired head centerline arc length** (a model/geometry *proxy*, not a reference fascicle measurement). Extract BICshort 0.1321 m, BIClong 0.1157 m and BRA 0.0858 m from the preserved XML and match their named heads. Label the proxy's missing physiological correspondence explicitly. Peak sigma0, width and passive-fiber normalization remain unchanged, so the prototype isolates active normalization rather than refitting strengths or simultaneously changing passive tissue. A true material revision must reconcile active and passive reference configurations; this ablation is not one.

At the previously source-bound fourteen saved worst acoustic points (five control/calibration and nine selected loaded-head states), retain F, fibers, activation, material and thirteen reference test directions. Compare full and exactly incompressibility-admissible rank-one curvature. For each m, impose **u dot F^-T m=0**, and diagonalize Q on that two-dimensional polarization plane. An exactly admissible rank-one path keeps det(F+h u tensor m)=det(F), not merely its first derivative. This matters because an unconstrained negative direction does not automatically establish constrained material instability.

Record full and constrained minimum curvature, selected directions/polarizations, normalized fiber length, force-length value/slope and active mean Cauchy stress. Check analytic energy/stress/tangent at two finite-difference scales, retaining the **1e-4** relative derivative gate. Baseline full/lambda*=1 must reproduce the existing material stress/tangent to **1e-10 relative**. Verify objectivity under a proper superposed rotation. At J=1, full and isochoric active forms must agree in energy along determinant-preserving paths and in constrained rank-one curvature within **1e-8 relative**; their stress difference must be purely pressure-like. An isochoric projection alone must not be advertised as a cure for an incompressible descending-limb instability.

Negative frozen controls retain their original labels; no coordinates, activation, time, optimum map or new constitutive choice become accepted history. No diagnostic parameter value is promoted into a physiological default. This local prototype neither solves a new equilibrium nor proves that a true full-space equilibrium is unstable. The recommendation must distinguish the retained 49.09 N nonstationary full nodal force and negative full-P2 direction from any subsequently established stable/unstable true equilibrium.

Source locations and meaning are given in [the closure recommendation](recommendation.md). Rate-dependent behavior, active strain, compatible mixed formulation and passive support are researched there but not implemented in this first prototype.
