import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {SceneStatus} from './scene-status.mjs';
import {BOX_FACES} from './continuum-properties.mjs';
import {SERIAL_DEFAULTS,validateSerialParameters,serialSpecimen,globalVolumeOnlyCandidate} from './serial-specimen.mjs';

const DISPLAY=Object.freeze({displacementMagnification:1,gridSpacingM:.01,fixedPhysicalWidthM:.224,strainPalette:[-.4,.75],forceArrowScaleMPerN:.2});
const TARGET=[.065,0,0];
const fmt=(value,digits=7)=>value===0?'0':Number(value).toPrecision(digits);
const colour=strain=>{
 const amount=Math.min(1,Math.abs(strain)/(strain<0?.4:.75));
 return new THREE.Color('#e4edf0').lerp(new THREE.Color(strain<0?'#bd5129':'#1677ba'),amount);
};
// Only this displayed-coordinate adapter is used to construct the real mesh.
export function displayedVertices(cell){return cell.currentVertices.map(vertex=>[...vertex]);}
function boxGeometry(vertices){
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices.flat(),3));
 geometry.setIndex(BOX_FACES.flat());geometry.computeVertexNormals();return geometry;
}
function lineGeometry(vertices){return new THREE.BufferGeometry().setFromPoints(vertices.map(v=>new THREE.Vector3(...v)));}
function geometrySnapshot(mesh){
 mesh.updateWorldMatrix(true,false);const p=mesh.geometry.getAttribute('position'),v=new THREE.Vector3(),positions=[];
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);positions.push(v.toArray());}
 return {cellIndex:mesh.userData.cellIndex,positions,indices:Array.from(mesh.geometry.index?.array||[])};
}

