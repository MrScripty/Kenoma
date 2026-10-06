import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Module.Pi
import Mathlib.Algebra.Module.Submodule.Defs
import Mathlib.Algebra.Module.LinearMap.Defs
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Research-only, finite-dimensional mixed log-volume algebra on `Fin n → ℝ`.
Strictly positive weights define the inner product and squared norm. A supplied
linear map P must land in Q and have residual weighted-orthogonal to Q. These are
explicit hypotheses, not a construction or verification of a numerical projector.
K is a positive scalar constant. g is abstract; sampling log J is outside this proof.
-/
noncomputable section
namespace KenomaMixedVolume

abbrev Vector (n : ℕ) := Fin n → ℝ

/-- Positive quadrature weights; zero and negative weights are excluded. -/
structure Weights (n : ℕ) where
  value : Fin n → ℝ
  positive : ∀ i, 0 < value i

variable {n : ℕ}

def Weights.inner (W : Weights n) (x y : Vector n) : ℝ :=
  ∑ i, W.value i * x i * y i

/-- Squared weighted norm, written without introducing square roots. -/
def Weights.normSq (W : Weights n) (x : Vector n) : ℝ := W.inner x x

theorem inner_comm (W : Weights n) (x y : Vector n) : W.inner x y = W.inner y x := by
  unfold Weights.inner
  apply Finset.sum_congr rfl
  intro i _
  ring

theorem inner_add_right (W : Weights n) (x y z : Vector n) :
    W.inner x (y + z) = W.inner x y + W.inner x z := by
  simp only [Weights.inner, Pi.add_apply, mul_add, Finset.sum_add_distrib]

theorem inner_add_left (W : Weights n) (x y z : Vector n) :
    W.inner (x + y) z = W.inner x z + W.inner y z := by
  rw [inner_comm, inner_add_right, inner_comm W z x, inner_comm W z y]

theorem inner_sub_right (W : Weights n) (x y z : Vector n) :
    W.inner x (y - z) = W.inner x y - W.inner x z := by
  simp only [Weights.inner, Pi.sub_apply, mul_sub, Finset.sum_sub_distrib]

theorem inner_sub_left (W : Weights n) (x y z : Vector n) :
    W.inner (x - y) z = W.inner x z - W.inner y z := by
  rw [inner_comm, inner_sub_right, inner_comm W z x, inner_comm W z y]

