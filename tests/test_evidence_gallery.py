import base64
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]/'skills/gamedev-workbench/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('evidence_gallery', SCRIPTS/'evidence_gallery.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')


class GalleryTests(unittest.TestCase):
    def fixture(self, root, **patch):
        report = {'passed': True, 'checks': [{'name': 'layout', 'passed': True}],
                  'frames': [{'image': 'a.png', 'width': 1, 'height': 1}]}
        report.update(patch)
        (root/'a.png').write_bytes(PNG)
        (root/'report.json').write_text(json.dumps(report), encoding='utf-8')
        return report

    def test_export_preserves_originals_and_escapes_inert_payload(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); report = self.fixture(root, input='</script><script>alert(1)</script>')
            original = (root/'report.json').read_bytes()
            output = root/'gallery.html'; result = g.export_gallery(root, output)
            text = output.read_text(encoding='utf-8')
            self.assertNotIn(report['input'], text)
            self.assertIn(base64.b64encode(PNG).decode(), text)
            self.assertEqual((root/'a.png').read_bytes(), PNG)
            self.assertEqual((root/'report.json').read_bytes(), original)
            self.assertFalse(result['engine_started'])
            with self.assertRaises(FileExistsError): g.export_gallery(root, output)
            with self.assertRaises(FileExistsError): g.export_gallery(root, root/'report.json')
            self.assertEqual((root/'report.json').read_bytes(), original)

    def test_rejects_escape_external_and_dimension_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ['../a.png', '/a.png', 'C:/a.png', 'https://x/a.png', 'dir\\a.png']:
                self.fixture(root, frames=[{'image': name}])
                with self.subTest(name=name), self.assertRaises(ValueError): g.load_evidence(root)
            self.fixture(root, frames=[{'image': 'a.png', 'width': 2}])
            with self.assertRaises(ValueError): g.load_evidence(root)
            self.fixture(root); (root/'a.png').write_bytes(b'not png')
            with self.assertRaises(ValueError): g.load_evidence(root)

    def test_truthfulness_headless_and_resource_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.fixture(root, checks=[{'name': 'failure', 'passed': False}])
            with self.assertRaises(ValueError): g.load_evidence(root)
            self.fixture(root, checks=[])
            with self.assertRaises(ValueError): g.load_evidence(root)
            self.fixture(root, passed=False, frames=[], checks=[{'name': 'failure', 'passed': False}])
            report, images = g.load_evidence(root)
            self.assertFalse(report['passed']); self.assertEqual(images, [])
            self.fixture(root, frames=[{'image': 'a.png'}]*201)
            with self.assertRaises(ValueError): g.load_evidence(root)
            self.fixture(root); (root/'a.png').write_bytes(PNG + b'x'*g.MAX_IMAGE)
            with self.assertRaises(ValueError): g.load_evidence(root)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.fixture(root)
            try: (root/'linked.png').symlink_to(root/'a.png')
            except (OSError, NotImplementedError): self.skipTest('Symlink creation unavailable')
            self.fixture(root, frames=[{'image': 'linked.png'}])
            with self.assertRaises(ValueError): g.load_evidence(root)
