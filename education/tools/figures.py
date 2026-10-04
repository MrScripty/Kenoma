"""Original vector teaching diagrams. No anatomical geometry or external images."""
from pathlib import Path
import json

def svg(name,body,out):
    base='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 260" role="img"><title>'+name+'</title><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#ffc66d"/></marker></defs><style>text{font-family:Arial,sans-serif;fill:#e8f2f7;font-size:18px}.small{font-size:14px}.axis{stroke:#567183;stroke-width:1}.force{stroke:#ffc66d;stroke-width:4;marker-end:url(#arrow)}.line{stroke:#a2bdcf;stroke-width:8;stroke-linecap:round}.teal{fill:#70e0cc}</style><rect width="720" height="260" fill="#101d2c"/>'
    out.write_text(base+body+'</svg>')

def generate(out):
    out.mkdir(parents=True,exist_ok=True)
    svg('Force laboratory reference state at one second', '''
<path class="axis" d="M65 150H650 M100 190V65"/><text x="658" y="156">x</text><text x="93" y="52">y</text>
<circle cx="100" cy="150" r="7" fill="#a2bdcf"/><text x="76" y="213" class="small">x₀ = 0</text>
<path stroke="#70e0cc" stroke-dasharray="5 5" d="M100 150H360"/>
<circle cx="360" cy="150" r="22" class="teal"/><path class="force" d="M386 150H500"/>
<text x="420" y="124">F = 4 N</text><text x="300" y="213">x(1 s) = 1 m</text>
<text x="38" y="32">Constant net force • m = 2 kg • starts from rest</text>
<text x="500" y="220" class="small">Schematic xy plane</text>''',out/'force.svg')
    svg('Torque laboratory reference state at horizontal angle', '''
<path class="axis" d="M75 135H630 M120 230V65"/><text x="642" y="140">x</text><text x="113" y="52">y</text>
<path class="line" d="M120 135H470"/><circle cx="120" cy="135" r="14" fill="#a2bdcf"/><circle cx="470" cy="135" r="22" class="teal"/>
<path class="force" d="M470 163V238"/><text x="492" y="215">Fᵧ = -49.05 N</text>
<path stroke="#fff" d="M125 91H467 M125 85V97 M467 85V97"/><text x="235" y="78">L = 0.30 m</text>
<text x="38" y="32">Posed massless lever • m = 5 kg • θ = 0°</text><text x="72" y="183" class="small">pivot</text>
<text x="65" y="228">τz = -14.715 N m</text>''',out/'torque.svg')
    pts=' '.join(f'{110+i*3.2:.1f},{130+(0 if i in [0,100] else (12 if (i//3)%2 else -12))}' for i in range(101))
    svg('Energy laboratory initial spring state',f'''
<path class="axis" d="M75 160H630"/><path class="line" d="M105 70V170"/>
<polyline fill="none" stroke="#a2bdcf" stroke-width="3" points="{pts}"/>
<circle cx="430" cy="130" r="24" class="teal"/><path stroke="#fff" stroke-dasharray="5 5" d="M380 180V98"/>
<path stroke="#70e0cc" stroke-width="2" d="M380 195H430 M380 189V201 M430 189V201"/>
<text x="328" y="227">x₀ = 0.20 m; v₀ = 0 m/s</text>
<text x="38" y="32">Linear spring • m = 1 kg • k = 40 N/m • E₀ = 0.80 J</text>
<text x="54" y="222" class="small">Extension exaggerated</text><text x="490" y="134">mass</text>''',out/'energy.svg')
    (out/'figure-provenance.json').write_text(json.dumps({'schema':1,'creator':'Kenoma education contribution','license':'Apache-2.0','kind':'original schematic vector diagrams','anatomical_measurements':False,'generator':'tools/figures.py','figures':['force.svg','torque.svg','energy.svg']},indent=2)+'\n')
