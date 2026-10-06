import Mathlib.Data.Real.Sqrt

/-!
Real-domain counterparts for the homogeneous specimen's geometric, bulk-energy
and assumed contact/virtual-work algebra. These do not prove constitutive real
power derivatives, root existence/uniqueness, JavaScript refinement or biology.
No checked status may be assigned until pinned mathlib compiles this source.
-/
noncomputable section
namespace Kenoma.MaterialReal

def volumeRatio (b h : ℝ) : ℝ := b * b * h
def bulkEnergy (V K J : ℝ) : ℝ := V * K / 2 * ((J - 1) * (J - 1))

theorem confined_volume (h : ℝ) (hh : 0 < h) (hc : h < 1) :
    volumeRatio 1 h = h ∧ 0 < volumeRatio 1 h ∧ volumeRatio 1 h < 1 := by
  constructor
  · simp [volumeRatio]
  · simpa [volumeRatio] using And.intro hh hc

theorem finite_bulk_energy_nonnegative (V K J : ℝ) (hV : 0 ≤ V) (hK : 0 ≤ K) :
    0 ≤ bulkEnergy V K J := by
  apply mul_nonneg
  · exact div_nonneg (mul_nonneg hV hK) (le_of_lt zero_lt_two)
  · simpa only [pow_two] using sq_nonneg (J - 1)

theorem positive_bulk_zero_energy (V K J : ℝ) (hV : 0 < V) (hK : 0 < K) :
    bulkEnergy V K J = 0 ↔ J = 1 := by
  have coefficient : V * K / 2 ≠ 0 := ne_of_gt (div_pos (mul_pos hV hK) zero_lt_two)
  simp [bulkEnergy, mul_eq_zero, coefficient, sub_eq_zero]

theorem separated_wall_zero_reaction (reaction gap : ℝ)
    (hg : 0 < gap) (hc : reaction * gap = 0) : reaction = 0 := by
  exact (mul_eq_zero.mp hc).resolve_right (ne_of_gt hg)

-- The association of stress with an energy derivative is a separate obligation.
theorem lateral_virtual_work (V stress reaction delta : ℝ) :
    2 * V * stress * delta + 2 * V * reaction * delta =
      2 * V * (stress + reaction) * delta := by
  rw [← add_mul, ← mul_add]

end Kenoma.MaterialReal

#print axioms Kenoma.MaterialReal.confined_volume
#print axioms Kenoma.MaterialReal.finite_bulk_energy_nonnegative
#print axioms Kenoma.MaterialReal.positive_bulk_zero_energy
#print axioms Kenoma.MaterialReal.separated_wall_zero_reaction
#print axioms Kenoma.MaterialReal.lateral_virtual_work
