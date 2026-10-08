"""Register an independently accepted bounded lab without altering its source laws."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import hashlib, html, json, os, shutil, subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED = '15c624c32378b9c773a3d0c25a65150804b68c90'

def build():
    source = ROOT / 'contributions/nonuniform-isochoric-kinematics'
    out = ROOT / 'dist/nonuniform'
    out.mkdir(parents=True, exist_ok=True)
    composition = json.loads((ROOT / 'review/nonuniform-volume-acceptance/composition.json').read_text())
    assert composition['standaloneAccepted'] == ACCEPTED
    assert composition['totalCandidateProofs'] == 109
    for name, digest in composition['acceptedSourceFiles'].items():
        assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest, name
    assert (ROOT / 'proofs/NonuniformIsochoric.lean').read_bytes() == (source / 'NonuniformIsochoric.lean').read_bytes()
    standalone = json.loads((source / 'claims.json').read_text())
    registered = json.loads((ROOT / 'proofs/nonuniform-real-claims.json').read_text())
    for original, book in zip(standalone, registered, strict=True):
        assert all(book[key] == value for key, value in original.items())
        assert book['claim'] == original['statement']
    receipt = json.loads((ROOT / 'dist/nonuniform-real-proof-status.json').read_text())
    assert receipt['source_sha256'] == hashlib.sha256((source / 'NonuniformIsochoric.lean').read_bytes()).hexdigest()
    assert len(receipt['claims']) == 6 and all(c['status'] == 'checked' for c in receipt['claims'])
    commands = [
        ['python3', 'model_audit.py', '--output', str(out / 'audit')],
        ['python3', 'check_proofs.py', '--mathlib', str(ROOT / '.tools/mathlib4'), '--lean-bin', str(ROOT / '.tools/lean-4.19.0-linux/bin'), '--output', str(out / 'proof-check')],
        ['python3', 'build.py', '--output', str(out), '--proof-receipt', str(out / 'proof-check/nonuniform-proof-status.json'), '--model-audit', str(out / 'audit/model-audit.json')],
    ]
    for command in commands:
        subprocess.run(command, cwd=source, check=True)
    target = out / 'nonuniform-volume-lab.html'
    text = target.read_text()
    replacements = {
        'The existing book remains at 103 claims; this extension is not registered pending independent acceptance.': 'This accepted extension adds six scoped contracts to the original 103, giving 109 checked declarations in the book candidate.',
        'Independent peer acceptance is pending.': 'Independent peer acceptance applies to exact source ' + ACCEPTED + '; this candidate preserves its mathematical and model source bytes.',
        'Separate property-lab review candidate. Existing research-book sources and 103 proof identities are unchanged. Six scoped Real contracts are compiled for this standalone extension; book registration requires independent acceptance.': 'Accepted property lab in a separate research-book candidate. Original 103 proof identities are preserved; six scoped Real contracts bring the candidate to 109. Source ' + ACCEPTED + '.',
    }
    for old, new in replacements.items():
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    assert text.count('<footer>') == 1
    text = text.replace('<footer>', '<footer style="overflow-wrap:anywhere">', 1)
    target.write_text(text)
    # Retain the original checker output under proof-check; annotate only the
    # assembled download and rebind the assembly receipt to the actual HTML.
    download = out / 'nonuniform-proof-status.json'
    payload = json.loads(download.read_text())
    payload.update(bookRegistration='REGISTERED_IN_SEPARATE_ACCEPTED_BOOK_CANDIDATE', bookTotal=109, independentlyAcceptedSource=ACCEPTED)
    download.write_text(json.dumps(payload, indent=2)+'\n')
    assembly = json.loads((out / 'build-receipt.json').read_text())
    assembly.update(formalProofRegistration='REGISTERED_IN_SEPARATE_ACCEPTED_BOOK_CANDIDATE', bookTotal=109, independentlyAcceptedSource=ACCEPTED, originalCheckerReceipt='proof-check/nonuniform-proof-status.json')
    assembly['proofReceiptSha256'] = hashlib.sha256(download.read_bytes()).hexdigest()
    assembly['output']['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    assembly['output']['bytes'] = target.stat().st_size
    (out / 'build-receipt.json').write_text(json.dumps(assembly, indent=2)+'\n')
    for name in ['acceptance-note.md', 'composition.json']:
        shutil.copyfile(ROOT / 'review/nonuniform-volume-acceptance' / name, out / name)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = ThreadingHTTPServer(('127.0.0.1',0), partial(Quiet,directory=str(out)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
            page = browser.new_page(viewport={'width':1200, 'height':1000})
            page.goto(f'http://127.0.0.1:{server.server_port}/nonuniform-volume-lab.html', wait_until='networkidle')
            assert page.locator('.real-contract').count() == 6
            figure = page.locator('#shape').evaluate('(svg)=>svg.outerHTML')
            browser.close()
    finally:
        server.shutdown();server.server_close()
    figure = figure.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    # The same accepted SVG includes inherited style rules; preserve readable
    # text explicitly for the standalone image used by Markdown and PDF.
    figure = figure.replace('>', '><style>text{font:23px sans-serif;fill:#193438}</style>', 1)
    assets = ROOT / 'dist/assets';assets.mkdir(exist_ok=True)
    (assets / 'nonuniform-volume.svg').write_text(figure)
    manifest = {'acceptedSource':ACCEPTED, 'candidateRevision':subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(), 'registeredContracts':6, 'bookTotal':109, 'sourceSha256':receipt['source_sha256'], 'standaloneClaimsSha256':hashlib.sha256((source / 'claims.json').read_bytes()).hexdigest(), 'registeredClaimsSha256':receipt['claims_sha256'], 'outputSha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'assemblyReplacements':replacements, 'physicalLawsChanged':False}
    (out / 'registration.json').write_text(json.dumps(manifest, indent=2)+'\n')

def block(web):
    caption = 'Default prescribed geometry: m = 1, a = 0.4, 32 axial cells, 16 polygon sides and local radial compensation. Teal strips share the full mesh vertices. Fixed scale: 4 SVG units/mm; reference length 120 mm, circumradius 15 mm.'
    link = 'nonuniform/nonuniform-volume-lab.html'
    if not web:
        return '\n![Longitudinal section of prescribed uneven stretch at a fixed millimetre scale](assets/nonuniform-volume.svg)\n\n'+caption+'\n\n[Open the portable interactive local-volume lab]('+link+'). Change mean stretch, uneven-stretch amplitude, mesh cells and local compensation; reset returns to the declared reference.\n'
    return '\n<figure class="nonuniform-reference"><img src="assets/nonuniform-volume.svg" alt="Longitudinal section of prescribed uneven stretch at a fixed millimetre scale"><figcaption>'+html.escape(caption)+'</figcaption></figure><p><a href="'+link+'">Open the interactive local-volume lab</a>. Change mean stretch, uneven-stretch amplitude, mesh cells and local compensation; reset returns to the declared reference. The full six-contract inventory, complete Lean source and independent audit downloads are bundled with the lab.</p>\n'
