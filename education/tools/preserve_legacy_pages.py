"""Recover exact historical static bytes, and refuse incomplete Pages replacement.

No generators, browser, research program, or network call. A provided directory
may contain a legitimate retained Pages/Actions artifact; every accepted byte
must match the historical manifest. Existing artifacts are never modified.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import re
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
from urllib.parse import quote, urlsplit, unquote

REPO=Path(__file__).resolve().parents[2]
PUBLISHED='596df78f5cb652b4ac70917a82d8aa908b617056'
TREE='8fb39d42575dc5593869315e46e80a64e828d7e3'
MANIFEST='education/review/projection-responsive-successor/qualification/portable-bundle.json'
MANIFEST_SHA='adf5f33c7a6bce984ab4a86dba76bfd3190556bd2e9bec1a73d5016fe16d6296'

def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def sha(data):return hashlib.sha256(data).hexdigest()
def output(path):
    p=Path(path).resolve()
    if p.is_relative_to(REPO):raise ValueError('Generated legacy payload must be outside Git')
    return p

def names():
    if git('rev-parse',PUBLISHED+'^{tree}').decode().strip()!=TREE:raise ValueError('Historical tree changed')
    raw=git('show',PUBLISHED+':'+MANIFEST)
    if sha(raw)!=MANIFEST_SHA:raise ValueError('Historical manifest changed')
    files=json.loads(raw)['file_sha256']
    if len(files)!=1231:raise ValueError('Legacy manifest incomplete')
    for name in files:
        path=PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:raise ValueError('Unsafe historical path')
    return files

def inventory():
    expected=names();by_hash={};seen=set()
    entries=git('ls-tree','-r',PUBLISHED).decode().splitlines()
    # Each unique Git blob is read once; duplicate source locations are harmless.
    for entry in entries:
        metadata,path=entry.split('\t',1);mode,kind,blob=metadata.split()
        if kind!='blob' or mode=='120000' or blob in seen:continue
        seen.add(blob);h=sha(git('cat-file','blob',blob))
        if h in expected.values():by_hash[h]={'commit':PUBLISHED,'path':path,'blob':blob}
    files={name:{'sha256':h,'git':by_hash.get(h),'public_url':'https://mrscripty.github.io/Kenoma/'+quote(name,safe='/')} for name,h in expected.items()}
    missing=[name for name,f in files.items() if not f['git']]
    return {'kind':'EXACT_LEGACY_PAGES_INVENTORY','published_commit':PUBLISHED,'published_tree':TREE,'manifest_sha256':MANIFEST_SHA,'files':files,'missing':missing,'complete':not missing,'public_network_check':'UNRUN_BY_THIS_OFFLINE_TOOL'}

def no_symlinks(root):
    for path in root.rglob('*'):
        if path.is_symlink():raise ValueError('Symlink in static payload: '+str(path.relative_to(root)))


def link_closure(root):
    """Check deployed entry pages and reader, excluding downloadable upstream HTML/templates."""
    class Links(HTMLParser):
        def __init__(self,text):super().__init__();self.urls=[];self.ids=set();self.feed(text)
        def handle_starttag(self,tag,attrs):
            values=dict(attrs)
            if 'id' in values:self.ids.add(values['id'])
            for key in ['href','src']:
                if key in values:self.urls.append(values[key])
    entry=['index.html','anatomical-arm/index.html','anatomy-inspection/index.html',
           'coupled-fixture/index.html','standalone/pressure-projection-lab.html']
    entry += [str(p.relative_to(root)) for p in (root/'reading-edition').rglob('*.html')]
    count=0;styles=set()
    for name in entry:
        page=root/name
        if not page.is_file():raise ValueError('Missing deployed entry page: '+name)
        for href in Links(page.read_text()).urls:
            url=urlsplit(href)
            if url.scheme or url.netloc:continue
            if url.path.startswith('/'):
                if not url.path.startswith('/Kenoma/'):continue
                target=(root/unquote(url.path.removeprefix('/Kenoma/'))).resolve()
            else:target=(page.parent/unquote(url.path)).resolve() if url.path else page
            if target.is_dir():target=target/'index.html'
            if not target.is_relative_to(root) or not target.is_file():raise ValueError('Broken deployed link: '+name+' -> '+href)
            if url.fragment and target.suffix=='.html' and url.fragment not in Links(target.read_text()).ids:raise ValueError('Missing deployed fragment: '+name+' -> '+href)
            if target.suffix=='.css':styles.add(target)
            count+=1
    for style in styles:
        for href in re.findall(r'url\([\s\"\']*([^\)\"\']+)',style.read_text()):
            url=urlsplit(href)
            if url.scheme or url.netloc or href.startswith('#'):continue
            target=(style.parent/unquote(url.path)).resolve()
            if not target.is_relative_to(root) or not target.is_file():raise ValueError('Broken CSS resource: '+href)
            count+=1
    return count


def assemble(destination, reader, supplied=None):
    destination=output(destination)
    if destination.exists():raise FileExistsError(destination)
    m=inventory();supplied=Path(supplied).resolve() if supplied else None
    bound={};missing=[]
    for name,f in m['files'].items():
        if f['git']:
            raw=git('cat-file','blob',f['git']['blob']);origin='PINNED_GIT'
        else:
            p=supplied/name if supplied else None
            if p is None or not p.is_file():missing.append(name);continue
            if p.is_symlink() or not p.resolve().is_relative_to(supplied):raise ValueError('Unsafe preservation input: '+name)
            raw=p.read_bytes();origin='PROVIDED_HASH_VERIFIED_STATIC_ARTIFACT'
        if sha(raw)!=f['sha256']:raise ValueError('Legacy bytes changed: '+name)
        bound[name]=(raw,origin)
    if missing:
        receipt=destination.with_suffix('.missing.json');receipt.write_text(json.dumps({'status':'BLOCKED_INCOMPLETE_LEGACY_ROOT','missing':{n:m['files'][n] for n in missing},'missing_count':len(missing)},indent=2)+'\n')
        raise ValueError(f'Legacy root incomplete: {len(missing)} exact files unavailable; see {receipt}')
    reader=Path(reader).resolve();no_symlinks(reader);rm=json.loads((reader/'reading-manifest.json').read_text())
    actual={str(p.relative_to(reader)) for p in reader.rglob('*') if p.is_file()}-{'reading-manifest.json'}
    if actual!=set(rm['files']):raise ValueError('Reader inventory incomplete')
    for name,h in rm['files'].items():
        p=reader/name
        if p.is_symlink() or not p.resolve().is_relative_to(reader) or sha(p.read_bytes())!=h:raise ValueError('Reader changed')
    if any(n.startswith('reading-edition/') for n in m['files']):raise ValueError('Reader would overwrite legacy path')
    destination.mkdir()
    for name,(raw,_) in bound.items():
        p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    shutil.copytree(reader,destination/'reading-edition')
    for name,f in m['files'].items():
        if sha((destination/name).read_bytes())!=f['sha256']:raise ValueError('Copied legacy payload changed')
    no_symlinks(destination);links=link_closure(destination)
    destination.with_suffix('.preservation.json').write_text(json.dumps({'combined_root_links_checked':links,'status':'PASS_EXACT_LEGACY_PRESERVATION','files':1231,'reader_commit':rm['candidate_commit'],'published_commit':PUBLISHED,'manifest_sha256':MANIFEST_SHA,'proof_compilation':'UNRUN','anatomical_execution':'HELD_UNRUN'},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('inventory');a.add_argument('output')
    a=s.add_parser('assemble');a.add_argument('destination');a.add_argument('reader');a.add_argument('--legacy-directory')
    a=p.parse_args()
    if a.action=='inventory':output(a.output).write_text(json.dumps(inventory(),indent=2)+'\n')
    else:assemble(a.destination,a.reader,a.legacy_directory)
