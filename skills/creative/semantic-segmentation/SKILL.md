---
name: semantic-segmentation
description: "Chinese novel semantic paragraph segmentation: dialogue-aware + scene-boundary + jieba keyword similarity for natural paragraph breaks. Replaces mechanical period-based splitting."
version: 1.4.0
tags: [chinese, novel, segmentation, nlp, jieba]
---

# Semantic Segmentation (语义分段)

Replace mechanical period-based paragraph splitting with a **rule-first + semantic-fallback + mechanical兜底** hybrid pipeline that produces natural paragraph breaks matching professional novel formatting standards.

## Triggers

Use when:
- Re-segmenting text-wall chapters (欠分段, < 25 paragraphs)
- User asks for "语义分段" or "正常分段"
- After template dedup, before CJK expansion
- Part of the batch resegmentation workflow (分段→六维审计→修复→汇报)

## Pipeline

```
Phase 0: Pre-clean (template dedup: regex blocks → paragraph sig dedup → intra-para dedup)
Phase 1: Sentence splitting (regex split at 。！？)
Phase 2: DIALOGUE RULES — split at "\u201c...\u201d" quotes, one speaker = one paragraph
Phase 3: SCENE RULES — split at time/location/event keyword boundaries  
Phase 4: SEMANTIC GROUPING — jieba keyword Jaccard similarity, percentile boundary selection
Phase 5a: COMMA FLOW — internal 。→，， only final period stays
Phase 5b: MECHANICAL SPLIT — split paragraphs > max_cjk CJK at comma boundaries
Phase 5c: COMMA FLOW RE-CLEAN — fix periods introduced by mechanical split
Phase 6: FORMAT FIXES — ASCII "→"" state machine, ——→，
```

## Phase 2: Dialogue Rules (highest priority)

**Rule 2.1: Quote boundary = paragraph boundary**
Whenever `"..."` (Chinese curly quotes) content appears, that segment MUST be its own paragraph. The surrounding narration (who said it, how they moved) can merge with the dialogue.

Pattern matching:
- Opening quote `\u201c` starts a dialogue block
- Closing quote `\u201d` ends it
- Everything between one pair of quotes = one dialogue unit
- Each dialogue unit must be a separate paragraph (or merged with its attribution)

**Rule 2.2: Speaker change = forced paragraph break**
When speaker A's dialogue ends and speaker B's begins, force a paragraph break between them.

**Rule 2.3: Action+speech merge**
A character's action + their following speech can be in the same paragraph:
```
光头男眼睛滴溜溜一转，他马上笑着说："一百块，给一百块你就摆吧。"
```
This is ONE paragraph. Action + speech from SAME character → merge.

## Phase 3: Scene Rules

**Rule 3.1: Time/location shifts**
Keywords that trigger paragraph breaks:
- Time markers: 第二天, 那天晚上, 过了, 半个时辰后, 天亮, 傍晚, 夜里
- Location shifts: 回到, 走进, 来到, 站在, 码头, 下水道, 磨盘
- Event boundaries: 突然, 就在这时, 与此同时

**Rule 3.2: Sound/sensory shifts**
External sounds or sensory changes that shift attention:
- 喇叭响了, 炮声从远处传来, 敲门声
- These trigger immediate paragraph breaks

**Rule 3.3: POV shifts**
When the narrative focus shifts to a different character's perspective:
- 老马头看到... → new paragraph
- 老孙头想的却是... → new paragraph

## Phase 4: Semantic Grouping (fallback)

For remaining narrative text after rules have split out dialogue and scene transitions, use jieba keyword similarity to group related sentences into coherent paragraphs.

Algorithm:
- Window size: 4 sentences
- Extract top-8 keywords per window (jieba, >=2 chars)
- Compute Jaccard similarity between adjacent windows
- Target paragraph count: 40-65 (adjustable via `--target-paras`)
- Use percentile-based boundary selection

