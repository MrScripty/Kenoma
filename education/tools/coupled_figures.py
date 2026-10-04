"""Original numerical plot, generated from the coupled fixture's actual receipt."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1]
def generate(out):
    receipt=json.loads((ROOT/'data/anatomical-arm-v1/audit/coupling-results.json').read_text())
    run=receipt['runs'][0];rows=[{'timeS':0,'qRad':0,'activation':0}]+run['rows']
    x=lambda t:75+600*t/.48
    q=lambda a:300-240*a/(math.pi/4)
    activation=lambda a:300-240*a/.3
    points=lambda key,fn:' '.join(f"{x(r['timeS']):.3f},{fn(r[key]):.3f}" for r in rows)
    text=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 405" role="img" aria-labelledby="title desc"><title id="title">Actual coupled fixture lift and release</title><desc id="desc">Angle rises from zero, peaks at {run['peakQ']*180/math.pi:.3f} degrees, then decreases to {run['finalQ']*180/math.pi:.3f} degrees at 0.48 seconds. Activation falls after effort is released at 0.28 seconds. Synthetic geometry, no anatomical claim.</desc><rect width="760" height="405" fill="#fff"/><g font-family="Arial" font-size="16" fill="#173746"><text x="30" y="30" font-size="22">Coupled tissue / tendon / hinge: computed pulse</text><path d="M75 60V300H675" stroke="#456171" fill="none"/><path d="M425 60V300" stroke="#999" stroke-dasharray="5 4"/><text x="436" y="80">Release effort</text><polyline points="{points('qRad',q)}" fill="none" stroke="#b74a42" stroke-width="3"/><polyline points="{points('activation',activation)}" fill="none" stroke="#176c82" stroke-width="3"/><text x="20" y="67">45°</text><text x="35" y="305">0°</text><text x="684" y="67">a=.3</text><text x="684" y="305">a=0</text><text x="71" y="326">0</text><text x="645" y="326">0.48 s</text><text x="90" y="355" fill="#b74a42">Coral: flexion angle (left scale)</text><text x="390" y="355" fill="#176c82">Blue: activation (right scale)</text><text x="30" y="387">h=0.04 s; 0.5 kg; effort .25 then 0; authored P2 fixture, no skin/contact</text></g></svg>'''
    (out/'coupled-pulse.svg').write_text(text)
