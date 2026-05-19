# Batch Dash Removal v2: Pattern-Based → Zero Residuals

Session-validated technique for fixing em-dash overuse at scale. Applied to 64 chapters across Volumes 3-4, removing 3,597 dashes in ONE pass with zero CJK loss and zero residuals.

## The Algorithm

```python
import re

def fix_dashes(text):
    """Replace narrative —— with proper Chinese punctuation."""
    
    # Step 1: "不是X——是Y" → "不是X，是Y"
    text = re.sub(
        r'(不是[^。！？，；——]{1,30})——(是[^。！？]{1,30})', 
        r'\1，\2', 
        text
    )
    
    # Step 2: "X——Y——Z" chains → "X，Y。Z" (3+ parts, split at second dash)
    def break_chain(m):
        parts = m.group(0).split('——')
        if len(parts) >= 3:
            return parts[0] + '，' + parts[1] + '。' + '——'.join(parts[2:])
        return m.group(0)
    text = re.sub(r'[^。！？\n]{15,}——[^。！？\n]{10,}——', break_chain, text)
    
    # Step 3: After 。！？, —— is a new sentence start → remove
    text = re.sub(r'([。！？])\s*——', r'\1', text)
    
    # Step 4: All remaining —— → ，
    text = re.sub(r'——', '，', text)
    
    return text
```

## Key Design Decisions

1. **No categorization pass**: Unlike the manual A/B/C/D analysis in `references/em-dash-manual-analysis.md`, this v2 approach skips categorization. Rationale: when 64 chapters have 3-116 dashes each (3,597 total), categorization overhead exceeds replacement cost. Nearly all dashes in these chapters are C-class (connective) that should become `，`.

2. **"不是X——是Y" handled first**: This is the only pattern where `——` functions as rhetoric rather than connector. Handle it before the blanket replacement.

3. **Chain-breaking before blanket replace**: 3+ part chains need special treatment — breaking them all to `，` creates a run-on. Split the middle at `。`.

4. **Sentence-boundary dashes removed**: After `。！？`, a leading `——` is always extraneous.

5. **Everything else → `，`**: The blanket replacement is safe because all special cases were handled first.

## Post-Replacement Verification

After running the replacement, scan for artifacts:

```python
# Check for double punctuation created by replacement
if '。。' in text or '，，' in text or '，。' in text:
    # Fix: replace doublers with singles
    text = text.replace('。。', '。')
    while '，，' in text:
        text = text.replace('，，', '，')
```

## When to Use

- 10+ chapters with 10+ dashes each in narrative text
- User explicitly requests dash cleanup at volume scale
- After paragraph breaking (dashes look worse in short paragraphs)

## When NOT to Use

- 1-2 chapters with <10 dashes: use manual per-chapter fixes
- Chapters where dashes serve structural role (科目002, 航海日志) — filter those out first
- Arc 21+ chapters already written in zero-dash style

## Results (Session 2026-05-19)

| Volume | Range | Chapters | Dashes Removed |
|--------|-------|----------|---------------|
| 第三卷 | 138-160 | 23 | 631 |
| 第四卷 | 161-200 | 40 | 2,952 |
| 第四卷 | 206 | 1 | 14 |
| **Total** | | **64** | **3,597** |

Post-replacement: ZERO narrative dashes across all 64 chapters. Only 2 double-punctuation artifacts found and fixed (双逗号 in Ch.173, 双句号 in Ch.027).
