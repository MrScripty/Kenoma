"""A rerun may overwrite its own evidence, never the frozen book checkout."""
from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('research_workspace', Path(__file__).resolve().parents[1] / 'tools/prepare_research_workspace.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ResearchWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.source / 'education').mkdir()
        (self.source / '.gitignore').write_text('education/.tools/\neducation/node_modules/\neducation/.artifacts/\n')
        (self.source / 'education/evidence.json').write_text('{"original": true}\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'Frozen fixture')
        self.destination = self.root / 'research'

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.source, text=True).strip()

    def test_exact_head_and_mutation_isolation(self):
        for name in ('.tools', 'node_modules'):
            (self.source / 'education' / name).mkdir()
        receipt = module.prepare(self.source, self.destination)
        self.assertEqual(receipt['sourceHead'], self.git('rev-parse', 'HEAD'))
        self.assertTrue((self.destination / 'education/.tools').is_symlink())
        (self.destination / 'education/evidence.json').write_text('{"rerun": true}\n')
        self.assertEqual((self.source / 'education/evidence.json').read_text(), '{"original": true}\n')
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertTrue((self.destination / 'education/.artifacts/research-workspace.json').exists())

    def test_dirty_source_rejected(self):
        (self.source / 'education/evidence.json').write_text('changed')
        with self.assertRaisesRegex(RuntimeError, 'clean frozen'):
            module.prepare(self.source, self.destination)
        self.assertFalse(self.destination.exists())

    def test_nested_workspace_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'outside'):
            module.prepare(self.source, self.source / 'research')

    def test_existing_workspace_preserved(self):
        self.destination.mkdir()
        saved = self.destination / 'saved-receipt'
        saved.write_text('keep')
        with self.assertRaisesRegex(RuntimeError, 'already exists'):
            module.prepare(self.source, self.destination)
        self.assertEqual(saved.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
