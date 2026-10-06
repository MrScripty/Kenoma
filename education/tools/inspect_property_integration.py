"""Source-bound desktop/mobile proof captures and PDF property-chapter pages."""
from pathlib import Path
import hashlib,json,os,re,shutil
import fitz
from playwright.sync_api import sync_playwright
from render_pdf import serve
ROOT=Path(__file__).resolve().parents[1]
def inspect():
    out=ROOT/'dist/property-book-review';out.mkdir(exist_ok=True)
    (out/'render-receipt.json').unlink(missing_ok=True)
    for old in out.glob('pdf-page-*.png'):
        if re.fullmatch(r'pdf-page-[0-9]+\.png',old.name):old.unlink()
    captures=[];server,url=serve();views=[];errors=[]
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for name,width,height in [('desktop',1200,1000),('mobile',393,852)]:
            page=browser.new_page(viewport={'width':width,'height':height});page.on('pageerror',lambda error:errors.append(str(error)));page.goto(url+'/index.html',wait_until='networkidle')
            for claim in ['volume-edge-translation','volume-det-compose','volume-diagonal','volume-isochoric-sqrt']:
                card=page.locator('#proof-'+claim);card.scroll_into_view_if_needed()
                assert card.evaluate('(x)=>x.scrollWidth<=x.clientWidth+1')
                path=out/(name+'-'+claim+'.png');card.screenshot(path=str(path));captures.append(path)
            overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            assert not overflow
            views.append({'name':name,'horizontalOverflow':overflow,'proofCards':page.locator('.proof-card').count()});page.close()
        version=browser.version;browser.close()
    finally:server.shutdown();server.server_close()
    assert not errors,errors
    doc=fitz.open(ROOT/'dist/kenoma-mechanics.pdf');selected=[]
    phrases=['Measure deformation before choosing a muscle law','Property lab 1','Property lab 2','Property lab 3','Checked claim volume-','Checked source appendix: ContinuumProperties','Positive real axial stretch','KenomaProperties.isochoric_sqrt_construction']
    for index,page in enumerate(doc):
        matched=[phrase for phrase in phrases if phrase in page.get_text()]
        if matched:
            path=out/f'pdf-page-{index+1}.png';page.get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False).save(path);captures.append(path);selected.append({'page':index+1,'phrases':matched,'image':path.name})
    assert any('Property lab 1' in row['phrases'] for row in selected)
    assert any('Property lab 2' in row['phrases'] for row in selected)
    assert any('Property lab 3' in row['phrases'] for row in selected)
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    receipt={'schema':1,'result':'PASS_PROPERTY_BOOK_RENDER_CAPTURE','inspector_sha256':digest(Path(__file__)),'html_sha256':digest(ROOT/'dist/index.html'),'pdf_sha256':digest(ROOT/'dist/kenoma-mechanics.pdf'),'build_manifest_sha256':digest(ROOT/'dist/build-manifest.json'),'browser':version,'views':views,'page_errors':errors,'pdf_pages':selected,'outputs':{p.name:digest(p) for p in sorted(captures)},'scope':'Capture and layout evidence; manual appearance review is recorded separately. No biological or browser-arithmetic refinement proof.'}
    (out/'render-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='outputs'},indent=2))
if __name__=='__main__':inspect()
