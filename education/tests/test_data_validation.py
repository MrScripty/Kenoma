"""Adversarial source/shape mutations, with regenerated metadata, must fail."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1] / 'data/elbow-v1'
sys.path.insert(0, str(PACKAGE / 'scripts'))
import validate_package as validator
import prepare_data as prepare
import build_manifest as manifest


class DataValidation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'package'
        shutil.copytree(PACKAGE, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.regenerate_manifest()

    def validate(self):
        with patch.object(validator, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            validator.run()

    def regenerate_manifest(self):
        with patch.object(manifest, 'ROOT', self.root), contextlib.redirect_stdout(io.StringIO()):
            manifest.main()

    def test_unchanged_package_passes(self):
        self.validate()

    def test_actual_arm26_edit_and_regenerated_parameters_manifest_rejected(self):
        source = self.root / 'sources/arm26.osim'
        source.write_bytes(source.read_bytes() + b'\n<!-- harmless source edit -->\n')
        with patch.object(prepare, 'ROOT', self.root), patch.object(prepare, 'DATA', self.root / 'data'):
            prepare.arm26()
        self.regenerate_manifest()
        with self.assertRaisesRegex(AssertionError, 'Pinned Arm26 byte hash'):
            self.validate()

    def test_actual_obj_edit_and_regenerated_atlas_manifest_rejected(self):
        source = self.root / 'sources/bodyparts3d/FJ3368.obj'
        source.write_bytes(source.read_bytes() + b'\n# harmless source edit\n')
        with patch.object(prepare, 'ROOT', self.root), patch.object(prepare, 'DATA', self.root / 'data'):
            prepare.atlas()
        self.regenerate_manifest()
        with self.assertRaisesRegex(AssertionError, 'Source OBJ hash FJ3368'):
            self.validate()

    def test_source_document_edit_and_regenerated_manifest_rejected(self):
        source = self.root / 'sources/openarm_errata.md'
        source.write_bytes(source.read_bytes() + b'\n')
        self.regenerate_manifest()
        with self.assertRaisesRegex(AssertionError, 'Accepted document pin sources/openarm_errata.md'):
            self.validate()

    def test_vertex_shapes_and_counts_rejected_even_with_fresh_manifest(self):
        path = self.root / 'data/bodyparts3d_right_arm_m.json'
        original = json.loads(path.read_text())
        # Include shortened/extended outer arrays and coordinates: neither
        # nested zip nor a regenerated manifest may hide unmatched entries.
        mutations = {
            'short vertices': lambda p: p['vertices_m'].pop(),
            'long vertices': lambda p: p['vertices_m'].append(p['vertices_m'][0]),
            'short coordinate': lambda p: p['vertices_m'][0].pop(),
            'long coordinate': lambda p: p['vertices_m'][0].append(0),
            'declared count': lambda p: p.update(vertex_count=p['vertex_count'] + 1),
            'empty vertices': lambda p: p.update(vertices_m=[]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                data = json.loads(json.dumps(original))
                mutate(data['parts'][0])
                path.write_text(json.dumps(data))
                self.regenerate_manifest()
                with self.assertRaisesRegex(AssertionError, 'Vertex count and dimensions FJ3368'):
                    self.validate()
