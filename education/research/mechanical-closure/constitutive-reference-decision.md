# Constitutive and reference decision for the loaded-arm capstone

Date: 2026-10-06. This is a source-backed modeling decision, not a new solver result, human-biceps calibration or whole-envelope qualification. It preserves the existing failed cases and frozen witnesses. The bounded source-reproduction benchmark may proceed with explicitly educational parameters while anatomical calibration proceeds separately.

## Decision and retained evidence

Retain an additive active-stress/Hill family with an explicit reference-to-optimal fascicle length map, activation dynamics, force–velocity response and compliant tendon. First reproduce a pinned original musculotendon implementation independently in small cases. Then consider work-consistent tissue coupling under a separately reviewed protocol. Do not choose a constitutive law or coefficient by whether its eigenvalues are positive.

The parent reports independently verified commit `09e6698f`: coarse stretch 1.25 has a linearized-volume-kernel direction of −4443.1611 N/m, with active contribution −5631.46 N/m against positive passive contributions. Pointwise volume stiffness and pressure prestress are retained, first-order delta-log-J is approximately 2.7e−14/m, and base J approximately 1.000254. That commit was not locally available for this research review; these are explicitly parent-verified results, not a second raw-receipt inspection. This result is not an exact finite incompressible path or proof of human instability.

The preserved matched-force carried-state experiment gives a stiffer transient response but relaxes to the same macroscopic force–length envelope. It is not a demonstrated long-time repair. A static negative direction under fixed activation and a stable controlled powered hold are different claims. Dynamic classification requires the coupled mechanics, internal-state kinetics, inertia and controller. Damping alone does not remove an unchanged negative relaxed stiffness.

## Primary experimental evidence and transfer limits

