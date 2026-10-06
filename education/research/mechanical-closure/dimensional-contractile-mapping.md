# Dimensional contractile mapping before a controlled release

**A dimensionless cross-bridge moment is neither newtons nor pascals. Force requires a parallel-head capacity and single-head force scale; stress additionally requires a declared area convention. Serial sarcomere count supplies the length-to-link-strain map, not another force multiplier.** This document derives a bounded mapping and identifies calibration obligations. It selects no human head density, stiffness, force scale, passive offset or constitutive replacement, and runs no simulation.

Prepared 2026-10-06. Read with [reference-architecture-source-review.md](reference-architecture-source-review.md), [source-notation-and-lesson-implications-addendum.md](source-notation-and-lesson-implications-addendum.md), [contractile-state-source-review.md](contractile-state-source-review.md) and [cooperative-population-audit.md](cooperative-population-audit.md). The original fixed-capacity direct-CE fixture and all earlier negative witnesses remain unchanged.

## Source scope and notation

[Van der Zee et al. (2026), original article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748) and [publisher PDF, equations 3–4 and 14–22](https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1014748&type=printable) describe permeabilized rat soleus preparations at 22°C: eleven fibers, seven fitted. Reference preparation length was 0.8±0.2 mm, sarcomere length 2.60±0.05 µm; serial count **306±78** is this preparation's mean/SD, not a whole human fiber count. Model assumptions include dps=10 nm, kCB=0.5 pN/nm and β=0.5. Overlap was fixed to one near optimum; the paper does not validate a human descending-overlap map. Empirical forces were normalized by maximal isometric F0 at pCa 4.5. Its PE/SE parameters were fitted, not independently measured tissue constants.

Original PDF text extraction was readable through an already successful public-source reference; no rendered equation pixels were inspected. Fresh direct printable/thumbnail requests failed and were stopped. The [source-code initialization audit](source-code-initialization-audit.md) pins a prepublication source-code revision; final article equations and that code must remain distinct. This derivation uses the stated article convention. It does not claim code parity, import code, or overwrite the frozen mathematical fixture.

## 1. Density measure, attached fraction and dimensional force

Use the article's centered, dimensionless strain coordinate

\[
x=(d-d_{\rm ps})/d_{\rm ps},\qquad d=d_{\rm ps}(1+x).
\]

Let n(x,t) be an attached-population fraction density per unit normalized strain. Define

\[
B=\int n\,dx,\qquad Q=\int(1+x)n\,dx=B+\int x n\,dx.
\]

B and Q are dimensionless. A density ordinate is not a per-bin fraction: a discrete mass is approximately ni Δxi. If instead the dimensional centered displacement is y=d−dps in metres, the correctly transformed density is p(y)=n(y/dps)/dps, with units m−1 and ∫p dy=B. Dropping that measure factor changes both the population and force.

Now declare **H**, the number of potential parallel heads represented by one common half-sarcomere force-bearing cross-section at the chosen maximal-overlap reference. H is a count, not the number of heads along the entire fiber. For identical linear heads with kCB in N/m, our dimensional aggregation gives

\[
T_{\rm CB}=H\int k_{\rm CB}d\,n(x)\,dx
=\underbrace{H k_{\rm CB}d_{\rm ps}}_{C_{\rm CB}\,[\mathrm N]}Q.
\]

Equivalently TCB=H kCB∫(dps+y)p(y)dy. The source-assumed stiffness converts to 5×10−4 N/m and its stroke to 10−8 m, so their product is 5×10−12 N per attached head at x=0. This unit conversion identifies a source-model head force; it supplies no human H or force capacity.

H counts available structural capacity at the selected denominator; B already counts attachment. If n also contains overlap, thin activation and recruitment effects, multiplying TCB by another B, activation or overlap factor would count them twice. If the denominator varies with recruitment/geometry, specify how the physical capacity and fraction states transform. Keep a fixed reference capacity for the first dimensional declaration.

Heads within each half-sarcomere act in parallel; successive half-sarcomeres act in series and transmit the same force. Multiplying TCB by serial count Ns would therefore be incorrect. H also differs from microscopic fiber count, myofibril count, protein mass fraction and a continuum quadrature weight.

## 2. What F0/β normalization constrains

Write normalized article force as fCE=Q/β and dimensional candidate force as TCE=F0 fCE, where **F0 in this derivation is a physical force in N** for a specified specimen/protocol. It is not automatically an SI interpretation of a source file's variable named F0. Compatibility with the linear-head aggregation requires

\[
C_{\rm CB}=Hk_{\rm CB}d_{\rm ps}=F_0/\beta.
\]

