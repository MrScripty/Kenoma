"""Deterministic queued-work/reset and worker-error regressions in actual UI bundles.
Native workers handle init/reset. Step responses are deliberately held to expose
request lifecycle races without accepting a numerical step or changing time.
"""
from pathlib import Path
import hashlib,json,os,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import serve
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PROBE='''const NativeWorker=Worker;window.workerProbe={workers:[],posts:[],holdSteps:false};
globalThis.Worker=class extends NativeWorker{
 constructor(...args){super(...args);workerProbe.workers.push(this);}
 postMessage(message,...args){workerProbe.posts.push(structuredClone(message));if(message.kind==='step'&&workerProbe.holdSteps)return;return super.postMessage(message,...args);}
};'''
def run():
    out=ROOT/'dist/worker-lifecycle-review';out.mkdir(parents=True,exist_ok=True)
    server,url=serve();results=[]
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for case in ['coupled-queued-reset','anatomical-worker-error']:
          page=browser.new_page();page.set_default_timeout(60000);page.add_init_script(PROBE)
          try:
            if case=='coupled-queued-reset':
              page.goto(url+'/coupled-fixture/index.html');page.wait_for_function('window.coupledReady')
              original=page.evaluate('coupledApi.state')
              result=page.evaluate('''async()=>{workerProbe.holdSteps=true;document.querySelector('#step').click();await Promise.resolve();await Promise.resolve();document.querySelector('#step').click();document.querySelector('#reset').click();const settled=await Promise.race([coupledApi.idle().then(()=>true),new Promise(r=>setTimeout(()=>r(false),2500))]);return {settled,state:coupledApi.state,rows:coupledApi.rows,posts:workerProbe.posts};}''')
              assert result['settled'],'reset idle is blocked by stale queued work'
              assert result['state']==original and result['rows']==[], 'reset changed state/time or retained stale rows'
              steps=[x for x in result['posts'] if x['kind']=='step']
              assert len(steps)==1 and steps[0]['epoch']==0, 'queued pre-reset step emitted under a new epoch: '+str(steps)
              detail={'settled':True,'staleStepsSuppressed':True,'stateAndTimeRetained':True,'stepRequests':steps}
            else:
              page.goto(url+'/anatomical-arm/index.html');page.wait_for_function('window.anatomicalArmReady')
              original=page.evaluate('anatomicalArmApi.state')
              result=page.evaluate('''async()=>{workerProbe.holdSteps=true;document.querySelector('#step').click();await Promise.resolve();await Promise.resolve();workerProbe.workers.at(-1).onerror({message:'Injected worker failure'});const settled=await Promise.race([anatomicalArmApi.idle().then(()=>true),new Promise(r=>setTimeout(()=>r(false),2500))]);return {settled,state:anatomicalArmApi.state,rows:anatomicalArmApi.rows,status:document.querySelector('#status').textContent};}''')
              assert result['settled'],'worker error leaves pending request and queue unresolved'
              assert result['state']==original and result['rows']==[], 'failed worker advanced state/time or accepted a row'
              assert 'Reset' in result['status'] and 'Injected worker failure' in result['status'], 'failure lacks recoverable guidance'
              page.locator('#step').click();page.evaluate('()=>anatomicalArmApi.idle()')
              assert page.evaluate('anatomicalArmApi.state')==original
              page.locator('#reset').click();page.evaluate('()=>anatomicalArmApi.idle()')
              assert page.evaluate('anatomicalArmApi.state')==original
              assert page.evaluate('workerProbe.workers.length')==2
              assert 'reset complete' in page.locator('#status').inner_text()
              detail={'settled':True,'stateAndTimeRetained':True,'unavailableWorkerRejectsWithoutHang':True,'resetRestartsNativeWorker':True,'failureStatus':result['status']}
            results.append({'case':case,'passed':True,**detail})
          except Exception as error:
            results.append({'case':case,'passed':False,'error':str(error)})
          finally:page.close()
        version=browser.version;browser.close()
    finally:server.shutdown();server.server_close()
    receipt={'result':'PASS_WORKER_LIFECYCLE' if all(x['passed'] for x in results) else 'FAIL_WORKER_LIFECYCLE','browserVersion':version,'sourceHashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['tools/coupled-inspector.mjs','tools/anatomical-arm-inspector.mjs','tests/worker_lifecycle.py']},'rows':results,'scope':'Injected held step/error events exercising actual bundled UI; native worker init/reset; no numerical lift/release qualification.'}
    (out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['result']=='PASS_WORKER_LIFECYCLE'
if __name__=='__main__':run()
