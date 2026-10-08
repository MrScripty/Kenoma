import {labState,DEFAULT_INPUT} from './model.mjs';
document.documentElement.classList.add('js');
const $=id=>document.getElementById(id),fields={delta:'deltaMicrometres',leftg:'leftShearKPa',rightg:'rightShearKPa'};
let admitted=labState(),exportOpen=false;
const f=(x,n=3)=>x.toFixed(n),signed=x=>(x<0?'−':'+')+f(Math.abs(x)*1e3);
function render(){
 const r=admitted;
 for(const [id,key] of Object.entries(fields)){$(id).value=r.input[key];$(id+'-number').value=r.input[key];}
 $('preset').value=r.input.preset;
 $('end-force').innerHTML=`${f(r.externalRightForceN*1e3)} <span class="unit">mN</span>`;
 const paths=(r.CL>0?1:0)+(r.CR>0?1:0);$('path-tag').textContent=paths===0?'Disconnected':paths===1?'One load path':'Two load paths';
 const rows={u:f(r.u*1e6)+' µm',v:f(r.v*1e6)+' µm',fibres:`${f(r.upperForceN*1e3)} / ${f(r.lowerForceN*1e3)} mN`,
  exchange:`${f(r.leftExchangeN*1e3)} / ${f(r.rightExchangeN*1e3)} mN`,external:`${signed(r.externalLeftForceN)} / ${signed(r.externalRightForceN)} mN`,
  effective:f(r.effectiveStiffnessNPerM)+' N/m',axial:`${f(r.K1)} / ${f(r.K2)} N/m`,interfaces:`${f(r.CL)} / ${f(r.CR)} N/m`,
  energy:f(r.energyJ*1e12)+' pJ',axialStrain:`${r.upperStrain.toExponential(3)} / ${r.lowerStrain.toExponential(3)}`,
  shearStrain:`${f(r.leftShearStrain,4)} / ${f(r.rightShearStrain,4)}`,
  residual:Math.max(Math.abs(r.upperResidualN),Math.abs(r.lowerResidualN),Math.abs(r.wholeResultantN)).toExponential(3)+' N'};
 for(const [key,value] of Object.entries(rows))document.querySelector(`[data-key="${key}"]`).textContent=value;
 const scale=408/.01*1000,uX=480+r.u*scale,vX=72+r.v*scale,dX=480+r.delta*scale;
 $('upper-bar').setAttribute('width',uX-72);$('lower-bar').setAttribute('x',vX);$('lower-bar').setAttribute('width',dX-vX);
 for(const [id,x] of [['node-u',uX],['node-v',vX],['node-delta',dX]])$(id).setAttribute('cx',x);
 for(const [id,x] of [['u-label',uX],['v-label',vX],['delta-label',dX]])$(id).setAttribute('x',x);
 $('link-left').setAttribute('d',`M72 84 L${vX} 192`);$('link-right').setAttribute('d',`M${uX} 84 L${dX} 192`);
 $('link-left').setAttribute('stroke',r.CL===0?'#c6cbc6':'#ba743e');$('link-right').setAttribute('stroke',r.CR===0?'#c6cbc6':'#ba743e');
 $('link-left').setAttribute('stroke-dasharray',r.CL===0?'6 7':'none');$('link-right').setAttribute('stroke-dasharray',r.CR===0?'6 7':'none');
 $('interpretation').textContent=paths===0?'Both interfaces are zero. End force and storage are zero; the lower element follows its driven endpoint without providing a connected force path.':
  `${paths===1?'One localized interface carries force.':'Both localized interfaces carry force.'} Upper / lower contributions are ${f(r.upperForceN*1e3)} / ${f(r.lowerForceN*1e3)} mN. Opposite signed external forces sum to ${r.wholeResultantN.toExponential(2)} N within roundoff.`;
 $('state-export').hidden=!exportOpen;$('state-export').value=JSON.stringify(r,null,2);
}
function update(patch){
 try{admitted=labState({...admitted.input,...patch});$('status').textContent='Admitted small-strain state. Inputs are illustrative.';render();}
 catch(error){$('status').textContent='Input rejected; last admitted state retained. '+error.message;render();}
}
for(const [id,key] of Object.entries(fields))for(const suffix of ['', '-number']){
 $(id+suffix).addEventListener('input',()=>{const raw=$(id+suffix).value;update({[key]:raw.trim()===''?NaN:Number(raw)});});
}
$('preset').addEventListener('change',()=>update({preset:$('preset').value}));
$('reset').addEventListener('click',()=>{admitted=labState(DEFAULT_INPUT);exportOpen=false;$('status').textContent='Reset to authored defaults.';render();});
$('export').addEventListener('click',()=>{exportOpen=!exportOpen;render();if(exportOpen)$('state-export').focus();});
window.lateralTransfer=Object.freeze({snapshot:()=>structuredClone(admitted)});
render();
