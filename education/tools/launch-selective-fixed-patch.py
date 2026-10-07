"""New one-shot scope. Parent acceptance is required; old authorization cannot apply."""
import os,pathlib,subprocess,sys,time
from element247_shell_execution import need,read,digest,supervise_session
ROOT=pathlib.Path(__file__).resolve().parents[1]
COMMAND=['node','--max-old-space-size=1024','tools/run-selective-fixed-patch.mjs','--execute']
BUDGET={'plannedMaterialCalls':497500,'maximumMaterialCalls':497500,'maximumWallSeconds':300,'nodeHeapMiB':1024,'maximumRssBytes':2147483648,'maximumOutputBytes':67108864,'invocations':1}
def main():
 started=time.monotonic();need(sys.argv[1:]==['--execute'],'Explicit --execute only')
 auth_path=ROOT/'research/selective-fixed-patch-authorization-20261007.json';need(auth_path.is_file(),'NO_SELECTIVE_FIXED_PATCH_AUTHORIZATION');auth=read(auth_path)
 pref_dir=ROOT/'review/selective-fixed-patch-preflight-20261007';pref_path=pref_dir/'preflight.json';pref=read(pref_path);review=read(pref_dir/'independent-review.json')
 need(auth.get('authorized') is True and auth.get('scope')=='selective-fixed-patch-497500' and auth.get('parentAcceptance') is True and auth.get('invocations')==1 and auth.get('parentThread')=='01a103c3-a2e6-7606-8c1e-06987ac710f1','NEW_PARENT_ONE_SHOT_ACCEPTANCE_REQUIRED')
 need(auth.get('budget')==BUDGET and pref.get('budget')==BUDGET,'EXACT_NEW_BUDGET');need(auth.get('runnerSourceCommit')==pref['sourceCommit'] and auth.get('preflightSha256')==digest(pref_path),'PINNED_PREFLIGHT');need(review.get('verdict')=='PASS' and review.get('sourceCommit')==pref['sourceCommit'] and auth.get('independentReviewSha256')==digest(pref_dir/'independent-review.json'),'INDEPENDENT_PREFLIGHT_REQUIRED');need(pref.get('result')=='PASS_SELECTIVE_PATCH_STRUCTURAL_PREFLIGHT_NO_SPECIMEN_CALLS' and pref.get('specimenCalls')==0 and pref['tests']['fail']==0,'PREFLIGHT_REQUIRED')
 paths=list(pref['sourceHashes'])+[str((pref_dir/n).relative_to(ROOT)) for n in ['preflight.json','independent-review.json',*pref['artifactHashes']]]+[str(auth_path.relative_to(ROOT))]
 subprocess.run(['git','ls-files','--error-unmatch',*paths],cwd=ROOT,stdout=subprocess.DEVNULL,check=True);subprocess.run(['git','diff','--exit-code','HEAD','--',*paths],cwd=ROOT,stdout=subprocess.DEVNULL,check=True)
 for p,h in pref['sourceHashes'].items():need(digest(ROOT/p)==h,'CHANGED_SOURCE:'+p)
 for p,h in pref['artifactHashes'].items():need(digest(pref_dir/p)==h,'CHANGED_PREFLIGHT_ARTIFACT:'+p)
 subprocess.run(['git','merge-base','--is-ancestor',pref['sourceCommit'],'HEAD'],cwd=ROOT,check=True);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 return supervise_session(COMMAND,ROOT/'review/selective-fixed-patch-run-20261007',ROOT,head,digest(auth_path),BUDGET,started_at=started,execute_log_cap_bytes=65536)['exitCode']
if __name__=='__main__':os._exit(main())
