"""Exercise actual controls, invalid retention, real history, and responsive render."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json,shutil,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'education/data/vertical-force-command-v1/review'

def run():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(OUT)));Thread(target=server.serve_forever,daemon=True).start();checks=[];errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'));page=browser.new_page(viewport={'width':1200,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/vertical-force-lab.html');page.wait_for_function('window.verticalForceResult?.history.length > 5')
            assert abs(page.evaluate('verticalForceResult.history.at(-1).z[1]'))<1e-8;checks.append('Baseline uses actual integrated stationary history')
            old=page.evaluate('JSON.stringify(verticalForceResult)');page.locator('#mass').fill('0');page.locator('#run').click();assert 'Rejected request' in page.locator('#error').inner_text();assert old==page.evaluate('JSON.stringify(verticalForceResult)');checks.append('Invalid mass preserves previous accepted run and display')
            page.locator('#case').select_option('pulse');page.wait_for_function('verticalForceResult.cfg.caseName==="pulse"');r=page.evaluate('verticalForceResult');native=json.loads((OUT/'pulse-fine.json').read_text());assert abs(r['history'][-1]['z'][0]-native['history'][-1]['z'][0])<1e-12;checks.append('Browser pulse matches the tested model, not commanded animation')
            page.locator('#time').fill('0.14');page.locator('#time').dispatch_event('input');assert page.evaluate('verticalForceCurrent.z[1]')!=0;assert abs(page.evaluate('verticalForceCurrent.target')-.5*9.80665)<1e-10;checks.append('Weight-command stage retains actual nonzero velocity')
            page.locator('#end').click();assert abs(page.evaluate('verticalForceCurrent.t-verticalForceResult.acceptedTime'))<1e-12;checks.append('Last-state button exposes the actual terminal accepted time without range-step rounding');page.screenshot(path=str(OUT/'browser-pulse-desktop.png'),full_page=True)
            page.locator('#case').select_option('high');assert page.evaluate('verticalForceResult.failure.code')=='antiwindup-surface';assert 'Stopped' in page.locator('#integration').inner_text();assert page.evaluate('verticalForceCurrent.t')<=page.evaluate('verticalForceResult.failure.acceptedTime')+1e-12;page.screenshot(path=str(OUT/'browser-high-desktop.png'),full_page=True);checks.append('High command exposes unqualified switching trial and accepted-state retention')
            page.locator('#case').select_option('descending_pi');assert page.evaluate('verticalForceComparison.cfg.caseName')=='descending_fixed';assert page.locator('#comp-y').is_visible();assert 'not stability' in page.locator('#tracking').inner_text();page.screenshot(path=str(OUT/'browser-descending-desktop.png'),full_page=True);checks.append('Descending PI/fixed activation comparison is live and distinct from tracking quality')
            page.locator('#case').select_option('mass');page.locator('#mass').fill('1');page.locator('#run').click();assert page.evaluate('verticalForceResult.cfg.m')==1;assert abs(page.evaluate('verticalForceResult.history[0].acceleration')+4.903325)<1e-10;checks.append('Mass control restarts common preload and changes actual inertial acceleration')
            page.set_viewport_size({'width':360,'height':820});page.locator('#case').select_option('pulse');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(OUT/'browser-pulse-mobile.png'),full_page=True);checks.append('360px controls/plots render without horizontal overflow')
            page.locator('#time').fill('0.1');page.locator('#time').dispatch_event('input');assert abs(page.evaluate('verticalForceCurrent.t')-.1)<1e-9;checks.append('History cursor reads accepted values and redraws the scalar scene')
            assert not errors,errors
            browser.close()
    finally:server.shutdown()
    receipt={'passed':True,'checks':checks,'javascript_errors':errors,'html_sha256':hashlib.sha256((OUT/'vertical-force-lab.html').read_bytes()).hexdigest()};(OUT/'browser-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print('\n'.join(checks))

if __name__=='__main__':run()
