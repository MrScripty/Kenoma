# Let material stiffness and boundaries choose the lateral shape {#compression-bulk-shear-confinement}

**Question:** when a block is shortened between plates, must its volume stay exactly fixed? The preceding [isochoric lesson](#measure-deformation-before-choosing-a-muscle-law) imposed that answer. Here a material law and lateral boundary conditions choose the shape. Compare both conditions at one prescribed height, then change one stiffness at a time.

This is an authored, homogeneous elastic specimen, not measured muscle. The reference width, height and depth are $W_0=0.08$ m, $H_0=0.06$ m and $D_0=0.05$ m; $V_0=0.00024$ m³. Ideal frictionless plates prescribe height stretch $0.5\le h\le1$. The single unknown lateral stretch $b>0$ acts equally in X and Z:

$$F=\operatorname{diag}(b,h,b),\qquad J=b^2h,\qquad I_1=2b^2+h^2.$$

This diagonal homogeneous ansatz rules out bulging, shear localization, buckling and spatially varying fields. Uniform stress makes the lateral traction condition meaningful within this ansatz; this is not a mesh solve or a proof of the unrestricted specimen's preferred deformation.

## An elastic energy, finite stiffness and units

Reuse the existing [homogeneous tissue energy](web/tissue.mjs), leaving the earlier labs' equations and calibration unchanged:

$$U(b,h)=V_0\left[\frac{\mu}{2}(J^{-2/3}I_1-3)+\frac{K}{2}(J-1)^2\right].$$

Here $\mu$ and $K$ are shear and bulk **parameters of this declared energy**, each in Pa = J/m³. They characterize the reference response; finite-deformation tangent stiffness need not equal these constants. Controls permit $500\le\mu\le5000$ Pa and $0\le K\le250000$ Pa. These are bounded teaching choices, not fitted biological ranges. The $K=0$ endpoint deliberately removes resistance to pure volume change.

A finite bulk term penalizes $J\ne1$ with finite energy; it does not impose $J=1$. The shear term penalizes distortional shape change and vanishes under positive isotropic scaling. Neither term supplies plasticity, damage, viscosity, fluid transport, fibre architecture or activation.

The constitutive framework has an original-author reference: [A. F. Bower, *Applied Mechanics of Solids*, §3.5](https://solidmechanics.org/Text/Chapter3_5/Chapter3_5.php) describes hyperelastic stress as an energy derivative and distinguishes nominal stress from force per deformed area. The formula and boundary reduction here are the book's illustrative model. No experimental response curve is reproduced or calibrated from that source.

| Quantity | Units | Meaning |
|:--|:--|:--|
| $h,b,J$ | dimensionless | Height stretch, lateral stretch, volume ratio |
| $U$ | J | Stored elastic energy for the whole reference block |
| $P_x,P_y,R$ | Pa | Nominal stresses and inward wall reaction per reference side area |
| $N$ | N | Compressive force on one height plate |
| $p$ | Pa | Plate force divided by its current area |
| $g_x,g_z$ | m | Clearance between specimen and each lateral wall |

## Derive the reduced equilibrium

The nominal stress components computed from this energy are

$$P_x=\mu J^{-2/3}\left(b-\frac{I_1}{3b}\right)+K(J-1)\frac{J}{b},\qquad
P_y=\mu J^{-2/3}\left(h-\frac{I_1}{3h}\right)+K(J-1)\frac{J}{h}.$$

Both lateral directions vary with $b$, hence $\partial U/\partial b=2V_0P_x$; $\partial U/\partial h=V_0P_y$. Finite-difference tests check these derivatives and the reduced plate force. **Free sides** require zero lateral traction, $P_x=0$. The numerical root bracket is $h\le b\le1/\sqrt h$: the left endpoint has zero shear contribution and nonpositive bulk contribution; the right has $J=1$ and nonnegative shear contribution. Analytic endpoints handle $K=0$ and $h=1$. This bracket supports the implemented root search; no Lean proof of existence, uniqueness, convergence or global optimality is claimed.

**Unilateral confinement** places smooth rigid walls at the reference X/Z faces. Walls prevent outward expansion but allow inward pull-away: $b\le1$. They apply inward compressive reaction $R\ge0$ and cannot pull the block outward. The reduced wall contract is

$$P_x+R=0,\qquad b\le1,\qquad R\ge0,\qquad R(1-b)=0.$$

At $b=1$, if $P_x<0$, use $b=1$ and $R=-P_x$. Otherwise solve the free-traction root on the restricted bracket $[h,1]$ and use $R=0$. The separate bracket keeps even a finite approximation inside the walls. At weak bulk stiffness, the specimen can shrink away from the walls; forcing $b=1$ in that case would require an unmodeled tensile attachment.

Plate force and pressure follow from the same nominal stress, not from displayed arrows:

$$N=-W_0D_0P_y,\qquad p=\frac{N}{W_0D_0b^2}.$$

The sign convention makes compression positive. Each X wall carries $N_x=RH_0D_0$; each Z wall carries $N_z=RW_0H_0$. Their current-area pressure is $R/(bh)$. Per-wall clearances are $g_x=W_0(1-b)/2$ and $g_z=D_0(1-b)/2$. The reported complementarity work is $2(N_xg_x+N_zg_z)$ in joules, accounting for both walls in each direction.

{{property:material}}

## Predict, change one input, and inspect the residual

At default $h=0.8$, $\mu=1500$ Pa and $K=50000$ Pa, the plate spacing is 0.048 m in both panels. These values come from a fresh reduced solve:

| Boundary condition | Lateral stretch $b$ | Volume ratio $J$ | Plate force (N) | Stored energy (J) |
|:--|--:|--:|--:|--:|
| Free lateral surfaces | 1.11462688 | 0.99391447 | 4.53637103 | 0.02497727 |
| Unilateral rigid walls | 1 | 0.8 | 42.08871498 | 0.25142075 |

**Try and predict.** Raise only $K$ to 250000 Pa. The free block approaches $J=1$ without imposing it: $J\approx0.99878057$, while its plate force is about 4.56728 N. Active rigid walls retain $b=1$ and $J=h=0.8$, so the plate force rises to about 202.08871 N. Confinement changes the work required to reach the same height; increasing finite bulk stiffness cannot restore volume while all three stretches are fixed.

Restore $K=50000$ Pa and raise only $\mu$ to 5000 Pa. Read the force, lateral expansion, and separate bulk/shear energy contributions. Height remains shared. Every comparison changes only the named input; no time or activation state is hidden in this static lesson.

**Counterexample.** Set $K=0$. The solved block has $b=h$, $J=h^3$ and zero stored energy/plate force up to roundoff: at $h=0.8$, $J=0.512$. Isotropic collapse costs no distortional energy in this deliberately degenerate law. It is not a plausible soft-muscle response or plastic failure. At $K=500$ Pa, both solutions shrink laterally to $b\approx0.90043115$, with zero wall reaction and positive clearance. Confinement does not manufacture tensile attachment.

**Feasibility check.** The “Test isochoric wall candidate” button tries $b=1/\sqrt h$ in the confined geometry. For $h<1$ it has positive $J=1$ but penetrates the lateral walls and is rejected without changing the solved state. Positive volume is necessary but does not establish boundary feasibility.

**Numerical check.** Select eight bisections. Geometry remains positive and wall-feasible, but the signed free residual generally fails the displayed criterion $|P_x+R|\le10^{-5}$ Pa. Restore 32 or 64 and compare the bracket width and residual. The criterion belongs to this new lesson; it changes none of the existing labs' acceptance limits. “Residual criterion met” refers only to this reduced lateral equation. Invalid, blank, nonfinite or out-of-domain inputs retain the prior displayed state.

Finally restore $h=1$: $b=1$, $J=1$, energy and force return to zero. This model has no history or irreversible state, so it cannot demonstrate plastic deformation or dissipative load/hold/release. Reset deliberately restores all authored defaults.

## Real properties: checked algebra and unfinished formal obligations

The specimen uses **real** stretches, stresses and energies. Five real-domain algebra claims below are compiled against the pinned mathlib dependencies before this book is built. Constitutive derivatives and equilibrium existence, uniqueness and optimality remain **unfinished**. The separate integer contracts do not substitute for these real claims or their remaining obligations.

| Real claim and assumptions | Derivation in this lesson | Real formal status |
|:--|:--|:--|
| $b=1$, $0<h<1$ imply $0<J=h<1$ | Substitute into $J=b^2h$ | Checked real substitution |
| $V_0>0$, $K\geq0$ imply $V_0K(J-1)^2/2\geq0$; for $K>0$ it vanishes exactly at $J=1$ | A real square is nonnegative; a product with positive factors vanishes only when the square does | Checked real bulk algebra |
| $g>0$ and $Rg=0$ imply $R=0$ | Divide the assumed complementarity equation by nonzero real $g$ | Checked real implication; complementarity is assumed, not certified |
| $dU/db=2V_0P_x$, $dU/dh=V_0P_y$ for positive stretches | Differentiate the stated energy with $dJ/db=2bh$ and $dJ/dh=b^2$ | Unfinished; real powers and derivatives need formal support |
| Lateral virtual work factors as $2V_0(P_x+R)\delta b$ | Add the two equal lateral stress and wall contributions | Checked real factorization; does not establish equilibrium |

{{proof:material-real-confined-volume}}

{{proof:material-real-bulk-sign}}

{{proof:material-real-bulk-zero}}

{{proof:material-real-separated-wall}}

{{proof:material-real-lateral-work}}

The earlier real determinant and square-root identities support the kinematic volume formula. They do not prove this constitutive law, wall solution, equilibrium existence/uniqueness or global optimality. A release build must compile any future real-domain claim with its supported pinned dependencies before presenting it as checked.

## Discrete arithmetic contracts and separate numerical evidence

The five declarations below are freshly compiled with pinned Lean 4.19.0 and bundled Std. They concern **exact scaled integers**, with positive external SI scaling factors. These are separate implementation arithmetic checks; real stretches, stresses and energies are not their quantified domain. The unfinished derivative and equilibrium obligations above remain separate.

{{proof:material-confined-volume}}

{{proof:material-bulk-sign}}

{{proof:material-bulk-zero}}

{{proof:material-separated-wall}}

{{proof:material-lateral-work}}

Numerical tests independently derive a stationarity equation in $J$, check energy derivatives and SI conversions, sweep the bounded controls, compare feasible energy samples, and exercise finite caps, wall onset, zero bulk and invalid candidates. Browser tests execute the generated controls, verify exported states and SVG dimensions at a common physical scale, and check rollback, reset, mobile/print and no-JavaScript alternatives. These tests establish behavior for this declared implementation, not global optimality, mesh accuracy, material calibration or biology.

Continue with [anatomical evidence](#anatomy-is-evidence) before attaching these parameters to a named muscle. [Laboratory 5](#tendon-tissue-coupling) later reuses the free-side law in a coupled hinge example. The unfinished anatomical capstone, measured fibre-to-muscle aggregation, force–length/velocity lessons retain their separate limits in the [coverage chapter](#coverage-and-evidence).
