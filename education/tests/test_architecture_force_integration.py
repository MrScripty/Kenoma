"""Pure source/assembly contracts; temporary receipts are synthetic fixtures.

No full build, Lean, browser, network, anatomy or numerical campaign is started.
"""
from pathlib import Path
from html.parser import HTMLParser
import ast
import copy
import json
import math
import re
import shutil
import sys
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import architecture_force_lab as lab
from check_architecture_force_artifact import check_assembly
from build import implementation_link
from check_real_lesson_proofs import FAMILIES, BOOK_CLAIMS, BOOK_SOURCES


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.targets = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.targets.extend((tag, value) for key, value in attrs if key in {'href', 'src'})


def fixture_receipt(root):
    """Synthetic data only; does not call or impersonate Lean."""
    claims = json.loads((root / lab.CLAIMS).read_text())
    return {'source': lab.SOURCE, 'source_sha256': lab.digest(root / lab.SOURCE),
            'claims_sha256': lab.digest(root / lab.CLAIMS),
            'mathlib': json.loads((root / 'proofs/mathlib-lock.json').read_text()),
            'lean_version': 'UNIT TEST FIXTURE; NOT KERNEL EVIDENCE',
            'claims': [dict(c, status='checked', axioms=['propext', 'Quot.sound']) for c in claims]}


