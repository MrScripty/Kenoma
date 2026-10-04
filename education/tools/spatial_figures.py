"""Original vector diagrams rendered from the actual solved, authored meshes."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def generate(folder,spatial):
 def svg(body,title,description):return '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="640" viewBox="0 0 960 640" role="img"><title>'+html.escape(title)+'</title><desc>'+html.escape(description)+'</desc><rect width="960" height="640" fill="#f4f8fa"/>'+body+'</svg>'
 def project(X,offset,scale,yshift):return (offset+scale*(X[0]+.22*X[2]),yshift-scale*(X[1]+.12*X[2]))
 def poly(X,faces,offset,scale,yshift,color,opacity):
  result=''
  for f in sorted(faces,key=lambda f:sum(X[i][2] for i in f)):
   points=' '.join(f'{x:.2f},{y:.2f}' for x,y in [project(X[i],offset,scale,yshift) for i in f]);result+=f'<polygon points="{points}" fill="{color}" fill-opacity="{opacity}" stroke="#314958" stroke-width=".65"/>'
  return result
 r=spatial['reference'];m=spatial['mesh'];q=3.141592653589793/2
 body='<text x="30" y="34" font-family="sans-serif" font-size="25">Muscle under a separate skin membrane · same q = 90°</text>'
 for X,offset,label,color in [(r['x'],135,'Mechanical volume + skin','#ef8c74'),(r['baseline'],580,'Naive linear blend skinning','#bdcaff')]:
  body+=f'<text x="{offset-105}" y="72" font-family="sans-serif" font-size="21">{label}</text>'
  # Bones use the SAME rigid geometry and pose on both sides, SI scale 1000 px/m.
  body+=f'<path d="M{offset} 370V100 M{offset} 370H{offset+350}" fill="none" stroke="#e2c48e" stroke-width="38" stroke-linecap="round"/>'
  body+=poly(X,m['surface'],offset,1000,370,color,.7)+poly(X,m['skinSurface'],offset,1000,370,'#70cdbc',.09)
  fibre=' '.join(f'{x:.2f},{y:.2f}' for x,y in [project(X[i],offset,1000,370) for i in [4,13,22,31,40]])
  body+=f'<polyline points="{fibre}" fill="none" stroke="#ce3028" stroke-width="4"/>'
  p0,p1=project(X[40],offset,1000,370),project(X[49],offset,1000,370);body+=f'<path d="M{p0[0]} {p0[1]}L{p1[0]} {p1[1]}" stroke="#ba831c" stroke-width="4"/>'
  body+=f'<path d="M{offset+340} 348V392 M{offset+360} 348V392" stroke="#4b5962" stroke-width="12"/>'
  text=f"Min J {r['minJ']:.3f}; mean J {r['meanJ']:.3f}" if X is r['x'] else f"Min J {r['baselineMinJ']:.3f}; mean J {r['baselineMeanJ']:.3f}"
  body+=f'<text x="{offset-110}" y="500" font-family="sans-serif" font-size="20">{text}</text>'
 for c in r['contacts']:
  x,y=project(c['point'],135,1000,370);body+=f'<circle cx="{x}" cy="{y}" r="4" fill="#8a6000"/>'
 body+='<text x="35" y="545" font-family="sans-serif" font-size="19">Coral: tissue · Red: active span · Gold: tendon/bones · Mint: separate skin</text>'+f'<text x="35" y="579" font-family="sans-serif" font-size="19">Sampled penetration: {r["penetrationM"]*1000:.4f} mm mechanical / {r["baselinePenetrationM"]*1000:.4f} mm LBS</text>'+ '<text x="35" y="613" font-family="sans-serif" font-size="18">Schematic geometry · one-way quasistatic solve · finite iterations · not medical pressure</text>'
 (folder/'spatial.svg').write_text(svg(body,'Spatial arm contact comparison','Actual solved schematic mesh with separate skin and identical posed bones. Numerical values retain SI units.'))
 example=json.loads((ROOT/'contributions/continuum_reference/data/example.json').read_text());nodes=example['nodes'];faces=[f['tri'] for f in example['surface']]
 body='<text x="30" y="34" font-family="sans-serif" font-size="25">The same spatial implicit target, solved two ways</text>'
 states=[(example['implicit'],100,'Converged FEM reference','#70cdbc'),(next(s for s in example['compliant'] if s['sweeps']==5),560,'Five compliant strain sweeps','#bdcaff')]
 for state,offset,label,color in states:
  u=state['u'];X=[[v+50*u[3*i+d] for d,v in enumerate(node)] for i,node in enumerate(nodes)]
  body+=f'<text x="{offset-60}" y="95" font-family="sans-serif" font-size="22">{label}</text>'+poly(X,faces,offset,7000,400,color,.8)
  body+=f'<path d="M{offset} 400V260" stroke="#ba831c" stroke-width="7"/>'
 body+='<text x="35" y="490" font-family="sans-serif" font-size="21">40 × 20 × 20 mm · E = 100 kPa · ν = 0.25 · h = 0.0005 s</text><text x="35" y="535" font-family="sans-serif" font-size="21">Both from rest · 64 nodes / 162 tetrahedra · displacement display 50×</text><text x="35" y="580" font-family="sans-serif" font-size="20">Small-strain authored fixture · no contact · unscaled errors in worked tables</text>'
 (folder/'continuum.svg').write_text(svg(body,'Matched FEM and compliant solve','Both mesh states use the same load, initial state, timestep and common displacement magnification.'))
