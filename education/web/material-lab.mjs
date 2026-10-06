import {MATERIAL_DEFAULTS,compressionPair,evaluateCompressionCandidate} from './material-response.mjs';
const pretty=v=>Number(v).toPrecision(6);
export function materialSvg(pair,stacked=false){
 const scale=2400,y0=270;
 const panel=(s,cx)=>{
  const w=s.widthM*scale,h=s.heightM*scale,r=pair.reference;
  const rw=r.widthM*scale,rh=r.heightM*scale;
  return `<g data-boundary="${s.boundary}"><text x="${cx}" y="32" text-anchor="middle" font-size="18">${s.boundary==='free'?'Free lateral surfaces':'Rigid lateral walls (pull-away allowed)'}</text><rect x="${cx-rw/2}" y="${y0-rh}" width="${rw}" height="${rh}" fill="none" stroke="#77859a" stroke-dasharray="5 4"/><rect class="specimen" x="${cx-w/2}" y="${y0-h}" width="${w}" height="${h}" fill="#339bd9" fill-opacity=".3" stroke="#1474b1" stroke-width="2"/><path d="M${cx-w/2-12} ${y0-h}H${cx+w/2+12}M${cx-w/2-12} ${y0}H${cx+w/2+12}" stroke="#936700" stroke-width="5"/>${s.boundary==='confined'?`<path d="M${cx-rw/2-3} ${y0-rh-10}V${y0+10}M${cx+rw/2+3} ${y0-rh-10}V${y0+10}" stroke="${s.wallActive?'#c53e48':'#526479'}" stroke-width="5"/>`:''}<text x="${cx}" y="310" text-anchor="middle" font-size="16">b=${pretty(s.b)}; J=${pretty(s.J)}</text><text x="${cx}" y="337" text-anchor="middle" font-size="16">Plate force ${pretty(s.plateForceN)} N</text></g>`;
 };
 const width=stacked?440:880,height=stacked?800:400;
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Solved free-side and rigid-wall specimens at the same prescribed height; common fixed physical scale"><rect width="${width}" height="${height}" fill="#f4f7fb"/>${panel(pair.free,220)}${stacked?`<g transform="translate(0 400)">${panel(pair.confined,220)}</g>`:panel(pair.confined,660)}<text x="${width/2}" y="${height-27}" text-anchor="middle" font-size="16">Front view. Dashed: reference. Gold: plates.</text><text x="${width/2}" y="${height-6}" text-anchor="middle" font-size="16">Both depths also scale by b; same physical scale.</text></svg>`;
}
export class MaterialLab{
 constructor(root){
  this.root=root;this.params={...MATERIAL_DEFAULTS};this.pair=compressionPair(this.params);
  root.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>this.change(input)));
  root.querySelector('[data-action=reset]').addEventListener('click',()=>{this.params={...MATERIAL_DEFAULTS};this.pair=compressionPair(this.params);root.querySelectorAll('[data-param]').forEach(i=>{i.value=this.params[i.dataset.param];i.removeAttribute('aria-invalid');});root.querySelector('.announce').textContent='Defaults restored.';this.render();});
  root.querySelector('[data-action=summary]').addEventListener('click',()=>{root.querySelector('.announce').textContent=root.querySelector('.readout').innerText;});
  root.querySelector('[data-action=copy]').addEventListener('click',()=>{const box=root.querySelector('.preset');box.hidden=false;box.value=JSON.stringify({schema:1,lesson:'material-compression',...this.pair},null,2);box.focus();box.select();});
  root.querySelector('[data-action=candidate]').addEventListener('click',()=>{
   const candidate=evaluateCompressionCandidate(this.params,1/Math.sqrt(this.params.heightStretch),'confined');
   root.querySelector('.announce').textContent=candidate.accepted?'At h = 1 the isochoric candidate fits the walls. Current solved state retained.':`Rejected isochoric wall candidate: ${candidate.reason}; J=${pretty(candidate.J)} but X-wall penetration=${pretty(candidate.penetrationXM)} m. Current solved state retained.`;
  });
  this.observer=new ResizeObserver(()=>this.render());this.observer.observe(root);
  root.dataset.enhanced='true';this.render();
 }
 change(input){
  const value=Number(input.value),key=input.dataset.param;
  if(input.value===''||!input.checkValidity()||!Number.isFinite(value)){input.setAttribute('aria-invalid','true');this.root.querySelector('.announce').textContent='Invalid input; prior specimen retained.';return;}
  let pair;const candidate={...this.params,[key]:value};
  try{pair=compressionPair(candidate);}catch{input.setAttribute('aria-invalid','true');this.root.querySelector('.announce').textContent='Outside declared domain; prior specimen retained.';return;}
  input.removeAttribute('aria-invalid');this.params=candidate;this.pair=pair;
  this.root.querySelectorAll(`[data-param="${key}"]`).forEach(i=>{if(i!==input)i.value=value;});this.render();
  this.root.querySelector('.announce').textContent='Parameters applied to both boundary conditions; height is shared. Inspect the residual status below.';
 }
 render(){
  const pair=this.pair;
  this.root.querySelector('.property-scene').innerHTML=materialSvg(pair,this.root.clientWidth<660);
  const rows=[['Lateral stretch b','b',''],['Volume ratio J = V/V₀','J',''],['Volume','volumeM3','m³'],['Elastic energy','energyJ','J'],['Bulk energy','bulkEnergyJ','J'],['Shear energy','shearEnergyJ','J'],['Plate force (compression positive)','plateForceN','N'],['Plate pressure (current area)','platePressurePa','Pa'],['Lateral equilibrium residual','lateralResidualPa','Pa'],['Wall pressure (current area)','wallPressurePa','Pa'],['Force per X wall','wallForceXN','N'],['Force per Z wall','wallForceZN','N'],['Clearance per X wall','gapXM','m'],['Clearance per Z wall','gapZM','m'],['Wall complementarity work','complementarityJ','J']];
  const cell=(s,key,unit)=>s[key]===null?'No wall':`${pretty(s[key])} ${unit}`;
  this.root.querySelector('.readout').innerHTML=rows.map(([label,key,unit])=>`<div><dt>${label}</dt><dd>Free: ${cell(pair.free,key,unit)}; confined: ${cell(pair.confined,key,unit)}</dd></div>`).join('')+
   `<div><dt>Solve status</dt><dd>Free: ${pair.free.converged?'residual criterion met':'finite approximation; residual criterion NOT met'}; confined: ${pair.confined.converged?'residual criterion met':'finite approximation; residual criterion NOT met'}. Criterion |Pₓ + R| ≤ ${pair.solve.residualCriterionPa} Pa. Free ${pair.solve.free.iterations}/${pair.solve.free.cap} bisections, bracket width ${pretty(pair.solve.free.bracketWidth)}; confined ${pair.solve.confined.iterations}/${pair.solve.confined.cap}, width ${pretty(pair.solve.confined.bracketWidth)} (zero bisections at active walls or analytic endpoints).</dd></div><div><dt>Wall condition</dt><dd>${pair.confined.wallActive?'Compressive wall contact; b = 1':'No compressive contact; pull-away allowed (zero reaction)'}. Walls cannot pull the specimen outward.</dd></div><div><dt>Model validity</dt><dd>${pair.scope}. Positive stretches accepted; residual success is not material validation.</dd></div>`;
 }
}
if(typeof document!=='undefined')document.querySelectorAll('[data-material]').forEach(root=>new MaterialLab(root));
