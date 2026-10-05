"""Exercise actual Lab 5 compression controls and rejected-state retention."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import hashlib,json,os,shutil,subprocess,sys
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
def check(destination):
    out=Path(destination).resolve();qa=out/'qa';qa.mkdir(exist_ok=True)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(out)))
    Thread(target=server.serve_forever,daemon=True).start();errors=[];checks=[]
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        page=browser.new_page(viewport={'width':1200,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle')
        lab=page.locator('[data-compression]');expect(lab).to_have_attribute('data-enhanced','true')
        def state():
            lab.locator('[data-action=copy]').click();return json.loads(lab.locator('.preset').input_value())
        def number(key):return lab.locator(f'input[type=number][data-param={key}]')
        def hide():lab.locator('.preset').evaluate('(x)=>x.hidden=true')
        default=state();m=default['measurements']
        assert abs(m['J']-.9939144716354632)<1e-12 and abs(m['plateReactionN']-4.536371031795807)<1e-9
        assert abs(m['volumeMeasurementDifference'])<1e-12 and abs(m['volumeEquilibriumDifference'])<1e-10
        expect(number('force')).to_be_disabled();expect(number('heightStretch')).to_be_enabled()
        checks.append('Actual default free-side equilibrium, boundary-volume oracle and independent volume-variable root')
        lab.locator('select[data-param=boundary]').select_option('confined');confined=state()['measurements']
        assert abs(confined['J']-.8)<1e-12 and confined['plateReactionN']>42 and confined['sideSupportForceN']<0
        assert confined['lateralResidualPa'] is None
        lab.locator('select[data-param=mode]').select_option('force');cf=state()['measurements']
        assert abs(cf['plateReactionN']-2)<1e-8 and cf['heightStretch']>.99
        expect(number('heightStretch')).to_be_disabled();expect(number('force')).to_be_enabled()
        lab.locator('select[data-param=boundary]').select_option('free');ff=state()['measurements']
        assert abs(ff['plateReactionN']-2)<1e-8 and ff['heightStretch']<.9
        assert abs(ff['platePressurePa']-3*ff['bulkPressurePa'])<1e-7
        checks.append('Actual confined supports and force control: equal load gives different height and volume')
        before=state();number('force').fill('20');expect(number('force')).to_have_attribute('aria-invalid','true')
        expect(lab.locator('.announce')).to_contain_text('supported h ≥ 0.8')
        assert state()==before
        number('force').fill('2');expect(number('force')).not_to_have_attribute('aria-invalid','true')
        slider=lab.locator('input[type=range][data-param=force]');slider.focus();slider.press('ArrowRight')
        assert abs(float(number('force').input_value())-2.1)<1e-12
        assert abs(state()['measurements']['plateReactionN']-2.1)<1e-8
        number('bulk').fill('');expect(number('bulk')).to_have_attribute('aria-invalid','true')
        saved=state();number('bulk').fill('0');expect(lab.locator('.announce')).to_contain_text('no unique')
        assert state()==saved
        lab.locator('[data-action=reset]').click();number('bulk').fill('0');ablation=state()['measurements']
        assert abs(ablation['J']-.8**3)<1e-12 and abs(ablation['plateReactionN'])<1e-9
        lab.locator('select[data-param=mode]').select_option('force');expect(lab.locator('.announce')).to_contain_text('no unique')
        assert state()['measurements']==ablation
        expect(lab.locator('select[data-param=mode]')).to_have_value('displacement')
        lab.locator('[data-action=reset]').click();number('heightStretch').fill('0.2');assert state()['parameters']==default['parameters']
        checks.append('Unsupported force, empty/invalid input and zero-bulk force degeneracy reject without advancing state; keyboard slider and paired number work')
        for param,value in [('mu','3000'),('bulk','100000'),('heightStretch','0.9')]:
            lab.locator('[data-action=reset]').click();number(param).fill(value);assert state()['parameters'][param]==float(value)
        lab.locator('[data-action=reset]').click();lab.locator('[data-action=summary]').click();expect(lab.locator('.announce')).to_contain_text('Bulk / mean compressive pressure')
        for name,width,height in [('desktop',1200,1000),('mobile',393,852)]:
            page.set_viewport_size({'width':width,'height':height})
            for boundary in ['free','confined']:
                for mode in ['displacement','force']:
                    lab.locator('[data-action=reset]').click();lab.locator('select[data-param=boundary]').select_option(boundary);lab.locator('select[data-param=mode]').select_option(mode)
                    hide();lab.scroll_into_view_if_needed();assert lab.evaluate('(x)=>x.scrollWidth<=x.clientWidth+1')
                    lab.screenshot(path=str(qa/f'compression-{name}-{boundary}-{mode}.png'))
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
        page.emulate_media(media='print');expect(lab.locator('.static-figure')).to_be_visible();expect(lab.locator('.property-scene')).to_be_hidden()
        assert not errors,errors;version=browser.version;browser.close()
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        page=browser.new_page(java_script_enabled=False);page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
        image=page.locator('.compression-lesson .static-figure img');expect(image).to_be_visible();assert image.evaluate('(x)=>x.complete&&x.naturalWidth>0')
        browser.close();checks.append('Material, height, load and boundary controls; live summary/reset; desktop/mobile, print and zero-JavaScript alternatives')
    finally:server.shutdown()
    manifest='build-manifest.json' if (out/'build-manifest.json').exists() else 'compression-preview-manifest.json'
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    payload={'schema':1,'result':'PASS_LAB5_COMPRESSION_BROWSER','source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'checks':checks,'javascript_errors':errors,'browser':version,'manifest':manifest,'manifest_sha256':digest(out/manifest),'html_sha256':digest(out/'index.html'),'outputs':{p.name:digest(p) for p in sorted(qa.glob('compression-*.png'))}}
    (qa/'compression-browser-check.json').write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(payload,indent=2))
if __name__=='__main__':check(sys.argv[1] if len(sys.argv)>1 else ROOT/'dist')
