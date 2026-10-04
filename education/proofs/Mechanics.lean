import Std

/-!
Exact integer-coordinate identities. Interpret coordinates with fixed, positive
SI scale factors; no floating-point or biological correctness is claimed.
Only Lean's bundled standard library is required.
-/
namespace Kenoma

def torque (rx ry fx fy : Int) : Int := rx * fy - ry * fx

theorem force_pair_cancels (f : Int) : f + (-f) = 0 := by omega

theorem torque_linear (rx ry fx fy gx gy : Int) :
    torque rx ry (fx + gx) (fy + gy) =
      torque rx ry fx fy + torque rx ry gx gy := by
  simp only [torque, Int.mul_add]
  omega

theorem torque_origin_shift (rx ry ox oy fx fy : Int) :
    torque (rx - ox) (ry - oy) fx fy =
      torque rx ry fx fy - torque ox oy fx fy := by
  simp only [torque, Int.sub_mul]
  omega

theorem central_pair_torque (ax ay bx byy k : Int) :
    torque ax ay (k * (bx - ax)) (k * (byy - ay)) +
      torque bx byy (-(k * (bx - ax))) (-(k * (byy - ay))) = 0 := by
  simp only [torque, Int.mul_sub, Int.mul_neg, Int.mul_assoc]
  simp only [Int.mul_left_comm ax k, Int.mul_left_comm ay k,
    Int.mul_left_comm bx k, Int.mul_left_comm byy k,
    Int.mul_comm ax byy, Int.mul_comm ay bx, Int.mul_comm bx byy, Int.mul_comm ax ay]
  omega

def twiceKinetic (m vx vy : Int) : Int := m * (vx * vx + vy * vy)

theorem kinetic_numerator_nonnegative (m vx vy : Int) (hm : 0 ≤ m) :
    0 ≤ twiceKinetic m vx vy := by
  have square (v : Int) : 0 ≤ v * v := by
    rw [← Int.natAbs_mul_self' v]
    exact Int.ofNat_zero_le _
  exact Int.mul_nonneg hm (Int.add_nonneg (square vx) (square vy))

-- Exact scaled worked example: r=(300,0) mm, F=(0,-49050) mN.
-- Product scale is 10^-6 N m; result is -14.715 N m.
theorem torque_worked_example : torque 300 0 0 (-49050) = -14715000 := by decide

-- The weights are integers. This is a convex-combination numerator contract,
-- not a theorem about exp(), the RK4 code, or a physiological activation law.
theorem activation_weighted_bound (a u w d scale : Int)
    (ha0 : 0 ≤ a) (hau : a ≤ scale) (hu0 : 0 ≤ u) (huu : u ≤ scale)
    (hw : 0 ≤ w) (hwd : w ≤ d) :
    0 ≤ a * w + u * (d - w) ∧ a * w + u * (d - w) ≤ scale * d := by
  have hdw : 0 ≤ d - w := by omega
  constructor
  · exact Int.add_nonneg (Int.mul_nonneg ha0 hw) (Int.mul_nonneg hu0 hdw)
  · calc
      a * w + u * (d - w) ≤ scale * w + scale * (d - w) :=
        Int.add_le_add (Int.mul_le_mul_of_nonneg_right hau hw)
          (Int.mul_le_mul_of_nonneg_right huu hdw)
      _ = scale * d := by simp only [Int.mul_sub]; omega

theorem virtual_power_identity (force dl omega : Int) :
    (-force * dl) * omega = -(force * (dl * omega)) := by
  simp only [Int.neg_mul, Int.mul_assoc]

-- A volume element uses g0 = -(g1+g2+g3), coordinate by coordinate.
-- The derivative formula itself is tested numerically, not proved here.
theorem element_gradient_resultant (g1 g2 g3 scale : Int) :
    scale * (-(g1 + g2 + g3)) + scale * g1 + scale * g2 + scale * g3 = 0 := by
  simp only [Int.mul_neg, Int.mul_add]
  omega

-- The actual centroid-contact distribution uses four equal barycentric weights.
-- This numerator identity supports the motion/force transpose contract.
theorem centroid_contact_power (force v0 v1 v2 v3 : Int) :
    force * (v0 + v1 + v2 + v3) =
      force * v0 + force * v1 + force * v2 + force * v3 := by
  simp only [Int.mul_add]

-- A regularized scalar constraint denominator is positive under these inputs.
-- h^2 scaling and the construction of the real gradients remain assumptions.
theorem compliant_denominator_positive (w g alpha : Int)
    (hw : 0 ≤ w) (ha : 0 < alpha) : 0 < w * (g * g) + alpha := by
  have square : 0 ≤ g * g := by
    rw [← Int.natAbs_mul_self' g]
    exact Int.ofNat_zero_le _
  have term := Int.mul_nonneg hw square
  omega

-- Scaled Armijo sufficient decrease, with nonnegative step coefficient.
-- This checks the acceptance contract, not L-BFGS or nonconvex convergence.
theorem accepted_energy_nonincrease (oldE newE coefficient slope : Int)
    (hc : 0 ≤ coefficient) (hs : slope ≤ 0)
    (accept : newE ≤ oldE + coefficient * slope) : newE ≤ oldE := by
  have product : coefficient * slope ≤ 0 := by
    have positive := Int.mul_nonneg hc (show 0 ≤ -slope by omega)
    simp only [Int.mul_neg] at positive
    omega
  omega

end Kenoma

#print axioms Kenoma.force_pair_cancels
#print axioms Kenoma.torque_linear
#print axioms Kenoma.torque_origin_shift
#print axioms Kenoma.central_pair_torque
#print axioms Kenoma.kinetic_numerator_nonnegative
#print axioms Kenoma.torque_worked_example
#print axioms Kenoma.activation_weighted_bound
#print axioms Kenoma.virtual_power_identity

#print axioms Kenoma.element_gradient_resultant
#print axioms Kenoma.centroid_contact_power
#print axioms Kenoma.compliant_denominator_positive
#print axioms Kenoma.accepted_energy_nonincrease