```python
# Core semantic split function
def semantic_group(sentences, target_paras=50):
    win = 4
    sims = []
    for i in range(len(sentences) - win):
        prev = sentences[i:i+win]
        nxt = sentences[i+1:i+1+win]
        kw_prev = jieba_keywords(' '.join(prev), 8)
        kw_next = jieba_keywords(' '.join(nxt), 8)
        sim = len(kw_prev & kw_next) / max(len(kw_prev), len(kw_next))
        sims.append(sim)
    
    # Sort similarity drops, pick top-N as boundaries
    deltas = [(i+win, sims[i-1]-sims[i]) for i in range(1, len(sims))]
    deltas.sort(key=lambda x: -x[1])
    n_splits = min(target_paras - 1, len(deltas))
    split_points = sorted([d[0] for d in deltas[:n_splits]])
    
    paragraphs = []
    start = 0
    for b in split_points:
        if b > start:
            paragraphs.append(''.join(sentences[start:b]))
            start = b
    paragraphs.append(''.join(sentences[start:]))
    return paragraphs
```

## Phase 5b: Mechanical Split (兜底)

When semantic grouping produces paragraphs that are still too long (CJK > max_cjk), split them mechanically at comma boundaries. This ensures paragraph density in dense prose chapters where semantic boundaries are sparse.

**Recommended defaults** (validated on 中土纪元 40 chapters):
- `--target-paras 65` for CJK 2000-2200 chapters
- `--target-paras 70` for CJK 2200+ chapters  
- `max_cjk=65` (internal default) — produces 40-80 paragraphs/chapter consistently
- For very dense chapters, decrease `max_cjk` to 55 for more aggressive splitting

```python
def split_long_paragraphs(paragraphs, max_cjk=65):
    for p in paragraphs:
        if CJK(p) <= max_cjk: keep
        else: split at comma boundaries into ~max_cjk chunks
```

## Usage

```bash
# Process single chapter
python3 scripts/semantic_split.py <chapter_file> --target-paras 50

# With aggressive mechanical splitting (lower = more paragraphs)
python3 scripts/semantic_split.py ch.txt --target-paras 70 --max-cjk 40

# Process batch
for f in 第2*.txt; do python3 scripts/semantic_split.py "$f" --target-paras 50; done

# Custom target
python3 scripts/semantic_split.py ch.txt --target-paras 60 --min-cjk 2000
```

### `--max-cjk` Parameter (v1.3+)

Controls the mechanical split threshold — paragraphs with CJK > max_cjk are split at comma boundaries. Lower values produce more paragraphs.

**Golden standard**: Chapters 1-29 of 中土纪元 average **53 paragraphs/chapter** with **46 CJK/paragraph**. Degraded chapters (30+) average only 32 paragraphs with 83 CJK/paragraph — text walls.

### Tiered Segmentation Strategy (for re-segmenting inherited volumes)

When re-segmenting chapters written by prior AI sessions, match the golden standard using tiered `--max-cjk`:

| Original Paragraphs | max_cjk | target-paras | Effect |
|---|---|---|---|
| < 25 (text wall) | 40 | 75 | → 55-65 paragraphs |
| 25–40 (under-segmented) | 45 | 70 | → 55-70 paragraphs |
| 41–50 (acceptable) | 50 | 65 | → 60-75 paragraphs |
| > 50 (good) | 55 | 60 | → 60-70 paragraphs |

Validated on 中土纪元 Volume 1 chapters 39-48: 10 chapters from 32→67 avg paragraphs, CJK preserved, zero over-fragmentation.

## Batch Pipeline (每批必做，不可跳步)

After segmentation of each batch (10 chapters), run these checks in order. **Fixes MUST include specific line numbers** (e.g. "ch198 L20/L22 空引号对", "ch237 L127 多角色合并"). The user requires line-level precision in all fix reports.

```
1. semantic_segment() — layered max_cjk strategy
2. Quote balance — normalize all → state machine (see Post-Segmentation Quote Fix)
3. Orphan quote fragments — three-pattern scan FIRST (① 孤儿开引号 ② 空引号对 ③ 孤儿关引号), fix before multi-speaker scan
4. scan_multi_speaker.py — THEN scan, manually verify each flag (~75% false positives)
5. Comma flow —  。。|，，|。，|，。  scan
6. Report — table: ch, orig-segs, new-segs, CJK, fix-location (ch+L)
```

## Verification

