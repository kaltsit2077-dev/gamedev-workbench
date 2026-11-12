import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/gamedev-workbench/scripts'))
from git_review import review_git, git


def command(root, *args, check=True):
    return subprocess.run(['git', '-c', 'core.autocrlf=false', '-C', str(root), *args], capture_output=True, check=check,
                          env=dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0'))


class GitReviewTests(unittest.TestCase):
    def setup_repo(self, root):
        command(root, 'init', '-b', 'main'); command(root, 'config', 'user.name', 'Fixture')
        command(root, 'config', 'user.email', 'fixture@example.invalid')
        (root/'state.gd').write_text('extends Node\nvar value = 1\n', encoding='utf-8')
        (root/'state.gd.uid').write_text('uid://example\n', encoding='utf-8')
        command(root, 'add', '.'); command(root, 'commit', '-m', 'fixture base')
    def test_dirty_staged_rename_and_uid_hints_without_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); self.setup_repo(root)
            command(root, 'mv', 'state.gd', 'renamed state.gd')
            (root/'note space.md').write_text('changed', encoding='utf-8')
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            report = review_git(root, 'HEAD')
            after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            self.assertTrue(any(f['kind'] == 'metadata-rename' for f in report['findings']))
            self.assertIn('note space.md', [r['path'] for r in report['changes']])
    def test_actual_merge_index_and_markers_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); self.setup_repo(root); command(root, 'switch', '-c', 'other')
            (root/'state.gd').write_text('extends Node\nvar value = 2\n', encoding='utf-8')
            command(root, 'commit', '-am', 'other'); command(root, 'switch', 'main')
            (root/'state.gd').write_text('extends Node\nvar value = 3\n', encoding='utf-8')
            command(root, 'commit', '-am', 'main')
            self.assertNotEqual(command(root, 'merge', 'other', check=False).returncode, 0)
            report = review_git(root)
            self.assertEqual(report['assessment'], 'blocked-by-unmerged-index')
            self.assertIn('MERGE_HEAD', report['operations']); self.assertEqual(report['unmerged_paths'], ['state.gd'])
            self.assertTrue(any(f['kind'] == 'possible-conflict-markers' for f in report['findings']))
    def test_unknown_base_limits_and_no_network_freshness_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); self.setup_repo(root)
            report = review_git(root, 'missing-reference')
            self.assertFalse(report['scan_complete']); self.assertIsNone(report['base'])
            self.assertIsNone(report['local_divergence'])
            for name in ['one.md', 'two.md']: (root/name).write_text('text', encoding='utf-8')
            report = review_git(root, max_paths=1)
            self.assertFalse(report['scan_complete']); self.assertEqual(len(report['changes']), 1)
    def test_local_upstream_divergence_and_committed_base_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); self.setup_repo(root)
            base = command(root, 'rev-parse', 'HEAD').stdout.decode().strip()
            command(root, 'config', 'remote.origin.url', 'https://example.invalid/never-fetch.git')
            command(root, 'config', 'remote.origin.fetch', '+refs/heads/*:refs/remotes/origin/*')
            command(root, 'update-ref', 'refs/remotes/origin/main', base)
            command(root, 'config', 'branch.main.remote', 'origin')
            command(root, 'config', 'branch.main.merge', 'refs/heads/main')
            (root/'state.gd').write_text('extends Node\nvar value = 4\n', encoding='utf-8')
            command(root, 'commit', '-am', 'local change')
            report = review_git(root, base)
            self.assertEqual(report['local_divergence'], {'ahead': 1, 'behind': 0})
            self.assertEqual(report['changes'], [{'path': 'state.gd', 'status': 'M', 'origin': 'base-to-worktree'}])
            self.assertTrue(report['scan_complete'])
    @unittest.skipIf(os.name == 'nt', 'Windows does not support newline filenames')
    def test_null_delimited_paths_keep_newlines(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); self.setup_repo(root)
            (root/'line\nbreak.md').write_text('content', encoding='utf-8')
            self.assertIn('line\nbreak.md', [r['path'] for r in review_git(root)['changes']])
    def test_configured_clean_filter_is_not_executed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve(); self.setup_repo(root)
            (root/'.gitattributes').write_text('state.gd filter=fixture\n', encoding='utf-8')
            command(root, 'add', '.'); command(root, 'commit', '-m', 'attributes')
            driver = root/'filter.py'
            driver.write_text('import sys\nfrom pathlib import Path\nPath(__file__).with_name("filter-ran").write_text("ran")\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n', encoding='utf-8')
            command(root, 'config', 'filter.fixture.clean', '"'+sys.executable+'" "'+str(driver)+'"')
            (root/'state.gd').write_text('extends Node\nvar value = 8\n', encoding='utf-8')
            git(root, ['diff', '--no-ext-diff', '--no-textconv', '--numstat', '--'])
            self.assertFalse((root/'filter-ran').exists())
