# Inherited Arc Cleanup Pattern

When an arc has chapters inherited from a prior writing session (different agent, different model, different time), they will have GUARANTEED format issues. Do NOT assume they are clean just because they exist as files.

## Detection

An inherited arc has these signals:
- Chapters exist at regular intervals (e.g., every 3rd chapter: 211, 214, 217, 220)
- Internal chapter numbers don't match file numbers (file says 211, internal says 081)
- `cat -n` line number artifacts present (`\s+\d+|` prefixes on every line)
- Old Chinese-numeral end markers (第八十一章·完 instead of 第211章·完)
- 30-50+ ASCII quotes `"` per chapter
- CJK counts are OK (inherited chapters are usually long enough)

## Cleanup Sequence (per inherited chapter)

Step 1: Strip line numbers
```python
cleaned = [re.sub(r'^\s+\d+\|\s*', '', line) for line in lines]
```

Step 2: Fix internal numbering on line 1
```python
text = text.replace(f'第{old_num}章 {title}', f'第{new_num:03d}章 {title}', 1)
```

Step 3: Fix ASCII quotes via state machine
```python
result = []
flip = True
for ch in text:
    if ch == '"':
        result.append('\u201c' if flip else '\u201d')
        flip = not flip
    else:
        result.append(ch)
text = ''.join(result)
```

Step 4: Fix end marker (handle Chinese numerals)
Old: `*第八十一章·完*` -> New: `*第211章·完*`

Step 5: Verify
- CJK >= 2000 (stripping line numbers removes a few CJK)
- `——` count = 0
- `"` count = 0 (ASCII)
- `\u201c` count = `\u201d` count (curly quotes balanced)

## Cost Budget

4 inherited chapters cost ~6 tool calls total: 4 patch calls for end markers + 1 batch execute_code for line numbers and quotes + 1 verification execute_code.

## Historical Context

Validated on Arc 10-1 (211-220): 4 inherited chapters (211, 214, 217, 220) from a prior session all had internal numbering offset by 130 (081-084 vs 211-220), line number artifacts from `cat -n` compaction, Chinese-numeral end markers, and 32-46 ASCII quotes each.

Validated on Arc 10-2 (221-230): 3 inherited chapters (223, 226, 229) with same pattern — internal numbering offset by 138 (085-087), 34-38 ASCII quotes each, no line numbers this time. End marker format was `*第223章·完**` (double asterisk on one chapter). Fix sequence identical apart from line numbers.

## Additional Detected Artifacts

- **Double-asterisk end markers**: `*第223章·完**` — double `*` at end, likely from a prior expansion that appended `*` to an already-closed marker. Fix: replace `*完**` → `*完*`.
- **No-line-number variant**: Some inherited chapters may already have been cleaned of `|` line numbers but still have old internal numbering and ASCII quotes. The `has_pipes` check is a quick discriminator but not a guarantee of cleanliness.
