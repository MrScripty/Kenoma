import Std

/- Exact scaled integer algebra for a three-coordinate, one-DOF transfer.
   Positive common scales are assumed. Geometry, derivatives, browser arithmetic,
   material behavior and biological correctness require separate evidence. -/
namespace Kenoma.Anatomical

def dot3 (a0 a1 a2 b0 b1 b2 : Int) : Int := a0*b0+a1*b1+a2*b2

-- The implemented attachment has velocity B * omega and torque dot(B, force).
theorem attachment_transpose_power (b0 b1 b2 f0 f1 f2 omega : Int) :
    dot3 b0 b1 b2 f0 f1 f2 * omega =
      dot3 f0 f1 f2 (b0*omega) (b1*omega) (b2*omega) := by
  simp only [dot3, Int.add_mul, Int.mul_assoc,
    Int.mul_left_comm b0 f0, Int.mul_left_comm b1 f1, Int.mul_left_comm b2 f2]

-- If dU/dt = force dot (nodeVelocity - B*omega), transferred forces cancel it.
theorem paired_attachment_work (b0 b1 b2 f0 f1 f2 v0 v1 v2 omega : Int) :
    dot3 (-f0) (-f1) (-f2) v0 v1 v2 +
      dot3 b0 b1 b2 f0 f1 f2 * omega +
      dot3 f0 f1 f2 (v0-b0*omega) (v1-b1*omega) (v2-b2*omega) = 0 := by
  simp only [dot3, Int.neg_mul, Int.mul_sub, Int.add_mul, Int.mul_assoc,
    Int.mul_left_comm b0 f0, Int.mul_left_comm b1 f1, Int.mul_left_comm b2 f2]
  omega

end Kenoma.Anatomical
#print axioms Kenoma.Anatomical.attachment_transpose_power
#print axioms Kenoma.Anatomical.paired_attachment_work
