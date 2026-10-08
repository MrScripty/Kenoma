import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Original passive discrete guided load path over Real. E is a reduced axial
modulus. Two localized interface links are an authored discretization, not
distributed endomysium or measured fibre architecture. These algebraic claims
do not certify differentiation, JavaScript, continuum equilibrium or biology.
Checked status requires a fresh source-bound pinned kernel receipt.
-/
noncomputable section
namespace KenomaLateralTransfer

def axial (E A L : ℝ) : ℝ := E * A / L
def shear (G A h : ℝ) : ℝ := G * A / h
def upper (K C d : ℝ) : ℝ := C * d / (K + C)
def lower (K C d : ℝ) : ℝ := K * d / (K + C)
def branch (K C : ℝ) : ℝ := K * C / (K + C)
def effective (K1 K2 CL CR : ℝ) : ℝ := branch K1 CR + branch K2 CL
def energy (K1 K2 CL CR d u v : ℝ) : ℝ :=
  K1 * u ^ 2 / 2 + K2 * (d - v) ^ 2 / 2 + CL * v ^ 2 / 2 + CR * (d - u) ^ 2 / 2

theorem material_resultants (E A L G As h s : ℝ) (hL : 0 < L) (hh : 0 < h) :
    axial E A L * s = A * (E * (s / L)) ∧
      shear G As h * s = As * (G * (s / h)) := by
  dsimp [axial, shear]
  constructor <;> field_simp [ne_of_gt hL, ne_of_gt hh] <;> ring

theorem stationary_solution (K1 K2 CL CR d : ℝ)
    (hK1 : 0 < K1) (hK2 : 0 < K2) (hCL : 0 ≤ CL) (hCR : 0 ≤ CR) :
    K1 * upper K1 CR d = CR * (d - upper K1 CR d) ∧
      K2 * (d - lower K2 CL d) = CL * lower K2 CL d := by
  have h1 := ne_of_gt (add_pos_of_pos_of_nonneg hK1 hCR)
  have h2 := ne_of_gt (add_pos_of_pos_of_nonneg hK2 hCL)
  dsimp [upper, lower]
  constructor <;> field_simp [h1, h2] <;> ring

theorem matched_end_resultants (K1 K2 CL CR d : ℝ)
    (hK1 : 0 < K1) (hK2 : 0 < K2) (hCL : 0 ≤ CL) (hCR : 0 ≤ CR) :
    K1 * upper K1 CR d + CL * lower K2 CL d = effective K1 K2 CL CR * d ∧
      K2 * (d - lower K2 CL d) + CR * (d - upper K1 CR d) =
        effective K1 K2 CL CR * d := by
  have h1 := ne_of_gt (add_pos_of_pos_of_nonneg hK1 hCR)
  have h2 := ne_of_gt (add_pos_of_pos_of_nonneg hK2 hCL)
  dsimp [upper, lower, effective, branch]
  constructor <;> field_simp [h1, h2] <;> ring

theorem energy_completion_unique_minimum (K1 K2 CL CR d u v : ℝ)
    (hK1 : 0 < K1) (hK2 : 0 < K2) (hCL : 0 ≤ CL) (hCR : 0 ≤ CR) :
    energy K1 K2 CL CR d u v - effective K1 K2 CL CR * d ^ 2 / 2 =
      (K1 + CR) / 2 * (u - upper K1 CR d) ^ 2 +
        (K2 + CL) / 2 * (v - lower K2 CL d) ^ 2 ∧
    0 ≤ energy K1 K2 CL CR d u v - effective K1 K2 CL CR * d ^ 2 / 2 ∧
    (energy K1 K2 CL CR d u v = effective K1 K2 CL CR * d ^ 2 / 2 ↔
      u = upper K1 CR d ∧ v = lower K2 CL d) := by
  have hp1 : 0 < (K1 + CR) / 2 := div_pos (add_pos_of_pos_of_nonneg hK1 hCR) zero_lt_two
  have hp2 : 0 < (K2 + CL) / 2 := div_pos (add_pos_of_pos_of_nonneg hK2 hCL) zero_lt_two
  have h1 := ne_of_gt (add_pos_of_pos_of_nonneg hK1 hCR)
  have h2 := ne_of_gt (add_pos_of_pos_of_nonneg hK2 hCL)
  have hid : energy K1 K2 CL CR d u v - effective K1 K2 CL CR * d ^ 2 / 2 =
      (K1 + CR) / 2 * (u - upper K1 CR d) ^ 2 +
        (K2 + CL) / 2 * (v - lower K2 CL d) ^ 2 := by
    dsimp [energy, effective, branch, upper, lower]
    field_simp [h1, h2]
    ring
  have hn1 := mul_nonneg hp1.le (sq_nonneg (u - upper K1 CR d))
  have hn2 := mul_nonneg hp2.le (sq_nonneg (v - lower K2 CL d))
  refine ⟨hid, ?_, ?_⟩
  · rw [hid]
    exact add_nonneg hn1 hn2
  · constructor
    · intro heq
      have hz : (K1 + CR) / 2 * (u - upper K1 CR d) ^ 2 +
          (K2 + CL) / 2 * (v - lower K2 CL d) ^ 2 = 0 := by
        rw [← hid, heq, sub_self]
      have hs := (add_eq_zero_iff_of_nonneg hn1 hn2).mp hz
      have hu := (mul_eq_zero.mp hs.1).resolve_left (ne_of_gt hp1)
      have hv := (mul_eq_zero.mp hs.2).resolve_left (ne_of_gt hp2)
      exact ⟨sub_eq_zero.mp (sq_eq_zero_iff.mp hu), sub_eq_zero.mp (sq_eq_zero_iff.mp hv)⟩
    · rintro ⟨hu, hv⟩
      apply sub_eq_zero.mp
      rw [hid, hu, hv]
      simp

