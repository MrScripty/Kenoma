"""Real UI controls for dormant targets and retained active-PI semantics."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json,shutil,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'education/data/vertical-force-completion-v1/review'

def run():
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(OUT)));Thread(target=server.serve_forever,daemon=True).start();checks=[];errors=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'));page=browser.new_page(viewport={'width':1200,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/vertical-force-lab.html');page.wait_for_function('window.verticalForceResult?.history.length > 5')
            page.locator('#case').select_option('release');zero=page.evaluate('verticalForceResult.history.map(r=>r.z)');page.locator('#target').fill('150');page.locator('#run').click()
            assert page.evaluate('verticalForceResult.cfg.target')==150;assert page.evaluate('verticalForceResult.history.map(r=>r.z)')==zero
            assert 'Force target bypassed' in page.locator('#subtitle').inner_text();assert 'bypassed (floor-drive)' in page.locator('#values').inner_text();assert 'floor drive' in page.locator('#values').inner_text();assert 'limit active' not in page.locator('#values').inner_text();assert 'Command above' not in page.locator('#limit').inner_text()
            assert not page.evaluate('verticalForceCurrent.forceTargetApplicable || verticalForceCurrent.saturated || verticalForceCurrent.capacityComparisonApplicable')
            assert page.evaluate("document.querySelectorAll('#force-plot path')[1].getAttribute('d').match(/[ML]/g).length===verticalForceResult.history.filter(r=>r.forceTargetApplicable).length")
            checks.append('Custom release 150 N equals 0 N physically; floor drive/bypass labels and only PI-stage target points render')
            page.screenshot(path=str(OUT/'browser-release-150-desktop.png'),full_page=True)
            page.locator('#time').fill('0.03');page.locator('#time').dispatch_event('input');assert page.evaluate('verticalForceCurrent.forceTargetApplicable');assert 'Target tension is a command' in page.locator('#subtitle').inner_text();assert 'bypassed' not in page.locator('#values').inner_text();checks.append('Release initialization keeps its actual PI weight-stage target applicable')
            page.locator('#case').select_option('descending_fixed');page.locator('#target').fill('0');page.locator('#run').click();zero_fixed=page.evaluate('verticalForceResult.history.map(r=>r.z)');page.locator('#target').fill('150');page.locator('#run').click()
            assert page.evaluate('verticalForceResult.history.map(r=>r.z)')==zero_fixed;assert 'bypassed (fixed-activation)' in page.locator('#values').inner_text();assert 'fixed activation' in page.locator('#values').inner_text();assert 'Command above' not in page.locator('#limit').inner_text();assert 'limit active' not in page.locator('#values').inner_text();assert page.locator('#target-legend').is_hidden();assert page.evaluate("document.querySelectorAll('#force-plot path')[1].getAttribute('d')==='' ")
            assert page.evaluate('verticalForceComparison.cfg.target')==150
            if page.evaluate('verticalForceComparison.failure!==null'):assert 'Companion descending_pi: stopped' in page.locator('#limit').inner_text()
            checks.append('Fixed activation bypasses 0/150 N targets with identical state history, no target line/capacity/saturation claim')
            page.screenshot(path=str(OUT/'browser-fixed-150-desktop.png'),full_page=True)
            page.locator('#case').select_option('baseline');page.locator('#target').fill('150');page.locator('#run').click();assert page.evaluate('verticalForceCurrent.forceTargetApplicable');assert 'Command above' in page.locator('#limit').inner_text();assert page.locator('#target-legend').is_visible();checks.append('Active PI retains applicable target and conditional capacity warning')
            page.set_viewport_size({'width':360,'height':820});page.locator('#case').select_option('release');page.locator('#target').fill('150');page.locator('#run').click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(OUT/'browser-release-150-mobile.png'),full_page=True);checks.append('Corrected labels and controls fit 360px without overflow')
            assert not errors,errors;browser.close()
    finally:server.shutdown()
    receipt={'passed':True,'checks':checks,'javascript_errors':errors,'html_sha256':hashlib.sha256((OUT/'vertical-force-lab.html').read_bytes()).hexdigest()};(OUT/'mode-browser-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print('\n'.join(checks))

if __name__=='__main__':run()
