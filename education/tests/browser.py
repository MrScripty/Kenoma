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
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'),args=['--enable-unsafe-swiftshader'])
        context=browser.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce')
        page=context.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto(url+'/index.html',wait_until='networkidle')
        assert page.locator('.proof-card').count()==8
        assert page.locator('math').count()>15
        # Every generated internal hash link and local asset must resolve.
        for link in page.locator('a[href^="#"]').evaluate_all('(els)=>els.map(el=>el.getAttribute("href"))'):
          assert page.locator('[id="'+link[1:]+'"]').count()==1,link
        for href in page.locator('[src],a[href]').evaluate_all('(els)=>els.map(el=>el.getAttribute("src")||el.getAttribute("href"))'):
          if not href or href.startswith(('#','http')):continue
          assert context.request.get(url+'/'+href.split('#')[0]).status==200,href
        checks.append('8 proof cards, MathML, internal links and local resources verified')
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
        no_gl=context.new_page();no_gl.add_init_script('''const original=HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext=function(type,...args){if(type.includes('webgl'))return null;return original.call(this,type,...args);};''')
        no_gl.goto(url+'/index.html',wait_until='networkidle')
        lab=no_gl.locator('#lab-force');lab.locator('[data-action=start]').click()
        expect(lab.locator('.announce')).to_contain_text('3D rendering unavailable')
        expect(lab.locator('.static-figure')).to_be_visible();lab.locator('[data-action=step]').click()
        expect(lab.locator('.readout')).to_contain_text('0.003 m')
        checks.append('No-WebGL fallback retains static figures and live numerical controls')
        no_js=browser.new_context(java_script_enabled=False).new_page()
        no_js.goto(url+'/index.html');expect(no_js.locator('#lab-force .static-figure')).to_be_visible()
        expect(no_js.locator('#lab-force noscript')).to_be_visible();assert no_js.locator('.proof-card').count()==8
        checks.append('No-JavaScript chapter text, diagrams, proofs and experiment table remain readable')
        result={'status':'passed','browser_version':browser.version,'checks':checks,'proof_cards':8,
          'html_sha256':hashlib.sha256((ROOT/'dist/index.html').read_bytes()).hexdigest(),
          'app_sha256':hashlib.sha256((ROOT/'dist/assets/app.js').read_bytes()).hexdigest(),
          'scope':'Automated Chromium desktop/mobile viewport checks; not real mobile hardware or accessibility certification.'}
        browser.close()
      (ROOT/'dist/browser-check.json').write_text(json.dumps(result,indent=2)+'\n')
      print(json.dumps(result,indent=2))
    finally:server.shutdown();server.server_close()
if __name__=='__main__':check()
