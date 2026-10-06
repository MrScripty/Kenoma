#!/usr/bin/env python3
"""Acquire two additional licensed atlas members with bounded ZIP ranges.

Original elbow-v1 files are read-only inputs. This does not acquire a full atlas.
"""
import datetime,hashlib,json,pathlib,struct,urllib.request,zlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'elbow-v1'
URL='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20130619/isa_BP3D_4.0_obj_99.zip'
SELECTED={'FJ3362':('FMA13322','right clavicle'),'FJ3384':('FMA13395','right scapula')}
TOTAL_LIMIT=2*1024**2
def main():
 entries={e['filename']:e for e in json.loads((OLD/'audit/bodyparts_archive_entries.json').read_text())}
 log=[];transferred=0;members=[];error_message=None
 def fetch(start,length):
  nonlocal transferred
  if length<=0 or transferred+length>TOTAL_LIMIT:raise ValueError('Download budget exceeded')
  request=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{start+length-1}','User-Agent':'Kenoma-Educational-Data-Audit/1.0'})
  began=datetime.datetime.now(datetime.timezone.utc).isoformat()
  with urllib.request.urlopen(request,timeout=60) as response:
   if response.status!=206 or not response.headers.get('Content-Range','').startswith(f'bytes {start}-{start+length-1}/'):raise ValueError('Wrong range response')
   if int(response.headers.get('Content-Length',length))!=length:raise ValueError('Unexpected byte count')
   raw=response.read(length+1)
   if len(raw)!=length:raise ValueError('Incomplete or oversized range')
   transferred+=len(raw);log.append({'url':URL,'range':[start,start+length-1],'status':response.status,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'started_utc':began,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'etag':response.headers.get('ETag'),'last_modified':response.headers.get('Last-Modified')})
   return raw
 out=ROOT/'sources/bodyparts3d';out.mkdir(parents=True,exist_ok=True)
 try:
  for element,(concept,name) in SELECTED.items():
   entry=entries[f'isa_BP3D_4.0_obj_99/{element}.obj']
   if entry['bytes']>2*1024**2 or entry['compressed_bytes']>1024**2 or entry['compression']!=8:raise ValueError('Member outside bounds')
   header=fetch(entry['header_offset'],30);values=struct.unpack('<4s5H3I2H',header)
   if values[0]!=b'PK\x03\x04' or values[2]&1 or values[3]!=8:raise ValueError('Invalid local member header')
   n,e=values[-2:];payload=fetch(entry['header_offset']+30,n+e+entry['compressed_bytes'])
   if payload[:n].decode()!=entry['filename']:raise ValueError('Unexpected member name')
   decoder=zlib.decompressobj(-15);raw=decoder.decompress(payload[n+e:],entry['bytes']+1)
   if len(raw)!=entry['bytes'] or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('Invalid bounded decompression')
   if f'{zlib.crc32(raw):08x}'!=entry['crc32']:raise ValueError('Source CRC differs from retained archive directory')
   path=out/(element+'.obj');digest=hashlib.sha256(raw).hexdigest()
   if path.exists() and path.read_bytes()!=raw:raise ValueError('Existing source differs; do not overwrite')
   path.write_bytes(raw);members.append({'concept_id':concept,'element_id':element,'name':name,'path':str(path.relative_to(ROOT)),**entry,'sha256':digest,'license':'CC-BY-4.0 current official archive grant; original OBJ notices preserved'})
   print(name,len(raw),digest,flush=True)
 except Exception as error:
  error_message=f'{type(error).__name__}: {error}'
  raise
 finally:
  audit=ROOT/'audit';audit.mkdir(exist_ok=True)
  (audit/'shoulder_download_log.json').write_text(json.dumps({'url':URL,'byte_budget':TOTAL_LIMIT,'transferred_bytes':transferred,'requests':log,'status':'completed' if len(members)==2 else 'failed','error':error_message,'required_for_milestone':False},indent=2)+'\n')
 if len(members)!=2:raise ValueError('Incomplete shoulder acquisition')
 (ROOT/'audit/shoulder_source_pins.json').write_text(json.dumps({'schema':1,'archive_directory_reference':'../../elbow-v1/audit/bodyparts_archive_entries.json','archive_url_is_not_an_immutable_content_id':True,'members':members},indent=2)+'\n')
if __name__=='__main__':main()
