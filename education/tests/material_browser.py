"""Actual controls, fixed physical geometry, failure retention, mobile and print."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import hashlib,json,os,shutil,subprocess,sys
import fitz
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def check(destination):
    out=Path(destination).resolve();qa=out/'material-qa';qa.mkdir(exist_ok=True)
    preview=(out/'material-preview-manifest.json').exists();manifest='material-preview-manifest.json' if preview else 'build-manifest.json'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(out)))
    Thread(target=server.serve_forever,daemon=True).start()
    checks=[];observed={};errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page=browser.new_page(viewport={'width':1200,'height':1000})
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            lab=page.locator('[data-material=compression]');expect(lab).to_have_attribute('data-enhanced','true')
            if preview:assert page.locator('.proof-card').count()==5
            def state():
                lab.locator('[data-action=copy]').click();data=json.loads(lab.locator('.preset').input_value())
                lab.locator('.preset').evaluate('(x)=>x.hidden=true')
                return data
            def change(key,value):lab.locator(f'input[type=number][data-param={key}]').fill(str(value))
            def width(boundary):return float(lab.locator(f'g[data-boundary={boundary}] .specimen').get_attribute('width'))
            def capture(name):
                lab.locator('.property-scene').screenshot(path=str(qa/(name+'.png')))
                observed[name]=state()
            default=state()
            assert default['free']['converged'] and default['confined']['converged']
            assert abs(default['free']['J']-.9939144716354632)<1e-12
            assert abs(default['confined']['J']-.8)<1e-12
            fw,cw=width('free'),width('confined');assert abs(fw/cw-default['free']['b'])<1e-12
            capture('default-desktop')
            lab.locator('.controls').screenshot(path=str(qa/'controls-desktop.png'))
            lab.locator('.readout').screenshot(path=str(qa/'readout-desktop.png'))
            lab.locator('[data-action=candidate]').click()
            expect(lab.locator('.announce')).to_contain_text('Rejected isochoric wall candidate')
            assert state()==default
            checks.append('Positive-J isochoric wall penetration rejected through actual button; solved state retained')
            change('bulk',250000);high=state();assert high['free']['J']>default['free']['J']
            assert high['confined']['plateForceN']>default['confined']['plateForceN']
            assert high['free']['heightM']==high['confined']['heightM']==default['free']['heightM']
            assert width('confined')==cw and width('free')>fw
            capture('high-bulk-desktop')
            change('bulk',50000);change('mu',5000);stiff=state()
            assert stiff['free']['J']<default['free']['J'] and stiff['free']['plateForceN']>default['free']['plateForceN']
            assert stiff['free']['heightStretch']==default['free']['heightStretch']
            checks.append('Bulk and shear controls change the named material parameter at shared height; forces, volume and actual SVG widths respond')
            lab.locator('[data-action=reset]').click()
            slider=lab.locator('input[type=range][data-param=heightStretch]')
            slider.evaluate('(x)=>{x.value="0.6";x.dispatchEvent(new Event("input",{bubbles:true}))}')
            assert state()['parameters']['heightStretch']==.6
            expect(lab.locator('input[type=number][data-param=heightStretch]')).to_have_value('0.6')
            assert abs(float(lab.locator('g[data-boundary=free] .specimen').get_attribute('height'))/.6-2400*.06)<1e-10
            lab.locator('[data-action=reset]').click();change('bulk',0);zero=state()
            assert abs(zero['free']['J']-.512)<1e-12 and zero['free']['b']==.8
            assert abs(zero['free']['plateForceN'])<1e-12 and not zero['confined']['wallActive']
            assert width('free')==width('confined')<cw
            expect(lab.locator('.readout')).to_contain_text('pull-away allowed')
            capture('zero-bulk-desktop')
            change('bulk',500);weak=state();assert weak['confined']['gapXM']>0 and weak['confined']['wallReactionPa']==0
            capture('weak-bulk-desktop')
            checks.append('Actual zero-bulk counterexample and weak-bulk pull-away; geometry shrinks at the fixed reference scale')
            lab.locator('[data-action=reset]').click();lab.locator('select[data-param=iterations]').select_option('8')
            coarse=state();assert coarse['free']['accepted'] and not coarse['free']['converged']
            expect(lab.locator('.readout')).to_contain_text('finite approximation; residual criterion NOT met')
            capture('coarse-desktop')
            lab.locator('select[data-param=iterations]').select_option('32')
            assert state()['free']['converged']
            checks.append('Finite approximation visibly fails residual criterion, then improves with actual bisection control')
            before=state()
            for value in ['', '0', '-0.5', '1.1']:
                change('heightStretch',value)
                expect(lab.locator('input[type=number][data-param=heightStretch]')).to_have_attribute('aria-invalid','true')
                assert state()==before
            for key,value in [('mu','0'),('bulk','-500'),('bulk','250500')]:
                change(key,value);expect(lab.locator(f'input[type=number][data-param={key}]')).to_have_attribute('aria-invalid','true')
                assert state()==before
            lab.locator('select[data-param=iterations]').evaluate('(x)=>{x.add(new Option("invalid","7"));x.value="7";x.dispatchEvent(new Event("input",{bubbles:true}))}')
            assert state()==before;expect(lab.locator('select[data-param=iterations]')).to_have_attribute('aria-invalid','true')
            lab.locator('[data-action=reset]').click();assert state()==default
            assert lab.locator('[aria-invalid=true]').count()==0
            change('heightStretch',1);restored=state()
            assert restored['free']['J']==restored['confined']['J']==1
            assert restored['free']['energyJ']==restored['confined']['energyJ']==0
            lab.locator('[data-action=candidate]').click();expect(lab.locator('.announce')).to_contain_text('fits the walls')
            lab.locator('[data-action=reset]').click();lab.locator('[data-action=summary]').click()
            expect(lab.locator('.announce')).to_contain_text('Plate force')
            checks.append('Invalid/blank/out-of-domain controls retain prior state; reset clears errors; height restoration is elastic and history-free')
            page.set_viewport_size({'width':393,'height':852});lab.scroll_into_view_if_needed()
            expect(lab.locator('svg')).to_have_attribute('viewBox','0 0 440 800')
            assert lab.evaluate('(x)=>x.scrollWidth<=x.clientWidth+1')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            capture('default-mobile')
            assert abs(width('free')/width('confined')-default['free']['b'])<1e-12
            page.emulate_media(media='print')
            expect(lab.locator('.property-scene')).to_be_hidden()
            expect(lab.locator('.static-figure')).to_be_visible()
            checks.append('Mobile stacks panels without changing physical scale; print uses solved static figure')
            if preview:
                revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
                page.evaluate('''revision=>{
                  const targets={'proofs/MaterialResponse.lean':'#material-source-appendix','material-proof-status.json':'#material-proof-receipt','material-lean-check.txt':'#material-kernel-report'};
                  for(const a of document.querySelectorAll('a[href]')){
                    const h=a.getAttribute('href');if(targets[h])a.setAttribute('href',targets[h]);
                    else if(h.startsWith('web/'))a.setAttribute('href','https://github.com/MrScripty/Kenoma/blob/'+revision+'/education/'+h);
                  }
                }''',revision)
                page.pdf(path=str(out/'material-response.pdf'),format='A4',print_background=True,tagged=True,outline=True)
                with fitz.open(out/'material-response.pdf') as pdf:
                    text='\n'.join(p.get_text() for p in pdf)
                    assert '0.993914' in text and '42.0887' in text
                    assert 'Complete checked material source' in text and 'Kernel report' in text
                    assert all('127.0.0.1' not in link.get('uri','') for p in pdf for link in p.get_links())
                checks.append('Standalone PDF retains solved values, narrow contracts, full checked source and durable links')
            version=browser.version;browser.close()
            browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page=browser.new_page(java_script_enabled=False)
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
            image=page.locator('[data-material] .static-figure img')
            expect(image).to_be_visible();assert image.evaluate('(x)=>x.complete&&x.naturalWidth>0')
            browser.close();checks.append('Zero-JavaScript default diagram and derivation remain available')
            assert not errors,errors
    finally:server.shutdown();server.server_close()
    (qa/'observed.json').write_text(json.dumps(observed,indent=2)+'\n')
    receipt={'schema':1,'result':'PASS_MATERIAL_PREVIEW_BROWSER' if preview else 'PASS_INTEGRATED_MATERIAL_BROWSER','browserVersion':version,'checks':checks,'javascriptErrors':errors,
             'manifest':manifest,'manifestSHA256':digest(out/manifest),'HTMLSHA256':digest(out/'index.html'),
             'sourceHashes':{p:digest(ROOT/p) for p in ['web/material-lab.mjs','web/material-response.mjs','web/tissue.mjs','tools/material_lab.py','tests/material_browser.py']},
             'outputs':{p.name:digest(p) for p in sorted(qa.iterdir()) if p.is_file() and p.name!='browser-check.json'}}
    receipt['appSHA256']=digest(out/'assets/app.js')
    if preview:receipt['PDFSHA256']=digest(out/'material-response.pdf')
    (qa/'browser-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['result']);print('\n'.join(checks))
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist')
