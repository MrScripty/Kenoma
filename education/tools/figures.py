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
    svg('Schematic articulated elbow initial pose at thirty degrees', '''
<path class="line" d="M300 48V130 L350 216"/><circle cx="300" cy="130" r="10" class="teal"/>
<path stroke="#ff876f" stroke-width="5" d="M300 65L316 158"/><ellipse cx="308" cy="107" rx="13" ry="28" fill="#d95f4b"/>
<circle cx="300" cy="65" r="5" fill="#ffc66d"/><circle cx="316" cy="158" r="5" fill="#ffc66d"/>
<path stroke="#71818b" stroke-width="12" d="M331 216H369"/><path class="force" d="M350 223V251"/>
<text x="35" y="30">Force-driven hinge • q₀ = 30° • u = 0.6 • a₀ = 0</text>
<text x="390" y="85">Synthetic flexor line</text><text x="390" y="114" class="small">Rigid tendon; no contact model</text>
<text x="390" y="160">Dumbbell = 5 kg</text><text x="35" y="216" class="small">Authored schematic geometry</text><text x="35" y="238" class="small">No anatomical measurements</text>''',out/'elbow.svg')
    svg('Series actuator and affine tissue versus skinning at ninety degrees', '''
<text x="32" y="30">q = 90° • same pose • original schematic</text>
<text x="35" y="66">Coupled tissue block</text><text x="408" y="66">50/50 LBS baseline</text>
<path stroke="#e8cf9b" stroke-width="7" d="M45 110H285 M45 207H285 M415 110H655 M415 207H655"/>
<rect x="82" y="113" width="167" height="91" fill="#70e0cc"/><rect x="468" y="121" width="132" height="75" fill="none" stroke="#9bafff" stroke-width="4"/>
<text x="93" y="164" style="fill:#102d3a">J = 0.99290</text><text x="482" y="164">J = 0.50000</text>
<text x="40" y="236" class="small">N = 5.5027 N; pressure = 1064.75 Pa</text><text x="420" y="236" class="small">Force / pressure not modeled</text>''',out/'series.svg')
    (out/'figure-provenance.json').write_text(json.dumps({'schema':1,'creator':'Kenoma education contribution','license':'Apache-2.0','kind':'original schematic vector diagrams','anatomical_measurements':False,'generator':'tools/figures.py','figures':['force.svg','torque.svg','energy.svg','elbow.svg','series.svg']},indent=2)+'\n')
