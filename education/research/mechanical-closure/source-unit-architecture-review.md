# Human architecture and force–area calibration review

Research-only addition to the source-unit audit of frozen base `bc4f24a2`; 2026-10-06. No simulation, physical scale selection, or human constitutive coefficient is introduced. The machine-readable companion is [architecture-facts.json](../../data/anatomical-arm-v1/review/source-unit-calibration/architecture-facts.json). This complements the [dimensional mapping](dimensional-contractile-mapping.md) and [source calibration reconciliation](calibration-source-reconciliation.md).

**Finding:** the inspected upper-arm evidence supports geometry conventions and exposes inference assumptions. It does not close a measured force–area–sarcomere calibration for the authored BICshort geometry. A direct human gracilis study is a useful bounded comparison, but its optimal fibre length and maximal force include explicitly reported inference/correction. Neither its population stress nor a cadaveric arm PCSA can supply this model's force scale.

## Original evidence and its boundaries

**Murray, Buchanan & Delp (2000), original human elbow study.** Ten unembalmed upper extremities from nine cadavers were frozen, thawed, dissected and partly formalin-fixed. Measured fascicle length and laser-diffraction sarcomere length give

\[
L_{f,\mathrm{opt}}=L_{f,\mathrm{meas}}\frac{2.8\,\mu\mathrm m}{l_{s,\mathrm{meas}}}.
\]

The adopted optimum is a convention. PCSA is explicitly \(A_P=V/L_{f,\mathrm{opt}}\), with \(V=m/\rho\) and assumed \(\rho=1.06\,\mathrm{g\,cm^{-3}}\). Cosine enters moment-generating potential separately: \(A_P r\cos\alpha\). Frozen postures differ; Table 2 reports group architecture with differing sample counts, not paired living active force. Operating-range estimates assume inelastic tendon/aponeurosis. These equations permit a specimen's architecture normalization when its actual paired measurements are available; they do not measure its specific tension. Locators: printed pp.944–945, Methods/Eq.1; p.946, moment-generating potential; p.947, Table 2. [Original author-hosted paper](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf).

