"""Create once or verify the separate v0.2 manifest; never edits v0.1."""
import argparse
from pathlib import Path
from validation_common import HERE, sha, verify_baseline, verify_protocol


def files():
    found = []
    for path in HERE.rglob('*'):
        if path.is_symlink():
            raise ValueError('Unexpected symbolic link')
        if path.is_file() and path != HERE / 'SHA256SUMS.txt':
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                raise ValueError('Unexpected bytecode artifact')
            found.append(path)
    return sorted(found)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create', action='store_true', help='Create only if no v0.2 manifest exists')
    args = parser.parse_args()
    verify_baseline()
    verify_protocol()
    manifest = HERE / 'SHA256SUMS.txt'
    inventory = files()
    if args.create:
        with manifest.open('x', encoding='utf-8', newline='\n') as stream:
            for path in inventory:
                stream.write(sha(path) + '  ' + path.relative_to(HERE).as_posix() + '\n')
    entries = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        if name in entries or name == 'SHA256SUMS.txt':
            raise ValueError('Duplicate or self-referential manifest entry')
        path = (HERE / name).resolve()
        if HERE not in path.parents or not path.is_file() or sha(path) != digest:
            raise ValueError('v0.2 checksum mismatch: ' + name)
        entries[name] = digest
    if set(entries) != {p.relative_to(HERE).as_posix() for p in inventory}:
        raise ValueError('v0.2 manifest coverage mismatch')
    print('Original v0.1: 8/8 PASS; v0.2: ' + str(len(entries)) + '/' + str(len(entries)) + ' PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

