"""Offline geometry-only JPEG85 -> one shared palette GIF. Supervisor owns it.
No solver/material import, numerical evaluation, coordinate interpolation or external network.
"""
import hashlib, io, json, os, pathlib, struct, sys, time, tempfile, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image
from playwright.sync_api import sync_playwright
from capture_store import read_slots
from gif_encode import encode_shared_palette
from watchdog import read_regular, digest, encoded, ROOT, validate_review_bytes, HARNESS_PATHS
MAX_FRAMES=34;MAX_JPEG=262144;MAX_GIF=8388608;MAX_ARTIFACT_BYTES=33554432
PINNED_BUNDLE='8b374b95b55dfb8d81884ea1d1e7b705dccbbc56240efd762c1678df212157e5'
BUNDLE_CLOSURE={'geometry.mjs':'1805826268afbdd63474a13e37e150e9e81fdec0d8fdcd131ca0f6e6ed32c29f','render-browser.mjs':'8bdc261db1b8b301f87c96265c5ceebb6f0b0581198ec07346cc109505c33b81','three/build/three.module.js':'c8211c69345d2e9949dc7a8ac969380497aa0600a5a8ac6a459c8cd02dd9cb8a','three/build/three.core.js':'eb077d2417f61d3e6d9264c317cabc4ea35769ed6b0ab533067292a550784c20'}
def prebuilt_bundle(cfg):
    # Reuse the exact bundle independently reviewed at 424af685. This removes
    # redundant Node/esbuild children, not their charges from the watchdog.
    # Fixed byte and four-source closure pins reject caller-selected substitutes.
    modules=pathlib.Path(cfg['nodeModules'])
    if json.loads(read_regular(modules/'three/package.json'))['version']!='0.180.0' or json.loads(read_regular(modules/'esbuild/package.json'))['version']!='0.25.10':raise ValueError('Unpinned installed dependency')
    for name,sha in BUNDLE_CLOSURE.items():
        path=modules/name if name.startswith('three/') else pathlib.Path(__file__).with_name(name)
        if digest(read_regular(path,2097152))!=sha:raise ValueError('Changed prebuilt bundle closure '+name)
    bundle=read_regular(cfg['browserBundle'],1048576)
    if digest(bundle)!=PINNED_BUNDLE:raise ValueError('Changed exact prebuilt browser bundle')
    return bundle,dict(threeVersion='0.180.0',esbuildVersion='0.25.10',browserBundleSHA256=PINNED_BUNDLE,closureSHA256=BUNDLE_CLOSURE,bundleReviewedAt='424af6853028ae606a692fce99a31fe679d84f42',bundleReuse=True,buildChildProcesses=0,networkDownloads=0,physicalEvaluations=0)
def configure_scratch(profile):
    profile.mkdir(mode=0o700)
    # All Chromium/Playwright scratch, including crashpad and socket directories,
    # lies under the one independently charged owned scratch root.
    os.environ['XDG_CONFIG_HOME']=str(profile/'xdg-config')
    os.environ['XDG_CACHE_HOME']=str(profile/'xdg-cache')
    os.environ['TMPDIR']=str(profile);tempfile.tempdir=str(profile)
def local_preview(out):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ['/viewer.html','/viewer.js']:
                self.send_error(404);return
            data=read_regular(out/self.path[1:],2097152)
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8' if self.path.endswith('.html') else 'application/javascript');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
        def log_message(self,*args):pass
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server,thread,'http://127.0.0.1:'+str(server.server_port)
def existing_page(browser):
    if len(browser.pages)!=1:raise ValueError('Expected one initial persistent-context page')
    return browser.pages[0]
def display_frames(frames,synthetic):
    # Synthetic residual placeholders are not physical measurements. Retain
    # their raw capture metadata in the receipt; show 'not evaluated' on images.
    rows=[dict(row) for row in frames]
    if synthetic:
        for row in rows:row.pop('residualN',None)
    return rows
