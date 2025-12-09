#!/usr/bin/env python3
"""remove_comments.py

Scan a directory tree and remove comments from source files using regex.

WARNING: This script uses regular expressions and can remove comment-like
text inside string literals. Use `--dry-run` (default) to inspect changes
before applying. Backups are created when `--apply` is used.
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
from pathlib import Path
from typing import List


PY_EXTS = {'.py', '.sh', '.bash', '.zsh', '.ps1'}
C_LIKE_EXTS = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh', '.java', '.js', '.ts', '.tsx', '.css', '.go', '.rs'}
HTML_EXTS = {'.html', '.htm', '.xml'}
SQL_EXTS = {'.sql'}


def remove_comments_from_text(text: str, ext: str, preserve_shebang: bool = True) -> str:
    """Remove comments from text based on file extension.

    This uses simple regex rules and is NOT aware of language grammars.
    """
    if ext in PY_EXTS:
        lines = text.splitlines(True)
        shebang = ''
        if preserve_shebang and lines and lines[0].startswith('
            shebang = lines[0]
            rest = ''.join(lines[1:])
        else:
            rest = text
        
        rest = re.sub(r'(?m)
        return shebang + rest

    if ext in C_LIKE_EXTS:
        
        s = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        s = re.sub(r'(?m)//.*$', '', s)
        return s

    if ext in HTML_EXTS:
        s = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        return s

    if ext in SQL_EXTS:
        s = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        s = re.sub(r'(?m)--.*$', '', s)
        return s

    
    s = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    s = re.sub(r'(?m)//.*$', '', s)
    s = re.sub(r'(?m)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
    return s


def is_text_file(path: Path) -> bool:
    try:
        with path.open('rb') as f:
            chunk = f.read(4096)
        
        return b'\0' not in chunk
    except Exception:
        return False


def process_file(path: Path, apply: bool, backup: bool) -> bool:
    """Process a single file. Return True if file would be/was changed."""
    if not is_text_file(path):
        return False

    ext = path.suffix.lower()
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding='latin-1')
        except Exception:
            return False

    new = remove_comments_from_text(text, ext)
    if new == text:
        return False

    if not apply:
        print(f'CHANGED: {path}')
        diff = difflib.unified_diff(
            text.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=str(path), tofile=str(path) + ' (new)'
        )
        for line in diff:
            print(line.rstrip('\n'))
        return True

    
    if backup:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        print(f'Backup created: {bak}')

    path.write_text(new, encoding='utf-8')
    print(f'Applied: {path}')
    return True


def gather_files(root: Path, exts: List[str] | None = None, skip_dirs: List[str] | None = None):
    skip_dirs = set(skip_dirs or {'.git', '__pycache__', 'node_modules', 'venv', '.venv'})
    for dirpath, dirnames, filenames in os.walk(root):
        
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            p = Path(dirpath) / fn
            if exts:
                if p.suffix.lower() in exts:
                    yield p
            else:
                yield p


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Remove comments from source files (regex-based).')
    p.add_argument('--root', '-r', default='.', help='Root directory to scan')
    p.add_argument('--exts', '-e', default=None,
                   help='Comma-separated list of extensions to process (e.g. .py,.c,.js). Default: common code extensions')
    p.add_argument('--apply', action='store_true', help='Actually write changes. Without this flag script runs in dry-run mode')
    p.add_argument('--backup', action='store_true', default=True, help='Create .bak backups when applying (default ON)')
    p.add_argument('--no-backup', dest='backup', action='store_false', help='Disable backups')
    p.add_argument('--skip', default=None, help='Comma-separated list of directory names to skip')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    if args.exts:
        exts = [e if e.startswith('.') else f'.{e}' for e in (x.strip() for x in args.exts.split(','))]
    else:
        exts = sorted(list(PY_EXTS | C_LIKE_EXTS | HTML_EXTS | SQL_EXTS))

    skip = [x.strip() for x in args.skip.split(',')] if args.skip else None

    print('Root:', root)
    print('Extensions:', ','.join(exts))
    print('Dry-run (no changes will be written):', not args.apply)
    if args.apply:
        print('Backups enabled:', args.backup)

    changed = 0
    total = 0
    for p in gather_files(root, exts=exts, skip_dirs=skip):
        total += 1
        try:
            ok = process_file(p, apply=args.apply, backup=args.backup)
            if ok:
                changed += 1
        except Exception as ex:
            print(f'Error processing {p}: {ex}')

    print(f'Processed {total} files, {changed} files changed.')
    if not args.apply:
        print('Run with `--apply` to write changes. Backups created with .bak suffix when applied.')


if __name__ == '__main__':
    main()
