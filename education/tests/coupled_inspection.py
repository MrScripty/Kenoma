"""Native worker, control, reset and drawing checks. No GPU override flags."""
from pathlib import Path
import hashlib,json,os,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import serve
from executable_outputs import executable_outputs,unchanged_outputs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def run():
    checked_executables=executable_outputs(ROOT/'dist','coupled-fixture')
    out=ROOT/'dist/coupled-review';out.mkdir(parents=True,exist_ok=True)
    server,url=serve();results=[]
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for label,width,height in [('desktop',1200,1050),('mobile-emulation',393,852)]:
          page=browser.new_page(viewport={'width':width,'height':height});page.set_default_timeout(60000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
          page.goto(url+'/coupled-fixture/index.html');page.wait_for_function('window.coupledReady===true')
          assert page.locator('#proofs details').count()==8
          page.locator('#proofs details').last.locator('summary').click()
          assert sum(line.startswith('theorem ') for line in page.locator('#proofs pre').inner_text().splitlines())==7
          assert page.locator('canvas').count()==0
          page.locator('#start').click();page.wait_for_function('document.querySelector("canvas")?.width>0')
          page.locator('#scene').screenshot(path=str(out/(label+'-rest.png')))
          for i in range(7):
            page.locator('#step').click();page.evaluate('()=>coupledApi.idle()')
          loaded=page.evaluate('coupledApi.state');assert loaded['steps']==7 and loaded['q']>.6
          page.locator('#scene').screenshot(path=str(out/(label+'-loaded.png')))
          page.locator('#release').click();before=page.evaluate('coupledApi.state');assert before==loaded
          for i in range(5):page.locator('#step').click();page.evaluate('()=>coupledApi.idle()')
          released=page.evaluate('coupledApi.state');assert released['activation']<loaded['activation'] and released['q']<loaded['q']
          page.locator('#scene').screenshot(path=str(out/(label+'-released.png')))
          page.locator('#mass').evaluate('(el)=>{el.value=1;el.dispatchEvent(new Event("input",{bubbles:true}));}');page.evaluate('()=>coupledApi.idle()')
          changed=page.evaluate('coupledApi.state');assert changed['massKg']==1 and len(changed['events'])==1
          for key in ['q','omega','timeS','activation','positions']:assert changed[key]==released[key]
          page.locator('#reset').click();page.evaluate('()=>coupledApi.idle()');reset=page.evaluate('coupledApi.state');assert reset['steps']==0 and reset['q']==0 and reset['activation']==0 and reset['massKg']==.5
          page.locator('#step').click();page.evaluate('()=>coupledApi.idle()');first=page.evaluate('coupledApi.state')
          page.locator('#reset').click();page.evaluate('()=>coupledApi.idle()');page.locator('#step').click();page.evaluate('()=>coupledApi.idle()');assert first==page.evaluate('coupledApi.state')
          page.locator('#play').click();page.locator('#mass').evaluate('(el)=>{el.value=1;el.dispatchEvent(new Event("input",{bubbles:true}));}')
          page.wait_for_function('coupledApi.state.massKg===1');assert page.evaluate('coupledApi.state.steps')<24
          page.locator('#play').click();page.evaluate('()=>coupledApi.idle()')
          assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
          assert not errors,errors
          results.append({'viewport':label,'loadedQ':loaded['q'],'releasedQ':released['q'],'loadedActivation':loaded['activation'],'releasedActivation':released['activation'],'resetExactInRuntime':True,'massStatePreserved':True,'massEventDuringPlayback':True,'visibleCompiledClaims':7,'workerTraceRows':len(page.evaluate('coupledApi.rows')),'browserErrors':errors,'limit':'Mobile emulation, not a real phone; authored fixture, not anatomical capstone.'})
          page.close()
        page=browser.new_page(viewport={'width':393,'height':852});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script('const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...args){return kind.startsWith("webgl")?null:original.call(this,kind,...args);};')
        page.goto(url+'/coupled-fixture/index.html');page.wait_for_function('window.coupledReady');page.locator('#start').click()
        assert '3D unavailable' in page.locator('#status').inner_text()
        page.locator('#step').click();page.evaluate('()=>coupledApi.idle()');assert page.evaluate('coupledApi.state.steps')==1
        assert not errors,errors
        results.append({'viewport':'mobile-no-WebGL-fault','numericalWorkerContinues':True,'browserErrors':errors,'limit':'Injected unavailable context, not a GPU configuration override.'})
        page.close()
        version=browser.version;browser.close()
    finally:server.shutdown();server.server_close()
    unchanged_outputs(ROOT/'dist',checked_executables,'coupled-fixture')
    receipt={'executable_outputs':checked_executables,'result':'PASS','browserVersion':version,'sourceHashes':{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in ['web/anatomical-coupled-fixture.mjs','web/anatomical-coupled-worker.mjs','tools/coupled-inspector.mjs']},'rows':results}
    (out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'result':'PASS','output':str(out)}))
if __name__=='__main__':run()
