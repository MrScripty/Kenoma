import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';

test('actual arm redraw disposes every owned dumbbell descendant once',()=>{
 const source=fs.readFileSync(process.env.KENOMA_DRAW_SOURCE||new URL('../tools/anatomical-arm-inspector.mjs',import.meta.url),'utf8'),start=source.indexOf('function draw('),end=source.indexOf("document.querySelector('#start').onclick",start),liveGeometry=new Set(),liveMaterial=new Set();
 class Geometry{constructor(){liveGeometry.add(this);}setFromPoints(){return this;}dispose(){assert.ok(liveGeometry.delete(this),'geometry disposed twice');}}
 class Material{constructor(){liveMaterial.add(this);}clone(){return new Material();}dispose(){assert.ok(liveMaterial.delete(this),'material disposed twice');}}
 class Group{constructor(){this.children=[];this.position={set(){}};this.quaternion={setFromUnitVectors(){}};}add(x){this.children.push(x);}remove(x){this.children.splice(this.children.indexOf(x),1);}traverse(fn){fn(this);for(const c of this.children)c.traverse(fn);}}
 class Mesh extends Group{constructor(geometry,material){super();this.geometry=geometry;this.material=material;this.position={set(){}};}}
 class Vector3{}
 const context={THREE:{Group,Mesh,Vector3,CylinderGeometry:Geometry,BufferGeometry:Geometry,MeshStandardMaterial:Material,LineBasicMaterial:Material,LineSegments:Mesh},groups:[new Group(),new Group()],g:{bones:[],muscles:[],frame:{hand_grip_m:[0,0,0],axis_unit:[0,1,0]}},model:{shared:[]},state:{qRad:0},configuration:{branches:[]},attachmentMap:()=>({position:[0,0,0]}),comparison:()=>[],host:{clientWidth:1000,clientHeight:500},camera:{updateProjectionMatrix(){}},renderer:{setSize(){},render(){}},scene:{},mesh(){throw Error('Unexpected tissue mesh in glyph-only regression');}};
 vm.createContext(context);vm.runInContext(source.slice(start,end)+';globalThis.redraw=draw;',context);
 context.redraw();const initial=[liveGeometry.size,liveMaterial.size];
 for(let i=1;i<100;i++)context.redraw();
 assert.equal(liveGeometry.size,initial[0],`live geometries grew from ${initial[0]} to ${liveGeometry.size}`);
 assert.equal(liveMaterial.size,initial[1],`live materials grew from ${initial[1]} to ${liveMaterial.size}`);
 assert.equal(liveGeometry.size,7);
 assert.equal(liveMaterial.size,3,'one owned shared material per dumbbell plus tendon line');
});
