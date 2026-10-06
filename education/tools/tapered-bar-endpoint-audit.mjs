/** Preserve the reviewed warning failure and its independently checked fix. */
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {BAR_DEFAULTS,barState} from '../web/tapered-bar.mjs';
import {barState as frozenState} from '../data/property-labs-v1/review/first-preview/web/tapered-bar.mjs';
const parameters={...BAR_DEFAULTS,area:.0001,ratio:4,modulus:110000,force:.6,segments:8};
const old=frozenState(parameters),current=barState(parameters),oracleMaximumStrain=3/55;
if(old.smallStrainWarning||Math.max(...old.samples.map(s=>Math.abs(s.strain)))>=.05)throw Error('Frozen reviewed failure changed');
const refinements=[8,16,64,512].map(segments=>{const state=barState({...parameters,segments});if(!state.smallStrainWarning||Math.abs(state.maxAbsStrain-oracleMaximumStrain)>1e-15)throw Error('Endpoint oracle disagrees');return {segments,smallStrainWarning:state.smallStrainWarning,trueMaximumStrain:state.maxAbsStrain,midpointMaximumStrain:Math.max(...state.samples.map(s=>Math.abs(s.strain)))};});
const paths=['web/tapered-bar.mjs','web/property-labs.mjs','tests/tapered_bar.test.mjs','data/property-labs-v1/review/first-preview/web/tapered-bar.mjs','tools/tapered-bar-endpoint-audit.mjs'];
const receipt={schema:1,result:'PASS_PRESERVED_WARNING_FAILURE_AND_ENDPOINT_CORRECTION',frozenPreviewCommit:'83a9ee0715da01ef4548ebfe094a817f4c06e8b7',parameters,oracleMaximumStrain,frozen:{smallStrainWarning:old.smallStrainWarning,reportedMaximumStrain:old.maxAbsStrain},corrected:{smallStrainWarning:current.smallStrainWarning,maximumStrain:current.maxAbsStrain},refinements,sourceHashes:Object.fromEntries(paths.map(path=>[path,createHash('sha256').update(fs.readFileSync(path)).digest('hex')])),scope:'Monotone positive linear/step area, constant modulus and constant resultant; endpoint extrema are independent of display samples. No anatomical or finite-strain validation.'};
fs.writeFileSync('data/property-labs-v1/endpoint-warning-audit.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
