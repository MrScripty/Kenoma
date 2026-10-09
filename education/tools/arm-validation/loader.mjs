/** In-memory exact-source loader. No transformed source files or downloads. */
import {registerHooks} from 'node:module';import path from 'node:path';
import {instrument,sha256} from './core.mjs';
export function validateModules(modules){
 for(const [p,m] of Object.entries(modules)){
  if(!p.startsWith('education/')||path.posix.normalize(p)!==p||p.includes('..')||sha256(m.text)!==m.sha256||sha256(instrument(p,m.text))!==m.transformedSHA256)throw Error('Changed source/transform '+p);
 }
}
export function installLoader(modules){
 validateModules(modules);
 return registerHooks({
  resolve(specifier,context,next){
   if(specifier.startsWith('kenoma:')){const p=specifier.slice(7);if(!Object.hasOwn(modules,p))throw Error('Unlisted source '+p);return {url:'kenoma:'+p,shortCircuit:true};}
   if(context.parentURL?.startsWith('kenoma:')){
    if(!specifier.startsWith('./')&&!specifier.startsWith('../'))throw Error('Unlisted physical dependency '+specifier);
    const p=path.posix.normalize(path.posix.join(path.posix.dirname(context.parentURL.slice(7)),specifier));
    if(!Object.hasOwn(modules,p))throw Error('Unlisted source '+p);return {url:'kenoma:'+p,shortCircuit:true};
   }
   return next(specifier,context);
  },
  load(url,context,next){if(!url.startsWith('kenoma:'))return next(url,context);const m=modules[url.slice(7)];if(!m)throw Error('Unlisted module URL');return {format:'module',source:instrument(url.slice(7),m.text),shortCircuit:true};},
 });
}
