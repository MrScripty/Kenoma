/** Verify and inspect this fixture using Node only; no Rust/WASM execution. */
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {verifySurfaceTopology} from '../../../browser/simple-graph/tests/surface-topology.mjs';
const file=name=>new URL(name,import.meta.url),sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const manifest=JSON.parse(await readFile(file('manifest.json'),'utf8'));
const request=await readFile(file('request.json')),compressed=await readFile(file('response.json.gz'));
const response=gunzipSync(compressed,{maxOutputLength:manifest.response.bytes});
for(const [bytes,info]of [[request,manifest.request],[response,manifest.response]]){assert.equal(bytes.length,info.bytes);assert.equal(sha(bytes),info.sha256);}
assert.equal(compressed.length,manifest.response.compressed_bytes);assert.equal(sha(compressed),manifest.response.compressed_sha256);
assert.deepEqual(JSON.parse(request),{version:1,operation:{type:'rig_bind',rig_version:1}});
const r=JSON.parse(response);assert.equal(r.ok,true);assert.equal(r.version,1);assert.equal(r.rig_version,1);assert.equal(r.rig_id,1);
assert.equal(r.graph.nodes.length,manifest.counts.source_nodes);assert.equal(r.graph.edges.length,manifest.counts.source_edges);
const topology=verifySurfaceTopology(r.mesh);assert.equal(topology.vertices,manifest.counts.positions);assert.equal(topology.triangles,manifest.counts.triangles);
let volume=0;for(let i=0;i<r.mesh.indices.length;i+=3){const [a,b,c]=r.mesh.indices.slice(i,i+3).map(id=>r.mesh.positions[id]);volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}assert.ok(volume>0);
console.log(JSON.stringify({verified:true,...topology,signedVolume:volume,responseSha256:sha(response)},null,2));
