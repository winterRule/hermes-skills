# 「——」Em-Dash Overuse Fix

## Problem

The stream-of-consciousness prose style systematically defaults to `——` as the ONLY clause connector, producing chains like `X——Y——Z——W——` that degrade readability. At its worst (Volume 3, chapters 130-140), frequency reached 8-10 instances per 100 CJK characters — meaning every sentence contained at least one em-dash.

## Impact (measured 2026-05-17)

| Volume | Chapters | Before | After | Freq/百字 (before→after) |
|--------|----------|--------|-------|--------------------------|
| 第一卷 | 001-050 | 1,837 | 2 | 1.6→0.0 |
| 第二卷 | 051-120 | 4,365 | 0 | 2.7→0.0 |
| 第三卷 | 121-140 | 3,343 | 17 | 7.2→0.0 |
| **Total** | **140** | **9,545** | **19** | **99.8% reduction** |

Worst chapters pre-fix: 138章 (249个), 139章 (238个), 136章 (212个), 130章 (209个).

## Fix Rules (context-aware)

Apply these replacements in order per paragraph:

### Rule 1: `不是X——是Y` → `不是X，是Y`
```
不是进攻——是封锁 → 不是进攻，是封锁
不是堵——是存在 → 不是堵，是存在
```

### Rule 2: Multi-part chains (4+ segments)
Split on `——`, classify each segment:
- Short segments (len < 8) or starting with structural words (不是/但/而/却/就/才/还/也) → prepend `，`
- Segments starting with 是/在/用/从/因为 → prepend `，`
- All other segments → prepend `。`
- First segment: no prepend, last segment: prepend `。`

### Rule 3: Three-part chains
Same as Rule 2 but middle segment uses `，` if <10 chars, `。` otherwise.

### Rule 4: Two-part chains
- If second part starts with 是/在/用/从/因为 → `，`
- If second part is <6 chars → `：`
- Otherwise → `。`

### Rule 5: Keep dashes ONLY for
- Dramatic pauses in dialogue quotes
- Genuine emphasis ("是——收到了")
- At most 2-3 per chapter total

## Batch Fix Script

```python
import re, glob, os

def fix_em_dashes(text):
    """Replace excessive —— with proper Chinese punctuation."""
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # Preserve title and end markers
        if line.strip().startswith('第') and '章' in line and not any(c in line for c in ['*','「','」','：','的']):
            new_lines.append(line); continue
        if line.strip().startswith('*第') and '完' in line:
            new_lines.append(line); continue
        if not line.strip():
            new_lines.append(line); continue
        
        processed = line
        # Rule 1
        processed = re.sub(r'不是([^—]{1,30})——是', r'不是\1，是', processed)
        
        parts = processed.split('——')
        if len(parts) < 2:
            new_lines.append(processed); continue
        
        if len(parts) >= 4:
            result_parts = []
            for i, part in enumerate(parts):
                part = part.strip()
                if not part: continue
                if i == 0: result_parts.append(part)
                elif i < len(parts)-1:
                    if len(part) < 8 or re.match(r'^[不是但而却就才还也]', part):
                        result_parts.append('，' + part)
                    elif part.startswith(('是','在','用','从')):
                        result_parts.append('，' + part)
                    else:
                        result_parts.append('。' + part)
                else:
                    result_parts.append('。' + part)
            processed = ''.join(result_parts)
        elif len(parts) == 3:
            result_parts = []
            for i, part in enumerate(parts):
                part = part.strip()
                if not part: continue
                if i == 0: result_parts.append(part)
                elif i == 1: result_parts.append('，' + part if len(part) < 10 else '。' + part)
                else: result_parts.append('。' + part)
            processed = ''.join(result_parts)
        elif len(parts) == 2:
            p0, p1 = parts[0].strip(), parts[1].strip()
            if not p0 or not p1:
                processed = re.sub(r'——', '，', line, count=1)
            elif p1.startswith(('是','在','用','从','因为')):
                processed = p0 + '，' + p1
            else:
                processed = p0 + '。' + p1
        
        new_lines.append(processed)
    return '\n'.join(new_lines)

# Usage: process all chapters in a directory
base = "/path/to/novel/目录"
for vol in ["第一卷", "第二卷", "第三卷"]:
    for ch in sorted(glob.glob(f"{base}/{vol}/第*章*.txt")):
        with open(ch, 'r', encoding='utf-8') as f:
            text = f.read()
        before = text.count('——')
        if before < 10:
            continue  # Skip chapters already clean
        fixed = fix_em_dashes(text)
        after = fixed.count('——')
        if after < before:
            with open(ch, 'w', encoding='utf-8') as f:
                f.write(fixed)
```

## Verification After Fix

```python
import re, glob

# 1. Count remaining dashes per chapter
for ch in sorted(glob.glob(f"{base}/**/第*章*.txt", recursive=True)):
    with open(ch, 'r', encoding='utf-8') as f:
        text = f.read()
    content = '\n'.join([l for l in text.split('\n') if l.strip() and not l.startswith('*第')])
    dash = content.count('——')
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    if dash > 5:
        print(f"⚠️ {os.path.basename(ch)}: {dash}个—— | {cjk}字 | {round(dash/(cjk/100),1)}/百字")

# 2. Verify CJK ≥ 2000 for all chapters
for ch in sorted(glob.glob(f"{base}/**/第*章*.txt", recursive=True)):
    with open(ch, 'r', encoding='utf-8') as f:
        cjk = len(re.findall(r'[\u4e00-\u9fff]', f.read()))
    if cjk < 2000:
        print(f"❌ {os.path.basename(ch)}: {cjk} CJK字 — BELOW 2000")
```

## Prevention Rules for New Writing

1. After writing each batch of 3 chapters, run `content.count('——')` on each
2. Target: ≤5 per chapter (≤1 per 400 CJK characters)
3. If any chapter exceeds 5: rewrite the chapter replacing chains with 。，：
4. Manual rewrite produces better quality than batch regex for the worst chapters (>100 dashes)
5. The fix must never reduce CJK count — only change connectors
