"""Own actual Chromium controls at 1200/390/320px and portable local downloads.

Run only after dependency provisioning/memory ordering is approved. No anatomy,
global build, remote assets, deployment or whole-book claim.
"""
from pathlib import Path
from functools import partial
import argparse,hashlib,http.server,importlib.metadata,json,math,socketserver,threading
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from paths import HERE,checked_output,source_hashes

DEFAULT={'deltaMicrometres':1,'leftShearKPa':20,'rightShearKPa':20,'preset':'equal'}
FIELDS={'delta':'deltaMicrometres','leftg':'leftShearKPa','rightg':'rightShearKPa'}
def require(ok,message):
    if not ok:raise RuntimeError(message)

def oracle(values):
    d=values['deltaMicrometres']*1e-6;k1,k2=(100,100) if values['preset']=='equal' else (50,200)
    cl=5*values['leftShearKPa'];cr=5*values['rightShearKPa']
    qr=0 if cr==0 else d/(1/k1+1/cr);ql=0 if cl==0 else d/(1/k2+1/cl)
    u=qr/k1;v=d-ql/k2;ke=(0 if cr==0 else 1/(1/k1+1/cr))+(0 if cl==0 else 1/(1/k2+1/cl))
    return dict(delta=d,K1=k1,K2=k2,CL=cl,CR=cr,u=u,v=v,upperForceN=qr,lowerForceN=ql,
      leftExchangeN=ql,rightExchangeN=qr,leftPullN=qr+ql,rightPullN=qr+ql,externalLeftForceN=-qr-ql,externalRightForceN=qr+ql,
      effectiveStiffnessNPerM=ke,energyJ=(qr+ql)*d/2,upperStrain=u/.01,lowerStrain=(d-v)/.01,
      leftShearStrain=v/.0002,rightShearStrain=(d-u)/.0002)

def check_state(page,values):
    actual=page.evaluate('window.lateralTransfer.snapshot()');expected=oracle(values)
    require(actual['input']==values,'Unexpected admitted input')
    for key,x in expected.items():
        require(abs(actual[key]-x)<=1e-18+1e-11*abs(x),'Independent browser state mismatch: '+key)
    for control,key in FIELDS.items():
        require(float(page.locator('#'+control).input_value())==values[key],'Wrong slider: '+control)
        require(float(page.locator('#'+control+'-number').input_value())==values[key],'Wrong paired number: '+control)
    require(page.locator('#preset').input_value()==values['preset'],'Wrong preset')
    require(page.locator('#end-force').inner_text()==f"{expected['externalRightForceN']*1e3:.3f} mN",'Wrong visible force')
    for key,text in {'u':f"{expected['u']*1e6:.3f} µm",'v':f"{expected['v']*1e6:.3f} µm",
      'effective':f"{expected['effectiveStiffnessNPerM']:.3f} N/m",'energy':f"{expected['energyJ']*1e12:.3f} pJ"}.items():
        require(page.locator(f'[data-key="{key}"]').inner_text()==text,'Wrong visible output: '+key)
    paths=(expected['CL']>0)+(expected['CR']>0)
    require(page.locator('#path-tag').inner_text()==['Disconnected','One load path','Two load paths'][paths],'Wrong path interpretation')
    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'Horizontal overflow')
    return actual

