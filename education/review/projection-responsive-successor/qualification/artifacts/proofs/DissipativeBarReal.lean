import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Local real standard-linear-solid law: the equilibrium spring E0 is parallel to
a Maxwell branch with spring E1 and viscosity eta. The viscous strain is v.
These are mathematical density and constant-strain relaxation contracts, not
JavaScript refinement, quadrature, axial-bar solution, calibration, or biological
validation. No numerical work/energy residual or time-step acceptance is proved.
-/
noncomputable section
namespace Kenoma.DissipativeBarReal

def stress (E0 E1 eps v : ℝ) : ℝ := E0 * eps + E1 * (eps - v)

def storage (E0 E1 eps v : ℝ) : ℝ :=
  E0 / 2 * eps ^ 2 + E1 / 2 * (eps - v) ^ 2

def dissipationRate (eta vdot : ℝ) : ℝ := eta * vdot ^ 2

def storageRate (E0 E1 eps v epsdot vdot : ℝ) : ℝ :=
  E0 * eps * epsdot + E1 * (eps - v) * (epsdot - vdot)

def viscousStrain (eps v0 E1 eta t : ℝ) : ℝ :=
  eps + (v0 - eps) * Real.exp (-E1 * t / eta)

theorem storage_nonnegative (E0 E1 eps v : ℝ) (h0 : 0 ≤ E0) (h1 : 0 ≤ E1) :
    0 ≤ storage E0 E1 eps v := by
  exact add_nonneg
    (mul_nonneg (div_nonneg h0 (by norm_num)) (sq_nonneg eps))
    (mul_nonneg (div_nonneg h1 (by norm_num)) (sq_nonneg (eps - v)))

theorem dissipation_nonnegative (eta vdot : ℝ) (heta : 0 ≤ eta) :
    0 ≤ dissipationRate eta vdot :=
  mul_nonneg heta (sq_nonneg vdot)

theorem storage_hasDerivAt (E0 E1 t epsdot vdot : ℝ) (eps v : ℝ → ℝ)
    (heps : HasDerivAt eps epsdot t) (hv : HasDerivAt v vdot t) :
    HasDerivAt (fun s => storage E0 E1 (eps s) (v s))
      (storageRate E0 E1 (eps t) (v t) epsdot vdot) t := by
  have hd := ((heps.mul heps).const_mul (E0 / 2)).add
    (((heps.sub hv).mul (heps.sub hv)).const_mul (E1 / 2))
  convert hd using 1 <;> simp only [storage, storageRate, pow_two]
  ring

theorem local_power_balance (E0 E1 eps v eta epsdot vdot : ℝ)
    (hMaxwell : eta * vdot = E1 * (eps - v)) :
    stress E0 E1 eps v * epsdot =
      storageRate E0 E1 eps v epsdot vdot + dissipationRate eta vdot := by
  calc
    stress E0 E1 eps v * epsdot =
        storageRate E0 E1 eps v epsdot vdot + (E1 * (eps - v)) * vdot := by
      dsimp [stress, storageRate]
      ring
    _ = storageRate E0 E1 eps v epsdot vdot + dissipationRate eta vdot := by
      rw [← hMaxwell]
      dsimp [dissipationRate]
      ring

theorem zero_branch_recovers_elastic (E0 eps v : ℝ) :
    stress E0 0 eps v = E0 * eps ∧ storage E0 0 eps v = E0 / 2 * eps ^ 2 := by
  simp [stress, storage]

theorem viscous_strain_hasDerivAt (eps v0 E1 eta t : ℝ) (heta : eta ≠ 0) :
    HasDerivAt (fun s => viscousStrain eps v0 E1 eta s)
      (E1 * (eps - viscousStrain eps v0 E1 eta t) / eta) t := by
  have hd := (((hasDerivAt_id t).const_mul (-E1)).div_const eta).exp
  have hd' := (hd.const_mul (v0 - eps)).const_add eps
  convert hd' using 1
  simp only [viscousStrain, id_eq]
  field_simp [heta]
  ring

