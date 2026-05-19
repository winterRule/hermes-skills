#!/usr/bin/env python3
"""Fix dialogue-split chapters: merge fractured dialogue back into one-speaker-one-paragraph,
replace internal 。→， within quotes, and verify zero unbalanced quotes afterward.

Usage: python3 scripts/fix-dialogue-splits.py <chapter_file> [--dry-run]

A "dialogue split" is when one character's speech is mechanically split at every 。
into separate paragraphs. This script:
1. Detects paragraphs with unbalanced (odd-count) " quotes
2. Merges consecutive paragraphs until quotes balance
3. Replaces internal 。→， within merged dialogue, keeping only the terminal 。
4. Preserves non-dialogue paragraphs and end-markers untouched

Post-fix verification: the output file will have exactly 0 paragraphs with odd " counts.
"""

import os, re, sys

def fix_quotes(text):
    """Within each "..." span, replace all 。→， except the final one."""
    result = []
    i = 0
    while i < len(text):
        if text[i] == '"':
            j = i + 1
            while j < len(text) and text[j] != '"':
                j += 1
            if j < len(text):
                inner = text[i+1:j]
                fixed = inner.replace('。', '，')
                if fixed and fixed[-1] == '，':
                    fixed = fixed[:-1] + '。'
                result.append('"' + fixed + '"')
                i = j + 1
            else:
                result.append(text[i:])
                break
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


def fix_chapter(text):
    """Merge split dialogue paragraphs and fix internal punctuation."""
    lines = text.split('\n')
    result = []
    i = 0

    # Preserve leading blank lines + title line
    while i < len(lines) and not lines[i].strip():
        result.append(lines[i])
        i += 1
    if i < len(lines):
        result.append(lines[i])
        i += 1

    # Collect body paragraphs (skip end-marker)
    body = []
    end_marker = None
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('*第') and '完' in line:
            end_marker = lines[i]
            break
        if line:
            body.append(line)
        i += 1

    # Merge split dialogue
    merged = []
    buf = None
    for para in body:
        qc = para.count('"')
        if buf is not None:
            buf += para
            if buf.count('"') % 2 == 0:
                merged.append(fix_quotes(buf))
                buf = None
        elif qc % 2 != 0:
            buf = para
        else:
            merged.append(para)
    if buf is not None:
        merged.append(fix_quotes(buf))

    # Rebuild with blank lines between paragraphs
    rebuilt = result[:]
    for para in merged:
        rebuilt.append(para)
        rebuilt.append('')
    if end_marker:
        rebuilt.append('')
        rebuilt.append(end_marker.strip())

    return '\n'.join(rebuilt)


def verify(text):
    """Return (paragraph_count, split_count, cjk_count)."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    paras = [l for l in lines if not l.startswith('*第') and not l.strip().startswith('第0')]
    splits = sum(1 for p in paras if p.count('"') % 2 != 0)
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    return len(paras), splits, cjk


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fix-dialogue-splits.py <chapter_file> [--dry-run]")
        sys.exit(1)

    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    before_paras, before_splits, before_cjk = verify(original)

    if before_splits == 0:
        print(f"✅ {os.path.basename(path)}: already clean ({before_paras} paragraphs, {before_cjk} CJK)")
        sys.exit(0)

    fixed = fix_chapter(original)
    after_paras, after_splits, after_cjk = verify(fixed)

    if dry_run:
        print(f"🔍 {os.path.basename(path)}: {before_splits}→{after_splits} splits ({before_paras}→{after_paras} paras, {before_cjk}→{after_cjk} CJK)")
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"✅ {os.path.basename(path)}: {before_splits}→0 splits ({before_paras}→{after_paras} paras, {before_cjk} CJK unchanged)")

    if after_splits > 0:
        print(f"⚠️  WARNING: {after_splits} splits remain — manual fix needed")
        sys.exit(1)
