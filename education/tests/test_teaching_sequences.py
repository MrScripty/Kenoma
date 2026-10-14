"""Reader assembly checks; these do not synthesize or claim Lean receipts."""
from pathlib import Path
import json, re, shutil, subprocess, sys, unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from teaching_sequences import inventory, block, chapter_source
from chapter_examples import inventory as examples


class TeachingAssembly(unittest.TestCase):
    def test_every_chapter_has_distinct_worked_reading_and_audit(self):
        lessons = inventory()
        self.assertEqual([lesson['chapter'] for lesson in lessons], [example['id'] for example in examples()])
        self.assertEqual(sum(len(lesson['steps']) for lesson in lessons), 95)
        for lesson in lessons:
            self.assertGreater(len({json.dumps(step['parameters'], sort_keys=True) for step in lesson['steps']}), 1)
            self.assertNotIn('qualified', lesson['audit']['change'].lower())

    def test_canonical_text_is_unchanged_after_directive_insertion(self):
        for example in examples():
            path = ROOT / 'book/chapters' / example['chapter']
            original = path.read_text()
            staged = chapter_source(path)
            first, rest = original.split('\n', 1)
            self.assertEqual(staged, first + '\n\n{{teaching:' + example['id'] + '}}\n' + rest)
            self.assertEqual(re.findall(r'\{\{proof:([^}]+)\}\}', staged), example['claimIds'])

    def test_html_and_print_preserve_every_observation(self):
        for lesson in inventory():
            web = block(lesson['chapter'])
            plain = block(lesson['chapter'], False)
            self.assertEqual(web.count('data-teaching-step='), len(lesson['steps']))
            self.assertEqual(web.count('class="show-teaching-step"'), len(lesson['steps']))
            self.assertNotIn('<iframe', web)
            for step in lesson['steps']:
                self.assertIn(step['observe'], plain)
                self.assertIn(step['explanation'], plain)

    @unittest.skipUnless(shutil.which('pandoc'), 'Pandoc is required for the HTML render contract')
    def test_pandoc_retains_scroll_markers_and_semantic_steps(self):
        source = '# Force\n' + block('01-force')
        html = subprocess.check_output(['pandoc', '--from=markdown', '--to=html5'], input=source, text=True)
        self.assertEqual(html.count('data-teaching-chapter="01-force"'), 4)
        self.assertEqual(html.count('data-teaching-step='), 4)
        self.assertNotIn('{{', html)


if __name__ == '__main__':
    unittest.main()
