/** Source-bound material/BC experiment. Preserves unsupported-load rejection. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import {compressionState as state,COMPRESSION_DEFAULTS as D,COMPRESSION_LIMITS} from '../web/compression.mjs';
import {TISSUE,blockEnergy,blockStress} from '../web/tissue.mjs';
const assets=process.argv[2],output=process.argv[3];
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const inputs=['web/compression.mjs','web/compression-lab.mjs','web/tissue.mjs','web/continuum-properties.mjs','web/property-labs.mjs','tools/compression_lab.py','tools/compression-experiment.mjs','tests/compression.test.mjs'];
const heights=[1,.9,.8,.7,.6],rows=heights.flatMap(heightStretch=>['free','confined'].map(boundary=>state({...D,heightStretch,boundary})));
const forceControlled=['free','confined'].map(boundary=>state({...D,mode:'force',boundary}));
const materialSweep=[0,1500,50000,1000000].flatMap(bulk=>['free','confined'].map(boundary=>state({...D,bulk,boundary})));
const shapeSweep=[100,1500,10000].map(mu=>state({...D,mu}));
const V0=TISSUE.width*TISSUE.height*TISSUE.depth;
const dilation=[.7,.9,1.2].map(s=>({scale:s,J:s**3,energyDensityPa:blockEnergy(s,s,TISSUE)/V0,volumeEnergyDensityPa:TISSUE.bulk/2*(s**3-1)**2,piolaStressPa:blockStress(s,s,TISSUE).px,volumePiolaPa:TISSUE.bulk*(s**3-1)*s*s}));
for(const r of dilation){
 r.shapeEnergyDensityPa=r.energyDensityPa-r.volumeEnergyDensityPa;
 r.stressDifferencePa=r.piolaStressPa-r.volumePiolaPa;
 if(Math.abs(r.shapeEnergyDensityPa)>1e-8||Math.abs(r.stressDifferencePa)>1e-8)throw Error('Pure dilation identity failed numerically');
}
const shear=[-.6,.2,.7].map(gamma=>{
 const F=[1,gamma,0,0,1,0,0,0,1];
 const J=F[0]*(F[4]*F[8]-F[5]*F[7])-F[1]*(F[3]*F[8]-F[5]*F[6])+F[2]*(F[3]*F[7]-F[4]*F[6]),I1=F.reduce((s,x)=>s+x*x,0);
 const shapeEnergyDensityPa=TISSUE.mu/2*(J**(-2/3)*I1-3),expectedShapeEnergyDensityPa=TISSUE.mu/2*gamma**2,volumeEnergyDensityPa=TISSUE.bulk/2*(J-1)**2;
 if(J!==1||Math.abs(shapeEnergyDensityPa-expectedShapeEnergyDensityPa)>1e-10||volumeEnergyDensityPa!==0)throw Error('Simple shear identity failed numerically');
 return {gamma,F,J,I1,shapeEnergyDensityPa,expectedShapeEnergyDensityPa,volumeEnergyDensityPa};
});
const workChecks=['free','confined'].map(boundary=>{
 const final=state({...D,heightStretch:.6,boundary});
 const probes=[32,64].map(cells=>{
  const step=.4/cells;let sum=0;
  for(let i=0;i<=cells;i++)sum+=(i===0||i===cells?1:i%2?4:2)*state({...D,heightStretch:.6+i*step,boundary}).plateReactionN;
  const plateWorkJ=TISSUE.height*step*sum/3;
  return {cells,plateWorkJ,storedEnergyJ:final.energyJ,differenceJ:plateWorkJ-final.energyJ};
 });
 if(Math.abs(probes[1].differenceJ)>=Math.abs(probes[0].differenceJ)/10||Math.abs(probes[1].differenceJ)>1e-7)throw Error('Plate-work quadrature failed');
 return {boundary,probes,scope:'Quasistatic elastic path from h=1 to h=0.6; no kinetic, activation, dissipative or history energy'};
});
const negativeCases=[];
for(const parameters of [{...D,mode:'force',force:20},{...D,mode:'force',bulk:0}]){
 let rejection;
 try{state(parameters);}catch(error){rejection=error.message;}
 if(!rejection)throw new Error('Expected rejection did not occur');
 negativeCases.push({parameters,accepted:false,reason:rejection,stateAdvanced:false});
}
const receipt={schema:1,result:'PASS_LAB5_COMPRESSION_EXPERIMENT',node:process.version,inputs:Object.fromEntries(inputs.map(p=>[p,digest(p)])),defaults:D,limits:COMPRESSION_LIMITS,dimensionsM:{width:TISSUE.width,height:TISSUE.height,depth:TISSUE.depth},law:'mu/2*(J^(-2/3)*I1-3)+K/2*(J-1)^2 per reference volume; unchanged Lab 5',rows,forceControlled,materialSweep,shapeSweep,dilation,shear,workChecks,negativeCases,scope:'Homogeneous constitutive/boundary evidence only; not a mesh, mixed-pressure stability, biological validation or anatomical capstone qualification'};
if(assets){
 fs.mkdirSync(assets,{recursive:true});const pair=rows.filter(s=>Math.abs(s.heightStretch-.8)<1e-12),max=Math.max(...pair.map(s=>s.plateReactionN));
 const panels=pair.map((s,i)=>{const x=40+i*300,w=180*s.lateralStretch,h=140*s.heightStretch;return `<g><text x="${x}" y="35" font-size="20">${s.controls.boundary==='free'?'Free lateral faces':'Confined lateral faces'}</text><rect x="${x}" y="65" width="180" height="140" fill="none" stroke="#77859a" stroke-dasharray="6 4"/><rect x="${x-(w-180)/2}" y="${205-h}" width="${w}" height="${h}" fill="#339bd9" fill-opacity=".25" stroke="#1474b1" stroke-width="2"/><path d="M${x-20} ${205-h}H${x+200}M${x-20} 205H${x+200}" stroke="#9a6c14" stroke-width="4"/><text x="${x}" y="245" font-size="17">J = ${s.J.toFixed(6)}</text><text x="${x}" y="273" font-size="17">Reaction ${s.plateReactionN.toFixed(5)} N</text><rect x="${x}" y="290" width="${190*s.plateReactionN/max}" height="18" fill="#1474b1"/></g>`;}).join('');
 fs.writeFileSync(`${assets}/compression-reference.svg`,`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 355" role="img" aria-label="Same imposed 20 percent shortening: free sides retain near-unit volume, confined sides lose volume and need more force"><rect width="650" height="355" fill="#f4f7fb"/>${panels}<text x="40" y="337" font-size="16">Same h = 0.8, μ = 1500 Pa, K = 50000 Pa. Authored Lab 5.</text></svg>`);
}
if(output)fs.writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');else console.log(JSON.stringify(receipt,null,2));
