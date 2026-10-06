"""Read-only Chromium experiment: ordinary beforeprint fires before print CSS.
Synthetic wide MathML uses the exact current Kenoma CSS and print helper.
This does not qualify native printing of the complete shared book.
"""
from pathlib import Path
import shutil,json,hashlib,subprocess
import fitz
from playwright.sync_api import sync_playwright
root=Path('/workspace/kenoma-pr8-print-readability/education')
css=(root/'web/style.css').read_text(); helper=(root/'tools/print_layout.js').read_text()
expr='<mi>W</mi><mo>=</mo>'+'<mo>+</mo>'.join('<mfrac><msup><mi>x</mi><mn>2</mn></msup><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow></mfrac>' for _ in range(35))
result={'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'css_sha256':hashlib.sha256(css.encode()).hexdigest(),'helper_sha256':hashlib.sha256(helper.encode()).hexdigest(),'scope':'synthetic ordinary screen-media beforeprint hook experiment, not complete native book qualification','cases':[]}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'));result['browser_version']=b.version
 for width in [1280,658,390]:
  page=b.new_page(viewport={'width':width,'height':1000})
  page.set_content('<style>'+css+'</style><div class="layout"><main><p>Readable print text keeps its physical point size.</p><div class="equation"><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow>'+expr+'</mrow><annotation>original</annotation></semantics></math></div></main></div>')
  original=page.locator('.equation > math').evaluate('(node)=>node.outerHTML')
  page.evaluate('''(helper)=> {const run=eval('('+helper+')'); window.events=[]; window.addEventListener('beforeprint',()=>{window.events.push({event:'beforeprint',printMedia:matchMedia('print').matches,equationWidth:document.querySelector('.equation').clientWidth}); try{window.result=run()}catch(e){window.error=String(e)}});window.addEventListener('afterprint',()=>window.events.push({event:'afterprint',printMedia:matchMedia('print').matches}));}''',helper)
  path=Path(f'/tmp/pr8-native-beforeprint-{width}.pdf'); pdf=page.pdf(path=str(path),format='A4',prefer_css_page_size=True)
  with fitz.open(stream=pdf,filetype='pdf') as doc:
   sizes=[s['size'] for pg in doc for bl in pg.get_text('dict')['blocks'] for ln in bl.get('lines',[]) for s in ln['spans'] if 'Readable print text' in s['text']]
   if width==1280:doc[0].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save('/tmp/pr8-native-beforeprint-1280.png')
  result['cases'].append({'screenViewport':width,'events':page.evaluate('window.events'),'result':page.evaluate('window.result || null'),'error':page.evaluate('window.error || null'),'proseSizes':sizes,'originalPreserved':original==page.locator('.equation > math').evaluate('(node)=>node.outerHTML'),'screenOriginalVisible':page.locator('.equation > math').is_visible(),'screenAlternateHidden':not page.locator('.print-equation-rows').is_visible(),'pdf':str(path),'pdf_sha256':hashlib.sha256(pdf).hexdigest()});page.close()
 b.close()
print(json.dumps(result,indent=2))
