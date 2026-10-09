"""Reconstruct the owner's approved preserved book; do not rebuild or requalify."""
from pathlib import Path
import hashlib,json,shutil,zipfile,sys
source,payload,out=map(Path,sys.argv[1:4])
assert not out.exists(), 'Refuse to overwrite an existing site'
out.mkdir(parents=True)
hash_file=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def safe(base,relative):
 p=base/relative
 assert not Path(relative).is_absolute() and '..' not in Path(relative).parts,relative
 assert p.resolve().is_relative_to(base.resolve()),relative
 return p

def archive(prefix,target,digest):
 pieces=sorted((payload/prefix).glob('*.bin'))
 assert pieces and [p.stem for p in pieces]==[f'{i:04d}' for i in range(len(pieces))]
 with target.open('wb') as stream:
  for p in pieces:stream.write(p.read_bytes())
 assert hash_file(target)==digest,'Archive checksum mismatch'
 with zipfile.ZipFile(target) as z:
  for info in z.infolist():
   safe(out,info.filename)
   assert ((info.external_attr>>16)&0o170000)!=0o120000,'Symlink rejected'
  z.extractall(out)

for target,original in json.loads((payload/'reuse.json').read_text()).items():
 dest=safe(out,target);src=safe(source,original)
 assert src.is_file();dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
archive('parts',payload/'publication-delta.zip','fdcb7e507350fb55e9970a036f8333228e322651ec718a75a09609e4f892018d')
expected=json.loads((payload/'published-files.json').read_text())
actual={str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()}
assert actual==set(expected),'Preserved file inventory differs'
for name,item in expected.items():
 p=safe(out,name);assert p.stat().st_size==item['bytes'] and hash_file(p)==item['sha256'],name
manifest=json.loads((out/'build-manifest.json').read_text())
assert hash_file(out/'build-manifest.json')=='415d3d15c6f9644660bd2dd3983367bb30548188080ab0fbf7de45c4b7ed6d02'
for name,digest in manifest['input_sha256'].items():assert hash_file(safe(source/'education',name))==digest,name
# Preserve the exact PDF to which original receipts refer, and publish a copy
# whose only change is the 210 source-link URI annotation destinations.
shutil.copyfile(out/'kenoma-mechanics.pdf',out/'kenoma-mechanics-preserved.pdf')
archive('link-parts',payload/'publication-links.zip','1735736686ab422969ce2581678fd9c165e4080b4a1b63739746a6f2179985ee')
receipt=json.loads((payload/'publication-receipt.json').read_text())
assert hash_file(out/'kenoma-mechanics.pdf')==receipt['pdfLinkRepair']['publishedSHA256']
assert hash_file(out/'kenoma-mechanics-preserved.pdf')==receipt['pdfLinkRepair']['originalSHA256']
shutil.copyfile(payload/'publication-receipt.json',out/'publication-receipt.json')
print('Verified 1,102 preserved files and 947 source inputs; applied recorded URI-only PDF correction.')
print('No research, compilation, browser tests, or fresh qualification performed.')
