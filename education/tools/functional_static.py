"""Reconstruct historical presentation from fixed sources and stored results.

This module runs only static formatters, Pandoc and esbuild. It never invokes a
book builder, experiment, proof checker, browser or scientific solver. The
caller owns production startup gating and subsequent browser qualification.
"""
from pathlib import Path
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PUBLISHED = '596df78f5cb652b4ac70917a82d8aa908b617056'
TREE = '8fb39d42575dc5593869315e46e80a64e828d7e3'
REPO = Path(__file__).resolve().parents[2]
ARCHIVE = 'education/review/projection-responsive-successor/qualification/'
PROOF_RECEIPTS = ['proof-status.json', 'transfer-proof-status.json',
    'coupled-proof-status.json', 'arm-proof-status.json', 'property-proof-status.json',
    'material-proof-status.json', 'material-real-proof-status.json',
    'mechanics-real-proof-status.json', 'actuator-real-proof-status.json',
    'dissipative-real-proof-status.json', 'serial-real-proof-status.json',
    'mixed-volume-proof-status.json']
BUNDLES = [('web/app.mjs', 'assets/app.js', 'external'),
    ('tools/anatomy-inspector.mjs', 'anatomy-inspection/inspect.js', 'eof'),
    ('tools/coupled-inspector.mjs', 'coupled-fixture/inspect.js', 'eof'),
    ('web/anatomical-coupled-worker.mjs', 'coupled-fixture/worker.js', 'eof'),
    ('tools/anatomical-arm-inspector.mjs', 'anatomical-arm/inspect.js', 'eof'),
    ('web/anatomical-arm-worker.mjs', 'anatomical-arm/worker.js', 'eof')]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _outside(path):
    path = Path(path).resolve()
    # The managed workspace has a read-only .git directory which is not a Git
    # repository. Recognize real repositories/worktrees instead of that marker.
    def checkout(parent):
        marker=parent/'.git'
        return marker.is_file() or (marker.is_dir() and (marker/'HEAD').is_file())
    if path.is_relative_to(REPO) or any(checkout(parent) for parent in [path,*path.parents]):
        raise ValueError('Presentation outputs must be outside the Git checkout')
    return path


def _run(argv, cwd, **kwargs):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, **kwargs)
    if result.returncode:
        raise RuntimeError('Static command failed: '+json.dumps(argv)+'\n'+result.stderr)
    return result


def _proof_cards(out, read):
    cards = {}
    historical_hashes = json.loads(read(ARCHIVE+'portable-bundle.json'))['file_sha256']
    for filename in PROOF_RECEIPTS:
        receipt_raw = (out/filename).read_bytes()
        if sha(receipt_raw) != historical_hashes[filename]:
            raise ValueError('Historical proof receipt changed: '+filename)
        receipt = json.loads(receipt_raw)
        source = read('education/'+receipt['source']).decode()
        if sha(source.encode()) != receipt['source_sha256']:
            raise ValueError('Historical proof source differs: '+filename)
        for claim in receipt['claims']:
            key = claim['id']
            if key in cards or claim['status'] != 'checked':
                raise ValueError('Ambiguous historical proof card: '+key)
            name = claim['theorem'].split('.')[-1]
            match = re.search(r'^theorem '+re.escape(name)+
                r'\b(?:(?!^\s*(?:theorem|def|lemma)\b).)*?\s:=', source, re.S|re.M)
            if not match:
                raise ValueError('Historical theorem statement unavailable: '+name)
            statement = match.group().rsplit(':=', 1)[0].rstrip()
            e = lambda value: html.escape(str(value)).replace('*', '&#42;').replace('^', '&#94;')
            implementation = claim.get('implementation', 'See the adjacent derivation and historical claim map.')
            implementation_path = re.match(r'(web/[^: ]+)', implementation)
            implementation_html = ('<a href="'+html.escape(implementation_path[1], quote=True)+'">'+e(implementation)+'</a>'
                if implementation_path else e(implementation))
            cards[key] = '\n<aside class="proof-card" id="proof-'+key+'" aria-label="Historical checked mathematical claim">'+\
                '<h3>Historical checked claim · '+e(key)+'</h3><p>'+e(claim['claim'])+'</p>'+\
                '<p><strong>Evidence date:</strong> fixed published source '+PUBLISHED+'. No fresh compilation in this reconstruction.</p>'+\
                '<p><strong>Assumptions:</strong> '+e(claim['assumptions'])+'</p><pre><code>'+e(statement)+'</code></pre>'+\
                '<p><strong>Limits:</strong> '+e(claim['limitations'])+'</p><p>Declaration '+e(claim['theorem'])+\
                '. Historical transitive axioms: '+e(', '.join(claim['axioms']) or 'none')+\
                '. Source SHA-256: '+e(receipt['source_sha256'])+'.</p>'+\
                '<p><strong>Implementation:</strong> '+implementation_html+'</p><p><a href="'+receipt['source']+\
                '">Historical source</a> · <a href="'+filename+'">Historical kernel receipt</a></p></aside>\n'
    if len(cards) != 103:
        raise ValueError('Expected exactly 103 historical proof cards')
    return cards


