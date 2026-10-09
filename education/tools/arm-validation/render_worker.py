"""Offline geometry-only JPEG85 -> one shared palette GIF. Supervisor owns it.
No solver/material import, numerical evaluation, coordinate interpolation or network.
"""
import hashlib, io, json, os, pathlib, shutil, struct, subprocess, sys, time
from PIL import Image
from playwright.sync_api import sync_playwright
from capture_store import read_slots
from watchdog import read_regular, digest, encoded
MAX_FRAMES=34;MAX_JPEG=262144;MAX_GIF=8388608;MAX_ARTIFACT_BYTES=33554432
def main():
    cfg=json.loads(read_regular(sys.argv[1],4194304));out=pathlib.Path(cfg['output']);manifest_bytes=read_regular(cfg['manifest'],4194304);m=json.loads(manifest_bytes);mh=digest(manifest_bytes)
    camera=m['camera'];camera_bytes=json.dumps(camera,separators=(',',':'),ensure_ascii=False).encode()
    if digest(camera_bytes)!=m['cameraSHA256'] or camera['jpegQuality']!=85 or camera['width']!=960 or camera['height']!=720 or camera['cameraFit']!='FIXED_NO_FRAME_RESCALE':raise ValueError('Pinned fixed camera required')
    gitem=m['inputs']['generated/arm-reference.json'];gbytes=gitem['text'].encode()
    if digest(gbytes)!=gitem['sha256']:raise ValueError('Geometry source hash')
    frames=[];captureHashes={}
    for p in cfg['captures']:
        raw=read_regular(p,196608);captureHashes[pathlib.Path(p).name]=digest(raw)
        rows=read_slots(pathlib.Path(p));last=0
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
    started=time.monotonic();tool=pathlib.Path(__file__).with_name('render-build.mjs');bundle=out/'viewer.js'
    result=subprocess.run([cfg['nodeExecutable'],str(tool),cfg['nodeModules'],str(bundle)],capture_output=True,timeout=20,check=True)
    deps=json.loads(result.stdout);b=read_regular(bundle,1048576);used+=len(b);written['viewer.js']=dict(bytes=len(b),sha256=digest(b))
    data=dict(geometry=json.loads(gbytes),camera=camera,frames=frames,syntheticOnly=cfg['syntheticOnly'])
    # Embedded data makes viewer/downloads portable; escaped '<' prevents HTML
    # script termination from source strings. No external script/font/image.
    html=('''<!doctype html><meta charset="utf-8"><title>Kenoma provisional geometry</title><style>*{box-sizing:border-box}body{margin:0;background:#15202a;color:#f0f4f7;font:18px Arial;width:960px;height:720px}h1{font-size:22px;margin:14px 18px 8px}p{margin:8px 18px;line-height:1.3}#scope{font-size:16px}canvas{display:block;width:960px;height:580px}nav{display:none}</style><h1 id="title"></h1><p id="caption"></p><canvas></canvas><p id="scope"></p><nav><button id="previous">Previous</button><button id="next">Next</button></nav><script>window.captureData='''+json.dumps(data,separators=(',',':')).replace('<','\\u003c')+'''</script><script src="viewer.js"></script><script>let n=0;previous.onclick=()=>drawCapture(n=Math.max(0,n-1));next.onclick=()=>drawCapture(n=Math.min(captureData.frames.length-1,n+1));</script>''').encode()
    write('viewer.html',html,2097152)
    jpgs=[];browser_receipt={};profile=out/'browser-profile';profile.mkdir(mode=0o700)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch_persistent_context(str(profile),executable_path='/usr/bin/chromium',headless=True,viewport=dict(width=960,height=720),device_scale_factor=1)
            page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.route('**/*',lambda route:route.continue_() if route.request.url.startswith('file:') else route.abort())
            page.goto((out/'viewer.html').as_uri(),wait_until='load',timeout=20000);page.wait_for_function('window.captureReady===true',timeout=20000)
            for i,row in enumerate(frames):
                page.evaluate('(i)=>window.drawCapture(i)',i)
                rendered=page.evaluate('window.lastRendered')
                if rendered!=dict(index=i,coordinatesSHA256=row['coordinatesSHA256'],cameraSHA256=row['cameraSHA256'],physicalEvaluations=0):raise ValueError('Browser frame binding')
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
            if errors:raise ValueError('Browser errors: '+str(errors))
            browser_receipt=dict(browserVersion=browser.browser.version,renderer=page.evaluate("document.querySelector('canvas').getContext('webgl2').getParameter(document.querySelector('canvas').getContext('webgl2').RENDERER)"),frames=len(frames),jpegQuality=85,jpegQuantizationFirst=5,controls='PASS',pageErrors=errors,physicalEvaluations=0,externalRequestsAllowed=0)
            browser.close()
    finally:shutil.rmtree(profile)
    # One global palette sampled across every recorded JPEG. No interpolated
    # coordinates or intermediate GIF frames; quantization/encoding only.
    thumbs=[]
    for name in jpgs:
        with Image.open(out/name) as image:thumbs.append(image.convert('RGB').resize((160,120)))
    atlas=Image.new('RGB',(160,120*len(thumbs)))
    for i,im in enumerate(thumbs):atlas.paste(im,(0,120*i))
    palette=atlas.quantize(colors=256,method=Image.Quantize.MEDIANCUT);palette_bytes=bytes(palette.getpalette());quantized=[]
    for name in jpgs:
        with Image.open(out/name) as image:quantized.append(image.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE))
    gif=io.BytesIO();quantized[0].save(gif,format='GIF',save_all=True,append_images=quantized[1:],optimize=False,duration=500,loop=0,disposal=2);gifbytes=gif.getvalue();write('provisional-geometry.gif',gifbytes,MAX_GIF)
    with Image.open(io.BytesIO(gifbytes)) as im:
        if im.n_frames!=len(frames) or im.size!=(960,720):raise ValueError('GIF frame/resolution gate')
    receipt=dict(status='PASS_SYNTHETIC_ONLY' if cfg['syntheticOnly'] else 'PASS_PROVISIONAL_GEOMETRY_ONLY',physicalEvaluations=0,physicalMotionAccepted=False,anatomicalQualification=False,manifestSHA256=mh,sourceCommit=m['harnessCommit'],captureHashes=captureHashes,cameraSHA256=m['cameraSHA256'],dependencies=deps,browser=browser_receipt,globalPaletteSHA256=digest(palette_bytes),paletteMethod='Shared all-frame JPEG thumbnail median-cut, 256 colors; no dithering',frameDurationMilliseconds=500,interpolation=False,retainedFrames=[{k:row.get(k) for k in ['run','attempt','sequence','attemptSequence','kind','iteration','residualN','coordinatesSHA256']} for row in frames],fileHashes=written,wallSeconds=time.monotonic()-started,outputArtifactBytes=used)
    write('render-receipt.json',encoded(receipt),262144)
    os.write(int(os.environ['KENOMA_RESULT_FD']),encoded(dict(status='PASS',syntheticOnly=cfg['syntheticOnly'],renderReceiptSHA256=written['render-receipt.json']['sha256'],physicalEvaluations=0,physicalMotionAccepted=False)))
if __name__=='__main__':main()
