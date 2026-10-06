#!/usr/bin/env python3
"""Negative controls for proof/receipt custody, not numerical model tests."""
from pathlib import Path
import sys
import json
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_euler_constraint_defect_proofs import audit_source, audit_transcript

ROOT=Path(__file__).resolve().parents[1]


class ProofAudit(unittest.TestCase):
    def setUp(self):
        self.source=(ROOT/'proofs/EulerConstraintDefect.lean').read_text()
        self.claims=json.loads((ROOT/'proofs/euler-constraint-defect-claims.json').read_text())

    def transcript(self):
        return '\n'.join("'"+c['theorem']+"' depends on axioms: [propext, Classical.choice, Quot.sound]" for c in self.claims)

    def test_declared_claim_and_axiom_inventory_match(self):
        audit_source(self.source,self.claims)
        self.assertEqual(len(audit_transcript(self.transcript(),self.claims)),10)

    def test_admissions_and_custom_axioms_rejected(self):
        for token in ['sorry','admit','axiom invented : False','native_decide','unsafe']:
            with self.subTest(token=token),self.assertRaises(RuntimeError):
                audit_source(self.source+'\n'+token,self.claims)

    def test_nested_comments_do_not_hide_admission(self):
        audit_source('/- outer /- sorry -/ comment -/\n'+self.source,self.claims)
        with self.assertRaises(RuntimeError):
            audit_source('/- outer /- comment -/ -/\nsorry\n'+self.source,self.claims)
        with self.assertRaises(RuntimeError):
            audit_source(self.source+'\n/- unclosed',self.claims)

    def test_missing_duplicate_and_extra_declarations_rejected(self):
        for source in [self.source.replace('#print axioms KenomaEuler.normalized_error',''),
                       self.source+'\n#print axioms KenomaEuler.normalized_error',
                       self.source+'\ntheorem hidden : True := by trivial']:
            with self.assertRaises(RuntimeError):audit_source(source,self.claims)
        with self.assertRaises(RuntimeError):audit_source(self.source,self.claims+[self.claims[0]])

    def test_transcript_unknown_dependency_rejected(self):
        for ax in ['sorryAx','invented']:
            with self.assertRaises(RuntimeError):
                audit_transcript(self.transcript().replace('Quot.sound','Quot.sound, '+ax,1),self.claims)

    def test_transcript_missing_duplicate_or_wrong_name_rejected(self):
        t=self.transcript()
        for bad in ['\n'.join(t.splitlines()[1:]),t+'\n'+t.splitlines()[0],t.replace('KenomaEuler.normalized_error','Other.normal_gap_positive')]:
            with self.assertRaises(RuntimeError):audit_transcript(bad,self.claims)

    def test_no_axiom_statement_supported(self):
        t=self.transcript().replace('depends on axioms: [propext, Classical.choice, Quot.sound]','does not depend on any axioms',1)
        self.assertEqual(audit_transcript(t,self.claims)[0]['axioms'],[])


if __name__=='__main__':unittest.main(verbosity=2)