def _root_markdown(source, out, read, blocks):
    original_raw = (out/'kenoma-mechanics.md').read_bytes()
    original = original_raw.decode()
    expected = json.loads(read(ARCHIVE+'portable-bundle.json'))['file_sha256']['kenoma-mechanics.md']
    if sha(original_raw) != expected:
        raise ValueError('Expanded historical Markdown changed')
    cards = _proof_cards(out, read)
    composition = json.loads(read(ARCHIVE+'composition.json'))
    names = composition['curriculum_unchanged']
    if len(names) != 25:
        raise ValueError('Expected 25 historical chapters')
    replacement_spans = []
    proof_ids = []
    for name in names:
        raw = read('education/book/chapters/'+name).decode().strip()
        parts = re.split(r'\{\{([^}]+)\}\}', raw)
        pattern = ''.join(re.escape(part) if i%2 == 0 else '(.*?)' for i,part in enumerate(parts))
        matches = list(re.finditer(pattern, original, re.S))
        if len(matches) != 1:
            raise ValueError('Historical chapter expansion is ambiguous: '+name)
        match = matches[0]
        captured = dict(zip(parts[1::2], match.groups()))
        def replace(directive):
            key = directive[1]
            if key.startswith('proof:'):
                proof_id = key.split(':', 1)[1];proof_ids.append(proof_id)
                return cards[proof_id]
            if key in blocks:
                return blocks[key]
            return captured[key]
        replacement_spans.append((match.start(), match.end(), re.sub(r'\{\{([^}]+)\}\}', replace, raw)))
    if len(proof_ids) != 103 or set(proof_ids) != set(cards):
        raise ValueError('Historical proof anchors are incomplete')
    reconstructed = original
    for start,end,text in sorted(replacement_spans, reverse=True):
        reconstructed = reconstructed[:start]+text+reconstructed[end:]
    if reconstructed.count('# Checked source appendix:') != 12:
        raise ValueError('Historical source appendices incomplete')
    reconstructed = reconstructed.replace('Fresh successful invocation:', 'Historical successful invocation:')
    reconstructed = reconstructed.replace('This worker verified', 'The audit verified')
    notice = ('\n<div class="historical-scope" role="note"><strong>Historical research edition reconstructed from fixed source.</strong> '
        'The 25 chapters, twelve source appendices and 103 historical proof cards describe the published '+PUBLISHED+' evidence. '
        'Rendering and bundling do not establish fresh proof, solver, anatomical or biological qualification. '
        'The separate reading edition contains six additions with their own explicit source-only scope. '
        '<a href="reading-edition/index.html">Read the new complete reading edition</a> · '
        '<a href="static-regeneration-status.json">Reconstruction and external availability status</a>.</div>\n')
    front = re.match(r'\A---\n[\s\S]*?\n---\n', reconstructed)
    position = front.end() if front else 0
    reconstructed = reconstructed[:position]+notice+reconstructed[position:]
    return reconstructed


