import Mathlib.Data.Real.Sqrt

/-!
Real force/torque and power algebra, separate from the preserved Int cards.
Geometric differentiation, exponential activation, continuous work balance and
implementation refinement are not established by these polynomial identities.
This proposed source must compile before any checked claim is displayed.
-/
namespace Kenoma.MechanicsReal

def torque (rx ry fx fy : ℝ) : ℝ := rx * fy - ry * fx

theorem force_pair_cancels (force : ℝ) : force + (-force) = 0 := by
  exact add_neg_cancel force

theorem torque_linear (rx ry fx fy gx gy : ℝ) :
    torque rx ry (fx + gx) (fy + gy) =
      torque rx ry fx fy + torque rx ry gx gy := by
  unfold torque
  rw [mul_add, mul_add]
  exact (sub_add_sub_comm _ _ _ _).symm

-- The force moment/path-rate association is assumed separately, not derived.
theorem virtual_power_identity (force pathDerivative angularVelocity : ℝ) :
    ((-force) * pathDerivative) * angularVelocity =
      (-force) * (pathDerivative * angularVelocity) := by
  exact mul_assoc _ _ _

end Kenoma.MechanicsReal

#print axioms Kenoma.MechanicsReal.force_pair_cancels
#print axioms Kenoma.MechanicsReal.torque_linear
#print axioms Kenoma.MechanicsReal.virtual_power_identity
