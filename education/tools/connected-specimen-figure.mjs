/** Sample the actual solved Q2 side; fixed SI scale, no geometric correction. */
import fs from 'node:fs';import crypto from 'node:crypto';
import {prepareAxisymmetric,createMaterialSampler} from '../web/axisymmetric-specimen.mjs';
const [input,output,receipt]=process.argv.slice(2),data=JSON.parse(fs.readFileSync(input)),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const texts=[],parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 500" role="img" aria-label="Actual solved connected taper side boundaries with finite volume compliance"><rect width="600" height="500" fill="#f4f7fb"/>'];
const text=(x,y,s,size=16)=>{texts.push(s);parts.push(`<text x="${x}" y="${y}" font-family="Arial,sans-serif" font-size="${size}" fill="#173c49">${s}</text>`)};
text(20,30,'One connected passive taper',22);text(20,58,'L₀ = 50 mm · a₀ = 5 mm · μ = 1500 Pa · K = 30000 Pa');
const cases=[];
for(const [i,epsilon] of [-.1,0,.1].entries()){
 const row=data.cases.find(c=>c.axialCells===16&&c.radialCells===8&&c.order===7&&c.ratio===1.5&&c.epsilon===epsilon);if(!row||!row.state.converged)throw Error('Missing qualified figure state');
 const mesh=prepareAxisymmetric({axialCells:16,radialCells:8,order:7,ratio:1.5}),sample=createMaterialSampler(mesh,row.state),cx=100+i*200,scale=4000,bottom=326,points=[];
 for(let j=0;j<=128;j++){const Z=j===128?.05:.05*j/128,R=.005*(1+.5*Z/.05),p=sample(R,Z);points.push([p.r,p.z]);}
 const path=(p)=>'M'+p.map(([r,z])=>`${(cx+r*scale).toFixed(6)},${(bottom-z*scale).toFixed(6)}`).join('L')+'L'+p.slice().reverse().map(([r,z])=>`${(cx-r*scale).toFixed(6)},${(bottom-z*scale).toFixed(6)}`).join('L')+'Z';
 parts.push(`<path d="${path(points)}" fill="#63a7b2" stroke="#176773" stroke-width="1.5"/><path d="${path([[.005,0],[.0075,.05]])}" fill="none" stroke="#687983" stroke-width="1.5" stroke-dasharray="5 4"/>`);
 text(20+i*200,95,epsilon===0?'Zero end displacement':epsilon<0?'−10% compression':'+10% tension');
 text(20+i*200,355,`V/V₀ = ${row.state.diagnostics.volumeRatio.toFixed(6)}`);
 text(20+i*200,382,`Reaction ${row.state.diagnostics.rightReactionN.toFixed(5)} N`);
 cases.push({key:row.key,epsilon,q_sha256:sha(JSON.stringify(row.state.q)),volumeRatio:row.state.diagnostics.volumeRatio,rightReactionN:row.state.diagnostics.rightReactionN,side_samples:points});
}
text(20,421,'Gray dashed: reference · teal: solved side · fixed metre scale');text(20,448,'16 axial × 8 radial Q2 cells · assembly quadrature order 7');text(20,477,'Volume is solved with finite compliance; it is not corrected to J = 1.');parts.push('</svg>');fs.writeFileSync(output,parts.join(''));
fs.writeFileSync(receipt,JSON.stringify({scope:'Solved side meridian illustration, not an anatomical surface or incompressibility claim',experiment_sha256:sha(fs.readFileSync(input)),generator_sha256:sha(fs.readFileSync(new URL(import.meta.url))),svg_sha256:sha(fs.readFileSync(output)),labels:texts,cases},null,2)+'\n');
