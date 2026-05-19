# 四阶段弧线全面审查模式 (Four-Phase Arc Review)

Comprehensive review methodology for auditing completed arcs. Run after all chapters in an arc pass the CJK word-count gate. Covers format, outline compliance, logic chain, and story quality in sequence.

## When to Use

After every arc completion, after the CJK+keyword combined audit passes. This is the qualitative review layer on top of the quantitative audit.

## Phase 1: Format Scan

### 1a. Em-Dash Scan (`——`)
```python
dashes = content.count('——')
```
Target: ZERO in narrative text. Only `——` inside structured records (科目002-庚, 航海日志) are exempt.

### 1b. Dialogue Quote Format Scan
Check TWO types of quote issues:
```python
left_q = content.count('\u201c')   # Chinese left quote "
right_q = content.count('\u201d')  # Chinese right quote "
straight = content.count('"')      # English straight quotes — WRONG
```
- `straight > 0` → chapters using `"..."` instead of `"..."` — requires conversion
- `abs(left_q - right_q) > 2` → unbalanced quotes — possible corruption

**Batch conversion technique (state machine)**:
```python
result = []
in_quote = False
for ch in content:
    if ch == '"':
        if not in_quote:
            result.append('\u201c')  # "
            in_quote = True
        else:
            result.append('\u201d')  # "
            in_quote = False
    else:
        result.append(ch)
new_content = ''.join(result)
```
After conversion, verify `left_q == right_q` for every chapter — unbalanced counts signal a bug.

### 1c. Internal Chapter Numbering (POST-REORGANIZATION)
After bulk chapter reorganization, internal numbers may not match filenames:
```python
import re, os, glob
vol_dir = '/path/to/volume'
for f in sorted(glob.glob(f'{vol_dir}/第*.txt')):
    fname = os.path.basename(f)
    expected_num = re.search(r'第(\d+)章', fname).group(1)
    with open(f, 'r') as fh:
        first_line = fh.readline().strip()
    actual = re.search(r'第(\d+)章', first_line)
    if actual and actual.group(1) != expected_num:
        print(f"  ❌ {fname} → 内部标注为 第{actual.group(1)}章")
```

### 1d. Chapter End Marker Verification
After fixing first-line numbers, the CHAPTER END markers (`*第X章·完*`) may still carry old numbers — especially when old numbering used Chinese numerals (第十一章, 第二十章). This is a SEPARATE problem from 1c.

**Detection**:
```python
# Check last 400 chars for end marker
tail = content[-400:]
end_match = re.search(r'\*第(\S+)章·完\*', tail)
```

**Chinese numeral → Arabic mapping** needed for chapters 1-99:
```python
cn_map = {
    '一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,
    '十':10,'十一':11,'十二':12,'十三':13,'十四':14,'十五':15,
    '十六':16,'十七':17,'十八':18,'十九':19,'二十':20,
    '二十一':21,'二十二':22,'二十三':23,'二十四':24,'二十五':25,
    '二十六':26,'二十七':27,'二十八':28,'二十九':29,'三十':30,
    '三十一':31,'三十二':32,'三十三':33,'三十四':34,'三十五':35,
    '三十六':36,'三十七':37,'三十八':38,'三十九':39,'四十':40,
}
```

**Fix**: for every chapter, if end marker number ≠ actual chapter number, replace. Standardize to three-digit Arabic format `*第NNN章·完*` for consistency.

### 1e. Meta-Narrative & Arc Label Residue Scan
After fixing format issues, scan for residual meta-narrative markers that survived the initial cleanup:
```python
# Arc/volume labels in body text (NOT in end markers)
meta = re.findall(r'第[一二三四五六七八九十\d]+[阶段弧线卷]', body)
arc_labels = re.findall(r'第[一二三四五]弧线「[^」]*」', body)
```
Also check end markers for trailing pipe artifacts: `*第090章·完 | ` → `*第090章·完*`

### 1f. Deep Sweep — 9-Point Final Scan (RUN AFTER ALL FIXES)
After fixing the obvious issues (quotes, numbers, dashes), run this comprehensive check BEFORE reporting "done". The user will ask "看看还有什么问题" — this scan preempts that.

```python
checks = {
    '破折号——': content.count('——'),
    '英文引号': content.count('"'),
    '首行编号不一致': (first_line_num != expected_num),
    '章末编号不一致': (end_marker_num != expected_num),
    '元叙事残留': bool(re.findall(r'第[一二三四五六七八九十\d]+[阶段弧线卷]', body)),
    '弧线标注残留': bool(re.findall(r'第[一二三四五]弧线「[^」]*」', body)),
    '外观描写超标': any(len(desc) > 50 for desc in appearance_descriptions),
    'AI词汇超标': sum(content.count(w) for w in ai_words) > 3,
    '超长段落(>500字)': any(len(p) > 500 for p in paragraphs),
    '章节缺失': not file_exists,
}
```
Report as a table with ✅/❌ per dimension. Target: all ✅.

