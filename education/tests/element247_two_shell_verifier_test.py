"""Independent retained arithmetic damage controls, no law calls."""
import copy,importlib.util,json,pathlib,subprocess,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('two_shell_verifier',ROOT/'tools/verify-element247-two-shell.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
class RetainedControls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  code='''import fs from 'node:fs';import {compareChangedShells,buildConstructedStage} from './tools/element247-two-shell-protocol.mjs';import {compareShellStages} from './tools/element247-shell-runtime.mjs';const read=p=>JSON.parse(fs.readFileSync(p)),prefix='review/element247-shell-run-20261007/material/',arrays=read(prefix+'saved-arrays.json'),source=read('data/anatomical-arm-v1/generated/arm-reference.json').muscles.find(s=>s.element_id==='FJ1486'),oldRows=Array.from({length:21},(_,i)=>read(prefix+`A55-terminal46-${i===20?'core':'s'+(i+1)}-shell.json`)),rows=structuredClone(oldRows);rows[0].pointCount=rows[1].pointCount=2000;rows[0].localGradientsN.volume[1][0]+=2e-5;rows[0].localGradientsN.total[1][0]+=2e-5;const stage=buildConstructedStage(source,rows,arrays.terminalDirectionM),changed=compareChangedShells(oldRows.slice(0,2),rows.slice(0,2),arrays.terminalDirectionM,source.elements_ten_node[247]),whole={...compareShellStages(read(prefix+'A55-terminal46-assembly.json'),stage,arrays.terminalDirectionM,source.elements_ten_node[247],5.492029235357012e-7),qualification:false};console.log(JSON.stringify({rows,stage,changed,whole}));'''
  cls.js_fixture=json.loads(subprocess.check_output(['node','--input-type=module','-e',code],cwd=ROOT,text=True))
 def setUp(self):
  old=ROOT/V.OLD;read=lambda p:json.loads(p.read_text());self.rows=[read(old/f'A55-terminal46-{s}-shell.json') for s in V.SHELLS];self.rows[0]['pointCount']=self.rows[1]['pointCount']=2000;self.stage=read(old/'A55-terminal46-assembly.json');self.stage.update(pointCount=13500,evaluatedPoints=4000,reusedPoints=9500);self.stage['comparisonShells']=[{**copy.deepcopy(r),'originalShells':[r['shell']]} for r in self.rows];self.stage['reconstruction']={'gates':{'forceN':1e-8,'energyJ':1e-9},'component':self.stage['reconstruction']['component'],'elementToGlobal':{'maximumForceDifferenceN':0,'maximumEnergyDifferenceJ':0,'all585Nodes':True}};mesh=read(ROOT/'data/anatomical-arm-v1/generated/arm-reference.json');self.ids=next(s for s in mesh['muscles'] if s['element_id']=='FJ1486')['elements_ten_node'][247];self.direction=read(old/'saved-arrays.json')['terminalDirectionM']
 def test_nonzero_retained_components_reconstruct_without_law_calls(self):V.check_stage(self.rows,self.stage,self.ids,self.direction)
 def test_held_node_damage_is_rejected(self):
  self.stage['nodalGradientsN']['total'][109][0]+=2e-5;self.assertRaisesRegex(V.EvidenceFailure,'CONSTRUCTED_RECONSTRUCTION',V.check_stage,self.rows,self.stage,self.ids,self.direction)
 def test_changed_callback_and_reused_count_confusion_is_rejected(self):
  self.stage['evaluatedPoints']=13500;self.assertRaisesRegex(V.EvidenceFailure,'EVALUATED_COUNTS',V.check_stage,self.rows,self.stage,self.ids,self.direction)
 def test_missing_tail_region_is_rejected(self):self.assertRaisesRegex(V.EvidenceFailure,'ALL_21_REGIONS',V.check_stage,self.rows[:-1],self.stage,self.ids,self.direction)
 def test_nonzero_js_changed_and_whole_comparisons_verify(self):
  f=self.js_fixture;self.assertFalse(V.check_comparison(self.rows[:2],f['rows'][:2],f['changed'],self.ids,self.direction,True));self.assertFalse(V.check_comparison(self.rows,f['rows'],f['whole'],self.ids,self.direction,False));V.check_stage(f['rows'],f['stage'],self.ids,self.direction)
 def test_forged_changed_pass_flag_is_rejected(self):
  f=copy.deepcopy(self.js_fixture);f['changed']['terms']['total']['pass']=True;self.assertRaisesRegex(V.EvidenceFailure,'TERM_PASS_FLAG',V.check_comparison,self.rows[:2],f['rows'][:2],f['changed'],self.ids,self.direction,True)
 def test_nonzero_reused_tail_cannot_be_hidden(self):
  f=copy.deepcopy(self.js_fixture);f['rows'][2]['localGradientsN']['total'][9][2]+=2e-5;self.assertRaisesRegex(V.EvidenceFailure,'REUSED_TAIL_DIFFERENCE',V.check_comparison,self.rows,f['rows'],f['whole'],self.ids,self.direction,False)
if __name__=='__main__':unittest.main(verbosity=2)
