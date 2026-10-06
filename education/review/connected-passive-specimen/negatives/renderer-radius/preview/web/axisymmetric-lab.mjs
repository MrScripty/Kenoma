import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {SceneStatus} from './scene-status.mjs';
import {prepareAxisymmetric,materialPoint,signedBoundaryVolume} from './axisymmetric-specimen.mjs';
const DEFAULTS=Object.freeze({epsilon:0,ratio:1.5,axialCells:16,radialCells:8,cap:25});
const fmt=(x,d=8)=>x===0?'0':Number(x).toPrecision(d);
export function displayedVertices(boundary){return boundary.vertices.map(v=>[v[2],1.05*v[0],1.05*v[1]]);}
const copy=x=>x===undefined?null:JSON.parse(JSON.stringify(x));
class AxisymmetricLab{
 constructor(root){
  this.root=root;root.axisymmetricLab=this;this.configuration={...DEFAULTS};this.sequence=0;this.view='oblique';this.cameraPose=null;this.renderCount=0;this.solveCount=0;
  this.sceneStatus=new SceneStatus(root,()=>this.stopRenderer());
  for(const el of root.querySelectorAll('[data-setting]'))el.addEventListener('change',()=>this.change());
  for(const el of root.querySelectorAll('[data-probe]'))el.addEventListener('change',()=>this.updateProbe());
  root.querySelector('[data-action=start]').addEventListener('click',()=>this.start());
  root.querySelector('[data-action=reset]').addEventListener('click',()=>this.reset());
  root.querySelector('[data-action=front]').addEventListener('click',()=>this.setView('front'));
  root.querySelector('[data-action=oblique]').addEventListener('click',()=>this.setView('oblique'));
  root.querySelector('[data-action=export]').addEventListener('click',()=>this.export());
  window.addEventListener('pagehide',()=>{this.worker?.terminate();this.stopRenderer();});
  this.sync();this.request(this.configuration);
 }
 sync(){
  for(const el of this.root.querySelectorAll('[data-setting]'))el.value=el.dataset.setting==='mesh'?`${this.configuration.axialCells},${this.configuration.radialCells}`:String(this.configuration[el.dataset.setting]);
 }
 change(){
  const read=name=>this.root.querySelector(`[data-setting=${name}]`).value,c={epsilon:Number(read('epsilon')),ratio:Number(read('ratio')),cap:Number(read('cap'))},sizes=read('mesh').split(',').map(Number);[c.axialCells,c.radialCells]=sizes;
  if(![-.1,0,.1].includes(c.epsilon)||![1,1.5].includes(c.ratio)||![1,25].includes(c.cap)||!['4,2','8,4','16,8'].includes(sizes.join(','))){this.sync();this.root.querySelector('.progress').textContent='Unsupported control. Preceding displayed approximation and its warning retained.';return;}
  this.request(c);
 }
 reset(){this.view='oblique';this.cameraPose=null;this.request({...DEFAULTS});if(this.camera)this.restoreCamera();}
 request(configuration){
  this.worker?.terminate();this.worker=null;const sequence=++this.sequence;
  this.root.dataset.busy='true';this.root.setAttribute('aria-busy','true');this.root.querySelector('.progress').textContent='Computing requested end displacement in a worker. Preceding displayed state remains visible.';
  const worker=new Worker(new URL('./axisymmetric-worker.js',import.meta.url),{type:'module'});this.worker=worker;
  worker.onmessage=({data})=>{
   if(data.sequence!==this.sequence)return;
   if(data.error){this.root.querySelector('.progress').textContent='Solve failed: '+data.error+'. Preceding displayed approximation retained.';this.sync();this.finish(false);return;}
   this.configuration=data.configuration;this.state=data.state;this.boundary=data.boundary;this.surfaceJ=data.surfaceJ;this.trace=data.trace;this.mesh=prepareAxisymmetric({...this.configuration,order:7});this.solveCount++;
   this.sync();this.updateReadouts();if(this.renderer){this.rebuild();this.draw();}this.finish();
  };
  worker.onerror=event=>{if(sequence===this.sequence){this.root.querySelector('.progress').textContent='Worker failed: '+event.message+'. Preceding displayed approximation retained.';this.sync();this.finish(false);}};
  worker.postMessage({sequence,configuration});
 }
 finish(success=true){this.worker?.terminate();this.worker=null;this.root.dataset.busy='false';this.root.setAttribute('aria-busy','false');if(success&&this.state)this.root.querySelector('.progress').textContent='Current numerical state displayed. Controls keep the camera and recompute the declared boundary problem.';}
 updateReadouts(){
  const d=this.state.diagnostics,vol=signedBoundaryVolume(displayedVertices(this.boundary).map(v=>Array.from(new Float32Array(v))),this.boundary.indices);
  this.renderTessellationVolumeM3=vol;this.root.dataset.converged=String(this.state.converged);
  this.root.querySelector('.solve-status').textContent=this.state.converged?'Newton stationary in this connected Q2 mesh: every free radial/axial residual meets the displayed target. Spatial/quadrature checks remain separate.':'Not converged: preceding/current finite-cap approximation, with its actual residual and boundary displacement shown. '+(this.state.failure||'Iteration cap reached.');
  const rows=[['Radius ratio / area ratio',`${this.configuration.ratio} / ${this.configuration.ratio**2}`],['Reference length L',fmt(this.mesh.parameters.length)+' m'],['Imposed end displacement',fmt(this.state.epsilon*this.mesh.parameters.length)+' m'],['Shear / bulk modulus',`${this.mesh.parameters.mu} / ${this.mesh.parameters.bulk} Pa (K/μ = 20)`],['Exact frustum reference volume',fmt(this.mesh.exactReferenceVolumeM3)+' m³'],['Integrated current volume',fmt(d.volumeM3)+' m³'],['Integrated current/reference V',fmt(d.volumeRatio)],['Finite render tessellation volume',fmt(vol)+' m³'],['Right end reaction',fmt(d.rightReactionN)+' N'],['Left + right reaction',fmt(d.endBalanceN)+' N'],['Stored energy',fmt(d.energyJ)+' J'],['Maximum free-force residual',fmt(d.maxFreeResidualN)+' N'],['Residual / μAmin',fmt(d.scaledMaxFreeResidual)],['Positive zero-load force scale μAmin',fmt(d.forceScaleN)+' N'],['Residual target (provisional)',fmt(this.state.tolerance)],['Free radial/axial DOFs',String(d.freeDofs)],['Gauss order / axis regularity',`${d.quadratureOrder}; r=0 and z_R=0 on axis`],['Quadrature min/max J',fmt(d.minQuadratureJ)+' / '+fmt(d.maxQuadratureJ)],['Volume-weighted RMS(J−1)',fmt(d.weightedRmsJDefect)]];
  this.root.querySelector('.totals').innerHTML=rows.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('');
  this.root.querySelector('.plot').innerHTML=this.plot();this.updateProbe();
 }
 plot(){
  const points=this.trace.map(p=>`${40+520*p.Z/.05},${210-150*p.axialLineStretch}`).join(' ');
  return `<svg viewBox="0 0 600 140" role="img" aria-label="Axial material-line stretch at half reference radius from solved field"><path d="M40 110H560 M40 10V110" stroke="#536578" fill="none"/><path d="M40 60H560" stroke="#adb9c6" stroke-dasharray="4 3"/><polyline points="${points}" stroke="#176fa0" fill="none" stroke-width="2"/><text x="4" y="65">λ=1</text><text x="42" y="132">Reference axial position Z (0 to 0.05 m)</text></svg>`;
 }
 updateProbe(){
  if(!this.state)return;const zf=Number(this.root.querySelector('[data-probe=z]').value),rf=Number(this.root.querySelector('[data-probe=r]').value),Z=zf*this.mesh.parameters.length,R=rf*this.mesh.parameters.radius*(1+(this.configuration.ratio-1)*zf),p=materialPoint(this.mesh,this.state,R,Z);this.probe=p;
  this.root.querySelector('.probe-readout').textContent=`Reference (R,Z)=(${fmt(R)},${fmt(Z)}) m; current (r,z)=(${fmt(p.r)},${fmt(p.z)}) m. Axial line stretch ${fmt(p.axialLineStretch)}; radial line stretch ${fmt(p.radialLineStretch)}; hoop stretch ${fmt(p.hoopStretch)}; shear entries r_Z=${fmt(p.v[1])}, z_R=${fmt(p.v[2])}; J=${fmt(p.J)}; σrr=${fmt(p.cauchy.rr)} Pa, σzz=${fmt(p.cauchy.zz)} Pa. Volume is measured, not corrected.`;
 }
 start(){
  if(!this.boundary){this.root.querySelector('.progress').textContent='Wait for the numerical state before starting 3D.';return;}
  this.stopRenderer();this.sceneStatus.begin();
  try{
   this.renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));this.renderer.setClearColor('#f4f7fb');this.sceneStatus.watch(this.renderer);
   this.root.querySelector('.scene-host').replaceChildren(this.renderer.domElement);this.renderer.domElement.setAttribute('aria-label','Actual connected passive specimen at physical scale');
   this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#f4f7fb');this.scene.add(new THREE.HemisphereLight(0xffffff,0x8095a7,2));const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(.04,.12,.15);this.scene.add(light);
   const grid=new THREE.GridHelper(.12,12,0x8293a3,0xd4e0e9);grid.rotation.x=Math.PI/2;grid.position.set(.025,0,-.02);this.scene.add(grid);const axes=new THREE.AxesHelper(.01);axes.position.set(-.018,-.018,0);this.scene.add(axes);
   this.camera=new THREE.OrthographicCamera(-.065,.065,.04,-.04,.001,2);this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.enableZoom=false;this.controls.enableDamping=false;
   this.controls.addEventListener('change',()=>{this.captureCamera();this.draw();});this.rebuild();this.resize();this.restoreCamera();this.draw();this.sceneStatus.ready(this.renderer);
   this.resizeObserver=new ResizeObserver(()=>this.resize());this.resizeObserver.observe(this.root.querySelector('.scene-host'));
  }catch(error){this.sceneStatus.fail(error,'initialization');}
 }
 captureCamera(){if(this.camera&&this.controls)this.cameraPose={position:this.camera.position.toArray(),target:this.controls.target.toArray(),up:this.camera.up.toArray()};}
 restoreCamera(){
  if(!this.camera)return;const p=this.cameraPose||{position:this.view==='front'?[.025,0,.3]:[.12,.06,.1],target:[.025,0,0],up:[0,1,0]};this.camera.position.fromArray(p.position);this.camera.up.fromArray(p.up);this.controls.target.fromArray(p.target);this.camera.lookAt(this.controls.target);this.controls.update();
 }
 setView(view){this.view=view;this.cameraPose=null;this.restoreCamera();this.draw();}
 resize(){if(!this.renderer)return;const h=this.root.querySelector('.scene-host'),w=h.clientWidth,height=h.clientHeight;this.renderer.setSize(w,height,false);this.camera.left=-.065;this.camera.right=.065;this.camera.top=.065*height/w;this.camera.bottom=-this.camera.top;this.camera.updateProjectionMatrix();this.draw();}
 rebuild(){
  if(!this.scene)return;if(this.assembly){this.scene.remove(this.assembly);this.disposeTree(this.assembly);}
  this.assembly=new THREE.Group();const g=new THREE.BufferGeometry(),positions=displayedVertices(this.boundary);g.setAttribute('position',new THREE.Float32BufferAttribute(positions.flat(),3));g.setIndex(this.boundary.indices.flat());
  const colours=this.surfaceJ.flatMap(J=>{const c=new THREE.Color('#dde8ec').lerp(new THREE.Color(J<1?'#c55b3f':'#167fba'),Math.min(1,Math.abs(J-1)/.01));return c.toArray();});g.setAttribute('color',new THREE.Float32BufferAttribute(colours,3));g.computeVertexNormals();
  this.currentMesh=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.8}));this.assembly.add(this.currentMesh);
  for(const angleIndex of [0,64,128,192]){
   const v=Array.from({length:this.boundary.rings},(_,j)=>this.boundary.referenceVertices[j*this.boundary.azimuth+angleIndex]).map(v=>new THREE.Vector3(v[2],v[0],v[1]));
   this.assembly.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(v),new THREE.LineBasicMaterial({color:0x8a9ba8,transparent:true,opacity:.7,depthTest:false})));
  }
  this.scene.add(this.assembly);
 }
 draw(){if(this.renderer)this.sceneStatus.draw(()=>{this.renderer.render(this.scene,this.camera);this.renderCount++;});}
 disposeTree(tree){tree?.traverse(o=>{o.geometry?.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m?.dispose();});}
 stopRenderer(){this.captureCamera();this.resizeObserver?.disconnect();this.sceneStatus?.detach();this.controls?.dispose();this.disposeTree(this.scene);if(this.renderer){const r=this.renderer;this.renderer=null;r.dispose();r.forceContextLoss();r.domElement.remove();}this.scene=null;this.currentMesh=null;this.camera=null;this.controls=null;}
 snapshot(){
  return {configuration:copy(this.configuration),state:copy(this.state),probe:copy(this.probe),boundary:this.boundary?copy(this.boundary):null,trace:copy(this.trace),solveCount:this.solveCount,busy:this.root.dataset.busy==='true',scene:{state:this.root.dataset.sceneState,canvasCount:this.root.querySelectorAll('canvas').length,drawCalls:this.renderer?.info.render.calls||0,renderCount:this.renderCount,positions:this.currentMesh?Array.from(this.currentMesh.geometry.attributes.position.array):[],indices:this.currentMesh?Array.from(this.currentMesh.geometry.index.array):[],camera:this.camera?{position:this.camera.position.toArray(),target:this.controls.target.toArray(),projection:this.camera.projectionMatrix.toArray()}:null,physicalScale:1},renderTessellationVolumeM3:this.renderTessellationVolumeM3};
 }
 export(){if(!this.state)return;const blob=new Blob([JSON.stringify(this.snapshot(),null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='connected-passive-specimen-state.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
}
if(typeof document!=='undefined')for(const root of document.querySelectorAll('[data-axisymmetric]'))new AxisymmetricLab(root);