This is a calibration constraint on a product, not independent measurements of H and kCB. Force alone cannot identify both. If H is inferred using assumed kCB,dps, label H **inverse fitted conditional on those assumptions**. If a measured area is used instead, the same equation constrains the effective stress scale F0/A0. The repository's fitted σ0 cannot supply either factor without matching the preparation, area, stress convention and operating state.

The [source-code initialization audit, force normalization](source-code-initialization-audit.md) records that pinned `normalize_data` uses **(raw trace/baseline)×F0_i,pCa/Fmax_i**, which yields a dimensionless target. Such ratios do not identify a force in N or a reference/current section area. A plot axis labeled kPa is insufficient evidence for that dimensional calibration. If the raw measurement is stress, recover its verified area/configuration convention before converting to force; if it is force, retain the sensor units and specimen geometry. The SI scale remains unresolved here.

Maximal normalized **CE** force equals one only if its actual initialized/equilibrated moment Q*=β. An attached fraction B*=β is insufficient when ∫x n dx is nonzero. Combining parameter medians also need not preserve an individual fit's Q*. Preserve reported B*, Q*, mean attached strain and Q*/β; do not rescale Q to hide a failed normalization.

Further distinguish measured **total fiber** force from CE force. If F0 is total maximal isometric force, the model must satisfy

\[
1=Q_*/\beta+f_{\rm PE}(L_{{\rm CE},*}),
\]

at the calibration state. If F0 is a passive-subtracted active force, that subtraction must be documented and the total target reconstructed. A nonzero PE force cannot simultaneously be counted in F0 and added again without adjusting this constraint. This memo does not assume the authors' exact per-fiber subtraction/initialization convention.

The [source-code initialization audit, runtime and output conventions](source-code-initialization-audit.md) records a nonlinear positive force transformation in the pinned version. If that version is later selected, write its actual function G(Q) and use TCE=F0 G(Q), with tangent F0 G′(Q) times the state derivative. The raw Q/β compatibility above then applies only if G is that linear map. Softplus or clipping, their scale/offset, and normalization at Q=0 and Q* are physical/code conventions requiring explicit verification; they are not unit conversions.

## 3. Reference area, nominal traction and Cauchy stress

For a declared straight homogeneous bundle, let A0 be its reference area perpendicular to a0, λf=|F a0|, J=det F and t=F a0/λf. The current area normal to the fiber, or the fiber-normal projection of the transported section, is A=A0 J/λf. Define η0=H/A0 in heads/m². Then

\[
p_{\rm CB}=T_{\rm CB}/A_0=\eta_0 k_{\rm CB}d_{\rm ps}Q,
\qquad \sigma_{\rm CB}=T_{\rm CB}/A
=\frac{\lambda_f}{J}p_{\rm CB}.
\]

The corresponding oriented contributions are

\[
P_{\rm CB}=p_{\rm CB}\,t\otimes a_0,\qquad
\boldsymbol\sigma_{\rm CB}=\sigma_{\rm CB}\,t\otimes t
=J^{-1}P_{\rm CB}F^T.
\]

These are a uniaxial bundle homogenization, not a full transverse/shear constitutive law. For nonuniform architecture, integrate actual stresses/tractions with declared orientation and area/volume weights. A tendon reaction generally requires equilibrium and force transmission; it is not local stress multiplied by an atlas belly area. A simple uniform pennation projection would use fiber force times cosα, with the relevant fiber angle and area convention, rather than silently interpreting fascicle area as tendon area.

If capacity is calibrated to **contractile area**, report contractile packing fraction and conversion to total muscle area. If F0/area is already an effective whole-muscle value, applying packing fraction again counts the reduction twice. Geometric V/L, PCSA, microscopic fiber section and current anatomical cross-section remain different quantities. Continuum quadrature already contributes volume/area weighting and must not receive another microscopic count multiplier.

## 4. Serial geometry and length-to-link strain

The stated article convention maps CE length increments by

\[
\Delta L_{\rm CE}=\gamma\Delta x,\qquad
\gamma=2N_s d_{\rm ps}\ [\mathrm m],\qquad
\dot x=\dot L_{\rm CE}/\gamma.
\]

The factor two counts half-sarcomeres; it does not count parallel heads. Conditional on the fixed source stroke, its preparation count gives γ=6.12±1.56 µm by linear mean/SD conversion. This is a rat-preparation scale, not a permissible human range or a tendon rest length.