theorem transfer_stiffness_bounds (K1 K2 CL CR : ℝ)
    (hK1 : 0 < K1) (hK2 : 0 < K2) (hCL : 0 ≤ CL) (hCR : 0 ≤ CR) :
    0 ≤ effective K1 K2 CL CR ∧ effective K1 K2 CL CR < K1 + K2 ∧
      (effective K1 K2 CL CR = 0 ↔ CL = 0 ∧ CR = 0) := by
  have hp1 := add_pos_of_pos_of_nonneg hK1 hCR
  have hp2 := add_pos_of_pos_of_nonneg hK2 hCL
  have hn1 : 0 ≤ branch K1 CR := div_nonneg (mul_nonneg hK1.le hCR) hp1.le
  have hn2 : 0 ≤ branch K2 CL := div_nonneg (mul_nonneg hK2.le hCL) hp2.le
  have hgap : K1 + K2 - effective K1 K2 CL CR = K1 ^ 2 / (K1 + CR) + K2 ^ 2 / (K2 + CL) := by
    dsimp [effective, branch]
    field_simp [ne_of_gt hp1, ne_of_gt hp2]
    ring
  refine ⟨add_nonneg hn1 hn2, ?_, ?_⟩
  · apply sub_pos.mp
    rw [hgap]
    exact add_pos (div_pos (sq_pos_of_pos hK1) hp1) (div_pos (sq_pos_of_pos hK2) hp2)
  · constructor
    · intro hz
      have hs := (add_eq_zero_iff_of_nonneg hn1 hn2).mp hz
      have hnum1 : K1 * CR = 0 := (div_eq_zero_iff.mp hs.1).resolve_right (ne_of_gt hp1)
      have hnum2 : K2 * CL = 0 := (div_eq_zero_iff.mp hs.2).resolve_right (ne_of_gt hp2)
      exact ⟨(mul_eq_zero.mp hnum2).resolve_left (ne_of_gt hK2),
        (mul_eq_zero.mp hnum1).resolve_left (ne_of_gt hK1)⟩
    · rintro ⟨rfl, rfl⟩
      simp [effective, branch]

theorem interface_stiffness_difference (K1 K2 CL CR CR' : ℝ)
    (hK1 : 0 < K1) (hK2 : 0 < K2) (hCL : 0 ≤ CL) (hCR : 0 ≤ CR) (hCR' : CR ≤ CR') :
    effective K1 K2 CL CR' - effective K1 K2 CL CR =
      K1 ^ 2 * (CR' - CR) / ((K1 + CR') * (K1 + CR)) ∧
      effective K1 K2 CL CR ≤ effective K1 K2 CL CR' := by
  have hp := add_pos_of_pos_of_nonneg hK1 hCR
  have hp' := add_pos_of_pos_of_nonneg hK1 (le_trans hCR hCR')
  have hid : effective K1 K2 CL CR' - effective K1 K2 CL CR =
      K1 ^ 2 * (CR' - CR) / ((K1 + CR') * (K1 + CR)) := by
    dsimp [effective, branch]
    field_simp [ne_of_gt hp, ne_of_gt hp', ne_of_gt (add_pos_of_pos_of_nonneg hK2 hCL)]
    ring
  refine ⟨hid, ?_⟩
  apply sub_nonneg.mp
  rw [hid]
  exact div_nonneg (mul_nonneg (sq_nonneg K1) (sub_nonneg.mpr hCR')) (mul_pos hp' hp).le

end KenomaLateralTransfer
#print axioms KenomaLateralTransfer.material_resultants
#print axioms KenomaLateralTransfer.stationary_solution
#print axioms KenomaLateralTransfer.matched_end_resultants
#print axioms KenomaLateralTransfer.energy_completion_unique_minimum
#print axioms KenomaLateralTransfer.transfer_stiffness_bounds
#print axioms KenomaLateralTransfer.interface_stiffness_difference
