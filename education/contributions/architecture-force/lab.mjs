import {materialCut,aggregateTypes,forceLength} from './model.mjs';
const ids=['stretch','volume','packing','angle'];
const el=id=>document.getElementById(id);
const fmt=(n,d=2)=>n.toFixed(d);
function render(){
 const lambda=+el('stretch').value,J=+el('volume').value,phi=+el('packing').value,angle=+el('angle').value;
 const factor=el('length-law').checked?forceLength(lambda):1;
 const r=materialCut({referenceAreaM2:1e-4*phi,lambda,J,nominalStressPa:3e5*factor,cosPennation:Math.cos(angle*Math.PI/180)});
 el('stretch-value').value=fmt(lambda);el('volume-value').value=fmt(J);el('packing-value').value=fmt(phi);el('angle-value').value=`${angle}°`;
 const rows=[['Reference contractile area',`${fmt(r.referenceAreaM2*1e6)} mm²`],['Current projected area',`${fmt(r.projectedCurrentAreaM2*1e6)} mm²`],['Nominal stress P',`${fmt(r.nominalStressPa/1000)} kPa`],['Cauchy fibre stress σ',`${fmt(r.cauchyFiberStressPa/1000)} kPa`],['Axial force',`${fmt(r.axialForceN)} N`],['Tendon-directed component',`${fmt(r.tendonDirectedForceN)} N`]];
 const dl=document.createElement('dl');for(const [label,value] of rows){const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;row.append(dt,dd);dl.append(row)}el('readout').replaceChildren(dl);
 el('interpretation').textContent=el('length-law').checked?`The explicit force–length multiplier is ${fmt(factor,4)}. Area change is still not a separate force bonus.`:'Force–length is held at 1 to isolate the area/stress transformation. Axial force is independent of λ and J under this declared nominal-stress assumption.';
}
for(const id of ids)el(id).addEventListener('input',render);el('length-law').addEventListener('change',render);
el('reset').addEventListener('click',()=>{for(const [id,v] of Object.entries({stretch:.8,volume:1,packing:.8,angle:30}))el(id).value=v;el('length-law').checked=false;render()});
const groups=aggregateTypes([{count:50000,referenceFiberAreaM2:1e-9,nominalStressPa:1e5},{count:50000,referenceFiberAreaM2:2e-9,nominalStressPa:3e5}]);
el('composition').textContent=`Total reference area ${fmt(groups.totalAreaM2*1e6)} mm² · summed force ${fmt(groups.axialForceN)} N · area-weighted nominal stress ${fmt(groups.areaWeightedNominalStressPa/1000)} kPa`;
render();
