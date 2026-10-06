# Pinned source PE/SE units and conditional coefficient transformations

**The pinned implementation has a coherent internal elastic coordinate and force scaling, but it does not identify the missing SI force/area calibration or resolve final-publication coefficient labels.** Its PE force prefactor is kpe/K; its SE force prefactor is kse0. Output scaling multiplies both CE and PE in the main fitting path. A reported stiffness number cannot be copied into a force prefactor without declaring the coordinate, width, normalizer and selected source variant.

Read-only audit dated 2026-10-06. [Code-unit facts](../../data/anatomical-arm-v1/review/source-unit-calibration/code-unit-facts.json) record 20 independently read immutable blobs from commit `8c766dfb308051309193e7290ddd0bac3b726d11`, tree `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`, dated July8,2026. The commit/tree association and complete recursive tree were reread through authorized GitHub tools; returned immutable-blob identities matched their pinned tree paths. No LICENSE/COPYING-named file was present in that complete tree. No author code was imported, executed or copied into committed deliverables. This July revision is distinct from the final September article.

## Coordinate and force declarations

[Test/README.md:36](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Test/README.md#L36) declares seconds, reference-length units, reference lengths per second and micromolar calcium. [normalize_data.m:151](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/normalize_data.m#L151) supplies relative length change ε=(L−Lbaseline)/Lbaseline. The fitting routine then forms internal length Lts=Γε. The [reproduction script:344](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/reproduce_model_fitting.m#L344) resets stroke h=10nm and sarcomere length s=2.6µm, giving dimensionless Γ=s/(2h)=130.

If a declared physical reference length satisfies Lref=Ns s and h=dps, the physical conversion is ℓγ=Lref/Γ=2Ns dps, in metres per internal normalized link coordinate. Γ multiplies relative displacement; ℓγ divides physical displacement. They are not equal bare parameters. A physical offset must also be declared; a negative code PE onset is not automatically a negative absolute tissue length. The historical inspected MAT's h=12nm versus stored Γ=130 remains a separate version inconsistency recorded in [earlier parameter facts](source-code-parameter-facts.json); that MAT was not reread or selected here.

Write S=Fscale and normalized output Fhat=S Fint. To obtain newtons, additionally declare Tref, the physical force represented by the processed output normalizer, and set C=Tref S. This is a conditional unit map. It does not identify Tref from the saved Fmax value or supply an area. For stress one must further declare a matched reference/current section and use the appropriate force/area convention.

## Exact code elastic laws and tangents

[get_PE.m:3](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/get_PE.m#L3), blob `cb615867322c00c936638ca8f3934e26cd6955b0`, uses u=Lce−Lce0. In its soft branch Ku<10,

\[
F_{{\rm PE},\rm int}=\frac{k_{\rm pe}}K\ln(1+e^{Ku}),\qquad
\frac{dF_{{\rm PE},\rm int}}{du}=k_{\rm pe}\,\operatorname{sigmoid}(Ku).
\]

At u=0 the force is kpe ln2/K and slope kpe/2: the onset is not a zero-force slack length. For Ku≥10 the code uses kpe u and derivative kpe. There is a small value/tangent mismatch at the cutoff; the whole piecewise function is not an exact globally smooth softplus.

[complete_parms.m:14](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/complete_parms.m#L14), blob `f5656cc5dc7da581d29f68c74cc509c93ff6a155`, defines the SE law and inverse:

\[
F_{{\rm SE},\rm int}=k_{\rm se0}(e^{k_{\rm se}v}-1),\quad
v=\frac{\ln(1+F_{{\rm SE},\rm int}/k_{\rm se0})}{k_{\rm se}},\quad
\frac{dF_{{\rm SE},\rm int}}{dv}=k_{\rm se}(F_{{\rm SE},\rm int}+k_{\rm se0}).
\]

Here v is internal series extension, not independently measured tendon length. Negative v gives negative exponential force. A separate approximate path in [get_force_and_stiffness.m:4](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/get_force_and_stiffness.m#L4) clamps force/inverse extension and CE force; that changes its admissible law and must remain a distinct variant.

## Conditional dimensional transformations

For the same soft-branch code variant, let u=(ℓCE−ℓPE0)/ℓγ and v=(ℓSE−ℓSE0)/ℓγ. Algebra gives

\[
T_{\rm PE}=\frac{Ck_{\rm pe}}K
\ln\!\left(1+e^{K(\ell_{\rm CE}-\ell_{{\rm PE},0})/\ell_\gamma}\right),\qquad
K_{\rm PE}^{\rm SI}=\frac{Ck_{\rm pe}}{\ell_\gamma}
\operatorname{sigmoid}\!\left(\frac{K(\ell_{\rm CE}-\ell_{{\rm PE},0})}{\ell_\gamma}\right).
\]

The force prefactor is Ckpe/K in N, softening width ℓγ/K in m, and asymptotic slope Ckpe/ℓγ in N/m. For SE the force prefactor is Ckse0 in N and exponent coefficient kse/ℓγ in m⁻¹, giving KSE=(kse/ℓγ)(TSE+Ckse0). Normalized-output prefactors are S kpe/K and S kse0; normalized PE slope per internal u is S kpe. These identities supply no numerical SI calibration.

For a pure elastic coordinate change unew=a uold at unchanged force scale, exact law preservation requires kpe_new=kpe_old/a, Knew=Kold/a, onset_new=a onset_old, kse_new=kse_old/a and kse0_new=kse0_old, with the corresponding series offset scaled. The [reproduction script:347](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/reproduce_model_fitting.m#L347) instead visibly rescales only kpe by Γold/Γnew. For a genuine coordinate change this preserves the linear PE slope per relative input; alone it does not preserve an entire softplus or exponential law. The previously inspected individual MAT already stores Gamma=130, so its old/new ratio would be one under that reproducer; this derivation does not claim an actual coordinate change for that individual file. This derivation concerns elastic coordinate conversions, not a change to powerstroke, kinetic rates, density measure or specimen parameters.

## Fitting, runtime and parameter summaries remain separate

The main active [fitting path:149–171](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Fitting/fit_model_parameters_v2.m#L149), blob `fd56f3368c01f9f38640875382fecd74ca59dccc`, fixes K=1, uses raw CE=Q0+Q1, enforces FSE=CE+PE and compares Fscale·FSE to data. Its tangent is kpe sigmoid(Ku) before scaling. The passive fitting path uses linear PE and also multiplies by Fscale. The [old comparison script:62–64](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/compare_parms_versions.m#L62) visibly adds Fpe_func output to an already scaled CE term; that function's own scaling must be verified before assigning the resulting units. It is not the main fitting objective.

The runtime PE uses parms.K; the historical individual MAT's K=100 is a preserved stored metadata observation, not an article median. Initialization has a separate linear force-balance expression. Runtime discretized CE is softened by log(1+exp(KQ))/K, while reported force uses raw moments plus PE, multiplied together by Fscale. Differentiating the softened runtime CE would require sigmoid(KQ) in both its kinetic reaction derivative and frozen-population tangent; the observed runtime velocity formula uses raw reaction/tangent terms. This is a force/tangent convention discrepancy to disclose in any replay, not a unit conversion that this audit silently fixes. Lowercase lce0 transport origin and uppercase Lce0 PE onset also remain distinct.

The closest inspected summary script is [evaluate_parameters.m:9,23–25,40–42](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/evaluate_parameters.m#L9), blob `c0f7459218ea95ab1e95609735ac5ad913dfdd56`. It reads raw parameter fields including kpe,kse,kse0 and prints their componentwise medians. It contains no Fscale or /K transformation. Thus **that script summarizes raw kpe/kse0**, but its association with final Table3 and the exact parameter-family/version files is not proven. It does not establish that final two-state numbers .002/.19 are normalized PE/SE force prefactors, nor may one individual MAT stand in for those medians.

## Publication labels and calibration still unresolved

The parent's original-pixel reread gives Eq17–20 with physical γ=2Ns dps, a PE coefficient multiplying a log/exponential shape, and an SE force coefficient. The [primary article prose](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748) calls strain centered/normalized relative to the stroke. No distinct xps definition was recovered in this lane's inspected prose or pinned source; inline equation/table images prevent an exhaustive text search. Table xps⁻¹ therefore cannot be silently equated to physical10nm. If xps labels a normalized coordinate, an SI dimensional inconsistency need not follow, but prefactor-versus-slope interpretation still requires the width and normalizer. If it is a physical length unit, the PE formula needs a declared length factor converting stiffness to force. Full article/code matching additionally requires the same softening width and offsets, not just a prefactor match. This audit leaves the ambiguity open.

[calc_force_pCa.m:50,87,108](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L50) gain-corrects raw force by /1000/gain, averages selected early samples, takes pCa-specific medians and chooses each fiber's maximum. [normalize_data.m:154](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/normalize_data.m#L154) forms trace/prestretch-mean ×F0(pCa)/Fmax. These ratios yield a dimensionless target. No pCa9 subtraction occurs in those inspected operations; upstream tare/passive conventions remain unknown.

Needed data are the exact raw channel/sensor/gain calibration, same-specimen force denominator, area/configuration, reference length/sarcomere map, passive/series offsets and initialized force balance, chosen complete force transform, and final table/export convention. No human15°C rates or temperature conversion are mixed with the rat22°C source family. No numerical model/trajectory, source import/execution, Git operation, old-file edit or physiological coefficient selection occurred.
