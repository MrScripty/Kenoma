"""Reassemble an editorial review edition from source-bound historical evidence.

This never runs or replaces the release/proof checker. Unchanged proof cards,
appendices and experiment tables come from the pinned archived book; current
canonical prose, controls and app are rendered for layout/navigation review.
"""
from pathlib import Path
from zipfile import ZipFile
import argparse, hashlib, json, re, shutil, subprocess
from build import lab_block
from property_labs import block as property_block

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'deliverables/release-output-bound/kenoma-release-output-bound-portable.zip'
NOTE = ('Editorial review preview: chapter order and prose are regenerated from current source. '
        'Proof receipts and numerical evidence are reused unchanged from the archived edition; '
        'no fresh kernel, solver or release qualification is claimed. Not for publication.')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def title(line):
    return re.sub(r'\s*\{#[^}]+\}\s*$', '', line.removeprefix('# ')).strip()

def chapter_source(name, revision=None):
    relative = Path('book/chapters')/name if not name.startswith('../') else Path('contributions/continuum_reference/chapter.md')
    text = (ROOT/relative).read_text() if revision is None else subprocess.check_output(['git', 'show', f'{revision}:education/{relative}'], cwd=ROOT, text=True)
    if name.startswith('../'): text += '\n\n{{demo:continuum}}\n\n{{proof:compliance-denominator}}\n'
    return str(relative), text

