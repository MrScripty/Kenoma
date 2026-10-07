# Coupled tissue mechanics: a checked intermediate {#coupled-tissue-mechanics}

The preceding strip experiment separates spatial deformation from the line actuator that turns its hinge. That separation is useful for studying skinning, but it does not meet the requested anatomical lifting capstone. This chapter introduces a replacement force path: deforming tissue pulls distributed tendons, those tendons pull an actual rotating attachment map, and the same objective determines tissue coordinates and joint motion together. The first working experiment is a rectangular engineering fixture. Its results do not transfer to a human arm by renaming its parts.

[Open the resettable coupled 3D fixture](coupled-fixture/index.html). Effort and weight mass are its two primary controls. Numerical state, residuals, activation, fibre stretch, tendon torque and work defect remain readable without starting WebGL. The solver runs in a worker; fixed steps advance only after convergence. Skin is absent while the whole-arm tissue envelope is under review.

## Source anatomy and the interior axis

The separate [source inspection](anatomy-inspection/index.html) retains the actual shared-coordinate BodyParts3D humerus, radius, ulna and seven individual muscle surfaces. Derived belly cuts, fibre guides and mechanical patches remain authored estimates. Each patch records original triangle identifiers, outward normals, area weights and an edge-connected region. Broad humeral origins are surface bands rather than small terminal picks. The radial-tuberosity patch is on the medial side; the brachioradialis patch is on the lateral distal radius. These selections still require anatomical review. Original dataset notices remain with the data, alongside the current [official BodyParts3D licence](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html).

![Actual three-bone and seven-muscle BodyParts3D source assembly in its shared atlas bind coordinates; cyan marks the authored interior axis. Muscles have distinct source surfaces; there is no skin.](assets/atlas-assembly-bind.jpg)

BodyParts3D, © The Database Center for Life Science, current CC BY 4.0; original OBJ notices retained. This source view is not a deformed mechanical solution or an accepted anatomical rig.

The previous surface-pick hinge opened the articulation. The replacement fits an interior axis to connected articular source regions, then evaluates a finite grid of nearby centres against bone-surface crossings. Its centre in atlas metres is (-0.211000, -0.070235, 1.044410), direction (-0.954743, 0.103123, 0.278982), and atlas bind angle 16.2783°. No individual part is independently recentered or registered. Twenty-five tested poses, every 5° from 0° through 120°, have no transverse humerus/ulna or humerus/radius triangle crossing. This is finite sampled evidence, not continuous collision certification or a measured functional axis.

At 90°, the sampled ulnar articular face-centroid distances to the continuous humeral triangle surface have area-weighted median 4.082 mm and 95th percentile 7.923 mm. The nearest tested source vertex is 0.717 mm away. These are distances without cartilage; they are not universal medical tolerances, global triangle-pair minima, or an assertion of anatomical acceptance. Full records are in [apposition-results.json](data/anatomical-arm-v1/audit/apposition-results.json) and [interior-axis-fit.json](data/anatomical-arm-v1/audit/interior-axis-fit.json).

The final arm still needs an explicit shared biceps distal apparatus, tendon/aponeurosis transfer, distributed origins, corrected remesh/bone clearances and tissue contact. A whole belly cap will not be anchored to one patch centroid. Published architecture research provides a reason to model aponeuroses and curved fibres explicitly; it does not identify our atlas-derived guides as measured fascicles. [Blemker, Pinsky and Delp, original 3D biceps study](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf)

The reference-only [remesh discrepancy audit](data/anatomical-arm-v1/audit/remesh-discrepancy.json) localizes defects rather than treating closed positive cells as anatomical accuracy. For brachialis, 53 of 1,008 positive quadrature samples lie outside the source: 5.258% by point count but 2.029% by reference-volume weight. Maximum sampled outside depth is 1.434 mm. Forty-six samples lie inside a bone, reaching 1.908 mm depth. The medial triceps has 30 bone-intruding samples, reaching 2.473 mm. Boundary triangle tests also detect crossings that quadrature containment misses. These are uncorrected defects and prevent acceptance of the current bellies for the anatomical arm. Longitudinal-bin and original-triangle records support correction near attachments and bone clearances; no tolerance is relaxed to hide them.

