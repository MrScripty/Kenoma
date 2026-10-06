import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Data.Real.Sqrt
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
Real constitutive functions shared by the rigid and compliant teaching actuators.
The definitions match the mathematical expressions in web/elbow.mjs and
web/series.mjs. These results do not prove JavaScript floating-point refinement,
solver termination, finite-precision root residuals, or biological calibration.

The slope estimate below is the F0*sqrt(2/e)/(w*l0) coefficient used by the
JavaScript domain guard, with e represented by the exact real exponential of 1.
-/
noncomputable section
namespace Kenoma.ActuatorReal

def activation (a u h tau : ℝ) : ℝ :=
  u + (a - u) * Real.exp (-h / tau)

def normalizedFiber (fiber optimalFiber width : ℝ) : ℝ :=
  (fiber / optimalFiber - 1) / width

def activeForce (fiber a maxForce optimalFiber width : ℝ) : ℝ :=
  a * maxForce * Real.exp (-(normalizedFiber fiber optimalFiber width) ^ 2)

def activeSlope (fiber a maxForce optimalFiber width : ℝ) : ℝ :=
  -2 * normalizedFiber fiber optimalFiber width / (width * optimalFiber) *
    activeForce fiber a maxForce optimalFiber width

def seriesResidual (fiber a maxForce optimalFiber width compliance passiveK totalFiber : ℝ) : ℝ :=
  fiber + compliance *
    (activeForce fiber a maxForce optimalFiber width +
      passiveK * max 0 (fiber - optimalFiber)) - totalFiber

theorem activation_in_unit_interval (a u h tau : ℝ)
    (ha0 : 0 ≤ a) (ha1 : a ≤ 1) (hu0 : 0 ≤ u) (hu1 : u ≤ 1)
    (hh : 0 ≤ h) (htau : 0 < tau) :
    0 ≤ activation a u h tau ∧ activation a u h tau ≤ 1 := by
  have hr0 := Real.exp_nonneg (-h / tau)
  have hr1 : Real.exp (-h / tau) ≤ 1 :=
    Real.exp_le_one_iff.mpr (div_nonpos_of_nonpos_of_nonneg (neg_nonpos.mpr hh) htau.le)
  have hleft := mul_nonneg (sub_nonneg.mpr hr1) hu0
  have hright := mul_nonneg hr0 ha0
  have hupperLeft := mul_le_mul_of_nonneg_left hu1 (sub_nonneg.mpr hr1)
  have hupperRight := mul_le_mul_of_nonneg_left ha1 hr0
  dsimp [activation]
  constructor <;> nlinarith

theorem activation_hasDerivAt (a u h tau : ℝ) (htau : tau ≠ 0) :
    HasDerivAt (fun t => activation a u t tau)
      ((u - activation a u h tau) / tau) h := by
  have hd := ((((hasDerivAt_id h).neg).div_const tau).exp).const_mul (a - u)
  have hd' := hd.const_add u
  convert hd' using 1 <;> simp only [activation, id_eq] <;> field_simp [htau]

theorem active_force_bounds (fiber a maxForce optimalFiber width : ℝ)
    (ha : 0 ≤ a) (hF : 0 ≤ maxForce) :
    0 ≤ activeForce fiber a maxForce optimalFiber width ∧
    activeForce fiber a maxForce optimalFiber width ≤ a * maxForce := by
  have hweight := Real.exp_le_one_iff.mpr
    (neg_nonpos.mpr (sq_nonneg (normalizedFiber fiber optimalFiber width)))
  constructor
  · exact mul_nonneg (mul_nonneg ha hF) (Real.exp_nonneg _)
  · exact (mul_le_mul_of_nonneg_left hweight (mul_nonneg ha hF)).trans_eq (mul_one _)

theorem active_force_hasDerivAt (fiber a maxForce optimalFiber width : ℝ)
    (hl : optimalFiber ≠ 0) (hw : width ≠ 0) :
    HasDerivAt (fun f => activeForce f a maxForce optimalFiber width)
      (activeSlope fiber a maxForce optimalFiber width) fiber := by
  have hz := (((hasDerivAt_id fiber).div_const optimalFiber).sub_const 1).div_const width
  have hd := (((hz.mul hz).neg).exp).const_mul (a * maxForce)
  convert hd using 1 <;>
    simp only [activeSlope, activeForce, normalizedFiber, id_eq, pow_two] <;>
    field_simp [hl, hw] <;> ring

theorem gaussian_weighted_radius_bound (z : ℝ) :
    2 * |z| * Real.exp (-(z ^ 2)) ≤ Real.sqrt (2 / Real.exp 1) := by
  have he : 2 * z ^ 2 ≤ Real.exp (2 * z ^ 2 - 1) := by
    linarith [Real.add_one_le_exp (2 * z ^ 2 - 1)]
  have hexpSquare : Real.exp (-(z ^ 2)) ^ 2 = Real.exp (-2 * z ^ 2) := by
    rw [pow_two, ← Real.exp_add]
    congr 1
    ring
  apply Real.le_sqrt_of_sq_le
  calc
    (2 * |z| * Real.exp (-(z ^ 2))) ^ 2 = 4 * z ^ 2 * Real.exp (-2 * z ^ 2) := by
      rw [mul_pow, mul_pow, sq_abs, hexpSquare]
      ring
    _ = (2 * z ^ 2) * (2 * Real.exp (-2 * z ^ 2)) := by ring
    _ ≤ Real.exp (2 * z ^ 2 - 1) * (2 * Real.exp (-2 * z ^ 2)) :=
      mul_le_mul_of_nonneg_right he (mul_nonneg (by norm_num) (Real.exp_nonneg _))
    _ = 2 * Real.exp (-1) := by
      rw [mul_comm (Real.exp (2 * z ^ 2 - 1)), mul_assoc, ← Real.exp_add]
      congr 2
      ring
    _ = 2 / Real.exp 1 := by rw [Real.exp_neg, div_eq_mul_inv]

