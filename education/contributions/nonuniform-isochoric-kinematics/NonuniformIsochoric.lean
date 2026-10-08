import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Data.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Prescribed finite kinematics over Real. The matrix is the declared gradient
field, including off-axis shear. These contracts prove its algebraic determinant
and positive stretch on the stated material interval. They do not formally
derive the gradient, prove a change-of-variables integral, triangulation
correctness, floating-point refinement, equilibrium or biological validity.
-/
namespace KenomaNonuniform

def stretch (m a L S : ℝ) : ℝ := m * (1 + a * (2 * (S / L) - 1))

def transverse (lambda : ℝ) : ℝ := 1 / Real.sqrt lambda

def gradientField (lambda b shearY shearZ : ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  ![![lambda, 0, 0], ![shearY, b, 0], ![shearZ, 0, b]]

theorem gradient_determinant (lambda b shearY shearZ : ℝ) :
    Matrix.det (gradientField lambda b shearY shearZ) = lambda * b * b := by
  simp [gradientField, Matrix.det_fin_three, mul_assoc]

theorem positive_stretch_on_interval (m a L S : ℝ)
    (hm : 0 < m) (hL : 0 < L) (haLower : -1 < a) (haUpper : a < 1)
    (hS : 0 ≤ S) (hSL : S ≤ L) : 0 < stretch m a L S := by
  have ht0 : 0 ≤ S / L := div_nonneg hS hL.le
  have ht1 : S / L ≤ 1 := (div_le_one hL).mpr hSL
  have hinner : 0 < 1 + a * (2 * (S / L) - 1) := by
    rcases le_total 0 a with ha | ha
    · have hprod := mul_nonneg ha ht0
      nlinarith
    · have hprod := mul_nonneg (neg_nonneg.mpr ha) (sub_nonneg.mpr ht1)
      nlinarith
  exact mul_pos hm hinner

theorem pointwise_isochoric_gradient (lambda shearY shearZ : ℝ)
    (hlambda : 0 < lambda) :
    0 < transverse lambda ∧
      Matrix.det (gradientField lambda (transverse lambda) shearY shearZ) = 1 := by
  constructor
  · exact one_div_pos.mpr (Real.sqrt_pos.mpr hlambda)
  · rw [gradient_determinant]
    calc
      lambda * transverse lambda * transverse lambda =
          lambda * (Real.sqrt lambda * Real.sqrt lambda)⁻¹ := by
        simp only [transverse, one_div, mul_assoc, mul_inv]
      _ = 1 := by
        rw [Real.mul_self_sqrt hlambda.le]
        exact mul_inv_cancel₀ (ne_of_gt hlambda)

theorem nonuniform_isochoric_on_interval (m a L S shearY shearZ : ℝ)
    (hm : 0 < m) (hL : 0 < L) (haLower : -1 < a) (haUpper : a < 1)
    (hS : 0 ≤ S) (hSL : S ≤ L) :
    0 < transverse (stretch m a L S) ∧
      Matrix.det (gradientField (stretch m a L S)
        (transverse (stretch m a L S)) shearY shearZ) = 1 := by
  exact pointwise_isochoric_gradient _ _ _
    (positive_stretch_on_interval m a L S hm hL haLower haUpper hS hSL)

def straightCellRatio (r : ℝ) : ℝ :=
  (1 + r ^ 2) * (1 + 1 / r + 1 / r ^ 2) / 6

theorem straight_cell_error_factorization (r : ℝ) (hr : 0 < r) :
    straightCellRatio r - 1 =
      (r - 1) ^ 2 * (r ^ 2 + 3 * r + 1) / (6 * r ^ 2) := by
  unfold straightCellRatio
  field_simp [ne_of_gt hr]
  <;> ring

theorem straight_cell_ratio_ge_one (r : ℝ) (hr : 0 < r) :
    1 ≤ straightCellRatio r := by
  have hnum : 0 ≤ (r - 1) ^ 2 * (r ^ 2 + 3 * r + 1) :=
    mul_nonneg (sq_nonneg _) (by nlinarith [sq_nonneg r])
  have hden : 0 ≤ 6 * r ^ 2 := mul_nonneg (by norm_num) (sq_nonneg r)
  have herr := div_nonneg hnum hden
  rw [← straight_cell_error_factorization r hr] at herr
  linarith

end KenomaNonuniform

#print axioms KenomaNonuniform.gradient_determinant
#print axioms KenomaNonuniform.positive_stretch_on_interval
#print axioms KenomaNonuniform.pointwise_isochoric_gradient
#print axioms KenomaNonuniform.nonuniform_isochoric_on_interval
#print axioms KenomaNonuniform.straight_cell_error_factorization
#print axioms KenomaNonuniform.straight_cell_ratio_ge_one
