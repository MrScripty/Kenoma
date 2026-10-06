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
    # The unchanged standalone checker prints from loopback. Make the new
    # review PDF portable, retaining the unchanged lab and checker identities.
    pdf = out/'projection-qa/fixed-field-reference.pdf'
    revision = json.loads((out/'build-manifest.json').read_text())['git_revision']
    rewrites = []
    with fitz.open(pdf) as doc:
        for page in doc:
            for link in page.get_links():
                uri = link.get('uri', '')
                parsed = urlparse(uri)
                if parsed.hostname in {'127.0.0.1', 'localhost', '::1'}:
                    target = f'https://github.com/MrScripty/Kenoma/blob/{revision}/education{parsed.path}'
                    link['uri'] = target; page.update_link(link)
                    rewrites.append({'from':parsed.path,'to':target})
        if rewrites: doc.saveIncr()
    receipt_path = out/'projection-qa/receipt.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['evidence_sha256'][pdf.name] = digest(pdf)
    receipt['portable_pdf_links'] = {'annotation_only_rewrites':rewrites, 'source_commit':revision}
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    server, url = serve()
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page = browser.new_page(viewport={'width':1280,'height':900})
            page.on('pageerror', lambda error: errors.append(str(error)))
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