export class SerialLab{
 constructor(root){
  this.root=root;root.serialLab=this;this.renderCount=0;this.totalDrawCalls=0;this.view='oblique';this.cameraPose=null;
  this.sceneStatus=new SceneStatus(root,()=>this.stopRenderer());
  const fail=this.sceneStatus.fail.bind(this.sceneStatus);
  this.sceneStatus.fail=(error,stage)=>{fail(error,stage);root.querySelector('.scene-notice').textContent='Numerical-only current solution. The static undeformed reference does not move. Numerical controls retain or update the SI results; retry interactive 3D above.';this.announce('3D unavailable. Current numerical state retained; static undeformed reference shown.');};
  root.querySelectorAll('[data-param]').forEach(input=>input.addEventListener('input',()=>this.change(input)));
  for(const [action,handler] of Object.entries({start:()=>this.start(),reset:()=>this.reset(),front:()=>this.setView('front'),oblique:()=>this.setView('oblique'),'reject-volume':()=>this.rejectCandidate(),copy:()=>this.copy(),export:()=>this.export(),summary:()=>this.summary()}))root.querySelector('[data-action='+action+']')?.addEventListener('click',handler);
  this.reset();root.dataset.enhanced='true';
 }
 announce(message){this.root.querySelector('.announce').textContent=message;}
 sync(){this.root.querySelectorAll('[data-param]').forEach(input=>{input.value=this.params[input.dataset.param];input.removeAttribute('aria-invalid');});}
 hidePreset(){const el=this.root.querySelector('.preset');el.hidden=true;el.value='';}
 reset(){
  this.params={...SERIAL_DEFAULTS};this.state=serialSpecimen(this.params);this.lastCandidate=null;this.sync();this.hidePreset();this.view='oblique';this.cameraPose=null;
  this.updateReadouts();if(this.renderer){this.rebuildAssembly();this.setView('oblique');}
  this.announce('Documented defaults restored. Static solution recomputed; oblique physical-scale camera restored.');
 }
 change(input){
  const candidate={...this.params,[input.dataset.param]:Number(input.value)};let next;
  try{if(input.value===''||!input.checkValidity())throw new RangeError('Invalid input');validateSerialParameters(candidate);next=serialSpecimen(candidate);}
  catch{input.setAttribute('aria-invalid','true');this.announce('Invalid input. Last valid parameters, solved geometry and numerical state retained.');return;}
  this.params=candidate;this.state=next;this.lastCandidate=null;this.sync();this.hidePreset();this.updateReadouts();
  if(this.renderer){this.rebuildAssembly();this.draw();}
  this.announce(next.converged?'Current static solution recomputed at the displayed signed target force. Physical camera retained.':'Finite root-cap approximation displayed. The two actual cell resultants differ from the target; shared-force equilibrium is not qualified.');
 }
 updateReadouts(){
  this.root.dataset.converged=String(this.state.converged);
  this.root.querySelector('.serial-solve-status').textContent=this.state.converged?'Both force residuals meet 1e-10 N: qualified scalar roots within the declared bracket.':'Not converged: finite root-cap approximation. Force residuals exceed 1e-10 N; this displayed state is not a qualified shared-force equilibrium.';
  const totals=[['Signed target applied force',this.params.force,'N'],['Total block extension',this.state.extensionM,'m'],['Block volume V0 (spacer excluded)',this.state.referenceVolumeM3,'m³'],['Measured closed-mesh block volume',this.state.currentBoundaryVolumeM3,'m³'],['Total stored block energy',this.state.totalEnergyJ,'J']];
  this.root.querySelector('.serial-totals').innerHTML=totals.map(([label,value,unit])=>'<div><dt>'+label+'</dt><dd>'+fmt(value)+' '+unit+'</dd></div>').join('');
  const fields=[['referenceAreaM2','Reference area A0','m²'],['currentAreaM2','Current area a','m²'],['referenceLengthM','Reference length L0','m'],['currentLengthM','Current length ℓ','m'],['stretch','Axial stretch λ',''],['lateralStretch','Side stretch b',''],['J','Constraint J = λb²',''],['currentBoundaryVolumeM3','Measured closed-mesh V','m³'],['volumeRatio','Measured V/V0',''],['nominalStressPa','Nominal axial P','Pa'],['cauchyStressPa','Axial Cauchy σ = Ncell/a','Pa'],['lateralStressPa','Free-side Cauchy stress','Pa'],['incompressibilityMultiplierPa','Pressure multiplier p','Pa'],['resultantN','Cell resultant A0P','N'],['forceResidualN','Mismatch A0P − target N','N'],['energyJ','Stored cell energy','J']];
  this.root.querySelector('.serial-cells').innerHTML=this.state.cells.map(cell=>'<article class="serial-cell" data-cell="'+cell.index+'"><h4>Block '+(cell.index+1)+'</h4><dl class="readout">'+fields.map(([key,label,unit])=>'<div><dt>'+label+'</dt><dd data-field="'+key+'">'+fmt(cell[key],['resultantN','forceResidualN'].includes(key)?11:7)+(unit?' '+unit:'')+'</dd></div>').join('')+'<div><dt>Bisection cap / used</dt><dd>'+cell.solve.cap+' / '+cell.solve.iterations+'</dd></div><div><dt>Remaining stretch bracket width</dt><dd>'+fmt(cell.solve.bracketWidth)+'</dd></div></dl></article>').join('');
  const panel=this.root.querySelector('.serial-candidate');panel.hidden=!this.lastCandidate;
  if(this.lastCandidate)panel.textContent='Candidate rejected. Total V/V0 = '+fmt(this.lastCandidate.totalVolumeRatio)+'. Local J: '+this.lastCandidate.candidateCells.map(c=>fmt(c.J)).join(', ')+'; free-side stresses: '+this.lastCandidate.candidateCells.map(c=>fmt(c.lateralStressPa)+' Pa').join(', ')+'. The preceding displayed approximation was retained; its force-residual qualification is unchanged.';
 }
 rejectCandidate(){
  this.lastCandidate=globalVolumeOnlyCandidate(this.params,this.state);
  if(this.lastCandidate.accepted){this.announce('Candidate unexpectedly satisfies local tests; original solved specimen remains displayed.');}
  else this.announce(this.lastCandidate.reason);
  this.updateReadouts();
 }
 summary(){
  const rows=Array.from(this.root.querySelectorAll('.serial-totals>div')).map(row=>row.querySelector('dt').textContent+': '+row.querySelector('dd').textContent+'.');
  for(const article of this.root.querySelectorAll('.serial-cell'))rows.push(article.querySelector('h4').textContent+'. '+Array.from(article.querySelectorAll('.readout>div')).map(row=>row.querySelector('dt').textContent+': '+row.querySelector('dd').textContent+'.').join(' '));
  this.announce(rows.join(' '));
 }
 payload(){return {schema:1,model:this.state.model,units:'SI: m, m², m³, N, Pa, J; stretches dimensionless',parameters:{...this.params},state:this.state,display:{...DISPLAY},scene:this.sceneSnapshot(),lastCandidate:this.lastCandidate,policy:'Static equilibrium reduction; parameter edits reevaluate the displayed signed target force. No time history. Local incompressibility is a constitutive assumption, checked separately by mesh volume.'};}
 snapshot(){return this.payload();}
 copy(){const el=this.root.querySelector('.preset');el.hidden=false;el.value=JSON.stringify(this.payload(),null,2);el.focus();el.select();this.announce('Current parameters, scalar roots, measured geometry and scene diagnostics shown as JSON.');}
 export(){const url=URL.createObjectURL(new Blob([JSON.stringify(this.payload(),null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='kenoma-serial-specimen.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);this.announce('Downloaded the current static specimen and geometry diagnostics.');}
 start(){
  this.stopRenderer();this.sceneStatus.begin();
  try{
   this.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));this.renderer.setClearColor('#f4f7fb');this.sceneStatus.watch(this.renderer);
   this.root.querySelector('.scene-host').replaceChildren(this.renderer.domElement);this.renderer.domElement.setAttribute('aria-label','Actual physical-scale three-dimensional serial specimen');this.renderer.domElement.setAttribute('role','img');
   this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#f4f7fb');
   this.scene.add(new THREE.HemisphereLight(0xffffff,0x829098,2));const light=new THREE.DirectionalLight(0xffffff,2.5);light.position.set(.04,.12,.14);this.scene.add(light);
   const grid=new THREE.GridHelper(.2,20,0x869da7,0xd5e0e5);grid.rotation.x=Math.PI/2;grid.position.set(.065,0,-.045);this.scene.add(grid);
   const axes=new THREE.AxesHelper(.02);axes.position.set(-.025,-.045,0);this.scene.add(axes);
   this.camera=new THREE.OrthographicCamera(-.112,.112,.07,-.07,.001,2);this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.enableDamping=false;this.controls.enableZoom=false;this.controls.enablePan=true;
   this.controls.addEventListener('change',()=>{this.captureCameraPose();this.draw();});
   this.rebuildAssembly();this.resize();this.restoreCamera();this.draw();
   if(!this.renderer)return;
   this.sceneStatus.ready(this.renderer);this.root.classList.add('active-scene');
   this.resizeObserver=new ResizeObserver(()=>this.resize());this.resizeObserver.observe(this.root.querySelector('.scene-host'));
   this.announce('Actual 3D active at physical scale. Drag to orbit; right-drag to pan. Front and Oblique restore fixed comparison views.');
  }catch(error){this.sceneStatus.fail(error,'initialization');}
 }
 disposeTree(object){object?.traverse(node=>{node.geometry?.dispose();for(const material of Array.isArray(node.material)?node.material:[node.material])material?.dispose();});}
 stopRenderer(){
  if(this.camera&&this.controls)this.captureCameraPose();
  this.resizeObserver?.disconnect();this.resizeObserver=null;this.sceneStatus?.detach();this.controls?.dispose();this.controls=null;
  this.disposeTree(this.scene);this.scene=null;this.assembly=null;this.currentMeshes=[];this.referenceMeshes=[];this.arrows=[];this.spacerLine=null;
  if(this.renderer){const renderer=this.renderer;this.renderer=null;renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();}
  this.camera=null;this.root.classList.remove('active-scene');
 }
 captureCameraPose(){if(this.camera&&this.controls)this.cameraPose={position:this.camera.position.toArray(),target:this.controls.target.toArray(),up:this.camera.up.toArray()};}
 restoreCamera(){
  if(!this.camera)return;
  const pose=this.cameraPose||{position:this.view==='front'?[.065,0,.3]:[.205,.09,.18],target:TARGET,up:[0,1,0]};
  this.camera.position.fromArray(pose.position);this.camera.up.fromArray(pose.up);this.controls.target.fromArray(pose.target);this.camera.lookAt(this.controls.target);this.controls.update();
 }
 setView(view){this.view=view;this.cameraPose=null;if(this.camera){this.restoreCamera();this.draw();}this.announce((view==='front'?'Front':'Oblique')+' view selected. Fixed physical scale; parameter edits retain this camera.');}
 resize(){
  if(!this.renderer||!this.camera)return;
  const host=this.root.querySelector('.scene-host'),width=Math.max(1,host.clientWidth),height=Math.max(1,host.clientHeight);
  this.renderer.setSize(width,height,false);this.camera.left=-.112;this.camera.right=.112;this.camera.top=.112*height/width;this.camera.bottom=-this.camera.top;this.camera.updateProjectionMatrix();this.draw();
 }
 rebuildAssembly(){
  if(!this.scene)return;
  if(this.assembly){this.scene.remove(this.assembly);this.disposeTree(this.assembly);}
  this.assembly=new THREE.Group();this.currentMeshes=[];this.referenceMeshes=[];this.arrows=[];
  for(const cell of this.state.cells){
   const current=new THREE.Mesh(boxGeometry(displayedVertices(cell)),new THREE.MeshStandardMaterial({color:colour(cell.engineeringStrain),roughness:.8,flatShading:true}));current.userData.cellIndex=cell.index;this.currentMeshes.push(current);this.assembly.add(current);
   const edges=new THREE.LineSegments(new THREE.EdgesGeometry(current.geometry),new THREE.LineBasicMaterial({color:0x315365}));this.assembly.add(edges);
   const reference=new THREE.Mesh(boxGeometry(cell.referenceVertices),new THREE.MeshBasicMaterial({color:0x6c8593,wireframe:true,transparent:true,opacity:.5,depthTest:false}));reference.userData.cellIndex=cell.index;reference.renderOrder=4;this.referenceMeshes.push(reference);this.assembly.add(reference);
   for(const ids of [[0,2,6,4,0],[1,3,7,5,1]])this.assembly.add(new THREE.Line(lineGeometry(ids.map(i=>cell.currentVertices[i])),new THREE.LineBasicMaterial({color:0x233f48})));
  }
  const ends=[this.state.cells[0].currentVertices[1][0],this.state.cells[1].currentVertices[0][0]];
  this.spacerLine=new THREE.Line(lineGeometry(ends.map(x=>[x,0,0])),new THREE.LineBasicMaterial({color:0xa56816}));this.assembly.add(this.spacerLine);
  const sign=Math.sign(this.params.force),length=Math.abs(this.params.force)*DISPLAY.forceArrowScaleMPerN;
  for(const [side,x] of [[-1,0],[1,this.state.totalCurrentLengthM]]){
   const arrow=new THREE.ArrowHelper(new THREE.Vector3((sign||1)*side,0,0),new THREE.Vector3(x,0,0),Math.max(length,1e-8),0xbd4426,Math.min(.005,length*.35),Math.min(.003,length*.25));arrow.visible=sign!==0;
   arrow.line.material.depthTest=false;arrow.cone.material.depthTest=false;arrow.renderOrder=10;this.arrows.push(arrow);this.assembly.add(arrow);
  }
  this.scene.add(this.assembly);
 }
 draw(){
  if(!this.renderer||!this.scene||!this.camera)return false;
  return this.sceneStatus.draw(()=>{this.renderer.render(this.scene,this.camera);this.lastDrawCalls=this.renderer.info.render.calls;if(!this.lastDrawCalls)throw new Error('No actual WebGL draw calls');this.renderCount++;this.totalDrawCalls+=this.lastDrawCalls;});
 }
 sceneSnapshot(){
  return {sceneState:this.root.dataset.sceneState,runDisplay:this.root.dataset.runDisplay,display:{...DISPLAY},drawCalls:this.renderer?this.lastDrawCalls||0:0,renderCount:this.renderCount,totalDrawCalls:this.totalDrawCalls,canvasCount:this.root.querySelectorAll('canvas').length,meshes:(this.currentMeshes||[]).map(geometrySnapshot),referenceMeshes:(this.referenceMeshes||[]).map(geometrySnapshot),spacerEndpoints:this.spacerLine?geometrySnapshot(this.spacerLine).positions:[],arrows:(this.arrows||[]).map(arrow=>({origin:arrow.position.toArray(),direction:new THREE.Vector3(0,1,0).applyQuaternion(arrow.quaternion).toArray(),lengthM:arrow.cone.position.y,visible:arrow.visible})),camera:this.camera?{position:this.camera.position.toArray(),target:this.controls.target.toArray(),left:this.camera.left,right:this.camera.right,top:this.camera.top,bottom:this.camera.bottom,projectionMatrix:this.camera.projectionMatrix.toArray()}:null,context:this.renderer?this.sceneStatus.contextInfo(this.renderer):null};
 }
 pixelSignature(){
  if(!this.renderer)return null;
  const gl=this.renderer.getContext(),width=gl.drawingBufferWidth,height=gl.drawingBufferHeight,pixels=new Uint8Array(width*height*4);gl.readPixels(0,0,width,height,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
  const background=Array.from(pixels.slice(0,4)),colours=new Set();let count=0,hash=2166136261;
  for(let i=0;i<pixels.length;i++){hash=Math.imul(hash^pixels[i],16777619);if(i%4===0){if(pixels.slice(i,i+4).some((v,j)=>v!==background[j]))count++;if(colours.size<512)colours.add(pixels[i]+','+pixels[i+1]+','+pixels[i+2]);}}
  return {width,height,nonBackgroundPixels:count,checksum:(hash>>>0).toString(16).padStart(8,'0'),uniqueColours:colours.size,backgroundRGBA:background};
 }
}
if(typeof document!=='undefined')document.querySelectorAll('[data-serial]').forEach(root=>new SerialLab(root));
