"""One fresh reviewed scope; old consumed authorization cannot apply."""
import os,subprocess,sys,time
from fine_window_execution import ROOT,COMMAND,BUDGET,PREF,AUTH,RUN,need,read,digest,supervise_session,validate_authorization
def main():
 started=time.monotonic();need(sys.argv[1:]==['--execute'],'Explicit --execute only');need(AUTH.is_file(),'NO_FINE_WINDOW_AUTHORIZATION');auth=read(AUTH);pref=read(PREF/'preflight.json');review=read(PREF/'independent-review.json');validate_authorization(auth,pref,review)
 need(auth.get('preflightSha256')==digest(PREF/'preflight.json') and auth.get('independentReviewSha256')==digest(PREF/'independent-review.json'),'PINNED_EVIDENCE_HASHES')
 paths=list(pref['sourceHashes'])+[str((PREF/n).relative_to(ROOT)) for n in ['preflight.json','independent-review.json',*pref['artifactHashes']]]+[str(AUTH.relative_to(ROOT))]
 subprocess.run(['git','ls-files','--error-unmatch',*paths],cwd=ROOT,stdout=subprocess.DEVNULL,check=True);subprocess.run(['git','diff','--exit-code','HEAD','--',*paths],cwd=ROOT,stdout=subprocess.DEVNULL,check=True)
 for p,h in pref['sourceHashes'].items():need(digest(ROOT/p)==h,'CHANGED_SOURCE:'+p)
 for p,h in pref['artifactHashes'].items():need(digest(PREF/p)==h,'CHANGED_PREFLIGHT_ARTIFACT:'+p)
 subprocess.run(['git','merge-base','--is-ancestor',pref['sourceCommit'],'HEAD'],cwd=ROOT,check=True);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 return supervise_session(COMMAND,RUN,ROOT,head,digest(AUTH),BUDGET,started_at=started,execute_log_cap_bytes=65536)['exitCode']
if __name__=='__main__':os._exit(main())
