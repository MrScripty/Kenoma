"""Native desktop/mobile review surface smoke check; no GPU overrides."""
from pathlib import Path
import json,os,sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import serve
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def run():
    out=Path(os.environ.get('ANATOMY_REVIEW_OUTPUT',str(ROOT/'dist/anatomy-review')));out.mkdir(parents=True,exist_ok=True)
    server,url=serve();rows=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            for label,width,height in [('desktop',1200,1300),('mobile-emulation',393,852)]:
                page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url+'/anatomy-inspection/index.html');page.wait_for_function('window.inspectionReady===true')
                page.wait_for_function('document.querySelector("#transfer-proofs pre")?.textContent.includes("theorem paired_attachment_work")')
                assert page.locator('#transfer-proofs summary').count()==3
                assert page.locator('#transfer-proofs a').count()==3
                page.locator('#focus').select_option('arm');page.locator('#parts').select_option('all')
                for representation in ['source','regions','remesh']:
                    page.locator('#geometry').select_option(representation)
                    for view in ['anterior','lateral','oblique']:
                        page.locator('[data-view="'+view+'"]').click()
                        page.locator('#scene').screenshot(path=str(out/(label+'-'+representation+'-'+view+'.png')))
                page.locator('#parts').select_option('bones');page.locator('#geometry').select_option('source')
                for angle in [0,30,60,90,120]:
                    page.evaluate('(q)=>inspectApi.setPose(q*Math.PI/180)',angle)
                    page.locator('#scene').screenshot(path=str(out/(label+'-bones-'+str(angle)+'.png')))
                    assert 'bone diagnostic only' in page.locator('#pose-value').inner_text()
                page.locator('#bind').click()
                for patch in ['radial_tuberosity','brachialis_ulna','olecranon','distal_radius_brachioradialis','FJ1486_humerus_origin','FJ1480_humerus_origin','FJ1477_humerus_origin','FJ1487_humerus_origin']:
                    page.locator('#patch').select_option(patch);value=json.loads(page.locator('#selection').inner_text());assert value['triangle_indices_zero_based'];assert 'pending' in value['review_status'].lower()
                page.locator('#patch').select_option('none');page.locator('#parts').select_option('FJ3368');page.locator('#focus').select_option('elbow');page.locator('[data-view="anterior"]').click()
                page.locator('#scene').scroll_into_view_if_needed();target=page.evaluate('()=>inspectApi.project([-.2043111111,-.0813640919,1.041166678])');page.mouse.click(*target)
                pick=page.evaluate('window.lastSelection');assert pick and pick['element_id']=='FJ3368',(label,target,pick);assert abs(sum(pick['barycentric'])-1)<1e-12
                overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+1');assert not overflow,(label,'horizontal overflow')
                assert not errors,errors
                rows.append({'viewport':label,'width':width,'representations':3,'review_views_each':3,'bone_axis_angles':[0,30,60,90,120],'named_patch_selections':8,'native_source_triangle_pick':pick,'visible_compiled_claims':2,'horizontal_overflow':overflow,'browser_errors':errors,'limit':'Mobile emulation, not a real phone; source inspection, not coupled capstone.'})
                page.close()
            browser.close()
    finally:server.shutdown();server.server_close()
    receipt={'result':'PASS','rows':rows};(out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'result':'PASS','viewports':len(rows),'output':str(out)}))
if __name__=='__main__':run()
