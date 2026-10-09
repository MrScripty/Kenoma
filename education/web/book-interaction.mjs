/** Progressive disclosure and one active embedded laboratory. No model ownership. */
const cards=[...document.querySelectorAll('.proof-card')];
for(const card of cards){const button=card.querySelector('.claim-toggle'),body=card.querySelector('.claim-technical');if(!button||!body)continue;button.hidden=false;body.hidden=true;button.setAttribute('aria-expanded','false');button.addEventListener('click',()=>{const open=button.getAttribute('aria-expanded')!=='true';button.setAttribute('aria-expanded',String(open));body.hidden=!open;button.textContent=open?'Hide checked statement and evidence':'Expand checked statement and evidence';});}
function revealAnchor(){if(!location.hash)return;let node;try{node=document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch{return;}for(let p=node;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;}
window.addEventListener('hashchange',revealAnchor);revealAnchor();
let printing=[];
window.addEventListener('beforeprint',()=>{printing=[...document.querySelectorAll('.proof-appendices')].map(d=>[d,d.open]);for(const [d]of printing)d.open=true;});
window.addEventListener('afterprint',()=>{for(const [d,open]of printing)d.open=open;printing=[];});
let active=null;
function close(){if(!active)return;active.host.replaceChildren();active.button.setAttribute('aria-expanded','false');active.button.textContent='Open 3D example';active=null;}
for(const button of document.querySelectorAll('[data-chapter-example]')){button.hidden=false;button.addEventListener('click',()=>{if(active?.button===button){close();return;}close();const id=button.dataset.chapterExample,host=document.getElementById(button.getAttribute('aria-controls')),frame=document.createElement('iframe');frame.title=button.closest('section').querySelector('h2').textContent;frame.src='examples.html?chapter='+encodeURIComponent(id)+'&embedded=1';frame.className='chapter-example-frame';frame.loading='lazy';host.append(frame);button.setAttribute('aria-expanded','true');button.textContent='Close 3D example';active={button,host,frame};});}
window.addEventListener('pagehide',close);
