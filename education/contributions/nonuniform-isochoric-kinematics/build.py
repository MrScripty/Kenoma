from pathlib import Path
import argparse,hashlib,json
SOURCE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
template=(SOURCE/'index.template.html').read_text();model=(SOURCE/'model.mjs').read_text()
assert template.count('__MODEL_CODE__')==1
target=args.output/'nonuniform-volume-lab.html';target.write_text(template.replace('__MODEL_CODE__',model))
receipt={'kind':'SELF_CONTAINED_STANDALONE_PROPERTY_LAB','formalProofRegistration':'PENDING_REVIEW_NO_NEW_LEAN_CLAIM','inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'model.mjs',SOURCE/'index.template.html',Path(__file__)]},'output':{'name':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}}
(args.output/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(target)