# This child imports the fixed pure HTML helpers and static renderers only. No
# helper build(), experiment, check(), solver, browser or contribution builder.
_PRESENTATION_CHILD = r'''
import importlib.util,json,sys
from pathlib import Path
education=Path(sys.argv[1]);output=Path(sys.argv[2]);sys.path.insert(0,str(education/'tools'))
spec=importlib.util.spec_from_file_location('fixed_historical_presentation',education/'tools/build.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from property_labs import block as property_block
from dissipative_lab import block as dissipative_block
from serial_lab import block as serial_block
from figures import generate
from evidence_figures import generate as evidence
from spatial_figures import generate as spatial
from coupled_figures import generate as coupled
from projection_figure import generate as projection
output.mkdir(exist_ok=True);generate(output);evidence(output);projection(output);coupled(output)
stored=json.loads((education/'review/serial-specimen/spatial-experiment.json').read_text())
spatial(output,stored)
blocks={'demo:'+key:module.lab_block(key,True) for key in module.LABS}
chapters=(education/'book').rglob('*.md')
import re
for path in chapters:
 for group,key in re.findall(r'\{\{(property|dissipative|serial):([^}]+)\}\}',path.read_text()):
  fn={'property':property_block,'dissipative':dissipative_block,'serial':serial_block}[group]
  blocks[group+':'+key]=fn(key,True)
blocks['evidence']=(education/'web/evidence.html').read_text()
print(json.dumps(blocks))
'''


