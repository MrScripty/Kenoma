"""Real mobile-coordinate taps, rendered pixels and injected WebGL failures.
Default Chromium launch: no GL/security override flags. This is mobile
emulation, not a physical Android or ChatGPT WebView certification.
"""
from pathlib import Path
import hashlib,json,os,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import serve
from playwright.sync_api import sync_playwright,expect
from collections import Counter
import fitz
ROOT=Path(__file__).resolve().parents[1]
LABS=['force','torque','energy','elbow','series','continuum','spatial']


def tap_start(page,lab,point=(.5,.5)):
    button=lab.locator('[data-action=start]')
    expect(button).to_have_attribute('type','button')
    button.scroll_into_view_if_needed()
    rect=button.bounding_box();x=rect['x']+rect['width']*point[0];y=rect['y']+rect['height']*point[1]
    target=page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("button")?.dataset.action',[x,y])
    assert target=='start',target
    page.touchscreen.tap(x,y)
    return x,y


def check_draw(lab,out,name):
    expect(lab).to_have_attribute('data-scene-state','ready')
    canvas=lab.locator('canvas');expect(canvas).to_be_visible()
    context=canvas.evaluate('c=>{const gl=c.getContext("webgl2");return {available:!!gl,lost:gl?.isContextLost(),width:gl?.drawingBufferWidth,height:gl?.drawingBufferHeight};}')
    assert context['available'] and not context['lost'] and context['width']>0 and context['height']>0
    png=canvas.screenshot();(out/(name+'.png')).write_bytes(png)
    image=fitz.Pixmap(png)
    if image.alpha:image=fitz.Pixmap(image,0)
    assert image.n==3
    samples=image.samples;colors=Counter(tuple(samples[i:i+3]) for i in range(0,len(samples),3))
    background=(16,29,44)
    # Require substantial colored geometry in the actual composited canvas,
    # beyond a CSS rectangle, one background clear, or an empty draw buffer.
    vivid=sum(n for c,n in colors.items() if max(c)-min(c)>45 and sum(abs(c[i]-background[i]) for i in range(3))>100)
    assert len(colors)>100 and vivid>300,(name,len(colors),vivid)
    return {**context,'unique_colors':len(colors),'vivid_geometry_pixels':vivid,'sha256':hashlib.sha256(png).hexdigest()}


