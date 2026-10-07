/** Damage controls on immutable retained reads, without any law calls or file mutation. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {immutableSnapshotReader} from '../tools/reconstruct-element247-two-shell.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
const record='review/element247-two-shell-run-20261007/material/T24-terminal46-s1-shell.json';
test('immutable complete changed-shell record is readable without mutation',()=>{
 const reader=immutableSnapshotReader(root),r=reader.json(record);assert.equal(r.pointCount,2000);assert.equal(r.id,'s1');assert.equal(r.shell,undefined);assert.ok(r.localGradientsN.total.flat().some(x=>x!==0));assert.equal(reader.inventory[record].bytes,3281);
});
test('one-byte numerical or schema corruption refuses immutable input',()=>{
 const reader=immutableSnapshotReader(root,p=>{const b=fs.readFileSync(p);b[200]^=1;return b;});assert.throws(()=>reader.json(record),/IMMUTABLE_INPUT_MISMATCH/);
});
test('truncated physical-weight evidence refuses immutable input',()=>{
 const reader=immutableSnapshotReader(root,p=>fs.readFileSync(p).subarray(0,13));assert.throws(()=>reader.read(record.replace('shell.json','weights.f64le')),/IMMUTABLE_INPUT_MISMATCH/);
});
test('missing and nonportable inputs refuse without an alternate evidence source',()=>{
 const reader=immutableSnapshotReader(root,()=>{throw Error('ENOENT synthetic missing input');});assert.throws(()=>reader.json(record),/ENOENT/);assert.throws(()=>reader.read('../escape'),/PORTABLE_INPUT_PATH/);
});