The [source-code initialization audit](source-code-initialization-audit.md) traces a different variable convention to [the prepublication reproduction script at pinned revision 8c766dfb308051309193e7290ddd0bac3b726d11](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/reproduce_model_fitting.m#L344): h=10−8 m, assumed s=2.6×10−6 m and code `gamma=0.5*s/h=130`, with input length changes normalized by L0. For εCE=ΔLCE/L0, our conversion is

\[
\Delta x=\Gamma\Delta\varepsilon_{\rm CE},\qquad
\Gamma=L_0/\gamma_{\rm phys}=\frac{s}{2d_{\rm ps}}
\quad\text{if }L_0=N_s s.
\]

Thus code Γ=130 is dimensionless and multiplies normalized length change; article γphys=2Ns dps is a length and divides dimensional length change. Their relation is Γ=L0/γphys, not equality and not an unqualified reciprocal across units. The script's selected s is a model input distinct from the preparation's measured Ns and sarcomere statistics. Formula consistency alone does not resolve exact initialization/offset conventions or final article/code parity.

The [same audit's immutable individual MAT inspection](source-code-initialization-audit.md) records lowercase `lce0=0`, uppercase `Lce0≈−10`, Γ=130, `Fscale=2`, `K=100`, `w=1/6` and richer saved fields `ps=1`, s=2.6 µm, h=12 nm and `Fmax=120`. These are fields of one individual code fixture, **not publication medians or a selected calibration**. The historical h gives s/(2h)=108.33 rather than 130; the reproduction script's 10 nm override gives 130. A replay must select and record one convention. The dimensional units of `Fmax=120` remain unresolved. Lowercase `lce0` is a transport origin and uppercase `Lce0` a passive onset; they cannot be interchanged. The inspected lowercase zero removes that fixture's conditional runtime/output coordinate discrepancy, but establishes no parity for other files.

For a measured homogeneous human contractile chain, a **proposed** specimen map would use Ns≈LCE,0/ℓs,0, LCE,opt≈Ns ℓs,opt and λrefopt=LCE,opt/LCE,0. [Murray et al. (2000), original equation 1](https://nmbl.stanford.edu/publications/pdf/Murray2000.pdf) normalizes measured human fascicles with measured sarcomere length and a chosen optimum. Its group architecture estimates cannot replace paired observations for this specimen. [Adkins et al. (2022), original Methods/Results](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2021.817334/full) demonstrate live long-head biceps sarcomere sampling and approximately 0.25 µm combined uncertainty; no atlas-subject mapping follows.

LCE is the contractile-chain coordinate, not automatically the complete fascicle arc, centerline, total musculotendon path or whole preparation length. With compliant series tissues, those lengths differ. Nor is absolute cross-bridge extension dps(1+x) the macroscopic sarcomere length ℓs: overlap depends on filament/sarcomere geometry, while x represents attached-link strain and memory. Declaring overlap O(ℓs) needs a measured/reference force–length relation and population-capacity rule. The source's O=1 near optimum cannot supply it on a human descending branch. Adding an independent instantaneous fL multiplier to Q requires a separately justified hypothesis.

## 5. Compliant series/parallel path and physical stiffness

The article's interface has LPE=LCE, Lfiber=LSE+LCE and Tfiber=TSE=TCE+TPE. For an unambiguous SI transcription of its displayed functional forms, define ξPE=(LCE−LPE,0)/γ and ξSE=(LSE−LSE,0)/γ, and define normalized force coefficients κPE, ŝSE and dimensionless exponential slope ρ̂:

\[
T_{\rm PE}=F_0\kappa_{\rm PE}\ln(1+e^{\xi_{\rm PE}}),\qquad
T_{\rm SE}=F_0\hat s_{\rm SE}(e^{\hat\rho\xi_{\rm SE}}-1).
\]

These new symbols prevent confusing source SE σ with a continuum stress in Pa. They also prevent reading a strain-coordinate stiffness coefficient as N/m. Original Table 3 retains F0 and inverse cross-bridge-strain labels; the conversion of its bare numbers must be checked against the selected length/strain units and code version. The equations above define a dimensionally coherent convention, not automatic parameter parity. In particular, the [source-code initialization audit](source-code-initialization-audit.md) finds runtime PE sharpness K=100 in the inspected MAT but K=1 hardcoded in the fitting routine. Neither value can be transferred into this article-style κPE without matching its argument, prefactor and force scaling.

Differentiation gives physical local slopes

\[
K_{\rm PE}=\frac{F_0\kappa_{\rm PE}}{\gamma}\frac{1}{1+e^{-\xi_{\rm PE}}},\qquad
K_{\rm SE}=\frac{F_0\hat s_{\rm SE}\hat\rho}{\gamma}e^{\hat\rho\xi_{\rm SE}}\quad[\mathrm{N/m}].
\]

Thus force normalization and serial geometry are needed even to compute a stiffness. Softplus gives TPE=F0 κPE ln2 at its nominal resting offset; it is not a zero-force slack cutoff. The exponential gives negative force for ξSE<0; a tensile-only admissible domain or another physical law must be declared rather than silently clipping it.

The rat source PE represents internal parallel compliance; its SE includes preparation/attachment and heterogeneous sarcomere effects. Neither is an anatomical tendon/aponeurosis/fascia law by identity. A human free tendon and distributed sheets require their own geometry, rest metrics, force–extension/area conventions and force paths. They must not duplicate compliant terms already represented in an effective fiber fit.

At fixed attached material populations, a small translation produces ΔQ=B ΔLCE/γ. Therefore the linear-head fast CE stiffness is

\[
K_{{\rm CB},{\rm fast}}=C_{\rm CB}B/\gamma=Hk_{\rm CB}B/(2N_s).
\]

This formula explains the different roles of parallel H and serial Ns. It is a fast held-population derivative, not the relaxed force–length slope or a complete dynamic stability certificate. For the declared massless one-dimensional topology, the fast end stiffness would be KSE(KPE+KCB,fast)/(KSE+KPE+KCB,fast), provided those slopes/held-state assumptions hold. It does not stabilize every interior mode of a continuum.

## 6. Reference, initialization and work obligations

The active optimum LCE,opt, passive offset LPE,0, series zero-force length LSE,0, imaging pose and initial attached-link strain are separate inputs. Equating them creates new assumptions. At the initial total length solve the dimensional balance

\[
R(L_{\rm CE})=T_{\rm SE}(L_{\rm fiber}-L_{\rm CE})
-T_{\rm PE}(L_{\rm CE})-T_{\rm CE}=0.
\]

Declare whether changing LCE during initialization holds the Eulerian density n(x) or material attached labels. The latter translates n and changes TCE; it must be included in the residual/tangent. Report the root, permissible compression/tension domain, actual populations, force normalization and relaxation duration. No guessed offset is justified by a visually plausible reference pose.

For mechanical bookkeeping, a frozen attached population has aggregate link elastic energy

\[
E_{\rm CB}=2N_sH\int\tfrac12 k_{\rm CB}d_{\rm ps}^2(1+x)^2n(x)\,dx.
\]

With γ=2Ns dps, its translation derivative is dECB/dLCE=TCB. Serial links add energy, while transmitted force remains the same. Attachment/detachment changes this mechanical energy and requires a chemical/dissipation accounting; this expression is not the total ATP/free-energy law. Under the circuit's equilibrium constraint, external power Tfiber vfiber splits into TSE vSE+(TCE+TPE)vCE. A continuum implementation must preserve this work relation and avoid adding the old active term to a replacement CE contribution.

## 7. Evidence bounds and fields still missing

| Field | Current evidence / status | Permissible use |
|---|---|---|
| Rat preparation Ns, reference length/sarcomere length, temperature | Measured source-group mean/SD | Bounds source-preparation variability, not human inputs; group SD is not a hard specimen interval |
| dps, kCB, β | Assumed source-model parameters | Defines an explicitly nonhuman model scale; not a measured human density/stiffness |
| F0 in SI force units | Source normalization ratios readable; absolute trace units/area conversion unresolved; human value absent | Needed per specimen in N, with passive subtraction and held-state protocol stated |
| H or η0, contractile area/packing | Human mapping unknown | No numerical human force/stress coefficient can be selected from Q alone |
| Rate, activation, PE/SE coefficient sets | Source literature choices and per-fiber inverse fits | A reference-model fixture, not independent human measurements or a guaranteed combined-median fit |
| Paired human CE/fascicle/sarcomere reference geometry | Measurement routes available; atlas mapping absent | Required for Ns, γ and overlap; authored atlas arc does not supply them |
| Passive rest metrics, tendon/sheet geometry, distributed shear/load sharing | Missing for the current specimen | Cannot identify series or parallel stiffness from the atlas surface or population mean |
| Population/force maps and initialization in selected version | [Source-code initialization audit](source-code-initialization-audit.md) resolves distinct fields and records remaining parity obligations | Pin equation/code version before dimensional replay; retain fixed-capacity fixture unchanged |

Population bounds supply a limited mathematical force bound: if n≥0, B≤O≤1 and x lies in a declared finite interval [xmin,xmax], then (1+xmin)B≤Q≤(1+xmax)B. Without a strain bound, B≤1 alone supplies no finite Q bound or tensile-force guarantee. These are conditional mathematical bounds, not measured human ranges. A finite strain truncation is a numerical/domain choice, not a physiological coefficient interval.

Before a dimensional controlled release, specify one consistent force/area scale, serial length map, selected force transformation, passive/series circuit, initial equilibrated state and source/version identity. Source table alignment and formula rendering remain visually unverified. The [source-code initialization audit](source-code-initialization-audit.md) distinguishes CE reference offsets, historical length scales and runtime/reporting force maps; exact final-article parity remains unestablished. This memo provides no substitute for those gates. Validate dimensions and initial force/work balance before evolving the state. A release using uncalibrated human scales would remain a labeled synthetic experiment; it could not qualify the atlas arm or replace the retained active-stability evidence.
