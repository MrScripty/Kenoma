"""Receipt rejection checks; these do not replace the real Lean compilation."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('proof_audit', Path(__file__).resolve().parents[1] / 'tools/check_activation_equality_proofs.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    claims = [{'theorem': 'KenomaActivation.example'}]
    source = 'theorem example : True := by trivial\n#print axioms KenomaActivation.example\n'
    report = "'KenomaActivation.example' depends on axioms: [propext, Classical.choice, Quot.sound]\n"

    def test_complete_inventory(self):
        audit.audit_source(self.source, self.claims)
        self.assertEqual(audit.audit_transcript(self.report, self.claims)[0]['status'], 'checked')

    def test_admissions_rejected(self):
        for word in ('sorry', 'admit', 'axiom', 'native_decide', 'unsafe'):
            with self.subTest(word=word), self.assertRaises(RuntimeError):
                audit.audit_source(self.source.replace('trivial', word), self.claims)

    def test_nested_comments_not_admissions(self):
        audit.audit_source('/- outer /- sorry -/ axiom -/\n-- admit\n' + self.source, self.claims)

    def test_hidden_declaration_rejected(self):
        with self.assertRaises(RuntimeError):
            audit.audit_source(self.source + 'theorem omitted : True := by trivial\n', self.claims)

    def test_unclosed_comment_rejected(self):
        with self.assertRaises(RuntimeError):
            audit.audit_source(self.source + '/-', self.claims)

    def test_reports_rejected(self):
        for report in ('', self.report * 2, self.report.replace('propext', 'sorryAx')):
            with self.subTest(report=report), self.assertRaises(RuntimeError):
                audit.audit_transcript(report, self.claims)


if __name__ == '__main__':
    unittest.main(verbosity=2)
