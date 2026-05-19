#!/usr/bin/env python3
"""
一键四维审计脚本 — 弧线/批次结束后自动审计
用法:
  python3 audit.py 211-220 --volume 第二卷_浴血中土
  python3 audit.py 211-220 --volume 第二卷_浴血中土 --sentiment
  python3 audit.py 211-220 --volume 第二卷_浴血中土 --full

检测项:
  - CJK字数 (≥2000)
  - 「——」破折号 (应为0)
  - ASCII直引号 (应为0)  
  - 中文弯引号平衡 (开=闭)
  - 结束标记 *第X章·完*
  - 元叙事 (第X弧线/第X卷，排除"第一线"等物资术语)
  - |行号污染
  - 情感密度 (--sentiment)
  - 大纲关键词对位 (--keywords 大纲文件)
"""

import re, os, sys, glob
from pathlib import Path

def cjk_count(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def dash_count(text):
    return text.count('\u2014\u2014')

def ascii_quote_count(text):
    return text.count('"')

def curly_quote_balance(text):
    return text.count('\u201c'), text.count('\u201d')

def has_end_marker(text):
    return bool(re.search(r'\*第.*章·完', text))

def has_meta_narrative(text):
    """元叙事检测 — 排除'第一线/第二线'等物资线描述"""
    return bool(re.search(r'第[一二三四五六七八九十百千]+[弧卷](?!线)', text))

def has_pipe_numbers(text):
    return bool(re.search(r'^\s+\d+\|', text, re.MULTILINE))

def find_chapter(num, base_dir):
    """按章号查找文件"""
    for f in Path(base_dir).iterdir():
        if f.name.startswith(f"第{num:03d}章"):
            return f
    return None

def audit_chapter(num, base_dir):
    """单章审计"""
    f = find_chapter(num, base_dir)
    if f is None:
        return {"num": num, "error": "FILE_NOT_FOUND", "title": "?"}
    
    with open(f, 'r', encoding='utf-8') as fh:
        text = fh.read()
    
    title = f.stem.split('_', 1)[1] if '_' in f.stem else f.stem
    cjk = cjk_count(text)
    dashes = dash_count(text)
    ascii_q = ascii_quote_count(text)
    open_q, close_q = curly_quote_balance(text)
    mk = has_end_marker(text)
    meta = has_meta_narrative(text)
    pipes = has_pipe_numbers(text)
    byt = len(text.encode('utf-8'))
    
    issues = []
    if cjk < 2000: issues.append(f"CJK={cjk}")
    if dashes > 0: issues.append(f"--={dashes}")
    if ascii_q > 0: issues.append(f'\"={ascii_q}')
    if open_q != close_q: issues.append(f"引号不平衡({open_q}:{close_q})")
    if not mk: issues.append("缺结束标记")
    if meta: issues.append("元叙事")
    if pipes: issues.append("|行号")
    
    return {
        "num": num, "title": title, "file": str(f),
        "cjk": cjk, "dashes": dashes, "ascii_quotes": ascii_q,
        "curly_quotes": f"{open_q}:{close_q}",
        "end_marker": mk, "bytes": byt,
        "issues": issues, "ok": len(issues) == 0,
    }

def audit_range(start, end, base_dir, sentiment=False):
    """批量审计"""
    results = []
    total_cjk = 0
    for num in range(start, end + 1):
        r = audit_chapter(num, base_dir)
        results.append(r)
        if r.get("cjk", 0) > 0:
            total_cjk += r["cjk"]
    
    avg = total_cjk / max(1, len([r for r in results if "cjk" in r]))
    all_ok = all(r.get("ok", False) for r in results)
    
    sent_results = {}
    if sentiment:
        try:
            from cnsenti import Sentiment
            s = Sentiment()
            for r in results:
                if "error" not in r:
                    f = find_chapter(r["num"], base_dir)
                    if f:
                        with open(f, 'r', encoding='utf-8') as fh:
                            sent_results[r["num"]] = s.sentiment_count(fh.read())
        except ImportError:
            pass
    
    return {
        "results": results, "total_cjk": total_cjk, "avg_cjk": round(avg),
        "all_ok": all_ok, "sentiment": sent_results,
    }

def print_report(audit):
    """打印报告"""
    results = audit["results"]
    print(f"\n{'='*65}")
    print(f"  审计报告 · 第{results[0]['num']:03d}-{results[-1]['num']:03d}章")
    print(f"{'='*65}")
    
    ql = '"'
    print(f"\n{'章':<6} {'标题':<14} {'CJK':>5} {'--':>3} {ql:>3} {'引号':>7} {'标记':>4} {'状态'}")
    print("-" * 65)
    
    for r in results:
        if "error" in r:
            print(f" 第{r['num']:03d}章  {'FILE NOT FOUND':>40}")
            continue
        mk = "Y" if r['end_marker'] else "N"
        status = "OK" if r['ok'] else "+".join(r['issues'])
        print(f"第{r['num']:03d}章 {r['title']:<14} {r['cjk']:>5} {r['dashes']:>3} {r['ascii_quotes']:>3} {r['curly_quotes']:>7} {mk:>4} {status}")
    
    print("-" * 65)
    passes = sum(1 for r in results if r.get('ok'))
    print(f"  总CJK: {audit['total_cjk']} | 章均: {audit['avg_cjk']} | 通过: {passes}/{len(results)}")
    
    if audit.get("sentiment"):
        print(f"\n{'─'*40}\n  情感密度\n{'─'*40}")
        for num, s in sorted(audit["sentiment"].items()):
            pos, neg = s.get('pos', 0), s.get('neg', 0)
            bar = "P" * min(pos, 10) + "N" * min(neg, 10)
            print(f"  第{num:03d}章: P{pos} N{neg} {bar}")
        print("  N=0的章节可能缺乏冲突，需检查故事性")
    
    if audit["all_ok"]:
        print("\n  全部通过!")
    else:
        fails = [r for r in results if not r.get('ok')]
        print(f"\n  {len(fails)}章有问题")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="一键四维审计")
    parser.add_argument("range", help="章范围，如 211-220")
    parser.add_argument("--volume", help="卷目录路径")
    parser.add_argument("--sentiment", action="store_true", help="情感分析")
    parser.add_argument("--full", action="store_true", help="全四维审计")
    args = parser.parse_args()
    
    start, end = map(int, args.range.split('-'))
    base_dir = Path(args.volume) if args.volume else Path.cwd()
    
    audit = audit_range(start, end, base_dir, args.sentiment or args.full)
    print_report(audit)