After segmentation, verify:
1. Paragraph count: 40-80 (target 40-65; dense dialogue chapters may hit 80+)
2. CJK count: >= 2000
3. Zero `——` em-dashes
4. Zero ASCII `"`
5. Quote balance: `\u201c` count == `\u201d` count
6. **Comma flow**: zero `。。`, `，，`, `。，`, `，。` patterns within paragraphs
7. Every paragraph ends with `。` (or `！`/`？`), internal punctuation is `，` only
8. **Orphan quote fragment scan (THREE PATTERNS — ch074/ch198/ch253 validated across 140 chapters)**: 
   
   The `fix_quotes()` state machine in semantic_split.py normalizes ALL quotes (curly→ASCII→state machine) and guarantees `\u201c` count == `\u201d` count. But **three orphan patterns can survive** because each is quote-balanced (equal open/close) yet semantically wrong. Detection MUST run AFTER quote normalization.
   
   **Pattern ① — 孤儿开引号**: paragraph starts with `\u201c ` (opening quote + space) but has no `\u201d` in the same paragraph. This is a narrative paragraph with a stray opening quote prefix — the text is NOT dialogue. FIX: `line.replace('\u201c ', '', 1)`. Example: ch074 L117, ch238 L76.
   
   **Pattern ② — 空引号对**: `\u201c \u201d` consecutive (empty quoted pair with space between). Produced when the segmenter splits around tightly-quoted terms, leaving an orphan `\u201c` that gets paired with an orphan `\u201d` via state-machine. FIX: `text.replace('\u201c \u201d', '')` then re-run state machine. This is the MOST COMMON orphan pattern — 15+ instances across batches 221-280. Examples: ch198 L20/L22, ch221 L102, ch223 L110/L148, ch228 L112, ch230 L84, ch232 L132, ch234 L14/L24, ch236 L118, ch253 L42, ch266 L78/L134, ch272 L66.
   
   **Pattern ③ — 孤儿关引号**: paragraph starts with `\u201d ` (closing quote + space) and no `\u201c` within first 3 chars. FIX: rerun full-chapter quote normalization (all→ASCII→state machine). Example: ch238 after pattern-① removal exposed this pattern.
   
   Python detection (run AFTER quote normalization):
   ```python
   paras = [l for l in text.split('\n') if l.strip() and not l.strip().startswith('第') and not l.strip().startswith('*第')]
   orphan_open  = sum(1 for l in paras if l.strip().startswith('\u201c ') and '\u201d' not in l)
   orphan_empty = text.count('\u201c \u201d')
   orphan_close = sum(1 for l in paras if l.strip().startswith('\u201d ') and '\u201c' not in l[:3])
   ```
   All three must be zero. If any non-zero: fix AND report chapter+line numbers.
   
   **FIX ORDER**: Pattern ② first (empty pairs corrupt the quote count for the other patterns), then Pattern ①, then re-run state machine if Pattern ③ remains.

9. **Multi-speaker dialogue merge**: zero paragraphs where two different speakers' dialogue appears without a paragraph break. Use `scan_multi_speaker.py` for detection, then **manually verify every flag** — ~75% false positive rate across 140 chapters. Common false positives (validated):
   - 术语引号: `"羊毫"` — quoted term names, not dialogue
   - 叙事"写道": `"条目下面写道"` — narrator verb, same speaker
   - 同一人连续说话: `"志不是写...是写..."` — speaker verb in content only
   - 同一人动作: `"然后他问学生:"` — same character
   - Garbled speaker extraction: `"的人学写"`, `"底肥不写"`, `"务没有回答"`, `"大姐追问"` — regex matched partial phrases
   
   True positive signal: 2+ DIFFERENT character names as subjects of 说/问/道/写 in close proximity. Fix: split at speaker boundaries into separate paragraphs. Example: ch237 L127 (老陈→苏大姐), ch253 段#16 (韩先生→学员→韩先生).

Verification code:
```python
# Check comma flow violations
bad_patterns = ['。。', '，，']  # double punctuation
if '。。' in text or '，，' in text: FAIL
if re.search('。[，]', text): FAIL  # period before comma  
if re.search('，。(?=.)', text): FAIL  # comma-period mid-paragraph

# Multi-speaker dialogue merge (filtered — see references/multi-speaker-detection.md)
for para in paragraphs:
    close_pos = [j for j, c in enumerate(para) if c == '\u201d']
    for ci in range(len(close_pos)-1):
        between = para[close_pos[ci]:close_pos[ci+1]]
        if '\u201c' in between and re.search(r'(?:说道|说|写道|问|回答|答道|喊|叫)', between):
            FAIL  # two different speakers in one paragraph
```

