"""PDF outline repair changes known labels, preserving destinations and pages."""
from pathlib import Path
import hashlib, sys, tempfile, unittest
import fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import repair_outline_titles

class PdfOutline(unittest.TestCase):
    def test_wrapped_labels_repaired_without_changing_destinations_or_rendered_pages(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'book.pdf'
            doc=fitz.open()
            for text in ['A measured example','A later lesson']:
                doc.new_page().insert_text((72,90),text)
            doc.set_toc([[1,'A measuredexample',1],[2,'A later lesson',2],[1,'Unrecognizedtitle',2]])
            doc.save(path);doc.close()
            with fitz.open(path) as before:
                destinations=[row[3] for row in before.get_toc(simple=False)]
                pixels=[hashlib.sha256(page.get_pixmap().samples).hexdigest() for page in before]
            repair_outline_titles(path,['A measured\nexample','A later lesson'])
            with fitz.open(path) as after:
                self.assertEqual(after.get_toc(),[[1,'A measured example',1],[2,'A later lesson',2],[1,'Unrecognizedtitle',2]])
                self.assertEqual([row[3] for row in after.get_toc(simple=False)],destinations)
                self.assertEqual([hashlib.sha256(page.get_pixmap().samples).hexdigest() for page in after],pixels)
            before_bytes=path.read_bytes()
            repair_outline_titles(path,['A measured example','A later lesson'])
            self.assertEqual(path.read_bytes(),before_bytes,'A second pass must leave bytes unchanged')