def main():
    cfg=json.loads(read_regular(sys.argv[1],4194304));out=pathlib.Path(cfg['output']);manifest_bytes=read_regular(cfg['manifest'],4194304);m=json.loads(manifest_bytes);mh=digest(manifest_bytes)
    if set(m.get('harnessFiles',{}))!=HARNESS_PATHS:raise ValueError('Changed renderer/harness inventory')
    for name,h in m['harnessFiles'].items():
        if digest(read_regular(ROOT/name))!=h:raise ValueError('Changed local renderer/harness source '+name)
    if not cfg['syntheticOnly']:
        review=m.get('reviewReceipt') or {}
        if review.get('verdict')!='PASS_RUN_READY_SOURCE_ONLY' or review.get('sourceCommit')!=m['harnessCommit']:raise ValueError('Missing exact source review')
        validate_review_bytes(m)
    camera=m['camera'];camera_bytes=json.dumps(camera,separators=(',',':'),ensure_ascii=False).encode()
    if digest(camera_bytes)!=m['cameraSHA256'] or camera['jpegQuality']!=85 or camera['width']!=960 or camera['height']!=720 or camera['cameraFit']!='FIXED_NO_FRAME_RESCALE':raise ValueError('Pinned fixed camera required')
    gitem=m['inputs']['generated/arm-reference.json'];gbytes=gitem['text'].encode()
    if digest(gbytes)!=gitem['sha256']:raise ValueError('Geometry source hash')
    frames=[];captureHashes={}
    for p in cfg['captures']:
        raw=read_regular(p,196608);captureHashes[pathlib.Path(p).name]=digest(raw)
        rows=read_slots(pathlib.Path(p));last=-1
        for row in rows:
            for k,v in dict(manifestSHA256=mh,harnessCommit=m['harnessCommit'],operatorCommit=m['operatorCommit'],inputCommit=m['inputCommit'],modelSHA256=gitem['sha256'],inputStateSHA256=m['inputs']['audit/arm-rest-results.json']['sha256'],cameraSHA256=m['cameraSHA256'],jointScaleMPerRad=.1).items():
                if row.get(k)!=v:raise ValueError('Frame provenance '+k)
            if row['sequence']<=last:raise ValueError('Frame chronology')
            last=row['sequence'];frames.append(row)
    if not 1<=len(frames)<=MAX_FRAMES:raise ValueError('Retained frame count bound')
    # Never upgrade step-candidate/iterate captions to physical motion. Even a
    # successful campaign must be reviewed separately before scientific reuse.
    if not cfg['syntheticOnly']:
        receipt=json.loads(read_regular(cfg['resourceReceipt'],1048576))
        if receipt.get('manifestSHA256')!=mh or receipt.get('allProcessesDisposed') is not True or not all(r.get('allProcessesReaped') is True for r in receipt.get('resources',[])):raise ValueError('Numerical worker disposal not verified')
        for name,h in captureHashes.items():
            if receipt.get('fileHashes',{}).get(name,{}).get('sha256')!=h:raise ValueError('Unbound capture receipt')
    written={};used=0
    def write(name,b,maximum):
        nonlocal used
        if len(b)>maximum or used+len(b)>MAX_ARTIFACT_BYTES:raise ValueError('Postprocessing artifact ceiling')
        fd=os.open(out/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        try:
            with os.fdopen(fd,'wb',closefd=False) as f:f.write(b);f.flush();os.fsync(fd)
        finally:os.close(fd)
        used+=len(b);written[name]=dict(bytes=len(b),sha256=digest(b))
    started=time.monotonic();b,deps=prebuilt_bundle(cfg);write('viewer.js',b,1048576)
    data=dict(geometry=json.loads(gbytes),camera=camera,frames=display_frames(frames,cfg['syntheticOnly']),syntheticOnly=cfg['syntheticOnly'])
    # Embedded data makes viewer/downloads portable; escaped '<' prevents HTML
    # script termination from source strings. No external script/font/image.
    html=('''<!doctype html><meta charset="utf-8"><title>Kenoma provisional geometry</title><style>*{box-sizing:border-box}body{margin:0;background:#15202a;color:#f0f4f7;font:18px Arial;width:960px;height:720px}h1{font-size:22px;margin:14px 18px 8px}p{margin:8px 18px;line-height:1.3}#scope{font-size:16px}canvas{display:block;width:960px;height:560px}nav{display:flex;position:fixed;top:10px;right:12px;gap:6px}nav button{font:16px Arial;padding:6px}h1{max-width:690px}</style><h1 id="title"></h1><p id="caption"></p><canvas></canvas><p id="scope"></p><nav><button id="previous">Previous</button><button id="next">Next</button></nav><script>window.captureData='''+json.dumps(data,separators=(',',':')).replace('<','\\u003c')+'''</script><script src="viewer.js"></script><script>let n=0;previous.onclick=()=>drawCapture(n=Math.max(0,n-1));next.onclick=()=>drawCapture(n=Math.min(captureData.frames.length-1,n+1));</script>''').encode()
    write('viewer.html',html,2097152)
    jpgs=[];browser_receipt={};profile=out/'browser-profile';configure_scratch(profile)
    server,server_thread,origin=local_preview(out)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch_persistent_context(str(profile),executable_path='/usr/bin/chromium',headless=True,viewport=dict(width=960,height=720),device_scale_factor=1)
            page=existing_page(browser);errors=[];labels=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.route('**/*',lambda route:route.continue_() if route.request.url in [origin+'/viewer.html',origin+'/viewer.js'] else route.abort())
            page.goto(origin+'/viewer.html',wait_until='load',timeout=20000);page.wait_for_function('window.captureReady===true',timeout=20000)
            page.evaluate("document.querySelector('nav').style.display='none'")
            for i,row in enumerate(frames):
                page.evaluate('(i)=>window.drawCapture(i)',i)
                rendered=page.evaluate('window.lastRendered')
                if rendered!=dict(index=i,coordinatesSHA256=row['coordinatesSHA256'],cameraSHA256=row['cameraSHA256'],physicalEvaluations=0):raise ValueError('Browser frame binding')
                title=page.locator('#title').inner_text();caption=page.locator('#caption').inner_text();scope=page.locator('#scope').inner_text()
                expected_title='SYNTHETIC COORDINATE TEST — NO SIMULATION' if cfg['syntheticOnly'] else 'PROVISIONAL SOLVER GEOMETRY — NO ACCEPTED MOTION'
                if title!=expected_title or scope!=camera['depiction'] or f"Job {row['run']} · attempt {row['attempt']} · capture {row['sequence']} · {row['kind']}" not in caption:raise ValueError('Capture authority/caption gate')
                if cfg['syntheticOnly'] and 'residual not evaluated' not in caption:raise ValueError('Synthetic residual authority gate')
                labels.append(dict(frame=i,title=title,caption=caption,depiction=scope))
                jpeg=page.screenshot(type='jpeg',quality=85,animations='disabled',timeout=10000)
                im=Image.open(io.BytesIO(jpeg));im.load()
                if im.size!=(960,720) or im.format!='JPEG' or im.quantization[0][0]!=5:raise ValueError('Actual JPEG quality85 quantization gate')
                name=f'frame-{i:02d}.jpg';write(name,jpeg,MAX_JPEG);jpgs.append(name)
            # Exercise real portable viewer navigation after recording frames.
            page.evaluate("document.querySelector('nav').style.display='block'")
            page.locator('#previous').click();expected=max(0,len(frames)-2)
            # Buttons start at zero, independently of capture calls above.
            if page.evaluate('window.lastRendered.index')!=0:raise ValueError('Previous control')
            page.locator('#next').click()
            if page.evaluate('window.lastRendered.index')!=min(1,len(frames)-1):raise ValueError('Next control')
            for _ in range(len(frames)+1):page.locator('#next').click()
            if page.evaluate('window.lastRendered.index')!=len(frames)-1:raise ValueError('Next boundary control')
            for _ in range(len(frames)+1):page.locator('#previous').click()
            if page.evaluate('window.lastRendered.index')!=0:raise ValueError('Previous boundary control')
            if errors:raise ValueError('Browser errors: '+str(errors))
            browser_receipt=dict(browserVersion=browser.browser.version,renderer=page.evaluate("document.querySelector('canvas').getContext('webgl2').getParameter(document.querySelector('canvas').getContext('webgl2').RENDERER)"),frames=len(frames),jpegQuality=85,jpegQuantizationFirst=5,controls='PASS',boundaryControls='PASS',authorityLabels=labels,pageErrors=errors,physicalEvaluations=0,externalRequestsAllowed=0,transport='Exclusive two-file loopback HTTP; browser policy unchanged',initialPageReused=True,newPageCalls=0)
            browser.close()
    finally:
        server.shutdown();server.server_close();server_thread.join(timeout=1)
    # Only the driver removes owned scratch, after verified process disposal.
    # One global palette sampled across every recorded JPEG. No interpolated
    # coordinates or intermediate GIF frames; quantization/encoding only.
    gifbytes,gif_receipt=encode_shared_palette([out/name for name in jpgs]);write('provisional-geometry.gif',gifbytes,MAX_GIF)
    receipt=dict(status='PASS_SYNTHETIC_ONLY' if cfg['syntheticOnly'] else 'PASS_PROVISIONAL_GEOMETRY_ONLY',physicalEvaluations=0,physicalMotionAccepted=False,anatomicalQualification=False,manifestSHA256=mh,sourceCommit=m['harnessCommit'],captureHashes=captureHashes,cameraSHA256=m['cameraSHA256'],dependencies=deps,browser=browser_receipt,gif=gif_receipt,retainedFrames=[{k:row.get(k) for k in ['run','attempt','sequence','attemptSequence','kind','iteration','residualN','syntheticOnly','syntheticResidualPlaceholder','origin','coordinatesSHA256']} for row in frames],fileHashes=written,wallSeconds=time.monotonic()-started,outputArtifactBytes=used)
    write('render-receipt.json',encoded(receipt),262144)
    os.write(int(os.environ['KENOMA_RESULT_FD']),encoded(dict(status='PASS',syntheticOnly=cfg['syntheticOnly'],renderReceiptSHA256=written['render-receipt.json']['sha256'],physicalEvaluations=0,physicalMotionAccepted=False)))
if __name__=='__main__':main()
