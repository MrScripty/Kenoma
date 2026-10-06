import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/-!
Exact local identities for the connected passive specimen's declared kinematics
and finite volumetric material. No FEM convergence, stability, JS equivalence,
mesh/renderer volume, positive determinant between samples or anatomy is proved.
-/
noncomputable section
namespace Kenoma.AxisymmetricSpecimenReal

def axisMatrix (a b c d h : ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  ![![a, 0, b], ![0, h, 0], ![c, 0, d]]

theorem axis_determinant (a b c d h : ℝ) :
    Matrix.det (axisMatrix a b c d h) = h * (a * d - b * c) := by
  simp [axisMatrix, Matrix.det_fin_three]
  ring

theorem uniform_determinant (side axial : ℝ) :
    Matrix.det (axisMatrix side 0 0 axial side) = axial * side ^ 2 := by
  rw [axis_determinant]
  ring

def logarithmicEnergy (bulk J : ℝ) : ℝ := bulk / 2 * (Real.log J) ^ 2

theorem logarithmic_energy_nonnegative (bulk J : ℝ) (hbulk : 0 ≤ bulk) :
    0 ≤ logarithmicEnergy bulk J := by
  exact mul_nonneg (div_nonneg hbulk (by norm_num)) (sq_nonneg (Real.log J))

theorem logarithmic_energy_rest (bulk : ℝ) : logarithmicEnergy bulk 1 = 0 := by
  simp [logarithmicEnergy]

theorem logarithmic_energy_derivative (bulk J : ℝ) (hJ : 0 < J) :
    HasDerivAt (logarithmicEnergy bulk) (bulk * Real.log J / J) J := by
  have hd := ((Real.hasDerivAt_log (ne_of_gt hJ)).pow 2).const_mul (bulk / 2)
  convert hd using 1
  dsimp [logarithmicEnergy]
  simp only [div_eq_mul_inv]
  ring

theorem full_side_traction (A B C D H slope : ℝ) :
    (axisMatrix A B C D H).mulVec ![1, 0, -slope] =
      ![A - slope * B, 0, C - slope * D] := by
  ext i
  fin_cases i <;> simp [Matrix.mulVec, dotProduct, axisMatrix, Fin.sum_univ_succ] <;> ring

theorem uniform_force_conversion (area side axial sigma : ℝ) (haxial : axial ≠ 0) :
    area * ((axial * side ^ 2) / axial * sigma) = area * side ^ 2 * sigma := by
  field_simp [haxial]
  ring

def profilePrimitive (radius length ratio Z : ℝ) : ℝ :=
  Real.pi * radius ^ 2 *
    (Z + (ratio - 1) / length * Z ^ 2 + (ratio - 1) ^ 2 / (3 * length ^ 2) * Z ^ 3)

theorem profile_primitive_derivative (radius length ratio Z : ℝ) (hL : length ≠ 0) :
    HasDerivAt (profilePrimitive radius length ratio)
      (Real.pi * (radius * (1 + (ratio - 1) * Z / length)) ^ 2) Z := by
  have hi := hasDerivAt_id Z
  have hd := ((hi.add ((hi.pow 2).const_mul ((ratio - 1) / length))).add
    ((hi.pow 3).const_mul ((ratio - 1) ^ 2 / (3 * length ^ 2)))).const_mul
      (Real.pi * radius ^ 2)
  convert hd using 1
  dsimp [profilePrimitive]
  field_simp [hL]
  ring

theorem frustum_primitive_endpoints (radius length ratio : ℝ) (hL : length ≠ 0) :
    profilePrimitive radius length ratio length - profilePrimitive radius length ratio 0 =
      Real.pi * length * radius ^ 2 * (1 + ratio + ratio ^ 2) / 3 := by
  dsimp [profilePrimitive]
  field_simp [hL]
  ring

end Kenoma.AxisymmetricSpecimenReal
#print axioms Kenoma.AxisymmetricSpecimenReal.axis_determinant
#print axioms Kenoma.AxisymmetricSpecimenReal.uniform_determinant
#print axioms Kenoma.AxisymmetricSpecimenReal.logarithmic_energy_nonnegative
#print axioms Kenoma.AxisymmetricSpecimenReal.logarithmic_energy_rest
#print axioms Kenoma.AxisymmetricSpecimenReal.logarithmic_energy_derivative
#print axioms Kenoma.AxisymmetricSpecimenReal.full_side_traction
#print axioms Kenoma.AxisymmetricSpecimenReal.uniform_force_conversion
#print axioms Kenoma.AxisymmetricSpecimenReal.profile_primitive_derivative
#print axioms Kenoma.AxisymmetricSpecimenReal.frustum_primitive_endpoints
