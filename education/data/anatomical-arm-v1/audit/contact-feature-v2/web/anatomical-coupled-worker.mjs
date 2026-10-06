import {coupledFixture,fixtureInitialState,stepCoupledFixture,fixtureMassEvent} from './anatomical-coupled-fixture.mjs';
let fixture=coupledFixture(),state=fixtureInitialState(fixture),epoch=0;
self.onmessage=({data})=>{
 const {id,kind}=data;
 try{
  if(kind==='reset'){epoch=data.epoch;state=fixtureInitialState(fixture);self.postMessage({id,epoch,kind,state});return;}
  if(data.epoch!==epoch)return;
  if(kind==='mass'){state=fixtureMassEvent(fixture,state,data.massKg);self.postMessage({id,epoch,kind,state});return;}
  if(kind==='step'){const start=performance.now(),r=stepCoupledFixture(fixture,state,{h:.04,excitation:data.effort});if(r.accepted)state=r.state;const result=r.result;self.postMessage({id,epoch,kind,state,accepted:r.accepted,diagnostic:{elapsedMS:performance.now()-start,reason:result.reason,iterations:result.acceptedIterations,evaluations:result.evaluations,postSolveObjectiveEvaluations:r.accepted?1:0,hessianProducts:result.hessianProducts,tissueTorqueNm:result.tissueTorqueNm,gravityTorqueNm:result.gravityTorqueNm,torqueBalanceNm:r.torqueBalanceNm,maximumFreeNodalForceN:result.maximumFreeNodalForceN,minJ:result.minJ,volumeRatio:result.volumeRatio,meanFibreStretch:result.meanFibreStretch,work:r.work}});return;}
  throw Error('Unknown worker action');
 }catch(error){self.postMessage({id,epoch,kind,error:String(error)});}
};
