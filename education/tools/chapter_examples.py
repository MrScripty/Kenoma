"""Bind every chapter to a shared-GUI example and package source-traceable adapters."""
from pathlib import Path
import hashlib, html, json, re, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
REGISTRY=ROOT/'book/examples/registry.json'

# Every non-executable resource consumed by the shared chapter GUI.
RUNTIME_SOURCES={
 'assets/chapter-examples.css':'education/web/chapter-examples.css',
 'gui/embedded/theme.css':'browser/embedded/theme.css',
 'gui/simple-graph/editor.css':'browser/simple-graph/editor.css',
 'data/elbow-v1/data/bodyparts3d_right_arm_m.json':'education/data/elbow-v1/data/bodyparts3d_right_arm_m.json',
 'data/anatomical-arm-v1/generated/arm-geometry.json':'education/data/anatomical-arm-v1/generated/arm-geometry.json',
 'data/anatomical-arm-v1/audit/arm-trajectory-results.json':'education/data/anatomical-arm-v1/audit/arm-trajectory-results.json',
 'data/anatomical-arm-v1/audit/coupling-results.json':'education/data/anatomical-arm-v1/audit/coupling-results.json',
}
def runtime_resources(out,repo=REPO):
    result={}
    for delivered,source in RUNTIME_SOURCES.items():
        value=hashlib.sha256((Path(out)/delivered).read_bytes()).hexdigest()
        if value!=hashlib.sha256((Path(repo)/source).read_bytes()).hexdigest():
            raise RuntimeError('GUI runtime copy differs from source: '+delivered)
        result[delivered]=value
    return result

def inventory():
    data=json.loads(REGISTRY.read_text())
    chapters=json.loads((ROOT/'book/book.json').read_text())['chapters']
    examples=data['examples']
    if data['version']!=1 or [e['chapter'] for e in examples]!=chapters:
        raise ValueError('Every canonical chapter requires one ordered example')
    if len({e['id'] for e in examples})!=len(examples):
        raise ValueError('Duplicate chapter example')
    for e in examples:
        if not re.fullmatch(r'[a-z0-9-]+',e['id']) or not all(e[k] for k in ['task','limits','evidenceClass','kind']):
            raise ValueError('Incomplete example scope')
        claims=re.findall(r'\{\{proof:([\w-]+)\}\}',(ROOT/'book/chapters'/e['chapter']).read_text())
        if claims!=e['claimIds']:raise ValueError('Stale related-claim mapping: '+e['id'])
    return examples

def block(ident,web):
    e=next(e for e in inventory() if e['id']==ident);escape=html.escape
    url='examples.html?chapter='+ident
    if not web:return f"\n\n### Interactive 3D: {e['title']}\n\n{e['task']} **Evidence class:** {e['evidenceClass']}. **Scope:** {e['limits']} [Open the shared Kenoma GUI]({url}).\n"
    return f'''\n<section class="chapter-example" id="example-{ident}" aria-labelledby="example-title-{ident}">
<h2 id="example-title-{ident}">Interactive 3D · {escape(e['title'])}</h2>
<p class="example-evidence">{escape(e['evidenceClass'])} · related checked claims have separate exact-domain scope</p>
<p>{escape(e['task'])}</p><p class="example-scope">{escape(e['limits'])}</p>
<button type="button" data-chapter-example="{ident}" aria-expanded="false" aria-controls="example-host-{ident}" hidden>Open 3D example</button>
<a href="{url}">Open standalone laboratory</a><div class="chapter-example-host" id="example-host-{ident}"></div>
</section>\n'''

def package(out):
    out=Path(out);examples=inventory();assets=out/'assets';assets.mkdir(parents=True,exist_ok=True)
    gui=out/'gui';gui.mkdir(exist_ok=True)
    # Source trees and the independently generated immutable WASM package only.
    for name in ['embedded','simple-graph']:
        source=REPO/'browser'/name;dest=gui/name
        if dest.exists():shutil.rmtree(dest)
        shutil.copytree(source,dest,ignore=shutil.ignore_patterns('node_modules','test-output','tests','.DS_Store'))
    wasm=gui/'simple-graph/pkg/human_wasm_bg.wasm'
    if not wasm.is_file():raise RuntimeError('Build browser/simple-graph/build.sh before packaging the book GUI')
    for source,target in [('chapter-examples.html','examples.html'),('chapter-examples.css','assets/chapter-examples.css'),('book-interaction.mjs','assets/book-interaction.js')]:
        shutil.copy(ROOT/'web'/source,out/target)
    for entry in ['chapter-examples','chapter-worker']:
        subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web'/f'{entry}.mjs'),'--bundle','--minify','--format=esm','--target=es2022','--alias:three='+str(REPO/'browser/simple-graph/vendor/three.module.js'),f'--outfile={assets/entry}.js','--legal-comments=external'],check=True)
    source_dir=out/'example-sources';source_dir.mkdir(exist_ok=True)
    for source,name in [(ROOT/'web/chapter-models.mjs','chapter-models.mjs'),(ROOT/'contributions/nonuniform-isochoric-kinematics/model.mjs','nonuniform-model.mjs'),(ROOT/'contributions/architecture-force/model.mjs','architecture-model.mjs')]:shutil.copy(source,source_dir/name)
    shutil.copy(REGISTRY,out/'chapter-examples.json')
    input_paths=list((REPO/'browser').rglob('*'))+list((REPO/'crates').rglob('*'))+[REPO/'Cargo.toml',REPO/'Cargo.lock']
    inputs={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(input_paths) if p.is_file() and not any(x in p.parts for x in ['node_modules','tests','test-output','__pycache__'])}
    receipt={'version':1,'chapters':len(examples),'example_ids':[e['id'] for e in examples],'registry_sha256':hashlib.sha256(REGISTRY.read_bytes()).hexdigest(),'gui_inputs':inputs,'wasm_sha256':hashlib.sha256(wasm.read_bytes()).hexdigest(),'runtime_resources':runtime_resources(out),'qualification':'Source packaging only; does not establish Lean, browser, physics or clinical qualification.'}
    (out/'chapter-example-build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
