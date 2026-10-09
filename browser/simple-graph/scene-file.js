/** Internal versioned scene-source JSON transport. User-facing archives remain
 * SQLite; this module does not replace the native project/container format.
 * No generated meshes, cached buffers, renderer state or undo history are stored.
 */
import {LIMBS,solveTwoBone,vector} from './rig.js';
export const MAX_SCENE_BYTES=1024*1024;
export const MAX_SCENE_CHARACTERS=64;
const clone=value=>structuredClone(value);
const fail=message=>{throw new Error(`Invalid scene source: ${message}`);};
function record(value,keys,label){
  if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==keys.length||keys.some(key=>!Object.hasOwn(value,key)))fail(`${label} has unsupported or missing fields`);
  return value;
}
function scalar(value,label){if(!Number.isFinite(value)||Math.abs(value)>1e6)fail(`${label} must be finite within ±1000000`);return value;}
function identity(value){
  if(typeof value!=='string'||!/^character-[1-9]\d{0,15}$/.test(value))fail('invalid character ID');
  const number=Number(value.slice(10));
  if(!Number.isSafeInteger(number)||number>=Number.MAX_SAFE_INTEGER)fail('character ID exceeds allocation range');
  return number;
}
function counter(value){if(!Number.isSafeInteger(value)||value<1)fail('invalid nextId');return value;}
function envelope(state){
  if(!state||state.version!==1||!Array.isArray(state.characters)||state.characters.length>MAX_SCENE_CHARACTERS)fail('unsupported scene state');
  return {format:'kenoma.scene-source',version:1,rigVersion:1,
    characters:Array.from(state.characters,c=>{
      if(!c?.graph||!Array.isArray(c.graph.nodes)||c.graph.nodes.length!==16||!c.rig)fail('missing character source');
      return {id:c.id,name:c.name,color:c.color,position:c.position,yaw:c.yaw,head:c.head,
        rig:Object.fromEntries(Object.keys(LIMBS).map(limb=>{
          const handle=c.rig[limb];if(!handle)fail('missing limb source');
          return [limb,{target:handle.target,pole:handle.pole}];
        })),pose:Array.from(c.graph.nodes,n=>n?.position)};
    }),selectedId:state.selectedId,nextId:state.nextId};
}
function byteLimit(text){
  if(typeof text!=='string')fail('expected source text');
  if(text.length>MAX_SCENE_BYTES||new TextEncoder().encode(text).byteLength>MAX_SCENE_BYTES)fail('source exceeds 1 MiB');
}
/** Serialize a model snapshot as internal source JSON. Geometry is omitted. */
export function exportScene(state){
  const value=envelope(state);
  // Validate metadata/handles even though a canonical graph is only available
  // at reconstruction. Model exports are already graph-validated snapshots.
  validateEnvelope(value);
  const text=JSON.stringify(value);byteLimit(text);return text;
}
function validateEnvelope(value){
  record(value,['format','version','rigVersion','characters','selectedId','nextId'],'envelope');
  if(value.format!=='kenoma.scene-source'||value.version!==1||value.rigVersion!==1)fail('unsupported format, schema or canonical rig version');
  if(!Array.isArray(value.characters)||value.characters.length>MAX_SCENE_CHARACTERS)fail('at most 64 characters are supported');
  counter(value.nextId);
  const ids=new Set();
  for(const c of Array.from(value.characters)){
    record(c,['id','name','color','position','yaw','head','rig','pose'],'character');
    const serial=identity(c.id);
    if(ids.has(c.id))fail('duplicate character ID');ids.add(c.id);
    if(serial>=value.nextId)fail('nextId must exceed every character ID');
    if(typeof c.name!=='string'||!c.name.trim()||c.name.length>128)fail('name must contain 1–128 characters');
    if(typeof c.color!=='string'||!/^#[0-9a-f]{6}$/i.test(c.color))fail('color must be #rrggbb');
    vector(c.position,'character position');scalar(c.yaw,'character yaw');
    record(c.head,['yaw','pitch'],'head');scalar(c.head.yaw,'head yaw');scalar(c.head.pitch,'head pitch');
    record(c.rig,Object.keys(LIMBS),'rig');
    for(const limb of Object.keys(LIMBS)){
      record(c.rig[limb],['target','pole'],'limb');vector(c.rig[limb].target,'IK target');vector(c.rig[limb].pole,'IK pole');
    }
    if(!Array.isArray(c.pose)||c.pose.length!==16)fail('pose must contain 16 source points');
    Array.from(c.pose).forEach(p=>vector(p,'pose point'));
  }
  if(value.selectedId!==null&&!ids.has(value.selectedId))fail('selectedId must identify a character');
  if(value.characters.length===0&&value.selectedId!==null)fail('empty scene cannot select a character');
  return value;
}
function reconstruct(value,baseGraph){
  validateEnvelope(value);
  if(!baseGraph||!Array.isArray(baseGraph.nodes)||baseGraph.nodes.length!==16||!Array.isArray(baseGraph.edges))fail('canonical base graph is required');
  const characters=value.characters.map(source=>{
    const expected=clone(baseGraph),graph=clone(baseGraph),rig={};
    for(const [limb,[r,j,e]] of Object.entries(LIMBS)){
      const handle=source.rig[limb];
      const result=solveTwoBone({root:baseGraph.nodes[r].position,joint:baseGraph.nodes[j].position,end:baseGraph.nodes[e].position,target:handle.target,pole:handle.pole});
      expected.nodes[j].position=result.joint;expected.nodes[e].position=result.end;
      rig[limb]={target:[...handle.target],pole:[...handle.pole],status:result.status};
    }
    for(let i=0;i<16;i++){
      const point=source.pose[i],solved=expected.nodes[i].position;
      // Preserve the exact authored source floats (including the initial rest
      // pose) after verifying consistency. Re-solving untouched rest limbs can
      // differ by a few ulps; repeated import must not accumulate that drift.
      if(point.some((v,axis)=>Math.abs(v-solved[axis])>1e-8))fail('source pose disagrees with canonical IK handles');
      graph.nodes[i].position=[...point];
    }
    return {id:source.id,name:source.name,color:source.color,position:[...source.position],yaw:source.yaw,head:{...source.head},graph,rig};
  });
  return {version:1,characters,selectedId:value.selectedId,nextId:value.nextId};
}
/** Parse bounded source text and reconstruct validated canonical source graphs. */
export function parseScene(text,baseGraph){
  byteLimit(text);
  let value;try{value=JSON.parse(text);}catch{fail('malformed JSON');}
  return reconstruct(value,baseGraph);
}
/** Revalidate imported state before the model's atomic replacement. Never trust
 * a mutable parsed snapshot merely because parseScene was called earlier. */
export function validateScene(state,baseGraph){
  // Round through the bounded transport contract; validates without mutation.
  return parseScene(exportScene(state),baseGraph);
}
