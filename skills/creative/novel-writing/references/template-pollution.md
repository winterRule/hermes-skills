# Template Pollution Patterns (模板污染模式)

Discovered in 中土纪元 第二卷 (chapters 121-200), inherited from prior writing sessions.

## Pattern 1: Cross-Chapter Template (跨章模板)

**"暗河的水在远处无声地流着"** — a large ~200-CJK atmospheric paragraph that appears verbatim at the end of multiple chapters (134, 135, 136, 137, 138, 141, 142, 143, 144, and more).

```
暗河的水在远处无声地流着。从北岭发源，穿过采石场，绕过石浦，流过江南城外，汇入东海。这条河在战争开始之后的每一天都在变化，水位涨落、渡口易手、滩涂上的归码石子被洪水冲走又被后来者重新埋下。但河本身没有变。它还是从北往南流。...水伯站在渡口的石阶上，把竹篙重新插进水里。水位的湿痕在篙身上画出了战争段的全部水文记录。...
```

Detection: `grep -c "暗河的水在远处无声地流着" *.txt` across all volume directories.

## Pattern 2: Cross-Chapter Analysis Block (跨章复用段)

**"在下水道网络的运转过程中，老陈发现了一个规律..."** — a tactical analysis paragraph that appears identically in chapters 141, 142, 143 (下水道灯火, 仁济堂灰瓷罐, 林文渊逃亡). It belongs in chapter 141 but was pasted into 142 and 143.

Detection: `grep -c "在下水道网络的运转过程中" *.txt`

## Pattern 3: Mechanical End-of-Chapter Repetition (章末机械重复)

The final paragraph of a chapter is duplicated 5-25 times. Examples:

| Chapter | Repeated Text | Count | CJK Inflation |
|---------|--------------|-------|---------------|
| 142 | "灰瓷罐的盖子旋紧之后，林嫂在罐身外面贴了一张小纸条..." | ×12 | ~900 CJK |
| 134 | "京系车队碾过的车辙压在泥路中央..." | ×8 | ~600 CJK |
| 191 | "被烧的村庄废墟里，一块还没有完全烧焦的门板上留着半副对联..." | ×25 | ~1,800 CJK |
| 144 | "炮声从北岭方向传过来，在暗河的峡谷里回荡了三次..." | ×15 | ~1,200 CJK |
| 143 | "论文手稿被暗河的水溅湿了几个字..." | ×15 | ~900 CJK |
| 141 | "下水道里的油灯被潮气打灭了一盏..." | ×12 | ~800 CJK |
| 135 | "写日志的炭条又短了一截..." | ×5+ | ~400 CJK |
| 133 | "溃兵踩过的泥路上，被丢弃的军服和靴子在雨水里泡着..." | ×9 | ~650 CJK |

Detection:
```python
from collections import Counter
lines = text.split('\n')
counts = Counter(l.strip() for l in lines if l.strip())
dupes = {k: v for k, v in counts.items() if v >= 3}
```

## Impact on CJK

| Chapter | Apparent CJK | After Dedup | Difference |
|---------|-------------|-------------|------------|
| 191 | 5,472 | 761 | -4,711 |
| 142 | ~2,500 | ~1,300 | -1,200 |
| 143 | ~2,500 | ~1,200 | -1,300 |
| 134 | ~2,500 | ~1,500 | -1,000 |

**Every chapter with template pollution needs 500-1,200 CJK of expansion after dedup.**

## Expansion Guidelines

When expanding dedup-shortened chapters:
1. Add sensory detail (sound, smell, temperature, texture) to existing scenes
2. Add character interiority (what they remember, fear, hope)
3. Extend物码体系 connections (reference objects from other chapters)
4. NEVER pad with generic descriptions or repeated phrases
5. ALIGN with outline keywords and chapter theme
