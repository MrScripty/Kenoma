/** Bundle installed, official dependencies only. Never installs/downloads. */
import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {sha256,json} from './core.mjs';
const [modules,out]=process.argv.slice(2);if(!modules||!out)throw Error('Installed node_modules and exclusive output required');
const require=createRequire(path.join(path.resolve(modules),'package.json')),esbuild=require('esbuild');
const pkg=JSON.parse(fs.readFileSync(path.join(modules,'three/package.json')));if(pkg.version!=='0.180.0'||esbuild.version!=='0.25.10')throw Error('Unpinned installed dependency');
const moduleSHA=sha256(fs.readFileSync(path.join(modules,'three/build/three.module.js'))),coreSHA=sha256(fs.readFileSync(path.join(modules,'three/build/three.core.js')));
if(moduleSHA!=='c8211c69345d2e9949dc7a8ac969380497aa0600a5a8ac6a459c8cd02dd9cb8a'||coreSHA!=='eb077d2417f61d3e6d9264c317cabc4ea35769ed6b0ab533067292a550784c20')throw Error('Changed pinned Three.js source');
const result=await esbuild.build({entryPoints:[new URL('./render-browser.mjs',import.meta.url).pathname],bundle:true,write:false,format:'iife',platform:'browser',nodePaths:[path.resolve(modules)],minify:true,metafile:true});
const expectedInputs=[new URL('./render-browser.mjs',import.meta.url).pathname,new URL('./geometry.mjs',import.meta.url).pathname,path.join(path.resolve(modules),'three/build/three.module.js'),path.join(path.resolve(modules),'three/build/three.core.js')].sort();
if(json(Object.keys(result.metafile.inputs).map(p=>path.resolve(p)).sort())!==json(expectedInputs))throw Error('Unlisted browser import dependency');
if(result.outputFiles.length!==1||result.outputFiles[0].contents.length>1048576)throw Error('Browser bundle bound');fs.writeFileSync(out,result.outputFiles[0].contents,{flag:'wx',mode:0o600});
process.stdout.write(json({threeVersion:pkg.version,esbuildVersion:esbuild.version,threeModuleSHA256:sha256(fs.readFileSync(path.join(modules,'three/build/three.module.js'))),threeCoreSHA256:sha256(fs.readFileSync(path.join(modules,'three/build/three.core.js'))),browserBundleSHA256:sha256(result.outputFiles[0].contents),inputs:Object.keys(result.metafile.inputs).sort(),networkDownloads:0,physicalEvaluations:0}));
