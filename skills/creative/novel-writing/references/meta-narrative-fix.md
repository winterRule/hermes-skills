# Meta-Narrative Fix: Removing "第X章" from Story Content

## Problem

Characters and narration should NOT reference chapter numbers. "第X章" references in story content are 4th-wall breaks that destroy immersion. A single novel can accumulate 72+ instances across 26+ files.

## Common Patterns

| Pattern | Example | Fix |
|---------|---------|-----|
| "第001章" as starting point | "从第001章到现在" | "从东海郡到现在" / "从最初到现在" |
| "第120章" as ending | "第120章——待明天" | "最后一页——待明天" / "明天" |
| Log entry titles | "第093章——江寒" | "江寒。第四道划痕..." |
| Chapter ranges | "第081-090章——前夜" | "从北岭烟柱到隘口血战——前夜" |
| Time markers | "在第111章的清晨" | "这天清晨" |
| Notebook labels | "第108章岔路口" | "这个岔路口" |

## Fix Strategy (Python Script)

```python
import re

# 1. Fixed meanings (specific replacements first)
text = re.sub(r'第001章', '最初在东海郡', text)
text = re.sub(r'第004章', '第一次伏击那夜', text)
text = re.sub(r'第060章', '云泽那段日子', text)
text = re.sub(r'第120章', '明天', text)
# ... etc for each chapter with semantic meaning

# 2. Chapter ranges (spoken by characters)
text = re.sub(
    r'第081-090章——前夜。第091-110章——大撤退中的逆行。.',
    '从北岭烟柱到隘口血战——那是前夜。从大撤退到敌后破袭——那是逆行。.',
    text
)

# 3. "从第X章到第Y章" → time/event description
text = re.sub(r'从第\d+章到第\d+章', '这段时间', text)

# 4. "第X章——XXX" → keep description, drop chapter number
text = re.sub(r'第\d+章——', '', text)

# 5. Time markers
text = re.sub(r'在第\d+章的清晨', '这天清晨', text)
text = re.sub(r'在第\d+章的中途', '这天', text)

# 6. Cleanup any remaining standalone "第X章"
text = re.sub(r'第\d+章', '今天', text)

# 7. Deduplicate
text = re.sub(r'今天今天', '今天', text)
```

## CRITICAL: Restore Title Lines After Global Replacement

The global regex will corrupt chapter title lines (line 3). After the fix, restore titles:

```python
for fname in files:
    match = re.match(r'(第\d+章)_', fname)
    if match:
        chap_num = match.group(1)
        lines[2] = f"{chap_num} {original_title_text}\n"
```

## Pitfalls of Batch Replacement (2026-05-16 Session Lessons)

### 1. Range patterns survive simple regex
`re.sub(r'第\d+章', ...)` does NOT catch combined ranges like `"第001-120章"` or `"第081-090章"` because the dash separates the two chapter numbers. Use an additional pass:
```python
text = re.sub(r'第\d+-\d+章', '从最初到现在', text)  # catch ranges
```

### 2. `\"` escaped quotes break sed/patch
Files from earlier compaction may contain literal `\"` sequences. `patch` with unescaped `"` won't match. Use `sed` on the raw file:
```bash
sed -i 's/\"第081-090章——前夜。\"/\"前夜。\"/g' 第090章_从今天起.txt
```
Or use the exact text from `read_file` output (which may show `\"` as `\\"`).

### 3. Duplicated phrases from replacement collisions
When replacing e.g. `第081章` → `北岭第一次见烟柱那天`, lines already containing `北岭` get doubled: "从北岭第一次见烟柱那天北岭第一缕烟"。After all replacements, scan for duplication:
```bash
grep -nE '(最初在东海郡最初|云泽那段日子云泽|今天今天|明天明天|北岭.*北岭|老铁匠.*老铁匠)' *.txt
```

### 4. Final verification MUST use grep, not Python
Python `re.findall(r'第\d+章', text)` may miss patterns visible to `grep`. Always end with:
```bash
for f in 第*.txt; do
  result=$(grep -n '第[0-9]\+章' "$f" | grep -v '^3:' | grep -v '^1:')
  [ -n "$result" ] && echo "❌ $f: $result"
done
```
This excludes title line (line 3) and volume line (line 1).

## Session Data (2026-05-16, 第一卷120章)

### Round 1: Batch Python script
- Total instances found: **72** across **26** files
- Worst offenders: ch110 (8), ch120 (8), ch111 (7), ch107 (6), ch117 (6), ch100 (5)
- Script result: claimed 0 remaining, but **4 instances survived** (ranges not caught)

### Round 2: User flagged remaining issues
- ch090 L9: `"第081-090章——前夜。"` → `"前夜。"`
- ch100 L11: `"第001-100章。"` → `"从最初到现在——百页。"`
- ch106 L19: `"第三弧线收束——第107-110章。"` → `"第三弧线收束。"`
- ch106 L21: `"从北岭第一次见烟柱那天北岭第一缕烟"` (duplicate) → fixed
- ch111 L27: `"赤炬会的根——第001-120章。"` → `"赤炬会的根——从东海郡到隘口。"`
- ch117 L11: `"老铁匠磨扳手那天老铁匠"` (duplicate) → fixed
- ch117 L15: `"测绘本——第001-120章。"` → `"测绘本——从东海郡到隘口。"`
- ch117 L17: `"第118-120章——是全部人的收束"` → `"接下来的收束——是全部人的收束"`

### Round 3: Final verification
- Shell grep scan: **0** remaining in content across all 120 chapters
- Post-fix title verification: ch001, ch004 titles corrupted → manually repaired
- Duplicate phrase scan: 0 instances
