# Inherited Volume Segmentation Workflow

When processing a volume that was NOT written in the current session (inherited from prior bulk-generation sessions), expect and handle these systemic corruption patterns before beginning semantic segmentation.

## Detection (Phase 0 — run before any segmentation)

```python
import re, os, glob
from collections import Counter

vol_path = "/path/to/volume"
files = sorted(glob.glob(f"{vol_path}/*.txt"))

# 1. Line number prefixes
line_num = sum(1 for f in files[:5] for l in open(f) if re.match(r'^\s+\d+\|', l))
print(f"Line numbers: {'⚠️' if line_num > 0 else '✅'} ({line_num} lines in sample)")

# 2. Section separators
seps = sum(1 for f in files[:5] if '---' in open(f).read())
print(f"|---| separators: {'⚠️' if seps > 0 else '✅'} ({seps} files)")

# 3. Intra-chapter duplication (same paragraph repeated 3+ times)
for f in files:
    text = open(f).read()
    paras = [p.strip() for p in text.split('\n') if p.strip()]
    counts = Counter(p[:60] for p in paras)  # first 60 chars as key
    dupes = {k: v for k, v in counts.items() if v >= 3}
    if dupes:
        print(f"  ⚠️ {os.path.basename(f)}: {sum(dupes.values())} dupes across {len(dupes)} patterns")

# 4. Cross-chapter template sharing
# Known template signatures from 中土纪元:
templates = [
    "暗河的水在远处无声地流着",
    "陆辰正在汇总一份给苏大姐的每日简报",
    "水伯站在渡口的石阶上，把竹篙重新插进水里",
]
for tmpl in templates:
    count = sum(1 for f in files if tmpl in open(f).read())
    if count > 1:
        print(f"  ⚠️ Template '{tmpl[:20]}...' found in {count} chapters")
```

## Systemic Corruption Patterns

### 1. Intra-Chapter Duplication (8-10x same paragraph)
**Appearance**: The same closing paragraph repeated 5-10+ times at chapter end.
**Impact**: CJK massively inflated. After dedup, chapters drop 400-600 CJK.
**Fix**: Keep ONE instance, remove all duplicates. Budget expansion for post-dedup CJK recovery.

```python
# Dedup within a chapter
seen_prefixes = set()
cleaned = []
for para in paras:
    prefix = para[:50]  # first 50 chars as fingerprint
    if prefix not in seen_prefixes:
        seen_prefixes.add(prefix)
        cleaned.append(para)
# Keep first occurrence, drop repeats
```

### 2. Cross-Chapter Template Pollution
**Appearance**: The same 3-5 paragraph block appears verbatim in many chapters (e.g., "暗河的水..." block in chapters 133-138 of 中土纪元).
**Decision per chapter**: If the template serves the current chapter's theme, keep one instance. If it doesn't belong, remove entirely.
**注意**: Removing the template block drops 200-400 CJK per chapter — budget expansion.

### 3. `|---|` Section Separators
**Appearance**: `---` lines used as visual separators between sections.
**Fix**: Remove all instances. Use paragraph breaks (double newline) instead.

### 4. Line Number Prefixes (`NNN|`)
**Appearance**: `     1|text`, `    25|text` at the start of every line — `cat -n` artifacts from prior session compaction.
**Fix**: `re.sub(r'^\s+\d+\|', '', line, flags=re.MULTILINE)`

## Workflow Order\n\n1. **Detect** all patterns (run Phase 0 scan)\n2. **Dedup** intra-chapter duplicates first (changes CJK)\n3. **Remove** separators and line numbers\n4. **Decide** on cross-chapter templates (keep or remove per chapter)\n5. **🚨 Re-count CJK** — chapters will be below 2000 after dedup. **NEVER report \"CJK全部通过\" based on pre-dedup CJK.** 实测：191章原5472CJK→去重后761CJK（25次重复虚增4700）。\n6. **Expand** short chapters with content that respects outline, logic, and物码体系\n7. **Segment** semantically (apply comma-flow rules)\n8. **Fix** dashes and quotes\n9. **Verify** CJK ≥ 2000, dashes = 0, quotes balanced\n10. **Check paragraph density**: 段数10-15但CJK>4000 = 虚假通过(去重后大概率<800)。正常40-65段/章 → CJK≈2000-3000。段数与CJK严重不匹配时优先怀疑重复内容。

## CJK Recovery After Dedup

Expected drop per chapter:
- Light duplication (3-5x one paragraph): -200 to -300 CJK
- Heavy duplication (8-10x one paragraph): -400 to -600 CJK
- Cross-chapter template removal: -200 to -400 CJK per template removed

Expansion must:
- Respect the chapter's existing narrative arc
- Use existing物码 (灰瓷罐, 炭条, 归码, 三角, 绿布灯, etc.)
- Reference prior chapters' events for continuity
- Maintain the prose style and emotional register
- Never introduce new characters or plot threads without outline support
