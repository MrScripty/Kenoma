import {createSimpleGraph} from './client.js';
const client = await createSimpleGraph();
const sample = client.request({version:1,operation:{type:'mannequin'}});
if (!sample.ok) throw new Error(sample.error.message);
const angle = document.querySelector('#angle');
const status = document.querySelector('#status');
// Orthographic software rasterization of actual WASM triangle buffers. The
// painter's algorithm is a demo renderer, not a production depth-buffer renderer.
function render(canvas, graph, mesh) {
  const context = canvas.getContext('2d');
  const project = ([x,y,z]) => [260+(x*.94+z*.342)*235,462-y*235+(z*.94-x*.342)*27,z*.94-x*.342];
  const vertices = mesh.positions.map(project);
  context.fillStyle='#172630'; context.fillRect(0,0,520,500);
  context.strokeStyle='#263b47'; context.lineWidth=1;
  for(let i=0;i<11;i++){context.beginPath();context.moveTo(30+i*46,35);context.lineTo(30+i*46,470);context.stroke();}
  const triangles=[];
  for(let i=0;i<mesh.indices.length;i+=3){
    const ids=mesh.indices.slice(i,i+3);
    const points=ids.map(id=>vertices[id]);
    const normal=ids.map(id=>mesh.normals[id]).reduce((a,b)=>a.map((v,j)=>v+b[j]),[0,0,0]);
    const length=Math.hypot(...normal)||1;
    const light=Math.max(0,(normal[0]*.3+normal[1]*.5+normal[2]*.81)/length);
    triangles.push({points,depth:points.reduce((a,p)=>a+p[2],0)/3,light});
  }
  triangles.sort((a,b)=>a.depth-b.depth);
  for(const {points,light} of triangles){
    context.beginPath();context.moveTo(...points[0].slice(0,2));context.lineTo(...points[1].slice(0,2));context.lineTo(...points[2].slice(0,2));context.closePath();
    context.fillStyle=`rgb(${Math.round(44+light*62)} ${Math.round(116+light*100)} ${Math.round(121+light*82)})`;context.fill();
    context.strokeStyle='rgba(12,35,42,.11)';context.lineWidth=.4;context.stroke();
  }
  context.strokeStyle='rgba(234,246,245,.6)';context.lineWidth=1.5;
  for(const edge of graph.edges){const a=project(graph.nodes[edge.a].position),b=project(graph.nodes[edge.b].position);context.beginPath();context.moveTo(a[0],a[1]);context.lineTo(b[0],b[1]);context.stroke();}
  for(const node of graph.nodes){const p=project(node.position);context.beginPath();context.arc(p[0],p[1],2.5,0,Math.PI*2);context.fillStyle='#ecfbf7';context.fill();}
}
render(document.querySelector('#neutral'),sample.graph,sample.mesh);
function update(){
  const degrees=Number(angle.value);
  const result=client.request({version:1,operation:{type:'edit',graph:sample.graph,commands:[{RotateBranch:{pivot:5,child:6,axis:[0,0,1],radians:degrees*Math.PI/180}}]}});
  if(!result.ok){status.textContent=result.error.message;return;}
  render(document.querySelector('#posed'),result.graph,result.mesh);
  document.querySelector('#angleValue').value=`${degrees}°`;
  status.textContent=`${result.graph.nodes.length} source vertices · ${result.graph.edges.length} edges · ${result.mesh.positions.length} mesh vertices · ${result.mesh.indices.length/3} triangles`;
  window.simpleGraphDemo={client,sample,result,rendered:true};
}
angle.addEventListener('input',update);
document.querySelector('#reset').addEventListener('click',()=>{angle.value='0';update();});
update();
