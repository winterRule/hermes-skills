---
name: novel-writing
description: "Write novel chapters from an outline following strict word-count, structure, and style rules. For 历史穿越 novels with 双向穿越, reform arcs, and multi-volume structure."
version: 1.45.0
author: Hermes Agent
tags: [novel, writing, chinese, historical, time-travel, outline-driven]
---

# Novel Writing (小说创作)

Write novel chapters from a pre-written outline, following strict constraints on word count, structure, POV, language style, and content direction. Designed for Chinese historical time-travel web novels with 双向穿越 (bidirectional穿越) mechanics, reform arcs, and multi-volume structure.

## 🚨 WRITE GATE — 5 SECOND SCAN (read before every write_file)

**EVERY write_file call MUST be followed by ONE execute_code call that verifies: CJK count, byte size, dash count. This is not optional. 45 chapters in this session (421-465) all needed post-hoc fixes because this gate was deferred to batch-level. The per-chapter gate costs 1 extra tool call per chapter and saves 5-10 fix calls per batch.**

**THE TWO NUMBERS THAT MATTER — check these immediately after every write_file:**

1. `CJK >= 2000` — if not, expand NOW before next chapter
2. `dashes = 0` — if not, `sed -i 's/——/, /g'` NOW before next chapter

These two numbers take one `execute_code` call to check. Skip them and you WILL pay 5-10x in post-batch fixes.

**FASTEST BATCH FIX (Arc 15-16 validated — 65 chapters, 13 batches)**: If dashes accumulated across 3+ chapters:
```bash
# One terminal call fixes ALL dashes in ALL chapters in the directory:
for f in *.txt; do sed -i 's/——/, /g' "$f"; done
# Then verify:
for f in *.txt; do echo "$f: $(grep -c '——' "$f" 2>/dev/null || echo 0)"; done
```
This is 10x faster than Python for bulk dash fixes. The sed pattern is `sed -i 's/——/, /g'` — replaces em-dash with comma+space. **Run immediately after EVERY batch of 3-5 AND after every execute_code-based expansion pass.** Expansion text via patch/execute_code ALWAYS introduces new dashes — verified across Arcs 15-16 (7 batches, ~350 dashes total, all caught post-hoc). The sed fix takes one terminal call and is the only reliable gate. Do NOT skip it hoping the chapters are clean — they never are after expansion.

**Per-chapter gate** (use when writing one chapter at a time):
```python
import re
with open(path) as f: text = f.read()
text = text.replace('——', '，')  # auto-fix dashes
flip = True; chars = list(text)
for i, c in enumerate(chars):
    if c == '"': chars[i] = '\u201c' if flip else '\u201d'; flip = not flip
text = ''.join(chars)
text = re.sub(r'(?<=[\u4e00-\u9fff]), ', '\uff0c', text)
text = re.sub(r', ', '\uff0c', text)
text = re.sub(r'(?<=[\u4e00-\u9fff]): ', '\uff1a', text)
text = re.sub(r'(?<=[\u4e00-\u9fff]); ', '\uff1b', text)
text = re.sub(r'\uff0c\uff0c+', '\uff0c', text)
text = re.sub(r'\u3002\u3002+', '\u3002', text)
cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
sz = len(text.encode('utf-8'))
with open(path, 'w') as f: f.write(text)
print(f"CJK={cjk} bytes={sz} dashes=0")
# If CJK<2000 or sz<7000: EXPAND NOW before next chapter
```

After batch of 3-5: run 5-dimension audit → ALL PASS → THEN report → THEN ask "continue?"

**Why this gate**: Arc 13 batches 2-5 accumulated 146 dashes + Arc 14 batch 1 added 28 = 174 dashes across 6 batches. Arc 15: 301 dashes across 30 chapters (6 batches), all fixed post-hoc via sed. Every dash was avoidable with batch-level or per-chapter sed fix before audit.

**Why this gate**: Arc 13 batches 2-5 accumulated 146 dashes + Arc 14 batch 1 added 28 more = 174 total across 6 batches. Arc 14 batch 2: 53 dashes across 5 chapters. Every single dash was avoidable with per-chapter verify. First-draft bytes consistently 4000-5600 (1200-1700 CJK) when 8000+ was the target. Arc 14 batch 1: all 5 chapters 1227-1630 CJK — worst first-draft performance in the entire project. Arc 14 batch 2: 1243-1652 CJK, second-worst.

📋 **Pre-batch 15-second scan**: see `references/pre-batch-checklist.md` — the scannable version of this gate.

## Triggers

**MANDATORY**: Load this skill with `skill_view(name='novel-writing')` BEFORE writing a single word of any novel chapter. The memory system already says "创作时加载novel-writing技能获取完整规则和工作流" — this is not a suggestion. The skill contains byte-count gates, per-chapter structure rules, expansion techniques, and audit workflows that prevent the most expensive session failures (17+ short chapters requiring hours of rework).

Use this skill when the user asks you to:
- Continue writing novel chapters from where they left off
- Write chapters following an outline (大纲)
- Write in arcs (弧线) of ~10 chapters at a time
- Create novel content with strict word-count enforcement
- Start a new novel from a prompt

## Novel Types

### Type A: 历史穿越 with 双向穿越
- Protagonist travels back and forth between ancient and modern worlds
- Modern knowledge → ancient reform is the core loop
- Rules in `references/permanent-rules.md` apply fully

### Type B: 隐喻历史小说 (Metaphor Historical)
- Protagonist穿越进一个架空大陆，该大陆是真实历史的隐喻映射
- One-way穿越 (魂穿) — no return, no bidirectional travel
- The fantasy world's factions and events mirror real historical forces (e.g., 1911–1949)
- Rules in the novel's own 大纲 take precedence over `references/permanent-rules.md`
- See `references/metaphor-novel-guide.md` for the full pattern

### Arc Sub-Types

**Battle Arc (战斗弧线)**: Large-scale military campaigns across distinct terrain types (mountain, water, stone pass, plains). The antagonist is瀛烬 military forces. Climax is a battle. Closure symbol is geometric/directional (全圈偏北, 水中悬浮点, 明天, 还在).

**Political Transition Arc (政治过渡弧线)**: Post-war or inter-battle arcs where the conflict is institutional/political rather than military. The antagonist is bureaucracy (公章, 征税通知, 军法条例). Climax is a threshold event (第一枪打偏). Closure symbol is open-ended (裂缝, 暗流). See `references/political-transition-arcs.md` for patterns, techniques, pitfalls, and antagonist treatment rules — especially the 赵元朗 complexity rule (must NOT be a cartoon villain).

## Permanent Rules

### 字数铁律 (Word Count)
1. 全书总字数: 150万字整 (strict total)
2. 单章字数: 硬地板2000字，上限可超过3000字
3. 全书结构: 4–5卷, no增减
4. 禁止水字、禁止重复、禁止凑字数、禁止省略关键情节

### 核心设定 (Core Setting)
1. 模式: 双向穿越 — 明朝皇帝 ↔ 现代影视城
2. 主线: 现代学习知识 → 带回古代全面改造
3. 风格: 喜剧碰撞 + 硬核权谋 + 写实改革 + 文化反思
4. 无系统、无空间、无异能、无玄幻

### 内容方向 (Content Direction)
1. 现代线: 剧组生活、拍戏、查资料、学科技、搞图纸、收集工具
2. 古代线: 朝堂制衡、吏治、军事、经济、民生、文化、教育全面改革
3. 必须覆盖: 军事、经济、民生、文化、制度五大改造方向
4. 改革循序渐进，符合历史逻辑

### 输出格式 (Output Format)
1. 每章完整、有头有尾、有冲突、有推进
2. 语言: 皇帝古风庄重，现代口语自然
3. 剧情双线并行，现代与古代来回切换
4. 每章自检: 字数、设定、主线、逻辑

### 段落格式铁律 (USER-ENFORCED SINCE 2026-05-17)

**多分段，短段落。** 小说不是论文，不需要长段。对标第001章：65段/2074CJK。

**一、对话铁律 (USER-ENFORCED 2026-05-20)**

1. **一人一段**：一个人说的所有话 = 一个段落。不论多长，同一个人说的话不能拆成多段。
2. **对话内逗号**：子句之间用逗号（，）连接，只有最后一句用句号（。）收尾。禁止对话内部全是句号。
3. **禁止机械按句号分段**：绝不能看到句号就分段。必须先判断语义边界（时间/地点/人物/事件阶段是否变化），只有语义变了才能分段。
4. **引号不跨段**：一对引号 `"..."` 必须在同一段内闭合。裂引号（上段开引号、下段关引号）是格式硬伤。

修复工具：`scripts/fix-dialogue-splits.py` — 合并碎片对话、内部句号改逗号、保留末句句号。第一卷验证：29章436处裂引号→0。

**二、段落内逗号流 (USER-ENFORCED 2026-05-20)**

段落是完整语义流。**段落内部所有子句用逗号（，）连接，句号（。）只在段末收束。** 段落之间的空行就是最强停顿，段落内不需要句号打断。此规则适用于对话段落和叙事段落。

修复工具：`scripts/fix-internal-periods.py` — 段落内除最后一个句号外全部替换为逗号。第一卷验证：120章8,603处句号→逗号。

**三、语义分段口诀**

时间变、地点变，事情阶段变；内容换、感情换，总分结构看。一段讲一个意思，意思变了就分段。

**四、段落长度与节奏**

1. 每段3-5句为宜，最长不超过8句。超过8句的段落必须拆分。
2. 场景切换即分段：人物切换、位置切换、时间切换 → 换段。
3. 动作与对话可合并（同一人），不同人的话必须在不同段。
4. 禁止两段以上连续长度超过8句的长段落。
5. 原因/经过/结果各一段。叙事段落1-2句为主，对话不超过3句。

**注意**：多分段会降低byte/CJK比率。同样的CJK内容，分段多的章节byte数更低。因此多分段创作时，8000+ bytes目标更关键——分段后的5500 bytes可能只有1400 CJK（而密集段落下5500 bytes ≈ 1650 CJK）。**Arc 15实测**：4922 bytes → 1441 CJK（比率3.41），6350 bytes → 1877 CJK（比率3.38）。多分段模式下，byte目标建议维持8000+不变，并每次写完后立即用CJK-count验证而非依赖byte估算。

## Agent Constraints (USER-ENFORCED 2026-05-17)

The user established these constraints to govern agent behavior during novel creation/editing. Violating any of them triggers immediate correction and wastes session time.

### 1. Outline-First (大纲优先)
- Before writing ANY chapter, locate the outline file and confirm the chapter's expected title and content要点
- Chapter titles must match the outline character-for-character
- Content expansion must be based on outline要点, never deviate
- If multiple outline versions exist (files titled differently from the official outline), the single merged authoritative outline (`全书大纲_完整版_v5_终极合并版.txt`) takes precedence. Delete intermediate supplement files after merging.

### 2. Batch Progression (分批推进) & Re-Segmentation (重分段)
- Process ONE arc or ONE batch (≤10 chapters) at a time
- **重新分段时的四步工作流（USER-ENFORCED 2026-05-19）**：分段 → 五维审计 → 修复 → 汇报五维。不可跳步。
- Complete batch → audit → report → WAIT for user confirmation → next batch
- Never jump ahead to other chapters without approval
- Never start fixing a later section while the current batch is incomplete
- For inherited chapters needing re-segmentation, see `references/batch-resegmentation-workflow.md` for the full dedup→segment→expand→audit pattern

### 3. Five-Dimension Audit Per Batch (六维审计·每批必做·不可跳过) — UPGRADED to 6-dimension v4.0

**MANDATORY GATE**: After EVERY batch (10 chapters), run the six-dimension audit BEFORE reporting completion:

1. **技术审计**: CJK≥2000 / 零—— / 零ASCII引号 / 中文引号平衡
2. **大纲对位**: 逐章对位大纲要点，标题一字不差
3. **逻辑链**: 前后因果衔接、时间线闭合、物码体系一致
4. **故事性**: 节奏张弛/情感冲击/细节密度/视角切换/主题统御
5. **衔接点**: 新章与前文≥3处明确衔接
6. **分段质量**: 逗号流「，，，。」零内部句号违规 / 禁止模式(。。 ，， 。， ，。)全零 / 段数40-65 / 零机械句号拆分痕迹

六维全通过方可汇报"通过"。任一维不达标立即修复后再审。
```
python3 scripts/audit.py <range> --volume <path> [--sentiment] [--full]
```

This script checks ALL of: CJK word count, em-dashes, ASCII quotes, curly-quote balance, end markers, meta-narrative, and line-number artifacts. It also optionally runs sentiment density analysis. See `scripts/audit.py` for the full implementation (portable to any novel project).

For a browser-viewable HTML report with Chart.js trend graphs, use `python3 tools/audit_html.py <range>` — generates a dark-themed interactive audit dashboard. See `references/support-tools.md`.

**WORKFLOW ORDER**: Write chapters → Expand shorts → Run audit.py → Fix all issues → Re-run audit.py → ALL PASS → THEN report. Do NOT report "done" while audit.py shows failures. Presenting short chapters as "complete" wastes the user's time and forces re-issuance of instructions.

**Five dimensions** (audit.py covers dimensions 1 and 2 automatically; dimensions 3-5 require qualitative analysis):
- **字数+格式 (audit.py)**: Every chapter ≥ 2000 CJK, zero `——`, zero ASCII `"`, curly-quote balance, end marker present.
- **大纲对位 (Outline Alignment)**: Content matches expected themes/keywords per chapter. Use audit.py `--keywords` mode or manual keyword scan.
- **逻辑链 (Logic Chain)**: Causal chain clear across the 10-chapter arc, timeline consistent, no chapter repeats previous beat.
- **故事性 (Story Quality)**: Thematic unity, sensory anchoring, character interiority,物码 continuity. Use audit.py `--sentiment` to detect chapters with N=0 (zero negative sentiment — likely lacks conflict).
- **衔接点 (Continuity Links)**: Every new chapter MUST have explicit connection points to PREVIOUS chapters (prior arc or prior batch). Check: character carryover, 物码 (object) carryover, plot thread carryover, time window consistency. List at least 3 concrete衔接点 per chapter in the audit report. Chapters with zero衔接点 are不合格 — same severity as CJK<2000 or dashes>0. **(USER-ENFORCED 2026-05-15: "新创作的章节内容，需要与前文有衔接点，按这条再审查一下")**

