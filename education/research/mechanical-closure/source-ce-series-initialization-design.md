# Source-informed CE/PE/SE algebraic initialization design

**This is a protocol for dimensionless algebra qualification, with execution pending a parent-owned protocol commit.** It prepares a coherent initial force balance for the already declared conserved \(M=1-B\), held-\(N\) CE fixture. It does not run a coupled trajectory, release, fit, source-code replay, human calibration or continuum experiment. Production, books, proofs and earlier fixtures remain frozen.

Implementation: [source_ce_series_initialization.py](../../tools/source_ce_series_initialization.py). Its equations are independent mathematical implementation; no author source code is imported. The runner requires explicit `--qualify --protocol-commit <40-character commit>` arguments. A supplied commit string records an external gate; the script does not itself verify repository approval or content identity. The parent must first commit this design and runner and then authorize execution against that exact revision.

## Inspected source identity and unresolved PE units

I visually inspected the preserved [original series-context pixels](plos-original-table-visual-evidence/original-series-context.png) and [original Table 3 pixels](plos-original-table-visual-evidence/table-3-original.png), under [visual audit commit 64ef2727](original-plos-table-visual-audit.md). Source: [van der Zee et al. (2026)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014748). Printed Eqs14–22 give

\[
F_f=F_{\rm SE}=F_{\rm CE}+F_{\rm PE},\quad
L_f=L_{\rm CE}+L_{\rm SE},\quad \gamma=2N_s d_{\rm ps},
\]
\[
F_{\rm PE}=k_{\rm PE}\log[1+\exp((L_{\rm CE}-L_{\rm PE,0})/\gamma)],
\]
\[
F_{\rm SE}=\sigma[\exp(\rho(L_{\rm SE}-L_{\rm SE,0})/\gamma)-1],
\qquad F_{\rm CE}=\widetilde F_{\rm CB}/\beta.
\]

The original noncooperative two-state column gives \(\sigma=.19\,F_0,\rho=.24\,(x_{\rm ps}^{-1})\), and \(k_{\rm PE}=.002\,F_0(x_{\rm ps}^{-1})\). Eq19's logarithm is dimensionless and its coefficient must have force units; the table's displayed PE coefficient has a stiffness unit. This memo does **not** silently resolve that mismatch by copying .002 as a force prefactor. It declares a separate normalized force prefactor \(\kappa\), leaves its source mapping unresolved, and labels every numeric \(\kappa\) qualification value an authored algebra probe. The former individual MAT's K100, Lce0≈−10, width1/6 and PE/SE coefficients are not used. Article softplus sharpness is one in the coordinate below.

The SE median numbers are used only with the declared interpretation that the table's normalized stroke coordinate has numerical unit one: \(\widehat\sigma=.19\), exponent coefficient \(r=.24\). If \(x_{\rm ps}\) denotes a dimensional length rather than that normalization convention, \(r\) must first absorb its unit conversion; a literal dimensionful \(\rho\) times a dimensionless extension is inadmissible. This is a declared source-informed normalized law, not a complete SI interpretation of the table.

## Coordinates, force convention and free reference metrics

Choose the CE reference position as \(u_{\rm CE,0}=0\), and define

\[
u_{\rm CE}=(L_{\rm CE}-L_{\rm CE,ref})/\gamma,\quad
u_{\rm PE,0}=(L_{\rm PE,0}-L_{\rm CE,ref})/\gamma,\quad
e_{\rm SE}=(L_{\rm SE}-L_{\rm SE,0})/\gamma.
\]

All three are dimensionless. Total reference-gauge extension is \(u_f=u_{\rm CE}+e_{\rm SE}\); absolute reference lengths remain unknown. CE and SE rest origins cannot be inferred from a normalized kinetic state. Setting the **authored probe** \(u_{\rm PE,0}=0\) places the passive transition at this CE reference; it is not a measured physical slack length, and an unknown PE offset cannot generally be eliminated merely by moving the coordinate origin.

Let \(F_0>0\) be an unspecified physical normalization force. Define \(\widehat F=F/F_0\) and, at fixed source \(\beta=.5\),

\[
\widehat F_{\rm CE}=Q/\beta,\qquad
Q=\int(1+x)n(x)\,dx,\quad B=\int n(x)\,dx,\quad M=1-B.
\]

The held-\(N\) conserved source fixture has, on its declared \([-3,3]\) domain at \(N=1\), baseline normalized raw CE force approximately **.9883483646**, not one. This baseline is inherited as a checkable consequence of the [conserved CE convention](conserved-ce-trajectory-protocol.md), never imposed by scaling.

