"""Damage genuine private PDF/receipt copies; require their actual gates to fail."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
import fitz
from paths import HERE,checked_output,source_hashes
from build import bound_receipts

def run(args):
    out=checked_output(args.output);site=args.site.resolve();audit=args.audit.resolve();proof=args.proof_receipt.resolve()
    bound_receipts(audit,proof)
    manifest=json.loads((site/'build-manifest.json').read_text())
    if manifest['source_sha256']!=source_hashes():raise RuntimeError('Negative controls require genuine current source-bound build')
    rows=[]
    for name in ['nine-point-text','missing-source-line','missing-diagram-label']:
        damaged=out/name;damaged.mkdir();shutil.copyfile(site/'build-manifest.json',damaged/'build-manifest.json')
        doc=fitz.open(site/'lateral-interface-transfer.pdf')
        if name=='nine-point-text':doc[0].insert_text((42,20),'Damaged nine point caption',fontsize=9)
        elif name=='missing-source-line':
            index=next(i for i,p in enumerate(doc) if 'Appendix: exact Lean source' in p.get_text())
            rects=doc[index].search_for('import Mathlib.Data.Real.Basic')
            if not rects:raise RuntimeError('Unique actual source line required for damage')
            doc[index].add_redact_annot(rects[0],fill=(1,1,1));doc[index].apply_redactions()
        else:
            rects=doc[0].search_for('Upper guided element')
            if not rects:raise RuntimeError('Actual vector diagram label required for damage')
            doc[0].add_redact_annot(rects[0],fill=(1,1,1));doc[0].apply_redactions()
        pdf=damaged/'lateral-interface-transfer.pdf';doc.save(pdf);doc.close()
        r=subprocess.run([sys.executable,str(HERE/'check_pdf.py'),'--site',str(damaged),'--output',str(out/(name+'-check'))],capture_output=True,text=True)
        transcript=r.stdout+r.stderr;(out/(name+'.txt')).write_text(transcript)
        fragment={'nine-point-text':'Sub-10pt actual PDF text','missing-source-line':'Exact complete Lean source is not readable','missing-diagram-label':'Missing actual vector diagram'}[name]
        if r.returncode==0 or fragment not in transcript:raise RuntimeError('Actual damaged PDF was not rejected: '+name+' '+transcript)
        rows.append({'damage':name,'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'detected_by':fragment,'exit_code':r.returncode})
    damaged_proof=out/'wrong-proof-source.json';p=json.loads(proof.read_text());p['source_sha256']['LateralInterfaceTransfer.lean']='0'*64
    damaged_proof.write_text(json.dumps(p,indent=2)+'\n')
    try:bound_receipts(audit,damaged_proof)
    except RuntimeError as error:
        if 'Proof source binding mismatch' not in str(error):raise
        rows.append({'damage':'wrong-proof-source','detected_by':str(error),'receipt_sha256':hashlib.sha256(damaged_proof.read_bytes()).hexdigest()})
    else:raise RuntimeError('Copied genuine proof receipt source damage was accepted')
    (out/'qualification-negatives.json').write_text(json.dumps({'status':'passed','controls':rows,'source_sha256':source_hashes(),
      'scope':'Actual copied artifact/receipt defects rejected; original successful evidence preserved.'},indent=2)+'\n')
    print('Three actual damaged PDFs and one source-damaged genuine kernel receipt rejected.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--site',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--proof-receipt',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args())