The audit also finds crossings in the original full atlas muscle surfaces. Of the 46 bone-intruding brachialis samples, 27 lie outside the original muscle surface and 19 remain inside it. Thus both remesh approximation and source assembly clearance need attention. Full source surfaces and trimmed belly surfaces cover different regions, so their crossing counts cannot be subtracted as an accuracy norm. A licensed anatomical atlas is valuable evidence; it is not automatically a mechanically admissible CAD assembly.

## One energy supplies each tissue force

At each positive quadrature point define deformation gradient $F$, volume ratio $J=\det F>0$, normalized reference fibre direction $f_0$, stretch $\lambda=\lVert Ff_0\rVert$, current direction $n=Ff_0/\lambda$, and $e=\max(\lambda-1,0)$. The authored passive density is

$$W_{pas}=\frac{\mu}{2}(J^{-2/3}\operatorname{tr}(F^T F)-3)+\frac K2(\ln J)^2+\frac{k_f}{b^2}[\exp(be)-1-be].$$

At fixed activation use exactly one active solve potential,

$$U_{act}=a\sigma_0\int_1^\lambda f_L(s)\,ds,\qquad f_L(s)=\max(0,1-((s-1)/0.5)^2)^2.$$

This active potential is a device for differentiating force during a fixed-activation solve. It is not passive storage or metabolic energy. With $I_1=\operatorname{tr}(F^TF)$, the first Piola stress is

$$P=\mu J^{-2/3}(F-\tfrac13 I_1F^{-T})+K\ln J\,F^{-T}+[\tfrac{k_f}{b}(\exp(be)-1)+a\sigma_0f_L(\lambda)]\,n\otimes f_0.$$

The Cauchy stress is $PF^T/J$. No second preferred-length force or independent scalar lifting muscle is added. The fixture uses $\mu=1$ kPa, $K=1$ MPa, $k_f=20$ kPa, $b=6$, optimal reference stretch one and placeholder $\sigma_0=0.3$ MPa. These are engineering assumptions, not measured human properties. Force-velocity is fixed to one; activation time constants 0.04 s on and 0.06 s off are authored. Dynamic shortening speed is not a physiological prediction.

Ten-node quadratic tetrahedra interpolate displacement. Four-point positive quadrature is the live fixture choice; 32-point positive subdivided quadrature is the reference profile. The exact shape-weight numerator identity below explains rational partition of unity under a common denominator. Irrational quadrature locations and floating-point evaluation remain separate numerical checks.

{{proof:quadratic-partition}}

## Distributed tendon traction and its torque

For each branch, $\epsilon=l/L_0-1$. Nominal stress is zero in compression, $E\epsilon^2/(2\epsilon_{toe})$ in the positive toe region, and $E(\epsilon-\epsilon_{toe}/2)$ above it. Force is $A_0$ times nominal stress. Integrating gives the positive toe storage

$$U_{toe}=A_0L_0\frac{E\epsilon^3}{6\epsilon_{toe}}.$$

The fixture has nine cap nodes receiving positive geometric area weights, total tendon reference area 30 mm², initial branch length 50 mm, $E=50$ MPa and $\epsilon_{toe}=0.03$. All are authored. Tendons transmit tension only. They are a distributed axial network, not a full transverse aponeurosis solid.

{{proof:tendon-toe-storage}}

A rotating bone attachment is $p(q)=O+R(q-q_{ref})(X-O)$, with derivative $B=\hat e\times(p-O)$. If $f$ is force on that bone, its generalized torque is $Q=B^Tf$. Opposite node and bone forces arise from differentiating the very same branch energy. Independent differences test both the energy gradient and the rigid derivative.

{{proof:attachment-transpose-power}}

{{proof:paired-attachment-work}}

## Joint and tissue are solved together

With tissue quasistatic, angular inertia $I$, fixed step $h$, old velocity $\omega_n$, and documented damping $D$, minimize over tissue positions $x$ and joint angle $q$:

$$\Phi(x,q)=\frac{I}{2h^2}(q-q_n-h\omega_n)^2+U_{pas}(x)+U_{act}(x,a_{next})+U_{tendon}(x,q)+V_g(q)+\frac{D}{2h}(q-q_n)^2.$$

The fixture uses downward-positive world $z$, so $V_g=-g(mz_{grip}+m_{segment}z_{COM})$. Its authored segment mass is 0.1 kg, segment inertia 0.0025 kg m² and damping 0.002 N m s. Dumbbell inertia is $m\lVert B_{grip}\rVert^2$. Tissue mass is not counted again as nodal inertia or local sag. The angle domain [-0.2, 2.1] rad is a synthetic diagnostic domain; a rejected solve preserves the previous state rather than clamping the angle into a hidden support force.

