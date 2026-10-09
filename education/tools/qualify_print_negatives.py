"""Actual full-book 9pt corruption plus missing/forged print receipts."""
from pathlib import Path
import ast,copy,hashlib,json,shutil,sys
import fitz
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.tools/integration-print-negative-fixtures'
sys.path.insert(0,str(ROOT/'tools'))
import render_pdf
from check_print_readability import qualify,check
from package_education_bundle import validate_build
from check_real_lesson_proofs import FAMILIES
OUT.mkdir(exist_ok=True)
fixture=OUT/'dist'
shutil.copytree(ROOT/'dist',fixture,dirs_exist_ok=True)
manifest=json.loads((fixture/'build-manifest.json').read_text())
receipt=fixture/'print-readability-check.json';original=receipt.read_bytes()
results=[]
for label,mutation in [('missing readability receipt',lambda:receipt.unlink()),('forged actual PDF binding',lambda:receipt.write_text(json.dumps(dict(json.loads(original),pdf_sha256='0'*64))))]:
    mutation()
    try:
        validate_build(fixture,manifest)
        raise RuntimeError('FALSE_PASS '+label)
    except (AssertionError,FileNotFoundError) as error:
        results.append({'case':label,'result':'REJECTED_PACKAGE','reason':str(error)})
    finally:receipt.write_bytes(original)

tree=ast.parse((ROOT/'tools/render_pdf.py').read_text())
mapping=next(n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='evaluate' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and n.args[0].value.startswith('({revision,realDestinations,architectureImplementationDestinations})'))
destinations={}
for source,_,prefix,_ in FAMILIES:
    destinations.update({'proofs/'+source:'#'+prefix+'-source-appendix',prefix+'-proof-status.json':'#'+prefix+'-proof-receipt',prefix+'-lean-check.txt':'#'+prefix+'-kernel-report'})
server,url=render_pdf.serve()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium')
        page=browser.new_page(viewport={'width':658,'height':1000})
        page.goto(url+'/index.html',wait_until='networkidle');page.emulate_media(media='print')
        page.locator('.proof-appendices').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=true)')
        page.evaluate('document.fonts.ready')
        page.add_style_tag(content='@media print {pre, pre code, pre code span {font-size:9pt!important}}')
        reflow=page.evaluate((ROOT/'tools/print_layout.js').read_text())
        page.evaluate(mapping,{'revision':manifest['git_revision'],'realDestinations':destinations,'architectureImplementationDestinations':render_pdf.pdf_implementation_links(ROOT)})
        path=fixture/'kenoma-mechanics.pdf'
        page.pdf(path=str(path),format='A4',print_background=True,prefer_css_page_size=True,tagged=True,outline=True)
        browser.close()
finally:server.shutdown();server.server_close()
pdf_sha=hashlib.sha256(path.read_bytes()).hexdigest()
with fitz.open(path) as doc:
    spans=[s for pg in doc for block in pg.get_text('dict')['blocks'] for line in block.get('lines',[]) for s in line['spans'] if 'theorem' in s['text']]
    assert spans and min(s['size'] for s in spans)==9
forged=json.loads(original);forged['pdf_sha256']=pdf_sha;receipt.write_text(json.dumps(forged))
try:
    check(fixture)
    raise RuntimeError('FALSE_PASS source-preserving undersized code PDF')
except AssertionError as error:
    assert '9.000000 pt below 10 pt' in str(error)
    results.append({'case':'source-preserving actual 9pt code PDF with rebound PDF hash','result':'REJECTED_PRINT_READABILITY','reason':str(error),'pdf_sha256':pdf_sha,'measured_theorem_minimum_pt':9,'print_layout':reflow})
(OUT/'results.json').write_text(json.dumps({'qualified_source':manifest['git_revision'],'positive_pdf_sha256':json.loads(original)['pdf_sha256'],'results':results},indent=2)+'\n')
print('PASS_NEGATIVE_CONTROLS',len(results))
