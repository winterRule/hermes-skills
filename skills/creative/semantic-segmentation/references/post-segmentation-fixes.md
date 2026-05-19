# Post-Segmentation Fixes

Mandatory cleanup steps after running `semantic_split.py` on inherited chapters.

## 1. Quote Balance Check (80%+ chapters need this)

`semantic_split.py`'s internal `fix_quotes()` now normalizes curly→ASCII→state-machine in the pipeline. But inherited chapters may still have imbalanced quotes from pre-existing damage.

**Quick audit after every batch:**
```python
for ch in chapters:
    text = open(ch).read()
    L = text.count('\u201c')
    R = text.count('\u201d')
    if L != R:
        print(f"FAIL {ch}: L={L} R={R}")
```

**Batch fix:**
```python
text = text.replace('\u201c', '"').replace('\u201d', '"')
chars = list(text); flip = True
for i, c in enumerate(chars):
    if c == '"':
        chars[i] = '\u201c' if flip else '\u201d'
        flip = not flip
text = ''.join(chars)
```

## 2. Unmatched End-of-Chapter Quotes

Symptom: `L > R` by exactly 1. Cause: an opening quote near the chapter end with no closing quote.

The updated `fix_quotes()` now auto-detects and inserts `\u201d` before the chapter-end marker.

## 3. Multi-Speaker Dialogue in One Paragraph

**Pattern**: Inherited chapters may have 3+ speakers' dialogue merged into a single paragraph:
```
林嫂写的是"..."老钱写道："..."铁根写道："..."韩先生...
```

**Detection**: Paragraphs where `\u201d` count ≥ 2 AND speaker-indicating words appear between quote pairs. False positives: paragraphs using quotes for terminology emphasis ("表面依托", "内外双层").

**Fix**: Split into one paragraph per speaker, each with complete opening+closing quotes, then the narration paragraph.

Example fix (ch208):
```
# Before (one paragraph):
林嫂写的是"我种了绷带上的线头...留着线是为了疤不裂，"老钱写道："梯田下面..."铁根写道："我种的是一管火铳..."

# After (four paragraphs):
林嫂在袖珍手册里写的是："我种了绷带上的线头，...留着线是为了疤不裂。"

老钱写道："梯田下面蓄水沟里的碎石，...每一块碎石代表一次我差点没站稳。"

铁根——那个曾被叫错名字的石根——写道："我种的是一管磨圆了裂口的火铳，它现在叫铁根。"

韩先生把这几段话一字不改地逐篇念给全班听。
```