class SourceInventory(unittest.TestCase):
    def test_canonical_order_and_original_claim_slots(self):
        chapters = json.loads((ROOT / 'book/book.json').read_text())['chapters']
        self.assertEqual(len(chapters), 27)
        i = chapters.index('09ab-architecture-force.md')
        self.assertEqual(chapters[i-1:i+2], ['09aa-nonuniform-volume.md', '09ab-architecture-force.md', '09b-material-response.md'])
        self.assertFalse(any('contributions/architecture-force' in x for x in chapters))
        text = (ROOT / 'book/chapters/09ab-architecture-force.md').read_text()
        _, claims = lab.source_inventory()
        self.assertCountEqual(re.findall(r'\{\{proof:([\w-]+)\}\}', text), [c['id'] for c in claims])
        self.assertEqual(text.count('{{architecture-force-lab}}'), 1)
        for phrase in ['{#architecture-to-force}', '{#architecture-force-evidence}', '103 + 6 = 109', '115-declaration source inventory', 'No fit, material coefficient, calibration state, accepted trajectory, reference asset, or failure threshold is changed.']:
            self.assertIn(phrase, text)

    def test_complete_registry_count_and_exact_statements(self):
        base = [('Mechanics.lean', 'claims.json'), ('AnatomicalTransfer.lean', 'anatomical-claims.json'),
                ('CoupledMechanics.lean', 'coupled-claims.json'), ('AnatomicalArm.lean', 'arm-claims.json'),
                ('ContinuumProperties.lean', 'property-claims.json'), ('MaterialResponse.lean', 'material-claims.json')]
        families = base + [(s, m) for s, m, *_ in FAMILIES]
        self.assertEqual(len(families), BOOK_SOURCES)
        self.assertEqual(BOOK_SOURCES, 14)
        ids, theorems, real = [], [], 0
        for source, mapping in families:
            claims = json.loads((ROOT / 'proofs' / mapping).read_text())
            text = (ROOT / 'proofs' / source).read_text()
            self.assertEqual(len(re.findall(r'^theorem ', text, re.M)), len(claims), source)
            ids += [c['id'] for c in claims]
            theorems += [c['theorem'] for c in claims]
            if source == 'ContinuumProperties.lean' or source in {f[0] for f in FAMILIES}:
                real += len(claims)
        self.assertEqual(len(ids), BOOK_CLAIMS)
        self.assertEqual(BOOK_CLAIMS, 115)
        self.assertEqual((len(ids)-real, real), (30, 85))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(theorems), len(set(theorems)))
        chapters = json.loads((ROOT/'book/book.json').read_text())['chapters']
        manuscript = '\n'.join((ROOT/'book/chapters'/name).read_text() for name in chapters)
        self.assertCountEqual(re.findall(r'\{\{proof:([\w-]+)\}\}', manuscript), ids)
        _, claims = lab.source_inventory()
        text = (ROOT / lab.SOURCE).read_text()
        for c in claims:
            self.assertTrue(c['assumptions'])
            self.assertEqual(c['limitations'], c['not_proved']+'.')
            name = c['theorem'].split('.')[-1]
            stmt = re.search(r'^theorem '+name+r'\b.*?\s:=', text, re.S | re.M)[0].rsplit(':=', 1)[0].rstrip()
            self.assertEqual(c['statement_lean'], stmt)

    def test_implementation_link_retains_escaping_and_existing_scope(self):
        self.assertEqual(Links(implementation_link('web/mechanics.mjs: force')).targets,
                         [('a', 'web/mechanics.mjs')])
        self.assertEqual(Links(implementation_link('contributions/other/model.mjs')).targets, [])
        rendered = implementation_link('contributions/architecture-force/model.mjs; a*b^2 < bounds')
        self.assertEqual(Links(rendered).targets, [('a', 'contributions/architecture-force/model.mjs')])
        self.assertIn('a&#42;b&#94;2 &lt; bounds', rendered)

    def test_defaults_match_the_analytic_case_in_both_formats(self):
        A0, J, stretch, nominal = 100e-6*.8, 1, .8, 300e3
        expected = [f'{A0*1e6:.2f} mm²', f'{A0*J/stretch*1e6:.2f} mm²', f'{nominal/1000:.2f} kPa',
                    f'{nominal*stretch/J/1000:.2f} kPa', f'{nominal*A0:.2f} N', f'{nominal*A0*math.cos(math.pi/6):.2f} N']
        self.assertEqual([v for _, v in lab.DEFAULT_ROWS], expected)
        for web in (True, False):
            text = lab.block(web)
            for label, value in lab.DEFAULT_ROWS:
                self.assertIn(label, text)
                self.assertIn(value, text)
            self.assertIn('architecture-force/index.html', text)
            self.assertIn('force–length multiplier is held at 1', text)

    def test_full_build_hooks_and_portable_print_destinations(self):
        source = (ROOT / 'tools/build.py').read_text()
        self.assertIn('build_architecture_force()', source)
        self.assertIn("text.replace('{{architecture-force-lab}}',architecture_force_block(web))", source)
        self.assertIn(('ArchitectureForce.lean', 'architecture-force-real-claims.json', 'architecture-force-real', 6), FAMILIES)
        destinations = (ROOT / 'tools/render_pdf.py').read_text()
        for target in ['architecture-force/index.html', 'architecture-force/sources.json', 'architecture-force/registration.json', 'contributions/architecture-force/README.md']:
            self.assertIn("'"+target+"':'#architecture-", destinations)
        text = (ROOT / 'tools/nonuniform_lab.py').read_text()
        self.assertIn("composition['totalCandidateProofs'] == 109", text)
        self.assertIn('historicalNonuniformBookTotal=109', text)
        self.assertNotIn('bookTotal=109', text)
        scripts = json.loads((ROOT / 'package.json').read_text())['scripts']
        self.assertIn('contributions/architecture-force/*.test.mjs', scripts['test'])
        self.assertNotIn('build', scripts['test:architecture-force'])
        print_gate = (ROOT/'tools/check_print_readability.py').read_text()
        self.assertIn(f'EXPECTED_CARDS = {BOOK_CLAIMS}', print_gate)
        self.assertIn(f'EXPECTED_SOURCES = {BOOK_SOURCES}', print_gate)


