# Paragraph Reformatting Workflow

When existing novel chapters have dense, essay-like paragraphing (5-10 sentences per paragraph, <20 paragraphs/chapter) that needs to be converted to the short-paragraph comma-flow style (~50-65 paragraphs for ~2200 CJK, matching Chapter 001 benchmark).

## Detection

Scan paragraph density:
```python
import os, re
base = "/path/to/volume"
for f in sorted(os.listdir(base)):
    with open(os.path.join(base, f)) as fh: text = fh.read()
    body = [l for l in text.split('\n') if l.strip() and not l.startswith('*第') and not l.strip().startswith('第0')]
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    print(f"{f[:30]:30s} 段{len(body):3d} CJK{cjk}")
# Benchmark: Chapter 001 = ~65 paragraphs, ~2074 CJK
# Chapters below 25 paragraphs are severely under-segmented
```

## Semantic Paragraphing Rules (USER-ENFORCED 2026-05-20)

**口诀**: 时间变、地点变，事情阶段变；内容换、感情换，总分结构看。一段讲一个意思。

**对话铁律**: 一个人说的话 = 一个段落。A说→一段，B说→一段。对话内部用逗号（，）连接子句，段末句号（。）收束。禁止把一个人的话拆成多个段落。

**段落内逗号流**: 段落是完整语义流，中间用逗号不用句号打断。句号仅段末收束（或引号关闭前）。段落间空行=最强停顿。

**引号格式**: 英文直引号 `"..."` 用于对话，禁止 `「」`。

**动作+对话可合并**: 角色动作与话语可在同一段。不同人的话必须在不同段。

## Batch Fix Workflow (VALIDATED V1 120章)

### Phase 1: Fix Split Dialogue (裂引号合并)

Chapters that were previously "fixed" by mechanically splitting at periods will have broken dialogue (odd quote counts per paragraph).

```python
def fix_split_dialogue(text):
    """Merge consecutive paragraphs with unbalanced quotes"""
    lines = text.split('\n')
    body = [l.strip() for l in lines if l.strip() and not l.startswith('*第') and not l.strip().startswith('第0')]
    merged = []; buf = None
    for para in body:
        qc = para.count('"')
        if buf is not None:
            buf += para
            if buf.count('"') % 2 == 0:
                merged.append(fix_dialogue_punctuation(buf)); buf = None
        elif qc % 2 != 0: buf = para
        else: merged.append(para)
    # Rebuild file with merged paragraphs
```

### Phase 2: Dialogue Internal Punctuation Fix

Within merged dialogue blocks, replace internal `。` with `，`, keep only the final `。` before closing `"`:

```python
def fix_dialogue_punctuation(text):
    result = []; i = 0
    while i < len(text):
        if text[i] == '"':
            j = i + 1
            while j < len(text) and text[j] != '"': j += 1
            if j < len(text):
                inner = text[i+1:j]
                fixed = inner.replace('。', '，')
                if fixed and fixed[-1] == '，': fixed = fixed[:-1] + '。'
                result.append('"' + fixed + '"'); i = j + 1
        else: result.append(text[i]); i += 1
    return ''.join(result)
```

### Phase 3: Paragraph-Level Comma Flow

Replace all internal `。` with `，` across all paragraphs, keeping only the LAST period per paragraph (or the one before closing `"`):

```python
def fix_internal_periods(text):
    for line in text.split('\n'):
        s = line.strip()
        if not s: continue
        periods = [m.start() for m in re.finditer('。', s)]
        if len(periods) <= 1: continue
        # Keep rightmost 。that is at end or before closing "
        keep = None
        for p in reversed(periods):
            after = s[p+1:].strip()
            if not after or (after.startswith('"') and len(after) <= 2): keep = p; break
        if keep is None: keep = periods[-1]
        # Replace all others
        chars = list(s)
        for p in periods:
            if p != keep: chars[p] = '，'
```

### Phase 4: Deep Semantic Resegmentation

For chapters still below ~35 paragraphs after Phase 1-3, read manually and split at semantic boundaries:

1. **Time jumps**: `第二天`, `当天晚上`, `傍晚`, `临走前` → new paragraph
2. **Location changes**: `回到客栈`, `走上山坡`, `进了军务处` → new paragraph  
3. **Character switches**: Different character acting/speaking → new paragraph
4. **Event phase changes**: `他把辞呈交到...`, `陆辰还没来得及回答...` → new paragraph
5. **Emotion/topic shifts**: Reflection → action, despair → hope → new paragraph

### Phase 5: Deduplication

Scan for duplicate paragraphs (common in chapters from multi-session creation):
```python
seen = set()
for p in paras:
    key = p[:60]  # first 60 chars as fingerprint
    if key not in seen: seen.add(key); keep(p)
```

