import {writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {SLS_DEFAULTS,runProtocol} from '../web/dissipative-bar.mjs';
const destination=process.argv[2];if(!destination)throw new Error('Output directory required');mkdirSync(destination,{recursive:true});
const cases={};
for(const [name,overrides] of Object.entries({creep:{},relaxation:{holdMode:'extension'},elastic:{E1:0},lowViscosity:{eta:20000},highViscosity:{eta:500000},fastRamp:{ramp:.2},slowRamp:{ramp:2},stepped:{shape:'two-segment'},reversed:{ratio:.5}})){
 const result=runProtocol({...SLS_DEFAULTS,...overrides});const {ramp,hold}=result.parameters;
 const frames=[0,ramp,ramp+hold,2*ramp+hold,result.state.time].map(t=>{const row=result.trace.find(s=>Math.abs(s.time-t)<1e-10);if(!row)throw new Error('Missing phase boundary');const {samples,...measurements}=row;return measurements;});
 cases[name]={parameters:result.parameters,finalState:result.state,frames};
}
const result={schema:1,model:'Quasistatic small-strain axial standard linear solid',coefficients:'Authored demonstration values in SI; no measured tissue calibration',cases,inputs:Object.fromEntries(['web/dissipative-bar.mjs','tools/dissipative-experiment.mjs'].map(p=>[p,createHash('sha256').update(readFileSync(new URL('../'+p,import.meta.url))).digest('hex')]))};
writeFileSync(destination+'/dissipative-experiment.json',JSON.stringify(result,null,2)+'\n');
const p=SLS_DEFAULTS,run=runProtocol(p),times=[0,1,3,4,7],rows=times.map(t=>run.trace.find(r=>Math.abs(r.time-t)<1e-10));
const body=rows.map((r,i)=>{const x=90,base=140,y=50+i*76,end=x+p.length*1600+r.extensionM*1600*10;return `<g><text x="10" y="${y+4}" font-size="15">${r.time.toFixed(0)} s</text><line x1="${x}" y1="${y}" x2="${x+p.length*1600}" y2="${y}" stroke="#abbac3" stroke-dasharray="5 4" stroke-width="26"/><line x1="${x}" y1="${y}" x2="${end}" y2="${y}" stroke="#267f91" stroke-width="14"/><text x="460" y="${y-7}" font-size="14">N=${r.force.toFixed(3)} N; δ=${(r.extensionM*1000).toFixed(3)} mm</text><text x="460" y="${y+14}" font-size="14">U=${(r.storageJ*1000).toFixed(4)}; D=${(r.dissipationJ*1000).toFixed(4)} mJ</text></g>`;}).join('');
writeFileSync(destination+'/property-dissipative.svg',`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 450" role="img" aria-label="Force-controlled SLS load hold unload and recovery"><rect width="760" height="450" fill="#f4f8fb"/><text x="16" y="20" font-size="16">Default force hold: axial displacement magnified 10×; fixed reference scale</text>${body}<text x="16" y="438" font-size="15">Dash: reference length. Schematic thickness. Recoverable U and cumulative viscous loss D.</text></svg>`);
console.log('Generated independent protocol frames and static reading figure');