## Coherent initializer

The independent normalized elastic functions are

\[
P(u)=\kappa\log(1+\exp(u-u_{\rm PE,0})),\quad
S(e)=\widehat\sigma\,\operatorname{expm1}(r e),
\]
\[
\kappa\ge0,\qquad \widehat\sigma>0,\qquad r>0.
\]

Given an admissible held stationary CE distribution and chosen \(u_{\rm CE,0}=0\), compute

\[
T_0=Q/\beta+P(0),\qquad
e_{\rm SE,0}=\frac{\log(1+T_0/\widehat\sigma)}{r},\qquad
u_{f,0}=e_{\rm SE,0}.
\]

This exactly enforces \(S(e_{\rm SE,0})=Q/\beta+P(0)\). No ten-second settling, passive-force subtraction, hidden state reset, baseline-to-one rescaling or length fit is part of initialization. For \(T_0\ge0\), \(e_{\rm SE,0}\ge0\); negative total force is rejected rather than clipping the inverse. Functions accept arbitrary declared \(\kappa,u_{\rm PE,0}\), and a nonzero initial CE coordinate if a later protocol explicitly supplies one.

The helper independently constructs the stationary conserved distribution from source rates

\[
a=\int_{-3}^{3}\frac{f(x)}{g(x)}dx,\quad
B=a(1-B)(N-B),\quad
n(x)=(1-B)(N-B)f(x)/g(x).
\]

It selects the positive smaller quadratic root by a rationalized expression. Rates are the publication two-state medians \(f_1=52,g_1=4,g_2=21.1,E_1=2,E_2=-.6,w=.3\), using normalized Gaussian attachment and \(g=g_1e^{-E_1x}+g_2e^{-E_2x}\). This is a stationary quadrature, not time integration or a new kinetic trajectory. \(N\) remains held; no cooperative/5 ms activation dynamics are introduced.

Qualification uses the same source-fixture calcium conversion and sigmoid at **pCa 4.5 and 6.1**, plus the separate **N=1 normalization audit**:

\[
C_{\mu M}=10^{6-\mathrm{pCa}},\qquad
N=\frac{1}{1+(0.83/C_{\mu M})^{3.1}}.
\]

The N=1 condition does not replace the pCa 4.5 capacity with exactly one. Each of the three conditions obtains its own stationary B,Q,M and raw CE force. Held capacity is never selected to change a force or stability result.

## Tangents and symbolic physical reflection

The following fast CE/parallel/whole tangent probe holds the populations and rigidly translates the complete distribution support, with **no outflow**. Its moments therefore obey \(Q(\delta u)=Q+B\delta u\), even though the starting stationary distribution was constructed on \([-3,3]\). Under this full-support rigid moment probe,

\[
K_{\rm CE}^{u}=B/\beta,\qquad
K_{\rm PE}^{u}=\kappa\,\operatorname{sigmoid}(u-u_{\rm PE,0}),\qquad
K_{\parallel}^{u}=K_{\rm CE}^{u}+K_{\rm PE}^{u},
\]
\[
K_{\rm SE}^{e}=\widehat\sigma r\,e^{re}
=r(S(e)+\widehat\sigma).
\]

All are normalized force per normalized extension. For this scalar instantaneous series split, the total-fiber tangent is \(K_f^u=K_{\parallel}^uK_{\rm SE}^e/(K_{\parallel}^u+K_{\rm SE}^e)\), under the same full-support held-population, no-outflow convention. It can be nonnegative without establishing a relaxed force-length slope, pole stability, descending-overlap behavior or continuum stability.

