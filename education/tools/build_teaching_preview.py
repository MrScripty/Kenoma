"""Build an explicitly unqualified reading preview from the pinned publication.

Missing immutable Git objects are fetched from the official Kenoma repository.
No new datasets, proof compilation, physical campaigns, or publication occur.
"""
from pathlib import Path
import argparse, hashlib, html, json, re, shutil, subprocess
from chapter_examples import inventory as examples, package as package_examples
from teaching_sequences import block, inventory
from executable_outputs import executable_outputs
from preserved_publication import DEFAULT_CACHE, preserved_book

ROOT = Path(__file__).resolve().parents[1]
PINNED_BUILD = '415d3d15c6f9644660bd2dd3983367bb30548188080ab0fbf7de45c4b7ed6d02'
NOTE = ('Review preview · Worked readings and layout are new. Proof receipts, recorded results '
        'and the linked PDF are preserved evidence; no fresh full-book qualification is claimed.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(preserved, out, provenance=None):
    if out.exists():
        raise FileExistsError('Choose a new preview directory: ' + str(out))
    if digest(preserved / 'build-manifest.json') != PINNED_BUILD:
        raise ValueError('Expected the pinned preserved publication build')
    original = json.loads((preserved / 'build-manifest.json').read_text())
    # Prose, citations and formal claims are copied only while source-identical.
    for name, expected in original['input_sha256'].items():
        if name.startswith(('proofs/', 'book/chapters/')) and digest(ROOT / name) != expected:
            raise ValueError('Preserved book no longer matches source: ' + name)
    for name, expected in original['executable_outputs'].items():
        if digest(preserved / name) != expected:
            raise ValueError('Preserved executable differs: ' + name)
    # The unchanged independent poser binary is reused, not freshly built.
    for name, expected in original['chapter_examples']['gui_inputs'].items():
        if '/pkg/' in name:
            continue
        if digest(ROOT.parent / name) != expected:
            raise ValueError('Preserved poser no longer matches source: ' + name)
    expected_wasm = original['chapter_examples']['wasm_sha256']
    if digest(preserved / 'gui/simple-graph/pkg/human_wasm_bg.wasm') != expected_wasm:
        raise ValueError('Preserved poser WASM differs')
    inventory()
    shutil.copytree(preserved, out)
    # A preview must not masquerade as a release artifact or reuse a browser pass.
    for name in ['build-manifest.json', 'browser-check.json', 'artifact-check.json',
                 'pdf-render.json', 'mobile-startup-check.json', 'chapter-example-check.json']:
        path = out / name
        if path.exists():
            target = out / 'preserved-evidence' / name
            target.parent.mkdir(exist_ok=True)
            path.rename(target)
    old = (preserved / 'index.html').read_text()
    body = re.search(r'<main id="book-content">(.*?)</main>', old, re.S).group(1)
    toc = re.search(r'<nav class="toc"[^>]*>.*?(<ul>.*?)</nav>', old, re.S).group(1)
    for example in examples():
        pattern = r'(<h1\b[^>]*\bid="' + re.escape(example['anchor']) + r'"[^>]*>.*?</h1>)'
        body, count = re.subn(pattern, lambda m: m[1] + block(example['id']), body, count=1, flags=re.S)
        if count != 1:
            raise ValueError('Missing canonical chapter heading: ' + example['id'])
    book = json.loads((ROOT / 'book/book.json').read_text())
    page = (ROOT / 'web/template.html').read_text()
    for token, value in {'title': html.escape(book['title']), 'subtitle': html.escape(book['subtitle']), 'toc': toc, 'body': body}.items():
        page = page.replace('$' + token + '$', value)
    page = page.replace('</head>', '<link rel="stylesheet" href="assets/dissipative-lab.css"><link rel="stylesheet" href="assets/serial-lab.css"></head>')
    page = page.replace('<body>', '<body><p class="preview-notice">' + html.escape(NOTE) + '</p>')
    page = page.replace('>Illustrated PDF</a>', '>Preserved PDF (before this change)</a>')
    (out / 'index.html').write_text(page)
    markdown = (preserved / 'kenoma-mechanics.md').read_text()
    for example in examples():
        # The canonical heading is kept by Pandoc's source-book output.
        heading = (ROOT / 'book/chapters' / example['chapter']).read_text().splitlines()[0]
        if heading not in markdown:
            raise ValueError('Missing Markdown chapter: ' + example['id'])
        markdown = markdown.replace(heading, heading + block(example['id'], False), 1)
    (out / 'kenoma-mechanics.md').write_text('> ' + NOTE + '\n\n' + markdown)
    shutil.copy(ROOT / 'web/style.css', out / 'assets/style.css')
    shutil.copytree(ROOT / 'web', out / 'web', dirs_exist_ok=True)
    receipt = package_examples(out, preserved_poser=preserved / 'gui/simple-graph/pkg')
    inputs = {str(path.relative_to(ROOT)): digest(path) for folder in ['web', 'book/examples']
              for path in sorted((ROOT / folder).rglob('*')) if path.is_file()}
    for name in ['tools/build_teaching_preview.py', 'tools/preserved_publication.py', 'tools/teaching_sequences.py', 'tools/chapter_examples.py', 'tools/build.py']:
        inputs[name] = digest(ROOT / name)
    receipt = {'kind': 'research-book-teaching-preview', 'qualification': NOTE,
               'source_base_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'preserved_publication': provenance,
               'preserved_build_sha256': PINNED_BUILD, 'preserved_poser_wasm_sha256': expected_wasm,
               'input_sha256': inputs, 'teaching': receipt['teaching'],
               'teaching_sha256': digest(out / 'teaching-sequences.json'),
               'executable_outputs': executable_outputs(out)}
    (out / 'teaching-preview-manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'out': str(out), 'teaching': receipt['teaching'], 'qualification': NOTE}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preserved', type=Path, help='Use an already verified local publication instead of reconstructing it')
    parser.add_argument('--cache', type=Path, default=DEFAULT_CACHE, help='Ignored/external staging and immutable Git-object cache')
    parser.add_argument('--offline', action='store_true', help='Require pinned Git objects locally; never fetch')
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    if args.out.exists():
        parser.error('Choose a new preview directory: ' + str(args.out))
    if not (ROOT / 'node_modules/.bin/esbuild').is_file():
        parser.error('Install the locked preview dependencies first: cd education && npm ci')
    if args.preserved:
        build(args.preserved.resolve(), args.out.resolve())
    else:
        with preserved_book(args.cache, args.offline) as (preserved, provenance):
            build(preserved, args.out.resolve(), provenance)
