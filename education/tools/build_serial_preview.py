"""Build the actual Three.js serial-block controls without a full-book claim."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
from serial_lab import block
ROOT=Path(__file__).resolve().parents[1]

def build(destination):
    out=Path(destination).resolve()
    if out.exists():raise FileExistsError('Choose a fresh preview directory')
    out.mkdir(parents=True);(out/'web').mkdir();(out/'assets').mkdir()
    modules=['serial-specimen.mjs','serial-lab.mjs','continuum-properties.mjs','scene-status.mjs']
    for name in modules:shutil.copy2(ROOT/'web'/name,out/'web'/name)
    for name in ['style.css','serial-lab.css']:shutil.copy2(ROOT/'web'/name,out/'assets'/name)
    subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web/serial-lab.mjs'),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={out/"assets/serial-app.js"}','--legal-comments=external'],check=True)
    document='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kenoma serial specimen preview</title><link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/serial-lab.css"></head><body><main style="max-width:820px;margin:1rem auto;padding:0 1rem"><h1>Force-driven serial specimen</h1><p>Production controls and model, with actual Three.js rendering. This standalone preview does not compile proof cards or qualify a full-book release.</p>'+block('assembly',True)+'</main><script type="module" src="assets/serial-app.js"></script></body></html>'
    (out/'index.html').write_text(document)
    (out/'THIRD_PARTY_NOTICES.txt').write_text('Kenoma original content: Apache-2.0. Three.js0.180.0, MIT:\n'+(ROOT/'node_modules/three/LICENSE').read_text())
    inputs=['web/'+name for name in modules]+['web/style.css','web/serial-lab.css','tools/serial_lab.py','tools/build_serial_preview.py']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    record={'schema':1,'scope':'Actual production serial specimen controls and Three.js renderer; no compiled-proof or full-book qualification','source_base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'input_sha256':{n:digest(ROOT/n) for n in inputs},'output_sha256':{str(p.relative_to(out)):digest(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out/'serial-preview-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('Built serial specimen preview at '+str(out))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path);build(parser.parse_args().out)
