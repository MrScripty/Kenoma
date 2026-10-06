# Independent audit of the held-capacity implicit reduction

Reviewed 2026-10-06 against the new [implicit derivation](source-two-state-implicit-derivation.md). **The equilibrium and backward-Euler scalar reductions are correct in exact arithmetic for fixed 0≤B≤N≤1, nonnegative attachment cell rates Fi and positive detachment rates gi.** This is an analytical review before an implementation receipt. No physiological/loading experiment, source replay, simulation, coefficient selection, old-packet edit or Git operation was performed.

Write a(B)=(1−B)(N−B), c=1−N and q=N−B. Then a=q(c+q). Equilibrium has pi*=(Fi/gi)q*(c+q*), with I=ΣFi/gi and Iq²+(1+Ic)q−N=0. The rationalized root in the derivation gives the unique admissible equilibrium; I=0 gives q=N and pi*=0. Compute B*=Σpi* or Iq*(c+q*) rather than relying on N−q*: the latter subtracts nearly equal numbers for small I. This equilibrium does not impose Q*=β or normalized force one.

For backward Euler let ai=(1+hgi)⁻¹, U=Σai pi_old, V=hΣai Fi and W=N−U. The full nonlinear equations are

\[
R_i=p_i-p_{i,\rm old}-h\{F_i(1-B)(N-B)-g_i p_i\}=0.
\]

Their reduction is Vq²+(1+Vc)q−W=0. At q=0 the polynomial is −W≤0; at q=N it is VN+U≥0, and its derivative is 1+Vc+2Vq>0 on q≥0. Thus the displayed positive root is unique in [0,N]. Reconstruction is nonnegative and Σpi_new=U+Vq(c+q)=N−q. It simultaneously preserves nonnegative free-head capacity M=1−B and available-site capacity N−B. These are exact-arithmetic conclusions; floating-point acceptance still needs full residual and population checks.

The full continuous Jacobian, including cross-bin terms, is

\[
J_{ij}=-g_i\delta_{ij}-F_i(1+N-2B).
\]

Consequently the BE residual Jacobian is (1+hgi)δij+hFi(1+N−2B). With all Fi>0 and r=1+N−2B≥0, similarity by diag(√Fi) gives −diag(gi)−r vvᵀ, vi=√Fi. All its eigenvalues are real and strictly negative. Zero-Fi bins have their own −gi eigenvalues and a triangular coupling to the remaining bins. This supports local stability for the held-input population reduction; it supplies no series/load/continuum stability claim.

## Floating-point pitfalls and useful checks

The rationalized root avoids subtracting two large quadratic-root terms, but does not alone prevent every cancellation or overflow:

- Near B_old=N and very small h, direct W=N−U loses the newly detached increment. The equivalent expression W=(N−B_old)+Σ[hgi/(1+hgi)]pi_old is a positive accumulation on a valid input state. Tests should include N=1 and a saturated old population, with independently computed high-precision W and q.
- Squaring 1+Vc, computing 4VW, or forming hgi/hFi can overflow for finite inputs. Use scaled evaluation or explicitly reject nonfinite intermediates rather than accepting a silent zero/NaN population. A hypot-based discriminant still needs safe construction of its arguments. Rate and timestep validation alone does not establish finite intermediate arithmetic.
- Very small I requires checking B* through reconstructed populations, not subtraction from N. Very large h should approach that independently calculated equilibrium; extremely small h should satisfy the initial RHS derivative to the achievable absolute precision.
- Full population/BE residual checks must use independently accumulated RHS and B, rather than only rechecking the reduced quadratic. Preserve a failed witness instead of repairing it with clipping, renormalization or a capacity reset.

A meaningful independent implementation check should solve the original vector BE residual with a general nonlinear solver on small heterogeneous-rate systems, compare its state to the closed update, and evaluate the full analytic Jacobian against numerical derivatives. Unequal gi are essential: a single common detachment rate collapses much of the coupling and misses errors in U. Include zero attachment, zero N, N=1, old saturation, sparse old mass, stiff rate ratios, bin permutations, and the h→0/h→∞ limits. A numerical reference root is accepted only when its own full residual and bounds pass.

Rejection checks should exercise negative individual bin mass even when the total looks valid; B_old>N; N outside [0,1]; negative Fi; nonpositive gi under this positive-detachment contract; nonpositive h; nonfinite inputs/intermediates; and incompatible array shapes. All-zero Fi is a valid limiting case, not a rejection. A failed reference solver is a reference failure, not permission to loosen gates.

## Capacity transitions

The pre-step invariant must be checked using **B_old≤N**, not merely U≤N. A reduced capacity N_new below B_old is invalid at input even if detachment over a sufficiently long step makes U≤N_new and the quadratic admits a nonnegative root. Accepting that step would hide an occupied-site capacity violation. A future varying-capacity law needs its own occupied-site dynamics and transition convention; silently clipping, rescaling attached mass, resetting M, or interpreting N−B<0 as a valid attachment state changes the model.

The parent reports new original table pixel verification in a separate lane. This audit does not repeat retrieval or claim its own visual inspection; publication/code parity and physical calibration remain separate obligations.
