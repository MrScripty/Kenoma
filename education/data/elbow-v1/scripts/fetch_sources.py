#!/usr/bin/env python3
"""Small, bounded public-source downloads; never fetch a complete atlas."""
import datetime, hashlib, io, json, pathlib, struct, urllib.request, zipfile, zlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
URL = BASE + 'isa_BP3D_4.0_obj_99.zip'
MAX_TOTAL = 30 * 1024**2
transferred = 0
log = []
def fetch(url, limit, byte_range=None):
    global transferred
    if not 0 < limit <= MAX_TOTAL-transferred:
        raise RuntimeError('Download budget exceeded before request')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    if __import__('shutil').disk_usage(ROOT).free < 1536 * 1024**2 + limit:
        raise RuntimeError('Preserve 1.5 GiB free-space floor')
    headers = {'User-Agent':'Kenoma-Educational-Data-Audit/1.0'}
    if byte_range: headers['Range'] = 'bytes=' + byte_range
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
        if byte_range and r.status != 206: raise RuntimeError('Server ignored range')
        n = r.headers.get('Content-Length')
        if n is not None and int(n)>limit: raise RuntimeError('Response exceeds limit')
        data = r.read(limit+1)
        if len(data)>limit or transferred+len(data)>MAX_TOTAL: raise RuntimeError('Download budget exceeded')
        transferred += len(data)
        log.append({'url':url,'final_url':r.geturl(),'range':byte_range,'status':r.status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'headers':dict(r.headers),'started_utc':started,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        return data
def main():
    (ROOT/'sources').mkdir(exist_ok=True)
    (ROOT/'audit').mkdir(exist_ok=True)
    tail=fetch(URL,65557,'-65557')
    i=tail.rfind(b'PK\x05\x06')
    sig,disk,cd_disk,n1,n2,cd_size,cd_off,comment=struct.unpack('<4s4H2LH',tail[i:i+22])
    assert sig==b'PK\x05\x06' and disk==0 and cd_disk==0 and n1==n2 and comment==0
    cd=fetch(URL,cd_size,f'{cd_off}-{cd_off+cd_size-1}')
    (ROOT/'audit/bodyparts_zip_central_directory.bin').write_bytes(cd)
    (ROOT/'audit/bodyparts_zip_end_record.bin').write_bytes(tail[i:])
    # Build an in-memory central-directory-only ZIP to read entry metadata.
    end=struct.pack('<4s4H2LH',sig,0,0,n1,n2,cd_size,0,0)
    z=zipfile.ZipFile(io.BytesIO(cd+end))
    entries=[{'filename':v.filename,'compressed_bytes':v.compress_size,'bytes':v.file_size,'header_offset':v.header_offset,'crc32':f'{v.CRC:08x}','compression':v.compress_type} for v in z.infolist()]
    (ROOT/'audit/bodyparts_archive_entries.json').write_text(json.dumps(entries,indent=2))
    mapping=fetch(BASE+'isa_element_parts.txt',2*1024**2)
    (ROOT/'sources/bodyparts_isa_element_parts.txt').write_bytes(mapping)
    for name,link,limit in [('bodyparts_license.html','https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html',128000),('bodyparts_README.html',BASE+'README_e.html',128000)]:
        (ROOT/'sources'/name).write_bytes(fetch(link,limit))
    (ROOT/'audit/download_log.json').write_text(json.dumps(log,indent=2))
    print('Archive entries',len(entries),'downloaded bytes',transferred)
    print('Example entries',entries[:5])
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--documents',action='store_true',help='Reacquire the five documents outside the historical atlas metadata log')
    parser.add_argument('--output',type=pathlib.Path,help='New directory outside the accepted package (required with --documents)')
    parser.add_argument('--openarm-release-directory',type=pathlib.Path,help='Official release readme.md and errata.md, verified against accepted pins')
    args=parser.parse_args()
    if args.documents:
        if args.output is None:parser.error('--documents requires --output')
        from fetch_documents import reacquire
        receipt=reacquire(args.output,args.openarm_release_directory)
        print(json.dumps(receipt,indent=2))
        raise SystemExit(0 if receipt['complete'] else 1)
    if args.output or args.openarm_release_directory:parser.error('Document options require --documents')
    main()
