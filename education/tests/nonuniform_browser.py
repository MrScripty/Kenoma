"""Exercise the book's real entry point and bundled accepted local-volume controls."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys
import fitz
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from render_pdf import serve
from executable_outputs import checked_build_outputs, unchanged_outputs

out = ROOT / 'dist'
lab = out / 'nonuniform'
before = checked_build_outputs(out)
registration = json.loads((lab / 'registration.json').read_text())
assert registration['acceptedSource'] == '15c624c32378b9c773a3d0c25a65150804b68c90'
assert registration['bookTotal'] == 109 and registration['registeredContracts'] == 6
assert registration['outputSha256'] == hashlib.sha256((lab / 'nonuniform-volume-lab.html').read_bytes()).hexdigest()
assembly = json.loads((lab / 'build-receipt.json').read_text())
assert assembly['output']['sha256'] == registration['outputSha256']
assert assembly['proofReceiptSha256'] == hashlib.sha256((lab / 'nonuniform-proof-status.json').read_bytes()).hexdigest()
assert assembly['formalProofRegistration'] == 'REGISTERED_IN_SEPARATE_ACCEPTED_BOOK_CANDIDATE'
subprocess.run(['python3', str(ROOT / 'contributions/nonuniform-isochoric-kinematics/browser.py'), str(lab)], check=True)
server, url = serve()
views = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium'))
        for name, width in [('desktop',1200), ('mobile',390), ('narrow',320)]:
            page = browser.new_page(viewport={'width':width,'height':1000})
            errors = [];page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(url + '/index.html', wait_until='networkidle')
            assert page.locator('.proof-card').count() == 109
            for item in ['nonuniform-local-volume','nonuniform-evidence-boundaries']:
                expect(page.locator('#'+item)).to_have_count(1)
            entry = page.get_by_role('link', name='Open the interactive local-volume lab', exact=True)
            entry.click();page.wait_for_load_state('networkidle')
            assert page.url == url + '/nonuniform/nonuniform-volume-lab.html'
            assert page.locator('.real-contract').count() == 6
            assert 'giving 109 checked declarations' in page.locator('#real-contracts').inner_text()
            assert 'acceptance is pending' not in page.locator('body').inner_text()
            state = lambda:page.evaluate('KinematicLab.state()')
            page.locator('#compensate').uncheck()
            s=state();assert abs(s['continuumVolumeRatio']-1)<1e-12 and s['pointwiseJRange']==[.6,1.4]
            page.locator('#reset').click()
            expect(page.locator('#compensate')).to_be_checked()
            assert all(abs(j-1)<1e-12 for j in state()['pointwiseJRange'])
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            for name2 in ['composition.json','acceptance-note.md']:
                assert page.request.get(url+'/nonuniform/'+name2).status==200
            assert not errors, errors
            views.append({'name':name,'width':width,'entryAndControlsPassed':True,'errors':errors})
            page.close()
        browser.close()
finally:
    server.shutdown();server.server_close()
with fitz.open(out/'kenoma-mechanics.pdf') as doc:
    flat=''.join(''.join(page.get_text().split()) for page in doc)
    assert 'Unevenstretchandlocalvolume' in flat
    assert registration['acceptedSource'] in flat
    source=(ROOT/'proofs/NonuniformIsochoric.lean').read_text()
    assert ''.join(source.split()) in flat
    for page in doc:
        for link in page.get_links():
            uri=link.get('uri','');assert '127.0.0.1' not in uri and 'localhost' not in uri, uri
    pages=len(doc)
unchanged_outputs(out,before)
result={'result':'PASS_ACCEPTED_NONUNIFORM_BOOK_ENTRY_CONTROLS_SOURCE_PDF_AND_PORTABLE_LINKS','candidateRevision':registration['candidateRevision'],'acceptedSource':registration['acceptedSource'],'bookProofs':109,'views':views,'pdfPages':pages,'standaloneBrowserReceiptSha256':hashlib.sha256((lab/'browser-receipt.json').read_bytes()).hexdigest(),'physicalLawsChanged':False,'authorCampaignInvocations':0}
(lab/'book-integration-browser.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
