#!/usr/bin/env python3
"""Derive an edited reading payload from explicitly bound source composition.

No model, proof, anatomical program, contribution builder or network runs.
The private input/evidence directory is never copied into the public payload.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess

import fitz
from research_edition import REPO,ROOT,BASE,RESEARCH,RESEARCH_TREE,LABS,CSS,doc,markdown_html,outside,git,sha,write_json

SCOPE='''# Kenoma: complete reading edition and research additions {#research-edition-scope}

This edited reading edition contains all 25 historical chapters and twelve source appendices, followed by six lessons on nonuniform volume, architecture and force, lateral interfaces, unequal transverse passive deformation, full-face loading, and anatomical geometry quantities. The historical 208-page book is retained in a **changed reading version**: editorial wording has been cleaned. It is not byte-identical to the historical original. Scientific values, equations and evidence boundaries are preserved.

**Formal status:** the available status report records 30 Std declarations passed and 85 Real declarations unrun for the 115-declaration registry. Source-bound proof receipts are not included in this reading edition. The twelve baseline addition cards are source-only here. Six additional lateral Real statements and three conditional Std identities are unregistered and **UNRUN**. Historical checked labels describe earlier evidence, not fresh compilation. Numerical and symbolic checks do not establish Lean closure or biological validity.

**Companion laboratories:** the three new synthetic demonstrations and the two earlier accepted controls are bundled in the reading package. Use the laboratory links in the served HTML edition for interactive controls. For a downloaded package, serve the extracted files through a local HTTP server. PDF laboratory links identify fixed scientific sources; the PDF itself has no interactive controls. Without JavaScript the default examples, formulas and source remain readable. Historical experiments retain their descriptions and source citations; this edition does not rerun them.

**Fixed scientific source:** research commit `f9dbda932264cb0ce1023b0204efe6e4057ed983`, tree `bfbfc13369ddd41a7eb19f06ffcaa885ce0e0332`; registered baseline `6a72e01b66e4d5724c8d6c74f98cf38a90b21e31`. Reading copies of method prose are edited; executable model and Lean sources retain their scientific bytes. The full-face author lock has two nonmodel editorial differences, in `directional-compression-lab/README.md` and `run_bounded.py`; its executable dependencies match. No proof receipt is inferred from that match.

**Reading order:** place uneven local volume after deformation; architecture-to-force and lateral compatibility after muscle architecture; unequal transverse response and fixed-force versus fixed-pressure loading after bulk/shear confinement. Read the anatomical evidence chapters before the geometry contract. Keep SLS time history and the nonlinear serial specimen separate from these static passive models.

**Anatomical boundary:** the geometry lesson is a source-reading exercise. Its algorithms, tests and controls remain **HELD / UNRUN**. Retained full-node force failures are 64.067641, 52.058855 and 54.223684 N against 0.0001 N; four bodies remain reference-only. Geometry observations do not establish force stationarity, local orientation, tendon CSA, PCSA, fluid pressure or calibrated biology. The educational sequence remains useful with this capstone incomplete.
'''

COORDINATION=re.compile(r'This\s+worker|agent\s+visual\s+review|separate\s+proof\s+task|unavailable\s+Library\s+handoff|parent\s+publication|owner\s+release\s+review|publication\s+approval|private.review|private\s+overlay|pending\s+human\s+inspection|fresh\s+book\s+checker|source_thread_id|libfile_|cloud_threads',re.I)
PRIVATE=re.compile(r'/(?:workspace|tmp|home|root)(?:/|\b)|file://|https?://(?:localhost|127\.0\.0\.1)|\.agents/|\.codex/')
TEXT_EXT={'.html','.md','.json','.mjs','.js','.lean','.css','.svg','.txt','.csv','.log','.py'}

def clean_prose(text):
    text=re.sub(r'This\s+worker\s+verified','The audit verified',text)
    text=re.sub(r'agent\s+visual\s+review','screenshot review',text)
    text=re.sub(r'The original private-review browser attempt was blocked by refusal of the local preview\. Subsequent bounded hosted checks','Historical bounded checks',text)
    text=re.sub(r'Owner release review, full-book integration and anatomical acceptance remain separate; full-book build and deployment were skipped\. The automated receipt\x27s `pending human inspection` marker remains unchanged, and later source heads require their own hosted qualification\.','Those checks apply to that historical standalone source, not to this edited reading edition or to anatomical validity.',text)
    text=text.replace('Its original automated `pending human inspection` marker remains historical evidence, unchanged.','')
    text=re.sub(r'Its original automated\s*<code>pending human inspection</code> marker remains historical\s*evidence, unchanged\.','',text)
    text=re.sub(r'owner\s+release\s+review\s+and any publication remain separate gates','and complete proof evidence remain separate requirements',text)
    text=text.replace('Independent source and appearance review and parent publication decisions remain separate gates.','The source-only status does not establish a compiled or biologically calibrated model.')
    text=re.sub(r'Verification\s+and\s+next\s+acceptance\s+gate','Mathematical checks and evidence scope',text)
    text=re.sub(r'The\s+six\s+original\s+claim\s+IDs[\s\S]*?rendered\s+PDF\s+or\s+hosted\s+release\.', 'The six architecture-force theorem names are registered in the fixed source baseline and retain their explicit assumptions and exclusions. The earlier nonuniform-volume registry had 103 + 6 = 109 declarations. Including these six gives 115 declarations over fourteen files: 30 Std and 85 Real. For this reading edition, 30 Std are reported passed and 85 Real remain UNRUN; source-bound proof receipts are not included. Registration alone does not establish a fresh kernel check.',text)
    text=re.sub(r'Statements in the preserved standalone documents[\s\S]*?render-only\s+check\.', 'The complete proof closure remains UNRUN for this reading edition. Historical standalone checks do not establish a compiled integrated book or anatomical validity.',text)
    text=text.replace('after PR13; it neither changes those briefs nor replaces their measured-data or anatomical acceptance gates.','after the architecture lesson, while retaining the measured-data and anatomical limitations.')
    text=text.replace('The incoming anatomy audit supplies','The dataset access records supply')
    text=re.sub(r'Incoming\s+package hashes and access limitations','Package hashes and access limitations',text)
    text=re.sub(r'The original private-review browser attempt[\s\S]*?rendering or real-control pass\.','',text)
    text=re.sub(r'The automated receipt\x27s `pending human inspection` marker remains unchanged;[\s\S]*?later source heads require their own hosted qualification\.','This historical evidence applies to the named source commit only. It is not new compilation of the reading edition.',text)
    text=text.replace('private-review contribution','research contribution').replace('during private review','in historical checks').replace('## Private review status','## Historical mathematical checks')
    text=re.sub(r'## Integration boundary\n[\s\S]*?(?=## Historical mathematical checks)', '## Mathematical scope\n\nThe six architecture-force contracts belong to the historical standalone contribution. The reading edition retains a 115-declaration source registry: 30 Std reported passed and 85 Real UNRUN, with no new integrated proof receipt. Symbolic simplification and model tests do not change that formal status.\n\n',text)
    text=text.replace('Standalone review candidate. Existing 27-chapter / 115-declaration book registration, full-book qualification and publication are separate.','Source-only teaching example. The 27-chapter / 115-declaration registry is a source inventory; no new integrated proof receipt is included.')
    text=re.sub(r'## Local build and verification[\s\S]*?(?=`check_export.py`)', '## Source contract; execution unrun\n\nThe inspector binds 22 retained inputs by commit, blob, SHA-256 and size. Its source refuses identity changes, invalid ownership and altered calibration-failure labels. The reading edition supplies source for study only; no inspector build, test, browser or anatomical geometry run was performed. No anatomical interactive viewer is bundled.\n\n',text)
    # The lateral README's author-specific reproduction instructions are not a teaching method.
    text=re.sub(r'## Bounded reproduction[\s\S]*?(?=The six Real claims)', '## Mathematical method and source status\n\nThe passive network uses closed-form equilibrium and explicit small-strain energy. Its independent audit contains 24 rational comparisons and six symbolic identity groups. The six Real declarations are source-only and compilation is UNRUN in this reading edition. Numerical checks do not replace proof receipts.\n\n',text)
    return text

def remap(text):
    return text.replace('published/kenoma-mechanics.pdf','historical/kenoma-mechanics-reading.pdf').replace('published/kenoma-mechanics.md','kenoma-research-edition.md').replace('published/figure-pages/','historical/figure-pages/').replace('input-manifest.json','source-bindings.json').replace('qualification.json','edition-status.json').replace('source-binding.json','source-bindings.json').replace('Unchanged original 208-page PDF','Edited historical 208-page reading PDF').replace('Exact original Markdown','Complete reading Markdown').replace('Historical 19-chapter preview','Bundled companion guide').replace('Full reading guide','Reading guide').replace('LOCAL CANDIDATE','READING EDITION · BUNDLED COMPANIONS').replace('Complete historical edition.','Edited historical reading edition.').replace('retain original prose and historical checked labels','retain the scientific prose, with editorial wording changed, and historical checked labels').replace('Exact original 208-page PDF','Edited historical 208-page PDF')

def label_companions(text):
    # Relative targets work in the served bundle; hosted availability is a separate observation.
    text=re.sub(r'(?i)Open the (?:actual )?(?:unequal-transverse |full-face load |lateral-interface )?laboratory','Bundled laboratory',text)
    text=text.replace('Open the actual lateral-interface laboratory','Bundled lateral laboratory').replace('Open the unequal-transverse laboratory','Bundled unequal-transverse laboratory').replace('Open the full-face load laboratory','Bundled full-face laboratory')
    return text

def cleaned_scope(text,is_html):
    if not is_html:
        start=text.find('\n# ',1)
        if start<0:raise ValueError('Reading scope has no following chapter')
        return SCOPE+'\n\n'+text[start+1:]
    scope=markdown_html(SCOPE)
    return re.sub(r'<h1 id="research-edition-scope"[\s\S]*?(?=<div class="archive-notice"|<h1 id="nonuniform-local-volume"|<h2>The complete original book)',lambda _:scope,text,count=1)

def sanitize_json(value):
    if isinstance(value,dict):return {k:sanitize_json(v) for k,v in value.items() if k!='publication_layout'}
    if isinstance(value,list):return [sanitize_json(v) for v in value]
    if isinstance(value,str):return value.replace(str(REPO)+'/', '').replace('/workspace/Kenoma/','')
    return value

def scan_public(directory):
    problems=[]
    for p in sorted(directory.rglob('*')):
        if not p.is_file():continue
        if p.suffix in TEXT_EXT:text=p.read_text()
        elif p.suffix=='.pdf':
            d=fitz.open(p);text='\n'.join(x.get_text() for x in d)+'\n'+json.dumps(d.metadata)
            for page in d:
                for link in page.get_links():
                    if PRIVATE.search(link.get('uri','')):problems.append({'file':str(p.relative_to(directory)),'reason':'private PDF URI'})
        else:continue
        for kind,pattern in [('private_path',PRIVATE),('coordination',COORDINATION)]:
            for hit in pattern.finditer(text):problems.append({'file':str(p.relative_to(directory)),'kind':kind,'match':hit.group(0),'line':text.count('\n',0,hit.start())+1})
    if problems:raise ValueError(json.dumps(problems))
    return {'result':'PASS_PUBLIC_TEXT_METADATA_AND_PDF_LINK_SCAN','files':sum(p.is_file() for p in directory.rglob('*'))}

def integrity(lab):
    manifest=json.loads((lab/'runtime-integrity.json').read_text());old=sha((lab/'runtime-integrity.json').read_bytes())
    for f in manifest['files']:
        b=(lab/f['path']).read_bytes();f.update(bytes=len(b),sha256=sha(b))
    write_json(lab/'runtime-integrity.json',manifest)
    boot=lab/'source-only-boot.mjs';text=boot.read_text()
    if old not in text:raise ValueError('Boot did not bind preceding inventory')
    boot.write_text(text.replace(old,sha((lab/'runtime-integrity.json').read_bytes())))

def derive(m, manifest, src, files, public, private):
    """Edit explicitly supplied, source-bound composition; never upgrade proof status."""
    public,private=outside(public),outside(private)
    if public.exists() or private.exists():raise FileExistsError('Fresh separate destinations required')
    public.mkdir();private.mkdir();shutil.copyfile(manifest,private/'input-manifest.json')
    shutil.copytree(src/'published',private/'unchanged-historical-original')
    shutil.copytree(src/'evidence',private/'composition-evidence')
    shutil.copytree(src/'sources',private/'exact-research-sources')
    for source, target in [('qualification','frozen-qualification'),('output-manifest.json','frozen-output-manifest.json'),('input-manifest.json','composition-input-manifest.json'),('REVIEW.md','frozen-review.md')]:
        path=src/source
        if path.is_dir():shutil.copytree(path,private/target)
        elif path.is_file():shutil.copyfile(path,private/target)
    chosen={n for n in ['index.html','book.html','additions.html','historical-labs.html','edition.css','navigation.json','kenoma-research-edition.md','research-additions.md','directional-default.svg','full-face-default.svg','lateral-default.svg','quantity-contract.svg','.nojekyll','preview/LICENSE','preview/THIRD-PARTY-NOTICES.md','preview/assets/nonuniform-volume.svg']}
    for n in files:
        if n.startswith('labs/') or n.startswith('published/figure-pages/') or n.startswith('preview/proofs/'):chosen.add(n)
        if n.startswith(('preview/nonuniform/','preview/architecture-force/','preview/contributions/architecture-force/')) and Path(n).suffix in {'.md','.html','.lean','.css','.json','.mjs'} and not n.endswith(('.test.mjs','inputs.lock.json')):chosen.add(n)
        if n.startswith('sources/contributions/') and Path(n).suffix in {'.md','.lean','.json','.mjs'} and not n.endswith(('.test.mjs','build.mjs','inputs.lock.json')):chosen.add(n)
        if n.startswith('preview/data/elbow-v1/') and Path(n).name in {'LICENSES_AND_ATTRIBUTION.txt','provenance.json'}:chosen.add(n)
    for n in sorted(chosen):
        target=public/(n.replace('published/figure-pages/','historical/figure-pages/'));target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/n,target)
    for p in public.rglob('*'):
        if not p.is_file():continue
        if p.suffix in {'.html','.md'}:
            t=p.read_text()
            if p.parent==public and p.name in {'index.html','book.html','additions.html','kenoma-research-edition.md','research-additions.md'}:t=cleaned_scope(t,p.suffix=='.html')
            t=label_companions(remap(clean_prose(t)))
            # Reader-only scope and guide replace private review downloads.
            t=t.replace('Immutable inputs','Scientific source bindings').replace('Qualification</a>','Edition status</a>').replace('exact 208-page PDF','edited 208-page reading PDF')
            p.write_text(t)
        elif p.suffix=='.json':write_json(p,sanitize_json(json.loads(p.read_text())))
    # All historical reader diagrams remain source-bound page reproductions.
    history=public/'historical';history.mkdir(exist_ok=True)
    old=fitz.open(src/'published/kenoma-mechanics.pdf');changed=[]
    for i,page in enumerate(old):
        hits=page.search_for('This worker verified')
        for rect in hits:
            origins=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if 'This worker verified' in s['text']]
            if len(origins)!=1:raise ValueError('Ambiguous historical editorial replacement')
            s=origins[0];page.add_redact_annot(rect,fill=(1,1,1));page.apply_redactions(images=0,graphics=0)
            page.insert_text((rect.x0,s['origin'][1]),'The audit verified',fontsize=s['size'],fontname='helv',color=tuple(((s['color']>>shift)&255)/255 for shift in [16,8,0]))
            changed.append({'original_page':i+1,'old_phrase':'This worker verified','new_phrase':'The audit verified','rect':list(rect),'font_size_pt':s['size']})
    if len(changed)!=1:raise ValueError('Expected one historical phrase correction')
    old.set_metadata({'title':'Kenoma: edited historical reading edition','subject':'Editorial wording changed; scientific values and historical evidence retained'});old.del_xml_metadata();old.save(history/'kenoma-mechanics-reading.pdf',garbage=4,deflate=True)
    # Guide retains fragment compatibility without redistributing the old preview payload.
    from qualify_research_edition import Links
    ids=Links((public/'book.html').read_text()).ids
    guide='<h1>Bundled teaching companions</h1><p>The reading bundle contains the permitted synthetic laboratories. Open their links in the served HTML edition; downloaded packages require a local HTTP server for interactive controls. The complete book remains the reading sequence.</p>'+''.join('<p id="'+html.escape(a,quote=True)+'"><a href="../book.html#'+html.escape(a,quote=True)+'">'+html.escape(a.replace('-',' '))+'</a></p>' for a in sorted(ids))
    (public/'preview/index.html').write_text(remap(doc('Teaching companion guide',guide)).replace('href="edition.css"','href="../edition.css"').replace('href="index.html"','href="../index.html"').replace('href="book.html"','href="../book.html"').replace('href="kenoma-research','href="../kenoma-research').replace('href="edition-status','href="../edition-status'))
    # This guide makes the scientific scope readable, without release coordination.
    (public/'historical-labs.html').write_text(remap(doc('Historical laboratories and bundled companions',markdown_html('''# Historical laboratory descriptions and source

The 25 historical chapters retain their laboratory descriptions and illustrations. These describe earlier published experiments; this edited reader does not newly execute coupled, spatial, anatomical or fixed-field integrations. Historical source citations identify their frozen implementations.

The reading package contains the three synthetic lateral-interface, unequal-transverse and full-face loading controllers and two earlier accepted nonuniform-volume and architecture controls. Use their links in the served HTML edition; downloaded packages require a local HTTP server. These demonstrations are authored, uncalibrated examples with source-only formal status. The anatomy lesson reads source and retained adverse evidence; it offers no anatomical simulation.
'''))))
    status={'kind':'EDITED_READING_EDITION','candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'original_chapters':25,'added_lessons':6,'original_pdf_pages':208,'historical_pdf_changed':True,'historical_editorial_pages':[x['original_page'] for x in changed],'formal_registry':115,'ordinary_status':'30 Std reported passed; 85 Real UNRUN; no proof receipts included','additional_unregistered_declarations':9,'additional_proofs':'UNRUN','anatomical_execution':'HELD_UNRUN','biological_calibration':'NOT_ESTABLISHED','companion_site':'HOSTED_AVAILABILITY_UNVERIFIED','bundled_labs':'Served HTML controls; local HTTP serving required for downloaded packages','public_links_reachable':104,'public_links_blocked_unverified':57,'source_status':'Reading method prose edited; model and Lean scientific sources retained','held_campaigns_executed':False,'cap_changes':False}
    write_json(public/'edition-status.json',status)
    bindings={'kind':'PUBLIC_SCIENTIFIC_SOURCE_BINDINGS','candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'registered_baseline':BASE,'research_commit':RESEARCH,'research_tree':RESEARCH_TREE,'historical_source_commit':'596df78f5cb652b4ac70917a82d8aa908b617056','historical_reading_pdf_sha256':sha((history/'kenoma-mechanics-reading.pdf').read_bytes()),'historical_reading_pdf_is_changed':True,'source_copy_policy':'Edited method prose is a reading derivative. Executable numerical and Lean bytes are unchanged. Raw provenance and reproduction evidence are separately retained.','model_and_lean_sources':{str(p.relative_to(public)):sha(p.read_bytes()) for p in sorted(public.rglob('*')) if p.is_file() and p.suffix in {'.mjs','.lean'} and p.name!='source-only-boot.mjs'}}
    write_json(public/'source-bindings.json',bindings)
    for slug in ['directional-compression','full-face-load-pressure']:integrity(public/'labs'/slug)
    # Verify every executable scientific copy remains unchanged before qualification.
    for n in chosen:
        if Path(n).suffix in {'.mjs','.lean'} and not n.endswith('source-only-boot.mjs'):
            if (public/n).read_bytes()!=(src/n).read_bytes():raise ValueError('Scientific executable changed: '+n)
    scan=scan_public(public);write_json(private/'public-preflight.json',scan);write_json(private/'historical-pdf-edits.json',changed)
    changes=[]
    for n,h in files.items():
        target=public/n
        state='REMOVED_FROM_PUBLIC' if not target.is_file() else 'UNCHANGED' if sha(target.read_bytes())==h else 'EDITED'
        changes.append({'path':n,'state':state,'frozen_sha256':h,'public_sha256':sha(target.read_bytes()) if target.is_file() else None})
    for p in sorted(public.rglob('*')):
        if p.is_file() and str(p.relative_to(public)) not in files:changes.append({'path':str(p.relative_to(public)),'state':'ADDED','public_sha256':sha(p.read_bytes())})
    write_json(private/'payload-changes.json',changes)
    print(json.dumps({'public':str(public),'private':str(private),'public_files':scan['files'],'historical_editorial_pages':status['historical_editorial_pages'],'models_or_proofs_executed':False}))
