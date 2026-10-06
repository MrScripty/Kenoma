"""Actual in-book connected controls, all mobile widths and source-bound evidence."""
from pathlib import Path
import hashlib,json,os,shutil,sys
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from render_pdf import serve
from executable_outputs import checked_build_outputs,unchanged_outputs
from axisymmetric_browser import GPU_TRACK,ready,snap,edit,verify_state,verify_scene
from check_connected_artifact import check
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 out=ROOT/'dist';outputs=checked_build_outputs(out);manifest=sha(out/'build-manifest.json');errors=[];cases=[]
 oracle=json.loads((out/'connected-material-oracle.json').read_text());experiment=json.loads((out/'connected-experiment.json').read_text());server,url=serve()
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium') or pw.chromium.executable_path,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
   context=browser.new_context(viewport={'width':1280,'height':900});context.add_init_script(GPU_TRACK);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(url+'/index.html#connected-passive-specimen',wait_until='networkidle');element=page.locator('iframe[title="Connected passive finite-compliance specimen controls"]');element.scroll_into_view_if_needed()
   page.frame_locator('iframe[title="Connected passive finite-compliance specimen controls"]').locator('[data-axisymmetric]').wait_for()
   frame=next(f for f in page.frames if '/connected-passive/' in f.url);ready(frame);lab=frame.locator('[data-axisymmetric]');lab.locator('[data-action=start]').click();expect(lab).to_have_attribute('data-scene-state','ready')
   for epsilon in ['-0.1','0.1','0']:
    edit(frame,lab,'epsilon',epsilon);state=snap(lab);cases.append({'epsilon':float(epsilon),'state':verify_state(state,oracle,experiment),'scene':verify_scene(frame,state)})
   edit(frame,lab,'epsilon','-0.1');lab.locator('[data-setting=cap]').select_option('1');ready(frame);expect(lab).to_have_attribute('data-converged','false');lab.locator('[data-action=reset]').click();ready(frame);assert snap(lab)['configuration']=={'epsilon':0,'ratio':1.5,'axialCells':16,'radialCells':8,'cap':25}
   for width in [320,360,390,414,768,1280]:
    page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width;assert frame.evaluate('document.documentElement.scrollWidth<=innerWidth'),('frame',width)
    assert frame.evaluate("()=>![document.documentElement,document.body].some(e=>['hidden','clip'].includes(getComputedStyle(e).overflowX))")
   element.screenshot(path=str(out/'connected-in-book-controls.png'));version=browser.version;browser.close()
 finally:server.shutdown();server.server_close()
 assert not errors;unchanged_outputs(out,outputs);assert manifest==sha(out/'build-manifest.json')
 result={'result':'PASS_INTEGRATED_CONNECTED_SPECIMEN','browser':version,'manifest_sha256':manifest,'html_sha256':sha(out/'index.html'),'child_manifest_sha256':sha(out/'connected-passive/axisymmetric-preview-manifest.json'),'native_receipt_sha256':sha(out/'connected-qa/axisymmetric-browser-status.json'),'api_receipt_sha256':sha(out/'connected-api-qa/axisymmetric-end-face-browser-status.json'),'test_sha256':sha(Path(__file__)),'widths':[320,360,390,414,768,1280],'actual_cases':cases,'errors':errors,'controls_capture_sha256':sha(out/'connected-in-book-controls.png'),'scope':'Actual embedded controls and GPU reconstruction, strict parent/child no-overflow, warning and explicit reset. No clinical or continuum/stability claim.'}
 (out/'connected-integration.json').write_text(json.dumps(result,indent=2)+'\n');check(out);print(result['result'])
if __name__=='__main__':run()
