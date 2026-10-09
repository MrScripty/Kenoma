"""Renderer scratch/bundle regression and damage probes; no browser or physics."""
import json,os,pathlib,sys,tempfile,types,unittest,urllib.request,urllib.error
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/arm-validation'))
import render as r,render_worker as rw,watchdog as w
class ScratchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kr-scratch-',dir='/tmp');self.root=pathlib.Path(self.tmp.name);self.reserves=[]
        self.out=types.SimpleNamespace(path=self.root,staging={'A':0},reserve=lambda *a:self.reserves.append(a))
    def tearDown(self):self.tmp.cleanup()
    def test_socket_path_rejected_before_output_creation(self):
        r.validate_output_path(pathlib.Path('/workspace/kr1'))
        for q in [pathlib.Path('relative'),pathlib.Path('/workspace/'+'x'*100),pathlib.Path('/workspace/a/../b')]:
            with self.assertRaises(w.Refusal):r.validate_output_path(q)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_all_chromium_scratch_names_are_charged_inside_owned_root(self):
        p=self.root/'browser-profile';p.mkdir()
        for name in ['org.chromium.Chromium.123','.org.chromium.Chromium.456','playwright-artifacts-abc','xdg-config','xdg-cache']:
            d=p/name;d.mkdir();(d/'data').write_bytes(b'123')
        r.monitor_output(self.out)
        expected=16777216+sum(q.lstat().st_size for q in self.root.rglob('*'))
        self.assertEqual(self.out.staging['A'],expected);self.assertEqual(self.reserves,[('A',0)])
    def test_old_unconfined_scratch_and_nested_artifacts_refuse(self):
        for name in ['.config','org.chromium.Chromium.bad','playwright-artifacts-bad','nested']:
            d=self.root/name;d.mkdir()
            with self.assertRaisesRegex(w.Refusal,'Foreign'):r.monitor_output(self.out)
            d.rmdir()
        p=self.root/'browser-profile';p.mkdir();(p/'foreign-link').symlink_to('/tmp')
        with self.assertRaisesRegex(w.Refusal,'symlink'):r.monitor_output(self.out)
    def test_scratch_size_ceiling_stays_64mib(self):
        p=self.root/'browser-profile';p.mkdir()
        with (p/'large').open('wb') as f:f.truncate(67108865)
        with self.assertRaisesRegex(w.Refusal,'ceiling'):r.monitor_output(self.out)
    def test_entry_ceiling_stays_2048(self):
        p=self.root/'browser-profile';p.mkdir()
        with patch.object(r.os,'walk',return_value=iter([(str(p),[],[str(i) for i in range(2048)])])),patch.object(pathlib.Path,'lstat',return_value=types.SimpleNamespace(st_mode=0o100600,st_size=0)):
            # Include the scratch directory plus 2048 files.
            with patch.object(r.os,'walk',return_value=iter([(str(self.root),['browser-profile'],[]),(str(p),[],[str(i) for i in range(2048)])])):
                with self.assertRaisesRegex(w.Refusal,'ceiling'):r.monitor_output(self.out)
    def test_lstat_disappearance_restarts_full_inventory(self):
        p=self.root/'browser-profile';p.mkdir();target=p/'temporary';target.write_bytes(b'x');original=pathlib.Path.lstat;calls=0
        def race(q):
            nonlocal calls
            if q==target and calls==0:calls+=1;raise FileNotFoundError(2,'disappeared',str(q))
            return original(q)
        with patch.object(pathlib.Path,'lstat',race):r.monitor_output(self.out)
        self.assertEqual(calls,1);self.assertEqual(len(self.reserves),1)
    def test_walk_disappearance_restarts_but_bounded_retry_refuses(self):
        p=self.root/'browser-profile';p.mkdir();original=os.walk;calls=0
        def race(*args,**kwargs):
            nonlocal calls
            calls+=1
            if calls==1:kwargs['onerror'](FileNotFoundError(2,'gone',str(p/'gone')))
            return original(*args,**kwargs)
        with patch.object(r.os,'walk',race):r.monitor_output(self.out)
        self.assertEqual(calls,2)
        def unstable(*args,**kwargs):raise FileNotFoundError(2,'gone',str(p/'gone'))
        with patch.object(r.os,'walk',unstable):
            with self.assertRaisesRegex(w.Refusal,'Unstable'):r.monitor_output(self.out)
    def test_non_scratch_disappearance_and_permission_error_fail_closed(self):
        for error in [FileNotFoundError(2,'gone',str(self.root/'viewer.js')),PermissionError(13,'denied',str(self.root/'browser-profile'))]:
            with patch.object(r.os,'walk',side_effect=error):
                with self.assertRaises(type(error)):r.monitor_output(self.out)
    def test_worker_scratch_routing_is_local_and_does_not_change_flags(self):
        profile=self.root/'browser-profile'
        with patch.dict(os.environ,{},clear=False),patch.object(tempfile,'tempdir',None):
            rw.configure_scratch(profile)
            self.assertEqual(os.environ['TMPDIR'],str(profile));self.assertEqual(tempfile.tempdir,str(profile))
            self.assertEqual(os.environ['XDG_CONFIG_HOME'],str(profile/'xdg-config'));self.assertEqual(os.environ['XDG_CACHE_HOME'],str(profile/'xdg-cache'))
    def test_existing_page_reused_without_new_page(self):
        page=object();context=types.SimpleNamespace(pages=[page],new_page=lambda:(_ for _ in ()).throw(AssertionError('extra page')))
        self.assertIs(rw.existing_page(context),page)
        for pages in [[],[page,page]]:
            with self.assertRaisesRegex(ValueError,'one initial'):rw.existing_page(types.SimpleNamespace(pages=pages))
    def test_synthetic_caption_copy_never_invents_measured_residual(self):
        rows=[dict(coordinatesSHA256='pinned',residualN=0)]
        self.assertEqual(rw.display_frames(rows,True),[dict(coordinatesSHA256='pinned')]);self.assertEqual(rows[0]['residualN'],0)
        self.assertEqual(rw.display_frames(rows,False),rows)
    def test_local_server_only_serves_two_exact_files(self):
        (self.root/'viewer.html').write_bytes(b'<p>Synthetic</p>');(self.root/'viewer.js').write_bytes(b'window.synthetic=true')
        server,thread,origin=rw.local_preview(self.root);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            self.assertEqual(server.server_address[0],'127.0.0.1')
            for name in ['viewer.html','viewer.js']:self.assertEqual(opener.open(origin+'/'+name,timeout=2).read(),(self.root/name).read_bytes())
            for path in ['/','/../manifest.json','/viewer.js?x=1','/manifest.json']:
                with self.assertRaises(urllib.error.HTTPError) as error:opener.open(origin+path,timeout=2)
                self.assertEqual(error.exception.code,404)
        finally:server.shutdown();server.server_close();thread.join(timeout=1)
    def test_prebuilt_bundle_requires_fixed_bytes_and_four_source_closure(self):
        cfg=dict(nodeModules='/installed',browserBundle='/pinned.js');bundle=b'fixture';expected=w.digest(bundle)
        def read(path,*args):
            path=str(path)
            if path.endswith('three/package.json'):return b'{"version":"0.180.0"}'
            if path.endswith('esbuild/package.json'):return b'{"version":"0.25.10"}'
            return bundle
        hashes={k:expected for k in rw.BUNDLE_CLOSURE}
        with patch.object(rw,'read_regular',side_effect=read),patch.object(rw,'BUNDLE_CLOSURE',hashes),patch.object(rw,'PINNED_BUNDLE',expected):
            raw,receipt=rw.prebuilt_bundle(cfg);self.assertEqual(raw,bundle);self.assertEqual(len(receipt['closureSHA256']),4);self.assertEqual(receipt['buildChildProcesses'],0)
            with patch.object(rw,'PINNED_BUNDLE','bad'):
                with self.assertRaisesRegex(ValueError,'exact prebuilt'):rw.prebuilt_bundle(cfg)
            with patch.object(rw,'BUNDLE_CLOSURE',{**hashes,'geometry.mjs':'bad'}):
                with self.assertRaisesRegex(ValueError,'closure'):rw.prebuilt_bundle(cfg)
if __name__=='__main__':unittest.main()
