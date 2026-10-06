"""The frozen, readable heading-only PDF must fail complete limits coverage."""
from pathlib import Path
import sys, unittest
import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from check_projection_print_limits import measure


class ProjectionLimitsRegression(unittest.TestCase):
    def test_frozen_heading_and_large_glyphs_do_not_establish_paragraph_coverage(self):
        pdf = ROOT/'review/accepted-book-integration/artifacts/projection-qa/fixed-field-reference.pdf'
        with fitz.open(pdf) as document:
            self.assertTrue(any('Interpretation and limits' in page.get_text() for page in document))
            sizes = [span['size'] for page in document
                     for block in page.get_text('dict')['blocks']
                     for line in block.get('lines', []) for span in line['spans']
                     if span['text'].strip()]
            self.assertGreaterEqual(min(sizes), 10)
        with self.assertRaisesRegex(AssertionError,
                'projection:complete-limits-paragraph: missing or truncated printed text'):
            measure(pdf, ROOT/'standalone/pressure-projection-lab.html')


if __name__ == '__main__':
    unittest.main()
