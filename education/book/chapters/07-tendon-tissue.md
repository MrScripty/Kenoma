# Store tendon energy and resist compression {#tendon-tissue-coupling}

Laboratory 4 used a rigid tendon and an illustrative belly. Laboratory 5 adds two physical mechanisms while preserving that earlier lesson: a massless series tendon/fiber equilibrium and a quasistatic tissue block whose reaction changes the hinge acceleration. The right-hand drawing is a synchronized graphics baseline at the **same q**, not another dynamics simulation.

{{demo:series}}

The tissue block's boundary is the rendered surface. There is no separate skin membrane, fascia layer, fiber architecture field or anatomical attachment map yet. The plate gap is an authored function of angle, rather than a distance measured from elbow meshes. This bounded proxy makes tendon stretch, elastic storage, compression and skinning volume loss measurable before anatomical detail is introduced.

## One-dimensional contraction can redistribute length at fixed endpoints

Let l be the synthetic musculotendon path from Laboratory 4, l_f the fiber length and l_T the tendon length. There is zero pennation and l = l_f + l_T. An active force source in parallel with a passive fiber spring supplies

$$F_A=aF_0,\qquad F_P=k_M\max(0,l_f-l_0),\qquad
F_T=k_T\max(0,l_T-l_{Ts}),\qquad F_T=F_A+F_P.$$

