import {createSimpleGraph} from './client.js';
// BoundRig data stays inside this worker's WASM instance. Only small pose graphs
// cross into it, and only generated mesh responses cross back to the renderer.
const clientPromise=createSimpleGraph();
const rigs=new Map();
let binding=null;
const identity=message=>`${message.id}:${message.generation}`;
self.addEventListener('message',async({data:message})=>{
 const started=performance.now();
 try{
  const client=await clientPromise;const key=identity(message);let response;
  if(message.type==='bind'){
   response=binding||client.request({version:1,operation:{type:'rig_bind',rig_version:1}});
   if(response.ok){binding=response;if(JSON.stringify(message.graph)!==JSON.stringify(response.graph))throw Error('Renderer base graph differs from canonical rig rest graph');rigs.set(key,response.rig_id);}
  }else if(message.type==='pose'){
   const rigId=rigs.get(key);if(rigId===undefined)throw Error('Rig binding is unavailable');
   response=client.request({version:1,operation:{type:'rig_deform',rig_version:1,rig_id:rigId,graph:message.graph,head:message.head}});
  }else if(message.type==='release'){
   const rigId=rigs.get(key);rigs.delete(key);response={ok:true};if(rigId!==undefined&&rigs.size===0){response=client.request({version:1,operation:{type:'rig_release',rig_version:1,rig_id:rigId}});binding=null;}
  }else throw Error('Unknown rig worker request');
  self.postMessage({jobId:message.jobId,ok:response.ok,mesh:response.mesh,error:response.error,timing:{workerMilliseconds:performance.now()-started}});
 }catch(error){self.postMessage({jobId:message.jobId,ok:false,error:{message:error.message||String(error)}});}
});
