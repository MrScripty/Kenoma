/** Versioned, bounded presentation adapters. Existing educational laws are imported unchanged.
 * Geometry is SI except projection glyphs (abstract coordinates) and declared displacement magnification.
 * Nothing here is a clinical model or a new Lean theorem. */
import {forceState,leverState,springStep,springEnergy,exactSpring,DEFAULTS} from './mechanics.mjs';
import {deformationState,DEFORMATION_DEFAULTS,TETRAHEDRON_FACES,BOX_FACES} from './continuum-properties.mjs';
import {state as nonuniformState} from '../contributions/nonuniform-isochoric-kinematics/model.mjs';
import {materialCut} from '../contributions/architecture-force/model.mjs';
import {compressionPair,MATERIAL_DEFAULTS} from './material-response.mjs';
import {serialSpecimen,SERIAL_DEFAULTS} from './serial-specimen.mjs';
import {runProtocol,SLS_DEFAULTS} from './dissipative-bar.mjs';
import {ELBOW,activation,activeFiber,elbowInitial,elbowGeometry,elbowResults,elbowStep} from './elbow.mjs';
import {SERIES,seriesInitial,seriesResults} from './series.mjs';
import {TISSUE} from './tissue.mjs';
import {makeCase,solveReference,solveCompliant,diagnose,difference} from '../contributions/continuum_reference/continuum.mjs';
import {SPATIAL,SPATIAL_MESH,solveSpatial} from './spatial.mjs';
import {coupledFixture} from './anatomical-coupled-fixture.mjs';
import {attachmentMap} from './anatomical-transfer.mjs';
import {EDGE_PAIRS} from './anatomical-element.mjs';

const number=(key,label,min,max,step,value)=>({key,label,min,max,step,value,type:'number'});
const choice=(key,label,options,value)=>({key,label,options,value,type:'choice'});
export const CONTROLS=Object.freeze({
 force:[number('force','Net force (N)',-8,8,.5,4),number('mass','Mass (kg)',.5,5,.5,2),number('time','Elapsed time (s)',0,2,.25,1)],
 torque:[number('angle','Lever angle (degrees)',-120,120,5,30),number('mass','Load (kg)',1,8,.5,5)],
 energy:[choice('method','Integrator',['explicit','symplectic','verlet'],'symplectic'),choice('dt','Step size (s)',[.01,.02,.05],.02),number('steps','Completed steps',0,400,10,50)],
 deformation:[number('stretch','Axial stretch',.6,1.4,.05,1),number('shear','Prescribed shear',-.5,.5,.05,0),number('rotation','Rigid rotation (degrees)',0,180,30,0)],
 nonuniform:[number('gradient','Uneven-stretch amplitude a',-.6,.6,.1,.4),choice('compensate','Local compensation',['on','off'],'on'),choice('cells','Longitudinal cells',[8,32,128],32)],
 architecture:[number('angle','Pennation (degrees)',0,60,5,30),number('stretch','Material stretch',.6,1.4,.05,.8)],
 material:[number('stretch','Height stretch',.5,1,.05,.8),choice('bulk','Bulk modulus (Pa)',[0,50000,250000],50000),choice('iterations','Bisection cap',[8,32,64],64)],
 dissipative:[number('time','Protocol time (s)',0,7,.2,2),choice('holdMode','Hold constant',['force','extension'],'force')],
 serial:[number('force','Transmitted force (N)',-.1,.1,.01,.1),number('ratio','Reference area ratio',.5,4,.5,2),choice('iterations','Bisection cap',[8,48],48)],
 physiology:[number('angle','Prescribed hinge (degrees)',10,100,5,30),number('activation','Initial activation',0,1,.1,.3),number('excitation','Excitation',0,1,.1,.3),number('time','Elapsed time (s)',0,.3,.05,0)],
 elbow:[number('load','Load (kg)',0,5,.5,2),number('excitation','Excitation',0,1,.1,.6),number('steps','Steps of 0.005 s',0,80,5,20)],
 tendon:[number('angle','Prescribed hinge (degrees)',10,100,5,30),number('activation','Activation',0,.6,.1,.3),choice('tendon','Tendon model',['rigid','compliant'],'compliant'),choice('contact','Plate contact',['on','off'],'on')],
 continuum:[choice('sweeps','Compliant sweeps',[1,5,20],5),choice('order','Constraint order',['forward','reverse'],'forward')],
 projection:[choice('level','Pressure values',[1,2,4],1),choice('field','Prescribed sample field',['unresolved','paired','constant'],'unresolved')],
 spatial:[number('angle','Prescribed hinge (degrees)',0,90,10,30),number('activation','Shape activation',0,.6,.2,.2),choice('sweeps','Iteration cap',[80,160,320],80),choice('boneContact','Sampled bone contact',['on','off'],'on')],
 coupled:[number('sample','Saved sample (index)',0,11,1,0)],
 atlas:[{...choice('part','Atlas structure',['all','0','1','2','3','4','5','6','7','8','9'],'all'),optionLabels:{all:'All ten structures',0:'Humerus',1:'Radius',2:'Ulna',3:'Brachialis',4:'Biceps short head',5:'Biceps long head',6:'Triceps medial head',7:'Triceps lateral head',8:'Triceps long head',9:'Brachioradialis'}}],
 apparatus:[choice('part','Reference layer',['bones','muscles','both'],'both')],
 coverage:[choice('layer','Evidence class',['prescribed','atlas'],'prescribed'),number('stretch','Prescribed axial stretch',.6,1.4,.05,1.2)],
 research:[choice('layer','Research stage',['atlas','apparatus'],'atlas'),choice('part','Visible reference parts',['all','bones','muscles'],'all')],
 pose:[choice('preset','Prescribed pose',['neutral','translated','hand-on-torso','crossed-arms'],'neutral')]
});
/** Authored actions for the independent artistic poser, applied to its neutral scene.
 * IK targets reuse its existing contact-regression poses; none supplies forces or a contact solve. */
