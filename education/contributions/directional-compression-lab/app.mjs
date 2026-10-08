import {DEFAULTS,specimen} from './model.mjs';
import {sceneMarkup} from './view.mjs';
let parameters={...DEFAULTS},result=specimen(parameters);
const root=document.querySelector('main'),status=document.querySelector('#status'),pretty=x=>Number(x).toPrecision(7);
document.querySelectorAll('input,select,button').forEach(input=>input.disabled=false);
const rows=[['Width X (m)',s=>s.dimensionsM[0]],['Height Y (m)',s=>s.dimensionsM[1]],['Depth Z (m)',s=>s.dimensionsM[2]],['J, dimensionless',s=>s.J],['Independent boundary V/V0',s=>s.independentVolumeRatio],['Stored energy U (J)',s=>s.energyJ],['End resultant Nx (N), tension positive',s=>s.endResultantN],['One-face transverse resultant C (N), compression positive',s=>s.compressionResultantN],['Applied current-area normal traction q (Pa), compression positive',s=>s.contactPressurePa],['Reference controlled-face area (m²)',s=>s.referenceAreaM2],['Current controlled-face area (m²)',s=>s.currentAreaM2],['Free normal Pi residual (Pa)',s=>s.freeResidualPa]];
function render(){
 const s=result.state;document.querySelector('#scene').innerHTML=sceneMarkup(s);
 document.querySelector('#readout').innerHTML=rows.map(([label,fn])=>`<div><dt>${label}</dt><dd>${pretty(fn(s))}</dd></div>`).join('')+`<div><dt>Scalar free-face criterion</dt><dd>${s.converged?'MET':'FAILED'}: |Pfree| ≤ ${s.solve.residualCriterionPa} Pa; ${s.solve.used}/${s.solve.cap} bisections</dd></div><div><dt>Control faces</dt><dd>Fixed X length; ${parameters.direction} bilateral displacement grips; ${result.freeAxis===1?'Y':'Z'} traction-free</dd></div><div><dt>Tensile grip required?</dt><dd>${s.requiresTensileGrip?'YES: this state needs an attached grip that can pull; compression-only contact cannot produce it':'No: the imposed face resultant is compressive or zero'}</dd></div><div><dt>End force at h=1, same X stretch (N)</dt><dd>${pretty(result.baselineEndResultantN)}</dd></div><div><dt>Change in signed end force from that baseline (N)</dt><dd>${pretty(result.changeInEndResultantN)}</dd></div>`;
 root.dataset.ready='true';window.labResult=result;
}
document.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>{
 const value=input.tagName==='SELECT'?(input.dataset.param==='iterations'?Number(input.value):input.value):input.valueAsNumber;
 if(input.value===''||!input.checkValidity()){input.setAttribute('aria-invalid','true');status.textContent='Invalid control: previous valid state retained.';return;}
 try{const candidate={...parameters,[input.dataset.param]:value},next=specimen(candidate);parameters=candidate;result=next;input.removeAttribute('aria-invalid');status.textContent='Updated passive specimen. Read the residual and grip signs.';render();}
 catch{input.setAttribute('aria-invalid','true');status.textContent='Out-of-domain control: previous valid state retained.';}
}));
document.querySelector('#reset').addEventListener('click',()=>{parameters={...DEFAULTS};result=specimen(parameters);document.querySelectorAll('[data-param]').forEach(i=>{i.value=parameters[i.dataset.param];i.removeAttribute('aria-invalid');});status.textContent='Defaults restored.';render();});
document.querySelector('#export').addEventListener('click',()=>{const a=document.createElement('a'),url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\n'],{type:'application/json'}));a.href=url;a.download='directional-compression-state.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Exported actual displayed state, definitions and calibration status.';});
render();
