"""Negative control: valid proof bytes, dirty tracked explanation, no success receipt."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    proof = ROOT / 'proofs/MixedLogVolume.lean'
    proof_hash = hashlib.sha256(proof.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='kenoma-mixed-binding-') as directory:
        fixture = Path(directory) / 'repo'
        education = fixture / 'education'
        paths = ('proofs/MixedLogVolume.lean', 'tools/check_mixed_volume_proofs.py',
                 'tools/bootstrap_proofwidgets.py', 'research/mixed-log-volume-projection.md')
        for relative in paths:
            target = education / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        def git(*args):
            return subprocess.run(['git', *args], cwd=fixture, check=True,
                                  capture_output=True, text=True)
        git('init', '--quiet')
        git('config', '--local', 'user.name', 'MrScripty')
        git('config', '--local', 'user.email', 'TheEnvironmentGuy@protonmail.com')
        git('add', 'education')
        git('commit', '--quiet', '-m', 'Negative-control fixture')
        note = education / 'research/mixed-log-volume-projection.md'
        note.write_text(note.read_text() + '\n<!-- Uncommitted binding negative control. -->\n')
        evidence = Path(directory) / 'check'
        evidence.mkdir()
        (evidence / 'receipt.json').write_text('{"result":"STALE_SUCCESS"}\n')
        result = subprocess.run([sys.executable, str(education / paths[1]),
                                 '--output', str(evidence)], capture_output=True, text=True)
        message = 'Research source files do not match HEAD; refusing success receipt'
        assert result.returncode != 0, 'Dirty source incorrectly passed'
        assert message in result.stderr, result.stderr
        assert not (evidence / 'receipt.json').exists(), 'Stale success receipt survived'
        assert hashlib.sha256((education / paths[0]).read_bytes()).hexdigest() == proof_hash
        payload = {
            'schema': 1, 'result': 'PASS_DIRTY_SOURCE_BINDING_NEGATIVE_CONTROL',
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                     cwd=ROOT, text=True).strip(),
            'proof_sha256': proof_hash, 'dirty_tracked_file': paths[3],
            'negative_check_exit_code': result.returncode,
            'expected_rejection': message, 'success_receipt_emitted': False,
            'stale_success_receipt_removed': True,
            'scope': 'Disposable Git fixture; valid proof unchanged; no dependency or kernel check attempted.',
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + '\n')
    print(payload['result'])
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / '.tools/mixed-volume-successor-check/binding-negative.json')
    run(parser.parse_args().output)
