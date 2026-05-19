#!/usr/bin/env python3
"""Fix internal periods within paragraphs: replace all 。→，except the last one 
(or the one before closing quote). Applies to both dialogue and narrative paragraphs.

Usage: python3 scripts/fix-internal-periods.py <chapter_file> [--dry-run]

Rule: a paragraph is a complete semantic flow. Use commas (，) to connect clauses
within a paragraph. Periods (。) only at paragraph end (or before closing ").

Volume 1 validation: 8,603 internal periods → commas across 120 chapters.
"""

import os, re, sys


def fix_internal_periods(text):
    """Replace all 。with ，except the last one per paragraph (or before closing ")."""
    lines = text.split('\n')
    result = []

    for line in lines:
        s = line.strip()
        # Preserve special lines unchanged
        if not s or s.startswith('*第') or (s.startswith('第0') and '章' in s):
            result.append(line)
            continue

        # Find all 。positions
        periods = [m.start() for m in re.finditer('。', s)]
        if len(periods) <= 1:
            result.append(line)
            continue

        # Keep the rightmost 。that should be preserved:
        # Priority: 。before " at end, then 。at end of line
        chars = list(s)
        keep_idx = None
        for p_idx in reversed(periods):
            after = s[p_idx+1:].strip()
            if not after or (after.startswith('"') and len(after) <= 2):
                keep_idx = p_idx
                break

        if keep_idx is None:
            keep_idx = periods[-1]  # fallback: keep last

        # Replace all other 。with ，
        for p_idx in periods:
            if p_idx != keep_idx:
                chars[p_idx] = '，'

        result.append(''.join(chars))

    return '\n'.join(result)


def verify(text):
    """Return (paragraph_count, multi_period_count, cjk_count)."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    paras = [l for l in lines if not l.startswith('*第') and not l.strip().startswith('第0')]
    multi = sum(1 for p in paras if p.count('。') > 1)
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    return len(paras), multi, cjk


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fix-internal-periods.py <chapter_file> [--dry-run]")
        sys.exit(1)

    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    before_paras, before_multi, before_cjk = verify(original)

    if before_multi == 0:
        print(f"✅ {os.path.basename(path)}: already clean ({before_paras} paragraphs, {before_cjk} CJK)")
        sys.exit(0)

    fixed = fix_internal_periods(original)
    after_paras, after_multi, after_cjk = verify(fixed)

    if dry_run:
        print(f"🔍 {os.path.basename(path)}: {before_multi}→{after_multi} multi-period paragraphs")
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"✅ {os.path.basename(path)}: {before_multi}→0 multi-period paragraphs ({before_cjk} CJK unchanged)")

    if after_multi > 0:
        print(f"⚠️  WARNING: {after_multi} multi-period paragraphs remain — manual fix needed")
        sys.exit(1)
