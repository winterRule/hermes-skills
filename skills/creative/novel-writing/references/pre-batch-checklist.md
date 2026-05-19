# Pre-Batch Checklist (批次前 15 秒自检)

Read this BEFORE writing each batch of 3-5 novel chapters. Takes 15 seconds. Skipping it cost 174 dashes and 40+ fix calls in Arc 13-14 alone.

## Before First write_file

1. **Read outline for this batch**: confirm all 5 chapter titles and 内容要点
2. **Read last 2 chapters** of previous batch for continuity
3. **Plan 4-5 vignettes per chapter** (character + object + sensory detail each)
4. **Target: 8000+ bytes first draft** — anything below 7000 WILL be short

## After Each write_file

Run this ONE execute_code call per chapter:
```python
import re
with open(path) as f: text = f.read()
text = text.replace('——', '，')
flip = True; chars = list(text)
for i, c in enumerate(chars):
    if c == '"': chars[i] = '\u201c' if flip else '\u201d'; flip = not flip
text = ''.join(chars)
text = re.sub(r'，，+', '，', text)
cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
with open(path, 'w') as f: f.write(text)
print(f"CJK={cjk} bytes={len(text.encode('utf-8'))} dashes=0")
```

If CJK < 2000 or bytes < 7000: **expand NOW** (add 2-3 paragraphs sensory detail), re-run verify. Do NOT proceed to next chapter.

## After Batch Complete (3-5 chapters)

1. Run full audit on all chapters in batch
2. Fix ALL issues (dashes, quotes, CJK, outline alignment)
3. Re-verify ALL PASS
4. **Explicit outline-title verification**: Create a per-chapter table showing 大纲标题 vs 实际标题 vs 大纲内容要点 vs 实际内容 (one line per chapter), confirming each matches. User explicitly requested this check — do NOT assume the "大纲对位" summary row in the 5-dimension audit is sufficient. After the first batch of a new arc or volume, the user may specifically ask "与大纲标注的章节标题和内容一致吗" — have the table ready before they ask.
5. THEN report to user with audit table AND title-verification table
6. THEN ask "继续下一批？"

## After patch() Expansion

`patch()` ALWAYS introduces dashes and escaped quotes. After EVERY patch:
1. Run the same verify snippet above
2. It auto-fixes dashes and quotes
3. Check CJK — if still short, patch again

## Red Flags (stop and fix immediately)

- write_file output < 5500 bytes → guaranteed <1700 CJK
- Any `——` in grep output → you skipped per-chapter verify
- User says "审查呢" → you skipped batch audit gate
- 3+ chapters in batch need expansion → first drafts too short, plan more vignettes
