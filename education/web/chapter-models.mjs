/** Versioned, bounded presentation adapters. Existing educational laws are imported unchanged.
 * Geometry is SI except projection glyphs (abstract coordinates) and declared displacement magnification.
 * Nothing here is a clinical model or a new Lean theorem. */
import {forceState,leverState,springStep,springEnergy,DEFAULTS} from './mechanics.mjs';
import {deformationState,DEFORMATION_DEFAULTS,TETRAHEDRON_FACES,BOX_FACES} from './continuum-properties.mjs';
import {state as nonuniformState} from '../contributions/nonuniform-isochoric-kinematics/model.mjs';
import {materialCut} from '../contributions/architecture-force/model.mjs';
import {compressionPair,MATERIAL_DEFAULTS} from './material-response.mjs';
import {serialSpecimen,SERIAL_DEFAULTS} from './serial-specimen.mjs';
import {runProtocol,SLS_DEFAULTS} from './dissipative-bar.mjs';
import {ELBOW,elbowInitial,elbowGeometry,elbowResults,elbowStep} from './elbow.mjs';
import {SERIES,seriesInitial,seriesResults} from './series.mjs';
import {makeCase,solveReference,solveCompliant,diagnose} from '../contributions/continuum_reference/continuum.mjs';
import {SPATIAL,SPATIAL_MESH,solveSpatial} from './spatial.mjs';
import {coupledFixture} from './anatomical-coupled-fixture.mjs';
import {EDGE_PAIRS} from './anatomical-element.mjs';

