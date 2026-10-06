# Pinned source-code initialization, population and normalization audit

## Finding and scope

**The pinned author code includes population transfer that was absent from the earlier article-equation excerpt. In the two-state code, detached population is generally \(M=1-B\), not a permanently fixed \(M=1\).** A source implementation and the existing direct-CE equation fixture therefore describe distinct kinetic systems. Preserve the old fixture and its results; do not rename it an exact author-code trajectory replay.

This is a read-only source audit, with one temporary individual-parameter measurement. No source code was executed, imported into the repository, or installed. No simulation, coefficient selection, old-file edit, Git operation, or production/book/Lean change occurred. This new document supplements [cooperative-population-audit.md](cooperative-population-audit.md); its conditional mathematical analysis of the displayed article equation remains conditional, while this audit resolves the inspected code convention.

All code claims below are pinned to commit [`8c766dfb308051309193e7290ddd0bac3b726d11`](https://github.com/timvanderzee/biophysical-muscle-model/commit/8c766dfb308051309193e7290ddd0bac3b726d11), tree `a802ec6f7299d0745dfab1d5b715a3d9b7aa6f20`. The commit date is **2026-07-08T12:06:31Z**, preceding the September publication. It is evidence for this repository revision, not proof of parity with the final published algorithm. Each inspected text blob hash matches the pinned recursive tree. No LICENSE/COPYING path appeared in that complete tree. Only factual parameter measurements and independently expressible mathematics are recorded here; no author file or MAT binary is redistributed.

The original publication Table 2/3 pixel-verification prerequisite remains **BLOCKED**, as recorded in [visual-parameter-column-audit.md](visual-parameter-column-audit.md). Readable author code does not satisfy that separate prerequisite. No coupled controlled-release experiment is authorized by this audit alone.

## Population variables and family branches

In the discretized state vector, the last four entries are CE length, available thin-filament sites \(N\), detached relaxed population \(M\) (code `DRX`), and forcibly detached population \(R\). Attached population is \(B=\int n(x)dx\). The thick-filament routine explicitly defines

\[
S=1-B-M-R,\qquad J_1=k_1(1+k_F F/N_{\rm tot})S,\qquad J_2=k_2M.
\]

The caller computes reaction-only \(\dot B\), and then uses

\[
\dot M=J_1-J_2-(\dot B+\dot R).
\]

Both the discretized and moment-approximation callers contain this transfer. Thus \(\dot S=-J_1+J_2\), provided the moment integrals and state derivatives refer to the same population. This is a falsifiable algebraic conservation inference, not a simulation or an assertion of global positivity for every source branch. Sources: [Common/myofilaments/ThickFilament_Dynamics.m:4](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/myofilaments/ThickFilament_Dynamics.m#L4), [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:62](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L62), [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:82](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L82), [Common/fiber/biophysical/fiber_dynamics_explicit_approximated.m:64](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_approximated.m#L64).

The code family names map to parameter files: two-state noncooperative → `biophysical_no_regular`; two-state cooperative → `biophysical_thin_regular`; three-state cooperative → `biophysical_full_regular`; four-state cooperative → `biophysical_full_alternative`. All explicit XB families use the same dynamics routine selected by discretized versus approximated method; rates and auxiliary states distinguish families. Source: [Common/simulate/look_up_model.m:8](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/look_up_model.m#L8).

For two-state parameters with \(J_1=J_2=0\) and \(R=0\), the code has \(\dot M=-\dot B\). Starting \(B=0,M=1\) gives \(M+B=1\). The fitting routine directly defines \(M=1-B\) for its default two-state family. Starting a moment approximation with \(B=.001,M=1\), however, gives conserved \(M+B=1.001\); the general initialization routine actually does this. This is a concrete path-dependent initialization difference, not a declaration that the original experiment or author software fails. Sources: [Common/simulate/get_steady_state.m:26](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/get_steady_state.m#L26), [Common/simulate/get_steady_state.m:39](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/get_steady_state.m#L39), [Common/simulate/get_steady_state.m:48](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/get_steady_state.m#L48), [Fitting/fit_model_parameters_v2.m:182](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Fitting/fit_model_parameters_v2.m#L182).

In the noncooperative **ODE** branch, thin-filament activation is not an instantaneous algebraic sigmoid:

\[
A(C)=\frac{C^{n_H}}{\kappa^{n_H}+C^{n_H}},\qquad \dot N=\frac{A-N}{0.005\,\mathrm{s}}.
\]

The fit routine instead uses \(N=A(C)\) algebraically for the default noncooperative model. At constant equilibrated calcium these agree; calcium transients can distinguish them. The 5 ms lag is source-code-specific. Cooperative branches use the explicit on/off flux routine, with \(N_{\rm off}=N_{\rm tot}-N\), recruitment proportional to \(Ck_{\rm on}N_{\rm off}(1+k_{\rm coop}N/N_{\rm tot})\), and loss proportional to \(k_{\rm off}(N-B)(1+k_{\rm coop}N_{\rm off}/N_{\rm tot})\). Sources: [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:68](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L68), [Fitting/fit_model_parameters_v2.m:183](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Fitting/fit_model_parameters_v2.m#L183), [Common/myofilaments/ThinFilament_Dynamics.m:4](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/myofilaments/ThinFilament_Dynamics.m#L4).

## Rate function, signs and calcium units

The parameter-completion routine gives a normalized Gaussian attachment density:

\[
f(x)=\frac{f_1}{\sqrt{2\pi w^2}}\exp[-x^2/(2w^2)],\qquad \int_{\mathbb R} f(x)dx=f_1.
\]

Combined with the discretized caller, detachment is

\[
g(x)=k_{11}e^{-k_{12}x}+k_{21}e^{+k_{22}x}.
\]

Consequently the article-style \(g_1e^{-E_1x}+g_2e^{-E_2x}\) maps as \(g_1=k_{11},E_1=k_{12},g_2=k_{21},E_2=-k_{22}\). The source variable named `beta` is an attachment-rate array; it is **not** the article's force-normalization coefficient. Sources: [Reproduce/Parameters/complete_parms.m:6](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/complete_parms.m#L6), [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:45](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L45).

Code inputs use seconds, length change relative to reference fiber length, velocity in reference lengths per second, and calcium in **µM**. The source test converts \(C_{\mu M}=10^{6-\mathrm{pCa}}\). Hence \(\kappa\) is in µM, \(n_H\) dimensionless, Gaussian width and strain-exponent coefficients refer to the powerstroke-normalized coordinate, and rate amplitudes have inverse-second units. These units follow the code input declaration and equations, rather than a guessed table alignment. Sources: [Test/README.md:36](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Test/README.md#L36), [Test/test_model.m:28](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Test/test_model.m#L28).

## Initialization and series conventions

The normal simulation path integrates for **10 s** at the first prescribed length/calcium and zero velocity, then uses the final state. It does not test an equilibrium residual before declaring the returned state steady. Discretized initialization has the entire attached density zero, \(N=0,R=0\), and \(M=1\) for two-state or \(M=0\) otherwise; CE position is obtained by minimizing squared force-balance error. Moment initialization instead starts \(B=.001,p=0,q=.1\). Its \(Q_2=(q+p^2)B\) makes \(q\) a variance despite an initialization comment calling it a standard deviation. Sources: [Common/simulate/get_steady_state.m:3](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/get_steady_state.m#L3), [Common/simulate/get_steady_state.m:25](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/get_steady_state.m#L25), [Common/simulate/find_steady_state.m:10](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/find_steady_state.m#L10).

Series force and extension are related by

\[
F_{\rm SE}=k_{\rm SE0}(e^{k_{\rm SE}\Delta L_{\rm SE}}-1),\qquad
\Delta L_{\rm SE}=\log(1+F_{\rm SE}/k_{\rm SE0})/k_{\rm SE}.
\]

The finite-series discretized CE velocity uses force balance and the series/passive stiffnesses:

\[
\dot L_{\rm CE}=\frac{\gamma v_{\rm input}k_{\rm SE}^{\rm tangent}-\dot F_{\rm reaction}}
{B+k_{\rm SE}^{\rm tangent}+k_{\rm PE}^{\rm tangent}},
\quad k_{\rm SE}^{\rm tangent}=k_{\rm SE}(F_{\rm SE}+k_{\rm SE0}).
\]

Therefore a commanded whole-fiber step does not generally equal an instantaneous CE strain shift. A direct-CE clamp bypasses this series equation and must be labeled accordingly. Sources: [Reproduce/Parameters/complete_parms.m:14](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/complete_parms.m#L14), [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:85](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L85).

The distinct fields `lce0` and `Lce0` must not be merged: lowercase is the transport-coordinate origin, uppercase the passive-element onset. Runtime transport uses \(x=x_i+L_{\rm CE}-lce0\), while force reporting uses \(x=x_i+L_{\rm CE}\). If lowercase \(lce0\ne0\), reported raw XB force exceeds the runtime raw moment by \(lce0 B\) before output scaling. **The one inspected MAT fixture has lowercase \(lce0=0\), so this conditional difference vanishes there.** Sources: [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:14](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L14), [Common/simulate/simulate_model.m:87](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/simulate_model.m#L87), [Common/fiber/get_PE.m:3](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/get_PE.m#L3).

Other implementation differences require an explicit choice for any independent replay: local negative density is set to zero in the RHS; runtime active force is softened to \(\log(1+e^{KF})/K\), whereas output uses raw moments; the approximate branch clips active force nonnegative and inverse series extension nonnegative. Initial force balance uses piecewise-linear PE, runtime uses \(k_{\rm pe}\log(1+e^{K\Delta L})/K\) below its linear cutoff, and the fitting routine hardcodes \(K=1\) while the inspected saved parameter has \(K=100\). These are observed code differences, with no execution-based attribution of their effects. Sources: [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:24](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L24), [Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m:42](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m#L42), [Common/fiber/get_force_and_stiffness.m:4](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/get_force_and_stiffness.m#L4), [Common/fiber/get_PE.m:5](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/fiber/get_PE.m#L5), [Fitting/fit_model_parameters_v2.m:149](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Fitting/fit_model_parameters_v2.m#L149).

For a macroscopic physical CE coordinate, code \(L=\gamma\,\Delta L_{\rm CE,phys}/L_{\rm CE,ref}\), so \(\Delta L_{\rm CE,phys}=\ell_\gamma\Delta L\), with \(\ell_\gamma=L_{\rm CE,ref}/\gamma=2N_s d_{\rm ps}\) when the reference fiber contains \(N_s\) sarcomeres and \(\gamma=s/(2d_{\rm ps})\). If physical PE is written \(c_{\rm PE}\log(1+e^{\Delta L_{\rm CE,phys}/\ell})\), matching the code function requires \(K=\ell_\gamma/\ell\) and \(c_{\rm PE}=\mathrm{Fscale}\,k_{\rm pe}/K\) in the dimensionless output-force convention. A further physical-force conversion needs the unresolved calibration. The single-link formula \(K=d_{\rm ps}/\ell\) applies only if the physical coordinate is a single-link extension; it does not convert this macroscopic CE coordinate. Merely copying a numerical article coefficient into code `kpe` does not establish equivalence. The code multiplies relative input length by gamma explicitly: [Common/simulate/simulate_model.m:49](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Common/simulate/simulate_model.m#L49).

## Force normalization and physical calibration limit

The processed fit target is dimensionless:

\[
F_{\rm target}(t)=\frac{F_{\rm trace}(t)}{\overline F_{\rm pre}}
\frac{F_0({\rm fiber,pCa})}{F_{\max}({\rm fiber})},
\qquad \Delta L_{\rm input}=\frac{L(t)-\overline L_{\rm pre}}{\overline L_{\rm pre}}.
\]

The pCa processor divides raw force by 1000 and recording gain, computes median pre-stretch force at each pCa, and sets \(F_{\max}\) to the maximum across measured pCas. A plotting label says kPa, but the inspected processing code does not expose raw sensor calibration or area conversion sufficient to independently establish physical units. Do not infer µN, newtons, or a Kenoma stress from the MAT values. Sources: [Data/Processing/normalize_data.m:151](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/normalize_data.m#L151), [Data/Processing/calc_force_pCa.m:50](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L50), [Data/Processing/calc_force_pCa.m:87](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L87), [Data/Processing/calc_force_pCa.m:108](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/calc_force_pCa.m#L108), [Data/Processing/normalize_data.m:75](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Data/Processing/normalize_data.m#L75).

Source raw active force is \(B+Q_1\); output total force is multiplied by `Fscale`. For the inspected fixture `Fscale=2`. If the article writes output force \((B+Q_1)/\beta\) under the same normalizer, this algebraically corresponds to \(\beta=1/Fscale=.5\). The equivalence is an inference; the code does not store a force-normalization field named beta. It does not imply that fully activated equilibrium has \(B=.5\) or total force exactly one.

## One immutable individual-fit measurement

Ordinary authorized read recipe: GitHub `fetch_file` for repository `timvanderzee/biophysical-muscle-model`, path [`Reproduce/Parameters/7Aug2018a/parms_biophysical_no_regular.mat`](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/7Aug2018a/parms_biophysical_no_regular.mat), ref `8c766dfb308051309193e7290ddd0bac3b726d11`, encoding `base64`; expected blob **`51750762436ff52f22abaa40614cf2c1a73f1c2d`**, 460,311 bytes. Decode in memory and inspect `scipy.io.loadmat(..., simplify_cells=True)` fields. A temporary base64 staging file was deleted after inspection; no MAT file or author functions were retained or executed.

The [compact factual receipt](source-code-parameter-facts.json) records the read recipe, values, unit limitations and outstanding gates. These measured scalar fields are factual source metadata, **not a selected Kenoma fit or paper median**:

| Field | Measured value | Interpretation/limit |
|---|---:|---|
| f | 59.60978106169219 | Gaussian area, inverse seconds |
| k11, k12 | 7.095011829474687, 2 | First rate amplitude and negative exponent magnitude |
| k21, k22 | 23.219667463502386, 0.7018824385221679 | Second amplitude and positive code exponent |
| w | 0.16666666666666666 | Powerstroke-normalized Gaussian SD |
| n, kappa | 2.8363440515652822, 1.0811918539382133 | Hill exponent and Ca50 in µM |
| gamma, Fscale | 130, 2 | Length conversion and dimensionless output scaling |
| lce0, Lce0 | 0, −9.999999953798886 | Transport origin and passive onset, distinct |
| K | 100 | Runtime softplus sharpness |
| kse, kse0 | 0.18270123175971706, 0.1810599266136319 | Series law in code internal units |
| kpe | 0.0023943631682408345 | PE slope parameter in code internal units |
| Noverlap | 1 | No descending overlap path in this fixture |
| J1,J2,kon,koff,koop,k,b,kF | all 0 | Two-state noncooperative parameter switches |
| JF | 145.0548 | Stored but J1=0 makes the inspected recruitment flux vanish |
| x0 | [0,0,0,0,0,1,0] | Stored older state layout; general initializer separately constructs its state |

The richer `newparms` struct additionally stores `ps=1,s=2.6e-6,h=1.2e-8,Fmax=120`. The lengths suggest 2.6 µm sarcomere and 12 nm historical stroke, but \(.5s/h=108.333\ldots\) conflicts with stored \(\gamma=130\). The reproduction fitting script explicitly resets stroke to **10 nm** and computes \(\gamma=.5(2.6\ \mu m)/(10\ nm)=130\). Thus an independent implementation should state whether it follows current gamma or historical h; these fields cannot silently define the same coordinate. The reduced test path uses gamma and omits historical h/ps/Fmax. Sources: [Reproduce/reproduce_model_fitting.m:344](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/reproduce_model_fitting.m#L344), [Reproduce/Parameters/create_reduced_parms.m:7](https://github.com/timvanderzee/biophysical-muscle-model/blob/8c766dfb308051309193e7290ddd0bac3b726d11/Reproduce/Parameters/create_reduced_parms.m#L7).

## Bounded recommendation and rejection checks

After the publication visual gate is satisfied, a new **independent pinned-source convention fixture** could test the measured nonhuman individual parameters, with explicitly chosen direct-CE or finite-series protocol. It should retain the original equation fixture as a separate diagnostic. Record the branch, variance convention, activation lag, population conservation, density/force clipping, coordinate origin, PE sharpness, and physical-to-internal length conversion.

Before claiming author-code parity, independently check: \(S+B+M+R=1\) including initialization; two-state \(M+B=1\); held-length kinetic and series-force residuals after the 10 s preparation; agreement of runtime versus reported moments; Gaussian quadrature area and detachment exponent signs; and gamma/h consistency. Reject a proposed replay if any convention is implicit or if it uses the frozen \(M=1\) fixture while calling it the source two-state algorithm. This audit supplies no original waveform replay, visual median verification, descending force-length closure, human calibration, or continuum/long-time stability conclusion.

## Blob manifest

| Pinned source path | Blob SHA |
|---|---|
| Common/fiber/biophysical/fiber_dynamics_explicit_discretized.m | 37c94486239ff58f4830b3fb94715b0472d0fb1c |
| Common/fiber/biophysical/fiber_dynamics_explicit_approximated.m | 57b034e7b250afc8d8d405d894dd0a90db0c6edf |
| Common/myofilaments/ThickFilament_Dynamics.m | 8a53a214e7bbb5a23b1ccca474d79234085d4429 |
| Common/myofilaments/ThinFilament_Dynamics.m | 3c4b57484464a1119cfbcddd97a7cf8283d3c664 |
| Common/simulate/get_steady_state.m | 76406e95533069d113490fcca9fea26f14df9bb5 |
| Common/simulate/find_steady_state.m | 3c2937d8e9a29ddff548d11842270535f75b7263 |
| Common/simulate/simulate_model.m | 3fb14f1475d49b6af9e5e0541b7b54cae1200aa3 |
| Common/fiber/get_PE.m | cb615867322c00c936638ca8f3934e26cd6955b0 |
| Common/fiber/get_force_and_stiffness.m | 4320a5510c6dfa27ab2a3822d4c1b4058f81ca64 |
| Fitting/fit_model_parameters_v2.m | fd56f3368c01f9f38640875382fecd74ca59dccc |
| Reproduce/Parameters/complete_parms.m | f5656cc5dc7da581d29f68c74cc509c93ff6a155 |
| Reproduce/reproduce_model_fitting.m | 76ffc631d12bc6259d34f527863ba712ce65dee5 |
| Data/Processing/normalize_data.m | 6e5179a726d1a4dfa929dec3d7a4d3e3d10ba436 |
| Data/Processing/calc_force_pCa.m | e2e4ed6427a094cb6e23c77439c0237d03c8cf1c |
| Test/README.md | 664bd1a4852242869d3d95ad35b594cd2fd62779 |
| Individual MAT measurement | 51750762436ff52f22abaa40614cf2c1a73f1c2d |
