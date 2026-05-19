# Batch Quote Fix After Segmentation

When `semantic_split.py` processes inherited chapters, quote balance can break in two scenarios:

## Scenario 1: Imbalanced curly quotes (most common)

The input text already has `\u201c`/`\u201d` pairs that don't match. The pre-v1.2 `fix_quotes()` only converted ASCII `"` → curly, leaving existing curly quotes untouched.

**Fix** (v1.2+ script handles this automatically — manual fallback):

```python
import re, os

base = "/path/to/chapters"

for i in range(start, end+1):
    for f in os.listdir(base):
        if f.startswith(f'第{i}章_') and f.endswith('.txt'):
            fpath = os.path.join(base, f)
            break
    
    with open(fpath, 'r', encoding='utf-8') as fh:
        text = fh.read()
    
    # Normalize ALL quotes to ASCII, then state-machine
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    chars = list(text)
    flip = True
    for j, c in enumerate(chars):
        if c == '"':
            chars[j] = '\u201c' if flip else '\u201d'
            flip = not flip
    text = ''.join(chars)
    
    # Fix dashes too
    text = text.replace('——', '，')
    
    with open(fpath, 'w', encoding='utf-8') as fh:
        fh.write(text)
    
    left = text.count('\u201c')
    right = text.count('\u201d')
    print(f"ch{i}: L={left} R={right} {'✅' if left==right else '❌ ODD'}")
```

## Scenario 2: Odd total quote count (rare, 2/100 chapters)

When the total number of quotes is odd, the state machine will always leave one unmatched (L=R+1 or R=L+1). This happens when the original text has broken/missing quote pairs.

**Fix pattern** (2026-05-19, ch202/ch205):

```python
# For chapters where L > R after state-machine:
# Find the last unmatched opening quote and insert closing before end marker
if left > right:
    balance = 0
    last_open_pos = -1
    for i, c in enumerate(text):
        if c == '\u201c':
            if balance == 0:
                last_open_pos = i
            balance += 1
        elif c == '\u201d':
            balance -= 1
    
    m = re.search(r'\*第.*章·完', text)
    if m and last_open_pos >= 0:
        text = text[:m.start()].rstrip() + '\u201d\n\n' + text[m.start():]
```

## Prevention

After EVERY segmentation batch, run:
```python
for chapter in batch:
    assert text.count('\u201c') == text.count('\u201d'), f"Quote imbalance in {chapter}"
    assert text.count('"') == 0, f"ASCII quotes in {chapter}"
    assert text.count('——') == 0, f"Em dashes in {chapter}"
```

**Validated**: 181-220 (40 chapters), 3 batches needed quote fixes. With v1.2+ script fix, post-segmentation quote imbalance should drop to near-zero.
