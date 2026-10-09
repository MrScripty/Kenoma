"""Build and qualify the reader from pinned Git objects, never prior output snapshots.

Only five synthetic teaching controllers and their bounded audits execute.
No npm build, Lean invocation, contribution builder or anatomical program runs.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import json
import os
import sys
from pathlib import Path
import re
import shutil
import subprocess
from threading import Thread

from research_edition import (REPO, ROOT, BASE, RESEARCH, RESEARCH_TREE, PUBLISHED,
                              ARCHIVE, compose, markdown_html, sha, git, outside, write_json)
from educational_supplement import TREE
from clean_reading_edition import derive, clean_prose, scan_public
from qualify_clean_reading import qualify
from scoped_release import inventory, proof_block, EDITS
from architecture_force_lab import DEFAULT_ROWS, DEFAULT_CAPTION, source_inventory

PLAN = ROOT/'book/source-first-reading.json'


def run(argv, **kwargs):
    return subprocess.check_output(argv, cwd=REPO, text=True, **kwargs)


def browser_path():
    from playwright.sync_api import sync_playwright
    explicit = os.environ.get('KENOMA_READING_CHROMIUM')
    if explicit:
        p = Path(explicit).resolve()
    else:
        with sync_playwright() as pw:
            p = Path(pw.chromium.executable_path)
    if not p.is_file():
        raise ValueError('Install the pinned Playwright Chromium or specify KENOMA_READING_CHROMIUM')
    return str(p)


def setup():
    plan = json.loads(PLAN.read_text())['setup']
    if '.'.join(map(str,sys.version_info[:3]))!=plan['python']:raise ValueError('Python differs from pinned setup')
    versions = {n: importlib.metadata.version(n) for n in plan['python_packages']}
    if versions != plan['python_packages']:
        raise ValueError('Python package versions differ from source-first setup')
    node = run(['node', '--version']).strip()
    pandoc = run(['pandoc', '--version']).splitlines()[0]
    if node != plan['node'] or pandoc not in plan['pandoc_versions']:
        raise ValueError('Node/Pandoc differ from pinned setup: '+str((node, pandoc)))
    browser = browser_path()
    browser_version = run([browser, '--version']).strip()
    if plan['chromium_version'] not in browser_version:
        raise ValueError('Chromium differs from pinned rendering setup: '+browser_version)
    fonts=[]
    for name in plan['fonts']:
        family,path=run(['fc-match','-f','%{family}|%{file}',name]).strip().split('|',1)
        if name not in family.split(','):raise ValueError('Required font substituted: '+name)
        fonts.append(path)
    if len(fonts) != 4 or any(not Path(p).is_file() for p in fonts):
        raise ValueError('Required Liberation/DejaVu fonts are unavailable')
    return {'python':'.'.join(map(str,sys.version_info[:3])), 'node':node, 'pandoc':pandoc, 'python_packages':versions,
            'chromium_version':browser_version, 'chromium_sha256':sha(Path(browser).read_bytes()),
            'node_sha256':sha(Path(shutil.which('node')).resolve().read_bytes()),
            'pandoc_sha256':sha(Path(shutil.which('pandoc')).resolve().read_bytes()),
            'fonts':{Path(p).name:sha(Path(p).read_bytes()) for p in fonts}}, browser


def pinned_inputs():
    plan = json.loads(PLAN.read_text())
    for ref, tree in plan['git_inputs'].items():
        if git('rev-parse', ref+'^{tree}').decode().strip() != tree:
            raise ValueError('Pinned tree mismatch: '+ref)
    # Every copied/executed scientific file is checked against its registered fixed source.
    research = git('diff','--name-only',BASE,RESEARCH).decode().splitlines()
    if len(research) != 60:
        raise ValueError('Expected 60 frozen research source paths')
    paths = set(git('ls-files','education/tools','education/book','education/proofs',
                    'education/contributions','education/requirements.txt','education/reading-requirements.lock','.github/workflows/reading-edition.yml',
                    'education/research/architecture-force-book-source.json','education/research/source-first-reading-pipeline.md',
                    'education/review/nonuniform-volume-acceptance/composition.json',
                    'education/data/elbow-v1/LICENSES_AND_ATTRIBUTION.txt',
                    'education/data/elbow-v1/provenance.json','LICENSE').decode().splitlines())
    deps=json.loads((ROOT/'contributions/directional-compression-lab/inputs.lock.json').read_text())['reusedModules']
    paths.update(f['path'] for f in deps)
    files={}
    for name in sorted(paths):
        ref=RESEARCH if name in research else BASE
        present=subprocess.run(['git','cat-file','-e',ref+':'+name],cwd=REPO,capture_output=True).returncode==0
        # Release implementation/new editorial chapters are bound to this candidate instead.
        if name.startswith(('education/tools/','education/book/')) or not present:
            ref='HEAD'
        raw=git('show',ref+':'+name)
        p=REPO/name
        if p.is_symlink() or p.read_bytes()!=raw:
            raise ValueError('Pinned scientific/source bytes changed: '+name)
        files[name]={'commit':git('rev-parse',ref).decode().strip(),
                     'blob':git('rev-parse',ref+':'+name).decode().strip(),
                     'sha256':sha(raw),'bytes':len(raw)}
    history={}
    portable=json.loads(git('show',PUBLISHED+':'+ARCHIVE.removesuffix('artifacts/')+'portable-bundle.json'))
    for name in ['kenoma-mechanics.md','kenoma-mechanics.pdf']:
        path=ARCHIVE+name;raw=git('show',PUBLISHED+':'+path)
        if sha(raw)!=portable['file_sha256'][name]:raise ValueError('Historical archive hash mismatch')
        history[name]={'commit':PUBLISHED,'path':path,'blob':git('rev-parse',PUBLISHED+':'+path).decode().strip(),'sha256':sha(raw),'bytes':len(raw)}
    return files, {n:files[n] for n in research}, history


def seal(destination):
    destination=outside(destination)
    if destination.exists():raise FileExistsError(destination)
    if git('status','--porcelain'):raise ValueError('Commit source before sealing')
    files,research,history=pinned_inputs();tools,_=setup()
    write_json(destination,{'kind':'PINNED_SOURCE_FIRST_READING_INPUTS',
        'candidate_commit':git('rev-parse','HEAD').decode().strip(),
        'candidate_tree':git('rev-parse','HEAD^{tree}').decode().strip(),
        'plan_sha256':sha(PLAN.read_bytes()),'sources':files,'authored_research_sources':research,
        'historical_archive':history,'git_inputs':json.loads(PLAN.read_text())['git_inputs'],
        'setup':tools,'proof_compilation':'UNRUN','anatomical_execution':'HELD_UNRUN',
        'held_campaigns_executed':False,'cap_changes':False})
    destination.chmod(0o444)


def verify(manifest):
    m=json.loads(outside(manifest).read_text())
    if git('status','--porcelain') or m['candidate_commit']!=git('rev-parse','HEAD').decode().strip() or m['candidate_tree']!=git('rev-parse','HEAD^{tree}').decode().strip():
        raise ValueError('Candidate changed')
    files,research,history=pinned_inputs();tools,browser=setup()
    if (m['sources'],m['authored_research_sources'],m['historical_archive'],m['setup'])!=(files,research,history,tools):
        raise ValueError('Source or setup binding changed')
    if m['plan_sha256']!=sha(PLAN.read_bytes()) or m['git_inputs']!=json.loads(PLAN.read_text())['git_inputs']:
        raise ValueError('Source-first plan changed')
    if m['proof_compilation']!='UNRUN' or m['anatomical_execution']!='HELD_UNRUN' or m['held_campaigns_executed'] or m['cap_changes']:
        raise ValueError('Scientific scope changed')
    return m,browser


def audits(evidence, m):
    evidence.mkdir()
    commands=[['node','--test','--test-reporter=tap',*[f'education/contributions/{g}/model.test.mjs' for g in ['lateral-interface-transfer','directional-compression-lab','full-face-load-pressure']]],
        ['python3','education/contributions/lateral-interface-transfer/check_algebra.py','--output',str(evidence/'lateral-audit')],
        ['python3','education/contributions/directional-compression-lab/math_audit.py','--out',str(evidence/'directional-audit.json')],
        ['python3','education/contributions/full-face-load-pressure/math_audit.py','--model','education/contributions/full-face-load-pressure/model.mjs','--out',str(evidence/'full-face-audit.json')]]
    for i,command in enumerate(commands):
        result=subprocess.run(command,cwd=REPO,capture_output=True,text=True)
        (evidence/f'command-{i}.log').write_text(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError('Bounded audit failed: '+str(command))
        if i==0:
            if not re.search(r'# pass 15\b',result.stdout) or not re.search(r'# fail 0\b',result.stdout):raise ValueError('Expected fifteen successful model tests')
            write_json(evidence/'node-tests.json',{'command':command,'passed':15,'failed':0,'source_commit':RESEARCH,'proof_compilation':'UNRUN'})
    groups=[]
    for group in ['directional-compression-lab','full-face-load-pressure']:
        lock=json.loads((ROOT/'contributions'/group/'inputs.lock.json').read_text());rows=[]
        # Traverse explicit lock entries, retaining the two documented editorial differences.
        def entries(value):
            if isinstance(value,dict):
                if {'path','sha256','bytes'}<=value.keys():yield value
                else:
                    for x in value.values():yield from entries(x)
            elif isinstance(value,list):
                for x in value:yield from entries(x)
        for f in entries(lock):
            path=f['path'];p=REPO/path
            if not p.is_file():raise ValueError('Missing locked source: '+path)
            matches=sha(p.read_bytes())==f['sha256'] and p.stat().st_size==f['bytes']
            allowed=path in ['education/contributions/directional-compression-lab/README.md','education/contributions/directional-compression-lab/run_bounded.py']
            if not matches and not allowed:raise ValueError('Scientific dependency lock mismatch: '+path)
            rows.append({'path':path,'matches':matches,'editorial_difference':not matches and allowed,'actual_sha256':sha(p.read_bytes()),'expected_sha256':f['sha256']})
        groups.append({'contribution':group,'files':rows})
    write_json(evidence/'source-binding-audit.json',{'kind':'FRESH_FIXED_SOURCE_BINDING_AUDIT','groups':groups,'research_commit':RESEARCH,'proof_receipt_inferred':False})
    write_json(evidence/'commands.json',{'commands':commands,'proof_compilation':'UNRUN','anatomical_execution':'HELD_UNRUN'})


def baseline_labs(out, m, browser):
    """The two accepted controls only; no broad preview or proof-gated builders."""
    out.mkdir();(out/'assets').mkdir();(out/'proofs').mkdir()
    for p in (ROOT/'proofs').iterdir():
        if p.is_file() and p.suffix in {'.lean','.json'}:shutil.copyfile(p,out/'proofs'/p.name)
    shutil.copyfile(REPO/'LICENSE',out/'LICENSE')
    (out/'THIRD-PARTY-NOTICES.md').write_text('# Notices\n\nReference notices retained under data/elbow-v1. Synthetic lab sources retain their existing Apache-2.0 license.\n')
    data=out/'data/elbow-v1';data.mkdir(parents=True)
    for n in ['LICENSES_AND_ATTRIBUTION.txt','provenance.json']:shutil.copyfile(ROOT/'data/elbow-v1'/n,data/n)
    src=ROOT/'contributions/architecture-force';arch=out/'architecture-force';shutil.copytree(src,arch)
    source_inventory(ROOT)
    body=(arch/'index.html').read_text();defaults='<dl>'+''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k,v in DEFAULT_ROWS)+'</dl>'
    body=body.replace('<div id="readout" role="status" aria-live="polite"></div>','<div id="readout" role="status" aria-live="polite">'+defaults+'</div>')
    body=body.replace('<p id="interpretation"></p>','<p id="interpretation">Force–length held at 1 for the default area/stress transformation.</p>').replace('<div id="composition"></div>','<div id="composition">Total area 150 mm²; force 35 N; area-weighted nominal stress 233.33 kPa.</div>')
    body=body.replace('<main>','<main><p><a href="../index.html#architecture-to-force">Return to the reader</a> · <a href="registration.json">Source binding and formal status</a></p>');(arch/'index.html').write_text(body)
    write_json(arch/'registration.json',{'kind':'SOURCE_ONLY_READING_ASSEMBLY','candidate_commit':m['candidate_commit'],'compilation':'UNRUN','contracts':6})
    shutil.copytree(src,out/'contributions/architecture-force')
    src=ROOT/'contributions/nonuniform-isochoric-kinematics';nu=out/'nonuniform';nu.mkdir()
    composition=json.loads((ROOT/'review/nonuniform-volume-acceptance/composition.json').read_text())
    for name,h in composition['acceptedSourceFiles'].items():
        if sha((src/name).read_bytes())!=h:raise ValueError('Accepted nonuniform source changed')
    for name in ['model.mjs','claims.json','NonuniformIsochoric.lean','README.md']:shutil.copyfile(src/name,nu/name)
    write_json(nu/'composition.json',composition)
    content='<section id="real-contracts"><h2>Registered source; compilation UNRUN</h2><p>Six registered contracts; no new proof receipt.</p><p><a href="NonuniformIsochoric.lean">Complete Lean source</a> · <a href="claims.json">Claim map</a> · <a href="composition.json">Historical source composition</a></p></section>'
    template=(src/'index.template.html').read_text().replace('finite-mesh measurement requires JavaScript.','The captured default is readable; recomputation requires JavaScript.').replace('The complete map, assumptions and checked statements remain readable above.','The complete map, assumptions and source statements remain readable above.')
    template=re.sub(r'<footer>.*?</footer>','<footer>Source-only teaching assembly. Six contracts registered; compilation UNRUN. No anatomical completion.</footer>',template,flags=re.S)
    path=nu/'nonuniform-volume-lab.html';path.write_text(template.replace('__MODEL_CODE__',(src/'model.mjs').read_text()).replace('__PROOF_CONTENT__',content))
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(out)));Thread(target=server.serve_forever,daemon=True).start()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b=pw.chromium.launch(headless=True,executable_path=browser);page=b.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/nonuniform/nonuniform-volume-lab.html',wait_until='networkidle')
            figure=page.locator('#shape').evaluate('(e)=>e.outerHTML');path.write_text(page.content());b.close()
        figure=figure.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ',1).replace('>','><style>text{font:23px sans-serif;fill:#193438}</style>',1)
        (out/'assets/nonuniform-volume.svg').write_text(figure)
    finally:server.shutdown();server.server_close()


def components(parent,m,browser):
    parent.mkdir();published=parent/'published';published.mkdir()
    for name,f in m['historical_archive'].items():(published/name).write_bytes(git('show',PUBLISHED+':'+f['path']))
    preview=parent/'preview';baseline_labs(preview,m,browser)
    claims,_=inventory();mdparts=[];htmlparts=[]
    for name in ['09aa-nonuniform-volume.md','09ab-architecture-force.md']:
        text=(ROOT/'book/chapters'/name).read_text()
        for web in [False,True]:
            def expansion(match):
                key=match[1]
                if key.startswith('proof:'):return proof_block(claims[key.split(':')[1]],web)
                if key=='nonuniform-lab':return '\n![Actual default prescribed nonuniform geometry](assets/nonuniform-volume.svg)\n\n[Open the local-volume laboratory](nonuniform/nonuniform-volume-lab.html).\n'
                if key=='architecture-force-lab':return '\n| Default quantity | Value |\n|:--|:--|\n'+''.join(f'| {k} | {v} |\n' for k,v in DEFAULT_ROWS)+'\n'+DEFAULT_CAPTION+'\n\n[Open the architecture-force lab](architecture-force/index.html). [Primary sources](architecture-force/sources.json); [source binding](architecture-force/registration.json).\n'
                raise ValueError('Unexpected baseline directive: '+key)
            expanded=re.sub(r'\{\{([^}]+)\}\}',expansion,text)
            if web:htmlparts.append(markdown_html(expanded))
            else:mdparts.append(expanded)
    refs=(ROOT/'book/chapters/05-sources.md').read_text()
    for pattern,replacement in EDITS['05-sources.md']:
        refs,count=re.subn(pattern,replacement,refs,flags=re.S)
        if count!=1:raise ValueError('Sources editorial marker changed')
    (preview/'kenoma-mechanics.md').write_text('\n\n'.join(mdparts+[refs]))
    (preview/'index.html').write_text('<main>'+''.join(htmlparts)+markdown_html(refs)+'</main>')
    # Prefix baseline lesson downloads exactly once for the root reader.
    baseline=''.join(htmlparts)
    baseline=re.sub(r'((?:href|src)=")((?!https?:|mailto:|#)[^"]+)(")',lambda x:x[1]+'preview/'+x[2]+x[3],baseline)
    (parent/'supplement.html').write_text(baseline)
    composition=json.loads(git('show',PUBLISHED+':'+ARCHIVE.removesuffix('artifacts/')+'composition.json'));chapters=[]
    for name in composition['curriculum_unchanged']:
        path='education/book/chapters/'+name;raw=git('show',PUBLISHED+':'+path);title=re.sub(r'\s*\{#.*?\}','',re.search(r'^# (.+)',raw.decode(),re.M)[1])
        chapters.append({'name':name,'title':title,'sha256':sha(raw),'source_url':'https://github.com/MrScripty/Kenoma/blob/'+PUBLISHED+'/'+path})
    if len(chapters)!=25:raise ValueError('Historical chapter inventory changed')
    write_json(parent/'navigation.json',{'chapters':chapters})


def fonts(public):
    """Ship sealed font files so the static reader uses the same declared families."""
    families=json.loads(PLAN.read_text())['setup']['fonts'];folder=public/'fonts';folder.mkdir()
    css=[]
    for family in families:
        path=Path(run(['fc-match','-f','%{file}',family]).strip());shutil.copyfile(path,folder/path.name)
        css.append('@font-face{font-family:"'+family+'";src:url("fonts/'+path.name+'") format("truetype");font-display:block}')
    for group in ['fonts-dejavu-core','fonts-dejavu-extra','fonts-liberation']:
        p=Path('/usr/share/doc')/group/'copyright'
        if not p.is_file():raise ValueError('Font license notice missing: '+group)
        (folder/(group+'-LICENSE')).write_bytes(p.read_bytes())
    css.append('body{font-family:"DejaVu Serif",serif}pre,code{font-family:"DejaVu Sans Mono",monospace}input,select,button,.badge,svg text{font-family:"Liberation Sans",sans-serif}math{font-family:"DejaVu Math TeX Gyre",serif}math:not([display=block]){display:inline-block;max-width:100%;overflow:auto;vertical-align:middle}')
    with (public/'edition.css').open('a') as f:f.write('\n'+'\n'.join(css)+'\n')


def build(manifest, destination):
    m,browser=verify(manifest);destination=outside(destination)
    if destination.exists():raise FileExistsError(destination)
    destination.mkdir();work=destination/'build-evidence';work.mkdir()
    print(json.dumps({'phase':'bounded-audits','candidate':m['candidate_commit']}),flush=True)
    evidence=work/'numerical-audits';audits(evidence,m)
    print(json.dumps({'phase':'source-composition'}),flush=True)
    parent=work/'source-components';components(parent,m,browser)
    raw=work/'raw-composition';compose(m,manifest,raw,parent,evidence)
    files={str(p.relative_to(raw)):sha(p.read_bytes()) for p in raw.rglob('*') if p.is_file()}
    public=destination/'reader';private=destination/'private';derive(m,manifest,raw,files,public,private)
    fonts(public)
    # Fresh output never inherits network reachability observations from another build.
    status=json.loads((public/'edition-status.json').read_text())
    for key in ['public_links_reachable','public_links_blocked_unverified']:status.pop(key,None)
    status.update(external_link_network_check='UNRUN',build_kind='PINNED_SOURCE_FIRST_READING')
    write_json(public/'edition-status.json',status)
    print(json.dumps({'phase':'controls-print-and-privacy-qualification'}),flush=True)
    qualify(manifest,public,private,inputs=m,browser_executable=browser)
    status=json.loads((public/'edition-status.json').read_text());status['external_link_network_check']='UNRUN';write_json(public/'edition-status.json',status)
    receipt=json.loads((private/'qualification.json').read_text());receipt.update(external_links='Network reachability UNRUN; own-source Git objects checked',human_editorial_review='UNRUN_INFORMATIONAL',publication='NOT_EXECUTED',build_kind='PINNED_SOURCE_FIRST_READING')
    write_json(private/'qualification.json',receipt)
    # Compare all historical numeric tokens as well as the existing text/pixel checks.
    import fitz
    old=fitz.open(private/'unchanged-historical-original/kenoma-mechanics.pdf');new=fitz.open(public/'historical/kenoma-mechanics-reading.pdf')
    for i in range(208):
        if re.findall(r'[-+]?\d+(?:\.\d+)?',old[i].get_text())!=re.findall(r'[-+]?\d+(?:\.\d+)?',new[i].get_text()):raise ValueError('Historical number changed')
    scientific={str(p.relative_to(public)):sha(p.read_bytes()) for p in public.rglob('*') if p.is_file() and p.suffix in {'.mjs','.lean'} and p.name!='source-only-boot.mjs'}
    pinned_hashes={f['sha256'] for f in m['sources'].values()}
    if any(h not in pinned_hashes for h in scientific.values()):raise ValueError('Unbound scientific source copy')
    scan_public(public)
    write_json(public/'reading-manifest.json',{'kind':'SOURCE_FIRST_PUBLIC_READING_PAYLOAD','candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'files':{str(p.relative_to(public)):sha(p.read_bytes()) for p in sorted(public.rglob('*')) if p.is_file() and p.name!='reading-manifest.json'}})
    verify(manifest)
    diagnostics=destination/'ci-diagnostics';diagnostics.mkdir()
    write_json(diagnostics/'qualification.json',{'candidate_commit':m['candidate_commit'],'candidate_tree':m['candidate_tree'],'controls':receipt['controls'],'local_links_checked':receipt['local_links_checked'],'pdf_pages':receipt['pdf_pages'],'minimum_new_text_pt':receipt['minimum_new_text_pt'],'input_manifest_sha256':sha(Path(manifest).read_bytes()),'historical_numeric_tokens':'PASS_ALL_208_PAGES','scientific_source_bindings':'PASS','privacy':'PASS','proof_compilation':'UNRUN','anatomical_execution':'HELD_UNRUN'})
    print(json.dumps({'reader':str(public),'candidate_commit':m['candidate_commit'],'pdf_sha256':sha((public/'kenoma-research-edition.pdf').read_bytes()),'legacy_root_preservation':'SEPARATE_COMPLETENESS_GATE','proof_compilation':'UNRUN','anatomical_execution':'HELD_UNRUN'}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('seal');a.add_argument('manifest')
    a=s.add_parser('build');a.add_argument('manifest');a.add_argument('destination')
    a=p.parse_args()
    if a.action=='seal':seal(a.manifest)
    else:build(a.manifest,a.destination)
