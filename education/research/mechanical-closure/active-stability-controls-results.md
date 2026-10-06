# Active mechanics: stability depends on the held state and control

**The current instantaneous fixed-activation law has an active-driven descending-branch instability even with end length prescribed and local volume-preserving variations. This does not establish that real muscle must be unstable on its descending isometric force–length branch.** The distinction is the constitutive state and timescale being linearized. Retain the converged original equilibria and negative witnesses; they are valid findings for that declared model.

Entry **97e645d3cef0d4fd6237bc4874cb085afa05d5c2**; bounded experiment source **a38c874d069e160eb9b9ef37629674419bc3353d**, successor **education/active-stability-controls**. See the [predeclared protocol](active-stability-controls-protocol.md), [raw summary](../../data/anatomical-arm-v1/review/active-stability-controls/summary.json) and [execution log](../../data/anatomical-arm-v1/review/active-stability-controls/execute.log). There was no optimizer, coefficient retuning, tolerance change, reference switch or physical-state/time advancement. Production, edition, Lean, protected scope files and all previous source-bound packets remain frozen.

## Four separate conclusions

1. **Equilibrium:** all eight active/passive re-evaluations pass the unchanged full-force, pressure, reaction/work, positive-J and strict boundary-crossing gates with independent 32/256-point original-Node replay. A stationary field need not be a stable equilibrium.
2. **Model tangent:** at fixed activation and the existing instantaneous fL law, descending-branch interior directions have negative physical curvature. Weak P1 pressure restriction and strict local volume admissibility do not remove it. Zero activation isolates the active contribution; it is not a recommended replacement activation.
3. **Physical response:** an isometric force–length relation across prepared equilibria is not automatically the transient incremental force response of a contractile system. Activation, attached cross-bridge/contractile state, series compliance, rate and history may have different held or evolving states. This packet contains no measured human stiffness, calibrated dynamics or complete activation controller.
4. **Reference calibration:** dimensionless model stretch 1.25 does not identify a human sarcomere or fascicle length. The atlas reference architecture remains unmapped. The original **1.4 dimensionless optimal/reference stretch benchmark** and Holzbaur's separate **1.4 MPa model specific tension** remain distinct; neither is selected or tuned here.

## Controlled numerical isolation

At each saved coarse/fine state, activation is either the original 0.01 or the passive isolation control zero. All passive coefficients, cap positions, pressure space and reference geometry remain identical. Removing the active term leaves adequately stationary states because these controlled fields are almost homogeneous; that result is checked, not presumed. No failed force gate is repaired with more iterations.

| Mesh / stretch | Active full minimum, a=.01 (N/m) | Passive full minimum, a=0 (N/m) | Active weak-pressure-constrained minimum (N/m) |
|---|---:|---:|---:|
| coarse / 1.01 | +5.433012 | +0.237231 | +5.450197 |
| fine / 1.01 | +1.024980 | +0.052486 | +1.028108 |
| coarse / 1.25 | **−4293.987496** | +1.978959 | **−4285.347756** |
| fine / 1.25 | **−3033.966160** | +0.468557 | **−3031.622699** |

The weak restriction is `ker D` for the discrete P1 log-J coupling. Dimensions are **169 and 1044**, corresponding to ranks 20 and 81. The largest `||D Z||/||D||` is **4.719e-16**, below the declared 1e-12 gate. This is not pointwise incompressibility. Eigenvalues use Euclidean nodal normalization; their mesh-dependent magnitude is not a continuum spectrum-convergence claim.

Original-Node gradient differences at 1e-7/5e-8 m pass the unchanged 1e-4 relative gate for all eight full-space witnesses. The worst error is **8.739e-5**, close to but below the gate for a small passive eigenvalue. Strict local stress differences at 1e-6/5e-7 pass, with maximum relative error **2.303e-10**. Preserve those actual accuracies rather than presenting every check as machine precision.

