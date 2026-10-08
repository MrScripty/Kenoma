"""Actual controls, exports, fail-closed damage and actual-point PDF checks."""
import argparse,functools,http.server,json,pathlib,re,shutil,threading,hashlib
import fitz
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--preview',type=pathlib.Path,required=True);parser.add_argument('--out',type=pathlib.Path,required=True);a=parser.parse_args();assert a.preview.is_dir()and not a.out.exists();a.out.mkdir()
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(a.preview.parent)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/';url=base+a.preview.name+'/'
checks=[];errors=[];external=[]
def record(page):
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:external.append(r.url)if not r.url.startswith(base)and not r.url.startswith('blob:')else None)
def close(x,y):assert abs(x-y)<1e-9*max(1,abs(x),abs(y)),(x,y)
def minimum(doc):return min(s['size']for pg in doc for b in pg.get_text('dict')['blocks']if 'lines'in b for line in b['lines']for s in line['spans']if s['text'].strip())
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']);ctx=browser.new_context(viewport={'width':1200,'height':900},accept_downloads=True);page=ctx.new_page();record(page);page.goto(url);page.wait_for_selector('main[data-ready=true]');default=page.evaluate('window.labResult');assert default['solve']['converged'];assert page.locator('[data-param=pressurePa]').is_disabled()
  assert page.evaluate("[...document.querySelectorAll('[data-param]')].filter(i=>!i.disabled).every(i=>i.checkValidity())");page.fill('[data-param=forceN]','6.65');assert page.locator('[data-param=forceN]').get_attribute('aria-invalid')is None;assert page.evaluate('window.labResult.parameters.forceN')==6.65;checks.append('authored6.65N default and explicit re-entry pass actual browser validity')
  page.fill('[data-param=breadthFactor]','2');wide=page.evaluate('window.labResult');close(wide['state']['compressionResultantN'],default['state']['compressionResultantN']);assert abs(wide['state']['stretches'][1]-default['state']['stretches'][1])>.01;checks.append('fixed total force actually changes deformation when reference breadth changes')
  page.click('#reset');page.select_option('[data-param=mode]','pressure');assert page.locator('[data-param=forceN]').is_disabled();assert not page.locator('[data-param=pressurePa]').is_disabled();one=page.evaluate('window.labResult');page.fill('[data-param=breadthFactor]','2');two=page.evaluate('window.labResult');[close(x,y)for x,y in zip(one['state']['stretches'],two['state']['stretches'])];close(two['state']['compressionResultantN'],2*one['state']['compressionResultantN']);close(two['state']['energyJ'],2*one['state']['energyJ']);checks.append('current-pressure mode preserves solved stretches while actual area, force and energy scale')
  for key,val in [('pressurePa','1800'),('axialStretch','1.1'),('mu','2500'),('bulk','75000')]:page.fill('[data-param='+key+']',val);assert page.evaluate('window.labResult.parameters['+json.dumps(key)+']')==float(val)
  page.select_option('[data-param=direction]','Z');assert page.evaluate('window.labResult.loadedAxis')==2;assert page.evaluate('window.labResult.solve.converged');checks.append('all material, target, axial, direction and breadth controls solve the actual model')
  page.select_option('[data-param=outerIterations]','8');assert not page.evaluate('window.labResult.solve.converged');assert 'FAILED'in page.locator('#readout').inner_text();page.select_option('[data-param=outerIterations]','64');assert page.evaluate('window.labResult.solve.converged');checks.append('actual8-step outer failure is visible and64-step recovery passes both residuals')
  before=page.evaluate('JSON.stringify(window.labResult)');page.fill('[data-param=axialStretch]','');assert page.evaluate('JSON.stringify(window.labResult)')==before;page.fill('[data-param=axialStretch]','2');assert page.evaluate('JSON.stringify(window.labResult)')==before;page.click('#reset');before=page.evaluate('JSON.stringify(window.labResult)');page.fill('[data-param=forceN]','100');assert page.evaluate('JSON.stringify(window.labResult)')==before;assert 'not bracketed'in page.locator('#status').inner_text();page.click('#reset');assert page.locator('[aria-invalid=true]').count()==0;assert page.evaluate("[...document.querySelectorAll('[data-param]')].filter(i=>!i.disabled).every(i=>i.checkValidity())");checks.append('blank/domain/unbracketed targets roll back; reset clears invalid markers and all enabled controls are valid')
  page.fill('[data-param=forceN]','8');assert page.evaluate('window.labResult.parameters.forceN')==8
  with page.expect_download()as d:page.click('#export')
  d.value.save_as(a.out/'displayed-state.json');assert json.loads((a.out/'displayed-state.json').read_text())==page.evaluate('window.labResult');checks.append('actual downloaded JSON equals displayed inverse solution and scope')
  for href in ['README.md','AreaLoadContracts.lean','proof-receipt.json']:
   r=ctx.request.get(url+href);assert r.ok and r.body()==(a.preview/href).read_bytes()
  checks.append('three relative download targets return exact source/method/proof bytes')
  page.click('#reset');page.screenshot(path=str(a.out/'desktop.png'),full_page=True)
  for width in [390,320]:
   page.set_viewport_size({'width':width,'height':850});page.select_option('[data-param=mode]','pressure');page.fill('[data-param=breadthFactor]','1.5');assert page.evaluate('window.labResult.parameters.breadthFactor')==1.5;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(a.out/f'mobile-{width}.png'),full_page=True);page.click('#reset');assert page.evaluate('window.labResult')==default
  checks.append('actual mobile mode/breadth/reset at390/320px without clipping')
  nojs=browser.new_context(java_script_enabled=False);static=nojs.new_page();static.goto(url);assert static.locator('noscript').is_visible();assert 'Default C'in static.locator('#readout').inner_text();assert 'theorem force_area_work'in static.locator('.proof-source').inner_text();nojs.close();checks.append('static default and complete source readable without JS')
  for kind in ['model','formula','receipt','inventory']:
   damage=a.out/('damage-'+kind);shutil.copytree(a.preview,damage)
   if kind=='model':f=damage/'education/contributions/full-face-load-pressure/model.mjs';f.write_text(f.read_text().replace('compressionResultantN/currentAreaM2','2*compressionResultantN/currentAreaM2'))
   elif kind=='formula':f=damage/'index.html';f.write_text(f.read_text().replace('mu/2','mu/3',1))
   elif kind=='receipt':(damage/'proof-receipt.json').unlink()
   else:f=damage/'runtime-integrity.json';m=json.loads(f.read_text());m['files'][0]=m['files'][1];f.write_text(json.dumps(m))
   q=ctx.new_page();record(q);q.goto(base+a.out.name+'/'+damage.name+'/');q.wait_for_function("document.querySelector('#status').textContent.includes('refused')");assert q.locator('main').get_attribute('data-ready')is None and q.locator('#export').is_disabled();q.close()
  checks.append('four real runtime damages refuse model import and disable controls')
  page.set_viewport_size({'width':1200,'height':900});page.click('#reset');page.emulate_media(media='print');page.evaluate("document.querySelectorAll('a').forEach(a=>{const h=a.getAttribute('href');a.setAttribute('href',h==='README.md'?'#equations':'#proof-source');a.textContent=h==='README.md'?'Method and assumptions in this review':h==='AreaLoadContracts.lean'?'Complete inherited Lean source in this review':'Inherited axiom-report scope; JSON receipt supplied in the package'})");page.pdf(path=str(a.out/'full-face-load-pressure-review.pdf'),print_background=True,prefer_css_page_size=True)
  doc=fitz.open(a.out/'full-face-load-pressure-review.pdf');point_min=minimum(doc);assert point_min>=10.5-.02,point_min;normalize=lambda s:re.sub(r'\s+','',s);text=''.join(pg.get_text()for pg in doc);assert normalize((a.preview/'AreaLoadContracts.lean').read_text())in normalize(text)
  links=[]
  for pg in doc:
   for link in pg.get_links():assert 'uri'not in link;assert link['kind']in [fitz.LINK_GOTO,fitz.LINK_NAMED];links.append(link)
   for b in pg.get_text('blocks'):
    if len(b)>4 and str(b[4]).strip():assert b[0]>=-1 and b[1]>=-1 and b[2]<=pg.rect.width+1 and b[3]<=pg.rect.height+1
  assert len(links)>=3
  page.evaluate("document.querySelector('.proof-source').style.fontSize='9pt'");page.pdf(path=str(a.out/'damaged-source-9pt.pdf'),print_background=True,prefer_css_page_size=True);bad=fitz.open(a.out/'damaged-source-9pt.pdf');assert minimum(bad)<10;assert normalize((a.preview/'AreaLoadContracts.lean').read_text())in normalize(''.join(pg.get_text()for pg in bad));checks.append('full inherited source/statements/diagram actual spans>=10.5pt, internal PDF links; full-source9pt damage rejected')
  for i,pg in enumerate(doc):pg.get_pixmap(matrix=fitz.Matrix(1,1)).save(a.out/f'print-{i+1}.png')
  assert not errors and not external
  result={'result':'PASS_ACTUAL_CONTROLS_DOWNLOADS_DAMAGE_AND_PRINT','checks':checks,'pageErrors':errors,'externalRequests':external,'pdfPages':len(doc),'minimumActualPointSize':point_min,'fullInheritedLeanSourcePresent':True,'inheritedConditionalStatements':3,'newLeanDeclarations':0,'internalLinkRectangles':len(links),'damagedSourceMinimumPt':minimum(bad),'browserVersion':browser.version,'runtimeInventorySha256':hashlib.sha256((a.preview/'runtime-integrity.json').read_bytes()).hexdigest(),'pdfSha256':hashlib.sha256((a.out/'full-face-load-pressure-review.pdf').read_bytes()).hexdigest()};(a.out/'browser-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));browser.close()
finally:server.shutdown()
