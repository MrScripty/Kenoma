import {DEFORMATION_DEFAULTS,ISOCHORIC_DEFAULTS,deformationState,isochoricState,measureTetrahedron,TETRAHEDRON_FACES,BOX_FACES} from './continuum-properties.mjs';
import {BAR_DEFAULTS,barState} from './tapered-bar.mjs';
const NS='http://www.w3.org/2000/svg';
const pretty=v=>v===0?'0':Number(v).toPrecision(6);
export function geometrySvg(state,faces){
 const all=[...state.reference,...state.current];
 const project=x=>[x[0]+.45*x[2],-x[1]-.3*x[2]],points=all.map(project);
 const min=[0,1].map(d=>Math.min(...points.map(p=>p[d]))),max=[0,1].map(d=>Math.max(...points.map(p=>p[d])));
 const scale=Math.min(500/(max[0]-min[0]||1),240/(max[1]-min[1]||1));
 const xy=x=>project(x).map((v,d)=>50+(v-min[d])*scale);
 return `<svg xmlns="${NS}" viewBox="0 0 620 360" role="img" aria-label="Reference gray and prescribed blue geometry; common physical scale"><rect width="620" height="360" fill="#f4f7fb"/>`+
 [state.reference,state.current].map((vertices,index)=>faces.map(face=>`<polygon points="${face.map(i=>xy(vertices[i]).join(',')).join(' ')}" fill="${index?'#339bd9':'#8896aa'}" fill-opacity="${index?.18:.06}" stroke="${index?'#1474b1':'#77859a'}" stroke-width="2"/>`).join('')).join('')+
 '<text x="30" y="330" fill="#26364b" font-size="17">Gray: reference. Blue: prescribed. SI readouts are unscaled.</text></svg>';
}
class PropertyLab{
 constructor(root){
  this.root=root;this.kind=root.dataset.property;this.defaults=this.kind==='deformation'?DEFORMATION_DEFAULTS:this.kind==='isochoric'?ISOCHORIC_DEFAULTS:BAR_DEFAULTS;this.params={...this.defaults};
  this.fn=this.kind==='deformation'?deformationState:this.kind==='isochoric'?isochoricState:barState;this.status=root.querySelector('.announce');this.state=this.fn(this.params);
  root.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>this.change(input)));
  root.querySelector('[data-action=reset]').addEventListener('click',()=>{this.params={...this.defaults};root.querySelectorAll('[data-param]').forEach(i=>{i.value=this.params[i.dataset.param];i.removeAttribute('aria-invalid');});this.state=this.fn(this.params);this.status.textContent='Defaults restored.';this.render();});
  root.querySelector('[data-action=summary]').addEventListener('click',()=>{this.status.textContent=root.querySelector('.readout').innerText;});
  root.querySelector('[data-action=copy]').addEventListener('click',()=>{const box=root.querySelector('.preset');box.hidden=false;box.value=JSON.stringify({schema:1,lesson:this.kind,parameters:this.params,measurements:this.state,scope:this.state.scope??'Prescribed kinematics; no force or equilibrium'},null,2);box.focus();box.select();});
  root.querySelector('[data-action=invert]')?.addEventListener('click',()=>{const candidate=this.state.current.map(x=>[...x]);[candidate[1],candidate[2]]=[candidate[2],candidate[1]];const measured=measureTetrahedron(this.state.reference,candidate);if(!measured.accepted)this.status.textContent=`Rejected inverted candidate: J=${pretty(measured.J)}, signed boundary volume=${pretty(measured.currentBoundary.signedVolumeM3)} m³. Prior valid state retained.`;});
  root.dataset.enhanced='true';this.render();
 }
 change(input){
  const key=input.dataset.param,value=input.tagName==='SELECT'?(['segments'].includes(key)?Number(input.value):input.value):input.valueAsNumber;
  if(input.value===''||!input.checkValidity()||(typeof value==='number'&&!Number.isFinite(value))){input.setAttribute('aria-invalid','true');return;}
  const candidate={...this.params,[key]:value};let state;
  try{state=this.fn(candidate);if(!state.accepted)throw new Error('Nonpositive orientation');}catch{input.setAttribute('aria-invalid','true');return;}
  input.removeAttribute('aria-invalid');this.params=candidate;this.state=state;
  this.root.querySelectorAll(`[data-param="${key}"]`).forEach(other=>{if(other!==input)other.value=value;});this.render();
 }
 renderBar(){
  const s=this.state,n=s.samples.length,m=Math.max(...s.samples.map(v=>Math.abs(v.strain)),1e-5),width=520/n;
  this.root.querySelector('.property-scene').innerHTML=`<svg xmlns="${NS}" viewBox="0 0 620 330" role="img" aria-label="Axial strain by position; blue extension and red compression"><rect width="620" height="330" fill="#f4f7fb"/><path d="M50 165H570" stroke="#526479"/>${s.samples.map((v,i)=>{const h=110*Math.abs(v.strain)/m;return `<rect x="${50+i*width}" y="${v.strain>=0?165-h:165}" width="${width}" height="${h}" fill="${v.strain>=0?'#1474b1':'#c53e48'}"/>`;}).join('')}<text x="50" y="25" font-size="17">Strain (dimensionless): scale ±${pretty(m)}</text><text x="50" y="310" font-size="16">0 → ${pretty(this.params.length)} m; blue extension, red compression</text></svg>`;
  const values=[['Constant resultant N (N)',s.resultantN],['Exact compliance (m/N)',s.exactComplianceMPerN],['Exact extension (m)',s.exactExtensionM],['Midpoint extension (m)',s.numericalExtensionM],['Extension error (m)',s.extensionErrorM],['Minimum strain (true area extrema)',s.minimumStrain],['Maximum strain (true area extrema)',s.maximumStrain]];
  this.root.querySelector('.readout').innerHTML=values.map(([label,value])=>`<div><dt>${label}</dt><dd>${pretty(value)}</dd></div>`).join('')+`<div><dt>Small-strain scope</dt><dd>${s.smallStrainWarning?'Exceeded 5% illustrative validity warning; reduced model remains unqualified':'Within 5% illustrative warning threshold; not a material validation'}</dd></div>`;
 }
 render(){
  const s=this.state;
  if(this.kind==='tapered'){this.renderBar();return;}
  this.root.querySelector('.property-scene').innerHTML=geometrySvg(s,this.kind==='deformation'?TETRAHEDRON_FACES:BOX_FACES);
  let values=[['det F (dimensionless)',s.J],['Independent boundary V / V₀',s.volumeRatio],['Boundary volume (m³)',s.currentBoundary.signedVolumeM3],['Volume-ratio disagreement',s.volumeMeasurementDifference]];
  if(this.kind==='deformation')values.push(['F (row major)',s.F.map(pretty).join(', ')],['Green strain (row major)',s.greenStrain.map(pretty).join(', ')]);
  else{values.push(['Lateral stretch b',s.lateralStretch],['Axial length (m)',s.lengthM],['Cross-section area (m²)',s.crossSectionAreaM2],['Exterior area (m²)',s.exteriorAreaM2],['Area × length (m³)',s.areaLengthVolumeM3]);this.root.querySelectorAll('[data-param=lateral]').forEach(i=>i.disabled=this.params.mode==='isochoric');}
  this.root.querySelector('.readout').innerHTML=values.map(([label,value])=>`<div><dt>${label}</dt><dd>${typeof value==='number'?pretty(value):value}</dd></div>`).join('');
 }
}
if(typeof document!=='undefined')document.querySelectorAll('[data-property]').forEach(root=>new PropertyLab(root));
