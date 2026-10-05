import fs from 'node:fs';
import crypto from 'node:crypto';
import {deformationState,isochoricState,DEFORMATION_DEFAULTS,ISOCHORIC_DEFAULTS,TETRAHEDRON_FACES,BOX_FACES} from '../web/continuum-properties.mjs';
import {barState,BAR_DEFAULTS} from '../web/tapered-bar.mjs';
import {geometrySvg} from '../web/property-labs.mjs';
const assets=process.argv[2],out=process.argv[3];
const deformation=deformationState(),isochoric=isochoricState();
const rows=[8,16,32,64,128].map(segments=>({segments,...barState({...BAR_DEFAULTS,segments})}));
const active=barState({...BAR_DEFAULTS,shape:'two-segment',mode:'active-fixed',segments:2});
const inputs=['web/continuum-properties.mjs','web/tapered-bar.mjs','web/property-labs.mjs','tools/property-experiment.mjs'];
const receipt={schema:1,node:process.version,inputs:Object.fromEntries(inputs.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')])),defaults:{deformation:DEFORMATION_DEFAULTS,isochoric:ISOCHORIC_DEFAULTS,bar:BAR_DEFAULTS},deformation,isochoric,taperRefinement:rows,activeTwoSegment:active,scope:'Prescribed kinematics and reduced small-strain axial bar; separate independent oracles; no anatomical qualification'};
if(assets){fs.mkdirSync(assets,{recursive:true});fs.writeFileSync(`${assets}/property-deformation.svg`,geometrySvg(deformation,TETRAHEDRON_FACES));fs.writeFileSync(`${assets}/property-isochoric.svg`,geometrySvg(isochoric,BOX_FACES));
 const bars=active.samples.map((v,i)=>`<rect x="${100+i*220}" y="${v.strain>0?70:180}" width="180" height="110" fill="${v.strain>0?'#1474b1':'#c53e48'}"/><text x="${100+i*220}" y="${v.strain>0?50:315}" font-size="19">${v.strain>0?'+':'−'}1/300 strain</text>`).join('');fs.writeFileSync(`${assets}/property-tapered.svg`,`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 360" role="img" aria-label="Two fixed-end segments: narrow extends, wide compresses"><rect width="620" height="360" fill="#f4f7fb"/><path d="M60 180H570" stroke="#526479"/>${bars}<text x="70" y="345" font-size="17">Equal lengths; A₂ = 2A₁; total extension = 0</text></svg>`);}
if(out)fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');else process.stdout.write(JSON.stringify(receipt,null,2)+'\n');
