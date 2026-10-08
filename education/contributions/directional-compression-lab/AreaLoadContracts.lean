import Std

namespace Kenoma.Directional

-- Conditional product algebra. No real constitutive or numerical theorem.
variable {A : Type} (mul : A → A → A)

theorem force_area_work
    (assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c))
    (pressure area displacement : A) :
    mul (mul pressure area) displacement =
      mul pressure (mul area displacement) := by
  exact assoc pressure area displacement

theorem constant_pressure_area_cross
    (assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c))
    (comm : ∀ a b, mul a b = mul b a)
    (pressure area1 area2 : A) :
    mul (mul pressure area1) area2 =
      mul (mul pressure area2) area1 := by
  rw [assoc, comm area1 area2, ← assoc]

theorem transverse_volume_permutation
    (comm : ∀ a b, mul a b = mul b a)
    (axial transverse1 transverse2 : A) :
    mul axial (mul transverse1 transverse2) =
      mul axial (mul transverse2 transverse1) := by
  rw [comm transverse1 transverse2]

end Kenoma.Directional

#print axioms Kenoma.Directional.force_area_work
#print axioms Kenoma.Directional.constant_pressure_area_cross
#print axioms Kenoma.Directional.transverse_volume_permutation
