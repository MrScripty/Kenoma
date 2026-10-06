import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Exact scalar real identities for the approved integrating-field weight.
No trajectory, event localization, existence, residence or stability theorem.
-/
namespace KenomaFilippov
noncomputable section

def weight (νon νoff : ℝ) : ℝ := -νoff / (νon - νoff)
def mixedNormal (θ νon νoff : ℝ) : ℝ := θ * νon + (1 - θ) * νoff
def onNormal (η d k : ℝ) : ℝ := η * (d + k)
def offNormal (η d : ℝ) : ℝ := η * d

theorem normal_gap_positive (νon νoff : ℝ) (hon : 0 < νon) (hoff : νoff < 0) :
    0 < νon - νoff := by
  linarith

theorem denominator_nonzero (νon νoff : ℝ) (hon : 0 < νon) (hoff : νoff < 0) :
    νon - νoff ≠ 0 := by
  exact ne_of_gt (normal_gap_positive νon νoff hon hoff)

theorem weight_positive (νon νoff : ℝ) (hon : 0 < νon) (hoff : νoff < 0) :
    0 < weight νon νoff := by
  exact div_pos (neg_pos.mpr hoff) (normal_gap_positive νon νoff hon hoff)

theorem weight_below_one (νon νoff : ℝ) (hon : 0 < νon) (hoff : νoff < 0) :
    weight νon νoff < 1 := by
  unfold weight
  exact (div_lt_one (normal_gap_positive νon νoff hon hoff)).2 (by linarith)

theorem weighted_normal_zero (νon νoff : ℝ) (hden : νon - νoff ≠ 0) :
    mixedNormal (weight νon νoff) νon νoff = 0 := by
  unfold mixedNormal weight
  field_simp [hden]
  ring

theorem unique_zero_normal_weight (θ νon νoff : ℝ) (hden : νon - νoff ≠ 0)
    (hz : mixedNormal θ νon νoff = 0) : θ = weight νon νoff := by
  unfold weight
  apply (eq_div_iff hden).2
  unfold mixedNormal at hz
  nlinarith

theorem strict_attraction_selection (νon νoff : ℝ) (hon : 0 < νon) (hoff : νoff < 0) :
    0 < weight νon νoff ∧ weight νon νoff < 1 ∧
      mixedNormal (weight νon νoff) νon νoff = 0 ∧
      ∀ θ : ℝ, mixedNormal θ νon νoff = 0 → θ = weight νon νoff := by
  have hden := denominator_nonzero νon νoff hon hoff
  exact ⟨weight_positive νon νoff hon hoff, weight_below_one νon νoff hon hoff,
    weighted_normal_zero νon νoff hden,
    fun θ hz => unique_zero_normal_weight θ νon νoff hden hz⟩

theorem source_normal_gap (η d k : ℝ) :
    onNormal η d k - offNormal η d = η * k := by
  unfold onNormal offNormal
  ring

theorem source_integrating_rate_nonzero (η d k : ℝ)
    (hon : 0 < onNormal η d k) (hoff : offNormal η d < 0) : k ≠ 0 := by
  have hgap := normal_gap_positive (onNormal η d k) (offNormal η d) hon hoff
  rw [source_normal_gap] at hgap
  intro hk
  simp [hk] at hgap

theorem source_weight_identity (η d k : ℝ) (hη : η ≠ 0) (hk : k ≠ 0) :
    weight (onNormal η d k) (offNormal η d) = -d / k := by
  unfold weight
  rw [source_normal_gap]
  unfold offNormal
  field_simp [hη, hk]
  ring

theorem source_weight_strict_bounds (η d k : ℝ) (hη : η ≠ 0)
    (hon : 0 < onNormal η d k) (hoff : offNormal η d < 0) :
    0 < -d / k ∧ -d / k < 1 := by
  have hk := source_integrating_rate_nonzero η d k hon hoff
  rw [← source_weight_identity η d k hη hk]
  exact ⟨weight_positive _ _ hon hoff, weight_below_one _ _ hon hoff⟩

theorem source_integral_rate (d k : ℝ) (hk : k ≠ 0) :
    (-d / k) * k + (1 - (-d / k)) * 0 = -d := by
  field_simp [hk]

theorem source_normal_tangency (η d k : ℝ) (hk : k ≠ 0) :
    η * (d + ((-d / k) * k + (1 - (-d / k)) * 0)) = 0 := by
  rw [source_integral_rate d k hk]
  ring

theorem source_unique_weight (θ η d k : ℝ) (hη : η ≠ 0) (hk : k ≠ 0)
    (hz : mixedNormal θ (onNormal η d k) (offNormal η d) = 0) : θ = -d / k := by
  have hden : onNormal η d k - offNormal η d ≠ 0 := by
    rw [source_normal_gap]
    exact mul_ne_zero hη hk
  rw [← source_weight_identity η d k hη hk]
  exact unique_zero_normal_weight θ _ _ hden hz

end
end KenomaFilippov

#print axioms KenomaFilippov.normal_gap_positive
#print axioms KenomaFilippov.denominator_nonzero
#print axioms KenomaFilippov.weight_positive
#print axioms KenomaFilippov.weight_below_one
#print axioms KenomaFilippov.weighted_normal_zero
#print axioms KenomaFilippov.unique_zero_normal_weight
#print axioms KenomaFilippov.strict_attraction_selection
#print axioms KenomaFilippov.source_normal_gap
#print axioms KenomaFilippov.source_integrating_rate_nonzero
#print axioms KenomaFilippov.source_weight_identity
#print axioms KenomaFilippov.source_weight_strict_bounds
#print axioms KenomaFilippov.source_integral_rate
#print axioms KenomaFilippov.source_normal_tangency
#print axioms KenomaFilippov.source_unique_weight