| Original evidence | Preparation and observation limits | Consequence |
| --- | --- | --- |
| [Gordon, Huxley and Julian (1966)](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/jphysiol.1966.sp007909), *The variation in isometric tension with sarcomere length in vertebrate muscle fibres* | Isolated frog fibers, controlled uniform sarcomere sections, isometric tetani; plateau around 2.05–2.2 µm and a descending branch above it. Temperature was not verified in the accessible abstract for this review. | Preserve descending isometric behavior; do not transfer frog optimal lengths or kinetics to human biceps. |
| [Julian and Morgan (1979)](https://pubmed.ncbi.nlm.nih.gov/315465/), *The effect on tension of non-uniform distribution of length changes applied to frog muscle fibres* | Single frog twitch fibers with segment tracking/control; internal shortening and lengthening differ between middle and ends. Temperature was not verified in the inspected abstract. | Permit internal length redistribution; global fiber length is not necessarily every sarcomere's length. |
| [Ford, Huxley and Simmons (1981)](https://pubmed.ncbi.nlm.nih.gov/6973625/), *The relation between stiffness and filament overlap in stimulated frog muscle fibres* | Intact frog tibialis anterior, 0–1°C, approximately 0.2 ms length steps, controlled segments and corrections for series compliance/apparatus dynamics. | Fast attached-state stiffness is distinct from a relaxed force–length derivative. These rates are not human physiological-temperature calibration. |
| [Minozzo et al. (2013)](https://www.nature.com/articles/srep02320), *Force produced after stretch in sarcomeres and half-sarcomeres isolated from skeletal muscles* | Permeabilized rabbit psoas, approximately 10°C, pCa 4.5; isolated single and half-sarcomeres, 15–36% half-sarcomere stretches and holds of at least five seconds; attachment and activation-shortening limitations. | Residual force enhancement in half-sarcomeres prevents selecting serial nonuniformity as the sole necessary mechanism. It does not identify infinite-time equilibrium or prove a titin mechanism. |
| [Campbell, Hatfield and Campbell (2011)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002156), *A mathematical model of muscle containing heterogeneous half-sarcomeres exhibits residual force enhancement* | Heterogeneous serial half-sarcomeres and three-state crossbridge dynamics, calibrated against permeabilized rabbit psoas at 15°C. Seconds-long activation/stretch protocols; enhanced simulated tensions eventually converge during longer relaxation. | A source-replay mechanism comparison, not a permanent repair or human-arm calibration. |
| [van der Zee et al. (2026)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748), *Cross-bridge model for predicting muscle short-range stiffness during movement* | Permeabilized rat soleus at 22°C; cooperative thin/thick-filament kinetics and near-optimal constant-overlap assumptions. No complete descending force–length or human-arm validation. | Useful transient-response research. Do not invent overlap/recruitment laws and attribute them to this source. Experimental series compliance is not automatically a whole human tendon. |

Retain measured descending behavior, history dependence and nonuniformity as phenomena. Do not interpret an authored local envelope, mesh-dependent redistribution, or a negative fixture direction as a measured biological instability. A fast frozen-state tangent, finite-time response and fully relaxed fixed-activation equilibrium must be reported separately.

## Reference lengths, stresses and boundaries

The atlas reference pose, passive stress-free configuration and active optimal length are distinct. Under an explicit serial/co-deformation assumption, define

\[
q(X)=|F a_0|/\lambda_{\mathrm{opt,ref}}(X),\qquad
\lambda_{\mathrm{opt,ref}}=L_{f,\mathrm{opt}}/L_{f,0}
\approx\ell_{s,\mathrm{opt}}/\ell_{s,0}.
\]

The approximation requires a stated relation between measured fascicle and sarcomere lengths. Choose full or isochoric fiber stretch explicitly and keep stress/reference-area conventions consistent. Fixture stretch 1.25 does not establish normalized sarcomere length 1.25.

[Murray, Buchanan and Delp (2000)](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf), *The isometric functional capacity of muscles that cross the elbow*, paired human cadaver fascicle lengths with laser-diffraction sarcomere lengths and normalized to 2.8 µm. Frozen/thawed and fixed cadaver preparation, joint pose and an inelastic-tendon assumption limit transfer. [Holzbaur, Murray and Delp (2005)](https://nmbl.stanford.edu/publications/pdf/Holzbaur2005.pdf), *A model of the upper extremity for simulating musculoskeletal surgery and analyzing neuromuscular control*, used a 2.7 µm normalization convention and population/cadaver priors. Their elbow/shoulder specific tension was selected to match joint moments, not measured as universal single-fiber stress. Neither source supplies this atlas's reference map.

[Adkins et al. (2022)](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.817334/full) measured sarcomere lengths in living human long-head biceps and flexor carpi ulnaris with microendoscopy, including unimpaired and stroke participants. Passive posed lengths and anatomical variability affect inferred optimal fascicle length and PCSA. This is architecture evidence, not crossbridge kinetic calibration.

[Blemker, Pinsky and Delp (2005)](https://nmbl.stanford.edu/publications/pdf/Blemker2005.pdf), *A 3D model of muscle reveals the causes of nonuniform strains in the biceps brachii*, used curved fascicles, internal aponeuroses and external fascia in a quasi-static long-head-inspired continuum. Their active optimum uses deviatoric stretch and a source-specific value 1.4; the numerically equal passive transition parameter has a different meaning. Architecture altered regional strains in their comparisons, but does not prove stability of the current witness. Do not copy the optimum or support stiffness to move the current fixture off its descending branch.

[Krivickas et al. (2011)](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/expphysiol.2010.055269) studied chemically skinned human vastus lateralis type-I fibers at 15°C, pCa 4.5 and near-optimal sarcomere length. The retained mean 15.5 N/cm² = 155 kPa is a peak-stress anchor for that preparation, not a biceps force–length width or reference-map calibration. Distinguish nominal and current-area stress and document PCSA, passive subtraction and pennation. Do not multiply by serial sarcomere count or apply pennation twice.

Tendon compliance changes contractile operating length and global response. A remote end spring supplies no direct restoring work to a perturbation whose endpoint displacement is zero. Distributed aponeurosis/fascia can alter load paths and tangents; whether it changes this mode requires an actual separately qualified comparison.

## Smallest defensible modeling choices

| Choice | Recommendation and limit |
| --- | --- |
| Reduced Hill-type contractile element, activation/fiber-length states, force–velocity response, compliant tendon | First bounded source-reproduction benchmark. Explicit educational parameters are allowed; it does not certify 3D shape or human biceps. |
| Reference-aware additive active-stress continuum | Capstone direction after reference, passive tissue and load-path calibration. Couple mechanics and actuator work consistently and count each force once. |
| Serial heterogeneous crossbridge/titin model | Optional mechanism study after reproducing original protocols and identifying data that distinguish competing mechanisms. |
| Active strain, stronger damping or new overlap law selected by eigenvalue sign | Unsupported selection criterion. Each requires independent constitutive evidence. |

[Millard, Uchida, Seth and Delp (2013)](https://nmbl.stanford.edu/publications/pdf/Millard2013.pdf), *Flexing computational muscle: modeling and simulation of musculotendon dynamics*, separates activation, fiber length, force–velocity response and tendon compliance and explicitly discusses descending-branch length instability. Its rat/cat force comparisons and numerical damping choices do not establish human-biceps kinetics or a physical cure. The [official implementation](https://github.com/opensim-org/opensim-core/blob/main/OpenSim/Actuators/Millard2012EquilibriumMuscle.h) also documents numerical floors and configuration choices. That `main` link was inspected for this decision; the reproduction benchmark must pin an immutable revision.

For target tendon-force control, let an explicit controller drive excitation. Actual activation, tendon force and motion are coupled responses under the variable external mass. Do not prescribe actual tension and activation as independent incompatible constraints. Controller gains, delays, saturation and energetic interpretation require their own declaration and qualification; no controller is implied by the constitutive law.

## Research before physiological implementation

1. Establish reference pose, fascicle trajectories and paired reference/optimal lengths, or transparently declare an educational population prior and uncertainty. Determine operating q over lift/release with tendon compliance.
2. Obtain compatible active/passive force–length, force–velocity and activation/recovery data. Peak stress alone is insufficient; submaximal activation need not share the fully activated curve.
3. Establish tendon/aponeurosis slack lengths, prestrain, areas, compliance, attachments and joint moment arms.
4. Pin the source implementation and reproduce units, initialization, states, numerical floors and curve conventions. This bounded task can proceed now without patient anatomy.
5. Define control targets and observation times; separate rapid perturbations, finite holds, shortening/post-stretch histories and mathematical fixed-activation equilibrium.
6. Predeclare matched-initial-force comparisons, preserve failed branches, and require geometry, residual, work/energy and refinement evidence before whole-arm deformation claims. No skin until the envelope is credible.

The source-reproduction benchmark is not delayed by missing anatomical datasets. Its declared educational scope is the basis for proceeding, not a substitute for physiological evidence.
