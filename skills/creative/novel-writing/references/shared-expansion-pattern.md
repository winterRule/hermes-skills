# Shared Expansion Pattern (共享扩展模式)

When 3+ chapters in a batch are all short (below 2000 CJK), writing individual expansion temp files for each chapter costs N×2 tool calls (N × `write_file` + N × `execute_code` merge). The shared-expansion pattern reduces this to 1×2.

## When to use

- 3+ chapters in a batch are short by comparable amounts
- The expansion text is thematically related (closing paragraphs, atmospheric wrap-up)
- The chapters share the same arc/theme, so generic closure text fits all

## Anti-pattern (what we did before, validated across arcs 9-10)

```
For each short chapter:
  1. write_file → /tmp/hermes_exp_{CH}.txt  (1 tool call)
  2. execute_code → merge + fix quotes       (1 tool call)
Total: N chapters × 2 = 6-14 tool calls per batch
```

## Shared pattern (what we did in arc 11-1, validated)

```
1. write_file → /tmp/hermes_exp_SHARED.txt   (1 tool call — all chapters)
2. execute_code → merge into ALL chapters     (1 tool call — batch merge)
Total: 2 tool calls regardless of N
```

## Implementation

### Step 1: Write shared expansion

```txt
# /tmp/hermes_exp_all.txt
[Paragraph 1: 韩先生/识字班 scene — applicable to 侨汇/万里归途 chapters]
[Paragraph 2: 老陈/渔网 scene — applicable to 青年投奔/技工 chapters]
[Paragraph 3: atmospheric closure — applicable to all chapters]
```

### Step 2: Merge with selective distribution

```python
import re, os

base = "/mnt/d/sideline/ai/novel/中土纪元/第二卷_浴血中土"

with open("/tmp/hermes_exp_all.txt", 'r', encoding='utf-8') as f:
    shared_exp = f.read().strip()

parts = shared_exp.split('\n\n')

for ch_num in short_chapters:
    # Pick appropriate parts based on chapter content
    if ch_num in [243, 244]:
        exp = parts[0]  # 韩先生/识字班 part
    elif ch_num in [246, 247]:
        exp = parts[1]  # 老陈/渔网 part
    else:
        exp = parts[0] + "\n\n" + parts[1]  # both
    
    # ... standard merge + fix quotes + fix dashes + verify ...
```

## Tool-call savings

| Batch | Chapters | Old pattern | Shared pattern | Savings |
|:--|:--|:--|:--|:--|
| Arc 10-1 (211-220) | 5 short | 10 calls | N/A | - |
| Arc 10-2 (221-230) | 5 short | 10 calls | N/A | - |
| Arc 10-3 (231-240) | 5 short | 10 calls | N/A | - |
| Arc 11-1 (241-250) | 7 short | 14 calls | 2 calls | -12 |

## Pitfall

- If chapters have distinct themes, shared text will feel forced. Use individual expansions for chapters with unique content needs.
- Shared expansions work best for atmospheric/closure paragraphs, not for chapter-specific plot content.
- Still run the full fix pipeline (quotes + dashes + CJK verify) after merge — temp files introduce the same format pollution as individual expansions.