Stationarity in $q$, with $\omega_{n+1}=(q-q_n)/h$, yields

$$I\frac{\omega_{n+1}-\omega_n}{h}=Q_{tendon}+Q_g-D\omega_{n+1}.$$

{{proof:implicit-impulse}}

Newton steps use the analytic directional derivative of the unchanged Piola stress and branch Hessian. Truncated conjugate gradients use a reference-elasticity Cholesky preconditioner for this small fixture. Indefinite search systems receive explicitly recorded solver regularization; this does not add a material energy. Determinant-invalid trials are rejected. Armijo sufficient decrease chooses accepted search steps, without promising global convergence of this nonconvex problem. [Armijo, original paper](https://msp.org/pjm/1966/16-1/pjm-v16-n1-p01-s.pdf)

The stopping target is maximum normalized-coordinate gradient $10^{-6}$ J; tissue displacements are normalized by reference block length and angle is in radians. The receipt separately reports the maximum free nodal vector norm in N and the joint residual in N m. Objective-call counts include rejected determinant trials; post-solve diagnostic calls are separate. A finite linear solve can stop short of its requested tolerance, but the nonlinear residual must pass before time and activation advance.

## Lift, release and work that remains unresolved

![Computed angle and activation for the actual coupled P2 fixture; effort drops at 0.28 seconds and the angle subsequently falls.](assets/coupled-pulse.svg)

The first reproducible pulse starts at $q=0$, $a=0$, 0.5 kg and $h=0.04$ s. Effort is 0.25 for seven steps, then zero for five steps. Tissue-generated tendon torque raises the lever; after release activation decays and the lever lowers. The authored route changes its moment-arm sign at some larger angles. That behaviour is part of this synthetic fixture, not an accepted human attachment path. [Full pulse, state coordinates and step refinement](data/anatomical-arm-v1/audit/coupling-results.json)

![Native rendering after seven loaded steps: coral is the actual P2 tissue boundary, gold shows nine distributed tendons, blue is the hinged rigid lever and violet is the point mass.](assets/fixture-loaded.jpg)

![The same coupled engineering fixture after five released-effort steps; activation and angle fall while the tissue coordinates remain part of the joint solve.](assets/fixture-released.jpg)

Original schematic fixture geometry, rendered at the actual solved coordinates. No skin, anatomical attachments or contact are represented in these two images.

For angular motion the exact identity is

$$I(\omega_{n+1}-\omega_n)\omega_{n+1}=\Delta(\tfrac12 I\omega^2)+\tfrac12 I(\omega_{n+1}-\omega_n)^2.$$

{{proof:kinetic-increment}}

Combining it with the assumed angular stationarity equation gives the angular endpoint-work identity. It does not supply conservation of the nonlinear tissue potentials.

{{proof:implicit-angular-work}}

{{proof:implicit-dissipation}}

The implementation computes active mechanical work as minus the fixed-$a_{next}$ active-potential change between old and new geometry. It separately records passive tissue, tendon, gravity and angular kinetic energy, damping work, angular implicit dissipation, and their nonlinear endpoint-work defect. Changing activation supplies an external input; an active potential is never booked as passive storage. Runs at 0.04, 0.02 and 0.01 s retain the observed work defects. An exact proof of the angular algebra does not erase those defects.

{{coupled-steps}}

The angular trajectory still changes materially with step refinement. The decreasing work defect is an observed trend over these runs, not a demonstrated asymptotic rate or convergence certificate.

Changing mass preserves pose, velocity, tissue, activation and elapsed time. At that instant it adds an external energy event

$$\Delta E_{mass}=\Delta m(\tfrac12\lVert B_{grip}\rVert^2\omega^2-gz_{grip}).$$

{{proof:mass-event-work}}

Matched profiles retain the same passive/active law, $K$, 32-point quadrature and nonlinear residual target for L-BFGS and Newton at two mesh resolutions. The measured timing and final-length differences are evidence for this fixture only. Dense Cholesky does not establish that seven atlas bellies will run at interactive speed. Remaining anatomy, contact, work-refinement and mobile checks must be resolved before this intermediate can replace the requested anatomical capstone.

{{coupled-profile}}

These are one local run per case. Timing is illustrative; final state and residual are the comparison contract. HVP means analytic Hessian-vector product. Post-solve reaction diagnostics are outside the objective-call counter.
