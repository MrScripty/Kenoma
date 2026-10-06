"""Fault injection: optional diagnostic failure must leave solver fields on disk."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import diagnose_pressure_residual as diagnostic
from source_amplitude_p2_p1 import ANCHOR, model
from run_full_p2_p1 import serial


class ExportTests(unittest.TestCase):
    def test_terminal_survives_postsolve_diagnostic_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); old = root/'old'; fine = root/'fine'; out = root/'out'
            old.mkdir(); fine.mkdir()
            (old/'coarse-1.01.json').write_text('{}')
            (old/'coarse-1.01-request.json').write_text(json.dumps(dict(sourceHashes={}, material=ANCHOR, activation=1.)))
            (fine/'fine-mesh.json').write_text(json.dumps(dict(mesh=serial(model.mesh((1, 1, 1))))))

            def terminal(body, start):
                state = body.evaluate(start)
                return start, state, [dict(iteration=0, forceResidualN=state['residual'])], 'INJECTED_RETURN_NO_SOLVE'

            with patch.object(diagnostic, 'ROOT', root), patch.object(diagnostic, 'OLD', old), \
                 patch.object(diagnostic, 'FINE', fine), patch.object(diagnostic, 'OUT', out), \
                 patch.object(diagnostic.amplitude.ExplicitBody, 'newton', terminal), \
                 patch.object(diagnostic, 'metrics', side_effect=ValueError('injected optional diagnostic failure')), \
                 patch.object(diagnostic.subprocess, 'check_output', return_value='test-commit\n'), \
                 patch.object(sys, 'argv', ['diagnostic', 'fine-recovery']), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'injected optional diagnostic failure'):
                    diagnostic.main()
            receipt = diagnostic.read(out/'fine-recovery-solver-terminal.json')
            self.assertEqual(receipt['reason'], 'INJECTED_RETURN_NO_SOLVE')
            self.assertEqual(receipt['label'], 'DIAGNOSTIC_ONLY_NO_ACCEPTANCE')
            self.assertTrue(receipt['recoveryOfExporterException'])
            self.assertGreater(len(receipt['terminalPositionsM']), 0)
            self.assertGreater(len(receipt['terminalPressurePa']), 0)
            self.assertFalse((out/'fine-recovery.json').exists())


if __name__ == '__main__':
    unittest.main()
