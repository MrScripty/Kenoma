"""Source-bound native review views for this candidate; not anatomical approval."""
from pathlib import Path
import hashlib,json,os,shutil
from render_pdf import serve
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'data/anatomical-arm-v1/review/coupling-candidate';out.mkdir(parents=True,exist_ok=True)
server,url=serve()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
  page=browser.new_page(viewport={'width':650,'height':1200});page.goto(url+'/anatomy-inspection/index.html');page.wait_for_function('window.inspectionReady')
  page.evaluate('()=>{inspectApi.setFocus("arm");inspectApi.show("all");inspectApi.setView("oblique");}')
  page.locator('#scene').screenshot(path=str(out/'atlas-assembly-bind.png'))
  page.evaluate('()=>{inspectApi.setFocus("elbow");inspectApi.show("bones");inspectApi.setView("anterior");}')
  for q in [0,90,120]:
   page.evaluate('(q)=>inspectApi.setPose(q*Math.PI/180)',q);page.locator('#scene').screenshot(path=str(out/f'interior-axis-{q}.png'))
  page.locator('#bind').click()
  for name in ['radial_tuberosity','brachialis_ulna','olecranon','distal_radius_brachioradialis','FJ1486_humerus_origin','FJ1480_humerus_origin','FJ1477_humerus_origin','FJ1487_humerus_origin']:
   page.evaluate('(name)=>{inspectApi.setFocus(name.includes("humerus")||name.includes("distal_radius")?"arm":"elbow");inspectApi.setView(name.includes("olecranon")?"lateral":"oblique");inspectApi.showPatch(name);}',name)
   page.locator('#scene').screenshot(path=str(out/f'patch-{name}.png'))
  browser.close()
finally:server.shutdown();server.server_close()
for name in ['rest','loaded','released']:shutil.copy(ROOT/f'dist/coupled-review/desktop-{name}.png',out/f'fixture-{name}.png')
paths=['data/elbow-v1/data/bodyparts3d_right_arm_m.json','data/anatomical-arm-v1/generated/arm-geometry.json','data/anatomical-arm-v1/config/attachments.json','data/anatomical-arm-v1/audit/interior-axis-fit.json','data/anatomical-arm-v1/audit/apposition-results.json','web/anatomical-coupled-fixture.mjs','tools/anatomy-inspector.mjs','tools/coupled-inspector.mjs','tools/capture-anatomical-review.py']
receipt={'schema':1,'sourceHashes':{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in paths},'images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.png'))},'fixtureBrowserReceipt':json.loads((ROOT/'dist/coupled-review/browser-receipt.json').read_text()),'limits':['Native Chromium default rendering. No GPU flags.','Axis views pose bones only; atlas muscles stay at bind.','Fixture loaded/released images are the separate authored P2 engineering fixture, not the actual anatomical arm.','Patch selection and remeshing remain pending anatomical review.'],'attribution':'Atlas images: BodyParts3D, © The Database Center for Life Science; current CC BY 4.0, original source notices retained. Original fixture images: Kenoma Apache-2.0.'}
(out/'source-identity.json').write_text(json.dumps(receipt,indent=2)+'\n');print(out)
