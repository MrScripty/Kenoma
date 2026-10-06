"""Exercise actual Chromium layout and token preservation at A4 print width."""
from pathlib import Path
import shutil
import unittest
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

class PrintLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True,executable_path=shutil.which('chromium'))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.playwright.stop()

    def page(self,expression):
        page=self.browser.new_page(viewport={'width':658,'height':1000})
        page.set_content('<style>'+ (ROOT/'web/style.css').read_text() + '</style><div class="layout"><main>'
            '<p>Readable print text keeps its physical point size.</p><div class="equation">'
            '<math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow>'
            +expression+'</mrow><annotation encoding="application/x-tex">unchanged source annotation</annotation>'
            '</semantics></math></div></main></div>')
        page.emulate_media(media='print');page.evaluate('document.fonts.ready')
        self.addCleanup(page.close)
        return page

    def test_wrap_preserves_nested_tokens_and_real_pdf_point_size(self):
        expression='<mi>W</mi><mo>=</mo>'+ '<mo>+</mo>'.join(
            '<mfrac><msup><mi>x</mi><mn>2</mn></msup><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow></mfrac>' for _ in range(35))
        page=self.page(expression)
        original=page.locator('.equation > math').evaluate('(node)=>node.outerHTML')
        result=page.evaluate((ROOT/'tools/print_layout.js').read_text())
        self.assertEqual(len(result['reflowed']),1)
        self.assertGreater(result['reflowed'][0]['rows'],1)
        self.assertEqual(page.locator('.equation > math').evaluate('(node)=>node.outerHTML'),original)
        self.assertEqual(page.locator('.print-equation-rows mfrac').count(),35)
        self.assertEqual(result['documentWidthPx'],658)
        with fitz.open(stream=page.pdf(format='A4',prefer_css_page_size=True),filetype='pdf') as pdf:
            sizes=[s['size'] for p in pdf for b in p.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if 'Readable print text' in s['text']]
            self.assertTrue(sizes);self.assertGreaterEqual(min(sizes),10)
        page.emulate_media(media='screen')
        self.assertTrue(page.locator('.equation > math').is_visible())
        self.assertFalse(page.locator('.print-equation-rows').is_visible())

    def test_indivisible_overflow_fails_instead_of_shrinking(self):
        page=self.page('<mi>'+'unbreakable'*100+'</mi>')
        with self.assertRaisesRegex(Exception,'Indivisible print math exceeds page width'):
            page.evaluate((ROOT/'tools/print_layout.js').read_text())

    def test_short_equation_is_left_intact(self):
        page=self.page('<mi>F</mi><mo>=</mo><mi>m</mi><mi>a</mi>')
        before=page.locator('.equation').inner_html()
        self.assertEqual(page.evaluate((ROOT/'tools/print_layout.js').read_text())['reflowed'],[])
        self.assertEqual(page.locator('.equation').inner_html(),before)

if __name__=='__main__':unittest.main()
