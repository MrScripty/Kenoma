import {lessonState} from './chapter-models.mjs';
self.onmessage=({data})=>{try{self.postMessage({id:data.id,ok:true,state:lessonState(data.kind,data.parameters,data.asset)});}catch(error){self.postMessage({id:data.id,ok:false,error:error.message});}};
