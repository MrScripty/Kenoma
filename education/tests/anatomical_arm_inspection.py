"""Browser acceptance of the actual-arm rest and reversible controls.
No successful loaded trajectory is asserted by this UI check.
"""
from pathlib import Path
import hashlib,json,os,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import serve
from executable_outputs import executable_outputs,unchanged_outputs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def run():
    checked_executables=executable_outputs(ROOT/'dist','anatomical-arm')
    out=ROOT/'dist/anatomical-arm-review';out.mkdir(parents=True,exist_ok=True)
    server,url=serve();results=[]
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for label,width,height in [('desktop',1200,1050),('mobile-emulation',393,852)]:
          page=browser.new_page(viewport={'width':width,'height':height});page.set_default_timeout(60000);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
          page.goto(url+'/anatomical-arm/index.html');page.wait_for_function('window.anatomicalArmReady===true')
          assert page.locator('#proofs details').count()==5
          page.locator('#proofs details').last.locator('summary').click()
          assert sum(s.startswith('theorem ') for s in page.locator('#proofs pre').inner_text().splitlines())==4
          assert page.locator('#heads tr').count()==7
          assert page.locator('canvas').count()==0
          original=page.evaluate('anatomicalArmApi.state');receipt=page.evaluate('anatomicalArmApi.receipt')
          assert receipt['maximumFreeModalGradientN']<=1e-4 and receipt['surfaceAudit']['transverseCrossingPairs']==0 and receipt['routingAudit']['accepted']
          page.locator('#start').click();page.wait_for_function('document.querySelector("canvas")?.width>0')
          page.locator('#scene').screenshot(path=str(out/(label+'-rest.png')))
          page.locator('#effort').evaluate('(el)=>{el.value=.08;el.dispatchEvent(new Event("input",{bubbles:true}));}')
          assert page.evaluate('anatomicalArmApi.state')==original
          page.locator('#release').click();assert page.evaluate('anatomicalArmApi.state')==original
          page.locator('#mass').evaluate('(el)=>{el.value=1;el.dispatchEvent(new Event("input",{bubbles:true}));}')
          page.wait_for_function('anatomicalArmApi.state.massKg===1')
          changed=page.evaluate('anatomicalArmApi.state')
          for key in ['qRad','omegaRadPerS','timeS','activation','coordinatesM']:assert changed[key]==original[key]
          assert len(changed['massEvents'])==1
          page.locator('#reset').click();page.evaluate('()=>anatomicalArmApi.idle()');assert page.evaluate('anatomicalArmApi.state')==original
          # Termination interrupts an in-flight expensive solve and prevents stale updates.
          page.locator('#step').click();page.wait_for_function('document.querySelector("#status").textContent.includes("Solving")')
          page.locator('#reset').click();page.evaluate('()=>anatomicalArmApi.idle()');assert page.evaluate('anatomicalArmApi.state')==original
          assert page.evaluate('anatomicalArmApi.rows.length')==0
          assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
          assert not errors,errors
          results.append({'viewport':label,'restResidualN':receipt['maximumFreeModalGradientN'],'visibleCompiledClaims':4,'headRows':7,'massStatePreserved':True,'releaseStatePreserved':True,'resetExactInRuntime':True,'busyResetWorkerTerminated':True,'browserErrors':errors,'limits':'Rest/control acceptance only. Mobile emulation, not a physical phone. This browser check does not execute a full anatomical lift/release trajectory.'})
          page.close()
        page=browser.new_page(viewport={'width':393,'height':852});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script('const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(kind,...args){return kind.startsWith("webgl")?null:original.call(this,kind,...args);};')
        page.goto(url+'/anatomical-arm/index.html');page.wait_for_function('window.anatomicalArmReady');page.locator('#start').click();assert '3D unavailable' in page.locator('#status').inner_text()
        page.locator('#mass').evaluate('(el)=>{el.value=1;el.dispatchEvent(new Event("input",{bubbles:true}));}');page.wait_for_function('anatomicalArmApi.state.massKg===1')
        assert not errors,errors;results.append({'viewport':'mobile-no-WebGL-fault','textMassControlWorks':True,'browserErrors':errors});page.close()
        version=browser.version;browser.close()
    finally:server.shutdown();server.server_close()
    paths=['tools/anatomical-arm-inspector.mjs','tools/build-anatomical-arm-inspector.mjs','web/anatomical-arm-worker.mjs','data/anatomical-arm-v1/audit/arm-rest-recheck.json']
    unchanged_outputs(ROOT/'dist',checked_executables,'anatomical-arm')
    receipt={'executable_outputs':checked_executables,'result':'PASS','browserVersion':version,'sourceHashes':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in paths},'rows':results}
    (out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'result':'PASS','output':str(out)}))
if __name__=='__main__':run()
