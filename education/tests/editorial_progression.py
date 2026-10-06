"""Inspect real editorial HTML/navigation and PDF, without release qualification."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import hashlib, json, os, re, shutil, subprocess, sys
import fitz
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from render_pdf import repair_outline_titles
normalize = lambda s: ' '.join(s.split())

def inspect(out, evidence):
    evidence.mkdir(parents=True,exist_ok=True)
    manifest = json.loads((out/'editorial-preview-manifest.json').read_text())
    for name, h in manifest['input_sha256'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == h, name
    headings = []
    for name in manifest['chapters']:
        path = ROOT/'book/chapters'/name if not name.startswith('../') else ROOT/'contributions/continuum_reference/chapter.md'
        headings.append(re.sub(r'\s*\{#[^}]+\}\s*$', '', path.read_text().splitlines()[0].removeprefix('# ')))
    md = (out/'kenoma-mechanics.md').read_text()
    assert [re.sub(r'\s*\{#[^}]+\}\s*$','',s) for s in re.findall(r'^# ([^\n]+)',md,re.M)[:len(headings)]] == headings
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(out)))
    Thread(target=server.serve_forever,daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}'
    receipt = {'scope':manifest['scope'],'checks':[],'page_errors':[]}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page = browser.new_page(viewport={'width':1280,'height':1000})
            page.on('pageerror',lambda e:receipt['page_errors'].append(str(e)))
            page.goto(url+'/index.html',wait_until='networkidle')
            actual = page.locator('main > h1').evaluate_all('(els)=>els.map(e=>({id:e.id,title:e.textContent}))')
            assert [normalize(h['title']) for h in actual[:len(headings)]] == headings
            top_ids = [h['id'] for h in actual]
            toc = page.locator('.toc a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href").slice(1))')
            assert [anchor for anchor in toc if anchor in top_ids] == top_ids
            assert len(top_ids) == len(set(top_ids))
            for anchor in set(page.locator('a[href^="#"]').evaluate_all('(els)=>els.map(e=>e.getAttribute("href").slice(1))')):
                assert page.locator('[id="'+anchor+'"]').count()==1, anchor
            assert page.locator('.proof-card').count()==29
            assert page.locator('[data-property]').count()==3 and page.locator('[data-demo],[data-advanced]').count()==7
            receipt['checks'].append('Canonical Markdown, actual HTML chapters and TOC have identical measurement-first order; all fragment targets are unique')
            for width,height,label in [(1280,1000,'desktop'),(393,852,'mobile')]:
                page.set_viewport_size({'width':width,'height':height})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                for name in ['deformation','isochoric','tapered']:
                    lab=page.locator(f'[data-property={name}]');lab.scroll_into_view_if_needed()
                    lab.screenshot(path=str(evidence/f'{label}-{name}.png'))
            receipt['checks'].append('Desktop/mobile property lessons render without page overflow')
            page.set_viewport_size({'width':1280,'height':1000})
            page.emulate_media(media='print')
            for name in ['deformation','isochoric','tapered']:
                expect(page.locator(f'[data-property={name}] .static-figure')).to_be_visible()
                expect(page.locator(f'[data-property={name}] .property-scene')).to_be_hidden()
            page.evaluate('document.fonts.ready')
            # Preserve source links beyond the temporary local server's lifetime.
            revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
            destinations={}
            for prefix,source in [('', 'Mechanics'),('transfer','AnatomicalTransfer'),('coupled','CoupledMechanics'),('arm','AnatomicalArm'),('property','ContinuumProperties')]:
                destinations[f'proofs/{source}.lean']='#'+(prefix+'-source-appendix' if prefix else 'checked-source-appendix')
                destinations[(prefix+'-' if prefix else '')+'proof-status.json']='#'+(prefix+'-proof-receipt' if prefix else 'proof-check-receipt')
                destinations[(prefix+'-' if prefix else '')+'lean-check.txt']='#'+(prefix+'-kernel-report' if prefix else 'kernel-dependency-report')
            page.evaluate('''({revision,destinations})=>{for(const link of document.querySelectorAll('a[href]')){
              const href=link.getAttribute('href');
              if(destinations[href])link.setAttribute('href',destinations[href]);
              else if(href.startsWith('web/')||href.startsWith('data/'))link.setAttribute('href',`https://github.com/MrScripty/Kenoma/blob/${revision}/education/${href}`);
              else if(href.startsWith('coupled-fixture/')||href.startsWith('anatomy-inspection/')||href.startsWith('anatomical-arm/'))link.setAttribute('href',`https://github.com/MrScripty/Kenoma/blob/${revision}/education/data/anatomical-arm-v1/README.md`);
            }}''',{'revision':revision,'destinations':destinations})
            page.pdf(path=str(out/'kenoma-mechanics.pdf'),format='A4',print_background=True,prefer_css_page_size=True,tagged=True,outline=True,
                     display_header_footer=True,header_template='<span></span>',footer_template='<div style="font-family:Arial;font-size:9px;width:100%;padding:0 18mm;color:#456171;display:flex;justify-content:space-between"><span>Kenoma · Editorial review preview · Not for publication</span><span class="pageNumber"></span></div>')
            repair_outline_titles(out/'kenoma-mechanics.pdf',page.locator('h1,h2,h3,h4,h5,h6').all_text_contents())
            links=set(page.locator('[src],a[href]').evaluate_all('(els)=>els.map(el=>el.getAttribute("src")||el.getAttribute("href"))'))
            requests=browser.new_context().request
            for href in links:
                if href and not href.startswith(('#','http','data:')):
                    assert requests.get(url+'/'+href.split('#')[0]).status==200,href
            receipt['checks'].append('All local linked assets/downloads resolve; print uses static alternatives')
            receipt['browser']=browser.version
            assert not receipt['page_errors'],receipt['page_errors']
            browser.close()
    finally:server.shutdown();server.server_close()
    doc=fitz.open(out/'kenoma-mechanics.pdf');outline=doc.get_toc()
    positions={normalize(title):number for level,title,number in outline if normalize(title) in headings}
    assert len(positions)==len(headings),positions
    assert [positions[h] for h in headings]==sorted(positions[h] for h in headings)
    assert positions[headings[3]]<positions[headings[4]]<positions[headings[5]]<positions['From a spring to a volume of tissue']
    selected={positions[h] for h in headings[:6]+['From a spring to a volume of tissue']}
    selected.update(range(positions[headings[4]],positions[headings[5]]+1))
    for i,page in enumerate(doc):
        text=normalize(page.get_text())
        if any(phrase in text for phrase in ['Property lab 1 ·','Property lab 2 ·','Property lab 3 ·','Try and predict.']): selected.add(i+1)
        assert '\ufffd' not in text, f'PDF replacement glyph on page {i+1}'
        assert all('127.0.0.1' not in link.get('uri','') for link in page.get_links()), f'PDF contains temporary-server URL on page {i+1}'
    for number in sorted(selected):
        doc[number-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(evidence/f'pdf-page-{number}.png')
    receipt.update(status='PASS_EDITORIAL_LAYOUT_AND_LINKS',pdf_pages=len(doc),chapter_pages=positions,
                   selected_pdf_pages=sorted(selected),manifest_sha256=hashlib.sha256((out/'editorial-preview-manifest.json').read_bytes()).hexdigest(),
                   outputs={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['index.html','kenoma-mechanics.md','kenoma-mechanics.pdf']})
    receipt['checks'].append('Actual PDF outline follows the canonical chapter order; selected pages captured for manual inspection')
    receipt['inspector_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (evidence/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':inspect(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
