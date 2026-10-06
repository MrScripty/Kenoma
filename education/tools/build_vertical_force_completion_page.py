#!/usr/bin/env python3
"""Standalone successor UI; base physics and frozen review HTML are untouched."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'education/data/vertical-force-completion-v1/review';out.mkdir(parents=True,exist_ok=True)
template=(ROOT/'education/web/vertical-force-completion.template.html').read_text()
mode=(ROOT/'education/web/vertical-force-mode-aware.js').read_text()
mode='\n'.join(line for line in mode.splitlines() if not line.startswith('import '))
s=template.replace('/*PROTOCOL*/',(ROOT/'education/data/vertical-force-command-v1/protocol.json').read_text()).replace('/*CONTROLS*/',(ROOT/'education/data/millard-reference-v1/review/native-controls.json').read_text()).replace('/*MODEL*/',(ROOT/'education/web/vertical-force-model.js').read_text()+'\n'+mode)
(out/'vertical-force-lab.html').write_text(s);print('Built mode-aware scalar lab',len(s.encode()),'bytes')
