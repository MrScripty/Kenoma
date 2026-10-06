> Independent material-response review. This lesson and its five Std contracts are executed freshly; this is not a rebuilt or qualified full-book release.

# Let material stiffness and boundaries choose the lateral shape {#compression-bulk-shear-confinement}

**Question:** when a block is shortened between plates, must its volume stay exactly fixed? The preceding [isochoric lesson](https://mrscripty.github.io/Kenoma/#measure-deformation-before-choosing-a-muscle-law) imposed that answer. Here a material law and lateral boundary conditions choose the shape. Compare both conditions at one prescribed height, then change one stiffness at a time.

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


### Property lab 4 · Compression, bulk stiffness and confinement

![Solved homogeneous 80 × 60 × 50 mm reference block at height stretch 0.8, shear parameter 1,500 Pa and bulk parameter 50,000 Pa. Free: J = 0.993914, plate force 4.53637 N. Rigid unilateral walls: J = 0.8, plate force 42.0887 N. Dashed outlines are reference; gold lines are frictionless plates. Front view at one fixed physical scale; depth also scales by lateral stretch b.](assets/property-material.svg)

Solved homogeneous 80 × 60 × 50 mm reference block at height stretch 0.8, shear parameter 1,500 Pa and bulk parameter 50,000 Pa. Free: J = 0.993914, plate force 4.53637 N. Rigid unilateral walls: J = 0.8, plate force 42.0887 N. Dashed outlines are reference; gold lines are frictionless plates. Front view at one fixed physical scale; depth also scales by lateral stretch b.

[Open the interactive lesson](index.html#lab-property-material).


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

## Exact contracts and separate numerical evidence

The five declarations below are freshly compiled with pinned Lean 4.19.0 and bundled Std. They concern **exact scaled integers**, with positive external SI scaling factors. They do not formalize the real fractional powers in the energy or certify the floating-point solver.


**Freshly checked claim material-confined-volume:** With both lateral stretch numerators fixed at their reference scale, a smaller height numerator gives a smaller volume numerator.

**Assumptions:** Exact integers s and h; s > 0 and h < s. Physical interpretation additionally takes h > 0 and stretches b=s/s=1, height=h/s. Volume numerator is b_numer² × h_numer over s³.

```lean
theorem confined_volume (s h : Int) (hs : 0 < s) (hh : h < s) :
    volumeNumerator s h < volumeNumerator s s
```

**Limits:** No real determinant, constitutive equilibrium, finite-element volume or floating-point result is proved.

Lean 4.19.0; bundled Std; exact scaled integers; transitive axioms: propext; source SHA-256: 8ce7f4b5bf4b68f9eeb0d85b06925f417995f945b64498a4533347ead1864092. [Full source](proofs/MaterialResponse.lean); [receipt](material-proof-status.json).



**Freshly checked claim material-bulk-sign:** The exact scaled bulk-penalty numerator k × delta² is nonnegative for k ≥ 0.

**Assumptions:** Integer k and delta; delta represents a scaled volume-ratio departure, and unit/denominator scale factors are positive.

```lean
theorem finite_bulk_penalty_nonnegative (k delta : Int) (hk : 0 ≤ k) :
    0 ≤ bulkPenaltyNumerator k delta
```

**Limits:** The full real energy, fractional-power shear term and its derivatives are not formalized. A finite penalty is not a hard volume constraint.

Lean 4.19.0; bundled Std; exact scaled integers; transitive axioms: propext; source SHA-256: 8ce7f4b5bf4b68f9eeb0d85b06925f417995f945b64498a4533347ead1864092. [Full source](proofs/MaterialResponse.lean); [receipt](material-proof-status.json).



**Freshly checked claim material-bulk-zero:** For a strictly positive bulk coefficient, the exact bulk-penalty numerator is zero exactly when its volume-departure numerator is zero.

**Assumptions:** Exact integer k > 0 and integer delta; positive external scaling factors.

```lean
theorem positive_bulk_zero_penalty (k delta : Int) (hk : 0 < k) :
    bulkPenaltyNumerator k delta = 0 ↔ delta = 0
```

**Limits:** Does not assert that a loaded equilibrium has zero penalty, or prove incompressibility, a real solver or biological validity.

Lean 4.19.0; bundled Std; exact scaled integers; transitive axioms: propext, Classical.choice, Quot.sound; source SHA-256: 8ce7f4b5bf4b68f9eeb0d85b06925f417995f945b64498a4533347ead1864092. [Full source](proofs/MaterialResponse.lean); [receipt](material-proof-status.json).



**Freshly checked claim material-separated-wall:** An assumed exact complementarity product with strictly positive wall gap forces zero wall reaction.

**Assumptions:** Integer reaction and gap; gap > 0 and reaction × gap = 0. Physical reaction nonnegativity and positive SI scales are separate inputs.

```lean
theorem separated_wall_zero_reaction (reaction gap : Int)
    (hg : 0 < gap) (hc : reaction * gap = 0) : reaction = 0
```

**Limits:** Complementarity is assumed, not derived or certified for the JavaScript root. No continuous collision or spatial contact guarantee.

Lean 4.19.0; bundled Std; exact scaled integers; transitive axioms: propext, Quot.sound; source SHA-256: 8ce7f4b5bf4b68f9eeb0d85b06925f417995f945b64498a4533347ead1864092. [Full source](proofs/MaterialResponse.lean); [receipt](material-proof-status.json).



**Freshly checked claim material-lateral-work:** The two lateral stress and wall-reaction contributions factor as 2 × V₀ × (Pₓ + R) in exact scaled arithmetic.

**Assumptions:** Integer volume, stress and reaction numerators with compatible positive external SI scales. The association with an energy derivative is assumed separately.

```lean
theorem lateral_virtual_work (volume stress reaction : Int) :
    2 * volume * stress + 2 * volume * reaction =
      2 * volume * (stress + reaction)
```

**Limits:** Does not prove the real energy derivative, stationarity, root existence, uniqueness, global optimality or force validity.

Lean 4.19.0; bundled Std; exact scaled integers; transitive axioms: propext; source SHA-256: 8ce7f4b5bf4b68f9eeb0d85b06925f417995f945b64498a4533347ead1864092. [Full source](proofs/MaterialResponse.lean); [receipt](material-proof-status.json).


Numerical tests independently derive a stationarity equation in $J$, check energy derivatives and SI conversions, sweep the bounded controls, compare feasible energy samples, and exercise finite caps, wall onset, zero bulk and invalid candidates. Browser tests execute the generated controls, verify exported states and SVG dimensions at a common physical scale, and check rollback, reset, mobile/print and no-JavaScript alternatives. These tests establish behavior for this declared implementation, not global optimality, mesh accuracy, material calibration or biology.

Continue with [anatomical evidence](https://mrscripty.github.io/Kenoma/#anatomy-is-evidence) before attaching these parameters to a named muscle. [Laboratory 5](https://mrscripty.github.io/Kenoma/#tendon-tissue-coupling) later reuses the free-side law in a coupled hinge example. The unfinished anatomical capstone, measured fibre-to-muscle aggregation, force–length/velocity and dissipative property lessons retain their separate limits in the [coverage chapter](https://mrscripty.github.io/Kenoma/#coverage-and-evidence).


# Complete checked material source {#material-source-appendix}

```lean
import Std

/-! Exact scaled integer contracts for the new homogeneous compression lesson.
Positive SI scales are interpreted externally. This does not formalize real
fractional powers, constitutive derivatives, numerical roots or global minima. -/
namespace Kenoma.Material
def volumeNumerator (b h : Int) : Int := b * b * h
def bulkPenaltyNumerator (k delta : Int) : Int := k * (delta * delta)

-- b and h are stretch numerators over a common positive scale s.
theorem confined_volume (s h : Int) (hs : 0 < s) (hh : h < s) :
    volumeNumerator s h < volumeNumerator s s := by
  exact Int.mul_lt_mul_of_pos_left hh (Int.mul_pos hs hs)

theorem finite_bulk_penalty_nonnegative (k delta : Int) (hk : 0 ≤ k) :
    0 ≤ bulkPenaltyNumerator k delta := by
  have square : 0 ≤ delta * delta := by
    rw [← Int.natAbs_mul_self' delta]
    exact Int.ofNat_zero_le _
  exact Int.mul_nonneg hk square

theorem positive_bulk_zero_penalty (k delta : Int) (hk : 0 < k) :
    bulkPenaltyNumerator k delta = 0 ↔ delta = 0 := by
  simp only [bulkPenaltyNumerator, Int.mul_eq_zero]
  omega

-- Complementarity is an assumed contact contract, not a solver theorem.
theorem separated_wall_zero_reaction (reaction gap : Int)
    (hg : 0 < gap) (hc : reaction * gap = 0) : reaction = 0 := by
  have := Int.mul_eq_zero.mp hc
  omega

-- dU/db + generalized wall reaction = 2 V0 (P_x + R).
theorem lateral_virtual_work (volume stress reaction : Int) :
    2 * volume * stress + 2 * volume * reaction =
      2 * volume * (stress + reaction) := by
  simp only [Int.mul_add]
end Kenoma.Material

#print axioms Kenoma.Material.confined_volume
#print axioms Kenoma.Material.finite_bulk_penalty_nonnegative
#print axioms Kenoma.Material.positive_bulk_zero_penalty
#print axioms Kenoma.Material.separated_wall_zero_reaction
#print axioms Kenoma.Material.lateral_virtual_work

```

## Fresh proof receipt {#material-proof-receipt}

```json
{
  "schema": 1,
  "lean_version": "Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release)",
  "mathlib": "not used; bundled Std only",
  "source": "proofs/MaterialResponse.lean",
  "source_sha256": "8ce7f4b5bf4b68f9eeb0d85b06925f417995f945b64498a4533347ead1864092",
  "claims_sha256": "c997267322002413263b8a7f9d04a41807a5b24e2d95f78285cff3404f08fdc9",
  "command": "lean -DwarningAsError=true proofs/MaterialResponse.lean",
  "claims": [
    {
      "id": "material-confined-volume",
      "theorem": "Kenoma.Material.confined_volume",
      "claim": "With both lateral stretch numerators fixed at their reference scale, a smaller height numerator gives a smaller volume numerator.",
      "assumptions": "Exact integers s and h; s > 0 and h < s. Physical interpretation additionally takes h > 0 and stretches b=s/s=1, height=h/s. Volume numerator is b_numer\u00b2 \u00d7 h_numer over s\u00b3.",
      "limitations": "No real determinant, constitutive equilibrium, finite-element volume or floating-point result is proved.",
      "implementation": "web/material-response.mjs: active walls impose b=1; J=h is separately tested numerically.",
      "status": "checked",
      "axioms": [
        "propext"
      ]
    },
    {
      "id": "material-bulk-sign",
      "theorem": "Kenoma.Material.finite_bulk_penalty_nonnegative",
      "claim": "The exact scaled bulk-penalty numerator k \u00d7 delta\u00b2 is nonnegative for k \u2265 0.",
      "assumptions": "Integer k and delta; delta represents a scaled volume-ratio departure, and unit/denominator scale factors are positive.",
      "limitations": "The full real energy, fractional-power shear term and its derivatives are not formalized. A finite penalty is not a hard volume constraint.",
      "implementation": "web/material-response.mjs: bulkEnergyJ uses the unchanged tissue law; derivatives and finite-bulk volume loss are numerical checks.",
      "status": "checked",
      "axioms": [
        "propext"
      ]
    },
    {
      "id": "material-bulk-zero",
      "theorem": "Kenoma.Material.positive_bulk_zero_penalty",
      "claim": "For a strictly positive bulk coefficient, the exact bulk-penalty numerator is zero exactly when its volume-departure numerator is zero.",
      "assumptions": "Exact integer k > 0 and integer delta; positive external scaling factors.",
      "limitations": "Does not assert that a loaded equilibrium has zero penalty, or prove incompressibility, a real solver or biological validity.",
      "implementation": "web/material-response.mjs: positive bulk energy may coexist with J\u22601; K=0 is an explicit counterexample.",
      "status": "checked",
      "axioms": [
        "propext",
        "Classical.choice",
        "Quot.sound"
      ]
    },
    {
      "id": "material-separated-wall",
      "theorem": "Kenoma.Material.separated_wall_zero_reaction",
      "claim": "An assumed exact complementarity product with strictly positive wall gap forces zero wall reaction.",
      "assumptions": "Integer reaction and gap; gap > 0 and reaction \u00d7 gap = 0. Physical reaction nonnegativity and positive SI scales are separate inputs.",
      "limitations": "Complementarity is assumed, not derived or certified for the JavaScript root. No continuous collision or spatial contact guarantee.",
      "implementation": "web/material-response.mjs: unilateral walls allow pull-away; numerical tests verify gap, reaction, feasibility and complementarity work.",
      "status": "checked",
      "axioms": [
        "propext",
        "Quot.sound"
      ]
    },
    {
      "id": "material-lateral-work",
      "theorem": "Kenoma.Material.lateral_virtual_work",
      "claim": "The two lateral stress and wall-reaction contributions factor as 2 \u00d7 V\u2080 \u00d7 (P\u2093 + R) in exact scaled arithmetic.",
      "assumptions": "Integer volume, stress and reaction numerators with compatible positive external SI scales. The association with an energy derivative is assumed separately.",
      "limitations": "Does not prove the real energy derivative, stationarity, root existence, uniqueness, global optimality or force validity.",
      "implementation": "web/material-response.mjs: signed lateral residual; finite-difference tests separately check dU/db=2V\u2080P\u2093.",
      "status": "checked",
      "axioms": [
        "propext"
      ]
    }
  ]
}
```

## Kernel report {#material-kernel-report}

```text
'Kenoma.Material.confined_volume' depends on axioms: [propext]
'Kenoma.Material.finite_bulk_penalty_nonnegative' depends on axioms: [propext]
'Kenoma.Material.positive_bulk_zero_penalty' depends on axioms: [propext, Classical.choice, Quot.sound]
'Kenoma.Material.separated_wall_zero_reaction' depends on axioms: [propext, Quot.sound]
'Kenoma.Material.lateral_virtual_work' depends on axioms: [propext]

```
