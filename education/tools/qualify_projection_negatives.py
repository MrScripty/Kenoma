"""Actual corrupted browser models and damaged copies; preserve checked bytes."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import argparse, importlib.util, json, os, shutil, tempfile
from playwright.sync_api import sync_playwright
from check_projection_artifact import check, digest, ROOT


def runtime(output):
    source = ROOT/'standalone/pressure-projection-lab.html'
    before = digest(source)
    spec = importlib.util.spec_from_file_location('projection_oracle', ROOT/'standalone/pressure-projection-lab-check.py')
    oracle = importlib.util.module_from_spec(spec); spec.loader.exec_module(oracle)
    mutations = {
        'unweighted-group-mean': ('group.reduce((sum,i)=>sum+weights[i]*g[i],0)/group.reduce((sum,i)=>sum+weights[i],0)', 'group.reduce((sum,i)=>sum+g[i],0)/group.length'),
        'wrong-residual-vector': ('g.map((x,i)=>x-projected[i])', 'g.map((x,i)=>x+projected[i])'),
    }
    rows = []
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as directory:
        folder = Path(directory)
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self,*args): pass
        server = ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(folder)))
        Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
                for name, (old,new) in mutations.items():
                    text = source.read_text(); assert text.count(old)==1
                    mutated = output/(name+'.html'); mutated.write_text(text.replace(old,new))
                    shutil.copy(mutated,folder/'lab.html')
                    page = browser.new_page()
                    page.goto(f'http://127.0.0.1:{server.server_port}/lab.html',wait_until='networkidle')
                    # Use the displayed executable through an actual radio control.
                    page.locator('input[name=space][value="2"]').check()
                    actual = page.evaluate('PressureProjectionLab.state()')
                    try: oracle.check_state(actual,oracle.oracle([-.75,.25,-.25,.75],8,2))
                    except AssertionError as error:
                        rows.append({'case':name,'detected':True,'reason':str(error),'mutated_html_sha256':digest(mutated),'actual_state':actual})
                    else: raise RuntimeError('Corrupted browser model passed: '+name)
                    page.close()
                browser.close()
        finally: server.shutdown(); server.server_close()
    assert digest(source)==before
    (output/'runtime-negative.json').write_text(json.dumps({'result':'PASS_TWO_CORRUPTED_PROJECTION_BROWSER_MODELS','original_unchanged':True,'cases':rows},indent=2)+'\n')
    print('PASS two corrupted projection browser models')


def artifacts(site, output):
    site = Path(site).resolve(); check(site)
    before = {str(p.relative_to(site)):digest(p) for p in site.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    rows = []
    for name in ['missing-receipt','stale-manifest','missing-proof','forged-kernel-source','rehashed-wrong-lab','changed-review-pdf','forged-static-vector']:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as directory:
            copy = Path(directory)/'dist'; shutil.copytree(site,copy)
            if name=='missing-receipt': (copy/'projection-qa/integration.json').unlink()
            elif name=='stale-manifest':
                path=copy/'projection-qa/integration.json';r=json.loads(path.read_text());r['manifest_sha256']='0'*64;path.write_text(json.dumps(r))
            elif name in ['missing-proof','forged-kernel-source']:
                path=copy/('mixed-volume-proof-status.json' if name=='missing-proof' else 'mixed-volume-kernel/receipt.json');r=json.loads(path.read_text())
                if name=='missing-proof':r['claims'].pop()
                else:r['source_sha256']='0'*64
                path.write_text(json.dumps(r))
            elif name=='rehashed-wrong-lab':
                path=copy/'standalone/pressure-projection-lab.html';path.write_text(path.read_text().replace('weights = Object.freeze([1,3,2,2])','weights = Object.freeze([1,1,1,1])'))
                path=copy/'projection-qa/receipt.json';r=json.loads(path.read_text());r['source_sha256']['standalone/pressure-projection-lab.html']=digest(copy/'standalone/pressure-projection-lab.html');path.write_text(json.dumps(r))
                path=copy/'projection-qa/integration.json';r=json.loads(path.read_text());r['lab_sha256']=digest(copy/'standalone/pressure-projection-lab.html');r['standalone_receipt_sha256']=digest(copy/'projection-qa/receipt.json');path.write_text(json.dumps(r))
            elif name=='changed-review-pdf':
                path=copy/'projection-qa/fixed-field-reference.pdf';path.write_bytes(path.read_bytes()+b'changed')
            else:
                path=copy/'assets/pressure-projection.svg';path.write_text(path.read_text().replace('y="223.75"','y="160"'))
            try: check(copy)
            except (AssertionError,FileNotFoundError) as error: rows.append({'case':name,'detected':True,'reason':str(error) or 'Required source/proof coverage rejected'})
            else: raise RuntimeError('Damaged projection artifact passed: '+name)
    assert before == {name:digest(site/name) for name in before}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'result':'PASS_SEVEN_DAMAGED_PROJECTION_ARTIFACTS','original_unchanged':True,'manifest_sha256':digest(site/'build-manifest.json'),'cases':rows},indent=2)+'\n')
    print('PASS seven damaged projection artifacts')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',type=Path)
    parser.add_argument('--site',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.runtime: runtime(args.runtime)
    if args.site: artifacts(args.site,args.output)
