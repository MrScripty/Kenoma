"""Exercise the shared GUI through actual controls, including nested poser and fallback.
--preview tests an explicitly unqualified GUI build; only dist binds a book receipt.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import argparse,hashlib,json,os,shutil,sys
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from executable_outputs import checked_build_outputs,executable_outputs,executable_digest,unchanged_outputs
from chapter_examples import runtime_resources
parser=argparse.ArgumentParser();parser.add_argument('--preview',type=Path);args=parser.parse_args()
out=(args.preview or ROOT/'dist').resolve();before=executable_outputs(out) if args.preview else checked_build_outputs(out)
runtime_before=runtime_resources(out)
registry=json.loads((out/'chapter-examples.json').read_text());capture=out/'chapter-example-qa';capture.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(out.parent)))
Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/{out.name}'
views=[]
try:
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'),args=['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  for name,width in [('desktop',1280),('mobile',390),('narrow',320)]:
   page=browser.new_page(viewport={'width':width,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(url+'/examples.html');tested=[]
   for e in registry['examples']:
    page.select_option('#example-choice',e['id']);page.wait_for_function('window.kenomaChapterExample?.ready',timeout=90000)
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),e['id']
    assert 'Scope:' in page.locator('#example-limits').inner_text()
    for link in page.locator('#example-links a').all():
     href=link.get_attribute('href')
     if not args.preview or not href.startswith('index.html#'):assert page.request.head(url+'/'+href).ok,href
    if e['kind']=='pose':
     frame=page.frames[1];assert frame.evaluate('simpleGraphEditor.ready')
     assert frame.locator('input[type=range]').count()==0
     assert frame.evaluate('simpleGraphEditor.renderer.webgl.info.render.calls>0')
    else:
     assert page.evaluate('!!kenomaChapterExample.viewport && kenomaChapterExample.viewport.webgl.info.render.calls>0')
     initial=page.evaluate('JSON.stringify(kenomaChapterExample.state)')
     fields=page.locator('#parameter-controls input[type=number],#parameter-controls select')
     for field in fields.all():
      tag=field.evaluate('e=>e.tagName')
      if tag=='SELECT':
       values=field.locator('option').evaluate_all('es=>es.map(e=>e.value)');value=next(v for v in values if v!=field.input_value());field.select_option(value)
      else:
       value=field.get_attribute('max') if field.input_value()!=field.get_attribute('max') else field.get_attribute('min');field.fill(value)
      key=field.get_attribute('id').removeprefix('parameter-')
      page.wait_for_function('({key,value})=>String(kenomaChapterExample.state.parameters[key])===value',arg={'key':key,'value':value},timeout=90000)
     assert page.evaluate('JSON.stringify(kenomaChapterExample.state)')!=initial,e['id']
     # Reset must rebuild the original state, not merely reposition the view.
     page.locator('#reset-example').click();page.wait_for_function('window.kenomaChapterExample?.ready',timeout=90000)
     assert page.evaluate('JSON.stringify(kenomaChapterExample.state)')==initial
    tested.append(e['id']);print(name,e['id'],'PASS',flush=True)
   # Pick an actual atlas triangle through the canvas, after clearing the default readout.
   page.select_option('#example-choice','04-anatomy');page.wait_for_function('kenomaChapterExample.ready')
   page.select_option('#parameter-part','3');page.wait_for_function("kenomaChapterExample.state.parameters.part==='3'")
   atlas_canvas=page.locator('#example-viewport canvas');atlas_canvas.scroll_into_view_if_needed();atlas_canvas.click(position={'x':2,'y':2});expect(page.locator('#selection-info')).to_be_empty()
   point=page.evaluate('''()=>{const v=kenomaChapterExample.viewport,s=kenomaChapterExample.state.objects[0],face=s.faces[0],p=v.controls.target.clone().set(0,0,0);for(const i of face)p.add(v.controls.target.clone().fromArray(s.vertices[i]));p.multiplyScalar(1/3).project(v.camera);const b=v.webgl.domElement.getBoundingClientRect();return {x:b.left+(p.x+1)*b.width/2,y:b.top+(1-p.y)*b.height/2,name:s.source.name,hash:s.source.hash}}''')
   page.mouse.click(point['x'],point['y']);expect(page.locator('#selection-info')).to_contain_text(point['name']);expect(page.locator('#selection-info')).to_contain_text(point['hash'])
   assert page.request.head(url+'/'+page.locator('#selection-info a').get_attribute('href')).ok
   page.select_option('#example-choice','01-force');page.wait_for_function('kenomaChapterExample.ready')
   canvas=page.locator('#example-viewport canvas');canvas.focus();position=page.evaluate('kenomaChapterExample.viewport.camera.position.toArray()');page.keyboard.press('ArrowLeft')
   assert page.evaluate('kenomaChapterExample.viewport.camera.position.toArray()')!=position
   force=page.locator('#parameter-force');force.fill('100');expect(force).to_have_attribute('aria-invalid','true');assert page.evaluate('kenomaChapterExample.parameters.force')==4
   force.fill('8');page.wait_for_function('kenomaChapterExample.state.parameters.force===8')
   assert page.evaluate('''()=>{const v=kenomaChapterExample.viewport;const s=kenomaChapterExample.state.objects.find(o=>o.type==='sphere');const p=v.controls.target.clone().fromArray(s.center).project(v.camera);return Math.abs(p.x)<.95&&Math.abs(p.y)<.95&&Math.abs(p.z)<1}'''), 'Changed force mass must remain visible'
   page.screenshot(path=str(capture/(name+'-force.png')),full_page=True)
   old=page.evaluate_handle('kenomaChapterExample.viewport');page.select_option('#example-choice','02-torque');page.wait_for_function('kenomaChapterExample.ready');assert old.evaluate('v=>v.disposed');old.dispose()
   page.evaluate("kenomaChapterExample.viewport.webgl.getContext().getExtension('WEBGL_lose_context').loseContext()")
   expect(page.locator('#example-viewport')).to_contain_text('context lost')
   page.set_viewport_size({'width':width+20,'height':1000});page.wait_for_timeout(100);page.set_viewport_size({'width':width,'height':1000})
   page.locator('#parameter-angle').fill('60');page.wait_for_function('kenomaChapterExample.state.parameters.angle===60')
   if not args.preview:
    page.goto(url+'/index.html');assert page.locator('.proof-card').count()==115
    assert page.locator('.claim-toggle[aria-expanded=false]').count()==115
    button=page.locator('.claim-toggle').first;body=page.locator('.claim-technical').first;expect(body).not_to_be_visible();button.focus();page.keyboard.press('Enter');expect(body).to_be_visible();page.keyboard.press('Space');expect(body).not_to_be_visible()
    assert page.locator('.chapter-example').count()==27
    for ident in ['01-force','00-scope']:
     page.locator('[data-chapter-example="'+ident+'"]').click()
     assert page.locator('.chapter-example-frame').count()==1
     page.frame_locator('.chapter-example-frame').locator('#example-choice').wait_for()
     frame=next(f for f in page.frames if 'examples.html' in f.url)
     frame.wait_for_function('window.kenomaChapterExample?.ready',timeout=90000)
    page.locator('[data-chapter-example="00-scope"]').click();assert page.locator('.chapter-example-frame').count()==0
    page.emulate_media(media='print');expect(body).to_be_visible()
   assert not errors,errors
   views.append({'name':name,'width':width,'chapters':tested,'controlsResetKeyboardInvalidInputDisposeContextLoss':True,'errors':errors});page.close()
  # Rendering failure must not erase numerical access.
  page=browser.new_page();page.add_init_script("HTMLCanvasElement.prototype.getContext=function(){return null}");page.goto(url+'/examples.html?chapter=01-force');page.wait_for_function('kenomaChapterExample.ready');expect(page.locator('#example-status')).to_contain_text('WebGL is unavailable');page.locator('#parameter-force').fill('8');page.wait_for_function('kenomaChapterExample.state.parameters.force===8');page.close()
  if not args.preview:
   page=browser.new_page(java_script_enabled=False);page.goto(url+'/index.html');expect(page.locator('.claim-technical').first).to_be_visible();assert page.locator('.chapter-example a').count()==27;page.close()
  browser.close()
finally:server.shutdown();server.server_close()
unchanged_outputs(out,before)
assert runtime_resources(out)==runtime_before
receipt={'result':'PASS_GUI_PREVIEW_ONLY' if args.preview else 'PASS_CHAPTER_EXAMPLES','chapters':27,'views':views,'executable_outputs_sha256':executable_digest(before),'registry_sha256':hashlib.sha256((out/'chapter-examples.json').read_bytes()).hexdigest(),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'noWebGLTextFallback':True,'preview':bool(args.preview),'runtime_resources':runtime_before}
(capture/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
