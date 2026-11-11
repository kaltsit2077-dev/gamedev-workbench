import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('gdw_package',ROOT/'tools/package.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
from release_audit import audit

class PackagingTests(unittest.TestCase):
    def test_renamed_checkout_fixed_root_and_deterministic_zip(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'renamed-checkout'; root.mkdir()
            (root/'README.md').write_text('original public content',encoding='utf-8')
            first=Path(d)/'one.zip'; second=Path(d)/'two.zip'
            self.assertEqual(p.archive(root,first),p.archive(root,second))
            with zipfile.ZipFile(first) as z:
                self.assertEqual(z.namelist(),['gamedev-workbench/README.md'])
                self.assertEqual(z.read(z.namelist()[0]),(root/'README.md').read_bytes())
    def test_local_files_excluded_even_inside_source_areas(self):
        with tempfile.TemporaryDirectory() as d:
            # macOS temp aliases and Windows short names resolve to a different spelling.
            root=Path(d).resolve(); (root/'docs').mkdir(); (root/'skills').mkdir()
            for name in ['local-profile.json','.env','notes.txt','docs/local-profile.json','skills/.env.local','docs/debug.log']:
                (root/name).write_text('private local data',encoding='utf-8')
            (root/'README.md').write_text('public',encoding='utf-8')
            self.assertEqual([f.relative_to(root).as_posix() for f in p.release_files(root)],['README.md'])
    def test_audit_detects_paths_and_credentials_without_echoing_values(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); file=root/'README.md'
            file.write_text('C:'+ '/Users/'+'example/private\n'+'gh'+'p_'+'A'*40,encoding='utf-8')
            found=audit(root)
            self.assertEqual(len(found),2)
            self.assertFalse(any('A'*40 in line or 'example/private' in line for line in found))
    def test_symlinks_rejected_when_host_supports_them(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'README.md').write_text('public')
            (root/'docs').mkdir()
            try: (root/'docs/alias.md').symlink_to(root/'README.md')
            except OSError: self.skipTest('Symlink creation unavailable on this host')
            with self.assertRaises(ValueError): p.release_files(root)

if __name__=='__main__': unittest.main()
