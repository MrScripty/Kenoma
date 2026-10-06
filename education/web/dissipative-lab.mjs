import {SLS_DEFAULTS,validateParameters,barGeometry,initialState,stepProtocol,observe,totalDuration} from './dissipative-bar.mjs';

export const DISSIPATIVE_BATCH_STEPS=64;
const SCALE=1600,MAGNIFICATION=10,STRAIN_LIMIT=.05,ENERGY_LIMIT=.004;
const PHASES={load:'Loading ramp',hold:'Hold',unload:'Unloading ramp',recovery:'Zero-force recovery',done:'Protocol complete'};
const fmt=(value,digits=5)=>Math.abs(value)<1e-12?'0':Number(value).toPrecision(digits);
const strainColour=value=>{
 const fraction=Math.min(1,Math.abs(value)/STRAIN_LIMIT),target=value<0?[190,65,35]:[20,108,184],base=[236,240,243];
 return `rgb(${base.map((v,i)=>Math.round(v+(target[i]-v)*fraction)).join(',')})`;
};

export function dissipativeBarSvg(p,current){
 const x0=65,y0=180,depth=.01;
 const cells=current.samples.map(row=>{
  const x=x0+(row.sM-row.dxM/2+MAGNIFICATION*row.displacementStartM)*SCALE;
  const width=(row.dxM+MAGNIFICATION*(row.displacementEndM-row.displacementStartM))*SCALE;
  const height=row.areaM2/depth*SCALE;
  return `<rect data-strain="${row.strain}" x="${x}" y="${y0-height/2}" width="${width}" height="${height}" fill="${strainColour(row.strain)}" stroke="#456171" stroke-width=".45"/>`;
 }).join('');
 const reference=current.samples.map(row=>`<rect x="${x0+(row.sM-row.dxM/2)*SCALE}" y="${y0-row.areaM2/depth*SCALE/2}" width="${row.dxM*SCALE}" height="${row.areaM2/depth*SCALE}" fill="none" stroke="#7a8994" stroke-dasharray="3 3"/>`).join('');
 const endpoint=x0+(p.length+MAGNIFICATION*current.extensionM)*SCALE;
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 330" role="img" aria-label="Axial bar cells coloured by actual strain, fixed plus or minus five percent palette; axial displacement enlarged ten times"><rect width="640" height="330" fill="#f4f7fb"/><text x="24" y="26">${PHASES[current.phase]} · t = ${fmt(current.time)} s</text><path d="M${x0-8} 60V270" stroke="#456171" stroke-width="5"/>${cells}${reference}<path d="M${endpoint} 65V265" stroke="#087567" stroke-width="2"/><text x="${Math.min(endpoint+7,535)}" y="54">N = ${fmt(current.force)} N</text><path d="M${x0} 280h${.05*SCALE}" stroke="#152e41" stroke-width="2"/><text x="${x0}" y="300">0.05 m reference scale</text><text x="24" y="321">Axial displacement ×10; gray dashed: reference. Section depth: 0.01 m.</text></svg>`;
}

function chart(p,history,type){
 const x0=65,x1=555,y0=205,y1=38,duration=totalDuration(p);
 const x=t=>x0+(x1-x0)*t/duration;
 const energy=type==='energy';
 const lines=energy?[['storageJ','Stored U','#1674b5',ENERGY_LIMIT],['workJ','Work W','#273e50',ENERGY_LIMIT],['dissipationJ','Loss D','#b75b17',ENERGY_LIMIT]]:[['force','Force N','#273e50',.6],['extensionM','Extension δ','#087567',.006]];
 const boundaries=[0,p.ramp,p.ramp+p.hold,2*p.ramp+p.hold,duration];
 const bands=['Load','Hold','Unload','Recovery'].map((name,i)=>`<rect x="${x(boundaries[i])}" y="${y1}" width="${x(boundaries[i+1])-x(boundaries[i])}" height="${y0-y1}" fill="${i%2?'#e8eef1':'#f6f8fa'}"/><text x="${(x(boundaries[i])+x(boundaries[i+1]))/2}" y="22" text-anchor="middle">${name}</text>`).join('');
 const paths=lines.map(([key,label,colour,max])=>`<polyline data-series="${key}" points="${history.map(row=>`${x(row.time)},${y0-(y0-y1)*Math.max(0,Math.min(max,row[key]))/max}`).join(' ')}" fill="none" stroke="${colour}" stroke-width="2.5"/><text x="${x0+lines.findIndex(line=>line[0]===key)*170}" y="268" fill="${colour}">${label}</text>`).join('');
 const clipped=lines.some(([key,,,max])=>history.some(row=>row[key]<-1e-12||row[key]>max));
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 295" role="img" aria-label="${energy?'Stored energy, signed cumulative boundary work and accumulated viscous loss':'Actual force and extension'} against simulated time; fixed labelled scales"><rect width="640" height="295" fill="#fff"/>${bands}<path d="M${x0} ${y1}V${y0}H${x1}" fill="none" stroke="#456171"/>${paths}<text x="12" y="44">${energy?'.004 J':'.6 N'}</text><text x="12" y="208">0</text>${energy?'':`<text x="${x1+8}" y="44">6 mm</text><text x="${x1+8}" y="208">0</text>`}<text x="${x0}" y="231">0</text><text x="${x1}" y="231" text-anchor="end">${fmt(duration)} s</text><text x="310" y="247" text-anchor="middle">Simulated time (s)</text><text x="${x0}" y="289">${clipped?'Plot clips values outside its fixed range; inspect SI readouts/export.':'Fixed scales; numerical values and full history are exported.'}</text></svg>`;
}