theorem active_slope_bound (fiber a maxForce optimalFiber width : ℝ)
    (ha0 : 0 ≤ a) (ha1 : a ≤ 1) (hF : 0 ≤ maxForce)
    (hl : 0 < optimalFiber) (hw : 0 < width) :
    |activeSlope fiber a maxForce optimalFiber width| ≤
      maxForce * Real.sqrt (2 / Real.exp 1) / (width * optimalFiber) := by
  have hden : 0 < width * optimalFiber := mul_pos hw hl
  have hcoef : 0 ≤ a * maxForce / (width * optimalFiber) :=
    div_nonneg (mul_nonneg ha0 hF) hden.le
  calc
    |activeSlope fiber a maxForce optimalFiber width| =
        (2 * |normalizedFiber fiber optimalFiber width| *
          Real.exp (-(normalizedFiber fiber optimalFiber width) ^ 2)) *
          (a * maxForce / (width * optimalFiber)) := by
      simp only [activeSlope, activeForce, abs_mul, abs_div,
        abs_of_nonneg ha0, abs_of_nonneg hF, abs_of_pos hden,
        abs_of_pos (Real.exp_pos _)]
      norm_num
      ring
    _ ≤ Real.sqrt (2 / Real.exp 1) * (a * maxForce / (width * optimalFiber)) :=
      mul_le_mul_of_nonneg_right (gaussian_weighted_radius_bound _) hcoef
    _ ≤ Real.sqrt (2 / Real.exp 1) * (maxForce / (width * optimalFiber)) :=
      mul_le_mul_of_nonneg_left (div_le_div_of_nonneg_right
        ((mul_le_mul_of_nonneg_right ha1 hF).trans_eq (one_mul _)) hden.le) (Real.sqrt_nonneg _)
    _ = maxForce * Real.sqrt (2 / Real.exp 1) / (width * optimalFiber) := by ring

theorem series_residual_strictMono (a maxForce optimalFiber width compliance passiveK totalFiber : ℝ)
    (ha0 : 0 ≤ a) (ha1 : a ≤ 1) (hF : 0 ≤ maxForce)
    (hl : 0 < optimalFiber) (hw : 0 < width)
    (hc : 0 ≤ compliance) (hk : 0 ≤ passiveK)
    (hbound : compliance * (maxForce * Real.sqrt (2 / Real.exp 1) / (width * optimalFiber)) < 1) :
    StrictMono (fun f => seriesResidual f a maxForce optimalFiber width compliance passiveK totalFiber) := by
  have hcore : StrictMono (fun f => f + compliance * activeForce f a maxForce optimalFiber width) := by
    apply strictMono_of_hasDerivAt_pos
      (fun f => (hasDerivAt_id f).add
        ((active_force_hasDerivAt f a maxForce optimalFiber width hl.ne' hw.ne').const_mul compliance))
    intro f
    have hs := (abs_le.mp (active_slope_bound f a maxForce optimalFiber width ha0 ha1 hF hl hw)).1
    have hcs := mul_le_mul_of_nonneg_left hs hc
    nlinarith
  intro x y hxy
  have hstrict := hcore hxy
  have hpassive := mul_le_mul_of_nonneg_left
    (max_le_max (le_refl (0 : ℝ)) (sub_le_sub_right hxy.le optimalFiber)) (mul_nonneg hc hk)
  convert (sub_lt_sub_right (add_lt_add_of_lt_of_le hstrict hpassive) totalFiber) using 1 <;>
    dsimp [seriesResidual] <;> ring

theorem series_equilibrium_unique (a maxForce optimalFiber width compliance passiveK totalFiber x y : ℝ)
    (ha0 : 0 ≤ a) (ha1 : a ≤ 1) (hF : 0 ≤ maxForce)
    (hl : 0 < optimalFiber) (hw : 0 < width)
    (hc : 0 ≤ compliance) (hk : 0 ≤ passiveK)
    (hbound : compliance * (maxForce * Real.sqrt (2 / Real.exp 1) / (width * optimalFiber)) < 1)
    (hx : seriesResidual x a maxForce optimalFiber width compliance passiveK totalFiber = 0)
    (hy : seriesResidual y a maxForce optimalFiber width compliance passiveK totalFiber = 0) : x = y := by
  exact (series_residual_strictMono a maxForce optimalFiber width compliance passiveK totalFiber
    ha0 ha1 hF hl hw hc hk hbound).injective (hx.trans hy.symm)

end Kenoma.ActuatorReal

#print axioms Kenoma.ActuatorReal.activation_in_unit_interval
#print axioms Kenoma.ActuatorReal.activation_hasDerivAt
#print axioms Kenoma.ActuatorReal.active_force_bounds
#print axioms Kenoma.ActuatorReal.active_force_hasDerivAt
#print axioms Kenoma.ActuatorReal.gaussian_weighted_radius_bound
#print axioms Kenoma.ActuatorReal.active_slope_bound
#print axioms Kenoma.ActuatorReal.series_residual_strictMono
#print axioms Kenoma.ActuatorReal.series_equilibrium_unique
