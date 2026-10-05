"""A repeated actual render must exclude stale owned PDF page images."""
from pathlib import Path
import json,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_property_integration import inspect,ROOT
def run():
    out=ROOT/'dist/property-book-review';ghost=out/'pdf-page-999.png'
    seed=next(out.glob('pdf-page-*.png'));shutil.copy2(seed,ghost)
    inspect();receipt=json.loads((out/'render-receipt.json').read_text())
    assert ghost.name not in receipt['outputs'],'stale page image was relabelled as a fresh render output'
    assert not ghost.exists(),'owned stale page image survived the rerun'
    assert {p['image'] for p in receipt['pdf_pages']}=={name for name in receipt['outputs'] if name.startswith('pdf-page-')}
    print('PASS_FRESH_RENDER_RERUN_COVERAGE')
if __name__=='__main__':run()
