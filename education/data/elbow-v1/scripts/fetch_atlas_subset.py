#!/usr/bin/env python3
"""Fetch just ten named arm meshes using ZIP HTTP ranges; validate each CRC."""
import csv, hashlib, json, pathlib, struct,zlib
from fetch_sources import ROOT, URL, fetch, log
IDS={'FMA23130','FMA23464','FMA23467','FMA37668','FMA37684','FMA37686','FMA37695','FMA37697','FMA37699','FMA38486'}
def main():
    table=list(csv.DictReader((ROOT/'sources/bodyparts_isa_element_parts.txt').open(),delimiter='\t'))
    selected=[r for r in table if r['concept id'] in IDS]
    assert len(selected)==10
    entries=json.loads((ROOT/'audit/bodyparts_archive_entries.json').read_text())
    byname={e['filename']:e for e in entries}
    out=ROOT/'sources/bodyparts3d'; out.mkdir(exist_ok=True)
    for r in selected:
        e=byname['isa_BP3D_4.0_obj_99/'+r['element file id']+'.obj']
        assert e['bytes']<5*1024**2 and e['compressed_bytes']<2*1024**2 and e['compression']==8
        off=e['header_offset']
        head=fetch(URL,30,f'{off}-{off+29}')
        vals=struct.unpack('<4s5H3I2H',head)
        assert vals[0]==b'PK\x03\x04' and not vals[2]&1 and vals[3]==8
        name_len,extra_len=vals[-2:]
        start=off+30; length=name_len+extra_len+e['compressed_bytes']
        data=fetch(URL,length,f'{start}-{start+length-1}')
        assert data[:name_len].decode()==e['filename']
        raw=zlib.decompress(data[name_len+extra_len:],-15)
        assert len(raw)==e['bytes'] and f'{zlib.crc32(raw):08x}'==e['crc32']
        path=out/(r['element file id']+'.obj'); path.write_bytes(raw)
        r.update(e); r['sha256']=hashlib.sha256(raw).hexdigest()
        print(r['name'],len(raw),flush=True)
    (ROOT/'audit/bodyparts_subset_members.json').write_text(json.dumps(selected,indent=2))
    (ROOT/'audit/bodyparts_subset_download_log.json').write_text(json.dumps(log,indent=2))
if __name__=='__main__': main()