class AssemblyContracts(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='kenoma-force-source-unit-')
        self.addCleanup(temp.cleanup)
        self.root, self.out = Path(temp.name)/'source', Path(temp.name)/'output'
        shutil.copytree(ROOT/'contributions/architecture-force', self.root/'contributions/architecture-force')
        for relative in [lab.SOURCE, lab.CLAIMS, lab.SOURCE_MANIFEST, 'proofs/mathlib-lock.json', 'tools/architecture_force_lab.py']:
            path = self.root/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/relative, path)
        self.out.mkdir()
        self.receipt = fixture_receipt(self.root)
        (self.out/lab.RECEIPT).write_text(json.dumps(self.receipt))

    def test_closure_preserves_runtime_and_thirteen_original_files(self):
        registration = lab.assemble(self.out, self.receipt, self.root)
        original, _ = lab.source_inventory(self.root)
        for name, digest in original['files'].items():
            self.assertEqual(lab.digest(self.out/'contributions/architecture-force'/name), digest)
        for name in ['model.mjs', 'lab.mjs', 'style.css', 'sources.json']:
            self.assertEqual((self.out/'architecture-force'/name).read_bytes(), (self.root/'contributions/architecture-force'/name).read_bytes())
        for relative, digest in registration['outputSha256'].items():
            self.assertEqual(lab.digest(self.out/relative), digest)
        self.assertEqual(registration['proofReceiptSha256'], lab.digest(self.out/lab.RECEIPT))
        self.assertEqual(registration['registeredContracts'], 6)
        self.assertFalse(registration['physicalLawsChanged'])
        self.assertIn('not this book assembly', registration['priorQualificationScope'])
        text = (self.out/'architecture-force/index.html').read_text()
        for phrase in ['book-print-reference', '@media print', 'JavaScript is unavailable', 'Total reference area 150.00 mm² · summed force 35.00 N']:
            self.assertIn(phrase, text)
        for name, value in lab.DEFAULT_ROWS:
            self.assertIn('<dt>'+name+'</dt><dd>'+value+'</dd>', text)
        (self.out/'index.html').write_text('<h1 id="architecture-to-force">Book fixture</h1>')
        for folder in ['architecture-force', 'contributions/architecture-force']:
            for tag, href in Links((self.out/folder/'index.html').read_text()).targets:
                self.assertFalse(href.startswith(('http:', 'https:', '//')), (tag, href))
                self.assertTrue((self.out/folder/href.split('#')[0]).is_file(), href)
        (self.out/'architecture-force/book-browser.json').write_text('stale browser fixture')
        self.assertEqual(lab.assemble(self.out, self.receipt, self.root), registration)
        self.assertFalse((self.out/'architecture-force/book-browser.json').exists())
        self.assertEqual(check_assembly(self.out, self.root)[0], registration)
        (self.out/'architecture-force/model.mjs').write_text('mutated fixture')
        with self.assertRaisesRegex(ValueError, 'Changed architecture-force output'):
            check_assembly(self.out, self.root)

    def test_six_generated_implementation_links_resolve_to_preserved_bundled_source(self):
        lab.assemble(self.out, self.receipt, self.root)
        _, claims = lab.source_inventory(self.root)
        expected = 'contributions/architecture-force/model.mjs'
        for claim in claims:
            with self.subTest(claim=claim['id']):
                markup = implementation_link(claim['implementation'])
                self.assertEqual(Links(markup).targets, [('a', expected)])
                self.assertEqual((self.out/expected).read_bytes(), (self.root/expected).read_bytes())
        self.assertIsNone(claims[-1]['model_function'])
        self.assertIn('mathematical contract only', implementation_link(claims[-1]['implementation']))

    def test_actual_pdf_rewriter_uses_the_immutable_public_source(self):
        lab.assemble(self.out, self.receipt, self.root)
        destination = lab.pdf_implementation_links(self.root)
        path = 'contributions/architecture-force/model.mjs'
        expected = 'https://github.com/MrScripty/Kenoma/blob/f6d6bde9974e9894bc5a527c80beef633fd5a1f6/education/'+path
        self.assertEqual(destination, {path: expected})
        # Execute the production rewrite JavaScript with plain anchor fixtures.
        # This is a pure Node unit test, not Chromium or a book/PDF build.
        tree = ast.parse((ROOT/'tools/render_pdf.py').read_text())
        rewrite = next(n.args[0].value for n in ast.walk(tree)
                       if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                       and n.func.attr == 'evaluate' and n.args and isinstance(n.args[0], ast.Constant)
                       and isinstance(n.args[0].value, str) and 'Object.assign(destinations,realDestinations)' in n.args[0].value)
        proof = 'proofs/ArchitectureForce.lean'
        params = {'revision': 'unpublished-book-fixture', 'realDestinations': {proof: '#architecture-force-real-source-appendix'},
                  'architectureImplementationDestinations': destination}
        script = ('const links='+json.dumps([path, proof, 'web/mechanics.mjs'])+'.map(href=>({href,getAttribute(){return this.href},setAttribute(name,value){this.href=value}}));'
                  'globalThis.document={querySelectorAll(){return links}};'
                  '('+rewrite+')('+json.dumps(params)+');console.log(JSON.stringify(links.map(a=>a.href)));')
        result = subprocess.run(['node', '--input-type=module'], input=script, text=True, capture_output=True, check=True)
        targets = json.loads(result.stdout)
        self.assertEqual(targets, [expected, '#architecture-force-real-source-appendix',
                                  'https://github.com/MrScripty/Kenoma/blob/unpublished-book-fixture/education/web/mechanics.mjs'])
        self.assertNotIn('unpublished-book-fixture', targets[0])
        self.assertNotIn('127.0.0.1', targets[0])

    def test_changed_original_is_rejected(self):
        p = self.root/'contributions/architecture-force/model.mjs'
        p.write_text(p.read_text()+'\n// mutation fixture\n')
        with self.assertRaisesRegex(ValueError, 'Contribution source changed'):
            lab.assemble(self.out, self.receipt, self.root)
        with self.assertRaisesRegex(ValueError, 'Contribution source changed'):
            lab.pdf_implementation_links(self.root)

    def test_changed_registered_lean_is_rejected(self):
        p = self.root/lab.SOURCE
        p.write_text(p.read_text()+'\n-- mutation fixture\n')
        with self.assertRaisesRegex(ValueError, 'Registered Lean source differs'):
            lab.assemble(self.out, self.receipt, self.root)

    def test_original_claim_identity_and_boundaries_cannot_be_relabelled(self):
        for key in ['id', 'theorem', 'claim', 'not_proved', 'domain']:
            with self.subTest(key=key):
                original = (self.root/lab.CLAIMS).read_text()
                claims = json.loads(original)
                claims[0][key] = 'changed'
                (self.root/lab.CLAIMS).write_text(json.dumps(claims))
                with self.assertRaisesRegex(ValueError, 'Original claim identity or boundary changed'):
                    lab.source_inventory(self.root)
                (self.root/lab.CLAIMS).write_text(original)

    def test_missing_assumptions_are_rejected(self):
        claims = json.loads((self.root/lab.CLAIMS).read_text())
        claims[0]['assumptions'] = ''
        (self.root/lab.CLAIMS).write_text(json.dumps(claims))
        with self.assertRaisesRegex(ValueError, 'Missing displayed assumptions'):
            lab.source_inventory(self.root)

    def test_stale_source_claim_dependency_or_count_is_rejected(self):
        for key, value in [('source_sha256', 'wrong'), ('claims_sha256', 'wrong'), ('mathlib', {}), ('claims', [])]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                lab.assemble(self.out, {**self.receipt, key: value}, self.root)

    def test_unchecked_claim_or_custom_axiom_is_rejected(self):
        for key, value in [('status', 'pending'), ('axioms', ['sorryAx']), ('assumptions', 'changed')]:
            with self.subTest(key=key):
                receipt = copy.deepcopy(self.receipt)
                receipt['claims'][-1][key] = value
                with self.assertRaises(ValueError):
                    lab.assemble(self.out, receipt, self.root)

    def test_failure_removes_stale_registration(self):
        lab.assemble(self.out, self.receipt, self.root)
        with self.assertRaises(ValueError):
            lab.assemble(self.out, {**self.receipt, 'source_sha256': 'wrong'}, self.root)
        self.assertFalse((self.out/'architecture-force/registration.json').exists())

    def test_delivered_receipt_must_match_supplied_receipt(self):
        (self.out/lab.RECEIPT).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'differs from the delivered book receipt'):
            lab.assemble(self.out, self.receipt, self.root)

    def test_output_cannot_overwrite_source(self):
        with self.assertRaisesRegex(ValueError, 'output must be dist or outside'):
            lab.assemble(self.root/'contributions/architecture-force', self.receipt, self.root)


if __name__ == '__main__':
    unittest.main()