These expressions are not derivatives of transport followed by clipping at a fixed \([-3,3]\) boundary: a truncated-domain outflow derivative includes endpoint terms and can change both attached mass and force moment. Finite-domain jumps and their escaped mass/force moments are governed separately by the [continuous strain reference's escape ledgers](continuous-strain-reference-design.md) and [continuous strain CE protocol](continuous-strain-ce-protocol.md). This initializer neither runs those jumps nor suppresses their escape terms in that reference.

The reflected physical identities stay symbolic:

\[
T_{\rm PE}=F_0\kappa\log[1+\exp((L_{\rm CE}-L_{\rm PE,0})/\gamma)],
\quad
T_{\rm SE}=F_0\widehat\sigma[\exp(r(L_{\rm SE}-L_{\rm SE,0})/\gamma)-1],
\]
\[
K_{\rm PE}^{\rm phys}=(F_0/\gamma)K_{\rm PE}^{u},\quad
K_{\rm SE}^{\rm phys}=(F_0/\gamma)K_{\rm SE}^{e},\quad
K_{\rm CE}^{\rm phys}=(F_0/\gamma)B/\beta.
\]

Neither \(F_0,\gamma=2N_s d_{\rm ps}\), specimen area nor physical slack lengths are assigned SI values. In particular, published mean \(N_s\) is not an individual specimen's count, and the normalized code length multiplier130 is not dimensional \(\gamma\). [Calibration reconciliation](calibration-source-reconciliation.md) and the earlier [dimensional bridge](dimensional-contractile-mapping.md) retain those limits. This memo does not turn a source coefficient into a human tendon or tissue constant.

## Predeclared algebra qualification

After the parent protocol commit, run the new qualifier at **60 decimal digits**. Its **27 initializer probes** are three stationary conditions (pCa 4.5, pCa 6.1 and N=1) × three authored \(\kappa\) values \(\{0,.002,.02\}\) × three authored \(u_{\rm PE,0}\) offsets \(\{-10,0,+10\}\). The .002 probe numerically coincides with a table entry but is expressly **not** an established mapping of that stiffness entry to Eq19's prefactor. These offsets and amplitudes are mathematical checks, not source uncertainty intervals, specimen fits or physical sensitivity estimates.

The fixed gates are:

- Strictly enforce \(0\le B\le N\le1\), \(0\le M=1-B\le1\), nonnegative stationary density, and nonnegative force-moment variance. No tolerance-based clipping/reset.
- Stationary attached integral and population-balance residual must be at most \(10^{-12}\) absolute. Recompute free fractions from the independently integrated attached mass and check the pointwise reaction residual at 129 uniformly spaced positions on [-3,3], with the same absolute gate. Nonnegative density follows analytically from positive rates and admitted population factors; the sampled reaction check is not presented as proof of a continuum supremum.
- Initialized force-balance error and SE inverse round-trip error must each be at most \(10^{-12}\) absolute.
- Independent centered finite differences with step \(10^{-15}\) must agree with PE, SE and full-support held-population rigid-translated CE+PE tangents, with no outflow, to relative \(10^{-8}\). The CE moment probe is exactly \(Q\pm B h\); it does not approximate fixed-domain clipped transport. When the expected derivative is zero, use the same numerical threshold on absolute error; do not divide by zero.
- SE inverse boundary probes \(T\in\{0,10^{-20},1,100\}\) must round-trip within the fixed absolute force gate.
- Negative/over-capacity attached mass and out-of-range held \(N\) must be rejected explicitly. Add negative SE force/extension/initial total force and nonpositive domain-radius rejection; require positive sigma/r/beta, reject negative kappa while retaining its admissible zero limit, and reject NaN or ±infinity in every parameter and each scalar-input class. The predeclared invalid-input matrix contains **56 rejection probes**.

Record the exact protocol commit, runner identity, precision, raw stationary \(B,Q,M,N\), baseline raw CE force, each authored probe, initial force/extension split, all residuals, and tangent errors. The **four fixed SE boundary probes** each retain their numerical input force, inverse extension, resulting force and absolute round-trip error, rather than recording only whether they passed. The declared matrix remains exactly **27 initializer probes, 56 invalid-input rejection probes and four SE boundary probes**; failure preservation does not change any equation or gate.

When `--output` is supplied, the runner must create that path exclusively **before any qualification**, including protocol-string validation. An existing output or a failure to create the new output aborts qualification; it cannot overwrite an earlier receipt. The new receipt starts with status `RUNNING` before stationary quadrature or any case. It is flushed and synchronized after progress checkpoints, retaining each completed stationary condition, initializer case, expected rejection and boundary probe with separate completed counts. Current context records the phase, condition, authored kappa/offset and known B/Q/N/M state. A separate current candidate retains intermediate values as they become available, including a gate-failing candidate; successful completed records are not cleared when the next candidate starts.

The CLI uses `try/except/finally` to preserve a partial receipt with status `FAILED`, exception type/message and traceback if any qualification step fails or is interrupted. The current context and candidate remain in that receipt. Its final export targets only the newly reserved file; without `--output`, the partial or final receipt is emitted on standard output. Success alone changes status to `PASSED`; a failed qualification exits with a nonzero status. This preservation covers handled process exceptions and ordinary interruptions, not abrupt process termination or failure of the storage medium itself. The already flushed checkpoints are the evidence available in those cases.

No trajectory or load release follows from passing these algebra gates; it requires another precommitted reviewed protocol. Results are **not executed or claimed passed in this design document**.
