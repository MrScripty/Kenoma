"""Bounded full-section capture preserves width and restores the viewport."""
from pathlib import Path
import importlib.util
import unittest

spec = importlib.util.spec_from_file_location('browser_capture', Path(__file__).with_name('browser_capture.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Page:
    def __init__(self):
        self.viewport_size = {'width': 393, 'height': 851}
        self.changes = []

    def set_viewport_size(self, size):
        self.viewport_size = size.copy()
        self.changes.append(size.copy())


class Section:
    def __init__(self, page, height=1800, fail=False):
        self.page, self.height, self.fail = page, height, fail
        self.captured = None

    def bounding_box(self):
        return {'width': 360, 'height': self.height}

    def screenshot(self, **kwargs):
        self.captured = (self.page.viewport_size.copy(), kwargs)
        if self.fail:
            raise RuntimeError('capture failed')


class CaptureTests(unittest.TestCase):
    def test_complete_tall_section_keeps_width_and_restores_mobile_viewport(self):
        page = Page()
        section = Section(page)
        module.capture_section(page, section, Path('example.png'))
        self.assertEqual(section.captured[0], {'width': 393, 'height': 1864})
        self.assertEqual(page.viewport_size, {'width': 393, 'height': 851})
        self.assertEqual(section.captured[1]['path'], 'example.png')

    def test_capture_failure_still_restores_viewport(self):
        page = Page()
        with self.assertRaisesRegex(RuntimeError, 'capture failed'):
            module.capture_section(page, Section(page, fail=True), Path('example.png'))
        self.assertEqual(page.viewport_size, {'width': 393, 'height': 851})

    def test_oversized_section_is_rejected_without_resizing(self):
        page = Page()
        with self.assertRaisesRegex(AssertionError, 'Unexpectedly large'):
            module.capture_section(page, Section(page, height=9000), Path('example.png'))
        self.assertEqual(page.changes, [])


if __name__ == '__main__':
    unittest.main()
