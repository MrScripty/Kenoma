import Std

/- Exact numerator algebra for the atlas-frame arm. Stationarity and compatible
   scales are assumptions. This file certifies no floating-point mechanics,
   anatomical architecture, tissue calibration or biological prediction. -/
namespace Kenoma.Arm

-- The atlas world has +Z superior, hence V = +m*g*z.
theorem upward_mass_event_work_numerator
    (oldInertia deltaMass radiusSquared velocity g z : Int) :
    (oldInertia+deltaMass*radiusSquared)*velocity*velocity -
      oldInertia*velocity*velocity + 2*g*z*deltaMass =
      deltaMass*(radiusSquared*velocity*velocity+2*g*z) := by
  simp only [Int.add_mul, Int.mul_add, Int.mul_assoc]
  have commute : deltaMass*(2*(g*z)) = 2*(g*(z*deltaMass)) := by ac_rfl
  rw [commute]
  omega

-- One shared guide component after interpolation: two head contributions,
-- the common distal apparatus, weak matrix and contact. Repeat for each component.
theorem shared_guide_force_balance
    (headA headB distal matrix contact : Int)
    (equilibrium : headA+headB+distal+matrix+contact=0) :
    distal = -(headA+headB+matrix+contact) := by
  omega

end Kenoma.Arm
#print axioms Kenoma.Arm.upward_mass_event_work_numerator
#print axioms Kenoma.Arm.shared_guide_force_balance
