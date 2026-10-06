#!/usr/bin/env python3
"""Build standalone review HTML from the actual scalar solver and pinned data."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'education/data/vertical-force-command-v1/review';out.mkdir(parents=True,exist_ok=True)
s=(ROOT/'education/web/vertical-force-lab.template.html').read_text()
s=s.replace('/*PROTOCOL*/',(ROOT/'education/data/vertical-force-command-v1/protocol.json').read_text()).replace('/*CONTROLS*/',(ROOT/'education/data/millard-reference-v1/review/native-controls.json').read_text()).replace('/*MODEL*/',(ROOT/'education/web/vertical-force-model.js').read_text())
(out/'vertical-force-lab.html').write_text(s);print('Built standalone scalar lab',len(s.encode()),'bytes')