## Verification

Run `python3 scripts/verify-paragraphs.py <volume_dir>` for a complete batch scan showing paragraphs, CJK, dialogue splits, multi-period segments, and em dashes per chapter.

After every batch, verify:
```python
body = [l for l in text.split('\n') if l.strip() and not l.startswith('*第') and not l.strip().startswith('第0')]
splits = sum(1 for p in body if p.count('"') % 2 != 0)  # MUST be 0
multi_period = sum(1 for p in body if p.count('。') > 1)  # MUST be 0
cjk = len(re.findall(r'[\u4e00-\u9fff]', text))  # MUST be >= 2000
```

Target: 50-65 paragraphs for ~2200 CJK. 0 dialogue splits. 0 multi-period paragraphs.

## V1 120-Chapter Full Validation (2026-05-20, COMPLETE)

Entire Volume 1 (120 chapters) processed end-to-end. Final results:

```
批次       章节      处理前→后段      操作
001-029    原生      48-88段 ✅      无需处理
030-058    裂引号    17-93段→18-67   合并436处裂引号+句号→逗号
059-060    原生      27-26段 ✅      无需处理  
061-070    深度      12-42段→18-38   去重(多章有重复段)+补字+语义分段
071-080    深度      13-42段→23-63   大段拆分+语义分段
081-090    深度      12-15段→12-19   短章分段+去重(081-082补CJK)
091-100    轻量      17-23段→14-20   轻量分段+修复(100章编号错误)
101-120    轻量      26-40段→31-37   轻量分段(原已较好,去---)
```

**Final V1 metrics**: 120章 | 4,568段 | 266,238 CJK | 均38段/章 | CJK均2,219
**Quality gates**: 裂引号0 | 破折号0 | CJK<2000:0 | 最低CJK:2002(107章)
**Benchmark**: 001章=65段/2074CJK

Key observations:
- Chapters 001-060: already well-segmented (30-88段), needed only dialogue fix
- Chapters 061-080: severely under-segmented (12-42段→18-63段), deep resegmentation
- Chapters 081-100: naturally short chapters (~2100 CJK, 12-23段), limited improvement ceiling
- Chapters 101-120: already decent (26-40段), light touch-up only
- 8,603 internal periods converted to commas across all 120 chapters

**Remaining**: Volumes 2-5 (515 chapters) await same processing.

## V2 Progress (中土纪元 第二卷·浴血中土, 2026-05-19)

Batches 1-3 (121-150) processed. Heavy template pollution found across all chapters — see `references/template-dedup-workflow.md`.

| Batch | Chapters | 段数 | CJK | 均段 | 均CJK |
|-------|----------|------|-----|------|-------|
| B1 | 121-130 | 311 | 21,137 | 31.1 | 2,114 |
| B2 | 131-140 | 293 | 21,686 | 29.3 | 2,169 |
| B3 | 141-150 | 185 | 24,339 | 18.5 | 2,434 |

Key findings:
- B1-B2: Moderate欠分段, chapters reached 26-41段 after deep segmentation
- B3: Heaviest template pollution. 141-143 needed 3-4 expansion rounds each after dedup. 144-150 received regex-only cleanup (15-19段, still dense) — may need deeper segmentation pass.

## Pitfalls

- **Mechanical period-splitting destroys dialogue (V1 VALIDATED, 29章)**: V1 chapters 030-058 had 436 dialogue splits after a prior "fix" that split at every `。`. Root cause: the prior script split EVERY paragraph at every period, fracturing dialogue into fragments where one character's speech was spread across 3-7 separate paragraphs. The three-phase fix (merge→punctuation→internal-periods) repaired all 29 chapters. **NEVER split a paragraph mechanically at periods — always check for semantic boundaries first.**
- **Dedup can drop CJK below 2000**: Chapters 061-064 lost ~150 CJK each from removing duplicates (common in multi-session chapters). Budget expansion after dedup. V1 confirmed: 061(1908), 062(1902), 063(1918), 064(1896) all dipped after deduplication, requiring ~100 CJK story-content expansion each.
- **Deep segmentation is manual**: 2-3 minutes per chapter to read and identify semantic break points. Plan batch sizes accordingly (10 chapters = ~25 minutes). V1 throughput: ~10 chapters/hour when doing full deep resegmentation.
- **Don't split within a single speaker's dialogue**: Even if a character's speech is 200+ CJK chars, it remains ONE paragraph. Commas (，) connect clauses; the paragraph break itself marks the end of their speech.
- **Chapters 081+ are structurally shorter**: V1 chapters 081-120 average ~2100 CJK with 12-15 original paragraphs. Post-segmentation they reach only 12-20 paragraphs (vs 50-65 benchmark). These chapters may need content expansion beyond segmentation to achieve target paragraph density.
