"""A repeated actual render must exclude stale owned PDF page images."""
from pathlib import Path
import json,shutil,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_property_integration import inspect as inspect_properties,ROOT
from inspect_compression_integration import inspect as inspect_compression
def run():
    for folder,inspector in [('property-book-review',inspect_properties),('compression-book-review',inspect_compression)]:check(folder,inspector)
def check(folder,inspect):
    out=ROOT/'dist'/folder;ghost=out/'pdf-page-999.png'
    seed=next(out.glob('pdf-page-*.png'));shutil.copy2(seed,ghost)
    inspect();receipt=json.loads((out/'render-receipt.json').read_text())
    assert ghost.name not in receipt['outputs'],'stale page image was relabelled as a fresh render output'
    assert not ghost.exists(),'owned stale page image survived the rerun'
    assert {p['image'] for p in receipt['pdf_pages']}=={name for name in receipt['outputs'] if name.startswith('pdf-page-')}
    print('PASS_FRESH_RENDER_RERUN_COVERAGE',folder)
if __name__=='__main__':run()