For detailed assessment criteria — including the five sub-dimensions of故事性 (pace/emotion/density/POV/theme) and the quantified衔接点 scoring rubric — see `references/five-dimension-audit.md`.

### 4. Format Iron Rules (格式铁律)
- Zero `——` em-dashes in narrative prose (structured records excepted)
- Zero ASCII straight quotes `"` — only Chinese curly quotes `""`
- **内心独白/自语使用「」角括号**（ARC 15 VALIDATED: 用户将"手还有"修正为「手还有」）——角色不出声的内心想法、自语对话用「」，出声的对话用""
- Zero meta-narrative (`第X弧线`, `第X卷` in narrative voice)
- Internal chapter number MUST match file number
- Every chapter ≥ 2000 CJK characters

### 5. Context Bridging (上下文衔接)
- Before writing a new chapter, read the FULL preceding 2 chapters AND following 2 chapters (if they exist)
- Character behavior, timeline markers, and locations must be consistent with surrounding chapters
- Series-named chapters (e.g., `苏大姐的日志（二）`) must verify the preceding numbered entry exists

### 6. Old File Cleanup
- When rewriting chapters with new titles matching the official outline, DELETE old files with mismatched titles
- Use `rm -v` to confirm removal
- Scan for filename conflicts after every batch rewrite

## Workflow

### Two Modes
- Mode A (Batch): Write 10-chapter arc, then audit. Default.
- Mode B (Per-Chapter Gate): Write one chapter, check word count + logic, fix if below 2000. Only proceed when it passes.

### Starting a New Novel
1. Wait for the "开始创作" signal from the user
2. Create project skeleton: 大纲, 人物人设, first 3 chapters, 支线剧情大纲
3. Respect the prompt's embedded rules; don't apply rules from other novels

### Continuing an Existing Novel
1. VERIFY directory path (WSL: `/mnt/d/sideline/ai/novel/{书名}/`)
2. **INHERITED VOLUME CHECK (新增)**: If the target volume was NOT written in the current session, run a Phase 0 corruption scan BEFORE any segmentation work. Inherited volumes from prior bulk-generation sessions frequently carry systemic corruption: intra-chapter duplication (same paragraph repeated 5-10x), cross-chapter template pollution (identical blocks in multiple chapters), `|---|` separators, and line-number prefixes. See `references/inherited-volume-segmentation.md` for the detection script and repair workflow. Skipping this scan inflates CJK counts by 400-600 per chapter and wastes expansion effort on content that will be deduplicated later.
3. **OUTLINE COVERAGE CHECK** (unchanged below)
3. **MANDATORY: Review previous arc's first-draft byte sizes.** Run `execute_code` to check the byte sizes of the last arc's chapters AS FIRST WRITTEN (before expansion). If the average was below 7000 bytes, set an EXPLICIT numeric byte target for the new arc (e.g., "every chapter MUST be 8000+ bytes before I submit it"). State this target in the todo list. The 8000-byte rule has been restated across 5+ skill versions and continues to be missed — a concrete numerical review of the last arc's failure creates the accountability that generic rules have failed to provide. **VALIDATED (Arc 13):** When this rule was strictly followed — explicit 8000+ byte target in todo, verify every 3 chapters, expand immediately — the result was 8/10 chapters passing first draft with only 2 needing single-round expansion (vs arcs 9-12 where 6-10 chapters needed 3+ rounds). The total expansion overhead dropped from ~30 tool calls to ~2.
4. **EXPANSION ARCS (inserting chapters between existing ones) require MORE vignettes per chapter.** When filling gaps in an existing narrative (e.g., Volume 1 arcs expanded from 10→25 chapters), each new chapter covers less "plot distance" but must still hit 2000+ CJK. The default 3-5 vignettes/chapter produces 700-1600 CJK first drafts. For expansion arcs: plan 5-6 vignettes per chapter, each with a distinct character moment, physical object, and sensory detail. **VALIDATED (Arc 4, 15 chapters):** First drafts at 3-4 vignettes averaged 900-1600 CJK, requiring 4+ expansion rounds per chapter and 60+ tool calls. Increasing to 5-6 vignettes targets 2500+ CJK on first draft.
4. **MANDATORY: Review previous arc's first-draft byte sizes.** Run `execute_code` to check the byte sizes of the last arc's chapters AS FIRST WRITTEN (before expansion). If the average was below 7000 bytes, set an EXPLICIT numeric byte target for the new arc (e.g., "every chapter MUST be 8000+ bytes before I submit it"). State this target in the todo list. The 8000-byte rule has been restated across 5+ skill versions and continues to be missed — a concrete numerical review of the last arc's failure creates the accountability that generic rules have failed to provide. **VALIDATED (Arc 13):** When this rule was strictly followed — explicit 8000+ byte target in todo, verify every 3 chapters, expand immediately — the result was 8/10 chapters passing first draft with only 2 needing single-round expansion (vs arcs 9-12 where 6-10 chapters needed 3+ rounds). The total expansion overhead dropped from ~30 tool calls to ~2.
5. Plan the arc, create todo list with the byte target as a checklist item. **If the outline for the current volume is sparse** (only arc names and themes, no per-chapter detail — common in Volumes 3-5), see `references/sparse-outline-volumes.md` for the planning pattern: extract themes → map to historical battles/events → create 10-chapter breakdown → ensure continuity with existing character arcs and物码体系.
6. **After writing each batch of 3 chapters, immediately verify ALL THREE with `execute_code` CJK count.** If any chapter is below 2000 CJK, expand it BEFORE writing the next batch. Do not defer expansion to the end of the arc — deferral creates 10-chapter death spirals (arcs 9-12 all required 3+ rounds of expansion because all 10 chapters were short).

7. **POST-WRITE VERIFICATION (PER-CHAPTER GATE, HARDENED 2026-05-15 — 57 dashes in one batch when skipped)**

**After EVERY `write_file` or `patch` call on a novel chapter**, immediately run the quick-verify script:
```
python3 scripts/quick-verify.py <chapter_file>
```
This auto-fixes em-dashes (`——`→`，`) and ASCII quotes (state-machine → `""`), then reports CJK, bytes, and quote balance. If CJK < 2000 or bytes < 7000, expand NOW. If dashes > 0 in the report, the auto-fix applied — re-verify.

**Batch of 3 pattern**: write 3 chapters → run quick-verify on all 3 in one call → fix any remaining issues → write next 3. This prevents the accumulation of 50+ dashes across a 5+ chapter batch (Arc 13 batch 4: 57 dashes across 5 chapters, all fixed post-hoc at 5x the cost).

### Per-Chapter Structure

**Type A (历史穿越): 四段式**
1. Opening Hook (300-500字), 2. Plot + Knowledge (800-1200字), 3. Climax (300-400字), 4. Ending + Hook (300-500字)

**Type B (隐喻历史): 场景驱动式**
- No rigid four-part structure. Chapters are built from interconnected vignettes/scenes, each centered on a character moment or sensory observation.
- Each vignette must include: physical detail (place, object, body), character interiority (what they feel/remember/decide), and one sensory anchor (sound, touch, smell).
- Chapters resolve with atmospheric closure — not a cliffhanger, but a resonant image or phrase that echoes the chapter's emotional core and threads back to earlier chapters' motifs (灰瓷罐, 炭条, 三角, 竖杠).
- Transitions between vignettes use parallel cutting (simultaneous action across locations/characters) or motif-linking (same object/symbol passing through different hands).
- **Vignette count by chapter type** (VALIDATED Arcs 15-16, 65 chapters):
  - **Battle chapters** (战斗场面, tactical POV, multiple combat angles): 3-4 vignettes → naturally 2000+ CJK
  - **Aftermath/quiet chapters** (战后收束, 单人反思, 归来, 和平第一动作): 3-4 vignettes → ONLY 1200-1600 CJK on first draft. **MUST plan 5-6 vignettes upfront** or budget 2-3 expansion rounds. Arc 16 chapters 401-410 all needed 2-3 rounds of expansion — the quiet, reflective tone does not reduce the required word count, it just makes each vignette "feel" complete sooner. Over-plan vignettes to compensate.
  - See `references/aftermath-chapter-patterns.md` for techniques and expansion budget planning.

### Before Submitting — First-Draft Length Gate

**CRITICAL**: The byte-to-CJK ratio for Chinese fiction chapters in this project is empirically **~3.3 bytes per CJK ideograph** — measured across arcs 5-6 (20 chapters / 40+ data points). This is higher than the 3.0 floor because this user's prose style uses substantial punctuation, paragraph breaks, and formatting that adds bytes without adding CJK characters. A 5000-byte chapter = ~1500 CJK characters. A 6500-byte chapter = ~1970 CJK — still borderline.

**CRITICAL**: The byte-to-CJK ratio for Chinese fiction chapters in this project is empirically **~3.3 bytes per CJK ideograph** — measured across arcs 5-6 (20 chapters / 40+ data points). This is higher than the 3.0 floor because this user's prose style uses substantial punctuation, paragraph breaks, and formatting that adds bytes without adding CJK characters. A 5000-byte chapter = ~1500 CJK characters. A 6500-byte chapter = ~1970 CJK — still borderline.

**FIRST-DRAFT BYTE TARGET: 8000+ bytes.** This is the only reliable way to hit 2000+ CJK on the first attempt. Chapters at 8000-9000 bytes consistently yield 2400-2700 CJK characters; chapters below 5500 bytes yield 1000-1650 CJK — always a fail, triggering 3-4 rounds of expansion across all 10 chapters (30+ tool calls). FIRST DRAFTS AT 3000-5500 BYTES ARE THE SINGLE LARGEST COST DRIVER IN NOVEL WRITING SESSIONS. This target has been restated across multiple skill versions and continues to be missed.

**HARDENED RULE (Arcs 9-12, 50-chapter validation, 2026-05-26)**: Across arcs 9-11 (50 chapters), EVERY chapter written via `write_file` produced first drafts at 3,600-6,500 bytes (1,100-1,950 CJK). ZERO chapters passed 2000 CJK on first draft. The empirical data:
- 3,600-4,600 bytes → 1,100-1,400 CJK (6 chapters)
- 4,700-5,800 bytes → 1,440-1,750 CJK (15 chapters)  
- 5,800-6,500 bytes → 1,750-1,950 CJK (12 chapters)
- 7,000-7,300 bytes → 2,100-2,200 CJK (3 chapters, all passed)

The 7000-byte threshold is NOT aspirational — it's the empirical floor for 2000+ CJK first drafts. Chapters below 6500 bytes are GUARANTEED to need expansion (validated 33/33 chapters). **NEW ENFORCEMENT (2026-05-26)**: After EVERY `write_file` call, immediately run this one-liner verification via `execute_code`: `len(text.encode('utf-8'))`. If below 7000 bytes, the chapter WILL be below 2000 CJK — expand it NOW, do NOT proceed to the next chapter. Budget 2 expansion rounds per chapter. Use `references/shared-expansion-pattern.md` when 3+ chapters all need expansion.

**MANDATORY MICRO-OUTLINE BEFORE EVERY write_file CALL**: Before writing each chapter, list 4-5 distinct vignettes/scenes. Each vignette must name: (1) a specific character, (2) a physical object that character interacts with, (3) a sensory detail (sound/smell/touch/temperature). Example micro-outline:
```
V1: 刘婶 at 炊事班 — iron pot, sound of ladle scraping
V2: 老钱 in 菜地 — hoe, smell of turned soil  
V3: 韩先生 at 识字班 — chalk on blackboard, morning light on dust
V4: 民兵 at 村口 — gun barrel, cold metal against cheek
V5: 陆辰 alone at night — 炭纸, scratching sound of charcoal
```
If you cannot name 4 vignettes before writing, the chapter WILL be short and WILL require 3+ expansion rounds. Write the micro-outline in your thinking block before every `write_file` call for a novel chapter.

- **Expansion budget for write_file first drafts**: When chapters are written via `write_file` (not `execute_code` batch), first drafts average 1,200-1,600 CJK — NOT the 2,000+ target. Budget 4-6 expansion rounds per batch of 5 chapters. This is NOT a failure of writing quality; it is a structural consequence of the `write_file` tool producing leaner prose than the `execute_code` batch-text approach. The solution is to accept the expansion overhead and do it systematically, not to try to compress it into fewer rounds.

- **ARC 12 vs ARC 13 — CONCRETE VALIDATION (2026-05-17, this session)**: Two arcs in same session, opposite results. Arc 12: 15 gap-fill chapters, first drafts 3,442-7,055 bytes (1,047-2,115 CJK), ALL 9 new chapters needed 3-round expansion, ~50+ extra tool calls, ~9,000 CJK of expansion text. Arc 13 batch 1 (301-305): 5 chapters, first drafts 5,894-10,593 bytes (1,763-3,199 CJK), 4/5 passed with zero expansion, 1 needed single-round fix. Net savings: ~45 tool calls. Root cause confirmed: arc 12 chapters had 1-2 vignettes each; arc 13 had 4-5 vignettes with explicit micro-outlines (character+object+sensory per vignette). The 8000-byte first-draft target, when actually enforced, eliminates the expansion death spiral. Future arcs: mandatory 4-5 vignette micro-outline before ANY write_file call.

**Arc 13 complete-session validation (2026-05-17)**: 30 chapters written across 6 batches. Total: 65,712 CJK, ch avg 2,190. 122+ dashes accumulated and fixed post-hoc because per-chapter quick-verify was NOT used. When the per-chapter gate was skipped, each 5-chapter batch needed 5-15 post-hoc fix calls. Total fix overhead: ~40 tool calls across 6 batches. Had quick-verify been used after each write_file, the dash/quotes overhead would have been ZERO — all dashes and ASCII quotes auto-fixed at write time. The CJK expansion overhead (4 chapters below 2000) would still exist but be caught immediately rather than at batch-end audit.

