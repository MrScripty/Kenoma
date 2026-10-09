import assert from 'node:assert/strict';
import http from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const {chromium}=await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root=fileURLToPath(new URL('../',import.meta.url));
const output=path.join(root,'test-output');await mkdir(output,{recursive:true});
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const server=http.createServer(async(req,res)=>{
  try {
    const pathname=new URL(req.url,'http://localhost').pathname;
    if(pathname==='/embed.html'){
      res.setHeader('Content-Type','text/html');res.end('<!doctype html><title>Static host</title><iframe title="Isolated graph demo" src="/preview/index.html" style="border:0;width:1200px;height:1000px"></iframe>');return;
    }
    if(!pathname.startsWith('/preview/')){res.writeHead(404).end();return;}
    const target=path.resolve(root,decodeURIComponent(pathname.slice('/preview/'.length)));
    if(!target.startsWith(root)){res.writeHead(404).end();return;}
    const bytes=await readFile(target);
    const type={'.html':'text/html','.js':'text/javascript','.wasm':'application/wasm'}[path.extname(target)]||'application/octet-stream';
    res.setHeader('Content-Type',type);res.end(bytes);
  }catch{res.writeHead(404).end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try {
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM || '/usr/bin/chromium'});
  const page=await browser.newPage({viewport:{width:1220,height:1040},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  const requests=[];page.on('request',request=>requests.push(request.url()));
  await page.goto(`http://127.0.0.1:${server.address().port}/embed.html`);
  const frame=page.frames().find(frame=>frame.url().endsWith('/preview/index.html'));
  assert.ok(frame,'Demo loaded embedded under a static-host subpath');
  await frame.waitForFunction(()=>window.simpleGraphDemo?.rendered===true);
  const evidence=await frame.evaluate(async()=>{
    const {client,sample,result}=window.simpleGraphDemo;
    const check=(condition,label)=>{if(!condition)throw new Error(label);};
    check(sample.ok&&result.ok,'success envelopes');
    check(sample.graph.nodes.length===16&&sample.mesh.positions.length===820&&sample.mesh.indices.length===4608,'canonical counts');
    const serialized=JSON.stringify(sample.graph);
    const repeated=client.request({version:1,operation:{type:'generate',graph:sample.graph}});
    check(JSON.stringify(repeated.mesh)===JSON.stringify(sample.mesh),'repeat deterministic');
    check(JSON.stringify(result.graph.nodes[6])!==JSON.stringify(sample.graph.nodes[6]),'hand moves');
    for(let i=0;i<16;i++)if(i!==6)check(JSON.stringify(result.graph.nodes[i])===JSON.stringify(sample.graph.nodes[i]),'pose isolation');
    const length=(graph,edge)=>Math.hypot(...graph.nodes[edge.a].position.map((x,j)=>x-graph.nodes[edge.b].position[j]));
    for(const edge of sample.graph.edges)check(Math.abs(length(sample.graph,edge)-length(result.graph,edge))<1e-6,'length preserved');
    for(const mesh of [sample.mesh,result.mesh]){
      check(mesh.indices.every(i=>Number.isInteger(i)&&i>=0&&i<mesh.positions.length),'valid indices');
      check(mesh.positions.flat().every(Number.isFinite),'finite positions');
      check(mesh.normals.every(n=>Math.abs(Math.hypot(...n)-1)<1e-5),'unit normals');
    }
    const bad=client.request({version:1,operation:{type:'edit',graph:sample.graph,commands:[{MoveNode:{node:5,position:[0,1,0]}},{DeleteNode:{node:999}}]}});
    check(!bad.ok&&bad.error.code==='invalid_node'&&!('graph'in bad),'batch failure');
    check(JSON.stringify(sample.graph)===serialized,'no caller mutation');
    const nonfinite=structuredClone(sample.graph);nonfinite.nodes[0].position[0]=Infinity;
    check(client.request({version:1,operation:{type:'generate',graph:nonfinite}}).error.code==='invalid_request','nonfinite rejected before JSON coercion');
    check(client.request({version:2,operation:{type:'mannequin'}}).error.code==='unsupported_version','version error');
    check(client.request({version:1,operation:{type:'generate',graph:sample.graph,options:{ring_sides:4294967296,target_segment_length_factor:1.25,max_edge_segments:64}}}).error.code==='invalid_request','portable u32 count error');
    const cycles={};cycles.self=cycles;check(client.request(cycles).error.code==='invalid_request','cycle error');
    const pixels=document.querySelector('#posed').getContext('2d').getImageData(0,0,520,500).data;
    let distinct=0;for(let i=0;i<pixels.length;i+=4)if(pixels[i+1]>130&&pixels[i+2]>100)distinct++;
    check(distinct>5000,'actual visible mesh pixels');
    return {vertices:sample.mesh.positions.length,triangles:sample.mesh.indices.length/3,poseDegrees:70,visibleMeshPixels:distinct,sourceGraph:sample.graph,posedGraph:result.graph,meshSerialized:JSON.stringify(result.mesh),checks:['WASM initialization','static subpath iframe embedding','canonical mesh counts','deterministic regeneration','branch isolation','edge lengths','finite buffers and unit normals','failed batch rollback','caller immutability','nonfinite and cyclic input rejection','version errors','portable u32 counts','visible mesh pixels']};
  });
  await frame.locator('#angle').fill('100');await frame.locator('#angle').dispatchEvent('input');
  assert.equal(await frame.locator('#angleValue').textContent(),'100°');
  await frame.locator('#reset').click();
  const resetEqual=await frame.evaluate(()=>JSON.stringify(window.simpleGraphDemo.result.graph)===JSON.stringify(window.simpleGraphDemo.sample.graph));assert.ok(resetEqual,'reset restores source pose');
  await frame.locator('#angle').fill('70');await frame.locator('#angle').dispatchEvent('input');
  await frame.locator('main').screenshot({path:path.join(output,'kenoma-wasm-mannequin.png')});
  assert.deepEqual(errors,[]);
  assert.ok(requests.some(url=>url.endsWith('human_wasm_bg.wasm')),'compiled wasm actually fetched');
  assert.ok(requests.every(url=>url.startsWith('http://127.0.0.1:')),'no external runtime requests');
  const meshHash=hash(evidence.meshSerialized);delete evidence.meshSerialized;
  const receipt={...evidence,checks:[...evidence.checks,'slider interaction','reset','no browser exceptions','no external requests'],browser:await browser.version(),wasmSha256:hash(await readFile(path.join(root,'pkg/human_wasm_bg.wasm'))),meshSha256:meshHash,sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),sourceDirty:execFileSync('git',['status','--porcelain'],{cwd:root,encoding:'utf8'}).trim()!=='',capturedAt:new Date().toISOString(),renderer:'Canvas 2D triangle projection of actual Rust/WASM-generated buffers; graph overlay; painter sorting'};
  await writeFile(path.join(output,'browser-verification.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({checks:receipt.checks.length,vertices:receipt.vertices,triangles:receipt.triangles,browser:receipt.browser,wasmSha256:receipt.wasmSha256,output}));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
