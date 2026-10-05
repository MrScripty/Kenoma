"""Bounded UI preflight. No proof badge or checked formal claim is emitted."""
from pathlib import Path
import hashlib,json,shutil,subprocess
from compression_lab import block
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'dist/compression-preview';out.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'web',out/'web',dirs_exist_ok=True)
subprocess.run(['node','tools/compression-experiment.mjs',str(out/'assets'),str(out/'compression-experiment.json')],cwd=ROOT,check=True)
(out/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lab 5 compression preflight</title><link rel="stylesheet" href="web/style.css"></head><body><main style="margin:auto;padding:1rem"><h1>Lab 5 compression preflight</h1><p>Interface preflight only. No checked proof claims or anatomical qualification.</p>'+block(True)+'</main><script type="module" src="web/compression-lab.mjs"></script></body></html>')
inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'web/compression.mjs',ROOT/'web/compression-lab.mjs',ROOT/'web/tissue.mjs',ROOT/'tools/compression_lab.py',Path(__file__)]}
(out/'compression-preview-manifest.json').write_text(json.dumps({'schema':1,'input_sha256':inputs,'scope':'Interface preflight only; no proof qualification'},indent=2)+'\n')
print('Built bounded compression preview without proof badges')
