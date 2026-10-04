"""Behavior checks and screenshots for the built portable static artifact."""
from pathlib import Path
import hashlib,json,os,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from render_pdf import serve
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]

def check():
    (ROOT/'dist/browser-check.json').unlink(missing_ok=True)
    server,url=serve();checks=[];out=ROOT/'dist/qa';out.mkdir(exist_ok=True)
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        context=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce')
        page=context.new_page();page.set_default_timeout(60000);errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto(url+'/index.html',wait_until='networkidle')
        assert page.locator('.proof-card').count()==12
        assert page.locator('math').count()>15
        # Every generated internal hash link and local asset must resolve.
        for link in page.locator('a[href^="#"]').evaluate_all('(els)=>els.map(el=>el.getAttribute("href"))'):
          assert page.locator('[id="'+link[1:]+'"]').count()==1,link
        for href in page.locator('[src],a[href]').evaluate_all('(els)=>els.map(el=>el.getAttribute("src")||el.getAttribute("href"))'):
          if not href or href.startswith(('#','http')):continue
          assert context.request.get(url+'/'+href.split('#')[0]).status==200,href
        checks.append('12 proof cards, MathML, internal links and local resources verified')
        force=page.locator('#lab-force');expect(force.locator('.readout')).to_contain_text('0 J')
        invalid=force.locator('input[type=number][data-param=mass]');invalid.fill('')
        expect(invalid).to_have_attribute('aria-invalid','true');force.locator('[data-action=reset]').click()
        assert invalid.get_attribute('aria-invalid') is None;expect(invalid).to_have_value('2')
        checks.append('Blank numeric input then Reset clears stale aria-invalid')
        force.locator('input[type=number][data-param=time]').fill('2')
        expect(force.locator('.readout')).to_contain_text('4.000 m')
        force.locator('[data-action=reset]').click()
        force.locator('[data-action=step]').click()
        first=force.locator('.readout').inner_text()
        force.locator('[data-action=reset]').click();force.locator('[data-action=step]').click()
        assert force.locator('.readout').inner_text()==first
        force.locator('[data-action=start]').click();expect(force.locator('canvas')).to_be_visible()
        force.locator('[data-action=view]').click();assert force.locator('.readout').inner_text()==first
        force.screenshot(path=str(out/'force-desktop.png'))
        torque=page.locator('#lab-torque')
        length=torque.locator('input[type=number][data-param=length]');length.fill('');length.press_sequentially('0.35')
        expect(length).to_have_value('0.35');assert length.get_attribute('aria-invalid') is None
        expect(torque.locator('.readout')).to_contain_text('-17.168 N m');torque.locator('[data-action=reset]').click()
        checks.append('Sequential decimal typing retains 0.35 without eager minimum clamping')
        expect(torque.locator('.readout')).to_contain_text('-14.715 N m')
        torque.locator('input[type=number][data-param=angle]').fill('90')
        expect(torque.locator('.readout')).to_contain_text('0 N m')
        torque.locator('[data-action=reset]').click();torque.locator('[data-action=start]').click()
        assert page.locator('canvas').count()==1
        torque.screenshot(path=str(out/'torque-desktop.png'))
        energy=page.locator('#lab-energy')
        for method in ['explicit','symplectic','verlet']:
          energy.locator('[data-action=reset]').click()
          energy.locator('select[data-param=method]').select_option(method)
          energy.locator('select[data-param=dt]').select_option('0.05')
          energy.locator('[data-action=step]').click();first=energy.locator('.readout').inner_text()
          energy.locator('[data-action=reset]').click()
          energy.locator('select[data-param=method]').select_option(method)
          energy.locator('select[data-param=dt]').select_option('0.05')
          energy.locator('[data-action=step]').click();assert energy.locator('.readout').inner_text()==first
        energy.locator('[data-action=start]').click();energy.locator('[data-action=view]').click()
        energy.locator('[data-action=copy]').click()
        preset=json.loads(energy.locator('.preset').input_value());assert preset['step']==1 and preset['parameters']['dt']==0.05
        energy.locator('[data-action=summary]').click();expect(energy.locator('.announce')).to_contain_text('Energy')
        energy.locator('[data-action=play]').click();page.wait_for_timeout(200)
        energy.locator('[data-action=play]').click();paused=energy.locator('.readout').inner_text()
        page.wait_for_timeout(100);assert energy.locator('.readout').inner_text()==paused
        energy.locator('[data-action=reset]').click();energy.screenshot(path=str(out/'energy-desktop.png'))
        page.screenshot(path=str(out/'book-desktop.png'))
        assert not errors,errors
        checks.append('Desktop real WebGL, camera, defaults, all integrators, stepping, reset replay, copy, pause verified')
        elbow=page.locator('#lab-elbow');expect(elbow.locator('.readout')).to_contain_text('Force-driven hinge')
        elbow.locator('[data-action=start]').click();expect(elbow.locator('canvas')).to_be_visible();assert page.locator('canvas').count()==1
        elbow.evaluate('(lab)=>{for(let i=0;i<60;i++)lab.querySelector("[data-action=step]").click()}')
        elbow.locator('[data-action=copy]').click();before=json.loads(elbow.locator('.preset').input_value())
        assert before['state']['q']>30*3.141592653589793/180 and before['state']['a']>0.5
        elbow.locator('[data-action=release]').click();elbow.locator('[data-action=copy]').click()
        released=json.loads(elbow.locator('.preset').input_value());assert released['state']==before['state'] and released['parameters']['excitation']==0
        with page.expect_download() as info:elbow.locator('[data-action=export]').click()
        info.value.save_as(str(out/'elbow-immediate-release.json'));instant=json.loads((out/'elbow-immediate-release.json').read_text())
        assert len(instant['trace'])==61 and instant['trace'][-1]['excitation']==0
        assert instant['trace'][-1]['work']==before['state']['work'] and instant['trace'][-1]['a']==before['state']['a']
        elbow.locator('[data-action=step]').click();elbow.locator('[data-action=copy]').click()
        after=json.loads(elbow.locator('.preset').input_value());assert 0<after['state']['a']<before['state']['a'] and after['step']==61
        with page.expect_download() as info:elbow.locator('[data-action=export]').click()
        downloaded=info.value;downloaded.save_as(str(out/'elbow-trace.json'));trace=json.loads((out/'elbow-trace.json').read_text())
        assert len(trace['trace'])==62 and trace['trace'][-1]['excitation']==0
        elbow.locator('[data-action=reset]').click();elbow.locator('select[data-param=mode]').select_option('prescribed')
        elbow.locator('input[type=number][data-param=angle]').fill('90');elbow.locator('[data-action=step]').click()
        expect(elbow.locator('.readout')).to_contain_text('90.00°');expect(elbow.locator('.readout')).to_contain_text('Prescribed static hold')
        elbow.locator('[data-action=reset]').click();elbow.screenshot(path=str(out/'elbow-desktop.png'))
        elbow.locator('[data-action=pulse]').click();page.wait_for_timeout(100);elbow.locator('[data-action=play]').click()
        elbow.locator('[data-action=reset]').click()
        checks.append('Elbow real WebGL, force-driven lift, continuous release, trace download, prescribed hold and pulse controls verified')
        series=page.locator('#lab-series');series.locator('[data-action=start]').click()
        expect(series.locator('canvas')).to_be_visible();assert page.locator('canvas').count()==1
        series.locator('select[data-param=mode]').select_option('prescribed');series.locator('input[type=number][data-param=angle]').fill('90')
        series.evaluate('(lab)=>{for(let i=0;i<60;i++)lab.querySelector("[data-action=step]").click()}')
        series.locator('[data-action=copy]').click();before=json.loads(series.locator('.preset').input_value())
        assert abs(before['state']['q']-3.141592653589793/2)<1e-12 and before['state']['work']>8.59
        series.locator('[data-action=release]').click();series.locator('[data-action=copy]').click()
        released=json.loads(series.locator('.preset').input_value());assert released['state']==before['state']
        with page.expect_download() as info:series.locator('[data-action=export]').click()
        info.value.save_as(str(out/'series-immediate-release.json'));instant=json.loads((out/'series-immediate-release.json').read_text());current=instant['trace'][-1]
        assert len(instant['trace'])==61 and current['step']==60 and current['excitation']==0
        assert current['fiberSpeed']>0 and current['activePower']<0 and current['work']==before['state']['work']
        assert current['a']==before['state']['a'] and 'current row refreshed' in instant['tracePolicy']
        series.locator('input[type=number][data-param=excitation]').fill('0.8')
        with page.expect_download() as info:series.locator('[data-action=export]').click()
        info.value.save_as(str(out/'series-immediate-change.json'));changed=json.loads((out/'series-immediate-change.json').read_text())['trace'][-1]
        assert changed['step']==60 and changed['excitation']==.8 and changed['fiberSpeed']<0 and changed['activePower']>0
        assert changed['work']==current['work'] and changed['time']==current['time'] and changed['a']==current['a']
        series.locator('[data-action=release]').click()
        series.locator('[data-action=step]').click()
        expect(series.locator('.readout')).to_contain_text('Lengthening')
        with page.expect_download() as info:series.locator('[data-action=export]').click()
        info.value.save_as(str(out/'series-trace.json'));trace=json.loads((out/'series-trace.json').read_text());r=trace['trace'][-1]
        assert trace['model']=='series-affine-tissue-v1' and len(trace['trace'])==62
        assert r['tissue']['normal']>5.5 and r['tissue']['volumeRatio']>.99 and abs(r['tissue']['skinVolumeRatio']-.5)<1e-12
        assert r['fiberSpeed']>0 and r['activePower']<0 and r['hingeMusclePower']==0
        series.screenshot(path=str(out/'series-desktop.png'))
        series.locator('select[data-param=contact]').select_option('off')
        expect(series.locator('.readout')).to_contain_text('13.891 mm')
        series.locator('select[data-param=contact]').select_option('on');series.locator('select[data-param=bulk]').select_option('0')
        expect(series.locator('.readout')).to_contain_text('0.45384')
        series.locator('select[data-param=tendon]').select_option('rigid');expect(series.locator('.readout')).to_contain_text('0 J')
        series.locator('[data-action=reset]').click();series.locator('[data-action=step]').click();first=series.locator('.readout').inner_text()
        series.locator('[data-action=reset]').click();series.locator('[data-action=step]').click();assert series.locator('.readout').inner_text()==first
        checks.append('Series fixed-end storage/release, immediate release/change exports before stepping, tissue ablations, same-pose LBS and deterministic reset verified')
        continuum=page.locator('#lab-continuum');expect(continuum.locator('.readout')).to_contain_text('One backward-Euler step from rest')
        continuum.locator('[data-action=start]').click();assert page.locator('canvas').count()==1
        continuum.locator('[data-action=copy]').click();c=json.loads(continuum.locator('.preset').input_value());assert c['diagnostics']['referenceConverged']
        assert abs(c['diagnostics']['metrics']['relativeObjectiveNorm']-.009212)<.000002
        assembly=c['diagnostics']['assemblyCount'];continuum.locator('select[data-param=sweeps]').select_option('20')
        continuum.locator('[data-action=copy]').click();better=json.loads(continuum.locator('.preset').input_value());assert better['diagnostics']['metrics']['relativeObjectiveNorm']<.000002
        assert better['diagnostics']['assemblyCount']==assembly
        continuum.locator('select[data-param=comparison]').select_option('static');expect(continuum.locator('.readout')).to_contain_text('Static analytic displacement L2 error')
        continuum.locator('select[data-param=n]').select_option('4');continuum.locator('[data-action=copy]').click();refined=json.loads(continuum.locator('.preset').input_value());assert abs(refined['diagnostics']['metrics']['relativeL2']-.1471)<.001
        continuum.locator('[data-action=reset]').click();continuum.screenshot(path=str(out/'continuum-desktop.png'))
        checks.append('Spatial FEM reference converged; matched sweep improvement, static refinement and cached assembly verified')
        spatial=page.locator('#lab-spatial');numeric=spatial.locator('input[type=number][data-param=excitation]');numeric.fill('');numeric.press_sequentially('0.35');expect(numeric).to_have_value('0.35');assert numeric.get_attribute('aria-invalid') is None
        spatial.locator('[data-action=reset]').click();spatial.locator('[data-action=start]').click();assert page.locator('canvas').count()==1
        spatial.locator('[data-action=compression]').click();spatial.locator('[data-action=copy]').click();compression=json.loads(spatial.locator('.preset').input_value());d=compression['diagnostics'];(out/'spatial-compression-state.json').write_text(json.dumps(compression,indent=2)+'\n')
        assert abs(d['q']-3.141592653589793/2)<1e-12 and d['minJ']>.7 and d['baselineMinJ']<.18
        assert d['penetrationM']<.00005 and d['baselinePenetrationM']>.009
        spatial.screenshot(path=str(out/'spatial-compression-desktop.png'))
        spatial.locator('select[data-param=boneContact]').select_option('off');spatial.locator('[data-action=copy]').click();contact_off=json.loads(spatial.locator('.preset').input_value());assert contact_off['diagnostics']['contactNormalSumN']==0
        spatial.locator('[data-action=reset]').click();spatial.locator('select[data-param=sweeps]').select_option('80')
        spatial.evaluate('(lab)=>{for(let i=0;i<60;i++)lab.querySelector("[data-action=step]").click()}')
        spatial.locator('[data-action=copy]').click();lifted=json.loads(spatial.locator('.preset').input_value());assert lifted['state']['q']>30*3.141592653589793/180 and lifted['state']['a']>.59
        spatial.locator('[data-action=release]').click()
        with page.expect_download() as info:spatial.locator('[data-action=export]').click()
        info.value.save_as(str(out/'spatial-immediate-release.json'));instant=json.loads((out/'spatial-immediate-release.json').read_text());assert instant['trace'][-1]['excitation']==0 and instant['trace'][-1]['time']==lifted['state']['time']
        assert instant['trace'][-1]['activation']==lifted['state']['a'] and instant['trace'][-1]['hingeWorkJ']==lifted['state']['work']
        spatial.locator('[data-action=step]').click();spatial.locator('[data-action=copy]').click();released=json.loads(spatial.locator('.preset').input_value());assert released['state']['a']<lifted['state']['a']
        spatial.locator('[data-action=reset]').click();reset_values=spatial.locator('.readout').inner_text();spatial.locator('[data-action=view]').click();assert spatial.locator('.readout').inner_text()==reset_values
        spatial.locator('[data-action=reset]').click();assert spatial.locator('.readout').inner_text()==reset_values
        checks.append('Spatial muscle/skin/contact same-pose fixture, force-driven lift, release-current export, camera and deterministic reset verified')
        # Exercise the real dt/dd DOM and both lab controller implementations.
        for name in ['force','torque','energy','elbow','series','continuum','spatial']:
          lab=page.locator('#lab-'+name)
          expected=lab.locator('.readout').evaluate('(dl)=>Array.from(dl.children).map(row=>row.querySelector("dt").textContent.trim()+": "+row.querySelector("dd").textContent.trim()+".").join(" ")')
          assert expected and ': ' in expected
          lab.locator('[data-action=summary]').click()
          assert lab.locator('.announce').text_content()==expected,name
        # Ordinary stepping/playback must not continuously announce changing numbers.
        for lab in [energy,spatial]:
          lab.locator('[data-action=reset]').click()
          lab.locator('[data-action=summary]').click()
          spoken=lab.locator('.announce').text_content()
          lab.locator('.announce').evaluate('(el)=>{el.summaryMutations=0;el.summaryObserver=new MutationObserver(records=>el.summaryMutations+=records.length);el.summaryObserver.observe(el,{childList:true,characterData:true,subtree:true});}')
          lab.locator('[data-action=step]').click()
          lab.locator('[data-action=play]').click();page.wait_for_timeout(250);lab.locator('[data-action=play]').click()
          assert lab.locator('.announce').text_content()==spoken
          assert lab.locator('.announce').evaluate('(el)=>{el.summaryObserver.disconnect();return el.summaryMutations;}')==0
        checks.append('All seven deliberate spoken summaries separate each actual DOM label/value pair; energy/spatial stepping and playback produce no live-region mutations')
        evidence=page.locator('#evidence-viewer');expect(evidence.locator('[data-evidence=bin]')).to_be_enabled()
        evidence.locator('[data-action=start]').click();expect(evidence.locator('canvas')).to_be_visible();assert page.locator('canvas').count()==1
        evidence.locator('[data-evidence=part]').select_option('bones');evidence.locator('[data-action=view]').click()
        slider=evidence.locator('[data-evidence=bin]');slider.focus();page.keyboard.press('End')
        expect(evidence.locator('.readout')).to_contain_text('172 / 172');expect(evidence.locator('.readout')).to_contain_text('unit 1')
        evidence.locator('[data-action=reset]').click();expect(slider).to_have_value('0');expect(evidence.locator('[data-evidence=part]')).to_have_value('all')
        expect(evidence.locator('.readout')).to_contain_text('0.219441 s');evidence.screenshot(path=str(out/'evidence-desktop.png'))
        assert not errors,errors
        checks.append('Actual atlas WebGL part/camera views and keyboard-accessible timestamp-aware recording bins/reset verified; one active canvas retained')
        page.set_viewport_size({'width':390,'height':844})
        page.goto(url+'/index.html',wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'), 'mobile overflow'
        torque=page.locator('#lab-torque');torque.locator('[data-action=start]').click()
        expect(torque.locator('canvas')).to_be_visible();torque.screenshot(path=str(out/'torque-mobile.png'))
        # Native number control is fully keyboard operable.
        number=torque.locator('input[type=number][data-param=angle]');number.focus();page.keyboard.press('ArrowUp')
        expect(number).to_have_value('1');torque.locator('[data-action=reset]').click()
        checks.append('390px viewport has no horizontal page overflow; WebGL and keyboard controls verified')
        elbow=page.locator('#lab-elbow');elbow.locator('[data-action=start]').click();elbow.screenshot(path=str(out/'elbow-mobile.png'))
        series=page.locator('#lab-series');series.locator('[data-action=start]').click()
        series.locator('select[data-param=mode]').select_option('prescribed');series.locator('input[type=number][data-param=angle]').fill('90');series.screenshot(path=str(out/'series-mobile.png'))
        continuum=page.locator('#lab-continuum');continuum.locator('[data-action=start]').click();continuum.screenshot(path=str(out/'continuum-mobile.png'))
        spatial=page.locator('#lab-spatial');spatial.locator('[data-action=start]').click();spatial.locator('[data-action=compression]').click();spatial.screenshot(path=str(out/'spatial-compression-mobile.png'))
        evidence=page.locator('#evidence-viewer');evidence.locator('[data-action=start]').click();expect(evidence.locator('canvas')).to_be_visible();evidence.screenshot(path=str(out/'evidence-mobile.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'), 'new chapter mobile overflow'
        no_gl=context.new_page();no_gl.add_init_script('''const original=HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext=function(type,...args){if(type.includes('webgl'))return null;return original.call(this,type,...args);};''')
        no_gl.goto(url+'/index.html',wait_until='networkidle')
        lab=no_gl.locator('#lab-force');lab.locator('[data-action=start]').click()
        expect(lab.locator('.announce')).to_contain_text('3D rendering unavailable')
        expect(lab.locator('.static-figure')).to_be_visible();lab.locator('[data-action=step]').click()
        expect(lab.locator('.readout')).to_contain_text('0.003 m')
        advanced=no_gl.locator('#lab-spatial');advanced.locator('[data-action=start]').click();expect(advanced.locator('.announce')).to_contain_text('3D unavailable');expect(advanced.locator('.static-figure')).to_be_visible()
        advanced.locator('[data-action=compression]').click();expect(advanced.locator('.readout')).to_contain_text('90.00°')
        checks.append('No-WebGL fallback retains static figures and live elementary/spatial numerical controls')
        no_js=browser.new_context(java_script_enabled=False).new_page()
        no_js.goto(url+'/index.html');expect(no_js.locator('#lab-force .static-figure')).to_be_visible()
        expect(no_js.locator('#lab-force noscript')).to_be_visible();assert no_js.locator('.proof-card').count()==12;expect(no_js.locator('#lab-spatial .static-figure')).to_be_visible();expect(no_js.locator('#lab-continuum .static-figure')).to_be_visible()
        checks.append('No-JavaScript chapter text, diagrams, proofs and experiment table remain readable')
        result={'status':'passed','browser_version':browser.version,'checks':checks,'proof_cards':12,
          'html_sha256':hashlib.sha256((ROOT/'dist/index.html').read_bytes()).hexdigest(),
          'app_sha256':hashlib.sha256((ROOT/'dist/assets/app.js').read_bytes()).hexdigest(),
          'scope':'Automated Chromium desktop/mobile viewport checks; not real mobile hardware or accessibility certification.'}
        browser.close()
      (ROOT/'dist/browser-check.json').write_text(json.dumps(result,indent=2)+'\n')
      print(json.dumps(result,indent=2))
    finally:server.shutdown();server.server_close()
if __name__=='__main__':check()
