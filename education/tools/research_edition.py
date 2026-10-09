#!/usr/bin/env python3
"""Compose a full archival reader plus additive, source-only teaching research.

Only the three allowlisted synthetic model defaults run. No contribution
builder, Lean command, anatomical code, or broad book build is invoked.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess

from educational_supplement import BASE, TREE, PUBLISHED, outside, sha, git, identity, write_json

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'education'
RESEARCH='f9dbda932264cb0ce1023b0204efe6e4057ed983'
RESEARCH_TREE='bfbfc13369ddd41a7eb19f06ffcaa885ce0e0332'
ARCHIVE='education/review/projection-responsive-successor/qualification/artifacts/'
FIGURE_PAGES={'assets/force.svg':6,'assets/torque.svg':8,'assets/energy.svg':12,
 'assets/property-deformation.svg':17,'assets/property-isochoric.svg':20,'assets/property-tapered.svg':22,
 'assets/property-material.svg':26,'assets/property-dissipative.svg':35,'assets/property-serial.svg':45,
 'assets/atlas-print.svg':58,'assets/recording-print.svg':59,'assets/elbow.svg':65,
 'assets/series.svg':75,'assets/continuum.svg':104,'assets/pressure-projection.svg':106,
 'assets/spatial.svg':126,'assets/atlas-assembly-bind.png':133,'assets/coupled-pulse.svg':139,
 'assets/fixture-loaded.png':139,'assets/fixture-released.png':140,'assets/anatomical-arm-rest.png':148,
 'assets/anatomical-contact-trajectory.png':152,
 'data/anatomical-arm-v1/review/dense-qualification/force-components/nodal-force-components.svg':155,
 'data/anatomical-arm-v1/review/dense-qualification/coarse/dense-qualification.svg':157,
 'data/anatomical-arm-v1/review/dense-qualification/envelope/dense-envelope.svg':158}
LABS={'lateral-interface-transfer':'lateral-interface-transfer','directional-compression':'directional-compression-lab','full-face-load-pressure':'full-face-load-pressure'}

CSS='''body{margin:0;background:#fafaf5;color:#17383b;font:18px/1.65 Georgia,serif;overflow-wrap:anywhere}header{background:#123c40;color:#fff;padding:30px 24px}header a{color:#bce3dd}main{max-width:1000px;margin:auto;padding:28px 22px}nav{display:flex;flex-wrap:wrap;gap:14px}a{color:#096576;overflow-wrap:anywhere}h1,h2,h3{line-height:1.2}h1{margin-top:40px}table{display:block;overflow:auto;max-width:100%;border-collapse:collapse}td,th{padding:9px;border:1px solid #bfceca;text-align:left}pre{font:14px/1.5 monospace;white-space:pre-wrap;overflow-wrap:anywhere;padding:14px;background:#edf2ee}img,svg{max-width:100%;height:auto}figure img{width:100%}.archive-page{display:block;max-width:620px;margin:auto}.proof-card,.scope{border-left:4px solid #528780;padding:14px;margin:24px 0}.scope{background:#e5efeb}.equation{overflow:auto;max-width:100%}.print-equation-rows{display:none}figure{margin:24px 0}figcaption{font-size:16px}.controls{display:flex;flex-wrap:wrap;gap:18px}label{display:flex;flex-direction:column;gap:6px}input,select,button{font:inherit;max-width:100%;padding:8px}button{margin:14px 10px 14px 0}dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}dl div{padding:12px;background:#eef2ee}dd{margin:4px 0;font-weight:bold}textarea{max-width:100%}.badge{font:14px sans-serif;letter-spacing:.04em}.archive-notice{background:#fff0cf;padding:18px}@media print{body{font-size:11pt;background:white;line-height:1.5}main{max-width:none;padding:0}header{padding:0;background:white;color:#17383b}header nav,.controls,button,.screen-only{display:none}h1{break-before:page}h1:first-child{break-before:auto}h2,h3{break-after:avoid}pre{font-size:10pt;padding:8pt}.proof-card{break-inside:avoid}table{display:table;overflow:visible;font-size:10pt}figcaption,.badge{font-size:10pt}a{color:inherit;text-decoration:none}math{font-size:15pt}.equation{overflow:visible}.equation.print-reflowed>math{display:none}.print-equation-rows{display:block}.print-equation-rows math{margin:6pt 0}svg text{font-size:22px}p{orphans:3;widows:3}}'''

def markdown_html(text):
    body=subprocess.check_output(['pandoc','--from=markdown','--to=html','--mathml','--wrap=none'],input=text.encode()).decode()
    return re.sub(r'(<math display="block"[\s\S]*?</math>)',r'<div class="equation" tabindex="0" aria-label="Scrollable displayed equation">\1</div>',body)

def doc(title,body):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><link rel="stylesheet" href="edition.css"></head><body><header><p class="badge">KENOMA / ADDITIVE EDUCATIONAL RESEARCH · LOCAL CANDIDATE</p><nav><a href="index.html">Full reading guide</a><a href="book.html">Complete reader</a><a href="kenoma-research-edition.pdf">Complete PDF</a><a href="kenoma-research-edition.md">Markdown</a><a href="qualification.json">Qualification</a></nav></header><main>'+body+'</main></body></html>'

def own_source_url(path,ref=PUBLISHED):
    for n in ['education/'+path,ARCHIVE+path]:
        r=subprocess.run(['git','cat-file','-e',ref+':'+n],cwd=REPO,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if r.returncode:continue
        return 'https://github.com/MrScripty/Kenoma/blob/'+ref+'/'+n
    return None

def model_default(group):
    path=ROOT/'contributions'/group
    if group=='lateral-interface-transfer':program="import {labState} from './model.mjs';console.log(JSON.stringify(labState()));"
    else:
        function='specimen' if group=='directional-compression-lab' else 'solveComparison'
        program=f"import {{{function}}} from './model.mjs';import {{sceneMarkup}} from '../directional-compression-lab/view.mjs';const r={function}();console.log(JSON.stringify({{result:r,scene:sceneMarkup(r.state)}}));"
    return json.loads(subprocess.check_output(['node','--input-type=module','-e',program],cwd=path))

def proof_card(claim):
    return '<aside class="proof-card" id="'+claim['id']+'"><h3>'+html.escape(claim['title'])+'</h3><p><strong>Unregistered mathematical source · compilation and axiom report UNRUN.</strong></p><pre>'+html.escape(claim['statement_lean'])+'</pre><p>'+html.escape(claim['assumptions'])+'</p><p>'+html.escape(claim['limitations'])+'</p></aside>'

def lab_build(out,slug,group,defaults):
    lab=out/'labs'/slug;lab.mkdir(parents=True)
    if group=='lateral-interface-transfer':
        for n in ['model.mjs','ui.mjs','style.css','LateralInterfaceTransfer.lean','claims.json','sources.json','chapter.md','README.md']:shutil.copyfile(ROOT/'contributions'/group/n,lab/n)
        body=(ROOT/'contributions'/group/'index.html').read_text()
        body=body.replace('href="lateral-interface-transfer.pdf"','href="../../research-additions.pdf"').replace('href="lateral-transfer-proof-status.json"','href="formal-status.json"').replace('>Kernel receipt<','>Source-only formal status<')
        body=body.replace('<main>','<main><p><a href="../../book.html#lateral-interface-transfer">Return to the full book additions</a> · <strong>Source-only assembly; no kernel receipt imported.</strong></p>')
        cards=''.join(proof_card(c) for c in json.loads((lab/'claims.json').read_text()))
        body=re.sub(r'<!-- STATEMENTS -->[\s\S]*?<!-- /STATEMENTS -->',lambda _:cards,body)
        body=re.sub(r'<!-- LEAN_SOURCE -->[\s\S]*?<!-- /LEAN_SOURCE -->',lambda _:'<pre>'+html.escape((lab/'LateralInterfaceTransfer.lean').read_text())+'</pre>',body)
        (lab/'index.html').write_text(body);shutil.copyfile(out/'evidence/lateral-audit/algebra-audit.json',lab/'algebra-audit.json')
    else:
        runtime=[]
        for family,names in [('directional-compression-lab',['model.mjs','app.mjs','view.mjs']),('full-face-load-pressure',['model.mjs','app.mjs'] if group=='full-face-load-pressure' else [])]:
            for n in names:
                rel='education/contributions/'+family+'/'+n;p=lab/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'contributions'/family/n,p);runtime.append(rel)
        lock=json.loads((ROOT/'contributions/directional-compression-lab/inputs.lock.json').read_text())
        for f in lock['reusedModules']:
            p=lab/f['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/f['path'],p);runtime.append(f['path'])
        shutil.copyfile(ROOT/'contributions/directional-compression-lab/AreaLoadContracts.lean',lab/'AreaLoadContracts.lean')
        shutil.copyfile(ROOT/'contributions'/group/'README.md',lab/'original-method.md')
        result=defaults['result'];p=result['parameters'];fields=[('axialStretch','Prescribed X stretch',.8,1.2,.01),('mu','Shear parameter mu (Pa)',500,5000,100),('bulk','Bulk parameter K (Pa)',0,250000,500)]
        if group=='directional-compression-lab':fields.insert(1,('heightStretch','Controlled transverse stretch h',.5,1,.01));title='Let the free transverse direction respond';mode='';iterations='iterations'
        else:
            fields[1:1]=[('breadthFactor','Reference free-axis breadth factor',.5,2,.1),('forceN','One-face force target (N)',0,100,.01),('pressurePa','Applied current-area traction target (Pa)',0,100000,50)];title='Hold total force or current-area pressure';mode='<label>Loading mode<select data-param="mode" disabled><option value="force">Fixed total force</option><option value="pressure">Fixed current pressure</option></select></label>';iterations='outerIterations'
        controls=mode+'<label>Loaded transverse axis<select data-param="direction" disabled><option>Y</option><option>Z</option></select></label>'+''.join(f'<label>{label}<input disabled type="number" data-param="{key}" min="{lo}" max="{hi}" step="{step}" value="{p[key]}"></label>' for key,label,lo,hi,step in fields)+f'<label>Bisection cap<select data-param="{iterations}" disabled><option>8</option><option>32</option><option selected>64</option></select></label>'
        s=result['state'];table='<dl>'+''.join('<div><dt>'+html.escape(k)+'</dt><dd>'+html.escape(str(v))+'</dd></div>' for k,v in [('Default stretches X/Y/Z',s['stretches']),('Default J',s['J']),('One-face C (N), compression positive',s['compressionResultantN']),('Applied current-area q (Pa)',s['contactPressurePa']),('X end resultant (N), tension positive',s['endResultantN']),('Free-face residual (Pa)',s['freeResidualPa'])])+'</dl>'
        method=(ROOT/'book/research-additions'/('03-directional-compression.md' if group=='directional-compression-lab' else '04-force-pressure.md')).read_text()
        method=re.sub(r'\{\{[^}]+\}\}','',method).split('## Predict',1)[0]
        method_html=markdown_html(method).replace('href="labs/','href="../../labs/').replace('href="sources/','href="../../sources/')
        body='<h1>'+title+'</h1><p class="scope">Authored, uncalibrated, passive isotropic homogeneous specimen. Bilateral grips, full-face loading. No anatomy, active fibres, biological validation or fluid pressure. Source-only Lean status; no proof receipt is attached.</p><div class="controls">'+controls+'</div><button disabled id="reset">Reset</button><button disabled id="export">Download displayed state</button><p role="status" id="status">Static default below; runtime byte checks enable controls.</p><div id="scene">'+defaults['scene']+'</div><div id="readout">'+table+'</div><noscript>JavaScript is disabled. The real default solution, formulas, methods and source remain readable.</noscript><h2>Method and formal scope</h2>'+method_html+'<p><a href="../../book.html#'+('directional-passive-compression' if group=='directional-compression-lab' else 'full-face-force-pressure')+'">Complete lesson and exercises</a> · <a href="AreaLoadContracts.lean">Exact conditional Lean source</a> · <a href="formal-status.json">Source-only formal status</a> · <a href="original-method.md">Frozen author method, including its separate proof-gated build instructions</a></p><pre class="proof-source">'+html.escape((lab/'AreaLoadContracts.lean').read_text())+'</pre>'
        page=doc(title,body).replace('href="edition.css"','href="../../edition.css"').replace('<a href="index.html">Full reading guide','<a href="../../index.html">Full reading guide').replace('href="book.html"','href="../../book.html"').replace('href="kenoma-research-edition','href="../../kenoma-research-edition').replace('href="qualification.json"','href="../../qualification.json"').replace('</body>','<script type="module" src="source-only-boot.mjs"></script></body>')
        (lab/'index.html').write_text(page);runtime+=['index.html','AreaLoadContracts.lean','original-method.md']
        manifest={'schema':2,'files':[{'path':n,'bytes':(lab/n).stat().st_size,'sha256':sha((lab/n).read_bytes())} for n in runtime]};write_json(lab/'runtime-integrity.json',manifest)
        boot="const allowed="+json.dumps(runtime)+";const manifestSha='"+sha((lab/'runtime-integrity.json').read_bytes())+"';\n"+'''const digest=async b=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');try{const r=await fetch('runtime-integrity.json');if(!r.ok)throw Error('missing inventory');const bytes=await r.arrayBuffer();if(await digest(bytes)!==manifestSha)throw Error('inventory changed');const m=JSON.parse(new TextDecoder().decode(bytes));if(m.schema!==2||m.files.length!==allowed.length||new Set(m.files.map(f=>f.path)).size!==allowed.length)throw Error('incomplete inventory');for(const f of m.files){if(!allowed.includes(f.path))throw Error('unsafe path');const r=await fetch(f.path);if(!r.ok)throw Error('missing source');const b=await r.arrayBuffer();if(b.byteLength!==f.bytes||await digest(b)!==f.sha256)throw Error('source changed')}await import('./education/contributions/'''+group+'''/app.mjs')}catch(e){document.querySelector('#status').textContent='Interactive model refused: '+e.message;document.querySelectorAll('input,select,button').forEach(x=>x.disabled=true)}'''
        (lab/'source-only-boot.mjs').write_text(boot)
    write_json(lab/'formal-status.json',{'kind':'SOURCE_ONLY_EDUCATIONAL_ASSEMBLY','research_commit':RESEARCH,'research_tree':RESEARCH_TREE,'proof_compilation':'UNRUN','verified_proof_receipt_imported':False,'registry_modified':False,'legacy_proof_gated_builder_executed':False})
    write_json(lab/'default-state.json',defaults)

def compose(m, manifest, out, parent, evidence):
    """Pure composition from explicit prepared source components; no verification shortcut."""
    out=outside(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir();shutil.copytree(parent/'preview',out/'preview');shutil.copytree(parent/'published',out/'published');shutil.copytree(evidence,out/'evidence');shutil.copyfile(manifest,out/'input-manifest.json')
    (out/'.nojekyll').write_text('');(out/'edition.css').write_text(CSS);(out/'sources/contributions').mkdir(parents=True)
    for n in m['authored_research_sources']:
        dest=out/'sources'/n.removeprefix('education/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/n,dest)
    defaults={g:model_default(g) for g in LABS.values()}
    for slug,group in LABS.items():lab_build(out,slug,group,defaults[group])
    # Recover illustrations as explicitly labelled pages of the immutable PDF.
    # This executes no historical numerical or anatomical code.
    import fitz
    from PIL import Image
    old=fitz.open(out/'published/kenoma-mechanics.pdf');figures=out/'published/figure-pages';figures.mkdir()
    for number in sorted(set(FIGURE_PAGES.values())):
        pix=old[number-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False);Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(figures/f'page-{number}.jpg',quality=85)
    original=(out/'published/kenoma-mechanics.md').read_text();original=re.sub(r'\A---\n[\s\S]*?\n---\n','',original);figure_receipts=[]
    def figure(match):
        alt,path=match.groups()
        if path not in FIGURE_PAGES:raise ValueError('Unbound historical figure: '+path)
        number=FIGURE_PAGES[path];figure_receipts.append({'original_path':path,'archived_page':number,'description':alt,'image_sha256':sha((figures/f'page-{number}.jpg').read_bytes())})
        alias=' id="lab-property-deformation"' if path=='assets/property-deformation.svg' else ''
        return f'<figure{alias}><a href="published/kenoma-mechanics.pdf#page={number}"><img class="archive-page" src="published/figure-pages/page-{number}.jpg" alt="Archived PDF page {number}: {html.escape(alt,quote=True)}"></a><figcaption>Historical illustration retained as archived PDF page {number}; no experiment rerun. {html.escape(alt)}</figcaption></figure>'
    historical=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',figure,original)
    historical=re.sub(r'<div class="projection-interactive">[\s\S]*?</div>','<p class="archive-notice">The fixed-field interactive experiment remains part of the original published edition. This archival reader preserves its text and illustration but executes no fixed-field integration. <a href="https://github.com/MrScripty/Kenoma/blob/'+PUBLISHED+'/education/standalone/pressure-projection-lab.html">Exact historical laboratory source</a>.</p>',historical)
    remapped=[]
    def legacy_link(match):
        target=match[2]
        if target.startswith(('https:','http:','mailto:','#')):return match[0]
        url=own_source_url(target)
        if not url:
            if target.endswith('index.html') or target.startswith('index.html#lab-'):url='historical-labs.html'
            else:raise ValueError('Unresolved historical download: '+target)
        remapped.append({'original':target,'destination':url});return match[1]+url+match[3]
    historical=re.sub(r'(\]\()([^)]+)(\))',legacy_link,historical)
    previous=(parent/'supplement.html').read_text();chunks=re.split(r'(?=<h1\b)',previous);first=[]
    for anchor in ['nonuniform-local-volume','architecture-to-force']:
        hits=[x for x in chunks if re.match('<h1[^>]*id="'+anchor+'"',x)]
        if len(hits)!=1:raise ValueError('Expected accepted baseline addition')
        first.append(hits[0])
    lateral=(ROOT/'contributions/lateral-interface-transfer/chapter.md').read_text();lateral=lateral.replace('# Give a lateral force a compatible load path','# Give a lateral force a compatible load path {#lateral-interface-transfer}',1)
    lateral+='\n\n[Open the actual lateral-interface laboratory](labs/lateral-interface-transfer/index.html).\n\n{{lateral-figure}}\n\n'+''.join('\n### '+c['title']+'\n\n**Unregistered source only; compilation and axiom report UNRUN.**\n\n```lean\n'+c['statement_lean']+'\n```\n\n'+c['limitations']+'\n' for c in json.loads((ROOT/'contributions/lateral-interface-transfer/claims.json').read_text()))
    lateral+='\n\n## Exact lateral-interface Lean source: compilation UNRUN\n\n```lean\n'+(ROOT/'contributions/lateral-interface-transfer/LateralInterfaceTransfer.lean').read_text()+'\n```\n'
    conditional=(ROOT/'contributions/directional-compression-lab/AreaLoadContracts.lean').read_text()
    addition_md=lateral+'\n\n'+''.join((ROOT/'book/research-additions'/n).read_text()+'\n\n' for n in ['03-directional-compression.md','04-force-pressure.md','05-geometry-contract.md'])
    for slug,group in [('directional','directional-compression-lab'),('full-face','full-face-load-pressure')]:
        svg=defaults[group]['scene']
        if 'xmlns=' not in svg:svg=svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ',1)
        (out/f'{slug}-default.svg').write_text(svg);addition_md=addition_md.replace('{{'+slug+'-figure}}',f'![Actual default solved passive block; gray reference, blue current.](./{slug}-default.svg)\n\nThe figure uses the exact displayed default state. [Default JSON](labs/'+('directional-compression' if slug=='directional' else 'full-face-load-pressure')+'/default-state.json).')
    raw_lateral=(ROOT/'contributions/lateral-interface-transfer/index.html').read_text();svg=re.search(r'<svg id="diagram"[\s\S]*?</svg>',raw_lateral)[0];(out/'lateral-default.svg').write_text(svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ',1));addition_md=addition_md.replace('{{lateral-figure}}','![Actual default schematic displacement graph, amplified 1000 times.](lateral-default.svg)')
    addition_md=addition_md.replace('{{conditional-source}}','```lean\n'+conditional+'\n```')
    diagram='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 220"><style>text{font:24px sans-serif;fill:#17383b}rect{fill:#e6eeea;stroke:#779c94}</style><rect x="12" y="12" width="625" height="194" rx="12"/><text x="30" y="55">Retained positions and source identities</text><text x="30" y="98">↓ geometry-only observer; execution held</text><text x="30" y="141">Material sections ≠ tendon CSA ≠ PCSA</text><text x="30" y="184">Force, local orientation and biology remain open</text></svg>'
    (out/'quantity-contract.svg').write_text(diagram);addition_md=addition_md.replace('{{quantity-figure}}','![The geometry observer connects retained positions to declared quantities, with execution held.](quantity-contract.svg)')
    scope='''# Read the full edition and its research additions {#research-edition-scope}

The composition retains the historical chapters and adds six source-bound lessons. Registered Lean sources do not establish compilation. Numerical demonstrations are synthetic; anatomical execution and biological calibration remain unqualified. The reading derivative supplies the full status and evidence boundaries.
'''
    archived_notice='<div class="archive-notice"><strong>Complete historical edition.</strong> The following 25 chapters and twelve source appendices retain original prose and historical checked labels at '+PUBLISHED+'. This is archival evidence, not new compilation or simulation qualification. Every original illustration is linked to its exact archived PDF page. Existing published interactive laboratories are retained independently.</div>'
    full_html=markdown_html(historical);additions_html=''.join(first)+markdown_html(addition_md)
    reference_source=(parent/'preview/index.html').read_text()
    reference_html=re.search(r'(<h1 id="sources-and-evidence-boundaries"[\s\S]*?)</main>',reference_source)[1]
    reference_html=re.sub(r'((?:href|src)=")((?!https?:|mailto:|#)[^"]+)(")',lambda x:x[1]+'preview/'+x[2]+x[3],reference_html)
    body=markdown_html(scope)+archived_notice+full_html+'<section id="research-additions">'+additions_html+'</section>'
    (out/'book.html').write_text(doc('Kenoma: complete edition and authored research additions',body))
    (out/'additions.html').write_text(doc('Kenoma: authored research additions',markdown_html(scope)+additions_html+reference_html))
    # Markdown keeps all original prose/appendices, with bound archive images and downloads.
    old_preview_md=(parent/'preview/kenoma-mechanics.md').read_text();parts=re.split(r'(?=^# )',old_preview_md,flags=re.M);two=''.join(x for x in parts if x.startswith('# Uneven stretch') or x.startswith('# Connect fibre architecture'))
    two=re.sub(r'\]\((?!https?:|mailto:)([^)]+)\)',lambda x:'](preview/'+('index.html' if x[1].startswith('#') else '')+x[1]+')',two)
    combined=scope+'\n\n'+historical+'\n\n'+two+'\n\n'+addition_md
    reference_md=next(x for x in parts if x.startswith('# Sources and evidence boundaries'))
    reference_md=re.sub(r'\]\((?!https?:|mailto:|#)([^)]+)\)',lambda x:'](preview/'+x[1]+')',reference_md)
    (out/'kenoma-research-edition.md').write_text(combined);(out/'research-additions.md').write_text(scope+'\n\n'+two+'\n\n'+addition_md+'\n\n'+reference_md)
    navigation=json.loads((parent/'navigation.json').read_text())['chapters'];rows=[]
    for item in navigation:
        text=git('show',PUBLISHED+':education/book/chapters/'+item['name']).decode();anchor=re.search(r'\{#([^}]+)\}',text)
        if anchor:target=anchor[1]
        else:target=re.sub(r'[^\w -]','',item['title'].lower()).replace(' ','-')
        rows.append('<li><a href="book.html#'+target+'">'+html.escape(item['title'])+'</a> · <a href="'+item['source_url']+'">Frozen source</a></li>');item['reader_anchor']=target
    anchors=['nonuniform-local-volume','architecture-to-force','lateral-interface-transfer','directional-passive-compression','full-face-force-pressure','anatomical-geometry-contract-source']
    portal=markdown_html(scope)+'<h2>The complete original book</h2><ol>'+''.join(rows)+'</ol><h2>Six coherent additions</h2><ol>'+''.join('<li><a href="book.html#'+a+'">'+html.escape(a.replace('-',' ').capitalize())+'</a></li>' for a in anchors)+'</ol><p><a href="published/kenoma-mechanics.pdf">Unchanged original 208-page PDF</a> · <a href="published/kenoma-mechanics.md">Exact original Markdown</a> · <a href="research-additions.pdf">Illustrated additions PDF</a> · <a href="preview/index.html">Historical 19-chapter preview</a></p><p><a href="input-manifest.json">Immutable inputs</a> · <a href="source-binding.json">Sources, locks and figure provenance</a> · <a href="historical-labs.html">Published laboratory preservation and execution scope</a></p>'
    (out/'index.html').write_text(doc('Kenoma: full edition and new authored lessons',portal))
    (out/'historical-labs.html').write_text(doc('Preserved published laboratories',markdown_html('''# The established laboratories remain in the published edition

This candidate is an additive directory and archival reading surface. It preserves all 25 original chapters and their exact 208-page PDF. It does not replace the current root or original interactive laboratories with the 19-chapter preview.

The complete reader retains every original laboratory description and illustration as exact PDF-page reproductions, and links to immutable historical sources. Its old exercises describe the original published runtime. This local candidate does not newly execute or qualify the original anatomical, coupled, spatial or fixed-field integrations. Their source paths and historical evidence remain part of the complete book and source checkout. Publication must preserve their existing URLs.

The newly permitted synthetic controllers are the lateral discrete network, unequal transverse passive block, and inverse full-face force/pressure lab. The accepted nonuniform-volume and architecture controls remain available in the preserved preview assets, with source-only formal status. The anatomy inspector and geometry adapter are downloadable source-reading material; their execution stays held.
''')))
    write_json(out/'navigation.json',{'published_chapters':navigation,'new_chapters':anchors,'ordinary_registry':115,'additional_unregistered_sources':9,'publication_layout':'Append a distinct educational-research directory and retain every existing root path. This local guide is not a replacement root.'})
    write_json(out/'source-binding.json',{'research_commit':RESEARCH,'research_tree':RESEARCH_TREE,'authored_sources':m['authored_research_sources'],'historical_figure_page_bindings':figure_receipts,'historical_download_remapping':remapped,'legacy_lock_audit':json.loads((out/'evidence/source-binding-audit.json').read_text()),'historical_pdf_sha256':sha((out/'published/kenoma-mechanics.pdf').read_bytes()),'proof_receipts_imported':False})
    write_json(out/'build-manifest.json',{'candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'input_manifest_sha256':sha(Path(manifest).read_bytes()),'kind':'ADDITIVE_FULL_BOOK_RESEARCH_CANDIDATE','complete_original_chapters':25,'complete_original_pages':208,'added_lessons':6,'new_permitted_labs':3,'anatomical_execution':'HELD_SOURCE_ONLY','proof_compilation':'UNRUN','original_standalone_builders_executed':False,'reference_datasets_changed':False,'publication_authorized':False,'allowed_default_models':list(LABS.values())})
    print(json.dumps({'output':str(out),'published_chapters_preserved':25,'added_lessons':6,'new_synthetic_labs':3,'research_commit':RESEARCH}))
