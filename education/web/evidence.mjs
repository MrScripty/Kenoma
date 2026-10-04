// Read-only evidence views. No anatomical rig or inference from recorded signals.
import * as THREE from 'three';
import {SceneStatus} from './scene-status.mjs';
export class EvidenceView {
 constructor(root,activate){
  this.root=root;this.activate=activate;this.host=root.querySelector('.scene-host');this.status=root.querySelector('.announce');this.view='anterior';
  this.part=root.querySelector('[data-evidence=part]');this.time=root.querySelector('[data-evidence=bin]');
  root.querySelector('[data-action=start]').addEventListener('click',()=>this.start());
  this.part.addEventListener('input',()=>this.draw());
  root.querySelector('[data-action=view]').addEventListener('click',()=>{this.view=this.view==='anterior'?'oblique':this.view==='oblique'?'posterior':'anterior';this.draw();this.status.textContent=`Atlas ${this.view} view; source geometry unchanged.`;});
  this.time.addEventListener('input',()=>this.read());
  root.querySelector('[data-action=reset]').addEventListener('click',()=>{this.part.value='all';this.time.value='0';this.view='anterior';this.draw();this.read();this.status.textContent='Atlas display and recorded bin reset; no mechanical model is driven.';});
  this.sceneStatus=new SceneStatus(root,()=>this.stopRenderer());
  this.load().catch(()=>{this.status.textContent='Evidence data could not load. Static figures and downloadable files remain available.';});
 }
 async load(){
  const responses=await Promise.all(['bodyparts3d_right_arm_m.json','openarm_s2_1b_0p5s_bins.json'].map(name=>fetch(`data/elbow-v1/data/${name}`)));
  if(responses.some(r=>!r.ok))throw new Error('evidence response');
  [this.atlas,this.recording]=await Promise.all(responses.map(r=>r.json()));
  this.time.disabled=false;this.read();
 }
 read(){
  if(!this.recording)return;const r=this.recording.rows[Number(this.time.value)];
  const values=[['Recorded bin (not uniform raw samples)',`${Number(this.time.value)+1} / ${this.recording.rows.length}`],['Actual mean time',`${r.mean_elapsed_s.toFixed(6)} s`],['Bin interval',`[${r.bin_start_s.toFixed(3)}, ${r.bin_end_s.toFixed(3)}) s`],['Retained sample count',String(r.sample_count)],['Brachioradialis thickness',`${r.brachioradialis_thickness_normalized_1_mean.toFixed(6)} (unit 1)`],['Biceps sEMG',`${r.biceps_semg_normalized_1_mean.toFixed(6)} (unit 1)`],['Wrist-contact force',`${r.wrist_contact_force_normalized_1_mean.toFixed(6)} (unit 1)`]];
  this.root.querySelector('.readout').replaceChildren(...values.map(([label,value])=>{const el=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;el.append(dt,dd);return el;}));
 }
 pause(){} // Evidence views do not animate or advance a simulation.
 async start(){
  if(!this.atlas){this.status.textContent='Loading local atlas evidence; try Start again when data is ready.';return;}
  this.activate(this);this.sceneStatus.begin();
  if(!this.renderer){
   try{
    this.renderer=new THREE.WebGLRenderer({antialias:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));this.renderer.setClearColor(0x101d2c);
    this.renderer.domElement.setAttribute('role','img');this.renderer.domElement.setAttribute('aria-label','Static BodyParts3D atlas surfaces. Source z is superior; no pose or tissue mechanics is applied. Part labels and static alternative follow.');
    this.host.replaceChildren(this.renderer.domElement);this.scene=new THREE.Scene();this.camera=new THREE.PerspectiveCamera(35,1,.001,100);
    this.sceneStatus.watch(this.renderer);
    this.observer=new ResizeObserver(()=>this.draw());this.observer.observe(this.host);
   }catch(error){this.sceneStatus.fail(error,'initialization');this.status.textContent='3D rendering unavailable. Static atlas figure and source data remain available.';return;}
  }
  if(!this.draw())return;
  try{this.sceneStatus.ready(this.renderer);}catch(error){this.sceneStatus.fail(error,'first-frame');return;}
  this.status.textContent='Actual static atlas loaded. Display centering and viewing rotation only; no rig, skin/contact or subject calibration.';
 }
 stopRenderer(){
  if(!this.renderer&&this.root.dataset.sceneState==='error')return;
  this.sceneStatus.idle();this.observer?.disconnect();this.scene?.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});this.renderer?.dispose();this.renderer?.forceContextLoss();this.renderer=null;this.host.replaceChildren();
 }
 draw(){if(!this.renderer||!this.atlas)return false;return this.sceneStatus.draw(()=>this.renderScene());}
 renderScene(){
  if(!this.renderer||!this.atlas)return;
  this.scene.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});this.scene.clear();
  this.scene.add(new THREE.AmbientLight(0xffffff,2));const lamp=new THREE.DirectionalLight(0xffffff,3);lamp.position.set(1,2,3);this.scene.add(lamp);
  const group=new THREE.Group(),bounds=new THREE.Box3();
  this.atlas.parts.forEach((p,i)=>{
   const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(p.vertices_m.flat(),3));geometry.setIndex(p.triangles_zero_based.flat());geometry.computeVertexNormals();geometry.computeBoundingBox();bounds.union(geometry.boundingBox);
   const bone=i<3,visible=this.part.value==='all'||(this.part.value==='bones'&&bone)||this.part.value===p.element_id;
   const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:bone?0xe8cf9b:new THREE.Color().setHSL((i-3)/7,.65,.58),roughness:.7,side:THREE.DoubleSide}));mesh.visible=visible;group.add(mesh);
  });
  // Shared rigid display mapping only: atlas (x,y,z)->display(-x,z,y).
  const center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3()),distance=size.length()*1.9;
  group.position.copy(center.clone().negate());const parent=new THREE.Group();parent.add(group);parent.rotation.set(-Math.PI/2,0,Math.PI);this.scene.add(parent);
  const width=Math.max(200,this.host.clientWidth);this.renderer.setSize(width,360,false);this.camera.aspect=width/360;
  this.camera.position.set(...(this.view==='anterior'?[0,0,-distance]:this.view==='posterior'?[0,0,distance]:[distance*.65,distance*.2,-distance]));this.camera.lookAt(0,0,0);this.camera.updateProjectionMatrix();this.renderer.render(this.scene,this.camera);
 }
}
