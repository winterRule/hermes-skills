# Per-Chapter Dash Audit (Surgical, User-Requested)

## When to Use

When the user says "一章一章的分析这个—，可以替换的进行替换，不用替换的就别替换" — or any variant asking for chapter-by-chapter em-dash review. This is a **judgment-based** approach, not batch replacement. The user wants you to decide which dashes are structural rhetoric (keep) vs. lazy connectors (replace).

## Workflow

### Step 1: Dump all dashes with context
```python
import re
content = ...  # chapter text
segments = content.split('——')
for j in range(1, len(segments)):
    before = segments[j-1][-35:] if len(segments[j-1]) > 35 else segments[j-1]
    after = segments[j][:50] if len(segments[j]) > 50 else segments[j]
    print(f"  [{j:2d}] ...{before}——{after}...")
```

### Step 2: Categorize every 「——」

| Category | Pattern | Action |
|----------|---------|--------|
| **Rhetorical "不是X——是Y"** | Core character speech pattern, redefines a concept | **KEEP** — this is the arc's structural rhetoric |
| **科目002/账本数据** | Structured data entries like `战后——疤章——继续——补` | **KEEP** — formatted data, not prose |
| **Character stream-of-consciousness** | Runner's pencil note, urgent intel report | **KEEP** — shows character's mental state |
| **Dramatic speech pause** | `竹雷只是在等——等触发` | **KEEP** if ≤2-3 per chapter |
| **Explanatory** | `补给节点——石浦码头` | **REPLACE** with `：` (colon) |
| **Clarifying/causal** | `没有纸——纸全被封了` | **REPLACE** with `，` |
| **Chain-breaking** | `X——Y——Z——W` (3+ in one sentence) | **REPLACE** middle dashes with `，` or `。` |
| **Sentence-splitting** | `是谁踩上来的——竹雷只知道` | **REPLACE** with `。` |

### Step 3: Apply targeted replacements via execute_code batch

Use exact old_string→new_string replacements with `content.replace()` in a Python script. This is safer than regex and preserves CJK counts.

### Step 4: Verify after each chapter

- CJK must stay ≥ 2000
- Dashes should drop but core rhetoric preserved
- Target: ≤2.0/百字 ideally, ≤3.0/百字 acceptable for arcs where dash rhetoric is structural

## Example: Chapter 171 (Arc 18)

- Original: 41 dashes / 2.0百字
- Categorized: 15 replaceable (explanatory/colon-comma), 26 must-keep (科目002 data, character voice, rhetoric)
- After: 27 dashes / 1.3百字 ✅

## Example: Chapter 173 (Arc 18)

- Original: 95 dashes / 3.8百字 — heavy chains in阿禾/林嫂 monologues
- Categorized: ~90 replaceable (chain-breaking, explanatory), ~5 must-keep
- After: 4 dashes / 0.2百字 ✅✅

## Pitfalls

- **Don't blindly regex-replace**: The user explicitly rejected blanket replacement. Each dash must be judged.
- **Keep the arc's structural rhetoric**: If the arc's core theme expression uses "不是X——是Y" across multiple characters, that's intentional style — don't destroy it.
- **Expansion text often introduces new dashes**: When you expand a chapter, the expansion text itself may contain dashes. Budget an additional dash-audit pass after expansion.
- **Chapters 175+ in arcs 18-20**: These arcs consistently had dash densities of 4-7/百字. The user accepted higher density in later chapters where the rhetoric was integral to character voice. Present honest frequency numbers and let the user decide.