**Kawakami et al. (1994), human elbow MRI/torque study.** The original publisher abstract describes four men with serial MRI area/volume and dynamometer torque. Fibre length uses previously reported fibre/muscle ratios; tendon force is calculated from torque and MRI moment arms. Thus same-subject MRI and torque do not make fibre length or individual tendon force direct measurements. Only the abstract was accessible: the ordinary publisher PDF route returned the subscription preview. No full-paper numbers or force-sharing equations are adopted. Locator: original Abstract, pp.139–147. [Original publisher article](https://link.springer.com/article/10.1007/BF00244027).

**Rockenfeller, Günther, Clemente & Dick (2024), original geometric analysis.** Its Eqs.1.1,1.2 and2.4 distinguish unprojected PCSA \(A_P=V/L_{f,\mathrm{opt}}\) from functional area \(A_F=A_P\cos\alpha\), and §2 distinguishes both from a single anatomical slice. This supplies an explicit convention, not new human-arm force measurements. [Original open-access article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11639153/).

**Lieber & Ward (2011), original architecture review.** The accessible text at §3 discusses force scaling and §5 warns that an ultrasound fascicle length lacks sarcomere normalization. Eq.3.1 is an image; this audit obtained its link but could not inspect its pixels. Its exact cosine convention is therefore not transcribed or attributed here. The ordinary image request failed at the proxy tunnel with HTTP403; no challenge or workaround was attempted. [Original open-access review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3130443/).

**Binder-Markey et al. (2023), bounded paired comparison.** Twelve complete living human gracilis datasets were acquired during thigh-to-arm transfer surgery. Distal-tendon buckle force and optical muscle volume are paired. Eq.1 corrects submaximal stimulation to maximal force; optimal fibre length is inferred from force–length FWHM using an animal-derived relation. Volume validation reports 7% average error; fixation/laser diffraction measures passive sarcomere length. Results report specific tension \(171\pm84\,\mathrm{kPa}\), a cohort summary rather than a new arm input. The original supporting XLSX request returned403 and was not bypassed. This is a candidate for reproducing that study's *inferred whole-muscle calibration* if subject records become normally accessible; it is not a fully measured BICshort/reference-head calibration. Locators: Methods, Maximum muscle force calculation/Eq.1, Muscle volume calculation, Patient-specific optimal fibre length calculation; Results/Fig.6; Data availability/Supporting Information. [Original open-access article](https://physoc.onlinelibrary.wiley.com/doi/full/10.1113/JP284092).

## Area and stress contract: independent derivation

Use distinct symbols and record their configuration. Let \(A_P\) mean aggregate area perpendicular to the relevant fibres, \(A_F\) its tendon-axis projection, and \(A_A(z)\) an anatomical slice at location \(z\). A PCSA is generally an aggregate architectural quantity; it need not equal a mesh slice, an individual fascicle section, or tendon CSA.

For uniform fibre length \(L_f\), volume bookkeeping gives \(A_P=V/L_f\). For separate uniform bundles,

\[
A_P=\sum_k\frac{V_k}{L_{f,k}},\qquad
T_{t,\mathrm{act}}=\sum_k\sigma_{f,k}A_{P,k}\cos\alpha_k.
\]

The second equation assumes the declared fibre-to-tendon force paths and projections. It does not independently establish lateral force transmission or a complete three-dimensional equilibrium. Replacing the sum by volume divided by an arithmetic mean length is an additional approximation. For a uniform stress and angle, \(T_t=\sigma_f A_P\cos\alpha=\sigma_f A_F\). If a source's quantity named PCSA already contains cosine, multiply by its stress directly; applying cosine again projects twice. Conversely \(T_t/A_P\) is a tendon-output stress \(\sigma_f\cos\alpha\), not necessarily fibre stress. Tendon stress \(T_t/A_{\mathrm{tendon}}\) is another quantity.

For a homogeneous local material patch, take unit reference fibre \(a_0\), deformation gradient \(F\), \(J=\det F>0\), fibre stretch \(\lambda=|Fa_0|\), and current direction \(t=Fa_0/\lambda\). The projected current area normal to \(t\), transported from a reference fibre-normal area \(A_0\), follows Nanson's formula:

\[
A_c= A_0\,t\cdot(JF^{-T}a_0)=\frac{J}{\lambda}A_0.
\]

This is a **projected** section; a sheared transported material plane need not itself be normal to the current fibre. For the same tensile resultant \(T\),

\[
p=\frac{T}{A_0},\qquad \sigma_f=\frac{T}{A_c}=\frac{\lambda}{J}p,
\qquad P_{\mathrm{act}}=p\,t\otimes a_0,
\qquad \sigma_{\mathrm{act}}=\frac{\lambda}{J}p\,t\otimes t.
\]

Consequently a published stress cannot enter nominal stress, Cauchy stress or energy density interchangeably. Under this local contract, axial virtual power per reference volume is \(p\dot\lambda\); a passive potential, if specified, satisfies \(p_{\mathrm{pass}}=\partial W/\partial\lambda\). An activation-dependent kinetic force is not thereby a conservative passive potential.

Under a uniform, incompressible, unchanged fibre population, a pose at stretch \(\lambda_{\mathrm{pose}}\) relative to the optimal-fibre reference has \(A_{P,\mathrm{pose}}=A_{P,\mathrm{opt}}/\lambda_{\mathrm{pose}}\). This conversion requires the reference, deformation and fibre population; pennation is evaluated in the force-measurement pose. It cannot be inferred merely by equating an atlas centreline to a normalized fascicle.

## Serial length, parallel force and identifiability

For a chain of equal sarcomeres, \(N_s=L_{f,0}/l_{s,0}\). This determines a serial length/strain conversion. It does not multiply the transmitted force: serial sarcomeres share force in an ideal series chain. A fascicle is a bundle, and its visible length need not be one cell's full sarcomere-chain length. Using fascicle length as cell length needs an explicit architecture assumption.

For the kinetic model's dimensionless weighted population moment \(Q\), a possible dimensional contract remains

\[
T_{\mathrm{CB}}=H k_{\mathrm{CB}}d_{\mathrm{ps}}Q,\qquad
p_{\mathrm{CB}}=\frac{H}{A_0}k_{\mathrm{CB}}d_{\mathrm{ps}}Q.
\]

Here \(H\) is the available parallel head capacity associated with a force-transmitting cross-section, not all heads summed over serial sarcomeres; \(k_{\mathrm{CB}}\) has units N/m and \(d_{\mathrm{ps}}\) m. If a separately verified dimensional law is \(T=F_0Q/\beta\), matching identifies only the product \(Hk_{\mathrm{CB}}d_{\mathrm{ps}}=F_0/\beta\). Neither force/PCSA nor \(N_s\) individually identifies head density or head stiffness. Capacity/overlap already represented in \(Q\) must not be counted again in \(H\). Any tissue packing fraction must declare whether its effects are already included in a whole-muscle specific tension.

Likewise joint torque obeys a force-sharing relation such as \(\tau=\sum_k r_kT_k+\tau_{\mathrm{pass}}+\tau_{\mathrm{other}}\), with explicit signs and gravitational/inertial corrections. One torque measurement cannot identify several elbow-muscle forces without additional measurements or assumptions.

Unit conversions are exact bookkeeping: \(1\,\mathrm{cm^2}=10^{-4}\,\mathrm{m^2}\), \(1\,\mathrm{cm^3}=10^{-6}\,\mathrm{m^3}\), \(1\,\mathrm{g/cm^3}=10^3\,\mathrm{kg/m^3}\), \(1\,\mathrm{N/cm^2}=10^4\,\mathrm{Pa}\), \(1\,\mathrm{kPa}=10^3\,\mathrm{Pa}\). A mass unit labelled kg cannot silently become a force unit. The original file's unit and calibration must be established first.

## Closure needed for a worked calibration

An individual, calibrated tendon-force record could identify \(T_{\mathrm{ref}}\) at its documented posture and activation, after separating its passive component. It would identify \(\sigma_{\mathrm{ref}}\) only with that individual's paired area, its cosine/configuration convention, and the fibre-to-tendon projection. Murray supplies no measured active force; Kawakami's individual muscle force is inverse-derived. In Binder-Markey, the measured stimulation force is observational, whereas \(P_o\) and the PCSA using FWHM-derived optimal length make the reported specific tension an **inferred whole-muscle normalizer**. It is not a directly measured local Cauchy stress. The inaccessible supporting rows prevent this audit from constructing even a subject-level reproduction of that normalizer. Its cohort summary cannot identify an actual specimen's \(T_{\mathrm{ref}}\) or \(\sigma_{\mathrm{ref}}\).

In particular, this candidate does not identify a compatible human calibration of the rat 22°C median CE model. Matching a specimen's measured maximum force would require that model's activation, overlap, reference state and recruitment to match the experiment, or explicitly introduce and validate a transfer assumption. No such transfer is selected here.

No fully measured numeric upper-arm calibration is selected. A reviewable same-specimen candidate requires:

- Identified muscle/head, specimen/preparation, posture, temperature and activation; sensor-to-newton calibration, zero/tare, passive contribution and uncertainty; tendon force or independently supported force sharing.
- Paired volume or mass/density, fibre-normal area convention, fibre/fascicle length and sarcomere length in a known configuration; pennation and force-path definition in the force-measurement pose. Normalized optimum and fixation corrections remain declared assumptions.
- A dimensional force scale at the same overlap/reference state as \(Q\); an explicit reference/current area choice and deformation if converting stress; compliant tendon/aponeurosis data if whole-MTU length is to determine CE length.
- Additional independent molecular evidence to separate \(H/A_0\), \(k_{\mathrm{CB}}\) and \(d_{\mathrm{ps}}\), if those are claimed as measured parameters.

Published group means cannot create a same-subject row: the product of mean area and mean stress generally differs from mean force. A cohort mean/SD is not an admissible human parameter interval without a sampling model. The authored atlas arc and Arm26 optimal-fibre input are different provenance classes; the frozen experiment's fitted stress is not a measured human specific tension. The rat source normalization issue remains governed by the separate calibration audit.