At the traction-free homogeneous benchmark for stretch 1.25, the fixed-activation admissible local minimum among 181 declared angles is **−47538.89754 Pa**, at **45°**. Its unit vectors are `m=(.70710678,.70710678,0)` and `u=(.81321508,−.58196326,0)`, with `u·F^-T m=5.552e-17`. The passive local scan minimum is +999.83064 Pa. Both scans at stretch 1.01 have minimum +999.99334 Pa. A positive finite scan proves no global ellipticity theorem; the negative tested direction is a concrete counterexample at this controlled field.

For the rank-one variation `H=u⊗m`, the matrix determinant lemma gives `det(F+εH)=J(1+ε u·F^-T m)`. With this constraint, J stays constant along the rank-one path. Therefore a volumetric potential depending only on J contributes zero directional curvature there. Increasing K or imposing incompressibility cannot remove this particular active-driven local witness. The [previous Rayleigh split](full-p2-p1-results.md) identifies the active term, not bulk prestress, as the dominant negative contribution.

Active stress is not negative in every mode: near stretch 1.01 it increases the full minimum from the passive value, even though its fiber force–length derivative is negative just beyond the optimum. Geometric tension and polarization matter. Classify the total constrained tangent rather than the sign of fL′ alone.

## Expected behavior under declared loading regimes

On the homogeneous branch with lateral traction zero, implicit transverse equilibrium determines s′(λ). Using the original full constitutive tangent, `dR/dL = A0/L0 [Cxxxx+(Cxxyy+Cxxzz)s′]`. Two centered axial differences independently verify this derivative below the unchanged gate. These scalar results are conditional on the homogeneous branch, not a complete tissue stability classification.

| Axial stretch | a=.01 axial slope (N/m) | a=0 axial slope (N/m) |
|---|---:|---:|
| 1.01 | +29.283042 | +69.076889 |
| 1.25 | **−484.557192** | +261.876011 |

- **Prescribed end length:** the global axial coordinate is excluded. A negative force–length slope alone is not a failure under this control. Nevertheless, the computed interior modes vanish on both caps and remain allowed; their negative curvature is a separate instability of the current full-nodal law.
- **Dead axial force:** linear external work contributes no curvature. The −484.557192 N/m homogeneous axial slope is an allowed negative mode at that matched equilibrium. Quasistatic balance is still possible; stability does not follow from it.
- **Passive series spring acting on end separation:** the global scalar mode requires **kseries>484.557192 N/m** at this branch point. No stiffness is selected or fitted. Such a spring acts through end separation and cannot stabilize the retained zero-cap interior negative witnesses. Anatomical tendon/aponeurosis/fascia may act through different distributed load paths and need their own geometry, reference and parameters.
- **Dynamic or feedback control:** stability requires the coupled linearization, including inertia, constitutive internal states and the actual activation/controller law. The current static Hessian supplies neither controller poles nor physiological rate calibration. For the same instantaneous conservative stiffness with positive inertia, negative curvature implies a growing undamped linear mode; adding ordinary damping alone is not a proof that a negative stiffness becomes stable. A supported internal-state model changes the physics and must be tested as such.

## What the original sources support

[Gordon, Huxley and Julian (1966)](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/jphysiol.1966.sp007909) measured an isometric tension plateau and descending branch in frog single fibers while controlling sarcomere uniformity. A descending isometric curve is therefore a phenomenon to retain, not erase by forcing fL′≥0. It supplies no human atlas reference map or universal incremental stiffness.