## Post-Segmentation Quote Fix (MANDATORY after every batch)

The `fix_quotes()` in semantic_split.py (v1.2+) normalizes ALL curly quotes back to ASCII then runs state-machine, and handles unmatched end-of-file opening quotes. This covers most cases, but inherited chapters may still need a second pass — **verify after every batch**.

**Batch quote fix** (run after ALL segmentation, before audit):
```python
# Fix imbalanced curly quotes by normalizing to ASCII then state-machine
text = text.replace('\u201c', '"').replace('\u201d', '"')
chars = list(text); flip = True
for i, c in enumerate(chars):
    if c == '"':
        chars[i] = '\u201c' if flip else '\u201d'
        flip = not flip
text = ''.join(chars)
# Then verify: left == right AND '"' count == 0
```

**Unclosed quotes at chapter end**: If `LDQUO > RDQUO` after state-machine fix, there's an unmatched opening quote (often at end-of-chapter narrative closing). Find the last unbalanced opening quote position and insert `\u201d` before the chapter-end marker.

## Multi-Speaker Dialogue Detection

Inherited chapters from prior AI bulk-generation sessions often have **multiple speakers' dialogue merged into one paragraph**. Example pattern (ch208):
```
林嫂写的是"..."老钱写道："..."铁根写道："..."韩先生把这几段话...
```
Three different speakers in one paragraph. This MUST be split so each speaker gets their own paragraph.

**Detection**: Check for paragraphs where `\u201d` count ≥ 2 AND there's a speaker-indicating word (写/说/道/喊) between a closing quote and the next opening quote. **False-positive caution**: paragraphs using quotes for terminology emphasis ("表面依托", "内外双层") will also match `close_count ≥ 2`. Filter by checking for speaker-pattern words between quote pairs.

**Fix**: Split into one paragraph per speaker, each with complete opening+closing quotes, followed by the narration paragraph.

## Pitfalls

- **🚨 Long-dialogue fragmentation with low max_cjk (ch074/ch101/ch115/ch116 validated)**: When `max_cjk ≤ 40`, the `split_long_paragraphs()` mechanical split can break a single character's long continuous speech into fragments. Middle fragments lose their enclosing `\u201c...\u201d` quotes and speaker attribution, producing **orphan quotes** — paragraphs that start with `\u201d ` (a closing quote followed by space, then text). Example from ch074 before fix:
  ```
  "我们熬了三年，熬了三年还在熬！
  ... (middle fragments without quotes) ...
  " 苏大姐没有拍桌子。"   ← orphan: closing quote + narration merged
  ```
  **Detection**: After segmentation, scan for paragraphs starting with `\u201d ` where no opening quote follows within 3 chars. Python: `orphans = sum(1 for l in text.split('\n') if l.strip().startswith('\u201d ') and '\u201c' not in l[:3])`. If > 0, the chapter has fragmented dialogue needing manual repair.
  
  **Prevention**: For chapters heavy in continuous dialogue (identified by high quote density in original), raise `max_cjk` to 50+ even if the tiered strategy says 40. The tiered strategy works for narrative chapters but over-fragments dialogue chapters. When in doubt, scan for orphan quotes after every batch — it takes one `execute_code` call and catches all instances.
  
  **Fix pattern**: Read the surrounding context, identify who is speaking, merge the fragments back into one dialogue paragraph with continuous `\u201c...\u201d` quotes. Then split at speaker-change boundaries only (not at mechanical comma splits).

- **`fix_quotes` state-machine limitation**: The built-in `fix_quotes()` function only handles ASCII `"` → `\u201c`/`\u201d` conversion and unmatched-end-of-file opening quotes. It does NOT fix existing curly-quote imbalances in the input text. If the input already has unbalanced `\u201c`/`\u201d` counts, the state machine cannot detect or repair them — it only processes ASCII quotes. **Solution**: Run a batch quote fix AFTER segmentation: convert ALL quotes (both `\u201c`/`\u201d` and `"`) to ASCII `"`, then re-run the state machine on the entire text. This guarantees balance.

