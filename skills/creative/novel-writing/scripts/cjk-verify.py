#!/usr/bin/env python3
"""Batch CJK character counter for novel chapters.

Usage (from Hermes execute_code):
    exec(open('/home/lwq/.hermes/skills/creative/novel-writing/scripts/cjk-verify.py').read())

Or imported:
    from cjk_verify import verify_directory
    verify_directory('/mnt/d/sideline/ai/novel/中土纪元/第一卷')
"""

import re
import os
import sys


def count_cjk(filepath):
    """Count CJK ideographs (U+4E00–U+9FFF) in a file. Returns int."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def verify_directory(directory, min_chars=2000):
    """Scan all .txt files in directory, report CJK counts.
    
    Returns (total_cjk, short_list) where short_list is [(filename, count, bytes), ...].
    """
    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    
    total_cjk = 0
    short_chapters = []
    
    for fname in files:
        filepath = os.path.join(directory, fname)
        cjk = count_cjk(filepath)
        byt = os.path.getsize(filepath)
        total_cjk += cjk
        
        status = '✅' if cjk >= min_chars else '❌'
        print(f'  {fname}: {cjk}字 ({byt}B) {status}')
        
        if cjk < min_chars:
            short_chapters.append((fname, cjk, byt))
    
    print(f'\n  Total: {total_cjk} CJK chars across {len(files)} files')
    
    if short_chapters:
        print(f'  ⚠️ {len(short_chapters)} chapters below {min_chars}字 threshold:')
        for fname, cjk, byt in short_chapters:
            print(f'    {fname}: {cjk}字 (need {min_chars - cjk} more, {byt}B)')
    else:
        print(f'  ✅ All {len(files)} chapters >= {min_chars}字')
    
    return total_cjk, short_chapters


def verify_arc(directory, arc_start, arc_end, min_chars=2000):
    """Scan chapters within a specific arc range (e.g., 011-020)."""
    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    
    total_cjk = 0
    count = 0
    short_chapters = []
    
    for fname in files:
        m = re.search(r'第(\d+)章', fname)
        if not m:
            continue
        num = int(m.group(1))
        if arc_start <= num <= arc_end:
            filepath = os.path.join(directory, fname)
            cjk = count_cjk(filepath)
            total_cjk += cjk
            count += 1
            status = '✅' if cjk >= min_chars else '❌'
            print(f'  {fname}: {cjk}字 {status}')
            if cjk < min_chars:
                short_chapters.append((fname, cjk))
    
    print(f'\n  Arc {arc_start:03d}-{arc_end:03d}: {total_cjk}字 ({count} chapters)')
    if short_chapters:
        print(f'  ⚠️ {len(short_chapters)} short chapters')
        for fname, cjk in short_chapters:
            print(f'    {fname}: {cjk}字 (need {min_chars - cjk} more)')
    else:
        print(f'  ✅ All chapters >= {min_chars}字')
    
    return total_cjk, short_chapters


# Run as script when executed directly
if __name__ == '__main__' or 'cjk_verify' not in sys.modules:
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Default: scan current novel project
        target_dir = '/mnt/d/sideline/ai/novel/中土纪元/第一卷'
    
    if not os.path.isdir(target_dir):
        print(f'Directory not found: {target_dir}')
        print('Usage: python cjk-verify.py [directory_path]')
        sys.exit(1)
    
    print(f'=== CJK Verification: {target_dir} ===\n')
    verify_directory(target_dir)
