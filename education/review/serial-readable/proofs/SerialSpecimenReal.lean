import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.Calculus.Deriv.Inv
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Local homogeneous incompressible neo-Hookean blocks, with positive axial stretch.
Separate blocks in series are assumed to transmit the same force through ideal
lateral-sliding fixtures. No continuous stepped-solid interface, numerical root
refinement, global stability, mesh-volume implementation, or anatomy is proved.
-/
noncomputable section
namespace Kenoma.SerialSpecimenReal

def energy (mu l : ℝ) : ℝ := mu / 2 * (l ^ 2 + 2 / l - 3)
def nominalStress (mu l : ℝ) : ℝ := mu * (l - 1 / l ^ 2)
def cauchyStress (mu l : ℝ) : ℝ := mu * (l ^ 2 - 1 / l)

theorem energy_factor (mu l : ℝ) (hl : 0 < l) :
    energy mu l = mu / (2 * l) * (l - 1) ^ 2 * (l + 2) := by
  dsimp [energy]
  field_simp [ne_of_gt hl]
  ring

theorem energy_nonnegative (mu l : ℝ) (hm : 0 ≤ mu) (hl : 0 < l) :
    0 ≤ energy mu l := by
  rw [energy_factor mu l hl]
  exact mul_nonneg (mul_nonneg (div_nonneg hm (by positivity)) (sq_nonneg _))
    (by linarith)

theorem energy_zero_iff (mu l : ℝ) (hm : 0 < mu) (hl : 0 < l) :
    energy mu l = 0 ↔ l = 1 := by
  rw [energy_factor mu l hl]
  have hcoeff : 0 < mu / (2 * l) := div_pos hm (by positivity)
  have hlast : 0 < l + 2 := by linarith
  constructor
  · intro h
    have hs : (l - 1) ^ 2 = 0 := by
      rcases mul_eq_zero.mp h with h | h
      · exact (mul_eq_zero.mp h).resolve_left (ne_of_gt hcoeff)
      · exact False.elim ((ne_of_gt hlast) h)
    nlinarith [sq_nonneg (l - 1)]
  · intro h
    simp [h]

theorem energy_hasDerivAt (mu l : ℝ) (hl : 0 < l) :
    HasDerivAt (energy mu) (nominalStress mu l) l := by
  have hid := hasDerivAt_id l
  have hd := ((((hid.mul hid).add ((hid.inv (ne_of_gt hl)).const_mul 2)).sub_const 3).const_mul (mu / 2))
  convert hd using 1
  · funext y
    dsimp [energy]
    ring
  · dsimp [nominalStress]
    ring

theorem nominal_factor_and_cauchy (mu l : ℝ) (hl : 0 < l) :
    nominalStress mu l = mu * (l - 1) * (l ^ 2 + l + 1) / l ^ 2 ∧
      cauchyStress mu l = l * nominalStress mu l := by
  dsimp [nominalStress, cauchyStress]
  constructor <;> field_simp [ne_of_gt hl] <;> ring

theorem nominal_sign (mu l : ℝ) (hm : 0 < mu) (hl : 0 < l) :
    (0 < nominalStress mu l ↔ 1 < l) ∧
      (nominalStress mu l = 0 ↔ l = 1) ∧
      (nominalStress mu l < 0 ↔ l < 1) := by
  have hpoly : 0 < l ^ 2 + l + 1 := by nlinarith [sq_nonneg l]
  have hcoeff : 0 < mu * (l ^ 2 + l + 1) / l ^ 2 :=
    div_pos (mul_pos hm hpoly) (sq_pos_of_pos hl)
  have hf : nominalStress mu l = (mu * (l ^ 2 + l + 1) / l ^ 2) * (l - 1) := by
    rw [(nominal_factor_and_cauchy mu l hl).1]
    ring
  rw [hf]
  constructor
  · constructor <;> intro h <;> nlinarith
  · constructor
    · constructor
      · intro h
        have hz := (mul_eq_zero.mp h).resolve_left (ne_of_gt hcoeff)
        linarith
      · intro h
        simp [h]
    · constructor <;> intro h <;> nlinarith

theorem nominal_difference (mu u v : ℝ) (hu : 0 < u) (hv : 0 < v) :
    nominalStress mu v - nominalStress mu u =
      mu * (v - u) * (1 + (u + v) / (u ^ 2 * v ^ 2)) := by
  dsimp [nominalStress]
  field_simp [ne_of_gt hu, ne_of_gt hv]
  ring