def run(site,output,chromium=None):
    out=checked_output(output);site=site.resolve()
    manifest=json.loads((site/'build-manifest.json').read_text())
    require(manifest['source_sha256']==source_hashes(),'Site/source binding mismatch')
    receipt={'status':'running','source_sha256':source_hashes(),'site_manifest_sha256':hashlib.sha256((site/'build-manifest.json').read_bytes()).hexdigest(),
      'checks':[],'captures':[],'visual_acceptance':'pending independent appearance inspection',
      'playwright_version':importlib.metadata.version('playwright'),'scope':'Standalone guided discrete lab only; no full-book or anatomy qualification.'}
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.path=='/favicon.ico':self.send_response(204);self.end_headers()
            else:super().do_GET()
    def capture(page,name):
        path=out/name;page.screenshot(path=str(path),type='jpeg',quality=85,full_page=True)
        receipt['captures'].append({'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'quality':85})
    try:
        with socketserver.TCPServer(('127.0.0.1',0),partial(Quiet,directory=str(site))) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            origin=f'http://127.0.0.1:{server.server_address[1]}'
            try:
                with sync_playwright() as playwright:
                    if chromium is not None:
                        chromium=chromium.resolve()
                        require(chromium.is_file(),'Explicit existing Chromium executable required; no installation performed')
                    browser=playwright.chromium.launch(headless=True,**({'executable_path':str(chromium)} if chromium is not None else {}))
                    receipt['browser_version']=browser.version
                    receipt['chromium_executable']=str(chromium) if chromium is not None else 'Playwright installed default'
                    for width,height in [(1200,900),(390,844),(320,720)]:
                        context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1)
                        errors=[]
                        def local_only(route):
                            if urlsplit(route.request.url).netloc==urlsplit(origin).netloc:route.continue_()
                            else:errors.append('Unexpected remote request: '+route.request.url);route.abort()
                        context.route('**/*',local_only);page=context.new_page()
                        page.on('pageerror',lambda error:errors.append(str(error)))
                        page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
                        page.on('requestfailed',lambda request:errors.append('Request failed: '+request.url))
                        page.on('response',lambda response:errors.append(f'HTTP {response.status}: {response.url}') if response.status>=400 else None)
                        page.goto(origin+'/index.html',wait_until='networkidle');page.wait_for_function('window.lateralTransfer !== undefined')
                        check_state(page,DEFAULT);capture(page,f'lab-{width}-default.jpg')
                        page.locator('#delta').focus();page.keyboard.press('ArrowRight')
                        check_state(page,{**DEFAULT,'deltaMicrometres':1.1})
                        exercised=[]
                        for control,key in FIELDS.items():
                            for action,value in [('Home',0),('End',2 if control=='delta' else 80)]:
                                page.locator('#reset').click();page.locator('#'+control).focus();page.keyboard.press(action)
                                check_state(page,{**DEFAULT,key:value});exercised.append(control+':'+action)
                        page.locator('#reset').click();page.locator('#preset').select_option('unequal')
                        values={**DEFAULT,'preset':'unequal'};check_state(page,values)
                        page.locator('#leftg-number').fill('5');page.locator('#rightg-number').fill('80')
                        values={**values,'leftShearKPa':5,'rightShearKPa':80};admitted=check_state(page,values)
                        if width==390:capture(page,'lab-390-asymmetric.jpg')
                        page.locator('#export').click();require(json.loads(page.locator('#state-export').input_value())==admitted,'Stale exported state')
                        for control,value in [('delta-number','3'),('leftg-number','-1'),('rightg-number','')]:
                            page.locator('#'+control).fill(value);check_state(page,values)
                            require('Input rejected; last admitted state retained.' in page.locator('#status').inner_text(),'Missing invalid rollback explanation')
                            require(json.loads(page.locator('#state-export').input_value())==admitted,'Export changed on rejection')
                        page.locator('#reset').click();check_state(page,DEFAULT)
                        page.locator('#leftg').focus();page.keyboard.press('Home');page.locator('#rightg').focus();page.keyboard.press('Home')
                        values={**DEFAULT,'leftShearKPa':0,'rightShearKPa':0};check_state(page,values)
                        if width==390:capture(page,'lab-390-disconnected.jpg')
                        for _ in range(2):page.locator('#reset').click();check_state(page,DEFAULT)
                        downloads=[]
                        for anchor in page.locator('.downloads a').all():
                            href=anchor.get_attribute('href');require(not urlsplit(href).scheme and not href.startswith('/'),'Download must be a portable relative target')
                            response=page.request.get(origin+'/'+href)
                            require(response.status==200 and response.body()==(site/href).read_bytes(),'Broken/stale actual download: '+href)
                            downloads.append(href)
                        require(page.locator('#full-statements details').count()==6,'Missing complete six statements')
                        page.locator('#exact-source > summary').click()
                        require('theorem material_resultants' in page.locator('#exact-source').inner_text(),'Missing full source')
                        require(not errors,'Browser errors: '+str(errors))
                        receipt['checks'].append({'width':width,'height':height,'controls':exercised,'asymmetric_material_preset':True,
                          'rollback_inputs':3,'state_export':True,'zero_links':True,'repeated_reset':True,'downloads':downloads,'browser_errors':errors,'horizontal_overflow':False})
                        context.close()
                    context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
                    page=context.new_page();page.goto(origin+'/index.html',wait_until='networkidle')
                    require(page.locator('noscript').is_visible(),'Missing no-JavaScript explanation')
                    require(page.locator('.nojs-controls').is_visible(),'Missing static default inputs')
                    require(page.locator('#end-force').inner_text()=='0.100 mN','Missing default force without JS')
                    require(page.locator('#full-statements details').count()==6,'Missing statements without JS')
                    page.locator('#exact-source > summary').click()
                    require('theorem stationary_solution' in page.locator('#exact-source').inner_text(),'Missing exact source without JS')
                    require(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'No-JavaScript overflow')
                    capture(page,'lab-390-no-javascript.jpg');receipt['no_javascript_static_fallback']=True
                    context.close();browser.close()
            finally:server.shutdown();thread.join()
        receipt['status']='passed'
    except Exception as error:
        receipt['status']='failed';receipt['error']=str(error);raise
    finally:(out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Actual 1200/390/320 controls, rollback, export, downloads, reset and static reading passed; inspect captures separately.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--site',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--chromium',type=Path,help='Explicit already-installed Chromium when the Playwright default is unavailable')
    a=p.parse_args();run(a.site,a.output,a.chromium)
