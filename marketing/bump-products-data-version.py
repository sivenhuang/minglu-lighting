#!/usr/bin/env python3
"""
Bump the cache-bust version of assets/js/products-data.js across all HTML files.

Rule (set 2026-11-04): every time assets/js/products-data.js is edited,
its version query string (?v=N) must be incremented by 1 so browsers fetch
the new file instead of a cached copy. This script detects the current
version from the HTML references and bumps it by 1 everywhere.

Usage (from repo root):
    python marketing/bump-products-data-version.py
    python marketing/bump-products-data-version.py --check   # print current version only

The script only rewrites the version suffix on `products-data.js?v=N`
references inside *.html files. It does not touch the JS file itself.
"""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERN = re.compile(r'products-data\.js\?v=(\d+)')


def find_references():
    refs = {}  # path -> current version string
    for root, dirs, files in os.walk(REPO_ROOT):
        if '.git' in dirs:
            dirs.remove('.git')
        for f in files:
            if not f.endswith('.html'):
                continue
            p = os.path.join(root, f)
            try:
                s = open(p, encoding='utf-8').read()
            except Exception:
                continue
            m = PATTERN.search(s)
            if m:
                refs[p] = m.group(1)
    return refs


def main():
    refs = find_references()
    if not refs:
        print('No products-data.js?v=N references found.')
        return
    versions = set(refs.values())
    if len(versions) > 1:
        print('WARNING: inconsistent versions found across files:', sorted(versions))
        print('Aborting to avoid partial bump. Please normalize first.')
        sys.exit(1)
    current = sorted(versions)[0]
    nxt = str(int(current) + 1)
    if '--check' in sys.argv:
        print(f'Current products-data.js version: v={current}  (referenced in {len(refs)} HTML files)')
        return
    old = f'products-data.js?v={current}'
    new = f'products-data.js?v={nxt}'
    changed = 0
    for p in refs:
        s = open(p, encoding='utf-8').read()
        if old in s:
            s = s.replace(old, new)
            open(p, 'w', encoding='utf-8').write(s)
            changed += 1
    print(f'Bumped products-data.js v={current} -> v={nxt} in {changed} HTML files.')
    print('Remember to `git add` the changed HTML files and commit together with products-data.js.')


if __name__ == '__main__':
    main()
