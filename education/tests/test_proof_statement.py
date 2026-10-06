"""Proof cards must show precisely the named checked theorem's statement."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build import theorem_statement

class ProofStatementTests(unittest.TestCase):
    def test_actual_term_proof_does_not_swallow_the_next_declaration(self):
        source=(ROOT/'proofs/DissipativeBarReal.lean').read_text()
        statement=theorem_statement(source,'dissipation_nonnegative')
        self.assertEqual(statement,'theorem dissipation_nonnegative (eta vdot : ℝ) (heta : 0 ≤ eta) :\n    0 ≤ dissipationRate eta vdot')
        self.assertNotIn('mul_nonneg',statement)
        self.assertNotIn('storage_hasDerivAt',statement)

    def test_missing_assignment_rejects_instead_of_borrowing_the_next_theorem(self):
        with self.assertRaisesRegex(ValueError,'Missing theorem statement'):
            theorem_statement('theorem unfinished : True\ntheorem later : True := by trivial','unfinished')

if __name__=='__main__':unittest.main()
