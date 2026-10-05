import {compressionState,COMPRESSION_DEFAULTS} from './compression.mjs';
import {geometrySvg} from './property-labs.mjs';
import {BOX_FACES} from './continuum-properties.mjs';
const pretty=v=>v===0?'0':Number(v).toPrecision(6);
export function compressionSvg(state){
 return geometrySvg(state,BOX_FACES).replaceAll('prescribed','current homogeneous').replace('Gray: reference. Blue: current homogeneous. SI readouts are unscaled.',`Gray: reference. Blue: current. ${state.controls.boundary==='free'?'Free sides':'Confined sides'}.`);
}
class CompressionLab{
 constructor(root){
  this.root=root;this.params={...COMPRESSION_DEFAULTS};this.state=compressionState(this.params);this.status=root.querySelector('.announce');
  root.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>this.change(input)));
  root.querySelector('[data-action=reset]').addEventListener('click',()=>{
   this.params={...COMPRESSION_DEFAULTS};this.state=compressionState(this.params);
   root.querySelectorAll('[data-param]').forEach(i=>{i.value=this.params[i.dataset.param];i.removeAttribute('aria-invalid');});
   this.status.textContent='Defaults restored.';this.render();
  });
  root.querySelector('[data-action=summary]').addEventListener('click',()=>{this.status.textContent=root.querySelector('.readout').innerText;});
  root.querySelector('[data-action=copy]').addEventListener('click',()=>{
   const box=root.querySelector('.preset');box.hidden=false;box.value=JSON.stringify({schema:1,lesson:'lab-5-compression',parameters:this.params,measurements:this.state},null,2);box.focus();box.select();
  });
  root.dataset.enhanced='true';this.render();
 }
 change(input){
  const key=input.dataset.param,value=input.tagName==='SELECT'?input.value:input.valueAsNumber;
  if(input.value===''||!input.checkValidity()||(typeof value==='number'&&!Number.isFinite(value))){input.setAttribute('aria-invalid','true');this.status.textContent='Invalid input; previous valid state retained.';return;}
  const candidate={...this.params,[key]:value};let state;
  try{state=compressionState(candidate);}catch(error){if(input.tagName==='SELECT'){input.value=this.params[key];input.removeAttribute('aria-invalid');}else input.setAttribute('aria-invalid','true');this.status.textContent=`Rejected candidate: ${error.message}. Previous valid state retained.`;return;}
  input.removeAttribute('aria-invalid');this.params=candidate;this.state=state;
  this.root.querySelectorAll(`[data-param="${key}"]`).forEach(other=>{other.value=value;other.removeAttribute('aria-invalid');});
  this.status.textContent='';this.render();
 }
 render(){
  const s=this.state,mode=this.params.mode;
  this.root.querySelectorAll('[data-param=heightStretch]').forEach(i=>i.disabled=mode==='force');
  this.root.querySelectorAll('[data-param=force]').forEach(i=>i.disabled=mode==='displacement');
  this.root.querySelector('.property-scene').innerHTML=compressionSvg(s);
  const values=[['Control interpretation',mode==='force'?'Force imposed; height solved':'Height imposed; plate reaction measured'],['Height stretch h',s.heightStretch],['Lateral stretch t',s.lateralStretch],['Local volume ratio J',s.J],['Independent boundary V / V₀',s.volumeRatio],['Volume-ratio disagreement',s.volumeMeasurementDifference],['Plate shortening (m)',s.plateDisplacementM],['Plate reaction (N)',s.plateReactionN],['Current plate area (m²)',s.currentPlateAreaM2],['Plate compressive pressure (Pa)',s.platePressurePa],['Bulk / mean compressive pressure (Pa)',s.bulkPressurePa],['Side support force on +x face (N)',s.sideSupportForceN],['Lateral Cauchy stress (Pa)',s.lateralCauchyStressPa],['Shape energy (J)',s.deviatoricEnergyJ],['Volume energy (J)',s.volumeEnergyJ],['Total stored energy (J)',s.energyJ],['Independent volume-equilibrium difference',s.volumeEquilibriumDifference],['Free-side residual (Pa)',s.lateralResidualPa===null?'Confinement supplies a support reaction':s.lateralResidualPa],['Force-control residual (N)',mode==='force'?s.forceResidualN:'Reaction is an output'],['Maximum energy/stress check error (Pa)',Math.max(...s.energyDerivativeProbes.flatMap(q=>[Math.abs(q.axialDifferencePa),Math.abs(q.lateralDifferencePa)]))],['Supported force at h = 0.8 (N)',s.maxSupportedForceN],['Prescribed isochoric t for comparison',s.isochoricComparison.lateralStretch]];
  const dl=this.root.querySelector('.readout');dl.replaceChildren(...values.map(([label,value])=>{
   const div=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=typeof value==='number'?pretty(value):value;div.append(dt,dd);return div;
  }));
 }
}
if(typeof document!=='undefined')document.querySelectorAll('[data-compression]').forEach(root=>new CompressionLab(root));
