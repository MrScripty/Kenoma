"""Qualify static URL closure and explicitly permitted elementary/read-only UI.

No historical computational opt-in route or worker is launched. No public URL
request is made; all browser requests are confined to the local candidate.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from threading import Thread
from urllib.parse import unquote, urlsplit

import fitz
from playwright.sync_api import sync_playwright
from preserve_legacy_pages import no_symlinks, sha, link_closure, git, PUBLISHED
from clean_reading_edition import PRIVATE, COORDINATION, TEXT_EXT
from source_first_reading import browser_path


RUNTIME_URLS = {
    'index.html': ['assets/app.js', 'assets/app.js.LEGAL.txt', 'assets/functional-reader-boot.mjs',
        'data/elbow-v1/data/bodyparts3d_right_arm_m.json', 'data/elbow-v1/data/openarm_s2_1b_0p5s_bins.json'],
    'anatomy-inspection/index.html': ['inspect.js', 'atlas.json', 'geometry.json', 'attachments.json',
        'proof-status.json', 'AnatomicalTransfer.lean', 'lean-check.txt'],
    'coupled-fixture/index.html': ['inspect.js', 'worker.js', 'proof-status.json', 'CoupledMechanics.lean', 'lean-check.txt', 'experiment.json'],
    'anatomical-arm/index.html': ['inspect.js', 'worker.js', 'geometry.json', 'attachments.json', 'matches.json',
        'routes.json', 'rest.json', 'proof-status.json', 'AnatomicalArm.lean', 'lean-check.txt'],
}
HELD = ['lab-series', 'lab-property-material', 'lab-serial-specimen', 'lab-spatial', 'lab-continuum']


def privacy(root, construction):
    exceptions = construction['privacy_literal_exceptions']; observed = {}
    for path in sorted(root.rglob('*')):
        if not path.is_file(): continue
        name = str(path.relative_to(root))
        if path.suffix in TEXT_EXT: text = path.read_text()
        elif path.suffix == '.pdf':
            with fitz.open(path) as pdf:
                text = '\n'.join(page.get_text() for page in pdf)+'\n'+json.dumps(pdf.metadata)
                if any(PRIVATE.search(link.get('uri', '')) for page in pdf for link in page.get_links()):
                    raise ValueError('Private PDF URL: '+name)
        else: continue
        hits = sorted(set(match.group(0) for match in PRIVATE.finditer(text)))
        if COORDINATION.search(text): raise ValueError('Public coordination metadata: '+name)
        if hits:
            expected = exceptions.get(name)
            if not expected or sha(path.read_bytes()) != expected['sha256'] or hits != expected['allowed_literals']:
                raise ValueError('Unapproved public environment-path metadata: '+name)
            observed[name] = expected['sha256']
    if set(observed) != set(exceptions): raise ValueError('Inherited code-literal exception changed')
    return observed


def source_checks(root, private, m):
    construction = json.loads((private/'construction.json').read_text())
    for name, f in construction['protected_public_files'].items():
        if sha((root/name).read_bytes()) != f['sha256']: raise ValueError('Protected public bytes changed: '+name)
    count = 0
    for name, f in m['historical_inventory']['files'].items():
        if f['git']:
            if sha((private/'original-records'/name).read_bytes()) != f['sha256']: raise ValueError('Original archived evidence changed: '+name)
            count += 1
    if count != 971: raise ValueError('Original record archive incomplete')
    raw = (private/'original-records/kenoma-mechanics.md').read_text()
    clean = (root/'kenoma-mechanics.md').read_text()
    if re.findall(r'\d+(?:\.\d+)?', raw) != re.findall(r'\d+(?:\.\d+)?', clean): raise ValueError('Historical Markdown numeric content changed')
    for name in m['unavailable_review_paths']:
        if (root/name).exists(): raise ValueError('Unavailable review evidence unexpectedly fabricated')
    return construction, count


def dependency_closure(root, construction):
    count = 0
    for entry, urls in RUNTIME_URLS.items():
        for url in urls:
            target = (root/entry).parent/url
            if not target.is_file(): raise ValueError('Missing runtime/download dependency: '+entry+' -> '+url)
            count += 1
    for filename in ['assets/functional-reader-boot.mjs', 'assets/archive-inspector-boot.mjs']:
        text = (root/filename).read_text()
        if filename.endswith('functional-reader-boot.mjs') and "import('./app.js')" not in text: raise ValueError('Root dynamic import changed')
        if filename.endswith('archive-inspector-boot.mjs') and "configuration.dataset.archiveEntry !== 'inspect.js'" not in text: raise ValueError('Inspector import guard changed')
    graphs = construction['static']['bundle_graphs']
    if len(graphs) != 6: raise ValueError('Missing six-bundle dependency evidence')
    for graph in graphs.values():
        for emitted in graph['outputs'].values():
            if any(item.get('external') for item in emitted.get('imports', [])): raise ValueError('Unbundled runtime import')
    return count


def control(page, selector, value):
    field = page.locator(selector)
    if field.get_attribute('type') == 'range': field.evaluate('(element,value)=>{element.value=value}', str(value))
    else: field.fill(str(value))
    field.dispatch_event('input')


def snapshot(page, section):
    section.locator('[data-action="copy"]').click()
    return json.loads(section.locator('textarea.preset').input_value())


def qualify(root, private, m, manifest):
    no_symlinks(root)
    construction, archived = source_checks(root, private, m)
    runtime = dependency_closure(root, construction)
    q = private/'qualification'; q.mkdir()
    class Mount(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
        def translate_path(self, path):
            prefix = '/Kenoma/'
            if not path.startswith(prefix): return '/nonexistent-functional-reader'
            target = (root/unquote(urlsplit(path).path[len(prefix):])).resolve()
            return str(target) if target.is_relative_to(root) else '/nonexistent-functional-reader'
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Mount, directory=str(root)))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/Kenoma/'
    errors = []; requests = []; controls = []; workers = []; http_failures = []
    try:
        # Resolve managed Chromium before entering Playwright's sync context.
        browser_executable = browser_path()
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=browser_executable,
                args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
            context = browser.new_context(accept_downloads=True)
            def route(request):
                if not request.request.url.startswith(base) and not request.request.url.startswith('blob:'):
                    errors.append('Unexpected network resource'); request.abort()
                else: request.continue_()
            context.route('**/*', route)
            def watch(page):
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: requests.append(request.url.removeprefix(base)))
                page.on('worker', lambda worker: workers.append(worker.url))
                page.on('response', lambda response: http_failures.append({'url': response.url.removeprefix(base), 'status': response.status})
                    if response.status >= 400 and urlsplit(response.url).path != '/favicon.ico' else None)
            # Persist the fixed, token-preserving print alternate in the served
            # page. Screen MathML remains intact; the pinned CSS selects the
            # alternate only for print. Qualify the resulting actual file.
            print_context = browser.new_context(java_script_enabled=False, viewport={'width': 658, 'height': 1123})
            print_context.route('**/*', route)
            print_page = print_context.new_page(); watch(print_page)
            print_page.goto(base, wait_until='networkidle'); print_page.emulate_media(media='print')
            print_page.evaluate('document.fonts.ready')
            reflow_path = 'education/tools/print_layout.js'
            reflow_source = git('show', PUBLISHED+':'+reflow_path)
            print_layout = print_page.evaluate(reflow_source.decode())
            before_print = sha((root/'index.html').read_bytes())
            (root/'index.html').write_text(print_page.content())
            print_derivative = {'before_sha256': before_print, 'after_sha256': sha((root/'index.html').read_bytes()),
                'kind': 'PERSISTED_PRINT_ALTERNATE_ORIGINAL_SCREEN_MATHML_RETAINED'}
            print_context.close()
            exceptions = privacy(root, construction)
            links = link_closure(root)
            page = context.new_page(); watch(page)
            page.goto(base, wait_until='networkidle'); page.wait_for_selector('html[data-elementary-controls="ready"]')
            assert page.locator('.proof-card').count() == 103
            assert page.locator('[data-demo="series"],[data-material],[data-serial],[data-advanced]').count() == 0
            for id in HELD:
                section = page.locator('#'+id)
                assert section.locator('input,select,button').evaluate_all('(xs)=>xs.every(x=>x.disabled)')
                assert section.locator('.archive-runtime-note a').count() == 1
            controls.append('production root gate prevents all five archived solver initializers on default load')
            force = page.locator('#lab-force')
            control(page, '#force-time-number', 1); one = snapshot(page, force)
            position = lambda: force.locator('.readout>div').filter(has=page.locator('dt', has_text=re.compile('^Position$'))).locator('dd').inner_text()
            assert position() == '1.000 m' and one['parameters']['time'] == 1
            control(page, '#force-mass-number', 4); control(page, '#force-time-number', 1)
            half = snapshot(page, force); assert position() == '0.500 m' and half['parameters']['mass'] == 4
            control(page, '#force-mass-number', ''); rejected = snapshot(page, force)
            assert rejected['parameters'] == half['parameters']
            force.locator('[data-action="reset"]').click(); assert snapshot(page, force)['parameters']['mass'] == 2
            controls.append('constant-force controls change actual position; blank rollback and reset')
            torque = page.locator('#lab-torque')
            assert '-14.715' in torque.locator('.readout').inner_text()
            control(page, '#torque-angle-number', 90)
            assert '-14.715' not in torque.locator('.readout').inner_text()
            torque.locator('[data-action="reset"]').click(); assert '-14.715' in torque.locator('.readout').inner_text()
            controls.append('lever rotation changes displayed torque; reset restores default')
            energy = page.locator('#lab-energy')
            energy.locator('[data-action="step"]').click(); state = snapshot(page, energy)
            assert state['step'] == 1 and abs(state['state']['x']-.1968) < 1e-10
            with page.expect_download() as downloaded: energy.locator('[data-action="export"]').click()
            downloaded.value.save_as(q/'elementary-energy-trace.json')
            trace = json.loads((q/'elementary-energy-trace.json').read_text())
            assert len(trace['trace']) == 2 and trace['trace'][-1]['step'] == 1
            energy.locator('[data-action="reset"]').click(); assert snapshot(page, energy)['step'] == 0
            controls.append('one elementary spring step and actual two-row export; reset')
            elbow = page.locator('#lab-elbow'); before = elbow.locator('.readout').inner_text()
            control(page, '#elbow-load-number', 2); assert elbow.locator('.readout').inner_text() != before
            elbow.locator('[data-action="reset"]').click(); assert elbow.locator('.readout').inner_text() == before
            controls.append('schematic hinge load changes readout without time stepping')
            for id in ['deformation', 'isochoric', 'tapered']:
                section = page.locator('#lab-property-'+id)
                assert section.locator('.readout').inner_text()
                before = section.locator('.readout').inner_text()
                field = section.locator('input[type="number"]').first
                field.fill(str(float(field.input_value())+.01)); field.dispatch_event('input')
                assert section.locator('.readout').inner_text() != before
                section.locator('[data-action="reset"]').click(); assert section.locator('.readout').inner_text() == before
                state = snapshot(page, section); assert state
            controls.append('three prescribed-geometry controls, actual copied state and reset')
            sls = page.locator('#lab-dissipative-bar'); before = sls.locator('.readout').inner_text()
            sls.locator('[data-action="reset"]').click(); sls.locator('[data-action="summary"]').click()
            assert sls.locator('.readout').inner_text() == before
            assert snapshot(page, sls)
            controls.append('closed-form SLS default, read summary and actual trace copy; no protocol run')
            evidence = page.locator('#evidence-viewer'); control(page, '#evidence-viewer [data-evidence="bin"]', 1)
            assert '2 /' in evidence.locator('.readout').inner_text()
            evidence.locator('[data-action="reset"]').click(); assert '1 /' in evidence.locator('.readout').inner_text()
            controls.append('recorded-data bin and reset; no mechanical inference')
            for width in [1280, 393, 320]:
                page.set_viewport_size({'width': width, 'height': 900})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), ('root', width)
                page.screenshot(path=str(q/f'root-{width}.jpg'), type='jpeg', quality=85)
            for entry in ['anatomical-arm', 'coupled-fixture']:
                page.goto(base+entry+'/', wait_until='networkidle')
                assert page.locator('#launch-archive-runtime').is_enabled()
                assert 'has not started' in page.locator('#archive-runtime-status').inner_text()
                assert not page.evaluate('Boolean(window.anatomicalArmReady||window.coupledReady)')
                assert not any(entry+'/inspect.js' in url or entry+'/worker.js' in url for url in requests)
            controls.append('both computational inspector pages remain static until explicit launch')
            page.goto(base+'anatomy-inspection/', wait_until='networkidle'); page.wait_for_function('window.inspectionReady===true')
            before = page.locator('#pose').input_value(); control(page, '#pose', 45)
            assert '45.00' in page.locator('#pose-value').inner_text(); page.locator('#bind').click()
            assert abs(float(page.locator('#pose').input_value())-float(before)) < 1e-7
            page.locator('#geometry').select_option('remesh'); page.locator('#geometry').select_option('source')
            page.screenshot(path=str(q/'atlas-read-only.jpg'), type='jpeg', quality=85)
            controls.append('read-only atlas pose and representation; bind pose restored without worker')
            assert not workers and not errors and not http_failures, (workers, errors, http_failures)
            static_context = browser.new_context(java_script_enabled=False)
            static_context.route('**/*', route)
            static = static_context.new_page(); watch(static)
            for width in [1280, 393, 320]:
                static.set_viewport_size({'width': width, 'height': 900})
                for entry in ['index.html', 'anatomy-inspection/index.html', 'anatomical-arm/index.html', 'coupled-fixture/index.html']:
                    static.goto(base+entry, wait_until='networkidle')
                    assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (entry, width)
                    assert static.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)'), entry
                static.screenshot(path=str(q/f'no-js-{width}.jpg'), type='jpeg', quality=85)
            static.goto(base); static.emulate_media(media='print'); static.set_viewport_size({'width': 658, 'height': 1123})
            static.evaluate('document.fonts.ready')
            assert static.evaluate('''()=>[...document.querySelectorAll('.equation.print-reflowed')].every(e=>{
                const original=[...e.querySelector(':scope > math > semantics > mrow').children];
                const copied=[...e.querySelectorAll(':scope > .print-equation-rows > math > mrow')].flatMap(row=>[...row.children]);
                return copied.length===original.length&&copied.every((node,i)=>node.outerHTML===original[i].outerHTML);
            })'''), 'Persisted print MathML differs from original token sequence'
            assert static.locator('.proof-card').count() == 103
            assert static.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            static.pdf(path=str(q/'functional-root-print.pdf'), format='A4', print_background=True,
                margin={'top': '16mm', 'bottom': '16mm', 'left': '16mm', 'right': '16mm'}, tagged=True)
            assert not errors and not workers and not http_failures, (errors, workers, http_failures)
            version = browser.version; browser.close()
    finally:
        server.shutdown(); server.server_close()
    write = lambda path, value: path.write_text(json.dumps(value, indent=2)+'\n')
    write(q/'local-browser-requests.json', {'requests': requests, 'workers': workers, 'errors': errors, 'http_failures': http_failures})
    with fitz.open(q/'functional-root-print.pdf') as pdf:
        pdf_pages = len(pdf)
        clipped = [(i+1, span['text'][:60]) for i, page in enumerate(pdf) for block in page.get_text('dict')['blocks']
            for line in block.get('lines', []) for span in line['spans']
            if span['bbox'][0] < -.5 or span['bbox'][2] > page.rect.width+.5 or span['bbox'][1] < -.5 or span['bbox'][3] > page.rect.height+.5]
        if clipped: raise ValueError('Clipped root print text: '+str(clipped[:10]))
    receipt = {'kind': 'SCOPED_FUNCTIONAL_PAGES_QUALIFICATION', 'candidate_commit': m['candidate_commit'],
        'candidate_tree': m['candidate_tree'], 'input_manifest_sha256': sha(Path(manifest).read_bytes()),
        'original_records_preserved': archived, 'protected_public_files': len(construction['protected_public_files']),
        'local_entry_reader_css_links_checked': links, 'explicit_dynamic_fetch_worker_dependencies_checked': runtime,
        'bundles': 6, 'historical_proof_cards': 103, 'controls': controls, 'browser_version': version,
        'privacy': 'PASS_WITH_EXACT_PINNED_EXECUTABLE_LITERAL_EXCEPTIONS', 'privacy_exception_files': exceptions,
        'source_bindings': 'PASS', 'historical_markdown_numeric_content': 'PASS',
        'root_print_pages': pdf_pages, 'clipped_print_spans': [], 'no_javascript_mobile_print': 'PASS',
        'print_layout': print_layout,
        'print_presentation_derivative': print_derivative,
        'print_reflow_source': {'commit': PUBLISHED, 'path': reflow_path,
            'blob': git('rev-parse', PUBLISHED+':'+reflow_path).decode().strip(), 'sha256': sha(reflow_source)},
        'held_browser_workers_started': 0, 'held_opt_in_runtime': 'UNRUN', 'anatomical_simulation': 'UNRUN',
        'failed_local_http_responses': [], 'favicon_response_exclusion': '/favicon.ico only',
        'proof_compilation': 'UNRUN', 'live_root_read': False, 'public_network_requests': 0,
        'scientific_status': 'Pinned historical evidence; later unbound results excluded', 'publication': 'NOT_EXECUTED'}
    write(private/'qualification.json', receipt)
    return receipt
