# Multi-Speaker Dialogue Merge Detection

## Problem

After semantic segmentation, chapters may still contain **multi-speaker dialogue merged into a single paragraph** — two or more different characters' spoken dialogue appearing in the same paragraph without a paragraph break between them.

This is NOT caught by standard comma-flow verification (`。。`/`，，` patterns) or quote balance checks (`\u201c` == `\u201d`). It requires structural analysis of quote placement within paragraphs. The semantic splitter's dialogue rules handle speaker changes in continuous text, but **pre-existing merges survive segmentation** because the quotes are syntactically balanced — they're just from different speakers in one paragraph.

### Example (before fix)

```
"顾明远说还会回来，我把烟留着，"他旁边一个川系老兵问了一句："如果有些人回不来了呢？"刘铁山没有马上回答。
```

Three distinct speech acts in ONE paragraph: 刘铁山 speaks → 川系老兵 asks → narration.

### Example (after fix)

```
"顾明远说还会回来，我把烟留着。"

他旁边一个川系老兵问了一句："如果有些人回不来了呢？"

刘铁山没有马上回答。
```

## Detection Algorithm (v2 — distance-filtered)

Validated on 100 chapters (中土纪元 V2, 121-220). Uses two-stage filtering:

```python
import re

SPEAKER_RE = re.compile(r'([\u4e00-\u9fff]{1,3})\s*(?:说道|回答|答道|喊道|叫道|骂道|吼道|念道|讲道|写道|问|说|喊|叫|骂|讲|念|写|答)')

# Stage 1: Find close consecutive closing quotes
for paragraph in paragraphs:
    close_positions = [j for j, c in enumerate(paragraph) if c == '\u201d']
    if len(close_positions) < 2:
        continue
    
    for ci in range(len(close_positions) - 1):
        c1 = close_positions[ci]
        c2 = close_positions[ci + 1]
        between = paragraph[c1:c2]
        
        # FILTER 1: Must have an opening quote between two closing quotes
        if '\u201c' not in between:
            continue
        
        # FILTER 2: Distance must be < 80 chars (close proximity = merge)
        # Larger distances are separate narration blocks, not merged dialogue
        if len(between) > 80:
            continue
        
        # FILTER 3: Must have a speaker indicator between quotes
        if not SPEAKER_RE.search(between):
            continue
        
        # TRUE POSITIVE — fix required
```

### Why the three filters matter

| Filter | What it catches | What it excludes |
|--------|----------------|-----------------|
| `\u201c` between `\u201d`s | Structural: two quote pairs overlapping | Single-quote paragraphs |
| Distance < 80 | Close-proximity merge | Separate narrations about different quoted terms |
| Speaker indicator | New speaker introducing dialogue | Term enumeration, concept quotes, written characters |

Without the distance + speaker filters, naive detection produces ~90% false positives (180 raw hits → ~4 true on 100 chapters).

## False Positive Categories

| Category | Pattern | Why excluded | Detection clue |
|----------|---------|-------------|----------------|
| Term enumeration | `"X"、"Y"或"Z"` | No speaker verb between quote pairs | No SPEAKER_RE match between quotes |
| Concept quotes | `从"扫荡"到"下一次扫荡"` | Narration about terms, not dialogue | Distance often > 80 |
| Character codenames | `代号是"翻书的人"` | Single speaker, term naming | Attribution before opening quote |
| Written characters | `写了一个"在"字` | Character writing, not speaking | Verb context is writing, not speaking |
| Same speaker continued | `"X," said A, "Y"` | Attribution break, same speaker | Same speaker name in both sides |
| **Narrative fragment** | `的⼈学写` / `底肥不写` / `务没有回答` | SPEAKER_RE matches random 1-3 char + verb in pure narrative — NO quotes in paragraph | **Check: paragraph has zero `\u201c`/`\u201d` quotes at all** |

### Narrative Fragment False Positives (v1.5 — 2026-05-22)

The SPEAKER_RE pattern `([\u4e00-\u9fff]{1,3})\s*(说|问|道|写|答|喊|叫|...)` is greedy enough to match random 1-3 character sequences in narrative text that happen to precede a verb-like character. This produces false positives in paragraphs that contain **zero** quotation marks — pure narration.

**Verify before fixing**: If the flagged paragraph has `count('\u201c') == 0`, it's a narrative-fragment false positive. Skip it.

**Real examples** (中土纪元 第二卷 161-180 batch):
| Chapter | Flagged | Actual text | Why false |
|---------|---------|------------|-----------|
| ch161 | "的⼈学写" | "地面上的⼈学写字是为了看懂告示" | Narrative clause, no dialogue |
| ch169 | "底肥不写" | "底肥不写在任何运单上" | Cargo description, no quotes |
| ch173 | "务没有回答" | "特务没有回答，他的中土文是..." | Agent narrative, no quotes |
| ch175 | "你刚才讲" | "他不知道藤原秀说这句话的意图" | Pure narrative, zero quotes in paragraph |

## Batch Scanning Workflow

Run after every 10-chapter batch completes segmentation and quote cleanup:

```bash
# Per-batch scan (10 chapters at a time)
cd <volume_directory>
python3 scripts/scan_multi_speaker.py . --start 221 --end 230 -v
```

The `-v` flag shows full context for each hit. Without `-v`, only summary counts are shown.

Integration with the batch segmentation pipeline:
```
分段(10章) → 引号修复 → 破折号修复 → CJK/段审计 → 逗号流验证 → 多角色扫描 → 汇报
```

## Fix Pattern

When a merge is detected, split into separate paragraphs — one per speaker:

```python
# Pattern: closing quote + speaker indicator + opening quote in same paragraph
# Split: each speaker gets their own paragraph
before = paragraph[:close_pos]
speaker_para = paragraph[close_pos:open_pos]  # speaker attribution
dialogue_para = paragraph[open_pos:]          # new speaker's dialogue
```

Manual fix via `patch()` is preferred for narrative-quality judgments (who speaks where, natural break points). For bulk fixes, the scripted approach works but may need per-chapter review.

## Validated Results

**中土纪元 V2, 100 chapters (121-220)**, scanned in 10-chapter batches:

| Chapter | Issue | Fix |
|---------|-------|-----|
| ch157 顾明远的告别 | 刘铁山+川系老兵 merge | → 3 paragraphs |
| ch166 苏大姐的日志(二) | 韩先生+老马头 4-turn conversation | → 5 paragraphs |
| ch205 秋霜 | 江寒 speech closing + narration merge | → 2 paragraphs |
| ch208 敌后扎根 | 林嫂/老钱/铁根 3-person merge | → 3 paragraphs + dash cleanup |
| ch215 白马集 | 马买办+山崎 merge | → 3 paragraphs |

- Raw detection hits: ~180 (naive `\u201d` + `\u201c` in same paragraph)
- After distance + speaker filtering: 5 true positives
- After fixes: 0 remaining merges in 100-chapter range
- Script: `novel-writing/scripts/scan_multi_speaker.py`
