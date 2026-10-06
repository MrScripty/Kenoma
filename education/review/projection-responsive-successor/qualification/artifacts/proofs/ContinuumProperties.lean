import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Data.Real.Sqrt

/-!
Real-valued kinematic identities. These do not prove floating-point refinement,
surface mesh correctness, equilibrium, material selection or biological validity.
Mathlib and its dependency manifest are pinned separately from the Std-only work.
-/
namespace KenomaProperties

def edgeMatrix (v : Fin 4 → Fin 3 → ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  fun i j => v j.succ i - v 0 i

theorem edge_translation_invariant (v : Fin 4 → Fin 3 → ℝ) (t : Fin 3 → ℝ) :
    edgeMatrix (fun j i => v j i + t i) = edgeMatrix v := by
  apply Matrix.ext
  intro i j
  simp [edgeMatrix]

theorem determinant_composition (A B : Matrix (Fin 3) (Fin 3) ℝ) :
    Matrix.det (A * B) = Matrix.det A * Matrix.det B := by
  exact Matrix.det_mul A B

def axialMatrix (lambda b : ℝ) : Matrix (Fin 3) (Fin 3) ℝ :=
  Matrix.diagonal ![lambda, b, b]

theorem axial_determinant (lambda b : ℝ) :
    Matrix.det (axialMatrix lambda b) = lambda * b * b := by
  simp [axialMatrix, Matrix.det_diagonal, Fin.prod_univ_succ, mul_assoc]

theorem isochoric_sqrt_construction (lambda : ℝ) (hlambda : 0 < lambda) :
    0 < 1 / Real.sqrt lambda ∧
    Matrix.det (axialMatrix lambda (1 / Real.sqrt lambda)) = 1 := by
  constructor
  · exact one_div_pos.mpr (Real.sqrt_pos.mpr hlambda)
  · rw [axial_determinant]
    calc
      lambda * (1 / Real.sqrt lambda) * (1 / Real.sqrt lambda) =
          lambda * (Real.sqrt lambda * Real.sqrt lambda)⁻¹ := by
        simp only [one_div, mul_assoc, mul_inv]
      _ = 1 := by
        rw [Real.mul_self_sqrt hlambda.le]
        exact mul_inv_cancel₀ (ne_of_gt hlambda)

end KenomaProperties

#print axioms KenomaProperties.edge_translation_invariant
#print axioms KenomaProperties.determinant_composition
#print axioms KenomaProperties.axial_determinant
#print axioms KenomaProperties.isochoric_sqrt_construction