theorem inner_smul_right (W : Weights n) (a : ℝ) (x y : Vector n) :
    W.inner x (a • y) = a * W.inner x y := by
  simp only [Weights.inner, Pi.smul_apply, smul_eq_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  ring

theorem inner_smul_left (W : Weights n) (a : ℝ) (x y : Vector n) :
    W.inner (a • x) y = a * W.inner x y := by
  rw [inner_comm, inner_smul_right, inner_comm W y x]

theorem normSq_nonneg (W : Weights n) (x : Vector n) : 0 ≤ W.normSq x := by
  unfold Weights.normSq Weights.inner
  apply Finset.sum_nonneg
  intro i _
  have h : 0 ≤ W.value i * (x i) ^ 2 := mul_nonneg (W.positive i).le (sq_nonneg _)
  nlinarith

theorem normSq_eq_zero_iff (W : Weights n) (x : Vector n) : W.normSq x = 0 ↔ x = 0 := by
  constructor
  · intro h
    have hn : ∀ i ∈ Finset.univ, 0 ≤ W.value i * x i * x i := by
      intro i _
      have hi := mul_nonneg (W.positive i).le (sq_nonneg (x i))
      nlinarith
    have hz := (Finset.sum_eq_zero_iff_of_nonneg hn).mp h
    funext i
    have hi := hz i (Finset.mem_univ i)
    have hs : (x i) ^ 2 = 0 := by
      have hm : W.value i * (x i) ^ 2 = 0 := by nlinarith [hi]
      exact (mul_eq_zero.mp hm).resolve_left (ne_of_gt (W.positive i))
    exact pow_eq_zero hs
  · rintro rfl
    simp [Weights.normSq, Weights.inner]

theorem normSq_sub (W : Weights n) (x y : Vector n) :
    W.normSq (x - y) = W.normSq x - 2 * W.inner x y + W.normSq y := by
  unfold Weights.normSq
  rw [inner_sub_left, inner_sub_right, inner_sub_right, inner_comm W y x]
  ring

theorem normSq_smul (W : Weights n) (a : ℝ) (x : Vector n) :
    W.normSq (a • x) = a ^ 2 * W.normSq x := by
  unfold Weights.normSq
  rw [inner_smul_left, inner_smul_right]
  ring

/-- An exact orthogonal projector supplied with its defining obligations. -/
structure Projection (W : Weights n) where
  space : Submodule ℝ (Vector n)
  map : Vector n →ₗ[ℝ] Vector n
  mem : ∀ g, map g ∈ space
  orthogonal : ∀ g p, p ∈ space → W.inner p (g - map g) = 0

theorem project_eq_self_iff (W : Weights n) (P : Projection W) (g : Vector n) :
    P.map g = g ↔ g ∈ P.space := by
  constructor
  · intro h
    rw [← h]
    exact P.mem g
  · intro hg
    have h := P.orthogonal g (g - P.map g) (P.space.sub_mem hg (P.mem g))
    have hz : g - P.map g = 0 := (normSq_eq_zero_iff W _).mp h
    exact (sub_eq_zero.mp hz).symm

theorem project_idempotent (W : Weights n) (P : Projection W) (g : Vector n) :
    P.map (P.map g) = P.map g := (project_eq_self_iff W P _).mpr (P.mem g)

theorem inner_project (W : Weights n) (P : Projection W) (g p : Vector n)
    (hp : p ∈ P.space) : W.inner p g = W.inner p (P.map g) := by
  have h := P.orthogonal g p hp
  rw [inner_sub_right] at h
  exact sub_eq_zero.mp h

theorem project_self_adjoint (W : Weights n) (P : Projection W) (g h : Vector n) :
    W.inner (P.map g) h = W.inner g (P.map h) := by
  calc
    W.inner (P.map g) h = W.inner (P.map g) (P.map h) := inner_project W P h _ (P.mem g)
    _ = W.inner (P.map h) (P.map g) := inner_comm W _ _
    _ = W.inner (P.map h) g := (inner_project W P g _ (P.mem h)).symm
    _ = W.inner g (P.map h) := inner_comm W _ _

def objective (W : Weights n) (K : ℝ) (g p : Vector n) : ℝ :=
  W.inner p g - W.normSq p / (2 * K)

def optimizer (W : Weights n) (K : ℝ) (P : Projection W) (g : Vector n) : Vector n :=
  K • P.map g

def condensedEnergy (W : Weights n) (K : ℝ) (P : Projection W) (g : Vector n) : ℝ :=
  K / 2 * W.normSq (P.map g)

def pointwiseEnergy (W : Weights n) (K : ℝ) (g : Vector n) : ℝ := K / 2 * W.normSq g

theorem optimizer_mem (W : Weights n) (K : ℝ) (P : Projection W) (g : Vector n) :
    optimizer W K P g ∈ P.space := P.space.smul_mem K (P.mem g)

/-- Completion of the square proves both the maximum value and uniqueness. -/
theorem square_completion (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g p : Vector n) (hp : p ∈ P.space) :
    objective W K g p = condensedEnergy W K P g - W.normSq (p - optimizer W K P g) / (2 * K) := by
  rw [objective, condensedEnergy, optimizer, normSq_sub, inner_smul_right,
    normSq_smul, inner_project W P g p hp]
  field_simp [ne_of_gt hK]
  ring

theorem optimizer_value (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g : Vector n) :
    objective W K g (optimizer W K P g) = condensedEnergy W K P g := by
  rw [square_completion W K hK P g _ (optimizer_mem W K P g)]
  simp [Weights.normSq, Weights.inner]

theorem objective_le_condensed (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g p : Vector n) (hp : p ∈ P.space) :
    objective W K g p ≤ condensedEnergy W K P g := by
  rw [square_completion W K hK P g p hp]
  exact sub_le_self _ (div_nonneg (normSq_nonneg W _)
    (mul_nonneg (by norm_num) hK.le))

theorem value_eq_iff_optimizer (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g p : Vector n) (hp : p ∈ P.space) :
    objective W K g p = condensedEnergy W K P g ↔ p = optimizer W K P g := by
  constructor
  · intro h
    have hd : W.normSq (p - optimizer W K P g) / (2 * K) = 0 := by
      linarith [square_completion W K hK P g p hp]
    rcases div_eq_zero_iff.mp hd with hs | hz
    · exact sub_eq_zero.mp ((normSq_eq_zero_iff W _).mp hs)
    · nlinarith
  · rintro rfl
    exact optimizer_value W K hK P g

theorem unique_maximizer (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g p : Vector n) (hp : p ∈ P.space) :
    (∀ q ∈ P.space, objective W K g q ≤ objective W K g p) ↔ p = optimizer W K P g := by
  constructor
  · intro h
    apply (value_eq_iff_optimizer W K hK P g p hp).mp
    apply le_antisymm (objective_le_condensed W K hK P g p hp)
    rw [← optimizer_value W K hK P g]
    exact h _ (optimizer_mem W K P g)
  · rintro rfl
    intro q hq
    rw [optimizer_value W K hK P g]
    exact objective_le_condensed W K hK P g q hq

theorem pythagoras (W : Weights n) (P : Projection W) (g : Vector n) :
    W.normSq g = W.normSq (P.map g) + W.normSq (g - P.map g) := by
  rw [normSq_sub, inner_comm W g (P.map g), inner_project W P g _ (P.mem g)]
  unfold Weights.normSq
  ring

theorem pointwise_minus_condensed (W : Weights n) (K : ℝ)
    (P : Projection W) (g : Vector n) :
    pointwiseEnergy W K g - condensedEnergy W K P g = K / 2 * W.normSq (g - P.map g) := by
  unfold pointwiseEnergy condensedEnergy
  rw [pythagoras W P g]
  ring

theorem condensed_nonneg (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g : Vector n) : 0 ≤ condensedEnergy W K P g := by
  exact mul_nonneg (div_nonneg hK.le (by norm_num)) (normSq_nonneg W _)

theorem gap_nonneg (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g : Vector n) :
    0 ≤ pointwiseEnergy W K g - condensedEnergy W K P g := by
  rw [pointwise_minus_condensed]
  exact mul_nonneg (div_nonneg hK.le (by norm_num)) (normSq_nonneg W _)

theorem gap_zero_iff_represented (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P : Projection W) (g : Vector n) :
    pointwiseEnergy W K g - condensedEnergy W K P g = 0 ↔ g ∈ P.space := by
  rw [pointwise_minus_condensed, mul_eq_zero]
  have hk : K / 2 ≠ 0 := ne_of_gt (div_pos hK (by norm_num))
  simp only [hk, false_or, normSq_eq_zero_iff, sub_eq_zero]
  exact eq_comm.trans (project_eq_self_iff W P g)

/-- Both spaces use the same weights, K and g. -/
theorem nested_energy_monotone (W : Weights n) (K : ℝ) (hK : 0 < K)
    (P R : Projection W) (hQR : P.space ≤ R.space) (g : Vector n) :
    condensedEnergy W K P g ≤ condensedEnergy W K R g := by
  rw [← optimizer_value W K hK P g]
  exact objective_le_condensed W K hK R g _ (hQR (optimizer_mem W K P g))

end KenomaMixedVolume

#print axioms KenomaMixedVolume.inner_comm
#print axioms KenomaMixedVolume.inner_add_right
#print axioms KenomaMixedVolume.inner_add_left
#print axioms KenomaMixedVolume.inner_sub_right
#print axioms KenomaMixedVolume.inner_sub_left
#print axioms KenomaMixedVolume.inner_smul_right
#print axioms KenomaMixedVolume.inner_smul_left
#print axioms KenomaMixedVolume.normSq_nonneg
#print axioms KenomaMixedVolume.normSq_eq_zero_iff
#print axioms KenomaMixedVolume.normSq_sub
#print axioms KenomaMixedVolume.normSq_smul
#print axioms KenomaMixedVolume.project_eq_self_iff
#print axioms KenomaMixedVolume.project_idempotent
#print axioms KenomaMixedVolume.inner_project
#print axioms KenomaMixedVolume.project_self_adjoint
#print axioms KenomaMixedVolume.optimizer_mem
#print axioms KenomaMixedVolume.square_completion
#print axioms KenomaMixedVolume.optimizer_value
#print axioms KenomaMixedVolume.objective_le_condensed
#print axioms KenomaMixedVolume.value_eq_iff_optimizer
#print axioms KenomaMixedVolume.unique_maximizer
#print axioms KenomaMixedVolume.pythagoras
#print axioms KenomaMixedVolume.pointwise_minus_condensed
#print axioms KenomaMixedVolume.condensed_nonneg
#print axioms KenomaMixedVolume.gap_nonneg
#print axioms KenomaMixedVolume.gap_zero_iff_represented
#print axioms KenomaMixedVolume.nested_energy_monotone
