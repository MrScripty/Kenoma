"""Read-only producer arithmetic/refusal check; no material-law imports or calls."""
import argparse, hashlib, importlib.util, json, pathlib, sys

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=pathlib.Path, required=True)
parser.add_argument('--candidate', type=pathlib.Path, required=True)
args = parser.parse_args()
root = args.root.resolve()
sys.path.insert(0, str(root / 'tools'))
spec = importlib.util.spec_from_file_location('two_shell_retained_verifier', root / 'tools/verify-element247-two-shell.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
read = lambda p: json.loads(p.read_text())
candidate = read(args.candidate)
raw = root / 'review/element247-two-shell-run-20261007'
old = root / 'review/element247-shell-run-20261007/material'
assert candidate['operationalCompletion'] is False
assert candidate['originalExitCodes'] == {'child': 1, 'worker': 1, 'publicEntry': 1}
assert candidate['newMaterialCalls'] == candidate['newSpecimenCalls'] == candidate['newQuadratureEvaluations'] == 0
assert candidate['element247Qualification'] is candidate['patchQualification'] is False
assert candidate['authorizationStatus'] == 'CONSUMED_BY_ORIGINAL_ONE_SHOT; NO_RETRY_AUTHORIZATION'
for name, info in candidate['provenance']['immutableInputInventory'].items():
    data = (root / name).read_bytes()
    assert len(data) == info['bytes'] and hashlib.sha256(data).hexdigest() == info['sha256'], name
rows = []
for shell in v.SHELLS:
    row = read(raw / 'material' / f'{"T24" if shell in ["s1", "s2"] else "A55"}-terminal46-{shell}-shell.json')
    if shell in ['s1', 's2']:
        assert row['id'] == row['comparisonShell'] == shell and 'shell' not in row
        row = {**row, 'shell': row['id']}
    rows.append(row)
arrays = read(raw / 'material/saved-arrays.json')
source = next(s for s in read(root / 'data/anatomical-arm-v1/generated/arm-reference.json')['muscles'] if s['element_id'] == 'FJ1486')
ids, direction = source['elements_ten_node'][247], arrays['terminalDirectionM']
v.check_stage(rows, candidate['constructedWholeValues'], ids, direction)
old_rows = [read(old / f'A55-terminal46-{shell}-shell.json') for shell in v.SHELLS]
changed_pass = v.check_comparison(old_rows[:2], rows[:2], candidate['changedShellComparison'], ids, direction, True)
whole_pass = v.check_comparison(old_rows, rows, candidate['constructedWholeComparison'], ids, direction, False)
try:
    v.require_terminal_evidence(raw, budget=v.BUDGET, command=v.COMMAND)
except v.EvidenceFailure as error:
    refusal = str(error)
    assert refusal == 'EXTERNAL_INCOMPLETE_TAKES_PRECEDENCE'
else:
    raise AssertionError('FAILED_RUN_TERMINAL_ACCEPTANCE_FORBIDDEN')
print(json.dumps({'result': 'PASS_PRODUCER_RECONSTRUCTED_ARITHMETIC_WITH_ORIGINAL_COMPLETION_REFUSED', 'candidateSha256': hashlib.sha256(args.candidate.read_bytes()).hexdigest(), 'reconstructionSourceCommit': candidate['reconstructionSourceCommit'], 'newMaterialCalls': 0, 'newSpecimenCalls': 0, 'changedArithmeticPass': changed_pass, 'constructedWholeArithmeticPass': whole_pass, 'nodesVerified': 585, 'regionsVerified': 21, 'immutableInputsVerified': len(candidate['provenance']['immutableInputInventory']), 'operationalCompletion': False, 'terminalRefusal': refusal, 'qualification': False}, indent=2))
