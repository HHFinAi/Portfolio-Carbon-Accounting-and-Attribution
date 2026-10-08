"""Release inventory rejects changed or unreviewed bytes before publication."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.check_release_manifest import check


class ReleaseInventoryTests(unittest.TestCase):
    def make_root(self, directory):
        root = Path(directory)
        (root / 'README.md').write_text('Reviewed research package\n')
        manifest = {'files': {'README.md': hashlib.sha256((root / 'README.md').read_bytes()).hexdigest()}}
        (root / 'FILE_MANIFEST.json').write_text(json.dumps(manifest))
        return root

    def test_changed_reviewed_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / 'README.md').write_text('Unreviewed change\n')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                check(root)

    def test_unlisted_public_file_is_rejected_but_run_logs_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / 'runs').mkdir()
            (root / 'runs/log.txt').write_text('Transient replay log')
            self.assertEqual(check(root)['status'], 'PASS')
            (root / 'new-claim.md').write_text('Unreviewed publication claim')
            with self.assertRaisesRegex(ValueError, 'inventory coverage mismatch'):
                check(root)

    def test_manifest_cannot_register_a_parent_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / 'FILE_MANIFEST.json').write_text(json.dumps({'files': {'../outside.txt': '0' * 64}}))
            with self.assertRaisesRegex(ValueError, 'unsafe release inventory path'):
                check(root)

    def test_unlisted_symlink_cannot_hide_outside_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / 'alias.md').symlink_to(root / 'README.md')
            with self.assertRaisesRegex(ValueError, 'symlink'):
                check(root)

    def test_nested_evaluation_predictions_are_reviewed_release_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            archive = root / 'evaluation/claim-accuracy/runs/session-a/predictions.json'
            archive.parent.mkdir(parents=True)
            archive.write_text('{"predictions": []}\n')
            with self.assertRaisesRegex(ValueError, 'inventory coverage mismatch'):
                check(root)
            manifest = json.loads((root / 'FILE_MANIFEST.json').read_text())
            manifest['files'][archive.relative_to(root).as_posix()] = hashlib.sha256(archive.read_bytes()).hexdigest()
            (root / 'FILE_MANIFEST.json').write_text(json.dumps(manifest))
            self.assertEqual(check(root)['status'], 'PASS')
            archive.write_text('{"predictions": ["changed"]}\n')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                check(root)
