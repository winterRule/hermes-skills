# Arc Full-Scan Audit Script (Python, reusable)
# PURPOSE: Single-pass check of internal numbering, internal titles, formatting,
#   CJK word count, duplicate paragraphs, and template/repetitive-ending detection.
#   Designed to catch the internal-number/title drift that affected 7/20 chapters in Arc 8.
# USAGE: Set base_dir to the arc's directory, adjust expected_chapter_range, run in execute_code.

import os, re
from collections import Counter

base_dir = "/mnt/d/sideline/ai/novel/中土纪元/第二卷_浴血中土"
expected_chapter_range = range(181, 201)  # Adjust per arc

# Collect files matching expected chapter range
files = []
for ch_num in expected_chapter_range:
    pattern = f"第{ch_num:03d}章_" if ch_num < 1000 else f"第{ch_num}章_"
    matches = [f for f in os.listdir(base_dir) if f.startswith(pattern) and f.endswith('.txt')]
    if matches:
        files.append((ch_num, matches[0]))
    else:
        print(f"⚠️ Chapter {ch_num}: file not found")

files.sort(key=lambda x: x[0])

# Template patterns for repetitive-ending detection
templates = [
    "这件事情后来被陆辰记在了科目002",
    "暗河的水在远处流着",
    "风从暗河方向吹过来",
    "苏大姐在磨盘前翻看科目002更新的时候说了一句话"
]

results = []
title_mismatches = []
internal_number_mismatches = []
duplicate_paragraphs = []
template_chapters = []

for ch_num, fname in files:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    
    text = ''.join(lines)
    
    # --- 1. Internal chapter number check ---
    first_line = lines[0].strip() if lines else ''
    internal_match = re.search(r'第(\d+)章', first_line)
    internal_num = internal_match.group(1) if internal_match else 'NOT_FOUND'
    num_ok = (internal_num == str(ch_num))
    if not num_ok:
        internal_number_mismatches.append((ch_num, fname, internal_num, first_line[:80]))
    
    # --- 2. Internal title check ---
    file_title = re.sub(r'第\d+章_', '', fname).replace('.txt', '')
    internal_title = re.sub(r'第\d+章\s*', '', first_line)
    title_ok = (file_title == internal_title)
    if not title_ok:
        title_mismatches.append((ch_num, fname, file_title, internal_title))
    
    # --- 3. CJK word count ---
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # --- 4. Em-dash count ---
    em_dash = text.count('——')
    
    # --- 5. English straight-quote count ---
    # Count " characters (not the curly Chinese ones)
    straight_quotes = text.count('"')  # U+0022
    
    # --- 6. Meta-narrative references ---
    meta = len(re.findall(r'第[一二三四五六七八九十百千\d]+[弧线卷]', text))
    
    # --- 7. Template pattern detection ---
    t_counts = {t: text.count(t) for t in templates}
    has_templates = any(c > 0 for c in t_counts.values())
    if has_templates:
        template_chapters.append((ch_num, fname, {k: v for k, v in t_counts.items() if v > 0}))
    
    # --- 8. Duplicate paragraph detection ---
    long_lines = [l.strip() for l in lines if len(l.strip()) > 20]
    line_counts = Counter(long_lines)
    dupes = [(line, count) for line, count in line_counts.items() if count >= 3]
    if dupes:
        duplicate_paragraphs.append((ch_num, fname, dupes[:2]))
    
    results.append({
        'ch_num': ch_num,
        'fname': fname,
        'internal_num': internal_num,
        'num_ok': num_ok,
        'title_ok': title_ok,
        'cjk': cjk,
        'em_dash': em_dash,
        'straight_quotes': straight_quotes,
        'meta': meta,
        'has_templates': has_templates,
        'dupe_count': len(dupes)
    })

# --- REPORT ---
print("=" * 80)
print("PHASE 1: STRUCTURE + FORMAT SCAN")
print(f"{'章':>4} {'文件':<30} {'CJK':>6} {'破折号':>4} {'引号':>4} {'元叙事':>4} {'模板':>4} {'重复段':>4}")
print("-" * 80)

all_pass = True
for r in results:
    flags = []
    if r['em_dash'] > 0: flags.append('D')
    if r['straight_quotes'] > 0: flags.append('Q')
    if r['meta'] > 0: flags.append('M')
    if r['has_templates']: flags.append('T')
    if r['dupe_count'] > 0: flags.append('R')
    if r['cjk'] < 2000: flags.append('C')
    if not r['num_ok']: flags.append('#')
    if not r['title_ok']: flags.append('Tt')
    
    flag_str = ','.join(flags) if flags else '✅'
    if flags: all_pass = False
    
    print(f"{r['ch_num']:>4} {r['fname']:<30} {r['cjk']:>6} {r['em_dash']:>4} {r['straight_quotes']:>4} {r['meta']:>4} {'T' if r['has_templates'] else '':>4} {r['dupe_count']:>4}  {flag_str}")

total_cjk = sum(r['cjk'] for r in results)
print("-" * 80)
print(f"总计 CJK: {total_cjk}, 章均: {total_cjk // len(results)}")

# --- INTERNAL NUMBERING ISSUES ---
if internal_number_mismatches:
    print(f"\n🔴 INTERNAL NUMBER MISMATCH ({len(internal_number_mismatches)} chapters):")
    for ch_num, fname, got, line in internal_number_mismatches:
        print(f"  第{ch_num}章 {fname}: expected 「第{ch_num}章」, got 「第{got}章」")

# --- TITLE MISMATCHES ---
if title_mismatches:
    print(f"\n🔴 TITLE MISMATCH ({len(title_mismatches)} chapters):")
    for ch_num, fname, file_title, internal_title in title_mismatches:
        print(f"  第{ch_num}章 {fname}")
        print(f"    File title: {file_title}")
        print(f"    Internal title: {internal_title}")

# --- DUPLICATE PARAGRAPHS ---
if duplicate_paragraphs:
    print(f"\n🔴 DUPLICATE PARAGRAPHS ({len(duplicate_paragraphs)} chapters):")
    for ch_num, fname, dupes in duplicate_paragraphs:
        print(f"  第{ch_num}章 {fname}:")
        for line, count in dupes:
            print(f"    ×{count}: {line[:60]}...")

# --- TEMPLATE PATTERNS ---
if template_chapters:
    print(f"\n⚠️ TEMPLATE PATTERNS ({len(template_chapters)} chapters):")
    for ch_num, fname, counts in template_chapters:
        print(f"  第{ch_num}章 {fname}: {counts}")

# --- FINAL VERDICT ---
print(f"\n{'=' * 80}")
if all_pass:
    print("✅ ALL CHAPTERS CLEAN — zero format issues, all internal numbers match")
else:
    print("🔴 ISSUES FOUND — see details above")
print(f"CJK total: {total_cjk}, avg: {total_cjk // len(results)}")