export class DissipativeLab{
 constructor(root){
  this.root=root;this.running=false;this.epoch=0;this.params={...SLS_DEFAULTS};
  root.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>this.change(input)));
  for(const [action,handler] of Object.entries({reset:()=>this.reset(),step:()=>{this.pause();this.advance();this.render();},play:()=>this.running?this.pause(true):this.play(false),run:()=>this.running?this.pause(true):this.play(true),copy:()=>this.copy(),export:()=>this.export(),summary:()=>this.announce(Array.from(root.querySelectorAll('.readout>div')).map(row=>`${row.querySelector('dt').textContent}: ${row.querySelector('dd').textContent}.`).join(' '))})){
   root.querySelector(`[data-action=${action}]`)?.addEventListener('click',handler);
  }
  this.reset();root.dataset.enhanced='true';
 }
 announce(message){this.root.querySelector('.announce').textContent=message;}
 hidePreset(){const box=this.root.querySelector('.preset');box.hidden=true;box.value='';}
 sync(){this.root.querySelectorAll('[data-param]').forEach(input=>{input.value=this.params[input.dataset.param];input.removeAttribute('aria-invalid');});}
 begin(){this.state=initialState(this.params);this.index=0;this.history=[{step:0,...observe(this.params,this.state)}];this.hidePreset();this.render();}
 reset(){this.pause();this.params={...SLS_DEFAULTS};this.sync();this.begin();this.announce('Defaults restored. New experiment: time, internal strain, work, loss and trace reset; playback paused.');}
 change(input){
  const key=input.dataset.param,value=['shape','holdMode'].includes(key)?input.value:Number(input.value);
  const candidate={...this.params,[key]:value};
  try{
   if(input.value===''||!input.checkValidity())throw new RangeError('Invalid control');
   validateParameters(candidate);initialState(candidate);
  }catch{
   this.pause();input.setAttribute('aria-invalid','true');this.announce('Invalid input. Prior experiment, parameters and trace retained; playback paused.');return;
  }
  this.pause();this.params=candidate;this.sync();this.begin();
  this.announce('Parameter applied as a new experiment: time, internal strain, work, loss and trace reset; playback paused.');
 }
 pause(spoken=false){
  this.running=false;this.epoch++;cancelAnimationFrame(this.frame);this.root.dataset.running='false';
  this.root.querySelector('[data-action=play]').textContent='Play';this.root.querySelector('[data-action=run]').textContent='Run protocol';
  if(spoken)this.announce(`Paused at ${fmt(this.state.time)} of ${fmt(totalDuration(this.params))} s. Step, Play or Run protocol resumes this experiment.`);
 }
 advance(){
  if(this.state.phase==='done')return false;
  try{
   const next=stepProtocol(this.params,this.state),row=observe(this.params,next);
   if(!(next.time>this.state.time)||this.index>=Math.ceil(totalDuration(this.params)/this.params.dt)+2||!Object.entries(row).filter(([,v])=>typeof v==='number').every(([,v])=>Number.isFinite(v)))throw new RangeError('Non-finite or non-advancing result');
   this.state=next;this.history.push({step:++this.index,...row});this.hidePreset();
   if(next.phase==='done'){this.pause();this.announce(`Completed ${fmt(totalDuration(this.params))} simulated seconds; ${this.index} steps and ${this.history.length} samples including the initial state.`);}
   return true;
  }catch(error){this.pause();this.announce(`Step rejected: ${error.message}. Last accepted state and trace retained.`);return false;}
 }
 play(fast){
  if(this.state.phase==='done')return;
  this.pause();this.running=true;this.fast=fast;this.root.dataset.running='true';this.lastFrame=null;this.accumulator=0;
  this.root.querySelector('[data-action=play]').textContent='Pause';this.root.querySelector('[data-action=run]').textContent='Pause protocol';
  this.announce(fast?'Running protocol in batches of at most 64 fixed physics steps; Pause retains the current experiment.':'Playing at simulated-time pace; Pause retains the current experiment.');
  const epoch=this.epoch;
  const frame=now=>{
   if(!this.running||epoch!==this.epoch)return;
   let budget=DISSIPATIVE_BATCH_STEPS;
   if(!fast){this.accumulator+=this.lastFrame===null?0:Math.min((now-this.lastFrame)/1000,this.params.dt*DISSIPATIVE_BATCH_STEPS);budget=Math.min(DISSIPATIVE_BATCH_STEPS,Math.floor((this.accumulator+1e-12)/this.params.dt));this.accumulator-=budget*this.params.dt;}
   this.lastFrame=now;
   for(let i=0;i<budget&&this.running;i++)if(!this.advance())break;
   this.render();if(this.running&&epoch===this.epoch)this.frame=requestAnimationFrame(frame);
  };
  this.frame=requestAnimationFrame(frame);
 }
 payload(){return {schema:1,model:'standard-linear-solid-axial-bar-v1',units:'SI: m, m², N, Pa, Pa·s, s, J, W; strain dimensionless',parameters:{...this.params},state:{...this.state},steps:this.index,samples:this.history.length,initialEnergyJ:this.history[0].storageJ,tracePolicy:'Initial state and every returned fixed-step observation; protocol phase boundaries are clipped by the model. Parameter edits start a new experiment.',display:{axialDisplacementMagnification:MAGNIFICATION,physicalScalePixelsPerM:SCALE,strainPalette:[-STRAIN_LIMIT,STRAIN_LIMIT],sectionReferenceDepthM:.01},trace:this.history};}
 copy(){const box=this.root.querySelector('.preset');box.hidden=false;box.value=JSON.stringify(this.payload(),null,2);box.focus();box.select();this.announce('Current experiment and complete trace shown below. Copy the selected JSON.');}
 export(){const blob=new Blob([JSON.stringify(this.payload(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='kenoma-dissipative-bar-trace.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);this.announce('Downloaded the initial state and every completed protocol step with parameters and independent energy accounting.');}
 render(){
  const current=this.history.at(-1),geometry=barGeometry(this.params);
  this.root.dataset.step=String(this.index);this.root.dataset.time=String(current.time);this.root.dataset.phase=current.phase;
  this.root.querySelector('.dissipative-scene').innerHTML=dissipativeBarSvg(this.params,current);
  this.root.querySelector('.dissipative-history').innerHTML=chart(this.params,this.history,'force');
  this.root.querySelector('.dissipative-energy').innerHTML=chart(this.params,this.history,'energy');
  const rows=[['Phase',PHASES[current.phase]],['Hold condition',this.params.holdMode==='force'?'Constant force: creep':'Held extension: relaxation'],['Time',`${fmt(current.time)} / ${fmt(totalDuration(this.params))} s`],['Steps / samples',`${this.index} / ${this.history.length} (initial included)`],['Axial resultant',`${fmt(current.force)} N`],['Extension δ',`${fmt(current.extensionM)} m`],['Stored energy U',`${fmt(current.storageJ)} J`],['Signed cumulative work W',`${fmt(current.workJ)} J`],['Accumulated viscous loss D',`${fmt(current.dissipationJ)} J`],['Work − storage − loss',`${fmt(current.balanceResidualJ)} J`],['Maximum balance residual so far',`${fmt(this.state.maxResidualJ)} J`],['Boundary power',`${fmt(current.powerW)} W`],['Viscous loss rate',`${fmt(current.dissipationRateW)} W`],['Maximum endpoint |strain|',`${fmt(current.maxStrain)} (limit 0.05)`],['Profile compliance Cg',`${fmt(geometry.Cg)} m⁻¹`],['Exact profile compliance',`${fmt(geometry.exactCg)} m⁻¹`],['Profile extension quadrature error',`${fmt(current.profileQuadratureErrorM)} m`]];
  this.root.querySelector('.readout').innerHTML=rows.map(([label,value])=>`<div><dt>${label}</dt><dd>${value}</dd></div>`).join('');
  for(const action of ['step','play','run'])this.root.querySelector(`[data-action=${action}]`).disabled=current.phase==='done';
 }
}

if(typeof document!=='undefined')document.querySelectorAll('[data-dissipative]').forEach(root=>new DissipativeLab(root));