**This session validates**: the skill's per-chapter gate is correct and the quick-verify script works — the failure was execution discipline. If you find yourself writing a batch of 5 chapters and then running `grep` or `python3 -c` to find dashes, you already lost. Run `python3 scripts/quick-verify.py <file>` after EVERY write_file.

The contrast with arcs 9-12 (all required 3+ rounds) proves that the review→commit→verify-every-3 pattern works when executed, not just stated.

**MANDATORY SELF-CHECK BEFORE SUBMITTING EACH CHAPTER**: After writing, check the byte size IMMEDIATELY with `len(text.encode('utf-8'))`. If below 7000: expand the chapter before declaring it done. Do NOT submit a chapter below 7000 bytes — it will be 1000-1800 CJK and trigger the expansion death spiral. Add 3-4 more paragraphs (vignettes, sensory detail, character interiority) until the file crosses 7000 bytes, then verify with CJK count.

Use `execute_code` with Python `re.findall(r'[\u4e00-\u9fff]', text)` for reliable character counting. NEVER rely on `wc -c` alone for the final gate — it systematically overestimates CJK word count.

Byte-count quick-gate (based on empirical 3.3 ratio, for initial draft pass):
- < 5500 bytes: DEFINITELY under 2000字 (~1650 max). Expand immediately, don't count.
- 5500-7000: Likely 1650-2100字. Count with Python. Expand if below 2000.
- 7000-8000: Likely 2100-2400字. Verify with Python — could still dip below 2000 if prose has heavy paragraph breaks.
- \> 8000: Solid chance of 2400+. Still verify.

**First-draft checklist**: BEFORE writing, mentally outline 3-4 distinct scenes/character moments (not just 1-2). Each scene should have: physical description, character interiority, and one sensory detail. After writing, count paragraphs — fewer than 10 paragraphs almost always means under 2000字. Then `execute_code` CJK count AND dash count. **If dash count > 0, fix BEFORE declaring done** — batch-fix with `text.replace('——', '，')` and re-verify. Do NOT submit a chapter with any dashes; every chapter in this session's first draft had 3-9 dashes that needed post-hoc fixing. The zero-dash rule must be enforced at the chapter level, not deferred to arc-level audit.
**First-draft checklist**: BEFORE writing, mentally outline 3-4 distinct scenes/character moments (not just 1-2). Each scene should have: physical description, character interiority, and one sensory detail. After writing, count paragraphs — fewer than 10 paragraphs almost always means under 2000字. Then `execute_code` CJK count AND dash count. **If dash count > 0, fix BEFORE declaring done** — batch-fix with `text.replace('——', '，')` and re-verify. Do NOT submit a chapter with any dashes; every chapter in this session's first draft had 3-9 dashes that needed post-hoc fixing. The zero-dash rule must be enforced at the chapter level, not deferred to arc-level audit.

### After Writing the Arc — MANDATORY AUDIT (字数+大纲对位)

**WORKFLOW ORDER (USER-ENFORCED)**: Fix word count → Report progress → Run audit. Do NOT report "done" while chapters are below 2000 CJK. The user explicitly requires: "差字数一定要先补完，再汇报进度，然后进行审查". Presenting short chapters as "complete" wastes the user's time and forces them to re-issue instructions.

This is a COMBINED audit — structure, CJK word count, AND outline-alignment check run in sequence. The user explicitly requires both after every arc: "创作结束的时候需要检测，章节内容是否符合大纲符合逻辑性". Do NOT report arc completion until all three pass.

**Phase 0 — Structure Scan (RUN FIRST)**
Before counting words or checking keywords, scan every chapter for content placed AFTER the `*第X章·完*` end marker. Chapters from prior writing sessions frequently have orphaned summary paragraphs below the marker. This must be fixed FIRST because moving residue into the body changes word counts — skip this and you'll get false CJK-fail results that waste expansion effort.

Use `execute_code` with Python:
1. For each chapter: use `re.search(r'\*第.*章·完', content)` to find the marker — this handles BOTH standard (`*第171章·完*`) AND arc-final (`*第180章·完 | 第十八弧线「内战重燃」终*`) formats. The `.` wildcard is reliable; character-class patterns like `[一二三四五六七八九十百]+` may silently fail.
2. If `content[m.end():].strip() != ''` (content after marker is NON-WHITESPACE): rebuild as `before.rstrip() + '\n\n' + leftover + '\n\n' + marker`. Trailing `\n` after the marker is normal and should NOT be flagged.
3. Also scan for DUPLICATE end markers (two identical `*第X章·完*` lines) — a side effect of running expansion on already-expanded arc-final chapters
4. Re-count CJK after all structure fixes

Only proceed to Phase 1 when ALL chapters have zero content after their end markers.

Phase 1 — Full Structure Scan (internal numbering + formatting + CJK)
**New arcs only (fresh creation)**: Use `references/arc-audit-full-scan.py` — a single-pass Python script that checks ALL of: internal chapter numbers vs filenames, internal titles vs filenames, CJK word count, em dashes, English quotes, meta-narrative references, template/repetitive ending patterns, and duplicate paragraphs. This caught 7/20 chapters in Arc 8 with internal number/title drift from the creation process.

Phase 2 — Outline Keyword Alignment Scan
Use `references/arc-audit-combined.py` pattern: a Python script that:
1. Reads every chapter in the arc
2. Counts CJK ideographs with `re.findall(r'[\u4e00-\u9fff]', text)`
3. Checks keyword markers against the outline for that chapter (e.g., chapter 044 should mention "长丰"/"石浦"/"青山"; chapter 047 should mention "林文渊"/"论文"/"知识分子")
4. Prints one line per chapter: `第XXX章: ✅ XXXX字 | 大纲对齐: N/M` or `❌ XXXX字 | 缺关键词: ...`

Define keyword markers by reading the outline for each chapter and selecting 3-4 unique terms that MUST appear (character names, locations, key events). Keep the list tight — only terms that uniquely identify that chapter's content.

**Phase 3 — Expand below-2000 chapters**
7. If any chapter < 2000 CJK字: expand with `patch`, insert content BEFORE `*第X章·完*` marker
8. Re-run audit to verify all ≥ 2000

**Keyword matching is fuzzy**: "舰队" matches "战舰" for intent. Don't fail a chapter because the exact string differs — check if the *concept* is present. A 3/4 match with 2000+字 is a pass.

**Phase 4 — Story Quality Audit (USER-REQUIRED)**

The user explicitly asks for three qualitative dimensions after every arc: "是否符合大纲，是否有逻辑性，故事性怎么样". This is NOT optional — do not report arc completion without this analysis. The audit covers:

**3a. 大纲符合性 (Outline Compliance)**
- Verify all major outline themes appear (正面/敌后/民间三序列)
- Check metaphor mappings (天衡盟=国民党, 赤炬会=共产党, etc.) are consistent
- Confirm volume-level theme is served (e.g., 第三卷 "双线作战→艰苦相持")
- Flag any character betrayals of the outline's stated arc (e.g., outline says钱伯钧=汉奸 but writing developed him as hero — flag for user decision, don't silently override)

**3b. 逻辑链分析 (Logical Chain)**
- Trace the 10-chapter progression: does each chapter have a distinct function that builds on the previous?
- Draw the arc's causal chain (e.g., 情报→准备→首战→应变→双线→后勤→民间→反击→收束)
- Verify time-sync between 正面 and 敌后 storylines — do events in both lines reference the same day/causal trigger?
- Check that no chapter repeats the same beat as its predecessor without advancing

**3c. 人物弧线 (Character Arcs)**
- For each of the 7 core characters (陆辰/萧旅长/江寒/铁柱/钱伯钧/沈之默/阿来): did they appear? Did their behavior/logic advance from the previous arc?
- New characters introduced this arc: are they distinct? Do they serve a function the existing cast couldn't?
- Peripheral lines: 苏大姐日志, 韩先生识字班, 阿禾码头石子 — each must advance at least once per arc

**3d. 故事性评估 (Story Quality)**
- **Thematic unity**: What ONE concept does every chapter explore from a different angle? Identify the arc's governing theme (e.g., Arc 12 "并肩", Arc 13 "守住", Arc 14 "水"). Every chapter should be a variation on this theme.
- **物码体系 (Motif/Object System)**: Track key objects across the arc. Objects from PREVIOUS arcs must continue evolving (石子, 枯枝, 归码符号, 蓝色, 止血麻纤维, 科目002). New objects introduced this arc must have clear origin and future potential.
- **Sensory anchoring**: Each chapter should ground its emotional weight in physical sensation (temperature, texture, color, sound). Identify the arc's key sensory palette.
- **Writing technique**: Note the dominant rhetorical patterns. If a pattern becomes pervasive (e.g., "不是X——是Y" appearing 8-12 times/chapter), flag it so the user can decide whether to vary in future arcs.
- **Chapter 10 arc-closing quality**: Does the final chapter provide satisfying thematic closure while opening toward the next arc? Check: 阿来符号, 苏大姐结语, 韩先生识字, 阿禾石子, 物码闭环.

**3e. 格式合规 (Format Compliance)**
Re-run the format scan (`references/format-compliance-scan.md`): |行号, \\和\\, 多余反斜杠, 中文标点, 结束标记.

**Phase 5 — Dual-Arc Comparison (when back-to-back arcs complete)**

When two consecutive arcs in the same volume are both complete (e.g., Arcs 13-14 both done), include a comparison table covering: terrain, core weapon, enemy-rear tactic, civilian support method, closing symbol. This helps the user see how the volume's theme is explored across different battlefields. See `references/dual-arc-comparison.md` for the template.

**Phase 6 — Report**
Report only after ALL phases pass. Present the Phase 0-1 technical results as a table, then the Phase 3 qualitative analysis as structured sections. If two consecutive arcs are both freshly complete, include the Phase 4 comparison.

### Full-Volume Audit (全卷审核)

**COMPLETE WORKFLOW**: See `references/volume-completion-review.md` for the full 5-step volume completion checklist — 9-indicator format scan → outline spot-check → character arc spans → arc transitions → volume-ending hook. Validated on Volume 1 (160 chapters, 355k CJK, 6 arcs).

