"""Build a standalone production-control preview; no proof/release claim."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
from dissipative_lab import block
ROOT=Path(__file__).resolve().parents[1]

def build(destination):
    out=Path(destination).resolve()
    if out.exists():raise FileExistsError('Choose a fresh output directory')
    out.mkdir(parents=True);(out/'web').mkdir();(out/'assets').mkdir()
    for name in ['dissipative-bar.mjs','dissipative-lab.mjs']:shutil.copy2(ROOT/'web'/name,out/'web'/name)
    for name in ['style.css','dissipative-lab.css']:shutil.copy2(ROOT/'web'/name,out/'assets'/name)
    text='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kenoma axial dissipative protocol preview</title><link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/dissipative-lab.css"></head><body><main style="max-width:820px;margin:1rem auto;padding:0 1rem"><h1>Axial dissipative protocol</h1><p>Standalone production controls and model. This preview does not compile proof cards or qualify a full-book release.</p>'+block('sls',True)+'</main><script type="module" src="web/dissipative-lab.mjs"></script></body></html>'
    (out/'index.html').write_text(text)
    inputs=['web/dissipative-bar.mjs','web/dissipative-lab.mjs','web/dissipative-lab.css','web/style.css','tools/dissipative_lab.py','tools/build_dissipative_preview.py']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    record={'schema':1,'scope':'Actual production dissipative control/model preview; no compiled proof or full-book qualification','source_base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'input_sha256':{name:digest(ROOT/name) for name in inputs},'output_sha256':{str(p.relative_to(out)):digest(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out/'dissipative-preview-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(f'Built dissipative controls at {out}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('out',type=Path);build(parser.parse_args().out)
