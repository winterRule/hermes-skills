# Batch Paragraph Breaking (批量分段拆分)

## When to use

When existing chapters have fewer than 12 paragraphs and average paragraph length exceeds 150 CJK characters. This typically occurs in chapters written before the user enforced the multi-paragraph rule (2026-05-17) — Volumes 1-2 and parts of 3-4.

## Technique

Use `execute_code` with the `break_long_paragraph()` function. It splits long paragraphs at sentence boundaries (。！？) when they exceed a character threshold.

### Core function

```python
import re

def break_long_paragraph(text, max_chars=140):
    """Break paragraphs > max_chars at nearest sentence boundary."""
    lines = text.split('\n')
    result = []
    
    for line in lines:
        stripped = line.strip()
        # Skip empty lines, end markers, and title lines
        if not stripped or stripped.startswith('*') or stripped.startswith('第'):
            result.append(line)
            continue
        
        if len(stripped) <= max_chars:
            result.append(line)
            continue
        
        # Split at sentence boundaries (。！？)
        sentences = re.split(r'(?<=[。！？])', stripped)
        new_paras = []
        current = ''
        for sent in sentences:
            if len(current + sent) > max_chars and current:
                new_paras.append(current.strip())
                current = sent
            else:
                current += sent
        
        if current.strip():
            new_paras.append(current.strip())
        
        if len(new_paras) > 1:
            result.append('\n\n'.join(new_paras))
        else:
            result.append(line)
    
    return '\n'.join(result)
```

### Batch processing pattern

```python
import re, os

base = "/mnt/d/sideline/ai/novel/中土纪元/第二卷/"

for fname in sorted(os.listdir(base)):
    if not fname.endswith('.txt'):
        continue
    
    fpath = os.path.join(base, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    modified = break_long_paragraph(original, max_chars=140)
    
    orig_paras = len([l for l in original.split('\n') 
        if l.strip() and not l.strip().startswith('*') and not l.strip().startswith('第')])
    mod_paras = len([l for l in modified.split('\n') 
        if l.strip() and not l.strip().startswith('*') and not l.strip().startswith('第')])
    
    if mod_paras > orig_paras:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(modified)
        print(f"{fname}: {orig_paras}→{mod_paras}段 (+{mod_paras - orig_paras})")
```

## Verification after splitting

After batch processing, verify:
1. All chapters have ≥ 18 paragraphs
2. No paragraphs exceed 140 characters: `len([p for p in paras if len(p) > 140]) == 0`
3. Average paragraph length is ≤ 110 characters
4. CJK count unchanged (paragraph breaks don't add CJK characters)

## Validated results (2026-05-19)

| Volume | Chapters | New breaks added | Result |
|--------|----------|-----------------|--------|
| Vol 2 | 70 (51-120) | +883 | 13-28 paras/ch, avg 80-110 chars |
| Vol 3 | 40 (121-160) | +434 | 14-56 paras/ch, avg 80-110 chars |
| Vol 4 | 70 (161-230) | +various | 17-36 paras/ch, avg 80-110 chars |
| Arc 23 | 10 (221-230) | +121 | 21-25 paras/ch, avg 91-106 chars |

## Pitfalls

- **Don't break dialogue mid-speech**: The sentence-boundary split (`。！？`) naturally respects dialogue boundaries because Chinese dialogue typically ends sentences with these markers.
- **Title/skip detection**: Lines starting with `*第` (end markers) or `第XXX章` (title) must be skipped — breaking a title line corrupts the chapter header.
- **CJK count unchanged**: Paragraph breaking only adds `\n\n` characters, not CJK ideographs. Always verify CJK after splitting to confirm no content was lost.
