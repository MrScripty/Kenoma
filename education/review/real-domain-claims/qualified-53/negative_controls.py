"""Reject damaged copies of the genuine final Real render evidence."""
from pathlib import Path
import copy, json, shutil, sys, tempfile
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from check_real_lesson_artifact import check
from check_real_lesson_proofs import FAMILIES

def run():
    dist = ROOT / 'dist'
    check(dist)
    rows = []
    with tempfile.TemporaryDirectory(prefix='kenoma-real-negative-') as directory:
        target = Path(directory)
        for name in ['index.html', 'assets/app.js', 'kenoma-mechanics.pdf', 'build-manifest.json'] + [p + '-proof-status.json' for _, _, p, _ in FAMILIES]:
            path = target / name; path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dist / name, path)
        shutil.copytree(dist / 'real-proof-review', target / 'real-proof-review')
        folder = target / 'real-proof-review'
        receipt_path = folder / 'render-receipt.json'
        original = json.loads(receipt_path.read_text())
        mutations = [
            ('false mobile overflow', lambda r: r['views'][1].update(horizontal_overflow=True)),
            ('missing claim coverage', lambda r: r['real_claims'].pop()),
            ('stale PDF digest', lambda r: r.update(pdf_sha256='0' * 64)),
            ('missing source continuation', lambda r: (r['outputs'].pop(r['source_pages'][-2]['image']), r['source_pages'].pop(-2))),
        ]
        for name, mutate in mutations:
            receipt = copy.deepcopy(original); mutate(receipt)
            receipt_path.write_text(json.dumps(receipt))
            try: check(target)
            except (AssertionError, FileNotFoundError, KeyError) as error:
                rows.append({'case': name, 'result': 'REJECTED', 'reason': str(error)})
            else: raise RuntimeError('Damaged evidence accepted: ' + name)
        receipt_path.write_text(json.dumps(original))
        image = folder / next(iter(original['outputs']))
        image.write_bytes(image.read_bytes() + b'changed image')
        try: check(target)
        except AssertionError as error:
            rows.append({'case': 'changed PNG bytes', 'result': 'REJECTED', 'reason': str(error)})
        else: raise RuntimeError('Changed PNG accepted')
    check(dist)
    result = {'result': 'PASS_FIVE_REAL_RENDER_NEGATIVE_CONTROLS', 'source_revision': original['source_revision'], 'cases': rows}
    Path(__file__).with_name('negative-controls.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__': run()