def check():
    out=ROOT/'dist/qa/mobile-startup';out.mkdir(parents=True,exist_ok=True)
    receipt=ROOT/'dist/mobile-startup-check.json';receipt.unlink(missing_ok=True)
    server,url=serve();result={'status':'passed','scope':'Pixel 7 touch emulation with default headless Chromium; not physical Android/WebView evidence','startup_draws':{},'fault_tests':[]}
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        context=browser.new_context(**p.devices['Pixel 7'],reduced_motion='reduce')
        page=context.new_page();page.set_default_timeout(60000);downloads=[];errors=[]
        page.on('download',lambda d:downloads.append(d.suggested_filename));page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url+'/index.html',wait_until='networkidle')
        for name in LABS:
          lab=page.locator('#lab-'+name);expect(lab.locator('.scene-host')).to_be_hidden()
          assert lab.locator('[data-action=start]').evaluate('(b)=>b.getBoundingClientRect().top<b.closest(".laboratory").querySelector(".static-figure").getBoundingClientRect().top')
          x,y=tap_start(page,lab);expect(lab).to_have_attribute('data-scene-state','ready')
          # Original tap coordinate must still target Start after drawing/hiding
          # the figure, never the nearby export/trace action on a second tap.
          assert page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("button")?.dataset.action',[x,y])=='start'
          page.touchscreen.tap(x,y);expect(lab).to_have_attribute('data-scene-state','ready')
          result['startup_draws'][name]=check_draw(lab,out,name)
          assert not downloads,downloads
        assert not errors,errors
        # Atlas viewer shares lifecycle handling although it is not a numbered lab.
        atlas=page.locator('#evidence-viewer');tap_start(page,atlas);result['startup_draws']['atlas']=check_draw(atlas,out,'atlas')
        assert not downloads
        # Owner reported Lab 7 exporting this exact filename after Start.
        # Exercise native taps over the whole Start hitbox at narrower Android
        # widths, with normal motion, then separately test the intended export.
        spatial=page.locator('#lab-spatial');hitbox_cases=[]
        page.emulate_media(reduced_motion='no-preference')
        for width in [320,360,375,393,412]:
          page.set_viewport_size({'width':width,'height':780})
          for point in [(x,y) for y in [.05,.5,.95] for x in [.05,.5,.95]]:
            tap_start(page,spatial,point)
            expect(spatial).to_have_attribute('data-scene-state','ready')
            assert not downloads,downloads
            hitbox_cases.append({'width':width,'fractional_point':point,'target':'start','download_count':0})
        export=spatial.locator('[data-action=export]');export.scroll_into_view_if_needed()
        r=export.bounding_box();x=r['x']+r['width']/2;y=r['y']+r['height']/2
        assert page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("button")?.dataset.action',[x,y])=='export'
        with page.expect_download() as info:page.touchscreen.tap(x,y)
        download=info.value;assert download.suggested_filename=='kenoma-spatial-trace.json'
        download.save_as(str(out/'intentional-spatial-export.json'))
        payload=json.loads((out/'intentional-spatial-export.json').read_text())
        diagnostic=payload['interactionDiagnostics'];events=diagnostic['events']
        assert diagnostic['lab']=='lab-spatial' and len(events)<=32
        assert [e['type'] for e in events[-3:]]==['pointerdown','pointerup','click']
        assert all(e['action']=='export' and e['trusted'] for e in events[-3:])
        assert any(e['action']=='start' and e['trusted'] for e in events)
        result['spatial_touch_contract']={'start_hitbox_cases':hitbox_cases,'intentional_export_filename':download.suggested_filename,'export_hit_target':'export','trace_model':payload['model'],'local_diagnostics_verified':True}
        # The controlled export is expected; keep the Start-download contract
        # separate from deliberately tapping Download trace.
        assert downloads==['kenoma-spatial-trace.json'];downloads.clear()
        # Actual context-loss extension, not just a synthetic DOM event.
        lab=page.locator('#lab-spatial');tap_start(page,lab)
        supported=lab.locator('canvas').evaluate('c=>{const gl=c.getContext("webgl2"),ext=gl.getExtension("WEBGL_lose_context");if(!ext)return false;ext.loseContext();return true;}')
        assert supported,'Context-loss extension unavailable: failure-path test incomplete'
        expect(lab).to_have_attribute('data-scene-state','error')
        expect(lab.locator('.scene-error')).to_be_visible();expect(lab.locator('.static-figure')).to_be_visible()
        assert lab.locator('canvas').count()==0
        tap_start(page,lab);check_draw(lab,out,'spatial-recovered');assert not downloads
        result['fault_tests'].append('Actual WebGL context loss exposes visible diagnostics, preserves static alternative and recovers on Retry without a download')
        # Draw/shader errors after context creation must not leave a blank canvas.
        page.evaluate('''()=>{window.failDraw=true;for(const method of ['drawArrays','drawElements']){const original=WebGL2RenderingContext.prototype[method];WebGL2RenderingContext.prototype[method]=function(...args){if(window.failDraw)throw new Error('Injected draw failure');return original.apply(this,args);};}}''')
        lab=page.locator('#lab-force');tap_start(page,lab);expect(lab).to_have_attribute('data-scene-state','error')
        expect(lab.locator('.scene-error')).to_contain_text('Injected draw failure');assert lab.locator('canvas').count()==0
        page.evaluate('window.failDraw=false');tap_start(page,lab);check_draw(lab,out,'force-recovered')
        result['fault_tests'].append('Injected post-context draw failure produces in-viewport diagnostics and Retry restores real drawn geometry')
        # Context creation can be unavailable in an embedded browser. Label this
        # as injection; it is not a diagnosis of the owner phone's capability.
        failed=context.new_page();failed.set_default_timeout(60000);failed_downloads=[]
        failed.on('download',lambda d:failed_downloads.append(d.suggested_filename))
        failed.add_init_script('''const getContext=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){if(type.includes('webgl'))return null;return getContext.call(this,type,...args);};''')
        failed.goto(url+'/index.html',wait_until='networkidle')
        for name in LABS:
          lab=failed.locator('#lab-'+name);tap_start(failed,lab)
          expect(lab).to_have_attribute('data-scene-state','error');expect(lab.locator('.scene-host .scene-error')).to_be_visible()
          expect(lab.locator('.scene-notice')).to_contain_text('3D unavailable')
          expect(lab.locator('.static-figure')).to_be_visible();assert lab.locator('canvas').count()==0
          before=lab.locator('.readout').inner_text()
          if name=='continuum':lab.locator('select[data-param=sweeps]').select_option('20')
          elif name=='torque':lab.locator('input[type=number][data-param=angle]').fill('90')
          else:lab.locator('[data-action=step]').click()
          assert lab.locator('.readout').inner_text()!=before,name
          expect(lab.locator('.scene-error')).to_be_visible()
        for name in LABS:expect(failed.locator('#lab-'+name+' .scene-error')).to_be_visible()
        failed.locator('#lab-series').screenshot(path=str(out/'unavailable-series.png'))
        failed.locator('#lab-series .scene-host').screenshot(path=str(out/'unavailable-message.png'))
        failed.locator('#lab-series .scene-toolbar').screenshot(path=str(out/'retry-toolbar.png'))
        assert not failed_downloads
        result['fault_tests'].append('Unavailable WebGL in all seven labs gives prominent in-viewport error plus functional numerical controls, explicitly without 3D')
        result.update(browser=browser.version,downloads_on_start=downloads+failed_downloads,html_sha256=hashlib.sha256((ROOT/'dist/index.html').read_bytes()).hexdigest(),app_sha256=hashlib.sha256((ROOT/'dist/assets/app.js').read_bytes()).hexdigest())
        browser.close()
      receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    finally:server.shutdown();server.server_close()


if __name__=='__main__':check()
