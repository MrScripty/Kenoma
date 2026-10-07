from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from fetch_historical_outputs import recover, safe_path, verify


class HistoricalOutputTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.root = self.repo / 'education'
        self.path = 'review/old/receipt.json'
        file = self.root / self.path
        file.parent.mkdir(parents=True)
        self.raw = b'{"archived": true}\n'
        file.write_bytes(self.raw)
        subprocess.run(['git', 'init', '-q'], cwd=self.repo, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.repo, check=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'Historical fixture'], cwd=self.repo, check=True)
        self.commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.repo, text=True).strip()
        blob = hashlib.sha1(b'blob ' + str(len(self.raw)).encode() + b'\0' + self.raw).hexdigest()
        self.record = {'bytes': len(self.raw), 'sha256': hashlib.sha256(self.raw).hexdigest(),
                       'gitBlob': blob, 'url': 'https://raw.githubusercontent.com/MrScripty/Kenoma/' + self.commit + '/education/' + self.path}

    def tearDown(self):
        self.temporary.cleanup()

    def test_exact_offline_recovery_and_reuse(self):
        destination = recover(self.path, self.record, self.commit, self.root, False)
        self.assertEqual(destination.read_bytes(), self.raw)
        self.assertEqual(recover(self.path, self.record, self.commit, self.root, False), destination)
        self.assertNotEqual(destination, self.root / self.path)

    def test_corrupt_cached_input_is_rejected(self):
        destination = recover(self.path, self.record, self.commit, self.root, False)
        destination.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            recover(self.path, self.record, self.commit, self.root, False)

    def test_each_identity_is_required(self):
        for field, value in [('bytes', 1), ('sha256', '0' * 64), ('gitBlob', '0' * 40)]:
            record = dict(self.record, **{field: value})
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify(self.raw, record)

    def test_invalid_paths_and_mutable_revisions_are_rejected(self):
        for path in ['', '/tmp/x', '../x', 'review/../../x', 'review\\x']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_path(path)
        with self.assertRaises(ValueError):
            recover(self.path, self.record, 'main', self.root, False)

    def test_output_symlink_is_rejected(self):
        (self.root / '.artifacts').symlink_to(self.repo / 'escape')
        with self.assertRaises(ValueError):
            recover(self.path, self.record, self.commit, self.root, False)

    def test_missing_object_does_not_synthesize_evidence(self):
        with self.assertRaises(RuntimeError):
            recover(self.path, self.record, '0' * 40, self.root, False)

    def test_network_url_must_match_the_exact_pin(self):
        with self.assertRaises(ValueError):
            recover(self.path, dict(self.record, url='https://example.invalid/output'), '0' * 40, self.root, True)


if __name__ == '__main__':
    unittest.main()
