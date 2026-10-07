"""Accepted lifetime suite, excluding its historical pre-authorization-only check.

The old authorization/output are deliberately retained. The new preflight
separately checks the new launcher's missing-authorization refusal.
"""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import element247_shell_execution_test as old
suite=unittest.defaultTestLoader.loadTestsFromModule(old)
def selected(items):
 for item in items:
  if isinstance(item,unittest.TestSuite):yield from selected(item)
  elif not item.id().endswith('LauncherTests.test_public_launcher_refuses_missing_authorization_without_creating_run'):yield item
if __name__=='__main__':
 tests=list(selected(suite));assert len(tests)==30
 # Exact old frozen data stays present; deleting it to satisfy the excluded
 # pre-run-only test would violate preservation of accepted history.
 assert (old.ROOT/'research/element247-shell-execution-authorization-20261007.json').exists()
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests));sys.exit(0 if result.wasSuccessful() else 1)
