from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import argparse,hashlib,json,os,shutil,tempfile
from playwright.sync_api import sync_playwright,expect
import fitz

parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args();out=args.output.resolve()
original=(out/'nonuniform-volume-lab.html').read_text();sha=lambda b:hashlib.sha256(b).hexdigest()
receipt={'scope':'Prescribed finite kinematics only; not a material/equilibrium/anatomical model or new Lean claim.','sourceHTMLSha256':sha(original.encode()),'viewports':[],'negativeControls':[],'authorScheduleRuns':0}
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
with tempfile.TemporaryDirectory(dir=out) as directory:
    root=Path(directory);(root/'lab.html').write_text(original)
    for name in ['NonuniformIsochoric.lean','claims.json','nonuniform-proof-status.json','nonuniform-lean-check.txt','model-audit.json']:
        shutil.copyfile(out/name,root/name)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}'
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for name,width,height in [('desktop',1200,1000),('mobile',390,844),('narrow',320,800)]:
            page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda error:errors.append(str(error)));page.goto(url+'/lab.html',wait_until='networkidle')
            state=lambda:page.evaluate('KinematicLab.state()')
            s=state();assert all(abs(x-1)<1e-12 for x in s['pointwiseJRange'])
            assert page.locator('.real-contract').count()==6
            for href in page.locator('.downloads a').evaluate_all('(els)=>els.map(a=>a.getAttribute("href"))'):
                assert not href.startswith('/') and page.request.get(url+'/'+href).status==200,href
            assert abs(s['independentMeshMeasurementError'])<1e-17
            before=s['parameters'];page.locator('#mean').fill('');expect(page.locator('#error')).not_to_be_empty();assert state()['parameters']==before
            page.locator('#reset').click();expect(page.locator('#error')).to_be_empty()
            page.locator('#compensate').uncheck();s=state();assert abs(s['meshVolumeRatio']-1)<1e-12
            assert abs(s['pointwiseJRange'][0]-.6)<1e-12 and abs(s['pointwiseJRange'][1]-1.4)<1e-12
            assert s['rows'][0]['cellVolumeRatio']<.7 and s['rows'][-1]['cellVolumeRatio']>1.3
            page.locator('#compensate').check();page.locator('#cells').select_option('8');a=abs(state()['relativeMeshVolumeError'])
            page.locator('#cells').select_option('32');b=abs(state()['relativeMeshVolumeError']);assert b<a/15
            page.locator('#gradient').fill('-0.4');s=state();assert s['rows'][0]['lambda']>s['rows'][-1]['lambda']
            page.locator('#mean').fill('1.2');s=state();assert abs(s['continuumVolumeRatio']-1)<1e-12
            page.locator('#reset').click();assert state()['parameters']['mean']==1 and state()['parameters']['gradient']==.4
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            assert not errors,errors;page.screenshot(path=str(out/(name+'.png')),full_page=True)
            receipt['viewports'].append({'name':name,'width':width,'controlsPassed':True,'refinementErrors':[a,b],'horizontalOverflow':False});page.close()
        mutations=[('lost-local-compensation','const b=p.compensate?1/Math.sqrt(lambda):1;','const b=1;'),('lost-uneven-strain','lambda=p.mean*(1+p.gradient*(2*S/p.length-1));','lambda=p.mean;')]
        for name,old,new in mutations:
            assert original.count(old)==1
            raw=original.replace(old,new);(root/'damaged.html').write_text(raw);page=browser.new_page();page.goto(url+'/damaged.html',wait_until='networkidle');s=page.evaluate('KinematicLab.state()')
            detected=any(abs(x-1)>1e-9 for x in s['pointwiseJRange']) if name=='lost-local-compensation' else not (s['centerlineStrainRange'][0]<-.3 and s['centerlineStrainRange'][1]>.3)
            assert detected,name;receipt['negativeControls'].append({'name':name,'detected':True,'mutatedHTMLSha256':sha(raw.encode()),'measuredMeshVolumeRatio':s['meshVolumeRatio'],'pointwiseJRange':s['pointwiseJRange'],'strainRange':s['centerlineStrainRange']});page.close()
        page=browser.new_page(viewport={'width':658,'height':1000});page.goto(url+'/lab.html',wait_until='networkidle');page.emulate_media(media='print');expect(page.locator('.controls')).to_be_hidden();assert page.locator('#shape path').count()>30
        page.evaluate('''for(const a of document.querySelectorAll('[data-print-target]'))a.setAttribute('href','#'+a.dataset.printTarget)''')
        page.pdf(path=str(out/'nonuniform-volume-lab-review.pdf'),format='A4',print_background=True,margin={'top':'18mm','bottom':'18mm','left':'18mm','right':'18mm'});page.close()
        browser.close()
        with fitz.open(out/'nonuniform-volume-lab-review.pdf') as doc:
            spans=[s for page in doc for block in page.get_text('dict')['blocks'] for line in block.get('lines',[]) for s in line['spans'] if s['text'].strip()]
            minimum=min(s['size'] for s in spans);assert minimum>=10,minimum
            assert all('127.0.0.1' not in (link.get('uri') or '') for page in doc for link in page.get_links())
            text=''.join(page.get_text() for page in doc)
            normalize=lambda raw:''.join(raw.split())
            lean=(out/'NonuniformIsochoric.lean').read_text()
            assert normalize(lean) in normalize(text),'Incomplete full Lean source in PDF'
            claims=json.loads((out/'claims.json').read_text())
            for claim in claims:assert normalize(claim['statement_lean']) in normalize(text),claim['id']
            receipt['print']={'pages':len(doc),'minimumActualPt':minimum,'floorPt':10,'controlsHidden':True,'currentGeometryRetained':True,'portableLinks':True,'completeLeanSource':True,'completeRealStatements':len(claims)}
    finally:server.shutdown();server.server_close()
assert (out/'nonuniform-volume-lab.html').read_text()==original
receipt['result']='PASS_ACTUAL_PROPERTY_CONTROLS_INDEPENDENT_VOLUME_LOCALITY_REFINEMENT_AND_DAMAGE'
receipt['outputs']={p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file() and p.name!='browser-receipt.json'}
(out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='outputs'},indent=2))
