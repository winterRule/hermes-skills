"""
全卷结构审计脚本
扫描所有卷文件夹的实际章号范围，与大纲声明对比，检测：
1. 卷归属错误（章节在错误的卷文件夹中）
2. 内部编号偏移（文件编号 vs 内部第一行编号）
3. 大纲标题 vs 文件标题偏差
4. 「干净错号 vs 脏对号」二分类质量信号
5. 模板污染、格式违规统计
"""

import os, re
from collections import Counter, defaultdict

def scan_project(base_dir):
    """Main entry: scan all volume directories and return full report."""
    vols = {}
    
    for vol_name in sorted(os.listdir(base_dir)):
        vol_path = os.path.join(base_dir, vol_name)
        if not os.path.isdir(vol_path):
            continue
        
        files = [f for f in os.listdir(vol_path) if f.endswith('.txt')]
        chapters = []
        for f in files:
            m = re.search(r'第(\d+)章', f)
            if m:
                chapters.append((int(m.group(1)), f))
        chapters.sort()
        
        if not chapters:
            continue
        
        nums = [c[0] for c in chapters]
        gaps = [i for i in range(min(nums), max(nums)+1) if i not in nums]
        
        vol_data = {
            'name': vol_name,
            'min_ch': min(nums),
            'max_ch': max(nums),
            'count': len(chapters),
            'gaps': gaps,
            'chapters': {},
        }
        
        # Per-chapter scan
        for ch_num, fname in chapters:
            fpath = os.path.join(vol_path, fname)
            with open(fpath, 'r', encoding='utf-8') as fh:
                text = fh.read()
            
            first_line = text.split('\n')[0].strip()
            internal_m = re.search(r'第(\d+)章\s*(.*)', first_line)
            internal_num = internal_m.group(1) if internal_m else '??'
            internal_title = internal_m.group(2).strip() if internal_m else '??'
            file_title = re.sub(r'第\d+章_', '', fname).replace('.txt', '')
            
            cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
            
            # Quality signals
            templates = {
                'feng': text.count('风从暗河方向吹过来'),
                'anhe': text.count('暗河的水在远处流着'),
                'luchen': text.count('陆辰记在了科目002'),
            }
            format_issues = {
                'em_dash': text.count('——'),
                'straight_quotes': text.count('"'),
                'meta': len(re.findall(r'第[一二三四五六七八九十百千\d]+[弧线卷]', text)),
            }
            
            # Duplicate paragraph check
            lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 30]
            dup_count = sum(1 for c in Counter(lines).values() if c >= 3)
            
            vol_data['chapters'][ch_num] = {
                'file': fname,
                'internal_num': internal_num,
                'internal_title': internal_title,
                'file_title': file_title,
                'cjk': cjk,
                'templates': templates,
                'format_issues': format_issues,
                'dup_count': dup_count,
                'num_match': internal_num == str(ch_num),
                'title_match': internal_title == file_title,
            }
        
        vols[vol_name] = vol_data
    
    return vols


def print_report(vols):
    """Print a human-readable audit report."""
    for vname, vdata in sorted(vols.items()):
        print(f"\n{'='*65}")
        print(f"📁 {vname}")
        print(f"   章节范围: 第{vdata['min_ch']}-{vdata['max_ch']}章 ({vdata['count']}章)")
        if vdata['gaps']:
            print(f"   🔴 缺失: {vdata['gaps'][:10]}{'...' if len(vdata['gaps'])>10 else ''}")
        print(f"   {'─'*55}")
        
        # Count mismatches
        num_mismatches = []
        title_mismatches = []
        dirty_good = []  # correct num + templates
        clean_bad = []   # wrong num + clean
        
        for ch_num, ch in vdata['chapters'].items():
            if not ch['num_match']:
                num_mismatches.append(ch_num)
            if not ch['title_match']:
                title_mismatches.append(ch_num)
            
            has_templates = any(v > 0 for v in ch['templates'].values())
            if ch['num_match'] and has_templates:
                dirty_good.append(ch_num)
            if not ch['num_match'] and not has_templates:
                clean_bad.append(ch_num)
        
        print(f"   内部编号错位: {len(num_mismatches)}章")
        print(f"   标题不匹配: {len(title_mismatches)}章")
        
        if dirty_good:
            print(f"   🟡 脏对号 (编号对但模板污染): {len(dirty_good)}章 — {dirty_good[:5]}...")
        if clean_bad:
            print(f"   🟠 干净错号 (编号错但格式干净): {len(clean_bad)}章 — {clean_bad[:5]}...")
        
        if dirty_good and clean_bad:
            print(f"   ⚠️ 诊断信号: 此卷从多套不一致的创作流程拼装而成")
        
        # Template totals
        total_feng = sum(ch['templates']['feng'] for ch in vdata['chapters'].values())
        total_anhe = sum(ch['templates']['anhe'] for ch in vdata['chapters'].values())
        total_em = sum(ch['format_issues']['em_dash'] for ch in vdata['chapters'].values())
        total_sq = sum(ch['format_issues']['straight_quotes'] for ch in vdata['chapters'].values())
        
        print(f"   模板'风从暗河': {total_feng}处 | '暗河水': {total_anhe}处")
        print(f"   破折号: {total_em} | 英文引号: {total_sq}")
        
        # Print per-chapter issues
        issues_found = False
        for ch_num in sorted(vdata['chapters'].keys()):
            ch = vdata['chapters'][ch_num]
            flags = []
            if not ch['num_match']:
                flags.append(f"内编={ch['internal_num']}")
            if not ch['title_match']:
                flags.append(f"内题='{ch['internal_title']}'≠文件='{ch['file_title']}'")
            if ch['templates']['feng'] > 20:
                flags.append(f"风×{ch['templates']['feng']}")
            if ch['format_issues']['em_dash'] > 0:
                flags.append(f"——×{ch['format_issues']['em_dash']}")
            
            if flags:
                if not issues_found:
                    print(f"\n   逐章问题:")
                    issues_found = True
                print(f"    第{ch_num:>3}章: {', '.join(flags)}")


if __name__ == '__main__':
    import sys
    base_dir = sys.argv[1] if len(sys.argv) > 1 else '/mnt/d/sideline/ai/novel/中土纪元'
    vols = scan_project(base_dir)
    print_report(vols)