def build(out):
    if out.exists(): raise FileExistsError(f'Choose a new output directory: {out}')
    delivery = json.loads((ARCHIVE.parent/'delivery-manifest.json').read_text())
    assert digest(ARCHIVE) == delivery['sha256'][ARCHIVE.name], 'Archive is not bound by the historical delivery manifest'
    with ZipFile(ARCHIVE) as archive:
        old_manifest = json.loads(archive.read('build-manifest.json'))
        historical_revision = old_manifest['git_revision']
        old_md = archive.read('kenoma-mechanics.md').decode()
        old_html = archive.read('index.html').decode()
        old_order = json.loads(subprocess.check_output(['git', 'show', f'{historical_revision}:education/book/book.json'], cwd=ROOT, text=True))['chapters']
        order = json.loads((ROOT/'book/book.json').read_text())
        assert sorted(order['chapters']) == sorted(old_order), 'This preview supports reordering existing chapters'
        # Keep useful assets/source evidence, omit historical release/layout passes.
        omitted = {'index.html', 'kenoma-mechanics.md', 'kenoma-mechanics.pdf', 'build-manifest.json',
                   'browser-check.json', 'artifact-check.json', 'pdf-render.json', 'mobile-startup-check.json'}
        for entry in archive.infolist():
            path = Path(entry.filename)
            assert not path.is_absolute() and '..' not in path.parts, 'Unsafe archive entry'
            if entry.is_dir() or path.parts[0] in {'qa', 'property-book-review'} or str(path) in omitted: continue
            target = out/path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(archive.read(entry))
    # Every reused formal receipt must bind to the exact current source/claim bytes.
    for filename in old_manifest['proof_families']:
        receipt = json.loads((out/filename).read_text())
        assert digest(ROOT/receipt['source']) == receipt['source_sha256'], filename
        claims_name = {'proof-status.json':'claims.json','transfer-proof-status.json':'anatomical-claims.json',
                       'coupled-proof-status.json':'coupled-claims.json','arm-proof-status.json':'arm-claims.json',
                       'property-proof-status.json':'property-claims.json'}[filename]
        assert digest(ROOT/'proofs'/claims_name) == receipt['claims_sha256'], filename
    headings = list(re.finditer(r'^# [^\n]+', old_md, re.M))
    sections = {title(h.group()): old_md[h.start():headings[i+1].start() if i+1<len(headings) else len(old_md)].strip() for i,h in enumerate(headings)}
    directive = re.compile(r'\{\{([\w:-]+)\}\}')
    cards = {key: card for card, key in re.findall(r'(<aside class="proof-card" id="proof-([\w-]+)".*?</aside>)', old_html, re.S)}
    expanded = {False: [], True: []}; inputs = {}
    for name in order['chapters']:
        relative, old = chapter_source(name, historical_revision)
        raw_old = subprocess.check_output(['git', 'show', f'{historical_revision}:education/{relative}'], cwd=ROOT)
        assert hashlib.sha256(raw_old).hexdigest() == old_manifest['input_sha256'][relative], relative
        _, current = chapter_source(name)
        inputs[relative] = digest(ROOT/relative)
        parts = directive.split(old.strip())
        pattern = ''.join(re.escape(p) if i%2==0 else '(.*?)' for i,p in enumerate(parts))
        match = re.fullmatch(pattern, sections[title(old.splitlines()[0])], re.S)
        assert match is not None, f'Archived chapter does not match canonical source: {name}'
        replacements = dict(zip(parts[1::2], match.groups()))
        for web in [False, True]:
            def replace(m):
                key = m[1]
                if key.startswith('demo:'): return lab_block(key.split(':')[1], web)
                if key.startswith('property:'): return property_block(key.split(':')[1], web)
                if key.startswith('proof:') and web: return cards[key.split(':')[1]]
                if key == 'evidence' and web: return (ROOT/'web/evidence.html').read_text()
                return replacements[key]
            expanded[web].append(directive.sub(replace, current).strip())
    appendices = old_md[old_md.index('# Checked source appendix:'):]
    front = old_md[:headings[0].start()]
    disclaimer = '\n> '+NOTE+'\n\n'
    (out/'kenoma-mechanics.md').write_text(front+disclaimer+'\n\n'.join(expanded[False])+'\n\n'+appendices)
    # Historical appendices remain intact and are identified as historical above.
    staging = out/'editorial-staging.md'; staging.write_text(front+disclaimer+'\n\n'.join(expanded[True])+'\n\n'+appendices)
    result = subprocess.run(['pandoc', str(staging), '--standalone', '--mathml', '--toc', '--toc-depth=2',
                             '--template', str(ROOT/'web/template.html'), '-o', str(out/'index.html')], capture_output=True, text=True, check=True)
    assert 'Could not convert TeX math' not in result.stderr, result.stderr
    staging.unlink()
    html = (out/'index.html').read_text()
    html = re.sub(r'<mrow>(<mo[^>]*>\[</mo>)(<mtable>.*?</mtable>)(<mo[^>]*>\]</mo>)</mrow>', r'<mrow class="matrix-fenced">\1\2\3</mrow>', html, flags=re.S)
    html = re.sub(r'<math display="block".*?</math>', lambda m:'<div class="equation" tabindex="0" aria-label="Scrollable displayed equation">'+m[0]+'</div>', html, flags=re.S)
    # Preserve the production print workaround for this inline matrix identity.
    def inline(m):
        formula = m[0]
        if '<annotation encoding="application/x-tex">M(u-y)=G^T\\ell</annotation>' not in formula: return formula
        return '<span class="print-safe-inline">'+formula+'<span class="print-inline-equation" role="math" aria-label="M times u minus y equals G transpose times ell"><i>M</i>(<i>u</i>−<i>y</i>) = <i>G</i><sup><i>T</i></sup>ℓ</span></span>'
    (out/'index.html').write_text(re.sub(r'<math display="inline".*?</math>', inline, html, flags=re.S))
    shutil.copy(ROOT/'web/style.css', out/'assets/style.css')
    shutil.copytree(ROOT/'web', out/'web', dirs_exist_ok=True)
    subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'web/app.mjs'),'--bundle','--minify','--format=esm','--target=es2022',f'--outfile={out/"assets/app.js"}','--legal-comments=external'], check=True)
    inputs['book/book.json'] = digest(ROOT/'book/book.json')
    inputs['tools/build_editorial_preview.py'] = digest(Path(__file__))
    for p in list((ROOT/'web').glob('*.mjs'))+[ROOT/'web/style.css',ROOT/'web/template.html',ROOT/'tools/build.py',ROOT/'tools/property_labs.py',ROOT/'tools/render_pdf.py',ROOT/'package-lock.json']:
        inputs[str(p.relative_to(ROOT))] = digest(p)
    manifest = {'kind':'editorial-review-only', 'scope':NOTE, 'historical_revision':historical_revision,
                'historical_archive_sha256':digest(ARCHIVE), 'source_base_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'chapters':order['chapters'], 'input_sha256':inputs,
                'outputs':{name:digest(out/name) for name in ['index.html','kenoma-mechanics.md','assets/app.js']}}
    (out/'editorial-preview-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Built editorial review edition at '+str(out))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out',type=Path)
    build(parser.parse_args().out.resolve())
