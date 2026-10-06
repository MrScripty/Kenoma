/** Source-bound common-old-state control summary; no mechanics or optimizer. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';

const base='data/anatomical-arm-v1/';
const paths={
  execution:base+'audit/dense-controlled-release-interval.json',
  replay:base+'audit/dense-controlled-release-interval-recheck.json',
  coarse:base+'audit/anatomical-dense-trajectory.json',
  fullComparison:base+'audit/dense-release-secant-matched-times.json',
};
const output=process.argv[2];
assert.ok(output&&!fs.existsSync(output),'Explicit new output required');
const hash=p=>createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p));
const run=read(paths.execution), replay=read(paths.replay), coarse=read(paths.coarse), full=read(paths.fullComparison);
assert.notEqual(run.result,'RUNNING');
assert.equal(replay.result,'PASS_FRESH_DENSE_CONTROL_REPLAY');
assert.equal(replay.executionReceiptSHA256,hash(paths.execution));
for(const [p,h] of Object.entries(run.sourceHashes))assert.equal(hash(p),h,p);
for(const [p,h] of Object.entries(full.sourceHashes))assert.equal(hash(p),h,p);
assert.deepEqual(run.cases.map(c=>c.factor),[1,3]);
const stateKeys=['coordinatesM','qRad','omegaRadPerS','activation','massKg','timeS','contactRule'];
for(const key of stateKeys)assert.deepEqual(run.oldState[key],coarse.snapshots.at(-2)[key],'Same physical old '+key);
const coarseEnd=run.cases[0].snapshots.at(-1);
for(const key of stateKeys)assert.deepEqual(coarseEnd[key],coarse.snapshots.at(-1)[key],'Exactly reproduced coarse '+key);
const cases=run.cases.map((c,i)=>({
  factor:c.factor,hS:c.hS,result:c.result,
  acceptedSteps:c.snapshots.length,
  acceptedEndpointTimeS:c.snapshots.at(-1)?.timeS??run.oldState.timeS,
  acceptedEndpointAngleDeg:(c.snapshots.at(-1)?.qRad??run.oldState.qRad)*180/Math.PI,
  maximumAcceptedIndependentResidualN:Math.max(...replay.rows[i].rows.map(r=>r.independentResidualN)),
  minimumAcceptedCornerJ:Math.min(...replay.rows[i].rows.map(r=>r.minimumCornerJ)),
  attempts:c.attempts.map((a,k)=>({
    accepted:a.accepted,targetTimeS:run.oldState.timeS+(k+1)*c.hS,residualN:a.residualN,
    iterationsAcrossFrozenContactRules:(a.receipt?.contactRefinement??[]).reduce((n,r)=>n+r.iterations,0),
    contactRefinement:a.receipt?.contactRefinement??null,
    recordedIterationSummary:(()=>{
      const rows=c.trace.filter(r=>r.stage===k);
      assert.ok(rows.length);
      return {
        rows:rows.length,
        frozenRuleIterationCounterRestarts:rows.filter((r,i)=>i>0&&r.iteration<=rows[i-1].iteration).length,
        minimumRecordedIterationResidualN:Math.min(...rows.map(r=>r.residualN)),
        finalRecordedIterationResidualN:rows.at(-1).residualN,
        minimumAcceptedLineSearchStep:Math.min(...rows.map(r=>r.step)),
        maximumRegularizationNPerM:Math.max(...rows.map(r=>r.regularizationNPerM)),
        maximumCGIterations:Math.max(...rows.map(r=>r.cgIterations)),
      };
    })(),
  })),
  traceIterations:c.trace.length,
  rejectedReplay:replay.rows[i].rejected,
  rollback:c.rollback??null,
}));
const receipt={schema:1,result:'PASS_SOURCE_BOUND_CONTROL_SUMMARY',
  samePhysicalOldState:true,coarsePhysicalEndpointExactlyReproduced:true,
  fixed:{bodyPointsPerElement:run.pointsPerElement,maxIterationsPerFrozenContactRule:run.maxIterationsPerFrozenContactRule,stationarityToleranceN:run.parameters.stationarityToleranceN},
  cases,localMatchedEndpoint:replay.comparison,
  fullReleaseMatchedEndpoint:full.rows.at(-1),
  sourceHashes:{...Object.fromEntries(Object.values(paths).map(p=>[p,hash(p)])),'tools/summarize-dense-release-controls.mjs':hash('tools/summarize-dense-release-controls.mjs')},
  limits:[
    'Both controls start from identical accepted physical state and constitutive law. Different explicit seeds and adaptive contact quadrature prevent attributing the result solely to timestep.',
    'The local interval and full release refinement have different histories; their differences cannot be subtracted to identify a causal error contribution.',
    'Independent P2 force projection into the existing reduced basis is not full-nodal equilibrium, mesh/quadrature/timestep convergence, or anatomical calibration.',
  ],
};
fs.writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify(receipt,null,2));
