"""Verify the explicitly reviewed release inventory; never rewrite its hashes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath

EXCLUDED_DIRECTORIES = {'.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'build', 'dist', 'htmlcov'}


def candidate_files(root: Path) -> set[str]:
    result = set()
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        # Only top-level run/output folders are transient. Reviewed evaluation
        # archives under evaluation/claim-accuracy/runs belong to the release.
        if relative.parts[0] in {'runs', 'exports', 'outputs'}:
            continue
        if any(part in EXCLUDED_DIRECTORIES or part.endswith('.egg-info') for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f'symlink is not a reviewed release file: {relative}')
        if not path.is_file() or path.name in {'FILE_MANIFEST.json', '.DS_Store', '.coverage'} or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.name.startswith('.env') and path.name != '.env.example':
            raise ValueError(f'local credentials must not enter a release: {relative}')
        result.add(relative.as_posix())
    return result


def check(root: Path) -> dict:
    root = root.resolve()
    manifest = json.loads((root / 'FILE_MANIFEST.json').read_text(encoding='utf-8'))
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('release manifest has no reviewed file inventory')
    for relative, expected in files.items():
        path = PurePosixPath(relative)
        if path.is_absolute() or '..' in path.parts or '\\' in relative or path.as_posix() != relative:
            raise ValueError(f'unsafe release inventory path: {relative}')
        source = root / relative
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(root):
            raise ValueError(f'release file missing or outside repository: {relative}')
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError(f'release hash mismatch: {relative}')
    actual = candidate_files(root)
    missing = sorted(actual - set(files))
    obsolete = sorted(set(files) - actual)
    if missing or obsolete:
        raise ValueError(f'release inventory coverage mismatch; unlisted={missing}; obsolete={obsolete}')
    return {'status': 'PASS', 'files': len(files), 'unsigned_integrity_manifest': True,
            'scope': 'Reviewed local bytes and inventory only; not authenticated provenance or source truth.'}


if __name__ == '__main__':
    import sys
    try:
        print(json.dumps(check(Path(__file__).resolve().parents[1]), indent=2))
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
