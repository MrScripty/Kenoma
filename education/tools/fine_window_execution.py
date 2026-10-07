"""New accepted preparation budgets; no authorization or specimen callback."""
import pathlib
from element247_shell_execution import need,read,digest,supervise_session,require_terminal_evidence
ROOT=pathlib.Path(__file__).resolve().parents[1]
COMMAND=['node','--max-old-space-size=1024','tools/run-fine-window.mjs','--execute']
BUDGET={'plannedMaterialCalls':19716000,'maximumMaterialCalls':19716000,'maximumWallSeconds':7200,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':536870912,'invocations':1}
SCOPE='fine-window-fixed-patch-19716000'
RESULTS={'PASS_BOUNDED_FINE_WINDOW_FIXED_PATCH_AGREEMENT','UNRESOLVED_FIXED_PATCH_INTEGRATION'}
PREF=ROOT/'review/fine-window-preflight-20261007';AUTH=ROOT/'research/fine-window-authorization-20261007.json';RUN=ROOT/'review/fine-window-run-20261007'
def validate_authorization(auth,pref,review):
 need(auth.get('authorized') is True and auth.get('parentAcceptance') is True and auth.get('scope')==SCOPE and auth.get('invocations')==1 and auth.get('parentThread')=='01a103c3-a2e6-7606-8c1e-06987ac710f1','NEW_PARENT_ONE_SHOT_ACCEPTANCE_REQUIRED')
 need(auth.get('budget')==BUDGET and pref.get('budget')==BUDGET,'EXACT_NEW_BUDGET')
 need(auth.get('runnerSourceCommit')==pref.get('sourceCommit'),'PINNED_PREFLIGHT_SOURCE')
 need(pref.get('result')=='PASS_FINE_WINDOW_STRUCTURAL_PREFLIGHT_NO_SPECIMEN_CALLS' and pref.get('specimenCalls')==0 and pref.get('materialLawInvocations')==0 and pref.get('tests',{}).get('fail')==0,'PREFLIGHT_REQUIRED')
 need(review.get('verdict')=='PASS' and review.get('sourceCommit')==pref.get('sourceCommit'),'INDEPENDENT_PREFLIGHT_REQUIRED')
