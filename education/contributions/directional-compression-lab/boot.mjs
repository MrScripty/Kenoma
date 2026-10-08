const status=document.querySelector('#status');
try{
 const manifest=await (await fetch('./runtime-integrity.json')).json();
 const expected=['index.html','style.css','README.md','AreaLoadContracts.lean','proof-receipt.json',...['app','model','view'].map(n=>'education/contributions/directional-compression-lab/'+n+'.mjs'),...['continuum-properties','material-response','tissue','property-labs','tapered-bar'].map(n=>'education/web/'+n+'.mjs')];
 if(manifest.schema!==1||!Array.isArray(manifest.files)||manifest.files.length!==expected.length||new Set(manifest.files.map(f=>f.path)).size!==expected.length)throw Error('Invalid runtime inventory');
 for(const file of manifest.files){
  if(!expected.includes(file.path))throw Error('Unsafe runtime path');
  const response=await fetch(file.path);if(!response.ok)throw Error('Missing runtime file');const bytes=await response.arrayBuffer();
  const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
  if(bytes.byteLength!==file.bytes||digest!==file.sha256)throw Error('Runtime source identity mismatch');
 }
 await import('./education/contributions/directional-compression-lab/app.mjs');
}catch(error){status.textContent='Interactive model refused: '+error.message+'. Static assumptions remain readable.';document.querySelectorAll('input,select,button').forEach(i=>i.disabled=true);}
