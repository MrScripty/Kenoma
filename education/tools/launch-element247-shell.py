"""One bounded material invocation, only after separate pinned authorization.
This launcher is prepared but must not be invoked for material work yet.
"""
import os,pathlib,subprocess,sys,time
from element247_shell_execution import BUDGET,COMMAND,need,read,digest,supervise_session
root=pathlib.Path(__file__).resolve().parents[1]
def main():
 started=time.monotonic()  # Includes all authorization/source/preflight checks.
 need(sys.argv[1:]==['--execute'],'Explicit --execute only')
 auth_path=root/'research/element247-shell-execution-authorization-20261007.json'
 need(auth_path.is_file(),'NO_MATERIAL_EXECUTION_AUTHORIZATION')
 auth=read(auth_path);preflight_path=root/'review/element247-shell-lifetime-20261007/runtime-preflight.json';preflight=read(preflight_path)
 need(auth.get('authorized') is True and auth.get('invocations')==1 and auth.get('parentThread')=='01a103c3-a2e6-7606-8c1e-06987ac710f1','ONE_SHOT_AUTHORIZATION_REQUIRED');need(auth.get('budget')==BUDGET,'FROZEN_BUDGET');need(auth.get('runnerSourceCommit')==preflight['sourceCommit'] and auth.get('runtimePreflightSha256')==digest(preflight_path),'PINNED_PREFLIGHT_AUTHORIZATION')
 need(preflight.get('result')=='PASS_ELEMENT247_SHELL_RUNTIME_PREFLIGHT_NO_MATERIAL_ASSEMBLY' and preflight.get('specimenConstitutiveCalls')==0 and preflight['tests']['fail']==0,'RUNTIME_PREFLIGHT_REQUIRED')
 paths=list(preflight['sourceHashes'])+['review/element247-shell-lifetime-20261007/runtime-preflight.json','review/element247-shell-lifetime-20261007/js-tests.log','review/element247-shell-lifetime-20261007/python-tests.log',str(auth_path.relative_to(root))]
 subprocess.run(['git','ls-files','--error-unmatch',*paths],cwd=root,stdout=subprocess.DEVNULL,check=True);subprocess.run(['git','diff','--exit-code','HEAD','--',*paths],cwd=root,stdout=subprocess.DEVNULL,check=True)
 for p,h in preflight['sourceHashes'].items():need(digest(root/p)==h,'CHANGED_SOURCE:'+p)
 need(digest(root/'review/element247-shell-lifetime-20261007/js-tests.log')==preflight['tests']['jsLogSha256'] and digest(root/'review/element247-shell-lifetime-20261007/python-tests.log')==preflight['tests']['pythonLogSha256'],'CHANGED_TEST_LOG')
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();subprocess.run(['git','merge-base','--is-ancestor',preflight['sourceCommit'],head],cwd=root,check=True)
 result=supervise_session(COMMAND,root/'review/element247-shell-run-20261007',root,head,digest(auth_path),started_at=started);return result['exitCode']
if __name__=='__main__':os._exit(main())  # No stdout/error work after successful acceptance publication.
