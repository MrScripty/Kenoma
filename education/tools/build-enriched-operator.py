"""Isolate six extra nodal modes without changing source-bound web operators.

Generated copies keep the original solver/contact/material code. The only
edits generalize body dimensions and rotate the extra vector modes in the
existing search retraction. This is an experimental operator, not the viewer.
"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/enriched'
NAMES=['anatomical-apparatus','anatomical-aponeurosis','anatomical-retraction','anatomical-contact','anatomical-contact-refinement','anatomical-arm']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace(text,old,new):
    if old not in text:raise ValueError('Expected original operator text missing: '+old)
    return text.replace(old,new)
def build():
    OUT.mkdir(exist_ok=True)
    records={}
    for name in NAMES:
        source=ROOT/'web'/f'{name}.mjs';s=source.read_text()
        if name=='anatomical-apparatus':
            s=replace(s,'new Float64Array(63)','new Float64Array(body.modal.ndof)')
            s=replace(s,'offset:63*i','offset:g.muscles.slice(0,i).reduce((n,previous)=>n+(previous.element_id===\'FJ1512\'?69:63),0)')
            s=replace(s,'ndof:bodies.length*63','ndof:bodies.reduce((n,b)=>n+b.modal.ndof,0)')
            s=replace(s,'x.slice(b.offset,b.offset+63)','x.slice(b.offset,b.offset+b.modal.ndof)')
            s=replace(s,'i<63','i<b.modal.ndof')
            s=replace(s,'j<63','j<b.modal.ndof')
            s=replace(s,'i*63+j','i*b.modal.ndof+j')
            s=replace(s,'63 P2 Galerkin displacement modes per head; no full nodal convergence claim.','63 base P2 Galerkin modes per head plus 6 selected nodal coefficients in short biceps; no full nodal convergence claim.')
            s=replace(s,'x.slice(b.offset,b.offset+63)','x.slice(b.offset,b.offset+b.modal.ndof)') if 'x.slice(b.offset,b.offset+63)' in s else s
        elif name=='anatomical-aponeurosis':
            s=replace(s,'new Float64Array(63)','new Float64Array(body.ndof)')
            s=replace(s,'const n=63','const n=body.ndof')
        elif name=='anatomical-retraction':
            s=replace(s,'inside the unchanged 63-mode P2 space.','inside the frozen enriched P2 space.')
            s=replace(s,'new Float64Array(63),m=body.source','new Float64Array(body.ndof),m=body.source')
            s=replace(s,'}return result;}','}for(let base=63;base<body.ndof;base+=3){const remainder=rotationRemainder(Array.from(coordinates.slice(base,base+3)),omega,step);for(let d=0;d<3;d++)result[base+d]=remainder[d];}return result;}')
            s=replace(s,'b.offset+63','b.offset+b.modal.ndof')
            s=replace(s,'strain=new Float64Array(63)','strain=new Float64Array(b.modal.ndof)')
            s=replace(s,'}return {body:b,x,strain,...fit};','}for(let base=63;base<b.modal.ndof;base+=3){const spin=cross(fit.omega,Array.from(x.slice(base,base+3)));for(let k=0;k<3;k++)strain[base+k]=d[base+k]-spin[k];}return {body:b,x,strain,...fit};')
            s=replace(s,'base<63','base<s.body.modal.ndof')
            s=replace(s,'i<63','i<s.body.modal.ndof')
        def link(m):
            target=m[1];local=target.removesuffix('.mjs') in NAMES or target=='anatomical-modal.mjs'
            return "from '"+('./' if local else '../../web/')+target+"'"
        s=re.sub(r"from '\./([^']+)'",link,s)
        output=OUT/f'{name}.mjs';output.write_text('// Generated experiment copy; see tools/build-enriched-operator.py.\n'+s)
        records[str(source.relative_to(ROOT))]={'sourceSHA256':digest(source),'experimentPath':str(output.relative_to(ROOT)),'experimentSHA256':digest(output)}
    (OUT/'source-manifest.json').write_text(json.dumps({'schema':1,'generatorSHA256':digest(Path(__file__)),'files':records,'limits':['Original web operators remain byte-identical.','Six orthogonal nodal vector coefficients are added only to short biceps; no material, Newton iteration or acceptance assumption changes.']},indent=2)+'\n')
    print('Generated isolated enriched operator copies')
if __name__=='__main__':build()