[Ford, Huxley and Simmons (1981), original abstract](https://pubmed.ncbi.nlm.nih.gov/6973625/) distinguishes rapid tension transients, instantaneous stiffness and early recovery in stimulated frog tibialis fibers at 0–1°C; their analysis separates contractile behavior from tendon compliance and apparatus effects. This supports distinguishing transient internal-state response from an equilibrium force–length slope. It does not justify importing a stiffness, relaxation time or viscosity into this human-arm fixture. The abstract was readable; a later PubMed request returned an empty page. No access restriction was bypassed.

[Ambrosi and Pezzuto's original preprint, sections 4–5](https://www.mate.polimi.it/biblioteca/add/qmox/21-2011.pdf) treats frame indifference and total-law ellipticity, including incompressibility-admissible rank-one variations. Its examples are cardiac. A mathematical guarantee for one active-strain/active-stress form is not a skeletal force–length/reference calibration. [Klotz, Bleiler and Röhrle (2021)](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.685531/full) distinguishes serial, parallel and combined interpretations; changing families changes the contractile/passive force path. The [rate-source ledger](rate-source-addendum.md) retains OpenSim's distinction between fiber length/velocity, activation and tendon state. None makes joint damping a substitute for local contractile physics.

The Allinger–Epstein–Herzog 1996 stability paper was identified but its publisher returned 403 and its PubMed page supplied no readable abstract. Its findings are not used to justify any conclusion here. No service, credential or permission change was attempted.

## Falsifiable next recommendation

**Retain the additive family as the first explicit contractile/series-state candidate, but stop interpreting the instantaneous isometric fL derivative as a validated transient tissue stiffness.** First declare the held input and state, reference fascicle/optimal-length convention and tested timescale. Compare candidate responses at matched isometric force and reference configuration, with the existing negative witnesses as regressions. Do not select a positive tangent by suppressing fL′ or moving the reference to an ascending limb.

For a state-dependent candidate `P(F,a,z)`, a fast perturbation at fixed a,z uses `P_F`; a relaxed branch `z=z_eq(F,a)` uses `P_F+P_z dz_eq/dF`. These are different physical experiments. Choosing one without defining z and its evolution is not closure. Predeclare both tests and, for dynamics, test the actual coupled Jacobian and time refinement rather than demanding a positive static potential at every controlled saddle.

| Candidate / hypothesis | Test that can reject it before anatomy |
|---|---|
| Original instantaneous fixed-activation law | Reproduces current balance but retains descending admissible negative directions. It fails stable quasistatic homogeneous-continuum qualification in that declared regime; preserve it as the baseline. |
| Additive active stress with explicit contractile/internal and series state | Must retain source-supported isometric force–length/velocity conventions, passive/deactivated limit and stress/work units. At matched force, distinguish short perturbation from relaxed response and validate the internal/series parameters from appropriate preparations. A newly positive fast tangent alone does not prove long-time or feedback stability. |
| Multiplicative active strain | Independently specify Fa and its activation/evolution/reference meaning, determinant and passive response; match uniaxial force, transverse/shear response and declared timescale. A λ-dependent distortion introduced merely to fit fL may forfeit inherited ellipticity; fixed-Fa arguments cannot certify that different law. |
| Combined serial/parallel formulation | Define force paths and state variables; reject if it fails the same matched-force, deactivated, transverse/shear, dissipation and dynamic-response tests. Model complexity is not validation. |
| Lagged/clipped fL derivative or arbitrary damping | If only the solver Jacobian changes, the original physical witness remains. If the physical law changes, disclose and validate it. Neither is an acceptable hidden stability repair. |

The immediate next bounded experiment requires a source-backed choice of internal/series state and reference architecture with identified missing parameters. It must not fabricate human values or re-fit the existing target merely to obtain a positive spectrum. The present comparison narrows the blocker; it does not select a physiological replacement law.

## Arm and lesson implications

The arm still needs reference architecture, distributed passive load paths, controlled constitutive/rate validation and nonuniform full-nodal mixed equilibrium before a self-consistent loaded trajectory. The dense lift/release and tissue envelope remain unqualified; no skin. Parameter uncertainty studies follow numerical gate closure rather than concealing a constitutive or geometry failure.

Keep the published lesson files unchanged now. The next evidence-backed lesson revision should explicitly sequence: **01-force** (balance/reaction), **03-energy** (active solve potential versus storage and controlled external work), **04-muscle-physiology** (isometric force–length versus transient state/reference), **09-continuum-medical** (physical tangent and admissible variations), **10-fast-methods** (algorithmic solver matrix versus physical stability), **14-coupled-mechanics** (constraints, series force paths and dynamic linearization), then **15-anatomical-apparatus** (validated reference, material and loading assumptions). Teach neither “equilibrium means stable” nor “descending force–length means every real muscle must be unstable.” Update equations/book/Lean only when an explicit replacement model is selected and its actual obligations are established.
