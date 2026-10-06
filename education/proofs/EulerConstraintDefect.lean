import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Local real algebra for the actual lower scalar source surface, using exact
rationals: FT=100*f(s), e=(r-FT)/100, H=.01-(ub+.4*e+I),
s=(L0-y-.1*q)/.2, ydot=w, qdot=10*v, Idot=-2*slope*(w+v).
The slope is a supplied real scalar; no derivative or C2 kernel fact is proved.
The quadratic tendon specialization is an example, not the OpenSim curve.
No numerical integration, policy admissibility, convergence or anatomy theorem.
-/
namespace KenomaEuler
noncomputable section

def error (f : ℝ → ℝ) (r s : ℝ) : ℝ := (r - 100 * f s) / 100
def surface (f : ℝ → ℝ) (r ub s I : ℝ) : ℝ :=
  (1 / 100) - (ub + (2 / 5) * error f r s + I)
def tendonLength (L0 y q : ℝ) : ℝ := (L0 - y - (1 / 10) * q) / (1 / 5)
def normalRate (slope sdot Idot : ℝ) : ℝ := (2 / 5) * slope * sdot - Idot
def quadraticTendon (A D E s : ℝ) : ℝ := A * s ^ 2 + D * s + E

theorem normalized_error (f : ℝ → ℝ) (r s : ℝ) :
    error f r s = r / 100 - f s := by
  unfold error
  ring

theorem source_tendon_euler_increment (L0 y q w v τ : ℝ) :
    tendonLength L0 (y + τ * w) (q + τ * (10 * v)) =
      tendonLength L0 y q + τ * (-5 * (w + v)) := by
  unfold tendonLength
  ring

theorem tangent_normal_cancellation (slope sdot : ℝ) :
    normalRate slope sdot ((2 / 5) * slope * sdot) = 0 := by
  unfold normalRate
  ring

theorem euler_constraint_defect_identity (f : ℝ → ℝ) (r ub s I slope sdot τ : ℝ) :
    surface f r ub (s + τ * sdot) (I + τ * ((2 / 5) * slope * sdot)) -
      surface f r ub s I =
    (2 / 5) * (f (s + τ * sdot) - f s - slope * (τ * sdot)) := by
  unfold surface error
  ring

theorem source_euler_constraint_defect (f : ℝ → ℝ) (r ub L0 y q I slope w v τ : ℝ) :
    surface f r ub (tendonLength L0 (y + τ * w) (q + τ * (10 * v)))
      (I - τ * (2 * slope * (w + v))) -
      surface f r ub (tendonLength L0 y q) I =
    (2 / 5) * (f (tendonLength L0 y q + τ * (-5 * (w + v))) -
      f (tendonLength L0 y q) - slope * (τ * (-5 * (w + v)))) := by
  rw [source_tendon_euler_increment]
  have hI : I - τ * (2 * slope * (w + v)) =
      I + τ * ((2 / 5) * slope * (-5 * (w + v))) := by ring
  rw [hI]
  exact euler_constraint_defect_identity f r ub (tendonLength L0 y q) I slope
    (-5 * (w + v)) τ

theorem on_surface_euler_defect (f : ℝ → ℝ) (r ub s I slope sdot τ : ℝ)
    (hentry : surface f r ub s I = 0) :
    surface f r ub (s + τ * sdot) (I + τ * ((2 / 5) * slope * sdot)) =
      (2 / 5) * (f (s + τ * sdot) - f s - slope * (τ * sdot)) := by
  have h := euler_constraint_defect_identity f r ub s I slope sdot τ
  simpa only [hentry, sub_zero] using h

theorem defect_bound_from_remainder (f : ℝ → ℝ) (r ub s I slope sdot τ M : ℝ)
    (hremainder : |f (s + τ * sdot) - f s - slope * (τ * sdot)| ≤
      (M / 2) * (τ * sdot) ^ 2) :
    |surface f r ub (s + τ * sdot) (I + τ * ((2 / 5) * slope * sdot)) -
      surface f r ub s I| ≤ (M / 5) * τ ^ 2 * sdot ^ 2 := by
  rw [euler_constraint_defect_identity, abs_mul]
  norm_num only [abs_of_pos (by norm_num : (0 : ℝ) < 2 / 5)]
  calc
    (2 / 5) * |f (s + τ * sdot) - f s - slope * (τ * sdot)| ≤
        (2 / 5) * ((M / 2) * (τ * sdot) ^ 2) := by
      exact mul_le_mul_of_nonneg_left hremainder (by norm_num)
    _ = (M / 5) * τ ^ 2 * sdot ^ 2 := by ring

theorem quadratic_tendon_remainder (A D E s δ : ℝ) :
    quadraticTendon A D E (s + δ) - quadraticTendon A D E s -
      (2 * A * s + D) * δ = A * δ ^ 2 := by
  unfold quadraticTendon
  ring

theorem quadratic_euler_constraint_defect (A D E r ub s I sdot τ : ℝ) :
    surface (quadraticTendon A D E) r ub (s + τ * sdot)
      (I + τ * ((2 / 5) * (2 * A * s + D) * sdot)) -
      surface (quadraticTendon A D E) r ub s I =
      (2 / 5) * A * τ ^ 2 * sdot ^ 2 := by
  rw [euler_constraint_defect_identity, quadratic_tendon_remainder]
  ring

theorem tangent_quadratic_predictor_can_leave_surface (A D E r ub s I sdot τ : ℝ)
    (hA : 0 < A) (hτ : τ ≠ 0) (hsdot : sdot ≠ 0)
    (hentry : surface (quadraticTendon A D E) r ub s I = 0) :
    normalRate (2 * A * s + D) sdot ((2 / 5) * (2 * A * s + D) * sdot) = 0 ∧
      0 < surface (quadraticTendon A D E) r ub (s + τ * sdot)
        (I + τ * ((2 / 5) * (2 * A * s + D) * sdot)) := by
  constructor
  · exact tangent_normal_cancellation (2 * A * s + D) sdot
  · have h := quadratic_euler_constraint_defect A D E r ub s I sdot τ
    rw [hentry, sub_zero] at h
    rw [h]
    have hτsq : 0 < τ ^ 2 := sq_pos_of_ne_zero hτ
    have hssq : 0 < sdot ^ 2 := sq_pos_of_ne_zero hsdot
    exact mul_pos (mul_pos (mul_pos (by norm_num) hA) hτsq) hssq

end
end KenomaEuler

#print axioms KenomaEuler.normalized_error
#print axioms KenomaEuler.source_tendon_euler_increment
#print axioms KenomaEuler.tangent_normal_cancellation
#print axioms KenomaEuler.euler_constraint_defect_identity
#print axioms KenomaEuler.source_euler_constraint_defect
#print axioms KenomaEuler.on_surface_euler_defect
#print axioms KenomaEuler.defect_bound_from_remainder
#print axioms KenomaEuler.quadratic_tendon_remainder
#print axioms KenomaEuler.quadratic_euler_constraint_defect
#print axioms KenomaEuler.tangent_quadratic_predictor_can_leave_surface