The active source is deliberately independent of fiber length and velocity in this lesson. It is a tensile teaching actuator, not a calibrated Hill model. This choice differs from Laboratory 4's bell-shaped active curve and is disclosed rather than attributing that change to tendon compliance alone. A rigid/compliant comparison **within Laboratory 5** changes only the tendon assumption. Millard and colleagues' original comparison motivates making tendon assumptions and internal state explicit; the formulas here are original simpler teaching laws. [Original actuator comparison](#source-muscle)

Write c_T = 1/k_T and Δ = l − l_Ts − l₀. The equilibrium is piecewise analytic. If Δ − c_T F_A ≤ 0, the passive spring is slack and F_T = F_A. Otherwise,

$$F_T=\frac{F_A+k_M\Delta}{1+k_Mc_T},\qquad
l_T=l_{Ts}+c_TF_T,\qquad l_f=l-l_T.$$

Both cases retain tensile tendon force. At zero activation and sufficiently short path, the tendon carries no force; a slack tendon is not a compressive strut. The rigid switch sets c_T = 0, so the tendon cannot store energy. The supported fiber domain is l_f ≥ 0.04 m; leaving it stops the teaching solve instead of extrapolating toward zero fiber length. This is an authored admissibility bound, not a physiological threshold.

For the passive-taut case set d = 1 + k_M c_T; in the passive-slack case d = 1. Differentiating the equilibrium gives

$$\dot l_f=\frac{\dot l-c_TF_0\dot a}{d},\qquad
\dot l_T=\dot l-\dot l_f.$$

Thus a held joint can have l̇ = 0 while fibers shorten and the tendon lengthens as activation rises. Release can lengthen an active fiber while the whole path remains fixed. “Isometric” must name the quantity that is held: joint angle, total path, or fiber length. The controls show all three length quantities and the fiber velocity.

**Try a fixed-end activation.** Choose prescribed hold, q = 90°, and step through activation. Compare rigid and compliant tendon after resetting the experiment. The generated 0.30 s fixture is:

{{series-holds}}

All values belong to the authored schematic. At this pose the passive fiber spring is slack. The compliant case stores about 8.60 J in the tendon while the rigid case stores none. That energy does not come from motion of the prescribed skeleton: it comes from active fiber shortening. No metabolic efficiency or ATP consumption is modeled.

## Count active work at the fiber, not twice at the hinge

The passive stores are

$$U_M=\tfrac12k_M\max(0,l_f-l_0)^2,\qquad U_T=\tfrac12c_TF_T^2.$$

The hinge receives muscle power −F_T l̇. The active element delivers P_A = −F_A l̇_f. They differ because the passive fiber and tendon store or release energy. Indeed,

$$\dot U_M+\dot U_T=F_P\dot l_f+F_T\dot l_T,
\qquad P_A-(\dot U_M+\dot U_T)=-F_T\dot l.$$

The moment arm r = −dl/dq therefore still transmits τ_MT = r F_T, once. There is no second muscle-body actuator. Negative P_A during active lengthening is retained as signed mechanical work absorbed by this simple active source. The initial elastic state is included in E₀, so switching the initial pose does not silently erase a preload.

## A small continuum ansatz with an explicit material law

The tissue proxy is one homogeneous block, reference width W = 0.08 m, height H = 0.06 m and depth D = 0.05 m. It deforms affinely with F = R(q/2) diag(t,h,t), where t is free lateral stretch and h is compression stretch. This is a **reduced continuum ansatz**, not a six-edge spring network, a tetrahedral FEM mesh, or a full arm tissue solve. Its homogeneous strain cannot describe folds, heterogeneous stress or local sliding. The rigid rotation R changes neither the following invariants nor energy.

Define J = t²h, I₁ = 2t² + h² and V₀ = WHD. The chosen hyperelastic energy is

$$U_B=V_0\left[\frac{\mu}{2}\left(J^{-2/3}I_1-3\right)+\frac{\kappa}{2}(J-1)^2\right].$$

The first term penalizes shape change and the second penalizes volume change. The default μ = 1,500 Pa and κ = 50,000 Pa are authored material values. They are not the skin/adipose estimates cited in the anatomy chapter. J remains positive in the supported model domain. The continuum framework relates an energy to its stress and forces; the bibliographic Sifakis/Barbič record and independently opened Ryan et al. compression research supply further-reading context, while this block solve and numerical experiments are Kenoma's own. [Continuum source record](#source-continuum), [compression study](#source-compression)

For stretches λ_i = (t,h,t), the diagonal first Piola components are

$$P_i=\mu J^{-2/3}\left(\lambda_i-\frac{I_1}{3\lambda_i}\right)
+\kappa(J-1)\frac{J}{\lambda_i}.$$

Free lateral faces require P_x = P_z = 0. For a compressed block, the implementation brackets t between h and 1/√h and bisects that scalar equation. It reports the remaining lateral stress residual. The hard plate constraint fixes h; this is not a penalty that merely makes penetration small. Removing bulk resistance sets κ = 0 and allows stress-free uniform contraction t = h, exposing large volume loss under the same imposed gap.

## Contact produces a force, pressure and generalized moment

The ideal opposed plates have gap

$$g(q)=0.085-0.055\sin(q/2)\ \mathrm{m}.$$

When g ≥ H, the block is unstressed with t = h = 1 and zero reaction. When g < H and contact is enabled, h = g/H and the lateral equilibrium supplies t. The normal force on either plate is N = −WD P_y, taken nonnegative. The current contact area is WD t², so this **uniform model plate pressure** is N/(WD t²). It is not a measured anterior-elbow or cartilage pressure.

The tissue resists closure. Its generalized hinge moment is

$$Q_B=N\frac{dg}{dq}=-\frac{dU_B}{dq}.$$

Because dg/dq is negative, the moment opposes flexion. Both plate reactions are represented by this one gap-coordinate work N ġ; adding twice that generalized moment would double-count the same interface work. There is no tissue inertia or extra mass. Its conservative reaction does feed back into the existing hinge, while the prescribed mode displays the external support needed to oppose it.

The diagnostics show clearance g − hH, penetration max(0,hH − g), normal force, and the complementarity product N(g − hH). The zero clearance in active contact is a consequence of this closed-form plate constraint. It supplies no collision guarantee for arbitrary meshes, trajectories or skin self-contact. Turning contact off leaves the unstressed block at its rest height and exposes overlap with the closing plates; its reaction is then zero.

## Compare a surface transformation at the identical angle

Both views start with the same reference block. The naive baseline assigns every vertex uniform weights 1/2 to identity and a rotation R(q) about the common hinge axis:

$$x_{LBS}=\tfrac12(X+R(q)X),\qquad J_{LBS}=\cos^2(q/2).$$

The renderer applies that transform to the actual bind-space vertices. It does not add a rest-relative displacement to an already posed surface. The physical block has its own affine deformation and shared bisector-frame orientation. Insets are translated and enlarged equally for display, and the reported volumes use physical dimensions. The comparison isolates constitutive/contact response versus a geometric transform; it is not a full, spatially weighted anatomical elbow-skin benchmark. [Original geometric skinning paper](#source-dqs)

{{series-compression}}

At 90°, the physical block retains about 99.29% of its reference volume, while this LBS fixture retains 50%. In this particular fixture the LBS surface remains separated from the plates; the lesson reports volume loss rather than inventing an intersection. Its force, stress and pressure outputs are “not modeled.” The teal block with contact disabled instead produces a genuine measurable overlap. These are distinct failure demonstrations.

## Close the full work balance and expose numerical cost

The hinge now obeys I q̈ = τ_MT + τ_g − b q̇ + Q_B. Total mechanical energy includes hinge kinetic energy, gravity, U_M, U_T and U_B. With W_A = ∫P_A dt and D = ∫b q̇² dt,

$$E-E_0-W_A+D=0$$

for the continuous forward model. In prescribed static hold q̇ = 0, the support performs no work, but fiber/tendon redistribution can still change E. Gravity is counted once through its potential and moment, and tissue work is exchanged between its store and the hinge, not added again as external energy.

The solver uses RK4 with exact constant-input activation at each stage. It locally bisects a step when trial stages cross the passive-fiber or plate-contact branch, up to eight levels. The visible event-subdivision count and exported accepted substep count disclose this extra work. This reduces branch-related work error; it does not prove general convergence or floating-point correctness. The generated pulse/release experiment is:

{{series-trajectories}}

Independent checks cover series equilibrium and lengths, fixed-end fiber shortening and release lengthening, the rigid-tendon limit, energy/stress finite differences, the tissue moment versus an energy derivative, free-side stress residuals, contact complementarity, contact/volume ablations, LBS vertex geometry, replay, and timestep refinement. The existing Lean cards remain limited to their exact algebraic domains; none certifies this continuum solve or biology.

The following chapters implement spatial FEM and a separate on-arm skin/fascia/contact teaching model. Laboratory 7 completes the schematic same-pose capstone with its own one-way limits and measured defects. An anatomical extension would still need registered geometry, identified properties, routed attachment regions and robust surface self-contact; those clinical questions are separate from this completed teaching progression.
