"""Read-only source closure and HTML/PDF checks for an actually built book.

Running this checker is not a build, proof invocation or browser-control test.
The full artifact gate also requires independent browser and print receipts.
"""
from pathlib import Path
from html.parser import HTMLParser
import json
import sys
from architecture_force_lab import (ROOT, SOURCE_MANIFEST, SOURCE, RECEIPT, DEFAULT_ROWS,
                                    digest, require, source_inventory, validate_receipt)
from check_real_lesson_proofs import BOOK_CLAIMS, BOOK_SOURCES


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.targets = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key, value in attrs if key in {'href', 'src'})


def check_assembly(out, root=ROOT):
    """Validate source/receipt/output bindings without executing lab code."""
    out, root = Path(out), Path(root)
    manifest, claims = source_inventory(root)
    receipt = json.loads((out / RECEIPT).read_text())
    validate_receipt(receipt, root)
    registration = json.loads((out / 'architecture-force/registration.json').read_text())
    require(registration['bookTotal'] == BOOK_CLAIMS and registration['bookSources'] == BOOK_SOURCES
            and registration['registeredContracts'] == 6, 'Architecture-force inventory mismatch')
    require(registration['sourceBaseCommit'] == manifest['sourceBaseCommit']
            and registration['sourceBaseTree'] == manifest['sourceBaseTree']
            and registration['qualifiedContributionCommit'] == manifest['qualifiedContributionCommit'],
            'Architecture-force provenance mismatch')
    for key, path in [('sourceSha256', root / SOURCE), ('registeredClaimsSha256', root / 'proofs/architecture-force-real-claims.json'),
                      ('proofReceiptSha256', out / RECEIPT), ('sourceManifestSha256', root / SOURCE_MANIFEST),
                      ('assemblySourceSha256', root / 'tools/architecture_force_lab.py')]:
        require(registration[key] == digest(path), 'Architecture-force binding mismatch: '+key)
    expected = {'architecture-force/'+name for name in ['index.html', 'lab.mjs', 'model.mjs', 'style.css', 'sources.json', 'source-manifest.json']}
    expected |= {'contributions/architecture-force/'+name for name in manifest['files']}
    require(set(registration['outputSha256']) == expected, 'Incomplete architecture-force source closure')
    for relative, value in registration['outputSha256'].items():
        require(digest(out / relative) == value, 'Changed architecture-force output: '+relative)
    for name, value in manifest['files'].items():
        require(digest(out / 'contributions/architecture-force' / name) == value,
                'Changed architecture-force archive: '+name)
    for name in ['lab.mjs', 'model.mjs', 'style.css', 'sources.json']:
        require(digest(out / 'architecture-force' / name) == manifest['files'][name],
                'Changed architecture-force runtime/source: '+name)
    require((out / 'architecture-force/source-manifest.json').read_bytes() == (root / SOURCE_MANIFEST).read_bytes(),
            'Delivered architecture-force source manifest differs')
    text = (out / 'architecture-force/index.html').read_text()
    for label, value in DEFAULT_ROWS:
        require('<dt>'+label+'</dt><dd>'+value+'</dd>' in text,
                'Missing architecture-force no-JavaScript default: '+label)
        require('<th scope="row">'+label+'</th><td>'+value+'</td>' in text,
                'Missing architecture-force print default: '+label)
    for folder in ['architecture-force', 'contributions/architecture-force']:
        for href in Links((out / folder / 'index.html').read_text()).targets:
            require(not href.startswith(('http:', 'https:', '//', '/')), 'Nonlocal lab asset/link: '+href)
            require((out / folder / href.split('#')[0]).is_file(), 'Broken architecture-force local link: '+href)
    return registration, claims


def check(out=None):
    from check_print_readability import HTMLTree, PDFText, normalized
    import fitz
    out = Path(out) if out is not None else ROOT / 'dist'
    registration, claims = check_assembly(out)
    browser = json.loads((out / 'architecture-force/book-browser.json').read_text())
    require(browser['status'] == 'PASS_ARCHITECTURE_FORCE_BOOK_CONTROLS'
            and browser['bookProofs'] == BOOK_CLAIMS, 'Missing architecture-force book control qualification')
    require(browser['checkerSha256'] == digest(ROOT / 'tests/architecture_force_book_browser.py')
            and browser['controlOracleSha256'] == digest(ROOT / 'tests/architecture_force_browser.py'),
            'Stale architecture-force browser checker binding')
    expected_inputs = {'index.html', 'build-manifest.json', RECEIPT,
                       'architecture-force/registration.json', 'architecture-force/index.html'}
    require(set(browser['inputSha256']) == expected_inputs, 'Incomplete architecture-force browser bindings')
    for name, value in browser['inputSha256'].items():
        require(digest(out / name) == value, 'Stale architecture-force browser input: '+name)
    require(len(browser['views']) == 3 and {v['name'] for v in browser['views']} == {'desktop', 'mobile', 'no-javascript'}
            and all(v['entry_defaults_links_print_and_controls'] and not v['errors'] for v in browser['views']),
            'Incomplete architecture-force browser views')
    expected_captures = {'architecture-force/qa/'+name+'.jpg' for name in
                         ['desktop-default', 'desktop-force-length', 'mobile-default', 'mobile-force-length', 'no-javascript-default']}
    require(set(browser['captureSha256']) == expected_captures, 'Incomplete architecture-force capture inventory')
    for name, value in browser['captureSha256'].items():
        require(digest(out / name) == value, 'Changed architecture-force capture: '+name)
    nodes = list(HTMLTree((out / 'index.html').read_text()).root.nodes())
    for ident in ['architecture-to-force', 'architecture-force-evidence', 'architecture-force-lab']:
        require(sum(n.attrs.get('id') == ident for n in nodes) == 1, 'Missing/duplicate book anchor: '+ident)
    for claim in claims:
        require(sum(n.attrs.get('id') == 'proof-'+claim['id'] for n in nodes) == 1,
                'Missing/duplicate architecture-force proof card: '+claim['id'])
    reference = next(n for n in nodes if n.attrs.get('id') == 'architecture-force-lab')
    for label, value in DEFAULT_ROWS:
        require(normalized(label+value) in normalized(reference.text()), 'Missing book static default: '+label)
    with fitz.open(out / 'kenoma-mechanics.pdf') as doc:
        pdf = PDFText(doc)
        title = 'Connect fibre architecture to force without inventing strength'
        following = 'Let material stiffness and boundaries choose the lateral shape'
        bounds = next((b for b in pdf.bounded(title, following)
                       if all(normalized(label+value) in pdf.text[b[0]:b[1]] for label, value in DEFAULT_ROWS)), None)
        require(bounds is not None, 'Architecture-force chapter/defaults missing in PDF')
        for label, value in DEFAULT_ROWS:
            pdf.target('architecture-force-default:'+label, label+value, *bounds, prose=True)
        source = (ROOT / SOURCE).read_text()
        require(any(list(pdf.occurrences(source, *b)) for b in
                    pdf.bounded('Checked source appendix: ArchitectureForce', 'Proof check receipt')),
                'Architecture-force complete source missing in PDF')
    print('PASS: architecture-force source closure and actual book HTML/PDF defaults')
    return registration


if __name__ == '__main__':
    check(sys.argv[1] if len(sys.argv) > 1 else None)
