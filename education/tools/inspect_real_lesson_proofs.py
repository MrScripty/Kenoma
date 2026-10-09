"""Capture actual new Real cards and verify their durable PDF source evidence."""
from pathlib import Path
import hashlib,json,os,shutil
import fitz
from playwright.sync_api import sync_playwright,expect
from check_real_lesson_proofs import FAMILIES
from render_pdf import serve
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inspect():
    dist=ROOT/'dist';out=dist/'real-proof-review';out.mkdir(exist_ok=True)
    target=out/'render-receipt.json';target.unlink(missing_ok=True)
    receipts=[json.loads((dist/(prefix+'-proof-status.json')).read_text()) for _,_,prefix,_ in FAMILIES]
    claims=[c for r in receipts for c in r['claims']]
    lock=json.loads((ROOT/'proofs/mathlib-lock.json').read_text())
    for receipt,(source,map_name,_,count) in zip(receipts,FAMILIES):
        assert receipt['mathlib']==lock
        assert receipt['source_sha256']==digest(ROOT/'proofs'/source)==digest(dist/'proofs'/source)
        assert receipt['claims_sha256']==digest(ROOT/'proofs'/map_name)==digest(dist/'proofs'/map_name)
        assert len(receipt['claims'])==count and all(c['status']=='checked' for c in receipt['claims'])
    server,url=serve();errors=[];views=[];captures=[]
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for name,width,height in [('desktop',1200,1000),('mobile',393,852)]:
            page=browser.new_page(viewport={'width':width,'height':height})
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(url+'/index.html',wait_until='networkidle')
            for receipt in receipts:
                for claim in receipt['claims']:
                    card=page.locator('#proof-'+claim['id']);card.scroll_into_view_if_needed()
                    expect(card).to_be_visible()
                    toggle=card.locator('.claim-toggle')
                    expect(toggle).to_have_attribute('aria-expanded','false')
                    toggle.focus();page.keyboard.press('Enter')
                    expect(toggle).to_have_attribute('aria-expanded','true')
                    expect(card.locator('.claim-technical')).to_be_visible()
                    expect(card).to_contain_text(claim['assumptions']);expect(card).to_contain_text(claim['limitations'])
                    expect(card.locator('.proof-meta')).to_contain_text(receipt['source_sha256'])
                    from build import theorem_statement
                    expect(card.locator('pre').first).to_have_text(theorem_statement((ROOT / receipt['source']).read_text(), claim['theorem'].split('.')[-1]))
                    assert card.evaluate('(x)=>x.scrollWidth<=x.clientWidth+1')
                    path=out/(name+'-'+claim['id']+'.png');card.screenshot(path=str(path));captures.append(path)
            overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+1');assert not overflow
            views.append({'name':name,'real_cards':len(claims),'horizontal_overflow':overflow});page.close()
        version=browser.version;browser.close()
    finally:server.shutdown();server.server_close()
    assert not errors,errors
    pages=[]
    with fitz.open(dist/'kenoma-mechanics.pdf') as pdf:
        all_text=''.join(''.join(page.get_text().split()) for page in pdf)
        for receipt in receipts:
            assert receipt['source_sha256'] in all_text
            for claim in receipt['claims']:
                assert claim['theorem'] in all_text
                assert ''.join(claim['assumptions'].split()) in all_text
                assert ''.join(claim['limitations'].split()) in all_text
        source_names={Path(r['source']).stem for r in receipts}
        source_started=False
        for index,page in enumerate(pdf):
            text=page.get_text();flat=''.join(text.split())
            for link in page.get_links():
                uri=link.get('uri','');assert '127.0.0.1' not in uri and 'localhost' not in uri,uri
            source_started=source_started or any('Checkedsourceappendix:'+name in flat for name in source_names)
            # These Real appendices are the final book families. Capture their
            # continuation pages as well as the pages bearing their headings.
            if source_started:
                path=out/f'pdf-source-page-{index+1}.png'
                page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(path);captures.append(path)
                pages.append({'page':index+1,'image':path.name})
        assert len(pages)>=len(receipts)
        page_count=len(pdf)
    result={'schema':1,'result':'PASS_REAL_PROOF_RENDER_CAPTURE','source_revision':json.loads((dist/'build-manifest.json').read_text())['git_revision'],
      'inspector_sha256':digest(Path(__file__)),'html_sha256':digest(dist/'index.html'),'app_sha256':digest(dist/'assets/app.js'),
      'pdf_sha256':digest(dist/'kenoma-mechanics.pdf'),'manifest_sha256':digest(dist/'build-manifest.json'),
      'browser':version,'views':views,'page_errors':errors,'real_claims':[c['id'] for c in claims],
      'pdf_pages':page_count,'source_pages':pages,'outputs':{path.name:digest(path) for path in captures},
      'scope':'Actual generated desktop/mobile card captures, source-bound metadata and complete PDF theorem/hash text with durable links. Appearance review is separate; no numerical refinement or biological certificate.'}
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='outputs'},indent=2))
if __name__=='__main__':inspect()
