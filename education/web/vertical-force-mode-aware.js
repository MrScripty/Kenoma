/* Presentation metadata only; immutable source dynamics remain delegated. */
import {createVerticalForceLab} from './vertical-force-model.js';

export function createModeAwareVerticalForceLab(P,controls){
  const base=createVerticalForceLab(P,controls);
  function annotate(o,mode){
    const active=mode==='PI';
    return {...o,forceTargetApplicable:active,capacityComparisonApplicable:active,
      driveMode:mode==='release'?'floor-drive':mode==='fixed'?'fixed-activation':'PI',
      saturated:active&&o.saturated,
      excitationFloorDrive:mode==='release',
      uraw:active?o.uraw:null,e:active?o.e:null};
  }
  return {...base,
    output:(z,cfg,phase)=>annotate(base.output(z,cfg,phase),phase.mode||'PI'),
    run:(cfg,dt)=>{const result=base.run(cfg,dt);return {...result,history:result.history.map(r=>annotate(r,r.mode))};}};
}