const number=(key,label,min,max,step,value)=>({key,label,min,max,step,value,type:'number'});
const choice=(key,label,options,value)=>({key,label,options,value,type:'choice'});
export const CONTROLS=Object.freeze({
 force:[number('force','Net force (N)',-8,8,.5,4),number('mass','Mass (kg)',.5,5,.5,2)],
 torque:[number('angle','Lever angle (degrees)',-80,80,5,30),number('mass','Load (kg)',1,8,.5,5)],
 energy:[choice('method','Integrator',['explicit','symplectic','verlet'],'symplectic'),number('steps','Steps of 0.02 s',0,200,10,50)],
 deformation:[number('stretch','Axial stretch',.6,1.4,.05,1.2),number('shear','Prescribed shear',-.5,.5,.05,.25)],
 nonuniform:[number('gradient','Uneven-stretch amplitude a',-.6,.6,.1,.4),choice('compensate','Local compensation',['on','off'],'on')],
 architecture:[number('angle','Pennation (degrees)',0,60,5,30),number('stretch','Material stretch',.6,1.4,.05,.8)],
 material:[number('stretch','Height stretch',.5,1,.05,.8)],
 dissipative:[number('time','Protocol time (s)',0,7,.2,2)],
 serial:[number('force','Transmitted force (N)',-.1,.1,.01,.1),number('ratio','Reference area ratio',.5,4,.5,2)],
 physiology:[number('angle','Prescribed hinge (degrees)',10,100,5,30),number('activation','Activation (unit 1)',0,1,.1,.3)],
 elbow:[number('load','Load (kg)',0,5,.5,2),number('steps','Steps of 0.005 s',0,80,5,20)],
 tendon:[number('angle','Prescribed hinge (degrees)',10,100,5,30),number('activation','Activation (unit 1)',0,.6,.1,.3)],
 continuum:[choice('sweeps','Compliant sweeps',[1,5,20],5)],
 projection:[choice('level','Pressure values',[1,2,4],1)],
 spatial:[number('angle','Prescribed hinge (degrees)',10,90,10,30)],
 coupled:[number('sample','Saved sample (index)',0,11,1,0)],
 atlas:[choice('part','Atlas structure',['all','0','1','2','3','4','5','6','7','8','9'],'all')],
 apparatus:[choice('part','Reference layer',['bones','muscles','both'],'both')],
 coverage:[choice('layer','Evidence class',['prescribed','atlas'],'prescribed')],
 research:[choice('layer','Research stage',['atlas','apparatus'],'atlas')],
 pose:[]
});
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
export function projectedSamples(level){
 // Exact same finite weighted grouping as standalone/pressure-projection-lab.html.
 const g=[-.75,.25,-.25,.75],weights=[1,3,2,2],groups={1:[[0,1,2,3]],2:[[0,1],[2,3]],4:[[0],[1],[2],[3]]}[level];
 if(!groups)throw new RangeError('Unsupported pressure space');const projected=Array(4).fill(0);
 for(const group of groups){const mean=group.reduce((s,i)=>s+weights[i]*g[i],0)/group.reduce((s,i)=>s+weights[i],0);for(const i of group)projected[i]=mean;}
 const residual=g.map((v,i)=>v-projected[i]);const energy=a=>4*a.reduce((s,v,i)=>s+weights[i]*v*v,0);
 return {g,weights,projected,residual,full:energy(g),condensed:energy(projected),gap:energy(residual)};
}
function coupledSurface(connectivity){
 const faces=new Map(),edges=new Map();for(const ids of connectivity){EDGE_PAIRS.forEach(([i,j],k)=>edges.set([ids[i],ids[j]].sort((a,b)=>a-b).join(','),ids[k+4]));for(const f of [[ids[0],ids[2],ids[1]],[ids[0],ids[1],ids[3]],[ids[0],ids[3],ids[2]],[ids[1],ids[2],ids[3]]]){const key=[...f].sort((a,b)=>a-b).join(',');if(faces.has(key))faces.delete(key);else faces.set(key,f);}}
 return [...faces.values()].flatMap(([a,b,c])=>{const e=(i,j)=>edges.get([i,j].sort((x,y)=>x-y).join(',')),ab=e(a,b),bc=e(b,c),ca=e(c,a);return [[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]];});
}
const sls=()=>runProtocol(SLS_DEFAULTS);let slsCache;
export function lessonState(kind,input={},asset=null){
 const p=parameters(kind,input);let objects=[],metrics=[],note='';
 if(kind==='force'){const s=forceState({...p,time:1});objects=[sphere([s.position,.15,0],.1),line([[0,0,0],[s.position,0,0]]),arrow([s.position,.15,0],[p.force*.08,0,0])];metrics=[metric('Acceleration',s.acceleration,'m/s²'),metric('Displacement at 1 s',s.position,'m'),metric('Work',s.work,'J')];note='Force arrow: 0.08 display metres per N.';}
 else if(kind==='torque'){const s=leverState({...p,length:.3});objects=[line([[0,0,0],[...s.r,0]]),sphere([0,0,0],.015),arrow([...s.r,0],[0,s.force[1]*.004,0]),arrow([0,0,0],[0,0,s.torque*.02],'#067d91')];metrics=[metric('Moment arm',s.momentArm,'m'),metric('Torque about +Z',s.torque,'N m')];note='Force: 0.004 m/N; torque: 0.02 m/(N m).';}
 else if(kind==='energy'){const q={...DEFAULTS.energy,method:p.method};let s={x:q.x,v:q.v};for(let i=0;i<p.steps;i++)s=springStep(s,q);const E=springEnergy(s,q);objects=[line([[-.4,0,0],[s.x,0,0]]),sphere([s.x,0,0],.04),arrow([s.x,0,0],[s.v*.1,0,0])];metrics=[metric('Time',p.steps*q.dt,'s'),metric('Position',s.x,'m'),metric('Energy',E,'J'),metric('Drift from 0.8 J',E-.8,'J')];note='Velocity arrow uses 0.1 display seconds; no visual energy-conservation badge.';}
 else if(kind==='deformation'||(kind==='coverage'&&p.layer==='prescribed')){const s=deformationState({...DEFORMATION_DEFAULTS,sx:p.stretch??1.2,shear:p.shear??.25});objects=[mesh(s.reference,TETRAHEDRON_FACES,'#b65e36',.2),mesh(s.current,TETRAHEDRON_FACES)];metrics=[metric('det F',s.J),metric('Measured volume ratio',s.volumeRatio),metric('Difference',s.volumeMeasurementDifference)];note='Orange is reference; teal is prescribed current geometry. No equilibrium solve.';}
 else if(kind==='nonuniform'){const s=nonuniformState({gradient:p.gradient,compensate:p.compensate==='on'});objects=[mesh(s.reference.vertices,s.reference.faces,'#b65e36',.18),mesh(s.deformed.vertices,s.deformed.faces)];metrics=[metric('Continuum volume ratio',s.continuumVolumeRatio),metric('Measured mesh ratio',s.meshVolumeRatio),metric('Mesh error',s.relativeMeshVolumeError)];note='The actual original triangle mesh is displayed; its discretization error is retained.';}
 else if(kind==='architecture'){const theta=p.angle*Math.PI/180,s=materialCut({referenceAreaM2:80e-6,lambda:p.stretch,J:1,nominalStressPa:300000,cosPennation:Math.cos(theta)});for(let i=0;i<7;i++){const y=(i-3)*.006;objects.push(line([[0,y,0],[.12*p.stretch*Math.cos(theta),y+.12*p.stretch*Math.sin(theta),0]],'#067d91'));}objects.push(box([.002,.055,.025],[.04,0,0],'#b65e36',.25),arrow([.14,0,0],[s.tendonDirectedForceN*.002,0,0]));metrics=[metric('Current projected area',s.projectedCurrentAreaM2*1e6,'mm²'),metric('Axial force',s.axialForceN,'N'),metric('Current-cut force',s.fromCurrentCutN,'N'),metric('Tendon-directed force',s.tendonDirectedForceN,'N')];note='Seven lines schematically indicate orientation, not measured fibre count. Cut slab is a diagram; areas are the analytic readout. Force arrow: 0.002 m/N.';}
 else if(kind==='material'){const s=compressionPair({...MATERIAL_DEFAULTS,heightStretch:p.stretch});for(const [i,c]of [s.free,s.confined].entries())objects.push(box([c.widthM,c.heightM,c.depthM],[i*.14,c.heightM/2,0],i?'#b65e36':'#067d91'));metrics=[metric('Free J',s.free.J),metric('Confined J',s.confined.J),metric('Free lateral residual',s.free.lateralResidualPa,'Pa'),metric('Wall reaction',s.confined.wallReactionPa,'Pa')];note='Teal: free sides. Orange: confined sides. Dimensions come from the original reduced solve.';}
 else if(kind==='serial'){const s=serialSpecimen({...SERIAL_DEFAULTS,...p});objects=s.cells.map((c,i)=>mesh(c.currentVertices,BOX_FACES,i?'#b65e36':'#067d91'));metrics=[metric('First stretch',s.cells[0].stretch),metric('Second stretch',s.cells[1].stretch),metric('First volume ratio',s.cells[0].volumeRatio),metric('Second volume ratio',s.cells[1].volumeRatio),metric('Converged',s.converged)];note=s.scope;}
 else if(kind==='dissipative'){slsCache??=sls();const s=slsCache.trace.reduce((a,b)=>Math.abs(b.time-p.time)<Math.abs(a.time-p.time)?b:a);for(const c of s.samples){const width=Math.sqrt(c.areaM2),x=c.sM;objects.push(box([c.dxM*(1+c.strain),width,width],[x+(c.displacementStartM+c.displacementEndM)/2,0,0]));}metrics=[metric('Saved protocol time',s.time,'s'),metric('Extension',s.extensionM,'m'),metric('Storage',s.storageJ,'J'),metric('Dissipated',s.dissipationJ,'J'),metric('Work residual',s.balanceResidualJ,'J')];note='Original finite protocol recomputed once; no transverse contraction model. Geometric displacement is not magnified.';}
 else if(['physiology','elbow','tendon'].includes(kind)){const q={...ELBOW,angle:p.angle??30,load:p.load??ELBOW.load},s0=elbowInitial(q);let s={...s0,a:p.activation??0};if(kind==='elbow')for(let i=0;i<p.steps;i++){s=elbowStep(s,q);if(s.halted)break;}const r=kind==='tendon'?seriesResults(s,{...SERIES,mode:'prescribed'}):elbowResults(s,q);const end=[q.length*Math.sin(s.q),-q.length*Math.cos(s.q),0],origin=[0,q.origin,0],insertion=[...r.point,0];objects=[line([[0,.25,0],[0,0,0],end]),sphere([0,0,0],.012),line([origin,insertion],'#b65e36'),sphere(end,.025)];metrics=[metric('Angle',s.q*180/Math.PI,'degrees'),metric('Activation',s.a),metric('Path length',r.length,'m'),metric('Moment arm',r.momentArm,'m'),metric('Tension',r.tension,'N')];if(kind==='tendon')metrics.push(metric('Tendon length',r.tendon,'m'),metric('Force residual',r.forceResidual,'N'));note=kind==='elbow'?(s.halted?'Halted at last admissible state.':'Existing RK4 hinge; no new joint contact.'):'Prescribed static state; no trajectory or shape solve.';}
 else if(kind==='continuum'){const problem=makeCase({n:2,kind:'quadratic'}),zeros=problem.mesh.nodes.flatMap(()=>[0,0,0]),settings={h:.0005,u0:zeros,v0:zeros};const ref=solveReference(problem,settings),approx=solveCompliant(problem,{...settings,sweeps:p.sweeps});const faces=problem.mesh.surface.map(f=>f.tri);for(const [i,s]of [ref,approx].entries())objects.push(mesh(problem.mesh.nodes.map((x,j)=>x.map((v,d)=>v+20*s.u[3*j+d]+(d===0?i*.055:0))),faces,i?'#b65e36':'#067d91'));const dr=diagnose(problem,ref.u,settings),da=diagnose(problem,approx.u,settings);metrics=[metric('Reference converged',ref.converged),metric('Reference residual',dr.residualN,'N'),metric('Compliant residual',da.residualN,'N'),metric('Sweeps',p.sweeps)];note='Same mesh, load and implicit step. Displacements ×20 for visibility; diagnostics use unscaled metres. Teal reference; orange finite-sweep approximation.';}
 else if(kind==='projection'){const s=projectedSamples(p.level);for(const [j,key]of ['g','projected','residual'].entries())for(let i=0;i<4;i++)objects.push(arrow([i*.3,0,j*.45],[0,s[key][i],0],['#067d91','#518163','#b65e36'][j]));metrics=[metric('Full energy',s.full),metric('Represented energy',s.condensed),metric('Unresolved energy',s.gap)];note='Front to back: g, Pg, residual. Coordinates and energies are abstract weighted-sample quantities, not metres or tissue pressure.';}
 else if(kind==='spatial'){const s=solveSpatial(p.angle*Math.PI/180,.2,{...SPATIAL,sweeps:80});objects=[mesh(s.x,SPATIAL_MESH.surface),mesh(s.baseline,SPATIAL_MESH.skinSurface,'#b65e36',.25)];metrics=[metric('Free residual',s.freeResidualN,'N'),metric('Converged',s.converged),metric('Minimum J',s.minJ),metric('Maximum penetration',s.maxPenetrationM,'m')];note='Existing 80-sweep cap; iteration count is not acceptance. Orange: baseline artistic skin; no hinge reaction feedback.';}
 else if(kind==='coupled'){if(!asset)throw new Error('Saved coupling evidence required');const rows=asset.runs[0].rows,row=rows[Math.min(p.sample,rows.length-1)],f=coupledFixture();objects=[mesh(row.positionsM,coupledSurface(f.block.connectivity))];metrics=[metric('Saved time',row.timeS,'s'),metric('Maximum free nodal residual',row.maximumNodalForceN,'N'),metric('Work defect',row.nonlinearEndpointWorkDefectJ,'J'),metric('Minimum J',row.minJ)];note='Saved authored tissue boundary only, displayed in original fixture axes (+Z downward). Historical receipt is not a new qualification run.';}
 else if(kind==='atlas'||(kind==='coverage'&&p.layer==='atlas')||(kind==='research'&&p.layer==='atlas')){if(!asset?.parts)throw new Error('Atlas asset required');const parts=asset.parts.map((a,i)=>({...a,partIndex:i})).filter(a=>!p.part||p.part==='all'||Number(p.part)===a.partIndex);objects=parts.map(a=>({...mesh(a.vertices_m.map(v=>[v[0],v[2],-v[1]]),a.triangles_zero_based,a.partIndex<3?'#aebcab':'#b65e36',.85),source:{name:a.name,hash:a.source_sha256,path:a.source_obj,vertices:a.vertex_count,triangles:a.triangle_count}}));metrics=[metric('Parts',parts.length),metric('Source length unit',asset.length_unit),metric('Licence',asset.license),metric('Subject registration',asset.registered_to_other_assets)];note='Display rotates source +Z into up; original metre coordinates and topology are preserved. Click a surface for its provenance.';}
 else if(kind==='apparatus'||(kind==='research'&&p.layer==='apparatus')){if(!asset?.geometry)throw new Error('Apparatus reference evidence required');const {geometry:g,trajectory:t}=asset;if(p.part!=='muscles')objects.push(...g.bones.map(a=>mesh(a.vertices_m,a.triangles,'#aebcab')));if(p.part!=='bones')objects.push(...g.muscles.map(a=>mesh(a.nodes_m,a.surface_triangles,'#b65e36',.7)));metrics=[metric('Reference bones',g.bones.length),metric('Reference muscles',g.muscles.length),metric('Trajectory completed',t.completedAllSteps),metric('Saved accepted snapshots',t.snapshots.length),metric('Original rejection',t.attempts[0]?.reason??'See receipt')];note='Reference geometry only. The failed trajectory has no accepted snapshots; no successful motion is fabricated.';}
 else if(kind==='pose'){note='Open the independent gizmo-only poser.';}
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
