"""A generated, readable heading-only PDF must fail complete limits coverage."""
from pathlib import Path
import sys, unittest, tempfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from check_projection_print_limits import measure


class ProjectionLimitsRegression(unittest.TestCase):
    def test_frozen_heading_and_large_glyphs_do_not_establish_paragraph_coverage(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        pdf = Path(temporary.name)/'heading-only.pdf'
        with fitz.open() as document:
            document.new_page().insert_text((72,72), 'Interpretation and limits', fontsize=11)
            document.save(pdf)
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
