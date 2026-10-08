"""Actual local controls, portable links and runtime damage checks under fixed caps."""
import argparse, functools, hashlib, http.server, json, os, pathlib, signal, subprocess, sys, threading, time, urllib.request

CGROUP_CAP = 16_000_000_000
RSS_CAP = 1_000_000_000
WALL_CAP = 240
OUTPUT_CAP = 16*1024*1024
def cg(): return int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
def group_rss(group):
    total=0
    for p in pathlib.Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try:
            stat=(p/'stat').read_text().rsplit(')',1)[1].split()
            if int(stat[2])!=group: continue
            for line in (p/'status').read_text().splitlines():
                if line.startswith('VmRSS:'): total+=int(line.split()[1])*1024
        except (OSError,ValueError): pass
    return total
def worker(preview,out):
    from playwright.sync_api import sync_playwright
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    handler=functools.partial(Quiet,directory=str(preview))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}/'
    failures=[];external=[];checks=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
            context=browser.new_context(viewport={'width':1280,'height':1000},accept_downloads=True)
            page=context.new_page()
            page.on('pageerror',lambda e: failures.append(str(e)))
            page.on('request',lambda r: external.append(r.url) if not r.url.startswith(base) and not r.url.startswith('blob:') else None)
            page.goto(base,wait_until='networkidle');page.locator('#workspace').wait_for(state='visible')
            def state():return json.loads(page.locator('#workspace').get_attribute('data-state'))
            assert state()['body']=='FJ1486' and state()['forceGate'] is False
            static=json.loads((preview/'geometry-receipt.json').read_text())
            oracle=next(r for r in static['rows'] if r['body']=='FJ1486' and r['fraction']==.5)
            for key,value in oracle['reference'].items():assert abs(state()['reference'][key]-value)<1e-8
            checks.append('actual browser quantities match source-bound geometry receipt')
            assert '64.067641' in page.locator('#failure').inner_text();checks.append('original adverse force gate visible')
            page.screenshot(path=str(out/'desktop.png'),full_page=True)
            values=page.locator('#body option').evaluate_all('(xs)=>xs.map(x=>x.value)')
            assert len(values)==7
            for id in values:
                page.select_option('#body',id);assert state()['body']==id
                assert state()['forceGate']==(False if id in ['FJ1486','FJ1512','FJ1478'] else None)
                assert ('Reference geometry only' in page.locator('#failure').inner_text())==(state()['forceGate'] is None)
            checks.append('all seven body controls and reference-only boundaries')
            page.select_option('#body','FJ1512');a=state()['reference']['tessellatedAreaMm2']
            page.locator('#station').fill('23');page.locator('#station').dispatch_event('input');b=state()
            assert b['fraction']==.23 and abs(b['reference']['tessellatedAreaMm2']-a)>1;checks.append('material station changes actual heterogeneous geometry')
            page.select_option('#resolution','8');assert state()['resolution']==8;checks.append('refinement control')
            page.select_option('#view','lateral');assert state()['view']=='lateral'
            page.select_option('#view','superior');assert state()['view']=='superior';checks.append('actual atlas projection controls')
            page.select_option('#patch','FJ1486_humerus_origin');assert state()['patch']=='FJ1486_humerus_origin';assert 'Distributed authored candidate' in page.locator('#attachment').inner_text();checks.append('source-face patch control')
            assert 'not assigned to this belly' in page.locator('#ownership').inner_text() and 'scapular origin estimate' in page.locator('#ownership').inner_text();checks.append('attachment ownership and estimated origin boundaries visible')
            page.locator('#overlay').uncheck();assert state()['overlay'] is False
            page.locator('#overlay').check();assert state()['overlay'] is True;checks.append('recorded-field overlay control')
            with page.expect_download() as pending:page.click('#export')
            download=pending.value;download.save_as(str(out/'downloaded-section.json'))
            saved=json.loads((out/'downloaded-section.json').read_text());assert saved['body']=='FJ1512' and saved['section']['fraction']==.23
            assert saved['modelSha256']==sha((preview/'model.json').read_bytes());assert len(saved['section']['triangles'])>0
            checks.append('actual downloaded P2 section positions and immutable identity')
            hrefs=page.locator('a[href]').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))')
            for href in hrefs:
                assert not href.startswith(('/', 'http:', 'https:')) and '..' not in href.split('/')
                with urllib.request.urlopen(base+href) as response:
                    assert response.status==200
                    assert response.read()==(preview/href).read_bytes()
            checks.append(f'{len(hrefs)} portable downloadable/reference links')
            page.click('#reset');assert state()['body']=='FJ1486' and state()['fraction']==.5 and state()['resolution']==4 and state()['view']=='posterior' and state()['overlay']
            checks.append('reset restores all controls')
            page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(200)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert page.locator('#station').is_visible();page.screenshot(path=str(out/'mobile.png'),full_page=True);checks.append('390px responsive controls without overflow')
            original=(preview/'model.json').read_bytes();manifest=json.loads((preview/'manifest.json').read_text())
            damage=json.loads(original);damage['patches']['radial_tuberosity']['triangle_indices_zero_based'][0]=999999
            damaged=json.dumps(damage,separators=(',',':')).encode()
            for label,rebind,message in [('identity',False,'Model identity mismatch'),('source-face',True,'Patch source face outside bone')]:
                ctx=browser.new_context();q=ctx.new_page()
                ctx.route('**/model.json',lambda route:route.fulfill(body=damaged,content_type='application/json'))
                if rebind:
                    altered={**manifest,'modelSha256':sha(damaged)}
                    ctx.route('**/manifest.json',lambda route:route.fulfill(body=json.dumps(altered),content_type='application/json'))
                q.goto(base,wait_until='networkidle');assert message in q.locator('#loading').inner_text();assert q.locator('#workspace').is_hidden()
                checks.append('runtime damage refusal: '+label);ctx.close()
            assert not failures and not external
            checks.append('no browser errors or external network requests')
            result={'result':'PASS_ACTUAL_BROWSER_CONTROLS_AND_DAMAGE','checks':checks,'browser':browser.version,'modelSha256':sha(original),'downloadSha256':sha((out/'downloaded-section.json').read_bytes()),'pageErrors':failures,'externalRequests':external,'limits':['Geometry/browser qualification only; Real, solver, whole-book/PDF and anatomical acceptance are not run.']}
            (out/'controls.json').write_text(json.dumps(result,indent=2)+'\n');browser.close()
    finally:server.shutdown();server.server_close()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',type=pathlib.Path,required=True);parser.add_argument('--evidence',type=pathlib.Path,required=True);parser.add_argument('--worker',action='store_true');args=parser.parse_args()
    if args.worker:worker(args.preview,args.evidence);return
    assert args.preview.is_absolute() and args.evidence.is_absolute() and not args.evidence.exists()
    assert cg()<CGROUP_CAP
    args.evidence.mkdir();start=time.monotonic();peak_cg=cg();peak_rss=0;failed=None
    command=[sys.executable,__file__,'--preview',str(args.preview),'--evidence',str(args.evidence),'--worker']
    with (args.evidence/'browser.log').open('x') as stream:
        child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        while child.poll() is None:
            peak_cg=max(peak_cg,cg());peak_rss=max(peak_rss,group_rss(child.pid))
            output=sum(p.stat().st_size for p in args.evidence.rglob('*') if p.is_file())
            if peak_cg>CGROUP_CAP:failed='cgroup cap'
            elif peak_rss>RSS_CAP:failed='browser group RSS cap'
            elif time.monotonic()-start>WALL_CAP:failed='wall cap'
            elif output>OUTPUT_CAP:failed='output cap'
            if failed:os.killpg(child.pid,signal.SIGKILL);break
            time.sleep(.05)
        code=child.wait()
    result={'result':'PASS_RESOURCE_GUARD' if code==0 and not failed else 'FAIL_RESOURCE_OR_BROWSER','exitCode':code,'failure':failed,'peakCgroupBytes':peak_cg,'peakBrowserGroupRssBytes':peak_rss,'elapsedSeconds':time.monotonic()-start,'caps':{'totalCgroupBytes':CGROUP_CAP,'browserGroupRssBytes':RSS_CAP,'wallSeconds':WALL_CAP,'outputBytes':OUTPUT_CAP}}
    (args.evidence/'resource-guard.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(0 if result['result']=='PASS_RESOURCE_GUARD' else 1)
if __name__=='__main__':main()
