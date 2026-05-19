# Full-Volume Audit (全卷审核)

## Default: Serial Chapter-by-Chapter Audit

**For this user, serial (串行) checking is the default.** Do NOT use parallel sub-agents unless the user explicitly asks for speed.

### Serial Audit Workflow

1. Set up a 12-item todo list (001-010, 011-020, … 111-120)
2. For each block of 10 chapters, run a Python script that checks EVERY chapter:
   - Title format: `^第\d+章\s+\S` (line 3 must be intact)
   - Meta-narrative: `第\d+章` in content (SKIP line 3 — only check lines 4+)
   - Format artifacts: `^\s+\d+\|` line numbers, `\和\` patterns
   - Word count: ≥ 2000 Chinese characters (use `[\u4e00-\u9fff\u3400-\u4dbf]`)
3. Print one line per chapter: `filename: XXXX字 ✅/❌`
4. For ❌ chapters, print the specific issue
5. Report to user: "011-020章：全部通过 ✅"
6. Continue to next block
7. Only BEGIN FIXING after ALL 120 chapters are scanned

### Serial Audit Script Template

```python
import re, os, glob

base = "/mnt/d/sideline/ai/novel/{书名}/{卷名}"

for i in range(start, end+1):
    fname = f"第{i:03d}章_*.txt"
    matches = glob.glob(os.path.join(base, fname))
    fpath = matches[0]
    with open(fpath, 'r') as f:
        text = f.read()
        lines = text.split('\n')
    
    issues = []
    # Title check (line 3)
    title = lines[2].strip() if len(lines) > 2 else ""
    if not re.match(r'^第\d+章\s+\S', title):
        issues.append(f"标题异常:{title[:30]}")
    
    # Meta-narrative in content (lines 4+)
    meta = []
    for j, line in enumerate(lines):
        if j <= 2: continue
        if re.findall(r'第\d+章', line):
            meta.append(j+1)
    if meta:
        issues.append(f"元叙事残留:行{meta}")
    
    # Format artifacts
    if re.search(r'^\s+\d+\|', text, re.MULTILINE):
        issues.append("含|行号")
    if '\\和\\' in text:
        issues.append("含\\和\\")
    
    # Word count
    cn = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    
    st = "✅" if not issues else "❌"
    print(f"{os.path.basename(fpath)}: {cn}字 {st}")
    for iss in issues:
        print(f"  ⚠️ {iss}")
```

## Alternative: Parallel Sub-Agent Audit

Only use this when the user explicitly requests speed or confirms parallel is OK.

Split volume into 3 equal ranges (e.g., 001-040, 041-080, 081-120) and dispatch `delegate_task` calls simultaneously. Aggregate into a priority-ranked issue list.

See the original pattern below.

## Per-Chapter Audit Checklist

Each chapter is checked for:
1. Word count ≥ 2000
2. Content matches outline event description
3. Logical continuity with adjacent chapters
4. Setting compliance (无系统/超能力, 灵械术 consistency, 灵晶等级)
5. No "/，" artifacts, no isolated numbers, no duplicate paragraphs
6. No meta-narrative breaking 4th wall (e.g., "第一卷第033章终", "第X章")
7. No time references contradicting the outline timeline
8. Chapter titles match outline
9. No `|` line number artifacts
10. No `\和\` patterns

## Issue Priority

- Red: timeline contradictions, outline misalignment, setting violations
- Yellow: missing word count, title mismatches, 4th-wall breaks, format artifacts
- Green: style choices, optional improvements