**CRITICAL**: The first pass of fixes (quotes, first-line numbers) often reveals SECOND-ORDER issues (end markers, meta labels, trailing pipes). The two-pass pattern is: fix Phase 1a-1c → re-scan → fix Phase 1d-1e → 9-point final sweep. Do NOT report "done" after just the first pass.
## Phase 2: Outline Compliance

Sample 2-3 chapters per arc for content-to-outline mapping. Check:
- Title matches outline
- Core content (location, characters, events) matches outline description
- Metaphor mappings are consistent

## Phase 3: Logic Chain

### 3a. Character Appearance Tracking
Track first appearance of each named character across all chapters:
```python
names_to_check = ['陆辰', '老陈', '江寒', '苏大姐', '顾明远', ...]
first_appear = {}
for f in sorted(chapter_files):
    with open(f, 'r') as fh:
        content = fh.read()
    ch_num = re.search(r'第(\d+)章', os.path.basename(f)).group(1)
    for name in names_to_check:
        if name in content and name not in first_appear:
            first_appear[name] = ch_num
```
Compare against outline expectations. Early appearances (伏笔) are acceptable; missing appearances are not.

### 3b. Arc Transition Continuity
Check the last 500 chars of chapter N and first 500 chars of chapter N+1 at arc boundaries. Verify:
- No jarring scene jumps
- Time/place continuity is maintained
- End markers are present

### 3c. Metaphor Mapping Consistency
Track key terms across arc ranges to verify they appear where expected:
```python
term = '归码'  # or 瀛烬, 暗河, 星火盟, etc.
arcs = [(1,20), (21,40), (41,65), (66,90)]
for start, end in arcs:
    count = 0
    for i in range(start, end+1):
        # check if term appears in chapter i
```

## Phase 4: Story Quality

### 4a. Dialogue Density
Count Chinese quote marks per chapter. Very low dialogue density in later arc chapters may indicate pacing issues.

### 4b. Sensory Anchoring
Count sensory terms per chapter: `风|雨|光|暗|冷|热|汗|血|烟|火|味|声|响`

### 4c. Action Verb Density
Count action verbs: `站起|转身|拔出|挥|砍|踢|冲|跑|跳`

### 4d. Cliffhanger Presence
Check last 300 chars for suspense markers: `他不知道|还没意识到|即将|正在这时|突然`

### 4e. Character Arc Continuity
Build a presence matrix: which characters appear in which arcs? Gaps may indicate underutilization.

## Phase 5: Volume-End Link Check

When a review covers the last chapter of a volume, verify it has a proper bridge to the next volume — NOT just thematic closure:

**Required elements in volume-final chapter**:
1. Protagonist closes/archives a recording artifact (notebook, logbook, map)
2. Artifact is labeled with the volume number ("第一卷")
3. Glance toward the next phase's geography/threat direction
4. Recurring motif (归码/灯/炭条) used as transition symbol
5. Explicit statement: "第X卷将从这里开始" + unresolved motif ("归码还没有刻完")

**Anti-pattern**: Chapter ending that is purely thematic ("野草从废墟中生长") without narrative bridge. This reads as a series finale, not a volume transition.

**Detection script**:
```python
# Check volume-final chapter for link elements
tail = content[-800:]
has_archive = bool(re.search(r'(合上|放进|归档|标签)', tail))
has_volume_label = '第' in tail and '卷' in tail  
has_forward_gaze = bool(re.search(r'(望去|方向|远处|下一)', tail))
has_motif_bridge = bool(re.search(r'(归码|灯|炭条|暗河|石子)', tail))
# All four should be present for a proper volume transition
```

## Post-Expansion Cleanup Checklist (BATCH OPERATIONS)

After ANY batch expansion via `execute_code`, run this atomic cleanup BEFORE reporting:

```python
# 1. Remove em dashes introduced by expansion text
content = content.replace('\u2014\u2014', '\uff0c').replace('\u2014', '\uff0c')

# 2. Fix English quotes introduced by expansion text
if '"' in content:
    chars = []; in_q = False
    for ch in content:
        if ch == '"':
            chars.append('\u201c' if not in_q else '\u201d'); in_q = not in_q
        else: chars.append(ch)
    content = ''.join(chars)

# 3. Remove trailing pipe artifacts from meta-label cleanup
content = re.sub(r'\|\s*\*', '*', content)
content = re.sub(r'\| $', '', content)

# 4. Detect and deduplicate repeated filler text
# (e.g., "风从暗河方向..." repeated 3x from final-push pattern)
repeats = re.findall(r'((.{20,})\2{2,})', content[-800:])
for dup_pattern, _ in repeats:
    content = content.replace(dup_pattern, dup_pattern[:len(dup_pattern)//3])
```

**Expansion→cleanup is an ATOMIC operation**. Never separate them — chapters that look clean before expansion will have 10-90 dashes and quotes after.
