import http from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
export const root=fileURLToPath(new URL('../',import.meta.url));
export const output=path.join(root,'test-output');
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function startServer(){
  await mkdir(output,{recursive:true});
  const server=http.createServer(async(req,res)=>{
    try{
      const pathname=new URL(req.url,'http://localhost').pathname;
      if(pathname==='/embed.html'){
        res.setHeader('Content-Type','text/html');
        res.end('<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Static host</title><body style="margin:0"><iframe title="Scene editor" src="/preview/index.html" style="border:0;width:100vw;height:100dvh;display:block"></iframe>');return;
      }
      if(!pathname.startsWith('/preview/')){res.writeHead(404).end();return;}
      const target=path.resolve(root,decodeURIComponent(pathname.slice('/preview/'.length)));
      if(!target.startsWith(root)){res.writeHead(404).end();return;}
      const bytes=await readFile(target);
      res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.wasm':'application/wasm','.css':'text/css','.json':'application/json'})[path.extname(target)]||'application/octet-stream');
      res.end(bytes);
    }catch{res.writeHead(404).end();}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  return {url:`http://127.0.0.1:${server.address().port}`,close:()=>new Promise(resolve=>server.close(resolve))};
}
export async function saveReceipt(browser,data){
  const receipt={...data,browser:await browser.version(),wasmSha256:hash(await readFile(path.join(root,'pkg/human_wasm_bg.wasm'))),sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),sourceDirty:execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim()!=='',capturedAt:new Date().toISOString(),renderer:'Three.js WebGL depth-tested scene; single welded WASM body/head surface per character; scene rotation gizmos'};
  await writeFile(path.join(output,'scene-editor-verification.json'),JSON.stringify(receipt,null,2)+'\n');
  return receipt;
}
export async function verifyBinding(frame){
  return frame.evaluate(async()=>{
    const {createSimpleGraph}=await import('/preview/client.js');
    const client=await createSimpleGraph();
    const sample=client.request({version:1,operation:{type:'mannequin'}});
    const check=(condition,label)=>{if(!condition)throw new Error(label);};
    check(sample.ok&&sample.graph.nodes.length===16&&sample.mesh.positions.length===820&&sample.mesh.indices.length===4608,'canonical counts');
    const repeated=client.request({version:1,operation:{type:'generate',graph:sample.graph}});
    check(JSON.stringify(repeated.mesh)===JSON.stringify(sample.mesh),'repeat deterministic');
    const before=JSON.stringify(sample.graph);
    const bad=client.request({version:1,operation:{type:'edit',graph:sample.graph,commands:[{MoveNode:{node:5,position:[0,1,0]}},{DeleteNode:{node:999}}]}});
    check(!bad.ok&&bad.error.code==='invalid_node'&&!('graph'in bad),'batch failure');
    check(JSON.stringify(sample.graph)===before,'no caller mutation');
    const nonfinite=structuredClone(sample.graph);nonfinite.nodes[0].position[0]=Infinity;
    check(client.request({version:1,operation:{type:'generate',graph:nonfinite}}).error.code==='invalid_request','nonfinite rejection');
    check(client.request({version:2,operation:{type:'mannequin'}}).error.code==='unsupported_version','version error');
    check(client.request({version:1,operation:{type:'generate',graph:sample.graph,options:{ring_sides:4294967296,target_segment_length_factor:1.25,max_edge_segments:64}}}).error.code==='invalid_request','portable u32 counts');
    const cycle={};cycle.self=cycle;check(client.request(cycle).error.code==='invalid_request','cycle rejection');
    return ['WASM initialization and canonical mesh','deterministic generation','atomic failed request','nonfinite/cyclic/version/u32 validation'];
  });
}
