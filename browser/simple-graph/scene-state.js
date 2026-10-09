import {LIMBS,solveTwoBone,vector} from './rig.js';
const clone = value => structuredClone(value);
function freeze(value) { if(value && typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value);} return value; }
const same = (a,b) => JSON.stringify(a)===JSON.stringify(b);
function angle(value,name) { if(!Number.isFinite(value)||Math.abs(value)>1e6) throw new Error(`${name} must be a finite angle within ±1000000`); return value; }
/** Renderer-independent, versioned scene state. All public snapshots are frozen.
 * A gesture is atomic in history; invalid actions leave it and state untouched.
 * History is bounded to 100 entries. Selection does not create undo entries.
 */
export class SceneModel {
  #base; #state; #past=[]; #future=[]; #gesture=null; #serial=1;
  constructor(baseGraph) {
    this.#base=clone(baseGraph);
    if(!Array.isArray(this.#base?.nodes)||this.#base.nodes.length!==16||!Array.isArray(this.#base.edges)) throw new Error('SceneModel requires the 16-node mannequin graph');
    Array.from(this.#base.nodes).forEach(n=>{
      vector(n?.position,'node position');
      if(!Array.isArray(n.radii)||n.radii.length!==2||!Array.from(n.radii).every(v=>Number.isFinite(v)&&v>0&&v<=1e6)||typeof n.root!=='boolean')throw new Error('Invalid mannequin node radii or root');
    });
    const links=new Set();
    for(const edge of this.#base.edges){
      if(!edge||![edge.a,edge.b].every(v=>Number.isInteger(v)&&v>=0&&v<16)||edge.a===edge.b)throw new Error('Invalid mannequin edge');
      const key=[edge.a,edge.b].sort((a,b)=>a-b).join(':');
      if(links.has(key))throw new Error('Duplicate mannequin edge');links.add(key);
    }
    const required=[[0,1],[1,2],[2,3],[1,4],[4,5],[5,6],[1,7],[7,8],[8,9],[0,10],[10,11],[11,12],[0,13],[13,14],[14,15]];
    if(links.size!==15||required.some(pair=>!links.has(pair.join(':')))||!this.#base.nodes[0].root||this.#base.nodes.slice(1).some(n=>n.root))throw new Error('SceneModel requires mannequin topology and pelvis root');
    for(const [r,j,e] of Object.values(LIMBS))solveTwoBone({root:this.#base.nodes[r].position,joint:this.#base.nodes[j].position,end:this.#base.nodes[e].position,target:this.#base.nodes[e].position,pole:this.#base.nodes[j].position});
    this.#state={version:1,characters:[],selectedId:null,nextId:1};
    this.dispatch({type:'add'}); this.#past=[];
  }
  get state(){return freeze(clone(this.#state));}
  get canUndo(){return this.#past.length>0;}
  get canRedo(){return this.#future.length>0;}
  #record(before){this.#past.push(before);if(this.#past.length>100)this.#past.shift();this.#future=[];}
  beginGesture(){if(this.#gesture)throw new Error('A gesture is already active');this.#gesture=clone(this.#state);return this.state;}
  commitGesture(){if(this.#gesture&&!same(this.#gesture.characters,this.#state.characters))this.#record(this.#gesture);this.#gesture=null;return this.state;}
  cancelGesture(){if(this.#gesture)this.#state=this.#gesture;this.#gesture=null;this.#state.nextId=this.#serial;return this.state;}
  undo(){if(this.#gesture)this.cancelGesture();if(this.#past.length){this.#future.push(this.#state);this.#state=this.#past.pop();this.#state.nextId=this.#serial;}return this.state;}
  redo(){if(this.#gesture)this.cancelGesture();if(this.#future.length){this.#past.push(this.#state);this.#state=this.#future.pop();this.#state.nextId=this.#serial;}return this.state;}
  dispatch(action){
    if(!action||typeof action.type!=='string')throw new Error('Action type is required');
    const next=clone(this.#state);
    const character=next.characters.find(c=>c.id===action.id);
    if(action.type!=='add'&&!character)throw new Error(`Unknown character: ${action.id}`);
    switch(action.type){
      case 'add': {
        const id=`character-${this.#serial}`;
        const graph=clone(this.#base),rig={};
        for(const [name,[r,j,e]] of Object.entries(LIMBS)){
          const root=graph.nodes[r].position,joint=graph.nodes[j].position,end=graph.nodes[e].position;
          const endpointAxis=end.map((v,i)=>v-root[i]);
          const axis=Math.hypot(...endpointAxis)>1e-10?endpointAxis:joint.map((v,i)=>v-root[i]);
          const length=Math.hypot(...axis),unit=axis.map(v=>v/length);
          const along=joint.reduce((sum,v,i)=>sum+(v-root[i])*unit[i],0);
          let bend=joint.map((v,i)=>v-root[i]-along*unit[i]);
          const magnitude=Math.hypot(...bend);
          bend=magnitude>1e-8?bend.map(v=>v/magnitude):[0,0,1];
          rig[name]={target:[...end],pole:joint.map((v,i)=>v+bend[i]*.4),status:'reachable'};
          solveTwoBone({root,joint,end,target:end,pole:rig[name].pole});
        }
        let spawnX=0;
        while(next.characters.some(c=>Math.hypot(c.position[0]-spawnX,c.position[2])<1.3))spawnX+=1.4;
        next.characters.push({id,name:`Character ${this.#serial}`,color:'#61b9b2',position:[spawnX,0,0],yaw:0,head:{yaw:0,pitch:0},graph,rig});
        next.selectedId=id;next.nextId=this.#serial+1;break;
      }
      case 'select':next.selectedId=character.id;break;
      case 'remove':next.characters=next.characters.filter(c=>c.id!==character.id);if(next.selectedId===character.id)next.selectedId=next.characters[0]?.id??null;break;
      case 'color':if(typeof action.color!=='string'||!/^#[0-9a-f]{6}$/i.test(action.color))throw new Error('Color must be #rrggbb');character.color=action.color.toLowerCase();break;
      case 'placement':if(action.position!==undefined)character.position=vector(action.position,'position');if(action.yaw!==undefined)character.yaw=angle(action.yaw,'yaw');break;
      case 'head':for(const key of ['yaw','pitch'])if(action[key]!==undefined)character.head[key]=angle(action[key],key);break;
      case 'ik': {
        if(!Object.hasOwn(LIMBS,action.limb))throw new Error('Unknown limb');
        const [r,j,e]=LIMBS[action.limb],handle=character.rig[action.limb];
        if(action.target!==undefined)handle.target=vector(action.target,'target');
        if(action.pole!==undefined)handle.pole=vector(action.pole,'pole');
        // Solve against immutable rest lengths/plane, never accumulated float drift.
        const result=solveTwoBone({root:this.#base.nodes[r].position,joint:this.#base.nodes[j].position,end:this.#base.nodes[e].position,target:handle.target,pole:handle.pole});
        character.graph.nodes[j].position=result.joint;character.graph.nodes[e].position=result.end;handle.status=result.status;break;
      }
      default:throw new Error(`Unknown action: ${action.type}`);
    }
    if(same(next,this.#state))return this.state;
    if(!this.#gesture&&action.type!=='select')this.#record(clone(this.#state));
    this.#state=next;if(action.type==='add')this.#serial=next.nextId;
    return this.state;
  }
}
