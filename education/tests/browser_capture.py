"""Capture a complete section without Chromium's oversized-element resize path."""
from math import ceil


def capture_section(page, section, path):
    original = page.viewport_size.copy()
    before = section.bounding_box()
    assert before and before['height'] > 0, 'Capture section must be visible'
    height = max(original['height'], ceil(before['height']) + 64)
    assert height <= 8192, 'Unexpectedly large capture section'
    try:
        page.set_viewport_size({'width': original['width'], 'height': height})
        after = section.bounding_box()
        assert after and abs(after['width'] - before['width']) < .5
        assert after['height'] <= height - 32, 'Complete section must fit capture viewport'
        section.screenshot(path=str(path), timeout=30000)
    finally:
        page.set_viewport_size(original)
