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
