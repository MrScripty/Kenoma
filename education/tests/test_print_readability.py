"""Independent actual PDF fixtures for point sizes and complete printed code."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
import json
from unittest.mock import patch

import fitz

MODULE = Path(__file__).resolve().parents[1] / 'tools/check_print_readability.py'
spec = importlib.util.spec_from_file_location('print_readability', MODULE)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PrintedReadabilityTests(unittest.TestCase):
    def pdf(self, lines, width=595, height=842):
        doc = fitz.open()
        page = doc.new_page(width=width, height=height)
        y = 45
        for text, size in lines:
            page.insert_text((30, y), text, fontsize=size, fontname='cour')
            y += 20
        # Reopen serialized actual PDF so tests exercise extraction, not input data.
        reopened = fitz.open(stream=doc.tobytes(), filetype='pdf')
        doc.close()
        self.addCleanup(reopened.close)
        return reopened

    def test_actual_ten_point_boundary(self):
        document = self.pdf([('Instructional prose at the required point floor.', 10)])
        result = checker.PDFText(document).target('prose', 'Instructional prose at the required point floor.', prose=True)
        self.assertEqual(result['minimum_pt'], 10)

    def test_actual_undersized_body_rejected_despite_large_heading(self):
        pdf = checker.PDFText(self.pdf([('A large heading', 18), ('A small instructional paragraph.', 9.99)]))
        with self.assertRaisesRegex(AssertionError, 'below 10 pt'):
            pdf.target('body', 'A small instructional paragraph.', prose=True)

    def test_actual_undersized_theorem_rejected(self):
        text = 'theorem cancel (f : Int) : f + (-f) = 0'
        pdf = checker.PDFText(self.pdf([(text, 7.4)]))
        with self.assertRaisesRegex(AssertionError, 'below 10 pt'):
            pdf.target('theorem', text)

    def test_missing_card_cannot_borrow_full_source_appendix(self):
        text = 'theorem cancel (f : Int) : f + (-f) = 0'
        pdf = checker.PDFText(self.pdf([
            ('Checked claim - cancel', 11), ('Claim and assumptions.', 11),
            ('Full source - Build receipt - Kernel dependency report', 11),
            ('Checked source appendix: Mechanics', 11), (text, 11)]))
        bounds = next(pdf.bounded('Checked claim - cancel', 'Full source - Build receipt - Kernel dependency report'))
        with self.assertRaisesRegex(AssertionError, 'missing or truncated'):
            pdf.target('theorem', text, *bounds)
        self.assertEqual(pdf.target('appendix', text)['minimum_pt'], 11)

    def test_wrapped_full_code_across_pages_excludes_only_named_footer(self):
        first = 'theorem wrapped (a b c d : Int) :\n  a + b + c + d = d + c + b + a := by'
        second = '  omega\nend Example'
        document = fitz.open()
        for text in (first, second):
            page = document.new_page()
            page.insert_text((30, 40), text, fontsize=10.5, fontname='cour')
            page.insert_text((30, 820), 'Kenoma · Mechanics of Moving Bodies · Spatial mechanics and evidence', fontsize=6, fontname='helv')
            page.insert_text((550, 820), str(len(document)), fontsize=6)
        reopened = fitz.open(stream=document.tobytes(), filetype='pdf')
        document.close()
        self.addCleanup(reopened.close)
        pdf = checker.PDFText(reopened)
        result = pdf.target('complete source', first + '\n' + second)
        self.assertEqual(result['pages'], [1, 2])
        self.assertEqual(result['minimum_pt'], 10.5)
        self.assertGreater(pdf.footer_glyphs, 0)

    def test_missing_wrapped_code_line_rejected(self):
        text = 'theorem wrapped (a b : Int) :\n a + b = b + a := by\n omega'
        pdf = checker.PDFText(self.pdf([('theorem wrapped (a b : Int) :', 11), (' omega', 11)]))
        with self.assertRaisesRegex(AssertionError, 'missing or truncated'):
            pdf.target('source', text)

    def test_small_body_near_bottom_is_not_a_footer(self):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((30, 815), 'Actual instructional content at bottom', fontsize=7)
        self.addCleanup(doc.close)
        with self.assertRaisesRegex(AssertionError, 'below 10 pt'):
            checker.PDFText(doc).target('body', 'Actual instructional content at bottom', prose=True)

    def superscript_pdf(self, before, after):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((30, 50), before, fontsize=11, fontname='helv')
        x = 30 + fitz.get_text_length(before, fontname='helv', fontsize=11)
        page.insert_text((x, 46), '2', fontsize=7, fontname='helv')
        page.insert_text((x + fitz.get_text_length('2', fontname='helv', fontsize=7), 50), after, fontsize=11, fontname='helv')
        reopened = fitz.open(stream=doc.tobytes(), filetype='pdf')
        doc.close()
        self.addCleanup(reopened.close)
        return checker.PDFText(reopened)

    def test_code_never_exempts_actual_superscript_flags(self):
        pdf = self.superscript_pdf('theorem square : x^', ' = x*x')
        self.assertTrue(pdf.characters[pdf.text.index('2')]['flags'] & 1)
        with self.assertRaisesRegex(AssertionError, 'below 10 pt'):
            pdf.target('code', 'theorem square : x^2 = x*x', superscript_text='2')

    def test_actual_superscript_requires_html_annotation_and_prose(self):
        pdf = self.superscript_pdf('Area is m', '.')
        self.assertTrue(pdf.characters[pdf.text.index('2')]['flags'] & 1)
        with self.assertRaisesRegex(AssertionError, 'below 10 pt'):
            pdf.target('body', 'Area is m2.', prose=True)
        result = pdf.target('body', 'Area is m2.', prose=True, superscript_text='2')
        self.assertEqual(result['superscript_glyphs_exempted'], 1)
        self.assertEqual(result['minimum_pt'], 11)

    def test_actual_wrapping_preserves_a_long_source_line(self):
        original = 'theorem long_line (alpha beta gamma delta : Int) : alpha + beta + gamma + delta = delta + gamma + beta + alpha := by omega'
        # The reference source has one long line; the printed PDF wraps it.
        wrapped = original.replace(' : alpha', ' :\nalpha').replace(' = delta', ' =\ndelta')
        document = fitz.open()
        page = document.new_page()
        remaining = page.insert_textbox(fitz.Rect(30, 30, 430, 160), wrapped, fontsize=10.5, fontname='cour')
        self.assertGreaterEqual(remaining, 0)
        reopened = fitz.open(stream=document.tobytes(), filetype='pdf')
        document.close()
        self.addCleanup(reopened.close)
        result = checker.PDFText(reopened).target('wrapped source', original)
        self.assertEqual(result['minimum_pt'], 10.5)

    def test_svg_inventory_cannot_borrow_an_unrelated_large_label(self):
        with tempfile.TemporaryDirectory() as directory:
            svg = Path(directory) / 'figure.svg'
            svg.write_text('<svg><text>Figure title</text><text>Force (N)</text><text>0.2</text></svg>')
            pdf = checker.PDFText(self.pdf([('Force (N)', 12), ('Figure title', 11), ('Force (N)', 8), ('0.2', 11)]))
            with self.assertRaisesRegex(AssertionError, 'figure:figure.svg:1:Force.*below 10 pt'):
                checker.svg_label_measurements(pdf, svg)

    def test_svg_missing_numeric_tick_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            svg = Path(directory) / 'figure.svg'
            svg.write_text('<svg><text>Figure title</text><text>Force (N)</text><text>0.2</text></svg>')
            pdf = checker.PDFText(self.pdf([('Figure title', 11), ('Force (N)', 11)]))
            with self.assertRaisesRegex(AssertionError, 'complete printed SVG label inventory'):
                checker.svg_label_measurements(pdf, svg)

    def test_saved_receipt_recheck_rejects_forged_pdf_binding(self):
        actual = {'status': 'PASS', 'pdf_sha256': 'current', 'baseline_pdf_sha256': None}
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / 'print-readability-check.json'
            receipt_path.write_text(json.dumps({**actual, 'pdf_sha256': 'old'}))
            with patch.object(checker, 'qualify', return_value=actual):
                with self.assertRaisesRegex(AssertionError, 'Stale/forged.*pdf_sha256'):
                    checker.check(directory)

    def test_saved_receipt_recheck_preserves_optional_baseline_binding(self):
        actual = {'status': 'PASS', 'pdf_sha256': 'current', 'baseline_pdf_sha256': None}
        saved = {**actual, 'baseline_pdf_sha256': 'explicit original baseline'}
        with tempfile.TemporaryDirectory() as directory:
            receipt_path = Path(directory) / 'print-readability-check.json'
            receipt_path.write_text(json.dumps(saved))
            before = receipt_path.read_bytes()
            with patch.object(checker, 'qualify', return_value=actual):
                self.assertEqual(checker.check(directory), saved)
            self.assertEqual(receipt_path.read_bytes(), before)

    def test_theorem_extractor_stops_before_either_proof_kind(self):
        self.assertEqual(checker.theorem_statement('theorem a : True := by trivial\ntheorem b : True := True.intro', 'X.a'), 'theorem a : True')
        self.assertEqual(checker.theorem_statement('theorem b : True := True.intro', 'X.b'), 'theorem b : True')
        with self.assertRaisesRegex(AssertionError, 'Crossed source declaration'):
            checker.theorem_statement('theorem a : True\ntheorem b : True := by trivial', 'X.a')

    def test_portable_link_targets_ignore_annotation_count(self):
        def document(revision, copies):
            doc = fitz.open()
            page = doc.new_page()
            for i in range(copies):
                page.insert_link({'kind': fitz.LINK_URI, 'from': fitz.Rect(10, 10+i*20, 30, 25+i*20),
                                  'uri': f'https://github.com/MrScripty/Kenoma/blob/{revision}/education/data/a.json'})
            reopened = fitz.open(stream=doc.tobytes(), filetype='pdf')
            doc.close()
            self.addCleanup(reopened.close)
            return reopened
        a, b = checker.portable_links(document('abc', 1)), checker.portable_links(document('def', 2))
        self.assertEqual(a['external_targets'], b['external_targets'])
        self.assertNotEqual(a['annotations'], b['annotations'])

    def test_localhost_link_rejected(self):
        doc = fitz.open()
        page = doc.new_page()
        page.insert_link({'kind': fitz.LINK_URI, 'from': fitz.Rect(10,10,20,20), 'uri': 'http://127.0.0.1/proof'})
        reopened = fitz.open(stream=doc.tobytes(), filetype='pdf')
        doc.close()
        self.addCleanup(reopened.close)
        with self.assertRaisesRegex(AssertionError, 'Nonportable'):
            checker.portable_links(reopened)


if __name__ == '__main__':
    unittest.main()