_STORED_SVGS = r'''
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [education,out]=process.argv.slice(1),read=p=>JSON.parse(fs.readFileSync(education+'/'+p,'utf8'));
const {materialSvg}=await import(pathToFileURL(education+'/web/material-lab.mjs'));
const material=read('review/serial-specimen/material-experiment.json');
for(const [name,file] of [['default','property-material.svg'],['highBulk','material-highBulk.svg'],['zeroBulk','material-zeroBulk.svg'],['weakBulk','material-weakBulk.svg'],['coarse','material-coarse.svg']])fs.writeFileSync(out+'/'+file,materialSvg(material.cases[name]));
const creep=read('review/serial-readable/dissipative-experiment.json').cases.creep,p=creep.parameters;
const rows=[0,1,3,4,7].map(t=>{const row=creep.frames.find(r=>Math.abs(r.time-t)<1e-10);if(!row)throw Error('Missing historical SLS frame');return row});
const body=rows.map((r,i)=>{const x=90,y=50+i*76,end=x+p.length*1600+r.extensionM*1600*10;return `<g><text x="10" y="${y+4}" font-size="16">${r.time.toFixed(0)} s</text><line x1="${x}" y1="${y}" x2="${x+p.length*1600}" y2="${y}" stroke="#abbac3" stroke-dasharray="5 4" stroke-width="26"/><line x1="${x}" y1="${y}" x2="${end}" y2="${y}" stroke="#267f91" stroke-width="14"/><text x="460" y="${y-7}" font-size="16">N=${r.force.toFixed(3)} N; δ=${(r.extensionM*1000).toFixed(3)} mm</text><text x="460" y="${y+14}" font-size="16">U=${(r.storageJ*1000).toFixed(4)}; D=${(r.dissipationJ*1000).toFixed(4)} mJ</text></g>`;}).join('');
fs.writeFileSync(out+'/property-dissipative.svg',`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 450" role="img" aria-label="Historical force-controlled SLS load hold unload and recovery"><rect width="760" height="450" fill="#f4f8fb"/><text x="16" y="20" font-size="16">Default force hold: axial displacement magnified 10×; fixed reference scale</text>${body}<text x="16" y="438" font-size="16">Dash: reference length. Schematic thickness. Recoverable U and cumulative viscous loss D.</text></svg>`);
const cases=read('review/serial-specimen/serial-experiment.json').cases;
const {BOX_FACES}=await import(pathToFileURL(education+'/web/continuum-properties.mjs'));
const project=(v,y)=>[70+3500*(v[0]+.35*v[2]),y-3500*(v[1]+.25*v[2])];
const polygon=(vertices,face,y)=>face.map(i=>project(vertices[i],y).join(',')).join(' ');
const serialRows=['tension','rest','compression'].map((name,i)=>{
 const state=cases[name],y=110+i*160,color=name==='compression'?'#bd4b44':'#1675ae';
 const cells=state.cells.map(c=>BOX_FACES.map(face=>`<polygon points="${polygon(c.currentVertices,face,y)}" fill="${color}" fill-opacity=".12" stroke="${color}" stroke-width="1.5"/>`).join('')+BOX_FACES.map(face=>`<polygon points="${polygon(c.referenceVertices,face,y)}" fill="none" stroke="#76899a" stroke-dasharray="4 3"/>`).join('')).join('');
 const a=state.cells[0].currentVertices[1][0],b=state.cells[1].currentVertices[0][0];
 return `<g><text x="35" y="${y-60}" font-size="20">${name}: N=${state.parameters.force.toFixed(3)} N</text>${cells}<path d="M${70+3500*a} ${y}H${70+3500*b}" stroke="#967027" stroke-width="6"/><text x="410" y="${y-30}" font-size="18">Block 1: λ=${state.cells[0].stretch.toFixed(6)}</text><text x="410" y="${y}" font-size="18">Block 2: λ=${state.cells[1].stretch.toFixed(6)}</text><text x="410" y="${y+30}" font-size="18">Local volume ratios: ${state.cells.map(c=>c.volumeRatio.toFixed(6)).join(', ')}</text></g>`;
}).join('');
fs.writeFileSync(out+'/property-serial.svg',`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 570" role="img" aria-label="Historical solved two-block assembly in tension, rest and compression; same physical scale"><rect width="800" height="570" fill="#f4f7fb"/><text x="35" y="25" font-size="20">Two separate blocks; same force, different local stretches</text>${serialRows}<path d="M70 525H140" stroke="#23364b" stroke-width="3"/><text x="160" y="533" font-size="18">0.02 m reference scale; geometry ×1</text><text x="35" y="561" font-size="18">Dashed: reference. Gold: fixed-length fixture spacer, excluded from volume.</text></svg>`);
'''


_CONTACT_PLOT = r'''
import json,hashlib,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
education=Path(sys.argv[1]);out=Path(sys.argv[2]);base=education/'data/anatomical-arm-v1/audit'
raw=(base/'contact-lift-release-results.json').read_bytes();run=json.loads(raw);check=json.loads((base/'contact-lift-release-recheck.json').read_text())
if check['result']!='PASS' or check['executionReceiptSHA256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Historical plotting inputs do not match')
rows=check['rows'];time=[0]+[r['timeS'] for r in rows];angle=[run['held']['state']['qRad']]+[r['qRad'] for r in rows]
activation=[0]+[r['activation'] for r in rows];effort=[0]+[r['effort'] for r in run['attempts']];residual=[check['heldResidualN']]+[r['residualN'] for r in rows]
release=next(r['timeS']-a['hS'] for r,a in zip(rows,run['attempts']) if a['label']=='release')
plt.rcParams.update({'font.size':17,'legend.fontsize':15})
fig,axes=plt.subplots(2,2,figsize=(10,7),constrained_layout=True)
axes[0,0].plot(time,[q*180/3.141592653589793 for q in angle],marker='.');axes[0,0].set_ylabel('Elbow flexion (degrees)')
axes[0,1].plot(time,activation,label='Activation',marker='.');axes[0,1].step(time,effort,where='pre',label='Effort',linestyle='--');axes[0,1].set_ylabel('Authored\nactivation / effort');axes[0,1].legend()
axes[1,0].semilogy(time,residual,marker='.',label='Historical replayed residual');axes[1,0].axhline(run['parameters']['stationarityToleranceN'],linestyle='--',color='red',label='Historical force gate');axes[1,0].set_ylabel('Maximum free gradient (N)');axes[1,0].legend()
axes[1,1].plot([r['timeS'] for r in rows],[r['minimumJ'] for r in rows],marker='.');axes[1,1].set_ylabel('Minimum sampled body J')
for ax in axes.flat:ax.axvline(release,color='grey',linestyle=':');ax.set_xlabel('Recorded accepted time (s)');ax.grid(alpha=.2)
fig.suptitle('Historical reduced arm: 0.5 kg, effort 0.04, then release\nStored 596df78 result; no fresh anatomical qualification')
fig.savefig(out/'anatomical-contact-trajectory.png',dpi=180)
Image.open(out/'anatomical-contact-trajectory.png').convert('RGB').save(out/'anatomical-contact-trajectory.jpg',quality=85)
plt.close(fig)
'''