theorem viscous_strain_bounded (eps v0 E1 eta t : ℝ)
    (hE : 0 ≤ E1) (heta : 0 < eta) (ht : 0 ≤ t) :
    min v0 eps ≤ viscousStrain eps v0 E1 eta t ∧
      viscousStrain eps v0 E1 eta t ≤ max v0 eps := by
  have hr0 := Real.exp_nonneg (-E1 * t / eta)
  have hr1 : Real.exp (-E1 * t / eta) ≤ 1 :=
    Real.exp_le_one_iff.mpr (div_nonpos_of_nonpos_of_nonneg
      (mul_nonpos_of_nonpos_of_nonneg (neg_nonpos.mpr hE) ht) heta.le)
  have hleft := mul_le_mul_of_nonneg_left (min_le_right v0 eps) (sub_nonneg.mpr hr1)
  have hright := mul_le_mul_of_nonneg_left (min_le_left v0 eps) hr0
  have hupperLeft := mul_le_mul_of_nonneg_left (le_max_right v0 eps) (sub_nonneg.mpr hr1)
  have hupperRight := mul_le_mul_of_nonneg_left (le_max_left v0 eps) hr0
  dsimp [viscousStrain]
  constructor <;> nlinarith

theorem viscous_strain_monotone (eps v0 E1 eta : ℝ)
    (hE : 0 ≤ E1) (heta : 0 < eta) (hstart : v0 ≤ eps) :
    Monotone (fun t => viscousStrain eps v0 E1 eta t) := by
  intro s t hst
  have hexp := Real.exp_le_exp_of_le (div_le_div_of_nonneg_right
    (mul_le_mul_of_nonpos_left hst (neg_nonpos.mpr hE)) heta.le)
  have hweight := mul_le_mul_of_nonpos_left hexp (sub_nonpos.mpr hstart)
  exact add_le_add_left hweight eps

theorem viscous_strain_antitone (eps v0 E1 eta : ℝ)
    (hE : 0 ≤ E1) (heta : 0 < eta) (hstart : eps ≤ v0) :
    Antitone (fun t => viscousStrain eps v0 E1 eta t) := by
  intro s t hst
  have hexp := Real.exp_le_exp_of_le (div_le_div_of_nonneg_right
    (mul_le_mul_of_nonpos_left hst (neg_nonpos.mpr hE)) heta.le)
  have hweight := mul_le_mul_of_nonneg_left hexp (sub_nonneg.mpr hstart)
  exact add_le_add_left hweight eps

theorem held_stress_bounded (E0 E1 eps v0 eta t : ℝ)
    (hE : 0 ≤ E1) (heta : 0 < eta) (ht : 0 ≤ t) (hstart : v0 ≤ eps) :
    E0 * eps ≤ stress E0 E1 eps (viscousStrain eps v0 E1 eta t) ∧
      stress E0 E1 eps (viscousStrain eps v0 E1 eta t) ≤ stress E0 E1 eps v0 := by
  have hb := viscous_strain_bounded eps v0 E1 eta t hE heta ht
  rw [min_eq_left hstart, max_eq_right hstart] at hb
  have hlow := mul_nonneg hE (sub_nonneg.mpr hb.2)
  have hhigh := mul_le_mul_of_nonneg_left (sub_le_sub_left hb.1 eps) hE
  dsimp [stress]
  constructor <;> linarith

theorem held_stress_antitone (E0 E1 eps v0 eta : ℝ)
    (hE : 0 ≤ E1) (heta : 0 < eta) (hstart : v0 ≤ eps) :
    Antitone (fun t => stress E0 E1 eps (viscousStrain eps v0 E1 eta t)) := by
  intro s t hst
  have hv := viscous_strain_monotone eps v0 E1 eta hE heta hstart hst
  have hspring := mul_le_mul_of_nonneg_left (sub_le_sub_left hv eps) hE
  exact add_le_add_left hspring (E0 * eps)

end Kenoma.DissipativeBarReal

#print axioms Kenoma.DissipativeBarReal.storage_nonnegative
#print axioms Kenoma.DissipativeBarReal.dissipation_nonnegative
#print axioms Kenoma.DissipativeBarReal.storage_hasDerivAt
#print axioms Kenoma.DissipativeBarReal.local_power_balance
#print axioms Kenoma.DissipativeBarReal.zero_branch_recovers_elastic
#print axioms Kenoma.DissipativeBarReal.viscous_strain_hasDerivAt
#print axioms Kenoma.DissipativeBarReal.viscous_strain_bounded
#print axioms Kenoma.DissipativeBarReal.viscous_strain_monotone
#print axioms Kenoma.DissipativeBarReal.viscous_strain_antitone
#print axioms Kenoma.DissipativeBarReal.held_stress_bounded
#print axioms Kenoma.DissipativeBarReal.held_stress_antitone
