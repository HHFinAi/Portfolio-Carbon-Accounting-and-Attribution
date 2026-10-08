"""Run this independently packaged repository's checks and archive their logs."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    targets = json.loads((ROOT / 'scripts/validation_targets.json').read_text())
    checks = [
        {'name': 'unit-tests', 'arguments': ['-m', 'unittest', 'discover', '-s', 'tests', '-v']},
        {'name': 'repository-contracts', 'arguments': ['scripts/check_repository.py']},
        {'name': 'release-inventory', 'arguments': ['scripts/check_release_manifest.py']},
        *targets['checks'],
    ]
    results = []
    for check in checks:
        arguments = [value.replace('{run_output}', str(output.resolve())) for value in check['arguments']]
        command = [sys.executable, *arguments]
        try:
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
            code, stdout, stderr = process.returncode, process.stdout, process.stderr
        except (OSError, subprocess.TimeoutExpired) as exc:
            code, stdout, stderr = 1, '', str(exc)
        log = output / (check['name'] + '.log')
        log.write_text(stdout + stderr, encoding='utf-8')
        result = {'name': check['name'], 'status': 'PASS' if code == 0 else 'FAIL',
                  'returncode': code, 'command': command, 'log': str(log)}
        results.append(result)
        print(f"{result['status']}: {check['name']}", flush=True)
    result = {'status': 'PASS' if all(item['returncode'] == 0 for item in results) else 'FAIL',
              'python_version': sys.version.split()[0], 'repository': ROOT.name, 'checks': results,
              'scope': 'Local software, arithmetic and archived evidence checks; not investment approval or clinical/regulatory certification.'}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='New log directory, normally under ignored runs/')
    args = parser.parse_args()
    try:
        result = validate(args.out)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['status'] == 'PASS' else 1)
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
