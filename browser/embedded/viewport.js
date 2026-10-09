/** Shared presentation only. Models, proof status and persistence belong to adapters. */
import * as THREE from 'three';
import {OrbitControls} from '../simple-graph/vendor/OrbitControls.js';

export const THEME = Object.freeze({paper:'#fafaf5', ink:'#18363d', muted:'#52676d', accent:'#067d91', rule:'#d8e1df', viewport:'#e9f1ee'});

export function disposeObject(root) {
  const geometries=new Set(), materials=new Set();
  root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of [].concat(o.material||[]))materials.add(m);});
  for(const g of geometries)g.dispose();
  for(const m of materials)m.dispose();
}

export function createViewport(container,{label='Interactive 3D scene',target=[0,.95,0],position=[2.8,2.1,4.8],floor=true}={}) {
  const scene=new THREE.Scene();scene.background=new THREE.Color(THEME.viewport);
  const camera=new THREE.PerspectiveCamera(42,1,.001,100);camera.position.fromArray(position);
  const webgl=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
  webgl.setPixelRatio(Math.min(globalThis.devicePixelRatio||1,2));webgl.outputColorSpace=THREE.SRGBColorSpace;
  const canvas=webgl.domElement;canvas.tabIndex=0;canvas.setAttribute('aria-label',label);container.append(canvas);
  const controls=new OrbitControls(camera,canvas);controls.target.fromArray(target);controls.enableDamping=true;controls.minDistance=.02;controls.maxDistance=30;
  scene.add(new THREE.HemisphereLight(0xffffff,0xa1b5ad,2.4));
  const light=new THREE.DirectionalLight(0xffffff,2.2);light.position.set(3,6,5);scene.add(light);
  let plane=null,grid=null;
  if(floor){plane=new THREE.Mesh(new THREE.PlaneGeometry(30,30),new THREE.MeshStandardMaterial({color:0xe9f1ee,roughness:1}));plane.rotation.x=-Math.PI/2;plane.position.y=-.012;scene.add(plane);grid=new THREE.GridHelper(30,60,0xa9bcb5,0xd4dfd9);grid.position.y=-.008;scene.add(grid);}
  let disposed=false;
  function resize(){if(disposed)return;const {width,height}=container.getBoundingClientRect();camera.aspect=Math.max(width,1)/Math.max(height,1);camera.updateProjectionMatrix();webgl.setSize(Math.max(width,1),Math.max(height,1));}
  function frame(object){const box=new THREE.Box3().setFromObject(object);if(box.isEmpty())return;const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());const distance=Math.max(size.y,size.x/camera.aspect,size.z,.01)/Math.tan(camera.fov*Math.PI/360)*.85;controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(.5,.3,1).normalize().multiplyScalar(distance));controls.minDistance=Math.max(distance*.1,.001);controls.maxDistance=Math.max(distance*10,2);controls.update();}
  function render(){if(!disposed){controls.update();webgl.render(scene,camera);}}
  function dispose(){if(disposed)return;disposed=true;webgl.setAnimationLoop(null);controls.dispose();disposeObject(scene);webgl.dispose();canvas.remove();}
  return {scene,camera,webgl,controls,floor:plane,grid,resize,frame,render,dispose,get disposed(){return disposed;}};
}
