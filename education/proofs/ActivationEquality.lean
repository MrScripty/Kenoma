import Mathlib.Topology.Algebra.Ring.Real
import Mathlib.Topology.Order.DenselyOrdered
import Mathlib.Topology.Algebra.Field
import Mathlib.Topology.Piecewise
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring.Basic

/-!
Exact real activation equations from the pinned OpenSim source, evaluated at
an already clamped activation. Numerical solvers and ODE invariance are not proved.
-/
namespace KenomaActivation
noncomputable section

def scale (a : ℝ) : ℝ := 1 / 2 + 3 / 2 * a
def activationTau (TA a : ℝ) : ℝ := TA * scale a
def deactivationTau (TD a : ℝ) : ℝ := TD / scale a
def activationRate (TA a u : ℝ) : ℝ := (u - a) / activationTau TA a
def deactivationRate (TD a u : ℝ) : ℝ := (u - a) / deactivationTau TD a
def rate (TA TD a u : ℝ) : ℝ :=
  if a < u then activationRate TA a u else deactivationRate TD a u
def clampedRate (TA TD amin a u : ℝ) : ℝ :=
  rate TA TD (min 1 (max amin a)) u

theorem clamp_identity (TA TD amin a u : ℝ) (hl : amin ≤ a) (hu : a ≤ 1) :
    clampedRate TA TD amin a u = rate TA TD a u := by
  simp [clampedRate, max_eq_right hl, min_eq_right hu]

theorem scale_positive (a : ℝ) (ha : 0 ≤ a) : 0 < scale a := by
  unfold scale
  linarith

theorem time_constants_positive (TA TD a : ℝ) (hTA : 0 < TA)
    (hTD : 0 < TD) (ha : 0 ≤ a) :
    0 < activationTau TA a ∧ 0 < deactivationTau TD a := by
  exact ⟨mul_pos hTA (scale_positive a ha), div_pos hTD (scale_positive a ha)⟩

theorem one_sided_equality (TA TD a : ℝ) :
    activationRate TA a a = 0 ∧ deactivationRate TD a a = 0 := by
  simp [activationRate, deactivationRate]

theorem rate_equality (TA TD a : ℝ) : rate TA TD a a = 0 := by
  simp [rate, deactivationRate]

theorem positive_above (TA TD a u : ℝ) (hTA : 0 < TA)
    (ha : 0 ≤ a) (h : a < u) : 0 < rate TA TD a u := by
  simp only [rate, if_pos h, activationRate]
  exact div_pos (sub_pos.mpr h) (mul_pos hTA (scale_positive a ha))

theorem negative_below (TA TD a u : ℝ) (hTD : 0 < TD)
    (ha : 0 ≤ a) (h : u < a) : rate TA TD a u < 0 := by
  simp only [rate, if_neg (not_lt.mpr h.le), deactivationRate]
  exact div_neg_of_neg_of_pos (sub_neg.mpr h) (div_pos hTD (scale_positive a ha))

theorem restoring_sign (TA TD a u : ℝ) (hTA : 0 < TA)
    (hTD : 0 < TD) (ha : 0 ≤ a) : (a - u) * rate TA TD a u ≤ 0 := by
  rcases lt_trichotomy a u with h | h | h
  · exact mul_nonpos_of_nonpos_of_nonneg (sub_nonpos.mpr h.le)
      (positive_above TA TD a u hTA ha h).le
  · subst u
    simp
  · exact mul_nonpos_of_nonneg_of_nonpos (sub_nonneg.mpr h.le)
      (negative_below TA TD a u hTD ha h).le

theorem restoring_strict (TA TD a u : ℝ) (hTA : 0 < TA)
    (hTD : 0 < TD) (ha : 0 ≤ a) (hne : a ≠ u) :
    (a - u) * rate TA TD a u < 0 := by
  rcases lt_or_gt_of_ne hne with h | h
  · exact mul_neg_of_neg_of_pos (sub_neg.mpr h) (positive_above TA TD a u hTA ha h)
  · exact mul_neg_of_pos_of_neg (sub_pos.mpr h) (negative_below TA TD a u hTD ha h)

theorem lower_boundary_inward (TA TD amin u : ℝ) (hTA : 0 < TA)
    (hmin : 0 ≤ amin) (hu : amin ≤ u) : 0 ≤ rate TA TD amin u := by
  rcases hu.eq_or_lt with h | h
  · subst u
    rw [rate_equality]
  · exact (positive_above TA TD amin u hTA hmin h).le

theorem upper_boundary_inward (TA TD u : ℝ) (hTD : 0 < TD)
    (hu : u ≤ 1) : rate TA TD 1 u ≤ 0 := by
  rcases hu.eq_or_lt with h | h
  · subst u
    rw [rate_equality]
  · exact (negative_below TA TD 1 u hTD (by norm_num) h).le

theorem continuous_excitation (TA TD a : ℝ) :
    Continuous (fun u : ℝ => rate TA TD a u) := by
  unfold rate
  apply Continuous.if
  · intro u hu
    have heq : u = a := by
      simpa only [show {u : ℝ | a < u} = Set.Ioi a from rfl,
        frontier_Ioi, Set.mem_singleton_iff] using hu
    subst u
    exact (one_sided_equality TA TD a).1.trans (one_sided_equality TA TD a).2.symm
  · exact (continuous_id.sub continuous_const).div_const _
  · exact (continuous_id.sub continuous_const).div_const _

theorem deactivation_rewrite (TD a u : ℝ) :
    deactivationRate TD a u = (u - a) * scale a / TD := by
  unfold deactivationRate deactivationTau
  simp only [div_div_eq_mul_div]

theorem coefficient_agreement_iff (TA TD a : ℝ) (hTA : 0 < TA)
    (hTD : 0 < TD) (ha : 0 ≤ a) :
    1 / activationTau TA a = 1 / deactivationTau TD a ↔
      TD = TA * (scale a) ^ 2 := by
  have hs := ne_of_gt (scale_positive a ha)
  have htA := ne_of_gt hTA
  have htD := ne_of_gt hTD
  unfold activationTau deactivationTau
  field_simp
  ring_nf

theorem default_coefficients_at_upper :
    1 / activationTau (1 / 100) 1 = 1 / deactivationTau (1 / 25) 1 := by
  norm_num [activationTau, deactivationTau, scale]

end
end KenomaActivation

#print axioms KenomaActivation.clamp_identity
#print axioms KenomaActivation.scale_positive
#print axioms KenomaActivation.time_constants_positive
#print axioms KenomaActivation.one_sided_equality
#print axioms KenomaActivation.rate_equality
#print axioms KenomaActivation.positive_above
#print axioms KenomaActivation.negative_below
#print axioms KenomaActivation.restoring_sign
#print axioms KenomaActivation.restoring_strict
#print axioms KenomaActivation.lower_boundary_inward
#print axioms KenomaActivation.upper_boundary_inward
#print axioms KenomaActivation.continuous_excitation
#print axioms KenomaActivation.deactivation_rewrite
#print axioms KenomaActivation.coefficient_agreement_iff
#print axioms KenomaActivation.default_coefficients_at_upper