theorem nominal_strictMono (mu : ℝ) (hm : 0 < mu) :
    StrictMonoOn (nominalStress mu) (Set.Ioi 0) := by
  intro u hu v hv huv
  have hratio : 0 < (u + v) / (u ^ 2 * v ^ 2) :=
    div_pos (add_pos hu hv) (mul_pos (sq_pos_of_pos hu) (sq_pos_of_pos hv))
  have hdiff := mul_pos (mul_pos hm (sub_pos.mpr huv)) (show 0 < 1 + (u + v) / (u ^ 2 * v ^ 2) by linarith)
  rw [← nominal_difference mu u v hu hv] at hdiff
  linarith

theorem homogeneous_root_unique (mu A N u v : ℝ) (hm : 0 < mu) (hA : 0 < A)
    (hu : 0 < u) (hv : 0 < v)
    (hNu : A * nominalStress mu u = N) (hNv : A * nominalStress mu v = N) :
    u = v := by
  have hp : nominalStress mu u = nominalStress mu v := by nlinarith
  exact (nominal_strictMono mu hm).injOn hu hv hp

theorem area_length_volume (A L l : ℝ) (hl : 0 < l) :
    (A / l) * (L * l) = A * L := by
  field_simp [ne_of_gt hl]
  ring

theorem same_force_tension_order (mu A1 A2 N l1 l2 : ℝ)
    (hm : 0 < mu) (hA1 : 0 < A1) (hA : A1 < A2) (hN : 0 < N)
    (hl1 : 0 < l1) (hl2 : 0 < l2)
    (h1 : A1 * nominalStress mu l1 = N) (h2 : A2 * nominalStress mu l2 = N) :
    1 < l2 ∧ l2 < l1 := by
  have hA2 : 0 < A2 := lt_trans hA1 hA
  have hp2 : 0 < nominalStress mu l2 := by nlinarith
  have hstretch := (nominal_sign mu l2 hm hl2).1.mp hp2
  refine ⟨hstretch, ?_⟩
  by_contra h
  have hle : l1 ≤ l2 := le_of_not_gt h
  have hp : nominalStress mu l1 ≤ nominalStress mu l2 :=
    (nominal_strictMono mu hm).monotoneOn hl1 hl2 hle
  have hgap := mul_pos (sub_pos.mpr hA) hp2
  nlinarith

theorem same_force_compression_order (mu A1 A2 N l1 l2 : ℝ)
    (hm : 0 < mu) (hA1 : 0 < A1) (hA : A1 < A2) (hN : N < 0)
    (hl1 : 0 < l1) (hl2 : 0 < l2)
    (h1 : A1 * nominalStress mu l1 = N) (h2 : A2 * nominalStress mu l2 = N) :
    l1 < l2 ∧ l2 < 1 := by
  have hA2 : 0 < A2 := lt_trans hA1 hA
  have hp2 : nominalStress mu l2 < 0 := by nlinarith
  have hstretch := (nominal_sign mu l2 hm hl2).2.2.mp hp2
  refine ⟨?_, hstretch⟩
  by_contra h
  have hle : l2 ≤ l1 := le_of_not_gt h
  have hp : nominalStress mu l2 ≤ nominalStress mu l1 :=
    (nominal_strictMono mu hm).monotoneOn hl2 hl1 hle
  have hgap := mul_neg_of_pos_of_neg (sub_pos.mpr hA) hp2
  nlinarith

end Kenoma.SerialSpecimenReal

#print axioms Kenoma.SerialSpecimenReal.energy_factor
#print axioms Kenoma.SerialSpecimenReal.energy_nonnegative
#print axioms Kenoma.SerialSpecimenReal.energy_zero_iff
#print axioms Kenoma.SerialSpecimenReal.energy_hasDerivAt
#print axioms Kenoma.SerialSpecimenReal.nominal_factor_and_cauchy
#print axioms Kenoma.SerialSpecimenReal.nominal_sign
#print axioms Kenoma.SerialSpecimenReal.nominal_difference
#print axioms Kenoma.SerialSpecimenReal.nominal_strictMono
#print axioms Kenoma.SerialSpecimenReal.homogeneous_root_unique
#print axioms Kenoma.SerialSpecimenReal.area_length_volume
#print axioms Kenoma.SerialSpecimenReal.same_force_tension_order
#print axioms Kenoma.SerialSpecimenReal.same_force_compression_order
