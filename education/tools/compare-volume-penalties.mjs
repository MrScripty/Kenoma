/** Frozen constitutive diagnostic only. No equilibrium solve or material update. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {muscleMaterial,MUSCLE_FIXTURE} from '../web/anatomical-material.mjs';
import {blockEnergy,blockStress,TISSUE} from '../web/tissue.mjs';

const evidence='data/anatomical-arm-v1/audit/anatomical-dense-trajectory-recheck.json';
const saved=JSON.parse(fs.readFileSync(evidence));
assert.equal(saved.result,'PASS_DENSE_TRAJECTORY');
const worst=[saved.held,...saved.rows].reduce((a,b)=>a.minimumCornerJ<b.minimumCornerJ?a:b);
const p={...TISSUE,mu:MUSCLE_FIXTURE.mu,bulk:MUSCLE_FIXTURE.bulk};
const referenceVolume=p.width*p.height*p.depth;
const actualLog=J=>{
 const s=Math.cbrt(J),m=muscleMaterial([s,0,0,0,s,0,0,0,s],[1,0,0],0);
 return {energyDensityPa:m.energy.volume,pressurePa:-(m.cauchy[0]+m.cauchy[4]+m.cauchy[8])/3,matrixDensityPa:m.energy.matrix,fiberDensityPa:m.energy.passiveFiber};
};
const actualQuadratic=J=>{
 const s=Math.cbrt(J),m=blockStress(s,s,p);
 return {energyDensityPa:blockEnergy(s,s,p)/referenceVolume,pressurePa:-(2*m.px+m.py)*s/(3*m.J)};
};
const rows=[1,.999,.9,.8,worst.minimumCornerJ,.6].map(J=>{
 const log=actualLog(J),quadratic=actualQuadratic(J);
 const expectedLog=-p.bulk*Math.log(J)/J,expectedQuadratic=p.bulk*(1-J);
 const stressErrorPa=Math.max(Math.abs(log.pressurePa-expectedLog),Math.abs(quadratic.pressurePa-expectedQuadratic));
 assert.ok(stressErrorPa<=1e-7,`actual stress/independent formula: ${stressErrorPa}`);
 assert.ok(Math.abs(log.matrixDensityPa)<=1e-7&&log.fiberDensityPa===0,'pure compressed dilation isolates volume');
 const finiteDifferences=[2e-6,1e-6].map(delta=>{
  const logPressurePa=-(actualLog(J+delta).energyDensityPa-actualLog(J-delta).energyDensityPa)/(2*delta);
  const quadraticPressurePa=-(actualQuadratic(J+delta).energyDensityPa-actualQuadratic(J-delta).energyDensityPa)/(2*delta);
  const errorPa=Math.max(Math.abs(logPressurePa-log.pressurePa),Math.abs(quadraticPressurePa-quadratic.pressurePa));
  assert.ok(errorPa<=1e-3,`volume-energy derivative: ${errorPa}`);
  return {delta,logPressurePa,quadraticPressurePa,maximumErrorPa:errorPa};
 });
 return {J,log,quadratic,stressErrorPa,finiteDifferences,energyRatio:J===1?null:log.energyDensityPa/quadratic.energyDensityPa,pressureRatio:J===1?null:log.pressurePa/quadratic.pressurePa};
});
const files=['tools/compare-volume-penalties.mjs','web/anatomical-material.mjs','web/tissue.mjs',evidence];
const receipt={schema:1,result:'PASS_FROZEN_VOLUME_PENALTY_COMPARISON',sourceHashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')])),matchedBulkPa:p.bulk,matchedShearPa:p.mu,savedCorner:{timeS:worst.timeS,J:worst.minimumCornerJ},rows,limits:['Shared authored moduli isolate law shape; no parameter calibration or default change.','Pure isotropic compression at zero activation isolates volume energy; actual anisotropic arm points may have other stress contributions.','A larger logarithmic restoring pressure does not prove correct compression, equilibrium, locking diagnosis or convergence.','No optimizer, state/time advancement, skin, tolerance or iteration change.']};
const output=process.argv[2];if(output){assert.ok(!fs.existsSync(output),'preserve existing receipt');fs.writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');}
console.log(JSON.stringify(receipt,null,2));
