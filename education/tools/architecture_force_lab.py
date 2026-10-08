"""Assemble the preserved architecture-force lab; no solver or proof invocation.

The full book supplies its freshly checked family receipt. This adapter validates
source/claim bindings, adds static defaults and ships the exact contribution as
an archive. It never upgrades historical contribution evidence to book evidence.
"""
from pathlib import Path
import hashlib
import html
import json
import shutil
from check_real_lesson_proofs import BOOK_CLAIMS, BOOK_SOURCES

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = 'research/architecture-force-book-source.json'
SOURCE = 'proofs/ArchitectureForce.lean'
CLAIMS = 'proofs/architecture-force-real-claims.json'
RECEIPT = 'architecture-force-real-proof-status.json'
DEFAULT_ROWS = (
    ('Reference contractile area', '80.00 mm²'),
    ('Current projected area', '100.00 mm²'),
    ('Nominal stress P', '300.00 kPa'),
    ('Cauchy fibre stress σ', '240.00 kPa'),
    ('Axial force', '24.00 N'),
    ('Tendon-directed component', '20.78 N'),
)
DEFAULT_CAPTION = ('Authored default: geometric reference area 100 mm², contractile '
                   'fraction 0.80, fibre stretch 0.80, volume ratio 1.00 and '
                   'pennation 30°. The force–length multiplier is held at 1. '
                   'The tendon-directed component is rounded to two decimals.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_inventory(root=ROOT):
    root = Path(root)
    source = root / 'contributions/architecture-force'
    manifest = json.loads((root / SOURCE_MANIFEST).read_text())
    require(len(manifest['files']) == 13, 'Expected the preserved 13-file contribution')
    for name, expected in manifest['files'].items():
        require(Path(name).name == name, 'Contribution source must be a direct filename')
        require(digest(source / name) == expected, 'Contribution source changed: ' + name)
    require((root / SOURCE).read_bytes() == (source / 'ArchitectureForce.lean').read_bytes(),
            'Registered Lean source differs from preserved contribution')
    originals = json.loads((source / 'claims.json').read_text())['claims']
    registered = json.loads((root / CLAIMS).read_text())
    require(len(originals) == len(registered) == 6, 'Expected six architecture-force contracts')
    for original, claim in zip(originals, registered, strict=True):
        require(all(claim.get(key) == value for key, value in original.items()),
                'Original claim identity or boundary changed: ' + original['id'])
        require(bool(claim.get('assumptions')) and bool(claim.get('limitations')),
                'Missing displayed assumptions or limitations')
    return manifest, registered


def pdf_implementation_links(root=ROOT):
    """Use the already-public immutable source, not an unpublished book revision."""
    manifest, _ = source_inventory(root)
    path = 'contributions/architecture-force/model.mjs'
    return {path: 'https://github.com/MrScripty/Kenoma/blob/'
            + manifest['sourceBaseCommit'] + '/education/' + path}


def validate_receipt(receipt, root=ROOT):
    root = Path(root)
    manifest, claims = source_inventory(root)
    require(receipt.get('source') == SOURCE and receipt.get('source_sha256') == digest(root / SOURCE),
            'Architecture-force receipt source mismatch')
    require(receipt.get('claims_sha256') == digest(root / CLAIMS),
            'Architecture-force receipt claim-map mismatch')
    require(receipt.get('mathlib') == json.loads((root / 'proofs/mathlib-lock.json').read_text()),
            'Architecture-force receipt dependency mismatch')
    checked = receipt.get('claims', [])
    require(len(checked) == 6, 'Architecture-force receipt must contain six checked claims')
    for claim, actual in zip(claims, checked, strict=True):
        require(all(actual.get(key) == value for key, value in claim.items()),
                'Architecture-force receipt claim mismatch: ' + claim['id'])
        require(actual.get('status') == 'checked' and isinstance(actual.get('axioms'), list)
                and set(actual['axioms']) <= {'propext', 'Quot.sound', 'Classical.choice'},
                'Architecture-force receipt lacks allowed checked dependency report')
    return manifest


def default_table():
    rows = ''.join('<tr><th scope="row">'+html.escape(name)+'</th><td>'+html.escape(value)+'</td></tr>'
                   for name, value in DEFAULT_ROWS)
    return '<table><caption>Default material-cut case</caption><tbody>'+rows+'</tbody></table>'


def block(web):
    links = ('[Open the interactive architecture-force lab](architecture-force/index.html). '
             '[Primary-source ledger](architecture-force/sources.json) · '
             '[Preserved contribution source](contributions/architecture-force/README.md) · '
             '[Book source binding](architecture-force/registration.json).')
    if not web:
        rows = '| Quantity | Default value |\n|:--|--:|\n'
        rows += ''.join('| '+name+' | '+value+' |\n' for name, value in DEFAULT_ROWS)
        return '\n'+rows+'\n'+DEFAULT_CAPTION+'\n\n'+links+'\n'
    return ('\n<section class="architecture-force-reference" id="architecture-force-lab" '
            'aria-label="Architecture-force default reference">'+default_table()+'<p>'
            +html.escape(DEFAULT_CAPTION)+'</p><p><a href="architecture-force/index.html">'
            'Open the interactive architecture-force lab</a>. Change stretch, volume ratio, '
            'packing fraction and pennation separately, then enable the authored force–length '
            'curve and reset. The table remains readable in print and without JavaScript.</p>'
            '<p><a href="architecture-force/sources.json">Primary-source ledger</a> · '
            '<a href="contributions/architecture-force/README.md">Preserved contribution source</a> · '
            '<a href="architecture-force/registration.json">Book source binding</a></p></section>\n')


def assemble(out, receipt, root=ROOT):
    """Copy source bytes and add reading fallbacks after validating a supplied receipt.

    Does not compile or certify proofs: the caller owns fresh kernel execution.
    Unit tests exercise this with explicitly synthetic receipts only.
    """
    root, out = Path(root), Path(out)
    require(not out.resolve().is_relative_to(root.resolve()) or out.resolve() == (root / 'dist').resolve(),
            'Assembly output must be dist or outside the source tree')
    for name in ['registration.json', 'book-browser.json']:
        (out / 'architecture-force' / name).unlink(missing_ok=True)
    manifest = validate_receipt(receipt, root)
    require(json.loads((out / RECEIPT).read_text()) == receipt,
            'Supplied receipt differs from the delivered book receipt')
    source = root / 'contributions/architecture-force'
    lab, archive = out / 'architecture-force', out / 'contributions/architecture-force'
    lab.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)
    for name in manifest['files']:
        shutil.copyfile(source / name, archive / name)
    for name in ('style.css', 'lab.mjs', 'model.mjs', 'sources.json'):
        shutil.copyfile(source / name, lab / name)
    text = (source / 'index.html').read_text()
    readout = '<div id="readout" role="status" aria-live="polite"></div>'
    defaults = '<dl>'+''.join('<div><dt>'+html.escape(name)+'</dt><dd>'+html.escape(value)+'</dd></div>'
                             for name, value in DEFAULT_ROWS)+'</dl>'
    replacements = {
        readout: '<div id="readout" role="status" aria-live="polite">'+defaults+'</div>',
        '<p id="interpretation"></p>': '<p id="interpretation">Force–length is held at 1 to isolate the area/stress transformation.</p>',
        '<div id="composition"></div>': '<div id="composition">Total reference area 150.00 mm² · summed force 35.00 N · area-weighted nominal stress 233.33 kPa</div>',
        'href="chapter.md"': 'href="../index.html#architecture-to-force"',
        'href="README.md"': 'href="../contributions/architecture-force/README.md"',
        '</head>': '<style>.book-print-reference{display:none}@media print{#controls,#readout,#interpretation{display:none}.book-print-reference{display:block}main{padding:0}.book-print-reference table{width:100%;border-collapse:collapse}.book-print-reference th,.book-print-reference td{text-align:left;padding:4pt;border-bottom:1px solid #cededb}}</style></head>',
        '<main>': '<main><p><a href="../index.html#architecture-to-force">Return to the book lesson</a> · <a href="../contributions/architecture-force/index.html">Preserved standalone lab</a> · <a href="registration.json">Book source binding</a></p>',
        '<section aria-labelledby="series-title">': '<section class="book-print-reference">'+default_table()+'<p>'+html.escape(DEFAULT_CAPTION)+'</p></section>\n<section aria-labelledby="series-title">',
    }
    for old, new in replacements.items():
        require(text.count(old) == 1, 'Expected one lab assembly marker: ' + old)
        text = text.replace(old, new)
    (lab / 'index.html').write_text(text)
    shutil.copyfile(root / SOURCE_MANIFEST, lab / 'source-manifest.json')
    paths = [lab / name for name in ['index.html', 'style.css', 'lab.mjs', 'model.mjs', 'sources.json', 'source-manifest.json']]
    paths += [archive / name for name in manifest['files']]
    outputs = {str(path.relative_to(out)): digest(path) for path in sorted(paths)}
    registration = {
        'schema': 1, 'scope': 'Source-bound book assembly; no anatomical calibration or capstone acceptance.',
        'sourceBaseCommit': manifest['sourceBaseCommit'], 'sourceBaseTree': manifest['sourceBaseTree'],
        'qualifiedContributionCommit': manifest['qualifiedContributionCommit'],
        'priorQualificationRun': manifest['qualificationRun'],
        'priorQualificationScope': 'Original standalone contribution only, not this book assembly.',
        'registeredContracts': 6, 'bookTotal': BOOK_CLAIMS, 'bookSources': BOOK_SOURCES,
        'proofReceipt': '../'+RECEIPT,
        'proofReceiptSha256': digest(out / RECEIPT),
        'sourceSha256': receipt['source_sha256'], 'registeredClaimsSha256': receipt['claims_sha256'],
        'sourceManifestSha256': digest(root / SOURCE_MANIFEST),
        'assemblySourceSha256': digest(root / 'tools/architecture_force_lab.py'),
        'outputSha256': outputs, 'physicalLawsChanged': False,
    }
    (lab / 'registration.json').write_text(json.dumps(registration, indent=2)+'\n')
    return registration


def build():
    out = ROOT / 'dist'
    return assemble(out, json.loads((out / RECEIPT).read_text()))