def regenerate(source_root, out, dependencies):
    """Render into a supplied outside-Git legacy payload, leaving retained bytes intact.

    source_root contains the complete fixed published export's education folder.
    dependencies is a node_modules path, or a mapping with node_modules and
    optional node, esbuild, pandoc paths. The caller must preserve the 711 reader
    separately and install the production startup gate before browser checks.
    """
    source = Path(source_root).resolve();education = source/'education';out = _outside(out)
    if not education.is_dir() or not out.is_dir():
        raise ValueError('Fixed source export and materialized legacy payload required')
    deps = dependencies if isinstance(dependencies, dict) else {'node_modules':str(dependencies)}
    modules = Path(deps['node_modules']).resolve()
    node = str(deps.get('node') or shutil.which('node'))
    pandoc = str(deps.get('pandoc') or shutil.which('pandoc'))
    esbuild = str(Path(deps.get('esbuild') or modules/'.bin/esbuild').resolve())
    for name,version in [('esbuild','0.25.10'),('three','0.180.0')]:
        if json.loads((modules/name/'package.json').read_text())['version'] != version:
            raise ValueError('Historical bundler dependency changed: '+name)
    bindings = {};changes = [];commands = [];dependency_inputs = {};retained_inputs = {};bundle_graphs = {}
    def read(relative):
        path=source/relative
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError('Unsafe fixed source path: '+relative)
        raw=path.read_bytes()
        fixed=subprocess.check_output(['git','show',PUBLISHED+':'+relative],cwd=REPO)
        if raw != fixed:
            raise ValueError('Export differs from pinned published source: '+relative)
        blob=subprocess.check_output(['git','rev-parse',PUBLISHED+':'+relative],cwd=REPO,text=True).strip()
        bindings[relative]={'commit':PUBLISHED,'git_blob':blob,'sha256':sha(raw),'bytes':len(raw)}
        return raw
    def publish(relative, raw, kind):
        path=out/relative;before=sha(path.read_bytes()) if path.is_file() else None
        if path.is_symlink() or not path.resolve().is_relative_to(out):raise ValueError('Unsafe output')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        changes.append({'path':relative,'before_sha256':before,'after_sha256':sha(raw),'kind':kind})
    if subprocess.check_output(['git','rev-parse',PUBLISHED+'^{tree}'],cwd=REPO,text=True).strip()!=TREE:
        raise ValueError('Published tree changed')
    # Bind all helper/model modules before any static import or bundler access.
    for folder,pattern in [('tools','*.py'),('web','*.mjs'),('contributions/continuum_reference','*.mjs')]:
        for path in (education/folder).glob(pattern):read(str(path.relative_to(source)))
    for relative in ['education/package-lock.json','education/web/evidence.html','education/web/template.html',
        'education/review/serial-specimen/spatial-experiment.json','education/review/serial-specimen/material-experiment.json',
        'education/review/serial-specimen/serial-experiment.json','education/review/serial-readable/dissipative-experiment.json',
        'education/data/elbow-v1/figures/bodyparts3d_right_arm.svg','education/data/elbow-v1/figures/openarm_recorded_trial.svg',
        'education/contributions/continuum_reference/data/example.json',
        'education/data/anatomical-arm-v1/audit/coupling-results.json',
        'education/data/anatomical-arm-v1/audit/contact-lift-release-results.json',
        'education/data/anatomical-arm-v1/audit/contact-lift-release-recheck.json']:read(relative)
    # A separate temp directory prevents legacy exact assets being overwritten by
    # general SVG functions which also produce already-retained figure names.
    work=Path(tempfile.mkdtemp(prefix='kenoma-static-presentation-',dir=out.parent));assets=work/'assets'
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['NODE_PATH']=str(modules);env['MPLCONFIGDIR']=str(work/'matplotlib-cache')
    command=[sys.executable,'-c',_PRESENTATION_CHILD,str(education),str(assets)]
    blocks=json.loads(_run(command,source,env=env).stdout);commands.append({'kind':'PURE_STATIC_SVG_AND_HTML','passed':True})
    _run([node,'--input-type=module','-e',_STORED_SVGS,str(education),str(assets)],source,env=env);commands.append({'kind':'STORED_RESULT_SVG_FORMATTERS','passed':True})
    _run([sys.executable,'-c',_CONTACT_PLOT,str(education),str(assets)],source,env=env);commands.append({'kind':'HISTORICAL_STORED_CONTACT_PLOT','passed':True})
    core_assets=['force.svg','torque.svg','energy.svg','elbow.svg','series.svg','figure-provenance.json',
        'atlas-print.svg','recording-print.svg','evidence-figure-provenance.json','spatial.svg','continuum.svg',
        'coupled-pulse.svg','pressure-projection.svg','property-material.svg','material-highBulk.svg',
        'material-zeroBulk.svg','material-weakBulk.svg','material-coarse.svg','property-dissipative.svg',
        'property-serial.svg','anatomical-contact-trajectory.png','anatomical-contact-trajectory.jpg']
    for name in core_assets:publish('assets/'+name,(assets/name).read_bytes(),'STATIC_DERIVATIVE_OF_FIXED_SOURCE_OR_STORED_RESULT')
    scope=('<p class="historical-scope"><strong>Historical research source reconstruction.</strong> '
        'These sources and receipts belong to published '+PUBLISHED+'. No fresh proof, anatomical or biological qualification. '
        '<a href="../reading-edition/index.html">New reading edition</a> · '
        '<a href="../static-regeneration-status.json">Reconstruction and external availability</a>.</p>')
    for folder,builder in [('anatomy-inspection','build-anatomy-inspector.mjs'),('coupled-fixture','build-coupled-inspector.mjs'),('anatomical-arm','build-anatomical-arm-inspector.mjs')]:
        code=read('education/tools/'+builder).decode()
        match=re.search(r'writeFile\(out\+\s*[\'\"]index\.html[\'\"]\s*,\s*`([\s\S]*?)`\)',code)
        if not match or '${' in match[1]:raise ValueError('Inspector template must be a literal: '+builder)
        page=match[1].replace('<header>','<header>'+scope,1)
        page=page.replace('Compiled Lean4 identities','Historical compiled Lean4 identities').replace('Checked Lean4 claims','Historical checked Lean4 claims').replace('Checked transfer identities','Historical checked transfer identities').replace('Loading the kernel receipt…','Loading the historical kernel receipt…')
        if folder=='anatomical-arm':page=page.replace('The resting state and a default 0.5 kg loaded step pass reduced force, full boundary and tendon-path gates.','Historical receipts report reduced resting/default-step checks; those checks are not renewed by this static reconstruction.')
        publish(folder+'/index.html',page.encode(),'HISTORICAL_TEMPLATE_WITH_DISPLAY_SCOPE_EDITS')
    for entry,target,legal in BUNDLES:
        read('education/'+entry)
        bundle=work/target;bundle.parent.mkdir(parents=True,exist_ok=True);meta=work/(target.replace('/','-')+'.metafile.json')
        _run([esbuild,str(education/entry),'--bundle','--minify','--format=esm','--target=es2022','--legal-comments='+legal,'--outfile='+str(bundle),'--metafile='+str(meta)],source,env=env)
        metadata=json.loads(meta.read_text())
        def graph_name(name):
            path=(source/name).resolve() if not Path(name).is_absolute() else Path(name).resolve()
            if path.is_relative_to(source):return str(path.relative_to(source))
            if path.is_relative_to(modules):return 'dependencies/'+str(path.relative_to(modules))
            if path.is_relative_to(work):return 'presentation/'+str(path.relative_to(work))
            if Path(name).is_absolute():raise ValueError('Unexpected absolute bundler graph path: '+name)
            return 'external:'+name
        def graph_item(item):
            result=dict(item)
            if 'entryPoint' in result:result['entryPoint']=graph_name(result['entryPoint'])
            if 'inputs' in result:result['inputs']={graph_name(k):v for k,v in result['inputs'].items()}
            if 'imports' in result:result['imports']=[dict(value,path=graph_name(value['path'])) for value in result['imports']]
            return result
        bundle_graphs[target]={section:{graph_name(k):graph_item(v) for k,v in metadata[section].items()} for section in ['inputs','outputs']}
        for name in metadata['inputs']:
            path=(source/name).resolve() if not Path(name).is_absolute() else Path(name).resolve()
            if path.is_relative_to(source):read(str(path.relative_to(source)))
            elif path.is_relative_to(modules):
                dependency_inputs[str(path.relative_to(modules))]={'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}
            else:raise ValueError('Unexpected bundler input outside fixed sources/dependencies: '+name)
        original_bundle=bundle.read_bytes()
        raw=original_bundle.decode()
        for before,after in [('Fresh kernel receipt','Historical kernel receipt'),('Full compiled Lean source','Historical compiled Lean source'),('Actual compiled source','Historical compiled source')]:raw=raw.replace(before,after)
        bundle_graphs[target]['presentation_derivative']={'bundler_output_sha256':sha(original_bundle),
            'bundler_output_bytes':len(original_bundle),'published_output_sha256':sha(raw.encode()),'published_output_bytes':len(raw.encode()),
            'changes':'Historical display labels only; esbuild inputs/outputs describe the bundle before these documented display edits'}
        publish(target,raw.encode(),'FIXED_SOURCE_BUNDLE_WITH_HISTORICAL_DISPLAY_LABELS')
        if legal=='external':publish(target+'.LEGAL.txt',Path(str(bundle)+'.LEGAL.txt').read_bytes(),'LEGACY_THIRD_PARTY_LICENSE_COMPATIBILITY_ASSET')
        commands.append({'kind':'ESBUILD_STATIC_BUNDLE','entry':'education/'+entry,'target':target,'passed':True})
    staging=work/'root-web-staging.md';staging.write_text(_root_markdown(source,out,read,blocks))
    rendered=work/'index.html'
    result=_run([pandoc,str(staging),'--standalone','--mathml','--toc','--toc-depth=2','--template',str(education/'web/template.html'),'-o',str(rendered)],source,env=env)
    if 'Could not convert TeX math' in result.stderr:raise ValueError(result.stderr)
    page=rendered.read_text().replace('</head>','<link rel="stylesheet" href="assets/dissipative-lab.css">\n<link rel="stylesheet" href="assets/serial-lab.css">\n</head>')
    page=re.sub(r'<mrow>(<mo[^>]*>\[</mo>)(<mtable>.*?</mtable>)(<mo[^>]*>\]</mo>)</mrow>',r'<mrow class="matrix-fenced">\1\2\3</mrow>',page,flags=re.S)
    def inline_math(match):
        formula=match[0]
        if '<annotation encoding="application/x-tex">M(u-y)=G^T\\ell</annotation>' not in formula:return formula
        return '<span class="print-safe-inline">'+formula+'<span class="print-inline-equation" role="math" aria-label="M times u minus y equals G transpose times ell"><i>M</i>(<i>u</i>−<i>y</i>) = <i>G</i><sup><i>T</i></sup>ℓ</span></span>'
    page=re.sub(r'<math display="inline".*?</math>',inline_math,page,flags=re.S)
    page=re.sub(r'<math display="block".*?</math>',lambda m:'<div class="equation" tabindex="0" aria-label="Scrollable displayed equation">'+m[0]+'</div>',page,flags=re.S)
    publish('index.html',page.encode(),'25_CHAPTER_12_APPENDIX_HISTORICAL_ROOT_WITH_103_CONTEXTUALIZED_CARDS')
    status={'kind':'STATIC_HISTORICAL_PRESENTATION_RECONSTRUCTION','published_commit':PUBLISHED,'published_tree':TREE,
        'original_chapters':25,'historical_source_appendices':12,'historical_proof_cards':103,
        'new_proof_compilation':'UNRUN','anatomical_execution':'UNRUN_IN_REGENERATION','historical_status':'Historical checked labels identify fixed published receipts only',
        'current_anatomical_status':'No newly bound anatomical outcome included','external_network_reachability':'UNRUN',
        'browser_qualification':'UNRUN','production_startup_gate':'CALLER_MUST_INSTALL_BEFORE_BROWSER_CHECKS_OR_PUBLICATION',
        'protected_retained_data_policy':'Existing971 canonical data/source/receipt bytes are not rewritten; only regenerated presentation paths are authored'}
    publish('static-regeneration-status.json',(json.dumps(status,indent=2)+'\n').encode(),'PUBLIC_RECONSTRUCTION_STATUS')
    for name in ['kenoma-mechanics.md']+PROOF_RECEIPTS:retained_inputs[name]=sha((out/name).read_bytes())
    receipt={'kind':'FIXED_SOURCE_STATIC_REGENERATION','published_commit':PUBLISHED,'published_tree':TREE,
        'renderer_source_sha256':sha(Path(__file__).read_bytes()),
        'sources':bindings,'changes':changes,'commands':commands,'outputs':{r['path']:r['after_sha256'] for r in changes},
        'retained_inputs':retained_inputs,'bundled_dependency_inputs':dependency_inputs,'bundle_graphs':bundle_graphs,
        'chapters':25,'appendices':12,'proof_cards':103,'proof_compilation':'UNRUN','scientific_experiments_executed':False,
        'anatomical_execution':'UNRUN','browser_execution':'UNRUN','publication':'NOT_EXECUTED',
        'presentation_label_edits':['Root historical scope and proof-card labels','Historical successful invocation and audit wording in rendered root only','Inspector historical scope, proof headings and reduced-rest wording','Inspector bundle display strings only','Contact plot identifies stored historical results'],
        'compatibility_exceptions':['Scientific historical contact plot retained at known PNG URL; new JPEG derivative is quality85','Existing .LEGAL.txt URL carries actual esbuild third-party license notices, not a TXT document deliverable'],
        'bundler_dependencies':{'three':'0.180.0','esbuild':'0.25.10','node':_run([node,'--version'],source).stdout.strip(),'esbuild_executable_sha256':sha(Path(esbuild).read_bytes())},
        'reproducibility':'New derivatives are source-bound and must be freshly qualified; no historical byte-identity claim for regenerated presentation'}
    (work/'static-regeneration-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
