"""Light positive/negative receipt controls. No browser, Lean or research execution."""
from pathlib import Path
from types import SimpleNamespace
import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('architecture_force_qualification',
    Path(__file__).resolve().parents[1] / 'tools/qualify_architecture_force.py')
Q = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(Q)


class SourceControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='kenoma-force-receipt-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        names = ['ArchitectureForce.lean'] + [f'fixture-{i}.txt' for i in range(12)]
        for path in [Q.CONTRIBUTION + '/' + name for name in names] + list(Q.SUPPORT):
            p = self.root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(path + '\n')
        self.commit()

    def commit(self):
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        subprocess.run(['git', '-c', 'user.email=test@example.invalid', '-c', 'user.name=Receipt test',
                        '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Local fixture'], cwd=self.root, check=True)
        self.head = Q.git('rev-parse', 'HEAD', cwd=self.root)

    def test_exact_clean_head_binds_inputs(self):
        receipt = Q.snapshot(self.head, self.root)
        self.assertEqual(receipt['commit'], self.head)
        self.assertEqual(len(receipt['files']), 13 + len(Q.SUPPORT))

    def test_wrong_commit_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'differs'):
            Q.snapshot('0' * 40, self.root)

    def test_dirty_tracked_source_rejected(self):
        (self.root / Q.SUPPORT[0]).write_text('changed')
        with self.assertRaisesRegex(RuntimeError, 'Pristine'):
            Q.snapshot(self.head, self.root)

    def test_untracked_source_rejected(self):
        (self.root / 'unexpected.txt').write_text('unexpected')
        with self.assertRaisesRegex(RuntimeError, 'Pristine'):
            Q.snapshot(self.head, self.root)

    def test_fourteenth_contribution_file_rejected(self):
        (self.root / Q.CONTRIBUTION / 'extra.txt').write_text('extra')
        self.commit()
        with self.assertRaisesRegex(RuntimeError, '13-file'):
            Q.snapshot(self.head, self.root)

    def test_missing_tracked_input_rejected(self):
        (self.root / Q.SUPPORT[0]).unlink()
        self.commit()
        with self.assertRaisesRegex(RuntimeError, 'tracked'):
            Q.snapshot(self.head, self.root)

    def test_output_inside_checkout_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'outside'):
            Q.external(self.root / 'evidence', self.root)
        self.assertEqual(Q.external(self.root.parent / 'external', self.root), self.root.parent / 'external')


class FinishControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='kenoma-force-finish-test-')
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name)
        self.checker = Q.contribution_checker()
        self.source = {'commit': '1' * 40, 'git_tree': '2' * 40, 'files': {
            str(p.relative_to(Q.ROOT)): {'sha256': Q.sha256(p), 'bytes': p.stat().st_size}
            for p in (Q.ROOT / Q.CONTRIBUTION).iterdir() if p.is_file()}}
        Q.write_json(self.output / 'source.json', self.source)
        (self.output / 'node.txt').write_text('# tests 12\n# pass 12\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n')
        Q.write_json(self.output / 'symbolic.json', {'count': 7,
            'symbolic_identities': {str(i): True for i in range(7)}, 'performs_lean_compilation': False})
        Q.write_json(self.output / 'formal/architecture-force-proof-status.json', {
            'source_sha256': self.source['files'][Q.CONTRIBUTION + '/ArchitectureForce.lean']['sha256'],
            'mathlib_commit': self.checker.PIN, 'manifest_sha256': self.checker.MANIFEST,
            'claims': [{'theorem': 'KenomaArchitectureForce.' + name, 'status': 'checked', 'axioms': ['propext']}
                       for name in self.checker.THEOREMS], 'book_registered': False})
        Q.write_json(self.output / 'dependencies.json', {
            'mathlib_commit': self.checker.PIN, 'manifest_sha256': self.checker.MANIFEST,
            'cache_roots': list(Q.CACHE_ROOTS), 'all_sources_pristine': True,
            'cache_fetched_in_this_command': True, 'full_book_from_source_gate': False})
        captures = []
        for name in ('lab-1280-default.jpg', 'lab-1280-force-length.jpg', 'lab-393-default.jpg',
                     'lab-393-force-length.jpg', 'lab-393-no-javascript.jpg'):
            path = self.output / 'browser' / name
            path.parent.mkdir(exist_ok=True)
            # Synthetic signature only, used to exercise receipt binding, not image validity.
            path.write_bytes(b'\xff\xd8\xffreceipt-test')
            captures.append({'file': name, 'sha256': Q.sha256(path), 'format': 'jpeg', 'quality': 85})
        Q.write_json(self.output / 'browser/browser.json', {'status': 'passed',
            'visual_acceptance': 'pending human inspection', 'no_javascript_static_fallback': True,
            'source_sha256': {p: data['sha256'] for p, data in self.source['files'].items()},
            'captures': captures, 'checks': [{'width': w, 'height': h, 'horizontal_overflow': False,
                'range_keyboard_input': True, 'controls': [f'{c}:{k}' for c in ('stretch', 'volume', 'packing', 'angle')
                                                        for k in ('Home', 'End')],
                'force_length_toggle': True, 'repeated_reset': True, 'local_links': True,
                'browser_errors': []} for w, h in ((1280, 1000), (393, 852))]})
        self.args = SimpleNamespace(output=self.output, expected_head=self.source['commit'])

    def edit(self, path, mutate):
        p = self.output / path
        data = json.loads(p.read_text())
        mutate(data)
        Q.write_json(p, data)

    def finish(self, source=None):
        with patch.object(Q, 'snapshot', return_value=source or self.source):
            Q.finish(self.args)

    def reject(self, text):
        with self.assertRaisesRegex(RuntimeError, text):
            self.finish()
        self.assertFalse((self.output / 'qualification.json').exists())

    def test_complete_receipts_bind_without_visual_acceptance(self):
        self.finish()
        result = json.loads((self.output / 'qualification.json').read_text())
        self.assertEqual(result['visual_acceptance'], 'pending human inspection')
        self.assertFalse(result['full_book_qualification'])
        self.assertEqual(result['commit'], self.args.expected_head)
        self.assertIn('browser/lab-393-default.jpg', result['artifact_sha256'])

    def test_changed_source_rejected(self):
        other = copy.deepcopy(self.source)
        other['git_tree'] = '0' * 40
        with self.assertRaisesRegex(RuntimeError, 'Source changed'):
            self.finish(other)

    def test_node_count_mismatch_rejected(self):
        (self.output / 'node.txt').write_text('# pass 10\n# fail 0\n')
        self.reject('twelve Node')

    def test_symbolic_failure_rejected(self):
        self.edit('symbolic.json', lambda data: data['symbolic_identities'].update({'0': False}))
        self.reject('symbolic')

    def test_lean_source_mismatch_rejected(self):
        self.edit('formal/architecture-force-proof-status.json', lambda data: data.update(source_sha256='0' * 64))
        self.reject('Lean source')

    def test_missing_lean_contract_rejected(self):
        self.edit('formal/architecture-force-proof-status.json', lambda data: data['claims'].pop())
        self.reject('Lean contracts')

    def test_untrusted_axiom_rejected(self):
        self.edit('formal/architecture-force-proof-status.json', lambda data: data['claims'][0]['axioms'].append('sorryAx'))
        self.reject('Lean result')

    def test_wrong_cache_scope_rejected(self):
        self.edit('dependencies.json', lambda data: data.update(cache_roots=['Mathlib.lean']))
        self.reject('bounded dependency')

    def test_missing_browser_control_rejected(self):
        self.edit('browser/browser.json', lambda data: data['checks'][0]['controls'].pop())
        self.reject('browser control')

    def test_missing_browser_source_hash_rejected(self):
        self.edit('browser/browser.json', lambda data: data['source_sha256'].pop(next(iter(data['source_sha256']))))
        self.reject('browser source')

    def test_unreviewed_visual_acceptance_rejected(self):
        self.edit('browser/browser.json', lambda data: data.update(visual_acceptance='passed'))
        self.reject('visual acceptance')

    def test_changed_capture_rejected(self):
        (self.output / 'browser/lab-393-default.jpg').write_bytes(b'\xff\xd8\xffchanged')
        self.reject('Capture mismatch')

    def test_missing_capture_rejected(self):
        self.edit('browser/browser.json', lambda data: data['captures'].pop())
        self.reject('captures')


if __name__ == '__main__':
    unittest.main()
