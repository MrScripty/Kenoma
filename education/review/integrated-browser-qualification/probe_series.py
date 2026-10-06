"""Record the exact failing legacy whole-book fixture without changing its checks."""
from pathlib import Path
import json, shutil, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools')]
from render_pdf import serve
from playwright.sync_api import sync_playwright
server,url=serve()
out=ROOT/'review/integrated-browser-qualification'
try:
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'))
    page=browser.new_page(viewport={'width':1280,'height':900})
    page.goto(url+'/index.html',wait_until='networkidle')
    lab=page.locator('#lab-series')
    lab.locator('[data-action=start]').click()
    lab.locator('select[data-param=mode]').select_option('prescribed')
    lab.locator('input[type=number][data-param=angle]').fill('90')
    lab.evaluate('(lab)=>{for(let i=0;i<60;i++)lab.querySelector("[data-action=step]").click()}')
    lab.locator('[data-action=copy]').click()
    result={'held':json.loads(lab.locator('.preset').input_value()),'heldReadout':lab.locator('.readout').inner_text()}
    lab.screenshot(path=str(out/'series-held-current.png'))
    lab.locator('[data-action=release]').click()
    lab.locator('input[type=number][data-param=excitation]').fill('0.8')
    lab.locator('[data-action=release]').click()
    lab.locator('[data-action=step]').click()
    with page.expect_download() as info:lab.locator('[data-action=export]').click()
    info.value.save_as(str(out/'series-released-current.json'))
    for key,value in [('contact','off'),('contact','on'),('bulk','0'),('tendon','rigid')]:
      lab.locator(f'select[data-param={key}]').select_option(value)
      lab.locator('[data-action=copy]').click()
      result[f'{key}-{value}']={'preset':json.loads(lab.locator('.preset').input_value()),'readout':lab.locator('.readout').inner_text()}
    browser.close()
  (out/'series-current-fixture.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({key: value if key.endswith('Readout') else value.get('state', value.get('readout')) for key,value in result.items()},indent=2))
finally:
  server.shutdown();server.server_close()
