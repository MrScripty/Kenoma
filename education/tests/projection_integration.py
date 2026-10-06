"""Exercise the shipped lab and in-book frame; bind every result to the build."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys
from urllib.parse import urlparse
import fitz
from playwright.sync_api import sync_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from render_pdf import serve
from executable_outputs import checked_build_outputs, unchanged_outputs


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    out = ROOT/'dist'
    manifest_hash = digest(out/'build-manifest.json')
    outputs = checked_build_outputs(out)
    shutil.rmtree(out/'projection-qa', ignore_errors=True)
    for name in ['pressure-projection-lab.html', 'pressure-projection-proof-guide.md', 'pressure-projection-lab-check.py']:
        assert digest(ROOT/'standalone'/name) == digest(out/'standalone'/name)
    subprocess.run([sys.executable, str(out/'standalone/pressure-projection-lab-check.py'), '--output', str(out/'projection-qa')], check=True)
    # Retain accepted source bytes, but re-render the new review PDF at actual
    # readable print size and with permanent source links. The standalone
    # checkpoint's original PDF was never a portable print qualification.
    pdf = out/'projection-qa/fixed-field-reference.pdf'
    revision = json.loads((out/'build-manifest.json').read_text())['git_revision']
    original_pdf_hash = digest(pdf)
    receipt_path = out/'projection-qa/receipt.json'
    receipt = json.loads(receipt_path.read_text())
    server, url = serve()
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page = browser.new_page(viewport={'width':1280,'height':900})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(url+'/standalone/pressure-projection-lab.html',wait_until='networkidle')
            page.emulate_media(media='print'); page.set_viewport_size({'width':658,'height':1000})
            page.add_style_tag(content='''@page{size:A4;margin:18mm}
                @media print{*{font-size:14px!important}main{width:100%;padding:0}
                .hero,.charts,.details-grid,.definition,.footer{display:block}
                .chart svg{width:310px!important;max-width:100%!important;margin:auto}
                .chart{margin:12px 0;break-inside:avoid}.panel{break-inside:avoid}
                .controls{display:none!important}svg text{font-size:14px!important}}
            ''')
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'Review print overflow'
            graphics = page.locator('svg[role=img]').evaluate_all('(nodes)=>nodes.map(n=>n.outerHTML)')
            page.evaluate('''revision=>{for(const a of document.querySelectorAll('a[href]')){
                const url=new URL(a.href);if(url.origin===location.origin)
                a.href=`https://github.com/MrScripty/Kenoma/blob/${revision}/education${url.pathname}`;
            }}''',revision)
            page.pdf(path=str(pdf),format='A4',print_background=True,prefer_css_page_size=True,tagged=True)
            from check_print_readability import PDFText, svg_label_measurements, portable_links
            with fitz.open(pdf) as doc:
                glyphs = [s['size'] for pg in doc for b in pg.get_text('dict')['blocks'] for line in b.get('lines',[]) for s in line['spans'] if s['text'].strip()]
                assert glyphs and min(glyphs)>=10, 'Review PDF actual-point readability failed'
                measured = PDFText(doc); labels = []
                for index,svg in enumerate(graphics):
                    target=out/'projection-qa'/f'review-chart-{index}.svg';target.write_text(svg)
                    labels.extend(svg_label_measurements(measured,target))
                    receipt['evidence_sha256'][target.name]=digest(target)
                receipt['portable_pdf_links'] = portable_links(doc)
                receipt['review_print_qualification'] = {'minimum_actual_pt':min(glyphs),'diagram_labels':labels,'source_commit':revision,'original_unqualified_pdf_sha256':original_pdf_hash,'pages':len(doc)}
            receipt['evidence_sha256'][pdf.name] = digest(pdf)
            receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
            page.emulate_media(media='screen');page.set_viewport_size({'width':1280,'height':900})
            page.goto(url+'/index.html#fixed-field-pressure-projection', wait_until='networkidle')
            frame = page.frame_locator('iframe[title="Fixed-field weighted pressure projection controls"]')
            expect(frame.locator('#full')).to_have_text('8')
            frame.locator('input[name=space][value="2"]').check()
            expect(frame.locator('#condensed')).to_have_text('1')
            expect(frame.locator('#gap')).to_have_text('7')
            frame.locator('input[name=space][value="4"]').check()
            expect(frame.locator('#gap')).to_have_text('0')
            frame.locator('#reset').click()
            expect(frame.locator('#gap')).to_have_text('7.5')
            page.locator('.projection-interactive').screenshot(path=str(out/'projection-qa/book-controls.png'))
            version = browser.version
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    assert not errors
    unchanged_outputs(out, outputs)
    assert manifest_hash == digest(out/'build-manifest.json')
    result = {'result':'PASS_INTEGRATED_FIXED_FIELD_PROJECTION', 'browser':version, 'manifest_sha256':manifest_hash,
        'html_sha256':digest(out/'index.html'), 'lab_sha256':digest(out/'standalone/pressure-projection-lab.html'),
        'standalone_receipt_sha256':digest(out/'projection-qa/receipt.json'), 'book_capture_sha256':digest(out/'projection-qa/book-controls.png'),
        'checks':['Shipped source equals accepted standalone bytes', '5625 independent rational browser cases and real desktop/mobile controls', 'Actual in-book iframe refinement and Reset', 'Executable outputs and build manifest unchanged'], 'errors':errors}
    (out/'projection-qa/integration.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'])


if __name__ == '__main__':
    check()
