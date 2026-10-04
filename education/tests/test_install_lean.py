"""Exercise cache/download failures without downloading or running a toolchain."""
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('install_lean', Path(__file__).resolve().parents[1] / 'tools/install_lean.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
VALID = b'fixed archive fixture; never a real executable'


class Response(io.BytesIO):
    def __init__(self, data, length=None):
        super().__init__(data)
        self.headers = {} if length is None else {'Content-Length': str(length)}


class Interrupted(Response):
    def read(self, count):
        if self.tell():
            raise OSError('interrupted test download')
        return super().read(3)


class LeanCache(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.archive = self.directory / f'lean-{installer.VERSION}-linux.tar.zst'
        self.digest = patch.object(installer, 'SHA256', hashlib.sha256(VALID).hexdigest())
        self.digest.start()
        self.addCleanup(self.digest.stop)

    def assert_no_cache_or_temporary(self):
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_interruption_leaves_no_final_or_partial_then_retry_succeeds(self):
        with patch.object(installer.urllib.request, 'urlopen', return_value=Interrupted(VALID)):
            with self.assertRaisesRegex(OSError, 'interrupted'):
                installer.ensure_archive(self.directory)
        self.assert_no_cache_or_temporary()
        with patch.object(installer.urllib.request, 'urlopen', return_value=Response(VALID)):
            self.assertEqual(installer.ensure_archive(self.directory).read_bytes(), VALID)
        self.assertEqual(list(self.directory.iterdir()), [self.archive])

    def test_wrong_digest_never_promoted_extracted_or_executed(self):
        with patch.object(installer.urllib.request, 'urlopen', return_value=Response(b'wrong')), patch.object(installer.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'hash mismatch'):
                installer.install(self.directory)
            run.assert_not_called()
        self.assert_no_cache_or_temporary()

    def test_valid_cache_reused_without_network(self):
        self.archive.write_bytes(VALID)
        with patch.object(installer.urllib.request, 'urlopen') as fetch:
            self.assertEqual(installer.ensure_archive(self.directory), self.archive)
            fetch.assert_not_called()

    def test_corrupt_old_final_cache_safely_recovered(self):
        self.archive.write_bytes(b'old partial bytes')
        with patch.object(installer.urllib.request, 'urlopen', return_value=Response(VALID)) as fetch:
            self.assertEqual(installer.ensure_archive(self.directory).read_bytes(), VALID)
            fetch.assert_called_once()

    def test_extraction_and_execution_only_after_verified_promotion(self):
        observed = []
        def run(command, **kwargs):
            self.assertTrue(installer.verified(self.archive))
            self.assertEqual(list(self.directory.iterdir()), [self.archive])
            observed.append(command)
        with patch.object(installer.urllib.request, 'urlopen', return_value=Response(VALID)), patch.object(installer.subprocess, 'run', side_effect=run), contextlib.redirect_stdout(io.StringIO()):
            installer.install(self.directory)
        self.assertEqual(len(observed), 2)
        self.assertEqual(observed[0][0], 'tar')
        self.assertEqual(observed[1][1], '--version')

    def test_advertised_and_streamed_byte_budget(self):
        for response in [Response(VALID, len(VALID)), Response(VALID)]:
            with self.subTest(advertised=bool(response.headers)), patch.object(installer, 'MAX_ARCHIVE_BYTES', 5), patch.object(installer.urllib.request, 'urlopen', return_value=response):
                with self.assertRaisesRegex(RuntimeError, 'byte budget'):
                    installer.ensure_archive(self.directory)
                self.assert_no_cache_or_temporary()
