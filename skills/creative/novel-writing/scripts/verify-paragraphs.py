#!/usr/bin/env python3
"""Paragraph segmentation verification for novel chapters.
Checks: paragraph count, CJK word count, dialogue splits, multi-period paragraphs, em dashes.
Usage: python3 scripts/verify-paragraphs.py /path/to/volume/
"""

import os, re, sys

def verify_chapter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    body = [l.strip() for l in text.split('\n') 
            if l.strip() and not l.startswith('*第') and not l.strip().startswith('第0')]
    
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    splits = sum(1 for p in body if p.count('"') % 2 != 0)
    multi_period = sum(1 for p in body if p.count('。') > 1)
    dashes = text.count('——')
    
    issues = []
    if cjk < 2000: issues.append(f"CJK={cjk}")
    if splits > 0: issues.append(f"裂引号={splits}")
    if multi_period > 0: issues.append(f"多句号段={multi_period}")
    if dashes > 0: issues.append(f"破折号={dashes}")
    
    return len(body), cjk, issues

if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else '.'
    files = sorted([f for f in os.listdir(base) if f.endswith('.txt')])
    
    ttl_p = ttl_c = 0
    failed = []
    
    print(f"{'章节':35s} {'段':>4s} {'CJK':>5s} {'状态'}")
    print("-" * 60)
    
    for f in files:
        path = os.path.join(base, f)
        paras, cjk, issues = verify_chapter(path)
        ttl_p += paras; ttl_c += cjk
        
        status = '✅' if not issues else f"⚠️ {','.join(issues)}"
        if issues: failed.append(f)
        print(f"{f[:35]:35s} {paras:4d} {cjk:5d} {status}")
    
    print(f"\n{'总计':35s} {ttl_p:4d} {ttl_c:5d}")
    print(f"均{ttl_p/len(files):.0f}段/章 | CJK均{ttl_c/len(files):.0f}")
    
    if failed:
        print(f"\n⚠️ {len(failed)}章有问题")
    else:
        print(f"\n🎉 {len(files)}章全部通过")