export function posePreset(preset){
 parameters('pose',{preset});
 const actions={neutral:[],translated:[{type:'placement',position:[.4,0,0]}],
  'hand-on-torso':[{type:'ik',limb:'rightArm',target:[.04,1.22,.20],pole:[.62,1.08,.30]}],
  'crossed-arms':[{type:'ik',limb:'rightArm',target:[-.18,1.28,.24],pole:[.45,.95,.28]},{type:'ik',limb:'leftArm',target:[.18,1.18,.28],pole:[-.45,.94,.30]}]};
 return structuredClone(actions[preset]);
}
export function parameters(kind,input={}){
 if(!Object.hasOwn(CONTROLS,kind))throw new RangeError('Unknown lesson kind');
 if(!input||typeof input!=='object'||Array.isArray(input))throw new TypeError('Object parameters required');
 const p={};for(const c of CONTROLS[kind]){const x=input[c.key]??c.value;if(c.type==='choice'){if(!c.options.includes(x))throw new RangeError('Unsupported '+c.key);}else if(!Number.isFinite(x)||x<c.min||x>c.max||Math.abs((x-c.min)/c.step-Math.round((x-c.min)/c.step))>1e-7)throw new RangeError('Out-of-domain '+c.key);p[c.key]=x;}
 if(Object.keys(input).some(k=>!Object.hasOwn(p,k)))throw new RangeError('Unknown parameter');return p;
}
const mesh=(vertices,faces,color='#067d91',opacity=1)=>({type:'mesh',vertices,faces,color,opacity});
const line=(points,color='#18363d')=>({type:'line',points,color});
const arrow=(origin,vector,color='#b65e36')=>({type:'arrow',origin,vector,color});
const sphere=(center,radius=.02,color='#067d91')=>({type:'sphere',center,radius,color});
const box=(size,center=[0,0,0],color='#067d91',opacity=1)=>mesh(Array.from({length:8},(_,i)=>size.map((s,d)=>center[d]+(((i>>d)&1)-.5)*s)),BOX_FACES,color,opacity);
const shifted=(vertices,delta)=>vertices.map(v=>v.map((x,i)=>x+delta[i]));
const metric=(label,value,unit='')=>[label,typeof value==='number'?Number(value.toPrecision(6))+(unit?' '+unit:''):String(value)];
const result=(kind,p,objects,metrics,note='')=>({version:1,kind,parameters:p,objects,metrics,note});
export function projectedSamples(level,field='unresolved'){
 // Exact same finite weighted grouping as standalone/pressure-projection-lab.html.
 const g={unresolved:[-.75,.25,-.25,.75],paired:[-.5,-.5,.25,.25],constant:[.25,.25,.25,.25]}[field];if(!g)throw new RangeError('Unsupported sample field');const weights=[1,3,2,2],groups={1:[[0,1,2,3]],2:[[0,1],[2,3]],4:[[0],[1],[2],[3]]}[level];
 if(!groups)throw new RangeError('Unsupported pressure space');const projected=Array(4).fill(0);
 for(const group of groups){const mean=group.reduce((s,i)=>s+weights[i]*g[i],0)/group.reduce((s,i)=>s+weights[i],0);for(const i of group)projected[i]=mean;}
 const residual=g.map((v,i)=>v-projected[i]);const energy=a=>4*a.reduce((s,v,i)=>s+weights[i]*v*v,0);
 return {g,weights,projected,residual,full:energy(g),condensed:energy(projected),gap:energy(residual)};
}
function coupledSurface(connectivity){
 const faces=new Map(),edges=new Map();for(const ids of connectivity){EDGE_PAIRS.forEach(([i,j],k)=>edges.set([ids[i],ids[j]].sort((a,b)=>a-b).join(','),ids[k+4]));for(const f of [[ids[0],ids[2],ids[1]],[ids[0],ids[1],ids[3]],[ids[0],ids[3],ids[2]],[ids[1],ids[2],ids[3]]]){const key=[...f].sort((a,b)=>a-b).join(',');if(faces.has(key))faces.delete(key);else faces.set(key,f);}}
 return [...faces.values()].flatMap(([a,b,c])=>{const e=(i,j)=>edges.get([i,j].sort((x,y)=>x-y).join(',')),ab=e(a,b),bc=e(b,c),ca=e(c,a);return [[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]];});
}
const slsCache=new Map();
export function lessonState(kind,input={},asset=null){
 const p=parameters(kind,input);let objects=[],metrics=[],note='';
 if(kind==='force'){
  const s=forceState(p);
  objects=[line([[-4.5,0,0],[4.5,0,0]],'#aebcab'),...Array.from({length:9},(_,i)=>line([[i-4,-.12,0],[i-4,.12,0]],'#52676d')),sphere([0,.3,0],.12,'#aebcab'),sphere([s.position,.3,0],.2),line([[0,.06,0],[s.position,.06,0]]),arrow([s.position,.3,0],[p.force*.2,0,0])];
  metrics=[metric('Time',p.time,'s'),metric('Acceleration',s.acceleration,'m/s²'),metric('Displacement',s.position,'m'),metric('Velocity',s.velocity,'m/s'),metric('Work',s.work,'J'),metric('Kinetic energy',s.kinetic,'J'),metric('Work minus kinetic energy',s.work-s.kinetic,'J')];
  note='From rest at x = 0; grey marker is the origin. Fixed ruler: 1 m ticks from −4 to +4 m. Force arrow: 0.2 display metres per N; sphere size has no physical meaning. Use Frame if a manual state leaves view.';
 }
 else if(kind==='torque'){
  const s=leverState({...p,length:.3});
  objects=[line([[0,0,0],[...s.r,0]]),line([[s.r[0],-.35,0],[s.r[0],.35,0]],'#aebcab'),line([[0,0,0],[s.r[0],0,0]],'#b65e36'),sphere([0,0,0],.015),arrow([...s.r,0],[0,s.force[1]*.004,0]),arrow([0,0,0],[0,0,s.torque*.02],'#067d91')];
  metrics=[metric('Gravity force Y',s.force[1],'N'),metric('Signed horizontal offset',s.r[0],'m'),metric('Moment arm',s.momentArm,'m'),metric('Torque about +Z',s.torque,'N m'),metric('Required static hold moment',-s.torque,'N m')];
  note='Grey vertical line is gravity’s line of action; orange horizontal line is the perpendicular offset. Prescribed pose requires the reported external hold moment. Force: 0.004 m/N; torque: 0.02 m/(N m).';
 }
 else if(kind==='energy'){
  const q={...DEFAULTS.energy,method:p.method,dt:p.dt},initial=springEnergy({x:q.x,v:q.v},q);let s={x:q.x,v:q.v},maximumDrift=0;
  for(let i=0;i<p.steps;i++){s=springStep(s,q);maximumDrift=Math.max(maximumDrift,Math.abs(springEnergy(s,q)-initial));}
  const E=springEnergy(s,q),reference=exactSpring(p.steps*q.dt,q);
  objects=[line([[-1.6,-.1,0],[1.6,-.1,0]],'#aebcab'),...Array.from({length:17},(_,i)=>line([[(i-8)*.2,-.12,0],[(i-8)*.2,-.08,0]],'#aebcab')),line([[0,-.15,0],[0,.1,0]],'#aebcab'),line([[0,0,0],[s.x,0,0]]),sphere([reference.x,0,0],.045,'#aebcab'),sphere([s.x,0,0],.055),arrow([s.x,0,0],[s.v*.1,0,0])];
  metrics=[metric('Time',p.steps*q.dt,'s'),metric('Position',s.x,'m'),metric('Analytic position',reference.x,'m'),metric('Absolute position error',Math.abs(s.x-reference.x),'m'),metric('Energy',E,'J'),metric('Drift from 0.8 J',E-initial,'J'),metric('Maximum energy deviation',100*maximumDrift/initial,'%')];
  note='x is extension from equilibrium at 0. Fixed ruler: 0.2 m ticks across ±1.6 m. Grey marker is the analytic reference at the same time. Maximum deviation includes every step. Marker sizes are illustrative. Velocity arrow: 0.1 display seconds. Use Frame if a manual state leaves view.';
 }
 else if(kind==='deformation'){const s=deformationState({...DEFORMATION_DEFAULTS,sx:p.stretch,sy:1,sz:1,shear:p.shear,angle:p.rotation});objects=[mesh(s.reference,TETRAHEDRON_FACES,'#b65e36',.2),mesh(s.current,TETRAHEDRON_FACES)];metrics=[metric('det F',s.J),metric('Measured volume ratio',s.volumeRatio),metric('Green strain norm',Math.hypot(...s.greenStrain)),metric('Reference Y-line stretch',s.materialLineStretches[1]),metric('Difference',s.volumeMeasurementDifference)];note='Orange reference; teal prescribed current geometry. Transverse diagonal stretches are 1. Rotation acts after stretch/shear; no equilibrium or stored-energy law.';}
 else if(kind==='coverage'&&p.layer==='prescribed'){const s=deformationState({...DEFORMATION_DEFAULTS,sx:p.stretch,sy:1,sz:1,shear:0,angle:0});objects=[mesh(s.reference,TETRAHEDRON_FACES,'#b65e36',.2),mesh(s.current,TETRAHEDRON_FACES)];metrics=[metric('det F',s.J),metric('Measured volume ratio',s.volumeRatio),metric('Difference',s.volumeMeasurementDifference)];note='Orange is reference; teal is prescribed current geometry. No equilibrium solve.';}
 else if(kind==='nonuniform'){const s=nonuniformState({gradient:p.gradient,compensate:p.compensate==='on',cells:p.cells});objects=[mesh(s.reference.vertices,s.reference.faces,'#b65e36',.18),mesh(s.deformed.vertices,s.deformed.faces)];metrics=[metric('Continuum volume ratio',s.continuumVolumeRatio),metric('Minimum local J',s.pointwiseJRange[0]),metric('Maximum local J',s.pointwiseJRange[1]),metric('Measured mesh ratio',s.meshVolumeRatio),metric('Mesh error',s.relativeMeshVolumeError),metric('Longitudinal cells',p.cells)];note='Mean axial stretch is 1. The boundary triangles approximate the curved imposed map; their nonzero volume error is retained. No material or force solve.';}
 else if(kind==='architecture'){const theta=p.angle*Math.PI/180,s=materialCut({referenceAreaM2:80e-6,lambda:p.stretch,J:1,nominalStressPa:300000,cosPennation:Math.cos(theta)});for(let i=0;i<7;i++){const y=(i-3)*.006;objects.push(line([[0,y,0],[.12*p.stretch*Math.cos(theta),y+.12*p.stretch*Math.sin(theta),0]],'#067d91'));}objects.push(box([.002,.055,.025],[.04,0,0],'#b65e36',.25),arrow([.14,0,0],[s.tendonDirectedForceN*.002,0,0]));metrics=[metric('Reference area',s.referenceAreaM2*1e6,'mm²'),metric('Current projected area',s.projectedCurrentAreaM2*1e6,'mm²'),metric('Cauchy fibre stress',s.cauchyFiberStressPa/1000,'kPa'),metric('Axial force',s.axialForceN,'N'),metric('Current-cut force',s.fromCurrentCutN,'N'),metric('Tendon-directed force',s.tendonDirectedForceN,'N')];note='Fixed nominal stress 300 kPa and imposed J=1. Seven orientation lines are not fibre counts; orange cut slab is schematic. Force arrow: 0.002 m/N. Stretch changes area and Cauchy stress, not the prescribed nominal force.';}
 else if(kind==='material'){const s=compressionPair({...MATERIAL_DEFAULTS,heightStretch:p.stretch,bulk:p.bulk,iterations:p.iterations});for(const [i,c]of [s.free,s.confined].entries())objects.push(box([c.widthM,c.heightM,c.depthM],[i*.14,c.heightM/2,0],i?'#b65e36':'#067d91'));metrics=[metric('Free lateral stretch',s.free.b),metric('Free J',s.free.J),metric('Confined J',s.confined.J),metric('Free plate force',s.free.plateForceN,'N'),metric('Confined plate force',s.confined.plateForceN,'N'),metric('Free lateral residual',s.free.lateralResidualPa,'Pa'),metric('Free converged',s.free.converged),metric('Residual criterion',s.solve.residualCriterionPa,'Pa'),metric('Wall reaction',s.confined.wallReactionPa,'Pa')];note='Teal free sides; orange unilateral walls. Mu=1500 Pa. Finite bisection iterates remain visible with their actual convergence status; a positive J alone does not certify equilibrium.';}
 else if(kind==='serial'){const s=serialSpecimen({...SERIAL_DEFAULTS,...p});objects=s.cells.map((c,i)=>mesh(c.currentVertices,BOX_FACES,i?'#b65e36':'#067d91'));objects.push(line([[s.cells[0].currentLengthM,0,0],[s.cells[1].currentVertices[0][0],0,0]],'#7d8991'));metrics=[metric('First stretch',s.cells[0].stretch),metric('Second stretch',s.cells[1].stretch),metric('First current area',s.cells[0].currentAreaM2*1e6,'mm²'),metric('Second current area',s.cells[1].currentAreaM2*1e6,'mm²'),metric('First volume ratio',s.cells[0].volumeRatio),metric('Second volume ratio',s.cells[1].volumeRatio),metric('Maximum force residual',Math.max(...s.cells.map(c=>Math.abs(c.forceResidualN))),'N'),metric('Force criterion',s.forceCriterionN,'N'),metric('Converged',s.converged)];note='Teal first block; orange second block; grey line is the ideal massless spacer. '+s.scope;}
 else if(kind==='dissipative'){if(!slsCache.has(p.holdMode))slsCache.set(p.holdMode,runProtocol({...SLS_DEFAULTS,holdMode:p.holdMode}));const trace=slsCache.get(p.holdMode).trace,s=trace.reduce((a,b)=>Math.abs(b.time-p.time)<Math.abs(a.time-p.time)?b:a);for(const c of s.samples){const width=Math.sqrt(c.areaM2),x=c.sM;objects.push(box([c.dxM*(1+c.strain),width,width],[x+(c.displacementStartM+c.displacementEndM)/2,0,0]));}metrics=[metric('Saved protocol time',s.time,'s'),metric('Phase',s.phase),metric('Axial force',s.force,'N'),metric('Extension',s.extensionM*1000,'mm'),metric('External work',s.workJ,'J'),metric('Storage',s.storageJ,'J'),metric('Dissipated',s.dissipationJ,'J'),metric('Work residual',s.balanceResidualJ,'J')];note='One-dimensional standard linear solid: load 0–1 s, hold 1–3 s, unload 3–4 s, recover 4–7 s. Cross-sections are prescribed, not solved. Geometry uses unscaled displacements; inspect the millimetre readout.';}
 else if(['physiology','elbow','tendon'].includes(kind)){
  const q={...(kind==='tendon'?SERIES:ELBOW),mode:kind==='elbow'?'forward':'prescribed',angle:p.angle??30,load:p.load??ELBOW.load,excitation:p.excitation??p.activation,tendon:p.tendon??SERIES.tendon,contact:p.contact??SERIES.contact},s0=elbowInitial(q);
  let s={...s0,a:p.activation??0};
  if(kind==='physiology'){const tau=p.excitation>=p.activation?q.rise:q.fall;s={...s,a:activation(p.activation,p.excitation,p.time,tau),time:p.time};}
  if(kind==='elbow')for(let i=0;i<p.steps;i++){s=elbowStep(s,q);if(s.halted)break;}
  const r=kind==='tendon'?seriesResults(s,q):elbowResults(s,q),end=[q.length*Math.sin(s.q),-q.length*Math.cos(s.q),0],origin=[0,q.origin,0],insertion=[...r.point,0],junction=origin.map((x,i)=>x+(insertion[i]-x)*r.fiber/r.length);
  objects=[line([[0,.25,0],[0,0,0],end]),sphere([0,0,0],.012),line([origin,junction],'#b65e36'),line([junction,insertion],'#067d91'),sphere(junction,.007,'#b65e36'),sphere(end,.025),arrow(insertion,origin.map((x,i)=>(x-insertion[i])/r.length*r.tension*.0002))];
  metrics=[metric('Time',s.time,'s'),metric('Angle',s.q*180/Math.PI,'degrees'),metric('Activation',s.a),metric('Path length',r.length,'m'),metric('Fiber length',r.fiber,'m'),metric('Moment arm',r.momentArm,'m'),metric('Active force',r.active,'N'),metric('Passive force',r.passive,'N'),metric('Tension',r.tension,'N')];
  if(kind==='elbow'){
   const initial=elbowResults(s0,q).energy;
   objects.push(line([[0,0,0],[q.length*Math.sin(s0.q),-q.length*Math.cos(s0.q),0]],'#aebcab'));
   metrics.push(metric('Angular velocity',s.w,'rad/s'),metric('Muscle moment',r.activeTorque+r.passiveTorque,'N m'),metric('Gravity moment',r.gravityTorque,'N m'),metric('Damping moment',r.dampingTorque,'N m'),metric('Work balance residual',r.energy-initial-s.work+s.dissipation,'J'),metric('Domain stop',s.halted));
   note='Forward RK4 hinge from 30° and rest; grey line is the initial forearm. Orange fiber and teal rigid tendon are path segments, not muscle shape. Tension arrow: 0.0002 m/N. '+(s.halted?'Halted at the last admissible state; reported time is the completed time.':'Constant excitation, no hidden hold motor or joint-contact solve.');
  }else if(kind==='tendon'){
   const t=r.tissue,center=[.15,.14,0],width=TISSUE.width*t.lateralStretch,depth=TISSUE.depth*t.lateralStretch;
   objects.push(box([width,t.height,depth],center),box([.13,.002,.075],[center[0],center[1]+t.gap/2+.001,0],'#aebcab'),box([.13,.002,.075],[center[0],center[1]-t.gap/2-.001,0],'#aebcab'));
   metrics.push(metric('Tendon length',r.tendon,'m'),metric('Tendon storage',r.tendonEnergy,'J'),metric('Force residual',r.forceResidual,'N'),metric('Length residual',r.lengthResidual,'m'),metric('Admissible fiber',r.admissible),metric('Tissue volume ratio',t.volumeRatio),metric('Plate reaction',t.normal,'N'),metric('Plate penetration',t.penetration,'m'),metric('Lateral stress residual',t.lateralStressResidual,'Pa'),metric('Required static hold moment',r.motorTorque,'N m'));
   note='Prescribed hold. Orange fiber and teal tendon split the solved path lengths; tension arrow: 0.0002 m/N. The separate block is an unrotated, translated reduced tissue inset with physical dimensions and grey plates, not registered arm anatomy. No trajectory or full tissue shape solve.';
  }else{
   metrics.push(metric('Excitation',p.excitation),metric('Force-length multiplier',activeFiber(r.fiber,1,q).force/q.maxForce),metric('Muscle moment',r.activeTorque+r.passiveTorque,'N m'),metric('Required static hold moment',r.motorTorque,'N m'));
   note='Prescribed hold with exact constant-input activation. Orange fiber and teal rigid tendon show path lengths, not tissue shape; tension arrow: 0.0002 m/N. Authored Gaussian force-length law; no force-velocity law or metabolic model.';
  }
 }
 else if(kind==='continuum'){const problem=makeCase({n:2,kind:'quadratic'}),zeros=problem.mesh.nodes.flatMap(()=>[0,0,0]),settings={h:.0005,u0:zeros,v0:zeros};const ref=solveReference(problem,settings),approx=solveCompliant(problem,{...settings,sweeps:p.sweeps,reverse:p.order==='reverse'});const faces=problem.mesh.surface.map(f=>f.tri);for(const [i,s]of [ref,approx].entries())objects.push(mesh(problem.mesh.nodes.map((x,j)=>x.map((v,d)=>v+20*s.u[3*j+d]+(d===0?i*.055:0))),faces,i?'#b65e36':'#067d91'));const dr=diagnose(problem,ref.u,settings),da=diagnose(problem,approx.u,settings),error=difference(problem,approx.u,ref.u,settings);metrics=[metric('Reference converged',ref.converged),metric('Reference residual',dr.residualN,'N'),metric('Reference target',ref.targetN,'N'),metric('Compliant residual',da.residualN,'N'),metric('Maximum nodal difference',error.maxNodalM*1e6,'µm'),metric('Relative objective-norm error',error.relativeObjectiveNorm),metric('Constraint visits',approx.constraintVisits),metric('Sweeps',p.sweeps)];note='One 0.5 ms implicit step on 48 linear tetrahedra, identical loads/materials/masses. Teal PCG reference; orange finite-sweep approximation. Displacements ×20; diagnostics use unscaled metres. This is not the chapter’s static manufactured-solution experiment.';}
 else if(kind==='projection'){const s=projectedSamples(p.level,p.field);for(const [j,key]of ['g','projected','residual'].entries())for(let i=0;i<4;i++)objects.push(arrow([i*.3,0,j*.45],[0,s[key][i],0],['#067d91','#518163','#b65e36'][j]));metrics=[metric('Full energy',s.full),metric('Represented energy',s.condensed),metric('Unresolved energy',s.gap),metric('Energy identity defect',s.full-s.condensed-s.gap)];note='Teal g; green Pg; orange residual g−Pg, front to back. Weights (1,3,2,2), K=8. Glyphs and energies are abstract weighted samples, not tissue pressure or a deformation solve.';}
 else if(kind==='spatial'){const s=solveSpatial(p.angle*Math.PI/180,p.activation,{...SPATIAL,sweeps:p.sweeps,boneContact:p.boneContact});objects=[mesh(s.x,SPATIAL_MESH.surface),mesh(s.baseline,SPATIAL_MESH.skinSurface,'#b65e36',.25)];metrics=[metric('Maximum free force',s.maxFreeForceN,'N'),metric('Free L2 residual',s.freeResidualN,'N'),metric('Stopping criterion',2e-5,'N per coordinate'),metric('Converged',s.converged),metric('Minimum J',s.minJ),metric('Baseline minimum J',s.baselineMinJ),metric('Mean J',s.meanJ),metric('Upper span',s.muscleLengthM*1000,'mm'),metric('Maximum penetration',s.maxPenetrationM*1000,'mm'),metric('Iterations',s.iterations)];note='Teal authored edge/volume network; orange same-pose artistic skin baseline. Sampled compliant contact can penetrate. Local residual controls convergence; pose/activation are prescribed and shape reactions do not drive the hinge. This is not FEM or calibrated anatomy.';}
 else if(kind==='coupled'){
  if(!Array.isArray(asset?.runs?.[0]?.rows)||!asset.runs[0].rows[p.sample])throw new Error('Requested saved coupling sample is unavailable');
  const row=asset.runs[0].rows[p.sample],f=coupledFixture(),display=v=>[v[0],-v[2],v[1]],point=X=>attachmentMap(X,f.frame,row.qRad).position;
  objects=[mesh(row.positionsM.map(display),coupledSurface(f.block.connectivity)),line([display(f.frame.origin_m),display(point(f.grip))],'#426da4'),sphere(display(f.frame.origin_m),.008,'#426da4'),sphere(display(point(f.grip)),.014,'#80569b'),...f.tendons.map(t=>({...line([display(row.positionsM[t.node]),display(point(t.anchor))],'#b68b36'),role:'tendon-branch'})),...f.tendons.map(t=>({...line([display(point(t.anchor)),display(f.frame.origin_m)],'#426da4'),role:'rigid-carrier-guide'}))];
  metrics=[metric('Saved time',row.timeS,'s'),metric('Hinge angle',row.qRad*180/Math.PI,'degrees'),metric('Excitation',row.excitation),metric('Activation',row.activation),metric('Angular velocity',row.angularVelocityRadS,'rad/s'),metric('Tissue torque',row.tissueTorqueNm,'N m'),metric('Maximum free nodal residual',row.maximumNodalForceN,'N'),metric('Joint torque residual',row.torqueBalanceNm,'N m'),metric('Work defect',row.nonlinearEndpointWorkDefectJ,'J'),metric('Minimum J',row.minJ)];
  note='Saved synthetic fixture: teal tissue, gold tendon branches, blue hinge lever, violet load marker. Blue carrier guides join the actual rigid attachment points to their hinge; these are diagrammatic mounting guides, not tendon extensions or modeled structural bars. Source +Z downward is rotated to screen-world −Y; lengths remain metres. Saved coordinates and rigid attachment maps only; no new solve. A small force residual does not remove the recorded work defect.';
 }
 else if(kind==='atlas'||(kind==='coverage'&&p.layer==='atlas')||(kind==='research'&&p.layer==='atlas')){
  if(!asset?.parts)throw new Error('Atlas asset required');
  const parts=asset.parts.map((a,i)=>({...a,partIndex:i})).filter(a=>!p.part||p.part==='all'||(p.part==='bones'?a.partIndex<3:p.part==='muscles'?a.partIndex>=3:Number(p.part)===a.partIndex));
  objects=parts.map(a=>({...mesh(a.vertices_m.map(v=>[v[0],v[2],-v[1]]),a.triangles_zero_based,a.partIndex<3?'#aebcab':'#b65e36',.85),source:{name:a.name,hash:a.source_sha256,path:a.source_obj,vertices:a.vertex_count,triangles:a.triangle_count}}));
  metrics=[metric('Parts',parts.length),metric('Vertices',parts.reduce((n,a)=>n+a.vertex_count,0)),metric('Triangles',parts.reduce((n,a)=>n+a.triangle_count,0)),metric('Source length unit',asset.length_unit),metric('Licence',asset.license),metric('Subject registration',asset.registered_to_other_assets),metric('Clinical validation',asset.clinical_validation)];
  note='Static constructed BodyParts3D reference atlas. Display rotates source +Z into up; metre coordinates and topology are preserved. Select a named part for its provenance. No posed anatomical rig, measured fibre field or registration to the recorded participant.';
 }
 else if(kind==='apparatus'||(kind==='research'&&p.layer==='apparatus')){
  if(!asset?.geometry||!asset?.trajectory)throw new Error('Apparatus reference and trajectory evidence required');
  const {geometry:g,trajectory:t}=asset,display=v=>[v[0],v[2],-v[1]];
  if(p.part!=='muscles')objects.push(...g.bones.map(a=>mesh(a.vertices_m.map(display),a.triangles,'#aebcab')));
  if(p.part!=='bones')objects.push(...g.muscles.map(a=>mesh(a.nodes_m.map(display),a.surface_triangles,'#b65e36',.7)));
  metrics=[metric('Reference bones',g.bones.length),metric('Reference muscles',g.muscles.length),metric('Historical trajectory completed',t.completedAllSteps),metric('Historical accepted snapshots',t.snapshots.length),metric('Historical rejection',t.attempts[0]?.reason??'See receipt'),metric('Historical residual',t.attempts[0]?.residualN??'Unavailable','N'),metric('Historical residual gate',t.parameters.stationarityToleranceN,'N')];
  note='Original arm-geometry.json reference remesh, before the later reference repair; +Z is displayed up. This geometry is not a solved pose. The selected historical arm-trajectory-results.json has no accepted snapshots. Later reduced-model trajectory receipts are discussed separately in the chapter; they do not establish full nodal, quadrature or physiological convergence.';
 }
 else if(kind==='pose'){
  metrics=[metric('Prescribed pose',p.preset),metric('Pose actions',posePreset(p.preset).length),metric('Force / pressure','Not modeled'),metric('Contact response','Not modeled')];
  note='Independent artistic poser: prescribed placement or IK targets followed by geometric skinning. Neutral resets the authored pose; translation does not deform it. Hand-on-torso and crossed-arms do not supply collision detection, contact force or a tissue solve.';
 }
 else throw new RangeError('Unsupported adapter');
 const out=result(kind,p,objects,metrics,note);validateScene(out);return out;
}
export function validateScene(s){
 if(!s||s.version!==1||!Array.isArray(s.objects)||s.objects.length>256)throw new Error('Invalid scene contract');
 const vector=v=>Array.isArray(v)&&v.length===3&&[0,1,2].every(i=>Object.hasOwn(v,i)&&Number.isFinite(v[i]));
 for(const o of s.objects){
  if(!o||!['mesh','line','arrow','sphere'].includes(o.type))throw new Error('Unsupported scene object');
  const vectors=o.type==='mesh'?o.vertices:o.type==='line'?o.points:o.type==='arrow'?[o.origin,o.vector]:[o.center];
  if(!Array.isArray(vectors)||!Array.from(vectors).every(vector))throw new Error('Nonfinite scene geometry');
  if(o.type==='sphere'&&(!Number.isFinite(o.radius)||o.radius<=0))throw new Error('Invalid sphere radius');
  if(o.type==='mesh'&&(!Array.isArray(o.faces)||!Array.from(o.faces).every(f=>Array.isArray(f)&&f.length===3&&[0,1,2].every(k=>Object.hasOwn(f,k)&&Number.isInteger(f[k])&&f[k]>=0&&f[k]<o.vertices.length))))throw new Error('Invalid triangle index');
 }
 return s;
}
