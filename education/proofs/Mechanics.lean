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

end Kenoma

#print axioms Kenoma.force_pair_cancels
#print axioms Kenoma.torque_linear
#print axioms Kenoma.torque_origin_shift
#print axioms Kenoma.central_pair_torque
#print axioms Kenoma.kinetic_numerator_nonnegative
#print axioms Kenoma.torque_worked_example