**PRIORITY RULE**: This user prefers **serial (串行) chapter-by-chapter checking**, NOT parallel sub-agents. Do NOT dispatch `delegate_task` calls for novel auditing OR segmentation. The user explicitly rejected subagents (\"不要用子代理处理，串行化执行\"). Instead, process chapters one at a time, in order, and report every 10 chapters with a status line. Subagents timeout on /mnt/ paths and cannot apply the user's precise formatting judgment.

#### Serial Audit Workflow (default for this user)
1. Set up a 12-item todo list (001-010, 011-020, … 111-120)
2. For each block of 10 chapters, run a Python script that checks every chapter in that block for:
   - Title format: `^第\d+章\s+\S`
   - Meta-narrative: `第\d+章` in content (excluding line 3 title)
   - Format artifacts: `^\s+\d+\|` line numbers, `\和\` patterns
   - Word count: ≥ 2000 Chinese characters
3. Print one line per chapter: `filename: XXXX字 ✅/❌`, with issue details for ❌
4. Report the 10-chapter block to the user: "011-020章：全部通过 ✅"
5. Continue to next block
6. Only proceed to fixing after ALL 120 chapters are scanned

#### Parallel Audit (only if user explicitly requests speed)
When the user accepts parallel processing, use the delegate_task pattern in `references/full-volume-audit.md`.

#### Checklist per chapter
- Word count ≥ 2000
- Outline alignment
- Logical continuity
- Setting compliance (no system/superpowers/magic)
- No `/，` artifacts
- No duplicate paragraphs
- No 4th-wall breaks (第X章 meta-narrative)
- No `|` line numbers
- No `\和\` patterns

### Format Compliance Rules (USER-ENFORCED SINCE 2026-05-16)

These rules apply to ALL novel content — both new writing and edits. After every major editing session, run a format compliance scan before reporting completion.

1. **No `|` line numbers**: Every line starting with `\s+\d+|` (e.g., `     1|text`) must be stripped. These are `cat -n` artifacts from multi-session compaction. Fix: `re.sub(r'^\s+\d+\|\s*', '', line)` on every line. Scan: `grep -rnE '^\s+[0-9]+\|' *.txt`.
2. **No `\和\` patterns**: Scan: `grep -rn '\\和\\' *.txt`. Replace with plain `和` if found.
3. **No extra backslashes**: Scan: `grep -rnE '\\\\' *.txt | grep -vE '\\\\n|\\\\\"'` to find stray backslashes not part of escaped quotes or newlines.
4. **Chinese punctuation only**: Use `，。！？：；""` not ASCII `, . ! ? : ; ""`.
5. **Content compliance**: Strictly follow the novel's metaphor settings (玄朔=满清, 瀛烬=日本, 天衡盟=国民党, 赤炬=共产党, etc.), protagonist constraints (无系统/超能力/金手指), and style (热血动漫+硬核权谋+写实战争).

### 「——」Em-Dash Overuse Rule (USER-ENFORCED SINCE 2026-05-16)

**CRITICAL**: The user explicitly rejects the dense use of `——` (em dash) as a sentence connector. This style was used heavily in Volumes 2-3 (up to 10.2/百字 in worst chapters), creating an oppressive, run-on reading experience. The user required a full 140-chapter scan and fix.

**Target frequency**: Under 2.0 per 100 CJK characters (ideally under 1.0). Volume 1 averaged 1.6/百字 — this is the acceptable baseline.

**What to do instead**:
- `X——Y——Z` chains → break into separate sentences with `。` or join with `，`
- `不是X——是Y` → `不是X，是Y` (the dash here is replaced by a comma)
- Short explanatory `——` → `：` (colon)
- Dialogue dramatic pauses → keep sparingly (1-2 per chapter maximum)

**Batch repair technique**: Use `execute_code` with a Python script that splits on `——`, categorizes each segment, and reassembles with proper punctuation. See `references/em-dash-removal.md` for the reusable script pattern.

**Manual analysis technique (USER-PREFERRED)**: When the user asks to analyze dashes chapter by chapter (「一章一章的分析」), use the four-category classification in `references/em-dash-manual-analysis.md`: A类 (修辞「不是X——是Y」→保留), B类 (解释/列举→替换为：), C类 (连接→替换为，或。), D类 (数据格式→保留). Process one chapter at a time, replace only B and C categories.

**Verification**: After every arc, run `content.count('——')` and compute frequency per 100 CJK. If any chapter exceeds 3.0/百字, fix before reporting completion.

### Paragraph Structure Rule (USER-ENFORCED SINCE 2026-05-16, REFINED 2026-05-20)

**The user requires short paragraphs and frequent paragraph breaks.** The dense, one-paragraph-per-page style used in early volumes is explicitly rejected.

**Semantic paragraphing rules** (USER-REQUIRED 2026-05-20, V1 120-chapter validated):

1. **口诀**: 时间变/地点变/事情阶段变/内容换/感情换/总分结构看。一段讲一个意思，意思变了就分段。

2. **对话铁律**: 一个人说的话 = 一个段落。A说→一段，B说→一段。对话内部用逗号（，）连接子句，段末句号（。）收束。**禁止把一个人的话拆成多个段落。**即使一段对话很长（200+ CJK），只要是一个人连续说的，就保持一段。

3. **段落内逗号流**: 段落是完整语义流，中间用逗号不用句号打断。句号仅段末收束。段落间空行=最强停顿。**禁止机械按句号分段——那是错的。**必须先判断语义边界再决定分段。

4. **引号格式**: 英文直引号 `"..."` 用于对话，禁止 `「」`。角色动作描写与话语可在同一段。不同人的话必须在不同段。

5. **目标密度**: 对标第001章（65段/2074 CJK），目标每章40-65段。低于25段的章节视为严重欠分段。低于15段的章节为不可读的文本墙。

**Three-phase repair workflow for broken chapters** (see `references/paragraph-reformatting.md`):
- Phase 1: Merge split dialogue (odd-quote paragraphs)
- Phase 2: Dialogue internal periods → commas
- Phase 3: Paragraph-level comma flow (all internal 。→，)
1. **口诀**: 时间变、地点变，事情阶段变；内容换、感情换，总分结构看。一段讲一个意思。
2. **对话铁律**: 一个人说的话 = 一个段落。A说→一段，B说→一段。对话内部用逗号（，）连接子句，段末句号（。）收束。**禁止把一个人的话拆成多个段落。**
3. **段落内逗号流**: 段落是完整语义流，中间用逗号不用句号打断。句号仅用于段末收束（或引号关闭前）。段落间空行=最强停顿。
4. **引号格式**: 英文直引号 `"..."` 用于对话，禁止 `「」`。
5. **动作+对话可合并**: 角色动作描写与他的话可在同一段。不同人的话必须在不同段。
6. **段落长度**: 每段3-5句为宜，最长不超8句。对标第001章密集分段风格（~65段/章）。
7. **禁止机械按句号分段** — 这是错的。必须先判断语义边界再分段。一人连续说话，即使很长也只算一段。

**CRITICAL PITFALL — "修复"变破坏**: 按句号机械拆分章节会把对话拆碎，产生大量裂引号（奇数引号）。上一轮V1的030-058章因按句号拆分产生了436处裂引号。正确做法：合并裂引号段落→对话内句号改逗号→全卷段落内句号改逗号（段末保留）。修复流程见 `references/paragraph-reformatting.md`。

**创作时预分段**: 写新章时直接用逗号流+短段落，避免事后修复。写完后验证：`裂引号=0, 多句号段=0, CJK≥2000`。
6. 「——」em-dash ELIMINATION RULE (USER-ENFORCED, HARDENED 2026-05-18): 「——」MUST NOT appear in narrative/descriptive/dialogue prose. Target: ZERO. The only exception is inside structured records (科目002账本 fields, 航海日志备注, 物资清单) where dashes function as field separators, not sentence connectors. VALIDATED in Arc 21 (all 10 chapters): 201-210 achieved zero dashes in narrative text. Any —— in narrative text on verification is a rewrite trigger.

7. 段落内逗号流 (USER-ENFORCED 2026-05-20, V1 120章全卷验证): 段落内部是完整语义流，用逗号（，）连接，句号（。）仅段末收束。段落间空行=最强停顿。禁止在段落中间出现多余句号打断语义。全卷验证：8,603处内部句号→逗号替换，0多句号段。适用于所有段落——叙事和对话同规则。 (USER-ENFORCED, HARDENED 2026-05-18)**: 「——」MUST NOT appear in narrative/descriptive/dialogue prose. Target: ZERO. The only exception is inside structured records (科目002账本 fields, 航海日志备注, 物资清单) where dashes function as field separators, not sentence connectors. **VALIDATED in Arc 21 (all 10 chapters)**: 201-210 achieved zero dashes in narrative text (27 total across the arc, all in科目002-庚/航海日志/密约 structured records). The technique: write every sentence as a complete unit ending with 。or ；. Never chain clauses with ——. The former "不是X——是Y" chain becomes two sentences: "不是X，是Y。" This produces cleaner prose with no CJK loss. The old ≤3 tolerance is retired. Any —— in narrative text on verification is a rewrite trigger — no exceptions.

**ZERO-DASH FIRST-DRAFT TECHNIQUE (VALIDATED Arcs 21-23, 30 chapters)**: Write first drafts using ONLY standard Chinese punctuation (，。：；「」) — no 「——」 at all. This eliminates the massive post-hoc reduction overhead (arcs 19-20 required 476 replacements across 20 chapters; Arc 18 required chapter-by-chapter manual analysis). Techniques:
- Use short complete sentences ending with 。instead of chaining clauses
- Use ：for explanatory/listing relationships  
- Use ，for simple clause joins
- For dramatic pauses: end sentence with 。and start a new one
- The "不是X——是Y" pattern becomes "不是X，是Y。" as two assertions

**VALIDATED at scale**: Arcs 21, 22, and 23 (30 chapters total) all achieved ZERO narrative dashes in natural paragraphs. Arc 21: 27 total dashes (all in 科目002-庚/航海日志 structured records), 22,959 CJK. Arc 22: 4 total dashes (all in arc-final 物码收束 structured enumerations), 21,344 CJK. Arc 23: 0 total dashes, 20,870 CJK. The zero-dash style does NOT reduce word count — chapter averages remained at 2,087-2,296 CJK. This is the ONLY acceptable style going forward. Prevention: before submitting each batch of 3 chapters, run `execute_code` to count "——" per chapter. Any —— in narrative text (outside structured records) is a rewrite trigger — no exceptions. See `references/em-dash-fix.md` for fix patterns.
7. **多分段/短段落 (USER-ENFORCED SINCE 2026-05-17)**: Every character dialogue MUST be its own paragraph. No two characters in same paragraph. Paragraphs 3-5 sentences, max 8. Scene/character switches require paragraph breaks. No consecutive long paragraphs (>8 sentences). See 段落格式铁律 for full rules. Multi-paragraph style lowers byte/CJK ratio (Arc 15: 4922 bytes→1441 CJK, ratio 3.41). Always verify CJK count after writing, do not rely on byte estimate.

### Word Count Verification (字数验证方法对比)
See `references/word-count-verification.md` for the full comparison. Key facts:
- `wc -c`: byte count. Use for quick gate check ONLY — see updated thresholds above.
- `len(re.findall(r'[\u4e00-\u9fff]', text))`: CJK ideographs only. THE authoritative metric. Use `scripts/cjk-verify.py` for batch verification.
- `wc -m`: character count. Good for final quality report to user, but less precise than CJK-regex for ideograph counting.

## Pre-Writing Checklist (每章写前必检)

Before writing ANY chapter — new or rewrite — verify these three things:

1. **大纲对位**: Confirm the chapter's title and content要点 in the outline file. If the outline file exists but you haven't read it yet, STOP and read it first. The outline is the contract — writing without consulting it produced 13/40 chapters with mismatched titles/content in this session.
2. **系列命名连续性**: If the chapter title contains a series label (「苏大姐的日志（二）」、「暗河的水位（二）」), VERIFY that the preceding numbered entry exists. Writing "part 2" without verifying "part 1" exists creates orphaned references. Check: scan all volume directories for the base name without the number suffix.
3. **上下文衔接**: Read the FULL preceding chapter AND the FULL following chapter (if it exists). Not just the last lines — read both chapters completely. The new chapter must bridge both without gap or contradiction. Pay special attention to: timeline markers (days/months since occupation), character locations (who is where), and物码 continuity (objects passing through whose hands).
4. **约束铁律自检**: Before first `write_file`, mentally confirm: zero `——` planned, only `""` (Chinese curly quotes) for dialogue, no meta-narrative terms like "第X弧线""第X卷", internal number = file number. If you find yourself reaching for `——` while writing, use `，` or `。` instead.

## Pre-Creation Mandatory Check: Outline Completeness (USER-REQUIRED)

## Semantic Segmentation

For Chinese novel paragraph segmentation, use the companion `semantic-segmentation` skill. It provides a rule-first + semantic-fallback pipeline that replaces mechanical period-based splitting with natural paragraph breaks. Load it via `skill_view(name='semantic-segmentation')` before any segmentation work.

Key parameters (validated on 100+ chapters):
- `--target-paras 70` for initial run
- `--max-cjk 40` for text-wall chapters (< 25 original paragraphs)
- `--max-cjk 55` for already-decent chapters (> 50 original paragraphs)
- Tiered strategy table: see semantic-segmentation skill § Tiered Segmentation Strategy

The semantic segmentation pipeline integrates with this skill's workflow: pre-clean (template dedup) → semantic split → comma flow cleanup → **multi-speaker scan** (`scripts/scan_multi_speaker.py`) → six-dimension audit.

### Multi-Speaker Dialogue Scan (post-segmentation gate)

After every batch segmentation, scan for merged multi-speaker dialogue:
```bash
python3 scripts/scan_multi_speaker.py <dir> --start N --end M [-v]
```
Detection: paragraphs where `\u201d` (close quote) → speaker verb (说/写/问/道/喊) → `\u201c` (open quote) within 80 chars = merge. Validated on 100 chapters: 5 true positives, zero false positives after filtering.

**Before writing ANY chapter**, verify that the outline has a per-chapter entry for that chapter. Do NOT assume the outline is complete. The main outline was verified to have gaps: arcs 9-16 (chapters 201-460) were missing per-chapter detail. The user explicitly requires: "大纲缺失先补充大纲" and "大纲里面全部都要补充完整" and "把大纲全部写在一个文件里面". The user will stop the session to enforce this — do not write chapters against a gap-ridden outline.

**Single-file requirement**: The user requires ONE authoritative outline file. Multiple supplement files are an intermediate step — after user confirms the supplements, merge them into the main outline and DELETE intermediate files. Keep only one outline file in the project root.

**Verified gap-detection + supplement + merge workflow (arcs 9-16, 800-chapter validation)**:
1. Scan: `grep -oP '\|\s*\d+\s*\|\' 大纲文件 | grep -oP '\d+' | sort -n` → detect gaps
2. Report gaps to user with exact chapter ranges
3. Create supplement file(s) with per-chapter entries for ALL missing ranges
4. Merge supplements into main outline → SINGLE authoritative file (v5)
5. Delete intermediate supplement files (`rm 大纲补充_*.txt`)
6. Verify: all 800 chapters have entries, 30 arcs all present

**This session validated**: merging arcs 9-16 into the main outline took one terminal pass and produced `全书大纲_完整版_v5_终极合并版.txt` (146KB, 30 arcs, 800 chapters, all per-chapter). The first batch written against this complete outline (301-305) produced ZERO short first drafts — all 5 chapters passed 2000+ CJK on first write. This proves outline completeness directly impacts first-draft quality: a detailed per-chapter outline produces 2100-3200 CJK first drafts; a missing outline produces 1100-1700 CJK first drafts requiring 4+ expansion rounds.

**Gap detection workflow**:
1. Run `execute_code` to extract all chapter numbers from the outline: `grep -oP '\|\s*\d+\s*\|\' 大纲文件 | grep -oP '\d+' | sort -n`
2. Compare against expected range (1-800). Gap = missing chapters.
3. Report gaps to user BEFORE writing. Do not write chapters against a missing outline.
4. When gaps found: supplement the outline with per-chapter entries (title + content要点) for ALL missing chapters, following the existing outline's format and the volume's metaphor framework.
5. User prefers a SINGLE authoritative outline file. If supplements are created as separate files, merge them into the main outline after user confirms. Delete intermediate supplement files.

**Chapter range conflicts**: The original outline may have overlapping chapter ranges between volumes and arcs (e.g., arc 17 labeled 421-460 but in Vol 4 which should start at 461). When merging, resolve ranges to match actual file numbering on disk. See `references/outline-gap-supplement.md`.

## Pitfalls

- **OUTLINE-GAP BLOCKER (USER-ENFORCED, 2026-05-17)**: The user explicitly requires the outline to be complete before ANY chapter is written. Phrases "大纲缺失先补充大纲" and "大纲里面全部都要补充完整" are absolute directives. The main v4 outline was verified to have gaps in arcs 9-16 (201-460). If the outline lacks per-chapter entries for the target range, do NOT start writing — detect the gap, report it, supplement the outline, get it into a single file, THEN write. See `references/outline-gap-supplement.md`.

- **OUTLINE-EXISTS-BUT-IGNORED (本会话确认，第二卷56/83章内部编号错位)**: The outline file (`全书大纲_完整版_v4_终极版.txt`, 131KB) existed in the project directory but previous writing sessions didn't consult it. Result: chapters were written with old internal numbering (065-120), then file-renamed to new numbers (161-299) without updating internal content. Detection: after any volume audit, compare internal chapter numbers vs file names. If >30% mismatch, the volume was assembled from an incompatible prior session. Fix: read the outline, map every chapter title to expected content, rewrite mismatched chapters matching the current outline.

- **多角色对话合并（100章全卷扫描验证，4真阳性）**: 语义分段后，部分继承/重分段章节仍可能存在不同角色的完整对话挤在同一段落的问题。逗号流审计（检查`。。`/`，，`）无法发现此类问题，因为引号语法上可能是平衡的但语义上错误。**检测**：扫描段落内`\u201d`之间夹带`\u201c`+说话人标记（说/写道/问/回答）的模式。**修复**：在说话人边界拆分段落。100章中土纪元V2验证：原始检测180处→精确过滤后4处真阳性（ch157/166/208/215），其余均为术语引号/概念引号误报。完整检测算法见`semantic-segmentation`技能的`references/multi-speaker-detection.md`。

- **模板污染五模式（中土纪元第二卷180章全量验证，2026-05-19）**: Inherited chapters carry FIVE types of template pollution: (1) 跨章大模板——\"暗河的水在远处无声地流着。从北岭发源...\"大段出现在134-143等多章末尾; (2) 跨章复用段——\"在下水道网络的运转过程中，老陈发现了一个规律...\"同一段落出现在141-143; (3) 章末机械重复——同一段落在一章内复制5-25次（\"灰瓷罐的盖子旋紧之后...\"×12次）; (4) **短模板重复（161-168批新发现）**——\"水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。暗河的水在远处无声地流着。\"单句模板在161/162/164/165/167/168六章重复5-12次; (5) **跨章场景复制（161-168批新发现）**——完整叙事场景\"陆辰记录在科目002/升格符号/苏大姐评价\"同时出现在162/164/165/167/168五章。这五种污染使CJK从真实的700-1,600虚高到2,000-7,000。**严重污染章（模板占70%+内容）需4-5轮扩充**，每轮追加的扩展文本需该章物码体系+人物弧线驱动，禁止水字。检测方法：扫描章末段落重复(Counter)+跨章公共段落(grep)+单句模板频率(同一句出现3+次即标记)。

- **卷归属错误（本会话确认，第一卷多40章）**: 第一卷文件夹包含121-160章，但大纲规定第一卷为001-120（或001-160，需确认）。在开始任何卷的工作前，扫描该卷的实际章节范围，与大纲声明的范围对比。如果不一致，先将多出的章节移入正确卷文件夹，再开始内容修复。移动命令模式：`mv 第一卷_星火初燃/第12[1-9]*.txt 第二卷_浴血中土/`。

- **大纲标题 vs 文件标题系统偏差（本会话确认，9/10章在151-160）**: 第一卷文件夹中151-160章的文件标题与大纲完全不同（如文件「上江陷落」→大纲「瀛烬占领军」）。这意味着存在两套竞争性大纲——文件是按旧版大纲写的，但"官方"大纲已经更新。**解决方案**：以当前大纲文件为准，重写不匹配章节。不要假设文件标题代表正确内容。

- **Post-marker content residue from prior sessions (PERSISTENT — 17/20 chapters in arcs 7-8)**: Chapters inherited from previous writing sessions often have summary paragraphs or closure text placed AFTER the `*第X章·完*` end marker. This is a different problem from correct insertion — the residue was in the ORIGINAL first-draft, not added by expansion. When you load an arc for expansion or audit, ALWAYS run a structure scan first: check every chapter for text after the end marker. If found, move it BEFORE the marker (it's legitimate content that was mis-placed, not garbage to delete). The fix pattern: `re.search(r'(\\\\*第.*章·完)', content)` to find the marker, split, and reassemble as `before + leftover + marker`. Moving residue into the chapter body often adds 150-250 CJK chars — this can change a borderline-fail into a pass without needing new expansion text.

- **Mechanical period-splitting destroys dialogue (V1 VALIDATED, 29章, 436 splits)**: V1 chapters 030-058 were damaged by a prior \"fix\" that split EVERY paragraph at every `。`. Result: one character's speech spread across 3-7 separate paragraphs with broken quotes. The three-phase repair (merge dialogue→fix punctuation→internal-period cleanup) repaired all 29 chapters. **NEVER split a paragraph mechanically at periods — always check for semantic boundaries (time/location/character/event/emotion changes) first.**
- **Cross-arc structure audit sequence**: When the user asks to check multiple arcs (e.g., "检查最近两次创作"), run the structure scan across ALL chapters first, THEN the combined CJK+keyword audit. Structure fixes change word counts (moving residue adds CJK), so doing structure-then-audit prevents false word-count failures. The effective sequence: (1) structure scan + fix all arcs, (2) combined CJK+keyword audit, (3) keyword-miss patches, (4) final sweep.
- **Arc-final chapters use dual-format end markers**: The last chapter of every arc uses `*第X章·完 | 第X弧线「弧线名」终*` instead of the standard `*第X章·完*`. Batch regex patterns that only match the simple form will silently skip arc-final chapters (as happened with chapters 070 and 080). Always use: `\\n(\\*第.*章·完[^\\n]*)` which captures both formats. Always verify the arc-final chapter's exact marker string before running any batch operation.
- **Batch expansion can create duplicate end markers on arc-final chapters**: When using `execute_code` to insert expansion text before the end marker via `re.search()` + `match.start()`, the arc-final chapter's dual-format marker is matched correctly, but the reassembly pattern (`text[:match.start()] + expansion + '\n\n' + marker`) re-appends the full marker string including the `终*` suffix. If the original was already correct, the result is a clean single marker. But if a previous expansion already appended a closure followed by the marker, running a second expansion on the same chapter can leave the old marker in place AND add a new one — producing a duplicate (as happened with chapter 100). Detection: after batch expansion, run a structure scan that counts end-marker lines (must be exactly 1). Fix for duplicate: `patch` tool → replace `marker + '\n\n' + marker` with `marker`.
- **Duplicate paragraphs after end markers**: The most severe form of post-marker residue is full duplicate paragraphs — the chapter's body paragraphs repeated verbatim after the end marker. Chapter 070 had 4+ duplicate blocks. Detection: scan for any paragraph after the marker whose first 30 chars match a paragraph before the marker. Fix: delete all content after the marker, verify CJK count, then expand if needed.
- **Em-dash overuse (PERSISTENT — CAUGHT BY USER)**: Chapters in Volumes 2-3 accumulated `——` at rates up to 10.2/百字 — ~250 dashes in a single 2400 CJK chapter. This creates run-on, unreadable prose. The batch replacement script in `references/em-dash-removal.md` can fix moderate cases (under 100 dashes); chapters with 200+ dashes need full manual rewrites. After any arc, run the dash-frequency check: `dash_count / (cjk/100)`. Target under 2.0, ideally under 1.0. See `references/em-dash-removal.md`. Chapters below 2000字 are the most common failure. This is NOT limited to the first 2-3 arcs. Arc 5 (chapters 041-050) and arc 6 (051-060) both required extensive expansion passes — 6/10 chapters in arc 6 started below 2000字. The root cause is first drafts averaging ~5000 bytes (~1500 CJK) instead of the required 8000+. The ONLY reliable fix is writing longer first drafts. See byte-count quick-gate above.
- **Batch-expansion death spiral**: The write→verify 1500字→patch→verify 1800字→patch→verify 2000字 cycle is the most expensive failure mode in novel writing. A single 10-chapter arc can consume 30+ tool calls in expansion alone. Prevention: write first drafts at 8000+ bytes. If a draft comes out at 5000 bytes, expand it to 8000+ in ONE pass, not 2-3 small patches of 50-100 characters each.
- **Use execute_code batch-append for expansion, NOT repeated patch calls**: When 4+ chapters in an arc are below 2000字, use `execute_code` to run a Python script that appends substantive closure paragraphs to all short chapters simultaneously. The reliable code pattern (verified across arcs 9-12):

```python
import re, glob

expansions = {
    chapter_number: "paragraphs of expansion content...",
    # ... one entry per short chapter
}

for ch_num, content in expansions.items():
    fpath = glob.glob(f"{base}/第{ch_num:03d}章_*.txt")[0]
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # MUST handle BOTH formats: standard '第X章·完*' AND arc-final '第X章·完 | 弧线名终*'
    # The simple pattern \*第.*章·完\* FAILS on arc-final chapters — it won't match
    # because '完' is followed by ' | 弧线名终' not by '*'. Use this instead:
    m = re.search(r'\*第.*章·完[^\n]*', text)
    if m:
        marker = m.group(0).rstrip()
        # Ensure marker ends with '*' (arc-final format may have trailing content)
        if not marker.rstrip().endswith('*'):
            marker = marker.rstrip() + '*'
        before = text[:m.start()]
        new_text = before.rstrip() + '\n\n' + content + '\n\n' + marker + '\n'
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_text)
```

This pattern replaces 8-12 individual `patch` calls with one `execute_code` call. Key detail: use `re.search(r'\*第.*章·完[^\n]*', text)` which captures BOTH standard markers (`*第171章·完*`) AND arc-final markers (`*第180章·完 | 第十八弧线「内战重燃」终*`). The CJK character class `[一二三四五六七八九十百]+` may silently return no match.
- **Multi-round expansion budget**: When first drafts average <5500 bytes (as in Arc 10 where all 10 chapters were 3200-5500 bytes / 958-1651 CJK), budget THREE rounds: R1 (substantive closures, 500-800 CJK each → chapters go from ~1100 to ~1750), R2 (micro-closures, 250-400 CJK each → ~1750 to ~2000), R3 (targeted pushes, 150-250 CJK each → final 2000+). The "never >2" guideline was too optimistic for arcs where the writer consistently produced short first drafts. Total expansion needed per arc can exceed 10,000 CJK when all 10 chapters start below 2000.
- **Losing continuity**: Always re-read the last chapter before writing the next.
- **Naming drift**: Verify character names, reign years match the outline exactly. See "Naming Consistency" section.
- **Over-accelerating**: Reform must be gradual — don't jump from "just learned chemistry" to "building a steam engine" in one chapter.
- **Outline drift**: The outline is the contract. Don't write about military reform when the topic is "皇子教育".
- **"修复"变破坏 — 机械按句号分段 (V1 030-058 validated)**: 按句号机械拆分章节会破坏对话完整性。V1的030-058章曾被按句号拆分，产生436处裂引号。正确做法：合并裂引号→对话内句号改逗号→全卷段落内句号改逗号。完整修复流程见 `references/paragraph-reformatting.md`。
- **旧章模板污染·批量去重（中土纪元第二卷121-300章验证）**: 旧创作会话的章节存在三种模板污染：(1)跨章模板段落（"暗河的水在远处无声地流着..."大段重复出现在多章末尾）；(2)章末机械重复（同一段落复制5-15次填充字数）；(3)行号前缀`NNN|`和`---`分隔线。去重后CJK从2,000-2,600骤降至1,200-1,500，需大幅补字。补字时优先延续该章物码体系和人物弧线，不得引入新模板。**🔥 扩充预防铁律**：所有扩充/修复内容必须绑定该章独有物码体系（具体人物+具体物件+具体感官），禁止使用任何泛化收束模板。每段扩充须满足：①专有人物/物件 ②感官细节 ③与前文因果衔接。跨章复用同一段落=红线。完整去重+分批复工作流见 `references/batch-resegmentation-workflow.md`。

- **🚨 去重→分段→扩展：执行顺序铁律（139-148批验证）**: 必须先去重再分段，绝不能分段后再去重——分段会把重复内容拆散到不同段落中，使去重无法识别。也不能去重后直接报告——去重后CJK通常骤降50-70%，每章需1-3轮扩展。扩展预算：去重后CJK<1200→3轮，1200-1500→2-3轮，1500-1800→1-2轮。

- **段落内重复（Intra-paragraph repetition，139-148批新发现）**: 同一句子在单一段落内连续重复10-20次（如"烧焦的黑板被韩先生从废墟里搬..."×19次）。段落级去重无法检测，需用句号拆分段落内句子后检查连续3+相同前缀。见 `references/template-dedup-workflow.md` 第2a节。

- **跨章内容复制（Cross-chapter content duplication，139-148批新发现）**: 完整叙事场景被复制到多个章节。如「陆辰回复绷带信」场景同时出现在146/147/148章。确定核心章后从其余章删除。见 `references/template-dedup-workflow.md` 第2b节。\n- **🚨 虚假CJK通过——去重后必须重新验证（USER-CORRECTED 2026-05-20）**: 继承章的去重会移除大量重复内容（实测191章：原10段/5472CJK→去重后15段/761CJK，25次重复撑起4700虚增CJK）。**绝不能用去重前的CJK判断章节是否达标**。五维审计报告的CJK列必须是去重+分段之后的真实CJK，不是去重前的虚高数字。本会话B7(181-190)和B8(191-200)首次报告时用了去重前CJK（均4000-5000），用户直接指出"并没有分段"——虚高CJK掩盖了欠分段和缺字问题。**正确顺序：去重→语义分段→补字→CJK验证→报告**。报告前确认每章段数≥25（目标40+），段数10-15=CJK虚高=假通过。

- **Old-project file contamination**: When creating a new novel in a directory that previously held another project, stale chapter files may persist. 《中土纪元》inherited 118 old chapters from a prior novel. Always `ls` the target directory before writing and delete stale files first. Old files inflate word-count scans and pollute audit results.
- **Patch insertion point for expansion**: When expanding a short chapter, insert new content BEFORE the chapter-ending marker, NOT after it. Adding content after the closer creates format corruption. The marker format varies: standard chapters use `*第X章·完*`, but the arc's final chapter often uses `*第X章·完 | 第X弧线「弧线名」终*`. The batch-expansion regex must handle both with `\n(\*第[一二三四五六七八九十百]+章·完[^\n]*)`. Always verify the last chapter's exact marker before running batch expansions.
- **Regex CJK character class silently fails on chapter markers**: The pattern `\*第[一二三四五六七八九十百]+章·完\*` may return no matches even when the marker exists in the file. This was confirmed in Arc 11 where `re.search(r'\*第[一二三四五六七八九十百]+章·完\*', text)` returned None for all 9 chapters, but the markers were present. The simpler pattern `\*第.*章·完\*` works reliably. Also avoid `\s*$` anchors after the marker — the `·` (U+00B7) character and trailing newlines cause anchors to fail. Use `re.search(r'\*第.*章·完\*', text)` for all end-marker operations — batch expansion, structure scans, and post-marker residue detection.
- **Terminal timeout on /mnt/ paths**: Use `execute_code` with Python regex instead of `wc -c` via terminal on Windows mounts.
- **Internal-reference errors**: Verify "过去N章" claims and tool serial numbers against actual arc boundaries before submitting.
- **Duplicate paragraphs**: Patch operations may accumulate duplicate paragraphs. After any arc, run anomaly scan.
- **Regex-only Chinese char counting**: Excludes Chinese punctuation (U+FF00). Cross-check with total non-whitespace count before patching.
- **Time inconsistency (TIMELINE DRIFT)**: The outline specifies a time span for the volume. In-character reflections like "两年" when the outline says "约6个月" must be corrected to the outline's duration. Before writing, grep for duration phrases and cross-check.
**Meta-narrative breaking 4th wall**: Phrases like "第一卷第033章终" or "接下来是第二卷" or characters speaking chapter numbers ("第081-090章——前夜") break immersion. Replace with in-world transitions and event markers. See `references/meta-narrative-fix.md` for the full detection, replacement, and title-restoration workflow. A single volume can accumulate 72+ instances — after fixing, always verify titles on lines 1-3 weren't corrupted.
- **"新增" arcs are thinner**: Transitional arcs not in the original outline consistently produce shorter chapters. Budget extra expansion passes.
- **Duplicate line numbers**: `NNN|` prefixes from `cat -n` compaction accumulate across sessions. Fix: strip with `re.sub(r'^\s+\d+\|\s*', '', line)` across all chapters after major edits.
- **Global regex corrupts title lines**: When using Python scripts to batch-fix patterns like `第\d+章` across all chapters, the replacement will corrupt line 3 (chapter titles). ALWAYS verify title lines after a global regex pass and restore them from filenames: `re.match(r'(第\d+章)_', fname).group(1)`.
- **User prefers serial over parallel for novel audits**: After a parallel audit was rejected, the user explicitly chose scheme B. Use the serial audit workflow in `references/full-volume-audit.md` — do NOT dispatch `delegate_task` for novel auditing unless the user says "parallel" or "快速" explicitly.
- **Outline-alignment check is mandatory (USER-REQUIRED since Arc 5)**: After every arc, run the COMBINED CJK + outline-keyword-alignment audit. The user explicitly requires "检测章节内容是否符合大纲符合逻辑性". Do NOT skip the keyword alignment pass even if word counts all pass — a chapter at 2000+字 that misses outline-mandated keywords (characters, locations, events) fails just like a short chapter. See `references/arc-audit-combined.py` for the reusable pattern. Define keyword markers as 3-4 unique terms per chapter from the outline. Keyword matching is fuzzy: "舰队" = "战舰" in intent.
- **Multi-line string SyntaxError in batch expansion via execute_code (THREE TRIGGERS, all confirmed)**: When using `execute_code` to batch-expand chapters with Chinese text, Python may throw `SyntaxError`. Three distinct triggers identified:
  1. **Triple-quoted strings with special punctuation**: Long Chinese strings in `"""..."""` containing 「」、《》、英文引号 can cause invisible encoding/escape interactions. Workaround: use individual `patch` tool calls.
  2. **Chinese double-quotes in Python string literals**: Chinese `""` (U+201C/U+201D) inside Python single or double quotes are valid Unicode but the sandbox parser may reject them with `SyntaxError: invalid character '...' (U+201C)`. This occurred when defining `extra = "..."` strings containing dialogue with Chinese quotes in `execute_code` (confirmed 2026-05-21 and 2026-05-22, novel-writing sessions). **Verified workaround**: use `\u201c` and `\u201d` Unicode escapes instead of literal `""` characters in all Python string literals inside `execute_code`. Example: `text = '\u201c你好\u201d'` works where `text = '"你好"'` may fail. For expansion text containing dialogue, use `\u201c`/`\u201d` throughout. Then run a post-expansion format cleanup pass that converts any remaining raw `\u2014\u2014` (em dashes in expansion text) to `，` — these are ALSO introduced by expansion text and cause "format pollution" (see pitfall below).
  3. **Triple-quoted string unterminated error with embedded quotes**: When Chinese `""` or `——` appear inside `"""..."""` blocks, Python may report `SyntaxError: unterminated triple-quoted string literal`. This is a variant of trigger #2. Same workaround: avoid triple-quoted strings for Chinese text. Use single-quoted strings with `\n` joins and `\u201c`/`\u201d` escapes.

- **execute_code tuple unpacking silently corrupts strings (sandbox-specific)**: When iterating over a list of tuples like `for ch_num, content in [(221, e221), (222, e222)]:`, the sandbox may silently treat `content` as a tuple rather than unpacking the string. This causes `AttributeError: 'tuple' object has no attribute 'strip'` at the `content.strip()` call. **Workaround**: use `for item in data: ch_num, content = item[0], item[1]` — accessing by index forces the type. Or define separate variables per chapter and process one at a time in separate calls. This is confirmed reproducible across multiple sessions (Arc 22-23).

- **Zero-dash first drafts are SYSTEMATICALLY shorter (VALIDATED Arcs 21-22, 20 chapters)**: Removing 「——」 from prose reduces first-draft byte counts by 30-50%. In the dash-heavy style, first drafts averaged 5,000-7,000 bytes (1,500-2,000 CJK). In the zero-dash style, the same conceptual density produces only 2,700-5,500 bytes (800-1,650 CJK). This is NOT a failure of writing technique — it's a natural consequence of the style change: the old pattern chained 3-5 clauses into one long sentence with dashes; the new pattern breaks those into separate sentences with periods. The CJK count per idea is the same, but the byte count drops because sentences are shorter. **Budget 2-3 expansion rounds per chapter** (Arc 21 averaged 2.4 rounds, Arc 22 averaged 2.6 rounds). Do NOT try to compress expansion into 1 round — the chapters need substantive content, not padding. The batch expansion pattern (`execute_code` with `re.search(r'\*第.*章·完', text)`) remains the fastest method, but expect to run it 2-3 times per batch of 3 chapters. The surgical approach: (1) dump every dash with context, (2) categorize each as rhetorical/keep vs. replaceable, (3) apply targeted replacements with `content.replace()`, (4) verify CJK ≥ 2000 after each chapter. The user explicitly rejected blanket replacement — they want judgment per dash. Typical results: chapters at 40-95 dashes can be reduced to 4-27 dashes while preserving the arc's structural "不是X——是Y" rhetoric.

- **「——」fix on expanded chapters can corrupt files (Arc 18 confirmed — Ch.174 duplicated 2x)**: When running dash-fix `execute_code` scripts on chapters that were previously expanded, the file may already contain duplicate content from a prior expansion round. The dash-fix script's read→replace→write cycle can inadvertently normalize and preserve the duplication rather than detecting it. **Prevention**: before running any dash-fix on an expanded chapter, verify file integrity: (1) check for duplicate paragraphs via `Counter`, (2) verify CJK is in expected range (e.g., 2000-3000, not 4000+), (3) check title line appears exactly once. If corruption is found, rebuild the chapter from the original first-draft content by re-running the expansion insertion — do NOT attempt to surgically remove duplicate blocks from a corrupted file. The rebuild approach is the only reliable fix validated in Arc 18.

- **QQ平台引号渲染陷阱（2026-05-19 实际确认）**: QQ（中国即时通讯平台）会将标准中文双引号 `""` 渲染显示为 `【】`。用户可能在QQ消息中看到 `【举例】` 但实际文件内容为 `"举例"` ——这是平台显示层面的问题，不是文件内容问题。**永远先检查实际文件**，不要根据QQ聊天中的显示效果判断文件内容是否有误。确认方法：`execute_code` 扫描 `text.count('【')`，如果文件为零而用户看到【】，那就是QQ渲染问题。

- **「」→"" 对话与标签区分技术（230章全卷验证）**: 全书使用 `「」`（角括号）作为统一引用符号。用户要求对话使用标准中文双引号 `""`，但铭文/刻字/标签/科目名（如「中土正统」、「辛」、「昭和十九年，铁锭二十块」）应保留「」。区分规则：(1) 含句末标点（。！？）或长度超20字 → 对话 → 替换为 `""`；(2) 短标签/刻字/科目名 → 保留 `「」`。**陷阱**：不能全局替换所有 `「」`——会丢失铭文/标签的视觉标记功能。实现：`re.sub(r'「([^」]+)」', lambda m: '\u201c'+m.group(1)+'\u201d' if any(p in m.group(1) for p in '。！？') or len(m.group(1))>20 else m.group(0), text)`。本会话验证：1,046对——→""，362对「」保留。

- **批量操作后结束标记丢失（6章实际发生）**: 在分段拆分、破折号替换等批量编辑操作后，部分章节的结束标记 `*第X章·完*` 可能丢失。本会话涉及6章（056/058/059/060/063/065）。**每次批量操作后必须全卷扫描结束标记**：`execute_code` 检查每章是否包含 `re.search(r'\*第.*章·完', text)`，缺失则补入。补入格式：`f"\n\n*第{int(num)}章·完*\n"`。扫描代码见 `references/missing-end-marker-scan.md`。

- **大纲编号与实际文件错位（本会话确认，250章全部偏离）**: 初始大纲的章节编号（如"第三卷401章"）可能与实际文件编号（如"第三卷121章"）完全不同。原因是初始大纲使用理论编号，而实际创作从001开始连续编号。检测方法：扫描所有卷目录提取实际章号范围，与大弧线结束标记对比。如果用户说"大纲和章节对不上"，立即运行全卷结构扫描而非尝试修复单章。完整检测和重建流程见 `references/outline-rebuild-and-expansion.md`。修复后必须逐章核实：`for i in range(min_ch, max_ch+1): assert file exists for chapter i`。

- **创作期内部编号/标题漂移（弧8验证，7/20章）**: 弧线创作过程中章节文件被重命名（例如从旧主题改为新主题），但文件内部第一行的编号和标题未同步更新。结果是：文件名正确、内容正确，但内部第一行仍标注旧编号（如"第072章"）和旧标题。这与重组后的残留不同——这是创作过程中发生的，而非重组。**检测**：使用 `references/arc-audit-full-scan.py` 逐章对比文件名编号/标题 vs 内部第一行编号/标题。**修复**：`content.replace(f'第{old}章 {old_title}', f'第{new:03d}章 {new_title}', 1)` 替换第一行。注意：只替换内部编号和标题，内容本身无需修改（内容匹配新标题）。如 `第021章_江南水乡.txt` 内部标注为 `第011章 江南水乡`（偏移+10）。这不会影响阅读但会在审计和引用时产生混淆。**必须审计**：重组完成后立即运行 `references/four-phase-arc-review.md` 中的内部编号扫描（Phase 1c），对偏移章进行批量修复。受影响模式：021-030标为011-020（+10）、041-050标为021-030（+20）、066-075标为031-040（+35）。修复：`content.replace(f'第{old}章', f'第{new}章', 1)` 仅替换第一处出现的标题行。

- **章末编号遗留旧中文数字（第一卷验证，36/90章受影响）**: 首行编号修复后章末标记 `*第X章·完*` 仍可能使用旧编号的中文数字。001-009用中文数字（"第一章"）但对位正确无需修改；021-029标"第十一章"至"第十九章"偏移+10；041-049标"第二十一章"至"第二十九章"偏移+20；066-074标"第三十一章"至"第三十九章"偏移+35。修复：统一为三位阿拉伯数字 `*第{num:03d}章·完*`。中文数字→阿拉伯转换表涵盖一至四十。章节重组后必须双重检查——首行+章末都可能有旧编号残留。

- **批量扩充后尾随竖线和重复填充文本（第一卷验证）**: (1) 弧线标注清除后章末可能留下孤立竖线 `*第065章·完 | ` — 尾随空格和竖线。修复：`re.sub(r'\|\s*\*', '*', content)` 和 `re.sub(r'\| $', '', content)`。(2) 最后一推添加的重复文本（如 `风从暗河方向吹过来...` 重复3次）会在章末形成冗余。检测：`re.findall(r'((.{20,})\\\2)', content[-500:])` 扫描章末重复模式。修复：去重保留一次。

- **旧章标题与大纲不匹配（第二卷弧7/8验证，6+7章）**: 前v4创作会话中生成的章节文件名与当前大纲标题不一致（如 `第163章_地下火种.txt` vs 大纲 `铁柱的秘密工棚`）。这是重组遗留问题，不是内容错误。**启动新卷时第一步**:运行标题对位扫描 → 批量重命名不匹配章 → 再开始创作。重命名脚本模式见 `references/volume-start-workflow.md`。注意:重命名后内部首行标题可能仍用旧名——内容匹配即可，不需修复首行。但如果内容本身也匹配旧标题而非新文件名主题，则需要重写内容匹配新标题（本会话弧7/8验证：13章内容与文件名不匹配，已全部重写）。

- **多角色对话合并（100章全卷扫描验证，4真阳性）**: 语义分段后，部分继承/重分段章节仍可能存在不同角色的完整对话挤在同一段落的问题。逗号流审计（检查`。。`/`，，`）无法发现此类问题，因为引号语法上可能是平衡的但语义上错误。**检测**：扫描段落内`\u201d`之间夹带`\u201c`+说话人标记（说/写道/问/回答）的模式。**修复**：在说话人边界拆分段落。100章中土纪元V2验证：原始检测180处→精确过滤后4处真阳性（ch157/166/208/215），其余均为术语引号/概念引号误报。完整检测算法见`semantic-segmentation`技能的`references/multi-speaker-detection.md`。

- **模板污染五模式（中土纪元第二卷180章全量验证，2026-05-19）**: Inherited chapters carry FIVE types of template pollution: (1) 跨章大模板——\"暗河的水在远处无声地流着。从北岭发源...\"大段出现在134-143等多章末尾; (2) 跨章复用段——\"在下水道网络的运转过程中，老陈发现了一个规律...\"同一段落出现在141-143; (3) 章末机械重复——同一段落在一章内复制5-25次（\"灰瓷罐的盖子旋紧之后...\"×12次）; (4) **短模板重复（161-168批新发现）**——\"水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。暗河的水在远处无声地流着。\"单句模板在161/162/164/165/167/168六章重复5-12次; (5) **跨章场景复制（161-168批新发现）**——完整叙事场景\"陆辰记录在科目002/升格符号/苏大姐评价\"同时出现在162/164/165/167/168五章。这五种污染使CJK从真实的700-1,600虚高到2,000-7,000。**严重污染章（模板占70%+内容）需4-5轮扩充**，每轮追加的扩展文本需该章物码体系+人物弧线驱动，禁止水字。检测方法：扫描章末段落重复(Counter)+跨章公共段落(grep)+单句模板频率(同一句出现3+次即标记)。

- **`patch()` introduces ASCII quotes AND em-dashes (本会话再确认)**: Using `patch(action='patch', new_string=...)` with `new_string` containing Chinese curly quotes `""` (U+201C/U+201D) converts them to ASCII `\"`. Additionally, `——` in patch expansion text survives into the file. After EVERY `patch()` call on a novel chapter: (1) verify `content.count('\"')` and run state-machine converter if > 0; (2) verify `content.count('——')` and run `text.replace('——', '，')` if > 0. Do NOT defer to arc-level audit — this session accumulated 10+ em-dashes and 12+ ASCII quotes from patch calls. **Workaround for `execute_code` batch expansion**: use `\u201c`/`\u201d` Unicode escapes instead of literal `""` in Python string literals. Then run a post-expansion format cleanup pass. **Better workaround (Arc 10-2 validated)**: use the temp-file pattern — write expansion to `/tmp/` via `write_file`, then merge + fix quotes/dashes in one `execute_code` call. See `references/temp-file-expansion.md` for the 4-step pattern (write→merge→fix→verify).

- **审计跳过（用户反复纠正，三次触发：2026-05-26, 2026-05-15, 2026-05-15同日）**: 用户明确要求"每次创作后都需要审查"。写完后立即问"继续下一批？"而不先做审查 = 违反审计铁律 = 用户必然纠正。本会话弧13第二批（306-310）再次触发：写完5章后直接问"继续第三批"，用户立即纠正"审查，每次创作后都需要审查，这个审查写入永久记忆中"。**识别信号**：如果报告里出现"完成，继续（下一批）？"而前面没有四维审查结果表格→你跳过了审计→立即停止报告，补做审查。正确的汇报格式：先展示审查结果表格（CJK/格式/大纲/逻辑/人物弧线），全部通过后再问"继续下一批？"。不要用"完成"这个词直到审计通过。**扩展文本同样引入破折号**：本会话第三批311章扩展时，新增的围裙搓洗+铁纽扣段落含2处「——」，需立即修复。扩展后验证与写后验证同等级别——不得跳过。

- **`write_file()` SYSTEMATICALLY converts curly quotes to ASCII (VALIDATED Arc 10, 6/6 chapters)**: When writing novel chapters via `write_file`, ALL Chinese curly quotes `""` in the submitted text are converted to ASCII `"` on disk. This is NOT sporadic — every chapter written via `write_file` in this session had 30-50 ASCII quotes requiring post-hoc state-machine fix. **Mitigation**: After EVERY `write_file` call for a novel chapter, immediately run `execute_code` to: (1) verify `content.count('"')` and run state-machine converter if > 0; (2) verify `content.count('——')` and fix if > 0. Code pattern for the state machine: iterate each char, flip between `\u201c`/`\u201d` on each `"`. This adds ~1 tool call per chapter but prevents format pollution from accumulating across 6+ chapters and requiring bulk cleanup. Combine quote fix + dash fix + CJK verify into ONE `execute_code` call per batch of 3 to keep overhead at +1 call per batch.

- **Inherited volume systemic corruption (中土纪元 V2 validated, 20章)**: Volumes from prior bulk-generation sessions carry four systemic corruption patterns: (1) intra-chapter duplication — same closing paragraph repeated 5-10x at chapter end, inflating CJK by 400-600; (2) cross-chapter template pollution — identical blocks like "暗河的水在远处无声地流着..." appearing verbatim in 6+ chapters; (3) `|---|` section separators; (4) `NNN|` line-number prefixes. Detection MUST happen BEFORE segmentation — dedup drops CJK significantly and chapters that passed the 2000-CJK gate will fail after cleanup. Budget expansion for post-dedup recovery. See `references/inherited-volume-segmentation.md`.

- **大纲覆盖不全——补大纲优先（USER-ENFORCED 弧11-12验证）**: 全书大纲可能仅覆盖部分弧线（如《中土纪元》大纲仅到250章，弧9-16缺失）。在开始创作大纲缺失的弧线时，必须先创建补充大纲（`大纲补充_弧XX.txt`），含每章标题和内容要点，确保章节标题与补充大纲一字不差。补充大纲须与已有章节标题一致。两个本会话验证的补充大纲模式：(1) 弧11-12共50章补纲 + (2) 弧12实际章节标题与初始预期不同时的自适应补充。补纲后再按分批推进规则创作，不得跳过补纲直接写。

- **Sparse inherited arcs with +3 interval gaps (Arc 10 validated, 211-220)**: When an arc has existing chapters at regular intervals (e.g., 211, 214, 217, 220 — every 3rd chapter exists, 6 gaps), extra steps are needed BEFORE writing any new chapters: (1) Read ALL existing chapters FULLY to understand the narrative thread and verify they bridge correctly; (2) Check each inherited chapter for: internal numbering drift (old session numbering), `cat -n` line number artifacts (`\s+\d+|`), old Chinese-numeral end markers (`第八十一章·完`), and ASCII quote pollution — these are GUARANTEED in inherited chapters from prior sessions; (3) Fix all format issues BEFORE writing new chapters — otherwise the new chapters get written against a corrupted baseline; (4) Infer gap-chapter titles from the narrative flow between existing anchors (e.g., 211→212→213→214 means 212 bridges 西迁→和谈); (5) Budget one extra `execute_code` call per inherited chapter for format cleanup. Inherited chapters consistently have 30-50 ASCII quotes each. See `references/inherited-arc-cleanup.md`.

- **内战游击/后勤章节首稿更短（Arc 18, 461-470验证）**: 内战弧线的章节（游击战、支前体系、地道网、防御规划、情报战）不依赖正面战斗场面，内容以间接行动和制度建设为主。首稿平均仅1000-1500 CJK，每章需3-5轮扩写，每批5章需15-25次扩写调用。这与政治过渡弧线（Arc 17）的开销模式一致。**预算**：每章3轮扩写，使用execute_code批量追加模式——单独patch调用会导致破折号污染。内战中每章写4-5个场景（非3个）可以缩小首稿差距。: When the outline file is missing chapters for the current arc (e.g., arcs 9-12 for 201-300 are not in the official outline), chapters must be written from inferred chapter titles rather than concrete content要点. First drafts in this mode consistently come out at 800-1,700 CJK — roughly HALF the density of chapters written against a detailed outline. Budget 4-6 expansion rounds per chapter (vs 2-3 for outline-driven chapters). The root cause: without specific content keywords to target, each chapter covers 1-2 vignettes instead of the 4-5 needed for 2000+ CJK. **Mitigation**: before writing, create your OWN micro-outline of 4-5 specific character moments to compensate for the missing outline detail. Treat the inferred chapter title as a prompt and pre-plan the concrete scenes.

- **大纲缺失弧线 → 须先补充大纲再创作 (USER-ENFORCED, Arc 11-2 validated)**: When the main outline (`全书大纲_完整版_v4_终极版.txt`) has a gap covering the current arc — no per-chapter titles or content要点 — the user explicitly requires supplementing the outline FIRST. Do NOT infer chapter titles on the fly and write directly. The proven workflow: (1) Read all existing chapters in the arc range to understand the narrative thread; (2) Infer gap-chapter titles and content要点 from the existing anchors; (3) Create a supplementary outline file (`大纲补充_弧XX-XX.txt`) using the same format as the main outline (arc theme + metaphor table + core conflict + per-chapter table with 章/标题/状态/内容要点 columns, existing chs marked ✅, gaps marked ⬜); (4) Present the supplementary outline to the user for tacit approval; (5) Only then write chapters. **This session validated**: supplementing the outline for arc 11-2 (251-260) took one `write_file` call and all 5 gap chapters hit 2000+ CJK on first draft — no expansion needed. Contrast with arcs 9-10 where writing without outline produced 800-1,700 CJK first drafts requiring 4-6 expansion rounds per chapter.

- **用户显式要求大纲标题逐章对照表（本会话确认）**: 用户问"与大纲标注的章节标题和内容一致吗", 这是在五维审计大纲对位摘要之外的独立检查。报告时需展示逐章对照表(大纲标题vs实际标题vs内容要点vs实际内容), 不只依赖审计摘要中的一行"大纲对位:✅"。首次进入新弧线或新卷时, 第一批完成后预建此表。**用户还会检查报告摘要中的章节标题是否与大纲一字不差**——你的五维审计表格中「章 | 大纲」列显示的标题如果使用了缩写、简称、或任何与大纲原文不同的表述，用户会指出不一致。报告中的标题必须从大纲原文逐字复制，不得改写。 When an arc has pre-existing chapters (e.g., arc 12 had odd-numbered chapters 271,273,275...,299), the supplementary outline MUST use those chapters' ACTUAL titles as-is. Do NOT assume what titles they should have — scan the directory with `ls` first to get the exact filenames, then build the supplementary outline around them. Arc 12's existing odd chapters had titles like 「磨合」「民间编入」that differed from expected titles — if the supplementary outline had forced different titles, all even-numbered bridge chapters would have been written against a fictional narrative, creating massive rewrites. **Workflow**: `ls` → extract titles → build supplementary outline matching actual titles → fill in gap (even) chapters.

- **继承章内部编号漂移 (Arc 11-2 validated, 5/10 chapters)**: When an arc has pre-existing chapters from prior sessions, those chapters' internal first-line numbering may not match their file numbers. Arc 11-2's inherited chapters (251, 254, 257, 259, 260) had internal numbers 096-100 from an old session's numbering system. **Detection**: scan first line with `re.match(r'第(\d+)章', text)` and compare against file number. **Fix BEFORE writing new chapters**: `content.replace(f'第{old}章 ', f'第{new}章 ', 1)` on the first line only — and `content.replace(f'*第{old}章·完*', f'*第{new}章·完*')` on the end marker. Also fix ASCII quotes in inherited chapters with the state-machine converter — inherited chapters consistently have 20-60 ASCII quotes each. Budget one `execute_code` call per inherited chapter for numbering+quote fix before starting new chapter creation.

- **卷末链接钩子（第一卷160章验证）**: 全卷最后一章需要明确的书卷间过渡钩子，而非仅主题收束。模式：(1) 主角合上记录工具（笔记本/日志）并归档；(2) 标签上写"第X卷"；(3) 望向下一阶段的方向（地理方向/战场方向）；(4) 用系列核心物码（归码/灯/炭条）作为过渡意象；(5) 明示"第X卷将从这里开始"。示例：`标签上只有两个字:第一卷。` → `第二卷将从这里开始。战争没有结束。归码还没有刻完。`

- **英文直引号 vs 中文弯引号系统性不一致（第一卷90章验证，40/90章受影响）**: 早期弧线（001-010、021-030、041-050）和部分后期章节使用英文直引号 `"..."` 而非中文弯引号 `"..."`。QQ平台渲染 `"` 为 `【】`，用户可能在QQ中看到 `【对话】` 但文件内容为 `"对话"`。检测：`content.count('"')` > 0 表示存在英文直引号。修复：使用状态机交替法——遍历每个字符，遇 `"` 时交替输出 `"`（U+201C）和 `"`（U+201D）。修复后必须验证 `left_q == right_q` 每章引号数成对。详见 `references/four-phase-arc-review.md` Phase 1b。

- **两轮审查陷阱（第一卷90章验证）**: 修复第一层格式问题（引号、首行编号）后，章节看起来"干净"了，但更深层问题被掩盖——章末编号（用中文数字的旧编号）、元叙事标注（"第一弧线终"）、弧线名残留、尾随竖线等。用户会问"看看还有什么问题"——这要求第二轮深度扫描。**工作流**：P0修复（引号+编号）→ 深度扫描（章末+元叙事+弧线标注+尾随符号）→ 九项终扫。不要在第一轮修复后就报告"完成"。具体检查清单见 `references/four-phase-arc-review.md` Phase 1d-1f。

- **碎片段落是风格特征，非缺陷**: 短段落（<10 CJK字符的非对话段落）在扫描中可能被标记为"碎片段落"，但这实际上是中国网文/动漫风的节奏节拍——动作断句（"他转身。"）、情感重击（"他没有回头。"）、场景切换（"三天后。"）。`多分段，短段落` 是用户明确要求的格式铁律，碎片段落是其自然结果。在质量扫描中标记为观察项即可，不要当作需要"修复"的问题。

- **英文直引号 vs 中文弯引号系统性不一致（第一卷90章验证，40/90章受影响）**: 早期弧线（001-010、021-030、041-050）和部分后期章节使用英文直引号 `"..."` 而非中文弯引号 `"..."`。QQ平台渲染 `"` 为 `【】`，用户可能在QQ中看到 `【对话】` 但文件内容为 `"对话"`。检测：`content.count('"')` > 0 表示存在英文直引号。修复：使用状态机交替法——遍历每个字符，遇 `"` 时交替输出 `"`（U+201C）和 `"`（U+201D）。修复后必须验证 `left_q == right_q` 每章引号数成对。

- **扩充文本引入格式污染（Arc 5·20章验证）**: 使用 `execute_code` 批量扩充章节时，Python字符串中的扩充文本本身可能包含「——」（如 `\u2014\u2014`）和英文直引号。扩充操作完成后章节的破折号和引号会"复阳"——所有章节在扩充前格式干净，扩充后大量破折号和英文引号重新出现。**解决方案**：每次批量扩充后必须立即运行格式清理（`content.replace('\u2014\u2014', '，')` + 引号交替转换），不得跳过。扩充+清理应视为一个原子操作——不要分开执行。已验证Arc 5：20章扩充完成后19章出现破折号+引号，统一清理后全部归零。本会话从v2.0（250章对齐）到v3.0（800章扩写）。（破折号替换、分段拆分、「」→""转换、元叙事清除）后，必须立即运行三项验证：(1) **结束标记扫描**——`re.search(r'\*第.*章·完', text)`，防止丢失（本次批量操作后发现第056/058/059/060/063/065章共6章缺标记）；(2) **双标点扫描**——`'。。' in text or '，，' in text or '，。' in text`，破折号替换可能产生双标点（本次发现第173章9处双逗号、第027章双句号）；(3) **CJK字数复验**——确保插入/删除操作后字数仍≥2000。修复模式见 `references/post-batch-verification.md`。

- **「」→""对话引号转换技术（Vol 3-4验证，1,046对转换）**: 用户要求对话使用标准中文双引号 `""`，铭文/标签/刻字保留角括号 `「」`。区分逻辑：正则 `「([^」]+)」`，若内容包含 `。！？` 或长度>20字符→对话→替换为 `\u201c` `\u201d`；若为短标签/科目名/石刻文字→保留 `「」`。技术要点：(1) 全局替换前先扫描统计；(2) 替换后逐弧线抽样验证对话和铭文分流正确；(3) 区分边界案例——`「中土正统」`（石刻）保留，`「仗打完了。」`（对话）转换。切忌全盘替换。已验证Arc 23结果：221章2对话→""、230章5对话→""、10铭文保留「」。全书1,046对对话转换、362对铭文保留。

- **机械按句号分段→对话拆碎 (USER-CORRECTED 2026-05-20, 29章修复验证)**: 用 `re.split(r'(?<=[。！？])', text)` 按句号切段落会破坏对话完整性——一个人说的三句话被拆成三段，每段引号不闭合（裂引号），且对话内部全变成句号而非逗号。用户明确纠正："不是只通过句号分段，一段别人说的话是，，，。这算一段话，不能别人说的话里面全是。" 后果：第一卷030-058章（29章）产生436处裂引号，每章6-36处。**修复**：使用 `scripts/fix-dialogue-splits.py`——检测奇数引号段落→合并至引号平衡→对话内句号改逗号。**预防**：写新章时，对话内部用逗号连接子句；修改已有章时，永远先判断语义边界再决定分段，禁止只按标点符号机械拆分。

- **段落内多句号 (USER-CORRECTED 2026-05-20, 全卷8603处修复)**: 段落内部不应该用句号打断语义流——句号只在段末收束。用户纠正："每段话都是，，，。虽然没有句号收尾，但是小说依然需要，，，。然后进行分段。" 修复：`scripts/fix-internal-periods.py` — 段落内除最后一个句号（或引号前句号）外全部替换为逗号。第一卷120章8,603处替换验证：CJK不变，多句号段→0。**预防**：写新章时段落内只用逗号连接子句，句号仅用于段末。

- **重复段落 (PERSISTENT — 第一卷061-064验证)**: 旧批次章节可能包含近乎完全重复的段落（如061章仁济堂场景出现两次、063章赵元朗方框描述重复）。去重会降低CJK（061-064去重后CJK从~2050降至~1900），需后续补字。**检测**：`for p in paras: if p[:60] in seen: duplicate`。**修复**：去重后若CJK<2000，使用expansion patterns在自然插入点补足内容（感官细节、内心独白、人物背景），禁止水字。

- **模板污染+跨章重复+去重后CJK崩塌（第二卷121-150验证）**: 从旧AI批量创作会话继承的章节可能携带三种系统性问题：(1) `|---|`分隔线；(2) 跨章共享的模板段落（如"暗河的水在远处无声地流着…"出现在10+章中）；(3) 章末同一段落重复5-15+次。去重后CJK预测性下降30-60%——原显示2500-7000 CJK的章节去重后通常仅1200-1800。**预算**：每批10章预计3-7章需扩充，每章2-3轮。完整检测/去重/修复流程见 `references/template-dedup-workflow.md`。第二卷B3(141-150)最严重：141-143章各需3-4轮扩充。**关键**：绝不跳过去重后CJK验证——原CJK≥2000不代表去重后仍达标。

- **全卷元叙事批量清除（49文件/150+处验证）**: "第X弧线"和"第X卷"作为角色/旁白口中的故事结构术语属于第四面墙破裂。使用分层正则替换批量清除：(1) 先处理具体模式（"第X弧线终了"→"这一阶段终了"，"第X弧线期间"→"这段时间里"，"下一弧线"→"下一步"）；(2) 再处理通用模式（"第X弧线"→"这一阶段"）；(3) 卷号同理（"第X卷结束"→"这一卷合上"）；(4) **陷阱**：正则 `第[一二三四五六七八九十]+卷[^结终了是]` 可能过度匹配产生残留（如"第三卷四"→保留"第"前缀+替换=错误）。修复后再跑验证扫描，逐处清理残留。详见 `references/meta-narrative-mass-removal.md`。

- **CONTEXT COMPACTION vs FILESYSTEM MISMATCH (Arc 18 batch 4 validated, 2026-05-19)**: When a novel-writing session resumes from a compacted context window, the compaction summary's chapter titles and filenames may NOT match the actual files on disk. This session found: (1) Compaction claimed chapter 467 is 「民心不可违」but disk has 「阿来的地道网」; (2) Compaction claimed single files per chapter but disk has DUPLICATE files at 461, 464, 467, 469, 472, 475 (two different `.txt` files for the same chapter number); (3) Compaction said files at `/mnt/d/sideline/ai/novel/` but actual location is `/mnt/d/sideline/ai/novel/中土纪元/`. **MANDATORY**: before writing ANY chapter after a compacted-resume, run `ls` on the volume directory and compare AGAINST the outline file (not the compaction summary). Use the outline + actual filesystem as the source of truth. The compaction is a reference hint, not ground truth. Verify: directory path, existing chapter range, duplicate files, and chapter titles before writing anything.

## Reference Files

- `scripts/fix-dialogue-splits.py` — **对话裂引号修复**：合并被句号拆碎的对话段落，内部句号→逗号。用法：`python3 scripts/fix-dialogue-splits.py <章节文件>`。第一卷29章436处裂引号归零验证。
- `scripts/fix-internal-periods.py` — **段落内逗号流修复**：段落内除末句外全部句号→逗号。用法：`python3 scripts/fix-internal-periods.py <章节文件>`。第一卷120章8,603处替换验证。
- `references/paragraph-density-scan.md` — **段落密度扫描**：检测欠分段章节，对标第001章65段基准。
- `references/deep-segmentation-workflow.md` — **深度语义分段三阶段修复**：合并裂引号→段落内逗号流→语义拆分。第一卷061-080验证（20章均25→37段）。
- `references/clean-dense-restructuring.md` — **格式干净但结构密集的继承章节**：无需三阶段修复，直接语义分段。第二卷121-130验证（10章均19.3→31.1段，格式零修复）。
- `tools/audit_html.py` — **增强HTML审计报告**：生成包含Chart.js趋势图的暗色主题HTML报告，浏览器打开查看。用法同audit.py但输出可视化报告。
- `tools/export_docx.py` — **校对稿导出**：pandoc一键将章节txt转为Word文档，支持逐章或合并导出。输出到 `exports/` 目录。
- `tools/progress.py` — **进度看板**：全书进度全景（章节+字数+完成率），支持终端/PNG图表/HTML三种模式。用法：`python3 tools/progress.py [--chart|--html]`。
- `tools/motifs.py` — **物码追踪器**：全书物码/人物/地点/阵营频率追踪，30+预定义模式，支持CSV导出。用法：`python3 tools/motifs.py [--tag 标记名] [--export file.csv]`。
- `references/template-dedup-workflow.md` — **模板去重工作流**：检测三种系统污染（`---`分隔线、跨章共享模板段落、章末批量重复），去重后CJK崩塌预算表（30-60%下降）。第二卷121-150验证。
- `references/batch-resegmentation-workflow.md` — **分批重分段工作流**：去重→分段→扩充→审计四阶段。第二卷139-218（80章）全验证。含模板污染七模式、deep_split()函数、已验证修复模式（ASCII引号/模板去重/扩充注入的首选方式）、五维审计汇报强制格式。
- `references/naming-batch-fix.md` — 名字/年号批量统一技术
- `references/permanent-rules.md` — 双向穿越小说永久强制规则
- `references/metaphor-novel-guide.md` — 隐喻历史小说创作指南
- `references/word-count-verification.md` — 字数验证方法对比
- `references/wsl-word-count-pattern.md` — WSL环境下可靠的字数统计模式
- `references/anomaly-scanning.md` — 系统性异常扫描：数字污染、重复段落
- `references/chapter-expansion-patterns.md` — 章节扩展模板
- `references/meta-narrative-fix.md` — 元叙事修复：检测、替换、标题恢复完整流程
- `references/full-volume-audit.md` — 全卷审核：串行逐章检查（默认）、并行子代理模式
- `references/arc-audit-combined.py` — 弧线双重审计：CJK字数+大纲关键词对位（用户要求，每次弧线完成后必须执行）
- `references/arc-audit-full-scan.py` — 弧线全扫描审计：内部编号、标题对位、格式、CJK、重复段落、模板检测（单次全量，弧8验证7/20章错位检出）
- `references/keyword-verification.md` — 关键词双重验证：精确匹配→模糊语义匹配两遍法，批量关键词补丁模式，全卷审计执行顺序
- `references/automated-audit-tools.md` — 自动化审计工具：jieba关键词提取+cnsenti情感密度+批量审计脚本（pip install jieba cnsenti rich）
- `references/em-dash-removal.md` — 「——」过度使用批量替换脚本与手工重写技术
- `references/format-compliance-scan.md` — 格式合规扫描脚本
- `references/keyword-verification.md` — 关键词双重验证：精确匹配→模糊语义匹配两遍法，批量关键词补丁模式
- `references/three-round-expansion.md` — 三轮批量扩展模式：第1轮实质性收尾→第2轮微收尾→第3轮定向推字数（Arc 10验证，10章全低于2000→三轮后全部达标）
- `references/sparse-outline-volumes.md` — 稀疏大纲卷创作模式：当大纲只有弧线名和主题无逐章分解时，如何提取主题→映射历史原型→创建10章大纲→确保连续性→终章收束
- `references/outline-gap-supplement.md` — 大纲缺失补充工作流：检测→补充→合并单文件→验证（arcs 9-16验证，201-460章）
- `references/dual-arc-comparison.md` — 双弧线对比模板：同卷内连续弧线审计完成后，以地形/武器/战术/民间/物码/收束六维对比呈现卷主题演进
- `references/per-chapter-dash-audit.md` — 逐章「——」审计：用户要求的逐章分析→分类→选择性替换模式（保留修辞性破折号，仅替换可替换的）
- `references/em-dash-manual-analysis.md` — 「——」逐章手动分析法：四分类体系(A/B/C/D)、保守替换流程、文件损坏预防（Arc 18验证）
- `references/civil-war-chapter-patterns.md` — 内战章节模式：物件对峙技术、短文原因、预写检查清单（Arc 17, 451-455验证, 5章全867-1272 CJK首稿, 3轮扩写）
- `references/batch-paragraph-breaking.md` — 批量分段拆分：`break_long_paragraph()` 函数，按句子边界机械拆分长段落（180+章验证）
- `references/batch-dash-removal-v2.md` — 批量破折号替换v2：三步正则→零残留（64章/3,597个）
- `references/meta-narrative-mass-removal.md` — 全卷元叙事批量清除："第X弧线"/"第X卷"分层正则替换+残留验证
- `references/missing-end-marker-scan.md` — 批量操作后结束标记扫描：检测缺失+补入脚本（6章实际发生）
- `references/gap-filling.md` — Gap-filling workflow: bridging existing chapters (read both sides, map continuity, handle outline contradictions)
- `references/inherited-arc-cleanup.md` — Inherited arc cleanup: detection, format fix, and cost budget for +3-interval sparse arcs with pre-existing chapters from prior sessions (Arc 10 validated)
- `references/inherited-volume-segmentation.md` — Inherited volume segmentation: detection and repair of systemic corruption (intra-chapter duplication, cross-chapter template pollution, `|---|` separators, line numbers) in volumes from prior bulk-generation sessions. Run Phase 0 scan BEFORE any segmentation work.
- `references/batch-resegmentation-workflow.md` — **分批重分段工作流**：六阶段（去重→分段→引号归一化→孤儿引号扫描→多角色扫描→逗号流→报告）。121-280（160章/16批）全验证。**报告铁律**：修复必须输出章节+行号（如"ch198 L20/L22 空引号对"）。孤儿引号三模式（①孤儿开引号`" `前缀 ②空引号对`" "` ③孤儿关引号`" `）为分割后最常见问题（280章中15+实例），必须在引号归一后、多角色扫描前检测修复。
- `references/temp-file-expansion.md` — Temp-file expansion technique: write→merge→fix→verify 4-step pattern that avoids Unicode-escape failures in execute_code and ASCII-quote conversion in patch (Arc 10-2 validated)
- `references/shared-expansion-pattern.md` — Shared expansion: one temp file → multiple chapters, saves 10+ tool calls per batch when 3+ chapters need expansion (Arc 11-1 validated)
- `references/chapter-reorganization.md` — 章节重组批量重映射：大纲重编号后旧章→新章内容对齐、均匀插入、批量复制重命名、验证关键映射
- `references/template-pollution.md` — 模板污染三模式：跨章模板/跨章复用/章末机械重复的检测与修复（中土纪元第二卷80章验证）
- `references/volume-migration-workflow.md` — Volume migration: moving chapters between volume folders when outline range doesn't match actual file distribution, with two-tier quality scan diagnostics
- `references/batch-template-replacement-personalized.md` — Batch template replacement: replace formulaic chapter closings (风从暗河 etc.) with personalized endings per chapter, with post-replacement cleanup pass
- `references/volume-start-workflow.md` — 新卷启动工作流：旧章标题扫描+批量重命名对齐v4大纲（第二卷弧7/8验证）
- `references/four-phase-arc-review.md` — 四阶段弧线全面审查：格式扫描→大纲对位→逻辑链→故事性，含可复用Python脚本模式
- `references/volume-structure-audit.py` — 全卷结构审计：扫描所有卷文件夹的实际章号范围，与大纲声明对比，检测卷归属错误、内部编号偏移、大纲标题vs文件标题偏差、模板污染vs格式干净的二分类质量信号
- `references/outline-supplement-workflow.md` — 大纲缺失弧线补充流程：检测→读已有章→推断缺失章→创建补充大纲→创作 (Arc 11-2验证，5章首稿全达标)
