import * as THREE from 'three';
import {geometryMapper} from './geometry.mjs';
// Camera/material recipe is passed by the bounded offline driver, which binds
// it to capture.cameraSHA256. Never import or run the physical operator here.
const data=window.captureData,g=data.geometry,C=data.camera,mapper=geometryMapper(g),canvas=document.querySelector('canvas');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(C.pixelRatio);renderer.setSize(C.width,C.canvasHeight,false);renderer.setClearColor(C.background);
const scene=new THREE.Scene();scene.add(new THREE.AmbientLight(0xffffff,C.ambientIntensity));const light=new THREE.DirectionalLight(0xffffff,C.directionalIntensity);light.position.set(...C.directionalPosition);scene.add(light);
const camera=new THREE.OrthographicCamera(-C.halfHeightM*C.width/C.canvasHeight,C.halfHeightM*C.width/C.canvasHeight,C.halfHeightM,-C.halfHeightM,C.nearM,C.farM);camera.up.set(...C.up);const center=g.frame.origin_m.map((v,d)=>v+C.centerOffsetM[d]);camera.position.set(...center.map((v,d)=>v+C.eyeOffsetM[d]));camera.lookAt(...center);const group=new THREE.Group();scene.add(group);
const colors=[0xd87575,0xffb46e,0xeb7f9b,0x76b6d8,0x758cde,0xaa8bcd,0xa9b678];
function mesh(nodes,indices,color,opacity=1){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(nodes.flat(),3));geometry.setIndex(indices.flat());geometry.computeVertexNormals();return new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color,roughness:.8,side:THREE.DoubleSide,transparent:opacity<1,opacity}));}
window.drawCapture=i=>{
 const row=data.frames[i],raw=Uint8Array.from(atob(row.coordinatesFloat64LE),c=>c.charCodeAt(0)),view=new DataView(raw.buffer),x=Array.from({length:460},(_,i)=>view.getFloat64(i*8,true)),p=mapper(x);
 while(group.children.length){const c=group.children[0];group.remove(c);c.geometry.dispose();c.material.dispose();}
 g.bones.forEach((b,j)=>group.add(mesh(p.bones[j],b.triangles,0xdde5dc)));g.muscles.forEach((b,j)=>group.add(mesh(p.muscles[j],b.surface_triangles,colors[j],C.muscleOpacity)));
 document.querySelector('#title').textContent=data.syntheticOnly?'SYNTHETIC COORDINATE TEST — NO SIMULATION':'PROVISIONAL SOLVER GEOMETRY — NO ACCEPTED MOTION';
 document.querySelector('#caption').textContent=`Job ${row.run} · attempt ${row.attempt} · capture ${row.sequence} · ${row.kind}${row.iteration===undefined?'':` · local Newton iteration ${row.iteration}`} · residual ${row.residualN===undefined?'not evaluated':row.residualN.toExponential(4)+' N'}`;
 document.querySelector('#scope').textContent=C.depiction;renderer.render(scene,camera);window.lastRendered={index:i,coordinatesSHA256:row.coordinatesSHA256,cameraSHA256:row.cameraSHA256,physicalEvaluations:0};
};window.drawCapture(0);window.captureReady=true;
