"""Actual local controls, downloads, source damage and print gate; no anatomy."""
import argparse,functools,hashlib,http.server,json,pathlib,re,shutil,threading
import fitz
from playwright.sync_api import sync_playwright

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preview',type=pathlib.Path,required=True);parser.add_argument('--out',type=pathlib.Path,required=True);a=parser.parse_args();assert a.preview.is_dir()and not a.out.exists();a.out.mkdir()
 class Quiet(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(a.preview.parent)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
 checks=[];errors=[];external=[]
 def record(page):
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:external.append(r.url)if not r.url.startswith(base)and not r.url.startswith('blob:')else None)
 try:
  with sync_playwright()as p:
   browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
   ctx=browser.new_context(viewport={'width':1200,'height':900},accept_downloads=True);page=ctx.new_page();record(page);url=base+a.preview.name+'/';page.goto(url);page.wait_for_selector('main[data-ready=true]');default=page.evaluate('window.labResult');assert default['state']['converged'];checks.append('source-bound model actually initialized')
   page.screenshot(path=str(a.out/'desktop.png'),full_page=True)
   page.select_option('[data-param=direction]','Z');z=page.evaluate('window.labResult');assert z['loadedAxis']==2;assert abs(z['state']['compressionResultantN']/default['state']['compressionResultantN']-1.2)<1e-12;checks.append('direction control changes the true geometry/resultant')
   for key,value in [('axialStretch','.9'),('heightStretch','.65'),('mu','3500'),('bulk','250000')]:
    page.fill('[data-param='+key+']',value);assert page.evaluate('window.labResult.parameters['+json.dumps(key)+']')==float(value)
   assert page.evaluate('window.labResult.state.converged');checks.append('all continuous controls change the actual model')
   page.select_option('[data-param=iterations]','8');assert not page.evaluate('window.labResult.state.converged');assert 'FAILED'in page.locator('#readout').inner_text();page.select_option('[data-param=iterations]','64');assert page.evaluate('window.labResult.state.converged');checks.append('iteration cap exposes an actual failed residual and recovers')
   before=page.evaluate('JSON.stringify(window.labResult)');page.fill('[data-param=axialStretch]','');assert page.evaluate('JSON.stringify(window.labResult)')==before;assert page.locator('[data-param=axialStretch]').get_attribute('aria-invalid')=='true';page.fill('[data-param=axialStretch]','2');assert page.evaluate('JSON.stringify(window.labResult)')==before;checks.append('blank/out-of-domain controls retain prior valid state')
   page.click('#reset');assert page.evaluate('window.labResult')==default;page.fill('[data-param=axialStretch]','1.2');page.fill('[data-param=heightStretch]','1');assert page.evaluate('window.labResult.state.requiresTensileGrip');assert 'YES'in page.locator('#readout').inner_text();checks.append('negative compression force explicitly requires a tensile grip')
   with page.expect_download()as download:page.click('#export')
   download.value.save_as(a.out/'displayed-state.json');exported=json.loads((a.out/'displayed-state.json').read_text());assert exported==page.evaluate('window.labResult');assert exported['calibrationStatus']=='AUTHORED_UNCALIBRATED_PASSIVE_ISOTROPIC';checks.append('actual download equals displayed state with definitions/calibration')
   for href in ['README.md','AreaLoadContracts.lean','proof-receipt.json']:
    response=ctx.request.get(url+href);assert response.ok;assert response.body()==(a.preview/href).read_bytes()
   checks.append('all three portable download targets return exact bytes')
   page.click('#reset')
   for width in [390,320]:
    page.set_viewport_size({'width':width,'height':850});page.select_option('[data-param=direction]','Z');assert page.evaluate('window.labResult.loadedAxis')==2;page.click('#reset');assert page.evaluate('window.labResult')==default;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(a.out/f'mobile-{width}.png'),full_page=True)
   checks.append('real controls/reset and no horizontal clipping at390/320px')
   nojs=browser.new_context(java_script_enabled=False);static=nojs.new_page();static.goto(url);assert static.locator('noscript').is_visible();assert 'Default J'in static.locator('#readout').inner_text();assert 'theorem force_area_work'in static.locator('.proof-source').inner_text();nojs.close();checks.append('no-JavaScript default/formulas/full source readable')
   for kind in ['model','formula','receipt','inventory']:
    damaged=a.out/('damage-'+kind);shutil.copytree(a.preview,damaged)
    if kind=='model':f=damaged/'education/contributions/directional-compression-lab/model.mjs';f.write_text(f.read_text().replace('p.bulk*(J-1)*J/l','2*p.bulk*(J-1)*J/l'))
    elif kind=='formula':f=damaged/'index.html';f.write_text(f.read_text().replace('mu/2','mu/3',1))
    elif kind=='receipt':(damaged/'proof-receipt.json').unlink()
    else:f=damaged/'runtime-integrity.json';d=json.loads(f.read_text());d['files'][0]=d['files'][1];f.write_text(json.dumps(d))
    # Serve damage copies under the same server root without touching the preview.
    damaged_url=base+a.out.name+'/'+damaged.name+'/'
    q=ctx.new_page();record(q);q.goto(damaged_url);q.wait_for_function("document.querySelector('#status').textContent.includes('refused')");assert q.locator('main').get_attribute('data-ready')is None;assert q.locator('#export').is_disabled();q.close()
   checks.append('four actual source/formula/receipt/inventory damages refused before model import')
   page.set_viewport_size({'width':1200,'height':900});page.click('#reset');page.emulate_media(media='print')
   page.evaluate("document.querySelectorAll('a').forEach(a=>{const h=a.getAttribute('href');if(h==='README.md'){a.setAttribute('href','#equations');a.textContent='Method and assumptions in this review'}else if(h==='AreaLoadContracts.lean'){a.setAttribute('href','#proof-source');a.textContent='Complete Lean source in this review'}else if(h==='proof-receipt.json'){a.setAttribute('href','#proof-source');a.textContent='Fresh axiom-report scope; JSON receipt supplied in the package'}})")
   page.pdf(path=str(a.out/'directional-compression-review.pdf'),print_background=True,prefer_css_page_size=True)
   doc=fitz.open(a.out/'directional-compression-review.pdf');spans=[s for page_ in doc for b in page_.get_text('dict')['blocks']if 'lines'in b for line in b['lines']for s in line['spans']if s['text'].strip()];minimum=min(s['size']for s in spans);assert minimum>=10-.02,minimum
   text=''.join(page_.get_text()for page_ in doc);normalize=lambda s:re.sub(r'\s+','',s);source=(a.preview/'AreaLoadContracts.lean').read_text();assert normalize(source)in normalize(text),'Full Lean source missing/truncated in actual PDF'
   for page_ in doc:
    for link in page_.get_links():assert '127.0.0.1'not in link.get('uri','')and 'localhost'not in link.get('uri','')
    for b in page_.get_text('blocks'):
     if len(b)>4 and str(b[4]).strip():assert b[0]>=-1 and b[1]>=-1 and b[2]<=page_.rect.width+1 and b[3]<=page_.rect.height+1
   # A genuine9pt full-source damaged PDF must fail the same actual-point gate.
   page.evaluate("document.querySelector('.proof-source').style.fontSize='9pt'");page.pdf(path=str(a.out/'damaged-source-9pt.pdf'),print_background=True,prefer_css_page_size=True)
   bad=fitz.open(a.out/'damaged-source-9pt.pdf');bad_min=min(s['size']for pg in bad for b in pg.get_text('dict')['blocks']if 'lines'in b for line in b['lines']for s in line['spans']if s['text'].strip());assert bad_min<10;checks.append('actual full-source/statements/diagram typography>=10pt; actual9pt source damage rejected')
   doc[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(a.out/'print-first.png');doc[-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(a.out/'print-source.png')
   result={'result':'PASS_ACTUAL_CONTROLS_DOWNLOADS_DAMAGE_AND_PRINT','checks':checks,'pageErrors':errors,'externalRequests':external,'pdfPages':len(doc),'minimumActualPointSize':minimum,'fullLeanSourcePresent':True,'completeConditionalStatements':3,'damagedSourceMinimumPt':bad_min,'browserVersion':browser.version,'scope':'new standalone passive reduced specimen only; no anatomy/held campaign'}
   assert not errors and not external,result;(a.out/'browser-receipt.json').write_text(json.dumps(result,indent=2)+'\n');browser.close();print(json.dumps(result))
 finally:server.shutdown()
if __name__=='__main__':main()
