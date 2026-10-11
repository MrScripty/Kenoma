"""Author and package worked readings without changing a solver or proof receipt."""
from pathlib import Path
import html, json, re

ROOT = Path(__file__).resolve().parents[1]


def inventory():
    chapters = json.loads((ROOT / 'book/book.json').read_text())['chapters']
    result = []
    for chapter in chapters:
        ident = chapter.removesuffix('.md')
        lesson = json.loads((ROOT / 'book/examples/lessons' / (ident + '.json')).read_text())
        if lesson['chapter'] != ident or not 3 <= len(lesson['steps']) <= 5:
            raise ValueError('Incomplete teaching sequence: ' + ident)
        seen = set()
        for step in lesson['steps']:
            if not re.fullmatch('[a-z0-9-]+', step['id']) or step['id'] in seen:
                raise ValueError('Invalid teaching step: ' + ident)
            seen.add(step['id'])
            if not all(isinstance(step[k], str) and step[k].strip() for k in ['title', 'explanation', 'observe']):
                raise ValueError('A teaching step needs reasoning and an observable result: ' + ident)
            if not isinstance(step['parameters'], dict):
                raise ValueError('A teaching step needs explicit bounded parameters: ' + ident)
        if not all(lesson['audit'].get(k) for k in ['finding', 'change', 'remaining']):
            raise ValueError('Missing scientific audit: ' + ident)
        result.append(lesson)
    return result


def block(ident, web=True):
    lesson = next(lesson for lesson in inventory() if lesson['chapter'] == ident)
    e = html.escape
    if not web:
        return '\n\n## Worked reading\n\n' + '\n\n'.join(
            f"### {i + 1}. {step['title']}\n\n{step['explanation']}\n\n**Observe:** {step['observe']}"
            for i, step in enumerate(lesson['steps'])) + '\n\n'
    steps = []
    for i, step in enumerate(lesson['steps']):
        key = ident + '-' + step['id']
        steps.append(f'''<section class="teaching-step" id="step-{key}" data-teaching-chapter="{ident}" data-teaching-step="{step['id']}">
<div class="step-label">Worked example · {i + 1} / {len(lesson['steps'])}</div>
<h3>{e(step['title'])}</h3><p>{e(step['explanation'])}</p>
<p class="step-observe"><strong>Observe</strong> {e(step['observe'])}</p>
<button type="button" class="show-teaching-step" data-show-step="{key}" hidden>Show this step</button>
</section>''')
    return '\n\n<div class="teaching-sequence" aria-label="Worked reading">\n' + '\n'.join(steps) + '\n</div>\n\n'


def chapter_source(path):
    text = Path(path).read_text()
    heading, rest = text.split('\n', 1)
    return heading + '\n\n{{teaching:' + Path(path).stem + '}}\n' + rest


def package(out):
    lessons = inventory()
    (Path(out) / 'teaching-sequences.json').write_text(json.dumps({'version': 1, 'lessons': lessons}, indent=2) + '\n')
    return {'chapters': len(lessons), 'steps': sum(len(lesson['steps']) for lesson in lessons)}
