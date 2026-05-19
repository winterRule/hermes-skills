# Orphan Quote Detection (孤儿引号检测)

## Problem

When `semantic_split.py` runs with low `--max-cjk` (≤40), the `split_long_paragraphs()` function mechanically splits long paragraphs at comma boundaries. If the long paragraph is continuous dialogue from one speaker, the split fragments lose their enclosing `\u201c...\u201d` quotes.

**Result**: Paragraphs that start with `\u201d ` (a closing quote at the START of a paragraph) — evidence that a dialogue was fragmented.

## Detection

```python
import re

def count_orphan_quotes(text):
    """Count paragraphs starting with orphaned closing quotes."""
    orphans = 0
    for line in text.split('\n'):
        stripped = line.strip()
        # Starts with " (closing quote) followed by space, no opening quote in first 3 chars
        if stripped.startswith('\u201d ') and '\u201c' not in stripped[:3]:
            orphans += 1
    return orphans
```

## Examples (from ch074, ch101, ch115, ch116)

**Type A: Closing-quote orphan (`\u201d ` at paragraph start)**
From ch074 before fix:
```
"我们熬了三年，熬了三年还在熬！

边熬边等，等到林嫂的金疮药用光？        ← fragment without quotes
" 苏大姐没有拍桌子。"                   ← ORPHAN: closing quote at paragraph start
```
After fix:
```
"我们熬了三年，熬了三年还在熬！边熬边等，等到林嫂的金疮药用光？"

苏大姐没有拍桌子。                       ← clean narration paragraph
```

**Type B: Opening-quote orphan (`\u201c ` prefix, no closing quote in paragraph)**
From ch074 before fix:
```
" 陆辰看了那份申请单很久，然后从怀里掏出那本在天衡盟用了近一个月的文书令符..."
```
After fix (remove `\u201c ` prefix):
```
陆辰看了那份申请单很久，然后从怀里掏出那本在天衡盟用了近一个月的文书令符..."
```
Detection: paragraph starts with `\u201c ` AND contains zero `\u201d` in the same paragraph.

**Type C: Empty quote pair (`\u201c \u201d` prefix)**
From ch074 before fix:
```
" "这个编号我们都记下了，"苏大姐打断他的话，不是不耐烦。"
```
After fix (remove `\u201c \u201d` prefix, keep `\u201c`):
```
"这个编号我们都记下了，"苏大姐打断他的话，不是不耐烦。"
```
This occurs when a dialogue continuation paragraph gets split right after `。"` (period + closing quote), leaving the next paragraph's opening quote stranded with an orphan closing quote from the split point.

### Combined Detection Script

```python
def detect_all_orphans(text):
    "Detect Type A (closing-quote start), Type B (opening-quote prefix), Type C (empty pair)."
    orphans = {'type_a': [], 'type_b': [], 'type_c': []}
    for i, line in enumerate(text.split('\n')):
        s = line.strip()
        if not s: continue
        # Type A: starts with closing quote, no opening quote nearby
        if s.startswith('\u201d ') and '\u201c' not in s[:3]:
            orphans['type_a'].append((i, s[:80]))
        # Type B: starts with opening quote + space, no closing quote in paragraph
        elif s.startswith('\u201c ') and '\u201d' not in s:
            orphans['type_b'].append((i, s[:80]))
        # Type C: empty quote pair prefix
        elif s.startswith('\u201c \u201d'):
            orphans['type_c'].append((i, s[:80]))
    return orphans
```

## Fix Patterns

| Type | Fix | sed / Python |
|------|-----|-------------|
| A | Merge fragments back to one dialogue block | Manual (read context) |
| B | `text.replace('\u201c ', '', 1)` | Remove orphan prefix |
| C | `text.replace('\u201c \u201d', '\u201c', 1)` | Remove empty pair, keep opening quote |

## Prevention

- For chapters with high dialogue density, raise `--max-cjk` to 50+
- Run orphan scan after EVERY batch segmentation
- One `execute_code` call per batch catches all instances

## Fix Pattern

1. Identify the speaking character from context
2. Merge all fragments back into one continuous `\u201c...\u201d` dialogue block
3. Split only at actual speaker-change boundaries
4. Move orphaned narration (e.g., "苏大姐没有拍桌子。") to its own paragraph
