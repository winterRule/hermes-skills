# Em-Dash (——) Removal Technique

## When to Use
When chapters have excessive `——` (em dash) usage — user's threshold is under 2.0 per 100 CJK, ideally under 1.0.

## Severity Levels
- 0-2/百字: Acceptable (Volume 1 baseline)
- 2-5/百字: Needs reduction (Volumes 2 mid-range)
- 5-10+/百字: CRITICAL — full rewrite or aggressive batch replacement (Volume 3 unfixed)

## Batch Replacement Script

This Python script processes all chapters in a volume, replacing excessive `——` with appropriate Chinese punctuation. It handles three cases:

```python
import re, glob, os

base = "/mnt/d/sideline/ai/novel/中土纪元/第三卷"
chapters = sorted(glob.glob(f"{base}/第*.txt"))

for ch in chapters:
    fname = os.path.basename(ch)
    with open(ch, 'r', encoding='utf-8') as f:
        text = f.read()
    
    before_count = text.count('——')
    if before_count < 15:
        continue  # Skip chapters with acceptable usage
    
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # Preserve title and end markers unchanged
        if line.strip().startswith('第') and '章' in line and not any(c in line for c in ['*','「','」','：','的']):
            new_lines.append(line)
            continue
        if line.strip().startswith('*第') and '完' in line:
            new_lines.append(line)
            continue
        if not line.strip():
            new_lines.append(line)
            continue
        
        processed = line
        
        # Rule 1: "不是X——是Y" → "不是X，是Y"
        processed = re.sub(r'不是([^—]{1,30})——是', r'不是\1，是', processed)
        
        parts = processed.split('——')
        
        if len(parts) >= 4:
            # Heavy chain: break into sentences
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
    
    new_text = '\n'.join(new_lines)
    after_count = new_text.count('——')
    
    if after_count < before_count:
        with open(ch, 'w', encoding='utf-8') as f:
            f.write(new_text)
    
    print(f"{fname}: {before_count} → {after_count}")
```

## Manual Rewrite (for worst offenders)

When a chapter has 200+ dashes (like 138章 with 249, 139章 with 238), the batch script cannot produce natural prose. These chapters need full manual rewrite:

1. Read the chapter and understand all scenes, characters, actions, and key dialogue
2. Rewrite the entire chapter from scratch keeping all content
3. Use `。，：` for normal prose; keep 3-6 `——` maximum for dramatic pauses only
4. Verify CJK count after rewrite

## Verification

After any fix, run:
```python
import re
with open(chapter_path, 'r', encoding='utf-8') as f:
    text = f.read()
cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
dash_count = text.count('——')
freq = round(dash_count / (cjk/100), 1)
print(f"——: {dash_count} | CJK: {cjk} | {freq}/百字")
```

Target: freq ≤ 2.0/百字 (ideally ≤ 1.0)
