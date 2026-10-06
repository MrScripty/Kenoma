import Std

/- Exact integer numerators for the implemented implicit joint step and controls.
   Compatible positive scales, force mappings and stationarity are supplied.
   These declarations establish no floating-point, anatomical or biological claim. -/
namespace Kenoma.Coupled

theorem impulse_balance (inertia oldVelocity newVelocity h tissue gravity damping : Int)
    (stationary : inertia * (newVelocity-oldVelocity) =
      h * (tissue+gravity-damping*newVelocity)) :
    inertia * (newVelocity-oldVelocity) + h*damping*newVelocity =
      h*tissue+h*gravity := by
  simp only [Int.mul_add, Int.mul_sub, Int.mul_assoc] at stationary ⊢
  omega

theorem kinetic_increment_identity (inertia oldVelocity newVelocity : Int) :
    inertia*(newVelocity*newVelocity-oldVelocity*oldVelocity) +
      inertia*(newVelocity-oldVelocity)*(newVelocity-oldVelocity) =
      2*(inertia*(newVelocity-oldVelocity)*newVelocity) := by
  simp only [Int.mul_sub, Int.sub_mul, Int.mul_assoc,
    Int.mul_comm oldVelocity newVelocity]
  omega

theorem implicit_kinetic_work_balance
    (inertia oldVelocity newVelocity h tissue gravity damping : Int)
    (stationary : inertia*(newVelocity-oldVelocity) =
      h*(tissue+gravity-damping*newVelocity)) :
    inertia*(newVelocity*newVelocity-oldVelocity*oldVelocity) +
      inertia*(newVelocity-oldVelocity)*(newVelocity-oldVelocity) =
      2*h*tissue*newVelocity + 2*h*gravity*newVelocity -
      2*h*damping*newVelocity*newVelocity := by
  rw [kinetic_increment_identity, stationary]
  simp only [Int.mul_add, Int.mul_sub, Int.add_mul, Int.sub_mul, Int.mul_assoc]

theorem implicit_dissipation_numerator_nonnegative
    (inertia h damping oldVelocity newVelocity : Int)
    (hi : 0 ≤ inertia) (hh : 0 ≤ h) (hd : 0 ≤ damping) :
    0 ≤ inertia*((newVelocity-oldVelocity)*(newVelocity-oldVelocity)) +
      2*h*damping*(newVelocity*newVelocity) := by
  have square (v : Int) : 0 ≤ v*v := by
    rw [← Int.natAbs_mul_self' v]
    exact Int.ofNat_zero_le _
  exact Int.add_nonneg
    (Int.mul_nonneg hi (square (newVelocity-oldVelocity)))
    (Int.mul_nonneg (Int.mul_nonneg (Int.mul_nonneg (by decide) hh) hd)
      (square newVelocity))

-- z is downward-positive in this authored block fixture, so V = -m*g*z.
theorem mass_event_work_numerator (oldInertia deltaMass radiusSquared velocity g z : Int) :
    (oldInertia+deltaMass*radiusSquared)*velocity*velocity -
      oldInertia*velocity*velocity - 2*g*z*deltaMass =
      deltaMass*(radiusSquared*velocity*velocity-2*g*z) := by
  simp only [Int.add_mul, Int.mul_sub, Int.mul_assoc]
  have commute : deltaMass*(2*(g*z)) = 2*(g*(z*deltaMass)) := by ac_rfl
  rw [commute]
  omega

theorem tendon_toe_energy_numerator_nonnegative (area length young strain : Int)
    (ha : 0 ≤ area) (hl : 0 ≤ length) (hy : 0 ≤ young) (he : 0 ≤ strain) :
    0 ≤ area*length*young*strain*strain*strain := by
  exact Int.mul_nonneg
    (Int.mul_nonneg (Int.mul_nonneg
      (Int.mul_nonneg (Int.mul_nonneg ha hl) hy) he) he) he

-- Common barycentric denominator d: corner numerators 2*l_i²-d*l_i;
-- midside numerators 4*l_i*l_j; their total is d² when sum(l_i)=d.
theorem quadratic_partition_numerator (l0 l1 l2 l3 d : Int)
    (normalized : l0+l1+l2+l3=d) :
    2*(l0*l0+l1*l1+l2*l2+l3*l3) - d*(l0+l1+l2+l3) +
      4*(l0*l1+l0*l2+l0*l3+l1*l2+l1*l3+l2*l3) = d*d := by
  rw [← normalized]
  simp only [Int.mul_add, Int.add_mul, Int.mul_comm l1 l0,
    Int.mul_comm l2 l0, Int.mul_comm l3 l0, Int.mul_comm l2 l1,
    Int.mul_comm l3 l1, Int.mul_comm l3 l2]
  omega

end Kenoma.Coupled
#print axioms Kenoma.Coupled.impulse_balance
#print axioms Kenoma.Coupled.kinetic_increment_identity
#print axioms Kenoma.Coupled.implicit_kinetic_work_balance
#print axioms Kenoma.Coupled.implicit_dissipation_numerator_nonnegative
#print axioms Kenoma.Coupled.mass_event_work_numerator
#print axioms Kenoma.Coupled.tendon_toe_energy_numerator_nonnegative
#print axioms Kenoma.Coupled.quadratic_partition_numerator
