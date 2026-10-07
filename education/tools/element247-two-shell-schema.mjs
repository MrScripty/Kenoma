/** Metadata only: preserve every numerical value and normalize changed-shell identity. */
import assert from 'node:assert/strict';
export function withChangedShellIdentity(row) {
 assert.ok(['s1','s2'].includes(row.id),'CHANGED_SHELL_ID');
 assert.ok(row.shell===undefined||row.shell===row.id,'CONFLICTING_SHELL_ID');
 assert.equal(row.comparisonShell,row.id,'CHANGED_COMPARISON_SHELL_ID');
 return {...row,shell:row.id};
}