- **`fix_quotes` blind spot — 空引号对 `\u201c \u201d` (140章验证)**: The state machine guarantees `\u201c` count == `\u201d` count, so chapters pass the balance check. But `\u201c \u201d` (empty quoted pair with nothing between open and close) is ALSO balanced (one open, one close) yet semantically wrong. The empty pair is a segmentation artifact — when a narrative sentence near a quoted term gets split, the orphan `\u201c` and `\u201d` end up adjacent after state-machine normalization. Detection requires scanning for the literal `\u201c \u201d` pattern AFTER normalization. This is the SINGLE MOST COMMON orphan artifact — 15+ instances in batches 221-280 alone. Fix: `text.replace('\u201c \u201d', '')` then re-run state machine.
```python
text = text.replace('\u201c', '"').replace('\u201d', '"')
chars = list(text); flip = True
for i, c in enumerate(chars):
    if c == '"':
        chars[i] = '\u201c' if flip else '\u201d'
        flip = not flip
text = ''.join(chars)
```
This pattern was validated across 100 chapters — resolves all quote imbalances in one pass.

- **Multi-speaker dialogue merge survives segmentation**: The semantic splitter's dialogue rules handle speaker changes within continuous text, but some inherited chapters have structurally broken dialogue (two speakers' complete utterances in one paragraph). These survive segmentation because the quotes are syntactically balanced but semantically wrong. Detection requires post-segmentation scanning (see `references/multi-speaker-detection.md`). Fix pattern: split the merged paragraph at speaker boundaries (`\u201d` + speaker indicator + `\u201c`), giving each speaker their own paragraph.

- **scan_multi_speaker.py has ~75% false positive rate (100章验证)**: The speaker regex matches loose patterns like `\u4e00-\u9fff{1,3}\s*(说|写|道|...)`, which picks up narrative fragments (e.g. `条目下面写道`, `底肥不写`, `务没有回答`, `你刚才讲`, `志不是写`). **After every batch scan, manually verify EACH flagged paragraph** — read the full paragraph text and check whether it truly contains two different speakers' dialogue. If the "speaker" is part of a longer narrative phrase or the same character's extended speech, it's a false positive. Only split paragraphs that genuinely contain A-speaks-then-B-speaks.
- **Semantic THEN mechanical**: Always run semantic grouping first, then mechanical split second. Mechanical-only produces uniform but unnatural breaks. Semantic-only on dense prose produces paragraphs that are too long (20-35 for 2000 CJK chapters). Combined: 40-80 paragraphs consistently.
- **max_cjk tuning**: Start at 65. If paragraph count < 40, decrease to 55. If > 80, increase to 75. Validated on 40 chapters of 中土纪元.
- **Comma flow verification is MANDATORY**: After every batch, scan for `。。`, `，，`, `。，`, `，。` patterns. These indicate broken comma flow cleanup.
- **Multi-speaker merge is a structural defect, not a segmentation issue**: The semantic_split.py dialogue rules handle quote-bounded segments but can't detect speaker changes within a paragraph that already contains multiple complete quotes from different people. This requires post-segmentation detection and manual (or scripted) splitting.

## Reference Files

- `scripts/semantic_split.py` — Main segmentation script with full pipeline (v1.2 — robust quote fix + unclosed quote handling)
- `scripts/scan_multi_speaker.py` — **Multi-speaker dialogue merge detector** (v2 — distance-filtered, speaker-verb gated). Per-batch: `python3 scripts/scan_multi_speaker.py <dir> --start N --end M [-v]`. Located at `novel-writing/scripts/scan_multi_speaker.py`.
- `references/orphan-quote-detection.md` — **Detection and fix for fragmented dialogue** (orphan `\u201d ` at paragraph starts). Caused by low max_cjk splitting continuous speech. Detection code, examples from ch074/ch101, fix pattern.
- `references/batch-tuning.md` — max_cjk tuning data from 中土纪元 batch processing
- `references/multi-speaker-detection.md` — **Detection algorithm v2**: three-filter approach, false-positive categories, batch workflow, 5 true positives/100 chapters validated
- `references/post-segmentation-fixes.md` — Post-segmentation cleanup: quote balance fix, unclosed quote detection, multi-speaker dialogue splitting
