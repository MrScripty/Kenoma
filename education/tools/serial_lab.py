"""Production controls for two separate homogeneous blocks in axial series."""
import html

def block(key='assembly',web=True):
    if isinstance(key,bool):web=key;key='assembly'
    if key not in ('assembly','serial'):raise ValueError('Unknown serial specimen lesson')
    title='Property lab 6 · Force, current area and local volume'
    caption='Two separate homogeneous square prisms in axial series, with ideal bilateral traction-distributing fixtures that allow lateral sliding. A fixed-length massless spacer moves with their ends. This is an assembly of two blocks, not a continuous stepped solid.'
    if not web:return f'\n### {title}\n\n{caption}\n\n[Open the physical-scale assembly](index.html#lab-serial-specimen).\n'
    fields=''
    for param,label,low,high,step,value in [('force','Signed target applied force N (N)',-.1,.1,.005,.1),('length','Each block reference length L0 (m)',.01,.04,.001,.025),('area','Block 1 reference area A1 (m²)',.0003,.001,.00001,.0003),('ratio','Reference area ratio A2/A1',.5,4,.1,2),('mu','Shear modulus μ (Pa)',500,5000,100,1500)]:
        fields+=f'<div class="control"><label for="serial-{param}">{label}</label><div class="input-pair"><input type="range" aria-label="{label} slider" data-param="{param}" min="{low}" max="{high}" step="{step}" value="{value}"><input id="serial-{param}" type="number" data-param="{param}" min="{low}" max="{high}" step="{step}" value="{value}"></div></div>'
    fields+='<div class="control"><label for="serial-iterations">Maximum bisection iterations</label><select id="serial-iterations" data-param="iterations">'+''.join(f'<option value="{n}"'+(' selected' if n==48 else '')+f'>{n}</option>' for n in [8,16,32,48,64])+'</select></div>'
    reference='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 260" role="img" aria-label="Static undeformed default reference: two separate blocks and a fixed length spacer"><rect width="640" height="260" fill="#f4f7fb"/><text x="24" y="32" fill="#152e41">Static undeformed default reference · not the current solution</text><g fill="none" stroke="#65808f" stroke-width="2"><rect x="100" y="100.55" width="85" height="58.9"/><rect x="225.8" y="88.36" width="85" height="83.28"/></g><path d="M185 130H225.8" stroke="#a56816" stroke-width="3"/><path d="M100 89V171M185 89V171M225.8 77V183M310.8 77V183" stroke="#233f48" stroke-width="2"/><text x="108" y="196" fill="#152e41">Block 1</text><text x="230" y="196" fill="#152e41">Block 2</text><path d="M430 130h34" stroke="#152e41" stroke-width="2"/><text x="412" y="158" fill="#152e41">0.01 m</text><text x="24" y="235" fill="#152e41">Each reference length 0.025 m; spacer length 0.012 m</text></svg>'''
    return f'''
<section class="laboratory serial-lesson" data-serial="assembly" id="lab-serial-specimen" aria-labelledby="serial-heading">
<h3 id="serial-heading">{title}</h3><p class="model-label">{caption}</p>
<p>Default reference length L0 = 0.025 m for each block; the length control changes both reference lengths. Exact incompressibility is a constitutive assumption: b = 1/√λ and J = λb² = 1. The pressure multiplier p = μ/λ makes the lateral Cauchy stresses zero. Closed-mesh volumes are measured separately; their constancy does not choose the axial equilibrium.</p>
<p>Static parameter edits reevaluate the displayed signed force. Reference geometry edits define a new specimen, so its reference volume can change. Invalid inputs retain the last valid state. A low root cap shows its actual force mismatch; it does not qualify equilibrium.</p>
<div class="scene-toolbar"><button type="button" data-action="start">Start interactive 3D</button><button type="button" data-action="front">Front view</button><button type="button" data-action="oblique">Oblique view</button></div><p class="scene-notice"></p>
<figure class="static-figure">{reference}<figcaption>Static undeformed reference. Current numerical results appear below; this diagram does not move.</figcaption></figure><div class="scene-host" hidden></div>
<p class="serial-scale">Live mesh coordinates are metres with no displacement magnification. Fixed physical camera; grid spacing 0.01 m. Gray wireframes show reference blocks; dark outlines are ideal sliding fixtures; gold line is the fixed 0.012 m spacer. Only block volumes are counted. Force arrows show equal and opposite <strong>target applied N</strong>, at a fixed 0.1 N → 0.02 m symbol scale; low-cap cell resultants are reported separately. Colours use a fixed strain scale: compression −0.4, neutral 0, extension +0.75.</p>
<p class="serial-scale">Drag the live canvas to orbit; right-drag to pan. Front and Oblique restore fixed comparison views. Two homogeneous constrained scalar roots, not a 3D mesh solver, continuous interface solution, unrestricted stability result or anatomical calibration.</p>
<div class="controls">{fields}</div>
<div class="actions"><button type="button" data-action="reset">Reset defaults</button><button type="button" data-action="reject-volume">Test total-volume-only candidate</button><button type="button" data-action="export">Download current state</button><button type="button" data-action="copy">Show state JSON</button><button type="button" data-action="summary">Read current results</button></div>
<p class="serial-solve-status"></p><dl class="readout serial-totals" aria-label="Whole assembly SI results"></dl><div class="serial-cells"></div><p class="serial-candidate" hidden></p>
<p class="announce" role="status" aria-live="polite"></p><textarea class="preset" aria-label="Current static parameters, scalar roots and measured three-dimensional geometry" readonly hidden></textarea>
<noscript>JavaScript is required for the controls and live 3D. The undeformed reference above is static; read the adjacent constitutive equations and equilibrium table for the worked solution.</noscript>
</section>
'''
