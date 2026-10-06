"""Print the shared HTML book. Static diagrams replace all interactive surfaces."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json,os,shutil,subprocess
import fitz
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

def repair_outline_titles(path,heading_titles):
    """Restore spaces Chromium can omit at wrapped PDF heading boundaries.

    Match only whitespace-equivalent labels from the actual HTML headings;
    preserve each outline level/page/destination and every rendered page.
    """
    canonical={''.join(title.split()):' '.join(title.split()) for title in heading_titles}
    with fitz.open(path) as doc:
        outline=doc.get_toc();changed=False
        for index,row in enumerate(outline):
            title=canonical.get(''.join(row[1].split()))
            if title is not None and title!=row[1]:doc.set_toc_item(index,title=title);changed=True
        if changed:doc.saveIncr()

def serve():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'dist')))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    return server,f'http://127.0.0.1:{server.server_port}'

def render():
    server,url=serve()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True, executable_path=os.environ.get("CHROMIUM_EXECUTABLE") or shutil.which("chromium"))
            page=browser.new_page()
            page.goto(url+'/index.html',wait_until='networkidle')
            page.emulate_media(media='print')
            page.evaluate('document.fonts.ready')
            heading_titles=page.locator('h1,h2,h3,h4,h5,h6').all_text_contents()
            # PDF links must survive the print server's lifetime. Web downloads stay relative.
            revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
            page.evaluate('''revision => {
              const destinations={'proofs/Mechanics.lean':'#checked-source-appendix','proof-status.json':'#proof-check-receipt','lean-check.txt':'#kernel-dependency-report'};
              Object.assign(destinations,{'proofs/AnatomicalTransfer.lean':'#transfer-source-appendix','transfer-proof-status.json':'#transfer-proof-receipt','transfer-lean-check.txt':'#transfer-kernel-report','proofs/CoupledMechanics.lean':'#coupled-source-appendix','coupled-proof-status.json':'#coupled-proof-receipt','coupled-lean-check.txt':'#coupled-kernel-report','proofs/AnatomicalArm.lean':'#arm-source-appendix','arm-proof-status.json':'#arm-proof-receipt','arm-lean-check.txt':'#arm-kernel-report','proofs/ContinuumProperties.lean':'#property-source-appendix','property-proof-status.json':'#property-proof-receipt','property-lean-check.txt':'#property-kernel-report'});
              for(const link of document.querySelectorAll('a[href]')){
                const href=link.getAttribute('href'),target=destinations[href];
                if(target)link.setAttribute('href',target);
                else if(href.startsWith('data/'))link.setAttribute('href',`https://github.com/MrScripty/Kenoma/blob/${revision}/education/${href}`);
                else if(href.startsWith('web/'))link.setAttribute('href',`https://github.com/MrScripty/Kenoma/blob/${revision}/education/${href}`);
                else if(href.startsWith('coupled-fixture/')||href.startsWith('anatomy-inspection/')||href.startsWith('anatomical-arm/')){
                  link.setAttribute('href',`https://github.com/MrScripty/Kenoma/blob/${revision}/education/data/anatomical-arm-v1/README.md`);
                  link.textContent='Reproduce this research preview from the pinned repository instructions';
                }
              }
            }''',revision)
            page.pdf(path=str(ROOT/'dist/kenoma-mechanics.pdf'),format='A4',print_background=True,
              display_header_footer=True,header_template='<span></span>',
              footer_template='<div style="font-family:Arial;font-size:9px;width:100%;padding:0 18mm;color:#456171;display:flex;justify-content:space-between"><span>Kenoma · Mechanics of Moving Bodies · Spatial mechanics and evidence</span><span class="pageNumber"></span></div>',
              prefer_css_page_size=True,tagged=True,outline=True)
            repair_outline_titles(ROOT/'dist/kenoma-mechanics.pdf',heading_titles)
            version=browser.version;browser.close()
        (ROOT/'dist/pdf-render.json').write_text(json.dumps({'renderer':'Playwright Chromium','browser_version':version,'source':'index.html','static_diagrams':True,'tagged':True,'pdf_byte_identity_asserted':False},indent=2)+'\n')
        print('Rendered illustrated PDF from the same HTML content')
    finally:server.shutdown();server.server_close()
if __name__=='__main__':render()
